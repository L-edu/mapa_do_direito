export default function Carregando({ texto = 'Carregando…' }) {
  return (
    <div className="carregando" role="status">
      <span className="spinner" aria-hidden="true" />
      <span>{texto}</span>
    </div>
  );
}
