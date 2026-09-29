from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Papel = Literal["admin", "assistente_social", "cidadao"]


class UsuarioCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=120, examples=["Maria Souza"])
    email: EmailStr = Field(examples=["maria@cras.salvador.ba.gov.br"])
    senha: str = Field(min_length=8, max_length=72, examples=["senhaSegura123"])
    papel: Papel = Field("cidadao", description="Apenas administradores podem criar outro admin.")


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    papel: Papel
    ativo: bool
    criado_em: datetime


class LoginRequisicao(BaseModel):
    email: EmailStr
    senha: str


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_em_minutos: int
    usuario: UsuarioResposta
