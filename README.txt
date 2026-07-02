# link para verlo: https://facturas-automatizadas.vercel.app/

#  Facturas IA — Extractor automático de datos con IA

Sube una factura o recibo en PDF y obtén sus datos clave extraídos automáticamente
(proveedor, fecha, total, conceptos) usando IA con salida estructurada garantizada.
Guarda todo en base de datos, muestra un dashboard, y exporta a Excel.

##  ¿Por qué este proyecto?
La captura manual de datos de facturas es una tarea repetitiva común en
administración/contabilidad. Esta app automatiza ese proceso de punta a punta.

##  Stack
- **Backend:** FastAPI + Python
- **IA:** Llama 3.3 70B vía Groq (function calling con salida JSON forzada)
- **Extracción de PDF:** pdfplumber
- **Base de datos:** SQLite
- **Frontend:** React + Recharts
- **Exportación:** Excel (pandas + openpyxl)

##  Arquitectura
[Aquí pego el diagrama]

##  Demo
[Aquí el GIF]

##  Instalación local
[backend y frontend, los comandos que ya usaste]

##  Limitaciones conocidas
- No soporta PDFs escaneados (imágenes sin texto extraíble) — requeriría OCR,
  fuera del alcance de esta versión.
- El demo público usa la capa gratuita de Groq, con límites de uso razonables.

##  Posibles mejoras futuras
- OCR para facturas escaneadas (Tesseract)
- Autenticación de usuarios
- Soporte multi-moneda

