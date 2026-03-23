from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.ask import router as ask_router

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

@app.get("/health")
def health():
    return {"status": "ok", "service": "ArigatoAI"}