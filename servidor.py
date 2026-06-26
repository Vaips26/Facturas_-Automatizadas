from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import pdfplumber
import os
import json
import sqlite3
import shutil
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Permite que el frontend de React (en otro puerto) le hable a este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción esto se restringe al dominio real del frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

CARPETA_UPLOADS = "uploads"
RUTA_DB = "facturas.db"
os.makedirs(CARPETA_UPLOADS, exist_ok=True)


def inicializar_db():
    conexion = sqlite3.connect(RUTA_DB)
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_archivo TEXT,
            proveedor TEXT,
            fecha_emision TEXT,
            fecha_limite_pago TEXT,
            folio TEXT,
            total REAL,
            periodo TEXT,
            tipo_documento TEXT,
            fecha_procesado TEXT
        )
    """)
    conexion.commit()
    conexion.close()


inicializar_db()


def extraer_texto_pdf(ruta):
    with pdfplumber.open(ruta) as pdf:
        texto = ""
        for pagina in pdf.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto += texto_pagina + "\n"
    return texto


herramienta_extraccion = [
    {
        "type": "function",
        "function": {
            "name": "extraer_datos_factura",
            "description": "Extrae los datos estructurados de una factura, recibo o aviso de cobro",
            "parameters": {
                "type": "object",
                "properties": {
                    "proveedor": {"type": "string"},
                    "fecha_emision": {"type": "string", "description": "Formato YYYY-MM-DD"},
                    "fecha_limite_pago": {"type": "string", "description": "Formato YYYY-MM-DD, si existe"},
                    "folio": {"type": "string"},
                    "total": {"type": "number", "description": "Monto TOTAL A PAGAR final"},
                    "periodo": {"type": "string"},
                    "tipo_documento": {"type": "string"}
                },
                "required": ["proveedor", "total"]
            }
        }
    }
]


def extraer_datos_con_ia(texto):
    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Eres un asistente que extrae datos estructurados de facturas y recibos. El texto puede venir desordenado porque salio de un PDF con tablas. Identifica el monto TOTAL A PAGAR real (ignora montos de periodos anteriores o historicos). TODAS las fechas debes devolverlas estrictamente en formato YYYY-MM-DD (ejemplo: 2026-05-14), sin excepcion. Usa siempre la herramienta extraer_datos_factura."},
            {"role": "user", "content": f"Extrae los datos de este documento:\n\n{texto}"}
        ],
        tools=herramienta_extraccion,
        tool_choice={"type": "function", "function": {"name": "extraer_datos_factura"}}
    )
    mensaje = respuesta.choices[0].message
    if mensaje.tool_calls:
        return json.loads(mensaje.tool_calls[0].function.arguments)
    raise ValueError("La IA no devolvio datos estructurados")


def guardar_factura(datos, nombre_archivo):
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO facturas
        (nombre_archivo, proveedor, fecha_emision, fecha_limite_pago, folio, total, periodo, tipo_documento, fecha_procesado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nombre_archivo,
        datos.get("proveedor"),
        datos.get("fecha_emision"),
        datos.get("fecha_limite_pago"),
        datos.get("folio"),
        datos.get("total"),
        datos.get("periodo"),
        datos.get("tipo_documento"),
        datetime.now().isoformat(timespec="seconds")
    ))
    conexion.commit()
    factura_id = cursor.lastrowid
    conexion.close()
    return factura_id


@app.post("/procesar-factura")
async def procesar_factura(archivo: UploadFile = File(...)):
    if not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    ruta_temporal = os.path.join(CARPETA_UPLOADS, archivo.filename)
    with open(ruta_temporal, "wb") as buffer:
        shutil.copyfileobj(archivo.file, buffer)

    try:
        texto = extraer_texto_pdf(ruta_temporal)
        if not texto.strip():
            raise HTTPException(status_code=422, detail="No se pudo extraer texto del PDF (¿es una imagen escaneada?)")

        datos = extraer_datos_con_ia(texto)
        factura_id = guardar_factura(datos, archivo.filename)

        return {"id": factura_id, **datos}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la factura: {str(e)}")


@app.get("/facturas")
async def listar_facturas():
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    filas = conexion.execute("SELECT * FROM facturas ORDER BY id DESC").fetchall()
    conexion.close()
    return [dict(fila) for fila in filas]


@app.get("/facturas/exportar")
async def exportar_facturas():
    conexion = sqlite3.connect(RUTA_DB)
    df = pd.read_sql_query("SELECT * FROM facturas ORDER BY id DESC", conexion)
    conexion.close()

    ruta_excel = "facturas_exportadas.xlsx"
    df.to_excel(ruta_excel, index=False)

    return FileResponse(
        ruta_excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="facturas.xlsx"
    )


@app.get("/")
async def home():
    return {"status": "Servidor de facturas corriendo"}