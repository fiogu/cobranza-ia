import os
import requests
from fastapi import APIRouter, HTTPException
from database import supabase

router = APIRouter(prefix="/llamadas", tags=["Llamadas"])

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_URL = "https://api.vapi.ai/call/phone"

@router.post("/iniciar/{cedula}")
def iniciar_llamada(cedula: str):
    # 1. Buscar deudor
    res = supabase.table("deudores")\
        .select("*").eq("cedula", cedula).single().execute()
    if not res.data:
        raise HTTPException(404, "Deudor no encontrado")
    
    deudor = res.data

    # 2. Llamar a Vapi
    payload = {
        "phoneNumberId": os.getenv("VAPI_PHONE_NUMBER_ID"),
        "customer": {
            "number": deudor["celular"]
        },
        "assistant": {
            "model": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "systemPrompt": f"""Eres un agente de cobranza profesional y amable de nuestra empresa.
Hablas español colombiano natural y cordial.
Estás llamando a {deudor['nombre']} sobre una deuda de ${deudor['monto']:,.0f} pesos 
que venció el {deudor['fecha_vencimiento']}.

Tu objetivo es llegar a un acuerdo de pago. Sé empático pero firme.

Maneja estas objeciones:
- "No tengo plata" → Ofrece un plan de pagos en cuotas
- "Ya pagué" → Pide el soporte y escala a un asesor humano
- "Llame después" → Confirma una fecha y hora específica
- "Es un error" → Escala a un asesor humano amablemente

Cuando logres un acuerdo, confirma: monto y fecha de pago.
Nunca seas agresivo. Siempre ofrece soluciones."""
            },
            "voice": {
                "provider": "11labs",
                "voiceId": os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
            },
            "firstMessage": f"Hola, ¿hablo con {deudor['nombre']}? Le llamo de nuestra empresa para hablar sobre su cuenta.",
            "endCallPhrases": ["hasta luego", "chao", "adiós", "que le vaya bien", "hasta pronto"]
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

    # 3. Actualizar intentos en DB
    supabase.table("deudores").update({
        "intentos_llamada": deudor["intentos_llamada"] + 1,
        "estado": "en_gestion"
    }).eq("cedula", cedula).execute()

    # 4. Registrar gestión
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
