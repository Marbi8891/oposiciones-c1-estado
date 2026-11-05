import unittest

from c1 import temario
from c1.store import Store
from tests.util import DATOS_REALES

PAGINAS = [
    "TEMA 05\n",
    "NORMAS LEGISLATIVAS DE REFERENCIA.\n- Constitución Española (Título IV)\n- Ley 50/1997 del\n  Gobierno.\n   2\n",
    " ÍNDICE DE CONTENIDOS\n\n1.   EL GOBIERNO Y LA\n     ADMINISTRACIÓN.\n     1.1 EL GOBIERNO.\n2.   EL PRESIDENTE.\n     2.1 NOMBRAMIENTO.\n  3\n",
    "EL GOBIERNO Y LA ADMINISTRACIÓN.\n1.1 El Gobierno.\nTexto del art. 97 de la CE.\n",
    "        EL PRESIDENTE.\nintroducción\n",
    "2.1 NOMBRAMIENTO.\nArt. 99: investidura.\n",
]


class IndiceTest(unittest.TestCase):
    def setUp(self):
        self.epigrafes, self.cuerpo = temario.indice(PAGINAS)
        temario.localizar_epigrafes(self.epigrafes, PAGINAS, self.cuerpo)
        self.por_num = {e["numero"]: e for e in self.epigrafes}

    def test_titulos_partidos_se_unen_y_no_absorben_el_cuerpo(self):
        self.assertEqual(self.por_num["1"]["titulo"], "EL GOBIERNO Y LA ADMINISTRACIÓN.")
        self.assertEqual(list(self.por_num), ["1", "1.1", "2", "2.1"])
        self.assertEqual(self.cuerpo, 4)

    def test_paginas_con_y_sin_numero_en_el_cuerpo(self):
        self.assertEqual([self.por_num[n]["pagina_ini"] for n in ("1", "1.1", "2", "2.1")], [4, 4, 5, 6])
        self.assertEqual(self.por_num["2"]["pagina_fin"], 6)

    def test_normas_de_referencia(self):
        self.assertEqual(temario.normas_referencia(PAGINAS),
                         ["Constitución Española (Título IV)", "Ley 50/1997 del Gobierno."])


class TemarioRealTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(DATOS_REALES)

    def test_doce_temas_cargados_con_hash_y_fecha(self):
        fuentes = [f for f in self.store.read("fuentes.json") if f["tipo"] == "temario_pdf"]
        self.assertEqual(len(fuentes), 12)
        self.assertEqual({f["tema_id"] for f in fuentes} - {f"B1-T{n:02d}" for n in range(1, 12)}, {"B2-T03"})
        for f in fuentes:
            self.assertEqual(len(f["sha256"]), 64)
            self.assertTrue(f["fecha_pdf"])

    def test_pdf_antiguo_lleva_aviso(self):
        t02 = next(f for f in self.store.read("fuentes.json") if f.get("tema_id") == "B1-T02" and f["tipo"] == "temario_pdf")
        self.assertIn("comprobar vigencia", t02["nota"])

    def test_texto_por_pagina_completo(self):
        datos = self.store.read("temario/B1-T05.json")
        paginas = self.store.events("temario/texto/B1-T05.jsonl")
        self.assertEqual(len(paginas), datos["paginas"])
        self.assertEqual([p["pagina"] for p in paginas], list(range(1, datos["paginas"] + 1)))

    def test_indice_sin_validar_y_con_paginas_ordenadas(self):
        for p in self.store.glob("temario/B*.json"):
            d = self.store.read(p.relative_to(self.store.root).as_posix())
            self.assertEqual(d["estado_indice"], "extraido_automaticamente")
            pags = [e["pagina_ini"] for e in d["epigrafes"] if e["pagina_ini"]]
            self.assertEqual(pags, sorted(pags), p.name)
            self.assertGreaterEqual(len(pags), len(d["epigrafes"]) - 1, p.name)

    def test_buscar_localiza_tema_epigrafe_y_pagina(self):
        r = temario.buscar(self.store, "art. 99", tema_id="B1-T05")
        self.assertEqual((r[0]["tema_id"], r[0]["pagina"]), ("B1-T05", 10))
        self.assertTrue(r[0]["epigrafe"].startswith("4.1"))
        self.assertIn("99", r[0]["fragmento"])

    def test_buscar_sin_resultado_no_inventa(self):
        self.assertEqual(temario.buscar(self.store, "artículo 9999 inexistente"), [])
