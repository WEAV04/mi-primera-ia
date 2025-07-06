from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse # Importado para devolver archivos
from pydantic import BaseModel
import random
import os # Importado para operaciones del sistema de archivos
import uuid # Importado para nombres de archivo únicos
from gtts import gTTS # Importado para Text-to-Speech
from pyngrok import ngrok, conf # Importado para exponer URLs locales (opcional)
import logging # Para logging

# Configuración de logging para pyngrok y la app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuración de ngrok (Opcional, pero útil para URLs públicas) ---
# Es recomendable configurar tu NGROK_AUTHTOKEN como variable de entorno
# o directamente aquí si es solo para desarrollo.
# Ejemplo: conf.get_default().auth_token = "TU_NGROK_AUTHTOKEN"
# Por ahora, lo dejaremos para que funcione sin auth token si es posible,
# o el usuario puede configurarlo en su entorno.

# Directorio para guardar los archivos de audio
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

app = FastAPI()

# Montar el directorio estático para servir los archivos de audio
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

class UserInput(BaseModel):
    text: str
    voz: bool = False

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

    response_data = {"emotion_detected": emotion, "ai_response": ai_response_text}

    if user_input.voz:
        try:
            # Generar nombre de archivo único
            filename = f"audio_{emotion}_{uuid.uuid4()}.mp3"
            filepath = os.path.join(AUDIO_DIR, filename)

            # Generar audio con gTTS
            tts = gTTS(text=ai_response_text, lang='es', slow=False) # 'es' para español
            tts.save(filepath)
            logger.info(f"Archivo de audio generado: {filepath}")

            # Construir la URL para acceder al archivo
            # Opción 1: Usar ngrok si está configurado y se desea una URL pública
            # (Requiere que ngrok esté instalado y, preferiblemente, un authtoken configurado)
            try:
                # Intentar obtener túneles existentes o crear uno nuevo
                tunnels = ngrok.get_tunnels()
                http_tunnel = None
                if tunnels:
                    for tunnel in tunnels:
                        if tunnel.proto == "http" or tunnel.proto == "https": # ngrok puede usar http o https
                            http_tunnel = tunnel
                            break

                if not http_tunnel:
                    # Asegúrate de que el puerto aquí coincida con el puerto en el que corre Uvicorn (por defecto 8000)
                    http_tunnel = ngrok.connect(8000, bind_tls=True) # bind_tls=True para https
                    logger.info(f"Nuevo túnel ngrok iniciado: {http_tunnel.public_url}")

                voz_url = f"{http_tunnel.public_url}/static/audio/{filename}"
                logger.info(f"URL pública de ngrok para el audio: {voz_url}")

            except Exception as e_ngrok:
                logger.warning(f"No se pudo obtener la URL de ngrok: {e_ngrok}. Usando URL local relativa.")
                # Opción 2: URL local relativa (funciona si el cliente está en la misma red o es el mismo host)
                # Esta URL dependerá de cómo se sirvan los archivos estáticos y la URL base del servidor.
                # Para uvicorn corriendo en localhost:8000, sería:
                voz_url = f"/static/audio/{filename}" # Asume que FastAPI sirve /static

            response_data["voz_url"] = voz_url

        except Exception as e_tts:
            logger.error(f"Error al generar el archivo de voz: {e_tts}")
            # No se añade voz_url si hay un error, la respuesta seguirá siendo JSON sin audio.
            # Podríamos añadir un mensaje de error específico si quisiéramos.
            response_data["voz_error"] = str(e_tts)


    return response_data

@app.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de IA Emocional. Usa la ruta POST /talk para interactuar."}

# Para ejecutar localmente: uvicorn app:app --reload
# (Esto es solo un comentario, no se ejecutará aquí)
