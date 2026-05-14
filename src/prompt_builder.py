def montar_prompt(instrucao, contexto="", input_dados="", formato_output=""):
	partes = []

	partes.append(f"[INSTRUÇÃO]: {instrucao}")
	if contexto:
		partes.append(f"[CONTEXTO]: {contexto}")
	if input_dados:
		partes.append(f"--- \n[INPUT]:\n  {input_dados}\n---")
	if formato_output:
		partes.append(f"[FORMATO OUTPUT]: {formato_output}")
	return "\n\n".join(partes)

def adicionar_exemplos(prompt, exemplos):
	""" 
	Args:
		prompt: String retornada pela função montar_prompt()
		exemplos: Lista de tuplas (input, output) para few-shot 
	"""

	few_shot = [prompt, "---\n[EXEMPLOS]:"]

	for i, (inp, out) in enumerate(exemplos, 1):
		line =[]
		line.append(f"  Exemplo {i}:")
		line.append(f"     [INPUT]: {inp}")
		line.append(f"    [OUTPUT]: {out}")
		if i == len(exemplos):
			line.append("---")
		few_shot.append("\n".join(line))

	return "\n\n".join(few_shot)

def adicionar_cot(prompt, passos):
	cot = ["---\nResolva passo a passo:"]

	for i, passo in enumerate(passos, 1):
		cot.append(f"  {i}. {passo}")
		if i == len(passos):
			cot.append("---")

	ret = [prompt, "\n".join(cot)]
	return "\n\n".join(ret)

# --------- TESTES DAS FUNCOES ----------------
# Teste montar_prompt()
# prompt = montar_prompt(
# 	instrucao="Classifique a avaliação como POSITIVA, NEUTRA ou NEGATIVA",
# 	contexto="Você é um analista de customer success de e-commerce brasileiro",
# 	input_dados="Produto chegou rápido, mas embalagem danificada. Funcionou no primeiro uso.",
# 	formato_output="Classificação + justificativa em 1 frase"
# )
# print(prompt)

# Teste adicionar_exemplos()
# few_shot_prompt = adicionar_exemplos(
# 	prompt,
# 	exemplos=[('Horrivel o produto!', '{"sentimento": "NEGATIVO", "justificativa": "Expressões negativas evidentes"}'), ('Comprei para minha mae, ela amou!', '{"sentimento": "POSITIVO", "justificativa": "Expressões positivas claras"}')]
# )
# print(few_shot_prompt)

# Teste CHAIN-OF-THOUGHT
# cot_prompt = adicionar_cot(
# 	prompt,
# 	passos=["Primeiro, analise cada palavra individualmente", "Depois, relacione ela com um sentimento", "Apresente o resultado final"]
# )

# print(cot_prompt)
