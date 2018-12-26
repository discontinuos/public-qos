# public-qos
Aplicación para el seguimiento de disponibilidad de sitios en Internet. Verifica a intervalos regulares una lista de dirección para averiguar su disponibilidad efectiva a lo largo del tiempo.

# Descripción
public-qos es una aplicación escrita en Python para el moniteo de disponibilidad de sitios web. Está diseñada para funcionar minimizando el consumo de recursos (procesador, red y disco rígido) dando un registro de las mediciones realizadas. 

El propósito de esta herramienta fue realizar una medición anual de calidad de servicios estatales para la escritura de un artículo académico. En consecuencia, sus premisas de diseño fueron:

1. La medición debía ser regular, homogénea y priorizar la validez de los resultados. El sitio controla su propia conectividad a interne antes de cada medición y generar registros separados de resultados y errores.
2. Debía poder ejecutarse en un ambiente 'neutral' (fuera de Argentina) y estable de bajo costo. Es decir, no era la intención  ejecutarse en la PC del investigador, dado que debía no reiniciarse ni sufrir problemas de conexión durante 1 año continuo. Se utilizó una cuenta gratuita de AWS (12 meses) con un cron de ejecución cada 60 segundos.
3. Debían poderse medir muchos sitios a la vez, sin que esto distorsione los resultados. Para esto la herramienta implementa un balanceo de carga y un manejo de timeouts para los pedidos lentos o sin respuesta. Incluso cuando mide cada 10 minutos cada sitio, reparte estos pedidos en ejecuciones cada 60 segundos.
4. Para registrar cada 10 minutos, durante 1 año, al menos 150 sitios, el uso de espacio debía ser optimizado (reducir la redundancia). Para esto el sitio genera archivos binarios consumiendo 3 bytes por cada medición en cada sitio (en ellos almacena el status de la respuesta y los milisegundos consumidos en el pedido).
5. Para poder monitorear los resultados parciales sin conectarse al ambiente de producción, la herramienta produce copias en espejo (externas) de los resultados parciales. Este objetivo mitigaba el hecho de que conectarse a producción podía afectar al registro de los datos, pudiéndose por ejemplo bloquear accidentalmente alguno de ellos al consultarlo. Para esto el sitio realiza automáticamente envíos de los binarios del mes hacia un servidor externo en los momentos en que no se encuentra monitoreando.

# Instalación y requerimientos
### Instalación
El sitio funciona como scripts de Python 3, sin requerir instalación de componentes o módulos externos. 

El idioma Python se eligió por su portabilidad y por su facilidad para el manejo de colas y threads. En cada medición los pedidos deben organizarse en paralelo (ej. verificar a la vez 10 sitios), con límites de pedidos simultáneos para no saturar la conexión.

### Ejecución (cron / job)
Para hacer funcionar la aplicación debe ejecutarse cada 1 minuto el script Main.py. A modo de prueba, se puede ejecutar este archivo en console, lo que producirá la ejecución de una medición. El cron o job deberá ejecutar con un runtime de Python 3 a Main.py:

    ej. @c:/python34/python c:/monitor/Main.py

### Actualización
En una instalación productiva, las nuevas versiones deben ponerse en la carpeta /next, de la cual el monitor copia los archivos de Python sobre el directorio principal. Este proceso buscar evitar que durante la copia manual de nuevos archivos .py se ejecute el monitor y ocurra una ejecución inválida por fuentes inconsistentes.

# Configuración
## config.ini
En el archivo viewer/config/config.ini se encuentran las opciones de configuración del monitoreo.

Para cada instalación se sugiere indicar un valor único para InstanceId (Ej. AR1, MIT). Esa clave identifica la instalación local frente a otras instalaciones, y permite administrar de manera clara los archivos de resultados.

En ese archivo pueden indicarse el valor para DefaultMinutesInterval, que marca cada cuánto debe monitorearse un sitio si en su detalle no se indica el intervalo.

### monitors.ini
Mantiene la lista de sitios a monitorear. Todas las entradas deben tener dos partes: la primera identificará al sitio (ej. Anses) y la segunda al contenido dentro de ese sitio representado por la URL (ej. Home). Cada entrada tiene sólo 1 dirección; para moniterear varios ítems de un mismo organismo o sitio deben crearse varias entradas. 
```
[Anses-Home]
Url=http://www.anses.gob.ar/
[Anses-Login]
Url=http://www.anses.gob.ar/login
```
### mirrors.ini
Indica si deben mantenerse copias externas de los resultados. Para ello se crean entradas en la forma:
```
[Aacademica]
Url=https://www.aacademica.org/monitorEndPoint.php
# Frequency = Daily [default] | Weekly.
Frequency = Daily
Key=xds5434345454ds
LastMonth=2016-12
```
En el destino debe estar el archivo monitorEndPoint.php que se ocupa de recibir los resultados en el mirror. El key es enviado a dicho archivo para validar el pedido como origen válido (debe elegirse un Key y replicarse en mirrors.ini y en monitorEndPoint.php).

# Resultados
Para poder analizar los resultados, es recomendable convertir los archivos binarios a archivos CSV. Esto puede realizarse por medio del script mon2csv.py:

  ej. @c:/python34/python/mon2csv.py c:/monitor/results/conit/home/conit-home#2016-12#1-0#r1.mon
  
