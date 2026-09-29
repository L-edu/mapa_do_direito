"""Schemas reutilizáveis: envelope de paginação e de erro."""

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class ParametrosPaginacao(BaseModel):
    pagina: int = Field(1, ge=1)
    tamanho: int = Field(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.pagina - 1) * self.tamanho


def paginacao(
    pagina: int = Query(1, ge=1, description="Página desejada, começando em 1."),
    tamanho: int = Query(20, ge=1, le=100, description="Itens por página (máx. 100)."),
) -> ParametrosPaginacao:
    return ParametrosPaginacao(pagina=pagina, tamanho=tamanho)


class Pagina(BaseModel, Generic[T]):
    itens: list[T]
    total: int
    pagina: int
    tamanho: int
    total_paginas: int

    @classmethod
    def montar(cls, itens: list[T], total: int, params: ParametrosPaginacao) -> "Pagina[T]":
        total_paginas = (total + params.tamanho - 1) // params.tamanho if total else 0
        return cls(
            itens=itens,
            total=total,
            pagina=params.pagina,
            tamanho=params.tamanho,
            total_paginas=total_paginas,
        )


class DetalheErro(BaseModel):
    codigo: str
    mensagem: str
    detalhes: list = []


class RespostaErro(BaseModel):
    erro: DetalheErro


ERROS_PADRAO = {
    401: {"model": RespostaErro, "description": "Token ausente ou inválido"},
    403: {"model": RespostaErro, "description": "Papel sem permissão para a operação"},
    404: {"model": RespostaErro, "description": "Recurso não encontrado"},
}
