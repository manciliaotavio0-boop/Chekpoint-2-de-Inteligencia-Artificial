"""
main.py — Ponto de entrada do Prompt Toolkit (Checkpoint 02 — FIAP)

Fluxo:
  inputs.json → prompt_builder → techniques (ZS/FS/CoT/Role)
              → llm_client → evaluator → report → output/
"""

import json
import os
import sys

from dotenv import load_dotenv

from src.llm_client import LLMClient
from src.tasks import TAREFAS
from src.techniques import zero_shot, few_shot, chain_of_thought, role_prompting
from src.evaluator import avaliar_todos, testar_temperatura
from src.report import ReportGenerator

load_dotenv()

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────
MODEL = os.getenv("MODEL", "gpt-oss:120b")
TEMPS_TESTE = [0.1, 0.5, 1.0]
OUTPUT_DIR = "output"


def carregar_json(caminho: str) -> dict | list:
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def obter_esperado(item: dict, nome_tarefa: str):
    """Extrai o campo esperado para a tarefa correta do item de inputs.json."""
    esperado = item.get("esperado", {})
    if isinstance(esperado, dict):
        return esperado.get(nome_tarefa, "")
    return esperado


def executar_tecnica(nome: str, tarefa: dict, input_texto: str,
                     exemplos: list, client: LLMClient) -> tuple[dict, dict]:
    """
    Monta e envia o prompt de uma técnica.
    Retorna (prompt_dict, resultado_llm).
    """
    if nome == "zero_shot":
        p = zero_shot(tarefa, input_texto)
    elif nome == "few_shot":
        p = few_shot(tarefa, input_texto, exemplos)
    elif nome == "cot":
        p = chain_of_thought(tarefa, input_texto, tarefa.get("passos_cot", []))
    elif nome == "role":
        p = role_prompting(tarefa, input_texto, tarefa.get("persona", "assistente_clinica"))
    else:
        raise ValueError(f"Técnica desconhecida: {nome}")

    resultado = client.chat(
        prompt=p["prompt"],
        system=p.get("system", ""),
        temp=0.3,
        max_tokens=500,
    )
    return p, resultado


def main():
    print("\n" + "=" * 60)
    print("  PROMPT TOOLKIT — FIAP Checkpoint 02")
    print("=" * 60)

    # 1. Carregar dados
    try:
        inputs_raw = carregar_json("data/inputs.json")
        exemplos_json = carregar_json("data/examples.json")
    except FileNotFoundError as e:
        print(f"  ERRO: arquivo de dados nao encontrado: {e}")
        sys.exit(1)

    client = LLMClient(model=MODEL)
    tecnicas = ["zero_shot", "few_shot", "cot", "role"]
    resultados: list[dict] = []

    # 2. Loop principal: tarefa × input × técnica
    for tarefa in TAREFAS:
        nome_tarefa = tarefa["nome"]
        exemplos = exemplos_json.get(nome_tarefa, tarefa.get("exemplos_few_shot", []))

        print(f"\n  TAREFA: {nome_tarefa}")
        print(f"  {'─' * 50}")

        for item in inputs_raw:
            input_texto = item.get("texto", item.get("input", ""))
            esperado = obter_esperado(item, nome_tarefa)

            for tec in tecnicas:
                print(f"    [{tec.upper():10}] input #{item.get('id', '?')}...", end=" ", flush=True)

                _, resultado_llm = executar_tecnica(
                    tec, tarefa, input_texto, exemplos, client
                )

                if "erro" in resultado_llm:
                    print(f"ERRO: {resultado_llm['erro']}")
                    continue

                resposta = resultado_llm["resposta"]
                print(f"ok | tokens={resultado_llm['tokens_prompt']}+{resultado_llm['tokens_resposta']}")

                resultados.append({
                    "tarefa":           nome_tarefa,
                    "tecnica":          tec,
                    "input_id":         item.get("id", "?"),
                    "resposta":         resposta,
                    "esperado":         str(esperado),
                    "tokens_prompt":    resultado_llm["tokens_prompt"],
                    "tokens_resposta":  resultado_llm["tokens_resposta"],
                    "tempo_ms":         resultado_llm["tempo_ms"],
                })

    if not resultados:
        print("\n  Nenhum resultado coletado. Verifique se o Ollama esta rodando.")
        sys.exit(1)

    # 3. Avaliação
    print("\n  Calculando acuracia...")
    resultados = avaliar_todos(resultados)

    # 4. Teste de temperatura no melhor prompt (primeira tarefa, zero_shot)
    print("\n  Testando temperaturas (0.1 / 0.5 / 1.0)...")
    prompt_temp = zero_shot(TAREFAS[0], inputs_raw[0].get("texto", ""))
    resultados_temp = testar_temperatura(
        prompt=prompt_temp["prompt"],
        temps=TEMPS_TESTE,
        llm_client=client,
    )

    # 5. Relatório
    print("\n  Gerando relatorio...")
    rep = ReportGenerator(resultados, output_dir=OUTPUT_DIR)
    rep.gerar_csv()
    rep.imprimir_tabela()
    rep.grafico_acuracia()
    rep.grafico_custo()
    rep.grafico_temperatura(resultados_temp)
    rep.recomendar()

    print("=" * 60)
    print("  Execucao concluida! Veja a pasta output/")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
