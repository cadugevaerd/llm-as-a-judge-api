"""
Workflow simplificado que trabalha APENAS com respostas pré-geradas.
Remove toda a lógica de geração de LLMs e foca apenas na comparação via judge.
"""

from typing import Optional, List
from typing_extensions import TypedDict

from laaj.api.schemas import CompareRequest, BatchComparisonResult

import asyncio
import json
import logging
import time

from laaj.agents import LLMFactory, chain_laaj

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComparisonState(TypedDict):
    """Estado simplificado contendo apenas respostas pré-geradas e resultado do judge."""
    
    input: str  # Pergunta/contexto original
    response_a: str  # Resposta pré-gerada A (obrigatória)
    response_b: str  # Resposta pré-gerada B (obrigatória)
    model_a_name: Optional[str]  # Nome do modelo A (opcional, apenas referência)
    model_b_name: Optional[str]  # Nome do modelo B (opcional, apenas referência)
    
    # Resultado do judge
    better_response: str  # "A", "B", "Empate", ou mensagem de erro
    judge_reasoning: Optional[str]  # Explicação do judge (quando disponível)

def parse_judge_response(response) -> dict:
    """
    Extrai e processa a resposta do judge, suportando JSON estruturado e texto natural.
    
    Args:
        response: Resposta do modelo judge (dict ou string)
        
    Returns:
        dict: {"better_response": str, "judge_reasoning": str}
    """
    try:
        # Parse da resposta do judge - pode ser dict ou string
        if response and isinstance(response, dict) and "Preference" in response:
            # Resposta estruturada (JSON)
            resultado = response["Preference"]
            logger.info(f"🎯 [PARSE] Preferência detectada (JSON): {resultado}")
            
            # Interpretar resultado
            if resultado == 1:
                better = "A"
                logger.info(f"🏆 [PARSE] Vencedor: Resposta A")
            elif resultado == 2:
                better = "B"
                logger.info(f"🏆 [PARSE] Vencedor: Resposta B")
            else:
                better = "Empate"
                logger.info(f"🤝 [PARSE] Resultado: Empate")
            
            # Extrair reasoning se disponível
            judge_reasoning = response.get("Reasoning", None) or response.get("reasoning", None)
            
            return {
                "better_response": better,
                "judge_reasoning": judge_reasoning
            }
        elif response and isinstance(response, str):
            # Resposta em texto natural - fazer parsing manual
            response_text = response.lower()
            judge_reasoning = response[:500] + "..." if len(response) > 500 else response
            
            logger.info(f"🔍 [PARSE] Analisando resposta em texto: {response[:100]}...")
            
            # Procurar por indicadores de preferência
            if "assistant a" in response_text and "winner:" in response_text and "assistant a" in response_text[response_text.find("winner:"):]:
                better = "A"
                logger.info(f"🏆 [PARSE] Vencedor: Resposta A (texto)")
            elif "assistant b" in response_text and "winner:" in response_text and "assistant b" in response_text[response_text.find("winner:"):]:
                better = "B"
                logger.info(f"🏆 [PARSE] Vencedor: Resposta B (texto)")
            elif "empate" in response_text or "tie" in response_text:
                better = "Empate"
                logger.info(f"🤝 [PARSE] Resultado: Empate (texto)")
            else:
                # Fallback: tentar detectar qual resposta foi mais elogiada
                if response_text.count("assistant a") > response_text.count("assistant b"):
                    better = "A"
                    logger.info(f"🏆 [PARSE] Vencedor: Resposta A (inferido)")
                elif response_text.count("assistant b") > response_text.count("assistant a"):
                    better = "B"
                    logger.info(f"🏆 [PARSE] Vencedor: Resposta B (inferido)")
                else:
                    better = "Empate"
                    logger.info(f"🤝 [PARSE] Resultado: Empate (não foi possível determinar)")
            
            return {
                "better_response": better,
                "judge_reasoning": judge_reasoning
            }
        else:
            # Resposta malformada
            logger.error(f"❌ [PARSE] Resposta malformada do judge: {type(response)} - {response}")
            return {
                "better_response": "ERRO - Resposta malformada do judge",
                "judge_reasoning": f"O judge retornou uma resposta inesperada: {response}"
            }
            
    except ValueError as e:
        # Capturar erro de parsing JSON e tentar extrair o resultado do texto do erro
        error_message = str(e)
        logger.info(f"🔧 [PARSE] Erro de JSON, tentando extrair resultado do texto: {error_message[:200]}...")
        
        # O erro contém o texto da resposta do judge
        if "Invalid json output:" in error_message:
            response_text = error_message.split("Invalid json output:", 1)[1].strip()
            judge_reasoning = response_text[:500] + "..." if len(response_text) > 500 else response_text
            
            # Procurar por padrões mais específicos baseado no erro real
            response_lower = response_text.lower()
            
            # Procurar por padrões que indicam conclusão
            if ("assistant a is better" in response_lower or 
                "**assistant a is better**" in response_lower or
                "assistant a provides a more" in response_lower or
                response_lower.endswith("assistant a is better") or
                "winner: assistant a" in response_lower):
                better = "A"
                logger.info(f"🏆 [PARSE] Vencedor extraído do erro: Resposta A")
            elif ("assistant b is better" in response_lower or 
                  "**assistant b is better**" in response_lower or
                  "assistant b provides a more" in response_lower or
                  response_lower.endswith("assistant b is better") or
                  "winner: assistant b" in response_lower or
                  "assistant b provides the better response" in response_lower):
                better = "B" 
                logger.info(f"🏆 [PARSE] Vencedor extraído do erro: Resposta B")
            elif ("both responses" in response_lower and ("equal" in response_lower or "tie" in response_lower)) or "empate" in response_lower:
                better = "Empate"
                logger.info(f"🤝 [PARSE] Resultado extraído do erro: Empate")
            else:
                # Buscar por conclusões no final do texto (últimas 3 linhas)
                lines = response_text.strip().split('\n')
                last_lines = ' '.join(lines[-3:]).lower() if len(lines) >= 3 else response_lower
                
                if ("assistant a" in last_lines and ("better" in last_lines or "more" in last_lines)) and "assistant b" not in last_lines:
                    better = "A"
                    logger.info(f"🏆 [PARSE] Vencedor inferido das linhas finais: Resposta A")
                elif ("assistant b" in last_lines and ("better" in last_lines or "more" in last_lines)) and "assistant a" not in last_lines:
                    better = "B"
                    logger.info(f"🏆 [PARSE] Vencedor inferido das linhas finais: Resposta B")
                else:
                    # Fallback: buscar palavras-chave de qualidade
                    a_score = 0
                    b_score = 0
                    
                    # Contar indicadores de qualidade após "assistant a"
                    a_indicators = ["assistant a provides a more", "assistant a is more", "assistant a better", 
                                   "assistant a gives a more", "assistant a offers a more"]
                    b_indicators = ["assistant b provides a more", "assistant b is more", "assistant b better",
                                   "assistant b gives a more", "assistant b offers a more"]
                    
                    for indicator in a_indicators:
                        if indicator in response_lower:
                            a_score += 1
                    for indicator in b_indicators:
                        if indicator in response_lower:
                            b_score += 1
                    
                    if a_score > b_score:
                        better = "A"
                        logger.info(f"🏆 [PARSE] Vencedor por indicadores: Resposta A (score: {a_score} vs {b_score})")
                    elif b_score > a_score:
                        better = "B"
                        logger.info(f"🏆 [PARSE] Vencedor por indicadores: Resposta B (score: {b_score} vs {a_score})")
                    else:
                        better = "Empate"
                        logger.info(f"🤝 [PARSE] Não foi possível determinar vencedor - considerado Empate")
            
        else:
            # Qualquer coisa que não seja JSON estruturado é erro
            logger.error(f"❌ [PARSE] Judge não retornou JSON estruturado esperado: {type(response)}")
            logger.error(f"❌ [PARSE] Resposta recebida: {str(response)[:200]}...")
            
            return {
                "better_response": "ERRO - Judge não retornou JSON estruturado",
                "judge_reasoning": f"Esperado JSON com campo 'Preference', recebido: {type(response)} - {str(response)[:200]}..."
            }
            
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"❌ [PARSE] Erro no parsing ({error_type}): {str(e)}")
        logger.error(f"❌ [PARSE] Resposta que causou erro: {str(response)[:200]}...")
        
        return {
            "better_response": f"ERRO - Falha no parsing: {error_type}",
            "judge_reasoning": f"Erro ao processar resposta do judge: {str(e)}"
        }

