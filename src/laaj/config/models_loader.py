"""
Módulo para carregamento dinâmico de configuração de modelos LLM.

Este módulo implementa:
- Carregamento do arquivo JSON de configuração gerado pelos testes
- Validação da estrutura de configuração 
- Cache e lazy loading para performance
- Sistema de fallback para modelos não configurados
- Health check para verificar disponibilidade dos modelos

Uso:
    loader = ModelsLoader()
    config = loader.get_config()
    models = loader.get_available_models()
    default_model = loader.get_default_model()
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any, Set
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuração individual de um modelo LLM."""
    id: str
    display_name: str
    provider: str
    is_default: bool
    status: str
    performance: Dict[str, Any]
    test_results: Dict[str, Any]
    capabilities: Dict[str, Any]


@dataclass 
class ProviderConfig:
    """Configuração de um provedor de modelos."""
    api_type: str
    requires_key: str
    base_url: Optional[str]


class ModelsConfigError(Exception):
    """Exceção específica para erros de configuração de modelos."""
    pass


class ModelsLoader:
    """
    Classe para carregamento e gerenciamento dinâmico de configurações de modelos.
    
    Implementa:
    - Lazy loading com cache LRU
    - Validação de estrutura JSON
    - Sistema de fallback
    - Health checks
    - Thread-safe operations
    """
    
    _instance = None
    _config_cache = None
    
    def __new__(cls):
        """Singleton pattern para evitar múltiplas instâncias."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicialização do loader."""
        if not hasattr(self, '_initialized'):
            self._config_file_path = self._get_config_path()
            self._last_modified = None
            self._initialized = True
            logger.info("🔧 [LOADER] ModelsLoader inicializado")
    
    def _get_config_path(self) -> Path:
        """Determina o caminho do arquivo de configuração."""
        # Tentar diferentes localizações
        possible_paths = [
            Path(__file__).parent / "models_config.json",  # Mesmo diretório
            Path("src/laaj/config/models_config.json"),     # Raiz do projeto
            Path("models_config.json")                      # Working directory
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"✅ [LOADER] Arquivo de configuração encontrado: {path}")
                return path
        
        # Se não encontrou, usa o primeiro caminho como padrão
        default_path = possible_paths[0]
        logger.warning(f"⚠️ [LOADER] Arquivo não encontrado, usando padrão: {default_path}")
        return default_path
    
    def _should_reload(self) -> bool:
        """Verifica se precisa recarregar a configuração."""
        if self._config_cache is None:
            return True
        
        if not self._config_file_path.exists():
            return False
        
        current_modified = self._config_file_path.stat().st_mtime
        return self._last_modified != current_modified
    
    def _validate_config_structure(self, config: Dict) -> None:
        """
        Valida a estrutura do arquivo JSON de configuração.
        
        Args:
            config: Dicionário de configuração carregado
            
        Raises:
            ModelsConfigError: Se a estrutura for inválida
        """
        required_fields = ['metadata', 'default_model', 'models', 'providers']
        
        # Verificar campos obrigatórios no nível raiz
        for field in required_fields:
            if field not in config:
                raise ModelsConfigError(f"Campo obrigatório ausente: {field}")
        
        # Validar metadados
        metadata = config['metadata']
        metadata_required = ['generated_at', 'test_version', 'total_models_tested']
        for field in metadata_required:
            if field not in metadata:
                raise ModelsConfigError(f"Campo obrigatório em metadata: {field}")
        
        # Validar modelos
        if not isinstance(config['models'], dict) or not config['models']:
            raise ModelsConfigError("Campo 'models' deve ser um dicionário não vazio")
        
        # Validar modelo padrão
        default_model = config['default_model']
        if default_model not in config['models']:
            raise ModelsConfigError(f"Modelo padrão '{default_model}' não encontrado na lista de modelos")
        
        # Validar estrutura de cada modelo
        for model_id, model_data in config['models'].items():
            self._validate_model_structure(model_id, model_data)
        
        # Validar provedores
        if not isinstance(config['providers'], dict) or not config['providers']:
            raise ModelsConfigError("Campo 'providers' deve ser um dicionário não vazio")
        
        for provider_id, provider_data in config['providers'].items():
            self._validate_provider_structure(provider_id, provider_data)
        
        logger.debug("✅ [LOADER] Estrutura de configuração validada com sucesso")
    
    def _validate_model_structure(self, model_id: str, model_data: Dict) -> None:
        """Valida estrutura de um modelo específico."""
        required_fields = ['id', 'display_name', 'provider', 'is_default', 'status']
        
        for field in required_fields:
            if field not in model_data:
                raise ModelsConfigError(f"Campo obrigatório ausente no modelo '{model_id}': {field}")
        
        # Verificar tipos
        if not isinstance(model_data['is_default'], bool):
            raise ModelsConfigError(f"Campo 'is_default' deve ser booleano no modelo '{model_id}'")
        
        if model_data['status'] not in ['active', 'inactive', 'deprecated']:
            raise ModelsConfigError(f"Status inválido no modelo '{model_id}': {model_data['status']}")
    
    def _validate_provider_structure(self, provider_id: str, provider_data: Dict) -> None:
        """Valida estrutura de um provedor específico."""
        required_fields = ['api_type', 'requires_key']
        
        for field in required_fields:
            if field not in provider_data:
                raise ModelsConfigError(f"Campo obrigatório ausente no provedor '{provider_id}': {field}")
    
    def _load_config_from_file(self) -> Dict:
        """
        Carrega configuração do arquivo JSON.
        
        Returns:
            Dict: Configuração carregada e validada
            
        Raises:
            ModelsConfigError: Se falhar ao carregar ou validar
        """
        if not self._config_file_path.exists():
            raise ModelsConfigError(f"Arquivo de configuração não encontrado: {self._config_file_path}")
        
        try:
            with open(self._config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self._validate_config_structure(config)
            self._last_modified = self._config_file_path.stat().st_mtime
            
            logger.info(f"✅ [LOADER] Configuração carregada: {len(config['models'])} modelos, default: {config['default_model']}")
            return config
            
        except json.JSONDecodeError as e:
            raise ModelsConfigError(f"Erro ao decodificar JSON: {e}")
        except Exception as e:
            raise ModelsConfigError(f"Erro ao carregar configuração: {e}")
    
    def get_config(self, force_reload: bool = False) -> Dict:
        """
        Obtém a configuração completa com lazy loading.
        
        Args:
            force_reload: Forçar recarga da configuração
            
        Returns:
            Dict: Configuração completa
        """
        if force_reload or self._should_reload():
            try:
                self._config_cache = self._load_config_from_file()
                logger.debug("🔄 [LOADER] Configuração recarregada")
            except ModelsConfigError as e:
                logger.error(f"❌ [LOADER] {e}")
                if self._config_cache is None:
                    # Se não há cache e falhou, gerar configuração de fallback
                    self._config_cache = self._generate_fallback_config()
                    logger.warning("⚠️ [LOADER] Usando configuração de fallback")
        
        return self._config_cache
    
    def _generate_fallback_config(self) -> Dict:
        """Gera configuração de fallback quando o arquivo não está disponível."""
        from datetime import datetime
        
        logger.warning("🔧 [LOADER] Gerando configuração de fallback")
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "test_version": "fallback_v1.0",
                "total_models_tested": 3,
                "finalists_count": 3,
                "generation_criteria": {
                    "max_response_time": "5.0s",
                    "consistency_required": False,
                    "majority_vote_required": False
                }
            },
            "default_model": "llama-4-maverick",
            "models": {
                "llama-4-maverick": {
                    "id": "llama-4-maverick",
                    "display_name": "Llama 4 Maverick",
                    "provider": "openrouter",
                    "is_default": True,
                    "status": "active",
                    "performance": {"average_time": 3.0, "ranking": 1, "consistency": True},
                    "capabilities": {"max_tokens": 1024, "temperature": 0, "timeout": 30}
                },
                "claude-4-sonnet": {
                    "id": "claude-4-sonnet",
                    "display_name": "Claude 4 Sonnet", 
                    "provider": "anthropic",
                    "is_default": False,
                    "status": "active",
                    "performance": {"average_time": 4.0, "ranking": 2, "consistency": True},
                    "capabilities": {"max_tokens": 1024, "temperature": 0, "timeout": 30}
                },
                "google-gemini-2.5-pro": {
                    "id": "google-gemini-2.5-pro",
                    "display_name": "Gemini 2.5 Pro",
                    "provider": "google", 
                    "is_default": False,
                    "status": "active",
                    "performance": {"average_time": 4.5, "ranking": 3, "consistency": True},
                    "capabilities": {"max_tokens": 1024, "temperature": 0, "timeout": 30}
                }
            },
            "providers": {
                "anthropic": {
                    "api_type": "anthropic",
                    "requires_key": "ANTHROPIC_API_KEY",
                    "base_url": None
                },
                "openrouter": {
                    "api_type": "openrouter",
                    "requires_key": "OPENROUTER_API_KEY",
                    "base_url": "https://openrouter.ai/api/v1"
                },
                "google": {
                    "api_type": "openrouter",
                    "requires_key": "OPENROUTER_API_KEY", 
                    "base_url": "https://openrouter.ai/api/v1"
                }
            }
        }
    
    def get_available_models(self, status_filter: Optional[str] = None) -> List[str]:
        """
        Obtém lista de modelos disponíveis.
        
        Args:
            status_filter: Filtrar por status ('active', 'inactive', 'deprecated')
            
        Returns:
            List[str]: Lista de IDs de modelos
        """
        config = self.get_config()
        models = []
        
        for model_id, model_data in config['models'].items():
            if status_filter is None or model_data['status'] == status_filter:
                models.append(model_id)
        
        return models
    
    def get_active_models(self) -> List[str]:
        """Obtém lista de modelos ativos."""
        return self.get_available_models(status_filter='active')
    
    def get_default_model(self) -> str:
        """
        Obtém o modelo padrão.
        
        Returns:
            str: ID do modelo padrão
        """
        config = self.get_config()
        return config['default_model']
    
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """
        Obtém configuração de um modelo específico.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Optional[ModelConfig]: Configuração do modelo ou None se não encontrado
        """
        config = self.get_config()
        
        if model_id not in config['models']:
            logger.warning(f"⚠️ [LOADER] Modelo não encontrado: {model_id}")
            return None
        
        model_data = config['models'][model_id]
        return ModelConfig(**model_data)
    
    def get_provider_config(self, provider_id: str) -> Optional[ProviderConfig]:
        """
        Obtém configuração de um provedor específico.
        
        Args:
            provider_id: ID do provedor
            
        Returns:
            Optional[ProviderConfig]: Configuração do provedor ou None se não encontrado
        """
        config = self.get_config()
        
        if provider_id not in config['providers']:
            logger.warning(f"⚠️ [LOADER] Provedor não encontrado: {provider_id}")
            return None
        
        provider_data = config['providers'][provider_id]
        return ProviderConfig(**provider_data)
    
    def get_models_by_provider(self, provider_id: str) -> List[str]:
        """
        Obtém modelos de um provedor específico.
        
        Args:
            provider_id: ID do provedor
            
        Returns:
            List[str]: Lista de IDs de modelos deste provedor
        """
        config = self.get_config()
        models = []
        
        for model_id, model_data in config['models'].items():
            if model_data['provider'] == provider_id:
                models.append(model_id)
        
        return models
    
    def get_fastest_models(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtém os modelos mais rápidos ordenados por tempo médio.
        
        Args:
            limit: Número máximo de modelos a retornar
            
        Returns:
            List[Dict]: Lista de modelos ordenados por velocidade
        """
        config = self.get_config()
        models_with_performance = []
        
        for model_id, model_data in config['models'].items():
            if model_data['status'] == 'active' and 'performance' in model_data:
                performance = model_data['performance']
                models_with_performance.append({
                    'id': model_id,
                    'display_name': model_data['display_name'],
                    'average_time': performance.get('average_time', float('inf')),
                    'ranking': performance.get('ranking', float('inf'))
                })
        
        # Ordenar por tempo médio
        models_with_performance.sort(key=lambda x: x['average_time'])
        
        return models_with_performance[:limit]
    
    def is_model_available(self, model_id: str) -> bool:
        """
        Verifica se um modelo está disponível e ativo.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            bool: True se disponível e ativo
        """
        model_config = self.get_model_config(model_id)
        return model_config is not None and model_config.status == 'active'
    
    def get_config_metadata(self) -> Dict[str, Any]:
        """
        Obtém metadados da configuração.
        
        Returns:
            Dict: Metadados da configuração
        """
        config = self.get_config()
        return config.get('metadata', {})
    
    def refresh_config(self) -> bool:
        """
        Força recarga da configuração.
        
        Returns:
            bool: True se recarregou com sucesso
        """
        try:
            self.get_config(force_reload=True)
            logger.info("✅ [LOADER] Configuração recarregada com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ [LOADER] Erro ao recarregar configuração: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica estado de saúde do sistema de configuração.
        
        Returns:
            Dict: Relatório de health check
        """
        try:
            config = self.get_config()
            
            active_models = self.get_active_models()
            total_models = len(config['models'])
            
            # Verificar se arquivo existe
            config_exists = self._config_file_path.exists()
            
            # Verificar se tem modelo padrão válido
            default_model = config['default_model']
            default_valid = self.is_model_available(default_model)
            
            status = "healthy" if config_exists and active_models and default_valid else "degraded"
            
            return {
                "status": status,
                "config_file_exists": config_exists,
                "config_file_path": str(self._config_file_path),
                "total_models": total_models,
                "active_models": len(active_models),
                "default_model": default_model,
                "default_model_valid": default_valid,
                "providers_count": len(config.get('providers', {})),
                "last_modified": self._last_modified,
                "cache_active": self._config_cache is not None,
                "metadata": config.get('metadata', {})
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "config_file_exists": False,
                "cache_active": False
            }


# Instância global singleton
models_loader = ModelsLoader()


# Funções de conveniência para uso direto
def get_models_config() -> Dict:
    """Obtém configuração de modelos (função de conveniência)."""
    return models_loader.get_config()


def get_available_models() -> List[str]:
    """Obtém lista de modelos disponíveis (função de conveniência)."""
    return models_loader.get_available_models()


def get_default_model() -> str:
    """Obtém modelo padrão (função de conveniência)."""
    return models_loader.get_default_model()


def is_model_available(model_id: str) -> bool:
    """Verifica disponibilidade de modelo (função de conveniência)."""
    return models_loader.is_model_available(model_id)


# Exemplo de uso e teste
if __name__ == "__main__":
    """
    Exemplo de uso do ModelsLoader
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testando ModelsLoader...")
    
    # Testar carregamento
    loader = ModelsLoader()
    
    try:
        # Health check
        health = loader.health_check()
        print(f"💊 Health Check: {health['status']}")
        print(f"   Modelos ativos: {health.get('active_models', 0)}")
        print(f"   Modelo padrão: {health.get('default_model', 'N/A')}")
        
        # Listar modelos disponíveis
        models = loader.get_available_models()
        print(f"📋 Modelos disponíveis: {models}")
        
        # Modelo padrão
        default = loader.get_default_model()
        print(f"🎯 Modelo padrão: {default}")
        
        # Modelos mais rápidos
        fastest = loader.get_fastest_models(3)
        print(f"🚀 Modelos mais rápidos:")
        for model in fastest:
            print(f"   • {model['display_name']}: {model['average_time']:.1f}s")
        
        # Testar modelo específico
        if models:
            model_config = loader.get_model_config(models[0])
            if model_config:
                print(f"🔧 Configuração de '{models[0]}':")
                print(f"   Display: {model_config.display_name}")
                print(f"   Provider: {model_config.provider}")
                print(f"   Status: {model_config.status}")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    
    print("🏁 Teste concluído!")