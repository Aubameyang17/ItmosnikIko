import requests

api_key = "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"

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
                "content": f"Можешь очень сильно сократить эту статью?:\n\n{text_to_summarize}"
            }
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    summary = response.json()['choices'][0]['message']['content']
    return summary
