"""Parâmetros de referência e relatórios agregados para gestores públicos."""

from collections import Counter
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.seguranca import exigir_papel
from app.database import get_db
from app.models import Familia, Parametro
from app.schemas.comum import ERROS_PADRAO
from app.schemas.programa import ParametroAtualizar, ParametroResposta
from app.services.elegibilidade import (
    carregar_parametros,
    carregar_programas_ativos,
    montar_resumo,
)
from app.core.motor_regras import avaliar_programas
from app.services.perfil import montar_perfil

router = APIRouter(prefix="/api/v1", tags=["Gestão"])

DB = Annotated[Session, Depends(get_db)]
SomenteAdmin = Depends(exigir_papel("admin"))


@router.get(
    "/parametros",
    response_model=list[ParametroResposta],
    summary="Valores de referência vigentes",
    description=(
        "Salário mínimo, linha de pobreza e demais valores usados pelas regras. "
        "Atualizar um parâmetro reajusta automaticamente todas as regras derivadas dele."
    ),
)
def listar_parametros(db: DB):
    return db.scalars(select(Parametro).order_by(Parametro.chave)).all()


@router.put(
    "/parametros/{chave}",
    response_model=ParametroResposta,
    summary="Atualiza ou cria um parâmetro (admin)",
    dependencies=[SomenteAdmin],
    responses={401: ERROS_PADRAO[401], 403: ERROS_PADRAO[403]},
)
def atualizar_parametro(chave: str, dados: ParametroAtualizar, db: DB):
    parametro = db.get(Parametro, chave)
    if parametro is None:
        parametro = Parametro(chave=chave, **dados.model_dump())
        db.add(parametro)
    else:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(parametro, campo, valor)
    db.commit()
    db.refresh(parametro)
    return parametro


@router.get(
    "/relatorios/cobertura",
    summary="Cobertura potencial por programa (admin)",
    description=(
        "Reavalia todas as famílias cadastradas e informa quantas seriam elegíveis a cada "
        "programa. Indicador de referência para o monitoramento da meta 1.3 do ODS 1."
    ),
    dependencies=[SomenteAdmin],
    responses={401: ERROS_PADRAO[401], 403: ERROS_PADRAO[403]},
)
def cobertura(db: DB, municipio: str | None = Query(None), uf: str | None = Query(None)):
    stmt = select(Familia).options(selectinload(Familia.membros))
    if municipio:
        stmt = stmt.where(Familia.municipio.ilike(f"%{municipio}%"))
    if uf:
        stmt = stmt.where(Familia.uf == uf.upper())

    familias = list(db.scalars(stmt).all())
    programas = carregar_programas_ativos(db)
    parametros = carregar_parametros(db)

    elegiveis = Counter()
    sem_nenhum = 0
    for familia in familias:
        resultados = avaliar_programas(programas, montar_perfil(familia), parametros)
        resumo = montar_resumo(resultados)
        if resumo["elegivel_em"] == 0:
            sem_nenhum += 1
        for r in resultados:
            if r.elegivel:
                elegiveis[r.programa_nome] += 1

    total = len(familias)
    return {
        "filtros": {"municipio": municipio, "uf": uf},
        "total_familias": total,
        "familias_sem_nenhum_beneficio": sem_nenhum,
        "cobertura_por_programa": [
            {
                "programa": p.nome,
                "familias_elegiveis": elegiveis.get(p.nome, 0),
                "percentual": round(elegiveis.get(p.nome, 0) / total * 100, 1) if total else 0.0,
            }
            for p in programas
        ],
    }


@router.get(
    "/relatorios/pendencias-frequentes",
    summary="Requisitos que mais reprovam (admin)",
    description=(
        "Ranking dos requisitos que mais bloqueiam o acesso a benefícios. "
        "Ajuda a direcionar busca ativa: se o campeão for a ausência de CadÚnico, "
        "o gargalo é cadastral, não de renda."
    ),
    dependencies=[SomenteAdmin],
    responses={401: ERROS_PADRAO[401], 403: ERROS_PADRAO[403]},
)
def pendencias_frequentes(db: DB, limite: int = Query(10, ge=1, le=50)):
    familias = list(db.scalars(select(Familia).options(selectinload(Familia.membros))).all())
    programas = carregar_programas_ativos(db)
    parametros = carregar_parametros(db)

    contagem: Counter = Counter()
    descricoes: dict[str, str] = {}
    for familia in familias:
        for resultado in avaliar_programas(programas, montar_perfil(familia), parametros):
            for pendencia in resultado.pendencias:
                contagem[pendencia.codigo] += 1
                descricoes[pendencia.codigo] = pendencia.descricao

    return {
        "familias_analisadas": len(familias),
        "pendencias": [
            {"codigo": codigo, "descricao": descricoes[codigo], "ocorrencias": qtd}
            for codigo, qtd in contagem.most_common(limite)
        ],
    }


@router.get("/health", tags=["Infraestrutura"], summary="Healthcheck")
def health(db: DB):
    try:
        db.scalar(select(Parametro).limit(1))
        return {"status": "ok", "banco": "conectado"}
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f"Banco indisponível: {exc}")
