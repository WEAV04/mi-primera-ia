# IA Emocional FastAPI

Esta es una sencilla aplicación API construida con FastAPI que simula ser una IA de compañía o emocional.
Puede detectar una emoción básica en el texto proporcionado por el usuario y responder con un mensaje empático.

## Características

-   Detección de emociones (simulada): alegría, tristeza, enojo, miedo, neutral.
-   Respuestas empáticas predefinidas para cada emoción.
-   Endpoint `/talk` para interactuar con la IA.
-   **Historial de interacciones:** Guarda cada conversación en `historial.json`.
-   **Detección de patrones emocionales:** Identifica si una emoción se ha repetido con frecuencia en las últimas interacciones y lo notifica en la respuesta.

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

Si interactúas varias veces y se detecta un patrón (por ejemplo, tristeza recurrente), la respuesta podría incluir una notificación del patrón:

```json
{
    "emotion_detected": "tristeza",
    "ai_response": "Tómate tu tiempo para sentir. Si necesitas algo, dímelo.",
    "emotional_pattern_detected": "He notado que te has sentido 'tristeza' con frecuencia últimamente (en 3 de las últimas 5 interacciones)."
}
```

### Estructura de `historial.json`

El archivo `historial.json` almacenará una lista de objetos, donde cada objeto representa una interacción y tiene la siguiente estructura:

```json
[
  {
    "timestamp": "2023-10-27T10:30:00.123456",
    "user_text": "Me siento un poco triste hoy.",
    "detected_emotion": "tristeza",
    "ai_response": "Lamento que te sientas así. ¿Quieres hablar de ello?"
  },
  {
    "timestamp": "2023-10-27T10:35:15.789012",
    "user_text": "Sí, he tenido una semana difícil.",
    "detected_emotion": "tristeza",
    "ai_response": "Entiendo, a veces las semanas son complicadas."
  }
  // ... más interacciones
]
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
