"""
evaluator.py — Métricas de qualidade, tokens e consistência (Aula 08)
"""

import json
import time
import tiktoken


# ─────────────────────────────────────────────────────────────
# 1. CONTAR TOKENS
# ─────────────────────────────────────────────────────────────
def contar_tokens(texto: str) -> int:
    """Conta tokens via tiktoken (cl100k_base); fallback por palavras se offline."""
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(texto))
    except Exception:
        # Fallback: estimativa por palavras (~1.3 tokens por palavra em PT-BR)
        return int(len(texto.split()) * 1.3)


# ─────────────────────────────────────────────────────────────
# 2. MEDIR ACURÁCIA
# ─────────────────────────────────────────────────────────────
def medir_acuracia(resposta: str, esperado) -> float:
    """
    Compara a resposta do LLM com o valor esperado.
    Suporta: match exato, keyword match e comparação de dicts (JSON).
    Retorna float entre 0.0 e 1.0.
    """
    # Se esperado for dict, serializa para comparar como JSON
    if isinstance(esperado, dict):
        esperado = json.dumps(esperado, ensure_ascii=False, sort_keys=True)

    resposta_norm = str(resposta).strip().upper()
    esperado_norm = str(esperado).strip().upper()

    # Estratégia 1: match exato
    if resposta_norm == esperado_norm:
        return 1.0

    # Estratégia 2: keyword — o esperado está contido na resposta
    if esperado_norm in resposta_norm:
        return 1.0

    # Estratégia 3: comparação de JSONs (extração de dados)
    try:
        resp_dict = json.loads(resposta)
        esp_dict = json.loads(esperado)
        if resp_dict == esp_dict:
            return 1.0
        chaves = set(esp_dict.keys())
        acertos = sum(
            1 for k in chaves
            if str(resp_dict.get(k, "")).strip().upper() == str(esp_dict.get(k, "")).strip().upper()
        )
        return round(acertos / len(chaves), 2) if chaves else 0.0
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass

    return 0.0


# ─────────────────────────────────────────────────────────────
# 3. MEDIR CONSISTÊNCIA
# ─────────────────────────────────────────────────────────────
def medir_consistencia(respostas: list) -> float:
    """
    Mede se o modelo responde a mesma coisa quando perguntado várias vezes.
    Temp baixa → consistente. Temp alta → varia.
    Retorna float entre 0.0 e 1.0 (% da resposta mais frequente).
    """
    if not respostas:
        return 0.0
    if len(respostas) == 1:
        return 1.0

    respostas_norm = [str(r).strip().upper() for r in respostas]
    contagem: dict = {}
    for r in respostas_norm:
        contagem[r] = contagem.get(r, 0) + 1

    mais_frequente = max(contagem.values())
    return round(mais_frequente / len(respostas_norm), 2)


# ─────────────────────────────────────────────────────────────
# 4. TESTAR TEMPERATURA
# ─────────────────────────────────────────────────────────────
def testar_temperatura(prompt: str, temps: list, llm_client=None) -> list:
    """
    Roda o mesmo prompt com diferentes valores de temperatura e mede consistência.

    Args:
        prompt:     Prompt a ser testado.
        temps:      Lista de temperaturas, ex: [0.1, 0.5, 1.0].
        llm_client: Instância de LLMClient (None = modo simulado para testes).

    Returns:
        Lista de dicts: [{temperatura, respostas, consistencia}, ...]
    """
    N_REPETICOES = 3
    resultados = []

    for temp in temps:
        respostas = []

        for _ in range(N_REPETICOES):
            if llm_client is not None:
                resultado = llm_client.chat(prompt=prompt, system="", temp=temp, max_tokens=100)
                respostas.append(resultado.get("resposta", "ERRO"))
                time.sleep(0.3)
            else:
                # Modo simulado sem Ollama
                import random
                opcoes_baixa = ["POSITIVO", "POSITIVO", "POSITIVO"]
                opcoes_media = ["POSITIVO", "POSITIVO", "MUITO POSITIVO"]
                opcoes_alta  = ["POSITIVO", "MUITO POSITIVO", "EXTREMAMENTE POSITIVO"]
                if temp <= 0.3:
                    respostas.append(random.choice(opcoes_baixa))
                elif temp <= 0.6:
                    respostas.append(random.choice(opcoes_media))
                else:
                    respostas.append(random.choice(opcoes_alta))

        consistencia = medir_consistencia(respostas)
        resultados.append({
            "temperatura": temp,
            "respostas": respostas,
            "consistencia": consistencia,
        })
        print(f"  Temperatura {temp}: {respostas} | consistencia={consistencia:.0%}")

    return resultados


# ─────────────────────────────────────────────────────────────
# 5. AVALIAR TODOS OS RESULTADOS
# ─────────────────────────────────────────────────────────────
def avaliar_todos(resultados: list) -> list:
    """
    Recebe lista de resultados e adiciona o campo 'acuracia' calculado.
    Cada item deve ter 'resposta' e 'esperado'.
    """
    for item in resultados:
        item["acuracia"] = medir_acuracia(item.get("resposta", ""), item.get("esperado", ""))
    return resultados


# ─────────────────────────────────────────────────────────────
# BLOCO DE TESTE — rode: python -m src.evaluator
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("TESTANDO evaluator.py")
    print("=" * 55)

    print("\n[1] CONTAR TOKENS")
    for t in ["Produto excelente, chegou rapido!", "Classifique o sentimento do texto."]:
        print(f"  '{t[:40]}' -> {contar_tokens(t)} tokens")

    print("\n[2] MEDIR ACURACIA")
    casos = [
        ("POSITIVO", "POSITIVO"),
        ("MUITO POSITIVO", "POSITIVO"),
        ("A classificacao e POSITIVO", "POSITIVO"),
        ('{"produto": "Dell", "preco": "R$3500"}', '{"produto": "Dell", "preco": "R$3500"}'),
    ]
    for resp, esp in casos:
        print(f"  '{resp[:30]}' | '{esp[:30]}' -> {medir_acuracia(resp, esp)}")

    print("\n[3] MEDIR CONSISTENCIA")
    for lista in [
        ["POSITIVO", "POSITIVO", "POSITIVO"],
        ["POSITIVO", "POSITIVO", "MUITO POSITIVO"],
        ["POSITIVO", "MUITO POSITIVO", "EXTREMAMENTE POSITIVO"],
    ]:
        print(f"  {lista} -> {medir_consistencia(lista):.0%}")

    print("\n[4] TESTAR TEMPERATURA (modo simulado)")
    testar_temperatura("Classifique: 'Produto excelente!'", [0.1, 0.5, 1.0], llm_client=None)

    print("\nTodos os testes concluidos!")
