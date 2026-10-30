import { Link, useParams } from 'react-router-dom';
import { simulacoesApi } from '../api/servicos.js';
import { useCarregar } from '../hooks/useCarregar.js';
import ResultadoSimulacao from '../components/simulacao/ResultadoSimulacao.jsx';
import Carregando from '../components/ui/Carregando.jsx';
import CabecalhoPagina from '../components/ui/CabecalhoPagina.jsx';
import { ErroApi } from '../components/ui/Alerta.jsx';
import { dataHora } from '../utils/formatadores.js';

/** Resultado de uma simulação gravada no histórico de uma família. */
export default function SimulacaoDetalhe() {
  const { id } = useParams();
  const { dados, carregando, erro } = useCarregar(() => simulacoesApi.obter(id), [id]);

  if (carregando) return <Carregando />;
  if (erro) return <ErroApi erro={erro} />;

  return (
    <>
      <CabecalhoPagina titulo="Resultado da simulação" subtitulo={`Realizada em ${dataHora(dados.criado_em)}`}>
        {dados.familia_id && (
          <Link to={`/familias/${dados.familia_id}`} className="btn btn--secundario">
            Voltar para a família
          </Link>
        )}
      </CabecalhoPagina>
      <ResultadoSimulacao dados={dados} />
    </>
  );
}
