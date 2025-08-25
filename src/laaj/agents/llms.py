"""
Factory functions para criação dinâmica de instâncias específicas de LLMs.

SISTEMA REFATORADO PARA MULTI-PROVIDER:
- Suporte dinâmico a anthropic, openrouter, google, mistral, xai, deepseek, etc.
- Configuração específica por provedor baseada no JSON
- Functions de criação geradas dinamicamente baseadas nos testes
- Compatibilidade mantida com funções existentes para fallback
- Configurações otimizadas por modelo (tokens, timeout, parâmetros especiais)

NOVO: Auto-descoberta via JSON + Múltiplos Provedores + Configuração Flexível
"""

import os
import logging
from typing import Union, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI

import laaj.config as config
from laaj.config.models_loader import models_loader

logger = logging.getLogger(__name__)


def create_llm(model_name: str, **override_params) -> Union[ChatOpenAI, ChatAnthropic, ChatMistralAI]:
    """
    Cria instância do modelo LLM pelo nome com suporte multi-provider dinâmico.
    
    NOVO SISTEMA:
    - Auto-detecção do provedor baseada no modelo
    - Configurações específicas por provedor do JSON
    - Parâmetros otimizados por modelo dos testes
    - Fallback inteligente para modelos não configurados
    
    Args:
        model_name (str): Nome do modelo a ser criado (ex: "claude-4-sonnet")
        **override_params: Parâmetros para sobrescrever configuração padrão
        
    Returns:
        Union[ChatOpenAI, ChatAnthropic, ...]: Instância configurada do modelo solicitado
        
    Examples:
        # Usando configuração padrão do JSON
        llm = create_llm("claude-4-sonnet")
        
        # Sobrescrevendo parâmetros
        llm = create_llm("google-gemini-2.5-pro", temperature=0.5, max_tokens=2048)
        
        # Modelo OpenRouter
        llm = create_llm("meta-llama/llama-4-maverick")
    """
    
    try:
        # Tentar obter configuração do JSON primeiro
        model_config = models_loader.get_model_config(model_name)
        provider_config = None
        
        if model_config:
            provider_config = models_loader.get_provider_config(model_config.provider)
            logger.debug(f"🔧 [LLMS] Usando configuração JSON para {model_name}")
        else:
            # Fallback: detectar provedor pelo nome do modelo
            provider_type = _detect_provider_from_model_name(model_name)
            logger.warning(f"⚠️ [LLMS] Modelo {model_name} não encontrado no JSON, usando fallback: {provider_type}")
        
        # Obter configurações (JSON ou fallback)
        if model_config and provider_config:
            return _create_from_json_config(model_name, model_config, provider_config, **override_params)
        else:
            return _create_from_fallback(model_name, **override_params)
            
    except Exception as e:
        logger.error(f"❌ [LLMS] Erro ao criar modelo {model_name}: {e}")
        raise


