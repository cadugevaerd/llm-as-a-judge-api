from langgraph.graph import START, END, StateGraph

from typing import Literal, Union
from typing_extensions import TypedDict, NotRequired

import asyncio
import json
import logging
import time

from laaj.config import LITERAL_MODELS, WORKFLOW_TIMEOUT_SECONDS
from laaj.agents import LLMFactory, chain_story, chain_laaj

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BestResponseState(TypedDict):
    model_llm_a: Literal[LITERAL_MODELS]
    model_llm_b: Literal[LITERAL_MODELS]
    response_a: str
    response_b: str
    better_llm: str
    input: str
    
    # 🆕 Campos opcionais para respostas pré-geradas
    # Quando fornecidos, os nós usarão estas respostas em vez de chamar LLMs
    pre_generated_response_a: NotRequired[str]  # Resposta A já pronta (pula LLM)
    pre_generated_response_b: NotRequired[str]  # Resposta B já pronta (pula LLM)

async def node_llm_a(state: BestResponseState):
    logger.info(f"🚀 [LLM_A] Iniciando - Modelo: {state['model_llm_a']}, Input: '{state['input']}'")
    
    try:
        # 🎭 NOVA FUNCIONALIDADE: Verificar se há resposta pré-gerada
        if "pre_generated_response_a" in state and state.get("pre_generated_response_a"):
            pre_generated = state["pre_generated_response_a"]
            logger.info(f"🎭 [LLM_A] Usando resposta pré-gerada - {len(str(pre_generated))} chars")
            logger.info(f"⚡ [LLM_A] Pulando chamada de LLM (economia de API)")
            
            return {
                "response_a": pre_generated,
                "model_llm_a": state["model_llm_a"]  # Mantém o modelo original para referência
            }
        
        # 🚀 Fluxo normal: gerar resposta via LLM
        logger.info(f"🤖 [LLM_A] Gerando resposta via LLM (sem pré-gerada)")
        input_topic = state["input"]
        model_name = state["model_llm_a"]
        
        # Usar factory para criar o LLM - elimina if/elif duplicados
        llm = LLMFactory.create_llm(model_name)
        
        logger.info(f"⚙️ [LLM_A] Criando chain e invocando LLM...")
        chain = chain_story(llm)
        response = await chain.ainvoke(input={"topic": input_topic})
        logger.info(f"✅ [LLM_A] Resposta gerada via LLM - {len(str(response))} chars")
        
        return {
            "response_a": response,
            "model_llm_a": model_name
        }
        
    except ValueError as e:
        # Factory lança ValueError para modelos não suportados
        logger.error(f"❌ [LLM_A] Erro de modelo não suportado: {str(e)}")
        error_msg = f"MODELO_ERROR: {str(e)}"
        return {
            "response_a": error_msg,
            "model_llm_a": state.get("model_llm_a", "unknown")
        }
    except Exception as e:
        # Captura qualquer outro erro (API, network, parsing, etc.)
        error_type = type(e).__name__
        logger.error(f"❌ [LLM_A] Erro inesperado ({error_type}): {str(e)}")
        logger.error(f"🔍 [LLM_A] Modelo: {state.get('model_llm_a', 'N/A')}, Input: '{state.get('input', 'N/A')}'")
        
        # Fallback: tentar resposta genérica
        fallback_response = f"LLM_A_ERROR: Falha na geração de resposta ({error_type}: {str(e)})"
        logger.warning(f"🔄 [LLM_A] Usando resposta de fallback")
        
        return {
            "response_a": fallback_response,
            "model_llm_a": state.get("model_llm_a", "error")
        }
    
