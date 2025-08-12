from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import logging
from typing import List
import requests
from bs4 import BeautifulSoup
from pdf_generator import generar_proforma_docx, numero_a_letras  # tus utilidades
from datetime import datetime
import os

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Modelos de datos (opcionales para tipado)
# -------------------------
class URLRequest(BaseModel):
    url: str

class Producto(BaseModel):
    cpc: str
    descripcion: str
    cantidad: float
    precio_unitario: float

class ProformaData(BaseModel):
    entidad: str
    ruc: str
    direccion: str
    ciudad: str
    tipo_necesidad: str
    codigo_necesidad: str
    objeto_compra: str
    productos: List[Producto]
    iva: float                    # (monto) - si lo usas en algún lado
    forma_pago: str
    plazo_ejecucion: str
    garantia_tecnica: str
    lugar_entrega: str
    vigencia_proforma: str
    anexos: str
    tipo_formulario: str          # andy | ecualimpio

# -------------------------
# Rutas
# -------------------------
@app.get("/")
async def root():
    return {"message": "API lista"}

@app.post("/importar")
async def importar(data: URLRequest):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(data.url, headers=headers, timeout=10)
        if res.status_code != 200:
            raise HTTPException(status_code=404, detail="No se pudo acceder a la página")

        soup = BeautifulSoup(res.content, "html.parser")

        datos = {
            "entidad": buscar_dato_por_strong(soup, "Nombre Entidad:"),
            "tipo_necesidad": buscar_dato_por_strong(soup, "Tipo de necesidad:"),
            "codigo_necesidad": buscar_dato_por_strong(soup, "Código Necesidad de Contratación:"),
            "objeto_compra": extraer_objeto_compra(soup),
            "forma_pago": buscar_forma_pago(soup),
            "direccion": buscar_direccion(soup),
            "productos": extraer_productos(soup)
        }

        logging.debug(f"Datos extraídos: {datos}")
        return JSONResponse(content=datos)

    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generar-pdf")
