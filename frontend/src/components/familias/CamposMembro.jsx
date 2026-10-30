import { PARENTESCOS } from '../../utils/constantes.js';
import { hoje } from '../../utils/formatadores.js';
import { CampoCheckbox, CampoSelect, CampoTexto } from '../ui/Campos.jsx';

let contador = 0;
const novoId = () => `membro-${++contador}`;

export const membroVazio = () => ({
  _id: novoId(),
  nome: '',
  data_nascimento: '',
  parentesco: 'outro',
  escolaridade: '',
  renda_individual: '0',
  possui_deficiencia: false,
  gestante: false,
  frequenta_escola: false,
});

/** Converte um membro devolvido pela API no formato editável do formulário. */
export const membroDaApi = (membro) => ({
  _id: novoId(),
  nome: membro.nome,
  data_nascimento: membro.data_nascimento,
  parentesco: membro.parentesco,
  escolaridade: membro.escolaridade ?? '',
  renda_individual: String(membro.renda_individual ?? 0),
  possui_deficiencia: membro.possui_deficiencia,
  gestante: membro.gestante,
  frequenta_escola: membro.frequenta_escola,
});

/** Converte o estado do formulário no payload esperado pela API. */
export const membroParaPayload = (membro) => ({
  nome: membro.nome.trim(),
  data_nascimento: membro.data_nascimento,
  parentesco: membro.parentesco,
  escolaridade: membro.escolaridade.trim() || null,
  renda_individual: Number(membro.renda_individual) || 0,
  possui_deficiencia: membro.possui_deficiencia,
  gestante: membro.gestante,
  frequenta_escola: membro.frequenta_escola,
});

/** Campos de uma pessoa da família. Componente controlado: valor + onChange(novoValor). */
export default function CamposMembro({ valor, onChange }) {
  const alterar = (campo) => (evento) => {
    const { type, checked, value } = evento.target;
    onChange({ ...valor, [campo]: type === 'checkbox' ? checked : value });
  };

  return (
    <>
      <div className="grade">
        <CampoTexto
          rotulo="Nome (apenas o primeiro nome)"
          obrigatorio
          maxLength={80}
          value={valor.nome}
          onChange={alterar('nome')}
          autoComplete="off"
        />
        <CampoTexto
          rotulo="Data de nascimento"
          type="date"
          obrigatorio
          max={hoje()}
          value={valor.data_nascimento}
          onChange={alterar('data_nascimento')}
        />
        <CampoSelect rotulo="Parentesco" opcoes={PARENTESCOS} value={valor.parentesco} onChange={alterar('parentesco')} />
        <CampoTexto rotulo="Escolaridade (opcional)" value={valor.escolaridade} onChange={alterar('escolaridade')} />
        <CampoTexto
          rotulo="Renda individual mensal (R$)"
          type="number"
          min="0"
          step="0.01"
          value={valor.renda_individual}
          onChange={alterar('renda_individual')}
        />
      </div>
      <div className="checks">
        <CampoCheckbox rotulo="Possui deficiência" checked={valor.possui_deficiencia} onChange={alterar('possui_deficiencia')} />
        <CampoCheckbox rotulo="Gestante" checked={valor.gestante} onChange={alterar('gestante')} />
        <CampoCheckbox rotulo="Frequenta a escola" checked={valor.frequenta_escola} onChange={alterar('frequenta_escola')} />
      </div>
    </>
  );
}
