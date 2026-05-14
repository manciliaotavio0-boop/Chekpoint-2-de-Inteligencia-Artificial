TAREFAS = [
    {
        "nome": "classificar_solicitacao_paciente",
        "tipo": "classificacao",
        "instrucao": "Classifique a mensagem do paciente em uma das categorias: agendamento_consulta, sintomas_urgentes, duvida_medicamento, resultado_exame ou acompanhamento.",
        "formato_output": "Retorne apenas a categoria escolhida.",
        "exemplos_few_shot": [
            {
                "input": "Gostaria de marcar uma consulta com cardiologista para a próxima semana.",
                "output": "agendamento_consulta"
            },
            {
                "input": "Estou com dor forte no peito e falta de ar.",
                "output": "sintomas_urgentes"
            }
        ],
        "passos_cot": [
            "Leia a mensagem do paciente.",
            "Identifique a intenção principal.",
            "Verifique se há sinais de urgência.",
            "Escolha apenas uma categoria final."
        ],
        "persona": "assistente_clinica"
    },
    {
        "nome": "extrair_informacoes_saude",
        "tipo": "extracao",
        "instrucao": "Extraia da mensagem do paciente as seguintes informações: sintoma_principal, duracao, especialidade_sugerida e nivel_urgencia.",
        "formato_output": "Retorne em JSON com os campos: sintoma_principal, duracao, especialidade_sugerida, nivel_urgencia.",
        "exemplos_few_shot": [
            {
                "input": "Estou com dor de cabeça há três dias e muita tontura.",
                "output": {
                    "sintoma_principal": "dor de cabeça e tontura",
                    "duracao": "três dias",
                    "especialidade_sugerida": "clínico geral ou neurologista",
                    "nivel_urgencia": "moderada"
                }
            }
        ],
        "passos_cot": [
            "Identifique os sintomas citados.",
            "Verifique se o paciente informou duração.",
            "Associe os sintomas a uma possível especialidade.",
            "Classifique a urgência como baixa, moderada ou alta."
        ],
        "persona": "triagem_saude"
    },
    {
        "nome": "gerar_resposta_paciente",
        "tipo": "geracao",
        "instrucao": "Gere uma resposta inicial educada, empática e segura para o paciente, sem realizar diagnóstico médico.",
        "formato_output": "Retorne um texto curto com acolhimento, orientação geral e recomendação de procurar atendimento profissional quando necessário.",
        "exemplos_few_shot": [
            {
                "input": "Estou com febre e dor no corpo desde ontem.",
                "output": "Olá! Sentimos muito que você esteja se sentindo assim. Febre e dor no corpo podem ter diferentes causas, por isso é importante acompanhar a evolução dos sintomas. Caso os sintomas persistam ou piorem, procure atendimento médico."
            }
        ],
        "passos_cot": [
            "Entenda a queixa do paciente.",
            "Use linguagem acolhedora.",
            "Evite diagnóstico definitivo.",
            "Oriente a procurar atendimento se houver piora ou sinais de alerta."
        ],
        "persona": "assistente_clinica"
    }
]
