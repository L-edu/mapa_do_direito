"""Motor de avaliação de elegibilidade.

Módulo puro: não conhece FastAPI nem banco de dados. Recebe objetos com os atributos
de uma regra, um dicionário de perfil e um dicionário de parâmetros, e devolve o
resultado. Isso o torna trivialmente testável de forma isolada.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Callable

OPERADORES: dict[str, Callable[[Any, Any], bool]] = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "in": lambda a, b: a in b,
    "entre": lambda a, b: b[0] <= a <= b[1],
}


class RegraInvalidaError(ValueError):
    """Regra mal cadastrada (operador desconhecido, valor impossível de converter)."""


@dataclass
class AvaliacaoRegra:
    codigo: str
    descricao: str
    atendida: bool
    valor_informado: Any = None
    valor_exigido: Any = None
    orientacao: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ResultadoPrograma:
    programa_id: int
    programa_nome: str
    elegivel: bool
    percentual_atendimento: float
    regras_atendidas: list[AvaliacaoRegra] = field(default_factory=list)
    pendencias: list[AvaliacaoRegra] = field(default_factory=list)


def resolver_valor(regra, parametros: dict[str, float]) -> Any:
    """Converte o valor textual da regra para o tipo correto.

    tipo_valor='parametro' aceita expressões como "0.25 * salario_minimo", de modo que
    reajustar o salário mínimo em um único registro atualiza todas as regras derivadas.
    """
    bruto = str(regra.valor).strip()
    tipo = regra.tipo_valor

    if tipo == "numero":
        return float(bruto)
    if tipo == "booleano":
        return bruto.lower() in ("true", "1", "sim", "verdadeiro")
    if tipo == "lista":
        return [item.strip() for item in bruto.split(",")]
    if tipo == "intervalo":
        partes = [float(p.strip()) for p in bruto.split(",")]
        if len(partes) != 2:
            raise RegraInvalidaError(f"Intervalo inválido na regra {regra.codigo}: {bruto}")
        return partes
    if tipo == "parametro":
        if "*" in bruto:
            fator, _, chave = bruto.partition("*")
            fator, chave = fator.strip(), chave.strip()
        else:
            fator, chave = "1", bruto
        if chave not in parametros:
            raise RegraInvalidaError(f"Parâmetro '{chave}' não cadastrado (regra {regra.codigo}).")
        return float(fator) * float(parametros[chave])
    return bruto


def avaliar_regra(regra, perfil: dict, parametros: dict[str, float]) -> AvaliacaoRegra:
    if regra.operador not in OPERADORES:
        raise RegraInvalidaError(f"Operador '{regra.operador}' desconhecido ({regra.codigo}).")

    valor_informado = perfil.get(regra.campo)
    valor_exigido = resolver_valor(regra, parametros)

    try:
        atendida = bool(OPERADORES[regra.operador](valor_informado, valor_exigido))
    except TypeError:
        # Dado ausente ou de tipo incompatível: por segurança, a regra não é atendida.
        atendida = False

    return AvaliacaoRegra(
        codigo=regra.codigo,
        descricao=regra.descricao,
        atendida=atendida,
        valor_informado=valor_informado,
        valor_exigido=valor_exigido,
        orientacao=None if atendida else _montar_orientacao(regra, valor_informado, valor_exigido),
    )


def _montar_orientacao(regra, informado: Any, exigido: Any) -> str:
    """Mensagem em linguagem simples explicando o que falta para atender a regra."""
    if regra.orientacao:
        return regra.orientacao
    if isinstance(informado, (int, float)) and isinstance(exigido, (int, float)):
        diferenca = abs(float(informado) - float(exigido))
        if regra.operador in ("<", "<="):
            return f"O valor informado está {diferenca:.2f} acima do limite de {exigido:.2f}."
        if regra.operador in (">", ">="):
            return f"Faltam {diferenca:.2f} para atingir o mínimo de {exigido:.2f}."
    return "Essa condição ainda não é atendida pela família."


def avaliar_programa(programa, perfil: dict, parametros: dict[str, float]) -> ResultadoPrograma:
    """Avalia um programa inteiro.

    Regras sem grupo_logico são combinadas em AND (quando obrigatórias).
    Regras que compartilham um grupo_logico são combinadas em OR entre si: basta uma
    delas ser atendida para o grupo ser considerado satisfeito. É assim que o BPC
    representa "ser idoso de 65 anos ou mais OU ser pessoa com deficiência".
    """
    atendidas: list[AvaliacaoRegra] = []
    pendencias: list[AvaliacaoRegra] = []
    grupos: dict[str, bool] = {}
    bloqueios = 0

    for regra in programa.regras:
        avaliacao = avaliar_regra(regra, perfil, parametros)
        (atendidas if avaliacao.atendida else pendencias).append(avaliacao)

        if regra.grupo_logico:
            grupos[regra.grupo_logico] = grupos.get(regra.grupo_logico, False) or avaliacao.atendida
        elif regra.obrigatoria and not avaliacao.atendida:
            bloqueios += 1

    bloqueios += sum(1 for satisfeito in grupos.values() if not satisfeito)

    total = len(programa.regras) or 1
    return ResultadoPrograma(
        programa_id=programa.id,
        programa_nome=programa.nome,
        elegivel=bloqueios == 0,
        percentual_atendimento=round(len(atendidas) / total * 100, 1),
        regras_atendidas=atendidas,
        pendencias=pendencias,
    )


def avaliar_programas(programas, perfil: dict, parametros: dict) -> list[ResultadoPrograma]:
    resultados = [avaliar_programa(p, perfil, parametros) for p in programas]
    # Elegíveis primeiro; entre os inelegíveis, os mais próximos de se enquadrar.
    resultados.sort(key=lambda r: (not r.elegivel, -r.percentual_atendimento))
    return resultados
