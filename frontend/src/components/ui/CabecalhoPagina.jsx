export default function CabecalhoPagina({ titulo, subtitulo, children }) {
  return (
    <header className="pagina-cabecalho">
      <div>
        <h1>{titulo}</h1>
        {subtitulo && <p>{subtitulo}</p>}
      </div>
      {children && <div className="acoes">{children}</div>}
    </header>
  );
}
