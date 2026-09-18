import re
from pydantic import BaseModel, Field, field_validator


class Commit(BaseModel):
    """
    Representa la trama de datos inmutables de un commit interceptado.
    Actua como entidad de dominio puro: sin dependencias de frameworks web
    ni librerias externa de infraestructura.
    """

    sha: str = Field(
        description="Identificador criptografico unico del commit (SHA-1 de 40 caracteres)"
    )
    author: str = Field(
        description="Nombre o identificador del autor que realizo el commit"
    )
    message: str = Field(
        description="Mensaje descriptivo asociado al commit"
    )
    files_changed: list[str] = Field(
        default_factory=list,
        description="lista de rutas relativas de los archivos afectados en el commit"
    )

    @field_validator("sha")
    @classmethod
    def validador_formato_sha(cls, valor: str) -> str:
        """
        Valida que el SHA cumpal con la especificacion hexadecimal de Git.
        """

        patron_hexadecimal = r"^[0-9a-fA-F]{40}$"
        if not re.fullmatch(patron_hexadecimal, valor):
            raise ValueError(
                "El SHA debe ser una cadena hexadecimal valida de exctamente 40 caracteres"
            )
        return valor.lower()