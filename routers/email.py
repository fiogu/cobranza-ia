
from fastapi import APIRouter

router = APIRouter(prefix="/email", tags=["Email"])

@router.get("/")
def status():
    return {"modulo": "email", "status": "pendiente"}
