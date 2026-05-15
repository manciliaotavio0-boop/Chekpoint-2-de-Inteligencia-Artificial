import pandas as pd
import matplotlib.pyplot as plt
import os

class ReportGenerator:
    def __init__(self, resultados: list[dict], output_dir="output"):
        self.df = pd.DataFrame(resultados)
        self.output_dir = output_dir
        self.graficos_dir = os.path.join(output_dir, "graficos")
        
        # Cria as pastas de saída se não existirem
        os.makedirs(self.graficos_dir, exist_ok=True)

    def gerar_csv(self):
        """Salva os resultados completos em CSV para entrega[cite: 76, 184]."""
        caminho_csv = os.path.join(self.output_dir, "resultados.csv")
        self.df.to_csv(caminho_csv, index=False, encoding='utf-8')
        print(f"Tabela CSV gerada em: {caminho_csv}")

    def grafico_acuracia(self):
        """Gera gráfico de barras de acurácia por técnica[cite: 107, 184]."""
        plt.figure(figsize=(10, 6))
        # Agrupa por técnica e tira a média da acurácia
        media_acuracia = self.df.groupby('tecnica')['acuracia'].mean() * 100
        
        media_acuracia.plot(kind='bar', color=['skyblue', 'salmon', 'lightgreen', 'orange'])
        plt.title('Acurácia Média por Técnica de Prompting')
        plt.ylabel('Acurácia (%)')
        plt.xlabel('Técnica')
        plt.ylim(0, 105)
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graficos_dir, "acuracia.png"))
        plt.close()
        print("Gráfico de acurácia salvo.")

    def grafico_custo(self):
        """Gera gráfico de tokens médios gastos."""
        plt.figure(figsize=(10, 6))
        
        # Calcula total de tokens (prompt + resposta)
        self.df['total_tokens'] = self.df['tokens_prompt'] + self.df['tokens_resposta']
        custo_medio = self.df.groupby('tecnica')['total_tokens'].mean()
        
        custo_medio.plot(kind='bar', color='gray')
        plt.title('Consumo Médio de Tokens por Técnica')
        plt.ylabel('Quantidade de Tokens')
        plt.xlabel('Técnica')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.graficos_dir, "custo.png"))
        plt.close()
        print("📊 Gráfico de custo salvo.")

    def recomendar(self):
        """Analisa os dados e recomenda a melhor técnica por tarefa[cite: 108, 184]."""
        print("\n" + "="*40)
        print("💡 RECOMENDAÇÃO AUTOMÁTICA")
        print("="*40)
        
        tarefas = self.df['tarefa'].unique()
        
        for tarefa in tarefas:
            df_tarefa = self.df[self.df['tarefa'] == tarefa]
            # Encontra a técnica com maior acurácia média para essa tarefa
            melhor = df_tarefa.groupby('tecnica')['acuracia'].mean().idxmax()
            print(f"• Para a tarefa '{tarefa}': A melhor técnica é {melhor.upper()}")
        print("="*40 + "\n")

# BLOCO DE TESTE
if __name__ == "__main__":
    # Mock de dados simulando o que o evaluator.py entregaria
    mock_resultados = [
        {"tarefa": "Classificação", "tecnica": "zero_shot", "acuracia": 0.8, "tokens_prompt": 50, "tokens_resposta": 10},
        {"tarefa": "Classificação", "tecnica": "few_shot", "acuracia": 1.0, "tokens_prompt": 150, "tokens_resposta": 10},
        {"tarefa": "Extração", "tecnica": "zero_shot", "acuracia": 0.6, "tokens_prompt": 60, "tokens_resposta": 40},
        {"tarefa": "Extração", "tecnica": "cot", "acuracia": 0.9, "tokens_prompt": 100, "tokens_resposta": 120},
    ]
    
    rep = ReportGenerator(mock_resultados)
    rep.gerar_csv()
    rep.grafico_acuracia()
    rep.grafico_custo()
    rep.recomendar()