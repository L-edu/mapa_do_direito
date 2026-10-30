/** Mensagem em bloco. tipo: erro | sucesso | info | aviso. */
export default function Alerta({ tipo = 'info', titulo, children }) {
  return (
    <div className={`alerta alerta--${tipo}`} role={tipo === 'erro' ? 'alert' : 'status'}>
      {titulo && <strong>{titulo}</strong>}
      {children}
    </div>
  );
}

/** Exibe um erro vindo da API (ApiError) com a lista de campos inválidos, se houver. */
export function ErroApi({ erro }) {
  if (!erro) return null;
  return (
    <Alerta tipo="erro">
      <span>{erro.message}</span>
      {erro.detalhes?.length > 0 && (
        <ul>
          {erro.detalhes.map((detalhe, indice) => (
            <li key={indice}>
              {detalhe.campo ? <strong>{detalhe.campo}: </strong> : null}
              {detalhe.mensagem}
            </li>
          ))}
        </ul>
      )}
    </Alerta>
  );
}
