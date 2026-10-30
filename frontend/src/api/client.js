/**
 * Cliente HTTP central. Todo acesso à API passa por aqui, o que garante:
 *  - URL base configurável (VITE_API_URL);
 *  - envio automático do token JWT;
 *  - erros padronizados (ApiError) no formato { erro: { codigo, mensagem, detalhes } } da API;
 *  - reação centralizada a sessão expirada (401).
 */
const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
const CHAVE_TOKEN = 'mapa_do_direito_token';

export const tokenStore = {
  get: () => localStorage.getItem(CHAVE_TOKEN),
  set: (token) => localStorage.setItem(CHAVE_TOKEN, token),
  clear: () => localStorage.removeItem(CHAVE_TOKEN),
};

export class ApiError extends Error {
  constructor(mensagem, { status = 0, codigo = 'ERRO', detalhes = [] } = {}) {
    super(mensagem);
    this.name = 'ApiError';
    this.status = status;
    this.codigo = codigo;
    this.detalhes = detalhes;
  }
}

let aoNaoAutorizado = null;
export function registrarAoNaoAutorizado(callback) {
  aoNaoAutorizado = callback;
}

function montarUrl(caminho, params) {
  const url = new URL(`${BASE_URL}/api/v1${caminho}`);
  Object.entries(params ?? {}).forEach(([chave, valor]) => {
    if (valor !== undefined && valor !== null && valor !== '') url.searchParams.set(chave, String(valor));
  });
  return url;
}

export async function request(caminho, { metodo = 'GET', corpo, params, auth = true } = {}) {
  const headers = { Accept: 'application/json' };
  const token = tokenStore.get();
  if (auth && token) headers.Authorization = `Bearer ${token}`;
  if (corpo !== undefined) headers['Content-Type'] = 'application/json';

  let resposta;
  try {
    resposta = await fetch(montarUrl(caminho, params), {
      method: metodo,
      headers,
      body: corpo !== undefined ? JSON.stringify(corpo) : undefined,
    });
  } catch {
    // fetch só lança exceção quando não há resposta HTTP (API fora do ar, CORS, sem rede).
    throw new ApiError(
      `Não foi possível conectar à API (${BASE_URL}). Verifique se o servidor está em execução.`,
      { codigo: 'REDE' },
    );
  }

  if (resposta.status === 204) return null;

  let json = null;
  try {
    json = await resposta.json();
  } catch {
    // resposta sem corpo JSON
  }

  if (!resposta.ok) {
    if (resposta.status === 401 && auth && token && aoNaoAutorizado) aoNaoAutorizado();
    const erro = json?.erro;
    throw new ApiError(erro?.mensagem || `A API respondeu com o status ${resposta.status}.`, {
      status: resposta.status,
      codigo: erro?.codigo,
      detalhes: erro?.detalhes ?? [],
    });
  }
  return json;
}
