# Lector de facturas

Un agente pequeño lee una factura en PDF una sola vez. Devuelve el nombre del emisor, su NIF, la base, el IVA y la retención. Si la IA duda de un dato, Python lo deja pendiente para el gestor y conserva los demás campos que pasan las comprobaciones. La salida JSON indica al gestor el campo y el motivo de la revisión.

## El Bar Kramer y el nombre equivocado

**El fallo.** En un tique de 79,75 €, Astra leyó **ROOMS AND HOST SERVICES SL** y dio ese nombre por bueno con el prompt básico. Esa sociedad aparecía en el aviso de privacidad. Arriba del tique solo figuraban la marca *Bar Kramer* y el NIF. [Tique que vio el agente](examples/bar-kramer/tique.pdf) · [Salida real del prompt básico en la prueba de desarrollo](examples/bar-kramer/prompt-basico.json)

**Cómo comprobé quién había vendido la comida.** En la página 3 del expediente público, un justificante identifica a **Emprendimientos Hosteleros Valencia** como proveedor. Coinciden el número de factura, el NIF y los 79,75 €. El agente solo recibió la página 1. Usamos la página 3 después para comprobar la respuesta. [Justificante, página 3](https://roviraleaks.compromis.net/invoices/24-03-25-FACTURA-Kramer.pdf#page=3)

**Cómo se detecta la duda con el tique solo.** El prompt pide comprobar qué texto relaciona el nombre de la empresa con la venta. Una mención en el aviso de privacidad solo acredita quién trata los datos. Si el agente duda del emisor, el programa deja el nombre pendiente para el gestor en esa misma lectura. El gestor puede usar los otros datos y sabe qué falta por confirmar. [Instrucciones del lector](prompts/factura.txt)

| Emisor | NIF del emisor | Base imponible | IVA | Retención |
| --- | --- | ---: | ---: | --- |
| Pendiente de revisión | B-98331887 | 72,50 € | 7,25 € | No aplica |

Esta salida se obtuvo al ejecutar el lector actual con Astra sobre el tique. Hizo una llamada. [Ver el resultado y el motivo de la duda](examples/bar-kramer/una-lectura.json)

En una versión anterior probamos a pedir una segunda opinión. La primera lectura propuso la sociedad del aviso con dudas. La segunda repitió el mismo error con seguridad. En el lector actual la primera duda basta para que el gestor revise ese campo. [Respuestas históricas](examples/bar-kramer/lecturas.json) · [Salida de aquella versión](examples/bar-kramer/salida.json) · [Prueba anterior del prompt nuevo con relectura](examples/bar-kramer/con-prompt-nuevo.json)

## Qué cambió al probar el prompt en 30 facturas reales

Los dos prompts pedían señalar las dudas por campo. Con las primeras **12 facturas** identificamos errores del prompt básico, incluido el Bar Kramer. Añadimos instrucciones concretas sobre cómo identificar al emisor, cuándo aceptar un total impreso y cuándo hace falta revisar la factura. Después, cada versión leyó las mismas **18 facturas nuevas**, en sesiones independientes de Astra. Hubo una sola lectura por factura y versión, con los mismos controles de Python. [Comparación completa, respuestas y fuentes](examples/evaluacion/30-facturas-reales/README.md)

| Resultado en las 18 facturas | Básico | Nuevo |
| --- | ---: | ---: |
| Campos que se dieron por buenos y debían revisarse | 2 | 0 |
| Facturas enviadas a revisión sin necesidad | 4 | 3 |
| Facturas que necesitaban revisión y fueron marcadas | 2 de 2 | 2 de 2 |

Los dos campos eran la base y el IVA de una misma factura. El prompt básico sumó bien las filas, pero presentó las sumas como totales leídos. La revisión que se ahorró correspondía a otra factura cuyos totales sí estaban impresos. En estas 18 facturas ambos prompts acertaron por igual en identificar al proveedor. Ninguna de las 30 llevaba una retención aplicada.

## Cómo lo probaría en Melso

Empezaría por facturas que un gestor ya haya revisado, tanto las que corrigió como las que estaban bien. Usaría una parte para entender por qué se equivoca el agente y ajustar las instrucciones. Reservaría el resto para comparar ambas versiones y contar dos cosas: cuántos errores se cuelan y cuántas facturas correctas llegan al gestor sin necesidad. Esa prueba permitiría decidir si conviene adoptar el cambio con facturas propias de Melso.

## Probar con un PDF

```sh
python lector.py examples/bar-kramer/tique.pdf
```

Puedes sustituir la ruta por la de tu factura en euros. Cada ejecución hace una lectura nueva y puede responder de otra manera. Para reproducir la decisión con la primera lectura dudosa guardada y comprobar que solo se llama al modelo una vez:

```sh
python -m unittest test_revision_directa.RevisionDirecta.test_tique_del_bar_kramer
```

**Instalación.** Se ha probado con Python 3.12, Poppler (`pdftoppm`) y Codex CLI con la sesión iniciada. El lector envía al modelo las imágenes de las páginas. En macOS puedes instalar Poppler con `brew install poppler`. En Debian y Ubuntu, el paquete es `poppler-utils`. [Instalación de Codex CLI](https://developers.openai.com/codex/cli/)

Prepara el entorno desde la carpeta del repositorio.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Cómo interpretar el resultado

La retención se expresa en euros como importe positivo que se descuenta del pago. Si un campo es dudoso, queda en `null`. Si los importes de una factura simple contradicen el total o un porcentaje impreso por más de un céntimo, los campos implicados quedan pendientes de revisión. Los valores leídos que requieren revisión se conservan como `candidato` en `revision_campos` y `motivos` explica la discrepancia. Un conflicto entre cifras permite seguir usando un nombre y un NIF legibles y sin incidencias. Un modelo puede dar por bueno un nombre equivocado. Si ya se dispone de una ficha de proveedor verificada, el lector puede contrastarla con el NIF. [Prueba con y sin ficha](test_revision_directa.py)

## Cómo se usó la IA

Pedro planteó qué pasaría si el lector acertaba el NIF y atribuía el gasto al proveedor equivocado. Después pidió probar esa hipótesis con facturas reales, sin añadir desenfoque. Codex implementó el lector y ejecutó las pruebas. El tique del Bar Kramer salió de un lote de ocho documentos públicos con referencias anotadas antes de las lecturas. El lector aceptó seis y dejó dos en revisión. Ninguna de las ocho facturas llevaba retención. [Ejemplo con retención en una factura ficticia](examples/lucia-240.json)

## Otros dos ejemplos

- **Una factura con los cinco campos.** Lucía Martín factura 240,00 € de base, 50,40 € de IVA y 36,00 € de retención. [PDF](examples/lucia-240.pdf) · [Salida del lector](examples/lucia-240.json)
- **Una factura borrosa.** En una lectura de un PDF degradado para la prueba, el modelo propuso *María* donde el original decía *Nuria*. El NIF ilegible activó la revisión. [Copia borrosa](examples/nuria-110px.pdf) · [Lectura observada](examples/lectura-original.json) · [Comparación con el original](examples/PRUEBA.md)

## Otras comprobaciones

- `python -m unittest -v` ejecuta las pruebas locales.
- Con `--proveedores proveedores.json` se cotejan el nombre y el NIF con un directorio local de proveedores verificados. [Ejemplo](examples/identidad/README.md)
- Si hay un QR fiscal compatible de la AEAT, se decodifica en local y se compara con los datos impresos. [Ejemplo de discrepancia](examples/qr/README.md)
- Se comparó el coste de una lectura y de añadir revisores en 24 facturas sintéticas. [Resultados](examples/evaluacion/README.md)
