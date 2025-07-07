# Módulo de Memoria Emocional (`memoria_emocional.py`)

Este módulo proporciona las funcionalidades básicas para que Willy pueda registrar, recordar y analizar patrones simples en su historial de interacciones emocionales. Su objetivo principal es sentar las bases para un comportamiento emocional más profundo y contextualizado.

## Archivo de Datos: `historial.json`

Todas las interacciones emocionales se registran en un archivo llamado `historial.json`, ubicado en la raíz del proyecto. Este archivo es una lista de objetos JSON, donde cada objeto representa un evento emocional individual.

### Estructura de un Evento Emocional

Cada evento en `historial.json` sigue la siguiente estructura:

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffff",
  "emotion": "nombre_de_la_emocion",
  "intensity": 0.0-1.0,
  "source_text": "el texto del usuario que generó la emoción",
  "context": "un breve resumen o palabras clave del input"
}
```

-   **`timestamp`**: (String) Fecha y hora del evento en formato ISO 8601. Se genera automáticamente al registrar la emoción.
-   **`emotion`**: (String) La emoción detectada. Debe ser una de las emociones predefinidas en `EMOCIONES_VALIDAS` dentro de `memoria_emocional.py` (ej: "alegría", "tristeza", "enojo", "miedo", "sorpresa", "neutral").
-   **`intensity`**: (Float) Un valor numérico entre 0.0 y 1.0 que indica la intensidad percibida de la emoción.
-   **`source_text`**: (String) El texto original del usuario que se analizó para determinar la emoción.
-   **`context`**: (String) Un resumen corto, palabras clave o una breve descripción del input del usuario para facilitar la comprensión del disparador emocional sin necesidad de procesar `source_text` completamente cada vez. Puede estar vacío.

## Funciones Principales

El módulo `memoria_emocional.py` expone las siguientes funciones clave:

### 1. `registrar_emocion(emocion: str, intensidad: float, source_text: str, context: str = None) -> bool`

-   **Propósito**: Registra un nuevo evento emocional en `historial.json`.
-   **Argumentos**:
    -   `emocion`: La emoción a registrar (debe estar en `EMOCIONES_VALIDAS`).
    -   `intensidad`: La intensidad de la emoción (0.0 a 1.0).
    -   `source_text`: El texto del usuario.
    -   `context` (opcional): Contexto adicional.
-   **Retorna**: `True` si el registro fue exitoso, `False` en caso contrario (ej., emoción o intensidad inválida, error de archivo).

### 2. `leer_historial() -> list`

-   **Propósito**: Lee y devuelve todos los eventos emocionales almacenados en `historial.json`.
-   **Retorna**: Una lista de diccionarios (eventos emocionales). Devuelve una lista vacía si el archivo no existe, está corrupto, o no contiene entradas.

### 3. `detectar_patrones_simples(historial_emociones: list, emocion_objetivo: str, umbral_conteo: int, ventana_tiempo_segundos: int = None) -> dict | None`

-   **Propósito**: Analiza una lista de eventos emocionales para detectar patrones básicos, como la repetición de una emoción específica.
-   **Argumentos**:
    -   `historial_emociones`: La lista de eventos a analizar (generalmente obtenida de `leer_historial()`).
    -   `emocion_objetivo`: La emoción específica a buscar (ej: "tristeza").
    -   `umbral_conteo`: El número mínimo de veces que la `emocion_objetivo` debe aparecer para considerarse un patrón.
    -   `ventana_tiempo_segundos` (opcional): Si se proporciona, solo considera eventos dentro de los últimos N segundos desde el evento más reciente en el historial. Si es `None`, considera todo el historial.
-   **Retorna**: Un diccionario con información sobre el patrón detectado (ej: `{"patron": "repeticion_emocion_tristeza", "emocion": "tristeza", "conteo": 3, "eventos_recientes": [...]}`) o `None` si no se detecta ningún patrón que cumpla los criterios.

## Ejemplo de Uso (Conceptual en `app.py`)

```python
# En app.py (o similar, después de que una emoción es detectada)
from modules.memoria_emocional import registrar_emocion, leer_historial, detectar_patrones_simples

# ... (código de detección de emoción) ...
# detected_emotion = "tristeza"
# user_text = "Hoy me siento muy mal."
# intensity_simulada = 0.8
# context_simulado = "sentimiento negativo general"

# Registrar la emoción
registrar_emocion(detected_emotion, intensity_simulada, user_text, context_simulado)

# Leer historial y buscar patrones
historial = leer_historial()
if historial:
    patron_tristeza = detectar_patrones_simples(historial, "tristeza", umbral_conteo=3, ventana_tiempo_segundos=86400) # 3 veces en las últimas 24h
    if patron_tristeza:
        print(f"Patrón detectado: {patron_tristeza['emocion']} se ha repetido {patron_tristeza['conteo']} veces recientemente.")
        # Aquí se podría activar una lógica especial, como el "modo terapia" o una respuesta más personalizada.
```

Este módulo es un componente fundamental para las futuras mejoras emocionales de Willy, permitiendo una comprensión más rica y continua de las interacciones del usuario.
