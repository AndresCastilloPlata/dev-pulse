import pytest
from httpx import HTTPStatusError

# Falla controlada: Intentamos importar el transceptor físico que aún no existe
from src.dev_pulse.infrastructure.vcs.github_client import GitHubApiClient


@pytest.mark.asyncio
async def test_obtener_diff_exitoso(httpx_mock: pytest.MonkeyPatch) -> None:
    """Verifica la decodificacion correcta de la señal cuando el nodo remoto responde 200 OK."""
    # 1. ARRANGE: Configuramos el generador de señales (httpx_mock) para simular a GitHub
    commit_sha = "a1b2c3d4e5f"
    repo_owner = "SilverCastleLabs"
    repo_name = "dev-pulse"
    token = "simulador-token-seguro"
    
    # La señal que esperamos recibir por el cable
    diff_simulado = "@@ -1 +1 @@\n-codigo viejo\n+codigo nuevo\n"

    # Interceptamos la llamada HTTP para que no salga a internet real
    url_esperada = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{commit_sha}"
    httpx_mock.add_response(
        url=url_esperada,
        headers={"Accept": "application/vnd.github.v3.diff"},
        text=diff_simulado,
        status_code=200,
    )

    # Energizamos nuestro adaptador inyectando las credenciales
    cliente = GitHubApiClient(token=token, owner=repo_owner, repo=repo_name)

    # 2. ACT: Disparamos la petición
    resultado = await cliente.get_commit_diff(commit_sha)

    # 3. ASSERT: Comprobamos que decodificó el texto intacto
    assert resultado == diff_simulado


@pytest.mark.asyncio
async def test_falla_con_commit_inexistente(httpx_mock: pytest.MonkeyPatch) -> None:
    """Verifica que el transceptor propague una interrupcion de error HTTP 404."""
    commit_sha = "hash_falso_123"
    
    # Simulamos que GitHub responde "Not Found" (404)
    httpx_mock.add_response(
        url=f"https://api.github.com/repos/SilverCastleLabs/dev-pulse/commits/{commit_sha}",
        status_code=404,
    )

    cliente = GitHubApiClient(token="dummy", owner="SilverCastleLabs", repo="dev-pulse")

    # Si la señal externa es un error, el adaptador debe levantar una excepción clara
    with pytest.raises(HTTPStatusError) as exc_info:
        await cliente.get_commit_diff(commit_sha)

    # Comprobamos que la interrupción capturada sea exactamente el error 404
    assert exc_info.value.response.status_code == 404
