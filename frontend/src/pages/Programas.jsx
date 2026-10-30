import { useState } from 'react';
import { Link } from 'react-router-dom';
import { programasApi } from '../api/servicos.js';
import { useAuth } from '../contexts/AuthContext.jsx';
import { useCarregar } from '../hooks/useCarregar.js';
import Badge from '../components/ui/Badge.jsx';
import Botao from '../components/ui/Botao.jsx';
import Carregando from '../components/ui/Carregando.jsx';
import CabecalhoPagina from '../components/ui/CabecalhoPagina.jsx';
import EstadoVazio from '../components/ui/EstadoVazio.jsx';
import Paginacao from '../components/ui/Paginacao.jsx';
import { ErroApi } from '../components/ui/Alerta.jsx';
import { CampoSelect, CampoTexto } from '../components/ui/Campos.jsx';
import { ESFERAS } from '../utils/constantes.js';
import { rotuloDe } from '../utils/formatadores.js';

const OPCOES_ESFERA = [{ valor: '', rotulo: 'Todas' }, ...ESFERAS];
const OPCOES_SITUACAO = [
  { valor: '', rotulo: 'Todos' },
  { valor: 'true', rotulo: 'Ativos' },
  { valor: 'false', rotulo: 'Inativos' },
];

/** Catálogo de programas. Público vê só os ativos; o admin vê todos e pode cadastrar. */
export default function Programas() {
  const { ehAdmin } = useAuth();
  const [form, setForm] = useState({ busca: '', esfera: '', ativo: '' });
  const [filtros, setFiltros] = useState(form);
  const [pagina, setPagina] = useState(1);

  const { dados, carregando, erro } = useCarregar(
    () => programasApi.listar({ ...filtros, ativo: ehAdmin ? filtros.ativo : 'true', pagina, tamanho: 9 }),
    [filtros, pagina, ehAdmin],
  );

  function aplicar(evento) {
    evento.preventDefault();
    setPagina(1);
    setFiltros(form);
  }

  return (
    <>
      <CabecalhoPagina titulo="Programas sociais" subtitulo="Catálogo dos programas avaliados pelo simulador e seus requisitos.">
        {ehAdmin && (
          <Link to="/admin/programas/novo" className="btn btn--primario">
            + Novo programa
          </Link>
        )}
      </CabecalhoPagina>

      <form className="filtros cartao" onSubmit={aplicar}>
        <CampoTexto rotulo="Buscar" placeholder="Nome ou órgão" value={form.busca} onChange={(e) => setForm({ ...form, busca: e.target.value })} />
        <CampoSelect rotulo="Esfera" opcoes={OPCOES_ESFERA} value={form.esfera} onChange={(e) => setForm({ ...form, esfera: e.target.value })} />
        {ehAdmin && (
          <CampoSelect rotulo="Situação" opcoes={OPCOES_SITUACAO} value={form.ativo} onChange={(e) => setForm({ ...form, ativo: e.target.value })} />
        )}
        <div className="acoes">
          <Botao type="submit">Filtrar</Botao>
        </div>
      </form>

      <ErroApi erro={erro} />
      {carregando && !dados && <Carregando />}
      {dados && dados.itens.length === 0 && <EstadoVazio titulo="Nenhum programa encontrado" texto="Ajuste os filtros e tente novamente." />}
      {dados && dados.itens.length > 0 && (
        <>
          <div className="programas-grid">
            {dados.itens.map((programa) => (
              <Link key={programa.id} to={`/programas/${programa.id}`} className="programa-item">
                <h3>{programa.nome}</h3>
                <p>{programa.orgao ?? 'Órgão não informado'}</p>
                <div className="selos">
                  <Badge>{rotuloDe(ESFERAS, programa.esfera)}</Badge>
                  {!programa.ativo && <Badge tom="erro">Inativo</Badge>}
                </div>
              </Link>
            ))}
          </div>
          <Paginacao pagina={dados.pagina} totalPaginas={dados.total_paginas} total={dados.total} onMudar={setPagina} />
        </>
      )}
    </>
  );
}
