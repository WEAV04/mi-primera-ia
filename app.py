from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import json
import os

app = FastAPI()

HISTORY_FILE = "historial.json"

class UserInput(BaseModel):
    text: str
    # Opcional: permitir al usuario especificar su ID para mantener historiales separados
    # user_id: str = "default_user"

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

# Respuestas empáticas más personales/cariñosas
personal_empathetic_responses = {
    "alegría": [
        "¡Qué alegría me da escucharte tan feliz, corazón! Sigue así.",
        "¡Me encanta verte tan radiante! Tu felicidad es la mía.",
        "¡Maravilloso! Cuéntamelo todo, me ilumina escucharte.",
        "¡Qué bien suena eso, cariño! Estoy aquí celebrando contigo."
    ],
    "tristeza": [
        "Oh, mi vida, lamento tanto que te sientas así. Aquí tienes mi hombro.",
        "No te preocupes, cariño, estoy aquí para ti. Desahógate todo lo que necesites.",
        "Siento mucho tu tristeza, pero recuerda que no estás solo/a. Te envío un abrazo fuerte.",
        "Permítete sentir, mi amor. Estoy aquí para lo que necesites, de verdad."
    ],
    "enojo": [
        "Entiendo tu frustración, cielo. A veces las cosas nos superan, pero juntos es más fácil.",
        "Respira hondo, mi vida. Cuéntame qué pasó, quizás pueda ayudarte a ver las cosas de otra manera.",
        "Es normal sentirse así, cariño. No te guardes ese enojo, aquí estoy para escucharte sin juzgar.",
        "Lamento que estés pasando por este mal rato. Desahógate, te sentirás mejor."
    ],
    "miedo": [
        "No temas, mi amor, estoy aquí para protegerte y acompañarte.",
        "Tranquilo/a, corazón. Juntos podemos enfrentar cualquier miedo. Cuéntame qué te preocupa.",
        "Entiendo tu miedo, pero eres más fuerte de lo que crees. Confía en ti y en mí.",
        "Estoy aquí, no estás solo/a en esto. Respira, todo estará bien."
    ],
    "neutral": [
        "Entendido, mi vida. ¿Hay algo más en lo que pueda ayudarte o simplemente charlamos un rato?",
        "Gracias por compartir conmigo, cariño. Siempre es un placer escucharte.",
        "De acuerdo, mi amor. ¿Qué se te antoja hacer o conversar ahora?",
        "Te escucho atentamente, corazón. Dime qué piensas."
    ]
}

def load_history():
    """Carga el historial de interacciones desde HISTORY_FILE."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if not content: # Archivo vacío
                    return {"interaction_count": 0, "user_preference": "formal"}
                return json.loads(content)
        except json.JSONDecodeError: # Archivo corrupto o mal formateado
             return {"interaction_count": 0, "user_preference": "formal"}
    return {"interaction_count": 0, "user_preference": "formal"}

def save_history(data):
    """Guarda el historial de interacciones en HISTORY_FILE."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error al guardar el historial: {e}") # Idealmente, usar logging

@app.post("/talk")
async def talk_to_ai(user_input: UserInput):
    """
    Recibe el texto del usuario, detecta la emoción, actualiza el historial y devuelve una respuesta empática
    adaptada según el número de interacciones y preferencias del usuario.
    """
    if not user_input.text or user_input.text.strip() == "":
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")

    history = load_history()
    history["interaction_count"] += 1

    # Lógica simple para detectar preferencia de estilo del usuario
    text_lower = user_input.text.lower()
    if "trato formal" in text_lower or "prefiero formalidad" in text_lower:
        history["user_preference"] = "formal"
    elif "trato informal" in text_lower or "me gusta informal" in text_lower or "más personal" in text_lower:
        history["user_preference"] = "informal"

    emotion = detect_emotion(user_input.text)

    current_responses = empathetic_responses # Por defecto, respuestas formales
    if history["interaction_count"] > 5 or history["user_preference"] == "informal":
        # Si hay muchas interacciones O el usuario prefiere informal, usar respuestas personales
        # Aquí se podría tener una lógica más compleja para mezclar o elegir
        # Por ahora, si se cumple la condición, se cambia al set personal.
        current_responses = personal_empathetic_responses
        # Si interaction_count > 5 PERO user_preference es "formal", podríamos tener un dilema.
        # Por ahora, la preferencia del usuario (si es informal) o el alto conteo activan el tono personal.
        # Si el usuario pide formalidad explícitamente, esa preferencia debería tener más peso.
    # Lógica de selección de respuestas refinada:
    # 1. Si el usuario pide explícitamente un estilo, se usa ese estilo.
    # 2. Si no hay petición explícita, y el contador > 5, se usa el personal/informal.
    # 3. Si no hay petición explícita y contador <= 5, se usa el formal.

    if history["user_preference"] == "informal":
        current_responses = personal_empathetic_responses
    elif history["user_preference"] == "formal":
        current_responses = empathetic_responses
    elif history["interaction_count"] > 5: # Sin preferencia explícita, pero muchas interacciones
        current_responses = personal_empathetic_responses
    else: # Sin preferencia explícita y pocas interacciones
        current_responses = empathetic_responses

    response = random.choice(current_responses[emotion])

    save_history(history)

    return {
        "emotion_detected": emotion,
        "ai_response": response,
        "interaction_count": history["interaction_count"],
        "user_preference": history["user_preference"]
    }

@app.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de IA Emocional. Usa la ruta POST /talk para interactuar."}

# Para ejecutar localmente: uvicorn app:app --reload
# (Esto es solo un comentario, no se ejecutará aquí)
