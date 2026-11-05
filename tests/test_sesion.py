import unittest

from c1 import progreso, sesion
from c1.revision import marcar_revision
from tests.util import copia_datos


class SesionTest(unittest.TestCase):
    def setUp(self):
        self.store, self.tmp = copia_datos()
        self.s = sesion.crear(self.store, temas=["B1-T05"], n=4, semilla=1)
        self.qs = {q["id"]: q for q in self.store.preguntas()}
        self.ids = [p["id"] for p in self.s["preguntas"]]

    def tearDown(self):
        self.tmp.cleanup()

    def _bien(self, i):
        return self.qs[self.ids[i]]["correcta"]

    def _mal(self, i):
        return next(l for l in "abcd" if l != self._bien(i))

    def test_crea_sin_soluciones(self):
        self.assertEqual(len(self.ids), 4)
        for q in sesion.enunciados(self.store, self.s):
            self.assertNotIn("correcta", q)
            self.assertEqual(q["tema_id"], "B1-T05")

    def test_excluye_preguntas_marcadas(self):
        marcar_revision(self.store, self.ids[0], "prueba")
        s2 = sesion.crear(self.store, temas=["B1-T05"], n=20)
        self.assertNotIn(self.ids[0], [p["id"] for p in s2["preguntas"]])

    def test_parsear(self):
        self.assertEqual(sesion.parsear("1a 2b? 3c* 4-"),
                         {1: ("a", "seguro"), 2: ("b", "dudoso"), 3: ("c", "azar"), 4: (None, "blanco")})
        with self.assertRaises(SystemExit):
            sesion.parsear("1e")

    def test_corregir_clasifica_y_abre_errores(self):
        texto = f"1{self._bien(0)} 2{self._bien(1)}? 3{self._mal(2)} 4-"
        r = sesion.corregir(self.store, self.s["id"], texto, minutos=5)
        self.assertEqual([f["clase"] for f in r["detalle"]],
                         ["ACIERTO REAL", "ACIERTO POR DUDAS", "ERROR", "EN BLANCO"])
        self.assertEqual((r["acierto_bruto_pct"], r["acierto_real_pct"]), (50, 25))
        errs = sesion.errores(self.store)
        self.assertEqual([(e["pregunta_id"], e["tipo"]) for e in errs], [(self.ids[2], None)])
        self.assertEqual(len(self.store.events("eventos/respuestas.jsonl")), 4)

    def test_no_se_corrige_dos_veces_ni_con_huecos(self):
        with self.assertRaises(SystemExit):
            sesion.corregir(self.store, self.s["id"], "1a 2b")
        sesion.corregir(self.store, self.s["id"], "1a 2a 3a 4a")
        with self.assertRaises(SystemExit):
            sesion.corregir(self.store, self.s["id"], "1b 2b 3b 4b")

    def test_clasificar_error_valida_tipo(self):
        sesion.corregir(self.store, self.s["id"], f"1{self._mal(0)} 2- 3- 4-")
        eid = sesion.errores(self.store)[0]["id"]
        with self.assertRaises(SystemExit):
            sesion.clasificar_error(self.store, eid, "Z", "x")
        sesion.clasificar_error(self.store, eid, "n", "Confundió 48 horas con 24", concepto="investidura: plazos")
        e = sesion.errores(self.store)[0]
        self.assertEqual((e["tipo"], e["concepto"]), ("N", "investidura: plazos"))

    def test_reincidencia_en_14_dias_y_ranking_de_temas(self):
        for _ in range(2):
            s = sesion.crear(self.store, temas=["B1-T05"], n=1, semilla=7)
            q = self.qs[s["preguntas"][0]["id"]]
            mal = next(l for l in "abcd" if l != q["correcta"])
            sesion.corregir(self.store, s["id"], f"1{mal}")
            eid = sesion.errores(self.store)[-1]["id"]
            sesion.clasificar_error(self.store, eid, "C", "x", concepto="Cuestión de confianza")
        inf = sesion.informe_errores(self.store, dias=14)
        self.assertEqual(inf["recurrentes_ultimos_dias"], {"cuestión de confianza": 2})
        self.assertEqual(inf["temas_peor_a_mejor"][0]["tema_id"], "B1-T05")
        self.assertEqual(inf["temas_peor_a_mejor"][0]["error_pct"], 100)

    def test_modo_errores_repite_solo_lo_fallado(self):
        sesion.corregir(self.store, self.s["id"], f"1{self._mal(0)} 2{self._bien(1)} 3- 4-")
        s2 = sesion.crear(self.store, modo="errores", n=20)
        self.assertEqual([p["id"] for p in s2["preguntas"]], [self.ids[0]])

    def test_el_progreso_usa_las_respuestas(self):
        sesion.corregir(self.store, self.s["id"], " ".join(f"{i + 1}{self._bien(i)}" for i in range(4)))
        p = progreso.calcular(self.store)
        t = next(t for b in p["bloques"] for t in b["temas"] if t["id"] == "B1-T05")
        self.assertEqual(t["dominio"], 2)  # 4 aciertos reales: aún no hay 5 para el nivel 3
        self.assertEqual(p["respuestas_evaluadas"], 4)
