from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Esfera = Literal["federal", "estadual", "municipal"]
TipoValor = Literal["numero", "booleano", "texto", "lista", "intervalo", "parametro"]
Operador = Literal["==", "!=", "<", "<=", ">", ">=", "in", "entre"]


class RegraBase(BaseModel):
    codigo: str = Field(max_length=60, examples=["BF_RENDA"])
    descricao: str = Field(max_length=255, examples=["Renda familiar por pessoa dentro do limite"])
    campo: str = Field(max_length=60, examples=["renda_per_capita"])
    operador: Operador = Field(examples=["<="])
    valor: str = Field(examples=["218"])
    tipo_valor: TipoValor = "numero"
    obrigatoria: bool = True
    grupo_logico: str | None = Field(
        None, description="Regras com o mesmo grupo são avaliadas em OR entre si."
    )
    orientacao: str | None = None
    ordem: int = 0


class RegraCriar(RegraBase):
    pass


class RegraAtualizar(BaseModel):
    codigo: str | None = Field(None, max_length=60)
    descricao: str | None = Field(None, max_length=255)
    campo: str | None = Field(None, max_length=60)
    operador: Operador | None = None
    valor: str | None = None
    tipo_valor: TipoValor | None = None
    obrigatoria: bool | None = None
    grupo_logico: str | None = None
    orientacao: str | None = None
    ordem: int | None = None


class RegraResposta(RegraBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    programa_id: int


class ProgramaBase(BaseModel):
    nome: str = Field(max_length=160, examples=["Bolsa Família"])
    slug: str = Field(max_length=80, pattern=r"^[a-z0-9-]+$", examples=["bolsa-familia"])
    orgao: str | None = Field(None, examples=["Ministério do Desenvolvimento e Assistência Social"])
    esfera: Esfera = "federal"
    descricao: str | None = None
    base_legal: str | None = None
    url_oficial: str | None = None
    ativo: bool = True


class ProgramaCriar(ProgramaBase):
    regras: list[RegraCriar] = []


class ProgramaAtualizar(BaseModel):
    nome: str | None = None
    orgao: str | None = None
    esfera: Esfera | None = None
    descricao: str | None = None
    base_legal: str | None = None
    url_oficial: str | None = None
    ativo: bool | None = None


class ProgramaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    slug: str
    orgao: str | None
    esfera: Esfera
    ativo: bool


class ProgramaResposta(ProgramaResumo):
    descricao: str | None
    base_legal: str | None
    url_oficial: str | None
    criado_em: datetime
    regras: list[RegraResposta] = []


class RequisitoLegivel(BaseModel):
    codigo: str
    descricao: str
    obrigatorio: bool
    condicao: str = Field(description="Regra traduzida para leitura humana.")


class ParametroBase(BaseModel):
    valor: float = Field(gt=0, examples=[1621.0])
    descricao: str | None = None
    fonte: str | None = None
    vigencia_inicio: date | None = None


class ParametroAtualizar(ParametroBase):
    pass


class ParametroResposta(ParametroBase):
    model_config = ConfigDict(from_attributes=True)

    chave: str
    atualizado_em: datetime
