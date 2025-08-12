from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

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
