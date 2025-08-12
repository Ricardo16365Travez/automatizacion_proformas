from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import requests
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from pydantic import BaseModel

@app.get("/")
async def root():
    return {"message": "API lista"}

class URLRequest(BaseModel):
    url: str
class Producto(BaseModel):
    cpc: str
    descripcion: str
    cantidad: float
    precio_unitario: float
from typing import List

class ProformaData(BaseModel):
    entidad: str
    ruc: str
    direccion: str
    ciudad: str
    tipo_necesidad: str
    codigo_necesidad: str
    objeto_compra: str
    productos: List[Producto]
    valor_iva: float
    iva: float
    forma_pago: str
    plazo_ejecucion: str
    garantia_tecnica: str
    lugar_entrega: str
    vigencia_proforma: str
    anexos: str
    tipo_formulario: str

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

        return JSONResponse(content=datos)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))