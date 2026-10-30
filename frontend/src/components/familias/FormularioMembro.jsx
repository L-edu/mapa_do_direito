import { useState } from 'react';
import Botao from '../ui/Botao.jsx';
import { ErroApi } from '../ui/Alerta.jsx';
import CamposMembro, { membroParaPayload, membroVazio } from './CamposMembro.jsx';

/** Adicionar ou editar uma pessoa de uma família já cadastrada. */
export default function FormularioMembro({ inicial, onSubmit, onCancelar, enviando, erro }) {
  const [membro, setMembro] = useState(() => inicial ?? membroVazio());

  function enviar(evento) {
    evento.preventDefault();
    onSubmit(membroParaPayload(membro));
  }

  return (
    <form className="cartao cartao--destaque" onSubmit={enviar}>
      <h3>{inicial ? 'Editar pessoa' : 'Adicionar pessoa'}</h3>
      <CamposMembro valor={membro} onChange={setMembro} />
      <ErroApi erro={erro} />
      <div className="acoes">
        <Botao type="submit" carregando={enviando}>
          {inicial ? 'Salvar alterações' : 'Adicionar'}
        </Botao>
        <Botao variante="secundario" onClick={onCancelar}>
          Cancelar
        </Botao>
      </div>
    </form>
  );
}
