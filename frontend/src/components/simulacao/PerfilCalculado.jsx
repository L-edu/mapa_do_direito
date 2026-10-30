import { rotuloPerfil, valorPerfil } from '../../utils/formatadores.js';

/** O perfil calculado vem da API como objeto livre; renderizamos qualquer chave recebida. */
export default function PerfilCalculado({ perfil }) {
  return (
    <dl className="perfil">
      {Object.entries(perfil).map(([chave, valor]) => (
        <div key={chave}>
          <dt>{rotuloPerfil(chave)}</dt>
          <dd>{valorPerfil(chave, valor)}</dd>
        </div>
      ))}
    </dl>
  );
}
