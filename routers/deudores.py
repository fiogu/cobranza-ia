from fastapi import APIRouter, HTTPException
from database import supabase
from models import DeudorCreate, DeudorUpdate

router = APIRouter(prefix="/deudores", tags=["Deudores"])

@router.get("/")
def listar_deudores(estado: str = None):
    query = supabase.table("deudores").select("*")
    if estado:
        query = query.eq("estado", estado)
    return query.order("created_at", desc=True).execute().data

@router.get("/{cedula}")
def obtener_deudor(cedula: str):
    res = supabase.table("deudores")\
        .select("*").eq("cedula", cedula).single().execute()
    if not res.data:
        raise HTTPException(404, "Deudor no encontrado")
    return res.data

@router.post("/")
def crear_deudor(deudor: DeudorCreate):
    data = deudor.model_dump()
    data["fecha_vencimiento"] = str(data["fecha_vencimiento"])
    return supabase.table("deudores").insert(data).execute().data[0]

@router.patch("/{cedula}")
def actualizar_deudor(cedula: str, update: DeudorUpdate):
    data = {k: v for k, v in update.model_dump().items() if v is not None}
    return supabase.table("deudores")\
        .update(data).eq("cedula", cedula).execute().data[0]

@router.post("/{cedula}/gestiones")
def registrar_gestion(cedula: str, gestion: dict):
    deudor = supabase.table("deudores")\
        .select("id").eq("cedula", cedula).single().execute()
    if not deudor.data:
        raise HTTPException(404, "Deudor no encontrado")
    gestion["deudor_id"] = deudor.data["id"]
    return supabase.table("gestiones").insert(gestion).execute().data[0]
