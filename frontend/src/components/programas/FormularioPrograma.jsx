import { useState } from 'react';
import { ESFERAS } from '../../utils/constantes.js';
import Botao from '../ui/Botao.jsx';
import { ErroApi } from '../ui/Alerta.jsx';
import { CampoCheckbox, CampoSelect, CampoTextarea, CampoTexto } from '../ui/Campos.jsx';

/** Cadastro/edição de um programa. O slug só pode ser definido na criação. */
export default function FormularioPrograma({ inicial, enviando, erro, onSubmit, onCancelar }) {
  const editando = Boolean(inicial);
  const [dados, setDados] = useState(() => ({
    nome: inicial?.nome ?? '',
    slug: inicial?.slug ?? '',
    orgao: inicial?.orgao ?? '',
    esfera: inicial?.esfera ?? 'federal',
    descricao: inicial?.descricao ?? '',
    base_legal: inicial?.base_legal ?? '',
    url_oficial: inicial?.url_oficial ?? '',
    ativo: inicial?.ativo ?? true,
  }));

  const alterar = (campo) => (evento) => {
    const { type, checked, value } = evento.target;
    setDados((atual) => ({ ...atual, [campo]: type === 'checkbox' ? checked : value }));
  };

  function enviar(evento) {
    evento.preventDefault();
    const vazioParaNulo = (texto) => texto.trim() || null;
    const payload = {
      nome: dados.nome.trim(),
      orgao: vazioParaNulo(dados.orgao),
      esfera: dados.esfera,
      descricao: vazioParaNulo(dados.descricao),
      base_legal: vazioParaNulo(dados.base_legal),
      url_oficial: vazioParaNulo(dados.url_oficial),
      ativo: dados.ativo,
    };
    if (!editando) payload.slug = dados.slug.trim();
    onSubmit(payload);
  }

  return (
    <form onSubmit={enviar}>
      <fieldset>
        <legend>Dados do programa</legend>
        <div className="grade">
          <CampoTexto rotulo="Nome" obrigatorio maxLength={160} value={dados.nome} onChange={alterar('nome')} />
          <CampoTexto
            rotulo="Identificador (slug)"
            obrigatorio={!editando}
            disabled={editando}
            maxLength={80}
            pattern="[a-z0-9\-]+"
            title="Apenas letras minúsculas, números e hífen"
            placeholder="bolsa-familia"
            ajuda={editando ? 'O identificador não pode ser alterado.' : 'Letras minúsculas, números e hífen.'}
            value={dados.slug}
            onChange={alterar('slug')}
          />
          <CampoTexto rotulo="Órgão responsável" value={dados.orgao} onChange={alterar('orgao')} />
          <CampoSelect rotulo="Esfera" opcoes={ESFERAS} value={dados.esfera} onChange={alterar('esfera')} />
          <CampoTexto rotulo="Base legal" value={dados.base_legal} onChange={alterar('base_legal')} />
          <CampoTexto rotulo="Endereço oficial (URL)" type="url" value={dados.url_oficial} onChange={alterar('url_oficial')} />
        </div>
        <CampoTextarea rotulo="Descrição" value={dados.descricao} onChange={alterar('descricao')} />
        {editando && <CampoCheckbox rotulo="Programa ativo (entra nas simulações)" checked={dados.ativo} onChange={alterar('ativo')} />}
      </fieldset>
      <ErroApi erro={erro} />
      <div className="acoes">
        <Botao type="submit" carregando={enviando}>
          {editando ? 'Salvar alterações' : 'Cadastrar programa'}
        </Botao>
        <Botao variante="secundario" onClick={onCancelar}>
          Cancelar
        </Botao>
      </div>
    </form>
  );
}
