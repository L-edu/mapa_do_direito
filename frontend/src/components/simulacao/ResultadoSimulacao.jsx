import CardPrograma from './CardPrograma.jsx';
import PerfilCalculado from './PerfilCalculado.jsx';

/** Resposta completa de uma simulação (anônima ou de família cadastrada). */
export default function ResultadoSimulacao({ dados }) {
  const { resumo, resultados, perfil_calculado: perfil } = dados;

  return (
    <div className="resultado" aria-live="polite">
      <section className="resumo">
        <div>
          <strong>{resumo.elegivel_em}</strong>
          <span>programa(s) elegível(is)</span>
        </div>
        <div>
          <strong>{resumo.quase_elegivel_em}</strong>
          <span>quase elegível(is) (70% ou mais)</span>
        </div>
        <div>
          <strong>{resumo.programas_avaliados}</strong>
          <span>programa(s) avaliado(s)</span>
        </div>
      </section>

      <section>
        <h2>Programas avaliados</h2>
        {resultados.map((resultado) => (
          <CardPrograma key={resultado.programa_id} resultado={resultado} />
        ))}
      </section>

      <details className="cartao">
        <summary>Perfil calculado da família</summary>
        <PerfilCalculado perfil={perfil} />
      </details>
    </div>
  );
}
