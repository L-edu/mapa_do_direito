from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.seguranca import exigir_papel
from app.database import get_db
from app.models import Programa, Regra
from app.schemas.comum import ERROS_PADRAO, Pagina, ParametrosPaginacao, paginacao
from app.schemas.programa import (
    ProgramaAtualizar,
    ProgramaCriar,
    ProgramaResposta,
    ProgramaResumo,
    RegraCriar,
    RegraResposta,
    RequisitoLegivel,
)

router = APIRouter(prefix="/api/v1", tags=["Programas"])

DB = Annotated[Session, Depends(get_db)]
SomenteAdmin = Depends(exigir_papel("admin"))

ROTULO_OPERADOR = {
    "==": "igual a",
    "!=": "diferente de",
    "<": "menor que",
    "<=": "menor ou igual a",
    ">": "maior que",
    ">=": "maior ou igual a",
    "in": "entre as opções",
    "entre": "no intervalo",
}


def buscar_programa(db: Session, programa_id: int) -> Programa:
    programa = db.scalar(
        select(Programa).where(Programa.id == programa_id).options(selectinload(Programa.regras))
    )
    if not programa:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Programa não encontrado.")
    return programa


@router.get(
    "/programas",
    response_model=Pagina[ProgramaResumo],
    summary="Lista os programas do catálogo",
    description="Endpoint público e paginado. Aceita filtros por esfera, situação e texto livre.",
)
def listar_programas(
    db: DB,
    params: Annotated[ParametrosPaginacao, Depends(paginacao)],
    esfera: str | None = Query(None, description="federal, estadual ou municipal"),
    ativo: bool | None = Query(None),
    busca: str | None = Query(None, description="Busca por nome ou órgão responsável."),
):
    stmt = select(Programa)
    if esfera:
        stmt = stmt.where(Programa.esfera == esfera)
    if ativo is not None:
        stmt = stmt.where(Programa.ativo.is_(ativo))
    if busca:
        termo = f"%{busca}%"
        stmt = stmt.where(or_(Programa.nome.ilike(termo), Programa.orgao.ilike(termo)))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    itens = db.scalars(
        stmt.order_by(Programa.nome).offset(params.offset).limit(params.tamanho)
    ).all()
    return Pagina.montar([ProgramaResumo.model_validate(i) for i in itens], total, params)


@router.get(
    "/programas/{programa_id}",
    response_model=ProgramaResposta,
    summary="Detalha um programa e suas regras",
    responses={404: ERROS_PADRAO[404]},
)
def detalhar_programa(programa_id: int, db: DB):
    return buscar_programa(db, programa_id)


@router.get(
    "/programas/{programa_id}/requisitos",
    response_model=list[RequisitoLegivel],
    summary="Requisitos em linguagem simples",
    description="Traduz as regras declarativas para frases legíveis por qualquer cidadão.",
    responses={404: ERROS_PADRAO[404]},
)
def requisitos(programa_id: int, db: DB):
    programa = buscar_programa(db, programa_id)
    return [
        RequisitoLegivel(
            codigo=r.codigo,
            descricao=r.descricao,
            obrigatorio=r.obrigatoria and not r.grupo_logico,
            condicao=f"{r.campo} {ROTULO_OPERADOR.get(r.operador, r.operador)} {r.valor}",
        )
        for r in programa.regras
    ]


@router.post(
    "/programas",
    response_model=ProgramaResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um programa (admin)",
    dependencies=[SomenteAdmin],
    responses={401: ERROS_PADRAO[401], 403: ERROS_PADRAO[403]},
)
def criar_programa(dados: ProgramaCriar, db: DB):
    if db.scalar(select(Programa).where(Programa.slug == dados.slug)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um programa com este slug.")

    programa = Programa(**dados.model_dump(exclude={"regras"}))
    programa.regras = [Regra(**r.model_dump()) for r in dados.regras]
    db.add(programa)
    db.commit()
    db.refresh(programa)
    return programa


@router.put(
    "/programas/{programa_id}",
    response_model=ProgramaResposta,
    summary="Atualiza um programa (admin)",
    dependencies=[SomenteAdmin],
    responses={**ERROS_PADRAO},
)
def atualizar_programa(programa_id: int, dados: ProgramaAtualizar, db: DB):
    programa = buscar_programa(db, programa_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(programa, campo, valor)
    db.commit()
    db.refresh(programa)
    return programa


@router.delete(
    "/programas/{programa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativa um programa (admin)",
    description="Exclusão lógica: o histórico de simulações continua íntegro.",
    dependencies=[SomenteAdmin],
    responses={**ERROS_PADRAO},
)
def desativar_programa(programa_id: int, db: DB):
    programa = buscar_programa(db, programa_id)
    programa.ativo = False
    db.commit()


@router.post(
    "/programas/{programa_id}/regras",
    response_model=RegraResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Adiciona uma regra de elegibilidade (admin)",
    dependencies=[SomenteAdmin],
    responses={**ERROS_PADRAO},
)
def adicionar_regra(programa_id: int, dados: RegraCriar, db: DB):
    programa = buscar_programa(db, programa_id)
    regra = Regra(programa_id=programa.id, **dados.model_dump())
    db.add(regra)
    db.commit()
    db.refresh(regra)
    return regra


@router.delete(
    "/regras/{regra_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove uma regra (admin)",
    dependencies=[SomenteAdmin],
    responses={**ERROS_PADRAO},
)
def remover_regra(regra_id: int, db: DB):
    regra = db.get(Regra, regra_id)
    if not regra:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Regra não encontrada.")
    db.delete(regra)
    db.commit()
