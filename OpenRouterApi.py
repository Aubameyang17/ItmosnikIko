import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("BOT_TOKEN")




headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://openrouter.ai",  # обязательный заголовок!
    "X-Title": "summarizer",                  # можно указать своё название
}
def summorize_text(text_to_summarize):
    data = {
        "model": "anthropic/claude-3-haiku",  # можно заменить на другую модель
        "messages": [
            {
                "role": "user",
                "content": f"Мне нужна краткая выжимка данной статьи:\n\n{text_to_summarize}\n\n "
                           f"не надо ничего перед этим писать, не надо писать 'Вот краткая выжимка статьи'"
            }
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    summary = response.json()['choices'][0]['message']['content']

    return summary