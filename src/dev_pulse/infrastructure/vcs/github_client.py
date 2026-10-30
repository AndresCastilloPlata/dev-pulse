import httpx
from typing import Dict, Any

# 1. Importamos el chip con el nombre exacto del datasheet
from src.dev_pulse.domain.interfaces.vcs_client import IVcsClient
from src.dev_pulse.core.config import settings

# 2. Heredamos de la interfaz correcta
class GitHubApiClient(IVcsClient):
    """Adaptador físico para comunicarse con la API de GitHub."""
    
    def __init__(self):
        token = settings.GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    # 3. Usamos el nombre de método exacto que pide la interfaz
    async def get_commit_diff(self, commit_sha: str, repo_full_name: str = "AndresCastilloPlata/dev-pulse") -> str:
        """Descarga los cambios físicos (diff) de un commit."""
        url = f"https://api.github.com/repos/{repo_full_name}/commits/{commit_sha}"
        
        async with httpx.AsyncClient(headers=self.headers) as client:
            respuesta = await client.get(url)
            respuesta.raise_for_status() 
            
            datos = respuesta.json()
            
            archivos_modificados = []
            for archivo in datos.get("files", []):
                nombre = archivo.get("filename")
                parche = archivo.get("patch", "Sin cambios en texto (binario/imagen)")
                archivos_modificados.append(f"--- Archivo: {nombre} ---\n{parche}")
                
            return "\n\n".join(archivos_modificados)
