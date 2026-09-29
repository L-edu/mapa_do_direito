'use strict';

/**
 * Ajuste esta constante se a API estiver rodando em outra porta ou host.
 * Padrão do `uvicorn app.main:app --reload`: http://localhost:8000
 */
const API_BASE_URL = 'http://localhost:8000';
const ENDPOINT_SIMULAR = `${API_BASE_URL}/api/v1/elegibilidade/simular`;

const form = document.getElementById('form-simulacao');
const listaMembros = document.getElementById('lista-membros');
const templateMembro = document.getElementById('template-membro');
const btnAddMembro = document.getElementById('btn-add-membro');
const btnSimular = document.getElementById('btn-simular');
const saidaErro = document.getElementById('erro');
const saidaResultado = document.getElementById('resultado');

// Rótulos amigáveis para as chaves de "perfil_calculado".
// Esse campo é tipado como objeto genérico na API (não tem um schema fixo de
// saída), então qualquer chave não mapeada aqui cai no formatador padrão.
const ROTULOS_PERFIL = {
  municipio: 'Município',
  uf: 'UF',
  num_membros: 'Número de pessoas na família',
  renda_total_mensal: 'Renda total mensal',
  renda_per_capita: 'Renda por pessoa',
  situacao_moradia: 'Situação de moradia',
  situacao_rua: 'Em situação de rua',
  possui_cadunico: 'Inscrita no CadÚnico',
  idade_minima: 'Idade da pessoa mais nova',
  idade_maxima: 'Idade da pessoa mais velha',
  possui_crianca_0_6: 'Tem criança de 0 a 6 anos',
  possui_adolescente_7_17: 'Tem criança/adolescente de 7 a 17 anos',
  possui_jovem_15_29: 'Tem jovem de 15 a 29 anos',
  possui_idoso_65: 'Tem pessoa idosa (65 anos ou mais)',
  possui_gestante: 'Tem gestante',
  possui_pcd: 'Tem pessoa com deficiência',
  possui_crianca_fora_escola: 'Tem criança/adolescente fora da escola',
  possui_publico_prioritario: 'Tem público prioritário (criança, adolescente ou gestante)',
};

const SITUACAO_MORADIA_LABEL = {
  propria: 'Própria',
  alugada: 'Alugada',
  cedida: 'Cedida',
  situacao_rua: 'Situação de rua',
};

const MOEDA = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

function formatarRotulo(chave) {
  if (ROTULOS_PERFIL[chave]) return ROTULOS_PERFIL[chave];
  // Chave desconhecida: melhor esforço (snake_case -> "Snake case").
  const legivel = chave.replaceAll('_', ' ');
  return legivel.charAt(0).toUpperCase() + legivel.slice(1);
}

function formatarValor(chave, valor) {
  if (valor === null || valor === undefined) return '—';
  if (typeof valor === 'boolean') return valor ? 'Sim' : 'Não';
  if (chave === 'situacao_moradia' && SITUACAO_MORADIA_LABEL[valor]) {
    return SITUACAO_MORADIA_LABEL[valor];
  }
  if (typeof valor === 'number' && chave.toLowerCase().includes('renda')) {
    return MOEDA.format(valor);
  }
  return String(valor);
}

// --- Membros dinâmicos -----------------------------------------------------

function adicionarMembro() {
  const clone = templateMembro.content.cloneNode(true);
  const fieldset = clone.querySelector('.membro');
  const campoNascimento = clone.querySelector('.campo-nascimento');
  campoNascimento.max = new Date().toISOString().split('T')[0];

  clone.querySelector('.btn-remover-membro').addEventListener('click', () => {
    if (listaMembros.querySelectorAll('.membro').length <= 1) {
      exibirErro('A família precisa ter ao menos uma pessoa cadastrada.');
      return;
    }
    fieldset.remove();
  });

  listaMembros.appendChild(clone);
}

btnAddMembro.addEventListener('click', adicionarMembro);
adicionarMembro(); // a API exige ao menos 1 membro (membros: min_length=1)

// --- Coleta do payload -------------------------------------------------------

function coletarMembros() {
  return Array.from(listaMembros.querySelectorAll('.membro')).map((fieldset) => ({
    nome: fieldset.querySelector('.campo-nome').value.trim(),
    data_nascimento: fieldset.querySelector('.campo-nascimento').value,
    parentesco: fieldset.querySelector('.campo-parentesco').value,
    escolaridade: fieldset.querySelector('.campo-escolaridade').value.trim() || null,
    renda_individual: Number(fieldset.querySelector('.campo-renda').value) || 0,
    possui_deficiencia: fieldset.querySelector('.campo-pcd').checked,
    gestante: fieldset.querySelector('.campo-gestante').checked,
    frequenta_escola: fieldset.querySelector('.campo-escola').checked,
  }));
}

function coletarPayload() {
  const dados = new FormData(form);
  return {
    municipio: String(dados.get('municipio') || '').trim(),
    uf: String(dados.get('uf') || '').trim().toUpperCase(),
    renda_total_mensal: Number(dados.get('renda_total_mensal')) || 0,
    situacao_moradia: dados.get('situacao_moradia'),
    possui_cadunico: document.getElementById('possui_cadunico').checked,
    membros: coletarMembros(),
  };
}

// --- Chamada à API -----------------------------------------------------------