async def node_llm_b(state: BestResponseState):
    logger.info(f"🚀 [LLM_B] Iniciando - Modelo: {state['model_llm_b']}, Input: '{state['input']}'")
    
    try:
        # 🎭 NOVA FUNCIONALIDADE: Verificar se há resposta pré-gerada
        if "pre_generated_response_b" in state and state.get("pre_generated_response_b"):
            pre_generated = state["pre_generated_response_b"]
            logger.info(f"🎭 [LLM_B] Usando resposta pré-gerada - {len(str(pre_generated))} chars")
            logger.info(f"⚡ [LLM_B] Pulando chamada de LLM (economia de API)")
            
            return {
                "response_b": pre_generated,
                "model_llm_b": state["model_llm_b"]  # Mantém o modelo original para referência
            }
        
        # 🚀 Fluxo normal: gerar resposta via LLM
        logger.info(f"🤖 [LLM_B] Gerando resposta via LLM (sem pré-gerada)")
        input_topic = state["input"]
        model_name = state["model_llm_b"]
        
        # Usar factory para criar o LLM - elimina if/elif duplicados
        llm = LLMFactory.create_llm(model_name)
        
        logger.info(f"⚙️ [LLM_B] Criando chain e invocando LLM...")
        chain = chain_story(llm)
        response = await chain.ainvoke(input={"topic": input_topic})
        logger.info(f"✅ [LLM_B] Resposta gerada via LLM - {len(str(response))} chars")
        
        return {
            "response_b": response,
            "model_llm_b": model_name
        }
        
    except ValueError as e:
        # Factory lança ValueError para modelos não suportados
        logger.error(f"❌ [LLM_B] Erro de modelo não suportado: {str(e)}")
        error_msg = f"MODELO_ERROR: {str(e)}"
        return {
            "response_b": error_msg,
            "model_llm_b": state.get("model_llm_b", "unknown")
        }
    except Exception as e:
        # Captura qualquer outro erro (API, network, parsing, etc.)
        error_type = type(e).__name__
        logger.error(f"❌ [LLM_B] Erro inesperado ({error_type}): {str(e)}")
        logger.error(f"🔍 [LLM_B] Modelo: {state.get('model_llm_b', 'N/A')}, Input: '{state.get('input', 'N/A')}'")
        
        # Fallback: tentar resposta genérica
        fallback_response = f"LLM_B_ERROR: Falha na geração de resposta ({error_type}: {str(e)})"
        logger.warning(f"🔄 [LLM_B] Usando resposta de fallback")
        
        return {
            "response_b": fallback_response,
            "model_llm_b": state.get("model_llm_b", "error")
        }


async def node_judge(state: BestResponseState):
    logger.info(f"⚖️ [JUDGE] Iniciando avaliação entre {state['model_llm_a']} vs {state['model_llm_b']}")
    
    try:
        response_a = state["response_a"]
        response_b = state["response_b"]
        
        # 🛡️ Verificar se alguma resposta falhou
        response_a_failed = response_a and ("ERROR" in str(response_a) or "TIMEOUT" in str(response_a))
        response_b_failed = response_b and ("ERROR" in str(response_b) or "TIMEOUT" in str(response_b))
        
        logger.info(f"📝 [JUDGE] Resposta A: {len(str(response_a))} chars (Failed: {response_a_failed})")
        logger.info(f"📝 [JUDGE] Resposta B: {len(str(response_b))} chars (Failed: {response_b_failed})")
        
        # 🛡️ LÓGICA DE FALLBACK: Se uma resposta falhou, a outra vence automaticamente
        if response_a_failed and response_b_failed:
            logger.warning(f"🚨 [JUDGE] AMBAS as respostas falharam - declarando empate técnico")
            return {
                "better_llm": "EMPATE_TÉCNICO - Ambos modelos falharam"
            }
        elif response_a_failed:
            logger.warning(f"🏆 [JUDGE] Resposta A falhou - {state['model_llm_b']} vence por WO")
            return {
                "better_llm": f"{state['model_llm_b']} (vitória por WO - A falhou)"
            }
        elif response_b_failed:
            logger.warning(f"🏆 [JUDGE] Resposta B falhou - {state['model_llm_a']} vence por WO")
            return {
                "better_llm": f"{state['model_llm_a']} (vitória por WO - B falhou)"
            }
        
        # 🚀 Fluxo normal: ambas respostas válidas, usar juiz
        logger.info(f"🔍 [JUDGE] Ambas respostas válidas - carregando modelo juiz (GPT-5)")
        
        # Usar factory para criar o modelo juiz
        judge_llm = LLMFactory.create_llm("gpt-5")
        chain = chain_laaj(judge_llm)
        logger.info(f"⚙️ [JUDGE] Invocando modelo juiz para comparação...")
        
        response = await chain.ainvoke(input={
            "answer_a": response_a, 
            "answer_b": response_b, 
            "question": state["input"]
        })
        
        logger.info(f"📊 [JUDGE] Resposta do juiz recebida: {response}")
        
        # 🛡️ PARSING ROBUSTO da resposta do juiz
        if response and isinstance(response, dict) and "Preference" in response:
            resultado = response["Preference"]
            logger.info(f"🎯 [JUDGE] Preferência detectada: {resultado}")
            
            if resultado == int(1):
                better_llm = state["model_llm_a"]
                logger.info(f"🏆 [JUDGE] Vencedor: {better_llm} (Modelo A)")
            elif resultado == int(2):
                better_llm = state["model_llm_b"]
                logger.info(f"🏆 [JUDGE] Vencedor: {better_llm} (Modelo B)")
            else:
                better_llm = "Empate"
                logger.info(f"🤝 [JUDGE] Resultado: Empate")
                
            return {
                "better_llm": better_llm
            }
        else:
            # Resposta do juiz malformada
            logger.error(f"❌ [JUDGE] Resposta malformada do juiz: {response}")
            return {
                "better_llm": "JUDGE_ERROR - Resposta malformada do juiz"
            }
            
    except ValueError as e:
        # Erro de modelo não suportado no juiz
        logger.error(f"❌ [JUDGE] Erro de modelo juiz não suportado: {str(e)}")
        return {
            "better_llm": f"JUDGE_MODEL_ERROR: {str(e)}"
        }
    except Exception as e:
        # Qualquer outro erro no juiz
        error_type = type(e).__name__
        logger.error(f"❌ [JUDGE] Erro inesperado ({error_type}): {str(e)}")
        logger.error(f"🔍 [JUDGE] Estado: A={state.get('model_llm_a', 'N/A')}, B={state.get('model_llm_b', 'N/A')}")
        
        # Fallback final: empate técnico
        logger.warning(f"🔄 [JUDGE] Fallback para empate técnico devido ao erro")
        return {
            "better_llm": f"JUDGE_ERROR - Empate técnico ({error_type}: {str(e)})"
        }
