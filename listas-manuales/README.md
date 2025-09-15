
# Parte 4 — Procesamiento de Listas Manuales



## Proveedor: Anaerobicos

### Pasos realizados

1. **Importación del archivo original**
   - Se cargó el archivo provisto en Google Sheets.
   - Configuración regional ajustada a **Argentina**.

2. **Limpieza inicial**
   - Se eliminaron columnas irrelevantes (como `Variación`).
   - Se eliminaron filas vacías usando un **filtro**.
   - Se eliminaron colores de fondo y formatos heredados del archivo original.

3. **Normalización de campos**
   - **Código (columna E):** extracción del número inicial con `REGEXEXTRACT`.
   - **Producto (columna F):** copiado tal cual desde el campo original.
   - **DESC (columna G):** se eliminaron números iniciales y espacios con `REGEXREPLACE` y `TRIM`.
   - **Precios (columnas H e I):** se limpiaron con `SUSTITUIR` para quitar `$`, espacios y separadores incorrectos, luego se convirtieron en valores numéricos.
   - Formato aplicado: `#.##0,00` (punto como separador de miles, coma como separador decimal).
   - **Código de barras (columna J):** se eliminaron caracteres especiales (`$`, puntos, comas, decimales) con `REGEXREPLACE`, quedando solo la secuencia numérica.

4. **Reorganización y hoja limpia**
   - Los datos finales se copiaron y pegaron como **valores** en una nueva hoja en blanco, sin fórmulas.
   - Se eliminaron formatos residuales, dejando solo texto y números planos.

5. **Cabeceras**
   - Se agregaron headers en la fila 1 con los nombres requeridos:
     - `Código`
     - `Producto`
     - `DESC`
     - `Precio Público IVA Incluido`
     - `Precio Minorista sin IVA`
     - `Código de barras`

6. **Validación**
   - Verificación de que todos los campos numéricos se muestran con dos decimales.
   - Confirmación de que las filas vacías ya no están presentes.
   - Confirmación de que no quedaron colores o formatos extraños.

7. **Resultado final**
   - Archivo limpio y formateado, listo para ser exportado como `.csv` o `.xlsx`.
   - Ubicado en la carpeta `finales/` bajo el nombre `pegamil_listado.csv` (o similar).

---

## Herramientas utilizadas
- Google Sheets:
  - Funciones: `ARRAYFORMULA`, `REGEXEXTRACT`, `REGEXREPLACE`, `TRIM`, `SUSTITUIR`, `VALOR`, `TEXTO`.
  - Filtro para eliminar filas vacías.
  - Pegado especial → valores para eliminar fórmulas.
- Limpieza manual de colores y formatos.
- Creación de una hoja nueva para consolidar los datos finales.

---

## Observaciones
- Algunos campos venían con formato de moneda en vez de número → se corrigió al limpiar los caracteres y aplicar formato numérico personalizado.
- Los códigos de barras podían aparecer como `$ 7,790,711,000,491.00` → se limpiaron con `REGEXREPLACE` para obtener solo los dígitos.



## Proveedor: Hurl (ejemplo con CSV)

### Pasos realizados

1. **Subida del archivo**
   - Se subió el archivo original `.csv` a **Google Sheets** (Archivo → Importar → Subir).  
   - Se verificó la configuración regional: **Argentina**.

2. **Limpieza inicial**
   - Se eliminaron columnas innecesarias.  
   - Se eliminaron filas vacías mediante **filtro**.  
   - Se limpiaron colores de fondo y formatos heredados.  
   - Se copió el contenido en una hoja nueva, limpia.

3. **Normalización de campos**
   - **Código**: extracción del valor numérico inicial con `REGEXEXTRACT`.  
   - **Producto**: copiado tal cual desde el archivo original.  
   - **Descripción (DESC)**: eliminación del código y espacios iniciales con `REGEXREPLACE` + `TRIM`.  
   - **Precios**:  
     - Limpieza de símbolos `$`, espacios y separadores con `SUSTITUIR`.  
     - Conversión a número con `VALOR`.  
     - Formateo con separador de miles (`.`) y decimales con coma (`,`) → `#.##0,00`.  
     - Truncado a enteros con `TRUNCAR` para generar precios finales.  
   - **Códigos de barras**: limpieza de caracteres especiales (`$`, puntos, comas, `.00`) con `REGEXREPLACE`, quedando solo dígitos.

4. **Consolidación**
   - Los resultados de fórmulas se copiaron y pegaron como **valores** en una nueva columna.  
   - Se eliminaron las columnas de fórmulas intermedias para dejar solo datos planos.  
   - Se verificó que todos los precios y códigos de barras quedaran como valores puros.

5. **Cabeceras**
   - Se agregaron headers claros en la fila 1:  
     - `Código`  
     - `Producto`  
     - `DESC`  
     - `Precio Público IVA Incluido`  
     - `Precio Minorista sin IVA`  
     - `Código de barras`  

6. **Formato adicional**
   - Se aplicaron reglas de **colores alternos** en toda la hoja usando **Formato condicional**.  
   - Patrón aplicado: un color verde claro en filas pares, celeste en filas impares.  
   - El header quedó con color propio fijo.

7. **Exportación**
   - Archivo final preparado, limpio y formateado.  
   - Exportado como `.csv` o `.xlsx`, sin fórmulas y con cabeceras correctas.  

---

## Herramientas utilizadas
- Google Sheets:
  - Funciones: `ARRAYFORMULA`, `REGEXEXTRACT`, `REGEXREPLACE`, `TRIM`, `SUSTITUIR`, `VALOR`, `TEXTO`, `TRUNCAR`.
  - Filtros para eliminar filas vacías.
  - Pegado especial → valores para eliminar fórmulas.
  - Formato condicional → colores alternos por fila.
- Limpieza manual de colores y formatos.
- Creación de hoja nueva para consolidar los datos finales.

---

## Observaciones
- Los precios se normalizaron a números con formato argentino.  
- Los códigos de barras se limpiaron para mostrar solo dígitos puros.  
- Se eliminó todo formato heredado del archivo original, quedando solo datos + cabeceras.  
- Se aplicó color alterno para mejorar la legibilidad del documento final.
