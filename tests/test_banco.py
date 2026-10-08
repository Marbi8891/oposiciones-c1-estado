import unittest
from collections import Counter

from c1.store import Store
from c1.validar import validar
from tests.util import DATOS_REALES


class BancoImportadoTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(DATOS_REALES)
        self.preguntas = self.store.preguntas()

    def test_cantidades(self):
        self.assertEqual(len(self.preguntas), 500)
        self.assertEqual(len(self.store.flashcards()), 165)
        self.assertEqual(len(self.store.glob("resumenes/*.md")), 25)

    def test_nada_importado_queda_aprobado(self):
        self.assertNotIn("aprobada", {q["estado"] for q in self.preguntas})
        self.assertNotIn("aprobada", {f["estado"] for f in self.store.flashcards()})

    def test_validacion_sin_errores(self):
        self.assertEqual(validar(self.store)["errores"], [])

    def test_trazabilidad_tema_y_fuente(self):
        temas = {t["id"] for b in self.store.read("programa.json")["bloques"] for t in b["temas"]}
        fuentes = {f["id"]: f for f in self.store.read("fuentes.json")}
        for q in self.preguntas:
            self.assertIn(q["tema_id"], temas)
            self.assertEqual(fuentes[q["fuente_id"]]["tipo"], "resumen_propio")

    def test_rebarajado_conserva_contenido_y_respuesta(self):
        for q in self.preguntas:
            o = q["origen"]
            self.assertEqual(sorted(q["opciones"].values()), sorted(o["opciones_originales"]))
            original = o["opciones_originales"]["abcd".index(o["correcta_original"])]
            self.assertEqual(q["opciones"][q["correcta"]], original, q["id"])

    def test_sesgo_de_posicion_corregido(self):
        for tema in {q["tema_id"] for q in self.preguntas}:
            reparto = Counter(q["correcta"] for q in self.preguntas if q["tema_id"] == tema)
            self.assertEqual(set(reparto.values()), {5}, tema)
        self.assertFalse([a for a in validar(self.store)["avisos"] if "Sesgo" in a])

    def test_duplicado_detectado(self):
        avisos = validar(self.store)["avisos"]
        self.assertTrue(any("exceso o acumulación de tareas" in a for a in avisos))
