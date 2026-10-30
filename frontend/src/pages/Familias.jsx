import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { familiasApi } from '../api/servicos.js';
import { useAlertas } from '../contexts/AlertasContext.jsx';
import { useCarregar } from '../hooks/useCarregar.js';
import Badge from '../components/ui/Badge.jsx';
import Botao from '../components/ui/Botao.jsx';
import Carregando from '../components/ui/Carregando.jsx';
import CabecalhoPagina from '../components/ui/CabecalhoPagina.jsx';
import EstadoVazio from '../components/ui/EstadoVazio.jsx';
import ModalConfirmacao from '../components/ui/ModalConfirmacao.jsx';
import Paginacao from '../components/ui/Paginacao.jsx';
import { ErroApi } from '../components/ui/Alerta.jsx';
import { CampoSelect, CampoTexto } from '../components/ui/Campos.jsx';
import { dataHora, moeda } from '../utils/formatadores.js';

const FILTROS_VAZIOS = { municipio: '', uf: '', possui_cadunico: '' };
const OPCOES_CADUNICO = [
  { valor: '', rotulo: 'Todas' },
  { valor: 'true', rotulo: 'Com CadÚnico' },
  { valor: 'false', rotulo: 'Sem CadÚnico' },
];

/** Listagem paginada e filtrável das famílias do usuário (admin vê todas). */
export default function Familias() {
  const alertas = useAlertas();
  const navigate = useNavigate();
  const [formFiltros, setFormFiltros] = useState(FILTROS_VAZIOS);
  const [filtros, setFiltros] = useState(FILTROS_VAZIOS);
  const [pagina, setPagina] = useState(1);
  const [excluir, setExcluir] = useState(null);
  const [excluindo, setExcluindo] = useState(false);

  const { dados, carregando, erro, recarregar } = useCarregar(
    () => familiasApi.listar({ ...filtros, pagina, tamanho: 8 }),
    [filtros, pagina],
  );

  function aplicar(evento) {
    evento.preventDefault();
    setPagina(1);
    setFiltros(formFiltros);
  }

  function limpar() {
    setFormFiltros(FILTROS_VAZIOS);
    setFiltros(FILTROS_VAZIOS);
    setPagina(1);
  }

  async function confirmarExclusao() {
    setExcluindo(true);
    try {
      await familiasApi.excluir(excluir.id);
      alertas.sucesso('Família excluída.');
      setExcluir(null);
      if (dados.itens.length === 1 && pagina > 1) setPagina(pagina - 1);
      else recarregar();
    } catch (e) {
      alertas.erro(e.message);
    } finally {
      setExcluindo(false);
    }
  }

  return (
    <>
      <CabecalhoPagina titulo="Famílias" subtitulo="Cadastre, consulte e simule a elegibilidade das famílias.">
        <Botao onClick={() => navigate('/familias/nova')}>+ Nova família</Botao>
      </CabecalhoPagina>

      <form className="filtros cartao" onSubmit={aplicar}>
        <CampoTexto rotulo="Município" value={formFiltros.municipio} onChange={(e) => setFormFiltros({ ...formFiltros, municipio: e.target.value })} />
        <CampoTexto
          rotulo="UF"
          maxLength={2}
          minLength={2}
          pattern="[A-Za-z]{2}"
          value={formFiltros.uf}
          onChange={(e) => setFormFiltros({ ...formFiltros, uf: e.target.value })}
        />
        <CampoSelect
          rotulo="CadÚnico"
          opcoes={OPCOES_CADUNICO}
          value={formFiltros.possui_cadunico}
          onChange={(e) => setFormFiltros({ ...formFiltros, possui_cadunico: e.target.value })}
        />
        <div className="acoes">
          <Botao type="submit">Filtrar</Botao>
          <Botao variante="secundario" onClick={limpar}>
            Limpar
          </Botao>
        </div>
      </form>

      <ErroApi erro={erro} />
      {carregando && !dados && <Carregando />}

      {dados && dados.itens.length === 0 && (
        <EstadoVazio titulo="Nenhuma família encontrada" texto="Cadastre a primeira família para simular a elegibilidade.">
          <Link to="/familias/nova" className="btn btn--primario">
            Cadastrar família
          </Link>
        </EstadoVazio>
      )}

      {dados && dados.itens.length > 0 && (
        <>
          <div className="tabela-wrap">
            <table className="tabela">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Município</th>
                  <th>Renda total</th>
                  <th>CadÚnico</th>
                  <th>Cadastrada em</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {dados.itens.map((familia) => (
                  <tr key={familia.id}>
                    <td>
                      <code>{familia.identificador.slice(0, 8)}</code>
                    </td>
                    <td>
                      {familia.municipio}/{familia.uf}
                    </td>
                    <td>{moeda(familia.renda_total_mensal)}</td>
                    <td>{familia.possui_cadunico ? <Badge tom="sucesso">Sim</Badge> : <Badge tom="alerta">Não</Badge>}</td>
                    <td>{dataHora(familia.criado_em)}</td>
                    <td className="acoes">
                      <Link to={`/familias/${familia.id}`}>Abrir</Link>
                      <Link to={`/familias/${familia.id}/editar`}>Editar</Link>
                      <Botao variante="link" className="texto-perigo" onClick={() => setExcluir(familia)}>
                        Excluir
                      </Botao>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Paginacao pagina={dados.pagina} totalPaginas={dados.total_paginas} total={dados.total} onMudar={setPagina} />
        </>
      )}

      <ModalConfirmacao
        aberto={Boolean(excluir)}
        titulo="Excluir família?"
        mensagem="A família, as pessoas cadastradas e todo o histórico de simulações serão removidos. Esta ação não pode ser desfeita."
        textoConfirmar="Excluir"
        perigo
        carregando={excluindo}
        onConfirmar={confirmarExclusao}
        onCancelar={() => setExcluir(null)}
      />
    </>
  );
}
