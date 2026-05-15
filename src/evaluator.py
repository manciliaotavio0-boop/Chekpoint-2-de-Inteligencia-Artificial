import json
import time
import tiktoken
 
# CONTAR OS TOKENS
def contar_tokens(texto: str) -> int:

    # cl100k_base é o encoding usado pelos modelos modernos (GPT-4, Claude, etc.)
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(texto)
    return len(tokens)


# MEDIR ACURÁCIA
def medir_acuracia(resposta: str, esperado: str) -> float:
    
    # Remove espaços extras e coloca tudo em maiúsculo
    resposta_norm = resposta.strip().upper()
    esperado_norm = esperado.strip().upper()
 
    # Estratégia 1: match exato
    if resposta_norm == esperado_norm:
        return 1.0
 
    # Estratégia 2: o esperado está contido dentro da resposta?
    if esperado_norm in resposta_norm:
        return 1.0
 
    # Estratégia 3: para respostas JSON — tenta comparar como dicionários
    try:
        resp_dict = json.loads(resposta)
        esp_dict = json.loads(esperado)
        if resp_dict == esp_dict:
            return 1.0
        # Acerto parcial: conta quantas chaves batem
        chaves = set(esp_dict.keys())
        acertos = sum(1 for k in chaves if resp_dict.get(k) == esp_dict.get(k))
        return round(acertos / len(chaves), 2)
    except (json.JSONDecodeError, TypeError):
        pass  
 
    return 0.0
 
 

# MEDIR CONSISTÊNCIA
def medir_consistencia(respostas: list[str]) -> float:
# Mede se o modelo responde a mesma coisa quando perguntado várias vezes.
# Temp baixa: consistente
# Temp alta: varia

    if not respostas:
        return 0.0
 
    if len(respostas) == 1:
        return 1.0  # com uma resposta só, é sempre 100%
 
    # Normaliza todas as respostas
    respostas_norm = [r.strip().upper() for r in respostas]
 
    contagem = {}
    for r in respostas_norm:
        contagem[r] = contagem.get(r, 0) + 1
 
    mais_frequente = max(contagem.values())
    total = len(respostas_norm)
 
    return round(mais_frequente / total, 2)
 
 

# TESTAR TEMPERATURA

def testar_temperatura(prompt: str, temps: list[float], llm_client=None) -> list[dict]:
    # Roda o mesmo prompt com diferentes valores de temperatura e mede consistência.
 
    
    N_REPETICOES = 3  # quantas vezes rodar o mesmo prompt por temperatura
    resultados = []
 
    for temp in temps:
        respostas = []
 
        for _ in range(N_REPETICOES):
            if llm_client is not None:
                # Modo real: chama o Ollama
                resultado = llm_client.chat(
                    prompt=prompt,
                    system="",
                    temp=temp,
                    max_tokens=100
                )
                respostas.append(resultado["resposta"])
                time.sleep(0.3)  # pequena pausa para não sobrecarregar a API
            else:
                # Modo simulado: para testes sem o LLM rodando
                # Simula que temp alta causa mais variação
                import random
                opcoes_baixa = ["POSITIVO", "POSITIVO", "POSITIVO"]
                opcoes_alta  = ["POSITIVO", "MUITO POSITIVO", "EXTREMAMENTE POSITIVO"]
                if temp <= 0.3:
                    respostas.append(random.choice(opcoes_baixa))
                elif temp <= 0.6:
                    respostas.append(random.choice(["POSITIVO", "POSITIVO", "MUITO POSITIVO"]))
                else:
                    respostas.append(random.choice(opcoes_alta))
 
        consistencia = medir_consistencia(respostas)
 
        resultados.append({
            "temperatura": temp,
            "respostas": respostas,
            "consistencia": consistencia
        })
 
        print(f"  Temperatura {temp}: respostas={respostas} | consistência={consistencia:.0%}")
 
    return resultados
 
 
# AVALIAR TODOS OS RESULTADOS

