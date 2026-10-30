import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext.jsx';
import { useAlertas } from '../../contexts/AlertasContext.jsx';
import { PAPEIS } from '../../utils/constantes.js';
import { rotuloDe } from '../../utils/formatadores.js';
import Botao from '../ui/Botao.jsx';

const classeLink = ({ isActive }) => (isActive ? 'ativo' : undefined);

export default function Navbar() {
  const { usuario, ehAdmin, sair } = useAuth();
  const alertas = useAlertas();
  const navigate = useNavigate();

  function aoSair() {
    sair();
    alertas.info('Você saiu da sua conta.');
    navigate('/');
  }

  return (
    <header className="topo">
      <div className="topo__interno">
        <Link to="/" className="topo__marca">
          Mapa do Direito
        </Link>
        <nav className="topo__nav" aria-label="Principal">
          <NavLink to="/" end className={classeLink}>
            Início
          </NavLink>
          <NavLink to="/simulador" className={classeLink}>
            Simulador
          </NavLink>
          <NavLink to="/programas" className={classeLink}>
            Programas
          </NavLink>
          {usuario && (
            <NavLink to="/familias" className={classeLink}>
              Famílias
            </NavLink>
          )}
          {ehAdmin && (
            <>
              <NavLink to="/admin" end className={classeLink}>
                Painel
              </NavLink>
              <NavLink to="/admin/parametros" className={classeLink}>
                Parâmetros
              </NavLink>
              <NavLink to="/admin/usuarios" className={classeLink}>
                Usuários
              </NavLink>
            </>
          )}
        </nav>
        <div className="topo__usuario">
          {usuario ? (
            <>
              <span>
                {usuario.nome} <small>({rotuloDe(PAPEIS, usuario.papel)})</small>
              </span>
              <Botao variante="secundario" onClick={aoSair}>
                Sair
              </Botao>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn--secundario">
                Entrar
              </Link>
              <Link to="/registro" className="btn btn--primario">
                Criar conta
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
