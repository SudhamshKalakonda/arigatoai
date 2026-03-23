from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.routes.ask import router as ask_router
import os

app = FastAPI(
    title="ArigatoAI",
    description="AI assistant for CA firms",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask_router, prefix="/api")

WIDGET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "widget")

@app.get("/health")
def health():
    return {"status": "ok", "service": "ArigatoAI"}

@app.get("/widget.js")
def widget_js():
    return FileResponse(os.path.join(WIDGET_DIR, "widget.js"), media_type="application/javascript")

@app.get("/demo")
def demo():
    return FileResponse(os.path.join(WIDGET_DIR, "demo.html"), media_type="text/html")
