import React, { useState } from 'react';

// Función para importar los datos de una URL
function importarDesdeURL(url, setFormData) {
  fetch('http://localhost:8001/importar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: url })
  })
    .then((response) => response.json())
    .then((data) => {
      setFormData((prevData) => ({
        ...prevData,
        entidad: data.entidad || '',
        direccion: data.direccion || '',
        ciudad: data.ciudad || '',
        tipo_necesidad: data.tipo_necesidad || '',
        codigo_necesidad: data.codigo_necesidad || '',
        objeto_compra: data.objeto_compra || '',
        forma_pago: data.forma_pago || '',
        lugar_entrega: data.lugar_entrega || '',
        fecha: new Date().toISOString().split('T')[0],
        productos: data.productos || [],
      }));
    })
    .catch((error) => {
      alert('Error al importar datos: ' + error.message);
    });
}

// Componente principal
function App() {
  const [formData, setFormData] = useState({
    entidad: '',
    direccion: '',
    ciudad: '',
    tipo_necesidad: '',
    codigo_necesidad: '',
    objeto_compra: '',
    forma_pago: '',
    lugar_entrega: '',
    fecha: '',
    productos: [],
    iva: 12,
    subtotal: 0,
    total: 0,
  });

  // Función para calcular el total
  function calcularTotal() {
    let subtotal = 0;
    formData.productos.forEach((producto) => {
      const total = producto.cantidad * producto.precio_unitario;
      subtotal += total;
    });

    const ivaValor = subtotal * (formData.iva / 100);
    const totalFinal = subtotal + ivaValor;

    setFormData((prevData) => ({
      ...prevData,
      subtotal,
      total: totalFinal,
    }));
  }

  // Actualización de los valores de productos
  function handleProductoChange(index, field, value) {
    const updatedProductos = [...formData.productos];
    updatedProductos[index][field] = value;

    setFormData((prevData) => ({
      ...prevData,
      productos: updatedProductos,
    }));

    calcularTotal();
  }

  // Renderiza la tabla de productos
  function renderProductos() {
    return formData.productos.map((producto, index) => (
      <tr key={index}>
        <td>{index + 1}</td>
        <td>
          <input
            type="text"
            value={producto.cpc}
            onChange={(e) => handleProductoChange(index, 'cpc', e.target.value)}
            required
          />
        </td>
        <td>
          <input
            type="text"
            value={producto.descripcion}
            onChange={(e) => handleProductoChange(index, 'descripcion', e.target.value)}
            required
          />
        </td>
        <td>
          <input
            type="number"
            value={producto.cantidad}
            onChange={(e) => handleProductoChange(index, 'cantidad', e.target.value)}
            required
            onBlur={calcularTotal}
          />
        </td>
        <td>
          <input
            type="text"
            value={producto.precio_unitario}
            onChange={(e) => handleProductoChange(index, 'precio_unitario', e.target.value)}
            required
            onBlur={calcularTotal}
          />
        </td>
        <td>
          <input
            type="text"
            value={producto.cantidad * producto.precio_unitario}
            disabled
          />
        </td>
      </tr>
    ));
  }

  return (
    <div>
      <h1 className="titulo-pagina">Proforma Electrónica</h1>

      <form action="http://localhost:8001/generar-pdf" method="POST" enctype="multipart/form-data" id="formulario">
        <input type="hidden" name="tipo_formulario" value="ecualimpio" />

        {/* Datos de la Proforma */}
        <section className="card">
          <h2>Datos de la Proforma</h2>
          <div className="input-container">
            <label htmlFor="numero_proforma">Número de Proforma:</label>
            <input
              type="text"
              name="numero_proforma"
              value={formData.numero_proforma}
              onChange={(e) => setFormData({ ...formData, numero_proforma: e.target.value })}
              required
            />
          </div>
        </section>

        {/* Ingresar URL del Proceso */}
        <section className="card">
          <h2>1. Ingresar URL del Proceso</h2>
          <div className="input-container">
            <label htmlFor="url">Proceso (URL):</label>
            <input
              type="url"
              name="url"
              id="url"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              required
            />
          </div>
          <button type="button" className="btn btn-turquesa" onClick={() => importarDesdeURL(formData.url, setFormData)}>
            <i className="fas fa-download"></i> Importar datos
          </button>
        </section>

        {/* Datos de la entidad */}
        <section className="card">
          <h2>2. DATOS DE LA ENTIDAD Y/O EMPRESA</h2>
          <div className="input-container">
            <label htmlFor="entidad">Nombre de la entidad:</label>
            <input
              type="text"
              name="entidad"
              id="entidad"
              value={formData.entidad}
              onChange={(e) => setFormData({ ...formData, entidad: e.target.value })}
              required
            />
          </div>
          {/* Otros campos de entrada como RUC, dirección, etc... */}
        </section>

        {/* Tabla de productos */}
        <section className="card">
          <h2>3. CONDICIONES COMERCIALES</h2>
          <div className="tabla-responsive">
            <table id="tabla-productos">
              <thead>
                <tr>
                  <th>Nº</th>
                  <th>CPC</th>
                  <th>Descripción</th>
                  <th>Cantidad</th>
                  <th>V. Unitario</th>
                  <th>V. Total</th>
                </tr>
              </thead>
              <tbody>{renderProductos()}</tbody>
            </table>
          </div>
        </section>

        {/* Subtotales */}
        <section className="card">
          <div className="subtotales">
            <table>
              <tr>
                <td><strong>SUBTOTAL</strong></td>
                <td>$ {formData.subtotal}</td>
              </tr>
              <tr>
                <td><strong>IVA</strong></td>
                <td>$ {formData.iva}</td>
              </tr>
              <tr>
                <td><strong>TOTAL</strong></td>
                <td>$ {formData.total}</td>
              </tr>
            </table>
          </div>
        </section>

        {/* Otros campos */}
        <button type="submit" className="btn-turquesa">Generar PDF</button>
      </form>
    </div>
  );
}

export default App;
