import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registrarAoNaoAutorizado, tokenStore } from '../api/client.js';
import { authApi } from '../api/servicos.js';
import { useAlertas } from './AlertasContext.jsx';

const AuthContext = createContext(null);

/** Guarda o usuário logado, valida o token salvo ao abrir o app e trata sessão expirada. */
export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [verificando, setVerificando] = useState(() => Boolean(tokenStore.get()));
  const alertas = useAlertas();
  const navigate = useNavigate();

  const sair = useCallback(
    (mensagem) => {
      tokenStore.clear();
      setUsuario(null);
      if (mensagem) alertas.info(mensagem);
    },
    [alertas],
  );

  useEffect(() => {
    registrarAoNaoAutorizado(() => {
      sair('Sua sessão expirou. Entre novamente.');
      navigate('/login');
    });
    return () => registrarAoNaoAutorizado(null);
  }, [sair, navigate]);

  useEffect(() => {
    if (!tokenStore.get()) return undefined;
    let ativo = true;
    authApi
      .me()
      .then((dados) => ativo && setUsuario(dados))
      .catch(() => tokenStore.clear())
      .finally(() => ativo && setVerificando(false));
    return () => {
      ativo = false;
    };
  }, []);

  const entrar = useCallback(async (email, senha) => {
    const resposta = await authApi.login(email, senha);
    tokenStore.set(resposta.access_token);
    setUsuario(resposta.usuario);
    return resposta.usuario;
  }, []);

  const valor = useMemo(
    () => ({ usuario, verificando, entrar, sair, ehAdmin: usuario?.papel === 'admin' }),
    [usuario, verificando, entrar, sair],
  );

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const contexto = useContext(AuthContext);
  if (!contexto) throw new Error('useAuth deve ser usado dentro de <AuthProvider>');
  return contexto;
}
