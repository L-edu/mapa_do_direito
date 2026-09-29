# Mapa do Direito

API de identificação de elegibilidade a programas sociais.
**ODS 1 — Erradicação da Pobreza** · meta 1.3

---

## O problema

Parte significativa das famílias em situação de vulnerabilidade **não acessa benefícios aos quais já teria direito**. As causas mais comuns não são de renda, e sim informacionais: desconhecimento dos critérios, cadastro desatualizado, ou uma negativa anterior sem qualquer orientação sobre o motivo.

O resultado é duplo: a família permanece desprotegida, e o poder público perde capacidade de focalizar a busca ativa.

## A solução

Uma API que recebe o perfil socioeconômico de uma família e responde, para cada programa disponível:

1. **se a família é elegível**;
2. **quais requisitos já são atendidos**;
3. quando não é elegível, **exatamente o que falta e quanto falta** — em linguagem simples.

Essa terceira resposta é o diferencial. Um "não" sozinho não muda a vida de ninguém; *"a renda por pessoa está R$ 48,67 acima do limite"* ou *"basta atualizar o CadÚnico no CRAS"* muda.

## Decisão de arquitetura: regras como dados

As regras de elegibilidade **não estão codificadas em `if/else`**. Elas vivem no banco como registros declarativos:

| campo | operador | valor | tipo_valor |
|---|---|---|---|
| `renda_per_capita` | `<=` | `limite_renda_bolsa_familia` | `parametro` |
| `possui_cadunico` | `==` | `true` | `booleano` |
| `renda_per_capita` | `<` | `0.25 * salario_minimo` | `parametro` |

Consequências práticas:

- **Cadastrar um programa novo** é uma chamada `POST /programas` — não um deploy.
- **Reajustar o salário mínimo** é atualizar um único registro em `parametros`; todas as regras derivadas se ajustam sozinhas. Há um teste automatizado que prova isso (`test_atualizar_parametro_reajusta_regras`).
- O motor de avaliação fica pequeno, puro e inteiramente testável sem banco nem HTTP.

Regras que compartilham um `grupo_logico` são combinadas em **OR** entre si — é assim que o BPC representa *"ser idoso de 65 anos ou mais **ou** ser pessoa com deficiência"*.

## Privacidade (LGPD)

A API **não recebe nem armazena CPF, NIS, RG ou qualquer identificador direto**. Cada família recebe um código interno opaco derivado de um UUID com salt. Dos membros, guarda-se apenas o primeiro nome e os atributos estritamente necessários para avaliar o direito ao benefício. Trata-se de dado de população vulnerável: coletar menos é um requisito, não um detalhe.

## Stack

FastAPI · SQLAlchemy 2.0 · Pydantic v2 · SQLite (dev) / PostgreSQL (prod) · JWT · pytest

## Como executar

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

python -m app.seed                    # popula programas, regras, parâmetros e demo
uvicorn app.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI: http://localhost:8000/openapi.json

### Contas de demonstração

| E-mail | Senha | Papel |
|---|---|---|
| `admin@mapadodireito.org` | `admin12345` | admin |
| `cras@mapadodireito.org` | `cras12345` | assistente_social |

### Testes

```bash
pytest -v          # 40 testes
```

### Coleção Postman

Já incluída em `docs/colecao-postman.json` (29 requisições, organizadas por tag). O request de login salva o token na variável `{{token}}` automaticamente — os demais já o utilizam.

Para regerar após mudar endpoints:

```bash
python scripts/gerar_postman.py
```

## Endpoints

### Autenticação
| Método | Rota | Acesso |
|---|---|---|
| POST | `/api/v1/auth/registrar` | público |
| POST | `/api/v1/auth/login` | público |
| GET | `/api/v1/auth/me` | autenticado |

### Programas
| Método | Rota | Acesso |
|---|---|---|
| GET | `/api/v1/programas` | público |
| GET | `/api/v1/programas/{id}` | público |
| GET | `/api/v1/programas/{id}/requisitos` | público |
| POST | `/api/v1/programas` | admin |
| PUT | `/api/v1/programas/{id}` | admin |
| DELETE | `/api/v1/programas/{id}` | admin |
| POST | `/api/v1/programas/{id}/regras` | admin |
| DELETE | `/api/v1/regras/{id}` | admin |

