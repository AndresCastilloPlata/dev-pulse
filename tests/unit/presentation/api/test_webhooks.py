import hmac
import hashlib
import json
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock

from src.dev_pulse.presentation.api.webhooks import router
from src.dev_pulse.domain.entities.audit_report import AuditReport, AuditStatus

app_de_prueba = FastAPI()
app_de_prueba.include_router(router)

def generar_firma_simulada(secreto: str, payload: bytes) -> str:
    """Generador de señales: Crea un hash HMAC valido para engañar al optoacoplador."""
    mac = hmac.new(secreto.encode(), msg=payload, digestmod=hashlib.sha256)
    return f"sha256={mac.hexdigest()}"

@pytest.mark.asyncio
async def test_webhook_rechaza_peticion_sin_firma(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "dummy-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    
    async with AsyncClient(transport=ASGITransport(app=app_de_prueba), base_url="http://testserver") as cliente:
        respuesta = await cliente.post("/github", json={"dummy": "data"})
        assert respuesta.status_code == 401
        assert "Firma" in respuesta.json()["detail"]

@pytest.mark.asyncio
async def test_webhook_rechaza_firma_invalida(monkeypatch: pytest.MonkeyPatch) -> None:
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
        # CORRECCION 1: Actualizamos el test para esperar la respuesta correcta de un payload sin commits
        assert respuesta.json()["status"] == "ignored"

@pytest.mark.asyncio
@patch("src.dev_pulse.presentation.api.webhooks.AuditCommitUseCase")
async def test_webhook_procesa_commit_y_retorna_reporte(mock_use_case_class, monkeypatch: pytest.MonkeyPatch) -> None:
    secreto = "secreto-real"
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", secreto)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")

    reporte_esperado = AuditReport(
        commit_sha="a1b2c3d4e5f67890abcdef1234567890abcdef12",
        status=AuditStatus.APPROVED,
        score=100,
        summary="Auditoria perfecta simulada",
        violations=[],
        recommendations=[]
    )

    # CORRECCION 2: Usar AsyncMock para que la funcion pueda ser esperada (await)
    mock_instancia = mock_use_case_class.return_value
    mock_instancia.execute = AsyncMock(return_value=reporte_esperado)

    payload_json = {
        "repository": {
            "name": "dev-pulse", 
            "owner": {"login": "SilverCastleLabs"}
        },
        "commits": [
            {
                "id": "a1b2c3d4e5f67890abcdef1234567890abcdef12",
                "message": "fix: resolver bug de integracion",
                "author": {"name": "Andres Castillo"},
                "added": ["src/main.py"],
                "modified": []
            }
        ]
    }

    payload_bytes = json.dumps(payload_json).encode("utf-8")
    firma_valida = generar_firma_simulada(secreto, payload_bytes)

    async with AsyncClient(transport=ASGITransport(app=app_de_prueba), base_url="http://testserver") as cliente:
        respuesta = await cliente.post(
            "/github", 
            content=payload_bytes,
            headers={"x-hub-signature-256": firma_valida}
        )

    assert respuesta.status_code == 200
    assert respuesta.json()["commit_sha"] == reporte_esperado.commit_sha
    assert respuesta.json()["score"] == 100
