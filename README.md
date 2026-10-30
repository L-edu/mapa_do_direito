# Mapa do Direito

Aplicação web que identifica a quais programas sociais uma família tem direito e, quando ainda não tem,
**mostra exatamente o que falta**. Vinculada ao **ODS 1 — Erradicação da Pobreza** (meta 1.3).

- **Sprint 1 — API** (FastAPI + SQLAlchemy): pasta `app/`, testes em `tests/`.
- **Sprint 2 — Front-end e integração** (React + Vite): pasta `frontend/`.

```
mapa-do-direito/
├── app/            # API FastAPI (rotas, regras, modelos, segurança)
├── tests/          # 48 testes automatizados da API
├── frontend/       # Aplicação React (componentizada) que consome a API
├── docs/           # Coleção Postman
├── scripts/        # Gerador da coleção Postman a partir do OpenAPI
└── .github/        # CI: testes da API + build do front
```

## O problema e a solução

Muitas famílias em vulnerabilidade não acessam benefícios aos quais já teriam direito: desconhecem os critérios, têm o
cadastro desatualizado ou foram negadas sem explicação. O Mapa do Direito recebe o perfil da família e responde, para
cada programa: **se é elegível**, **quais requisitos já cumpre** e **o que falta** (em linguagem simples).

**Decisão de arquitetura — regras como dados.** As regras de elegibilidade não estão em `if/else`: ficam no banco
(`campo` + `operador` + `valor`). Cadastrar um programa novo é uma chamada à API; reajustar o salário mínimo é atualizar
um registro e todas as regras derivadas (1/4, 1/2, 2x o salário) passam a usar o novo valor. Regras com o mesmo
`grupo_logico` são combinadas em **OU** (ex.: BPC = idoso 65+ **ou** pessoa com deficiência).

**Privacidade (LGPD).** Não recebemos nem armazenamos CPF, NIS ou RG. A família recebe um código opaco e as pessoas são
registradas só com o primeiro nome e os atributos necessários para avaliar o direito.

## Como executar (Windows / PowerShell)

Pré-requisitos: **Python 3.12+** e **Node.js 20+**. Use dois terminais.

