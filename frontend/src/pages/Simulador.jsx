import { useRef, useState } from 'react';
import { simulacoesApi } from '../api/servicos.js';
import { useAlertas } from '../contexts/AlertasContext.jsx';
import FormularioFamilia from '../components/familias/FormularioFamilia.jsx';
import ResultadoSimulacao from '../components/simulacao/ResultadoSimulacao.jsx';
import CabecalhoPagina from '../components/ui/CabecalhoPagina.jsx';

/** Simulação pública: nada é gravado no servidor. */
export default function Simulador() {
  const alertas = useAlertas();
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);
  const [resultado, setResultado] = useState(null);
  const areaResultado = useRef(null);

  async function simular(payload) {
    setEnviando(true);
    setErro(null);
    try {
      const dados = await simulacoesApi.simularAnonimo(payload);
      setResultado(dados);
      alertas.sucesso('Simulação concluída. Veja o resultado abaixo.');
      setTimeout(() => areaResultado.current?.scrollIntoView({ behavior: 'smooth' }), 50);
    } catch (e) {
      setResultado(null);
      setErro(e);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      <CabecalhoPagina
        titulo="Simulador de elegibilidade"
        subtitulo="Preencha os dados da família. A simulação é anônima: nada é salvo."
      />
      <FormularioFamilia comMembros textoEnviar="Simular elegibilidade" enviando={enviando} erro={erro} onSubmit={simular} />
      <div ref={areaResultado}>{resultado && <ResultadoSimulacao dados={resultado} />}</div>
    </>
  );
}
