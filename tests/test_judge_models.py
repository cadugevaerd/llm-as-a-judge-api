"""
Teste de compatibilidade de modelos OpenRouter com o sistema de judge.
Verifica quais modelos retornam JSON estruturado corretamente.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_mistralai.chat_models import ChatMistralAI
from langsmith import Client

# Adicionar src ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from laaj.config import PROMPT_LAAJ
import laaj.config as config


# Lista de modelos OpenRouter para testar
MODELS_TO_TEST = [
    "claude-sonnet-4-0",
    "claude-3-5-haiku-latest",
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-flash-lite",
    "google/gemma-3-27b-it",
    "openai/gpt-5",
    "openai/gpt-5-mini",
    "openai/gpt-5-nano",
    "openai/gpt-oss-120b",
    # "meta-llama/llama-4-maverick",
    # "qwen/qwq-32b",
    "qwen/qwen3-235b-a22b-2507",
    "deepseek/deepseek-chat-v3.1",
    "mistral-large-latest",
    "mistral-medium-latest",
    "mistral-small-latest",
    "x-ai/grok-4",
    "moonshotai/kimi-k2"
]

# Dados de teste - Rodada 1 (Complexidade Média)
TEST_INPUT_ROUND_1 = {
    "question": "Qual a melhor explicação sobre fotossíntese?",
    "answer_a": "Fotossíntese é um processo onde plantas fazem comida usando luz solar.",
    "answer_b": "A fotossíntese é o processo bioquímico pelo qual organismos fotossintetizantes, como plantas, algas e algumas bactérias, convertem energia luminosa (principalmente solar) em energia química. Durante esse processo, dióxido de carbono (CO2) e água (H2O) são convertidos em glicose (C6H12O6) e oxigênio (O2), utilizando a clorofila como catalisador. A equação geral é: 6CO2 + 6H2O + energia luminosa → C6H12O6 + 6O2. Este processo ocorre principalmente nos cloroplastos das células vegetais e é fundamental para a vida na Terra, pois produz oxigênio e serve como base da cadeia alimentar."
}

# Dados de teste - Rodada 2 (Complexidade Alta)
TEST_INPUT_ROUND_2 = {
    "question": "Compare as abordagens de inteligência artificial: aprendizado supervisionado vs não supervisionado vs por reforço, considerando vantagens, limitações, aplicações práticas e recursos computacionais necessários.",
    "answer_a": "Aprendizado supervisionado usa dados rotulados para treinar modelos. Não supervisionado encontra padrões em dados sem rótulos. Por reforço aprende através de recompensas. Cada um tem suas aplicações específicas.",
    "answer_b": "O aprendizado supervisionado utiliza datasets rotulados para treinar algoritmos preditivos, sendo eficaz para classificação e regressão, mas requer grandes volumes de dados anotados e pode sofrer overfitting. O não supervisionado identifica estruturas latentes em dados não rotulados através de clustering, redução dimensional e detecção de anomalias, sendo útil para análise exploratória mas com interpretação mais desafiadora. O aprendizado por reforço otimiza políticas através de interação ambiente-agente via sistema de recompensas, destacando-se em jogos e robótica, porém demanda significativo poder computacional e tempo de treinamento. Computacionalmente, supervisionado é mais eficiente, não supervisionado tem complexidade variável, e por reforço é o mais intensivo, exigindo simulações extensivas."
}

def get_anthropic_chat(model_name):
    return ChatAnthropic(
        model=model_name,
        api_key=config.ANTHROPIC_API,
        thinking={
            "type": "disabled"
        },
        temperature=0,
        timeout=5
    )
    
def get_mistralai_chat(model_name):
    return ChatMistralAI(
        model=model_name,
        api_key=config.MISTRAL_API_KEY,
        timeout=5,
        temperature=0,
    )

def create_llm_for_model(model_name: str) -> ChatOpenAI:
    """Cria instância LLM para um modelo específico."""
    
    llms_can_disabled_reasioning = [
        "google/gemma-3-27b-it",
        "google/gemini-2.5-flash",
        "qwen/qwen3-235b-a22b-2507",
    ]
    
    anthropics_llms = [
        "claude-sonnet-4-0",
        "claude-3-5-haiku-latest"
    ]
    
    mistralai_llms = [
        "mistral-large-latest",
        "mistral-medium-latest",
        "mistral-small-latest"
    ]
    
    if model_name in mistralai_llms:
        return get_mistralai_chat(model_name)
    
    elif model_name in anthropics_llms:
        return get_anthropic_chat(model_name)
    else:
        return ChatOpenAI(
            model=model_name,
            api_key=config.OPENROUTER_API,
            base_url="https://openrouter.ai/api/v1",
            temperature=0,  # Baixa temperatura para consistência
            timeout=5,
            extra_body={
                "reasoning": {
                    "enabled": False if model_name in llms_can_disabled_reasioning else True,
                    "effort": "minimal" if model_name not in llms_can_disabled_reasioning else None,
                },
            },
            max_tokens=1024,
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

def is_valid_json_response(response, execution_time: float) -> Tuple[bool, str, int]:
    """
    Verifica se a resposta é um JSON estruturado válido com campo 'Preference' e tempo de resposta aceitável.
    
    Args:
        response: Resposta do modelo para validação
        execution_time: Tempo de execução em segundos
    
    Returns:
        Tuple[bool, str, int]: (is_valid, error_message, preference_vote)
    """
    try:
        preference_vote = 0  # Default para casos de erro
        
        # Verificar tempo de resposta primeiro (máximo 5 segundos)
        if execution_time > 5.0:
            return False, f"❌ Tempo de resposta muito lento: {execution_time:.1f}s (máximo: 5.0s)", 0
        
        # Verificar se é dict com campo Preference
        if isinstance(response, dict) and "Preference" in response:
            preference = response["Preference"]
            
            # Verificar se Preference é 1, 2 ou outro valor válido
            if preference in [1, 2, "1", "2"]:
                preference_vote = int(preference)
                reasoning = response.get("Reasoning", response.get("reasoning", ""))
                return True, f"✅ JSON válido - Preference: {preference}, Reasoning: {len(str(reasoning))} chars", preference_vote
            else:
                return False, f"❌ Preference inválido: {preference}", 0
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
                        preference_vote = int(preference)
                        reasoning = parsed.get("Reasoning", parsed.get("reasoning", ""))
                        return True, f"✅ JSON parseado válido - Preference: {preference}, Reasoning: {len(str(reasoning))} chars", preference_vote
                    else:
                        return False, f"❌ Preference inválido: {preference}", 0
            except json.JSONDecodeError:
                pass
            
            return False, f"❌ Não é JSON estruturado: {str(response)[:100]}...", 0
                
    except Exception as e:
        return False, f"❌ Erro na validação: {str(e)}", 0

async def test_single_model(model_name: str, test_input: Dict, round_name: str = "Rodada") -> Dict:
    """
    Testa um modelo específico com um conjunto de dados.
    
    Args:
        model_name: Nome do modelo para teste
        test_input: Conjunto de dados (TEST_INPUT_ROUND_1 ou TEST_INPUT_ROUND_2)
        round_name: Nome da rodada para logs
    
    Returns:
        Dict com resultado do teste
    """
    print(f"🧪 Testando modelo: {model_name} ({round_name})")
    
    result = {
        "model": model_name,
        "success": False,
        "error": None,
        "response_preview": None,
        "validation_message": None,
        "execution_time": 0,
        "preference": 0,      # Campo: valor da preferência (1 ou 2)
        "vote_for": None      # Campo: "A", "B" ou None
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
        response = await chain.ainvoke(test_input)
        
        result["execution_time"] = time.time() - start_time
        
        # Validar resposta
        is_valid, validation_msg, preference_vote = is_valid_json_response(response, result["execution_time"])
        result["success"] = is_valid
        result["validation_message"] = validation_msg
        result["preference"] = preference_vote
        result["vote_for"] = "A" if preference_vote == 1 else "B" if preference_vote == 2 else None
        
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

async def test_two_rounds() -> List[Dict]:
    """
    Executa sistema de duas rodadas:
    1. Rodada 1: Todos os modelos com pergunta de complexidade média
    2. Rodada 2: Apenas modelos aprovados na rodada 1 com pergunta complexa
    
    Returns:
        List[Dict]: Resultados consolidados das duas rodadas
    """
    print(f"🚀 Iniciando sistema de DUAS RODADAS com {len(MODELS_TO_TEST)} modelos...")
    print("=" * 80)
    
    # ========== RODADA 1 ==========
    print("\n🔵 RODADA 1 - COMPLEXIDADE MÉDIA (Fotossíntese)")
    print("=" * 50)
    
    round1_results = []
    for model_name in MODELS_TO_TEST:
        try:
            result = await test_single_model(model_name, TEST_INPUT_ROUND_1, "Rodada 1")
            round1_results.append(result)
            await asyncio.sleep(1)  # Pausa entre requests
            
        except Exception as e:
            print(f"💥 Erro crítico no modelo {model_name}: {e}")
            round1_results.append({
                "model": model_name,
                "success": False,
                "error": f"Erro crítico: {str(e)}",
                "response_preview": None,
                "validation_message": None,
                "execution_time": 0,
                "preference": 0,
                "vote_for": None
            })
    
    # Analisar votação da Rodada 1 para determinar resposta mais popular
    successful_round1 = [r for r in round1_results if r["success"]]
    
    if not successful_round1:
        print("❌ Nenhum modelo passou na Rodada 1. Interrompendo testes.")
        return consolidate_results(round1_results, [])
    
    # Contar votos da Rodada 1
    votes_a_r1 = [r for r in successful_round1 if r["vote_for"] == "A"]
    votes_b_r1 = [r for r in successful_round1 if r["vote_for"] == "B"]
    
    # Determinar resposta mais votada na Rodada 1
    if len(votes_a_r1) > len(votes_b_r1):
        most_voted_r1 = "A"
        approved_models = [r["model"] for r in votes_a_r1]
        minority_voters = [r["model"] for r in votes_b_r1]
    elif len(votes_b_r1) > len(votes_a_r1):
        most_voted_r1 = "B" 
        approved_models = [r["model"] for r in votes_b_r1]
        minority_voters = [r["model"] for r in votes_a_r1]
    else:
        # Em caso de empate, todos os aprovados passam
        most_voted_r1 = "Empate"
        approved_models = [r["model"] for r in successful_round1]
        minority_voters = []
    
    print(f"\n📊 ANÁLISE RODADA 1:")
    print(f"  • Votos A: {len(votes_a_r1)} ({', '.join([r['model'] for r in votes_a_r1]) if votes_a_r1 else 'nenhum'})")
    print(f"  • Votos B: {len(votes_b_r1)} ({', '.join([r['model'] for r in votes_b_r1]) if votes_b_r1 else 'nenhum'})")
    print(f"  • Resposta mais votada: {most_voted_r1}")
    
    if minority_voters:
        print(f"  • Modelos eliminados (votaram na minoria): {', '.join(minority_voters)}")
    
    print(f"\n✅ {len(approved_models)} modelos qualificados para Rodada 2: {', '.join(approved_models)}")
    
    if not approved_models:
        print("❌ Nenhum modelo qualificado para Rodada 2. Interrompendo testes.")
        return consolidate_results(round1_results, [])
    
    # ========== RODADA 2 ==========
    print(f"\n🟡 RODADA 2 - COMPLEXIDADE ALTA (IA: Supervisionado vs Não-supervisionado vs Reforço)")
    print("=" * 50)
    
    round2_results = []
    for model_name in approved_models:
        try:
            result = await test_single_model(model_name, TEST_INPUT_ROUND_2, "Rodada 2")
            round2_results.append(result)
            await asyncio.sleep(1)  # Pausa entre requests
            
        except Exception as e:
            print(f"💥 Erro crítico no modelo {model_name}: {e}")
            round2_results.append({
                "model": model_name,
                "success": False,
                "error": f"Erro crítico: {str(e)}",
                "response_preview": None,
                "validation_message": None,
                "execution_time": 0,
                "preference": 0,
                "vote_for": None
            })
    
    # Consolidar resultados das duas rodadas
    final_results = consolidate_results(round1_results, round2_results)
    
    return final_results


def consolidate_results(round1_results: List[Dict], round2_results: List[Dict]) -> List[Dict]:
    """
    Consolida resultados das duas rodadas calculando tempo médio e status final.
    
    Args:
        round1_results: Resultados da rodada 1
        round2_results: Resultados da rodada 2
    
    Returns:
        List[Dict]: Resultados consolidados
    """
    consolidated = []
    
    # Criar dicionário para facilitar lookup da rodada 2
    round2_dict = {r["model"]: r for r in round2_results}
    
    for r1 in round1_results:
        model_name = r1["model"]
        r2 = round2_dict.get(model_name)
        
        # Estrutura consolidada
        result = {
            "model": model_name,
            
            # Dados da Rodada 1
            "round_1": {
                "success": r1["success"],
                "execution_time": r1["execution_time"],
                "vote_for": r1["vote_for"],
                "preference": r1["preference"],
                "validation_message": r1["validation_message"],
                "error": r1["error"]
            },
            
            # Dados da Rodada 2 (None se não participou)
            "round_2": {
                "success": r2["success"] if r2 else False,
                "execution_time": r2["execution_time"] if r2 else 0,
                "vote_for": r2["vote_for"] if r2 else None,
                "preference": r2["preference"] if r2 else 0,
                "validation_message": r2["validation_message"] if r2 else "Não participou da Rodada 2",
                "error": r2["error"] if r2 else None
            } if r2 else None,
            
            # Métricas consolidadas
            "final_success": r1["success"] and (r2["success"] if r2 else False),
            "average_time": calculate_average_time(r1, r2),
            "vote_consistency": check_vote_consistency(r1, r2),
            "overall_vote": determine_overall_vote(r1, r2),
            
            # Compatibilidade com código legado
            "success": r1["success"] and (r2["success"] if r2 else False),
            "execution_time": calculate_average_time(r1, r2),
            "vote_for": determine_overall_vote(r1, r2),
            "preference": r1["preference"],  # Usar preferência da rodada 1
            "validation_message": get_consolidated_message(r1, r2)
        }
        
        consolidated.append(result)
    
    return consolidated


def calculate_average_time(r1: Dict, r2: Dict = None) -> float:
    """Calcula tempo médio entre as rodadas."""
    if not r2 or not r2["success"]:
        return r1["execution_time"]
    return (r1["execution_time"] + r2["execution_time"]) / 2


def check_vote_consistency(r1: Dict, r2: Dict = None) -> bool:
    """Verifica se o modelo votou consistentemente nas duas rodadas."""
    if not r2 or not r1["success"] or not r2["success"]:
        return False
    return r1["vote_for"] == r2["vote_for"]


def determine_overall_vote(r1: Dict, r2: Dict = None) -> str:
    """Determina voto consolidado baseado nas duas rodadas."""
    if not r1["success"]:
        return None
    if not r2 or not r2["success"]:
        return r1["vote_for"]
    
    # Se votaram igual nas duas rodadas, usar esse voto
    if r1["vote_for"] == r2["vote_for"]:
        return r1["vote_for"]
    
    # Se votaram diferente, priorizar rodada 2 (mais complexa)
    return r2["vote_for"]


def get_consolidated_message(r1: Dict, r2: Dict = None) -> str:
    """Gera mensagem consolidada do status."""
    if not r1["success"]:
        return f"❌ Falhou na Rodada 1: {r1['validation_message']}"
    
    if not r2:
        return f"⚠️ Eliminado da Rodada 2: Votou na resposta minoritária da Rodada 1"
    
    if not r2["success"]:
        return f"⚠️ Falhou na Rodada 2: {r2['validation_message']}"
    
    consistency = "consistente" if r1["vote_for"] == r2["vote_for"] else "inconsistente"
    return f"✅ Passou em ambas as rodadas (voto {consistency})"

def analyze_voting_results(results: List[Dict]) -> Dict:
    """Analisa resultados de votação e retorna métricas."""
    successful_results = [r for r in results if r["success"]]
    
    if not successful_results:
        return {"error": "Nenhum modelo passou no teste"}
    
    # Contar votos
    votes_a = [r for r in successful_results if r["vote_for"] == "A"]
    votes_b = [r for r in successful_results if r["vote_for"] == "B"]
    
    # Determinar resposta mais votada
    if len(votes_a) > len(votes_b):
        most_voted_response = "A"
        winning_voters = votes_a
    elif len(votes_b) > len(votes_a):
        most_voted_response = "B"
        winning_voters = votes_b
    else:
        most_voted_response = "Empate"
        winning_voters = successful_results
    
    # Encontrar modelo mais rápido entre os vencedores
    if winning_voters:
        fastest_winner = min(winning_voters, key=lambda x: x['execution_time'])
        recommended_model = fastest_winner["model"]
        recommended_time = fastest_winner["execution_time"]
    else:
        recommended_model = None
        recommended_time = 0
    
    return {
        "total_votes": len(successful_results),
        "votes_for_a": len(votes_a),
        "votes_for_b": len(votes_b),
        "most_voted_response": most_voted_response,
        "vote_distribution": f"{len(votes_a)}A-{len(votes_b)}B",
        "recommended_model": recommended_model,
        "recommended_time": recommended_time,
        "winning_voters": [v["model"] for v in winning_voters]
    }

def generate_two_rounds_report(results: List[Dict]):
    """Gera relatório detalhado do sistema de duas rodadas."""
    
    # Separar modelos por status
    finalists = [r for r in results if r["final_success"]]  # Passaram em ambas
    round1_only = [r for r in results if r["round_1"]["success"] and not r["final_success"]]
    failed_round1 = [r for r in results if not r["round_1"]["success"]]
    
    print("\n" + "=" * 90)
    print("📊 RELATÓRIO FINAL - SISTEMA DE DUAS RODADAS")
    print("=" * 90)
    
    # ========== MODELOS FINALISTAS ==========
    print(f"\n🏆 MODELOS FINALISTAS - PASSARAM EM AMBAS AS RODADAS ({len(finalists)}/{len(results)}):")
    print("(Ordenados por velocidade - do mais rápido ao mais lento)")
    print("-" * 70)
    
    if finalists:
        # Ordenar finalistas por tempo médio (do mais rápido ao mais lento)
        finalists_sorted = sorted(finalists, key=lambda x: x['average_time'])
        
        for i, result in enumerate(finalists_sorted, 1):
            avg_time = f"{result['average_time']:.1f}s"
            consistency = "✓" if result['vote_consistency'] else "✗"
            
            # Adicionar posição no ranking
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"  {i}º"
            
            print(f"  {medal} {result['model']} (média: {avg_time}, consistência: {consistency})")
            print(f"     Rodada 1: {result['round_1']['execution_time']:.1f}s → {result['round_1']['vote_for']}")
            print(f"     Rodada 2: {result['round_2']['execution_time']:.1f}s → {result['round_2']['vote_for']}")
            print(f"     Voto final: {result['overall_vote']}")
    else:
        print("  Nenhum modelo passou em ambas as rodadas ❌")
    
    # ========== ANÁLISE DE VOTAÇÃO DOS FINALISTAS ==========
    if finalists:
        voting_analysis = analyze_voting_results(finalists)
        
        if not voting_analysis.get("error"):
            print(f"\n🗳️ ANÁLISE DE VOTAÇÃO DOS FINALISTAS:")
            print("-" * 50)
            print(f"  • Total de finalistas: {voting_analysis['total_votes']}")
            print(f"  • Distribuição final: {voting_analysis['vote_distribution']}")
            print(f"  • Resposta mais votada: {voting_analysis['most_voted_response']}")
            
            # Consistência de votos
            consistent_voters = [r for r in finalists if r["vote_consistency"]]
            inconsistent_voters = [r for r in finalists if not r["vote_consistency"]]
            
            print(f"  • Modelos consistentes: {len(consistent_voters)}/{len(finalists)}")
            if consistent_voters:
                print(f"    → {', '.join([r['model'] for r in consistent_voters])}")
            if inconsistent_voters:
                print(f"  • Modelos inconsistentes: {', '.join([r['model'] for r in inconsistent_voters])}")
            
            if voting_analysis["recommended_model"]:
                print(f"\n🏆 RECOMENDAÇÃO FINAL:")
                print(f"  • Modelo recomendado: {voting_analysis['recommended_model']}")
                print(f"  • Tempo médio: {voting_analysis['recommended_time']:.1f}s")
                print(f"  • Critério: Mais rápido entre finalistas que votaram na resposta mais popular")
                print(f"  • Finalistas concordantes: {', '.join(voting_analysis['winning_voters'])}")
    
    # ========== MODELOS QUE PASSARAM APENAS NA RODADA 1 ==========
    print(f"\n⚠️ MODELOS QUE PASSARAM APENAS NA RODADA 1 ({len(round1_only)}/{len(results)}):")
    print("-" * 70)
    
    if round1_only:
        for result in round1_only:
            r1_time = f"{result['round_1']['execution_time']:.1f}s"
            r2_msg = result['round_2']['validation_message'] if result['round_2'] else "Não participou da Rodada 2"
            
            print(f"  🟡 {result['model']} (R1: {r1_time} → {result['round_1']['vote_for']})")
            print(f"     Falha R2: {r2_msg}")
    else:
        print("  Todos os modelos aprovados na R1 também passaram na R2 ✅")
    
    # ========== MODELOS QUE FALHARAM NA RODADA 1 ==========
    print(f"\n❌ MODELOS QUE FALHARAM NA RODADA 1 ({len(failed_round1)}/{len(results)}):")
    print("-" * 70)
    
    if failed_round1:
        for result in failed_round1:
            error_msg = result['round_1']['error'] or result['round_1']['validation_message'] or "Erro desconhecido"
            print(f"  🔴 {result['model']}")
            print(f"     Motivo: {error_msg}")
    
    # ========== ESTATÍSTICAS GERAIS ==========
    print(f"\n📈 ESTATÍSTICAS GERAIS:")
    print("-" * 50)
    print(f"  • Total de modelos testados: {len(results)}")
    print(f"  • Aprovados na Rodada 1: {len(finalists) + len(round1_only)}/{len(results)} ({((len(finalists) + len(round1_only))/len(results)*100):.1f}%)")
    print(f"  • Finalistas (ambas rodadas): {len(finalists)}/{len(results)} ({(len(finalists)/len(results)*100):.1f}%)")
    print(f"  • Taxa de retenção R1→R2: {len(finalists)}/{len(finalists) + len(round1_only)} ({(len(finalists)/(len(finalists) + len(round1_only))*100):.1f}%)" if (len(finalists) + len(round1_only)) > 0 else "  • Taxa de retenção R1→R2: N/A")
    
    if finalists:
        avg_time_r1 = sum(r['round_1']['execution_time'] for r in finalists) / len(finalists)
        avg_time_r2 = sum(r['round_2']['execution_time'] for r in finalists) / len(finalists)
        avg_time_final = sum(r['average_time'] for r in finalists) / len(finalists)
        
        print(f"  • Tempo médio Rodada 1 (finalistas): {avg_time_r1:.1f}s")
        print(f"  • Tempo médio Rodada 2 (finalistas): {avg_time_r2:.1f}s")
        print(f"  • Tempo médio consolidado: {avg_time_final:.1f}s")


def get_model_provider(model_name: str) -> str:
    """Determina o provedor baseado no nome do modelo."""
    if model_name in ["claude-sonnet-4-0", "claude-3-5-haiku-latest"]:
        return "anthropic"
    elif model_name.startswith("google/"):
        return "google"
    elif model_name.startswith("openai/"):
        return "openai"
    elif model_name.startswith("mistral"):
        return "mistral"
    elif model_name.startswith("x-ai/"):
        return "xai"
    elif model_name.startswith("deepseek/"):
        return "deepseek"
    elif model_name.startswith("qwen/"):
        return "qwen"
    elif model_name.startswith("moonshotai/"):
        return "moonshot"
    else:
        return "unknown"


def get_model_display_name(model_name: str) -> str:
    """Gera nome amigável para exibição."""
    display_names = {
        "claude-sonnet-4-0": "Claude Sonnet 4.0",
        "claude-3-5-haiku-latest": "Claude 3.5 Haiku",
        "google/gemini-2.5-pro": "Gemini 2.5 Pro",
        "google/gemini-2.5-flash": "Gemini 2.5 Flash",
        "google/gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite",
        "google/gemma-3-27b-it": "Gemma 3 27B",
        "openai/gpt-5": "GPT-5",
        "openai/gpt-5-mini": "GPT-5 Mini",
        "openai/gpt-5-nano": "GPT-5 Nano",
        "openai/gpt-oss-120b": "GPT OSS 120B",
        "qwen/qwen3-235b-a22b-2507": "Qwen 3 235B",
        "deepseek/deepseek-chat-v3.1": "DeepSeek Chat v3.1",
        "mistral-large-latest": "Mistral Large",
        "mistral-medium-latest": "Mistral Medium", 
        "mistral-small-latest": "Mistral Small",
        "x-ai/grok-4": "Grok-4",
        "moonshotai/kimi-k2": "Kimi K2"
    }
    return display_names.get(model_name, model_name.title())


def generate_models_config(results: List[Dict]) -> None:
    """
    Gera arquivo JSON de configuração de modelos baseado nos resultados dos testes.
    
    Args:
        results: Lista de resultados dos testes de duas rodadas
    """
    print("\n🔧 Gerando configuração de modelos (models_config.json)...")
    
    # Separar modelos por status
    finalists = [r for r in results if r["final_success"]]
    
    if not finalists:
        print("❌ Nenhum finalista encontrado. Não foi possível gerar configuração.")
        return
    
    # Ordenar finalistas por tempo médio (mais rápido primeiro)
    finalists_sorted = sorted(finalists, key=lambda x: x['average_time'])
    
    # Modelo default é o mais rápido
    default_model = finalists_sorted[0]["model"]
    
    # Criar estrutura de configuração
    models_config = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "test_version": "two_rounds_v1.0",
            "total_models_tested": len(results),
            "finalists_count": len(finalists),
            "generation_criteria": {
                "max_response_time": "5.0s",
                "consistency_required": True,
                "majority_vote_required": True
            }
        },
        "default_model": default_model,
        "models": {},
        "providers": {
            "anthropic": {
                "api_type": "anthropic",
                "requires_key": "ANTHROPIC_API_KEY",
                "base_url": None
            },
            "google": {
                "api_type": "openrouter", 
                "requires_key": "OPENROUTER_API_KEY",
                "base_url": "https://openrouter.ai/api/v1"
            },
            "openai": {
                "api_type": "openrouter",
                "requires_key": "OPENROUTER_API_KEY", 
                "base_url": "https://openrouter.ai/api/v1"
            },
            "mistral": {
                "api_type": "mistral",
                "requires_key": "MISTRAL_API_KEY",
                "base_url": None
            },
            "xai": {
                "api_type": "openrouter",
                "requires_key": "OPENROUTER_API_KEY",
                "base_url": "https://openrouter.ai/api/v1"
            },
            "deepseek": {
                "api_type": "openrouter",
                "requires_key": "OPENROUTER_API_KEY",
                "base_url": "https://openrouter.ai/api/v1"
            },
            "qwen": {
                "api_type": "openrouter",
                "requires_key": "OPENROUTER_API_KEY", 
                "base_url": "https://openrouter.ai/api/v1"
            },
            "moonshot": {
                "api_type": "openrouter",
                "requires_key": "OPENROUTER_API_KEY",
                "base_url": "https://openrouter.ai/api/v1"
            }
        }
    }
    
    # Adicionar modelos finalistas
    for i, result in enumerate(finalists_sorted, 1):
        model_id = result["model"]
        provider = get_model_provider(model_id)
        
        models_config["models"][model_id] = {
            "id": model_id,
            "display_name": get_model_display_name(model_id),
            "provider": provider,
            "is_default": (model_id == default_model),
            "status": "active",
            "performance": {
                "average_time": round(result["average_time"], 2),
                "ranking": i,
                "consistency": result["vote_consistency"],
                "vote_accuracy": result["overall_vote"]
            },
            "test_results": {
                "round_1": {
                    "time": round(result["round_1"]["execution_time"], 2),
                    "vote": result["round_1"]["vote_for"],
                    "success": result["round_1"]["success"]
                },
                "round_2": {
                    "time": round(result["round_2"]["execution_time"], 2) if result["round_2"] else 0,
                    "vote": result["round_2"]["vote_for"] if result["round_2"] else None,
                    "success": result["round_2"]["success"] if result["round_2"] else False
                }
            },
            "capabilities": {
                "max_tokens": 1024,
                "temperature": 0,
                "timeout": 5,
                "supports_json": True
            }
        }
    
    # Salvar arquivo de configuração
    config_path = os.path.join("src", "laaj", "config", "models_config.json")
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(models_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuração de modelos salva em: {config_path}")
        print(f"🎯 Modelo padrão definido: {default_model}")
        print(f"📊 {len(finalists)} modelos ativos disponíveis")
        
        # Mostrar resumo dos modelos
        print(f"\n📋 MODELOS CONFIGURADOS:")
        for i, (model_id, config) in enumerate(models_config["models"].items(), 1):
            status = "🥇 DEFAULT" if config["is_default"] else f"#{i}"
            print(f"  {status} {config['display_name']} ({model_id})")
            print(f"      Tempo: {config['performance']['average_time']}s | Consistência: {'✓' if config['performance']['consistency'] else '✗'}")
            
    except Exception as e:
        print(f"❌ Erro ao salvar configuração: {e}")


async def main():
    """Função principal do teste com sistema de duas rodadas."""
    print("🔧 Verificando configuração...")
    
    # Verificar API keys
    if not config.OPENROUTER_API:
        print("❌ OPENROUTER_API_KEY não configurado!")
        return
    
    if not config.ANTHROPIC_API:
        print("⚠️ ANTHROPIC_API_KEY não configurado - modelos Claude não funcionarão")
    
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️ LANGSMITH_API_KEY não configurado - tentando continuar...")
    
    print("✅ Configuração OK\n")
    
    # Executar sistema de duas rodadas
    results = await test_two_rounds()
    
    # Gerar relatório detalhado
    generate_two_rounds_report(results)
    
    # Salvar resultados detalhados
    output_file = "judge_models_two_rounds_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados detalhados salvos em: {output_file}")
    except Exception as e:
        print(f"⚠️ Erro ao salvar resultados: {e}")
    
    # Gerar configuração de modelos estruturada
    generate_models_config(results)

if __name__ == "__main__":
    asyncio.run(main())