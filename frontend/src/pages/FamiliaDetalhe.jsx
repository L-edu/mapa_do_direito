import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { familiasApi, membrosApi } from '../api/servicos.js';
import { useAlertas } from '../contexts/AlertasContext.jsx';
import { useCarregar } from '../hooks/useCarregar.js';
import FormularioMembro from '../components/familias/FormularioMembro.jsx';
import { membroDaApi } from '../components/familias/CamposMembro.jsx';
import TabelaMembros from '../components/familias/TabelaMembros.jsx';
import PerfilCalculado from '../components/simulacao/PerfilCalculado.jsx';
import Badge from '../components/ui/Badge.jsx';
import Botao from '../components/ui/Botao.jsx';
import Carregando from '../components/ui/Carregando.jsx';
import CabecalhoPagina from '../components/ui/CabecalhoPagina.jsx';
import EstadoVazio from '../components/ui/EstadoVazio.jsx';
import ModalConfirmacao from '../components/ui/ModalConfirmacao.jsx';
import Paginacao from '../components/ui/Paginacao.jsx';
import { ErroApi } from '../components/ui/Alerta.jsx';
import { SITUACOES_MORADIA } from '../utils/constantes.js';
import { dataHora, moeda, rotuloDe } from '../utils/formatadores.js';

