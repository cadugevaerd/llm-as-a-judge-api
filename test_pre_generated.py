#!/usr/bin/env python3
"""
Teste das respostas pré-geradas
"""

import asyncio
import json
import sys
import os

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from laaj.workflow.workflow import main

async def test_all_modes():
    print("🧪 TESTANDO TODOS OS MODOS DE OPERAÇÃO\n")
    
    # Respostas pré-definidas para teste
    story_a = "Era uma vez três amigos: Ana, Bruno e Carlos. Eles se conheceram na escola e nunca mais se separaram. Fim."
    story_b = "João, Maria e Pedro eram inseparáveis. Desde pequenos dividiam tudo: brinquedos, segredos e sonhos. Uma amizade eterna."
    
    # TESTE 1: Modo Normal (sem pré-geradas)
    print("=" * 60)
    print("🤖 TESTE 1: MODO NORMAL (ambos LLMs via API)")
    print("=" * 60)
    
    result1 = await main("Amigos")
    print(f"✅ Vencedor: {result1['better_llm']}\n")
    
    # TESTE 2: Ambas pré-geradas (0 API calls)
    print("=" * 60)
    print("🎭 TESTE 2: MODO TESTE (ambas pré-geradas, 0 API calls)")
    print("=" * 60)
    
    result2 = await main(
        input="Amigos",
        pre_generated_response_a=story_a,
        pre_generated_response_b=story_b
    )
    print(f"✅ Vencedor: {result2['better_llm']}")
    print(f"📊 Resposta A usada: '{result2['response_a'][:50]}...'")
    print(f"📊 Resposta B usada: '{result2['response_b'][:50]}...'\n")
    
    # TESTE 3: Modo misto (A pré-gerada, B via LLM)
    print("=" * 60)
    print("🔀 TESTE 3: MODO MISTO (A pré-gerada, B via LLM)")
    print("=" * 60)
    
    result3 = await main(
        input="Amigos",
        pre_generated_response_a=story_a
    )
    print(f"✅ Vencedor: {result3['better_llm']}")
    print(f"📊 A foi pré-gerada: {result3['response_a'] == story_a}")
    print(f"📊 B foi via LLM: {len(result3['response_b']) > 100}\n")
    
    # TESTE 4: Modelos customizados com pré-geradas
    print("=" * 60)
    print("🎯 TESTE 4: MODELOS CUSTOMIZADOS + PRÉ-GERADAS")
    print("=" * 60)
    
    result4 = await main(
        input="Aventura",
        llm_a="qwen-3-instruct",
        llm_b="gpt-5",
        pre_generated_response_a="Uma aventura épica com dragões...",
        pre_generated_response_b="Três aventureiros partiram em uma jornada..."
    )
    print(f"✅ Vencedor: {result4['better_llm']}")
    print(f"🔧 Modelo A configurado: {result4['model_llm_a']}")
    print(f"🔧 Modelo B configurado: {result4['model_llm_b']}\n")
    
    print("🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")

if __name__ == "__main__":
    asyncio.run(test_all_modes())