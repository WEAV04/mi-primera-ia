from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import json
from datetime import datetime

app = FastAPI()

HISTORY_FILE = "historial.json"

class UserInput(BaseModel):
    text: str

# Funciones para manejar el historial
def load_history():
    """Carga el historial de interacciones desde el archivo JSON."""
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if not content: # Archivo vacío
                return []
            history = json.loads(content)
            return history
    except FileNotFoundError:
        return [] # Devuelve lista vacía si el archivo no existe
    except json.JSONDecodeError:
        return [] # Devuelve lista vacía si el JSON es inválido

def save_history_entry(text: str, emotion: str):
    """Guarda una nueva entrada en el historial de interacciones."""
    history = load_history()
    new_entry = {
        "text": text,
        "emotion": emotion,
        "timestamp": datetime.now().isoformat()
    }
    history.append(new_entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

# Simulación de detección de emociones
def detect_emotion(text: str) -> str:
    """
    Simula la detección de emociones en el texto del usuario.
    En una aplicación real, aquí se integraría un modelo de NLP.
    """
    text_lower = text.lower()
    # Palabras clave para alegría mejoradas
    if any(keyword in text_lower for keyword in ["feliz", "alegre", "contento", "genial", "maravilloso", "encantado", "fantástico", "mejor", "alegría"]):
        return "alegría"
    # Palabras clave para tristeza
    elif "triste" in text_lower or "deprimido" in text_lower or ("mal" in text_lower and "siento" in text_lower) or "desanimado" in text_lower:
        return "tristeza"
    # Palabras clave para enojo
    elif any(keyword in text_lower for keyword in ["enojado", "molesto", "furioso", "frustrado", "iracundo"]):
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
    save_history_entry(user_input.text, emotion) # Guardar interacción

    history = load_history()
    ai_response = ""
    history_analysis_active = False

    # Lógica simple de análisis de historial
    if len(history) > 2:
        recent_emotions = [entry["emotion"] for entry in history[-3:]] # Últimas 3 emociones

        contextual_response_generated = False
        if all(e == "tristeza" for e in recent_emotions):
            ai_response = "He notado que te has sentido triste últimamente. Recuerda que estoy aquí si necesitas hablar más a fondo o si hay algo específico que te gustaría compartir."
            contextual_response_generated = True
        elif all(e == "alegría" for e in recent_emotions):
            ai_response = "¡Parece que has estado de muy buen humor últimamente! Me encanta ver tanta alegría."
            contextual_response_generated = True
        elif all(e == "enojo" for e in recent_emotions):
            ai_response = "He percibido bastante enojo en nuestras últimas conversaciones. Si algo te sigue molestando, estoy aquí para escucharte."
            contextual_response_generated = True

        if contextual_response_generated:
            history_analysis_active = True

    if not ai_response: # Si no hay un patrón específico o el historial es corto, o no se generó respuesta contextual
        response_options = empathetic_responses.get(emotion, empathetic_responses["neutral"])
        ai_response = random.choice(response_options)

    return {"emotion_detected": emotion, "ai_response": ai_response, "history_analysis_active": history_analysis_active}

@app.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de IA Emocional con Memoria. Usa la ruta POST /talk para interactuar."}

# Inicializar el archivo de historial si no existe (opcional, ya que load_history lo maneja)
# Sin embargo, es buena práctica asegurar que esté ahí desde el inicio.
if __name__ == "__main__":
    # Esto es principalmente para cuando se ejecuta con "python app.py",
    # uvicorn maneja las importaciones de manera diferente.
    # No obstante, crear el archivo si no existe es inofensivo.
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            pass # Solo para verificar si existe
    except FileNotFoundError:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f) # Crear un archivo JSON con una lista vacía
            print(f"Archivo de historial '{HISTORY_FILE}' creado.")

# Para ejecutar localmente: uvicorn app:app --reload
# (Esto es solo un comentario, no se ejecutará aquí)
