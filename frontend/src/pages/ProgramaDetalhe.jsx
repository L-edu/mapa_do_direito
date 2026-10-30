import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { programasApi } from '../api/servicos.js';
import { useAlertas } from '../contexts/AlertasContext.jsx';
import { useAuth } from '../contexts/AuthContext.jsx';
import { useCarregar } from '../hooks/useCarregar.js';
import GerenciarRegras from '../components/programas/GerenciarRegras.jsx';
import Badge from '../components/ui/Badge.jsx';
import Botao from '../components/ui/Botao.jsx';
import Carregando from '../components/ui/Carregando.jsx';
import CabecalhoPagina from '../components/ui/CabecalhoPagina.jsx';
import ModalConfirmacao from '../components/ui/ModalConfirmacao.jsx';
import { ErroApi } from '../components/ui/Alerta.jsx';
import { ESFERAS } from '../utils/constantes.js';
import { rotuloDe } from '../utils/formatadores.js';

export default function ProgramaDetalhe() {
  const { id } = useParams();
  const { ehAdmin } = useAuth();
  const navigate = useNavigate();
  const alertas = useAlertas();
  const [desativar, setDesativar] = useState(false);
  const [processando, setProcessando] = useState(false);

  const programa = useCarregar(() => programasApi.obter(id), [id]);
  const requisitos = useCarregar(() => programasApi.requisitos(id), [id]);

  function recarregarTudo() {
    programa.recarregar();
    requisitos.recarregar();
  }

  async function confirmarDesativacao() {
    setProcessando(true);
    try {
      await programasApi.desativar(id);
      alertas.sucesso('Programa desativado. Ele não entra mais nas simulações.');
      setDesativar(false);
      recarregarTudo();
    } catch (e) {
      alertas.erro(e.message);
    } finally {
      setProcessando(false);
    }
  }

  if (programa.carregando && !programa.dados) return <Carregando />;
  if (programa.erro) return <ErroApi erro={programa.erro} />;

  const dados = programa.dados;

  return (
    <>
      <CabecalhoPagina titulo={dados.nome} subtitulo={dados.orgao ?? undefined}>
        {ehAdmin && (
          <>
            <Link to={`/admin/programas/${id}/editar`} className="btn btn--secundario">
              Editar
            </Link>
            {dados.ativo && (
              <Botao variante="perigo" onClick={() => setDesativar(true)}>
                Desativar
              </Botao>
            )}
          </>
        )}
      </CabecalhoPagina>

      <section className="cartao">
        <div className="selos">
          <Badge>{rotuloDe(ESFERAS, dados.esfera)}</Badge>
          <Badge tom={dados.ativo ? 'sucesso' : 'erro'}>{dados.ativo ? 'Ativo' : 'Inativo'}</Badge>
        </div>
        {dados.descricao && <p>{dados.descricao}</p>}
        <dl className="perfil">
          {dados.base_legal && (
            <div>
              <dt>Base legal</dt>
              <dd>{dados.base_legal}</dd>
            </div>
          )}
          {dados.url_oficial && (
            <div>
              <dt>Página oficial</dt>
              <dd>
                <a href={dados.url_oficial} target="_blank" rel="noreferrer">
                  {dados.url_oficial}
                </a>
              </dd>
            </div>
          )}
        </dl>
      </section>

      <section>
        <h2>Requisitos</h2>
        <ErroApi erro={requisitos.erro} />
        {requisitos.carregando && !requisitos.dados && <Carregando />}
        {requisitos.dados && (
          <ul className="lista-requisitos">
            {requisitos.dados.map((req) => (
              <li key={req.codigo}>
                <div>
                  <strong>{req.descricao}</strong>
                  <br />
                  <small>
                    <code>{req.condicao}</code>
                  </small>
                </div>
                {req.obrigatorio ? <Badge tom="sucesso">Obrigatório</Badge> : <Badge>Alternativo/opcional</Badge>}
              </li>
            ))}
            {requisitos.dados.length === 0 && <li>Este programa ainda não tem regras cadastradas.</li>}
          </ul>
        )}
        <p>
          <Link to="/simulador" className="btn btn--primario">
            Simular elegibilidade
          </Link>
        </p>
      </section>

      {ehAdmin && <GerenciarRegras programa={dados} onAlterado={recarregarTudo} />}

      <ModalConfirmacao
        aberto={desativar}
        titulo="Desativar programa?"
        mensagem="O programa deixa de ser avaliado nas simulações, mas o histórico existente é preservado. Você pode reativá-lo depois em Editar."
        textoConfirmar="Desativar"
        perigo
        carregando={processando}
        onConfirmar={confirmarDesativacao}
        onCancelar={() => setDesativar(false)}
      />
    </>
  );
}
