import { useState } from 'react';
import { usuariosApi } from '../../api/servicos.js';
import { useAlertas } from '../../contexts/AlertasContext.jsx';
import { useAuth } from '../../contexts/AuthContext.jsx';
import { useCarregar } from '../../hooks/useCarregar.js';
import Badge from '../../components/ui/Badge.jsx';
import Botao from '../../components/ui/Botao.jsx';
import Carregando from '../../components/ui/Carregando.jsx';
import CabecalhoPagina from '../../components/ui/CabecalhoPagina.jsx';
import Paginacao from '../../components/ui/Paginacao.jsx';
import { ErroApi } from '../../components/ui/Alerta.jsx';
import { CampoSelect, CampoTexto } from '../../components/ui/Campos.jsx';
import { PAPEIS } from '../../utils/constantes.js';
import { dataHora } from '../../utils/formatadores.js';

const OPCOES_FILTRO_PAPEL = [{ valor: '', rotulo: 'Todos os papéis' }, ...PAPEIS];

function FormularioUsuario({ enviando, erro, onSubmit, onCancelar }) {
  const [dados, setDados] = useState({ nome: '', email: '', senha: '', papel: 'assistente_social' });
  const alterar = (campo) => (e) => setDados({ ...dados, [campo]: e.target.value });

  return (
    <form
      className="cartao cartao--destaque"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ ...dados, nome: dados.nome.trim(), email: dados.email.trim() });
      }}
    >
      <h3>Nova conta</h3>
      <div className="grade">
        <CampoTexto rotulo="Nome" obrigatorio minLength={2} value={dados.nome} onChange={alterar('nome')} />
        <CampoTexto rotulo="E-mail" type="email" obrigatorio value={dados.email} onChange={alterar('email')} />
        <CampoTexto
          rotulo="Senha inicial"
          type="password"
          obrigatorio
          minLength={8}
          autoComplete="new-password"
          value={dados.senha}
          onChange={alterar('senha')}
        />
        <CampoSelect rotulo="Papel" opcoes={PAPEIS} value={dados.papel} onChange={alterar('papel')} />
      </div>
      <ErroApi erro={erro} />
      <div className="acoes">
        <Botao type="submit" carregando={enviando}>
          Criar conta
        </Botao>
        <Botao variante="secundario" onClick={onCancelar}>
          Cancelar
        </Botao>
      </div>
    </form>
  );
}

/** Gestão de contas: criar, trocar papel (PATCH) e ativar/desativar. */
export default function Usuarios() {
  const alertas = useAlertas();
  const { usuario: eu } = useAuth();
  const [form, setForm] = useState({ busca: '', papel: '' });
  const [filtros, setFiltros] = useState(form);
  const [pagina, setPagina] = useState(1);
  const [criando, setCriando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erroForm, setErroForm] = useState(null);
  const [alterandoId, setAlterandoId] = useState(null);

  const { dados, carregando, erro, recarregar } = useCarregar(
    () => usuariosApi.listar({ ...filtros, pagina, tamanho: 10 }),
    [filtros, pagina],
  );

  async function criar(payload) {
    setEnviando(true);
    setErroForm(null);
    try {
      await usuariosApi.criar(payload);
      alertas.sucesso('Conta criada.');
      setCriando(false);
      recarregar();
    } catch (e) {
      setErroForm(e);
    } finally {
      setEnviando(false);
    }
  }

  async function alterar(usuario, mudanca, mensagem) {
    setAlterandoId(usuario.id);
    try {
      await usuariosApi.atualizar(usuario.id, mudanca);
      alertas.sucesso(mensagem);
      recarregar();
    } catch (e) {
      alertas.erro(e.message);
    } finally {
      setAlterandoId(null);
    }
  }

  return (
    <>
      <CabecalhoPagina titulo="Usuários" subtitulo="Crie contas de assistentes sociais e administradores e gerencie permissões.">
        {!criando && <Botao onClick={() => { setErroForm(null); setCriando(true); }}>+ Nova conta</Botao>}
      </CabecalhoPagina>

      {criando && <FormularioUsuario enviando={enviando} erro={erroForm} onSubmit={criar} onCancelar={() => setCriando(false)} />}

      <form
        className="filtros cartao"
        onSubmit={(e) => {
          e.preventDefault();
          setPagina(1);
          setFiltros(form);
        }}
      >
        <CampoTexto rotulo="Buscar" placeholder="Nome ou e-mail" value={form.busca} onChange={(e) => setForm({ ...form, busca: e.target.value })} />
        <CampoSelect rotulo="Papel" opcoes={OPCOES_FILTRO_PAPEL} value={form.papel} onChange={(e) => setForm({ ...form, papel: e.target.value })} />
        <div className="acoes">
          <Botao type="submit">Filtrar</Botao>
        </div>
      </form>

      <ErroApi erro={erro} />
      {carregando && !dados && <Carregando />}
      {dados && (
        <>
          <div className="tabela-wrap">
            <table className="tabela">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>E-mail</th>
                  <th>Papel</th>
                  <th>Situação</th>
                  <th>Criado em</th>
                </tr>
              </thead>
              <tbody>
                {dados.itens.map((usuario) => {
                  const propria = usuario.id === eu.id;
                  return (
                    <tr key={usuario.id}>
                      <td>
                        {usuario.nome} {propria && <Badge>você</Badge>}
                      </td>
                      <td>{usuario.email}</td>
                      <td>
                        <select
                          aria-label={`Papel de ${usuario.nome}`}
                          value={usuario.papel}
                          disabled={propria || alterandoId === usuario.id}
                          onChange={(e) => alterar(usuario, { papel: e.target.value }, `Papel de ${usuario.nome} atualizado.`)}
                        >
                          {PAPEIS.map((papel) => (
                            <option key={papel.valor} value={papel.valor}>
                              {papel.rotulo}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <Botao
                          variante="link"
                          disabled={propria || alterandoId === usuario.id}
                          onClick={() =>
                            alterar(
                              usuario,
                              { ativo: !usuario.ativo },
                              usuario.ativo ? `${usuario.nome} foi desativado(a).` : `${usuario.nome} foi reativado(a).`,
                            )
                          }
                        >
                          {usuario.ativo ? <Badge tom="sucesso">Ativo — desativar</Badge> : <Badge tom="erro">Inativo — reativar</Badge>}
                        </Botao>
                      </td>
                      <td>{dataHora(usuario.criado_em)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <Paginacao pagina={dados.pagina} totalPaginas={dados.total_paginas} total={dados.total} onMudar={setPagina} />
        </>
      )}
    </>
  );
}
