from pydantic import BaseModel
from typing import Optional
from datetime import date

class DeudorCreate(BaseModel):
    cedula: str
    nombre: str
    celular: str
    correo: Optional[str] = None
    monto: float
    fecha_vencimiento: date

class DeudorUpdate(BaseModel):
    estado: Optional[str] = None
    notas: Optional[str] = None
    intentos_llamada: Optional[int] = None
    intentos_whatsapp: Optional[int] = None
    intentos_email: Optional[int] = None

class GestionCreate(BaseModel):
    deudor_id: str
    canal: str
    resultado: Optional[str] = None
    duracion_seg: Optional[int] = None
    transcripcion: Optional[str] = None
    acuerdo_monto: Optional[float] = None
    acuerdo_fecha: Optional[date] = None
