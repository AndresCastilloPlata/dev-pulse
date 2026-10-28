import httpx

from src.dev_pulse.domain.interfaces.vcs_client import IVcsClient

class GitHubApiClient(IVcsClient):
    """Adaptador de infraestructura para comunicarse con la API REST de GitHub.

    Analogia: Transceptor fisico de red que adapta las peticiones logicas
    de la CPU a tramas HTTP/TCP hacia el exterior.
    """
    
    def __init__(self, token: str, owner: str, repo: str) -> None:
        """Configura los pines estaticos del transceptor.

        Args:
            token: Credencial de portador (Bearer token) para autenticacion.
            owner: Propietario del repositorio (usuario u organizacion).
            repo: Nombre del repositorio.
        """
        self._token = token
        self._owner = owner
        self._repo = repo
        self._base_url = "https://api.github.com"

    async def get_commit_diff(self, commit_sha: str) -> str:
        """Ejecuta un ciclo de transmision/recepcion (TX/RX) para descargar el diff."""
        url = f"{self._base_url}/repos/{self._owner}/{self._repo}/commits/{commit_sha}"
        
        headers = {
            # Cabecera magica de GitHub para solicitar el archivo diff crudo
            "Accept": "application/vnd.github.v3.diff",
            "Authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        # El bloque 'async with' garantiza que el socket TCP se cierre al terminar
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            # Detector de umbral: si el servidor retorna error (4xx o 5xx),
            # dispara la excepcion HTTPStatusError (la que verificamos en el test).
            response.raise_for_status()
            
            # Si todo esta OK (200), retorna la carga util decodificada en texto
            return response.text