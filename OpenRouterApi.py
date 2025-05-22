import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("api_key")




headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://openrouter.ai",  # обязательный заголовок!
    "X-Title": "summarizer",                  # можно указать своё название
}
def summorize_text(text_to_summarize):
    if len(text_to_summarize) > 6000:
        text_to_summarize = text_to_summarize[:6000]

    data = {
        "model": "anthropic/claude-3-haiku",  # можно заменить на другую модель
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": f"Мне нужна краткая выжимка данной статьи:\n\n{text_to_summarize}\n\n"
                           f"Не пиши никаких вступлений, только краткая суть текста."
            }
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    print(response.status_code)
    print(response.text)
    summary = response.json()['choices'][0]['message']['content']

    return summary

def maintheme_text(text_to_summarize):
    data = {
        "model": "anthropic/claude-3-haiku",  # можно заменить на другую модель
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": f"Я изучаю рынок недвижимости и хочу классифицировать его новости. "
                           f"У меня может быть 4 типа новостей: Инвестиции, Аренда, Аналитика, Ипотека. "
                           f"Определи класс следующей статьи и пришли его одним словом, без других "
                           f"комментариев и каких-либо знаков препинания: {text_to_summarize}"
            }
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    print(response.status_code)
    print(response.text)
    summary = response.json()['choices'][0]['message']['content']

    return summary