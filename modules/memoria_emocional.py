import json
import datetime

HISTORIAL_FILE = "historial.json"
EMOCIONES_VALIDAS = ["alegría", "tristeza", "enojo", "miedo", "sorpresa", "neutral"]

def registrar_emocion(emocion: str, intensidad: float, source_text: str, context: str = None):
    """
    Registra un nuevo evento emocional en el historial.

    Args:
        emocion (str): La emoción detectada. Debe ser una de las EMOCIONES_VALIDAS.
        intensidad (float): La intensidad de la emoción (0.0 a 1.0).
        source_text (str): El texto del usuario que originó la emoción.
        context (str, optional): Un breve resumen o palabras clave del input. Defaults to None.

    Returns:
        bool: True si el registro fue exitoso, False en caso contrario.
    """
    if emocion not in EMOCIONES_VALIDAS:
        print(f"Error: Emoción '{emocion}' no es válida.")
        return False

    if not 0.0 <= intensidad <= 1.0:
        print(f"Error: Intensidad '{intensidad}' debe estar entre 0.0 y 1.0.")
        return False

    nueva_entrada = {
        "timestamp": datetime.datetime.now().isoformat(),
        "emotion": emocion,
        "intensity": intensidad,
        "source_text": source_text,
        "context": context if context else ""
    }

    try:
        historial = []
        try:
            with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
                historial = json.load(f)
        except FileNotFoundError:
            # Si el archivo no existe, empezamos con una lista vacía (ya debería estar creado, pero es una salvaguarda)
            pass
        except json.JSONDecodeError:
            # Si el archivo está corrupto o vacío, empezamos de nuevo para no perder el nuevo dato.
            # Considerar una mejor estrategia para producción (ej. backup, error específico)
            print(f"Advertencia: {HISTORIAL_FILE} está corrupto o vacío. Se creará uno nuevo.")
            pass # Empezamos con historial = []

        historial.append(nueva_entrada)

        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)

        return True

    except IOError as e:
        print(f"Error al escribir en {HISTORIAL_FILE}: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado al registrar emoción: {e}")
        return False

if __name__ == '__main__':
    # Ejemplos de uso (para prueba rápida)
    print("Probando el registro de emociones...")
    registrar_emocion("alegría", 0.8, "Hoy me siento genial, todo salió bien!", "éxito laboral")
    registrar_emocion("tristeza", 0.6, "He recibido una mala noticia.", "noticia negativa")
    registrar_emocion("enojo", 0.9, "¡No puedo creer que esto haya pasado de nuevo!", "frustración repetida")
    registrar_emocion("miedo", 0.7, "Tengo una presentación importante mañana y estoy nervioso.", "presentación importante")
    registrar_emocion("sorpresa", 0.5, "¡Vaya! No me esperaba esto para nada.", "evento inesperado")
    registrar_emocion("neutral", 0.3, "El día está nublado.", "observación climática")

    # Prueba de emoción inválida
    registrar_emocion("euforia", 0.9, "Estoy eufórico", "celebración")
    # Prueba de intensidad inválida
    registrar_emocion("alegría", 1.5, "Demasiado feliz", "exceso")

    print(f"\nContenido de {HISTORIAL_FILE} después de los registros:")
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            print(f.read())
    except FileNotFoundError:
        print(f"{HISTORIAL_FILE} no encontrado.")
    print(f"\nContenido de {HISTORIAL_FILE} después de los registros:")
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            print(f.read())
    except FileNotFoundError:
        print(f"{HISTORIAL_FILE} no encontrado.")
    print("\n--- Fin de pruebas de registro ---")


def leer_historial():
    """
    Lee y devuelve todo el historial de emociones desde el archivo JSON.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario es un evento emocional.
              Devuelve una lista vacía si el archivo no existe o hay un error.
    """
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            historial = json.load(f)
        return historial
    except FileNotFoundError:
        print(f"Advertencia: El archivo {HISTORIAL_FILE} no fue encontrado. Devolviendo historial vacío.")
        return []
    except json.JSONDecodeError:
        print(f"Error: El archivo {HISTORIAL_FILE} está corrupto o no es un JSON válido. Devolviendo historial vacío.")
        return []
    except Exception as e:
        print(f"Error inesperado al leer {HISTORIAL_FILE}: {e}")
        return []

