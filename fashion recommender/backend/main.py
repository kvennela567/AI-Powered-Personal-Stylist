import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models.database import Base, engine, SessionLocal
from .seed_data import seed_database
from .routes import (
    users_router,
    products_router,
    recommendations_router,
    outfits_router,
    feedback_router,
    weather_router,
    ai_router,
    dashboard_router
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed database
    print("Initializing SQLite Database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    print("AI Personal Stylist Backend initialized successfully.")
    yield
    # Shutdown:
    print("Shutting down AI Personal Stylist Backend...")


app = FastAPI(
    title="AI Personal Stylist API",
    description="Backend API for AI-powered Fashion Recommendation, Personalization, and E-Commerce Discovery",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(users_router)
app.include_router(products_router)
app.include_router(recommendations_router)
app.include_router(outfits_router)
app.include_router(feedback_router)
app.include_router(weather_router)
app.include_router(ai_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "AI Personal Stylist API",
        "version": "1.0.0",
        "docs": "/docs",
        "demo_mode": os.getenv("DEMO_MODE", "true") == "true"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
