#!/usr/bin/env python3
"""
Teste do sistema de timeout global
"""

import asyncio
import sys
import os

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from laaj.workflow.workflow import main

async def test_timeout_scenarios():
    print("🧪 TESTANDO SISTEMA DE TIMEOUT\n")
    
    # TESTE 1: Workflow normal (dentro do timeout padrão de 120s)
    print("=" * 60)
    print("✅ TESTE 1: WORKFLOW NORMAL (timeout 120s)")
    print("=" * 60)
    
    result1 = await main("Amigos")  # Timeout padrão 120s
    print(f"✅ Resultado: {result1.get('better_llm', 'N/A')}")
    print(f"⏰ Status: {'SUCESSO' if 'TIMEOUT_ERROR' not in str(result1.get('better_llm', '')) else 'TIMEOUT'}\n")
    
    # TESTE 2: Timeout muito baixo com respostas pré-geradas (deve funcionar)
    print("=" * 60) 
    print("🎭 TESTE 2: TIMEOUT BAIXO + PRÉ-GERADAS (deve funcionar)")
    print("=" * 60)
    
    result2 = await main(
        input="Amigos",
        pre_generated_response_a="História rápida A",
        pre_generated_response_b="História rápida B", 
        timeout_seconds=10  # Timeout muito baixo, mas com pré-geradas deve funcionar
    )
    print(f"✅ Resultado: {result2.get('better_llm', 'N/A')}")
    print(f"⏰ Status: {'SUCESSO' if 'TIMEOUT_ERROR' not in str(result2.get('better_llm', '')) else 'TIMEOUT'}\n")
    
    # TESTE 3: Timeout muito baixo sem pré-geradas (deve dar timeout)
    print("=" * 60)
    print("⏰ TESTE 3: TIMEOUT BAIXO + LLMs REAIS (deve dar timeout)")
    print("=" * 60)
    
    result3 = await main(
        input="Amigos",
        timeout_seconds=5  # Timeout impossível para LLMs reais
    )
    print(f"⚠️  Resultado: {result3.get('better_llm', 'N/A')}")
    print(f"⏰ Status: {'TIMEOUT (esperado)' if 'TIMEOUT_ERROR' in str(result3.get('better_llm', '')) else 'INESPERADO'}\n")
    
    # TESTE 4: Timeout customizado médio
    print("=" * 60)
    print("🎯 TESTE 4: TIMEOUT CUSTOMIZADO (60s)")
    print("=" * 60)
    
    result4 = await main(
        input="Aventura",
        timeout_seconds=60  # Timeout menor que padrão
    )
    print(f"✅ Resultado: {result4.get('better_llm', 'N/A')}")
    print(f"⏰ Status: {'SUCESSO' if 'TIMEOUT_ERROR' not in str(result4.get('better_llm', '')) else 'TIMEOUT'}\n")
    
    print("🎉 TODOS OS TESTES DE TIMEOUT CONCLUÍDOS!")

if __name__ == "__main__":
    asyncio.run(test_timeout_scenarios())