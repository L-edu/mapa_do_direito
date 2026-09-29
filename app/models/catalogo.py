"""Modelos do catálogo: usuários, programas sociais, regras de elegibilidade e parâmetros."""

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # papel: admin | assistente_social | cidadao
    papel: Mapped[str] = mapped_column(String(30), default="cidadao", nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    familias: Mapped[list["Familia"]] = relationship(back_populates="responsavel_cadastro")  # noqa: F821


class Programa(Base):
    """Um programa/benefício social (Bolsa Família, BPC, Tarifa Social...)."""

    __tablename__ = "programas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    orgao: Mapped[str | None] = mapped_column(String(160))
    esfera: Mapped[str] = mapped_column(String(20), default="federal", nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    base_legal: Mapped[str | None] = mapped_column(String(255))
    url_oficial: Mapped[str | None] = mapped_column(String(255))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    regras: Mapped[list["Regra"]] = relationship(
        back_populates="programa", cascade="all, delete-orphan", order_by="Regra.ordem"
    )


class Regra(Base):
    """Regra declarativa de elegibilidade.

    As regras não são codificadas em if/else: ficam no banco como dados, o que permite
    cadastrar um programa novo ou reajustar um limite sem alterar código.

    grupo_logico: regras sem grupo são avaliadas em AND (se obrigatórias).
    Regras que compartilham o mesmo grupo_logico são avaliadas em OR entre si.
    """

    __tablename__ = "regras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    programa_id: Mapped[int] = mapped_column(ForeignKey("programas.id", ondelete="CASCADE"))
    codigo: Mapped[str] = mapped_column(String(60), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    campo: Mapped[str] = mapped_column(String(60), nullable=False)
    operador: Mapped[str] = mapped_column(String(10), nullable=False)
    valor: Mapped[str] = mapped_column(String(120), nullable=False)
    # numero | booleano | texto | lista | intervalo | parametro
    tipo_valor: Mapped[str] = mapped_column(String(20), default="numero", nullable=False)
    obrigatoria: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    grupo_logico: Mapped[str | None] = mapped_column(String(40))
    orientacao: Mapped[str | None] = mapped_column(String(255))
    ordem: Mapped[int] = mapped_column(Integer, default=0)

    programa: Mapped["Programa"] = relationship(back_populates="regras")


class Parametro(Base):
    """Valores de referência versionáveis (salário mínimo, linha de pobreza...)."""

    __tablename__ = "parametros"

    chave: Mapped[str] = mapped_column(String(60), primary_key=True)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(255))
    fonte: Mapped[str | None] = mapped_column(String(255))
    vigencia_inicio: Mapped[date | None] = mapped_column(Date)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=agora, onupdate=agora
    )
