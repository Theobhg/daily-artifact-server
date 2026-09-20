"""Ponto de entrada da Daily Artifact API."""

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response

from app.config import settings
from app.database import init_db
from app.exceptions import DomainError
from app.routers import artifacts

API_DESCRIPTION = """
**One day. One artifact.**

A Daily Artifact API guarda um unico artefato por dia: um texto, uma citacao,
uma foto, um link ou uma musica que represente aquele dia. Ao longo do ano, a
colecao vira uma representacao visual das proprias memorias.

### Regras de negocio

* Existe **no maximo um artefato por data** (garantido por constraint no banco
  e validado pela aplicacao). Datas repetidas respondem `409 Conflict`.
* Nao e permitido registrar artefatos em **datas futuras** (`400 Bad Request`).
* Artefatos do tipo `text` e `quote` exigem `content`.
* Artefatos do tipo `photo`, `link` e `music` exigem `url`; `content` fica
  disponivel como legenda ou comentario.
* Tags sao enviadas como lista de strings, normalizadas em minusculas e
  reaproveitadas entre artefatos (relacionamento N:N).
"""


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Cria o banco SQLite e as tabelas antes de atender requisicoes."""
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description=API_DESCRIPTION,
    version=settings.app_version,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "artifacts",
            "description": "Registro, consulta, edicao e remocao de artefatos diarios.",
        }
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    # Sem credenciais: o frontend roda via file://, cujo Origin e "null".
    # Habilitar credenciais invalidaria o wildcard "*".
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def allow_private_network_access(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Libera o acesso a rede local no preflight.

    Navegadores baseados em Chromium aplicam Private Network Access: uma pagina
    aberta via file:// que chama 127.0.0.1 so e liberada se o preflight
    responder com este cabecalho.
    """
    response = await call_next(request)
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


@app.exception_handler(DomainError)
async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
    """Traduz erros de dominio para respostas HTTP consistentes."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Leva quem abre a raiz da API direto para a documentacao."""
    return RedirectResponse(url="/docs")


app.include_router(artifacts.router)
