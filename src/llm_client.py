import requests
import time
import tiktoken
from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


class LLMClient:
    def __init__(self, model="llama3"):
        self.model = model
        self.url = f"{OLLAMA_HOST}/api/chat"

    def contar_tokens(self, texto):
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(texto))
        except:
            return 0

    def chat(self, mensagem, retries=3, timeout=30):
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": mensagem
                }
            ],
            "stream": False
        }

        tentativa = 0

        while tentativa < retries:
            try:
                inicio = time.time()

                response = requests.post(
                    self.url,
                    json=payload,
                    timeout=timeout
                )

                response.raise_for_status()

                fim = time.time()

                data = response.json()

                resposta = data["message"]["content"]

                tokens_prompt = self.contar_tokens(mensagem)
                tokens_resposta = self.contar_tokens(resposta)

                return {
                    "resposta": resposta,
                    "tokens_prompt": tokens_prompt,
                    "tokens_resposta": tokens_resposta,
                    "tempo_ms": round((fim - inicio) * 1000, 2)
                }

            except requests.exceptions.Timeout:
                print(f"Timeout na tentativa {tentativa + 1}")

            except requests.exceptions.RequestException as erro:
                print(f"Erro na API: {erro}")

            tentativa += 1
            time.sleep(2)

        return {
            "erro": "Falha após múltiplas tentativas."
        }


if __name__ == "__main__":
    client = LLMClient()

    resposta = client.chat("Olá, tudo bem?")

    print(resposta)
