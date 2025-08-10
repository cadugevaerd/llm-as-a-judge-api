from re import S
from laaj.config import OPENROUTER_API
from laaj.agents.llms import get_llm_qwen_3_instruct, get_llm_gpt_5, get_llm_anthropic_claude_4_sonnet, get_llm_google_gemini_pro
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
    tracing_client = LangSmithClient()
    
    llm = get_llm_qwen_3_instruct()
    llm2 = get_llm_gpt_5()
    llm3 = get_llm_anthropic_claude_4_sonnet()
    llm_judge = get_llm_google_gemini_pro()
    
    chain1 = chain_story(llm)
    chain2 = chain_story(llm2)
    chain3 = chain_story(llm3)  
    
    # prompt = get_prompt_langsmith("laaj-prompt")
    # print(prompt)
    
    result3 = chain3.invoke(input={"topic":"Amigos"})
    result2 = chain2.invoke(input={"topic":"Amigos"})
    
    judge = chain_laaj(llm_judge)
    
    user_question = get_prompt_llm().invoke(input={"topic":"Amigos"})
    
    result_judge = judge.invoke(input={"answer_a":result2, "answer_b":result3, "question":user_question})
    
    print(result_judge)
    print(type(result_judge))
    
    
