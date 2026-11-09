import os
import time

from uuid import uuid4
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from astrapy import DataAPIClient

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from dotenv import load_dotenv


load_dotenv()

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):

    endpoint = os.getenv("ASTRA_DB_ENDPOINT")
    token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    keyspace = os.getenv("ASTRA_DB_KEYSPACE")

    # Conexión con Astra DB
    client = DataAPIClient()

    db = client.get_database(
        endpoint,
        token=token,
        keyspace=keyspace
    )

    # Definición de nuestra tabla
    definition = {
        "columns": {
            "id": {"type": "uuid"},
            "nombre": {"type": "text"},
            "fecha": {"type": "timestamp"}
        },
        "primaryKey": {
            "partitionBy": ["id"],
            "partitionSort": {}
        }
    }

    # Crear tabla si no existe
    db.create_table(
        "usuarios",
        definition=definition,
        if_not_exists=True
    )

    app.state.astra_client = client
    app.state.db = db
    app.state.usuarios = db.get_table("usuarios")

    print("Conectado correctamente a Astra DB")

    yield

    client.close()


app = FastAPI(lifespan=lifespan)

# Página principal
@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# Registrar usuario
@app.post("/api/usuarios")
def registrar_usuario(nombre: str = Form(...)):

    nombre = nombre.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="Escribe tu nombre."
        )

    if len(nombre) > 100:
        raise HTTPException(
            status_code=400,
            detail="Nombre demasiado largo."
        )

    registro = {
        "id": uuid4(),
        "nombre": nombre,
        "fecha": datetime.now(timezone.utc)
    }

    inicio = time.perf_counter()

    try:

        app.state.usuarios.insert_one(registro)

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail="Error al guardar en Astra DB."
        ) from exc

    tiempo = (time.perf_counter() - inicio) * 1000

    return {
        "mensaje": "Registro guardado correctamente",
        "id": str(registro["id"]),
        "nombre": nombre,
        "fecha": registro["fecha"].isoformat(),
        "tiempo_ms": round(tiempo, 2)
    }


# Comprobar conexión
@app.get("/health")
def health():

    try:
        app.state.db.list_table_names()

        return {
            "estado": "conectado",
            "keyspace": os.getenv("ASTRA_DB_KEYSPACE")
        }

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail="Error de conexión"
        ) from exc