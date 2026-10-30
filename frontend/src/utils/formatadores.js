import { ROTULOS_PERFIL, SITUACOES_MORADIA } from './constantes.js';

const FORMATO_MOEDA = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

export const rotuloDe = (lista, valor) => lista.find((item) => item.valor === valor)?.rotulo ?? valor;

export const moeda = (valor) =>
  valor === null || valor === undefined || valor === '' ? '—' : FORMATO_MOEDA.format(Number(valor));

/** Data de hoje no formato AAAA-MM-DD (fuso local), usada como `max` dos campos de data. */
export const hoje = () => new Date().toLocaleDateString('sv-SE');

/** Converte "1990-03-12" em "12/03/1990" sem passar por Date (evita erro de fuso horário). */
export function dataISO(iso) {
  if (!iso) return '—';
  const [ano, mes, dia] = String(iso).slice(0, 10).split('-');
  return `${dia}/${mes}/${ano}`;
}

export function dataHora(iso) {
  if (!iso) return '—';
  const data = new Date(iso);
  return Number.isNaN(data.getTime())
    ? '—'
    : data.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
}

export function rotuloPerfil(chave) {
  if (ROTULOS_PERFIL[chave]) return ROTULOS_PERFIL[chave];
  const texto = chave.replaceAll('_', ' ');
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

export function valorPerfil(chave, valor) {
  if (valor === null || valor === undefined) return '—';
  if (typeof valor === 'boolean') return valor ? 'Sim' : 'Não';
  if (chave === 'situacao_moradia') return rotuloDe(SITUACOES_MORADIA, valor);
  if (typeof valor === 'number' && chave.includes('renda')) return moeda(valor);
  return String(valor);
}
