import { useState } from 'react';
import { programasApi } from '../../api/servicos.js';
import { useAlertas } from '../../contexts/AlertasContext.jsx';
import Badge from '../ui/Badge.jsx';
import Botao from '../ui/Botao.jsx';
import ModalConfirmacao from '../ui/ModalConfirmacao.jsx';
import FormularioRegra from './FormularioRegra.jsx';

/** Seção do administrador: lista, cria, edita e remove as regras de um programa. */
export default function GerenciarRegras({ programa, onAlterado }) {
  const alertas = useAlertas();
  const [formulario, setFormulario] = useState(null); // null | 'nova' | regra
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);
  const [remover, setRemover] = useState(null);

  async function salvar(payload) {
    setEnviando(true);
    setErro(null);
    try {
      if (formulario === 'nova') {
        await programasApi.adicionarRegra(programa.id, payload);
        alertas.sucesso('Regra adicionada.');
      } else {
        await programasApi.atualizarRegra(formulario.id, payload);
        alertas.sucesso('Regra atualizada.');
      }
      setFormulario(null);
      onAlterado();
    } catch (e) {
      setErro(e);
    } finally {
      setEnviando(false);
    }
  }

  async function confirmarRemocao() {
    setEnviando(true);
    try {
      await programasApi.removerRegra(remover.id);
      alertas.sucesso(`Regra ${remover.codigo} removida.`);
      setRemover(null);
      onAlterado();
    } catch (e) {
      alertas.erro(e.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section className="cartao">
      <div className="secao-titulo">
        <h2>Gerenciar regras (admin)</h2>
        {!formulario && <Botao onClick={() => { setErro(null); setFormulario('nova'); }}>+ Nova regra</Botao>}
      </div>

      {formulario && (
        <FormularioRegra
          key={formulario === 'nova' ? 'nova' : formulario.id}
          inicial={formulario === 'nova' ? undefined : formulario}
          enviando={enviando}
          erro={erro}
          onSubmit={salvar}
          onCancelar={() => setFormulario(null)}
        />
      )}

      <div className="tabela-wrap">
        <table className="tabela">
          <thead>
            <tr>
              <th>Código</th>
              <th>Condição</th>
              <th>Tipo</th>
              <th>Grupo</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {programa.regras.map((regra) => (
              <tr key={regra.id}>
                <td>{regra.codigo}</td>
                <td>
                  <code>
                    {regra.campo} {regra.operador} {regra.valor}
                  </code>
                  <br />
                  <small>{regra.descricao}</small>
                </td>
                <td>{regra.obrigatoria ? <Badge tom="sucesso">Obrigatória</Badge> : <Badge>Opcional</Badge>}</td>
                <td>{regra.grupo_logico ?? '—'}</td>
                <td className="acoes">
                  <Botao variante="link" onClick={() => { setErro(null); setFormulario(regra); }}>
                    Editar
                  </Botao>
                  <Botao variante="link" className="texto-perigo" onClick={() => setRemover(regra)}>
                    Remover
                  </Botao>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ModalConfirmacao
        aberto={Boolean(remover)}
        titulo="Remover regra?"
        mensagem={`A regra ${remover?.codigo ?? ''} deixará de ser avaliada nas próximas simulações.`}
        textoConfirmar="Remover"
        perigo
        carregando={enviando}
        onConfirmar={confirmarRemocao}
        onCancelar={() => setRemover(null)}
      />
    </section>
  );
}
