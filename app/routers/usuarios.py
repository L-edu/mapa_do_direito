"""Gestão de contas e papéis — restrita a administradores."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.seguranca import exigir_papel, gerar_hash_senha
from app.database import get_db
from app.models import Usuario
from app.schemas.comum import ERROS_PADRAO, Pagina, ParametrosPaginacao, paginacao
from app.schemas.usuario import UsuarioAtualizar, UsuarioCriar, UsuarioResposta

router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuários"],
    dependencies=[Depends(exigir_papel("admin"))],
    responses={401: ERROS_PADRAO[401], 403: ERROS_PADRAO[403]},
)

DB = Annotated[Session, Depends(get_db)]
Admin = Annotated[Usuario, Depends(exigir_papel("admin"))]


@router.get("", response_model=Pagina[UsuarioResposta], summary="Lista usuários (admin)")
def listar_usuarios(
    db: DB,
    params: Annotated[ParametrosPaginacao, Depends(paginacao)],
    busca: str | None = Query(None, description="Busca por nome ou e-mail."),
    papel: str | None = Query(None, description="admin, assistente_social ou cidadao"),
    ativo: bool | None = Query(None),
):
    stmt = select(Usuario)
    if busca:
        termo = f"%{busca}%"
        stmt = stmt.where(or_(Usuario.nome.ilike(termo), Usuario.email.ilike(termo)))
    if papel:
        stmt = stmt.where(Usuario.papel == papel)
    if ativo is not None:
        stmt = stmt.where(Usuario.ativo.is_(ativo))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    itens = db.scalars(stmt.order_by(Usuario.nome).offset(params.offset).limit(params.tamanho)).all()
    return Pagina.montar([UsuarioResposta.model_validate(u) for u in itens], total, params)


@router.post(
    "",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma conta com qualquer papel (admin)",
)
def criar_usuario(dados: UsuarioCriar, db: DB):
    if db.scalar(select(Usuario).where(Usuario.email == dados.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma conta com este e-mail.")
    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
        papel=dados.papel,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch(
    "/{usuario_id}",
    response_model=UsuarioResposta,
    summary="Atualiza papel, situação, nome ou senha (admin)",
    description="Atualização parcial. Um administrador não pode rebaixar nem desativar a própria conta.",
    responses={404: ERROS_PADRAO[404]},
)
def atualizar_usuario(usuario_id: int, dados: UsuarioAtualizar, db: DB, admin: Admin):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário não encontrado.")

    campos = dados.model_dump(exclude_unset=True)
    if usuario.id == admin.id and (campos.get("papel", "admin") != "admin" or campos.get("ativo", True) is False):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Você não pode rebaixar nem desativar a sua própria conta de administrador.",
        )

    senha = campos.pop("senha", None)
    for campo, valor in campos.items():
        setattr(usuario, campo, valor)
    if senha:
        usuario.senha_hash = gerar_hash_senha(senha)
    db.commit()
    db.refresh(usuario)
    return usuario
