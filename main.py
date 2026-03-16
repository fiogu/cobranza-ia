from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import deudores

app = FastAPI(
    title="Cobranza IA API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deudores.router)

@app.get("/")
def health_check():
    return {"status": "ok", "mensaje": "Cobranza IA corriendo 🚀"}