def _create_from_json_config(
    model_name: str, 
    model_config, 
    provider_config, 
    **override_params
) -> Union[ChatOpenAI, ChatAnthropic, ChatMistralAI]:
    """
    Cria instância baseada na configuração JSON com parâmetros otimizados dos testes.
    
    ESTRATÉGIA DE PROVEDORES:
    - Anthropic: Usa API oficial (claude-sonnet-4-0, claude-3-5-haiku-latest)
    - Mistral: Usa API oficial (mistral-large-latest, mistral-medium-latest, mistral-small-latest)
    - Todos os outros: OpenRouter como proxy (Google, OpenAI, XAI, DeepSeek, Qwen, etc.)
    
    Args:
        model_name: Nome do modelo
        model_config: Configuração do modelo do JSON
        provider_config: Configuração do provedor do JSON  
        **override_params: Parâmetros para sobrescrever
        
    Returns:
        Instância configurada do LLM
    """
    
    # Obter configurações do JSON (testadas e otimizadas)
    capabilities = model_config.capabilities or {}
    base_params = {
        'model': model_name,
        'max_tokens': capabilities.get('max_tokens', 1024),
        'temperature': capabilities.get('temperature', 0),
        'timeout': capabilities.get('timeout', 60)
    }
    
    # Aplicar overrides
    base_params.update(override_params)
    
    logger.info(f"🏭 [LLMS] Criando {model_config.display_name} via {provider_config.api_type}")
    
    # Modelos que usam Anthropic diretamente
    anthropic_direct_models = [
        "claude-sonnet-4-0",
        "claude-3-5-haiku-latest"
    ]
    
    # Modelos que usam Mistral diretamente
    mistral_direct_models = [
        "mistral-large-latest",
        "mistral-medium-latest", 
        "mistral-small-latest"
    ]
    
    # ========== ANTHROPIC DIRETO ==========
    if model_name in anthropic_direct_models:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning(f"⚠️ [LLMS] ANTHROPIC_API_KEY não encontrada para {model_name}, usando fallback OpenRouter")
            return _create_openrouter_fallback(model_name, **base_params)
        
        # Remover 'model' dos base_params para evitar duplicação
        anthropic_params = {k: v for k, v in base_params.items() if k != 'model'}
        
        return ChatAnthropic(
            model=model_name,
            api_key=api_key,
            thinking={"type": "disabled"}, # Desabilita o Reasoning
            **anthropic_params
        )
    
    # ========== MISTRAL DIRETO ==========
    elif model_name in mistral_direct_models:
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            logger.warning(f"⚠️ [LLMS] MISTRAL_API_KEY não encontrada para {model_name}, usando fallback OpenRouter")
            return _create_openrouter_fallback(model_name, **base_params)
        
        # Remover 'model' dos base_params para evitar duplicação
        mistral_params = {k: v for k, v in base_params.items() if k != 'model'}
        
        return ChatMistralAI(
            model=model_name,
            mistral_api_key=api_key,
            **mistral_params
        )
    
    # ========== TODOS OS OUTROS VIA OPENROUTER ==========
    else:
        return _create_openrouter_fallback(model_name, **base_params)