/** Detalhe da família: dados, pessoas (CRUD), simulação e histórico. */
export default function FamiliaDetalhe() {
  const { id } = useParams();
  const navigate = useNavigate();
  const alertas = useAlertas();
  const [paginaHistorico, setPaginaHistorico] = useState(1);
  const [formulario, setFormulario] = useState(null); // null | 'novo' | membro
  const [salvandoMembro, setSalvandoMembro] = useState(false);
  const [erroMembro, setErroMembro] = useState(null);
  const [excluirMembro, setExcluirMembro] = useState(null);
  const [excluirFamilia, setExcluirFamilia] = useState(false);
  const [processando, setProcessando] = useState(false);
  const [simulando, setSimulando] = useState(false);

  const familia = useCarregar(() => familiasApi.obter(id), [id]);
  const historico = useCarregar(() => familiasApi.historico(id, { pagina: paginaHistorico, tamanho: 5 }), [id, paginaHistorico]);

  async function salvarMembro(payload) {
    setSalvandoMembro(true);
    setErroMembro(null);
    try {
      if (formulario === 'novo') {
        await familiasApi.adicionarMembro(id, payload);
        alertas.sucesso('Pessoa adicionada.');
      } else {
        await membrosApi.atualizar(formulario.id, payload);
        alertas.sucesso('Pessoa atualizada.');
      }
      setFormulario(null);
      familia.recarregar();
    } catch (e) {
      setErroMembro(e);
    } finally {
      setSalvandoMembro(false);
    }
  }

  async function confirmarRemocaoMembro() {
    setProcessando(true);
    try {
      await membrosApi.remover(excluirMembro.id);
      alertas.sucesso(`${excluirMembro.nome} foi removido(a) da família.`);
      setExcluirMembro(null);
      familia.recarregar();
    } catch (e) {
      alertas.erro(e.message);
    } finally {
      setProcessando(false);
    }
  }

  async function confirmarExclusaoFamilia() {
    setProcessando(true);
    try {
      await familiasApi.excluir(id);
      alertas.sucesso('Família excluída.');
      navigate('/familias');
    } catch (e) {
      alertas.erro(e.message);
      setProcessando(false);
    }
  }

  async function simular() {
    setSimulando(true);
    try {
      const resultado = await familiasApi.simular(id);
      alertas.sucesso('Simulação registrada no histórico.');
      navigate(`/simulacoes/${resultado.simulacao_id}`);
    } catch (e) {
      alertas.erro(e.message);
      setSimulando(false);
    }
  }

  if (familia.carregando && !familia.dados) return <Carregando />;
  if (familia.erro) return <ErroApi erro={familia.erro} />;

  const dados = familia.dados;
  const semMembros = dados.membros.length === 0;

  return (
    <>
      <CabecalhoPagina titulo={`Família ${dados.identificador.slice(0, 8)}`} subtitulo={`${dados.municipio}/${dados.uf}`}>
        <Botao onClick={simular} carregando={simulando} disabled={semMembros}>
          Simular elegibilidade
        </Botao>
        <Link to={`/familias/${id}/editar`} className="btn btn--secundario">
          Editar dados
        </Link>
        <Botao variante="perigo" onClick={() => setExcluirFamilia(true)}>
          Excluir
        </Botao>
      </CabecalhoPagina>
      {semMembros && <p className="ajuda">Adicione ao menos uma pessoa para poder simular a elegibilidade.</p>}

      <section className="cartao">
        <dl className="perfil">
          <div>
            <dt>Renda total mensal</dt>
            <dd>{moeda(dados.renda_total_mensal)}</dd>
          </div>
          <div>
            <dt>Situação de moradia</dt>
            <dd>{rotuloDe(SITUACOES_MORADIA, dados.situacao_moradia)}</dd>
          </div>
          <div>
            <dt>Cadastro Único</dt>
            <dd>{dados.possui_cadunico ? <Badge tom="sucesso">Inscrita</Badge> : <Badge tom="alerta">Não inscrita</Badge>}</dd>
          </div>
          <div>
            <dt>Código completo</dt>
            <dd>
              <code>{dados.identificador}</code>
            </dd>
          </div>
        </dl>
        <details>
          <summary>Perfil calculado pela API</summary>
          <PerfilCalculado perfil={dados.perfil_calculado} />
        </details>
      </section>

      <section>
        <div className="secao-titulo">
          <h2>Pessoas da família</h2>
          {!formulario && <Botao onClick={() => { setErroMembro(null); setFormulario('novo'); }}>+ Adicionar pessoa</Botao>}
        </div>
        {formulario && (
          <FormularioMembro
            key={formulario === 'novo' ? 'novo' : formulario.id}
            inicial={formulario === 'novo' ? undefined : membroDaApi(formulario)}
            enviando={salvandoMembro}
            erro={erroMembro}
            onSubmit={salvarMembro}
            onCancelar={() => setFormulario(null)}
          />
        )}
        {semMembros ? (
          <EstadoVazio titulo="Nenhuma pessoa cadastrada" texto="Use o botão acima para adicionar as pessoas desta família." />
        ) : (
          <TabelaMembros
            membros={dados.membros}
            onEditar={(m) => { setErroMembro(null); setFormulario(m); }}
            onExcluir={setExcluirMembro}
          />
        )}
      </section>

      <section>
        <h2>Histórico de simulações</h2>
        <ErroApi erro={historico.erro} />
        {historico.dados && historico.dados.itens.length === 0 && (
          <p className="ajuda">Nenhuma simulação registrada ainda.</p>
        )}
        {historico.dados && historico.dados.itens.length > 0 && (
          <>
            <div className="tabela-wrap">
              <table className="tabela">
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Programas elegíveis</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {historico.dados.itens.map((item) => (
                    <tr key={item.id}>
                      <td>{dataHora(item.criado_em)}</td>
                      <td>{item.total_elegiveis}</td>
                      <td className="acoes">
                        <Link to={`/simulacoes/${item.id}`}>Ver resultado</Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Paginacao
              pagina={historico.dados.pagina}
              totalPaginas={historico.dados.total_paginas}
              total={historico.dados.total}
              onMudar={setPaginaHistorico}
            />
          </>
        )}
      </section>

      <ModalConfirmacao
        aberto={Boolean(excluirMembro)}
        titulo="Remover pessoa?"
        mensagem={`${excluirMembro?.nome ?? ''} será removido(a) da família. Isso altera o resultado das próximas simulações.`}
        textoConfirmar="Remover"
        perigo
        carregando={processando}
        onConfirmar={confirmarRemocaoMembro}
        onCancelar={() => setExcluirMembro(null)}
      />
      <ModalConfirmacao
        aberto={excluirFamilia}
        titulo="Excluir família?"
        mensagem="A família, as pessoas e todo o histórico de simulações serão removidos. Esta ação não pode ser desfeita."
        textoConfirmar="Excluir"
        perigo
        carregando={processando}
        onConfirmar={confirmarExclusaoFamilia}
        onCancelar={() => setExcluirFamilia(false)}
      />
    </>
  );
}
