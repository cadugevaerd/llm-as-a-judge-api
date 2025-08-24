"""
Factory functions para criação de instâncias específicas de LLMs.
Usado pela LLMFactory para instanciar modelos através do OpenRouter.
No novo escopo, apenas modelos judge são necessários.
"""

from langchain_openai import ChatOpenAI
import laaj.config as config

def get_llm_anthropic_claude_4_sonnet():
    """Cria instância do Claude 4 Sonnet - modelo judge principal."""
    return ChatOpenAI(
        model="anthropic/claude-sonnet-4",
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
    )

def get_llm_google_gemini_pro():
    """Cria instância do Google Gemini 2.5 Pro - modelo judge alternativo."""
    return ChatOpenAI(
        model="google/gemini-2.5-pro",
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
    )

def get_llm_gpt_5():
    """Cria instância do GPT-5 - modelo judge alternativo."""
    return ChatOpenAI(
        model="openai/gpt-5-mini",
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
    )
    
def get_llm_qwen_3_instruct():
    """Cria instância do Qwen 3 Instruct - modelo judge alternativo."""
    return ChatOpenAI(
        model="qwen/qwen3-30b-a3b-instruct-2507",
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
    )
    
def get_llm_deepseek():
    """Cria instância do DeepSeek - modelo judge alternativo."""
    return ChatOpenAI(
        model="deepseek/deepseek-chat-v3.1",
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
    )

def get_llm_llama_4_maverick():
    """Cria instância do Llama 4 Maverick - modelo judge principal com melhor performance."""
    return ChatOpenAI(
        model="meta-llama/llama-4-maverick",
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.1  # Baixa temperatura para consistência
    )