from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Modulo supervisor y regulador de variables de entorno del sistema.

    Analogia: PMIC (Power Management Integrated Circuit) que valida tensiones
    de entrada antes de energizar el nucleo del microservicio.
    """

    # Secretos criticos obligatorios (Lineas de alimentacion principales)
    OPENAI_API_KEY: str = Field(
        ...,
        description="Llave secreta de autenticacion para la API de inferencia OpenAI.",
    )
    GITHUB_WEBHOOK_SECRET: str = Field(
        ...,
        description="Token secreto compartido para validar la firma HMAC SHA-256 de GitHub.",
    )

    # Parametros operativos con valores por defecto seguros (Pull-ups internos)
    OPENAI_MODEL: str = Field(
        default="gpt-4o-mini",
        description="Modelo de lenguaje utilizado para la auditoria de codigo.",
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Entorno de ejecucion (development, staging, production).",
    )
    PORT: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Puerto de red TCP para exponer el servidor ASGI.",
    )

    # Configuracion del decodificador de seÃ±ales externas
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignora ruidos o variables externas ajenas al servicio
    )