Si se monitorea un conjunto de sitios, también puede realizarse masivamente la salida ejecutando el script folder2csv.py indicando la carpeta de resultados:

  ej. @c:/python34/python/folder2csv.py c:/monitor/results
  
Los archivos convertidos pueden ser analizados con herramientas de análisis de datos (R+, Excel, SPSS, etc). También pueden ser visualizados con un visualizador web (en PHP)  provisto por la herramienta. Este visualizador genera una vista tabulada poniendo la salida de folder2csv en /viewer/results.

En la carpeta /errors hay un log de errors. En la carpeta /logs se genera una línea por cada ejecución. 

# Consultas y sugerencias
Para consultas o sugerencias, escribir a pablodg@gmail.com.

# Más información
El proceso de ejecución del monitor puede resumirse en los siguientes pasos:
1. El monitor averigua primero qué cosas tiene para verificar. Para eso lee del archivo config/monitors.ini la lista de monitores que esté definida
  Los monitores tienen su nombre en dos partes, separados por un guión (por ejemplo CONICET-SIGEVA).
  
2. Para cada monitor tiene un intervalo (en minutos) y un offset. Estos parámetros están definidos por valores default (para todos los monitores) en el archivo config/config.ini, y pueden también especificarse para cada monitor. Si el intervalo es 10, se tomará una muestra cada 10 minutos. El offset sirve para distribuir los monitores en los diferentes minutos que tiene una hora. De esta forma, si el offset es 0, se tomará a las 0, 10, 20, etc. minutos de cada hora. Si el offset es 1, se tomará al minuto 1, 11, 21, etc. de cada hora. El offset default asigna en forma aleatoria a los monitores a lo largo de las mediciones, manteniendo estable el intervalo.

3. Antes de comenzar a medir, ejecute un test de respuesta para validar que el agente de medición tiene conexión a internet. Esto lo hace ejecutando un pedido hacia google.com. El resultado del mismo se almacena igual que los demás monitores. Si este monitor falla, los demás no son evaluados, registrándose para ellos el resultado OFFLINE, que representa que el punto de medición no tenía acceso a internet para ese momento en el tiempo.

4. Para todos los monitores que deben tomar su muestra en el minuto en ejecución, el monitor navega la url indicada. Para eso, ejecuta un pedido http o https y analiza la respuesta (el status de respuesta y una longitud mayor a cero). Si hay redirects, los sigue. Para hacer esta verificación, utiliza el timeout de http indicado en el archivo config/config.ini. Luego almacena el resultado en un archivo por mes y monitor, dentro de la carpeta /results. 
    Los archivos tienen un formato binario, con bloques de 3 bytes que almacenan el tiempo de respuesta (en un uint16 en milisegundos), y un byte con el código de la respuesta (resultado del código HTTP o tipo de error no http, ej. Timeout). 
     Ese archivo no almacena en forma explícita la hora de registro de cada muestra, ya que la posición de cada entrada se corresponde con su posición en el tiempo considerado desde el inicio del mes que registra. De este modo, el archivo con nombre CONICET-SIGEVA#2016-12#5-2#MN1#r1 registra los datos para el monitor de CONICET, url de SIGEVA, mes 12 del 2016, con intervalos de 5 minutos y un offset de 2. 
       En su contenido, en la primera posición habrá un registro de 3 bytes que da cuenta de la medición hecha el día 1 de diciembre de 2016 a las 0:02. La siguiente posición contiene los valores para el mismo día, con hora 0:07 (offset 2 más intervalo 5), y así sucesivamente. Los monitores se ejecutan utilizando threads en paralelo, encolándose luego de alcanzarse el máximo de threads indicados en config/config.ini. Se recomienda no utilizar una cantidad excesiva de threads para no saturar la conexión local y perjudicar la medición.

5. Una vez registrados los valores para el minuto activo, se verifica si corresponde actualizar los mirrors. Cada mirror contiene una copia de los resultados producidos por el monitor. En el archivo config/config.ini debe indicarse un valor para la entrada InstanceId que sirve para identificar el origen de los datos en el mirror de almacenamiento (cada agente de medición debe tener un InstanceId propio, ej. AR1 para un medidor en Argentina). 
  La lista de mirrors a mantener actualizados se encuentra en config/mirrors.ini. La frecuencia de actualización puede ser diaria o semanal. Si corresponde realizar la actualización, el monitor envía al servidor de storage (mirror) los datos de los monitores para el mes actual en un archivo zip, con los archivos de configuración y logs anexados. La url del mirror debe apuntar a una versión ejecutable del script monitorEndPoint.php diseñado para recibir los datos. En ese archivo es posible indicar un key que también se indica en el archivo mirrors.ini que se envía como parámetro a modo de token de acceso. Para evitar bloqueos sobre los archivos durante el envío de los datos, el monitor primero genera los zips para todos los mirrors, y luego envía secuencialmente los datos a cada servidor de mirroring.

6. Por último, el Monitor examina la carpeta local /next para copiar de ella una versión nueva del monitor sobre los archivos existentes en la carpeta principal.

# Agradecimientos
El diseño de esta herramienta se vio beneficiada por las charlas e intercambios con Rodrigo Queipo y con Manuel Aristarán en sus etapas iniciales. A ellos mis agradecimientos.
