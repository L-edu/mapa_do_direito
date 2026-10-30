"""Mapa do Direito — API de elegibilidade a programas sociais.

Projeto vinculado ao ODS 1 (Erradicação da Pobreza), meta 1.3: implementar sistemas
de proteção social e garantir uma cobertura substancial dos pobres e vulneráveis.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.excecoes import registrar_handlers
from app.database import Base, engine
from app.models import *  # noqa: F401,F403  (garante o registro das tabelas no metadata)
from app.routers import auth, elegibilidade, familias, gestao, programas, usuarios

DESCRICAO = """
API que identifica a quais programas de transferência de renda e benefícios sociais
uma família tem direito, e — quando ainda não tem — **exatamente o que falta** para
se enquadrar.

### Problema
Parte significativa das famílias em situação de vulnerabilidade não acessa benefícios
aos quais já teria direito, por desconhecimento dos critérios ou por pendências
cadastrais simples. O caminho inverso também ocorre: pessoas tentam o benefício,
são negadas e não recebem orientação sobre o motivo.

### Como funciona
As regras de elegibilidade **não estão codificadas em `if/else`**: ficam no banco como
dados declarativos (`campo` + `operador` + `valor`). Isso permite cadastrar um programa
novo ou reajustar um limite de renda sem alterar uma linha de código.

### Papéis
| Papel | Permissões |
|---|---|
| `cidadao` | Simulação, cadastro e histórico da própria família |
| `assistente_social` | Cadastro de famílias atendidas e simulações com histórico |
| `admin` | Gestão de programas, regras, parâmetros, usuários e relatórios |

### Privacidade
Em conformidade com a LGPD, a API **não recebe nem armazena CPF, NIS ou qualquer
identificador direto**. Cada família recebe um código interno opaco.
"""

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Em produção, troque por migrations do Alembic (`alembic upgrade head`)."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NOME,
    version=settings.APP_VERSAO,
    description=DESCRICAO,
    contact={"name": "Luiz Eduardo Reis Souza", "email": "luiz.e.souzadev@gmail.com"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "Elegibilidade", "description": "Simulação do direito a benefícios."},
        {"name": "Programas", "description": "Catálogo de programas e seus requisitos."},
        {"name": "Famílias", "description": "Cadastro socioeconômico e composição familiar."},
        {"name": "Gestão", "description": "Parâmetros de referência e relatórios agregados."},
        {"name": "Autenticação", "description": "Registro, login e emissão de token JWT."},
        {"name": "Usuários", "description": "Gestão de contas e papéis (admin)."},
        {"name": "Infraestrutura", "description": "Healthcheck."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_handlers(app)

for modulo in (auth, usuarios, programas, familias, elegibilidade, gestao):
    app.include_router(modulo.router)


@app.get("/", include_in_schema=False)
def raiz():
    return {
        "aplicacao": settings.APP_NOME,
        "versao": settings.APP_VERSAO,
        "ods": "ODS 1 — Erradicação da Pobreza",
        "documentacao": "/docs",
        "openapi": "/openapi.json",
    }
