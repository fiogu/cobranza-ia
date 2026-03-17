import os
import requests
from fastapi import APIRouter, HTTPException
from database import supabase

router = APIRouter(prefix="/llamadas", tags=["Llamadas"])

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_URL = "https://api.vapi.ai/call/phone"

@router.post("/iniciar/{cedula}")
def iniciar_llamada(cedula: str):
    res = supabase.table("deudores")\
        .select("*").eq("cedula", cedula).single().execute()
    if not res.data:
        raise HTTPException(404, "Deudor no encontrado")
    
    deudor = res.data

    payload = {
        "phoneNumberId": os.getenv("VAPI_PHONE_NUMBER_ID"),
        "customer": {
            "number": deudor["celular"]
        },
        "assistant": {
            "model": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "systemPrompt": f"""Eres un agente de cobranza profesional y amable.
Hablas español colombiano natural y cordial.
Estás llamando a {deudor['nombre']} sobre una deuda de ${deudor['monto']:,.0f} pesos 
que venció el {deudor['fecha_vencimiento']}.
Tu objetivo es llegar a un acuerdo de pago.
Maneja objeciones:
- No tengo plata: Ofrece plan de pagos
- Ya pagué: Pide soporte y escala a humano
- Llame después: Confirma fecha y hora
- Es un error: Escala a humano amablemente
Cuando logres acuerdo confirma monto y fecha de pago."""
            },
            "voice": {
                "provider": "11labs",
                "voiceId": os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
            },
            "firstMessage": f"Hola, ¿hablo con {deudor['nombre']}? Le llamo para hablar sobre su cuenta.",
            "endCallPhrases": ["hasta luego", "chao", "adiós", "que le vaya bien"]
        }
    }

    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(VAPI_URL, json=payload, headers=headers)
    
    if response.status_code != 201:
        raise HTTPException(500, f"Error Vapi: {response.text}")

    call_data = response.json()

    supabase.table("deudores").update({
        "intentos_llamada": deudor["intentos_llamada"] + 1,
        "estado": "en_gestion"
    }).eq("cedula", cedula).execute()

    supabase.table("gestiones").insert({
        "deudor_id": deudor["id"],
        "canal": "llamada",
        "resultado": "iniciada",
    }).execute()

    return {
        "mensaje": "Llamada iniciada",
        "call_id": call_data.get("id"),
        "deudor": deudor["nombre"],
        "telefono": deudor["celular"]
    }

@router.get("/estado/{call_id}")
def estado_llamada(call_id: str):
    headers = {"Authorization": f"Bearer {VAPI_API_KEY}"}
    response = requests.get(f"https://api.vapi.ai/call/{call_id}", headers=headers)
    return response.json()
