# IA Emocional FastAPI

Esta es una sencilla aplicación API construida con FastAPI que simula ser una IA de compañía o emocional.
Puede detectar una emoción básica en el texto proporcionado por el usuario y responder con un mensaje empático.

## Características

-   Detección de emociones (simulada): alegría, tristeza, enojo, miedo, neutral.
-   Respuestas empáticas predefinidas para cada emoción.
-   Endpoint `/talk` para interactuar con la IA.
-   **Nueva Funcionalidad: Presencia Vocal (Beta)**
    -   Permite a la IA responder con voz (TTS - Text-to-Speech).
    -   Se activa opcionalmente con la bandera `"voz": true` en la solicitud.
    -   Genera un archivo de audio `.mp3` con la respuesta.
    -   La respuesta del API incluye `voz_url` con el enlace al audio.
    -   El nombre del archivo de audio incluye la emoción detectada (ej. `audio_alegria_uuid.mp3`).
    -   Utiliza la librería `gTTS` para la síntesis de voz.
    -   Opcionalmente, puede usar `pyngrok` para exponer URLs de audio públicas si está configurado.

## Requisitos Previos

-   Python 3.7+
-   pip

## Instalación

1.  **Clona el repositorio (o descarga los archivos):**
    ```bash
    # git clone <tu-repositorio-url>
    # cd <nombre-del-directorio>
    ```

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    ```
    Activa el entorno virtual:
    -   En Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    -   En macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

    Asegúrate de que el directorio `static/audio` exista o pueda ser creado por la aplicación en la raíz del proyecto. La aplicación intentará crearlo si no existe.

## Ejecución

Para iniciar la aplicación, ejecuta el siguiente comando en la raíz del proyecto:

```bash
uvicorn app:app --reload
```

Esto iniciará el servidor de desarrollo Uvicorn. La opción `--reload` hará que el servidor se reinicie automáticamente cada vez que modifiques el código.

La API estará disponible en `http://127.0.0.1:8000`.

## Uso de la API

Puedes interactuar con la IA enviando una solicitud POST al endpoint `/talk`. El cuerpo de la solicitud debe ser un JSON con una clave `text` que contenga el mensaje del usuario.

### Ejemplo con `curl`

Abre otra terminal (asegúrate de que el servidor Uvicorn siga ejecutándose) y prueba los siguientes ejemplos:

**Ejemplo de Alegría:**

```bash
curl -X POST "http://127.0.0.1:8000/talk" \
-H "Content-Type: application/json" \
-d '{"text": "¡Estoy muy feliz hoy, todo salió genial!"}'
```

Respuesta esperada (variará debido a la aleatoriedad):

```json
{
    "emotion_detected": "alegría",
    "ai_response": "¡Qué maravilla! Me alegra mucho escuchar eso."
}
```

**Ejemplo de Tristeza:**

```bash
curl -X POST "http://127.0.0.1:8000/talk" \
-H "Content-Type: application/json" \
-d '{"text": "Me siento un poco triste y solo."}'
```

Respuesta esperada (variará):

```json
{
    "emotion_detected": "tristeza",
    "ai_response": "Lamento mucho que te sientas así. Estoy aquí para escucharte."
}
```

**Ejemplo de Enojo:**

```bash
curl -X POST "http://127.0.0.1:8000/talk" \
-H "Content-Type: application/json" \
-d '{"text": "Estoy muy molesto con esta situación."}'
```

Respuesta esperada (variará):

```json
{
    "emotion_detected": "enojo",
    "ai_response": "Entiendo que te sientas así. A veces las cosas pueden ser frustrantes."
}
```

**Ejemplo de Miedo:**

```bash
curl -X POST "http://127.0.0.1:8000/talk" \
-H "Content-Type: application/json" \
-d '{"text": "Tengo miedo de lo que pueda pasar mañana."}'
```

Respuesta esperada (variará):

```json
{
    "emotion_detected": "miedo",
    "ai_response": "Es normal sentir miedo a veces. Estoy aquí contigo."
}
```

**Ejemplo Neutral:**

```bash
curl -X POST "http://127.0.0.1:8000/talk" \
-H "Content-Type: application/json" \
-d '{"text": "El cielo está nublado."}'
```

Respuesta esperada (variará):

```json
{
    "emotion_detected": "neutral",
    "ai_response": "Entendido. ¿Hay algo más en lo que pueda ayudarte hoy?"
}
```

**Ejemplo con Presencia Vocal:**

Para activar la respuesta con voz, añade la bandera `"voz": true` a tu solicitud.

```bash
curl -X POST "http://127.0.0.1:8000/talk" \
-H "Content-Type: application/json" \
-d '{"text": "¡Qué día tan maravilloso, estoy muy feliz!", "voz": true}'
```

Respuesta esperada (la `voz_url` variará y dependerá de si `ngrok` está activo y configurado):

```json
{
    "emotion_detected": "alegría",
    "ai_response": "¡Fantástico! Tu alegría es contagiosa.",
    "voz_url": "http://<ngrok_o_dominio_local>/static/audio/audio_alegria_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.mp3"
}
```
Si `ngrok` está funcionando y configurado, la `voz_url` será una URL pública. De lo contrario, será una ruta local como `/static/audio/audio_alegria_....mp3`. Puedes abrir esta URL en tu navegador para escuchar el audio.

### Consideraciones de la Presencia Vocal

-   La generación de voz se realiza con `gTTS` y actualmente soporta español.
-   La modulación del tono vocal según la emoción es una característica avanzada no implementada directamente con `gTTS` más allá de nombrar el archivo con la emoción.
-   Los archivos de audio se guardan en el directorio `static/audio`. Para un uso prolongado en producción, considera una estrategia de limpieza de archivos antiguos.
-   Si usas `pyngrok` para obtener URLs públicas, asegúrate de tener `ngrok` instalado y, opcionalmente, un token de autenticación configurado para un uso más estable. Puedes establecer la variable de entorno `NGROK_AUTHTOKEN` o configurarlo en el código (no recomendado para producción). Si `ngrok` no se puede iniciar o no está configurado, la `voz_url` será una ruta local.

### Endpoint Raíz
```

Respuesta esperada (variará):

```json
{
    "emotion_detected": "neutral",
    "ai_response": "Entendido. ¿Hay algo más en lo que pueda ayudarte hoy?"
}
```

### Endpoint Raíz

Puedes visitar `http://127.0.0.1:8000/` en tu navegador o usar `curl` para ver un mensaje de bienvenida:

```bash
curl http://127.0.0.1:8000/
```

Respuesta:

```json
{
    "message": "Bienvenido a la API de IA Emocional. Usa la ruta POST /talk para interactuar."
}
```
