# ¿Cuándo merece la pena una segunda lectura?

Se compararon tres formas de revisar las mismas 24 facturas sintéticas en euros. La primera lectura de cada PDF fue idéntica para las tres. Se contó cuántas veces el sistema aceptaba una factura que necesitaba revisión y cuántas veces le pedía a un gestor que revisara una factura correcta.

| Método | Casos que requerían revisión detectados | Facturas correctas enviadas a revisión | Coste estimado del modelo por factura |
| --- | ---: | ---: | ---: |
| Una lectura y comprobaciones en Python | 9 de 9 | 1 | 0,102 USD |
| Especialistas cuando hay dudas y revisión final | 9 de 9 | 0 | 0,237 USD |
| Dos especialistas y revisión final en todos los casos | 9 de 9 | 0 | 0,448 USD |

La diferencia fue un abono de dos páginas con dos tipos de IVA. El lector acertó los importes, pero señaló los dos tipos como incidencia. La revisión selectiva reconoció que ambos cuadraban. Evitar esa intervención humana costó unos 3,23 USD adicionales en el conjunto de 24 facturas. El coste estimado recoge los tokens de entrada, de caché y de salida observados. El tiempo del gestor se mide aparte. [Resultados y consumo por factura](resultados.csv)

## ¿Y si basta con cambiar la instrucción?

En una prueba posterior, GPT-6.2 Astra leyó seis facturas sintéticas nuevas con cada una de dos instrucciones. Se mantuvieron las imágenes, el modelo, el esquema de salida y los controles en Python. Se añadió la indicación de comprobar cada cuota contra su propia base y tipo, aceptar varios tipos cuando cuadran y distinguir a quién corresponde cada NIF.

Ambas instrucciones extrajeron los 30 campos correctamente y detectaron los cuatro documentos que necesitaban revisión. La instrucción original también marcó una de las dos facturas correctas. La nueva aceptó las dos. En un ejemplo, una línea cobraba 3 € de IVA de más y otra 3 € de menos. Ambas lecturas detectaron los errores aunque el total cuadraba.

Cada variante leyó cada factura una vez. Estos resultados describen dos lotes sintéticos anteriores a la incorporación del QR. Para estimar su impacto en Melso harían falta documentos y decisiones de revisión de su operativa real.
