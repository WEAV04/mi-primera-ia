import unittest
import os
import json
import datetime
from modules.memoria_emocional import (
    registrar_emocion,
    leer_historial,
    detectar_patrones_simples,
    HISTORIAL_FILE,
    EMOCIONES_VALIDAS
)

class TestMemoriaEmocional(unittest.TestCase):

    def setUp(self):
        """Configura un entorno limpio para cada prueba."""
        self.default_historial_backup = None
        if os.path.exists(HISTORIAL_FILE):
            # Hacer backup si existe para no interferir con datos reales
            with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f_read:
                self.default_historial_backup = f_read.read()
        # Asegurar que el archivo de historial esté vacío o no exista al inicio de cada prueba
        if os.path.exists(HISTORIAL_FILE):
            os.remove(HISTORIAL_FILE)
        # Crear un archivo de historial vacío para las pruebas
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

    def tearDown(self):
        """Restaura el archivo de historial original después de cada prueba."""
        if os.path.exists(HISTORIAL_FILE):
            os.remove(HISTORIAL_FILE)
        if self.default_historial_backup:
            with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f_write:
                f_write.write(self.default_historial_backup)
        elif os.path.exists(HISTORIAL_FILE): # Si se creó uno nuevo y no había backup
            os.remove(HISTORIAL_FILE)


    def test_registrar_emocion_valida(self):
        """Prueba registrar una emoción válida."""
        timestamp_before = datetime.datetime.now()
        result = registrar_emocion("alegría", 0.8, "Hoy fue un gran día", "celebración")
        self.assertTrue(result)

        historial = leer_historial()
        self.assertEqual(len(historial), 1)
        entrada = historial[0]
        self.assertEqual(entrada["emotion"], "alegría")
        self.assertEqual(entrada["intensity"], 0.8)
        self.assertEqual(entrada["source_text"], "Hoy fue un gran día")
        self.assertEqual(entrada["context"], "celebración")
        timestamp_entry = datetime.datetime.fromisoformat(entrada["timestamp"])
        self.assertTrue(timestamp_before <= timestamp_entry <= datetime.datetime.now())

    def test_registrar_emocion_invalida(self):
        """Prueba registrar una emoción no listada en EMOCIONES_VALIDAS."""
        result = registrar_emocion("euforia", 0.9, "Estoy en la cima del mundo", "éxtasis")
        self.assertFalse(result)
        historial = leer_historial()
        self.assertEqual(len(historial), 0)

    def test_registrar_intensidad_invalida(self):
        """Prueba registrar una emoción con intensidad fuera de rango."""
        result_mayor = registrar_emocion("tristeza", 1.5, "Muy mal", "malestar")
        self.assertFalse(result_mayor)
        result_menor = registrar_emocion("tristeza", -0.5, "Un poco mal", "ligero malestar")
        self.assertFalse(result_menor)
        historial = leer_historial()
        self.assertEqual(len(historial), 0)

    def test_leer_historial_vacio(self):
        """Prueba leer un historial vacío."""
        # setUp ya crea un historial.json vacío
        historial = leer_historial()
        self.assertEqual(historial, [])

    def test_leer_historial_con_datos(self):
        """Prueba leer un historial con varias entradas."""
        registrar_emocion("miedo", 0.7, "Examen mañana", "estrés")
        registrar_emocion("sorpresa", 0.5, "Regalo inesperado", "sorpresa agradable")
        historial = leer_historial()
        self.assertEqual(len(historial), 2)
        self.assertEqual(historial[0]["emotion"], "miedo")
        self.assertEqual(historial[1]["emotion"], "sorpresa")

    def test_leer_historial_no_existente(self):
        """Prueba leer si el archivo de historial no existe."""
        if os.path.exists(HISTORIAL_FILE):
            os.remove(HISTORIAL_FILE)
        historial = leer_historial()
        self.assertEqual(historial, []) # La función debe devolver [] si no encuentra el archivo

    def test_leer_historial_corrupto(self):
        """Prueba leer un archivo de historial con JSON corrupto."""
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            f.write("esto no es json valido {")
        historial = leer_historial()
        self.assertEqual(historial, []) # La función debe devolver [] si el JSON está corrupto

    def test_detectar_patrones_ninguno(self):
        """Prueba la detección de patrones cuando no hay ninguno."""
        registrar_emocion("alegría", 0.8, "Sol", "clima")
        registrar_emocion("neutral", 0.5, "Trabajo", "oficina")
        registrar_emocion("tristeza", 0.6, "Lluvia", "clima")
        historial = leer_historial()
        patron = detectar_patrones_simples(historial, "enojo", 2)
        self.assertIsNone(patron)

    def test_detectar_patron_simple_repeticion(self):
        """Prueba la detección de un patrón de repetición simple."""
        registrar_emocion("tristeza", 0.7, "Mal día", "general")
        registrar_emocion("alegría", 0.9, "Buenas noticias", "positivo")
        registrar_emocion("tristeza", 0.6, "Sigo mal", "persistente")
        registrar_emocion("tristeza", 0.8, "Muy triste hoy", "intenso")
        historial = leer_historial()

        patron = detectar_patrones_simples(historial, "tristeza", 3)
        self.assertIsNotNone(patron)
        self.assertEqual(patron["emocion"], "tristeza")
        self.assertEqual(patron["conteo"], 3)
        self.assertEqual(len(patron["eventos_recientes"]), 3)
        self.assertEqual(patron["eventos_recientes"][0]["source_text"], "Mal día") # El primero que se registró de los 3
        self.assertEqual(patron["eventos_recientes"][2]["source_text"], "Muy triste hoy") # El último

    def test_detectar_patron_con_ventana_tiempo_cumplida(self):
        """Prueba patrón con ventana de tiempo donde se cumple el patrón."""
        now = datetime.datetime.now()
        # Crear historial manualmente para controlar timestamps
        historial_manual = [
            {"timestamp": (now - datetime.timedelta(seconds=30)).isoformat(), "emotion": "enojo", "intensity": 0.7, "source_text": "txt1", "context": "c1"},
            {"timestamp": (now - datetime.timedelta(seconds=20)).isoformat(), "emotion": "alegría", "intensity": 0.7, "source_text": "txt2", "context": "c2"},
            {"timestamp": (now - datetime.timedelta(seconds=10)).isoformat(), "emotion": "enojo", "intensity": 0.8, "source_text": "txt3", "context": "c3"},
            {"timestamp": (now - datetime.timedelta(seconds=5)).isoformat(), "emotion": "enojo", "intensity": 0.9, "source_text": "txt4", "context": "c4"}, # Este es el más reciente referencial
        ]
        # Escribir este historial manual al archivo para que detectar_patrones lo lea
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(historial_manual, f)

        patron = detectar_patrones_simples(leer_historial(), "enojo", 2, ventana_tiempo_segundos=15) # Últimos 15 seg
        self.assertIsNotNone(patron)
        self.assertEqual(patron["emocion"], "enojo")
        # Debería encontrar los 2 últimos enojos (txt3 y txt4)
        self.assertEqual(patron["conteo"], 2)
        self.assertEqual(len(patron["eventos_recientes"]), 2)
        self.assertEqual(patron["eventos_recientes"][0]["source_text"], "txt3")
        self.assertEqual(patron["eventos_recientes"][1]["source_text"], "txt4")


    def test_detectar_patron_con_ventana_tiempo_no_cumplida(self):
        """Prueba patrón con ventana de tiempo donde NO se cumple el patrón por antigüedad."""
        now = datetime.datetime.now()
        historial_manual = [
            {"timestamp": (now - datetime.timedelta(seconds=100)).isoformat(), "emotion": "miedo", "intensity": 0.7, "source_text": "miedo antiguo", "context": "c1"},
            {"timestamp": (now - datetime.timedelta(seconds=80)).isoformat(), "emotion": "miedo", "intensity": 0.7, "source_text": "miedo menos antiguo", "context": "c2"},
            {"timestamp": (now - datetime.timedelta(seconds=10)).isoformat(), "emotion": "alegría", "intensity": 0.8, "source_text": "alegría reciente", "context": "c3"},
            {"timestamp": (now - datetime.timedelta(seconds=5)).isoformat(), "emotion": "miedo", "intensity": 0.9, "source_text": "miedo reciente", "context": "c4"},
        ]
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(historial_manual, f)

        # Buscamos 3 miedos en los últimos 60 segundos. Solo hay 1.
        patron = detectar_patrones_simples(leer_historial(), "miedo", 3, ventana_tiempo_segundos=60)
        self.assertIsNone(patron)

        # Buscamos 1 miedo en los últimos 60 segundos. Debería encontrar el más reciente.
        patron_uno = detectar_patrones_simples(leer_historial(), "miedo", 1, ventana_tiempo_segundos=60)
        self.assertIsNotNone(patron_uno)
        self.assertEqual(patron_uno["conteo"], 1)
        self.assertEqual(patron_uno["eventos_recientes"][0]["source_text"], "miedo reciente")


    def test_emociones_validas_constante(self):
        """Verifica que la constante EMOCIONES_VALIDAS exista y tenga elementos."""
        self.assertTrue(isinstance(EMOCIONES_VALIDAS, list))
        self.assertGreater(len(EMOCIONES_VALIDAS), 0)
        self.assertIn("neutral", EMOCIONES_VALIDAS)

if __name__ == '__main__':
    unittest.main()
