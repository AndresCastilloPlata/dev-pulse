import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.dev_pulse.domain.entities.audit_report import AuditReport, AuditStatus
from src.dev_pulse.domain.entities.commit import Commit
from src.dev_pulse.infrastructure.ai.openai_auditor import OpenAiCodeAuditor


@pytest.mark.asyncio
@patch("src.dev_pulse.infrastructure.ai.openai_auditor.AsyncOpenAI")
async def test_motor_openai_devuelve_reporte_estructurado(mock_async_openai_class) -> None:
    """Verifica que el adaptador decodifique la respuesta del LLM a nuestra entidad de dominio."""
    
    # 1. ARRANGE: Preparar las señales de entrada y la salida esperada
    commit_dummy = Commit(
        sha="12345abcde12345abcde12345abcde12345abcde", 
        author="Andres", 
        message="fix: error logico", 
        files_changed=["main.py"]
    )
    diff_dummy = "+ def logica_nueva(): pass"

    reporte_simulado = AuditReport(
        commit_sha=commit_dummy.sha,
        status=AuditStatus.APPROVED,
        score=90,
        summary="Codigo analizado correctamente",
        violations=[],
        recommendations=[]
    )

    # Configuramos el simulador del SDK de OpenAI (Inyector de señales)
    mock_client_instance = AsyncMock()
    mock_async_openai_class.return_value = mock_client_instance
    
    # Simulamos la estructura profunda que devuelve OpenAI con "Structured Outputs"
    mock_message = MagicMock()
    mock_message.parsed = reporte_simulado
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    # Cuando nuestro código llame al LLM, el mock devolverá esta respuesta instantáneamente
    mock_client_instance.beta.chat.completions.parse.return_value = mock_response

    # Instanciamos nuestro chip vacío
    auditor = OpenAiCodeAuditor(api_key="fake-key")

    # 2. ACT: Disparamos la ejecución
    resultado = await auditor.audit_code(commit=commit_dummy, code_diff=diff_dummy)

    # 3. ASSERT: Verificamos que el resultado coincida y que OpenAI haya sido llamado
    assert resultado == reporte_simulado
    mock_client_instance.beta.chat.completions.parse.assert_called_once()
