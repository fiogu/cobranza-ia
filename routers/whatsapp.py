from fastapi import APIRouter

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

@router.get("/")
def status():
    return {"modulo": "whatsapp", "status": "pendiente"}
