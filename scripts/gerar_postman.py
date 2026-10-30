"""Gera docs/colecao-postman.json a partir do schema OpenAPI da própria API.

    python scripts/gerar_postman.py

A coleção já vem com a variável {{base_url}} e o token {{token}} preenchido
automaticamente pelo script de teste do endpoint de login.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from app.main import app  # noqa: E402

SAIDA = RAIZ / "docs" / "colecao-postman.json"

EXEMPLOS = {
    "/api/v1/auth/login": {"email": "admin@mapadodireito.org", "senha": "admin12345"},
    "/api/v1/auth/registrar": {
        "nome": "Maria Souza",
        "email": "maria@exemplo.org",
        "senha": "senhaSegura123",
    },
    "/api/v1/elegibilidade/simular": {
        "municipio": "Salvador",
        "uf": "BA",
        "renda_total_mensal": 800.0,
        "situacao_moradia": "alugada",
        "possui_cadunico": True,
        "membros": [
            {
                "nome": "Maria",
                "data_nascimento": "1990-03-12",
                "parentesco": "responsavel",
                "gestante": True,
            },
            {"nome": "Joana", "data_nascimento": "2019-08-01", "parentesco": "filho"},
            {
                "nome": "Antônio",
                "data_nascimento": "1955-01-20",
                "parentesco": "pai",
                "possui_deficiencia": True,
            },
        ],
    },
    "/api/v1/familias": {
        "municipio": "Salvador",
        "uf": "BA",
        "renda_total_mensal": 600.0,
        "situacao_moradia": "cedida",
        "possui_cadunico": True,
        "membros": [
            {"nome": "Ana", "data_nascimento": "1988-02-10", "parentesco": "responsavel"},
            {"nome": "Lucas", "data_nascimento": "2012-06-05", "parentesco": "filho"},
        ],
    },
    "/api/v1/usuarios": {
        "nome": "Nova Assistente",
        "email": "assistente@exemplo.org",
        "senha": "senhaSegura123",
        "papel": "assistente_social",
    },
    "/api/v1/usuarios/{usuario_id}": {"papel": "assistente_social", "ativo": True},
    "/api/v1/regras/{regra_id}": {"valor": "250", "obrigatoria": True},
    "/api/v1/parametros/{chave}": {
        "valor": 1621.0,
        "descricao": "Salário mínimo vigente",
        "fonte": "Decreto federal",
    },
}

SCRIPT_LOGIN = [
    "const dados = pm.response.json();",
    "if (dados.access_token) {",
    "  pm.collectionVariables.set('token', dados.access_token);",
    "  console.log('Token salvo na variável {{token}}');",
    "}",
]


def montar_item(rota: str, metodo: str, operacao: dict) -> dict:
    caminho = [p for p in rota.strip("/").split("/") if p]
    item = {
        "name": operacao.get("summary", f"{metodo.upper()} {rota}"),
        "request": {
            "method": metodo.upper(),
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "url": {
                "raw": "{{base_url}}" + rota,
                "host": ["{{base_url}}"],
                "path": caminho,
            },
            "description": operacao.get("description", ""),
        },
    }

    if "requestBody" in operacao:
        exemplo = EXEMPLOS.get(rota, {})
        item["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(exemplo, indent=2, ensure_ascii=False),
            "options": {"raw": {"language": "json"}},
        }

    if "security" in operacao or "admin" in operacao.get("description", "").lower():
        item["request"]["header"].append({"key": "Authorization", "value": "Bearer {{token}}"})
    else:
        item["request"]["header"].append({"key": "Authorization", "value": "Bearer {{token}}"})

    if rota.endswith("/auth/login"):
        item["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": SCRIPT_LOGIN}}]

    return item


def main() -> None:
    schema = app.openapi()
    pastas: dict[str, dict] = {}

    for rota, metodos in schema["paths"].items():
        for metodo, operacao in metodos.items():
            tag = (operacao.get("tags") or ["Geral"])[0]
            pastas.setdefault(tag, {"name": tag, "item": []})
            pastas[tag]["item"].append(montar_item(rota, metodo, operacao))

    colecao = {
        "info": {
            "name": "Mapa do Direito — API de elegibilidade (ODS 1)",
            "description": schema["info"].get("description", ""),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [
            {"key": "base_url", "value": "http://localhost:8000"},
            {"key": "token", "value": ""},
        ],
        "item": list(pastas.values()),
    }

    SAIDA.parent.mkdir(exist_ok=True)
    SAIDA.write_text(json.dumps(colecao, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Coleção gerada em {SAIDA} ({sum(len(p['item']) for p in pastas.values())} requisições).")


if __name__ == "__main__":
    main()
