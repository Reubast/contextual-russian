import json
import os
import time
from typing import Any, Dict

import httpx

IAM_TOKEN_URL = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

class YandexClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("YANDEX_API_KEY")
        self._iam: str | None = None
        self._exp: float = 0

    def _get_iam(self) -> str:
        if self._iam and time.time() < self._exp - 60:
            return self._iam
        if not self.api_key:
            raise RuntimeError("YANDEX_API_KEY missing")
        resp = httpx.post(IAM_TOKEN_URL, json={"yandexPassportOauthToken": self.api_key}, timeout=10)
        resp.raise_for_status()
        j = resp.json()
        self._iam = j["iamToken"]
        self._exp = time.time() + 3600
        return self._iam

    def complete(self, prompt: str, model: str = "yandexgpt-lite", temperature: float = 0.3, max_tokens: int = 4000) -> str:
        iam = self._get_iam()
        payload = {
            "modelUri": f"gpt://b1g3v2s8qm1q9r5n4j6u/yandexgpt-lite",
            "completionOptions": {"stream": False, "temperature": temperature, "maxTokens": max_tokens},
            "messages": [{"role": "user", "text": prompt}],
        }
        headers = {"Authorization": f"Bearer {iam}"}
        resp = httpx.post(GPT_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        j = resp.json()
        return j["result"]["alternatives"][0]["message"]["text"]

if __name__ == "__main__":
    c = YandexClient()
    print(c.complete("test")[:30])
