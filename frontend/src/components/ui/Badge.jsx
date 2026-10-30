/** Selo de status. tom: sucesso | alerta | erro | neutro. */
export default function Badge({ tom = 'neutro', children }) {
  return <span className={`badge badge--${tom}`}>{children}</span>;
}
