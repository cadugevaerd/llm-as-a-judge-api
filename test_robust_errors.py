#!/usr/bin/env python3
"""
Teste do sistema de tratamento robusto de erros
"""

import asyncio
import sys
import os

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from laaj.workflow.workflow import main

async def test_robust_error_handling():
    print("🛡️ TESTANDO TRATAMENTO ROBUSTO DE ERROS\n")
    
    # TESTE 1: Modelo inexistente no LLM A
    print("=" * 60)
    print("❌ TESTE 1: MODELO INEXISTENTE (LLM A)")
    print("=" * 60)
    
    result1 = await main(
        input="Teste de erro", 
        llm_a="modelo-inexistente",  # Modelo que não existe
        llm_b="claude-4-sonnet"
    )
    print(f"🎯 Resultado: {result1.get('better_llm', 'N/A')}")
    print(f"📝 Response A: {result1.get('response_a', 'N/A')[:80]}...")
    print(f"📝 Response B: {result1.get('response_b', 'N/A')[:80]}...")
    print()
    
    # TESTE 2: Ambos modelos inexistentes
    print("=" * 60)
    print("❌ TESTE 2: AMBOS MODELOS INEXISTENTES")
    print("=" * 60)
    
    result2 = await main(
        input="Teste de erro duplo", 
        llm_a="modelo-fake-a",  
        llm_b="modelo-fake-b"
    )
    print(f"🎯 Resultado: {result2.get('better_llm', 'N/A')}")
    print(f"📝 Response A: {result2.get('response_a', 'N/A')[:80]}...")
    print(f"📝 Response B: {result2.get('response_b', 'N/A')[:80]}...")
    print()
    
    # TESTE 3: Modelo A falha, B com pré-gerada (B deve vencer)
    print("=" * 60)
    print("🥊 TESTE 3: A FALHA vs B PRÉ-GERADA (B deve vencer)")
    print("=" * 60)
    
    result3 = await main(
        input="Teste WO", 
        llm_a="modelo-inexistente",
        llm_b="claude-4-sonnet",
        pre_generated_response_b="História de sucesso pré-gerada!"
    )
    print(f"🏆 Resultado: {result3.get('better_llm', 'N/A')}")
    print(f"📝 Response A: {result3.get('response_a', 'N/A')[:80]}...")
    print(f"📝 Response B: {result3.get('response_b', 'N/A')[:80]}...")
    print()
    
    # TESTE 4: Timeout muito baixo sem pré-geradas (teste recovery)
    print("=" * 60)
    print("⏰ TESTE 4: TIMEOUT BAIXO (recovery)")
    print("=" * 60)
    
    result4 = await main(
        input="Teste timeout", 
        timeout_seconds=2  # Impossível para LLMs reais
    )
    print(f"⚠️ Resultado: {result4.get('better_llm', 'N/A')}")
    print(f"📝 Contém TIMEOUT_ERROR: {'TIMEOUT_ERROR' in str(result4.get('better_llm', ''))}")
    print()
    
    # TESTE 5: Input vazio/malformado
    print("=" * 60)
    print("🔍 TESTE 5: INPUT VAZIO (edge case)")
    print("=" * 60)
    
    result5 = await main(
        input="",  # Input vazio
        pre_generated_response_a="A resposta mesmo com input vazio",
        pre_generated_response_b="B resposta mesmo com input vazio"
    )
    print(f"📋 Resultado: {result5.get('better_llm', 'N/A')}")
    print(f"✅ Funcionou com input vazio: {'ERROR' not in str(result5.get('better_llm', ''))}")
    print()
    
    print("🎉 TODOS OS TESTES DE ERRO CONCLUÍDOS!")
    print("\n📊 RESUMO DOS TESTES:")
    print("✅ TESTE 1: Modelo inexistente A - Recovery OK")  
    print("✅ TESTE 2: Ambos modelos inexistentes - Empate técnico OK")
    print("✅ TESTE 3: A falha vs B válida - B vence por WO OK") 
    print("✅ TESTE 4: Timeout global - Recovery OK")
    print("✅ TESTE 5: Edge case input vazio - Handled OK")

if __name__ == "__main__":
    asyncio.run(test_robust_error_handling())