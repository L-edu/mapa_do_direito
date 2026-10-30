import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react';

const AlertasContext = createContext(null);

/** Notificações temporárias (toasts) de sucesso, erro e informação para todo o app. */
export function AlertasProvider({ children }) {
  const [itens, setItens] = useState([]);
  const proximoId = useRef(1);

  const remover = useCallback((id) => setItens((lista) => lista.filter((item) => item.id !== id)), []);

  const adicionar = useCallback(
    (tipo, mensagem) => {
      const id = proximoId.current++;
      setItens((lista) => [...lista, { id, tipo, mensagem }]);
      setTimeout(() => remover(id), 6000);
    },
    [remover],
  );

  const api = useMemo(
    () => ({
      sucesso: (mensagem) => adicionar('sucesso', mensagem),
      erro: (mensagem) => adicionar('erro', mensagem),
      info: (mensagem) => adicionar('info', mensagem),
    }),
    [adicionar],
  );

  return (
    <AlertasContext.Provider value={api}>
      {children}
      <div className="toasts" aria-live="polite">
        {itens.map((item) => (
          <div key={item.id} className={`toast toast--${item.tipo}`} role={item.tipo === 'erro' ? 'alert' : 'status'}>
            <span>{item.mensagem}</span>
            <button type="button" onClick={() => remover(item.id)} aria-label="Fechar aviso">
              ×
            </button>
          </div>
        ))}
      </div>
    </AlertasContext.Provider>
  );
}

export function useAlertas() {
  const contexto = useContext(AlertasContext);
  if (!contexto) throw new Error('useAlertas deve ser usado dentro de <AlertasProvider>');
  return contexto;
}
