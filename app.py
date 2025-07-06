from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

app = FastAPI()

class UserInput(BaseModel):
    text: str

# Simulación de detección de emociones
def detect_emotion(text: str) -> str:
    """
    Simula la detección de emociones en el texto del usuario.
    En una aplicación real, aquí se integraría un modelo de NLP.
    """
    text_lower = text.lower()
    if "feliz" in text_lower or "alegre" in text_lower or "contento" in text_lower or "genial" in text_lower:
        return "alegría"
    elif "triste" in text_lower or "deprimido" in text_lower or "mal" in text_lower and "siento" in text_lower:
        return "tristeza"
    elif "enojado" in text_lower or "molesto" in text_lower or "furioso" in text_lower:
        return "enojo"
    elif "miedo" in text_lower or "asustado" in text_lower or "temor" in text_lower:
        return "miedo"
    else:
        return "neutral"

# Respuestas empáticas predefinidas
empathetic_responses = {
    "alegría": [
        "¡Qué maravilla! Me alegra mucho escuchar eso.",
        "¡Eso suena genial! Comparte más si quieres.",
        "¡Fantástico! Tu alegría es contagiosa.",
        "Me llena de gozo saber que te sientes así."
    ],
    "tristeza": [
        "Lamento mucho que te sientas así. Estoy aquí para escucharte.",
        "Entiendo que estés pasando por un momento difícil. ¿Quieres hablar de ello?",
        "No estás solo en esto. A veces todos nos sentimos tristes.",
        "Tómate tu tiempo para sentir. Si necesitas algo, dímelo."
    ],
    "enojo": [
        "Entiendo que te sientas así. A veces las cosas pueden ser frustrantes.",
        "Respira profundo. Si quieres desahogarte, estoy aquí.",
        "Es válido sentir enojo. ¿Hay algo que pueda hacer para ayudar?",
        "Lamento que estés pasando por esto. El enojo es una emoción poderosa."
    ],
    "miedo": [
        "Es normal sentir miedo a veces. Estoy aquí contigo.",
        "Tranquilo, respira. ¿Qué es lo que te asusta?",
        "El miedo puede ser paralizante, pero también nos alerta. ¿Quieres que lo exploremos juntos?",
        "No tienes que enfrentar esto solo. Cuenta conmigo."
    ],
    "neutral": [
        "Entendido. ¿Hay algo más en lo que pueda ayudarte hoy?",
        "Gracias por compartir. ¿Cómo te hace sentir eso?",
        "De acuerdo. ¿Hay algo en particular sobre lo que te gustaría conversar?",
        "Te escucho. Continúa cuando quieras."
    ]
}

@app.post("/talk")
async def talk_to_ai(user_input: UserInput):
    """
    Recibe el texto del usuario, detecta la emoción y devuelve una respuesta empática.
    """
    if not user_input.text or user_input.text.strip() == "":
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")

    emotion = detect_emotion(user_input.text)
    response = random.choice(empathetic_responses[emotion])

    return {"emotion_detected": emotion, "ai_response": response}

@app.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de IA Emocional. Usa la ruta POST /talk para interactuar."}

# Para ejecutar localmente: uvicorn app:app --reload
# (Esto es solo un comentario, no se ejecutará aquí)
