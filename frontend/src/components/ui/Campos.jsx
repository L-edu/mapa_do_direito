import { useId } from 'react';

/** Campos de formulário com rótulo, marcação de obrigatório e texto de ajuda. */

function Rotulo({ id, rotulo, obrigatorio }) {
  return (
    <label htmlFor={id}>
      {rotulo}
      {obrigatorio && (
        <span className="obrigatorio" aria-hidden="true">
          {' '}
          *
        </span>
      )}
    </label>
  );
}

export function CampoTexto({ rotulo, ajuda, obrigatorio = false, className = '', ...input }) {
  const id = useId();
  return (
    <div className={`campo ${className}`.trim()}>
      <Rotulo id={id} rotulo={rotulo} obrigatorio={obrigatorio} />
      <input id={id} required={obrigatorio} aria-describedby={ajuda ? `${id}-ajuda` : undefined} {...input} />
      {ajuda && <small id={`${id}-ajuda`}>{ajuda}</small>}
    </div>
  );
}

export function CampoTextarea({ rotulo, ajuda, obrigatorio = false, className = '', ...area }) {
  const id = useId();
  return (
    <div className={`campo ${className}`.trim()}>
      <Rotulo id={id} rotulo={rotulo} obrigatorio={obrigatorio} />
      <textarea id={id} rows={3} required={obrigatorio} {...area} />
      {ajuda && <small>{ajuda}</small>}
    </div>
  );
}

/** opcoes: [{ valor, rotulo }] */
export function CampoSelect({ rotulo, opcoes, obrigatorio = false, className = '', ...select }) {
  const id = useId();
  return (
    <div className={`campo ${className}`.trim()}>
      <Rotulo id={id} rotulo={rotulo} obrigatorio={obrigatorio} />
      <select id={id} required={obrigatorio} {...select}>
        {opcoes.map((opcao) => (
          <option key={opcao.valor} value={opcao.valor}>
            {opcao.rotulo}
          </option>
        ))}
      </select>
    </div>
  );
}

export function CampoCheckbox({ rotulo, className = '', ...input }) {
  const id = useId();
  return (
    <div className={`campo campo--checkbox ${className}`.trim()}>
      <input id={id} type="checkbox" {...input} />
      <label htmlFor={id}>{rotulo}</label>
    </div>
  );
}
