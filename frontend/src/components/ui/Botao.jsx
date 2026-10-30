/** Botão padrão. variante: primario | secundario | perigo | link. */
export default function Botao({
  variante = 'primario',
  carregando = false,
  type = 'button',
  className = '',
  disabled = false,
  children,
  ...resto
}) {
  return (
    <button
      type={type}
      className={`btn btn--${variante} ${className}`.trim()}
      disabled={disabled || carregando}
      aria-busy={carregando || undefined}
      {...resto}
    >
      {carregando && <span className="spinner spinner--pequeno" aria-hidden="true" />}
      {children}
    </button>
  );
}
