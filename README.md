# PUBLIC-QOS
Aplicación para el seguimiento de disponibilidad de sitios en Internet.

# DETALLE
public-qos es una aplicación escrita en Python para el moniteo de disponibilidad de sitios web. Está diseñada para funcionar minimizando el consumo de recursos (procesador, red y disco rígido) dando un registro de las mediciones realizadas. El propósito de esta herramienta fue realizar una medición para la escritura de un artículo académica respecto a la disponibilidad de sitios estatales de la Argentina, por lo que sus premisas de diseño fueron:
- poder ejecutar en un ambiente 'neutral' (fuera de Argentina) de bajo costo. Se utilizó una cuenta gratuita de AWS (12 meses) con un cron de ejecución cada 60 segundos.
- poder medir muchos sitios a la vez, sin que esto distorsione los resultados. Para esto la herramienta implementa un balanceo de carga y un manejo de timeouts para los pedidos lentos o sin respuesta.
- poder registrar cada 10 minutos, durante 1 año, al menos 150 sitios utilizando un espacio de almacenamiento mínimo. Para esto el sitio genera archivos binarios consumiendo 2 bytes por cada medición (en ellos almacena el status de la respuesta y los milisegundos del roundtrip).
- poder mantener una copia en espejo (externa) de los resultados parciales. Este objetivo permitió monitorear los resultados parciales sin conectarse al ambiente de producción durante la medición. Conectarse a producción podría haber afectado archivos de datos, pudiéndose por  ejemplo bloquear accidentalmente alguno de ellos al consultarlo. Para esto el sitio realiza automáticamente envíos de los binarios del mes hacia un servidor externo, sin superponerse con los períodos de medición ni bloquear sus datos al replicarse.

# INSTALACIÓN Y REQUERIMIENTOS
El sitio funciona como scripts de Python 3, sin requerir la instalación (carpeta monitor)

# CONFIGURACION

## config.ini
En el archivo viewer/config/config.ini se encuentran las opciones de configuración del monitoreo.

Para cada instalación se sugiere indicar un valor único para InstanceId (Ej. AR1, MIT). Esa clave identifica la instalación local frente a otras instalaciones, y permite administrar de manera clara los archivos de resultados.

En ese archivo pueden indicarse el valor para DefaultMinutesInterval, que marca cada cuánto debe monitorearse un sitio si en su detalle no se indica el intervalo.

## monitors.ini
Mantiene la lista de sitios a monitorear. Todas las entradas deben tener dos partes: la primera identificará al sitio (ej. Anses) y la segunda al contenido dentro de ese sitio representado por la URL (ej. Home). Cada entrada tiene sólo 1 dirección; para moniterear varios ítems de un mismo organismo o sitio deben crearse varias entradas. 

[Anses-Home]
Url=http://www.anses.gob.ar/
[Anses-Login]
Url=http://www.anses.gob.ar/login

## mirrors.ini
Indica si debe mantenerse copias externas de los resultados. Para ello se crean entradas en la forma:

[Aacademica]
Url=https://www.aacademica.org/monitorEndPoint.php
# Frequency = Daily [default] | Weekly.
Frequency = Daily
Key=xds5434345454ds
LastMonth=2016-12

En el destino debe estar el archivo monitorEndPoint.php que se ocupa de recibir los resultados en el mirror. El key es enviado a dicho archivo para validar el pedido como origen válido (debe elegirse un Key y replicarse en mirrors.ini y en monitorEndPoint.php).

# CRON
Para hacer funcionar la aplicación debe ejecutarse cada 1 minuto el script Main.py. A modo de prueba, se puede ejecutar este archivo en console, lo que producirá la ejecución de una medición. El cron o job deberá ejecutar con runtime de Python 3 Main.py:

    ej. @c:/python34/python c:/monitor/Main.py

# RESULTADOS
Para poder analizar los resultados, es recomendable convertir los archivos binarios a archivos CSV. Esto puede realizarse por medio del script mon2csv.py:

  ej. @c:/python34/python/mon2csv.py c:/monitor/results/conit/home/conit-home#2016-12#1-0#r1.mon
  
Si se monitorea un conjunto de sitios, también puede realizarse masivamente la salida ejecutando el script folder2csv.py indicando la carpeta de resultados:

  ej. @c:/python34/python/folder2csv.py c:/monitor/results
  
Los archivos convertidos pueden ser analizados con herramientas de análisis de datos (R+, Excel, SPSS, etc). También pueden ser visualizados con un visualizador web (en PHP)  provisto por la herramienta. Este visualizador genera una vista tabulada poniendo la salida de folder2csv en /viewer/results.
