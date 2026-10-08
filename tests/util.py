import shutil
import tempfile
from pathlib import Path

from c1.store import REPO, Store

DATOS_REALES = REPO / "data"


def copia_datos():
    """Copia de data/ para pruebas que escriben; devuelve (Store, tmpdir)."""
    tmp = tempfile.TemporaryDirectory()
    destino = Path(tmp.name) / "data"
    shutil.copytree(DATOS_REALES, destino)
    return Store(destino), tmp


def store_vacio():
    tmp = tempfile.TemporaryDirectory()
    return Store(Path(tmp.name) / "data"), tmp
