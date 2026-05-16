"""
techniques.py — 4 técnicas de prompting (Aulas 06 + 07)

Cada função recebe uma tarefa (dict de tasks.py) + o texto de input
e retorna um dict pronto para ser enviado ao LLMClient.chat():
    {
        "prompt": str,   # mensagem do usuário
        "system": str,   # system prompt (vazio se não usar Role)
    }
"""

import json
from src.prompt_builder import montar_prompt, adicionar_exemplos, adicionar_cot


def _carregar_system_prompts() -> dict:
    """Carrega as personas definidas em prompts/system_prompts.json."""
    try:
        with open("prompts/system_prompts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# ─────────────────────────────────────────────────────────────
# 1. ZERO-SHOT
# ─────────────────────────────────────────────────────────────
def zero_shot(tarefa: dict, input_texto: str) -> dict:
    """
    Monta um prompt direto sem exemplos.
    Instrução clara + formato de output definido.
    Ref: Aula 06
    """
    prompt = montar_prompt(
        instrucao=tarefa["instrucao"],
        contexto="",
        input_dados=input_texto,
        formato_output=tarefa["formato_output"],
    )
    return {"prompt": prompt, "system": ""}


# ─────────────────────────────────────────────────────────────
# 2. FEW-SHOT
# ─────────────────────────────────────────────────────────────
def few_shot(tarefa: dict, input_texto: str, exemplos: list[dict]) -> dict:
    """
    Monta prompt com 2-3 exemplos no formato Input/Output.
    exemplos: lista de dicts com chaves 'input' e 'output'.
    Ref: Aula 06
    """
    prompt_base = montar_prompt(
        instrucao=tarefa["instrucao"],
        contexto="",
        input_dados=input_texto,
        formato_output=tarefa["formato_output"],
    )

    # Converte lista de dicts para lista de tuplas (input, output)
    pares = []
    for ex in exemplos:
        saida = ex["output"]
        if isinstance(saida, dict):
            saida = json.dumps(saida, ensure_ascii=False)
        pares.append((ex["input"], saida))

    prompt_final = adicionar_exemplos(prompt_base, pares)
    return {"prompt": prompt_final, "system": ""}


# ─────────────────────────────────────────────────────────────
# 3. CHAIN-OF-THOUGHT (CoT)
# ─────────────────────────────────────────────────────────────
def chain_of_thought(tarefa: dict, input_texto: str, passos: list[str]) -> dict:
    """
    Monta prompt com instrução de raciocínio explícito passo a passo.
    Ref: Aula 06
    """
    prompt_base = montar_prompt(
        instrucao=tarefa["instrucao"],
        contexto="",
        input_dados=input_texto,
        formato_output=tarefa["formato_output"],
    )

    prompt_final = adicionar_cot(prompt_base, passos)
    return {"prompt": prompt_final, "system": ""}


# ─────────────────────────────────────────────────────────────
# 4. ROLE PROMPTING
# ─────────────────────────────────────────────────────────────
def role_prompting(tarefa: dict, input_texto: str, persona_key: str) -> dict:
    """
    Usa system prompt com persona detalhada de system_prompts.json.
    Retorna dict com 'system' preenchido.
    Ref: Aula 07
    """
    system_prompts = _carregar_system_prompts()
    persona = system_prompts.get(persona_key, {})

    if persona:
        system_text = persona.get("system_prompt", str(persona))
    else:
        system_text = f"Você é um especialista em {persona_key}."

    prompt = montar_prompt(
        instrucao=tarefa["instrucao"],
        contexto="",
        input_dados=input_texto,
        formato_output=tarefa["formato_output"],
    )

    return {"prompt": prompt, "system": system_text}
