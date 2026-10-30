import { useState } from 'react';
import { CAMPOS_PERFIL, OPERADORES, TIPOS_VALOR } from '../../utils/constantes.js';
import Botao from '../ui/Botao.jsx';
import { ErroApi } from '../ui/Alerta.jsx';
import { CampoCheckbox, CampoSelect, CampoTexto } from '../ui/Campos.jsx';

const opcoes = (lista) => lista.map((valor) => ({ valor, rotulo: valor }));

/** Cria ou edita uma regra declarativa: campo + operador + valor. */
export default function FormularioRegra({ inicial, enviando, erro, onSubmit, onCancelar }) {
  const [dados, setDados] = useState(() => ({
    codigo: inicial?.codigo ?? '',
    descricao: inicial?.descricao ?? '',
    campo: inicial?.campo ?? 'renda_per_capita',
    operador: inicial?.operador ?? '<=',
    valor: inicial?.valor ?? '',
    tipo_valor: inicial?.tipo_valor ?? 'numero',
    obrigatoria: inicial?.obrigatoria ?? true,
    grupo_logico: inicial?.grupo_logico ?? '',
    orientacao: inicial?.orientacao ?? '',
    ordem: String(inicial?.ordem ?? 0),
  }));

  const alterar = (campo) => (evento) => {
    const { type, checked, value } = evento.target;
    setDados((atual) => ({ ...atual, [campo]: type === 'checkbox' ? checked : value }));
  };

  function enviar(evento) {
    evento.preventDefault();
    onSubmit({
      codigo: dados.codigo.trim(),
      descricao: dados.descricao.trim(),
      campo: dados.campo.trim(),
      operador: dados.operador,
      valor: dados.valor.trim(),
      tipo_valor: dados.tipo_valor,
      obrigatoria: dados.obrigatoria,
      grupo_logico: dados.grupo_logico.trim() || null,
      orientacao: dados.orientacao.trim() || null,
      ordem: Number(dados.ordem) || 0,
    });
  }

  return (
    <form className="cartao cartao--destaque" onSubmit={enviar}>
      <h3>{inicial ? `Editar regra ${inicial.codigo}` : 'Nova regra'}</h3>
      <datalist id="campos-perfil">
        {CAMPOS_PERFIL.map((campo) => (
          <option key={campo} value={campo} />
        ))}
      </datalist>
      <div className="grade">
        <CampoTexto rotulo="Código" obrigatorio maxLength={60} placeholder="BF_RENDA" value={dados.codigo} onChange={alterar('codigo')} />
        <CampoTexto rotulo="Descrição para o cidadão" obrigatorio maxLength={255} value={dados.descricao} onChange={alterar('descricao')} />
        <CampoTexto rotulo="Campo do perfil" obrigatorio list="campos-perfil" value={dados.campo} onChange={alterar('campo')} />
        <CampoSelect rotulo="Operador" opcoes={opcoes(OPERADORES)} value={dados.operador} onChange={alterar('operador')} />
        <CampoTexto
          rotulo="Valor"
          obrigatorio
          placeholder="218  ou  0.25 * salario_minimo"
          value={dados.valor}
          onChange={alterar('valor')}
        />
        <CampoSelect rotulo="Tipo do valor" opcoes={opcoes(TIPOS_VALOR)} value={dados.tipo_valor} onChange={alterar('tipo_valor')} />
        <CampoTexto
          rotulo="Grupo lógico (OU)"
          ajuda="Regras com o mesmo grupo são combinadas em OU."
          value={dados.grupo_logico}
          onChange={alterar('grupo_logico')}
        />
        <CampoTexto rotulo="Ordem" type="number" value={dados.ordem} onChange={alterar('ordem')} />
      </div>
      <CampoTexto rotulo="Orientação quando não atendida (opcional)" value={dados.orientacao} onChange={alterar('orientacao')} />
      <CampoCheckbox rotulo="Regra obrigatória" checked={dados.obrigatoria} onChange={alterar('obrigatoria')} />
      <ErroApi erro={erro} />
      <div className="acoes">
        <Botao type="submit" carregando={enviando}>
          {inicial ? 'Salvar regra' : 'Adicionar regra'}
        </Botao>
        <Botao variante="secundario" onClick={onCancelar}>
          Cancelar
        </Botao>
      </div>
    </form>
  );
}
