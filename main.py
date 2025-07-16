from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from typing import List
import json
import uvicorn
from functools import lru_cache

# Modelo Pydantic para definir la estructura de los CUPS
class CupsCode(BaseModel):
    codigo_sin_puntos: str
    codigo_con_puntos: str
    descripcion: str
    trazabilidad: str

# Configuración de la app
app = FastAPI(
    title="API CUPS Colombia",
    description="API para consultar códigos CUPS",
    version="1.0.0"
)

# Cargar datos del JSON
@lru_cache()
def load_cups_data():
    try:
        with open("cups_limpio.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Archivo cups_limpio.json no encontrado")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error al leer el archivo JSON")

# Funciones auxiliares usadas por los endpoints

def get_all_cups():
    return load_cups_data()

def find_by_code(codigo: str):
    cups_data = get_all_cups()
    for item in cups_data:
        if item["codigo_sin_puntos"] == codigo or item["codigo_con_puntos"] == codigo:
            return item
    return None

def find_by_description(desc: str):
    cups_data = get_all_cups()
    for item in cups_data:
        if desc.lower() in item["descripcion"].lower():
            return item
    return None

# Endpoints

@app.get("/", summary="Información de la API")
async def root():
    return {
        "message": "API CUPS Colombia - Versión Simplificada",
        "version": "1.0.0",
        "endpoints": {
            "listado_paginado": "/cups",
            "buscar_por_codigo": "/cups/codigo/{codigo}",
            "buscar_por_descripcion": "/cups/descripcion/{descripcion}"
        },
        "documentacion": "/docs"
    }

@app.get("/cups", response_model=List[CupsCode], summary="Listado completo de códigos CUPS")
async def get_cups():
    return get_all_cups()

@app.get("/cups/codigo/{codigo}", response_model=CupsCode, summary="Buscar código CUPS específico")
async def get_cups_by_code(
    codigo: str = Path(..., description="Código CUPS con o sin puntos (ej: '010101' o '01.0.1.01')")
):
    codigo = codigo.strip()
    result = find_by_code(codigo)
    if not result:
        raise HTTPException(status_code=404, detail=f"Código CUPS '{codigo}' no encontrado")
    return result

@app.get("/cups/descripcion/{descripcion}", response_model=CupsCode, summary="Buscar código por descripción")
async def get_cups_by_description(
    descripcion: str = Path(..., description="Texto parcial o completo de la descripción del procedimiento")
):
    descripcion = descripcion.strip()
    result = find_by_description(descripcion)
    if not result:
        raise HTTPException(status_code=404, detail=f"No se encontró ningún código con la descripción que contenga '{descripcion}'")
    return result

# Ejecutar la app
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
