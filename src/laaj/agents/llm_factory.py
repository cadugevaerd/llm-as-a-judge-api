"""
Factory Pattern para criação de instâncias LLM com auto-descoberta dinâmica

O Factory Pattern implementado aqui utiliza auto-descoberta via JSON para:
- Carregar modelos dinamicamente sem hardcoding
- Suportar múltiplos provedores de API automaticamente
- Permitir adição de novos modelos apenas atualizando o JSON
- Manter compatibilidade com configurações de fallback

Vantagens da abordagem dinâmica:
- Auto-descoberta de modelos via arquivo JSON gerado pelos testes
- Suporte automático a novos provedores (anthropic, openrouter, mistral, etc.)
- Configuração flexível per-modelo (tokens, timeout, parâmetros específicos)
- Sistema de fallback para quando JSON não está disponível
- Health checks e validação automática
"""

import logging
from typing import Callable, Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from laaj.config.models_loader import models_loader, ModelsConfigError
from laaj.agents.llms import create_llm  # Função genérica de criação

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory (Fábrica) para criar instâncias de Large Language Models (LLMs) com auto-descoberta
    
    Esta implementação revoluciona o padrão Factory tradicional:
    
    NOVO SISTEMA DINÂMICO:
    1. Auto-descoberta de modelos via arquivo JSON gerado pelos testes de performance
    2. Criação dinâmica de instâncias usando configuração per-modelo
    3. Suporte automático a múltiplos provedores (anthropic, openrouter, mistral, etc.)
    4. Sistema de fallback para compatibilidade quando JSON não disponível
    
    VANTAGENS:
    - Sem hardcoding de modelos - tudo vem do JSON
    - Adição de novos modelos apenas executando os testes
    - Configuração flexível per-modelo (tokens, timeout, parâmetros)
    - Health checks automáticos
    - Performance baseada em dados reais de testes
    
    Como funciona agora:
    1. Carrega configuração JSON com modelos testados e aprovados
    2. Cria instâncias dinamicamente usando configurações específicas
    3. Aplica fallback para modelos não encontrados no JSON
    4. Mantém compatibilidade com API existente
    """
    
    _cached_models: Dict[str, Callable[[], ChatOpenAI]] = {}
    _config_loaded = False
    
    @classmethod
    def _ensure_config_loaded(cls) -> None:
        """Garante que a configuração JSON está carregada e os modelos registrados."""
        if not cls._config_loaded:
            cls._load_models_from_config()
            cls._config_loaded = True
    
    @classmethod
    def _load_models_from_config(cls) -> None:
        """Carrega modelos dinamicamente do arquivo JSON de configuração."""
        try:
            logger.info("🔧 [FACTORY] Carregando modelos do arquivo JSON...")
            
            # Obter lista de modelos ativos da configuração
            active_models = models_loader.get_active_models()
            
            if not active_models:
                logger.warning("⚠️ [FACTORY] Nenhum modelo ativo encontrado no JSON, usando fallback")
                cls._load_fallback_models()
                return
            
            # Carregar cada modelo ativo
            for model_id in active_models:
                model_config = models_loader.get_model_config(model_id)
                if model_config and model_config.status == 'active':
                    # Criar função factory específica para este modelo
                    creator_func = cls._create_model_factory_function(model_id, model_config)
                    cls._cached_models[model_id] = creator_func
                    logger.debug(f"✅ [FACTORY] Modelo registrado: {model_id}")
            
            logger.info(f"✅ [FACTORY] {len(cls._cached_models)} modelos carregados dinamicamente")
            
        except Exception as e:
            logger.error(f"❌ [FACTORY] Erro ao carregar configuração: {e}")
            logger.warning("⚠️ [FACTORY] Usando configuração de fallback")
            cls._load_fallback_models()
    
    @classmethod 
    def _create_model_factory_function(cls, model_id: str, model_config) -> Callable[[], ChatOpenAI]:
        """
        Cria função factory específica para um modelo baseado na configuração JSON.
        
        Args:
            model_id: ID do modelo
            model_config: Configuração do modelo do JSON
            
        Returns:
            Callable: Função que cria instância do modelo
        """
        def create_model() -> ChatOpenAI:
            try:
                # Obter configuração do provedor
                provider_config = models_loader.get_provider_config(model_config.provider)
                
                if not provider_config:
                    logger.error(f"❌ [FACTORY] Provedor não encontrado: {model_config.provider}")
                    raise ValueError(f"Provedor '{model_config.provider}' não configurado")
                
                # Obter configurações específicas
                capabilities = model_config.capabilities or {}
                max_tokens = capabilities.get('max_tokens', 1024)
                temperature = capabilities.get('temperature', 0)
                timeout = capabilities.get('timeout', 30)
                
                logger.info(f"🏭 [FACTORY] Criando {model_config.display_name} ({model_id})")
                
                # Criar instância baseada no provedor
                if provider_config.api_type == 'anthropic':
                    # Usar ChatAnthropic diretamente para modelos Claude
                    import os
                    api_key = os.getenv(provider_config.requires_key)
                    if not api_key:
                        raise ValueError(f"API key não encontrada: {provider_config.requires_key}")
                    
                    return ChatAnthropic(
                        model=model_id,
                        api_key=api_key,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        timeout=timeout
                    )
                else:
                    # Usar create_llm para modelos OpenRouter e outros
                    return create_llm(model_id)
                    
            except Exception as e:
                logger.error(f"❌ [FACTORY] Erro ao criar {model_id}: {e}")
                raise
        
        return create_model
    
    @classmethod
    def _load_fallback_models(cls) -> None:
        """Carrega modelos de fallback quando JSON não está disponível."""
        logger.info("🔧 [FACTORY] Carregando modelos de fallback...")
        
        # Importar funções existentes para fallback
        try:
            from laaj.agents.llms import (
                get_llm_llama_4_maverick,
                get_llm_anthropic_claude_4_sonnet,
                get_llm_google_gemini_pro
            )
            
            fallback_models = {
                "llama-4-maverick": get_llm_llama_4_maverick,
                "claude-4-sonnet": get_llm_anthropic_claude_4_sonnet,
                "google-gemini-2.5-pro": get_llm_google_gemini_pro,
            }
            
            cls._cached_models.update(fallback_models)
            logger.info(f"✅ [FACTORY] {len(fallback_models)} modelos de fallback carregados")
            
        except ImportError as e:
            logger.error(f"❌ [FACTORY] Erro ao carregar funções de fallback: {e}")
            raise
    
    @classmethod
    def create_llm(cls, model_name: str) -> ChatOpenAI:
        """
        Método principal da Factory - cria uma instância do LLM solicitado dinamicamente
        
        NOVO: Agora usa auto-descoberta via JSON com fallback automático
        
        Args:
            model_name (str): Nome do modelo a ser criado (ex: "claude-4-sonnet")
            
        Returns:
            ChatOpenAI: Instância configurada do modelo solicitado
            
        Raises:
            ValueError: Se o modelo solicitado não estiver disponível
            
        Exemplo:
            llm = LLMFactory.create_llm("claude-4-sonnet")
        """
        # Garantir que a configuração está carregada
        cls._ensure_config_loaded()
        
        # Verificar se modelo está disponível
        if model_name not in cls._cached_models:
            # Tentar atualizar configuração antes de falhar
            try:
                logger.info(f"🔄 [FACTORY] Modelo '{model_name}' não encontrado, recarregando configuração...")
                cls._config_loaded = False
                cls._cached_models.clear()
                cls._ensure_config_loaded()
            except Exception as e:
                logger.warning(f"⚠️ [FACTORY] Erro ao recarregar configuração: {e}")
        
        # Validação final
        if model_name not in cls._cached_models:
            available_models = ", ".join(cls._cached_models.keys())
            error_msg = f"Modelo '{model_name}' não encontrado. Disponíveis: {available_models}"
            
            logger.error(f"❌ [FACTORY] {error_msg}")
            raise ValueError(error_msg)
        
        # Log informativo sobre qual modelo está sendo criado
        logger.info(f"🏭 [FACTORY] Criando instância do modelo: {model_name}")
        
        try:
            # Executar função factory
            model_instance = cls._cached_models[model_name]()
            
            logger.info(f"✅ [FACTORY] Modelo {model_name} criado com sucesso")
            return model_instance
            
        except Exception as e:
            logger.error(f"❌ [FACTORY] Erro ao criar instância de {model_name}: {e}")
            raise
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """
        Retorna lista de todos os modelos disponíveis na factory (DINÂMICO)
        
        NOVO: Carrega modelos dinamicamente do JSON de configuração
        
        Útil para:
        - Validações
        - Documentação dinâmica  
        - Interfaces de usuário
        - Testes
        
        Returns:
            List[str]: Lista com nomes de todos os modelos disponíveis
            
        Exemplo:
            models = LLMFactory.get_available_models()
            # Retorna modelos baseados nos testes de performance
        """
        cls._ensure_config_loaded()
        return list(cls._cached_models.keys())
    
    @classmethod
    def is_model_supported(cls, model_name: str) -> bool:
        """
        Verifica se um modelo é suportado sem tentar criá-lo (DINÂMICO)
        
        NOVO: Verifica tanto no cache quanto no JSON de configuração
        
        Útil para validações prévias antes de chamar create_llm()
        
        Args:
            model_name (str): Nome do modelo a verificar
            
        Returns:
            bool: True se o modelo é suportado, False caso contrário
            
        Exemplo:
            if LLMFactory.is_model_supported("claude-4-sonnet"):
                llm = LLMFactory.create_llm("claude-4-sonnet")
        """
        cls._ensure_config_loaded()
        
        # Verificar cache primeiro
        if model_name in cls._cached_models:
            return True
            
        # Verificar se está disponível no JSON mas não carregado ainda
        return models_loader.is_model_available(model_name)
    
    @classmethod
    def register_model(cls, model_name: str, creator_function: Callable[[], ChatOpenAI]) -> None:
        """
        Adiciona um novo modelo à factory dinamicamente
        
        NOVO: Registra no cache interno, não modifica JSON
        
        Permite extensibilidade - novos modelos podem ser adicionados em runtime
        
        Args:
            model_name (str): Nome identificador do modelo
            creator_function (Callable): Função que cria instância do modelo
            
        Exemplo:
            def get_my_custom_llm():
                return ChatOpenAI(model="custom-model")
                
            LLMFactory.register_model("my-custom", get_my_custom_llm)
        """
        cls._ensure_config_loaded()
        
        if model_name in cls._cached_models:
            logger.warning(f"⚠️ [FACTORY] Sobrescrevendo modelo existente: {model_name}")
        
        cls._cached_models[model_name] = creator_function
        logger.info(f"📝 [FACTORY] Modelo '{model_name}' registrado na factory dinamicamente")
    
    @classmethod
    def get_default_model(cls) -> str:
        """
        Obtém o modelo padrão definido no JSON de configuração.
        
        NOVO: Modelo padrão é determinado pelos testes de performance
        
        Returns:
            str: Nome do modelo padrão (mais rápido entre os testados)
        """
        try:
            return models_loader.get_default_model()
        except Exception as e:
            logger.warning(f"⚠️ [FACTORY] Erro ao obter modelo padrão: {e}")
            return "llama-4-maverick"  # fallback
    
    @classmethod
    def get_fastest_models(cls, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtém os modelos mais rápidos baseados nos testes de performance.
        
        NOVO: Dados reais de performance dos testes
        
        Args:
            limit: Número máximo de modelos a retornar
            
        Returns:
            List[Dict]: Lista de modelos ordenados por velocidade
        """
        try:
            return models_loader.get_fastest_models(limit)
        except Exception as e:
            logger.warning(f"⚠️ [FACTORY] Erro ao obter modelos mais rápidos: {e}")
            return []
    
    @classmethod
    def get_models_by_provider(cls, provider: str) -> List[str]:
        """
        Obtém modelos de um provedor específico.
        
        NOVO: Baseado na configuração dinâmica de provedores
        
        Args:
            provider: Nome do provedor (anthropic, google, openai, etc.)
            
        Returns:
            List[str]: Lista de modelos do provedor
        """
        try:
            return models_loader.get_models_by_provider(provider)
        except Exception as e:
            logger.warning(f"⚠️ [FACTORY] Erro ao obter modelos do provedor {provider}: {e}")
            return []
    
    @classmethod
    def validate_json_config(cls) -> bool:
        """
        Valida se a configuração JSON está consistente e disponível.
        
        NOVO: Substitui validate_config_models para sistema dinâmico
        
        Útil para verificar consistência entre JSON e sistema
        
        Returns:
            bool: True se configuração JSON está válida
        """
        try:
            health = models_loader.health_check()
            
            is_healthy = health['status'] in ['healthy', 'degraded']
            active_models = health.get('active_models', 0)
            
            if is_healthy and active_models > 0:
                logger.info(f"✅ [FACTORY] Configuração JSON válida - {active_models} modelos ativos")
                return True
            else:
                logger.warning(f"⚠️ [FACTORY] Configuração JSON com problemas: {health}")
                return False
                
        except Exception as e:
            logger.error(f"❌ [FACTORY] Erro ao validar configuração JSON: {e}")
            return False
    
    @classmethod
    def refresh_config(cls) -> bool:
        """
        Força recarga da configuração JSON e modelos.
        
        NOVO: Permite atualização dinâmica sem reiniciar aplicação
        
        Returns:
            bool: True se recarregou com sucesso
        """
        try:
            # Limpar cache interno
            cls._cached_models.clear()
            cls._config_loaded = False
            
            # Forçar recarga do models_loader
            models_loader.refresh_config()
            
            # Recarregar modelos
            cls._ensure_config_loaded()
            
            logger.info("✅ [FACTORY] Configuração recarregada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ [FACTORY] Erro ao recarregar configuração: {e}")
            return False
    
    @classmethod
    def health_check(cls) -> Dict[str, Any]:
        """
        Verifica estado de saúde do sistema Factory + JSON.
        
        NOVO: Health check completo do sistema dinâmico
        
        Returns:
            Dict: Relatório de saúde completo
        """
        try:
            cls._ensure_config_loaded()
            
            # Health check do models_loader
            loader_health = models_loader.health_check()
            
            # Health check do cache interno
            cached_models_count = len(cls._cached_models)
            config_loaded = cls._config_loaded
            
            # Testar criação de um modelo (se disponível)
            test_creation = False
            if cls._cached_models:
                try:
                    test_model = next(iter(cls._cached_models))
                    cls.create_llm(test_model)
                    test_creation = True
                except:
                    pass
            
            return {
                "factory_status": "healthy" if cached_models_count > 0 and config_loaded else "degraded",
                "cached_models_count": cached_models_count,
                "config_loaded": config_loaded,
                "test_model_creation": test_creation,
                "models_loader_health": loader_health,
                "available_models": list(cls._cached_models.keys())
            }
            
        except Exception as e:
            return {
                "factory_status": "error",
                "error": str(e),
                "cached_models_count": 0,
                "config_loaded": False
            }


