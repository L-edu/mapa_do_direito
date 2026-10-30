import { useEffect } from 'react';
import Botao from './Botao.jsx';

/** Janela de confirmação para ações destrutivas (excluir, desativar). */
export default function ModalConfirmacao({
  aberto,
  titulo,
  mensagem,
  textoConfirmar = 'Confirmar',
  perigo = false,
  carregando = false,
  onConfirmar,
  onCancelar,
}) {
  useEffect(() => {
    if (!aberto) return undefined;
    const aoTeclar = (evento) => evento.key === 'Escape' && onCancelar();
    document.addEventListener('keydown', aoTeclar);
    return () => document.removeEventListener('keydown', aoTeclar);
  }, [aberto, onCancelar]);

  if (!aberto) return null;

  return (
    <div className="modal__fundo" onClick={onCancelar}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-titulo"
        onClick={(evento) => evento.stopPropagation()}
      >
        <h2 id="modal-titulo">{titulo}</h2>
        <p>{mensagem}</p>
        <div className="acoes acoes--fim">
          <Botao variante="secundario" onClick={onCancelar} autoFocus>
            Cancelar
          </Botao>
          <Botao variante={perigo ? 'perigo' : 'primario'} carregando={carregando} onClick={onConfirmar}>
            {textoConfirmar}
          </Botao>
        </div>
      </div>
    </div>
  );
}
