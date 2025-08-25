"""
Configuração integrada para LLM as Judge Study - Multi-Provider Edition.

SISTEMA REFATORADO PARA MULTI-PROVIDER:
- Exportação de configurações estáticas para compatibilidade (config.py)
- Sistema dinâmico de carregamento via JSON (models_loader.py)
- Factory functions integradas para múltiplos provedores
- Configuração centralizada com fallbacks robustos

NOVO: Auto-descoberta + Carregamento Dinâmico + Multi-Provider Support
"""

# ========== CONFIGURAÇÕES ESTÁTICAS (LEGADO) ==========
# Mantidas para compatibilidade com sistema existente
from .config import (
    OPENROUTER_API, 
    LITERAL_MODELS, 
    WORKFLOW_TIMEOUT_SECONDS, 
    PROMPT_LAAJ, 
    ANTHROPIC_API, 
    MISTRAL_API_KEY
)

# ========== SISTEMA DINÂMICO DE MODELOS ==========
# Novo sistema para auto-descoberta e carregamento dinâmico
from .models_loader import models_loader

# ========== UTILITÁRIOS DE INTEGRAÇÃO ==========


def get_dynamic_models_list():
    """
    Obtém lista de modelos via sistema dinâmico com fallback para legado.
    
    Returns:
        List[str]: Lista de modelos disponíveis
    """
    try:
        config = models_loader.get_config()
        if config and 'models' in config:
            return [model['id'] for model in config['models']]
        else:
            return LITERAL_MODELS
    except Exception:
        return LITERAL_MODELS


def get_available_providers():
    """
    Obtém lista de provedores disponíveis via sistema dinâmico.
    
    Returns:
        List[str]: Lista de provedores disponíveis
    """
    try:
        config = models_loader.get_config()
        if config and 'providers' in config:
            return list(config['providers'].keys())
        else:
            return ["openrouter"]  # Fallback
    except Exception:
        return ["openrouter"]


def is_dynamic_config_available():
    """
    Verifica se configuração dinâmica está disponível.
    
    Returns:
        bool: True se JSON dinâmico disponível, False para fallback legado
    """
    try:
        config = models_loader.get_config()
        return bool(config and 'models' in config and 'providers' in config)
    except Exception:
        return False


def get_system_info():
    """
    Obtém informações do sistema de configuração atual.
    
    Returns:
        Dict[str, Any]: Informações do sistema
    """
    is_dynamic = is_dynamic_config_available()
    
    return {
        "config_system": "dynamic_json" if is_dynamic else "static_legacy",
        "total_models": len(get_dynamic_models_list()),
        "total_providers": len(get_available_providers()),
        "dynamic_available": is_dynamic,
        "last_update": models_loader.get_last_update() if is_dynamic else None,
        "fallback_active": not is_dynamic
    }


# ========== EXPORTS ==========

__all__ = [
    # Configurações estáticas (compatibilidade)
    "OPENROUTER_API", 
    "LITERAL_MODELS", 
    "WORKFLOW_TIMEOUT_SECONDS", 
    "PROMPT_LAAJ", 
    "ANTHROPIC_API", 
    "MISTRAL_API_KEY",
    
    # Sistema dinâmico
    "models_loader",
    
    # Utilitários de integração
    "get_dynamic_models_list",
    "get_available_providers", 
    "is_dynamic_config_available",
    "get_system_info"
]