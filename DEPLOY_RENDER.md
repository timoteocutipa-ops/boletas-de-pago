# Despliegue en Render

## Estado actual

Este proyecto ya quedo preparado para Render con:

- `gunicorn` en `requirements.txt`
- `render.yaml` en la raiz del proyecto
- almacenamiento configurable por variable `DATA_DIR`

## Importante sobre los guardados

La app guarda registros en un archivo JSON. En Render, el filesystem normal es temporal.

Si quieres conservar los registros guardados despues de reinicios o nuevos deploys, agrega un disco persistente en Render con estos valores:

- Mount Path: `/var/data`
- Size: `1 GB` o mas

La variable `DATA_DIR` ya apunta a:

```text
/var/data/boletas
```

Entonces Render guardara el archivo en:

```text
/var/data/boletas/payroll_records.json
```

## Pasos para subirlo

1. Crear un repositorio en GitHub.
2. Subir esta carpeta `Boletas_de_Pago` al repositorio.
3. Entrar a Render y elegir `New +` -> `Blueprint`.
4. Conectar el repositorio de GitHub.
5. Confirmar el archivo `render.yaml`.
6. Crear el servicio.
7. Despues del primer deploy, abrir el servicio en Render y agregar el disco persistente en `Disks`.
8. Redeployar el servicio.

## Alternativa manual en Render

Si no usas `render.yaml`, crea un `Web Service` con:

- Environment: `Python`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
- Health Check Path: `/api/health`
- Environment Variable: `DATA_DIR=/var/data/boletas`

Y luego agrega el disco persistente con mount path `/var/data`.
