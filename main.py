from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# La URI (con usuario y contraseña) NO va en el código: se lee de la variable
# de entorno MONGO_URI, tanto en local como en Render.
client = MongoClient(os.environ["MONGO_URI"])
# Cambie por el nombre de su base de datos (el mismo de su usuario, ej. ISIS2304E...)
db = client["ISIS2304A30202620"]


@app.get("/")
def inicio():
    return {"estado": "API funcionando correctamente"}


@app.get('/bares/{bar_id}/comentarios')
def get_comentarios(bar_id: int):
    # {"_id": 0} evita devolver el ObjectId, que FastAPI no puede convertir a JSON
    comentarios = list(db["comentarios_bares"].find({"bar_id": bar_id}, {"_id": 0}))
    return comentarios


@app.post('/bares/{bar_id}/comentarios')
def post_comentario(bar_id: int, datos: dict):
    datos['bar_id'] = bar_id
    datos['fecha']  = datetime.now().isoformat()

    calificacion = datos.get("calificacion")
    if calificacion is not None and not (isinstance(calificacion, int) and 1 <= calificacion <= 5):
        raise HTTPException(status_code=400, detail="calificacion debe ser un entero entre 1 y 5")

    db["comentarios_bares"].insert_one(datos)
    return {'mensaje': 'Comentario guardado'}


@app.get('/bares/{bar_id}/eventos')
def get_eventos(bar_id: int):
    return list(db["eventos"].find({"bar_id": bar_id}, {"_id": 0}))


@app.post('/bares/{bar_id}/eventos')
def post_evento(bar_id: int, datos: dict):
    # `dict` (y no un modelo fijo) permite campos distintos según el tipo de evento
    if not datos.get("nombre"):
        raise HTTPException(status_code=400, detail="El campo 'nombre' es obligatorio")

    datos['bar_id'] = bar_id
    datos['fecha_creacion'] = datetime.now().isoformat()

    db["eventos"].insert_one(datos)
    return {'mensaje': 'Evento guardado'}
