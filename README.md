# Prompt Toolkit — Checkpoint 02

Projeto desenvolvido para o Checkpoint 02 da disciplina de Prompt Engineering & Artificial Intelligence da FIAP.

O objetivo do projeto é construir um toolkit em Python capaz de aplicar automaticamente diferentes técnicas de prompting em tarefas de negócio, comparar os resultados e recomendar a melhor abordagem.

---

# Integrantes

- Otávio Mancilia - RM: 570225
- Marcos Paulo Sampaio - RM:573987
- Gabriela Angel - RM: 570808
- Izabelly Menezes - RM: 570673
- Tiago Muhlmann - RM: 569569
- Wesley Marques - RM: 573915

---

# Objetivo do Projeto

O sistema recebe tarefas definidas pelo grupo e executa automaticamente 4 técnicas de prompting:

- Zero-Shot
- Few-Shot
- Chain-of-Thought (CoT)
- Role Prompting

Para cada técnica o sistema:

- monta o prompt
- envia para o modelo LLM via Ollama
- mede tempo e tokens
- compara os resultados
- gera relatórios e gráficos automáticos

---

# Stack Utilizada

- Python 3.10+
- Ollama API
- Modelo local via Ollama
- requests
- tiktoken
- pandas
- matplotlib
- python-dotenv

---

# Estrutura do Projeto

```bash
prompt-toolkit/
│
├── README.md
├── requirements.txt
├── .env.example
├── main.py
│
├── src/
│   ├── __init__.py
│   ├── llm_client.py
│   ├── prompt_builder.py
│   ├── techniques.py
│   ├── tasks.py
│   ├── evaluator.py
│   └── report.py
│
├── data/
│   ├── inputs.json
│   └── examples.json
│
├── prompts/
│   ├── system_prompts.json
│   └── templates.json
│
├── output/
│   ├── resultados.csv
│   └── graficos/
│
└── docs/
    └── CP02_NomeDoGrupo.pdf
```

---

# Instalação

## 1. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
```

## 2. Entrar na pasta

```bash
cd prompt-toolkit
```

---

# Criar ambiente virtual

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Instalar dependências

```bash
pip install -r requirements.txt
```

---

# Configuração do Ollama

Instale o Ollama:

- https://ollama.com/

Depois baixe o modelo utilizado:

```bash
ollama pull gpt-oss:120b
```

Inicie o servidor:

```bash
ollama serve
```

---

# Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`

Exemplo:

```env
OLLAMA_HOST=http://localhost:11434
```

---

# Executando o Projeto

Rodar o sistema principal:

```bash
python main.py
```

O fluxo executado será:

1. Carregar tarefas e inputs
2. Aplicar as 4 técnicas de prompting
3. Enviar prompts para o Ollama
4. Medir tempo e tokens
5. Comparar resultados
6. Gerar CSV e gráficos automáticos

---

# Técnicas Implementadas

## Zero-Shot

Prompt direto sem exemplos.

## Few-Shot

Prompt com exemplos de entrada e saída.

## Chain-of-Thought

Prompt orientado a raciocínio passo a passo.

## Role Prompting

Uso de personas especializadas através de system prompts.

---

# Métricas Avaliadas

O sistema mede automaticamente:

- Tokens de prompt
- Tokens de resposta
- Tempo de execução
- Consistência
- Acurácia
- Custo médio por técnica

---

# Saídas Geradas

Os resultados serão salvos em:

```bash
output/
```

Arquivos gerados:

- resultados.csv
- gráficos PNG
- recomendações automáticas

---

# Exemplo de Execução

```bash
python main.py
```

Exemplo de saída:

```bash
Tarefa: Classificação de sentimento
Técnica vencedora: Few-Shot
Acurácia: 92%
Tempo médio: 850ms
```

---

# Requisitos do Projeto

Segundo especificação do checkpoint:

- Projeto modular em Python
- Uso obrigatório de Ollama
- Uso obrigatório de tiktoken
- Uso obrigatório de pandas e matplotlib
- 4 técnicas de prompting
- 3 ou mais tarefas
- 5 inputs reais por tarefa

---

# Disciplina

FIAP — Prompt Engineering & Artificial Intelligence

Checkpoint 02 — Prompt Toolkit
