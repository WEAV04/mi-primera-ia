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

@app.post("/talk_v2")
async def talk_to_ai_v2(user_input: UserInput):
    """
    Versión mejorada de /talk que integra el registro y detección de patrones emocionales.
    """
    if not user_input.text or user_input.text.strip() == "":
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")

    # Importar funciones del módulo de memoria emocional
    # Idealmente, esto estaría al inicio del archivo, pero para el ejemplo se coloca aquí.
    # En una app real, gestionar importaciones y posibles errores de importación.
    try:
        from modules.memoria_emocional import registrar_emocion, leer_historial, detectar_patrones_simples
    except ImportError:
        # Manejo básico si el módulo no se encuentra, podría devolver un error o funcionar en modo degradado
        raise HTTPException(status_code=500, detail="Módulo de memoria emocional no encontrado.")

    detected_emotion = detect_emotion(user_input.text)

    # Simular intensidad y contexto para el registro
    # En un sistema real, la intensidad podría venir del modelo de detección de emociones
    # y el contexto podría ser generado por NLP (ej. extracción de palabras clave).
    simulated_intensity = round(random.uniform(0.5, 0.9), 2) # Intensidad aleatoria para el ejemplo
    simulated_context = user_input.text[:50] # Primeros 50 caracteres como contexto simple

    # Registrar la emoción actual
    registro_exitoso = registrar_emocion(
        emocion=detected_emotion,
        intensidad=simulated_intensity,
        source_text=user_input.text,
        context=simulated_context
    )
    if not registro_exitoso:
        # Loggear o manejar el error de registro como sea apropiado
        print(f"Advertencia: No se pudo registrar la emoción para el input: {user_input.text}")

    # Leer el historial y detectar patrones
    # Podríamos definir umbrales y emociones objetivo basados en alguna lógica o configuración
    # Por ejemplo, buscar 3 tristezas recientes o 2 enojos en la última hora.
    # Para este ejemplo, buscaremos 3 ocurrencias de la emoción actual en todo el historial.
    # ¡Esto es solo un ejemplo simple! Una lógica de patrones más avanzada sería necesaria.

    patron_detectado_info = None
    if registro_exitoso: # Solo intentar leer y detectar si el registro fue ok (o si el historial podría existir)
        historial_emocional = leer_historial()
        if historial_emocional: # Si hay historial
            # Ejemplo: detectar si la emoción actual (si es negativa) se ha repetido 3 veces
            # en los últimos 10 eventos (simplificación de ventana de tiempo por conteo de eventos)
            # o en las últimas 24 horas (ventana de tiempo real)
            if detected_emotion in ["tristeza", "enojo", "miedo"]:
                # Usaremos una ventana de tiempo de 1 día (24 * 60 * 60 segundos)
                # y un umbral de 2 repeticiones (incluyendo la actual) para que sea más fácil de probar
                patron_detectado_info = detectar_patrones_simples(
                    historial_emociones=historial_emocional,
                    emocion_objetivo=detected_emotion,
                    umbral_conteo=2, # La actual + 1 anterior = patrón
                    ventana_tiempo_segundos=24 * 60 * 60
                )

    # Elegir respuesta empática
    ai_response_text = random.choice(empathetic_responses[detected_emotion])

    # Si se detectó un patrón, podríamos modificar la respuesta o añadir información
    # Esto es muy básico, en el futuro se refinaría.
    if patron_detectado_info:
        ai_response_text += f" (He notado que te has sentido {detected_emotion} varias veces recientemente. ¿Está todo bien?)"
        print(f"Patrón detectado: {patron_detectado_info}") # Para logging en servidor

    return {
        "emotion_detected": detected_emotion,
        "ai_response": ai_response_text,
        "emotion_registered": registro_exitoso,
        "pattern_info": patron_detectado_info
    }


@app.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de IA Emocional. Usa POST /talk para la versión simple o POST /talk_v2 para la versión con memoria."}

# Para ejecutar localmente: uvicorn app:app --reload
# (Esto es solo un comentario, no se ejecutará aquí)
