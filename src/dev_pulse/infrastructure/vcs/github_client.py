import httpx
from src.dev_pulse.domain.interfaces.vcs_client import IVcsClient
from src.dev_pulse.core.config import settings
import logging

# Configuramos un logger básico para ver los errores asíncronos
logger = logging.getLogger(__name__)

class GitHubApiClient(IVcsClient):
    """Adaptador para interactuar con la API REST de GitHub."""

    def __init__(self):
        # Aislamos el token y los headers exactos que GitHub exige para escritura
        self.token = settings.GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def get_commit_diff(self, commit_sha: str, repo_full_name: str = "AndresCastilloPlata/dev-pulse") -> str:
        """Obtiene la diferencia textual (diff) usando el header 'application/vnd.github.v3.diff'."""
        url = f"https://api.github.com/repos/{repo_full_name}/commits/{commit_sha}"
        
        # Clonamos los headers base pero cambiamos el 'Accept' para pedir el diff en texto crudo
        diff_headers = self.headers.copy()
        diff_headers["Accept"] = "application/vnd.github.v3.diff"
        
        async with httpx.AsyncClient() as client:
            respuesta = await client.get(url, headers=diff_headers)
            respuesta.raise_for_status()
            return respuesta.text

    async def post_commit_comment(self, commit_sha: str, comment: str, repo_full_name: str = "AndresCastilloPlata/dev-pulse") -> bool:
        """Envia el pulso HTTP POST a GitHub para escribir el comentario en el commit."""
        url = f"https://api.github.com/repos/{repo_full_name}/commits/{commit_sha}/comments"
        
        payload = {
            "body": comment
        }
        
        try:
            async with httpx.AsyncClient() as client:
                respuesta = await client.post(url, headers=self.headers, json=payload)
                
                # Si esto falla, el logger lo imprimirá en rojo en la terminal de Uvicorn
                respuesta.raise_for_status() 
                logger.info(f"Comentario publicado con éxito en {commit_sha}")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Fallo al publicar en GitHub: {e.response.status_code} - {e.response.text}")
            raise e
        except Exception as e:
            logger.error(f"Error inesperado de red al contactar GitHub: {str(e)}")
            raise e
