import pytest
from pydantic import ValidationError

from src.dev_pulse.core.config import Settings

def test_carga_configuracion_exitosa(monkeypatch: pytest.MonkeyPatch) -> None:
    "Verifica la lectura correcta de señales y valores de entorno nominales"
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-test-key-1234567890abcdef")
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "super-secret-webhook-token")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    settings = Settings()

    assert settings.OPENAI_API_KEY == "sk-proj-test-key-1234567890abcdef"
    assert settings.GITHUB_WEBHOOK_SECRET == "super-secret-webhook-token"
    assert settings.OPENAI_MODEL == "gpt-4o-mini"
    assert settings.ENVIRONMENT == "development"  # Valor por defecto esperado


def test_configuracion_falla_si_faltan_secretos_criticos(monkeypatch: pytest.MonkeyPatch) -> None:
    "Verifica el enclavamiento de seguridad ante falta de secretos"
    # Purgamos intencionalmente cualquier variable que pudiera existir en el entorno
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GITHUB_WEBHOOK_SECRET", raising=False)

    with pytest.raises(ValidationError):
        # Debe fallar inmediatamente porque son parametros obligatorios sin default
        Settings(_env_file=None)