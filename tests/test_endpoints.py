"""Testes de integração: autenticação, autorização, catálogo e simulação."""


def test_health(client):
    assert client.get("/api/v1/health").json()["status"] == "ok"


def test_catalogo_e_publico_e_paginado(client):
    resposta = client.get("/api/v1/programas", params={"tamanho": 2})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 4
    assert len(corpo["itens"]) == 2
    assert corpo["total_paginas"] == 2


def test_requisitos_em_linguagem_legivel(client):
    programa_id = client.get("/api/v1/programas").json()["itens"][0]["id"]
    requisitos = client.get(f"/api/v1/programas/{programa_id}/requisitos").json()
    assert requisitos and "condicao" in requisitos[0]


def test_programa_inexistente_retorna_erro_padronizado(client):
    resposta = client.get("/api/v1/programas/9999")
    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "NAO_ENCONTRADO"


def test_criar_programa_sem_token_e_negado(client):
    resposta = client.post("/api/v1/programas", json={"nome": "X", "slug": "x"})
    assert resposta.status_code == 401


def test_assistente_nao_pode_criar_programa(client, auth_assistente):
    resposta = client.post(
        "/api/v1/programas", json={"nome": "X", "slug": "x-teste"}, headers=auth_assistente
    )
    assert resposta.status_code == 403
    assert resposta.json()["erro"]["codigo"] == "ACESSO_NEGADO"


def test_validacao_retorna_campos(client):
    resposta = client.post("/api/v1/elegibilidade/simular", json={"uf": "BAHIA"})
    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "DADOS_INVALIDOS"


# --- simulação ------------------------------------------------------------

PERFIL_VULNERAVEL = {
    "municipio": "Salvador",
    "uf": "BA",
    "renda_total_mensal": 300.0,
    "situacao_moradia": "alugada",
    "possui_cadunico": True,
    "membros": [
        {"nome": "Maria", "data_nascimento": "1990-03-12", "parentesco": "responsavel", "gestante": True},
        {"nome": "Joana", "data_nascimento": "2021-08-01", "parentesco": "filho"},
        {"nome": "Antônio", "data_nascimento": "1950-01-20", "parentesco": "pai", "possui_deficiencia": True},
    ],
}


def test_simulacao_anonima_identifica_elegibilidade(client):
    resposta = client.post("/api/v1/elegibilidade/simular", json=PERFIL_VULNERAVEL)
    assert resposta.status_code == 200
    corpo = resposta.json()

    assert corpo["perfil_calculado"]["renda_per_capita"] == 100.0
    assert corpo["resumo"]["programas_avaliados"] == 4
    assert corpo["resumo"]["elegivel_em"] >= 3

    por_nome = {r["programa_nome"]: r for r in corpo["resultados"]}
    assert por_nome["Bolsa Família"]["elegivel"] is True
    assert por_nome["Benefício de Prestação Continuada (BPC/LOAS)"]["elegivel"] is True


def test_sem_cadunico_bloqueia_e_explica_o_que_falta(client):
    payload = {**PERFIL_VULNERAVEL, "possui_cadunico": False}
    corpo = client.post("/api/v1/elegibilidade/simular", json=payload).json()

    bolsa = next(r for r in corpo["resultados"] if r["programa_nome"] == "Bolsa Família")
    assert bolsa["elegivel"] is False
    codigos = [p["codigo"] for p in bolsa["pendencias"]]
    assert "BF_CADUNICO" in codigos
    assert bolsa["percentual_atendimento"] > 0


def test_renda_alta_informa_quanto_falta(client):
    payload = {**PERFIL_VULNERAVEL, "renda_total_mensal": 900.0}
    corpo = client.post("/api/v1/elegibilidade/simular", json=payload).json()

    bolsa = next(r for r in corpo["resultados"] if r["programa_nome"] == "Bolsa Família")
    renda = next(p for p in bolsa["pendencias"] if p["codigo"] == "BF_RENDA")
    assert "acima do limite" in renda["orientacao"]


def test_elegiveis_aparecem_primeiro(client):
    resultados = client.post("/api/v1/elegibilidade/simular", json=PERFIL_VULNERAVEL).json()["resultados"]
    elegiveis = [r["elegivel"] for r in resultados]
    assert elegiveis == sorted(elegiveis, reverse=True)


# --- ciclo completo com família cadastrada --------------------------------


def test_fluxo_cadastro_simulacao_e_historico(client, auth_assistente):
    criada = client.post("/api/v1/familias", json=PERFIL_VULNERAVEL, headers=auth_assistente)
    assert criada.status_code == 201
    familia = criada.json()
    assert len(familia["identificador"]) == 24  # código opaco, sem CPF
    assert familia["perfil_calculado"]["possui_pcd"] is True

    familia_id = familia["id"]
    simulacao = client.post(f"/api/v1/familias/{familia_id}/simulacoes", headers=auth_assistente)
    assert simulacao.status_code == 201
    assert simulacao.json()["resumo"]["elegivel_em"] >= 3

    historico = client.get(f"/api/v1/familias/{familia_id}/simulacoes", headers=auth_assistente)
    assert historico.json()["total"] == 1

    detalhe = client.get(f"/api/v1/simulacoes/{simulacao.json()['simulacao_id']}", headers=auth_assistente)
    assert detalhe.status_code == 200


def test_familia_de_outro_usuario_e_bloqueada(client, auth_assistente, auth_admin):
    criada = client.post("/api/v1/familias", json=PERFIL_VULNERAVEL, headers=auth_admin).json()
    resposta = client.get(f"/api/v1/familias/{criada['id']}", headers=auth_assistente)
    assert resposta.status_code == 403


def test_atualizar_parametro_reajusta_regras(client, auth_admin):
    """Prova a tese da arquitetura: mudar um parâmetro muda o resultado, sem tocar no código."""
    payload = {**PERFIL_VULNERAVEL, "renda_total_mensal": 1260.0}  # 420 per capita (3 membros)

    antes = client.post("/api/v1/elegibilidade/simular", json=payload).json()
    bpc_antes = next(r for r in antes["resultados"] if "BPC" in r["programa_nome"])
    assert bpc_antes["elegivel"] is False  # 420 > 1/4 de 1621 (405,25)

    client.put(
        "/api/v1/parametros/salario_minimo",
        json={"valor": 2000.0, "descricao": "Reajuste simulado"},
        headers=auth_admin,
    )

    depois = client.post("/api/v1/elegibilidade/simular", json=payload).json()
    bpc_depois = next(r for r in depois["resultados"] if "BPC" in r["programa_nome"])
    assert bpc_depois["elegivel"] is True  # 420 < 1/4 de 2000 (500)

    client.put(
        "/api/v1/parametros/salario_minimo",
        json={"valor": 1621.0, "descricao": "Restaurado"},
        headers=auth_admin,
    )


def test_relatorio_cobertura_exige_admin(client, auth_assistente, auth_admin):
    assert client.get("/api/v1/relatorios/cobertura", headers=auth_assistente).status_code == 403

    relatorio = client.get("/api/v1/relatorios/cobertura", headers=auth_admin).json()
    assert relatorio["total_familias"] >= 1
    assert len(relatorio["cobertura_por_programa"]) == 4


def test_relatorio_pendencias(client, auth_admin):
    corpo = client.get("/api/v1/relatorios/pendencias-frequentes", headers=auth_admin).json()
    assert "pendencias" in corpo
