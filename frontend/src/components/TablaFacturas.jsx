function TablaFacturas({ facturas, cargando, apiUrl }) {
  if (cargando) return <p>Cargando facturas...</p>;
  if (facturas.length === 0) return <p className="vacio">Aún no has subido ninguna factura.</p>;

  return (
    <div className="tabla-facturas">
      <div className="acciones-tabla">
        <a href={`${apiUrl}/facturas/exportar`} className="boton-exportar">⬇️ Exportar a Excel</a>
      </div>
      <table>
        <thead>
          <tr><th>Proveedor</th><th>Tipo</th><th>Fecha</th><th>Folio</th><th>Total</th></tr>
        </thead>
        <tbody>
          {facturas.map((f) => (
            <tr key={f.id}>
              <td>{f.proveedor}</td>
              <td>{f.tipo_documento || "—"}</td>
              <td>{f.fecha_emision || "—"}</td>
              <td>{f.folio || "—"}</td>
              <td>${Number(f.total).toLocaleString("es-MX", { minimumFractionDigits: 2 })}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TablaFacturas;