from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SituacaoMoradia = Literal["propria", "alugada", "cedida", "situacao_rua"]
Parentesco = Literal["responsavel", "conjuge", "filho", "pai", "mae", "outro"]


class MembroBase(BaseModel):
    nome: str = Field(
        max_length=80,
        description="Apenas o primeiro nome. Não informe CPF, NIS ou outro identificador.",
        examples=["Maria"],
    )
    data_nascimento: date = Field(examples=["1990-03-12"])
    parentesco: Parentesco = "outro"
    escolaridade: str | None = None
    renda_individual: float = Field(0, ge=0)
    possui_deficiencia: bool = False
    gestante: bool = False
    frequenta_escola: bool = False

    @field_validator("data_nascimento")
    @classmethod
    def nao_pode_ser_futura(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("A data de nascimento não pode estar no futuro.")
        return v


class MembroCriar(MembroBase):
    pass


class MembroAtualizar(BaseModel):
    nome: str | None = None
    data_nascimento: date | None = None
    parentesco: Parentesco | None = None
    escolaridade: str | None = None
    renda_individual: float | None = Field(None, ge=0)
    possui_deficiencia: bool | None = None
    gestante: bool | None = None
    frequenta_escola: bool | None = None


class MembroResposta(MembroBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    familia_id: int
    idade: int | None = None


class FamiliaBase(BaseModel):
    municipio: str = Field(max_length=120, examples=["Salvador"])
    uf: str = Field(min_length=2, max_length=2, examples=["BA"])
    renda_total_mensal: float = Field(0, ge=0, examples=[800.0])
    situacao_moradia: SituacaoMoradia = "alugada"
    possui_cadunico: bool = False

    @field_validator("uf")
    @classmethod
    def uf_maiuscula(cls, v: str) -> str:
        return v.upper()


class FamiliaCriar(FamiliaBase):
    membros: list[MembroCriar] = []


class FamiliaAtualizar(BaseModel):
    municipio: str | None = None
    uf: str | None = Field(None, min_length=2, max_length=2)
    renda_total_mensal: float | None = Field(None, ge=0)
    situacao_moradia: SituacaoMoradia | None = None
    possui_cadunico: bool | None = None


class FamiliaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    identificador: str
    municipio: str
    uf: str
    renda_total_mensal: float
    possui_cadunico: bool
    criado_em: datetime


class FamiliaResposta(FamiliaResumo):
    situacao_moradia: SituacaoMoradia
    atualizado_em: datetime
    membros: list[MembroResposta] = []
    perfil_calculado: dict = {}


# --- Elegibilidade -------------------------------------------------------------


class SimulacaoAnonima(FamiliaBase):
    """Payload da simulação pública: nada é gravado no banco."""

    membros: list[MembroCriar] = Field(min_length=1)


class AvaliacaoRegraResposta(BaseModel):
    codigo: str
    descricao: str
    atendida: bool
    valor_informado: object | None = None
    valor_exigido: object | None = None
    orientacao: str | None = None


class ResultadoProgramaResposta(BaseModel):
    programa_id: int
    programa_nome: str
    elegivel: bool
    percentual_atendimento: float
    regras_atendidas: list[AvaliacaoRegraResposta] = []
    pendencias: list[AvaliacaoRegraResposta] = []


class ResumoSimulacao(BaseModel):
    programas_avaliados: int
    elegivel_em: int
    quase_elegivel_em: int = Field(
        description="Programas inelegíveis com 70% ou mais dos requisitos atendidos."
    )


class SimulacaoResposta(BaseModel):
    simulacao_id: int | None = None
    familia_id: int | None = None
    criado_em: datetime | None = None
    perfil_calculado: dict
    resumo: ResumoSimulacao
    resultados: list[ResultadoProgramaResposta]


class SimulacaoResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    familia_id: int | None
    criado_em: datetime
    total_elegiveis: int = 0