def _create_openrouter_fallback(model_name: str, **params) -> ChatOpenAI:
    """
    Cria instância via OpenRouter (estratégia padrão).
    
    Args:
        model_name: Nome do modelo
        **params: Parâmetros base
        
    Returns:
        ChatOpenAI configurada para OpenRouter
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY não encontrada")
    
    # Configurações especiais para OpenRouter baseadas nos testes
    extra_body = _get_openrouter_extra_body(model_name)
    
    # Remover 'model' dos params para evitar duplicação
    openrouter_params = {k: v for k, v in params.items() if k != 'model'}
    
    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        extra_body=extra_body,
        **openrouter_params
    )


def _create_from_fallback(model_name: str, **override_params) -> ChatOpenAI:
    """
    Cria instância usando configuração de fallback (sistema legado).
    
    Args:
        model_name: Nome do modelo
        **override_params: Parâmetros para sobrescrever
        
    Returns:
        Instância ChatOpenAI configurada
    """
    
    logger.warning(f"⚠️ [LLMS] Usando configuração de fallback para {model_name}")
    
    # Configurações hardcoded para modelos conhecidos (sistema legado)
    llms_can_disabled_reasoning = [
        "google/gemma-3-27b-it",
        "google/gemini-2.5-flash",
        "qwen/qwen3-235b-a22b-2507",
    ]
    
    anthropics_llms = [
        "anthropic/claude-sonnet-4",
        "claude-4-sonnet",
        "claude-3-5-haiku-latest"
    ]
    
    # Parâmetros base
    base_params = {
        'model': model_name,
        'api_key': config.OPENROUTER_API,
        'base_url': "https://openrouter.ai/api/v1",
        'temperature': 0,
        'timeout': 30,
        'max_tokens': 2048 if model_name in anthropics_llms else 1024
    }
    
    # Extra body para OpenRouter
    extra_body = {
        "reasoning": {
            "enabled": False if model_name in llms_can_disabled_reasoning else True,
            "effort": "minimal" if model_name not in llms_can_disabled_reasoning and model_name not in anthropics_llms else None,
            "max_tokens": 1024 if model_name in anthropics_llms else None,
        }
    }
    
    base_params['extra_body'] = extra_body
    
    # Aplicar overrides
    base_params.update(override_params)
    
    return ChatOpenAI(**base_params)


def _detect_provider_from_model_name(model_name: str) -> str:
    """
    Detecta provedor baseado no nome do modelo (fallback).
    
    Args:
        model_name: Nome do modelo
        
    Returns:
        str: Nome do provedor detectado
    """
    
    if model_name.startswith("claude-") or model_name.startswith("anthropic/"):
        return "anthropic"
    elif model_name.startswith("google/") or model_name.startswith("gemini"):
        return "google"  
    elif model_name.startswith("openai/") or model_name.startswith("gpt-"):
        return "openai"
    elif model_name.startswith("mistral"):
        return "mistral"
    elif model_name.startswith("x-ai/") or model_name.startswith("grok"):
        return "xai"
    elif model_name.startswith("deepseek/"):
        return "deepseek"
    elif model_name.startswith("qwen/"):
        return "qwen"
    elif model_name.startswith("meta-llama/") or model_name.startswith("llama"):
        return "meta"
    else:
        return "openrouter"  # Padrão


def _get_openrouter_extra_body(model_name: str) -> Dict[str, Any]:
    """
    Obtém configuração extra_body otimizada para OpenRouter baseada nos testes.
    
    Args:
        model_name: Nome do modelo
        
    Returns:
        Dict: Configuração extra_body
    """
    
    # Modelos que podem desabilitar reasoning (baseado nos testes)
    can_disable_reasoning = [
        "google/gemma-3-27b-it",
        "google/gemini-2.5-flash",
        "google/gemini-2.5-flash-lite", 
        "qwen/qwen3-235b-a22b-2507",
    ]
    
    # Modelos Anthropic que precisam configuração especial
    anthropic_models = [
        "anthropic/claude-sonnet-4",
        "claude-sonnet-4-0",
        "claude-3-5-haiku-latest"
    ]
    
    extra_body = {
        "reasoning": {
            "enabled": False if model_name in can_disable_reasoning else True,
        }
    }
    
    # Configuração específica para modelos não-Anthropic
    if model_name not in anthropic_models and model_name not in can_disable_reasoning:
        extra_body["reasoning"]["effort"] = "minimal"
    
    # Configuração específica para modelos Anthropic  
    if model_name in anthropic_models:
        extra_body["reasoning"]["max_tokens"] = 1024
    
    return extra_body


# ========== FUNÇÕES DE FALLBACK PARA COMPATIBILIDADE ==========
# Mantidas para compatibilidade com código existente


def get_llm_llama_4_maverick() -> ChatOpenAI:
    """Cria instância do Llama 4 Maverick - modelo judge principal com melhor performance."""
    return create_llm("meta-llama/llama-4-maverick")


def get_llm_anthropic_claude_4_sonnet() -> Union[ChatAnthropic, ChatOpenAI]:
    """Cria instância do Claude 4 Sonnet - modelo judge principal."""
    try:
        # Tentar usar Anthropic diretamente se disponível
        if config.ANTHROPIC_API:
            return ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=config.ANTHROPIC_API,
                max_tokens=1024,
                temperature=0,
                timeout=30
            )
        else:
            # Fallback para OpenRouter
            return create_llm("anthropic/claude-sonnet-4")
    except Exception as e:
        logger.warning(f"⚠️ [LLMS] Erro ao criar Claude via Anthropic, usando OpenRouter: {e}")
        return create_llm("anthropic/claude-sonnet-4")


def get_llm_google_gemini_pro() -> ChatOpenAI:
    """Cria instância do Google Gemini 2.5 Pro - modelo judge alternativo."""
    return create_llm("google/gemini-2.5-pro")


def get_llm_gpt_5() -> ChatOpenAI:
    """Cria instância do GPT-5 - modelo judge alternativo."""
    return create_llm("openai/gpt-5")
    

def get_llm_qwen_3_instruct() -> ChatOpenAI:
    """Cria instância do Qwen 3 Instruct - modelo judge alternativo."""
    return create_llm("qwen/qwen3-30b-a3b-instruct-2507")
    

def get_llm_deepseek() -> ChatOpenAI:
    """Cria instância do DeepSeek - modelo judge alternativo."""
    return create_llm("deepseek/deepseek-chat-v3.1")


def get_llm_google_gemma() -> ChatOpenAI:
    """Cria instância do Google Gemma - modelo judge alternativo."""
    return create_llm("google/gemma-3-27b-it")


# ========== FUNÇÕES DE CONVENIÊNCIA E UTILITÁRIOS ==========


def get_available_providers() -> Dict[str, Dict[str, Any]]:
    """
    Obtém lista de provedores disponíveis com suas configurações.
    
    Returns:
        Dict: Dicionário de provedores disponíveis
    """
    try:
        config = models_loader.get_config()
        return config.get('providers', {})
    except Exception as e:
        logger.warning(f"⚠️ [LLMS] Erro ao obter provedores: {e}")
        return {}


def test_model_creation(model_name: str) -> bool:
    """
    Testa se é possível criar uma instância de um modelo.
    
    Args:
        model_name: Nome do modelo para testar
        
    Returns:
        bool: True se conseguiu criar, False caso contrário
    """
    try:
        llm = create_llm(model_name)
        logger.info(f"✅ [LLMS] Teste de criação bem-sucedido: {model_name}")
        return True
    except Exception as e:
        logger.error(f"❌ [LLMS] Falha no teste de criação para {model_name}: {e}")
        return False


def get_model_info(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Obtém informações sobre um modelo específico.
    
    Args:
        model_name: Nome do modelo
        
    Returns:
        Optional[Dict]: Informações do modelo ou None se não encontrado
    """
    try:
        model_config = models_loader.get_model_config(model_name)
        if not model_config:
            return None
            
        provider_config = models_loader.get_provider_config(model_config.provider)
        
        return {
            "model_id": model_config.id,
            "display_name": model_config.display_name,
            "provider": model_config.provider,
            "provider_config": provider_config.__dict__ if provider_config else None,
            "is_default": model_config.is_default,
            "status": model_config.status,
            "performance": model_config.performance,
            "capabilities": model_config.capabilities
        }
        
    except Exception as e:
        logger.warning(f"⚠️ [LLMS] Erro ao obter informações do modelo {model_name}: {e}")
        return None


# ========== EXEMPLO DE USO E TESTE ==========


if __name__ == "__main__":
    """
    Exemplo de uso das funções dinâmicas multi-provider
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testando sistema dinâmico multi-provider...")
    
    # 1. Testar criação dinâmica
    test_models = [
        "claude-4-sonnet",
        "google/gemini-2.5-pro", 
        "meta-llama/llama-4-maverick",
        "deepseek/deepseek-chat-v3.1"
    ]
    
    for model in test_models:
        try:
            print(f"\n🔧 Testando: {model}")
            
            # Obter informações
            info = get_model_info(model)
            if info:
                print(f"   Display: {info['display_name']}")
                print(f"   Provider: {info['provider']}")
                print(f"   Status: {info['status']}")
            
            # Testar criação
            success = test_model_creation(model)
            print(f"   Criação: {'✅' if success else '❌'}")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    # 2. Listar provedores disponíveis
    print(f"\n📋 Provedores disponíveis:")
    providers = get_available_providers()
    for provider_id, provider_info in providers.items():
        print(f"   • {provider_id}: {provider_info.get('api_type', 'unknown')}")
    
    print("\n🏁 Teste concluído!")