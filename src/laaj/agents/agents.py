"""
Módulo agents simplificado para o sistema LLM as Judge.
Agora trabalha APENAS com respostas pré-geradas, removida toda lógica de geração.
"""

from langsmith import Client
import os
from laaj.config import PROMPT_LAAJ

def chain_laaj(llm):
    """
    Cria chain do judge usando prompt do LangSmith.
    Esta é a única chain necessária no novo escopo - para avaliar respostas pré-geradas.
    
    Args:
        llm: Instância do modelo LLM que será usado como judge
        
    Returns:
        Chain configurada com o prompt 'laaj-prompt' do LangSmith
    """
    langsmith_client = Client()  # permite fallback para variáveis de ambiente suportadas
    try:
        prompt = langsmith_client.pull_prompt(PROMPT_LAAJ)
    except Exception as e:
        raise RuntimeError(
            f"Falha ao carregar o prompt '{PROMPT_LAAJ}' no LangSmith. "
            "Verifique as variáveis LANGSMITH_API_KEY/LANGCHAIN_API_KEY, permissões do projeto "
            "e se o prompt existe e está acessível."
        ) from e
    chain = prompt | llm
    return chain
    

if __name__ == "__main__":
    import asyncio
    from laaj.agents.llms import get_llm_llama_4_maverick
    
    async def test_judge_scenarios():
        print("🧪 Testando LLM as Judge com cenários óbvios...")
        
        llm = get_llm_llama_4_maverick()
        chain = chain_laaj(llm)
        
        # Teste 1: Resposta A claramente melhor (mais completa e precisa)
        print("\n" + "="*60)
        print("🎯 TESTE 1 - Resposta A deve vencer (muito melhor)")
        print("="*60)
        
        input_data_1 = {
            "question": "Explique como funciona a fotossíntese.",
            "answer_a": "A fotossíntese é um processo bioquímico fundamental realizado por plantas, algas e algumas bactérias, no qual a energia luminosa (principalmente solar) é convertida em energia química. Durante este processo, o dióxido de carbono (CO₂) do ar e a água (H₂O) absorvida pelas raízes são transformados em glicose (C₆H₁₂O₆) e oxigênio (O₂), utilizando a clorofila como catalisador. A equação química geral é: 6CO₂ + 6H₂O + energia luminosa → C₆H₁₂O₆ + 6O₂. Este processo ocorre principalmente nos cloroplastos das células vegetais e é vital para a vida na Terra, pois produz o oxigênio que respiramos e serve como base da cadeia alimentar.",
            "answer_b": "Fotossíntese é quando plantas fazem comida com sol."
        }
        
        print("🔍 Invocando modelo para Teste 1...")
        response_1 = await chain.ainvoke(input_data_1)
        print("📝 Resposta Teste 1:")
        print(f"Tipo: {type(response_1)}")
        print(f"Conteúdo: {response_1}")
        print(f"Resultado esperado: Resposta A (mais completa e científica)")
        
        # Teste 2: Resposta B claramente melhor (mais precisa e atualizada)
        print("\n" + "="*60)
        print("🎯 TESTE 2 - Resposta B deve vencer (muito melhor)")
        print("="*60)
        
        input_data_2 = {
            "question": "Quando foi fundada a cidade de Brasília?",
            "answer_a": "Brasília foi fundada em 1950.",
            "answer_b": "Brasília foi inaugurada em 21 de abril de 1960, sendo construída durante o governo de Juscelino Kubitschek como parte de seu plano de metas '50 anos em 5'. A cidade foi planejada pelo urbanista Lúcio Costa e teve sua arquitetura projetada por Oscar Niemeyer. Foi criada para ser a nova capital do Brasil, transferindo o centro político do Rio de Janeiro para o interior do país."
        }
        
        print("🔍 Invocando modelo para Teste 2...")
        response_2 = await chain.ainvoke(input_data_2)
        print("📝 Resposta Teste 2:")
        print(f"Tipo: {type(response_2)}")
        print(f"Conteúdo: {response_2}")
        print(f"Resultado esperado: Resposta B (correta, completa e informativa)")
        
        # Teste 3: Ambas as respostas igualmente erradas (deve dar empate)
        print("\n" + "="*60)
        print("🎯 TESTE 3 - Deve dar Empate (ambas erradas)")
        print("="*60)
        
        input_data_3 = {
            "question": "Qual é a capital da França?",
            "answer_a": "A capital da França é Londres.",
            "answer_b": "A capital da França é Madrid."
        }
        
        print("🔍 Invocando modelo para Teste 3...")
        response_3 = await chain.ainvoke(input_data_3)
        print("📝 Resposta Teste 3:")
        print(f"Tipo: {type(response_3)}")
        print(f"Conteúdo: {response_3}")
        print(f"Resultado esperado: Empate (ambas incorretas)")
        
        # Resumo dos testes
        print("\n" + "="*60)
        print("📊 RESUMO DOS TESTES")
        print("="*60)
        print("Teste 1 - Fotossíntese:")
        print(f"  Resultado: {response_1}")
        print(f"  Esperado: A (resposta científica completa)")
        print()
        print("Teste 2 - Brasília:")
        print(f"  Resultado: {response_2}")
        print(f"  Esperado: B (data correta e informações completas)")
        print()
        print("Teste 3 - Capital França:")
        print(f"  Resultado: {response_3}")
        print(f"  Esperado: Empate (ambas incorretas)")
    
    # Executar testes assíncronos
    asyncio.run(test_judge_scenarios())