async def node_judge(state: ComparisonState):
    """
    Nó do judge que compara apenas respostas pré-geradas.
    Não precisa mais de lógica de falhas de LLM pois as respostas já estão prontas.
    """
    logger.info(f"⚖️ [JUDGE] Iniciando comparação de respostas pré-geradas")
    
    try:
        response_a = state["response_a"]
        response_b = state["response_b"]
        input_question = state["input"]
        
        logger.info(f"📝 [JUDGE] Input: {input_question[:100]}...")
        logger.info(f"📝 [JUDGE] Resposta A: {len(response_a)} chars")
        logger.info(f"📝 [JUDGE] Resposta B: {len(response_b)} chars")
        
        # Usar modelo judge (Claude 4 Sonnet como padrão)
        logger.info(f"🔍 [JUDGE] Carregando modelo judge...")
        
        try:
            judge_llm = LLMFactory.create_llm("claude-4-sonnet")
            chain = chain_laaj(judge_llm)
            logger.info(f"⚙️ [JUDGE] Invocando modelo judge para comparação...")
            
            # Chamar o judge
            response = await chain.ainvoke(input={
                "answer_a": response_a, 
                "answer_b": response_b, 
                "question": input_question
            })
            
            logger.info(f"📊 [JUDGE] Resposta do judge recebida: {response}")
            
            # Usar função centralizada de parsing
            return parse_judge_response(response)
                
        except ValueError as e:
            # Para ValueError (erros de JSON), também usar a função de parsing
            logger.info(f"🔧 [JUDGE] Erro de JSON capturado, delegando para parse_judge_response...")
            return parse_judge_response(e)
        
        except Exception as e:
            # Outros erros do LLM/chain - tratamento específico do nó judge
            error_type = type(e).__name__
            logger.error(f"❌ [JUDGE] Erro de modelo judge ({error_type}): {str(e)}")
            
            return {
                "better_response": f"ERRO - Falha no modelo judge",
                "judge_reasoning": f"Erro durante execução do judge: {error_type} - {str(e)}"
            }
            
    except Exception as e:
        # Qualquer outro erro
        error_type = type(e).__name__
        logger.error(f"❌ [JUDGE] Erro inesperado ({error_type}): {str(e)}")
        
        return {
            "better_response": f"ERRO - Falha inesperada no judge",
            "judge_reasoning": f"Erro interno: {error_type} - {str(e)}"
        }
        
        