if __name__ == '__main__':
    # Ejemplos de uso (para prueba rápida)
    print("Probando el registro de emociones...")
    # ... (registros anteriores se mantienen para la prueba)
    # Asegurémonos de que el archivo exista para las pruebas de lectura
    if not registrar_emocion("alegría", 0.8, "Hoy me siento genial, todo salió bien!", "éxito laboral"):
        print("Error al registrar la primera emoción de prueba para leer_historial.")
    else:
        # Añadimos más para tener algo que leer
        registrar_emocion("tristeza", 0.6, "He recibido una mala noticia.", "noticia negativa")
        registrar_emocion("enojo", 0.9, "¡No puedo creer que esto haya pasado de nuevo!", "frustración repetida")

    # Prueba de emoción inválida
    registrar_emocion("euforia", 0.9, "Estoy eufórico", "celebración")
    # Prueba de intensidad inválida
    registrar_emocion("alegría", 1.5, "Demasiado feliz", "exceso")

    print(f"\nContenido de {HISTORIAL_FILE} después de los registros (re-leído para verificar):")
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            print(f.read())
    except FileNotFoundError:
        print(f"{HISTORIAL_FILE} no encontrado.")
    print("\n--- Fin de pruebas de registro ---")

    print("\nProbando leer_historial()...")
    historial_leido = leer_historial()
    if historial_leido:
        print(f"Se leyeron {len(historial_leido)} entradas del historial.")
        print("Última entrada leída:", historial_leido[-1] if historial_leido else "N/A")
    else:
        print("El historial está vacío o no se pudo leer.")

    # Simular un archivo corrupto para probar la robustez de leer_historial()
    print("\nProbando leer_historial() con archivo corrupto...")
    with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
        f.write("esto no es json")
    historial_corrupto = leer_historial()
    print(f"Lectura de historial corrupto devolvió: {historial_corrupto} (debería ser [])")

    # Restaurar un historial válido para futuras pruebas si es necesario
    with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f) # Dejarlo vacío para la próxima prueba
    registrar_emocion("neutral", 0.2, "Archivo restaurado para pruebas.", "sistema")
    print(f"Archivo {HISTORIAL_FILE} restaurado con una entrada neutral.")
    print("\n--- Fin de pruebas de lectura ---")


def detectar_patrones_simples(historial_emociones: list, emocion_objetivo: str, umbral_conteo: int, ventana_tiempo_segundos: int = None):
    """
    Detecta patrones simples como la repetición de una emoción específica.

    Args:
        historial_emociones (list): Lista de eventos emocionales del historial.
        emocion_objetivo (str): La emoción específica a buscar (ej: "tristeza").
        umbral_conteo (int): Número mínimo de veces que la emoción debe aparecer para ser considerada un patrón.
        ventana_tiempo_segundos (int, optional): Si se proporciona, solo considera las emociones dentro de
                                                 los últimos N segundos desde la más reciente. Defaults to None (considera todo el historial).

    Returns:
        dict: Un diccionario con información sobre el patrón detectado, o None si no se detecta.
              Ejemplo: {"patron": "repeticion_emocion", "emocion": "tristeza", "conteo": 4, "eventos": [...lista_eventos...]}
    """
    if not historial_emociones:
        return None

    ahora = datetime.datetime.fromisoformat(historial_emociones[-1]["timestamp"])

    eventos_relevantes = []
    for evento in reversed(historial_emociones): # Procesar desde el más reciente
        if evento["emotion"] == emocion_objetivo:
            if ventana_tiempo_segundos:
                timestamp_evento = datetime.datetime.fromisoformat(evento["timestamp"])
                if (ahora - timestamp_evento).total_seconds() > ventana_tiempo_segundos:
                    break # Salir si el evento es más antiguo que la ventana de tiempo
            eventos_relevantes.append(evento)

    if len(eventos_relevantes) >= umbral_conteo:
        return {
            "patron": f"repeticion_emocion_{emocion_objetivo}",
            "emocion": emocion_objetivo,
            "conteo": len(eventos_relevantes),
            "eventos_recientes": list(reversed(eventos_relevantes[:umbral_conteo])) # Los más recientes que cumplen el umbral
        }
    return None

