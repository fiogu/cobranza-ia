from fastapi import APIRouter

router = APIRouter(prefix="/llamadas", tags=["Llamadas"])

@router.get("/")
def status():
    return {"modulo": "llamadas", "status": "pendiente"}