async def batch_judge_processing(comparisons: List[CompareRequest]) -> List[BatchComparisonResult]:
    """
    Processa múltiplas comparações em paralelo usando abatch() do LangChain.
    Erros individuais não afetam outras comparações do batch.
    """
    logger.info(f"🔥 [BATCH] Iniciando processamento batch de {len(comparisons)} comparações")

    try:
        # 1. Preparar inputs batch (mesmo formato do input individual)
        batch_inputs = []
        for comp in comparisons:
            batch_inputs.append({
                "question": comp.input,
                "answer_a": comp.response_a,
                "answer_b": comp.response_b
            })

        # 2. Usar chain.abatch() para processamento paralelo
        judge_llm = LLMFactory.create_llm("claude-4-sonnet")
        chain = chain_laaj(judge_llm)
        
        logger.info(f"⚙️ [BATCH] Executando processamento paralelo...")

        # 3. Executar batch
        batch_results = await chain.abatch(batch_inputs)
        
        logger.info(f"📊 [BATCH] Processamento batch concluído, processando {len(batch_results)} resultados")

        # 4. Processar resultados individuais com tratamento de erro
        final_results = []
        successful_count = 0
        
        for i, (comparison, judge_result) in enumerate(zip(comparisons, batch_results)):
            try:
                # Usar mesmo parsing do node_judge existente
                parsed_result = parse_judge_response(judge_result)
                
                final_results.append(BatchComparisonResult(
                    input=comparison.input,
                    response_a=comparison.response_a,
                    response_b=comparison.response_b,
                    model_a_name=comparison.model_a_name,
                    model_b_name=comparison.model_b_name,
                    better_response=parsed_result["better_response"],
                    judge_reasoning=parsed_result["judge_reasoning"]
                ))
                
                # Contar sucessos (não considerar ERROs como sucesso)
                if not parsed_result["better_response"].startswith("ERRO"):
                    successful_count += 1
                
                logger.info(f"✅ [BATCH] Comparação {i+1}/{len(comparisons)} processada: {parsed_result['better_response']}")
                
            except Exception as e:
                # Erro no processamento individual - não interrompe o batch
                error_type = type(e).__name__
                logger.error(f"❌ [BATCH] Erro na comparação {i+1}: {error_type} - {str(e)}")
                
                final_results.append(BatchComparisonResult(
                    input=comparison.input,
                    response_a=comparison.response_a,
                    response_b=comparison.response_b,
                    model_a_name=comparison.model_a_name,
                    model_b_name=comparison.model_b_name,
                    better_response=f"ERRO - Falha no processamento individual",
                    judge_reasoning=f"Erro durante processamento da comparação: {error_type} - {str(e)}"
                ))

        logger.info(f"🏁 [BATCH] Processamento concluído: {successful_count}/{len(comparisons)} sucessos")
        return final_results
        
    except Exception as e:
        # Erro crítico que afeta todo o batch
        error_type = type(e).__name__
        logger.error(f"💥 [BATCH] Erro crítico no processamento batch ({error_type}): {str(e)}")
        
        # Retornar resultados de erro para todas as comparações
        error_results = []
        for comparison in comparisons:
            error_results.append(BatchComparisonResult(
                input=comparison.input,
                response_a=comparison.response_a,
                response_b=comparison.response_b,
                model_a_name=comparison.model_a_name,
                model_b_name=comparison.model_b_name,
                better_response=f"ERRO - Falha crítica no batch",
                judge_reasoning=f"Erro crítico durante processamento batch: {error_type} - {str(e)}"
            ))
        
        return error_results
        
