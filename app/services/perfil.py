"""Transforma uma família (ORM ou payload avulso) no perfil computado que o motor avalia.

As regras nunca olham os campos crus: elas olham atributos derivados como
renda_per_capita, possui_idoso_65 ou possui_crianca_fora_escola. Concentrar esse
cálculo aqui mantém o motor genérico e a regra de negócio em um único lugar.
"""

from datetime import date


def calcular_idade(nascimento: date, referencia: date | None = None) -> int:
    hoje = referencia or date.today()
    idade = hoje.year - nascimento.year
    if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
        idade -= 1
    return idade


def montar_perfil(familia, referencia: date | None = None) -> dict:
    """Recebe qualquer objeto com os atributos de família e uma coleção `membros`."""
    membros = list(getattr(familia, "membros", []) or [])
    num_membros = len(membros)
    renda_total = float(getattr(familia, "renda_total_mensal", 0.0) or 0.0)
    idades = [calcular_idade(m.data_nascimento, referencia) for m in membros]

    perfil = {
        "municipio": getattr(familia, "municipio", None),
        "uf": getattr(familia, "uf", None),
        "num_membros": num_membros,
        "renda_total_mensal": renda_total,
        # Família sem membros cadastrados: a renda per capita é a própria renda total,
        # evitando divisão por zero e evitando "aprovar" um cadastro incompleto.
        "renda_per_capita": round(renda_total / num_membros, 2) if num_membros else renda_total,
        "situacao_moradia": getattr(familia, "situacao_moradia", None),
        "situacao_rua": getattr(familia, "situacao_moradia", None) == "situacao_rua",
        "possui_cadunico": bool(getattr(familia, "possui_cadunico", False)),
        "idade_minima": min(idades) if idades else None,
        "idade_maxima": max(idades) if idades else None,
        "possui_crianca_0_6": any(i <= 6 for i in idades),
        "possui_adolescente_7_17": any(7 <= i <= 17 for i in idades),
        "possui_jovem_15_29": any(15 <= i <= 29 for i in idades),
        "possui_idoso_65": any(i >= 65 for i in idades),
        "possui_gestante": any(bool(m.gestante) for m in membros),
        "possui_pcd": any(bool(m.possui_deficiencia) for m in membros),
        "possui_crianca_fora_escola": any(
            4 <= calcular_idade(m.data_nascimento, referencia) <= 17 and not m.frequenta_escola
            for m in membros
        ),
    }
    # Composição típica exigida pelo Bolsa Família.
    perfil["possui_publico_prioritario"] = (
        perfil["possui_crianca_0_6"]
        or perfil["possui_adolescente_7_17"]
        or perfil["possui_gestante"]
    )
    return perfil
