from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.seguranca import (
    UsuarioAtual,
    criar_token,
    gerar_hash_senha,
    verificar_senha,
)
from app.database import get_db
from app.models import Usuario
from app.schemas.comum import ERROS_PADRAO
from app.schemas.usuario import LoginRequisicao, TokenResposta, UsuarioRegistro, UsuarioResposta

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])

DB = Annotated[Session, Depends(get_db)]


@router.post(
    "/registrar",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova conta",
    description=(
        "Cadastro público. A conta nasce sempre com o papel `cidadao`; contas de "
        "assistente social e administrador são criadas por um administrador em `/usuarios`."
    ),
)
def registrar(dados: UsuarioRegistro, db: DB):
    existente = db.scalar(select(Usuario).where(Usuario.email == dados.email))
    if existente:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma conta com este e-mail.")

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
        papel="cidadao",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post(
    "/login",
    response_model=TokenResposta,
    summary="Autentica e devolve o token JWT",
    responses={401: ERROS_PADRAO[401]},
)
def login(dados: LoginRequisicao, db: DB):
    usuario = db.scalar(select(Usuario).where(Usuario.email == dados.email))
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash) or not usuario.ativo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos.")

    return TokenResposta(
        access_token=criar_token(usuario),
        expira_em_minutos=settings.JWT_EXPIRACAO_MINUTOS,
        usuario=UsuarioResposta.model_validate(usuario),
    )


@router.get(
    "/me",
    response_model=UsuarioResposta,
    summary="Dados do usuário autenticado",
    responses={401: ERROS_PADRAO[401]},
)
def eu(usuario: UsuarioAtual):
    return usuario
