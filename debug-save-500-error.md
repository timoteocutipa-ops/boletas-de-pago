[OPEN] Debug Session: save-500-error

## Sintoma
- Al pulsar `Guardar`, la interfaz muestra `Error al guardar: Error HTTP 500`.

## Hipotesis Iniciales
1. El endpoint `/api/payroll-record` falla al abrir o escribir la base SQLite por ruta, permisos o archivos auxiliares.
2. El payload enviado desde frontend contiene campos no serializables o estructuras inesperadas y rompe el guardado.
3. La tabla `payroll_records` no se crea correctamente al arrancar el backend y el `INSERT` falla.
4. El servidor activo en `5001` no corresponde a la version actual del backend con la ruta de guardado.
5. El proceso Flask se cae o reinicia antes de completar la peticion `PUT`.

## Plan
- Reproducir el 500 con el backend correcto activo.
- Instrumentar el endpoint de guardado y la apertura de SQLite.
- Capturar evidencia antes y despues del fallo.
- Aplicar correccion minima basada en evidencia.

