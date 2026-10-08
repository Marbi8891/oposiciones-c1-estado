-- Índice derivado. La fuente de verdad son los JSON/JSONL de data/.
CREATE TABLE bloque (id TEXT PRIMARY KEY, romano TEXT, nombre TEXT);
CREATE TABLE tema (id TEXT PRIMARY KEY, bloque_id TEXT REFERENCES bloque(id), numero INTEGER, titulo_oficial TEXT);
CREATE TABLE epigrafe (id TEXT PRIMARY KEY, tema_id TEXT REFERENCES tema(id), padre_id TEXT, numero TEXT, titulo TEXT,
                       fuente_id TEXT, pagina_ini INTEGER, pagina_fin INTEGER);
CREATE TABLE concepto (id TEXT PRIMARY KEY, epigrafe_id TEXT REFERENCES epigrafe(id), nombre TEXT, tipo TEXT, modo TEXT,
                       importancia TEXT, cita_textual TEXT, fuente_id TEXT, pagina INTEGER);
CREATE TABLE fuente (id TEXT PRIMARY KEY, tipo TEXT, titulo TEXT, ruta TEXT, sha256 TEXT, fecha TEXT, nota TEXT);
CREATE TABLE estado_declarado (tema_id TEXT PRIMARY KEY REFERENCES tema(id), estado TEXT, dominio_declarado INTEGER,
                               primera_pasada TEXT, test_resuelto TEXT);
CREATE TABLE pregunta (id TEXT, version INTEGER, tema_id TEXT REFERENCES tema(id), epigrafe_id TEXT, concepto_id TEXT,
                       dificultad INTEGER, enunciado TEXT, correcta TEXT, fuente_id TEXT REFERENCES fuente(id),
                       norma_articulo TEXT, fecha_validacion TEXT, estado TEXT, origen TEXT,
                       PRIMARY KEY (id, version));
CREATE TABLE flashcard (id TEXT, version INTEGER, tema_id TEXT REFERENCES tema(id), concepto_id TEXT, tipo TEXT,
                        fuente_id TEXT, estado TEXT, PRIMARY KEY (id, version));
CREATE TABLE respuesta (id TEXT PRIMARY KEY, pregunta_id TEXT, pregunta_version INTEGER, sesion_id TEXT, marcada TEXT,
                        acierto INTEGER, confianza TEXT, tiempo_ms INTEGER, fecha TEXT);
CREATE TABLE alerta (id TEXT PRIMARY KEY, tipo TEXT, titulo TEXT, estado TEXT, creada TEXT);
CREATE TABLE alerta_pregunta (alerta_id TEXT REFERENCES alerta(id), pregunta_id TEXT);
CREATE TABLE verificacion (id TEXT PRIMARY KEY, norma TEXT, articulo TEXT, estado TEXT, url TEXT, fecha_consulta TEXT);
CREATE TABLE resumen (tema_id TEXT PRIMARY KEY REFERENCES tema(id), ruta TEXT);
CREATE TABLE auditoria (id TEXT PRIMARY KEY, fecha TEXT, actor TEXT, accion TEXT, entidad TEXT, motivo TEXT);
