from google import genai
from google.genai import types

from src.dev_pulse.domain.interfaces.code_auditor import ICodeAuditor
from src.dev_pulse.domain.entities.audit_report import AuditReport
from src.dev_pulse.domain.entities.commit import Commit
from src.dev_pulse.core.config import settings

class GeminiCodeAuditor(ICodeAuditor):
    """Adaptador físico para interactuar con los modelos de Google Gemini."""

    def __init__(self):
        # Energizamos el cliente con el voltaje del PMIC
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    # EL CAMBIO: Recibimos los dos cables exactos que envía el Caso de Uso
    async def audit_code(self, commit: Commit, code_diff: str) -> AuditReport:
        prompt = (
            f"Eres un Ingeniero de Software Senior. Evalúa el commit '{commit.message}' "
            f"realizado por {commit.author}.\n"
            "Busca vulnerabilidades (llaves expuestas), malas prácticas (código espagueti), "
            "o violaciones de Clean Architecture.\n\n"
            f"Código Diff:\n{code_diff}"
        )
        
        # Invocamos la inferencia usando la función asíncrona (aio)
        respuesta = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AuditReport, # Magia: Mapea directo a nuestra entidad Pydantic
                temperature=0.2,
            )
        )
        
        # Deserializamos el JSON de Gemini de vuelta a nuestra Entidad de Dominio
        return AuditReport.model_validate_json(respuesta.text)
