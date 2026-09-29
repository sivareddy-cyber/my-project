import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from backend/.env or root .env
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_env = os.path.join(current_dir, ".env")
root_env = os.path.join(os.path.dirname(current_dir), ".env")

if os.path.exists(backend_env):
    load_dotenv(backend_env)
elif os.path.exists(root_env):
    load_dotenv(root_env)
else:
    load_dotenv()

try:
    from .routes.health import router as health_router
    from .routes.memory import router as memory_router
    from .routes.review import router as review_router
    from .routes.feedback import router as feedback_router
except (ImportError, ValueError):
    from routes.health import router as health_router
    from routes.memory import router as memory_router
    from routes.review import router as review_router
    from routes.feedback import router as feedback_router

app = FastAPI(
    title="CodeReview Memory Agent API",
    description="Backend API for CodeReview Memory Agent powered by Hindsight and Groq",
    version="0.2.0",
)

# Configure CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health_router)
app.include_router(memory_router)
app.include_router(review_router)
app.include_router(feedback_router)


@app.get("/")
async def root():
    """Root endpoint with basic API info."""
    return {
        "service": "CodeReview Memory Agent API",
        "phase": "Phase 1 - Foundation",
        "health_check": "/health",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
