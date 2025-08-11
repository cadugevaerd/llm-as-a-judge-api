import asyncio
from laaj.config import OPENROUTER_API
from laaj.agents.llm_factory import LLMFactory
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from laaj.langsmith_integration import LangSmithClient
from langsmith import Client

import os

def get_prompt_llm():
    prompt = PromptTemplate.from_template(
        """
        # Instruções:
        - Conte uma história curta sobre {topic}
        - A história nao deve estar em markdown, json ou outro formato que nao seja texto plano.
        """
    )
    return prompt

def chain_story(llm: ChatOpenAI):
    prompt = get_prompt_llm()
    chain = prompt | llm | StrOutputParser()
    return chain

def get_prompt_langsmith(prompt_name: str):
    langsmith_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
    prompt = langsmith_client.pull_prompt(prompt_name)
    return prompt

def chain_laaj(llm):
    prompt = get_prompt_langsmith("laaj-prompt")
    chain = prompt | llm
    return chain

if __name__ == "__main__":
    async def main():
        tracing_client = LangSmithClient()
        
        # Usar factory em vez de imports individuais
        llm = LLMFactory.create_llm("qwen-3-instruct")
        llm2 = LLMFactory.create_llm("gpt-5")
        llm3 = LLMFactory.create_llm("claude-4-sonnet")
        llm_judge = LLMFactory.create_llm("google-gemini-2.5-pro")
        
        chain1 = chain_story(llm)
        chain2 = chain_story(llm2)
        chain3 = chain_story(llm3)  
        
        # prompt = get_prompt_langsmith("laaj-prompt")
        # print(prompt)
        
        result3 = await chain3.ainvoke(input={"topic":"Amigos"})
        result2 = await chain2.ainvoke(input={"topic":"Amigos"})
        
        judge = chain_laaj(llm_judge)
        
        # O prompt em si não precisa ser assíncrono, mas a invocação da chain que o usa, sim.
        # A linha abaixo foi simplificada.
        user_question_prompt = get_prompt_llm()
        user_question = user_question_prompt.format(topic="Amigos")

        result_judge = await judge.ainvoke(input={"answer_a":result2, "answer_b":result3, "question":user_question})
        
        print(result_judge)
        print(type(result_judge))

    asyncio.run(main())
    
    