async def builder_graph():
    logger.info(f"🔧 [BUILDER] Construindo grafo LangGraph")
    
    try:
        builder = StateGraph(
            BestResponseState
        )
        
        logger.info(f"➕ [BUILDER] Adicionando nós: llm_1, llm_2, judge")
        builder.add_node("llm_1", node_llm_a)
        builder.add_node("llm_2", node_llm_b)
        builder.add_node("judge", node_judge)

        logger.info(f"🔗 [BUILDER] Configurando fluxo: START -> llm_1,llm_2 -> judge -> END")
        builder.add_edge(START, "llm_1")
        builder.add_edge(START, "llm_2")
        builder.add_edge("llm_1", "judge")
        builder.add_edge("llm_2", "judge")
        builder.add_edge("judge", END)

        logger.info(f"⚡ [BUILDER] Compilando grafo...")
        graph = builder.compile()
        logger.info(f"✅ [BUILDER] Grafo compilado com sucesso")
        return graph
        
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"❌ [BUILDER] Erro na construção do grafo ({error_type}): {str(e)}")
        logger.error(f"🚨 [BUILDER] Falha crítica - não é possível continuar sem o grafo")
        raise RuntimeError(f"GRAPH_BUILD_ERROR: Falha na construção do grafo LangGraph ({error_type}: {str(e)})")