### Famílias
| Método | Rota | Acesso |
|---|---|---|
| POST | `/api/v1/familias` | assistente_social, admin |
| GET | `/api/v1/familias` | assistente_social, admin |
| GET | `/api/v1/familias/{id}` | dono ou admin |
| PUT | `/api/v1/familias/{id}` | dono ou admin |
| DELETE | `/api/v1/familias/{id}` | admin |
| POST | `/api/v1/familias/{id}/membros` | dono ou admin |
| GET | `/api/v1/familias/{id}/membros` | dono ou admin |
| PUT | `/api/v1/membros/{id}` | dono ou admin |
| DELETE | `/api/v1/membros/{id}` | dono ou admin |

### Elegibilidade
| Método | Rota | Acesso |
|---|---|---|
| POST | `/api/v1/elegibilidade/simular` | público |
| POST | `/api/v1/familias/{id}/simulacoes` | dono ou admin |
| GET | `/api/v1/familias/{id}/simulacoes` | dono ou admin |
| GET | `/api/v1/simulacoes/{id}` | dono ou admin |

### Gestão
| Método | Rota | Acesso |
|---|---|---|
| GET | `/api/v1/parametros` | público |
| PUT | `/api/v1/parametros/{chave}` | admin |
| GET | `/api/v1/relatorios/cobertura` | admin |
| GET | `/api/v1/relatorios/pendencias-frequentes` | admin |
| GET | `/api/v1/health` | público |

## Exemplo

**Requisição**

```bash
curl -X POST http://localhost:8000/api/v1/elegibilidade/simular \
  -H "Content-Type: application/json" \
  -d '{
    "municipio": "Salvador", "uf": "BA",
    "renda_total_mensal": 800, "situacao_moradia": "alugada",
    "possui_cadunico": true,
    "membros": [
      {"nome":"Maria","data_nascimento":"1990-03-12","parentesco":"responsavel","gestante":true},
      {"nome":"Joana","data_nascimento":"2019-08-01","parentesco":"filho"},
      {"nome":"Antônio","data_nascimento":"1955-01-20","parentesco":"pai","possui_deficiencia":true}
    ]}'
```

**Resposta (trecho)**

```json
{
  "perfil_calculado": {
    "num_membros": 3, "renda_per_capita": 266.67,
    "possui_gestante": true, "possui_idoso_65": true, "possui_pcd": true
  },
  "resumo": {"programas_avaliados": 4, "elegivel_em": 2, "quase_elegivel_em": 0},
  "resultados": [
    {"programa_nome": "Benefício de Prestação Continuada (BPC/LOAS)",
     "elegivel": true, "percentual_atendimento": 100.0},
    {"programa_nome": "Bolsa Família", "elegivel": false, "percentual_atendimento": 66.7,
     "pendencias": [{
        "codigo": "BF_RENDA",
        "descricao": "Renda mensal por pessoa dentro da linha de pobreza",
        "valor_informado": 266.67, "valor_exigido": 218.0,
        "orientacao": "O valor informado está 48.67 acima do limite de 218.00."
     }]}
  ]
}
```

## Formato de erro

Toda falha responde no mesmo envelope:

```json
{"erro": {"codigo": "ACESSO_NEGADO", "mensagem": "Acesso restrito aos papéis: admin.", "detalhes": []}}
```

## Observação sobre os valores dos programas

Os valores em `app/seed.py` foram conferidos em 22/09/2026 nas fontes oficiais: salário mínimo de R$ 1.621,00 (Decreto nº 12.797/2025, vigente desde 1º/jan/2026) e linha de pobreza do Bolsa Família de R$ 218,00 por pessoa (Lei 14.601/2023). O salário mínimo é reajustado todo mês de janeiro — vale reconferir antes de qualquer apresentação futura. Como as regras são dados, um reajuste é só atualizar o registro em `parametros`; nenhuma linha de código muda.

## Estrutura

```
app/
├── main.py              # instância FastAPI, routers, metadados do Swagger
├── config.py            # settings via .env
├── database.py          # engine, sessão, Base
├── core/
│   ├── motor_regras.py  # motor de avaliação (puro, sem banco nem HTTP)
│   ├── seguranca.py     # hash, JWT, papéis
│   └── excecoes.py      # envelope de erro padronizado
├── models/              # SQLAlchemy
├── schemas/             # Pydantic (entrada/saída separados)
├── services/            # perfil computado e orquestração da simulação
├── routers/             # camada HTTP
└── seed.py
tests/                   # 40 testes
scripts/gerar_postman.py
docs/                    # openapi.json + coleção Postman
```

## Autor

Luiz Eduardo Reis Souza · [GitHub](https://github.com/L-edu) · [LinkedIn](https://linkedin.com/in/eduardo-reisdeveloper)
