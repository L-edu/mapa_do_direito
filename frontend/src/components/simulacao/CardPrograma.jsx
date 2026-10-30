import Badge from '../ui/Badge.jsx';

function ListaRegras({ titulo, regras }) {
  return (
    <div className="regras">
      <h4>{titulo}</h4>
      <ul>
        {regras.map((regra) => (
          <li key={regra.codigo}>
            {regra.descricao}
            {regra.orientacao && <span className="regras__orientacao"> — {regra.orientacao}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}

/** Resultado de um programa: status, barra de requisitos atendidos e o que falta. */
export default function CardPrograma({ resultado }) {
  const { elegivel, percentual_atendimento: percentual, pendencias, regras_atendidas: atendidas } = resultado;

  return (
    <article className={`programa-card programa-card--${elegivel ? 'elegivel' : 'pendente'}`}>
      <h3>{resultado.programa_nome}</h3>
      <p className="programa-card__status">
        <Badge tom={elegivel ? 'sucesso' : 'alerta'}>{elegivel ? 'Elegível' : 'Ainda não elegível'}</Badge>
        <span>{percentual}% dos requisitos atendidos</span>
      </p>
      <div
        className="barra"
        role="progressbar"
        aria-valuenow={percentual}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${percentual}% dos requisitos atendidos`}
      >
        <span style={{ width: `${percentual}%` }} />
      </div>
      {pendencias.length > 0 && <ListaRegras titulo="O que falta" regras={pendencias} />}
      {atendidas.length > 0 && <ListaRegras titulo="Requisitos já atendidos" regras={atendidas} />}
    </article>
  );
}
