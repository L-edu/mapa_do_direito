import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAlertas } from '../contexts/AlertasContext.jsx';
import { useAuth } from '../contexts/AuthContext.jsx';
import Botao from '../components/ui/Botao.jsx';
import { ErroApi } from '../components/ui/Alerta.jsx';
import { CampoTexto } from '../components/ui/Campos.jsx';
import CabecalhoPagina from '../components/ui/CabecalhoPagina.jsx';

const CONTAS_DEMO = [
  { rotulo: 'Administrador', email: 'admin@mapadodireito.org', senha: 'admin12345' },
  { rotulo: 'Assistente social', email: 'cras@mapadodireito.org', senha: 'cras12345' },
  { rotulo: 'Cidadão', email: 'cidadao@mapadodireito.org', senha: 'cidadao12345' },
];
const MOSTRAR_DEMO = import.meta.env.VITE_MOSTRAR_CONTAS_DEMO !== 'false';

export default function Login() {
  const { entrar } = useAuth();
  const alertas = useAlertas();
  const navigate = useNavigate();
  const local = useLocation();
  const [form, setForm] = useState({ email: '', senha: '' });
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);

  async function enviar(evento) {
    evento.preventDefault();
    setEnviando(true);
    setErro(null);
    try {
      const usuario = await entrar(form.email.trim(), form.senha);
      alertas.sucesso(`Bem-vindo(a), ${usuario.nome}!`);
      navigate(local.state?.de ?? (usuario.papel === 'admin' ? '/admin' : '/familias'), { replace: true });
    } catch (e) {
      setErro(e);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="pagina-estreita">
      <CabecalhoPagina titulo="Entrar" subtitulo="Acesse para cadastrar famílias e guardar o histórico de simulações." />
      <form className="cartao" onSubmit={enviar}>
        <CampoTexto
          rotulo="E-mail"
          type="email"
          obrigatorio
          autoComplete="username"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <CampoTexto
          rotulo="Senha"
          type="password"
          obrigatorio
          autoComplete="current-password"
          value={form.senha}
          onChange={(e) => setForm({ ...form, senha: e.target.value })}
        />
        <ErroApi erro={erro} />
        <Botao type="submit" carregando={enviando} className="btn--cheio">
          Entrar
        </Botao>
        <p className="ajuda">
          Ainda não tem conta? <Link to="/registro">Criar conta</Link>
        </p>
      </form>

      {MOSTRAR_DEMO && (
        <section className="cartao cartao--destaque">
          <h2>Contas de demonstração</h2>
          <p className="ajuda">Clique para preencher o formulário.</p>
          <div className="acoes">
            {CONTAS_DEMO.map((conta) => (
              <Botao key={conta.email} variante="secundario" onClick={() => setForm({ email: conta.email, senha: conta.senha })}>
                {conta.rotulo}
              </Botao>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
