🧑‍💻 Pessoa 1 — Infraestrutura & Configuração
Responsabilidade: Montar a base do projeto para todo o grupo trabalhar.
O que fazer:

Criar a estrutura de pastas exata descrita no PDF (src/, data/, prompts/, output/, docs/)
Criar requirements.txt com as dependências (requests, tiktoken, matplotlib, pandas, python-dotenv)
Criar .env.example com a variável do host do Ollama
Criar o repositório no GitHub e adicionar todos os membros
Escrever o README.md com instruções de instalação e execução
Implementar src/llm_client.py: classe LLMClient com método chat() que chama a API REST do Ollama em http://localhost:11434/api/chat, trata erros (timeout, retry) e retorna {"resposta", "tokens_prompt", "tokens_resposta", "tempo_ms"}


🧑‍💻 Pessoa 2 — Construtor de Prompts
Responsabilidade: Módulo que monta os prompts corretamente.
O que fazer:

Implementar src/prompt_builder.py com 3 funções:

montar_prompt(instrucao, contexto, input_dados, formato_output) — separa instrução de dados
adicionar_exemplos(prompt, exemplos) — adiciona exemplos para few-shot
adicionar_cot(prompt, passos) — adiciona passos de raciocínio para CoT


Garantir validação: nenhum campo pode estar vazio
Criar prompts/templates.json com templates de prompt para cada tarefa do domínio


🧑‍💻 Pessoa 3 — As 4 Técnicas de Prompting
Responsabilidade: O coração do projeto — implementar as técnicas.
O que fazer:

Implementar src/techniques.py com 4 funções:

zero_shot(tarefa, input) — prompt direto, sem exemplos
few_shot(tarefa, input, exemplos) — prompt com 2-3 exemplos no formato Input: "..." → Output: "..."
chain_of_thought(tarefa, input, passos) — prompt com raciocínio explícito ("Analise passo a passo: 1... 2... 3...")
role_prompting(tarefa, input, persona) — usa system prompt com persona detalhada, retorna tupla (system, user)


Criar prompts/system_prompts.json com pelo menos 2 personas detalhadas para o domínio (incluir: experiência, especialidade, tom de voz, limitações — não basta "Você é um assistente")


🧑‍💻 Pessoa 4 — Tarefas do Domínio & Dados
Responsabilidade: Definir o que o toolkit vai analisar e alimentar com dados reais.
O que fazer:

Escolher o domínio do grupo (ex: e-commerce, saúde, RH, jurídico...)
Implementar src/tasks.py com 3 ou mais tarefas, cada uma com: nome, tipo, instrução, formato de output, exemplos few-shot, passos CoT e persona associada. Os tipos obrigatórios são: Classificação + Extração + pelo menos mais um (Sumarização ou Geração)
Criar data/inputs.json com 5 inputs reais (textos realistas do domínio, não genéricos) e o output esperado para cada tarefa
Criar data/examples.json com exemplos para few-shot


🧑‍💻 Pessoa 5 — Avaliador & Relatório
Responsabilidade: Medir os resultados e gerar o relatório automático.
O que fazer:

Implementar src/evaluator.py com:

contar_tokens(texto) via tiktoken
medir_acuracia(resposta, esperado) — match exato ou por keywords
medir_consistencia(respostas[]) — roda a mesma pergunta N vezes, calcula % de respostas iguais
testar_temperatura(prompt, temps) — roda com temperaturas 0.1, 0.5 e 1.0


Implementar src/report.py com:

gerar_tabela(resultados) — DataFrame pandas, salva CSV em output/resultados.csv
grafico_acuracia(resultados) — barras agrupadas por técnica
grafico_custo(resultados) — tokens médios por técnica
grafico_temperatura(resultados) — consistência por temperatura
recomendar(resultados) — imprime qual técnica foi melhor por tarefa e por quê




🧑‍💻 Pessoa 6 — Orquestrador & Documentação
Responsabilidade: Fazer tudo funcionar junto e documentar o projeto.
O que fazer:

Implementar main.py seguindo exatamente o fluxo descrito: carrega configs → para cada tarefa aplica as 4 técnicas em cada input → chama evaluator → chama report
Testar a integração completa (garantir que tudo roda com python main.py)
Escrever o PDF de documentação (4-6 páginas) com: capa com nomes e RMs, descrição do domínio, diagrama do fluxo (pode ser feito no draw.io), stack técnica, tabela de resultados com screenshots dos gráficos, guia de bolso ("quando usar cada técnica") e reflexão do grupo


⚡ Dica de ordem de execução
Para não travar, o grupo deve trabalhar nessa sequência:
Pessoa 1 (infra + llm_client) 
    → Pessoa 2 (prompt_builder) 
    → Pessoa 4 (tasks + dados) 
    → Pessoa 3 (techniques) 
    → Pessoa 5 (evaluator + report) 
    → Pessoa 6 (main.py + integração + PDF)
Pessoas 1 e 4 podem começar ao mesmo tempo. Pessoa 6 só finaliza o main.py depois que os outros módulos estiverem prontos, mas já pode ir escrevendo o PDF.
