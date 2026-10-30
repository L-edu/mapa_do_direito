import Botao from './Botao.jsx';

export default function Paginacao({ pagina, totalPaginas, total, onMudar }) {
  return (
    <nav className="paginacao" aria-label="Paginação">
      <span>{total ?? 0} registro(s)</span>
      {totalPaginas > 1 && (
        <div className="acoes">
          <Botao variante="secundario" disabled={pagina <= 1} onClick={() => onMudar(pagina - 1)}>
            Anterior
          </Botao>
          <span>
            Página {pagina} de {totalPaginas}
          </span>
          <Botao variante="secundario" disabled={pagina >= totalPaginas} onClick={() => onMudar(pagina + 1)}>
            Próxima
          </Botao>
        </div>
      )}
    </nav>
  );
}
