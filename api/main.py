from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from yandex_client import YandexClient

app = FastAPI()

class Req(BaseModel):
    text: str

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

@app.post("/api/kp")
def kp(req: Req):
    if not req.text or len(req.text) < 300:
        raise HTTPException(400, "too short")
    if len(req.text) > 2000:
        raise HTTPException(400, "too long")
    client = YandexClient()
    full = KP_SYSTEM + "\n\n[ТЕКСТ]:\n" + req.text
    try:
        res = client.complete(full)
        return {"result": res.strip()}
    except Exception as e:
        raise HTTPException(500, str(e))
