import unittest

from c1 import progreso
from c1.store import Store
from tests.util import DATOS_REALES, copia_datos


def r(qid, acierto, confianza, fecha):
    return {"id": f"RSP-{fecha}", "pregunta_id": qid, "pregunta_version": 1, "marcada": "a",
            "acierto": acierto, "confianza": confianza, "fecha": fecha}


class ProgresoTest(unittest.TestCase):
    def test_sin_respuestas_no_hay_evidencia_ni_dominio_mayor_que_1(self):
        p = progreso.calcular(Store(DATOS_REALES))
        self.assertEqual(p["respuestas_evaluadas"], 0)
        self.assertLessEqual(max(t["dominio"] for b in p["bloques"] for t in b["temas"]), 1)
        self.assertIn("SIN EVIDENCIA", progreso.texto(p))

    def test_leer_da_1_y_no_mas(self):
        self.assertEqual(progreso.dominio_tema(True, []), 1)
        self.assertEqual(progreso.dominio_tema(False, []), 0)

    def test_clasificacion_de_respuestas(self):
        self.assertEqual(progreso.clasificar(r("q", True, "seguro", "1")), "ACIERTO REAL")
        self.assertEqual(progreso.clasificar(r("q", True, "dudoso", "1")), "ACIERTO POR DUDAS")
        self.assertEqual(progreso.clasificar(r("q", True, "azar", "1")), "ACIERTO POR AZAR")
        self.assertEqual(progreso.clasificar(r("q", False, "seguro", "1")), "ERROR")

    def test_aciertos_por_azar_o_duda_no_suben_dominio(self):
        rs = [r("q", True, "azar", f"2026-10-0{i}") for i in range(1, 6)]
        rs += [r("q", True, "dudoso", f"2026-10-1{i}") for i in range(1, 6)]
        self.assertEqual(progreso.dominio_tema(True, rs), 1)

    def test_niveles_2_y_3_exigen_aciertos_reales(self):
        self.assertEqual(progreso.dominio_tema(True, [r("q", True, "seguro", "2026-10-01")]), 2)
        cinco = [r("q", True, "seguro", f"2026-10-0{i}") for i in range(1, 6)]
        self.assertEqual(progreso.dominio_tema(True, cinco), 3)

    def test_nunca_pasa_de_3_en_fase_0(self):
        muchas = [r("q", True, "seguro", f"2026-10-{i:02d}") for i in range(1, 30)]
        self.assertEqual(progreso.dominio_tema(True, muchas), 3)

    def test_respuestas_registradas_cuentan_en_el_tema(self):
        store, tmp = copia_datos()
        with tmp:
            store.append("eventos/respuestas.jsonl", r("Q-000001", True, "seguro", "2026-10-07"))
            p = progreso.calcular(store)
            t = next(t for b in p["bloques"] for t in b["temas"] if t["id"] == "B1-T01")
            self.assertEqual(t["dominio"], 2)
            self.assertEqual(p["clases_respuesta"], {"ACIERTO REAL": 1})

    def test_temas_con_material_sin_estado(self):
        p = progreso.calcular(Store(DATOS_REALES))
        self.assertEqual(p["sin_estado_con_material"], ["B4-T01", "B4-T02", "B4-T03"])
