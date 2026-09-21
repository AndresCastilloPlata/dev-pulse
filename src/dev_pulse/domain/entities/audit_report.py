

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class AuditStatus(str, Enum):
    """Estados discretos de evalucion de un commit"""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Violation(BaseModel):
    """
    Detalle puntal de una infraccion a PEP 8 o pricipios SOLID
    Representa la telemetria granular de una falla detectada en el codigo
    """

    file_path: str = Field(
        description="Ruta relativa del archivo inspeccionado"
    )
    line_number: int = Field(
        ge=1,
        description="Numero de linea de codigo donde ocurre la violacion"
    )
    rule: str= Field(
        description="Regla o principio infringido (ej. PEP 8, SRP, OCP)"
    )
    description: str = Field(
        description="Explicacion tecnica y causa del hallazgo"
    )

class AuditReport(BaseModel):
    """
    Reporte consolidado de telemetria y auditoria de calidad de codigo.
    
    Entidad raiz de agregacion que preserva la coherencia entre el puntaje
    cuantitativo y el veredicto cualitativo
    """

    commit_sha: str = Field(
        description="Identificador criptografico unico del commit auditado"
    )
    status: AuditStatus = Field(
        description="Veredicto final de la auditorio (APPROVED o REJECTED)"
    )
    score: int = Field(
        ge=0,
        le=100,
        description="Calificacion cuantitativa de calida acotada entre 0 y 100"
    )
    summary: str = Field(
        description="Resumen ejecutivo del analisis emitido"
    )
    violations: list[Violation] = Field(
        default_factory=list,
        description="Coleccion de violaciones tecnicas detectadas"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Listado de acciones correctivas recomendadas"
    )

    @model_validator(mode="after")
    def validar_coherencia_status_y_score(self) -> AuditReport:
        """
        Invariante de dominio: Enclavamiento logico
        
        Garantiza que ningun reporte con calificacion reprobatorio  <70
        pueda emitirsi con estado APPROVED
        """

        if self.score < 70 and self.status == AuditStatus.APPROVED:
            raise ValueError(
                "Inconsistencia de telemetria: Un reporte con score menor a 70"
                "no puede tener estatus APPROVED"
            )
        return self