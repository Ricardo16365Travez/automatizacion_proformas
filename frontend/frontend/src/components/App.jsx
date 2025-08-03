import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Nav from './Nav'; // Componente de navegación
import '../index.css'; // Ajusta la ruta según donde esté tu CSS global

function Inicio() {
  return (
    <div className="bg-light container py-5">
      <h2 className="titulo-formulario">SELECCIONA UN FORMULARIO</h2>
      <div className="row justify-content-center gy-4">
        {/* Formulario Ecualimpio */}
        <div className="col-md-5">
          <div className="card border-start border-3 border-success empresa-card shadow-sm">
            <div className="empresa-nombre">Datos de la Proforma</div>
            <Link to="/formularios/ecualimpio" className="btn btn-turquesa w-100">
              Ingresar
            </Link>
          </div>
        </div>

        {/* Formulario Andy Hierro */}
        <div className="col-md-5">
          <div className="card border-start border-3 border-primary empresa-card shadow-sm">
            <div className="empresa-nombre">Cotización</div>
            <Link to="/formularios/andy" className="btn btn-turquesa w-100">
              Ingresar
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <>
      {/* Cabecera de navegación */}
      <Nav />

      {/* Rutas de la aplicación */}
      <Routes>
        {/* Página de inicio que lista los formularios */}
        <Route path="/" element={<Inicio />} />

        {/* Rutas para cargar los formularios HTML dentro de iframes */}
        <Route
          path="/formularios/ecualimpio"
          element={
            <iframe
              src="/formularios/ecualimpio.html"
              style={{ width: '100%', height: '100vh', border: 'none' }}
              title="Formulario Ecualimpio"
            />
          }
        />

        <Route
          path="/formularios/andy"
          element={
            <iframe
              src="/formularios/andy.html"
              style={{ width: '100%', height: '100vh', border: 'none' }}
              title="Formulario Andy Hierro"
            />
          }
        />
      </Routes>
    </>
  );
}
