"""Testes dos ajustes de back-end da Sprint 2: papéis, usuários e edição de regras.

Obs.: este arquivo roda depois de test_endpoints.py (ordem alfabética), que conta
os programas do seed; por isso o programa criado aqui só nasce no último teste.
"""

FAMILIA = {
    "municipio": "Salvador",
    "uf": "ba",
    "renda_total_mensal": 500.0,
    "situacao_moradia": "alugada",
    "possui_cadunico": True,
    "membros": [{"nome": "Ana", "data_nascimento": "1990-01-01", "parentesco": "responsavel"}],
}


def test_registro_publico_sempre_cria_cidadao(client):
    resposta = client.post(
        "/api/v1/auth/registrar",
        json={"nome": "Fulano", "email": "fulano@exemplo.org", "senha": "senhaSegura1", "papel": "admin"},
    )
    assert resposta.status_code == 201
    assert resposta.json()["papel"] == "cidadao"


def test_cidadao_cadastra_lista_e_exclui_a_propria_familia(client, auth_cidadao):
    criada = client.post("/api/v1/familias", json=FAMILIA, headers=auth_cidadao)
    assert criada.status_code == 201
    familia_id = criada.json()["id"]

    lista = client.get("/api/v1/familias", headers=auth_cidadao).json()
    assert familia_id in [f["id"] for f in lista["itens"]]

    assert client.delete(f"/api/v1/familias/{familia_id}", headers=auth_cidadao).status_code == 204
    assert client.get(f"/api/v1/familias/{familia_id}", headers=auth_cidadao).status_code == 404


def test_cidadao_nao_acessa_familia_de_outro_usuario(client, auth_cidadao, auth_assistente):
    familia = client.post("/api/v1/familias", json=FAMILIA, headers=auth_assistente).json()
    assert client.get(f"/api/v1/familias/{familia['id']}", headers=auth_cidadao).status_code == 403
    assert client.delete(f"/api/v1/familias/{familia['id']}", headers=auth_cidadao).status_code == 403


def test_usuarios_exige_admin(client, auth_assistente):
    assert client.get("/api/v1/usuarios").status_code == 401
    assert client.get("/api/v1/usuarios", headers=auth_assistente).status_code == 403


def test_admin_lista_cria_e_atualiza_usuarios(client, auth_admin):
    lista = client.get("/api/v1/usuarios", headers=auth_admin, params={"busca": "mapadodireito"}).json()
    assert lista["total"] >= 3

    novo = client.post(
        "/api/v1/usuarios",
        json={"nome": "Nova Assistente", "email": "nova@exemplo.org", "senha": "senhaSegura1", "papel": "assistente_social"},
        headers=auth_admin,
    )
    assert novo.status_code == 201
    assert novo.json()["papel"] == "assistente_social"

    duplicado = client.post(
        "/api/v1/usuarios",
        json={"nome": "Outra", "email": "nova@exemplo.org", "senha": "senhaSegura1", "papel": "cidadao"},
        headers=auth_admin,
    )
    assert duplicado.status_code == 409

    alterado = client.patch(
        f"/api/v1/usuarios/{novo.json()['id']}", json={"papel": "cidadao", "ativo": False}, headers=auth_admin
    )
    assert alterado.status_code == 200
    assert alterado.json()["papel"] == "cidadao"
    assert alterado.json()["ativo"] is False


def test_conta_desativada_nao_consegue_logar(client):
    resposta = client.post("/api/v1/auth/login", json={"email": "nova@exemplo.org", "senha": "senhaSegura1"})
    assert resposta.status_code == 401


def test_admin_nao_pode_rebaixar_a_propria_conta(client, auth_admin):
    eu = client.get("/api/v1/auth/me", headers=auth_admin).json()
    resposta = client.patch(f"/api/v1/usuarios/{eu['id']}", json={"papel": "cidadao"}, headers=auth_admin)
    assert resposta.status_code == 400
    resposta = client.patch(f"/api/v1/usuarios/{eu['id']}", json={"ativo": False}, headers=auth_admin)
    assert resposta.status_code == 400


def test_admin_edita_regra_de_programa(client, auth_admin):
    programa = client.post(
        "/api/v1/programas",
        json={"nome": "Programa de Teste", "slug": "programa-teste-sprint2"},
        headers=auth_admin,
    ).json()
    regra = client.post(
        f"/api/v1/programas/{programa['id']}/regras",
        json={"codigo": "T1", "descricao": "Renda baixa", "campo": "renda_per_capita", "operador": "<=", "valor": "100"},
        headers=auth_admin,
    ).json()

    atualizada = client.put(f"/api/v1/regras/{regra['id']}", json={"valor": "250", "obrigatoria": False}, headers=auth_admin)
    assert atualizada.status_code == 200
    assert atualizada.json()["valor"] == "250"
    assert atualizada.json()["obrigatoria"] is False
    assert atualizada.json()["codigo"] == "T1"  # campos não enviados permanecem

    assert client.put("/api/v1/regras/99999", json={"valor": "1"}, headers=auth_admin).status_code == 404
