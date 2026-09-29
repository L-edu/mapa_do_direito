"""Padronização do corpo de erro da API.

Toda falha responde no mesmo formato, o que facilita o consumo por qualquer cliente:
    {"erro": {"codigo": "NAO_ENCONTRADO", "mensagem": "...", "detalhes": [...]}}
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.motor_regras import RegraInvalidaError

CODIGOS = {
    400: "REQUISICAO_INVALIDA",
    401: "NAO_AUTENTICADO",
    403: "ACESSO_NEGADO",
    404: "NAO_ENCONTRADO",
    409: "CONFLITO",
    422: "DADOS_INVALIDOS",
    500: "ERRO_INTERNO",
}


def corpo(codigo: str, mensagem: str, detalhes: list | None = None) -> dict:
    return {"erro": {"codigo": codigo, "mensagem": mensagem, "detalhes": detalhes or []}}


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_handler(_: Request, exc: StarletteHTTPException):
        codigo = CODIGOS.get(exc.status_code, "ERRO")
        return JSONResponse(
            status_code=exc.status_code,
            content=corpo(codigo, str(exc.detail)),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validacao_handler(_: Request, exc: RequestValidationError):
        detalhes = [
            {"campo": ".".join(str(p) for p in e["loc"][1:]), "mensagem": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=corpo("DADOS_INVALIDOS", "Há campos inválidos na requisição.", detalhes),
        )

    @app.exception_handler(RegraInvalidaError)
    async def regra_handler(_: Request, exc: RegraInvalidaError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=corpo("REGRA_INVALIDA", str(exc)),
        )
