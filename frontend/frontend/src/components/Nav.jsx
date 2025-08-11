// src/components/Nav.jsx
import React from 'react';
import { Link } from 'react-router-dom';

export default function Nav() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          Auto-Proforma
        </Link>
        <ul className="navbar-menu">
          <li>
            <Link to="/" className="navbar-item">Inicio</Link>
          </li>
          <li>
            <Link to="/formularios/andy" className="navbar-item">
              Formulario Andy Hierro
            </Link>
          </li>
          <li>
            <Link to="/formularios/ecualimpio" className="navbar-item">
              Formulario Ecualimpio
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}
