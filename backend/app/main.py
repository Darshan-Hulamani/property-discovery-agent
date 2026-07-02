import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.agent.loop import reset_session, run_agent
from app.models import ChatRequest, ChatResponse

_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)
load_dotenv()

app = FastAPI(title="Property Discovery Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@app.get("/api/health")
def health():
    return {"status": "ok", "model": os.getenv("GEMINI_MODEL", "gemini-3.5-flash")}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        reply, tool_trace, properties = run_agent(request.session_id, request.message)
        return ChatResponse(
            reply=reply,
            session_id=request.session_id,
            tool_trace=tool_trace,
            properties=properties,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc


@app.post("/api/reset")
def reset(session_id: str = "default"):
    reset_session(session_id)
    return {"status": "reset", "session_id": session_id}


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404)
        index = FRONTEND_DIST / "index.html"
        if index.exists():
            return FileResponse(index)
        raise HTTPException(status_code=404)
