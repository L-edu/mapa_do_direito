import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { familiasApi } from '../api/servicos.js';
import { useAlertas } from '../contexts/AlertasContext.jsx';
import { useCarregar } from '../hooks/useCarregar.js';
import FormularioFamilia from '../components/familias/FormularioFamilia.jsx';
import Carregando from '../components/ui/Carregando.jsx';
import CabecalhoPagina from '../components/ui/CabecalhoPagina.jsx';
import { ErroApi } from '../components/ui/Alerta.jsx';

/** Rota /familias/nova (cadastro) e /familias/:id/editar (edição dos dados da família). */
export default function FamiliaForm() {
  const { id } = useParams();
  const editando = Boolean(id);
  const navigate = useNavigate();
  const alertas = useAlertas();
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);

  const { dados: familia, carregando, erro: erroCarga } = useCarregar(
    () => (editando ? familiasApi.obter(id) : Promise.resolve(null)),
    [id],
  );

  async function salvar(payload) {
    setEnviando(true);
    setErro(null);
    try {
      const resultado = editando ? await familiasApi.atualizar(id, payload) : await familiasApi.criar(payload);
      alertas.sucesso(editando ? 'Dados da família atualizados.' : 'Família cadastrada com sucesso.');
      navigate(`/familias/${resultado.id}`);
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
      <CabecalhoPagina
        titulo={editando ? 'Editar família' : 'Nova família'}
        subtitulo={editando ? 'As pessoas da família são gerenciadas na tela de detalhe.' : undefined}
      />
      <FormularioFamilia
        inicial={familia ?? undefined}
        comMembros={!editando}
        textoEnviar={editando ? 'Salvar alterações' : 'Cadastrar família'}
        enviando={enviando}
        erro={erro}
        onSubmit={salvar}
        onCancelar={() => navigate(editando ? `/familias/${id}` : '/familias')}
      />
    </>
  );
}
