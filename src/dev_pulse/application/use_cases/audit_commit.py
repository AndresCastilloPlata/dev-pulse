import logging
from src.dev_pulse.domain.entities.commit import Commit
from src.dev_pulse.domain.entities.audit_report import AuditReport
from src.dev_pulse.domain.interfaces.vcs_client import IVcsClient
from src.dev_pulse.domain.interfaces.code_auditor import ICodeAuditor

logger = logging.getLogger(__name__)

class AuditCommitUseCase:
    """Procesador central que orquesta el flujo de auditoría de código con tolerancia a fallos."""

    def __init__(self, vcs_client: IVcsClient, code_auditor: ICodeAuditor):
        self._vcs_client = vcs_client
        self._code_auditor = code_auditor

    async def execute(self, commit: Commit) -> AuditReport | None:
        # 1. Leer pin RX (Extraer el código modificado)
        code_diff = await self._vcs_client.get_commit_diff(commit.sha)
        
        try:
            # 2. Procesamiento (Intentar conectar con Gemini)
            reporte = await self._code_auditor.audit_code(commit=commit, code_diff=code_diff)
            
            # 3. Ensamblaje visual (Convertir JSON a Markdown)
            comentario_md = self._formatear_a_markdown(reporte)
            
            # 4. Escribir pin TX (Publicar éxito)
            await self._vcs_client.post_commit_comment(commit.sha, comentario_md)
            return reporte
            
        except Exception as e:
            logger.error(f"Fallo en el chip de IA durante auditoría: {str(e)}")
            
            # CIRCUITO DE CONTINGENCIA: Avisar a GitHub que hubo un fallo en el proveedor
            fallback_md = (
                "## ⚠️ Auditoría Dev-Pulse Interrumpida\n\n"
                "El proveedor de Inteligencia Artificial (Google Gemini) rechazó la conexión "
                "debido a alta demanda temporal en su capa gratuita.\n\n"
                f"**Traza de Error:** `{str(e)}`\n\n"
                "> *El microservicio Dev-Pulse sigue operativo y evaluará los siguientes commits cuando el tráfico en Google se normalice.*"
            )
            
            # Usamos el pin TX para reportar el fallo al usuario
            await self._vcs_client.post_commit_comment(commit.sha, fallback_md)
            return None

    def _formatear_a_markdown(self, reporte: AuditReport) -> str:
        """Convierte la Entidad AuditReport en un bloque Markdown para GitHub."""
        md = f"## 🤖 Auditoría Dev-Pulse (Gemini 3.8)\n\n"
        md += f"**Puntaje de Calidad (Clean Architecture):** `{reporte.score}/100`\n\n"
        md += f"### 📊 Resumen Ejecutivo\n{reporte.summary}\n\n"
        
        if hasattr(reporte, 'vulnerabilities') and reporte.vulnerabilities:
            md += "### ⚠️ Vulnerabilidades Críticas\n"
            for vuln in reporte.vulnerabilities:
                md += f"- {vuln}\n\n"
                
        if hasattr(reporte, 'recommendations') and reporte.recommendations:
            md += "### 💡 Recomendaciones de Refactorización\n"
            for rec in reporte.recommendations:
                md += f"- {rec}\n"
                
        return md
