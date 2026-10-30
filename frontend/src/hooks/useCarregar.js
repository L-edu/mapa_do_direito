import { useEffect, useState } from 'react';

/**
 * Executa uma chamada à API quando os `deps` mudam e devolve o estado da requisição.
 * `recarregar()` repete a chamada (útil depois de criar/editar/excluir).
 */
export function useCarregar(carregador, deps = []) {
  const [estado, setEstado] = useState({ dados: null, carregando: true, erro: null });
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let ativo = true;
    setEstado((atual) => ({ ...atual, carregando: true, erro: null }));
    carregador()
      .then((dados) => ativo && setEstado({ dados, carregando: false, erro: null }))
      .catch((erro) => ativo && setEstado({ dados: null, carregando: false, erro }));
    return () => {
      ativo = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tentativa]);

  return { ...estado, recarregar: () => setTentativa((n) => n + 1) };
}
