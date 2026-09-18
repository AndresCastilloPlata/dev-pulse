import pytest
from pydantic import ValidationError

from src.dev_pulse.domain.entities.commit import Commit

def test_crear_commit_exitoso() -> None:
    """ Verifica la instanciacion valida de una traba de datos de Commit"""
    datos_commit = {
        "sha": "a1b2c3d4e5f67890abcdef1234567890abcdef12",
        "author": "Andres Castillo Plata",
        "message": "feat: implementar sensor de telemetria",
        "files_changed": ["src/main.py", "requirements.txt"],
    }

    commit = Commit(**datos_commit)

    # Aserciones de estado: comprobando que la carga util se almanece sin distorsión
    assert commit.sha == datos_commit["sha"]
    assert commit.author == datos_commit["author"]
    assert commit.message == datos_commit["message"]
    assert len(commit.files_changed) == 2
    assert "src/main.py" in commit.files_changed


def test_commit_falla_con_sha_invalido() -> None:
    """ Verifica que el modelo rechace tramas ruidosas o hashes incompletos"""
    with pytest.raises(ValidationError):
        # El SHA de git debe tener 40 caracteres hexadecimales; enviamos ruido corto
        Commit(
            sha="sha_incompleto_123",
            author="Andres Castillo Plata",
            message="fix: error de bus",
            files_changed=["src/main.py"],
        )