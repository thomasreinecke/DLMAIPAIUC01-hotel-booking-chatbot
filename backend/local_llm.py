import os
import requests
from langchain.llms.base import LLM

class LMStudioLLM(LLM):
    """
    A simple LangChain-compatible LLM wrapper for LM Studio.
    """
    @property
    def _llm_type(self) -> str:
        return "lmstudio"

    def _call(self, prompt: str, stop=None) -> str:
        LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://127.0.0.1:1234/v1")
        MODEL = os.getenv("MODEL", "meta-llama-3.1-8b-instruct@q4_k_m")
        api_key = os.getenv("LMSTUDIO_API_KEY", "lm-studio")

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
        }
        response = requests.post(
            f"{LMSTUDIO_URL}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def predict(self, prompt: str) -> str:
        return self._call(prompt)
