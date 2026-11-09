-- En Astra DB, primero crea/selecciona el keyspace desde el panel web.
-- Ejecuta este script dentro de ese keyspace:
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY,
    nombre TEXT,
    fecha TIMESTAMP
);

-- Verificar registros:
SELECT id, nombre, fecha FROM usuarios;
-- Para una práctica pequeña también puedes probar:
SELECT COUNT(*) FROM usuarios;
