import logging
from src.dev_pulse.domain.entities.commit import Commit
from src.dev_pulse.domain.entities.audit_report import AuditReport
from src.dev_pulse.domain.interfaces.vcs_client import IVcsClient
from src.dev_pulse.domain.interfaces.code_auditor import ICodeAuditor

logger = logging.getLogger(__name__)

class AuditCommitUseCase:
    """Procesador central que orquesta el flujo de auditoría de código con tolerancia a fallos extrema."""

    def __init__(self, vcs_client: IVcsClient, code_auditor: ICodeAuditor):
        self._vcs_client = vcs_client
        self._code_auditor = code_auditor

    async def execute(self, commit: Commit) -> AuditReport | None:
        try:
            # 1. MOVIDO ADENTRO DEL FUSIBLE: Leer pin RX
            code_diff = await self._vcs_client.get_commit_diff(commit.sha)
            
            # 2. Procesamiento (IA)
            reporte = await self._code_auditor.audit_code(commit=commit, code_diff=code_diff)
            
            # 3. Ensamblaje visual
            comentario_md = self._formatear_a_markdown(reporte)
            
            # 4. Escribir pin TX
            await self._vcs_client.post_commit_comment(commit.sha, comentario_md)
            print(f"✅ ÉXITO: Comentario publicado en commit {commit.sha}")
            return reporte
            
        except Exception as e:
            # TELEMETRÍA EN BRUTO: Esto se imprimirá obligatoriamente en Render
            print(f"🔥 ERROR CRÍTICO EN PROCESADOR: {str(e)}")
            logger.error(f"Excepción capturada: {str(e)}")
            
            # CIRCUITO DE CONTINGENCIA
            fallback_md = (
                "## ⚠️ Auditoría Dev-Pulse Interrumpida\n\n"
                "Se detectó una falla en el circuito de red o en el proveedor de Inteligencia Artificial.\n\n"
                f"**Traza de Error de Producción:** `{str(e)}`\n\n"
                "> *Sistema de resiliencia activo.*"
            )
            
            try:
                # Intentamos usar el pin TX para reportar la falla
                await self._vcs_client.post_commit_comment(commit.sha, fallback_md)
                print("⚠️ CONTINGENCIA: Comentario de error publicado en GitHub.")
            except Exception as ex:
                # Si esto falla, significa que el token de GitHub es el que tiene problemas
                print(f"💥 FALLO FATAL EN EL PIN TX (No se pudo escribir en GitHub): {str(ex)}")
                
            return None

    def _formatear_a_markdown(self, reporte: AuditReport) -> str:
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
