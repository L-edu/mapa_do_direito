import { Link } from 'react-router-dom';
import { programasApi } from '../api/servicos.js';
import { useAuth } from '../contexts/AuthContext.jsx';
import { useCarregar } from '../hooks/useCarregar.js';
import Carregando from '../components/ui/Carregando.jsx';
import { ErroApi } from '../components/ui/Alerta.jsx';
import Badge from '../components/ui/Badge.jsx';

export default function Inicio() {
  const { usuario } = useAuth();
  const { dados, carregando, erro } = useCarregar(() => programasApi.listar({ ativo: true, tamanho: 100 }), []);

  return (
    <>
      <section className="hero">
        <h1>Descubra a que programas sociais a sua família pode ter direito</h1>
        <p>
          Muitas famílias deixam de receber benefícios que já poderiam acessar por não conhecerem os critérios. O Mapa do
          Direito cruza o perfil da família com as regras de cada programa e mostra, em linguagem simples,{' '}
          <strong>o que já está atendido e exatamente o que falta</strong>.
        </p>
        <div className="acoes">
          <Link to="/simulador" className="btn btn--primario btn--grande">
            Simular agora, sem cadastro
          </Link>
          {usuario ? (
            <Link to="/familias" className="btn btn--secundario btn--grande">
              Minhas famílias
            </Link>
          ) : (
            <Link to="/registro" className="btn btn--secundario btn--grande">
              Criar conta para guardar o histórico
            </Link>
          )}
        </div>
      </section>

      <section className="passos">
        <div>
          <span>1</span>
          <h3>Informe o perfil</h3>
          <p>Renda, composição da família e situação de moradia. Sem CPF, sem NIS.</p>
        </div>
        <div>
          <span>2</span>
          <h3>Veja o resultado</h3>
          <p>Cada programa mostra se a família é elegível e quantos requisitos já cumpre.</p>
        </div>
        <div>
          <span>3</span>
          <h3>Saiba o próximo passo</h3>
          <p>Quando algo falta, a orientação diz quanto falta ou o que providenciar.</p>
        </div>
      </section>

      <section>
        <h2>Programas avaliados hoje</h2>
        {carregando && <Carregando />}
        <ErroApi erro={erro} />
        {dados && (
          <div className="programas-grid">
            {dados.itens.map((programa) => (
              <Link key={programa.id} to={`/programas/${programa.id}`} className="programa-item">
                <h3>{programa.nome}</h3>
                <p>{programa.orgao}</p>
                <Badge>{programa.esfera}</Badge>
              </Link>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
