export const SITUACOES_MORADIA = [
  { valor: 'propria', rotulo: 'Própria' },
  { valor: 'alugada', rotulo: 'Alugada' },
  { valor: 'cedida', rotulo: 'Cedida' },
  { valor: 'situacao_rua', rotulo: 'Situação de rua' },
];

export const PARENTESCOS = [
  { valor: 'responsavel', rotulo: 'Responsável' },
  { valor: 'conjuge', rotulo: 'Cônjuge' },
  { valor: 'filho', rotulo: 'Filho(a)' },
  { valor: 'pai', rotulo: 'Pai' },
  { valor: 'mae', rotulo: 'Mãe' },
  { valor: 'outro', rotulo: 'Outro' },
];

export const ESFERAS = [
  { valor: 'federal', rotulo: 'Federal' },
  { valor: 'estadual', rotulo: 'Estadual' },
  { valor: 'municipal', rotulo: 'Municipal' },
];

export const PAPEIS = [
  { valor: 'cidadao', rotulo: 'Cidadão' },
  { valor: 'assistente_social', rotulo: 'Assistente social' },
  { valor: 'admin', rotulo: 'Administrador' },
];

export const OPERADORES = ['==', '!=', '<', '<=', '>', '>=', 'in', 'entre'];
export const TIPOS_VALOR = ['numero', 'booleano', 'texto', 'lista', 'intervalo', 'parametro'];

/** Rótulos do perfil calculado devolvido pela API (campo de estrutura livre). */
export const ROTULOS_PERFIL = {
  municipio: 'Município',
  uf: 'UF',
  num_membros: 'Pessoas na família',
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

/** Campos disponíveis para escrever regras (sugestões no formulário de regra). */
export const CAMPOS_PERFIL = Object.keys(ROTULOS_PERFIL);
