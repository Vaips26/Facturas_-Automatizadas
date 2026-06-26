import { useState, useRef } from "react";

function SubirFactura({ apiUrl, onProcesada }) {
  const [arrastrando, setArrastrando] = useState(false);
  const [procesando, setProcesando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const procesarArchivo = async (archivo) => {
    if (!archivo || !archivo.name.toLowerCase().endsWith(".pdf")) {
      setError("Solo se aceptan archivos PDF.");
      return;
    }
    setProcesando(true);
    setError(null);
    setResultado(null);

    const formData = new FormData();
    formData.append("archivo", archivo);

    try {
      const res = await fetch(`${apiUrl}/procesar-factura`, { method: "POST", body: formData });
      if (!res.ok) {
        const datosError = await res.json();
        throw new Error(datosError.detail || "Error procesando la factura");
      }
      const datos = await res.json();
      setResultado(datos);
      onProcesada();
    } catch (err) {
      setError(err.message);
    } finally {
      setProcesando(false);
    }
  };

  const manejarDrop = (e) => {
    e.preventDefault();
    setArrastrando(false);
    procesarArchivo(e.dataTransfer.files[0]);
  };

  return (
    <div className="subir-factura">
      <div
        className={`zona-drop ${arrastrando ? "arrastrando" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setArrastrando(true); }}
        onDragLeave={() => setArrastrando(false)}
        onDrop={manejarDrop}
        onClick={() => inputRef.current.click()}
      >
        <input ref={inputRef} type="file" accept=".pdf" style={{ display: "none" }}
          onChange={(e) => procesarArchivo(e.target.files[0])} />
        {procesando ? (
          <p>⏳ Procesando con IA, espera un momento...</p>
        ) : (
          <>
            <p className="icono">📤</p>
            <p>Arrastra un PDF aquí, o haz clic para elegir un archivo</p>
          </>
        )}
      </div>

      {error && <div className="aviso error">⚠️ {error}</div>}

      {resultado && (
        <div className="resultado-card">
          <h3>✅ Factura procesada</h3>
          <p><strong>Proveedor:</strong> {resultado.proveedor}</p>
          <p><strong>Total:</strong> ${resultado.total}</p>
          <p><strong>Fecha:</strong> {resultado.fecha_emision || "N/A"}</p>
          <p><strong>Tipo:</strong> {resultado.tipo_documento || "N/A"}</p>
        </div>
      )}
    </div>
  );
}

export default SubirFactura;