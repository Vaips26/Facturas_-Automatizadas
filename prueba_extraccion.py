from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# Texto de ejemplo (simula lo que sacaríamos de un PDF real con pdfplumber)
texto_factura_ejemplo = """
FERRETERIA EL TORNILLO FELIZ S.A. DE C.V.
RFC: FTF010203ABC
Fecha: 12/03/2026
Folio: A-4521

Cliente: Construcciones del Sureste SA de CV

Concepto                  Cantidad   Precio Unit.   Importe
Cemento gris 50kg              10        185.00      1,850.00
Varilla 3/8" 6m                  6        145.00        870.00
Pintura vinilica 19L              2        620.00      1,240.00

Subtotal:                                            3,960.00
IVA (16%):                                             633.60
Total:                                               4,593.60
"""

herramienta_extraccion = [
    {
        "type": "function",
        "function": {
            "name": "extraer_datos_factura",
            "description": "Extrae los datos estructurados de una factura o recibo a partir de su texto",
            "parameters": {
                "type": "object",
                "properties": {
                    "proveedor": {"type": "string", "description": "Nombre de la empresa que emite la factura"},
                    "fecha": {"type": "string", "description": "Fecha de la factura en formato YYYY-MM-DD"},
                    "folio": {"type": "string", "description": "Numero de folio o factura, si existe"},
                    "subtotal": {"type": "number"},
                    "iva": {"type": "number"},
                    "total": {"type": "number", "description": "Monto total de la factura"},
                    "conceptos": {
                        "type": "array",
                        "description": "Lista de productos o servicios facturados",
                        "items": {
                            "type": "object",
                            "properties": {
                                "descripcion": {"type": "string"},
                                "cantidad": {"type": "number"},
                                "precio_unitario": {"type": "number"},
                                "importe": {"type": "number"}
                            }
                        }
                    }
                },
                "required": ["proveedor", "fecha", "total"]
            }
        }
    }
]

respuesta = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Eres un asistente que extrae datos estructurados de facturas. Usa siempre la herramienta extraer_datos_factura, nunca respondas en texto libre."},
        {"role": "user", "content": f"Extrae los datos de esta factura:\n\n{texto_factura_ejemplo}"}
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