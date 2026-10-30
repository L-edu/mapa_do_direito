import { PARENTESCOS } from '../../utils/constantes.js';
import { dataISO, moeda, rotuloDe } from '../../utils/formatadores.js';
import Badge from '../ui/Badge.jsx';
import Botao from '../ui/Botao.jsx';

export default function TabelaMembros({ membros, onEditar, onExcluir }) {
  return (
    <div className="tabela-wrap">
      <table className="tabela">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Nascimento</th>
            <th>Idade</th>
            <th>Parentesco</th>
            <th>Renda</th>
            <th>Situações</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {membros.map((membro) => (
            <tr key={membro.id}>
              <td>{membro.nome}</td>
              <td>{dataISO(membro.data_nascimento)}</td>
              <td>{membro.idade ?? '—'}</td>
              <td>{rotuloDe(PARENTESCOS, membro.parentesco)}</td>
              <td>{moeda(membro.renda_individual)}</td>
              <td className="selos">
                {membro.gestante && <Badge tom="neutro">Gestante</Badge>}
                {membro.possui_deficiencia && <Badge tom="neutro">Deficiência</Badge>}
                {membro.frequenta_escola && <Badge tom="neutro">Estuda</Badge>}
              </td>
              <td className="acoes">
                <Botao variante="link" onClick={() => onEditar(membro)} aria-label={`Editar ${membro.nome}`}>
                  Editar
                </Botao>
                <Botao variante="link" className="texto-perigo" onClick={() => onExcluir(membro)} aria-label={`Remover ${membro.nome}`}>
                  Remover
                </Botao>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
