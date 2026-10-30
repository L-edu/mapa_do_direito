import { Link } from 'react-router-dom';
import EstadoVazio from '../components/ui/EstadoVazio.jsx';

export default function NaoEncontrado() {
  return (
    <EstadoVazio titulo="Página não encontrada" texto="O endereço acessado não existe.">
      <Link to="/" className="btn btn--primario">
        Voltar ao início
      </Link>
    </EstadoVazio>
  );
}