def avaliar_todos(resultados: list[dict]) -> list[dict]:
    
    ''' Recebe a lista completa de resultados (do mock ou da execução real)
    e adiciona os campos de acurácia calculada a cada entrada.'''
 
   
    for item in resultados:
        item["acuracia"] = medir_acuracia(item["resposta"], item["esperado"])
    return resultados
 
 
# ─────────────────────────────────────────────
# BLOCO DE TESTE — rode: python evaluator.py
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("TESTANDO evaluator.py com mock_resultados.json")
    print("=" * 55)
 
    # --- Teste 1: contar_tokens ---
    print("\n[1] CONTAR TOKENS")
    textos = [
        "Produto excelente, chegou rápido!",
        "Classifique o sentimento do texto abaixo como POSITIVO, NEGATIVO, NEUTRO ou MISTO.",
    ]
    for t in textos:
        print(f"  '{t[:40]}...' → {contar_tokens(t)} tokens")
 
    # --- Teste 2: medir_acuracia ---
    print("\n[2] MEDIR ACURÁCIA")
    casos = [
        ("POSITIVO", "POSITIVO"),        # match exato → 1.0
        ("MUITO POSITIVO", "POSITIVO"),   # não contém → 0.0
        ("A classificação é POSITIVO", "POSITIVO"),  # keyword match → 1.0
        ('{"produto": "Dell", "preco": "R$3500", "defeito": "pixels mortos"}',
         '{"produto": "Dell", "preco": "R$3500", "defeito": "pixels mortos"}'),  # JSON igual → 1.0
        ('{"produto": "Dell", "preco": "3500", "defeito": "pixels mortos"}',
         '{"produto": "Dell", "preco": "R$3500", "defeito": "pixels mortos"}'),  # JSON parcial → 0.67
    ]
    for resposta, esperado in casos:
        acc = medir_acuracia(resposta, esperado)
        print(f"  resposta='{resposta[:30]}' | esperado='{esperado[:30]}' → acurácia={acc}")
 
    # --- Teste 3: medir_consistencia ---
    print("\n[3] MEDIR CONSISTÊNCIA")
    listas = [
        ["POSITIVO", "POSITIVO", "POSITIVO"],             # 100%
        ["POSITIVO", "POSITIVO", "MUITO POSITIVO"],       # 67%
        ["POSITIVO", "MUITO POSITIVO", "EXTREMAMENTE POSITIVO"],  # 33%
    ]
    for lista in listas:
        c = medir_consistencia(lista)
        print(f"  {lista} → consistência={c:.0%}")
 
    # --- Teste 4: testar_temperatura (modo simulado) ---
    print("\n[4] TESTAR TEMPERATURA (modo simulado, sem Ollama)")
    testar_temperatura(
        prompt="Classifique: 'Produto excelente, chegou rápido!'",
        temps=[0.1, 0.5, 1.0],
        llm_client=None  # None = modo simulado
    )
 
    # --- Teste 5: avaliar_todos com o mock ---
    print("\n[5] AVALIAR TODOS (mock_resultados.json)")
    try:
        with open("data/mock_resultados.json", "r", encoding="utf-8") as f:
            mock = json.load(f)
 
        avaliados = avaliar_todos(mock)
 
        # Mostra um resumo por técnica
        resumo = {}
        for item in avaliados:
            tec = item["tecnica"]
            if tec not in resumo:
                resumo[tec] = {"acertos": 0, "total": 0}
            resumo[tec]["total"] += 1
            resumo[tec]["acertos"] += item["acuracia"]
 
        print(f"\n  {'Técnica':<20} {'Acurácia Média':>15}")
        print("  " + "-" * 37)
        for tec, dados in resumo.items():
            media = dados["acertos"] / dados["total"]
            print(f"  {tec:<20} {media:>14.0%}")
 
    except FileNotFoundError:
        print("  Arquivo data/mock_resultados.json não encontrado.")
        print("  Coloque o arquivo na pasta data/ e rode novamente.")
 
    print("\nTodos os testes concluídos!")