async function simularElegibilidade(payload) {
  let resposta;
  try {
    resposta = await fetch(ENDPOINT_SIMULAR, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (falhaDeRede) {
    // fetch lança TypeError quando a API está fora do ar, CORS bloqueou,
    // ou não há conexão — nunca quando a API responde com erro HTTP.
    throw new Error(
      `Não foi possível conectar à API em ${API_BASE_URL}. ` +
      'Verifique se o servidor está rodando (uvicorn app.main:app --reload) ' +
      'e se a porta em API_BASE_URL (script.js) está correta.'
    );
  }

  let corpo = null;
  try {
    corpo = await resposta.json();
  } catch {
    // Resposta sem corpo JSON válido (ex.: erro 500 não tratado, proxy, etc.).
  }

  if (!resposta.ok) {
    const mensagem = corpo?.erro?.mensagem || `A API respondeu com o status ${resposta.status}.`;
    const erro = new Error(mensagem);
    erro.detalhes = corpo?.erro?.detalhes || [];
    throw erro;
  }

  return corpo;
}

// --- Renderização do resultado -----------------------------------------------

function limparSaida() {
  saidaErro.hidden = true;
  saidaErro.textContent = '';
  saidaResultado.innerHTML = '';
}

function exibirErro(mensagem, detalhes = []) {
  saidaErro.hidden = false;
  saidaErro.textContent = mensagem;

  if (detalhes.length) {
    const lista = document.createElement('ul');
    detalhes.forEach((detalhe) => {
      const item = document.createElement('li');
      item.textContent = `${detalhe.campo || 'campo'}: ${detalhe.mensagem}`;
      lista.appendChild(item);
    });
    saidaErro.appendChild(lista);
  }
}

function renderizarPerfil(perfil) {
  const secao = document.createElement('section');
  secao.innerHTML = '<h2>Perfil calculado</h2>';

  const lista = document.createElement('dl');
  Object.entries(perfil).forEach(([chave, valor]) => {
    const termo = document.createElement('dt');
    termo.textContent = formatarRotulo(chave);
    const definicao = document.createElement('dd');
    definicao.textContent = formatarValor(chave, valor);
    lista.appendChild(termo);
    lista.appendChild(definicao);
  });
  secao.appendChild(lista);
  return secao;
}

function renderizarResumo(resumo) {
  const secao = document.createElement('section');
  secao.innerHTML = '<h2>Resumo</h2>';

  const paragrafo = document.createElement('p');
  paragrafo.textContent =
    `${resumo.programas_avaliados} programa(s) avaliado(s) — ` +
    `elegível em ${resumo.elegivel_em}, ` +
    `quase elegível em ${resumo.quase_elegivel_em} ` +
    '(70% ou mais dos requisitos atendidos).';
  secao.appendChild(paragrafo);
  return secao;
}

function renderizarListaDeRegras(titulo, regras) {
  const bloco = document.createElement('div');
  const rotulo = document.createElement('h4');
  rotulo.textContent = titulo;
  bloco.appendChild(rotulo);

  const lista = document.createElement('ul');
  regras.forEach((regra) => {
    const item = document.createElement('li');
    item.textContent = regra.orientacao
      ? `${regra.descricao} — ${regra.orientacao}`
      : regra.descricao;
    lista.appendChild(item);
  });
  bloco.appendChild(lista);
  return bloco;
}

function renderizarPrograma(resultado) {
  const artigo = document.createElement('article');
  artigo.classList.add(resultado.elegivel ? 'programa--elegivel' : 'programa--pendente');

  const titulo = document.createElement('h3');
  titulo.textContent = resultado.programa_nome;
  artigo.appendChild(titulo);

  const status = document.createElement('p');
  const selo = document.createElement('span');
  selo.className = `badge ${resultado.elegivel ? 'badge--elegivel' : 'badge--pendente'}`;
  selo.textContent = resultado.elegivel ? 'Elegível' : 'Ainda não elegível';
  status.appendChild(selo);
  status.append(` — ${resultado.percentual_atendimento}% dos requisitos atendidos.`);
  artigo.appendChild(status);

  if (resultado.pendencias.length) {
    artigo.appendChild(renderizarListaDeRegras('O que falta', resultado.pendencias));
  }
  if (resultado.regras_atendidas.length) {
    artigo.appendChild(renderizarListaDeRegras('Requisitos já atendidos', resultado.regras_atendidas));
  }

  return artigo;
}

function renderizarResultado(dados) {
  saidaResultado.innerHTML = '';
  saidaResultado.appendChild(renderizarPerfil(dados.perfil_calculado));
  saidaResultado.appendChild(renderizarResumo(dados.resumo));

  const secaoProgramas = document.createElement('section');
  secaoProgramas.innerHTML = '<h2>Programas avaliados</h2>';

  const ordenados = [...dados.resultados].sort(
    (a, b) => Number(b.elegivel) - Number(a.elegivel) || b.percentual_atendimento - a.percentual_atendimento
  );
  ordenados.forEach((resultado) => secaoProgramas.appendChild(renderizarPrograma(resultado)));

  saidaResultado.appendChild(secaoProgramas);
}

// --- Envio do formulário -------------------------------------------------------

form.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  limparSaida();

  if (!form.reportValidity()) return;

  const payload = coletarPayload();

  btnSimular.disabled = true;
  const textoOriginal = btnSimular.textContent;
  btnSimular.textContent = 'Simulando...';

  try {
    const dados = await simularElegibilidade(payload);
    renderizarResultado(dados);
  } catch (erro) {
    exibirErro(erro.message, erro.detalhes || []);
  } finally {
    btnSimular.disabled = false;
    btnSimular.textContent = textoOriginal;
  }
});
