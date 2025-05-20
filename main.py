from fastapi import FastAPI
from Fontankaparser import get_links

app = FastAPI()

@app.get("/parse")
def run_parser():
    links, titles, times, imgs = get_links([], [], [], [])
    return {
        "status": "ok",
        "new_articles": len(links)
    }
