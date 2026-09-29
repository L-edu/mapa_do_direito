"""Modelos do cadastro socioeconômico e das simulações de elegibilidade.

LGPD: nenhum identificador direto (CPF, NIS, RG) é armazenado. A família recebe um
identificador interno opaco e os membros são registrados apenas com o primeiro nome
e os atributos estritamente necessários para avaliar o direito ao benefício.
"""

from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.catalogo import agora


class Familia(Base):
    __tablename__ = "familias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identificador: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    municipio: Mapped[str] = mapped_column(String(120), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    renda_total_mensal: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    # propria | alugada | cedida | situacao_rua
    situacao_moradia: Mapped[str] = mapped_column(String(30), default="alugada", nullable=False)
    possui_cadunico: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    criado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=agora, onupdate=agora
    )

    membros: Mapped[list["Membro"]] = relationship(
        back_populates="familia", cascade="all, delete-orphan"
    )
    simulacoes: Mapped[list["Simulacao"]] = relationship(
        back_populates="familia", cascade="all, delete-orphan"
    )
    responsavel_cadastro: Mapped["Usuario | None"] = relationship(back_populates="familias")  # noqa: F821


class Membro(Base):
    __tablename__ = "membros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    familia_id: Mapped[int] = mapped_column(ForeignKey("familias.id", ondelete="CASCADE"))
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    # responsavel | conjuge | filho | pai | mae | outro
    parentesco: Mapped[str] = mapped_column(String(30), default="outro", nullable=False)
    escolaridade: Mapped[str | None] = mapped_column(String(40))
    renda_individual: Mapped[float] = mapped_column(Float, default=0.0)
    possui_deficiencia: Mapped[bool] = mapped_column(Boolean, default=False)
    gestante: Mapped[bool] = mapped_column(Boolean, default=False)
    frequenta_escola: Mapped[bool] = mapped_column(Boolean, default=False)

    familia: Mapped["Familia"] = relationship(back_populates="membros")


class Simulacao(Base):
    __tablename__ = "simulacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    familia_id: Mapped[int | None] = mapped_column(ForeignKey("familias.id", ondelete="CASCADE"))
    # Fotografia do perfil calculado no momento da simulação: o resultado histórico
    # não muda se a família for atualizada depois.
    snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    familia: Mapped["Familia | None"] = relationship(back_populates="simulacoes")
    resultados: Mapped[list["ResultadoSimulacao"]] = relationship(
        back_populates="simulacao", cascade="all, delete-orphan"
    )


class ResultadoSimulacao(Base):
    __tablename__ = "resultados_simulacao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulacao_id: Mapped[int] = mapped_column(ForeignKey("simulacoes.id", ondelete="CASCADE"))
    programa_id: Mapped[int] = mapped_column(ForeignKey("programas.id"))
    programa_nome: Mapped[str] = mapped_column(String(160))
    elegivel: Mapped[bool] = mapped_column(Boolean, default=False)
    percentual_atendimento: Mapped[float] = mapped_column(Float, default=0.0)
    regras_atendidas: Mapped[list] = mapped_column(JSON, default=list)
    pendencias: Mapped[list] = mapped_column(JSON, default=list)

    simulacao: Mapped["Simulacao"] = relationship(back_populates="resultados")
