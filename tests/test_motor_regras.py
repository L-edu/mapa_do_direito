"""Testes do motor de regras — o núcleo da regra de negócio, testado sem banco nem HTTP."""

from types import SimpleNamespace

import pytest

from app.core.motor_regras import (
    RegraInvalidaError,
    avaliar_programa,
    avaliar_regra,
    resolver_valor,
)

PARAMETROS = {"salario_minimo": 1518.0, "limite_renda_bolsa_familia": 218.0}


def regra(**kwargs):
    base = {
        "codigo": "R1",
        "descricao": "Regra de teste",
        "campo": "renda_per_capita",
        "operador": "<=",
        "valor": "218",
        "tipo_valor": "numero",
        "obrigatoria": True,
        "grupo_logico": None,
        "orientacao": None,
        "ordem": 1,
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def programa(regras, nome="Programa Teste"):
    return SimpleNamespace(id=1, nome=nome, regras=regras)


# --- resolução de valores -------------------------------------------------


def test_resolve_numero():
    assert resolver_valor(regra(valor="218", tipo_valor="numero"), PARAMETROS) == 218.0


def test_resolve_booleano():
    assert resolver_valor(regra(valor="true", tipo_valor="booleano"), PARAMETROS) is True
    assert resolver_valor(regra(valor="false", tipo_valor="booleano"), PARAMETROS) is False


def test_resolve_parametro_com_fator():
    valor = resolver_valor(regra(valor="0.25 * salario_minimo", tipo_valor="parametro"), PARAMETROS)
    assert valor == pytest.approx(379.5)


def test_resolve_parametro_sem_fator():
    valor = resolver_valor(
        regra(valor="limite_renda_bolsa_familia", tipo_valor="parametro"), PARAMETROS
    )
    assert valor == 218.0


def test_parametro_inexistente_levanta_erro():
    with pytest.raises(RegraInvalidaError):
        resolver_valor(regra(valor="parametro_fantasma", tipo_valor="parametro"), PARAMETROS)


def test_operador_desconhecido_levanta_erro():
    with pytest.raises(RegraInvalidaError):
        avaliar_regra(regra(operador="~="), {"renda_per_capita": 100}, PARAMETROS)


# --- casos de borda da avaliação -----------------------------------------


def test_renda_exatamente_no_limite_e_atendida():
    """<= 218 com renda 218: o limite é inclusivo e deve passar."""
    resultado = avaliar_regra(regra(), {"renda_per_capita": 218.0}, PARAMETROS)
    assert resultado.atendida is True


def test_um_centavo_acima_do_limite_reprova():
    resultado = avaliar_regra(regra(), {"renda_per_capita": 218.01}, PARAMETROS)
    assert resultado.atendida is False
    assert "acima do limite" in resultado.orientacao


def test_campo_ausente_no_perfil_nao_atende():
    """Dado faltando nunca pode ser interpretado como requisito cumprido."""
    resultado = avaliar_regra(regra(), {}, PARAMETROS)
    assert resultado.atendida is False


def test_intervalo():
    r = regra(campo="idade_maxima", operador="entre", valor="15,29", tipo_valor="intervalo")
    assert avaliar_regra(r, {"idade_maxima": 20}, PARAMETROS).atendida is True
    assert avaliar_regra(r, {"idade_maxima": 30}, PARAMETROS).atendida is False


# --- combinação de regras -------------------------------------------------


def test_todas_obrigatorias_atendidas_torna_elegivel():
    p = programa(
        [
            regra(codigo="A", campo="possui_cadunico", operador="==", valor="true", tipo_valor="booleano"),
            regra(codigo="B"),
        ]
    )
    resultado = avaliar_programa(p, {"possui_cadunico": True, "renda_per_capita": 100}, PARAMETROS)
    assert resultado.elegivel is True
    assert resultado.percentual_atendimento == 100.0


def test_uma_obrigatoria_pendente_bloqueia():
    p = programa(
        [
            regra(codigo="A", campo="possui_cadunico", operador="==", valor="true", tipo_valor="booleano"),
            regra(codigo="B"),
        ]
    )
    resultado = avaliar_programa(p, {"possui_cadunico": False, "renda_per_capita": 100}, PARAMETROS)
    assert resultado.elegivel is False
    assert [pend.codigo for pend in resultado.pendencias] == ["A"]
    assert resultado.percentual_atendimento == 50.0


def test_regra_nao_obrigatoria_nao_bloqueia():
    p = programa([regra(codigo="A"), regra(codigo="B", campo="possui_gestante", operador="==", valor="true", tipo_valor="booleano", obrigatoria=False)])
    resultado = avaliar_programa(p, {"renda_per_capita": 100, "possui_gestante": False}, PARAMETROS)
    assert resultado.elegivel is True
    assert len(resultado.pendencias) == 1


def test_grupo_logico_funciona_como_ou():
    """BPC: idoso 65+ OU pessoa com deficiência. Uma das duas basta."""
    p = programa(
        [
            regra(codigo="IDOSO", campo="possui_idoso_65", operador="==", valor="true", tipo_valor="booleano", grupo_logico="publico"),
            regra(codigo="PCD", campo="possui_pcd", operador="==", valor="true", tipo_valor="booleano", grupo_logico="publico"),
        ]
    )
    so_pcd = avaliar_programa(p, {"possui_idoso_65": False, "possui_pcd": True}, PARAMETROS)
    assert so_pcd.elegivel is True

    nenhum = avaliar_programa(p, {"possui_idoso_65": False, "possui_pcd": False}, PARAMETROS)
    assert nenhum.elegivel is False


def test_programa_sem_regras_nao_quebra():
    resultado = avaliar_programa(programa([]), {}, PARAMETROS)
    assert resultado.elegivel is True
    assert resultado.percentual_atendimento == 0.0
