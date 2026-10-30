from abc import ABC, abstractmethod

class IVcsClient(ABC):
    """Puerto de dominio para la comunicacion con el sistema de control de versiones"""

    @abstractmethod
    async def get_commit_diff(self, commit_sha: str) -> str:
        """Obtiene la diferencia textual (diff) del codigo modificado en un commit"""
        pass

    # EL NUEVO PIN TX:
    @abstractmethod
    async def post_commit_comment(self, commit_sha: str, comment: str) -> bool:
        """
        Publica un comentario de auditoria directamente en el commit del repositorio.
        
        Args:
            commit_sha: Hash SHA-1 de 40 caracteres que identifica el commit.
            comment: El texto (en formato Markdown) que la IA escribira.
            
        Returns:
            True si el comentario se publico con exito.
        """
        pass
