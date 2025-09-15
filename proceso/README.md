# Automatización de Gestión de Listas de Precios

## Contexto

Actualmente, el proceso de gestión de listas de precios es manual y requiere de varias tareas repetitivas.  
Los proveedores envían las listas por email, el equipo debe revisar la casilla varias veces al día, crear manualmente una tarea en ClickUp con el archivo adjunto y notificar a través de Discord.  
Esto genera demoras, trabajo duplicado y poca trazabilidad.

## Objetivo

El objetivo de esta automatización es reducir las tareas manuales, minimizar los tiempos de espera y asegurar que todas las listas recibidas por correo queden registradas en ClickUp y notificadas automáticamente al equipo en Discord.

## Proceso Actual

1. Un proveedor envía una lista de precios por email.  
2. Una persona del equipo revisa el correo varias veces al día.  
3. Si hay un archivo adjunto, crea manualmente una tarjeta en ClickUp en la columna "Nueva Lista".  
4. Copia el archivo a Google Drive o lo adjunta directamente en la tarea.  
5. Luego avisa al equipo por Discord que llegó una nueva lista.  
6. Otra persona revisa ClickUp y toma la tarea para limpiar la lista y subirla a Boxer.

Este flujo es lento y depende totalmente de la intervención manual.

## Solución con n8n

Diseñé un workflow en **n8n** que automatiza este proceso:

- **Gmail Trigger**: monitorea la casilla de correo cada minuto en busca de mails con archivos adjuntos.  
- **Filter Attachments**: valida que el correo realmente tenga adjuntos.  
- **Gmail (Get)**: obtiene el contenido completo del mail y sus adjuntos.  
- **Edit Fields + Split Out + Merge**: preparan los datos de los adjuntos para su posterior carga.  
- **Google Drive**: guarda los archivos adjuntos automáticamente en una carpeta predefinida de Drive.  
- **ClickUp**: crea una tarea en la lista correspondiente y el link al archivo en Drive.  
- **Discord**: envía una notificación automática al canal de la organización indicando que hay una nueva lista y compartiendo los links directos a la tarea y al archivo.

## Beneficios

- El equipo ya no necesita revisar manualmente el correo.  
- Las tareas en ClickUp se generan solas y contienen toda la información necesaria.  
- Se centraliza la comunicación en Discord sin depender de avisos manuales.  
- El proceso completo es más rápido, eficiente y trazable.  

Con esta automatización, el equipo puede concentrarse en la **limpieza y preparación de las listas para Boxer**, en lugar de gastar tiempo en pasos administrativos.
