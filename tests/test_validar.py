import unittest

from tests.util import copia_datos
from c1.validar import validar


class ReglasDurasTest(unittest.TestCase):
    def _editar(self, store, cambio):
        lista = store.read("preguntas/B1-T01.json")
        cambio(lista[0])
        store.write("preguntas/B1-T01.json", lista, accion="test", entidad="test", motivo="test")

    def test_aprobada_sin_trazabilidad_es_error(self):
        store, tmp = copia_datos()
        with tmp:
            self._editar(store, lambda q: q.update(estado="aprobada"))
            errores = validar(store)["errores"]
            self.assertTrue(any("aprobada sin concepto_id" in e for e in errores), errores)

    def test_opciones_repetidas_es_error(self):
        store, tmp = copia_datos()
        with tmp:
            self._editar(store, lambda q: q["opciones"].update(d=q["opciones"]["a"]))
            self.assertTrue(any("repetidas" in e for e in validar(store)["errores"]))

    def test_fuente_inexistente_es_error(self):
        store, tmp = copia_datos()
        with tmp:
            self._editar(store, lambda q: q.update(fuente_id="SRC-INVENTADA-9999"))
            self.assertTrue(any("no registrada" in e for e in validar(store)["errores"]))

    def test_sesgo_de_posicion_avisa(self):
        store, tmp = copia_datos()
        with tmp:
            for p in store.glob("preguntas/*.json"):
                rel = p.relative_to(store.root).as_posix()
                lista = store.read(rel)
                for q in lista:
                    q["opciones"]["b"], q["opciones"][q["correcta"]] = q["opciones"][q["correcta"]], q["opciones"]["b"]
                    q["correcta"] = "b"
                store.write(rel, lista, accion="test", entidad="test", motivo="test")
            self.assertTrue(any("Sesgo de posición: la b" in a for a in validar(store)["avisos"]))
