# Desafío Data Entry — Automatización, ETL y Upload

## Objetivo
Automatizar la descarga de listas de precios, normalizarlas a un formato estándar y subir los archivos resultantes a una API.


## Instalación
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración
Crear un archivo `.env` en la raíz:
```
USER_ID=desafiodataentry
PASSWORD=desafiodataentrypass
```

## Cómo ejecutar
### Flujo completo
```bash
python automatizacion-web/main.py
```
Realiza: descarga de los 3 proveedores → procesamiento/estandarización → subida a la API.


## Detalle del flujo (main.py)
1. Inicializa WebDriver con carpeta `downloads/` relativa al proyecto.
2. Descarga:
   - AutoRepuestos Express
   - Mundo RepCar (login si corresponde, luego descarga)
   - Autofix (itera todas las marcas, descarga por marca, renombra con marca y timestamp)
3. Procesa y normaliza:
   - Columnas finales: `CODIGO`, `DESCRIPCION`, `MARCA`, `PRECIO`
   - `PRECIO` con punto como separador decimal
   - `DESCRIPCION` a máx. 100 caracteres
   - Mundo RepCar: `DESCRIPCION = Descripción + " - " + Rubro`
   - Autofix: unifica todas las marcas del día en un único `.xlsx`
   - Salidas del día:
     - `AutoRepuestos Express_YYYYMMDD.xlsx`
     - `Mundo RepCar_YYYYMMDD.xlsx`
     - `Autofix_YYYYMMDD.xlsx`
4. Sube a la API `POST https://desafio.somosait.com/api/upload/` con `form-data` campo `file`.

## Notas de implementación
- `driver.py` expone métodos con timeout por llamada (`click`, `type_in`, `get_text`, `check_visibility`, `check_existence`, `js_click`, `select_by_text`).
- Locators sin importar `By`: usar tuplas como `('ID', 'username')`.
- `wait_for_downloads` asegura que no haya `.crdownload` antes de continuar.
- `rename_with_timestamp` agrega `YYYYMMDD-HHMMSS`; corrige nombre de Mundo RepCar si baja mal; en Autofix agrega la marca al nombre.
- `files_processor.py` normaliza precios y descripciones, y genera los `.xlsx` finales del día en `downloads/`.
- `api_sender.py` sube sólo los archivos generados en la ejecución actual.

## Logs y salidas
- Logs: `automatizacion-web/output/logs/log_YYYY-MM-DD.log`
- Archivos descargados y finales: `automatizacion-web/downloads/`

## Proceso de descarga - Procesamiento - Envío a la API 

- El driver se inciializa con headless en false por defecto
- Una vez se obtiene, accede a la página con las distintas listas de precios
- Para la lista de AutoRepuestos Express simplemente hace click en el enlace de descarga, espera a que el archivo esté en la carpeta y le pasa el timestamp al nombre para diferenciarlo.
- Para la lista de Mundo RepCar, debe hacer click en el enlace y revisar si está logueado, si no lo está entonces se loguea, posteriormente hace click en el enlace de descarga y obtiene la lista, a la cual le cambia el nombre y agrega timestamp, ya que viene con el nombre de AutoRepuestos Express.
- Para la lista de Autofix, hace click en el enlace y revisa si ya sucedió el proceso de loguin. Una vez logueado, selecciona individualmente cada una de las marcas y descarga una por una las listas, espera a que aparezca y desaparezca el overlay, y pasa  a la siguiente. EL proceso d erenombrado es igual a los demás, solo que se le agrega la marca antes del timestamp. 
- Una vez descargadas todas las listas, se comienza a estandarizar los datos. 
- Las listas de Autofix se convierten en una y se agrega la marca a la columna correspondiente.
- Se envían las listas por api una por una y se notifica el estado de todo el proceso. 

## Nota de mejora futura. 

Como este challenge estaba orientado a la automatizacíon, decidí que todos los archivos se debían descargar utilizando el driver y desde la UI de la página, sin embargo considero mucho más efectivo hacerlo directamente desde los endpoints que se encuentran disponibles en la misma. 
De esta forma no tendríamos que esperar ningún overlay ni usariamos selenium casi para nada, lo cual sería menos costoso y más veloz y efectivo. 



