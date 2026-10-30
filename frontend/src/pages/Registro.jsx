import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi } from '../api/servicos.js';
import { useAlertas } from '../contexts/AlertasContext.jsx';
import { useAuth } from '../contexts/AuthContext.jsx';
import Botao from '../components/ui/Botao.jsx';
import { ErroApi } from '../components/ui/Alerta.jsx';
import { CampoTexto } from '../components/ui/Campos.jsx';
import CabecalhoPagina from '../components/ui/CabecalhoPagina.jsx';

export default function Registro() {
  const { entrar } = useAuth();
  const alertas = useAlertas();
  const navigate = useNavigate();
  const [form, setForm] = useState({ nome: '', email: '', senha: '', confirmar: '' });
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);
  const [erroSenha, setErroSenha] = useState('');

  const alterar = (campo) => (evento) => setForm({ ...form, [campo]: evento.target.value });

  async function enviar(evento) {
    evento.preventDefault();
    if (form.senha !== form.confirmar) {
      setErroSenha('As senhas não conferem.');
      return;
    }
    setErroSenha('');
    setEnviando(true);
    setErro(null);
    try {
      await authApi.registrar({ nome: form.nome.trim(), email: form.email.trim(), senha: form.senha });
      await entrar(form.email.trim(), form.senha);
      alertas.sucesso('Conta criada com sucesso!');
      navigate('/familias', { replace: true });
    } catch (e) {
      setErro(e);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="pagina-estreita">
      <CabecalhoPagina titulo="Criar conta" subtitulo="Com uma conta você cadastra a sua família e guarda o histórico." />
      <form className="cartao" onSubmit={enviar}>
        <CampoTexto rotulo="Nome" obrigatorio minLength={2} maxLength={120} value={form.nome} onChange={alterar('nome')} />
        <CampoTexto rotulo="E-mail" type="email" obrigatorio value={form.email} onChange={alterar('email')} />
        <CampoTexto
          rotulo="Senha"
          type="password"
          obrigatorio
          minLength={8}
          maxLength={72}
          autoComplete="new-password"
          ajuda="Mínimo de 8 caracteres."
          value={form.senha}
          onChange={alterar('senha')}
        />
        <CampoTexto
          rotulo="Confirmar senha"
          type="password"
          obrigatorio
          autoComplete="new-password"
          value={form.confirmar}
          onChange={alterar('confirmar')}
        />
        {erroSenha && <p className="campo__erro">{erroSenha}</p>}
        <ErroApi erro={erro} />
        <Botao type="submit" carregando={enviando} className="btn--cheio">
          Criar conta
        </Botao>
        <p className="ajuda">
          Já tem conta? <Link to="/login">Entrar</Link>
        </p>
      </form>
    </div>
  );
}
