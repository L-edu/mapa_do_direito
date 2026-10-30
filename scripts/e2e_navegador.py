"""Roteiro de teste ponta a ponta no navegador (Playwright) — 28 verificações.

Cobre público, login, CRUD de famílias/pessoas, simulação com histórico, permissões por papel e as telas de admin.

Pré-requisitos (três terminais):
    1) uvicorn app.main:app --port 8000          (com o banco recém-populado: python -m app.seed)
    2) cd frontend && npm run dev                (http://localhost:5173)
    3) pip install playwright && playwright install chromium
       python scripts/e2e_navegador.py

Cria dados de teste (usuário joana.e2e@..., programa "Programa E2E"); rode sobre um banco de desenvolvimento.
"""
import re, sys
from playwright.sync_api import sync_playwright, expect

URL = "http://localhost:5173"
erros_console = []
passos = []

def ok(msg):
    passos.append(msg); print("  OK ", msg)

def entrar_demo(page, rotulo):
    page.goto(f"{URL}/login")
    page.get_by_role("button", name=rotulo).click()
    page.get_by_role("button", name="Entrar", exact=True).click()

def preencher_membro(page, indice, nome, nasc, parentesco=None, gestante=False, pcd=False):
    f = page.locator("fieldset.membro").nth(indice)
    f.get_by_label("Nome (apenas o primeiro nome)").fill(nome)
    f.get_by_label("Data de nascimento").fill(nasc)
    if parentesco: f.get_by_label("Parentesco").select_option(parentesco)
    if gestante: f.get_by_label("Gestante").check()
    if pcd: f.get_by_label("Possui deficiência").check()

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1100, "height": 900})
    page = ctx.new_page()
    page.on("console", lambda m: erros_console.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: erros_console.append(str(e)))

    print("== 1. Público ==")
    page.goto(URL)
    expect(page.locator(".programa-item")).to_have_count(4)
    ok("Home carrega os 4 programas vindos da API")
    page.screenshot(path="/tmp/shots/01-home.png", full_page=True)

    page.goto(f"{URL}/simulador")
    page.get_by_label("Município").fill("Salvador"); page.get_by_label("UF").fill("ba")
    page.get_by_label("Renda total mensal da família (R$)").fill("300")
    page.get_by_label("A família está inscrita no Cadastro Único").check()
    preencher_membro(page, 0, "Maria", "1990-03-12", "responsavel", gestante=True)
    page.get_by_role("button", name="+ Adicionar pessoa").click()
    preencher_membro(page, 1, "Antonio", "1950-01-20", "pai", pcd=True)
    page.get_by_role("button", name="Simular elegibilidade").click()
    expect(page.locator(".programa-card")).to_have_count(4)
    expect(page.locator(".programa-card--elegivel").first).to_be_visible()
    ok("Simulador público: 2 pessoas, resultado com 4 programas")
    page.screenshot(path="/tmp/shots/02-simulador-resultado.png", full_page=True)

    print("== 2. Autenticação ==")
    page.goto(f"{URL}/login")
    page.get_by_label("E-mail").fill("cras@mapadodireito.org"); page.get_by_label("Senha").fill("errada123")
    page.get_by_role("button", name="Entrar", exact=True).click()
    expect(page.get_by_role("alert").filter(has_text="incorretos")).to_be_visible()
    ok("Login com senha errada mostra mensagem de erro da API")

    page.goto(f"{URL}/familias")
    expect(page).to_have_url(re.compile(r"/login"))
    ok("Rota protegida sem login redireciona para /login")

    print("== 3. Assistente social: CRUD de famílias ==")
    entrar_demo(page, "Assistente social")
    expect(page).to_have_url(re.compile(r"/familias$"))
    expect(page.get_by_text("Bem-vindo(a), Assistente Social CRAS!")).to_be_visible()
    ok("Login como assistente social redireciona para /familias")
    page.screenshot(path="/tmp/shots/03-familias-lista.png", full_page=True)

    page.get_by_role("button", name="+ Nova família").click(); expect(page.get_by_role("heading", name="Nova família")).to_be_visible()
    page.get_by_label("Município").fill("Lauro de Freitas"); page.get_by_label("UF").fill("BA")
    page.get_by_label("Renda total mensal da família (R$)").fill("600")
    page.get_by_label("A família está inscrita no Cadastro Único").check()
    preencher_membro(page, 0, "Ana", "1988-02-10", "responsavel")
    page.get_by_role("button", name="+ Adicionar pessoa").click()
    preencher_membro(page, 1, "Lucas", "2019-06-05", "filho")
    page.get_by_role("button", name="Cadastrar família").click()
    expect(page.get_by_text("Família cadastrada com sucesso.")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/familias/\d+$"))
    expect(page.locator("tbody tr")).to_have_count(2)
    ok("CREATE: família cadastrada com 2 pessoas e detalhe exibido")
    familia_url = page.url
    page.screenshot(path="/tmp/shots/04-familia-detalhe.png", full_page=True)

    page.get_by_role("button", name="+ Adicionar pessoa").click()
    painel = page.locator("form.cartao--destaque")
    painel.get_by_label("Nome (apenas o primeiro nome)").fill("Marta")
    painel.get_by_label("Data de nascimento").fill("1955-04-02")
    painel.get_by_label("Parentesco").select_option("mae")
    painel.get_by_role("button", name="Adicionar", exact=True).click()
    expect(page.get_by_text("Pessoa adicionada.")).to_be_visible()
    expect(page.locator("tbody tr").filter(has_text="Marta")).to_be_visible()
    ok("CREATE (membro): pessoa adicionada à família")

    page.get_by_role("button", name="Editar Marta").click()
    painel = page.locator("form.cartao--destaque")
    painel.get_by_label("Nome (apenas o primeiro nome)").fill("Marta Maria")
    painel.get_by_label("Possui deficiência").check()
    painel.get_by_role("button", name="Salvar alterações").click()
    expect(page.get_by_text("Pessoa atualizada.")).to_be_visible()
    expect(page.locator("tbody tr").filter(has_text="Marta Maria").get_by_text("Deficiência")).to_be_visible()
    ok("UPDATE (membro PUT): nome e deficiência atualizados")

    page.get_by_role("button", name="Remover Lucas").click()
    page.locator(".modal").get_by_role("button", name="Remover").click()
    expect(page.get_by_text("Lucas foi removido(a) da família.")).to_be_visible()
    expect(page.locator("tbody tr").filter(has_text="Lucas")).to_have_count(0)
    ok("DELETE (membro): pessoa removida após confirmação")

    page.get_by_role("button", name="Simular elegibilidade").click()
    expect(page).to_have_url(re.compile(r"/simulacoes/\d+$"))
    expect(page.locator(".programa-card")).to_have_count(4)
    ok("Simulação com histórico: resultado em /simulacoes/:id")
    page.screenshot(path="/tmp/shots/05-simulacao-detalhe.png", full_page=True)

    page.get_by_role("link", name="Voltar para a família").click()
    expect(page.get_by_role("heading", name="Histórico de simulações")).to_be_visible()
    expect(page.get_by_role("link", name="Ver resultado")).to_have_count(1)
    ok("Histórico lista a simulação registrada")

    page.get_by_role("link", name="Editar dados").click()
    page.get_by_label("Renda total mensal da família (R$)").fill("750")
    page.get_by_role("button", name="Salvar alterações").click()
    expect(page.get_by_text("Dados da família atualizados.")).to_be_visible()
    expect(page.get_by_text("R$ 750,00").first).to_be_visible()
    ok("UPDATE (família PUT): renda alterada para R$ 750,00")

    page.goto(f"{URL}/familias")
    page.locator("tbody tr").filter(has_text="Lauro de Freitas").get_by_role("button", name="Excluir").click()
    page.locator(".modal").get_by_role("button", name="Excluir").click()
    expect(page.get_by_text("Família excluída.")).to_be_visible()
    expect(page.locator("tbody tr").filter(has_text="Lauro de Freitas")).to_have_count(0)
    ok("DELETE (família): removida da listagem após confirmação")

    page.goto(f"{URL}/familias")
    page.get_by_label("Município").fill("Cidade Inexistente")
    with page.expect_request(re.compile(r"municipio=Cidade\+Inexistente|municipio=Cidade%20Inexistente")) as req:
        page.get_by_role("button", name="Filtrar").click()
    expect(page.get_by_text("Nenhuma família encontrada")).to_be_visible()
    ok("Filtros da listagem consultam a API (query string enviada e estado vazio exibido)")

    print("== 4. Cidadão: cadastro e permissões ==")
    page.get_by_role("button", name="Sair").click()
    page.goto(f"{URL}/registro")
    page.get_by_label(re.compile(r"^Nome\b")).fill("Joana Teste"); page.get_by_label("E-mail").fill("joana.e2e@exemplo.org")
    page.get_by_label(re.compile(r"^Senha\b")).fill("senhaSegura1"); page.get_by_label("Confirmar senha").fill("outraSenha1")
    page.get_by_role("button", name="Criar conta").click()
    expect(page.get_by_text("As senhas não conferem.")).to_be_visible()
    page.get_by_label("Confirmar senha").fill("senhaSegura1")
    page.get_by_role("button", name="Criar conta").click()
    expect(page.get_by_text("Conta criada com sucesso!")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/familias$"))
    ok("Registro valida senhas, cria conta de cidadão e já entra")

    page.goto(f"{URL}/admin")
    expect(page.get_by_text("Acesso restrito")).to_be_visible()
    ok("Cidadão não acessa área admin (tela de acesso restrito)")
    page.screenshot(path="/tmp/shots/06-acesso-restrito.png")

    page.goto(f"{URL}/familias/nova")
    page.get_by_label("Município").fill("Camaçari"); page.get_by_label("UF").fill("BA")
    preencher_membro(page, 0, "Joana", "1995-07-07", "responsavel")
    page.get_by_role("button", name="Cadastrar família").click()
    expect(page.get_by_text("Família cadastrada com sucesso.")).to_be_visible()
    ok("Cidadão cadastra a própria família")
    page.get_by_role("button", name="Sair").click()

    print("== 5. Administrador ==")
    entrar_demo(page, "Administrador")
    expect(page).to_have_url(re.compile(r"/admin$"))
    expect(page.get_by_text("família(s) analisada(s)")).to_be_visible()
    expect(page.locator(".barra-rotulada").first).to_be_visible()
    ok("Painel admin: relatórios de cobertura e pendências")
    page.screenshot(path="/tmp/shots/07-painel.png", full_page=True)

    page.goto(f"{URL}/admin/parametros")
    linha = page.locator("tbody tr").filter(has_text="salario_minimo")
    expect(linha).to_contain_text("1.621,00")
    linha.get_by_role("button", name="Editar").click()
    page.get_by_label("Valor").fill("1700")
    page.get_by_role("button", name="Salvar", exact=True).click()
    expect(page.get_by_text("Parâmetro salario_minimo salvo.")).to_be_visible()
    expect(page.locator("tbody tr").filter(has_text="salario_minimo")).to_contain_text("1.700,00")
    page.locator("tbody tr").filter(has_text="salario_minimo").get_by_role("button", name="Editar").click()
    page.get_by_label("Valor").fill("1621"); page.get_by_role("button", name="Salvar", exact=True).click()
    expect(page.locator("tbody tr").filter(has_text="salario_minimo")).to_contain_text("1.621,00")
    ok("Parâmetros: salário mínimo editado e restaurado")
    page.screenshot(path="/tmp/shots/08-parametros.png", full_page=True)

    page.goto(f"{URL}/admin/usuarios")
    page.get_by_label("Buscar").fill("joana.e2e"); page.get_by_role("button", name="Filtrar").click()
    linha = page.locator("tbody tr").filter(has_text="joana.e2e@exemplo.org")
    expect(linha).to_have_count(1)
    linha.get_by_label("Papel de Joana Teste").select_option("assistente_social")
    expect(page.get_by_text("Papel de Joana Teste atualizado.")).to_be_visible()
    linha.get_by_role("button", name="Ativo — desativar").click()
    expect(page.get_by_text("Joana Teste foi desativado(a).")).to_be_visible()
    expect(linha.get_by_role("button", name="Inativo — reativar")).to_be_visible()
    ok("Usuários: papel alterado (PATCH) e conta desativada")
    page.screenshot(path="/tmp/shots/09-usuarios.png", full_page=True)
    page.get_by_label("Buscar").fill("admin@"); page.get_by_role("button", name="Filtrar").click()
    expect(page.locator("tbody tr").first.get_by_label("Papel de Administrador")).to_be_disabled()
    ok("Admin não consegue rebaixar a própria conta (controle desabilitado)")

    page.get_by_role("button", name="+ Nova conta").click()
    page.get_by_label(re.compile(r"^Nome\b")).fill("Nova Assistente E2E"); page.get_by_label("E-mail").last.fill("nova.e2e@exemplo.org")
    page.get_by_label("Senha inicial").fill("senhaSegura1")
    page.get_by_role("button", name="Criar conta").click()
    expect(page.get_by_text("Conta criada.")).to_be_visible()
    ok("Usuários: nova conta de assistente social criada pelo admin")

    page.goto(f"{URL}/programas")
    page.get_by_role("link", name="+ Novo programa").click()
    page.get_by_label(re.compile(r"^Nome\b")).fill("Programa E2E")
    page.get_by_label("Identificador (slug)").fill("programa-e2e")
    page.get_by_role("button", name="Cadastrar programa").click()
    expect(page.get_by_text("Programa cadastrado.")).to_be_visible()
    expect(page.get_by_role("heading", name="Programa E2E")).to_be_visible()
    ok("Programa: criado pelo admin")

    page.get_by_role("button", name="+ Nova regra").click()
    painel = page.locator("form.cartao--destaque")
    painel.get_by_label("Código").fill("E2E_RENDA"); painel.get_by_label("Descrição para o cidadão").fill("Renda por pessoa até R$ 100")
    painel.get_by_label(re.compile(r"^Valor\b")).fill("100")
    painel.get_by_role("button", name="Adicionar regra").click()
    expect(page.get_by_text("Regra adicionada.")).to_be_visible()
    expect(page.locator("tbody tr").filter(has_text="E2E_RENDA")).to_be_visible()
    ok("Regra: adicionada ao programa")

    page.locator("tbody tr").filter(has_text="E2E_RENDA").get_by_role("button", name="Editar").click()
    painel = page.locator("form.cartao--destaque")
    painel.get_by_label(re.compile(r"^Valor\b")).fill("250")
    painel.get_by_role("button", name="Salvar regra").click()
    expect(page.get_by_text("Regra atualizada.")).to_be_visible()
    expect(page.locator("tbody tr").filter(has_text="E2E_RENDA")).to_contain_text("<= 250")
    ok("Regra: editada (PUT)")
    page.screenshot(path="/tmp/shots/10-programa-admin.png", full_page=True)

    page.locator("tbody tr").filter(has_text="E2E_RENDA").get_by_role("button", name="Remover").click()
    page.locator(".modal").get_by_role("button", name="Remover").click()
    expect(page.get_by_text("Regra E2E_RENDA removida.")).to_be_visible()
    ok("Regra: removida")

    page.get_by_role("button", name="Desativar").click()
    page.locator(".modal").get_by_role("button", name="Desativar").click()
    expect(page.get_by_text("Programa desativado.")).to_be_visible()
    expect(page.get_by_text("Inativo", exact=True)).to_be_visible()
    ok("Programa: desativado (DELETE lógico)")

    page.goto(f"{URL}/programas")
    expect(page.get_by_text("Programa E2E")).to_be_visible()
    ok("Admin continua vendo o programa inativo na listagem")
    b.close()

print(f"\n{len(passos)} verificações OK")
relevantes = [e for e in erros_console if "401" not in e and "409" not in e and "400" not in e]
print("Erros de console inesperados:", relevantes if relevantes else "nenhum")
