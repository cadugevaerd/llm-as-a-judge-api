"""
Factory Pattern para criação de instâncias LLM

O Factory Pattern é um padrão de design que fornece uma interface para criar 
objetos sem especificar suas classes concretas. Em vez de instanciar objetos 
diretamente no código, delegamos essa responsabilidade para uma "fábrica".

Vantagens:
- Centraliza a lógica de criação em um só lugar
- Facilita a adição de novos modelos
- Reduz duplicação de código
- Torna o código mais testável e manutenível
"""

import logging
from typing import Callable, Dict, List
from langchain_openai import ChatOpenAI

from laaj.agents.llms import (
    get_llm_anthropic_claude_4_sonnet,
    get_llm_google_gemini_pro, 
    get_llm_gpt_5,
    get_llm_qwen_3_instruct,
    get_llm_deepseek,
    get_llm_llama_4_maverick
)
from laaj.config import LITERAL_MODELS

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory (Fábrica) para criar instâncias de Large Language Models (LLMs)
    
    Este padrão resolve o problema de ter múltiplos if/elif espalhados pelo código
    para decidir qual modelo LLM instanciar. Em vez disso, centralizamos toda essa
    lógica em uma única classe.
    
    Como funciona:
    1. Mantemos um dicionário que mapeia nomes de modelos para suas funções criadoras
    2. Quando solicitado, consultamos o dicionário e chamamos a função apropriada
    3. Se o modelo não existe, lançamos uma exceção informativa
    """
    
    # Dicionário que mapeia nomes de modelos para suas funções de criação
    # Tipo: Dict[str, Callable[[], ChatOpenAI]]
    # - str: nome do modelo (ex: "claude-4-sonnet")  
    # - Callable[[], ChatOpenAI]: função que não recebe parâmetros e retorna ChatOpenAI
    _models: Dict[str, Callable[[], ChatOpenAI]] = {
        # Modelo Llama 4 Maverick - Principal (melhor performance no teste)
        "llama-4-maverick": get_llm_llama_4_maverick,
        
        # Modelo Claude 4 Sonnet da Anthropic
        "claude-4-sonnet": get_llm_anthropic_claude_4_sonnet,
        
        # Modelo Google Gemini 2.5 Pro
        "google-gemini-2.5-pro": get_llm_google_gemini_pro,
        
        # Modelo GPT-5 (através do OpenRouter)
        "gpt-5": get_llm_gpt_5,
        
        # Modelo Qwen 3 Instruct
        "qwen-3-instruct": get_llm_qwen_3_instruct,
        
        # Modelo DeepSeek
        "deepseek": get_llm_deepseek
    }
    
    @classmethod
    def create_llm(cls, model_name: str) -> ChatOpenAI:
        """
        Método principal da Factory - cria uma instância do LLM solicitado
        
        Args:
            model_name (str): Nome do modelo a ser criado (ex: "claude-4-sonnet")
            
        Returns:
            ChatOpenAI: Instância configurada do modelo solicitado
            
        Raises:
            ValueError: Se o modelo solicitado não estiver disponível
            
        Exemplo:
            llm = LLMFactory.create_llm("claude-4-sonnet")
        """
        
        # Validação: verifica se o modelo existe no nosso registro
        if model_name not in cls._models:
            # Se não existe, cria uma lista dos modelos disponíveis para ajudar o usuário
            available_models = ", ".join(cls._models.keys())
            error_msg = f"Modelo '{model_name}' não encontrado. Disponíveis: {available_models}"
            
            logger.error(f"❌ [FACTORY] {error_msg}")
            raise ValueError(error_msg)
        
        # Log informativo sobre qual modelo está sendo criado
        logger.info(f"🏭 [FACTORY] Criando instância do modelo: {model_name}")
        
        # Busca a função criadora no dicionário e a executa
        # cls._models[model_name] retorna a função (ex: get_llm_anthropic_claude_4_sonnet)
        # () no final executa a função, retornando a instância do ChatOpenAI
        model_instance = cls._models[model_name]()
        
        logger.info(f"✅ [FACTORY] Modelo {model_name} criado com sucesso")
        return model_instance
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """
        Retorna lista de todos os modelos disponíveis na factory
        
        Útil para:
        - Validações
        - Documentação dinâmica  
        - Interfaces de usuário
        - Testes
        
        Returns:
            List[str]: Lista com nomes de todos os modelos disponíveis
            
        Exemplo:
            models = LLMFactory.get_available_models()
            # ['claude-4-sonnet', 'google-gemini-2.5-pro', 'gpt-5', 'qwen-3-instruct']
        """
        return list(cls._models.keys())
    
    @classmethod
    def is_model_supported(cls, model_name: str) -> bool:
        """
        Verifica se um modelo é suportado sem tentar criá-lo
        
        Útil para validações prévias antes de chamar create_llm()
        
        Args:
            model_name (str): Nome do modelo a verificar
            
        Returns:
            bool: True se o modelo é suportado, False caso contrário
            
        Exemplo:
            if LLMFactory.is_model_supported("claude-4-sonnet"):
                llm = LLMFactory.create_llm("claude-4-sonnet")
        """
        return model_name in cls._models
    
    @classmethod
    def register_model(cls, model_name: str, creator_function: Callable[[], ChatOpenAI]) -> None:
        """
        Adiciona um novo modelo à factory dinamicamente
        
        Permite extensibilidade - novos modelos podem ser adicionados em runtime
        
        Args:
            model_name (str): Nome identificador do modelo
            creator_function (Callable): Função que cria instância do modelo
            
        Exemplo:
            def get_my_custom_llm():
                return ChatOpenAI(model="custom-model")
                
            LLMFactory.register_model("my-custom", get_my_custom_llm)
        """
        if model_name in cls._models:
            logger.warning(f"⚠️ [FACTORY] Sobrescrevendo modelo existente: {model_name}")
        
        cls._models[model_name] = creator_function
        logger.info(f"📝 [FACTORY] Modelo '{model_name}' registrado na factory")
    
    @classmethod
    def validate_config_models(cls) -> bool:
        """
        Valida se todos os modelos em LITERAL_MODELS estão disponíveis na factory
        
        Útil para verificar consistência entre configuração e implementação
        
        Returns:
            bool: True se todos os modelos da config estão implementados
        """
        config_models = set(LITERAL_MODELS)  # Converte para set para comparação
        factory_models = set(cls._models.keys())
        
        # Modelos que estão na config mas não na factory
        missing_in_factory = config_models - factory_models
        
        # Modelos que estão na factory mas não na config  
        extra_in_factory = factory_models - config_models
        
        if missing_in_factory:
            logger.error(f"❌ [FACTORY] Modelos na config mas não na factory: {missing_in_factory}")
            
        if extra_in_factory:
            logger.warning(f"⚠️ [FACTORY] Modelos na factory mas não na config: {extra_in_factory}")
            
        is_valid = len(missing_in_factory) == 0
        
        if is_valid:
            logger.info(f"✅ [FACTORY] Validação OK - todos os modelos da config estão implementados")
        
        return is_valid


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
    
    # 5. Validar consistência com config
    LLMFactory.validate_config_models()
    
    print("🏁 Teste concluído!")