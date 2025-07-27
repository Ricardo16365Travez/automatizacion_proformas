// app.js

window.importarDesdeURL = function importarDesdeURL() {
  const url = document.getElementById('url')?.value || document.getElementById('url_proceso')?.value;
  const isAndy = !!document.getElementById('url_proceso');

  fetch('http://localhost:8001/importar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: url })
  })
    .then(response => response.json())
    .then(data => {
      const entidad = document.getElementById('entidad') || document.getElementById('cliente');
      if (entidad) entidad.value = data.entidad || '';

      const direccion = document.getElementById('direccion');
      if (direccion) direccion.value = data.direccion || '';

      const ciudad = document.getElementById('ciudad');
      if (ciudad) ciudad.value = data.ciudad || '';

      const tipo_necesidad = document.getElementById('tipo_necesidad');
      if (tipo_necesidad) tipo_necesidad.value = data.tipo_necesidad || '';

      const codigo_necesidad = document.getElementById('codigo_necesidad');
      if (codigo_necesidad) codigo_necesidad.value = data.codigo_necesidad || '';

      const objeto_compra = document.getElementById('objeto_compra');
      if (objeto_compra) objeto_compra.value = data.objeto_compra || '';

      const forma_pago = document.getElementById('forma_pago');
      if (forma_pago) forma_pago.value = data.forma_pago || '';

      const lugar_entrega = document.getElementById('lugar_entrega');
      if (lugar_entrega) lugar_entrega.value = data.lugar_entrega || '';

      const fecha = document.getElementById('fecha');
      if (fecha) fecha.value = new Date().toISOString().split('T')[0];

      const tablaProductos = document.getElementById('tabla-productos')?.getElementsByTagName('tbody')[0];
      if (tablaProductos) {
        tablaProductos.innerHTML = '';

        data.productos.forEach((producto, index) => {
          const row = tablaProductos.insertRow();

          if (isAndy) {
            row.innerHTML = `
              <td><input type="number" name="cantidad[]" value="${producto.cantidad}" required onchange="calcularTotal()"></td>
              <td><input type="text" name="cpc[]" value="${producto.cpc}" required></td>
              <td><input type="text" name="descripcion[]" value="${producto.descripcion}" required></td>
              <td><input type="text" name="precio_unitario[]" inputmode="decimal" required onchange="validarDecimal(this); calcularTotal();"></td>
              <td><input type="text" name="total[]" placeholder="$ 0,00" disabled></td>
            `;
          } else {
            row.innerHTML = `
              <td>${index + 1}</td>
              <td><input type="text" name="cpc[]" value="${producto.cpc}" required></td>
              <td><input type="text" name="descripcion[]" value="${producto.descripcion}" required></td>
              <td><input type="number" name="cantidad[]" value="${producto.cantidad}" required onchange="calcularTotal()"></td>
              <td><input type="text" name="precio_unitario[]" inputmode="decimal" required onchange="validarDecimal(this); calcularTotal();"></td>
              <td><input type="text" name="total[]" placeholder="$ 0,00" disabled></td>
            `;
          }
        });
      }

      calcularTotal();
    })
    .catch(error => {
      alert('Error al importar datos: ' + error.message);
    });
  }

window.validarDecimal = function validarDecimal(input) {
  input.value = input.value.replace(',', '.'); // convierte coma en punto
}


window.prepararEnvio = function prepararEnvio() {
  const form = document.getElementById('formulario');
  const formData = new FormData(form);

  fetch('http://localhost:8001/generar-pdf', {
    method: 'POST',
    body: formData
  })
    .then(res => {
      if (!res.ok) throw new Error('Error generando PDF');
      return res.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'proforma.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
    })
    .catch(error => alert('Error al generar el PDF: ' + error.message));
}

function calcularTotal() {
  const cantidades = document.querySelectorAll('input[name="cantidad[]"]');
  const precios = document.querySelectorAll('input[name="precio_unitario[]"]');
  const totales = document.querySelectorAll('input[name="total[]"]');
  let subtotal = 0;

  cantidades.forEach((input, index) => {
    const cantidad = parseFloat((input.value || "0").replace(",", ".")) || 0;
    const precio = parseFloat((precios[index].value || "0").replace(",", ".")) || 0;
    const total = cantidad * precio;
    totales[index].value = `$ ${formatNumber(total)}`;
    subtotal += total;
  });

  const ivaInput = document.getElementById('iva');
  const ivaPorcentaje = parseFloat(ivaInput?.value || "0");
  const ivaValor = subtotal * (ivaPorcentaje / 100);
  const totalFinal = subtotal + ivaValor;

  document.getElementById('subtotal').textContent = `$${formatNumber(subtotal)}`;
  document.getElementById('valor-iva').textContent = formatNumber(ivaValor);
  document.getElementById('total').textContent = formatNumber(totalFinal);
}

function formatNumber(number) {
  return number.toLocaleString('es-ES', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}
