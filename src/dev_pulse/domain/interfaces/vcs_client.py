from abc import ABC, abstractmethod

class IVcsClient(ABC):
    """Puerto de dominio para la comunicacion con el sistema de control de versiones
    
    Conector estandar de bus para extraccion de telemetria de codigo, independiente
    de si el proveedor es Github, GitLab o un mock de prueba
    """

    @abstractmethod
    async def get_commit_diff(self, commit_sha: str) -> str:
        """
        Obtiene la diferencia textual (diff) del codigo modificado en un commit
        
        Args:
            commit_sha: Hash SHA-1 de 40 caracteres que identifica el commit
            
        Returns:
            Cadena de texto con las lineas agregadas, eliminadas o modificadas
            
        Raises:
            Exception: Si el commit no existe o falla la conexion con el proveedor"""

        pass