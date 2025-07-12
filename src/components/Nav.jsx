import React from 'react';
import { Link } from 'react-router-dom';  // Importa el componente Link de react-router-dom

const Nav = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">Proforma Electrónica</Link>
        <ul className="navbar-menu">
          <li><Link to="/" className="navbar-item">Inicio</Link></li>
          <li><Link to="/formularios/andy" className="navbar-item">Formulario Andy Hierro</Link></li>
          <li><Link to="/formularios/ecualimpio" className="navbar-item">Formulario Ecualimpio</Link></li>
          {/* <li><Link to="/contacto" className="navbar-item">Contacto</Link></li> */}
        </ul>
      </div>
    </nav>
  );
};

export default Nav;
