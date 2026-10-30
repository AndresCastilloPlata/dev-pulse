import hmac
import hashlib
from fastapi import APIRouter, Request, Header, HTTPException, Depends

from src.dev_pulse.core.config import Settings
from src.dev_pulse.domain.entities.commit import Commit
from src.dev_pulse.infrastructure.vcs.github_client import GitHubApiClient

# 1. Eliminamos el import de OpenAI, dejamos exclusivamente el de Gemini
from src.dev_pulse.infrastructure.ai.gemini_auditor import GeminiCodeAuditor
from src.dev_pulse.application.use_cases.audit_commit import AuditCommitUseCase

router = APIRouter()

def get_settings() -> Settings:
    return Settings()

@router.post("/github")
async def github_webhook_receiver(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    settings: Settings = Depends(get_settings)
):
    """Rutina de Interrupcion Externa (ISR) para eventos de GitHub con blindaje HMAC."""
    
    # 1. SEGURIDAD: Validacion HMAC (El Optoacoplador)
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Firma HMAC no proporcionada.")
        
    cuerpo_crudo = await request.body()
    secreto_bytes = settings.GITHUB_WEBHOOK_SECRET.encode('utf-8')
    firma_calculada = hmac.new(key=secreto_bytes, msg=cuerpo_crudo, digestmod=hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(x_hub_signature_256, f"sha256={firma_calculada}"):
        raise HTTPException(status_code=401, detail="Firma HMAC invalida o corrupta.")

    # 2. DECODIFICACION: Parsear el JSON masivo (El Demultiplexer)
    payload = await request.json()
    
    # Filtro de seguridad: Si el payload no trae commits (ej. evento ping de GitHub), respondemos OK y salimos
    commits_data = payload.get("commits", [])
    if not commits_data:
        return {"status": "ignored", "detail": "No hay commits analizables en este evento."}

    commit_data = commits_data[0]
    repo_data = payload.get("repository", {})
    
    # Extraemos solo los 4 pines de datos necesarios
    archivos_afectados = commit_data.get("added", []) + commit_data.get("modified", [])
    commit_entity = Commit(
        sha=commit_data.get("id"),
        author=commit_data.get("author", {}).get("name", "Unknown"),
        message=commit_data.get("message", ""),
        files_changed=archivos_afectados
    )

    # 3. ENSAMBLAJE: Conectar pines a los adaptadores (Inyeccion de Dependencias local)
    propietario = repo_data.get("owner", {}).get("login", "")
    nombre_repo = repo_data.get("name", "")
    
    vcs_client = GitHubApiClient()
    
    # EL CAMBIO CLAVE ESTÁ AQUÍ:
    # Desoldamos OpenAiCodeAuditor y soldamos GeminiCodeAuditor. 
    # Como el adaptador de Gemini se diseñó para tomar el token del PMIC interno, no le pasamos argumentos.
    ai_auditor = GeminiCodeAuditor()

    # 4. EJECUCION: Alimentar la CPU (La Inversión de Dependencias en acción)
    use_case = AuditCommitUseCase(vcs_client=vcs_client, code_auditor=ai_auditor)
    reporte = await use_case.execute(commit_entity)

    # 5. SALIDA: FastAPI serializa automáticamente nuestro modelo Pydantic AuditReport a JSON
    return reporte
