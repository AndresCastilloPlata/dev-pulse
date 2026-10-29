import hmac
import hashlib
from fastapi import APIRouter, Request, Header, HTTPException, Depends

from src.dev_pulse.core.config import Settings

router = APIRouter()

def get_settings() -> Settings:
    """Inyector de dependencias para leer los voltajes del PMIC (.env)."""
    return Settings()

@router.post("/github")
async def github_webhook_receiver(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    settings: Settings = Depends(get_settings)
):
    """Rutina de Interrupcion Externa (ISR) para eventos de GitHub con blindaje HMAC."""
    
    # 1. Verificar si el cable de validacion siquiera esta conectado
    if not x_hub_signature_256:
        raise HTTPException(
            status_code=401, 
            detail="Firma HMAC no proporcionada (Missing Header)."
        )
        
    # 2. Leer la señal en crudo (bytes) exactamente como llego por el cable
    cuerpo_crudo = await request.body()
    
    # 3. Calcular nuestra propia firma local con el secreto protegido
    secreto_bytes = settings.GITHUB_WEBHOOK_SECRET.encode('utf-8')
    firma_calculada = hmac.new(
        key=secreto_bytes, 
        msg=cuerpo_crudo, 
        digestmod=hashlib.sha256
    ).hexdigest()
    
    firma_esperada = f"sha256={firma_calculada}"
    
    # 4. Circuito comparador de tiempo constante (Anti Timing-Attacks)
    if not hmac.compare_digest(x_hub_signature_256, firma_esperada):
        raise HTTPException(
            status_code=401, 
            detail="Firma HMAC invalida o corrupta. Acceso denegado."
        )
        
    # 5. Si el comparador aprueba, la señal esta limpia
    # TODO: En la siguiente iteracion, orquestaremos la llamada al caso de uso aqui.
    return {"status": "ok"}
