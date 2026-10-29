import os
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

# 1. ENERGIZACION TEMPRANA: Inyectamos "voltaje de standby" ANTES de inspeccionar la placa
os.environ["OPENAI_API_KEY"] = "dummy-key-para-tests"
os.environ["GITHUB_WEBHOOK_SECRET"] = "dummy-secret-para-tests"

# Ahora si podemos importar la placa madre sin que el PMIC aborte el proceso
from src.dev_pulse.main import app


@pytest.mark.asyncio
async def test_health_check_responde_online() -> None:
    """Verifica el POST (Power-On Self-Test) del servidor."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as cliente:
        respuesta = await cliente.get("/health")
        
        assert respuesta.status_code == 200
        assert respuesta.json() == {"status": "online", "service": "Dev-Pulse"}


@pytest.mark.asyncio
async def test_rutas_principales_estan_conectadas() -> None:
    """Verifica mediante comportamiento que el router de GitHub fue soldado a la placa."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as cliente:
        
        # 1. Probamos enviar una peticion al webhook
        respuesta = await cliente.post("/github")
        
        # 2. Si el puerto NO existiera, FastAPI devolveria 404 (Not Found)
        assert respuesta.status_code != 404, "El puerto /github no fue encontrado en la placa"
        
        # 3. Como SI existe, pero no enviamos la firma de seguridad, 
        # el optoacoplador nos rechaza con 401 (Unauthorized). ¡Eso confirma que esta vivo!
        assert respuesta.status_code == 401, "El puerto existe pero el optoacoplador no respondio"


