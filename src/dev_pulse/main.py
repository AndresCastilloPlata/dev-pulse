from fastapi import FastAPI

# Importamos nuestro módulo de configuración para validar voltajes al encender
from src.dev_pulse.core.config import Settings
# Importamos nuestro Optoacoplador (Webhook)
from src.dev_pulse.presentation.api.webhooks import router as github_webhook_router

def create_app() -> FastAPI:
    """Fabrica y ensambla la placa madre del servidor (FastAPI)."""
    
    # 1. Enclavamiento de seguridad: Obligamos al PMIC a leer el .env justo al arrancar.
    # Si faltan claves (como OPENAI_API_KEY), esto arrojará ValidationError y el servidor
    # se negará a iniciar, aplicando nuestro principio "Fail-Fast".
    Settings()
    
    # 2. Instanciamos el chasis
    app = FastAPI(
        title="Dev-Pulse",
        description="Microservicio de auditoría de código automatizada con IA.",
        version="1.0.0",
    )
    
    # 3. Soldamos el LED de estado (Health Check)
    @app.get("/health", tags=["System"])
    async def health_check():
        return {"status": "online", "service": "Dev-Pulse"}
        
    # 4. Soldamos el bus de entrada del webhook
    app.include_router(github_webhook_router)
    
    return app

# Esta es la instancia global que buscará el servidor web (Uvicorn) para arrancar
app = create_app()
