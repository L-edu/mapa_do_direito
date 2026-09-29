"""Popula o banco com parâmetros, programas, regras e dados de demonstração.

    python -m app.seed

Valores conferidos em 22/09/2026 nas fontes oficiais (salário mínimo: Decreto
nº 12.797/2025; linha de pobreza do Bolsa Família: Lei 14.601/2023). Como as
regras são dados, um reajuste futuro é só atualizar o registro em `parametros`
— nenhum código muda. Vale reconferir antes de qualquer apresentação futura,
já que o salário mínimo é reajustado todo mês de janeiro.
"""

from datetime import date

from sqlalchemy import select

from app.core.seguranca import gerar_hash_senha, gerar_identificador
from app.database import Base, SessionLocal, engine
from app.models import Familia, Membro, Parametro, Programa, Regra, Usuario

PARAMETROS = [
    {
        "chave": "salario_minimo",
        "valor": 1621.00,
        "descricao": "Salário mínimo nacional vigente",
        "fonte": "Decreto nº 12.797/2025 — vigente desde 1º/jan/2026",
        "vigencia_inicio": date(2026, 1, 1),
    },
    {
        "chave": "limite_renda_bolsa_familia",
        "valor": 218.00,
        "descricao": "Renda mensal por pessoa que define a linha de pobreza do Bolsa Família",
        "fonte": "Lei 14.601/2023 — confirmado vigente em 2026",
        "vigencia_inicio": date(2023, 6, 1),
    },
]

PROGRAMAS = [
    {
        "nome": "Bolsa Família",
        "slug": "bolsa-familia",
        "orgao": "Ministério do Desenvolvimento e Assistência Social",
        "esfera": "federal",
        "descricao": "Transferência de renda para famílias em situação de pobreza.",
        "base_legal": "Lei nº 14.601/2023",
        "url_oficial": "https://www.gov.br/mds/pt-br/acoes-e-programas/bolsa-familia",
        "regras": [
            {
                "codigo": "BF_CADUNICO",
                "descricao": "Estar com o Cadastro Único atualizado",
                "campo": "possui_cadunico",
                "operador": "==",
                "valor": "true",
                "tipo_valor": "booleano",
                "orientacao": "Procure o CRAS mais próximo para fazer ou atualizar o CadÚnico.",
                "ordem": 1,
            },
            {
                "codigo": "BF_RENDA",
                "descricao": "Renda mensal por pessoa dentro da linha de pobreza",
                "campo": "renda_per_capita",
                "operador": "<=",
                "valor": "limite_renda_bolsa_familia",
                "tipo_valor": "parametro",
                "ordem": 2,
            },
            {
                "codigo": "BF_COMPOSICAO",
                "descricao": "Ter criança, adolescente ou gestante na família",
                "campo": "possui_publico_prioritario",
                "operador": "==",
                "valor": "true",
                "tipo_valor": "booleano",
                "obrigatoria": False,
                "ordem": 3,
            },
        ],
    },
    {
        "nome": "Benefício de Prestação Continuada (BPC/LOAS)",
        "slug": "bpc-loas",
        "orgao": "INSS / Ministério do Desenvolvimento e Assistência Social",
        "esfera": "federal",
        "descricao": "Um salário mínimo mensal a idosos de 65 anos ou mais e a pessoas com "
        "deficiência em situação de vulnerabilidade.",
        "base_legal": "Lei nº 8.742/1993 (LOAS), art. 20",
        "url_oficial": "https://www.gov.br/inss/pt-br/saiba-mais/auxilios-e-beneficios/bpc",
        "regras": [
            {
                "codigo": "BPC_RENDA",
                "descricao": "Renda por pessoa inferior a 1/4 do salário mínimo",
                "campo": "renda_per_capita",
                "operador": "<",
                "valor": "0.25 * salario_minimo",
                "tipo_valor": "parametro",
                "ordem": 1,
            },
            {
                "codigo": "BPC_IDOSO",
                "descricao": "Ter pessoa com 65 anos ou mais na família",
                "campo": "possui_idoso_65",
                "operador": "==",
                "valor": "true",
                "tipo_valor": "booleano",
                "grupo_logico": "publico_alvo",
                "ordem": 2,
            },
            {
                "codigo": "BPC_PCD",
                "descricao": "Ter pessoa com deficiência na família",
                "campo": "possui_pcd",
                "operador": "==",
                "valor": "true",
                "tipo_valor": "booleano",
                "grupo_logico": "publico_alvo",
                "ordem": 3,
            },
            {
                "codigo": "BPC_CADUNICO",
                "descricao": "Estar inscrito no Cadastro Único",
                "campo": "possui_cadunico",
                "operador": "==",
                "valor": "true",
                "tipo_valor": "booleano",
                "ordem": 4,
            },
        ],
    },
    {
        "nome": "Tarifa Social de Energia Elétrica",
        "slug": "tarifa-social-energia",
        "orgao": "ANEEL / distribuidoras de energia",
        "esfera": "federal",
        "descricao": "Desconto na conta de luz para famílias de baixa renda.",
        "base_legal": "Lei nº 12.212/2010",
        "url_oficial": "https://www.gov.br/aneel",
        "regras": [
            {
                "codigo": "TS_CADUNICO",
                "descricao": "Estar inscrito no Cadastro Único",
                "campo": "possui_cadunico",
                "operador": "==",
                "valor": "true",
                "tipo_valor": "booleano",
                "ordem": 1,
            },
            {
                "codigo": "TS_RENDA",
                "descricao": "Renda por pessoa de até meio salário mínimo",
                "campo": "renda_per_capita",
                "operador": "<=",
                "valor": "0.5 * salario_minimo",
                "tipo_valor": "parametro",
                "ordem": 2,
            },
        ],
    },
    {
        "nome": "ID Jovem",
        "slug": "id-jovem",
        "orgao": "Ministério do Esporte",
        "esfera": "federal",
        "descricao": "Meia-entrada e vagas gratuitas em transporte interestadual para jovens "
        "de baixa renda.",
        "base_legal": "Lei nº 12.852/2013 (Estatuto da Juventude)",
        "url_oficial": "https://www.gov.br/pt-br/servicos/obter-a-identidade-jovem",
        "regras": [
            {
                "codigo": "IDJ_CADUNICO",
                "descricao": "Estar inscrito no Cadastro Único",
                "campo": "possui_cadunico",
                "operador": "==",
                "valor": "true",
                "tipo_valor": "booleano",
                "ordem": 1,
            },
            {
                "codigo": "IDJ_IDADE",
                "descricao": "Ter pessoa entre 15 e 29 anos na família",
                "campo": "possui_jovem_15_29",
                "operador": "==",
                "valor": "true",
                "tipo_valor": "booleano",
                "ordem": 2,
            },
            {
                "codigo": "IDJ_RENDA",
                "descricao": "Renda por pessoa de até dois salários mínimos",
                "campo": "renda_per_capita",
                "operador": "<=",
                "valor": "2 * salario_minimo",
                "tipo_valor": "parametro",
                "ordem": 3,
            },
        ],
    },
]

