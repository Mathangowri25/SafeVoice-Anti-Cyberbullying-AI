from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import Base, engine
from classifier import router as classify_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ SafeVoice API started")
    yield
    print("SafeVoice API shutting down")

app = FastAPI(
    title       = "SafeVoice API",
    description = "Multilingual cyberbullying detection — Tamil, Hindi, English",
    version     = "1.0.0",
    lifespan    = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

app.include_router(classify_router)

@app.get("/")
def root():
    return {"status": "SafeVoice API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
