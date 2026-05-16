"""
report.py — Geração de tabelas, gráficos e recomendação automática (Aula 08)
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend sem display (funciona em servidor/terminal)
import matplotlib.pyplot as plt


class ReportGenerator:
    def __init__(self, resultados: list, output_dir: str = "output"):
        self.df = pd.DataFrame(resultados)
        self.output_dir = output_dir
        self.graficos_dir = os.path.join(output_dir, "graficos")
        os.makedirs(self.graficos_dir, exist_ok=True)

    # ─────────────────────────────────────────────────────────
    # CSV
    # ─────────────────────────────────────────────────────────
    def gerar_csv(self) -> str:
        """Salva os resultados completos em CSV."""
        caminho = os.path.join(self.output_dir, "resultados.csv")
        self.df.to_csv(caminho, index=False, encoding="utf-8")
        print(f"  [report] CSV salvo em: {caminho}")
        return caminho

    # ─────────────────────────────────────────────────────────
    # TABELA NO TERMINAL
    # ─────────────────────────────────────────────────────────
    def imprimir_tabela(self) -> None:
        """Imprime tabela resumida no terminal agrupada por tarefa e técnica."""
        if self.df.empty:
            print("  [report] Sem dados para exibir.")
            return

        colunas = ["tarefa", "tecnica", "acuracia", "tokens_prompt", "tokens_resposta", "tempo_ms"]
        colunas_presentes = [c for c in colunas if c in self.df.columns]

        resumo = (
            self.df[colunas_presentes]
            .groupby(["tarefa", "tecnica"])
            .mean(numeric_only=True)
            .round(3)
        )
        print("\n" + "=" * 65)
        print("  TABELA COMPARATIVA — MEDIA POR TAREFA × TECNICA")
        print("=" * 65)
        print(resumo.to_string())
        print("=" * 65 + "\n")

    # ─────────────────────────────────────────────────────────
    # GRÁFICO 1 — ACURÁCIA
    # ─────────────────────────────────────────────────────────
    def grafico_acuracia(self) -> str:
        """Barras agrupadas de acurácia média por técnica."""
        if "acuracia" not in self.df.columns:
            print("  [report] Coluna 'acuracia' ausente — pulando grafico_acuracia.")
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))
        media = self.df.groupby("tecnica")["acuracia"].mean() * 100
        cores = ["#4C9BE8", "#E87C4C", "#4CE87C", "#E84C9B"]
        media.plot(kind="bar", ax=ax, color=cores[: len(media)], edgecolor="white")

        ax.set_title("Acurácia Média por Técnica de Prompting", fontsize=14, pad=12)
        ax.set_ylabel("Acurácia (%)")
        ax.set_xlabel("Técnica")
        ax.set_ylim(0, 110)
        ax.tick_params(axis="x", rotation=30)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        for bar in ax.patches:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{bar.get_height():.1f}%",
                ha="center", va="bottom", fontsize=10,
            )

        plt.tight_layout()
        caminho = os.path.join(self.graficos_dir, "acuracia.png")
        plt.savefig(caminho, dpi=150)
        plt.close()
        print(f"  [report] Grafico de acuracia salvo em: {caminho}")
        return caminho

    # ─────────────────────────────────────────────────────────
    # GRÁFICO 2 — CUSTO (TOKENS)
    # ─────────────────────────────────────────────────────────
    def grafico_custo(self) -> str:
        """Barras de tokens médios por técnica (prompt + resposta)."""
        if "tokens_prompt" not in self.df.columns:
            print("  [report] Colunas de tokens ausentes — pulando grafico_custo.")
            return ""

        self.df["total_tokens"] = self.df["tokens_prompt"] + self.df["tokens_resposta"]
        fig, ax = plt.subplots(figsize=(10, 6))
        custo = self.df.groupby("tecnica")["total_tokens"].mean()
        custo.plot(kind="bar", ax=ax, color="#888888", edgecolor="white")

        ax.set_title("Consumo Médio de Tokens por Técnica", fontsize=14, pad=12)
        ax.set_ylabel("Tokens médios (prompt + resposta)")
        ax.set_xlabel("Técnica")
        ax.tick_params(axis="x", rotation=30)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        caminho = os.path.join(self.graficos_dir, "custo.png")
        plt.savefig(caminho, dpi=150)
        plt.close()
        print(f"  [report] Grafico de custo salvo em: {caminho}")
        return caminho

    # ─────────────────────────────────────────────────────────
    # GRÁFICO 3 — TEMPERATURA
    # ─────────────────────────────────────────────────────────
    def grafico_temperatura(self, resultados_temp: list) -> str:
        """
        Linha de consistência por temperatura.

        Args:
            resultados_temp: saída de evaluator.testar_temperatura()
                             lista de dicts: [{temperatura, consistencia, respostas}]
        """
        if not resultados_temp:
            print("  [report] Sem dados de temperatura — pulando grafico_temperatura.")
            return ""

        temps = [r["temperatura"] for r in resultados_temp]
        consistencias = [r["consistencia"] * 100 for r in resultados_temp]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(temps, consistencias, marker="o", linewidth=2, color="#4C9BE8", markersize=8)
        ax.fill_between(temps, consistencias, alpha=0.15, color="#4C9BE8")

        ax.set_title("Consistência das Respostas por Temperatura", fontsize=14, pad=12)
        ax.set_xlabel("Temperatura")
        ax.set_ylabel("Consistência (%)")
        ax.set_ylim(0, 110)
        ax.set_xticks(temps)
        ax.grid(linestyle="--", alpha=0.5)

        for x, y in zip(temps, consistencias):
            ax.annotate(f"{y:.0f}%", (x, y), textcoords="offset points",
                        xytext=(0, 10), ha="center", fontsize=10)

        plt.tight_layout()
        caminho = os.path.join(self.graficos_dir, "temperatura.png")
        plt.savefig(caminho, dpi=150)
        plt.close()
        print(f"  [report] Grafico de temperatura salvo em: {caminho}")
        return caminho

    # ─────────────────────────────────────────────────────────
    # RECOMENDAÇÃO AUTOMÁTICA
    # ─────────────────────────────────────────────────────────
    def recomendar(self) -> dict:
        """
        Analisa os dados e imprime + retorna a melhor técnica por tarefa.
        Critério: maior acurácia média; empate é desfeito pelo menor custo de tokens.
        """
        if self.df.empty or "acuracia" not in self.df.columns:
            print("  [report] Dados insuficientes para recomendacao.")
            return {}

        print("\n" + "=" * 50)
        print("  RECOMENDACAO AUTOMATICA POR TAREFA")
        print("=" * 50)

        recomendacoes = {}
        for tarefa in self.df["tarefa"].unique():
            df_t = self.df[self.df["tarefa"] == tarefa]

            resumo = df_t.groupby("tecnica").agg(
                acuracia_media=("acuracia", "mean"),
                tokens_medios=("total_tokens" if "total_tokens" in df_t.columns else "tokens_prompt", "mean"),
            )

            melhor = resumo["acuracia_media"].idxmax()
            acc = resumo.loc[melhor, "acuracia_media"]
            tok = resumo.loc[melhor, "tokens_medios"]

            justificativa = (
                f"Acuracia media de {acc:.0%} com {tok:.0f} tokens por chamada."
            )
            recomendacoes[tarefa] = {"tecnica": melhor, "justificativa": justificativa}
            print(f"  Tarefa '{tarefa}': melhor tecnica = {melhor.upper()}")
            print(f"    -> {justificativa}")

        print("=" * 50 + "\n")
        return recomendacoes


# ─────────────────────────────────────────────────────────────
# BLOCO DE TESTE — rode: python -m src.report
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mock = [
        {"tarefa": "classificacao", "tecnica": "zero_shot",  "acuracia": 0.8, "tokens_prompt": 50,  "tokens_resposta": 10, "tempo_ms": 300},
        {"tarefa": "classificacao", "tecnica": "few_shot",   "acuracia": 1.0, "tokens_prompt": 150, "tokens_resposta": 10, "tempo_ms": 400},
        {"tarefa": "classificacao", "tecnica": "cot",        "acuracia": 0.9, "tokens_prompt": 120, "tokens_resposta": 80, "tempo_ms": 600},
        {"tarefa": "classificacao", "tecnica": "role",       "acuracia": 0.9, "tokens_prompt": 200, "tokens_resposta": 15, "tempo_ms": 450},
        {"tarefa": "extracao",      "tecnica": "zero_shot",  "acuracia": 0.6, "tokens_prompt": 60,  "tokens_resposta": 40, "tempo_ms": 350},
        {"tarefa": "extracao",      "tecnica": "cot",        "acuracia": 0.9, "tokens_prompt": 100, "tokens_resposta": 120,"tempo_ms": 700},
        {"tarefa": "extracao",      "tecnica": "few_shot",   "acuracia": 0.8, "tokens_prompt": 180, "tokens_resposta": 50, "tempo_ms": 500},
        {"tarefa": "extracao",      "tecnica": "role",       "acuracia": 0.85,"tokens_prompt": 220, "tokens_resposta": 60, "tempo_ms": 520},
        {"tarefa": "geracao",       "tecnica": "zero_shot",  "acuracia": 0.7, "tokens_prompt": 70,  "tokens_resposta": 90, "tempo_ms": 800},
        {"tarefa": "geracao",       "tecnica": "role",       "acuracia": 0.95,"tokens_prompt": 210, "tokens_resposta": 110,"tempo_ms": 900},
        {"tarefa": "geracao",       "tecnica": "few_shot",   "acuracia": 0.85,"tokens_prompt": 160, "tokens_resposta": 100,"tempo_ms": 850},
        {"tarefa": "geracao",       "tecnica": "cot",        "acuracia": 0.80,"tokens_prompt": 130, "tokens_resposta": 130,"tempo_ms": 950},
    ]

    mock_temp = [
        {"temperatura": 0.1, "respostas": ["POSITIVO","POSITIVO","POSITIVO"], "consistencia": 1.0},
        {"temperatura": 0.5, "respostas": ["POSITIVO","POSITIVO","MISTO"],    "consistencia": 0.67},
        {"temperatura": 1.0, "respostas": ["POSITIVO","MISTO","NEGATIVO"],    "consistencia": 0.33},
    ]

    rep = ReportGenerator(mock)
    rep.gerar_csv()
    rep.imprimir_tabela()
    rep.grafico_acuracia()
    rep.grafico_custo()
    rep.grafico_temperatura(mock_temp)
    rep.recomendar()
    print("Teste concluido! Veja output/graficos/")
