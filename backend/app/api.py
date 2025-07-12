# app/api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

router = APIRouter()

class URLRequest(BaseModel):
    url: str

def buscar_valor(soup, label):
    """Función para extraer valores de la página."""
    elemento = soup.find('td', string=label)
    return elemento.find_next_sibling('td').text.strip() if elemento else ''

@router.post("/importar")
async def importar_datos(data: URLRequest):
    try:
        response = requests.get(data.url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="No se pudo acceder a la página")

        soup = BeautifulSoup(response.text, 'html.parser')

        datos = {
            "entidad": buscar_valor(soup, "Nombre Entidad:"),
            "tipo_necesidad": buscar_valor(soup, "Tipo de necesidad:"),
            "codigo_necesidad": buscar_valor(soup, "Código Necesidad de Contratación:"),
            "objeto_compra": buscar_valor(soup, "Objeto de compra:"),
            "forma_pago": soup.find("h3", string="Forma de Pago").find_next("div").text.strip() if soup.find("h3", string="Forma de Pago") else '',
            "lugar_entrega": buscar_valor(soup, "Dirección:"),
            "productos": []
        }

        # Buscar todas las tablas
        tablas = soup.find_all("table")
        for tabla in tablas:
            encabezados = [th.get_text(strip=True).lower() for th in tabla.find_all("th")]

            # ESTRUCTURA DE ECUALIMPIO
            if "cpc" in encabezados and "descripción del producto" in encabezados:
                filas = tabla.find_all("tr")[1:]
                for fila in filas:
                    celdas = fila.find_all("td")
                    if len(celdas) >= 5:
                        datos["productos"].append({
                            "cpc": celdas[1].text.strip(),
                            "descripcion": celdas[3].text.strip(),
                            "cantidad": celdas[4].text.strip(),
                            "precio_unitario": "0"
                        })

            # ESTRUCTURA DE ANDY
            elif "cantidad" in encabezados and "cpc" in encabezados and "descripción" in encabezados:
                filas = tabla.find_all("tr")[1:]
                for fila in filas:
                    celdas = fila.find_all("td")
                    if len(celdas) >= 3:
                        datos["productos"].append({
                            "cantidad": celdas[0].text.strip(),
                            "cpc": celdas[1].text.strip(),
                            "descripcion": celdas[3].text.strip(),
                            "precio_unitario": "0"
                        })

        return datos

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
