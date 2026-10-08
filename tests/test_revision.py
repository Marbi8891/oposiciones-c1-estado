import unittest

from c1.revision import anotar, buscar_pregunta, marcar_revision
from c1.store import Store
from tests.util import DATOS_REALES, copia_datos


class InterinoVerificadoTest(unittest.TestCase):
    """Caso real: la clave del plazo del interino se contrastó con el BOE (07/10/2026)."""

    def setUp(self):
        self.store = Store(DATOS_REALES)

    def test_verificacion_con_fuente_oficial(self):
        verif = self.store.read("normas/verificaciones.json")[0]
        self.assertEqual(verif["articulo"], "art. 10.1.d")
        self.assertTrue(verif["fuente"]["url"].startswith("https://www.boe.es/"))
        self.assertEqual(verif["fuente"]["fecha_consulta"], "2026-10-07")
        self.assertIn("nueve meses", verif["texto_literal"])

    def test_las_dos_claves_coinciden_con_el_boe_y_siguen_en_revision(self):
        for archivo, num in (("T01_Bloque_IV_test.md", 7), ("T03_Bloque_IV_test.md", 2)):
            q = buscar_pregunta(self.store, archivo=archivo, num=num)
            self.assertIn("9 meses", q["opciones"][q["correcta"]])
            self.assertEqual(q["estado"], "en_revision")
            self.assertTrue(any("VER-0001" in m for m in q["revision"]))

    def test_sin_alertas_abiertas(self):
        self.assertEqual(self.store.alertas(), [])


class MarcasDeRevisionTest(unittest.TestCase):
    def test_marcar_cambia_estado_no_contenido_y_audita(self):
        store, tmp = copia_datos()
        with tmp:
            antes = next(q for q in store.preguntas() if q["id"] == "Q-000001")
            n = len(store.events("eventos/auditoria.jsonl"))
            marcar_revision(store, "Q-000001", "prueba")
            despues = next(q for q in store.preguntas() if q["id"] == "Q-000001")
            self.assertEqual(despues["estado"], "marcada_revision")
            for campo in ("enunciado", "opciones", "correcta", "version"):
                self.assertEqual(antes[campo], despues[campo])
            ev = store.events("eventos/auditoria.jsonl")
            self.assertEqual(len(ev), n + 1)
            self.assertEqual((ev[-1]["accion"], ev[-1]["entidad"]), ("marcar_revision", "Q-000001"))

    def test_anotar_no_cambia_estado(self):
        store, tmp = copia_datos()
        with tmp:
            q = anotar(store, "Q-000002", "nota")
            self.assertEqual(q["estado"], "en_revision")

    def test_alerta_enlaza_preguntas(self):
        store, tmp = copia_datos()
        with tmp:
            a = store.crear_alerta({"tipo": "prueba", "titulo": "t", "preguntas": ["Q-000003"]}, motivo="test")
            self.assertEqual(a["id"], "ALR-0001")
            self.assertEqual(store.alertas()[0]["estado"], "abierta")
