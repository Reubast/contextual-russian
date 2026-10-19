import os

import httpx

GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


class YandexClient:
    def __init__(self, api_key: str = None, folder_id: str = None):
        self.api_key = api_key or os.getenv("YANDEX_API_KEY")
        self.folder_id = folder_id or os.getenv("YANDEX_FOLDER_ID")

    def complete(
        self,
        prompt: str,
        model: str = "yandexgpt-lite",
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> str:
        if not self.api_key or not self.folder_id:
            raise RuntimeError("YANDEX_API_KEY or YANDEX_FOLDER_ID missing")
        payload = {
            "modelUri": f"gpt://{self.folder_id}/{model}",
            "completionOptions": {"stream": False, "temperature": temperature, "maxTokens": max_tokens},
            "messages": [{"role": "user", "text": prompt}],
        }
        headers = {"Authorization": f"Api-Key {self.api_key}"}
        resp = httpx.post(GPT_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        j = resp.json()
        return j["result"]["alternatives"][0]["message"]["text"]


if __name__ == "__main__":
    print(YandexClient().complete("test")[:30])
