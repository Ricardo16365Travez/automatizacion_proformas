# app/__init__.py
from fastapi import FastAPI
from .api import router as api_router

app = FastAPI()

# Incluir el router de la API
app.include_router(api_router)
