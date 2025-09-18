from fastapi import FastAPI
from app.routers import health, recipes

app = FastAPI()

# Include routers
app.include_router(health.router)
app.include_router(recipes.router)