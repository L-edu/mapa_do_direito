import { useState } from 'react';
import { gestaoApi } from '../../api/servicos.js';
import { useCarregar } from '../../hooks/useCarregar.js';
import Botao from '../../components/ui/Botao.jsx';
import Carregando from '../../components/ui/Carregando.jsx';
import CabecalhoPagina from '../../components/ui/CabecalhoPagina.jsx';
import { ErroApi } from '../../components/ui/Alerta.jsx';
import { CampoTexto } from '../../components/ui/Campos.jsx';

/** Relatórios agregados para gestores: cobertura por programa e requisitos que mais reprovam. */
export default function Painel() {
  const [form, setForm] = useState({ municipio: '', uf: '' });
  const [filtros, setFiltros] = useState(form);

  const cobertura = useCarregar(() => gestaoApi.cobertura(filtros), [filtros]);
  const pendencias = useCarregar(() => gestaoApi.pendencias({ limite: 8 }), []);

  const total = cobertura.dados?.total_familias ?? 0;
  const maxPendencias = Math.max(1, ...(pendencias.dados?.pendencias.map((p) => p.ocorrencias) ?? [1]));

  return (
    <>
      <CabecalhoPagina
        titulo="Painel de gestão"
        subtitulo="Cobertura potencial dos programas entre as famílias cadastradas (meta 1.3 do ODS 1)."
      />

      <form
        className="filtros cartao"
        onSubmit={(e) => {
          e.preventDefault();
          setFiltros(form);
        }}
      >
        <CampoTexto rotulo="Município" value={form.municipio} onChange={(e) => setForm({ ...form, municipio: e.target.value })} />
        <CampoTexto
          rotulo="UF"
          maxLength={2}
          minLength={2}
          pattern="[A-Za-z]{2}"
          value={form.uf}
          onChange={(e) => setForm({ ...form, uf: e.target.value })}
        />
        <div className="acoes">
          <Botao type="submit">Aplicar filtro</Botao>
        </div>
      </form>

      <ErroApi erro={cobertura.erro} />
      {cobertura.carregando && !cobertura.dados && <Carregando />}
      {cobertura.dados && (
        <>
          <section className="resumo">
            <div>
              <strong>{total}</strong>
              <span>família(s) analisada(s)</span>
            </div>
            <div>
              <strong>{cobertura.dados.familias_sem_nenhum_beneficio}</strong>
              <span>sem nenhum benefício elegível</span>
            </div>
          </section>

          <section className="cartao">
            <h2>Famílias elegíveis por programa</h2>
            {total === 0 && <p className="ajuda">Nenhuma família cadastrada para os filtros informados.</p>}
            {cobertura.dados.cobertura_por_programa.map((item) => (
              <div key={item.programa} className="barra-rotulada">
                <div className="barra-rotulada__texto">
                  <span>{item.programa}</span>
                  <span>
                    {item.familias_elegiveis} ({item.percentual}%)
                  </span>
                </div>
                <div className="barra" role="img" aria-label={`${item.percentual}% das famílias elegíveis a ${item.programa}`}>
                  <span style={{ width: `${item.percentual}%` }} />
                </div>
              </div>
            ))}
          </section>
        </>
      )}

      <section className="cartao">
        <h2>Requisitos que mais impedem o acesso</h2>
        <p className="ajuda">Se o campeão for o CadÚnico, o gargalo é cadastral — não de renda.</p>
        <ErroApi erro={pendencias.erro} />
        {pendencias.carregando && !pendencias.dados && <Carregando />}
        {pendencias.dados?.pendencias.map((item) => (
          <div key={item.codigo} className="barra-rotulada">
            <div className="barra-rotulada__texto">
              <span>
                <code>{item.codigo}</code> {item.descricao}
              </span>
              <span>{item.ocorrencias}</span>
            </div>
            <div className="barra barra--alerta" role="img" aria-label={`${item.ocorrencias} ocorrências`}>
              <span style={{ width: `${(item.ocorrencias / maxPendencias) * 100}%` }} />
            </div>
          </div>
        ))}
        {pendencias.dados?.pendencias.length === 0 && <p className="ajuda">Sem pendências registradas.</p>}
      </section>
    </>
  );
}