# Exemplo de uso e teste da factory
if __name__ == "__main__":
    """
    Exemplo de como usar a LLMFactory
    Este bloco só executa quando o arquivo é rodado diretamente
    """
    
    # Configurar logging para ver os outputs
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testando LLMFactory...")
    
    # 1. Listar modelos disponíveis
    print(f"📋 Modelos disponíveis: {LLMFactory.get_available_models()}")
    
    # 2. Verificar se modelo existe
    model_name = "claude-4-sonnet"
    if LLMFactory.is_model_supported(model_name):
        print(f"✅ Modelo {model_name} é suportado")
        
        # 3. Criar instância do modelo
        try:
            llm = LLMFactory.create_llm(model_name)
            print(f"🎉 Instância criada: {type(llm)}")
        except Exception as e:
            print(f"❌ Erro ao criar modelo: {e}")
    
    # 4. Testar modelo inexistente
    try:
        LLMFactory.create_llm("modelo-inexistente")
    except ValueError as e:
        print(f"✅ Erro esperado capturado: {e}")
    
    # 5. Validar configuração JSON
    is_valid = LLMFactory.validate_json_config()
    print(f"📊 Configuração JSON válida: {is_valid}")
    
    # 6. Health check completo
    health = LLMFactory.health_check()
    print(f"💊 Health check: {health['factory_status']}")
    
    # 7. Testar modelo padrão
    default_model = LLMFactory.get_default_model()
    print(f"🎯 Modelo padrão: {default_model}")
    
    # 8. Modelos mais rápidos
    fastest = LLMFactory.get_fastest_models(3)
    if fastest:
        print(f"🚀 Top 3 modelos mais rápidos:")
        for i, model in enumerate(fastest, 1):
            print(f"   {i}. {model['display_name']}: {model['average_time']:.1f}s")
    
    print("🏁 Teste concluído!")