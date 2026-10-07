import unittest
from collections import Counter

from c1.store import Store
from tests.util import DATOS_REALES


class ProgramaTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(DATOS_REALES)
        self.programa = self.store.read("programa.json")

    def test_45_temas_en_6_bloques(self):
        cuenta = {b["romano"]: len(b["temas"]) for b in self.programa["bloques"]}
        self.assertEqual(cuenta, {"I": 11, "II": 4, "III": 7, "IV": 9, "V": 6, "VI": 8})

    def test_ids_unicos_y_titulos_completos(self):
        ids = [t["id"] for b in self.programa["bloques"] for t in b["temas"]]
        self.assertEqual(len(ids), len(set(ids)))
        titulos = [t["titulo_oficial"] for b in self.programa["bloques"] for t in b["temas"]]
        self.assertFalse([t for t in titulos if "..." in t], "títulos abreviados")

    def test_programa_no_se_da_por_verificado(self):
        self.assertFalse(self.programa["verificado_contra_convocatoria"])

    def test_estado_declarado_conservado_sin_convertirse_en_evidencia(self):
        temas = self.store.read("estado_declarado.json")["temas"]
        self.assertEqual(len(temas), 22)
        self.assertEqual(Counter(t["dominio_declarado"] for t in temas.values()), Counter({2: 22}))
        self.assertEqual(temas["B1-T01"]["primera_pasada"], "2026-08-29")
