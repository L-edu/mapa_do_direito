from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.seguranca import (
    UsuarioAtual,
    exigir_papel,
    gerar_identificador,
    pode_acessar_familia,
)
from app.database import get_db
from app.models import Familia, Membro
from app.schemas.comum import ERROS_PADRAO, Pagina, ParametrosPaginacao, paginacao
from app.schemas.familia import (
    FamiliaAtualizar,
    FamiliaCriar,
    FamiliaResposta,
    FamiliaResumo,
    MembroAtualizar,
    MembroCriar,
    MembroResposta,
)
from app.services.perfil import calcular_idade, montar_perfil

router = APIRouter(prefix="/api/v1", tags=["Famílias"])

DB = Annotated[Session, Depends(get_db)]
Cadastrador = Depends(exigir_papel("admin", "assistente_social"))


def montar_resposta_familia(familia: Familia) -> FamiliaResposta:
    resposta = FamiliaResposta.model_validate(familia)
    resposta.membros = [
        MembroResposta.model_validate(m).model_copy(
            update={"idade": calcular_idade(m.data_nascimento)}
        )
        for m in familia.membros
    ]
    resposta.perfil_calculado = montar_perfil(familia)
    return resposta


def obter_familia(db: Session, familia_id: int, usuario) -> Familia:
    familia = db.scalar(
        select(Familia).where(Familia.id == familia_id).options(selectinload(Familia.membros))
    )
    if not familia:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Família não encontrada.")
    if not pode_acessar_familia(usuario, familia):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Esta família pertence a outro cadastro.")
    return familia


@router.post(
    "/familias",
    response_model=FamiliaResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra uma família",
    description=(
        "Disponível para assistentes sociais e administradores. Por conformidade com a LGPD, "
        "a API não recebe CPF, NIS ou qualquer identificador direto: a família recebe um "
        "código interno opaco."
    ),
    dependencies=[Cadastrador],
    responses={401: ERROS_PADRAO[401], 403: ERROS_PADRAO[403]},
)
def criar_familia(dados: FamiliaCriar, db: DB, usuario: UsuarioAtual):
    familia = Familia(
        **dados.model_dump(exclude={"membros"}),
        identificador=gerar_identificador(uuid4().hex),
        criado_por_id=usuario.id,
    )
    familia.membros = [Membro(**m.model_dump()) for m in dados.membros]
    db.add(familia)
    db.commit()
    db.refresh(familia)
    return montar_resposta_familia(familia)


@router.get(
    "/familias",
    response_model=Pagina[FamiliaResumo],
    summary="Lista famílias cadastradas",
    description="Administradores veem todas; assistentes sociais veem apenas os próprios cadastros.",
    dependencies=[Cadastrador],
    responses={401: ERROS_PADRAO[401], 403: ERROS_PADRAO[403]},
)
def listar_familias(
    db: DB,
    usuario: UsuarioAtual,
    params: Annotated[ParametrosPaginacao, Depends(paginacao)],
    municipio: str | None = Query(None),
    uf: str | None = Query(None, min_length=2, max_length=2),
    possui_cadunico: bool | None = Query(None),
):
    stmt = select(Familia)
    if usuario.papel != "admin":
        stmt = stmt.where(Familia.criado_por_id == usuario.id)
    if municipio:
        stmt = stmt.where(Familia.municipio.ilike(f"%{municipio}%"))
    if uf:
        stmt = stmt.where(Familia.uf == uf.upper())
    if possui_cadunico is not None:
        stmt = stmt.where(Familia.possui_cadunico.is_(possui_cadunico))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    itens = db.scalars(
        stmt.order_by(Familia.criado_em.desc()).offset(params.offset).limit(params.tamanho)
    ).all()
    return Pagina.montar([FamiliaResumo.model_validate(i) for i in itens], total, params)


@router.get(
    "/familias/{familia_id}",
    response_model=FamiliaResposta,
    summary="Detalha uma família com o perfil calculado",
    responses={**ERROS_PADRAO},
)
def detalhar_familia(familia_id: int, db: DB, usuario: UsuarioAtual):
    return montar_resposta_familia(obter_familia(db, familia_id, usuario))


@router.put(
    "/familias/{familia_id}",
    response_model=FamiliaResposta,
    summary="Atualiza os dados da família",
    responses={**ERROS_PADRAO},
)
def atualizar_familia(familia_id: int, dados: FamiliaAtualizar, db: DB, usuario: UsuarioAtual):
    familia = obter_familia(db, familia_id, usuario)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(familia, campo, valor.upper() if campo == "uf" else valor)
    db.commit()
    db.refresh(familia)
    return montar_resposta_familia(familia)


@router.delete(
    "/familias/{familia_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui a família e todo o seu histórico (admin)",
    dependencies=[Depends(exigir_papel("admin"))],
    responses={**ERROS_PADRAO},
)
def excluir_familia(familia_id: int, db: DB, usuario: UsuarioAtual):
    familia = obter_familia(db, familia_id, usuario)
    db.delete(familia)
    db.commit()


@router.post(
    "/familias/{familia_id}/membros",
    response_model=MembroResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Adiciona um membro à família",
    responses={**ERROS_PADRAO},
)
def adicionar_membro(familia_id: int, dados: MembroCriar, db: DB, usuario: UsuarioAtual):
    familia = obter_familia(db, familia_id, usuario)
    membro = Membro(familia_id=familia.id, **dados.model_dump())
    db.add(membro)
    db.commit()
    db.refresh(membro)
    return MembroResposta.model_validate(membro).model_copy(
        update={"idade": calcular_idade(membro.data_nascimento)}
    )


@router.get(
    "/familias/{familia_id}/membros",
    response_model=list[MembroResposta],
    summary="Lista os membros da família",
    responses={**ERROS_PADRAO},
)
def listar_membros(familia_id: int, db: DB, usuario: UsuarioAtual):
    familia = obter_familia(db, familia_id, usuario)
    return [
        MembroResposta.model_validate(m).model_copy(
            update={"idade": calcular_idade(m.data_nascimento)}
        )
        for m in familia.membros
    ]


@router.put(
    "/membros/{membro_id}",
    response_model=MembroResposta,
    summary="Atualiza um membro",
    responses={**ERROS_PADRAO},
)
def atualizar_membro(membro_id: int, dados: MembroAtualizar, db: DB, usuario: UsuarioAtual):
    membro = db.get(Membro, membro_id)
    if not membro:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Membro não encontrado.")
    obter_familia(db, membro.familia_id, usuario)

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(membro, campo, valor)
    db.commit()
    db.refresh(membro)
    return MembroResposta.model_validate(membro).model_copy(
        update={"idade": calcular_idade(membro.data_nascimento)}
    )


@router.delete(
    "/membros/{membro_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um membro",
    responses={**ERROS_PADRAO},
)
def remover_membro(membro_id: int, db: DB, usuario: UsuarioAtual):
    membro = db.get(Membro, membro_id)
    if not membro:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Membro não encontrado.")
    obter_familia(db, membro.familia_id, usuario)
    db.delete(membro)
    db.commit()
