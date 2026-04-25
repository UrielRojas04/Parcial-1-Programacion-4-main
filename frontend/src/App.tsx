import './App.css';
import { useState } from 'react';
import Navegacion from './components/Navegacion';
import PaginaCategorias from './pages/PaginaCategorias';
import PaginaProductos from './pages/PaginaProductos';
import PaginaIngredientes from './pages/PaginaIngredientes';

type PaginaType = 'categorias' | 'productos' | 'ingredientes';

function App() {
  const [paginaActual, setPaginaActual] = useState<PaginaType>('categorias');

  const renderPagina = () => {
    switch (paginaActual) {
      case 'categorias':
        return <PaginaCategorias />;
      case 'productos':
        return <PaginaProductos />;
      case 'ingredientes':
        return <PaginaIngredientes />;
      default:
        return <PaginaCategorias />;
    }
  };

  return (
    <div className="app">
      <Navegacion paginaActual={paginaActual} setPaginaActual={setPaginaActual} />
      <main className="main-content">
        {renderPagina()}
      </main>
    </div>
  );
}

export default App;
