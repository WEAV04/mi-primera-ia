from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import json
from datetime import datetime, timezone # Added timezone

app = FastAPI()

HISTORY_FILE = "historial.json"

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
    ai_response_text = random.choice(empathetic_responses[emotion])

    # Guardar interacción en el historial
    try:
        history = []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Si el archivo no existe o está vacío/corrupto, empezamos con una lista vacía
            history = []

        interaction = {
            "timestamp": datetime.now(timezone.utc).isoformat(), # Changed to timezone-aware UTC datetime
            "user_text": user_input.text,
            "detected_emotion": emotion,
            "ai_response": ai_response_text
        }
        history.append(interaction)

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

    except IOError as e:
        # En un caso real, aquí podría ir un logging más robusto
        print(f"Error al escribir en el historial: {e}")
        # No relanzamos la excepción para no interrumpir la respuesta al usuario,
        # pero podría ser una opción dependiendo de los requisitos.

    # Detectar patrones emocionales
    pattern_message = detect_emotional_patterns(history) # history ya está cargada y actualizada

    response_data = {
        "emotion_detected": emotion,
        "ai_response": ai_response_text
    }
    if pattern_message:
        response_data["emotional_pattern_detected"] = pattern_message

    return response_data


def detect_emotional_patterns(history: list, num_interactions_to_check: int = 5, recurrence_threshold: int = 3) -> str | None:
    """
    Detecta patrones emocionales en las últimas interacciones.
    Por ejemplo, si una emoción específica aparece `recurrence_threshold` veces
    en las últimas `num_interactions_to_check` interacciones.
    """
    if not history or len(history) < num_interactions_to_check:
        return None # No hay suficientes datos para detectar un patrón

    recent_interactions = history[-num_interactions_to_check:]
    emotion_counts = {}
    for interaction in recent_interactions:
        emotion = interaction.get("detected_emotion")
        if emotion:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

    for emotion, count in emotion_counts.items():
        if count >= recurrence_threshold:
            return f"He notado que te has sentido '{emotion}' con frecuencia últimamente (en {count} de las últimas {len(recent_interactions)} interacciones)."

    return None

@app.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de IA Emocional. Usa la ruta POST /talk para interactuar."}

# Para ejecutar localmente: uvicorn app:app --reload
# (Esto es solo un comentario, no se ejecutará aquí)
