"""Autenticação JWT, hash de senha e controle de acesso por papel."""

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Usuario

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

PAPEIS_VALIDOS = ("admin", "assistente_social", "cidadao")


def gerar_hash_senha(senha: str) -> str:
    """PBKDF2-SHA256 da biblioteca padrão: sem dependência nativa, e seguro o bastante."""
    sal = hashlib.sha256(settings.SALT_IDENTIFICADOR.encode()).hexdigest()[:16]
    derivada = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal.encode(), 120_000)
    return f"pbkdf2_sha256${sal}${derivada.hex()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        _, sal, esperado = senha_hash.split("$")
    except ValueError:
        return False
    derivada = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal.encode(), 120_000).hex()
    return hmac.compare_digest(derivada, esperado)


def gerar_identificador(semente: str) -> str:
    """Identificador opaco da família. Nunca armazenamos CPF ou NIS em texto claro."""
    bruto = f"{settings.SALT_IDENTIFICADOR}:{semente}".encode()
    return hashlib.sha256(bruto).hexdigest()[:24].upper()


def criar_token(usuario: Usuario) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRACAO_MINUTOS)
    payload = {"sub": str(usuario.id), "email": usuario.email, "papel": usuario.papel, "exp": expira}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITMO)


def usuario_atual(
    token: Annotated[str | None, Depends(oauth2)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    nao_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou ausentes.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise nao_autorizado
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITMO])
        usuario_id = int(payload.get("sub", 0))
    except (JWTError, ValueError):
        raise nao_autorizado from None

    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.ativo:
        raise nao_autorizado
    return usuario


UsuarioAtual = Annotated[Usuario, Depends(usuario_atual)]


def exigir_papel(*papeis: str):
    """Dependência de autorização: `Depends(exigir_papel("admin"))`."""

    def verificador(usuario: UsuarioAtual) -> Usuario:
        if usuario.papel not in papeis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito aos papéis: {', '.join(papeis)}.",
            )
        return usuario

    return verificador


def pode_acessar_familia(usuario: Usuario, familia) -> bool:
    return usuario.papel == "admin" or familia.criado_por_id == usuario.id
