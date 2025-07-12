# app/models.py
from pydantic import BaseModel

class Producto(BaseModel):
    cpc: str
    descripcion: str
    cantidad: str
    precio_unitario: str

class Proforma(BaseModel):
    entidad: str
    tipo_necesidad: str
    codigo_necesidad: str
    objeto_compra: str
    forma_pago: str
    lugar_entrega: str
    productos: list[Producto]
