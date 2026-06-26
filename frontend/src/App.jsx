import { useState, useEffect } from "react";
import SubirFactura from "./components/SubirFactura";
import TablaFacturas from "./components/TablaFacturas";
import Dashboard from "./components/Dashboard";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [vista, setVista] = useState("subir");
  const [facturas, setFacturas] = useState([]);
  const [cargando, setCargando] = useState(false);

  const cargarFacturas = async () => {
    setCargando(true);
    try {
      const res = await fetch(`${API_URL}/facturas`);
      const datos = await res.json();
      setFacturas(datos);
    } catch (error) {
      console.error("Error cargando facturas:", error);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarFacturas();
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>📄 Facturas IA</h1>
        <p>Extracción automática de datos de facturas con IA</p>
      </header>

      <nav className="tabs">
        <button className={vista === "subir" ? "activo" : ""} onClick={() => setVista("subir")}>Subir factura</button>
        <button className={vista === "tabla" ? "activo" : ""} onClick={() => setVista("tabla")}>Facturas ({facturas.length})</button>
        <button className={vista === "dashboard" ? "activo" : ""} onClick={() => setVista("dashboard")}>Dashboard</button>
      </nav>

      <main className="contenido">
        {vista === "subir" && <SubirFactura apiUrl={API_URL} onProcesada={cargarFacturas} />}
        {vista === "tabla" && <TablaFacturas facturas={facturas} cargando={cargando} apiUrl={API_URL} />}
        {vista === "dashboard" && <Dashboard facturas={facturas} />}
      </main>
    </div>
  );
}

export default App;