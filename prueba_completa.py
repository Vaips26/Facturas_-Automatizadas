import pdfplumber
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

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
                    "proveedor": {"type": "string", "description": "Empresa o institucion que emite el documento"},
                    "fecha_emision": {"type": "string", "description": "Fecha en que se emitio o imprimio el documento, formato YYYY-MM-DD"},
                    "fecha_limite_pago": {"type": "string", "description": "Fecha limite de pago si existe, formato YYYY-MM-DD"},
                    "folio": {"type": "string", "description": "Numero de folio, cuenta o referencia, si existe"},
                    "total": {"type": "number", "description": "Monto TOTAL A PAGAR final, el numero mas relevante para el cliente"},
                    "periodo": {"type": "string", "description": "Periodo que cubre el cobro, si aplica (ej. servicios como luz o agua)"},
                    "tipo_documento": {"type": "string", "description": "Tipo de documento: factura, recibo de servicios, ticket de compra, etc."}
                },
                "required": ["proveedor", "total"]
            }
        }
    }
]

ruta_pdf = "recibo1.pdf"
texto = extraer_texto_pdf(ruta_pdf)

respuesta = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Eres un asistente que extrae datos estructurados de facturas y recibos. El texto puede venir desordenado porque salio de un PDF con tablas. Identifica el monto TOTAL A PAGAR real (ignora montos de periodos anteriores o historicos). Usa siempre la herramienta extraer_datos_factura."},
        {"role": "user", "content": f"Extrae los datos de este documento:\n\n{texto}"}
    ],
    tools=herramienta_extraccion,
    tool_choice={"type": "function", "function": {"name": "extraer_datos_factura"}}
)

mensaje = respuesta.choices[0].message

if mensaje.tool_calls:
    datos = json.loads(mensaje.tool_calls[0].function.arguments)
    print(json.dumps(datos, indent=2, ensure_ascii=False))
else:
    print("El modelo no devolvio datos estructurados:")
    print(mensaje.content)