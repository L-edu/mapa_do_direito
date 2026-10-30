import { useRef } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext.jsx';
import Carregando from '../ui/Carregando.jsx';
import EstadoVazio from '../ui/EstadoVazio.jsx';

/** Exige login (e, opcionalmente, um dos papéis informados) para renderizar as rotas filhas. */
export default function RotaProtegida({ papeis }) {
  const { usuario, verificando } = useAuth();
  const local = useLocation();
  // Se o usuário estava logado enquanto esta página estava aberta e a sessão caiu, foi um logout:
  // vai para o início, sem guardar "de onde veio" (senão o próximo login, de qualquer pessoa,
  // pularia direto para a página da sessão anterior).
  const estavaLogado = useRef(false);
  if (usuario) estavaLogado.current = true;

  if (verificando) return <Carregando texto="Verificando sessão…" />;
  if (!usuario) {
    if (estavaLogado.current) return <Navigate to="/" replace />;
    return <Navigate to="/login" replace state={{ de: `${local.pathname}${local.search}` }} />;
  }
  if (papeis && !papeis.includes(usuario.papel)) {
    return <EstadoVazio titulo="Acesso restrito" texto="Seu perfil não tem permissão para acessar esta página." />;
  }
  return <Outlet />;
}