async def main(input: str, llm_a: Union[LITERAL_MODELS, None] = "google-gemini-2.5-pro", llm_b: LITERAL_MODELS = "claude-4-sonnet", pre_generated_response_a: Union[str, None] = None, pre_generated_response_b: Union[str, None] = None, timeout_seconds: Union[int, None] = None):
    """
    Função principal do workflow com timeout global configurável
    
    Args:
        input (str): Tópico/pergunta para os LLMs
        llm_a (str): Modelo LLM A
        llm_b (str): Modelo LLM B  
        pre_generated_response_a (str, optional): Resposta pré-gerada para LLM A
        pre_generated_response_b (str, optional): Resposta pré-gerada para LLM B
        timeout_seconds (int, optional): Timeout em segundos (padrão: WORKFLOW_TIMEOUT_SECONDS)
    
    Returns:
        dict: Resultado do workflow ou erro de timeout
    """
    # Usar timeout da config se não especificado
    timeout = timeout_seconds if timeout_seconds is not None else WORKFLOW_TIMEOUT_SECONDS
    
    logger.info(f"🎬 [MAIN] Iniciando workflow principal com input: '{input}'")
    logger.info(f"⏰ [MAIN] Timeout configurado: {timeout}s")
    start_time = time.time()
    
    try:
        # 🆕 IMPLEMENTAÇÃO DE TIMEOUT GLOBAL
        async with asyncio.timeout(timeout):
            # 🛡️ Tentar construir o grafo com recuperação
            try:
                graph = await builder_graph()
            except RuntimeError as e:
                # Erro crítico na construção do grafo - não há recovery
                logger.error(f"🚨 [MAIN] Erro crítico na construção do grafo: {str(e)}")
                elapsed_time = time.time() - start_time
                return {
                    "model_llm_a": llm_a,
                    "model_llm_b": llm_b,
                    "response_a": "GRAPH_BUILD_ERROR",
                    "response_b": "GRAPH_BUILD_ERROR", 
                    "better_llm": f"CRITICAL_ERROR - Construção do grafo falhou após {elapsed_time:.2f}s",
                    "input": input,
                    "pre_generated_response_a": pre_generated_response_a,
                    "pre_generated_response_b": pre_generated_response_b,
                    "execution_time": elapsed_time
                }

            logger.info(f"🆚 [MAIN] Comparação: {llm_a} vs {llm_b}")
            
            # 🛡️ Executar workflow com recuperação
            logger.info(f"🚀 [MAIN] Executando workflow assíncrono...")
            try:
                response = await graph.ainvoke(
                    input={
                        "input": input,
                        "model_llm_a": llm_a,
                        "model_llm_b": llm_b,
                        "pre_generated_response_a": pre_generated_response_a,
                        "pre_generated_response_b": pre_generated_response_b
                    }
                )
            except Exception as workflow_error:
                # Erro durante execução do workflow - recovery com estado de erro
                error_type = type(workflow_error).__name__
                logger.error(f"❌ [MAIN] Erro durante execução do workflow ({error_type}): {str(workflow_error)}")
                elapsed_time = time.time() - start_time
                
                return {
                    "model_llm_a": llm_a,
                    "model_llm_b": llm_b,
                    "response_a": f"WORKFLOW_EXECUTION_ERROR: {error_type}",
                    "response_b": f"WORKFLOW_EXECUTION_ERROR: {error_type}",
                    "better_llm": f"WORKFLOW_ERROR - Execução falhou após {elapsed_time:.2f}s ({str(workflow_error)})",
                    "input": input,
                    "pre_generated_response_a": pre_generated_response_a,
                    "pre_generated_response_b": pre_generated_response_b,
                    "execution_time": elapsed_time
                }
            
            elapsed_time = time.time() - start_time
            logger.info(f"🏁 [MAIN] Workflow concluído em {elapsed_time:.2f}s")
            logger.info(f"🎯 [MAIN] Resultado final: {response.get('better_llm', 'N/A')}")
            
            # 🛡️ Validar response antes de retornar
            if not response or not isinstance(response, dict):
                logger.warning(f"⚠️ [MAIN] Resposta inválida do workflow: {type(response)}")
                return {
                    "model_llm_a": llm_a,
                    "model_llm_b": llm_b,
                    "response_a": "INVALID_WORKFLOW_RESPONSE",
                    "response_b": "INVALID_WORKFLOW_RESPONSE",
                    "better_llm": "RESPONSE_VALIDATION_ERROR - Resposta inválida do workflow",
                    "input": input,
                    "pre_generated_response_a": pre_generated_response_a,
                    "pre_generated_response_b": pre_generated_response_b,
                    "execution_time": elapsed_time
                }
            
            response['execution_time'] = elapsed_time
            return response
            
    except asyncio.TimeoutError:
        elapsed_time = time.time() - start_time
        error_msg = f"Workflow excedeu timeout de {timeout}s após {elapsed_time:.2f}s"
        
        logger.error(f"⏰ [MAIN] TIMEOUT: {error_msg}")
        logger.error(f"🚨 [MAIN] Workflow foi interrompido - possível LLM lento ou travado")
        
        # Retornar estado de erro consistente com o schema
        return {
            "model_llm_a": llm_a,
            "model_llm_b": llm_b, 
            "response_a": "WORKFLOW_TIMEOUT_ERROR",
            "response_b": "WORKFLOW_TIMEOUT_ERROR",
            "better_llm": f"TIMEOUT_ERROR - Excedeu {timeout}s",
            "input": input,
            "pre_generated_response_a": pre_generated_response_a,
            "pre_generated_response_b": pre_generated_response_b,
            "execution_time": elapsed_time
        }

if __name__ == "__main__":
    import asyncio
    
    logger.info("="*60)
    logger.info("🔥 INICIANDO EXECUÇÃO DO LLM AS JUDGE WORKFLOW")
    logger.info("="*60)
    
    response = asyncio.run(main("Amigos"))
    
    logger.info("="*60)
    logger.info("📋 RESULTADO FINAL:")
    logger.info("="*60)
    
    print(json.dumps(response, indent=2))

# print(type(response))

