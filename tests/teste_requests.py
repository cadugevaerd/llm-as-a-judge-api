import requests
import json

# url_base = "http://localhost:8000"
url_base = "http://laaj.local:30080"

# Teste 1: Root endpoint
print("=== Teste 1: Root endpoint ===")
response = requests.get(url_base + "/")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Teste 2: Health check
print("\n=== Teste 2: Health check ===")
response = requests.get(url_base + "/api/v1/health/")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Teste 3: Listar modelos
print("\n=== Teste 3: Listar modelos ===")
response = requests.get(url_base + "/api/v1/models/")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Teste 4: Comparação individual com modelo padrão
print("\n=== Teste 4: Comparação individual (modelo padrão) ===")
compare_data = {
    "input": "Explique os princípios fundamentais da teoria da relatividade de Einstein e suas implicações para nossa compreensão do universo.",
    "response_a": "A teoria da relatividade de Einstein revolucionou nossa compreensão do espaço e tempo. A relatividade especial (1905) estabeleceu que o espaço e o tempo são entrelaçados em um continuum espaço-temporal, onde nada pode viajar mais rápido que a luz. Isso significa que simultaneidade é relativa - eventos que parecem simultâneos para um observador podem não ser para outro em movimento. A relatividade geral (1915) descreveu a gravidade não como uma força, mas como a curvatura do espaço-tempo causada pela massa e energia. Isso explica desde o periélio de Mercúrio até a existência de buracos negros e ondas gravitacionais, transformando completamente nossa visão cosmológica do universo.",
    "response_b": "Einstein fez duas teorias importantes. A primeira é sobre velocidade da luz ser sempre igual. A segunda é sobre gravidade ser curvatura no espaço. Isso mudou como pensamos sobre o universo e explica coisas como GPS funcionando.",
    "model_a_name": "expert-physicist",
    "model_b_name": "student"
}
response = requests.post(url_base + "/api/v1/compare/", json=compare_data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Teste 5: Comparação individual com Claude Haiku
print("\n=== Teste 5: Comparação individual (Claude Haiku) ===")
compare_data_claude = {
    "input": "Analise os prós e contras da implementação de um sistema de renda básica universal em países em desenvolvimento, considerando aspectos econômicos, sociais e políticos.",
    "response_a": "A implementação de renda básica universal (RBU) em países em desenvolvimento apresenta vantagens significativas: redução direta da pobreza extrema, simplificação de sistemas de assistência social complexos e burocráticos, estímulo ao empreendedorismo local, e maior segurança alimentar. Economicamente, pode aumentar o consumo interno e gerar multiplicador econômico positivo. Socialmente, oferece dignidade e autonomia aos beneficiários, especialmente mulheres e jovens. No entanto, os desafios são substanciais: alto custo fiscal que pode exigir 10-20% do PIB, risco de inflação se mal implementado, possível redução de incentivos ao trabalho formal, e necessidade de sistemas de identificação e pagamento robustos. Politicamente, requer consenso amplo e pode enfrentar resistência de elites tradicionais. O sucesso depende de design cuidadoso, implementação gradual e forte capacidade institucional.",
    "response_b": "Renda básica universal é quando governo dá dinheiro para todos. É bom porque ajuda pobres e é ruim porque custa caro. Países pobres podem ter problema com inflação. Precisa pensar bem antes de fazer.",
    "model_a_name": "policy-expert",
    "model_b_name": "basic-user",
    "judge_model": "claude-3-5-haiku-latest"
}
response = requests.post(url_base + "/api/v1/compare/", json=compare_data_claude)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Teste 6: Comparação individual com GPT-5
print("\n=== Teste 6: Comparação individual (GPT-5) ===")
compare_data_gpt = {
    "input": "Desenvolva uma estratégia completa para mitigar os riscos de segurança cibernética em uma empresa de tecnologia financeira (fintech) que processa milhões de transações diárias.",
    "response_a": "Estratégia de segurança cibernética para fintech deve ser multicamada: 1) Arquitetura zero-trust com autenticação multifator obrigatória e segmentação de rede rigorosa; 2) Criptografia end-to-end para dados em trânsito e em repouso usando AES-256 e TLS 1.3; 3) Monitoramento contínuo com SIEM/SOAR para detecção de anomalias em tempo real e resposta automatizada a incidentes; 4) DevSecOps integrado com testes de penetração regulares, análise de vulnerabilidades automatizada e pipeline de CI/CD seguro; 5) Backup 3-2-1 com testes de recuperação mensais e RPO/RTO de 15 minutos; 6) Treinamento contínuo de conscientização em segurança para funcionários e simulações de phishing; 7) Compliance rigoroso com PCI-DSS, ISO 27001 e regulamentações locais; 8) Contratos robustos com fornecedores incluindo auditorias de segurança; 9) Plano de resposta a incidentes testado e equipe de resposta 24/7; 10) Seguro cibernético adequado cobrindo perdas operacionais e responsabilidade civil.",
    "response_b": "Para proteger empresa fintech precisa ter firewall bom, antivírus atualizado, senha forte para funcionários, backup dos dados importantes, e chamar especialista quando tem problema. Também é importante ter seguro e seguir as leis.",
    "model_a_name": "cybersecurity-expert",
    "model_b_name": "basic-assistant",
    "judge_model": "openai/gpt-5"
}
response = requests.post(url_base + "/api/v1/compare/", json=compare_data_gpt)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Teste 7: Comparação batch com modelo padrão
print("\n=== Teste 7: Comparação batch (modelo padrão) ===")
batch_data = {
    "comparisons": [
        {
            "input": "Compare as vantagens e desvantagens das arquiteturas de microserviços versus arquitetura monolítica para uma aplicação de e-commerce de grande escala.",
            "response_a": "Microserviços oferecem escalabilidade independente de cada componente (catálogo, pagamento, inventário), facilitam desenvolvimento paralelo por equipes, permitem tecnologias diversas por serviço, e fornecem isolamento de falhas - se o serviço de recomendações falhar, o checkout continua funcionando. Para e-commerce, isso significa poder escalar o serviço de catálogo durante Black Friday sem desperdiçar recursos em outros componentes. Porém, introduzem complexidade de rede, latência entre serviços, desafios de consistência de dados (transações distribuídas), e overhead operacional com orquestração, monitoramento e deployment. Monólitos são mais simples para começar, têm menor latência interna, transações ACID garantidas, e debugging mais direto. Contudo, toda a aplicação deve usar a mesma tecnologia, deployments são all-or-nothing, e escalabilidade é limitada pelo componente mais exigente.",
            "response_b": "Microserviços são pequenos e monólitos são grandes. Microserviços são mais difíceis de gerenciar mas podem crescer melhor. Monólitos são mais fáceis mas podem ter problemas quando ficam muito grandes. Para e-commerce, depende do tamanho da empresa.",
            "model_a_name": "senior-architect",
            "model_b_name": "junior-developer"
        },
        {
            "input": "Analise o impacto das mudanças climáticas na agricultura brasileira e proponha soluções tecnológicas sustentáveis para aumentar a produtividade.",
            "response_a": "As mudanças climáticas afetam drasticamente a agricultura brasileira: aumento de temperatura de 1-3°C até 2050 reduzirá produtividade de soja e milho no Cerrado; alteração de padrões de chuva compromete cultivos no Nordeste; eventos extremos (secas/enchentes) aumentaram 40% na última década. Soluções tecnológicas incluem: 1) Agricultura de precisão com sensores IoT, drones e satélites para otimização de irrigação e aplicação de insumos; 2) Biotecnologia para desenvolver cultivares resistentes ao estresse hídrico e térmico; 3) Sistema de plantio direto e rotação de culturas para melhorar retenção de água e carbono no solo; 4) Integração lavoura-pecuária-floresta (ILPF) para diversificação e sequestro de carbono; 5) Irrigação inteligente com reuso de água e energia solar; 6) Biodefensivos e controle biológico para reduzir dependência química; 7) Blockchain para rastreabilidade e certificação sustentável; 8) Inteligência artificial para previsão climática e otimização de plantio.",
            "response_b": "O clima está mudando e isso é ruim para plantação no Brasil. Pode ter menos chuva ou mais calor. Para resolver, pode usar tecnologia moderna, irrigação melhor, plantas mais resistentes e cuidar melhor do solo. Também é bom usar energia limpa e aplicativos para ajudar os fazendeiros.",
            "model_a_name": "agro-specialist",
            "model_b_name": "general-assistant"
        },
        {
            "input": "Explique como o blockchain pode revolucionar o sistema financeiro tradicional, abordando casos de uso específicos, desafios técnicos e implicações regulatórias.",
            "response_a": "O blockchain pode transformar o sistema financeiro através de: 1) DeFi (Finanças Descentralizadas) eliminando intermediários em empréstimos, seguros e trading com smart contracts automatizados e auditáveis; 2) Pagamentos transfronteiriços instantâneos e de baixo custo via stablecoins, substituindo SWIFT; 3) Tokenização de ativos reais (imóveis, commodities) democratizando investimentos e aumentando liquidez; 4) Identidade digital soberana reduzindo KYC/AML redundante; 5) Trade finance automatizado com cartas de crédito digitais. Desafios técnicos: escalabilidade (Bitcoin 7 TPS vs Visa 65.000 TPS), consumo energético do proof-of-work, experiência de usuário complexa, e interoperabilidade entre blockchains. Implicações regulatórias: necessidade de frameworks para stablecoins, classificação de tokens como securities, AML/CFT em DeFi, proteção ao consumidor, e CBDCs competindo com criptomoedas. Reguladores buscam equilibrar inovação com estabilidade sistêmica.",
            "response_b": "Blockchain é como um livro digital que não pode ser alterado. No sistema financeiro, pode ser usado para pagamentos mais rápidos e baratos, eliminar bancos intermediários e fazer contratos automáticos. Os problemas são velocidade baixa, gasto de energia e regras do governo que ainda não existem direito.",
            "model_a_name": "blockchain-expert",
            "model_b_name": "basic-user"
        }
    ]
}
response = requests.post(url_base + "/api/v1/compare/batch", json=batch_data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Teste 8: Comparação batch com Claude Sonnet 4.0
print("\n=== Teste 8: Comparação batch (Claude Sonnet 4.0) ===")
batch_data_claude = {
    "comparisons": [
        {
            "input": "Desenvolva uma análise SWOT completa para uma startup de inteligência artificial que pretende competir no mercado de chatbots empresariais.",
            "response_a": "**Forças:** Equipe técnica especializada em ML/NLP, agilidade de startup para inovação rápida, capacidade de personalização para nichos específicos, menor overhead que grandes corporações permitindo preços competitivos. **Fraquezas:** Recursos limitados para R&D intensivo, marca desconhecida versus gigantes estabelecidos, dificuldade para escalar infraestrutura globalmente, dependência de poucos talentos chave. **Oportunidades:** Crescimento exponencial do mercado de IA conversacional (CAGR 23%), demanda por soluções específicas de indústria que grandes players negligenciam, parcerias com consultorias especializadas, expansão internacional em mercados emergentes menos saturados. **Ameaças:** Competição direta com Microsoft (Copilot), Google (Bard for Business) e OpenAI (GPT for Enterprise) que têm recursos ilimitados, risco de commoditização da tecnologia, mudanças regulatórias sobre IA, possibilidade de aquisição predatória por concorrentes maiores.",
            "response_b": "Forças: time bom, empresa pequena e rápida. Fraquezas: pouco dinheiro, ninguém conhece. Oportunidades: mercado crescendo, pode fazer coisas específicas. Ameaças: empresas grandes como Google e Microsoft são muito fortes.",
            "model_a_name": "business-analyst",
            "model_b_name": "intern",
            "judge_model": "claude-sonnet-4-0"
        },
        {
            "input": "Explique como a computação quântica pode impactar a criptografia atual e quais são as implicações para a segurança da informação nos próximos 20 anos.",
            "response_a": "A computação quântica representa uma ameaça existencial à criptografia atual através do algoritmo de Shor, que pode quebrar RSA, ECC e criptografia de chave pública em tempo polinomial. Computadores quânticos com ~4000 qubits lógicos (estimados para 2040-2050) poderão descriptografar dados protegidos por RSA-2048 em horas. Isso significa que dados sigilosos criptografados hoje (dados médicos, financeiros, militares) estarão vulneráveis quando essa tecnologia amadurecer - conceito 'harvest now, decrypt later'. Contramedidas já em desenvolvimento: criptografia pós-quântica (algoritmos baseados em lattices, códigos, multivariados) sendo padronizada pelo NIST; protocolos híbridos combinando métodos clássicos e pós-quânticos; distribuição quântica de chaves (QKD) para comunicações ultrasseguras. Organizações devem iniciar migração agora: inventário de sistemas criptográficos, implementação gradual de algoritmos resistentes a quânticos, e desenvolvimento de estratégias de crypto-agilidade para futuras transições.",
            "response_b": "Computação quântica pode quebrar senhas atuais porque é muito mais rápida. Isso é perigoso para segurança na internet. Cientistas estão fazendo novas formas de criptografia que computadores quânticos não conseguem quebrar. Empresas precisam se preparar para trocar seus sistemas de segurança.",
            "model_a_name": "quantum-security-expert",
            "model_b_name": "tech-blogger",
            "judge_model": "claude-sonnet-4-0"
        }
    ]
}
response = requests.post(url_base + "/api/v1/compare/batch", json=batch_data_claude)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Teste 9: Comparação batch com Gemini 2.5 Flash
print("\n=== Teste 9: Comparação batch (Gemini 2.5 Flash) ===")
batch_data_gemini = {
    "comparisons": [
        {
            "input": "Analise as estratégias de marketing digital mais eficazes para uma empresa B2B de software empresarial em 2024, incluindo métricas de ROI e tendências emergentes.",
            "response_a": "Estratégias B2B software 2024: 1) **Account-Based Marketing (ABM)** personalizado com identificação de contas-alvo via intent data e engajamento multicanal (LinkedIn, email, retargeting), ROI médio 25-30% superior ao marketing tradicional; 2) **Content Marketing técnico** com case studies, whitepapers e webinars demonstrando ROI específico do produto - converte 3x mais que conteúdo genérico; 3) **LinkedIn Sales Navigator** e outreach social selling - gera 45% mais oportunidades que cold email; 4) **Marketing de influenciadores B2B** com líderes de indústria e analistas (Gartner, Forrester) - aumenta brand awareness em 67%; 5) **SEO técnico** focado em long-tail keywords específicas da indústria; 6) **Automação de marketing** com lead scoring baseado em comportamento e fit; 7) **Video marketing** com demos de produto e customer success stories - aumenta conversão em 80%. Métricas chave: CAC, LTV/CAC ratio >3:1, pipeline velocity, MQL-SQL conversion rate >25%.",
            "response_b": "Marketing B2B precisa usar LinkedIn para encontrar clientes, fazer conteúdo interessante como vídeos e artigos, usar SEO para aparecer no Google, e automatizar emails. É importante medir resultados e ver qual estratégia funciona melhor para gastar dinheiro certo.",
            "model_a_name": "b2b-marketing-director",
            "model_b_name": "marketing-trainee",
            "judge_model": "google/gemini-2.5-flash"
        },
        {
            "input": "Examine os desafios éticos da inteligência artificial generativa na criação de conteúdo, incluindo questões de propriedade intelectual, viés algorítmico e impacto no mercado de trabalho criativo.",
            "response_a": "Desafios éticos da IA generativa são complexos e multifacetados: **Propriedade Intelectual:** Modelos treinados em milhões de obras protegidas sem consentimento explícito geram questões sobre fair use versus violação de copyright. Casos como Getty Images vs Stability AI estabelecerão precedentes legais. **Viés Algorítmico:** Datasets históricos perpetuam estereótipos (sub-representação de minorias, associações enviesadas), exigindo técnicas de debiasing e datasets mais diversos. **Impacto no Trabalho:** Automação ameaça ilustradores, redatores, designers - estudo do Goldman Sachs projeta 18% de empregos criativos em risco. **Soluções emergentes:** Sistemas de compensação para criadores (como Shutterstock AI), watermarking de conteúdo AI (projeto C2PA), regulamentações como AI Act europeu, e modelos de colaboração humano-AI onde ferramentas amplificam criatividade ao invés de substituir. Necessária governança proativa com stakeholders criativos na mesa de decisão.",
            "response_b": "IA generativa tem problemas éticos como usar trabalhos de artistas sem permissão, ter preconceitos nos resultados, e pode tirar emprego de pessoas criativas. Precisa de regras melhores e compensação justa para artistas.",
            "model_a_name": "ai-ethics-researcher",
            "model_b_name": "concerned-citizen",
            "judge_model": "google/gemini-2.5-flash"
        }
    ]
}
response = requests.post(url_base + "/api/v1/compare/batch", json=batch_data_gemini)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Teste 10: Comparação individual com modelo inexistente (teste de erro)
print("\n=== Teste 10: Comparação individual (modelo inexistente) ===")
compare_data_invalid = {
    "input": "Teste de modelo que não existe no sistema.",
    "response_a": "Esta é uma resposta detalhada e técnica que demonstra conhecimento profundo sobre o assunto, incluindo referências específicas, dados quantitativos e análise crítica aprofundada.",
    "response_b": "Esta é uma resposta simples e básica sobre o tema.",
    "model_a_name": "expert-system",
    "model_b_name": "basic-bot",
    "judge_model": "modelo-que-nao-existe-xyz-123"
}
response = requests.post(url_base + "/api/v1/compare/", json=compare_data_invalid)
print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2, ensure_ascii=False))

# Teste 11: Comparação batch com modelo inexistente (teste de erro)
print("\n=== Teste 11: Comparação batch (modelo inexistente) ===")
batch_data_invalid = {
    "comparisons": [
        {
            "input": "Teste de erro com modelo inexistente para batch.",
            "response_a": "Resposta técnica completa com análise detalhada, métricas específicas, casos de uso práticos e recomendações baseadas em evidências empíricas.",
            "response_b": "Resposta básica e genérica sobre o assunto.",
            "model_a_name": "advanced-ai",
            "model_b_name": "simple-ai",
            "judge_model": "outro-modelo-inexistente-abc-456"
        },
        {
            "input": "Segunda comparação com modelo inválido.",
            "response_a": "Análise profunda com contextualização histórica, comparações internacionais, dados estatísticos relevantes e projeções futuras fundamentadas.",
            "response_b": "Explicação superficial do tópico.",
            "model_a_name": "research-bot",
            "model_b_name": "casual-bot",
            "judge_model": "modelo-fantasma-999"
        }
    ]
}
response = requests.post(url_base + "/api/v1/compare/batch", json=batch_data_invalid)
print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2, ensure_ascii=False))