**Terminal 1 — API**

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.seed                      # cria tabelas, programas, regras, parâmetros e contas de demonstração
uvicorn app.main:app --reload           # http://localhost:8000  (Swagger em /docs)
```

**Terminal 2 — Front-end**

```powershell
cd frontend
npm install
copy .env.example .env                  # opcional: só é preciso se a API não estiver em localhost:8000
npm run dev                             # http://localhost:5173
```

> Linux/macOS: troque `.venv\Scripts\activate` por `source .venv/bin/activate` e `copy` por `cp`.

### Contas de demonstração

| E-mail | Senha | Papel | O que pode fazer |
|---|---|---|---|
| `admin@mapadodireito.org` | `admin12345` | Administrador | Tudo: programas, regras, parâmetros, usuários, relatórios |
| `cras@mapadodireito.org` | `cras12345` | Assistente social | Cadastrar famílias atendidas e simular com histórico |
| `cidadao@mapadodireito.org` | `cidadao12345` | Cidadão | Cadastrar e simular a própria família |

A tela de login tem botões que preenchem essas contas (desligue com `VITE_MOSTRAR_CONTAS_DEMO=false`).
Quem cria conta pelo site entra sempre como **Cidadão**; só um administrador cria assistentes sociais e outros admins.

## Funcionalidades do front-end (Sprint 2)

| Tela | Rota | Acesso | Operações na API |
|---|---|---|---|
| Início | `/` | público | `GET /programas` |
| Simulador | `/simulador` | público | `POST /elegibilidade/simular` |
| Login / Criar conta | `/login`, `/registro` | público | `POST /auth/login`, `POST /auth/registrar`, `GET /auth/me` |
| Catálogo e requisitos | `/programas`, `/programas/:id` | público | `GET /programas`, `GET /programas/{id}`, `GET /programas/{id}/requisitos` |
| Famílias (lista, filtros, paginação) | `/familias` | logado | `GET /familias`, `DELETE /familias/{id}` |
| Cadastrar / editar família | `/familias/nova`, `/familias/:id/editar` | logado | `POST /familias`, `PUT /familias/{id}` |
| Detalhe da família + pessoas | `/familias/:id` | logado | `GET /familias/{id}`, `POST /familias/{id}/membros`, `PUT/DELETE /membros/{id}` |
| Simular com histórico | `/simulacoes/:id` | logado | `POST /familias/{id}/simulacoes`, `GET /familias/{id}/simulacoes`, `GET /simulacoes/{id}` |
| Painel de gestão | `/admin` | admin | `GET /relatorios/cobertura`, `GET /relatorios/pendencias-frequentes` |
| Parâmetros | `/admin/parametros` | admin | `GET /parametros`, `PUT /parametros/{chave}` |
| Usuários | `/admin/usuarios` | admin | `GET/POST /usuarios`, `PATCH /usuarios/{id}` |
| Programas e regras (CRUD) | `/admin/programas/...`, `/programas/:id` | admin | `POST/PUT/DELETE /programas`, `POST/PUT/DELETE /regras` |

Todas as telas consomem a API; não há dados estáticos. Erros da API (validação, permissão, rede, sessão expirada) são
exibidos ao usuário e as operações de sucesso geram avisos.

### Organização do front-end

```
frontend/src/
├── api/          # client.js (fetch + JWT + erros padronizados) e servicos.js (um objeto por recurso)
├── contexts/     # AuthContext (sessão/JWT) e AlertasContext (avisos)
├── hooks/        # useCarregar (estado de requisição)
├── components/
│   ├── ui/         # Botao, Campos, Alerta, Badge, Paginacao, ModalConfirmacao...
│   ├── layout/     # Layout, Navbar, RotaProtegida
│   ├── simulacao/  # CardPrograma, PerfilCalculado, ResultadoSimulacao
│   ├── familias/   # FormularioFamilia, CamposMembro, FormularioMembro, TabelaMembros
│   └── programas/  # FormularioPrograma, FormularioRegra, GerenciarRegras
├── pages/        # uma página por rota (e pages/admin)
└── utils/        # constantes e formatadores
```

## Testes

```powershell
pytest -v                    # 48 testes da API (regras, perfis, permissões, usuários, CRUD)
cd frontend; npm run build   # verifica a compilação do front
```

O CI do GitHub (`.github/workflows/ci.yml`) executa os dois a cada push.

## Documentação da API

- Swagger UI: http://localhost:8000/docs · ReDoc: `/redoc` · OpenAPI: `/openapi.json`
- Coleção Postman: `docs/colecao-postman.json` (33 requisições; o login salva o token em `{{token}}`).
  Para regenerar após mudar endpoints: `python scripts/gerar_postman.py`.

### Papéis e permissões

| Recurso | Anônimo | Cidadão | Assistente social | Admin |
|---|:--:|:--:|:--:|:--:|
| Simular sem cadastro, ver catálogo e parâmetros | ✅ | ✅ | ✅ | ✅ |
| Cadastrar, editar, simular e excluir **as próprias** famílias | — | ✅ | ✅ | ✅ (todas) |
| Gerir programas, regras e parâmetros | — | — | — | ✅ |
| Gerir usuários e ver relatórios | — | — | — | ✅ |

### Formato de erro

```json
{"erro": {"codigo": "ACESSO_NEGADO", "mensagem": "Acesso restrito aos papéis: admin.", "detalhes": []}}
```

## Valores de referência

Conferidos em 22/09/2026 nas fontes oficiais: salário mínimo de **R$ 1.621,00** (Decreto nº 12.797/2025, vigente desde
1º/jan/2026) e linha de pobreza do Bolsa Família de **R$ 218,00** por pessoa (Lei 14.601/2023). O salário mínimo é
reajustado todo janeiro: reconfira antes de apresentar e atualize em **Parâmetros** (sem alterar código).

## Segurança e produção

Para desenvolvimento, o CORS aceita qualquer origem. Em produção: restrinja `allow_origins`, troque `JWT_SECRET` e
`SALT_IDENTIFICADOR` no `.env`, use PostgreSQL (`DATABASE_URL`), sirva por HTTPS e defina
`VITE_MOSTRAR_CONTAS_DEMO=false`. O `Dockerfile` e o `docker-compose.yml` sobem API + PostgreSQL.

## Autor

Luiz Eduardo Reis Souza · [GitHub](https://github.com/L-edu) · [LinkedIn](https://linkedin.com/in/eduardo-reisdeveloper)
