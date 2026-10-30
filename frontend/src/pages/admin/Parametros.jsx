import { useState } from 'react';
import { gestaoApi } from '../../api/servicos.js';
import { useAlertas } from '../../contexts/AlertasContext.jsx';
import { useCarregar } from '../../hooks/useCarregar.js';
import Botao from '../../components/ui/Botao.jsx';
import Carregando from '../../components/ui/Carregando.jsx';
import CabecalhoPagina from '../../components/ui/CabecalhoPagina.jsx';
import Alerta, { ErroApi } from '../../components/ui/Alerta.jsx';
import { CampoTexto } from '../../components/ui/Campos.jsx';
import { dataHora, dataISO } from '../../utils/formatadores.js';

/** Formulário de um parâmetro (edição ou criação). */
function FormularioParametro({ inicial, enviando, erro, onSubmit, onCancelar }) {
  const [dados, setDados] = useState(() => ({
    chave: inicial?.chave ?? '',
    valor: String(inicial?.valor ?? ''),
    descricao: inicial?.descricao ?? '',
    fonte: inicial?.fonte ?? '',
    vigencia_inicio: inicial?.vigencia_inicio ?? '',
  }));
  const alterar = (campo) => (e) => setDados({ ...dados, [campo]: e.target.value });

  function enviar(evento) {
    evento.preventDefault();
    onSubmit(dados.chave.trim(), {
      valor: Number(dados.valor),
      descricao: dados.descricao.trim() || null,
      fonte: dados.fonte.trim() || null,
      vigencia_inicio: dados.vigencia_inicio || null,
    });
  }

  return (
    <form className="cartao cartao--destaque" onSubmit={enviar}>
      <h3>{inicial ? `Editar ${inicial.chave}` : 'Novo parâmetro'}</h3>
      <div className="grade">
        <CampoTexto
          rotulo="Chave"
          obrigatorio
          disabled={Boolean(inicial)}
          pattern="[a-z0-9_]+"
          title="Letras minúsculas, números e sublinhado"
          placeholder="salario_minimo"
          value={dados.chave}
          onChange={alterar('chave')}
        />
        <CampoTexto rotulo="Valor" type="number" step="0.01" min="0.01" obrigatorio value={dados.valor} onChange={alterar('valor')} />
        <CampoTexto rotulo="Descrição" value={dados.descricao} onChange={alterar('descricao')} />
        <CampoTexto rotulo="Fonte oficial" value={dados.fonte} onChange={alterar('fonte')} />
        <CampoTexto rotulo="Vigência a partir de" type="date" value={dados.vigencia_inicio} onChange={alterar('vigencia_inicio')} />
      </div>
      <ErroApi erro={erro} />
      <div className="acoes">
        <Botao type="submit" carregando={enviando}>
          Salvar
        </Botao>
        <Botao variante="secundario" onClick={onCancelar}>
          Cancelar
        </Botao>
      </div>
    </form>
  );
}

/** Valores de referência usados pelas regras (salário mínimo, linha de pobreza...). */
export default function Parametros() {
  const alertas = useAlertas();
  const { dados, carregando, erro, recarregar } = useCarregar(() => gestaoApi.parametros(), []);
  const [formulario, setFormulario] = useState(null); // null | 'novo' | parametro
  const [enviando, setEnviando] = useState(false);
  const [erroForm, setErroForm] = useState(null);

  async function salvar(chave, payload) {
    setEnviando(true);
    setErroForm(null);
    try {
      await gestaoApi.salvarParametro(chave, payload);
      alertas.sucesso(`Parâmetro ${chave} salvo. As regras que dependem dele já usam o novo valor.`);
      setFormulario(null);
      recarregar();
    } catch (e) {
      setErroForm(e);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      <CabecalhoPagina titulo="Parâmetros" subtitulo="Valores de referência usados pelas regras de elegibilidade.">
        {!formulario && <Botao onClick={() => { setErroForm(null); setFormulario('novo'); }}>+ Novo parâmetro</Botao>}
      </CabecalhoPagina>

      <Alerta tipo="info">
        Regras do tipo <code>parametro</code> (ex.: <code>0.25 * salario_minimo</code>) usam estes valores. Ao reajustar o
        salário mínimo aqui, todas as regras derivadas passam a usar o novo valor — sem alterar código.
      </Alerta>

      {formulario && (
        <FormularioParametro
          key={formulario === 'novo' ? 'novo' : formulario.chave}
          inicial={formulario === 'novo' ? undefined : formulario}
          enviando={enviando}
          erro={erroForm}
          onSubmit={salvar}
          onCancelar={() => setFormulario(null)}
        />
      )}

      <ErroApi erro={erro} />
      {carregando && !dados && <Carregando />}
      {dados && (
        <div className="tabela-wrap">
          <table className="tabela">
            <thead>
              <tr>
                <th>Chave</th>
                <th>Valor</th>
                <th>Descrição e fonte</th>
                <th>Vigência</th>
                <th>Atualizado</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {dados.map((parametro) => (
                <tr key={parametro.chave}>
                  <td>
                    <code>{parametro.chave}</code>
                  </td>
                  <td>{parametro.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
                  <td>
                    {parametro.descricao}
                    <br />
                    <small>{parametro.fonte}</small>
                  </td>
                  <td>{dataISO(parametro.vigencia_inicio)}</td>
                  <td>{dataHora(parametro.atualizado_em)}</td>
                  <td className="acoes">
                    <Botao variante="link" onClick={() => { setErroForm(null); setFormulario(parametro); }}>
                      Editar
                    </Botao>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
