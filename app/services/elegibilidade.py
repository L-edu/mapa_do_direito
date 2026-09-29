"""Orquestra a simulação: carrega programas ativos e parâmetros, chama o motor,
monta o resumo e (opcionalmente) persiste o histórico."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.motor_regras import ResultadoPrograma, avaliar_programas
from app.models import Parametro, Programa, ResultadoSimulacao, Simulacao
from app.services.perfil import montar_perfil

LIMIAR_QUASE_ELEGIVEL = 70.0


def carregar_parametros(db: Session) -> dict[str, float]:
    return {p.chave: p.valor for p in db.scalars(select(Parametro)).all()}


def carregar_programas_ativos(db: Session) -> list[Programa]:
    stmt = (
        select(Programa)
        .where(Programa.ativo.is_(True))
        .options(selectinload(Programa.regras))
        .order_by(Programa.nome)
    )
    return list(db.scalars(stmt).all())


def montar_resumo(resultados: list[ResultadoPrograma]) -> dict:
    return {
        "programas_avaliados": len(resultados),
        "elegivel_em": sum(1 for r in resultados if r.elegivel),
        "quase_elegivel_em": sum(
            1
            for r in resultados
            if not r.elegivel and r.percentual_atendimento >= LIMIAR_QUASE_ELEGIVEL
        ),
    }


def serializar(resultados: list[ResultadoPrograma]) -> list[dict]:
    return [
        {
            "programa_id": r.programa_id,
            "programa_nome": r.programa_nome,
            "elegivel": r.elegivel,
            "percentual_atendimento": r.percentual_atendimento,
            "regras_atendidas": [a.to_dict() for a in r.regras_atendidas],
            "pendencias": [p.to_dict() for p in r.pendencias],
        }
        for r in resultados
    ]


def simular(db: Session, familia_like) -> tuple[dict, list[dict], dict]:
    """Executa a simulação sem gravar nada. Retorna (perfil, resultados, resumo)."""
    perfil = montar_perfil(familia_like)
    programas = carregar_programas_ativos(db)
    parametros = carregar_parametros(db)
    resultados = avaliar_programas(programas, perfil, parametros)
    return perfil, serializar(resultados), montar_resumo(resultados)


def simular_e_persistir(db: Session, familia) -> Simulacao:
    """Executa a simulação de uma família cadastrada e grava o histórico."""
    perfil, resultados, _ = simular(db, familia)

    simulacao = Simulacao(familia_id=familia.id, snapshot=perfil)
    db.add(simulacao)
    db.flush()

    for r in resultados:
        db.add(
            ResultadoSimulacao(
                simulacao_id=simulacao.id,
                programa_id=r["programa_id"],
                programa_nome=r["programa_nome"],
                elegivel=r["elegivel"],
                percentual_atendimento=r["percentual_atendimento"],
                regras_atendidas=r["regras_atendidas"],
                pendencias=r["pendencias"],
            )
        )

    db.commit()
    db.refresh(simulacao)
    return simulacao


def montar_resposta_simulacao(simulacao: Simulacao) -> dict:
    resultados = [
        {
            "programa_id": r.programa_id,
            "programa_nome": r.programa_nome,
            "elegivel": r.elegivel,
            "percentual_atendimento": r.percentual_atendimento,
            "regras_atendidas": r.regras_atendidas,
            "pendencias": r.pendencias,
        }
        for r in simulacao.resultados
    ]
    resultados.sort(key=lambda r: (not r["elegivel"], -r["percentual_atendimento"]))
    return {
        "simulacao_id": simulacao.id,
        "familia_id": simulacao.familia_id,
        "criado_em": simulacao.criado_em,
        "perfil_calculado": simulacao.snapshot,
        "resumo": {
            "programas_avaliados": len(resultados),
            "elegivel_em": sum(1 for r in resultados if r["elegivel"]),
            "quase_elegivel_em": sum(
                1
                for r in resultados
                if not r["elegivel"] and r["percentual_atendimento"] >= LIMIAR_QUASE_ELEGIVEL
            ),
        },
        "resultados": resultados,
    }
