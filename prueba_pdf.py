import pdfplumber

with pdfplumber.open("recibo1.pdf") as pdf:
    texto_completo = ""
    for pagina in pdf.pages:
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto_completo += texto_pagina + "\n"

print("--- TEXTO EXTRAIDO ---")
print(texto_completo)
print("--- FIN ---")
print(f"\nTotal de caracteres extraidos: {len(texto_completo)}")