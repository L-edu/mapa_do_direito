import { Outlet } from 'react-router-dom';
import Navbar from './Navbar.jsx';

export default function Layout() {
  return (
    <>
      <a className="pular" href="#conteudo">
        Ir para o conteúdo
      </a>
      <Navbar />
      <main id="conteudo" className="conteudo">
        <Outlet />
      </main>
      <footer className="rodape">
        <p>
          Mapa do Direito · projeto acadêmico vinculado ao ODS 1 (Erradicação da Pobreza), meta 1.3. Nenhum CPF ou NIS é
          coletado.
        </p>
      </footer>
    </>
  );
}
