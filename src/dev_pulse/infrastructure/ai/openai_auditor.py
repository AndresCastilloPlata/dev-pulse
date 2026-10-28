from openai import AsyncOpenAI

from src.dev_pulse.domain.entities.audit_report import AuditReport
from src.dev_pulse.domain.entities.commit import Commit
from src.dev_pulse.domain.interfaces.code_auditor import ICodeAuditor


class OpenAiCodeAuditor(ICodeAuditor):
    """Adaptador de infraestructura para el motor de inferencia de OpenAI.
    
    Analogia: Coprocesador DSP que recibe datos crudos, aplica reglas de 
    procesamiento heuristico (LLM) y devuelve telemetria estructurada.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        """Inicializa el cliente de OpenAI.
        
        Args:
            api_key: Llave de autenticacion inyectada desde la configuracion segura.
            model: Modelo a utilizar (por defecto gpt-4o-mini para balancear costo/velocidad).
        """
        # Inicializamos el chip cliente oficial asincrono de OpenAI
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def audit_code(self, commit: Commit, code_diff: str) -> AuditReport:
        """Envia el diff al LLM y fuerza una respuesta tipo AuditReport."""
        
        # Instrucciones base de comportamiento (Firmware del coprocesador)
        prompt_sistema = (
            "Eres un auditor de codigo Senior (Tech Lead). "
            "Evalua el siguiente diff de git basandote estrictamente en Clean Architecture, "
            "principios SOLID (SRP, OCP, LSP, ISP, DIP) y PEP 8. "
            "Se implacable pero constructivo. Si el codigo presenta violaciones arquitectonicas, "
            "reduce el 'score' acorde a la gravedad y evalualo como 'REJECTED'. "
            "Si es seguro y limpio, evalualo como 'APPROVED'. "
            "Identifica la linea y el archivo exacto de cada violacion detectada."
        )

        # Carga util (Payload de la señal)
        prompt_usuario = (
            f"Contexto del commit: {commit.message}\n"
            f"Archivos afectados: {commit.files_changed}\n"
            f"Codigo fuente (diff):\n{code_diff}"
        )

        # Invocacion asincrona con Salida Estructurada (parse)
        respuesta = await self._client.beta.chat.completions.parse(
            model=self._model,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario},
            ],
            # ¡La magia ocurre aqui! Obligamos al LLM a devolver exactamente nuestro modelo de dominio
            response_format=AuditReport,
        )

        # El SDK ya instancio y valido el objeto AuditReport por nosotros
        return respuesta.choices[0].message.parsed
