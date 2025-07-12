from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import logging
from typing import List
import requests
from bs4 import BeautifulSoup
from pdf_generator import generar_proforma_docx, numero_a_letras  # Esto llama a las funciones del otro archivo
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

# Modelos de datos
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
    iva: float
    forma_pago: str
    plazo_ejecucion: str
    garantia_tecnica: str
    lugar_entrega: str
    vigencia_proforma: str
    anexos: str
    tipo_formulario: str  # Este campo identificará el tipo de formulario (Andy o Ecualimpio)

# Rutas de la API
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

    # Recoger el tipo de formulario
    tipo_formulario = form.get("tipo_formulario")
    logging.debug(f"Tipo de formulario recibido: {tipo_formulario}")

    productos = []
    for i in range(len(form.getlist("cpc[]"))):
        cantidad = float(form.getlist("cantidad[]")[i])
        precio = float(form.getlist("precio_unitario[]")[i])
        total = cantidad * precio
        productos.append({
            "cpc": form.getlist("cpc[]")[i],
            "descripcion": form.getlist("descripcion[]")[i],
            "cantidad": cantidad,
            "precio_unitario": precio,
            "total": total
        })

    subtotal = sum(p["total"] for p in productos)
    iva = float(form.get("iva") or 0)
    total_general = subtotal + iva

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
        "subtotal": subtotal,
        "iva": iva,
        "total": total_general,
        "forma_pago": form.get("forma_pago"),
        "plazo_ejecucion": form.get("plazo_ejecucion"),
        "garantia_tecnica": form.get("garantia_tecnica"),
        "lugar_entrega": form.get("lugar_entrega"),
        "vigencia_proforma": form.get("vigencia_proforma"),
        "anexos": form.get("anexos"),
        "letras": numero_a_letras(subtotal),
        "otros_parametros": form.get("otros_parametros"),
        "validez_proforma": form.get("validez_proforma"),
        "plazo_entrega": form.get("plazo_entrega"),
        "garantia": form.get("garantia"),
        "tipo_formulario": tipo_formulario  # Recibimos el tipo de formulario
    }

    # Selección de plantilla basada en el formulario
    if tipo_formulario == "andy":
        plantilla_path = "proforma_template_andy.docx"  # Plantilla para Andy
    else:
        plantilla_path = "proforma_template.docx"  # Plantilla para Ecualimpio

    logging.debug(f"Plantilla seleccionada: {plantilla_path}")

    try:
        # Llamamos a la función que maneja el llenado de la plantilla (pdf_generator.py)
        docx_path = generar_proforma_docx(data, plantilla_path)

        # Convertir el archivo a PDF
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

# Funciones utilitarias de scraping
def buscar_dato_por_strong(soup, etiqueta):
    try:
        elementos = soup.find_all("strong")
        for el in elementos:
            if etiqueta in el.get_text(strip=True):
                text_nodes = []
                for sibling in el.next_siblings:
                    if sibling.name == "strong":
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
    except:
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
            return ', '.join(textos) + ". " + direccion if textos else direccion
    except Exception as e:
        logging.warning(f"Error al extraer dirección: {e}")
    return ""

def extraer_productos(soup):
    productos = []
    for tabla in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in tabla.find_all("th")]
        if "cpc" in ' '.join(headers) and "descripción del producto" in ' '.join(headers):
            for fila in tabla.find_all("tr")[1:]:
                celdas = fila.find_all("td")
                if len(celdas) >= 6:
                    productos.append({
                        "cpc": celdas[1].text.strip(),
                        "descripcion": celdas[2].text.strip(),
                        "cantidad": celdas[5].text.strip(),
                        "precio_unitario": "0"
                    })
    return productos