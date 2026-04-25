import './Navegacion.css';
import { FC } from 'react';

interface NavegacionProps {
  paginaActual: string;
  setPaginaActual: (pagina: string) => void;
}

const Navegacion: FC<NavegacionProps> = ({ paginaActual, setPaginaActual }) => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <h1>🍽️ Gestor de Productos</h1>
        </div>
        <ul className="navbar-menu">
          <li>
            <button
              className={`nav-link ${paginaActual === 'categorias' ? 'activo' : ''}`}
              onClick={() => setPaginaActual('categorias')}
            >
              📂 Categorías
            </button>
          </li>
          <li>
            <button
              className={`nav-link ${paginaActual === 'productos' ? 'activo' : ''}`}
              onClick={() => setPaginaActual('productos')}
            >
              📦 Productos
            </button>
          </li>
          <li>
            <button
              className={`nav-link ${paginaActual === 'ingredientes' ? 'activo' : ''}`}
              onClick={() => setPaginaActual('ingredientes')}
            >
              🥘 Ingredientes
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navegacion;