USUARIOS = [
    {"nome": "Administrador", "email": "admin@mapadodireito.org", "senha": "admin12345", "papel": "admin"},
    {
        "nome": "Assistente Social CRAS",
        "email": "cras@mapadodireito.org",
        "senha": "cras12345",
        "papel": "assistente_social",
    },
]


def popular() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for dados in PARAMETROS:
            if not db.get(Parametro, dados["chave"]):
                db.add(Parametro(**dados))

        for dados in USUARIOS:
            if not db.scalar(select(Usuario).where(Usuario.email == dados["email"])):
                db.add(
                    Usuario(
                        nome=dados["nome"],
                        email=dados["email"],
                        senha_hash=gerar_hash_senha(dados["senha"]),
                        papel=dados["papel"],
                    )
                )

        for dados in PROGRAMAS:
            if db.scalar(select(Programa).where(Programa.slug == dados["slug"])):
                continue
            regras = dados.pop("regras")
            programa = Programa(**dados)
            programa.regras = [Regra(**r) for r in regras]
            db.add(programa)

        db.commit()

        # Família de demonstração, vinculada à assistente social.
        assistente = db.scalar(select(Usuario).where(Usuario.papel == "assistente_social"))
        if assistente and not db.scalar(select(Familia)):
            familia = Familia(
                identificador=gerar_identificador("demo-001"),
                municipio="Salvador",
                uf="BA",
                renda_total_mensal=800.0,
                situacao_moradia="alugada",
                possui_cadunico=True,
                criado_por_id=assistente.id,
            )
            familia.membros = [
                Membro(nome="Maria", data_nascimento=date(1990, 3, 12), parentesco="responsavel", gestante=True),
                Membro(nome="Joana", data_nascimento=date(2019, 8, 1), parentesco="filho"),
                Membro(
                    nome="Antônio",
                    data_nascimento=date(1955, 1, 20),
                    parentesco="pai",
                    possui_deficiencia=True,
                ),
            ]
            db.add(familia)
            db.commit()

        print("Seed concluído.")
        print("  admin@mapadodireito.org / admin12345")
        print("  cras@mapadodireito.org  / cras12345")
    finally:
        db.close()


if __name__ == "__main__":
    popular()
