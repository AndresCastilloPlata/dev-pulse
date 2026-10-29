import hmac
import hashlib
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from src.dev_pulse.presentation.api.webhooks import router

app_de_prueba = FastAPI()
app_de_prueba.include_router(router)

def generar_firma_simulada(secreto: str, payload: bytes) -> str:
    """Generador de señales: Crea un hash HMAC valido para engañar al optoacoplador."""
    mac = hmac.new(secreto.encode(), msg=payload, digestmod=hashlib.sha256)
    return f"sha256={mac.hexdigest()}"

@pytest.mark.asyncio
async def test_webhook_rechaza_peticion_sin_firma(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica que el sistema rechace pulsos sin la cabecera de seguridad."""
    
    # Inyectamos el voltaje simulado para que el PMIC (Settings) encienda correctamente
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "dummy-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    
    async with AsyncClient(transport=ASGITransport(app=app_de_prueba), base_url="http://testserver") as cliente:
        respuesta = await cliente.post("/github", json={"dummy": "data"})
        
        assert respuesta.status_code == 401
        assert "Firma" in respuesta.json()["detail"]


@pytest.mark.asyncio
async def test_webhook_rechaza_firma_invalida(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica que firmas falsas o manipuladas por atacantes sean rechazadas."""
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "secreto-real")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    
    async with AsyncClient(transport=ASGITransport(app=app_de_prueba), base_url="http://testserver") as cliente:
        respuesta = await cliente.post(
            "/github", 
            json={"dummy": "data"},
            headers={"x-hub-signature-256": "sha256=firma_falsa_inventada"}
        )
        assert respuesta.status_code == 401

@pytest.mark.asyncio
async def test_webhook_acepta_firma_valida(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ruta nominal: Verifica que un pulso de GitHub 100% legitimo logre entrar."""
    secreto = "secreto-real"
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", secreto)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    
    payload_crudo = b'{"dummy": "data"}'
    firma_valida = generar_firma_simulada(secreto, payload_crudo)
    
    async with AsyncClient(transport=ASGITransport(app=app_de_prueba), base_url="http://testserver") as cliente:
        respuesta = await cliente.post(
            "/github", 
            content=payload_crudo,
            headers={"x-hub-signature-256": firma_valida}
        )
        assert respuesta.status_code == 200
        assert respuesta.json() == {"status": "ok"}
