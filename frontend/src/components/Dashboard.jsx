import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

function Dashboard({ facturas }) {
  if (facturas.length === 0) return <p className="vacio">Sube facturas para ver el dashboard.</p>;

  const totalGeneral = facturas.reduce((suma, f) => suma + Number(f.total || 0), 0);

  const porProveedor = {};
  facturas.forEach((f) => {
    const nombre = f.proveedor || "Desconocido";
    porProveedor[nombre] = (porProveedor[nombre] || 0) + Number(f.total || 0);
  });
  const datosProveedor = Object.entries(porProveedor).map(([proveedor, total]) => ({ proveedor, total }));

  return (
    <div className="dashboard">
      <div className="tarjetas-resumen">
        <div className="tarjeta">
          <p className="numero">{facturas.length}</p>
          <p className="etiqueta">Facturas procesadas</p>
        </div>
        <div className="tarjeta">
          <p className="numero">${totalGeneral.toLocaleString("es-MX", { minimumFractionDigits: 2 })}</p>
          <p className="etiqueta">Total acumulado</p>
        </div>
      </div>

      <h3>Total por proveedor</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={datosProveedor}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="proveedor" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="total" fill="#1d6f5e" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default Dashboard;