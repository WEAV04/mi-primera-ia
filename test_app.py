import pytest
from fastapi.testclient import TestClient
import json
import os
from datetime import datetime, timedelta, timezone # Added timezone

# Asegúrate de que app.py esté en el PYTHONPATH o en el mismo directorio
from app import app, HISTORY_FILE, detect_emotional_patterns, detect_emotion

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture(autouse=True)
def cleanup_history_file():
    """Limpia el archivo de historial antes y después de cada prueba."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    # Crear un historial.json vacío para pruebas que puedan necesitar leerlo inicialmente
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)
    yield  # Esto es donde se ejecuta la prueba
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

@pytest.fixture
def sample_history_neutral():
    now = datetime.now(timezone.utc)
    return [
        {"timestamp": (now - timedelta(minutes=i*5)).isoformat(), "user_text": "test", "detected_emotion": "neutral", "ai_response": "ok"}
        for i in range(5)
    ]

@pytest.fixture
def sample_history_sad_pattern():
    now = datetime.now(timezone.utc)
    return [
        {"timestamp": (now - timedelta(minutes=20)).isoformat(), "user_text": "sad 1", "detected_emotion": "tristeza", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=15)).isoformat(), "user_text": "happy", "detected_emotion": "alegría", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=10)).isoformat(), "user_text": "sad 2", "detected_emotion": "tristeza", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=5)).isoformat(), "user_text": "ok", "detected_emotion": "neutral", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=1)).isoformat(), "user_text": "sad 3", "detected_emotion": "tristeza", "ai_response": "..."}
    ]

@pytest.fixture
def sample_history_mixed_less_than_threshold():
    now = datetime.now(timezone.utc)
    return [
        {"timestamp": (now - timedelta(minutes=20)).isoformat(), "user_text": "sad 1", "detected_emotion": "tristeza", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=15)).isoformat(), "user_text": "happy", "detected_emotion": "alegría", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=10)).isoformat(), "user_text": "sad 2", "detected_emotion": "tristeza", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=5)).isoformat(), "user_text": "angry", "detected_emotion": "enojo", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=1)).isoformat(), "user_text": "fear", "detected_emotion": "miedo", "ai_response": "..."}
    ]

@pytest.fixture
def sample_history_short():
    now = datetime.now(timezone.utc)
    return [
        {"timestamp": (now - timedelta(minutes=5)).isoformat(), "user_text": "sad 1", "detected_emotion": "tristeza", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=1)).isoformat(), "user_text": "sad 2", "detected_emotion": "tristeza", "ai_response": "..."}
    ]

# --- Pruebas para detect_emotion (simulada) ---
# Estas pruebas son más para asegurar que la lógica de simulación no cambie inesperadamente.
# Ahora usando la función `detect_emotion` importada directamente.

def test_detect_emotion_alegria():
    assert detect_emotion("Estoy muy feliz y contento") == "alegría"

def test_detect_emotion_tristeza():
    assert detect_emotion("Me siento mal y triste") == "tristeza"

def test_detect_emotion_enojo():
    assert detect_emotion("Estoy furioso y molesto") == "enojo"

def test_detect_emotion_miedo():
    assert detect_emotion("Tengo mucho miedo de esto") == "miedo"

def test_detect_emotion_neutral():
    assert detect_emotion("El clima está soleado") == "neutral"


# --- Pruebas para el endpoint /talk y la creación de historial.json ---

def test_talk_creates_history_file():
    response = client.post("/talk", json={"text": "Hola mundo feliz"})
    assert response.status_code == 200
    assert os.path.exists(HISTORY_FILE)

    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    assert len(history) == 1
    interaction = history[0]
    assert interaction["user_text"] == "Hola mundo feliz"
    assert interaction["detected_emotion"] == "alegría"
    assert "timestamp" in interaction
    assert "ai_response" in interaction

def test_talk_appends_to_history():
    client.post("/talk", json={"text": "Primer mensaje feliz"})
    client.post("/talk", json={"text": "Segundo mensaje triste"})

    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    assert len(history) == 2
    assert history[0]["user_text"] == "Primer mensaje feliz"
    assert history[0]["detected_emotion"] == "alegría"
    assert history[1]["user_text"] == "Segundo mensaje triste"
    assert history[1]["detected_emotion"] == "tristeza"

def test_talk_empty_input():
    response = client.post("/talk", json={"text": ""})
    assert response.status_code == 400
    with open(HISTORY_FILE, "r") as f: # Verificar que el historial no se modificó o se mantuvo vacío
        history = json.load(f)
        assert len(history) == 0

def test_talk_whitespace_input():
    response = client.post("/talk", json={"text": "   "})
    assert response.status_code == 400
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
        assert len(history) == 0

# --- Pruebas para detect_emotional_patterns ---

def test_pattern_no_history():
    assert detect_emotional_patterns([]) is None

def test_pattern_short_history(sample_history_short):
    # Por defecto, num_interactions_to_check es 5
    assert detect_emotional_patterns(sample_history_short) is None
    # Incluso si bajamos el listón, pero no el de recurrencia
    assert detect_emotional_patterns(sample_history_short, num_interactions_to_check=2, recurrence_threshold=3) is None


def test_pattern_sad_pattern_detected(sample_history_sad_pattern):
    expected_message = "He notado que te has sentido 'tristeza' con frecuencia últimamente (en 3 de las últimas 5 interacciones)."
    assert detect_emotional_patterns(sample_history_sad_pattern) == expected_message

def test_pattern_no_clear_pattern(sample_history_mixed_less_than_threshold):
    assert detect_emotional_patterns(sample_history_mixed_less_than_threshold) is None

def test_pattern_neutral_pattern_if_dominant(sample_history_neutral):
    # Si neutral es la emoción dominante y cumple el umbral
    history_mostly_neutral = [
        {"timestamp": "t1", "user_text": "n1", "detected_emotion": "neutral", "ai_response": "..."} ,
        {"timestamp": "t2", "user_text": "n2", "detected_emotion": "neutral", "ai_response": "..."} ,
        {"timestamp": "t3", "user_text": "s1", "detected_emotion": "tristeza", "ai_response": "..."} ,
        {"timestamp": "t4", "user_text": "n3", "detected_emotion": "neutral", "ai_response": "..."} ,
        {"timestamp": "t5", "user_text": "a1", "detected_emotion": "alegría", "ai_response": "..."}
    ]
    expected_message = "He notado que te has sentido 'neutral' con frecuencia últimamente (en 3 de las últimas 5 interacciones)."
    assert detect_emotional_patterns(history_mostly_neutral) == expected_message

def test_pattern_custom_thresholds():
    history = [
        {"timestamp": "t1", "user_text": "m1", "detected_emotion": "miedo", "ai_response": "..."} ,
        {"timestamp": "t2", "user_text": "m2", "detected_emotion": "miedo", "ai_response": "..."} ,
        {"timestamp": "t3", "user_text": "o1", "detected_emotion": "otro", "ai_response": "..."}
    ]
    # Detectar miedo si aparece 2 veces en las últimas 3 interacciones
    expected_message = "He notado que te has sentido 'miedo' con frecuencia últimamente (en 2 de las últimas 3 interacciones)."
    assert detect_emotional_patterns(history, num_interactions_to_check=3, recurrence_threshold=2) == expected_message
    # No debería detectar si el umbral de recurrencia es más alto
    assert detect_emotional_patterns(history, num_interactions_to_check=3, recurrence_threshold=3) is None


# --- Pruebas de integración: /talk con detección de patrones ---

def test_talk_reports_pattern_in_response():
    # Simular un historial previo que cause un patrón
    now = datetime.now(timezone.utc)
    initial_history = [
        {"timestamp": (now - timedelta(minutes=20)).isoformat(), "user_text": "sad 1", "detected_emotion": "tristeza", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=15)).isoformat(), "user_text": "happy", "detected_emotion": "alegría", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=10)).isoformat(), "user_text": "sad 2", "detected_emotion": "tristeza", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=5)).isoformat(), "user_text": "ok", "detected_emotion": "neutral", "ai_response": "..."}
        # La siguiente interacción "triste" debería disparar el patrón
    ]
    with open(HISTORY_FILE, "w") as f:
        json.dump(initial_history, f)

    response = client.post("/talk", json={"text": "Me siento muy triste hoy también"})
    assert response.status_code == 200
    data = response.json()

    assert data["emotion_detected"] == "tristeza" # Corregido: detected_emotion -> emotion_detected
    assert "ai_response" in data
    expected_pattern_msg = "He notado que te has sentido 'tristeza' con frecuencia últimamente (en 3 de las últimas 5 interacciones)."
    assert data["emotional_pattern_detected"] == expected_pattern_msg

    # Verificar que la nueva interacción se añadió al historial
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    assert len(history) == 5
    assert history[-1]["user_text"] == "Me siento muy triste hoy también"

def test_talk_no_pattern_in_response_if_none_detected():
    # Simular un historial que NO cause un patrón
    now = datetime.now(timezone.utc)
    initial_history = [
        {"timestamp": (now - timedelta(minutes=20)).isoformat(), "user_text": "sad 1", "detected_emotion": "tristeza", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=15)).isoformat(), "user_text": "happy", "detected_emotion": "alegría", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=10)).isoformat(), "user_text": "angry", "detected_emotion": "enojo", "ai_response": "..."} ,
        {"timestamp": (now - timedelta(minutes=5)).isoformat(), "user_text": "fear", "detected_emotion": "miedo", "ai_response": "..."}
    ]
    with open(HISTORY_FILE, "w") as f:
        json.dump(initial_history, f)

    response = client.post("/talk", json={"text": "Hoy me siento genial y feliz"})
    assert response.status_code == 200
    data = response.json()

    assert data["emotion_detected"] == "alegría" # Corregido: detected_emotion -> emotion_detected
    assert "ai_response" in data
    assert "emotional_pattern_detected" not in data

    # Verificar que la nueva interacción se añadió al historial
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    assert len(history) == 5
    assert history[-1]["user_text"] == "Hoy me siento genial y feliz"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenido a la API de IA Emocional. Usa la ruta POST /talk para interactuar."}

# Para ejecutar las pruebas:
# 1. Asegúrate de tener pytest y httpx instalados: pip install pytest httpx
# 2. Guarda este archivo como test_app.py en el mismo directorio que app.py
# 3. Ejecuta pytest en la terminal desde ese directorio: pytest
# (Opcionalmente, `pytest -v` para más detalle)

# Este archivo también necesita que app.py importe app desde sí mismo si se corre con pytest
# Para eso, se podría modificar app.py ligeramente o asegurar que el path de importación
# sea correcto. Dado que se importa `from app import app`, se asume que pytest
# maneja esto correctamente al estar en el mismo directorio, o que app.py es parte de un paquete.
# La importación `from app import app, HISTORY_FILE, detect_emotional_patterns`
# puede ser redundante si app ya es el módulo, pero es explícita.
# Si `app.detect_emotion` es una función global en app.py, entonces `app.detect_emotion` no funcionaría.
# Debería ser `detect_emotion` directamente si está en el mismo módulo.
# Corregiré esto en el código de prueba.
# En app.py, la función es global: `def detect_emotion(text: str) -> str:`
# Por lo tanto, en las pruebas, debería ser importada directamente o accedida a través del módulo `app`.
# Como he hecho `from app import app, HISTORY_FILE, detect_emotional_patterns`,
# las funciones globales de `app.py` deberían estar disponibles directamente o a través del módulo `app`.
# Para `detect_emotion`, como no la importé explícitamente, la accederé a través de `app.detect_emotion`
# asumiendo que `app` es el módulo. Sin embargo, `app = FastAPI()` es una instancia.
# Lo correcto sería:
# from app import app as fastapi_app, HISTORY_FILE, detect_emotional_patterns, detect_emotion
# client = TestClient(fastapi_app)
# Y luego usar `detect_emotion` directamente.
# Voy a ajustar las llamadas a `app.detect_emotion` para que sean `detect_emotion` tras importarla.

# Re-ajuste de importación para las pruebas de detect_emotion
# from app import app as fastapi_app, HISTORY_FILE, detect_emotional_patterns, detect_emotion
# client = TestClient(fastapi_app)
# ...
# def test_detect_emotion_alegria():
# assert detect_emotion("Estoy muy feliz y contento") == "alegría"
# ... etc.
# Haré esta corrección ahora.
# No, la estructura actual de app.py no permite importar `detect_emotion` directamente así de fácil
# sin causar problemas con la instancia de `app` de FastAPI si no se estructura como un paquete.
# Para simplificar, mantendré `app.detect_emotion` pero esto es una peculiaridad de cómo
# pytest podría estar cargando el módulo `app`.
# La forma más limpia sería tener las funciones de lógica de negocio separadas de la definición de la app FastAPI.
# Sin embargo, para este ejercicio, el código de prueba se adaptará a la estructura actual.
# Las pruebas para `detect_emotion` son más bien para la función de utilidad, no para un endpoint.
# `app.detect_emotion` no es la forma correcta de acceder a la función global `detect_emotion`
# desde el módulo `app`. Si `app.py` se importa como `import app`, entonces sería `app.detect_emotion`.
# Si se importa como `from app import detect_emotion`, entonces es `detect_emotion`.
# TestClient(app) usa la instancia `app` de FastAPI.
# La forma en que está escrito `from app import app` importa la instancia de FastAPI.
# Para acceder a la función `detect_emotion` directamente, debería ser `from app import detect_emotion`.
# Modificaré las importaciones y el uso en las pruebas para reflejar esto.
# (Hecho en el bloque siguiente)
#
# Al final, he optado por no cambiar la estructura de importación en este bloque,
# sino que lo haré en un bloque separado para mantener este bloque de creación de archivo puro.
# El siguiente bloque realizará las correcciones necesarias en este archivo de prueba.
# ```python
# import pytest
# from fastapi.testclient import TestClient
# import json
# import os
# from datetime import datetime, timedelta

# # Asegúrate de que app.py esté en el PYTHONPATH o en el mismo directorio
# from app import app, HISTORY_FILE, detect_emotional_patterns, detect_emotion

# client = TestClient(app)

# # --- Fixtures ---

# @pytest.fixture(autouse=True)
# def cleanup_history_file():
#     """Limpia el archivo de historial antes y después de cada prueba."""
#     if os.path.exists(HISTORY_FILE):
#         os.remove(HISTORY_FILE)
#     # Crear un historial.json vacío para pruebas que puedan necesitar leerlo inicialmente
#     with open(HISTORY_FILE, "w") as f:
#         json.dump([], f)
#     yield  # Esto es donde se ejecuta la prueba
#     if os.path.exists(HISTORY_FILE):
#         os.remove(HISTORY_FILE)

# @pytest.fixture
# def sample_history_neutral():
#     return [
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=i*5)).isoformat(), "user_text": "test", "detected_emotion": "neutral", "ai_response": "ok"}
#         for i in range(5)
#     ]

# @pytest.fixture
# def sample_history_sad_pattern():
#     return [
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=20)).isoformat(), "user_text": "sad 1", "detected_emotion": "tristeza", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(), "user_text": "happy", "detected_emotion": "alegría", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(), "user_text": "sad 2", "detected_emotion": "tristeza", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(), "user_text": "ok", "detected_emotion": "neutral", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=1)).isoformat(), "user_text": "sad 3", "detected_emotion": "tristeza", "ai_response": "..."}
#     ]

# @pytest.fixture
# def sample_history_mixed_less_than_threshold():
#     return [
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=20)).isoformat(), "user_text": "sad 1", "detected_emotion": "tristeza", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(), "user_text": "happy", "detected_emotion": "alegría", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(), "user_text": "sad 2", "detected_emotion": "tristeza", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(), "user_text": "angry", "detected_emotion": "enojo", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=1)).isoformat(), "user_text": "fear", "detected_emotion": "miedo", "ai_response": "..."}
#     ]

# @pytest.fixture
# def sample_history_short():
#     return [
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(), "user_text": "sad 1", "detected_emotion": "tristeza", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=1)).isoformat(), "user_text": "sad 2", "detected_emotion": "tristeza", "ai_response": "..."}
#     ]

# # --- Pruebas para detect_emotion (simulada) ---
# # Ahora usando la función `detect_emotion` importada directamente.

# def test_detect_emotion_alegria():
#     assert detect_emotion("Estoy muy feliz y contento") == "alegría"

# def test_detect_emotion_tristeza():
#     assert detect_emotion("Me siento mal y triste") == "tristeza"

# def test_detect_emotion_enojo():
#     assert detect_emotion("Estoy furioso y molesto") == "enojo"

# def test_detect_emotion_miedo():
#     assert detect_emotion("Tengo mucho miedo de esto") == "miedo"

# def test_detect_emotion_neutral():
#     assert detect_emotion("El clima está soleado") == "neutral"


# # --- Pruebas para el endpoint /talk y la creación de historial.json ---

# def test_talk_creates_history_file():
#     response = client.post("/talk", json={"text": "Hola mundo feliz"})
#     assert response.status_code == 200
#     assert os.path.exists(HISTORY_FILE)

#     with open(HISTORY_FILE, "r") as f:
#         history = json.load(f)
#     assert len(history) == 1
#     interaction = history[0]
#     assert interaction["user_text"] == "Hola mundo feliz"
#     assert interaction["detected_emotion"] == "alegría"
#     assert "timestamp" in interaction
#     assert "ai_response" in interaction

# def test_talk_appends_to_history():
#     client.post("/talk", json={"text": "Primer mensaje feliz"})
#     client.post("/talk", json={"text": "Segundo mensaje triste"})

#     with open(HISTORY_FILE, "r") as f:
#         history = json.load(f)
#     assert len(history) == 2
#     assert history[0]["user_text"] == "Primer mensaje feliz"
#     assert history[0]["detected_emotion"] == "alegría"
#     assert history[1]["user_text"] == "Segundo mensaje triste"
#     assert history[1]["detected_emotion"] == "tristeza"

# def test_talk_empty_input():
#     response = client.post("/talk", json={"text": ""})
#     assert response.status_code == 400
#     with open(HISTORY_FILE, "r") as f: # Verificar que el historial no se modificó o se mantuvo vacío
#         history = json.load(f)
#         assert len(history) == 0

# def test_talk_whitespace_input():
#     response = client.post("/talk", json={"text": "   "})
#     assert response.status_code == 400
#     with open(HISTORY_FILE, "r") as f:
#         history = json.load(f)
#         assert len(history) == 0

# # --- Pruebas para detect_emotional_patterns ---

# def test_pattern_no_history():
#     assert detect_emotional_patterns([]) is None

# def test_pattern_short_history(sample_history_short):
#     assert detect_emotional_patterns(sample_history_short) is None
#     assert detect_emotional_patterns(sample_history_short, num_interactions_to_check=2, recurrence_threshold=3) is None


# def test_pattern_sad_pattern_detected(sample_history_sad_pattern):
#     expected_message = "He notado que te has sentido 'tristeza' con frecuencia últimamente (en 3 de las últimas 5 interacciones)."
#     assert detect_emotional_patterns(sample_history_sad_pattern) == expected_message

# def test_pattern_no_clear_pattern(sample_history_mixed_less_than_threshold):
#     assert detect_emotional_patterns(sample_history_mixed_less_than_threshold) is None

# def test_pattern_neutral_pattern_if_dominant(sample_history_neutral):
#     history_mostly_neutral = [
#         {"timestamp": "t1", "user_text": "n1", "detected_emotion": "neutral", "ai_response": "..."} ,
#         {"timestamp": "t2", "user_text": "n2", "detected_emotion": "neutral", "ai_response": "..."} ,
#         {"timestamp": "t3", "user_text": "s1", "detected_emotion": "tristeza", "ai_response": "..."} ,
#         {"timestamp": "t4", "user_text": "n3", "detected_emotion": "neutral", "ai_response": "..."} ,
#         {"timestamp": "t5", "user_text": "a1", "detected_emotion": "alegría", "ai_response": "..."}
#     ]
#     expected_message = "He notado que te has sentido 'neutral' con frecuencia últimamente (en 3 de las últimas 5 interacciones)."
#     assert detect_emotional_patterns(history_mostly_neutral) == expected_message

# def test_pattern_custom_thresholds():
#     history = [
#         {"timestamp": "t1", "user_text": "m1", "detected_emotion": "miedo", "ai_response": "..."} ,
#         {"timestamp": "t2", "user_text": "m2", "detected_emotion": "miedo", "ai_response": "..."} ,
#         {"timestamp": "t3", "user_text": "o1", "detected_emotion": "otro", "ai_response": "..."}
#     ]
#     expected_message = "He notado que te has sentido 'miedo' con frecuencia últimamente (en 2 de las últimas 3 interacciones)."
#     assert detect_emotional_patterns(history, num_interactions_to_check=3, recurrence_threshold=2) == expected_message
#     assert detect_emotional_patterns(history, num_interactions_to_check=3, recurrence_threshold=3) is None


# # --- Pruebas de integración: /talk con detección de patrones ---

# def test_talk_reports_pattern_in_response():
#     initial_history = [
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=20)).isoformat(), "user_text": "sad 1", "detected_emotion": "tristeza", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(), "user_text": "happy", "detected_emotion": "alegría", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(), "user_text": "sad 2", "detected_emotion": "tristeza", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(), "user_text": "ok", "detected_emotion": "neutral", "ai_response": "..."}
#     ]
#     with open(HISTORY_FILE, "w") as f:
#         json.dump(initial_history, f)

#     response = client.post("/talk", json={"text": "Me siento muy triste hoy también"})
#     assert response.status_code == 200
#     data = response.json()

#     assert data["detected_emotion"] == "tristeza"
#     assert "ai_response" in data
#     expected_pattern_msg = "He notado que te has sentido 'tristeza' con frecuencia últimamente (en 3 de las últimas 5 interacciones)."
#     assert data["emotional_pattern_detected"] == expected_pattern_msg

#     with open(HISTORY_FILE, "r") as f:
#         history = json.load(f)
#     assert len(history) == 5
#     assert history[-1]["user_text"] == "Me siento muy triste hoy también"

# def test_talk_no_pattern_in_response_if_none_detected():
#     initial_history = [
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=20)).isoformat(), "user_text": "sad 1", "detected_emotion": "tristeza", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(), "user_text": "happy", "detected_emotion": "alegría", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(), "user_text": "angry", "detected_emotion": "enojo", "ai_response": "..."} ,
#         {"timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(), "user_text": "fear", "detected_emotion": "miedo", "ai_response": "..."}
#     ]
#     with open(HISTORY_FILE, "w") as f:
#         json.dump(initial_history, f)

#     response = client.post("/talk", json={"text": "Hoy me siento genial y feliz"})
#     assert response.status_code == 200
#     data = response.json()

#     assert data["detected_emotion"] == "alegría"
#     assert "ai_response" in data
#     assert "emotional_pattern_detected" not in data

#     with open(HISTORY_FILE, "r") as f:
#         history = json.load(f)
#     assert len(history) == 5
#     assert history[-1]["user_text"] == "Hoy me siento genial y feliz"

# def test_root_endpoint():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"message": "Bienvenido a la API de IA Emocional. Usa la ruta POST /talk para interactuar."}

# ```
