import { useState } from 'react';
import { SITUACOES_MORADIA } from '../../utils/constantes.js';
import Botao from '../ui/Botao.jsx';
import { ErroApi } from '../ui/Alerta.jsx';
import { CampoCheckbox, CampoSelect, CampoTexto } from '../ui/Campos.jsx';
import CamposMembro, { membroParaPayload, membroVazio } from './CamposMembro.jsx';

/**
 * Formulário da família, usado em três telas:
 *  - simulador público e cadastro (comMembros): envia a família com a lista de pessoas;
 *  - edição (sem comMembros): envia só os dados da família (pessoas são geridas na tela de detalhe).
 */
export default function FormularioFamilia({
  inicial,
  comMembros = false,
  textoEnviar = 'Salvar',
  enviando = false,
  erro,
  onSubmit,
  onCancelar,
}) {
  const [dados, setDados] = useState(() => ({
    municipio: inicial?.municipio ?? '',
    uf: inicial?.uf ?? '',
    renda_total_mensal: String(inicial?.renda_total_mensal ?? 0),
    situacao_moradia: inicial?.situacao_moradia ?? 'alugada',
    possui_cadunico: inicial?.possui_cadunico ?? false,
  }));
  const [membros, setMembros] = useState(() => (comMembros ? [membroVazio()] : []));

  const alterar = (campo) => (evento) => {
    const { type, checked, value } = evento.target;
    setDados((atual) => ({ ...atual, [campo]: type === 'checkbox' ? checked : value }));
  };

  const atualizarMembro = (id, novo) => setMembros((lista) => lista.map((m) => (m._id === id ? novo : m)));
  const removerMembro = (id) => setMembros((lista) => lista.filter((m) => m._id !== id));

  function enviar(evento) {
    evento.preventDefault();
    const payload = {
      municipio: dados.municipio.trim(),
      uf: dados.uf.trim().toUpperCase(),
      renda_total_mensal: Number(dados.renda_total_mensal) || 0,
      situacao_moradia: dados.situacao_moradia,
      possui_cadunico: dados.possui_cadunico,
    };
    if (comMembros) payload.membros = membros.map(membroParaPayload);
    onSubmit(payload);
  }

  return (
    <form onSubmit={enviar}>
      <fieldset>
        <legend>Dados da família</legend>
        <div className="grade">
          <CampoTexto
            rotulo="Município"
            obrigatorio
            maxLength={120}
            placeholder="Salvador"
            value={dados.municipio}
            onChange={alterar('municipio')}
          />
          <CampoTexto
            rotulo="UF"
            obrigatorio
            minLength={2}
            maxLength={2}
            pattern="[A-Za-z]{2}"
            title="Duas letras, por exemplo: BA"
            placeholder="BA"
            value={dados.uf}
            onChange={alterar('uf')}
          />
          <CampoTexto
            rotulo="Renda total mensal da família (R$)"
            type="number"
            min="0"
            step="0.01"
            value={dados.renda_total_mensal}
            onChange={alterar('renda_total_mensal')}
          />
          <CampoSelect
            rotulo="Situação de moradia"
            opcoes={SITUACOES_MORADIA}
            value={dados.situacao_moradia}
            onChange={alterar('situacao_moradia')}
          />
        </div>
        <CampoCheckbox
          rotulo="A família está inscrita no Cadastro Único (CadÚnico)"
          checked={dados.possui_cadunico}
          onChange={alterar('possui_cadunico')}
        />
      </fieldset>

      {comMembros && (
        <fieldset>
          <legend>Pessoas da família</legend>
          <p className="ajuda">Informe ao menos uma pessoa. Use apenas o primeiro nome: não coletamos CPF nem NIS.</p>
          {membros.map((membro, indice) => (
            <fieldset key={membro._id} className="membro">
              <legend>Pessoa {indice + 1}</legend>
              <CamposMembro valor={membro} onChange={(novo) => atualizarMembro(membro._id, novo)} />
              {membros.length > 1 && (
                <Botao variante="link" onClick={() => removerMembro(membro._id)}>
                  Remover esta pessoa
                </Botao>
              )}
            </fieldset>
          ))}
          <Botao variante="secundario" onClick={() => setMembros((lista) => [...lista, membroVazio()])}>
            + Adicionar pessoa
          </Botao>
        </fieldset>
      )}

      <ErroApi erro={erro} />
      <div className="acoes">
        <Botao type="submit" carregando={enviando}>
          {textoEnviar}
        </Botao>
        {onCancelar && (
          <Botao variante="secundario" onClick={onCancelar}>
            Cancelar
          </Botao>
        )}
      </div>
    </form>
  );
}
