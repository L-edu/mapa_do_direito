from types import SimpleNamespace
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.seguranca import UsuarioAtual, pode_acessar_familia
from app.database import get_db
from app.models import Familia, Simulacao
from app.routers.familias import obter_familia
from app.schemas.comum import ERROS_PADRAO, Pagina, ParametrosPaginacao, paginacao
from app.schemas.familia import SimulacaoAnonima, SimulacaoResposta, SimulacaoResumo
from app.services.elegibilidade import (
    montar_resposta_simulacao,
    simular,
    simular_e_persistir,
)

router = APIRouter(prefix="/api/v1", tags=["Elegibilidade"])

DB = Annotated[Session, Depends(get_db)]


@router.post(
    "/elegibilidade/simular",
    response_model=SimulacaoResposta,
    summary="Simula a elegibilidade sem cadastro (público)",
    description=(
        "Avalia o perfil informado contra todos os programas ativos e devolve, para cada um, "
        "se a família é elegível, quais requisitos já são atendidos e, quando não é elegível, "
        "exatamente o que falta. Nenhum dado é gravado."
    ),
)
def simular_anonimo(dados: SimulacaoAnonima, db: DB):
    familia_virtual = SimpleNamespace(
        **dados.model_dump(exclude={"membros"}),
        membros=[SimpleNamespace(**m.model_dump()) for m in dados.membros],
    )
    perfil, resultados, resumo = simular(db, familia_virtual)
    return SimulacaoResposta(perfil_calculado=perfil, resumo=resumo, resultados=resultados)


@router.post(
    "/familias/{familia_id}/simulacoes",
    response_model=SimulacaoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Simula e registra o resultado no histórico da família",
    responses={**ERROS_PADRAO},
)
def simular_familia(familia_id: int, db: DB, usuario: UsuarioAtual):
    familia = obter_familia(db, familia_id, usuario)
    if not familia.membros:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Cadastre ao menos um membro antes de simular a elegibilidade.",
        )
    simulacao = simular_e_persistir(db, familia)
    return montar_resposta_simulacao(simulacao)


@router.get(
    "/familias/{familia_id}/simulacoes",
    response_model=Pagina[SimulacaoResumo],
    summary="Histórico de simulações da família",
    responses={**ERROS_PADRAO},
)
def listar_simulacoes(
    familia_id: int,
    db: DB,
    usuario: UsuarioAtual,
    params: Annotated[ParametrosPaginacao, Depends(paginacao)],
):
    familia = obter_familia(db, familia_id, usuario)
    todas = sorted(familia.simulacoes, key=lambda s: s.criado_em, reverse=True)
    recorte = todas[params.offset : params.offset + params.tamanho]
    itens = [
        SimulacaoResumo(
            id=s.id,
            familia_id=s.familia_id,
            criado_em=s.criado_em,
            total_elegiveis=sum(1 for r in s.resultados if r.elegivel),
        )
        for s in recorte
    ]
    return Pagina.montar(itens, len(todas), params)


@router.get(
    "/simulacoes/{simulacao_id}",
    response_model=SimulacaoResposta,
    summary="Resultado detalhado de uma simulação",
    responses={**ERROS_PADRAO},
)
def detalhar_simulacao(simulacao_id: int, db: DB, usuario: UsuarioAtual):
    simulacao = db.scalar(
        select(Simulacao)
        .where(Simulacao.id == simulacao_id)
        .options(selectinload(Simulacao.resultados))
    )
    if not simulacao:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Simulação não encontrada.")

    familia = db.get(Familia, simulacao.familia_id) if simulacao.familia_id else None
    if familia and not pode_acessar_familia(usuario, familia):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Simulação de outro cadastro.")
    return montar_resposta_simulacao(simulacao)