async def main(
    input_question: str,
    response_a: str,
    response_b: str,
    model_a_name: Optional[str] = None,
    model_b_name: Optional[str] = None,
    timeout_seconds: int = 30
) -> dict:
    """
    Função principal simplificada para comparação de respostas pré-geradas.
    
    Args:
        input_question: Pergunta/contexto original
        response_a: Resposta pré-gerada A
        response_b: Resposta pré-gerada B  
        model_a_name: Nome do modelo A (opcional)
        model_b_name: Nome do modelo B (opcional)
        timeout_seconds: Timeout em segundos
    
    Returns:
        dict: Resultado da comparação com campos necessários para ComparisonResponse
    """
    logger.info(f"🎬 [MAIN] Iniciando comparação de respostas pré-geradas")
    logger.info(f"⏰ [MAIN] Timeout configurado: {timeout_seconds}s")
    start_time = time.time()
    
    try:
        # Aplicar timeout
        async with asyncio.timeout(timeout_seconds):
            
            # Validar inputs
            if not response_a or not response_a.strip():
                raise ValueError("response_a não pode ser vazia")
            if not response_b or not response_b.strip():
                raise ValueError("response_b não pode ser vazia")
            if not input_question or not input_question.strip():
                raise ValueError("input_question não pode ser vazio")
            
            # Preparar estado
            state = ComparisonState(
                input=input_question.strip(),
                response_a=response_a.strip(),
                response_b=response_b.strip(),
                model_a_name=model_a_name,
                model_b_name=model_b_name,
                better_response="",  # Será preenchido pelo judge
                judge_reasoning=None
            )
            
            # Executar judge
            logger.info(f"🚀 [MAIN] Executando comparação...")
            judge_result = await node_judge(state)
            
            # Mesclar resultado com estado original
            final_result = {
                "input": input_question,
                "response_a": response_a,
                "response_b": response_b,
                "model_a_name": model_a_name,
                "model_b_name": model_b_name,
                "better_response": judge_result["better_response"],
                "judge_reasoning": judge_result.get("judge_reasoning"),
                "execution_time": time.time() - start_time
            }
            
            elapsed_time = time.time() - start_time
            logger.info(f"🏁 [MAIN] Comparação concluída em {elapsed_time:.2f}s")
            logger.info(f"🎯 [MAIN] Resultado: {judge_result['better_response']}")
            
            return final_result
            
    except asyncio.TimeoutError:
        elapsed_time = time.time() - start_time
        error_msg = f"Comparação excedeu timeout de {timeout_seconds}s após {elapsed_time:.2f}s"
        
        logger.error(f"⏰ [MAIN] TIMEOUT: {error_msg}")
        
        return {
            "input": input_question,
            "response_a": response_a,
            "response_b": response_b,
            "model_a_name": model_a_name,
            "model_b_name": model_b_name,
            "better_response": f"TIMEOUT - Excedeu {timeout_seconds}s",
            "judge_reasoning": f"A comparação foi interrompida por timeout após {elapsed_time:.2f}s",
            "execution_time": elapsed_time
        }
    
    except ValueError as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ [MAIN] Erro de validação: {str(e)}")
        
        return {
            "input": input_question or "",
            "response_a": response_a or "",
            "response_b": response_b or "",
            "model_a_name": model_a_name,
            "model_b_name": model_b_name,
            "better_response": f"ERRO - Validação falhou",
            "judge_reasoning": f"Erro de validação de entrada: {str(e)}",
            "execution_time": elapsed_time
        }
    
    except Exception as e:
        elapsed_time = time.time() - start_time
        error_type = type(e).__name__
        logger.error(f"❌ [MAIN] Erro inesperado ({error_type}): {str(e)}")
        
        return {
            "input": input_question or "",
            "response_a": response_a or "",
            "response_b": response_b or "",
            "model_a_name": model_a_name,
            "model_b_name": model_b_name,
            "better_response": f"ERRO - {error_type}",
            "judge_reasoning": f"Falha inesperada durante a comparação: {str(e)}",
            "execution_time": elapsed_time
        }

if __name__ == "__main__":
    import asyncio
    
    logger.info("="*60)
    logger.info("🔥 TESTANDO WORKFLOW DE COMPARAÇÃO (APENAS RESPOSTAS PRÉ-GERADAS)")
    logger.info("="*60)
    
    # Teste com respostas de exemplo
    test_input = "Qual a capital do Brasil?"
    test_response_a = "A capital do Brasil é Brasília, localizada no Distrito Federal. Foi inaugurada em 1960 e é o centro político do país."
    test_response_b = "Brasília é a capital do Brasil desde 1960."
    
    response = asyncio.run(main(
        input_question=test_input,
        response_a=test_response_a,
        response_b=test_response_b,
        model_a_name="claude-4-sonnet",
        model_b_name="google-gemini-2.5-pro"
    ))
    
    logger.info("="*60)
    logger.info("📋 RESULTADO FINAL:")
    logger.info("="*60)
    
    print(json.dumps(response, indent=2, ensure_ascii=False))

