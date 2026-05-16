import requests
import time
import tiktoken
from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


class LLMClient:
    def __init__(self, model="gpt-oss:120b"):
        self.model = model
        self.url = f"{OLLAMA_HOST}/api/chat"

    def contar_tokens(self, texto: str) -> int:
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(texto))
        except Exception:
            # Fallback: estimativa por palavras (~1.3 tokens/palavra em PT-BR)
            return int(len(texto.split()) * 1.3)

    def chat(self, prompt: str, system: str = "", temp: float = 0.7,
             max_tokens: int = 1000, retries: int = 3, timeout: int = 60) -> dict:
        """
        Envia uma mensagem ao Ollama e retorna resposta + métricas.

        Args:
            prompt:     Mensagem do usuário (obrigatório).
            system:     System prompt / persona (opcional).
            temp:       Temperatura (0.1 = determinístico, 1.0 = criativo).
            max_tokens: Limite de tokens na resposta.
            retries:    Tentativas em caso de falha.
            timeout:    Timeout em segundos por tentativa.

        Returns:
            dict com chaves: resposta, tokens_prompt, tokens_resposta, tempo_ms
                  ou        erro (string) em caso de falha total.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temp,
                "num_predict": max_tokens,
            },
        }

        for tentativa in range(1, retries + 1):
            try:
                inicio = time.time()
                response = requests.post(self.url, json=payload, timeout=timeout)
                response.raise_for_status()
                fim = time.time()

                data = response.json()
                resposta = data["message"]["content"]

                return {
                    "resposta": resposta,
                    "tokens_prompt": self.contar_tokens(prompt + system),
                    "tokens_resposta": self.contar_tokens(resposta),
                    "tempo_ms": round((fim - inicio) * 1000, 2),
                }

            except requests.exceptions.Timeout:
                print(f"  [LLMClient] Timeout na tentativa {tentativa}/{retries}")
            except requests.exceptions.ConnectionError:
                print(f"  [LLMClient] Ollama nao encontrado em {OLLAMA_HOST}. Verifique se esta rodando.")
                break
            except requests.exceptions.RequestException as erro:
                print(f"  [LLMClient] Erro na API (tentativa {tentativa}): {erro}")

            if tentativa < retries:
                time.sleep(2 * tentativa)

        return {"erro": f"Falha apos {retries} tentativas. Verifique o Ollama."}


if __name__ == "__main__":
    client = LLMClient()
    resposta = client.chat("Ola, tudo bem? Responda em uma frase.")
    print(resposta)
