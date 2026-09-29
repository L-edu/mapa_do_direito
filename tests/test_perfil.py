"""Testes dos campos derivados do perfil socioeconômico."""

from datetime import date
from types import SimpleNamespace

from app.services.perfil import calcular_idade, montar_perfil

REFERENCIA = date(2026, 9, 19)


def membro(nascimento, **kwargs):
    base = {
        "data_nascimento": nascimento,
        "gestante": False,
        "possui_deficiencia": False,
        "frequenta_escola": True,
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def familia(membros, **kwargs):
    base = {
        "municipio": "Salvador",
        "uf": "BA",
        "renda_total_mensal": 900.0,
        "situacao_moradia": "alugada",
        "possui_cadunico": True,
        "membros": membros,
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_idade_no_dia_anterior_ao_aniversario():
    assert calcular_idade(date(1961, 9, 20), REFERENCIA) == 64


def test_idade_no_dia_do_aniversario():
    assert calcular_idade(date(1961, 9, 19), REFERENCIA) == 65


def test_renda_per_capita():
    f = familia([membro(date(1990, 1, 1)), membro(date(2015, 1, 1)), membro(date(2020, 1, 1))])
    assert montar_perfil(f, REFERENCIA)["renda_per_capita"] == 300.0


def test_familia_unipessoal():
    f = familia([membro(date(1990, 1, 1))], renda_total_mensal=1000.0)
    perfil = montar_perfil(f, REFERENCIA)
    assert perfil["num_membros"] == 1
    assert perfil["renda_per_capita"] == 1000.0


def test_familia_sem_membros_nao_divide_por_zero():
    f = familia([], renda_total_mensal=500.0)
    perfil = montar_perfil(f, REFERENCIA)
    assert perfil["num_membros"] == 0
    assert perfil["renda_per_capita"] == 500.0
    assert perfil["idade_minima"] is None


def test_renda_zero():
    f = familia([membro(date(1990, 1, 1))], renda_total_mensal=0.0)
    assert montar_perfil(f, REFERENCIA)["renda_per_capita"] == 0.0


def test_flags_de_composicao():
    f = familia(
        [
            membro(date(1990, 3, 12), gestante=True, frequenta_escola=False),
            membro(date(2021, 8, 1), frequenta_escola=False),
            membro(date(1955, 1, 20), possui_deficiencia=True, frequenta_escola=False),
        ]
    )
    perfil = montar_perfil(f, REFERENCIA)
    assert perfil["possui_crianca_0_6"] is True
    assert perfil["possui_gestante"] is True
    assert perfil["possui_pcd"] is True
    assert perfil["possui_idoso_65"] is True  # nascido em 1955 -> 71 anos
    assert perfil["possui_publico_prioritario"] is True


def test_crianca_fora_da_escola():
    f = familia([membro(date(2015, 5, 1), frequenta_escola=False)])
    assert montar_perfil(f, REFERENCIA)["possui_crianca_fora_escola"] is True

    g = familia([membro(date(2015, 5, 1), frequenta_escola=True)])
    assert montar_perfil(g, REFERENCIA)["possui_crianca_fora_escola"] is False


def test_situacao_de_rua():
    f = familia([membro(date(1990, 1, 1))], situacao_moradia="situacao_rua")
    assert montar_perfil(f, REFERENCIA)["situacao_rua"] is True
