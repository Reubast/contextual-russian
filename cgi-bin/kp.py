#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kp_config import YANDEX_API_KEY, YANDEX_FOLDER_ID
GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
MODEL = "yandexgpt-lite"

KP_SYSTEM = """[RULES]
1. Двусторонняя однозначность. Вход рус. Выход рус. Без идиом, метафор, двусмысленности.
2. Информационная плотность. Удаляй лишние слова, используй сильные глаголы.
3. Только пять блоков: РОЛЬ, ЦЕЛЬ, ИНВАРИАНТЫ, ОГРАНИЧЕНИЯ, ЗОНА ДЕЛЕГИРОВАНИЯ.
4. Пиши предельно чётко, без рассуждений, только результат.
5. Если чего-то не хватает — не домысливай. Заполни по факту из текста.

[FORMAT]
Вывод строго в формате:

РОЛЬ: ...
ЦЕЛЬ: ...
ИНВАРИАНТЫ: ...
ОГРАНИЧЕНИЯ: ...
ЗОНА ДЕЛЕГИРОВАНИЯ: ...

Без заголовков вне этого списка. Без комментариев."""


def respond(status, obj):
    sys.stdout.write("Content-Type: application/json; charset=utf-8\r\n")
    sys.stdout.write("Access-Control-Allow-Origin: https://aictx.ru\r\n")
    sys.stdout.write("Access-Control-Allow-Methods: POST, OPTIONS\r\n")
    sys.stdout.write("Access-Control-Allow-Headers: Content-Type\r\n")
    sys.stdout.write("Status: %d\r\n\r\n" % status)
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))


def main():
    if os.environ.get("REQUEST_METHOD") == "OPTIONS":
        respond(200, {})
        return
    if os.environ.get("REQUEST_METHOD") != "POST":
        respond(405, {"error": "method not allowed"})
        return

    length = int(os.environ.get("CONTENT_LENGTH") or 0)
    raw = sys.stdin.read(length)
    try:
        data = json.loads(raw)
    except Exception:
        respond(400, {"error": "bad json"})
        return

    text = (data.get("text") or "").strip()
    if len(text) < 300:
        respond(400, {"error": "too short"})
        return
    if len(text) > 2000:
        respond(400, {"error": "too long"})
        return

    prompt = KP_SYSTEM + "\n\n[ТЕКСТ]:\n" + text
    body = json.dumps({
        "modelUri": "gpt://%s/%s" % (YANDEX_FOLDER_ID, MODEL),
        "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": 4000},
        "messages": [{"role": "user", "text": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(
        GPT_URL,
        data=body,
        headers={
            "Authorization": "Api-Key %s" % YANDEX_API_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            j = json.loads(resp.read().decode("utf-8"))
        result = j["result"]["alternatives"][0]["message"]["text"].strip()
        respond(200, {"result": result})
    except Exception as e:
        respond(500, {"error": str(e)})


if __name__ == "__main__":
    main()
