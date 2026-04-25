import './styles/design-system.css';
import './styles/utilities.css';
import './styles/components.css';
import { useState } from 'react';
import { ToastProvider } from './context/ToastContext';
import ToastContainer from './components/ToastContainer';
import Navegacion from './components/Navegacion';
import PaginaCategorias from './pages/PaginaCategorias';
import PaginaProductos from './pages/PaginaProductos';
import PaginaIngredientes from './pages/PaginaIngredientes';

type PaginaType = 'categorias' | 'productos' | 'ingredientes';

function App() {
  const [paginaActual, setPaginaActual] = useState<PaginaType>('productos');

  const renderPagina = () => {
    switch (paginaActual) {
      case 'categorias':
        return <PaginaCategorias />;
      case 'productos':
        return <PaginaProductos />;
      case 'ingredientes':
        return <PaginaIngredientes />;
      default:
        return <PaginaProductos />;
    }
  };

  return (
    <ToastProvider>
      <div className="app">
        <Navegacion paginaActual={paginaActual} setPaginaActual={setPaginaActual} />
        <main className="main-content">
          {renderPagina()}
        </main>
        <ToastContainer />
      </div>
    </ToastProvider>
  );
}

export default App;