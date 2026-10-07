import unittest
from collections import Counter
from pathlib import Path

from c1.importar import chuleta
from tests.util import store_vacio

FIXTURE = Path(__file__).parent / "fixtures" / "chuleta_mini.html"


class ImportarChuletaTest(unittest.TestCase):
    def setUp(self):
        self.store, self.tmp = store_vacio()
        self.resultado = chuleta.importar(FIXTURE, self.store)
        self.preguntas = self.store.preguntas()

    def tearDown(self):
        self.tmp.cleanup()

    def test_cantidades_y_estado(self):
        self.assertEqual(self.resultado, {"resumenes": 1, "preguntas": 5, "flashcards": 1})
        self.assertEqual({q["estado"] for q in self.preguntas}, {"en_revision"})

    def test_referencia_posicional_no_se_rebaraja(self):
        q = next(q for q in self.preguntas if q["origen"]["num"] == 4)
        self.assertEqual(list(q["opciones"].values()), q["origen"]["opciones_originales"])
        self.assertEqual(q["correcta"], "c")

    def test_rebarajado_reproducible(self):
        store2, tmp2 = store_vacio()
        with tmp2:
            chuleta.importar(FIXTURE, store2)
            self.assertEqual([q["opciones"] for q in store2.preguntas()], [q["opciones"] for q in self.preguntas])

    def test_rebarajar_mantiene_orden_relativo(self):
        self.assertEqual(chuleta.rebarajar(["A", "B", "C", "D"], "b", "d"), ["A", "C", "D", "B"])

    def test_posiciones_equilibradas(self):
        self.assertEqual(set(Counter(chuleta.posiciones_equilibradas(20, "x")).values()), {5})

    def test_duplicado_anotado(self):
        q = next(q for q in self.preguntas if q["origen"]["num"] == 5)
        self.assertTrue(any("duplicado de Q-000001" in m for m in q["revision"]))

    def test_resumen_marcado_como_no_original(self):
        texto = self.store.path("resumenes/B1-T01.md").read_text(encoding="utf-8")
        self.assertIn("no es el temario original", texto)

    def test_cada_escritura_audita(self):
        acciones = Counter(e["accion"] for e in self.store.events("eventos/auditoria.jsonl"))
        self.assertEqual(acciones["importar_preguntas"], 1)
        self.assertEqual(acciones["importar_resumen"], 1)
        self.assertEqual(acciones["importar_flashcards"], 1)
