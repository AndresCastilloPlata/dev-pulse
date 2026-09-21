from abc import ABC, abstractmethod

from src.dev_pulse.domain.entities.audit_report import AuditReport
from src.dev_pulse.domain.entities.commit import Commit

class ICodeAuditor(ABC):
    """
    Puerto de dominio para el motol de inspeccion y analisis de codigo
    
    Zocalo para el modulo de procesamiento inteligente (AOI)
    Permite descoplar el nucleo del negocion del proveedor especifico de LLM
    (OpenAI, Anthropic, modelos locales)
    """

    @abstractmethod
    async def audit_code(self, commit: Commit, code_diff: str) -> AuditReport:
        """Inspecciona el codigo contra estandares de calidad y genera un reporte.

        Args:
            commit: Entidad de dominio con los metadatos del commit interceptado.
            code_diff: Contenido textual de las diferencias de codigo a auditar.

        Returns:
            Entidad AuditReport con el veredicto, puntaje y hallazgos detallados.

        Raises:
            Exception: Si ocurre un fallo en la inferencia o en la deserializacion.
        """
        pass