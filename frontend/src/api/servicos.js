/** Um objeto por recurso da API. Cada função corresponde a um endpoint documentado no Swagger. */
import { request } from './client.js';

export const authApi = {
  login: (email, senha) => request('/auth/login', { metodo: 'POST', corpo: { email, senha }, auth: false }),
  registrar: (dados) => request('/auth/registrar', { metodo: 'POST', corpo: dados, auth: false }),
  me: () => request('/auth/me'),
};

export const programasApi = {
  listar: (params) => request('/programas', { params }),
  obter: (id) => request(`/programas/${id}`),
  requisitos: (id) => request(`/programas/${id}/requisitos`),
  criar: (dados) => request('/programas', { metodo: 'POST', corpo: dados }),
  atualizar: (id, dados) => request(`/programas/${id}`, { metodo: 'PUT', corpo: dados }),
  desativar: (id) => request(`/programas/${id}`, { metodo: 'DELETE' }),
  adicionarRegra: (id, dados) => request(`/programas/${id}/regras`, { metodo: 'POST', corpo: dados }),
  atualizarRegra: (regraId, dados) => request(`/regras/${regraId}`, { metodo: 'PUT', corpo: dados }),
  removerRegra: (regraId) => request(`/regras/${regraId}`, { metodo: 'DELETE' }),
};

export const familiasApi = {
  listar: (params) => request('/familias', { params }),
  obter: (id) => request(`/familias/${id}`),
  criar: (dados) => request('/familias', { metodo: 'POST', corpo: dados }),
  atualizar: (id, dados) => request(`/familias/${id}`, { metodo: 'PUT', corpo: dados }),
  excluir: (id) => request(`/familias/${id}`, { metodo: 'DELETE' }),
  adicionarMembro: (id, dados) => request(`/familias/${id}/membros`, { metodo: 'POST', corpo: dados }),
  simular: (id) => request(`/familias/${id}/simulacoes`, { metodo: 'POST' }),
  historico: (id, params) => request(`/familias/${id}/simulacoes`, { params }),
};

export const membrosApi = {
  atualizar: (id, dados) => request(`/membros/${id}`, { metodo: 'PUT', corpo: dados }),
  remover: (id) => request(`/membros/${id}`, { metodo: 'DELETE' }),
};

export const simulacoesApi = {
  simularAnonimo: (dados) => request('/elegibilidade/simular', { metodo: 'POST', corpo: dados, auth: false }),
  obter: (id) => request(`/simulacoes/${id}`),
};

export const gestaoApi = {
  parametros: () => request('/parametros'),
  salvarParametro: (chave, dados) => request(`/parametros/${chave}`, { metodo: 'PUT', corpo: dados }),
  cobertura: (params) => request('/relatorios/cobertura', { params }),
  pendencias: (params) => request('/relatorios/pendencias-frequentes', { params }),
};

export const usuariosApi = {
  listar: (params) => request('/usuarios', { params }),
  criar: (dados) => request('/usuarios', { metodo: 'POST', corpo: dados }),
  atualizar: (id, dados) => request(`/usuarios/${id}`, { metodo: 'PATCH', corpo: dados }),
};
