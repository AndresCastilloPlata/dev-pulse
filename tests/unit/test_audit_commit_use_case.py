from unittest.mock import AsyncMock
import pytest

from src.dev_pulse.domain.entities.commit import Commit
from src.dev_pulse.domain.entities.audit_report import AuditReport, AuditStatus
from src.dev_pulse.domain.interfaces.vcs_client import IVcsClient
from src.dev_pulse.domain.interfaces.code_auditor import ICodeAuditor
from src.dev_pulse.application.use_cases.audit_commit import AuditCommitUseCase


@pytest.mark.asyncio
async def test_audit_commit_use_case_flujo_exitoso() -> None:
    """Verifica que el caso de uso orqueste correctamente la obtencion del diff

    y la generacion del reporte a traves de las interfaces de dominio.
    """
    # 1. ARRANGE: Preparacion de la trama de entrada y reporte esperado
    commit = Commit(
        sha="a1b2c3d4e5f67890abcdef1234567890abcdef12",
        author="Andres Castillo Plata",
        message="feat: implementar caso de uso de auditoria",
        files_changed=["src/main.py"],
    )
    diff_simulado = "@@ -1 +1 @@\n-def vieja(): pass\n+def nueva(): pass\n"

    reporte_esperado = AuditReport(
        commit_sha=commit.sha,
        status=AuditStatus.APPROVED,
        score=95,
        summary="Codigo limpio y conforme a SOLID",
        violations=[],
        recommendations=[],
    )

    # Configuracion de dobles de prueba (Mocks)
    mock_vcs_client = AsyncMock(spec=IVcsClient)
    mock_vcs_client.get_commit_diff.return_value = diff_simulado

    mock_code_auditor = AsyncMock(spec=ICodeAuditor)
    mock_code_auditor.audit_code.return_value = reporte_esperado

    caso_de_uso = AuditCommitUseCase(
        vcs_client=mock_vcs_client,
        code_auditor=mock_code_auditor,
    )

    # 2. ACT: Disparo de la ejecucion
    resultado = await caso_de_uso.execute(commit)

    # 3. ASSERT: Verificacion con coincidencia exacta de parametros nombrados (kwargs)
    mock_vcs_client.get_commit_diff.assert_awaited_once_with(commit.sha)
    mock_code_auditor.audit_code.assert_awaited_once_with(
        commit=commit,
        code_diff=diff_simulado,
    )
    assert resultado == reporte_esperado


@pytest.mark.asyncio
async def test_audit_commit_use_case_retorna_aprobado_si_diff_vacio() -> None:
    """Verifica la compuerta de ahorro: si no hay cambios, no consume al auditor."""
    commit = Commit(
        sha="a1b2c3d4e5f67890abcdef1234567890abcdef12",
        author="Andres Castillo Plata",
        message="docs: actualizar especificaciones",
        files_changed=["README.md"],
    )

    mock_vcs_client = AsyncMock(spec=IVcsClient)
    mock_vcs_client.get_commit_diff.return_value = ""  # Bus vacio sin codigo

    mock_code_auditor = AsyncMock(spec=ICodeAuditor)

    caso_de_uso = AuditCommitUseCase(
        vcs_client=mock_vcs_client,
        code_auditor=mock_code_auditor,
    )

    resultado = await caso_de_uso.execute(commit)

    # El cliente VCS se lee, pero la compuerta conmuta a bypass sin llamar al auditor
    mock_vcs_client.get_commit_diff.assert_awaited_once_with(commit.sha)
    mock_code_auditor.audit_code.assert_not_called()

    assert resultado.status == AuditStatus.APPROVED
    assert resultado.score == 100
    assert "No se detectaron cambios de codigo" in resultado.summary