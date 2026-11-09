# Registro concurrente con Cassandra + Astra DB + FastAPI

## Requisitos
- Python 3.10 o superior.
- Una base de datos Astra DB activa.
- Application Token y Secure Connect Bundle (SCB).

## 1. Preparar Astra DB
1. Crea una base de datos en Astra DB.
2. En el panel de la base, crea o selecciona un keyspace.
3. Descarga el Secure Connect Bundle (archivo ZIP).
4. Genera un Application Token con permisos de lectura/escritura sobre la base.
5. En CQL Console, selecciona el keyspace y ejecuta `cql/crear_tabla.cql`.

Nota: Astra DB Serverless administra los keyspaces desde su panel; no intentes crear uno con `CREATE KEYSPACE` en CQL Console.

## 2. Ejecutar localmente
En la carpeta del proyecto:

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\activate
```

Linux/macOS:
```bash
source .venv/bin/activate
```

Instala dependencias:
```bash
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y completa sus valores. Coloca el ZIP descargado en la raíz del proyecto (o cambia la ruta en `ASTRA_DB_SECURE_BUNDLE_PATH`).

PowerShell:
```powershell
$env:ASTRA_DB_APPLICATION_TOKEN="AstraCS:TU_TOKEN"
$env:ASTRA_DB_SECURE_BUNDLE_PATH="secure-connect-tu-db.zip"
$env:ASTRA_DB_KEYSPACE="tu_keyspace"
uvicorn main:app --reload
```

Abre http://127.0.0.1:8000

## 3. Publicar en GitHub
No subas el token ni el Secure Connect Bundle. Ambos están excluidos por `.gitignore`.
Sube el contenido del proyecto a un repositorio GitHub.

## 4. Desplegar en Render
Crea un Web Service conectado al repositorio:
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

En Environment agrega:
- `ASTRA_DB_APPLICATION_TOKEN`: tu Application Token.
- `ASTRA_DB_KEYSPACE`: nombre exacto del keyspace.
- `ASTRA_DB_SECURE_BUNDLE_PATH`: `/etc/secrets/secure-connect.zip`

En la sección Secret Files de Render, sube el Secure Connect Bundle con el nombre:
`secure-connect.zip`

Despliega y abre la URL pública que Render genere.

## 5. Prueba concurrente y verificación
Pide a tus compañeros que abran la misma URL y envíen el formulario en el momento acordado.
Después, en Astra CQL Console, ejecuta:

```sql
SELECT id, nombre, fecha FROM usuarios;
```

Para una práctica pequeña:
```sql
SELECT COUNT(*) FROM usuarios;
```

`COUNT(*)` puede ser costoso en tablas grandes; úsalo solo para esta demostración.
El tiempo que muestra la web es el tiempo de respuesta de la operación de inserción observado por el backend, no una medición aislada del tiempo interno de Cassandra.

## Endpoints
- `GET /`: formulario web.
- `POST /api/usuarios`: registra un nombre.
- `GET /health`: comprueba conexión con Astra DB.
- `GET /docs`: documentación automática de FastAPI.
