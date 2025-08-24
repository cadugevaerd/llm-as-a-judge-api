"""
Teste de compatibilidade de modelos OpenRouter com o sistema de judge.
Verifica quais modelos retornam JSON estruturado corretamente.
"""

import asyncio
import json
import os
import sys
from typing import Dict, List, Tuple
from langchain_openai import ChatOpenAI
from langsmith import Client

# Adicionar src ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from laaj.config import PROMPT_LAAJ
import laaj.config as config


# Lista de modelos OpenRouter para testar
MODELS_TO_TEST = [
    "anthropic/claude-sonnet-4",
    "google/gemini-2.5-pro", 
    "openai/gpt-5",
    "openai/gpt-oss-120b",
    "meta-llama/llama-4-maverick",
    "qwen/qwq-32b",
    "deepseek/deepseek-chat-v3.1",
    "mistralai/mistral-medium-3.1",
    "x-ai/grok-4",
    "google/gemma-3-27b-it"
]

# Dados de teste padrão
TEST_INPUT = {
    "question": "Qual a melhor explicação sobre fotossíntese?",
    "answer_a": "Fotossíntese é um processo onde plantas fazem comida usando luz solar.",
    "answer_b": "A fotossíntese é o processo bioquímico pelo qual organismos fotossintetizantes, como plantas, algas e algumas bactérias, convertem energia luminosa (principalmente solar) em energia química. Durante esse processo, dióxido de carbono (CO2) e água (H2O) são convertidos em glicose (C6H12O6) e oxigênio (O2), utilizando a clorofila como catalisador. A equação geral é: 6CO2 + 6H2O + energia luminosa → C6H12O6 + 6O2. Este processo ocorre principalmente nos cloroplastos das células vegetais e é fundamental para a vida na Terra, pois produz oxigênio e serve como base da cadeia alimentar."
}

def create_llm_for_model(model_name: str) -> ChatOpenAI:
    """Cria instância LLM para um modelo específico."""
    return ChatOpenAI(
        model=model_name,
        api_key=config.OPENROUTER_API,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.1,  # Baixa temperatura para consistência
        timeout=30
    )

def create_judge_chain(llm):
    """Cria chain do judge usando prompt do LangSmith."""
    try:
        langsmith_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        prompt = langsmith_client.pull_prompt(PROMPT_LAAJ)
        chain = prompt | llm
        return chain
    except Exception as e:
        print(f"❌ Erro ao criar chain: {e}")
        return None

