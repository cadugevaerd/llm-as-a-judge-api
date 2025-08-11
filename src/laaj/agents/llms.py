from langchain_openai import ChatOpenAI
import laaj.config as config

def get_llm_gpt_5():
    return ChatOpenAI(
        model="openai/gpt-5-mini",
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
)

    
def get_llm_google_gemini_pro():
    return ChatOpenAI(
        model="google/gemini-2.5-pro",
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
)
    

def get_llm_anthropic_claude_4_sonnet():
    return ChatOpenAI(
        model="anthropic/claude-sonnet-4",
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
)
    
def get_llm_qwen_3_instruct():
    return ChatOpenAI(
        model="qwen/qwen3-30b-a3b-instruct-2507",
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
)

if __name__ == "__main__":
    import asyncio
    # print(config.OPENROUTER_API)
    llm = get_llm_qwen_3_instruct()
    async def main():
        response = await llm.ainvoke("Hello, how are you?")
        print(response)
    asyncio.run(main())