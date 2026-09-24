from src.dev_pulse.domain.entities.audit_report import AuditReport, AuditStatus
from src.dev_pulse.domain.entities.commit import Commit
from src.dev_pulse.domain.interfaces.code_auditor import ICodeAuditor
from src.dev_pulse.domain.interfaces.vcs_client import IVcsClient


class AuditCommitUseCase:
    """
    Caso de uso orquestador de la auditorio de commits
    """
    def __init__(self, vcs_client: IVcsClient, code_auditor: ICodeAuditor) -> None:
        """
        Inicializa el cado de uso inyectando los puertos de comunicacion
        """

        self._vcs_client = vcs_client
        self._code_auditor = code_auditor

    async def execute(self, commit: Commit) -> AuditReport:
        """Ejecuta la secuencia de auditoria sobre la trama de un commit.

        Args:
            commit: Entidad con los metadatos e identificadores del commit.

        Returns:
            Entidad AuditReport con la calificacion e incidencias detectadas.
        """
        code_diff = await self._vcs_client.get_commit_diff(commit.sha)

        if not code_diff or not code_diff.strip():
            return AuditReport(
                commit_sha=commit.sha,
                status=AuditStatus.APPROVED,
                score=100,
                summary="No se detectaron cambios de codigo analizables en el commit",
                violations=[],
                recommendations=[
                    "Continuar con el registro habitual de commits de documentacion o configuracion"
                ],
            )
        reporte_auditado = await self._code_auditor.audit_code(
            commit=commit,
            code_diff=code_diff,
        )

        return reporte_auditado
        