import { FC, useState } from 'react';
import './Navegacion.css';

interface NavegacionProps {
  paginaActual: string;
  setPaginaActual: (pagina: string) => void;
}

const Navegacion: FC<NavegacionProps> = ({ paginaActual, setPaginaActual }) => {
  const [menuAbierto, setMenuAbierto] = useState(false);

  const toggleMenu = () => setMenuAbierto(!menuAbierto);

  const cerrarMenu = () => setMenuAbierto(false);

  const handleNavegacion = (pagina: string) => {
    setPaginaActual(pagina);
    cerrarMenu();
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <h1 className="brand-title">Gestor</h1>
          <span className="brand-subtitle">Productos</span>
        </div>

        <button 
          className={`menu-toggle ${menuAbierto ? 'active' : ''}`}
          onClick={toggleMenu}
          aria-label="Menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <div className={`navbar-menu ${menuAbierto ? 'open' : ''}`}>
          <button
            className={`nav-link ${paginaActual === 'productos' ? 'active' : ''}`}
            onClick={() => handleNavegacion('productos')}
          >
            Productos
          </button>
          <button
            className={`nav-link ${paginaActual === 'categorias' ? 'active' : ''}`}
            onClick={() => handleNavegacion('categorias')}
          >
            Categorias
          </button>
          <button
            className={`nav-link ${paginaActual === 'ingredientes' ? 'active' : ''}`}
            onClick={() => handleNavegacion('ingredientes')}
          >
            Ingredientes
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navegacion;