if __name__ == '__main__':
    # ... (pruebas anteriores se mantienen)

    print("\n--- Fin de pruebas de registro ---")

    print("\nProbando leer_historial()...")
    # ... (pruebas de leer_historial se mantienen)
    print("\n--- Fin de pruebas de lectura ---")

    print("\nProbando detectar_patrones_simples()...")
    # Limpiar y preparar historial para pruebas de patrones
    with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

    # Escenario 1: No hay patrón
    registrar_emocion("alegría", 0.8, "Día soleado", "clima")
    registrar_emocion("neutral", 0.5, "Reunión de trabajo", "trabajo")
    historial_actual = leer_historial()
    patron = detectar_patrones_simples(historial_actual, "tristeza", 3)
    print(f"Patrón detectado (ninguno esperado): {patron}")
    assert patron is None

    # Escenario 2: Patrón de tristeza simple
    registrar_emocion("tristeza", 0.7, "Me siento un poco solo", "soledad")
    registrar_emocion("tristeza", 0.6, "Extraño a mis amigos", "nostalgia")
    registrar_emocion("alegría", 0.9, "Recibí una buena llamada", "social")
    registrar_emocion("tristeza", 0.8, "Otro día difícil", "dificultad")
    historial_actual = leer_historial()
    patron_tristeza = detectar_patrones_simples(historial_actual, "tristeza", 3)
    print(f"Patrón de tristeza detectado (3 eventos): {patron_tristeza}")
    assert patron_tristeza is not None
    assert patron_tristeza["emocion"] == "tristeza"
    assert patron_tristeza["conteo"] == 3

    # Escenario 3: Patrón con ventana de tiempo (no se cumple)
    # Simular que el primer evento de tristeza fue hace mucho
    historial_temporal = [
        {"timestamp": (datetime.datetime.now() - datetime.timedelta(seconds=700)).isoformat(), "emotion": "tristeza", "intensity": 0.5, "source_text": "ayer", "context": "ayer"},
        {"timestamp": (datetime.datetime.now() - datetime.timedelta(seconds=10)).isoformat(), "emotion": "tristeza", "intensity": 0.5, "source_text": "ahora", "context": "ahora"},
        {"timestamp": (datetime.datetime.now() - datetime.timedelta(seconds=5)).isoformat(), "emotion": "tristeza", "intensity": 0.5, "source_text": "ahora mismo", "context": "ahora mismo"},
    ]
    patron_ventana_fail = detectar_patrones_simples(historial_temporal, "tristeza", 3, ventana_tiempo_segundos=60)
    print(f"Patrón con ventana (no esperado por tiempo): {patron_ventana_fail}")
    assert patron_ventana_fail is None # Solo 2 eventos en los últimos 60 segundos

    # Escenario 4: Patrón con ventana de tiempo (se cumple)
    patron_ventana_ok = detectar_patrones_simples(historial_temporal, "tristeza", 2, ventana_tiempo_segundos=60)
    print(f"Patrón con ventana (esperado): {patron_ventana_ok}")
    assert patron_ventana_ok is not None
    assert patron_ventana_ok["conteo"] == 2 # Los 2 más recientes

    # Escenario 5: Patrón de otra emoción
    registrar_emocion("enojo", 0.9, "Esto es frustrante", "frustración")
    registrar_emocion("enojo", 0.8, "De nuevo lo mismo", "repetición")
    registrar_emocion("enojo", 0.95, "No puedo más", "límite")
    historial_actual = leer_historial() # Recargar con los nuevos enojos
    patron_enojo = detectar_patrones_simples(historial_actual, "enojo", 3)
    print(f"Patrón de enojo detectado (3 eventos): {patron_enojo}")
    assert patron_enojo is not None
    assert patron_enojo["emocion"] == "enojo"
    assert patron_enojo["conteo"] == 3

    print("\n--- Fin de pruebas de detección de patrones ---")

    print("\nPruebas finalizadas.")
