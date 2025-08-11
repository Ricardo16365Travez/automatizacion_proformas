// src/components/Nav.jsx
import React from 'react';
import { Link } from 'react-router-dom';

export default function Nav() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          AUTO PROFORMA
        </Link>
        <ul className="navbar-menu">
          <li>
            <Link to="/" className="navbar-item">Inicio</Link>
          </li>
          <li>
            <Link to="/formularios/andy" className="navbar-item">
              Cotización
            </Link>
          </li>
          <li>
            <Link to="/formularios/ecualimpio" className="navbar-item">
              Datos de la Proforma
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}