def is_valid_json_response(response) -> Tuple[bool, str]:
    """
    Verifica se a resposta é um JSON estruturado válido com campo 'Preference'.
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Verificar se é dict com campo Preference
        if isinstance(response, dict) and "Preference" in response:
            preference = response["Preference"]
            
            # Verificar se Preference é 1, 2 ou outro valor válido
            if preference in [1, 2, "1", "2"]:
                reasoning = response.get("Reasoning", response.get("reasoning", ""))
                return True, f"✅ JSON válido - Preference: {preference}, Reasoning: {len(str(reasoning))} chars"
            else:
                return False, f"❌ Preference inválido: {preference}"
        else:
            # Tentar converter string para JSON se necessário
            if hasattr(response, 'content'):
                response_text = response.content
            elif isinstance(response, str):
                response_text = response
            else:
                response_text = str(response)
            
            # Tentar fazer parsing de JSON da string
            try:
                parsed = json.loads(response_text)
                if isinstance(parsed, dict) and "Preference" in parsed:
                    preference = parsed["Preference"]
                    if preference in [1, 2, "1", "2"]:
                        reasoning = parsed.get("Reasoning", parsed.get("reasoning", ""))
                        return True, f"✅ JSON parseado válido - Preference: {preference}, Reasoning: {len(str(reasoning))} chars"
                    else:
                        return False, f"❌ Preference inválido: {preference}"
            except json.JSONDecodeError:
                pass
            
            return False, f"❌ Não é JSON estruturado: {str(response)[:100]}..."
                
    except Exception as e:
        return False, f"❌ Erro na validação: {str(e)}"

async def test_single_model(model_name: str) -> Dict:
    """
    Testa um modelo específico.
    
    Returns:
        Dict com resultado do teste
    """
    print(f"🧪 Testando modelo: {model_name}")
    
    result = {
        "model": model_name,
        "success": False,
        "error": None,
        "response_preview": None,
        "validation_message": None,
        "execution_time": 0
    }
    
    try:
        import time
        start_time = time.time()
        
        # Criar LLM e chain
        llm = create_llm_for_model(model_name)
        chain = create_judge_chain(llm)
        
        if not chain:
            result["error"] = "Falha ao criar chain"
            return result
        
        # Executar teste
        print(f"  ⚙️ Executando comparação...")
        response = await chain.ainvoke(TEST_INPUT)
        
        result["execution_time"] = time.time() - start_time
        
        # Validar resposta
        is_valid, validation_msg = is_valid_json_response(response)
        result["success"] = is_valid
        result["validation_message"] = validation_msg
        
        # Preview da resposta (primeiros 200 chars)
        response_str = str(response)
        result["response_preview"] = response_str[:200] + "..." if len(response_str) > 200 else response_str
        
        if is_valid:
            print(f"  ✅ PASSOU: {validation_msg}")
        else:
            print(f"  ❌ FALHOU: {validation_msg}")
            
    except Exception as e:
        result["error"] = str(e)
        print(f"  💥 ERRO: {str(e)}")
    
    return result

async def test_all_models() -> List[Dict]:
    """Testa todos os modelos da lista."""
    print(f"🚀 Iniciando teste de {len(MODELS_TO_TEST)} modelos OpenRouter...")
    print("=" * 80)
    
    results = []
    
    for model_name in MODELS_TO_TEST:
        try:
            result = await test_single_model(model_name)
            results.append(result)
            
            # Pequena pausa entre requests para não sobrecarregar API
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"💥 Erro crítico no modelo {model_name}: {e}")
            results.append({
                "model": model_name,
                "success": False,
                "error": f"Erro crítico: {str(e)}",
                "response_preview": None,
                "validation_message": None,
                "execution_time": 0
            })
    
    return results

def generate_report(results: List[Dict]):
    """Gera relatório final dos testes."""
    successful_models = [r for r in results if r["success"]]
    failed_models = [r for r in results if not r["success"]]
    
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO FINAL - COMPATIBILIDADE DE MODELOS JUDGE")
    print("=" * 80)
    
    print(f"\n✅ MODELOS APTOS ({len(successful_models)}/{len(results)}):")
    print("-" * 50)
    
    if successful_models:
        for result in successful_models:
            exec_time = f"{result['execution_time']:.1f}s"
            print(f"  🟢 {result['model']} ({exec_time})")
            print(f"     {result['validation_message']}")
    else:
        print("  Nenhum modelo passou no teste ❌")
    
    print(f"\n❌ MODELOS NÃO APTOS ({len(failed_models)}/{len(results)}):")
    print("-" * 50)
    
    if failed_models:
        for result in failed_models:
            error_msg = result['error'] or result['validation_message'] or "Erro desconhecido"
            print(f"  🔴 {result['model']}")
            print(f"     Motivo: {error_msg}")
    
    print(f"\n📈 RESUMO ESTATÍSTICO:")
    print(f"  • Total testado: {len(results)}")
    print(f"  • Taxa de sucesso: {len(successful_models)/len(results)*100:.1f}%")
    
    if successful_models:
        avg_time = sum(r['execution_time'] for r in successful_models) / len(successful_models)
        print(f"  • Tempo médio execução: {avg_time:.1f}s")
    
    print("\n🎯 RECOMENDAÇÕES:")
    if successful_models:
        fastest = min(successful_models, key=lambda x: x['execution_time'])
        print(f"  • Modelo mais rápido: {fastest['model']} ({fastest['execution_time']:.1f}s)")
        
        recommended = [r for r in successful_models if 'claude' in r['model'].lower() or 'gpt' in r['model'].lower()]
        if recommended:
            print(f"  • Modelos premium recomendados: {', '.join([r['model'] for r in recommended])}")

async def main():
    """Função principal do teste."""
    print("🔧 Verificando configuração...")
    
    # Verificar API keys
    if not config.OPENROUTER_API:
        print("❌ OPENROUTER_API_KEY não configurado!")
        return
    
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️ LANGSMITH_API_KEY não configurado - tentando continuar...")
    
    print("✅ Configuração OK\n")
    
    # Executar testes
    results = await test_all_models()
    
    # Gerar relatório
    generate_report(results)
    
    # Salvar resultados detalhados
    output_file = "judge_models_test_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados detalhados salvos em: {output_file}")
    except Exception as e:
        print(f"⚠️ Erro ao salvar resultados: {e}")

if __name__ == "__main__":
    asyncio.run(main())