async def generar_pdf(request: Request):
    form = await request.form()

    # Porcentaje de IVA escrito por el usuario (0–100)
    iva_porcentaje = _to_float(form.get("iva"))

    # Tipo de formulario para escoger plantilla
    tipo_formulario = form.get("tipo_formulario")
    logging.debug(f"Tipo de formulario recibido: {tipo_formulario}")

    # -------------------------
    # Productos y totales
    # -------------------------
    cpcs = form.getlist("cpc[]")
    descripciones = form.getlist("descripcion[]")
    cantidades = form.getlist("cantidad[]")
    precios = form.getlist("precio_unitario[]")

    productos = []
    for i in range(len(cpcs)):
        cantidad = _to_float(cantidades[i])
        precio = _to_float(precios[i])
        total = round(cantidad * precio, 2)
        productos.append({
            "cpc": cpcs[i],
            "descripcion": descripciones[i],
            "cantidad": cantidad,
            "precio_unitario": precio,
            "total": total
        })

    subtotal = round(sum(p["total"] for p in productos), 2)
    valor_i = round(subtotal * iva_porcentaje / 100.0, 2)  # monto del IVA
    total_general = round(subtotal + valor_i, 2)

    # -------------------------
    # Datos para plantilla
    # -------------------------
    data = {
        "numero_proforma": form.get("numero_proforma"),
        "fecha_emision": datetime.now().strftime("%d/%m/%Y"),
        "entidad": form.get("entidad"),
        "ruc": form.get("ruc"),
        "direccion": form.get("direccion"),
        "ciudad": form.get("ciudad") or "",
        "tipo_necesidad": form.get("tipo_necesidad"),
        "codigo_necesidad": form.get("codigo_necesidad"),
        "objeto_compra": form.get("objeto_compra"),
        "productos": productos,

        # Claves usadas por la plantilla DOCX
        "subtotal": subtotal,
        "valor_i": valor_i,                 # monto de IVA (celda derecha)
        "iva_porcentaje": iva_porcentaje,   # porcentaje de IVA (para "IVA {{iva_porcentaje}}%")
        "total": total_general,

        "forma_pago": form.get("forma_pago"),
        "plazo_ejecucion": form.get("plazo_ejecucion"),
        "garantia_tecnica": form.get("garantia_tecnica"),
        "lugar_entrega": form.get("lugar_entrega"),
        "vigencia_proforma": form.get("vigencia_proforma"),
        "anexos": form.get("anexos"),
        "letras": numero_a_letras(subtotal),    # si quieres, cámbialo a total_general
        "otros_parametros": form.get("otros_parametros"),
        "validez_proforma": form.get("validez_proforma"),
        "plazo_entrega": form.get("plazo_entrega"),
        "garantia": form.get("garantia"),
        "tipo_formulario": tipo_formulario
    }

    # Selección de plantilla
    plantilla_path = "proforma_template_andy.docx" if tipo_formulario == "andy" else "proforma_template.docx"
    logging.debug(f"Plantilla seleccionada: {plantilla_path}")

    try:
        # Generar DOCX a partir de la plantilla
        docx_path = generar_proforma_docx(data, plantilla_path)

        # Convertir a PDF con tu servicio
        with open(docx_path, "rb") as f:
            files = {
                "file": (
                    os.path.basename(docx_path),
                    f,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            }
            response = requests.post("http://unoconv_service:8002/convert", files=files)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error al convertir a PDF")

        pdf_path = docx_path.replace(".docx", ".pdf")
        with open(pdf_path, "wb") as f:
            f.write(response.content)

        return FileResponse(path=pdf_path, filename=os.path.basename(pdf_path), media_type='application/pdf')

    except Exception as e:
        logging.error("Error en /generar-pdf", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Utilidades
# -------------------------
def _to_float(value: str) -> float:
    """Convierte string a float aceptando coma o punto decimal y valores vacíos."""
    if value is None:
        return 0.0
    s = str(value).strip().replace(" ", "")
    if s == "":
        return 0.0
    return float(s.replace(",", "."))

# --------- Scraping helpers ----------
def buscar_dato_por_strong(soup, etiqueta):
    try:
        elementos = soup.find_all("strong")
        for el in elementos:
            if etiqueta in el.get_text(strip=True):
                text_nodes = []
                for sibling in el.next_siblings:
                    if getattr(sibling, "name", None) == "strong":
                        break
                    if isinstance(sibling, str):
                        text_nodes.append(sibling.strip())
                    elif hasattr(sibling, "get_text"):
                        text_nodes.append(sibling.get_text(strip=True))
                return ' '.join(t for t in text_nodes if t).strip()
    except Exception as e:
        logging.warning(f"Error al buscar {etiqueta}: {e}")
    return ""

def extraer_objeto_compra(soup):
    try:
        strong = soup.find("strong", string=lambda t: t and "Objeto de compra:" in t)
        if strong:
            p = strong.find_next("p")
            if p:
                return p.get_text(strip=True)
        p_card = soup.find("p", class_="card-text")
        if p_card:
            return p_card.get_text(strip=True)
    except Exception as e:
        logging.warning(f"Error al extraer objeto de compra: {e}")
    return ""

def buscar_forma_pago(soup):
    try:
        seccion = soup.find("h2", string=lambda s: s and "Forma de Pago" in s)
        if seccion:
            tabla = seccion.find_next("table")
            return tabla.get_text(strip=True) if tabla else ""
    except Exception:
        return ""
    return ""

def buscar_direccion(soup):
    try:
        contenedor = soup.find("div", class_="funcionario-container mt-4")
        textos = []
        if contenedor:
            p = contenedor.find("p", class_="card-text")
            if p:
                textos = [s.strip() for s in p.stripped_strings]
            direccion_tag = contenedor.find("strong", string=lambda s: "Dirección" in s)
            direccion = direccion_tag.next_sibling.strip() if direccion_tag and direccion_tag.next_sibling else ""
            return (', '.join(textos) + ". " + direccion) if textos else direccion
    except Exception as e:
        logging.warning(f"Error al extraer dirección: {e}")
    return ""

def extraer_productos(soup):
    productos = []
    for tabla in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in tabla.find_all("th")]
        joined = ' '.join(headers)
        if "cpc" in joined and ("descripción del producto" in joined or "descripcion del producto" in joined):
            for fila in tabla.find_all("tr")[1:]:
                celdas = fila.find_all("td")
                if len(celdas) >= 6:
                    productos.append({
                        "cpc": celdas[1].get_text(strip=True),
                        "descripcion": celdas[2].get_text(strip=True),
                        "cantidad": _to_float(celdas[5].get_text(strip=True)),
                        "precio_unitario": 0.0
                    })
    return productos
