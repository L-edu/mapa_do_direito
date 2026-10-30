import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { programasApi } from '../api/servicos.js';
import { useAlertas } from '../contexts/AlertasContext.jsx';
import { useCarregar } from '../hooks/useCarregar.js';
import FormularioPrograma from '../components/programas/FormularioPrograma.jsx';
import Carregando from '../components/ui/Carregando.jsx';
import CabecalhoPagina from '../components/ui/CabecalhoPagina.jsx';
import { ErroApi } from '../components/ui/Alerta.jsx';

/** Rotas /admin/programas/novo e /admin/programas/:id/editar. */
export default function ProgramaForm() {
  const { id } = useParams();
  const editando = Boolean(id);
  const navigate = useNavigate();
  const alertas = useAlertas();
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);

  const { dados, carregando, erro: erroCarga } = useCarregar(
    () => (editando ? programasApi.obter(id) : Promise.resolve(null)),
    [id],
  );

  async function salvar(payload) {
    setEnviando(true);
    setErro(null);
    try {
      const resultado = editando ? await programasApi.atualizar(id, payload) : await programasApi.criar(payload);
      alertas.sucesso(editando ? 'Programa atualizado.' : 'Programa cadastrado. Agora adicione as regras de elegibilidade.');
      navigate(`/programas/${resultado.id}`);
    } catch (e) {
      setErro(e);
    } finally {
      setEnviando(false);
    }
  }

  if (editando && carregando) return <Carregando />; // criação não depende de carga
  if (erroCarga) return <ErroApi erro={erroCarga} />;

  return (
    <>
      <CabecalhoPagina titulo={editando ? 'Editar programa' : 'Novo programa'} />
      <FormularioPrograma
        inicial={dados ?? undefined}
        enviando={enviando}
        erro={erro}
        onSubmit={salvar}
        onCancelar={() => navigate(editando ? `/programas/${id}` : '/programas')}
      />
    </>
  );
}
