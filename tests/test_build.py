import unittest

from c1.build import build
from c1.store import Store
from tests.util import DATOS_REALES


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(DATOS_REALES)
        self.db = build(self.store)

    def test_recuentos_coinciden(self):
        q = self.db.execute
        self.assertEqual(q("SELECT COUNT(*) FROM tema").fetchone()[0], 45)
        self.assertEqual(q("SELECT COUNT(*) FROM pregunta").fetchone()[0], 500)
        self.assertEqual(q("SELECT COUNT(*) FROM flashcard").fetchone()[0], 165)

    def test_integridad_referencial(self):
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_cadena_pregunta_tema_bloque_fuente(self):
        fila = self.db.execute("""
            SELECT p.id, t.id AS tema, b.romano, f.tipo FROM pregunta p
            JOIN tema t ON t.id = p.tema_id JOIN bloque b ON b.id = t.bloque_id
            JOIN fuente f ON f.id = p.fuente_id WHERE p.id = 'Q-000001'""").fetchone()
        self.assertEqual((fila["tema"], fila["romano"], fila["tipo"]), ("B1-T01", "I", "resumen_propio"))

    def test_verificacion_indexada(self):
        fila = self.db.execute("SELECT norma, articulo, estado FROM verificacion").fetchone()
        self.assertEqual(tuple(fila), ("Real Decreto Legislativo 5/2015 (TREBEP)", "art. 10.1.d", "VERIFICADO VIGENTE"))
