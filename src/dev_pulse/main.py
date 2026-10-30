from fastapi import FastAPI
from src.dev_pulse.presentation.api import webhooks

# Inicialización del chasis principal (Servidor FastAPI)
app = FastAPI(
    title="Dev-Pulse API",
    description="Microservicio de auditoría automatizada de commits con Inteligencia Artificial",
    version="1.0.0"
)

# EL NUEVO PIN DE ESTADO (Health Check para el Keep-Alive)
@app.get("/health", tags=["System"])
def health_check():
    """Pin de respuesta básica para mantener vivo el servidor ante los pings del Cron-Job."""
    return {"status": "ok", "service": "dev-pulse-auditor"}

# Conexión del módulo receptor de GitHub
app.include_router(webhooks.router)
