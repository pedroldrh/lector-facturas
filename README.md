# Lector de facturas

Un agente pequeño que lee una factura en PDF y devuelve cinco campos en JSON. El modelo lee las páginas y Python decide qué valores se pueden usar y cuáles necesitan revisión.

## El Bar Kramer y el nombre equivocado

En un tique real de **79,75 €**, la IA propuso **Rooms and Host Services SL** como emisor. Había leído bien el nombre. El error fue atribuir la venta a la empresa que figuraba en el aviso de protección de datos. Estos son los cinco campos de esa ejecución, guardada antes del cambio de prompt.

| Emisor | NIF del emisor | Base imponible | IVA | Retención |
| --- | --- | ---: | ---: | ---: |
| Pendiente de revisión | B98331887 | 72,50 € | 7,25 € | No aplica |

**Qué hizo saltar la revisión.** La cabecera mostraba la marca *Bar Kramer* y el NIF. En el pie, la otra sociedad figuraba como **responsable del tratamiento de datos**. La primera lectura propuso esa sociedad, explicó la duda y marcó el emisor como `dudoso`. Con esa señal, Python dejó el campo en `null` y pidió una segunda lectura independiente del nombre. La segunda repitió la misma sociedad y la calificó como `claro`. El programa conservó el nombre como candidato para revisión porque la primera lectura había sido dudosa. [Tique](examples/bar-kramer/tique.pdf) · [Las dos lecturas de la IA](examples/bar-kramer/lecturas.json) · [Salida completa](examples/bar-kramer/salida.json)

**Cómo comprobamos el error.** El modelo solo recibió la primera página y trabajó sin directorio de proveedores. En la página 3 del expediente, la Administración identifica a **Emprendimientos Hosteleros Valencia** como proveedor de la factura 012526, con el mismo NIF e importe. Esa página fue la referencia para evaluar la prueba. La copia del tique incluida aquí conserva los píxeles de la página 1 tal como los recibió el modelo. [Expediente publicado por Compromís, pág. 1](https://roviraleaks.compromis.net/invoices/24-03-25-FACTURA-Kramer.pdf#page=1) · [Conformidad administrativa, pág. 3](https://roviraleaks.compromis.net/invoices/24-03-25-FACTURA-Kramer.pdf#page=3)

**Qué pasaría con una factura nueva.** Hicimos una prueba adicional: simulamos que la primera lectura marcaba ese mismo nombre como claro y no advertía de ninguna incidencia. Sin ficha de proveedor, el lector aceptó el nombre erróneo. Al facilitarle una ficha verificada para ese NIF con `--proveedores`, detectó la discrepancia y dejó el nombre pendiente. Si la gestoría aún no conoce al proveedor, el gestor puede pedir una factura completa que acredite la razón social. [Prueba con y sin ficha](test_relectura.py) · [Correspondencia entre NIF y razón social en el BOE](https://www.boe.es/buscar/doc.php?id=BOE-A-2015-4644)

**Al repetir el tique con el prompt nuevo**, la primera lectura ya dejó el nombre vacío y explicó que la sociedad del pie solo figuraba como responsable de los datos. La segunda volvió a proponer esa sociedad. El lector mantuvo el nombre pendiente y conservó el NIF, la base y el IVA. El tique de Kramer formaba parte de las 12 facturas de desarrollo. [Salida con el prompt actual](examples/bar-kramer/con-prompt-nuevo.json)

## Qué cambió al probar el prompt en 30 facturas reales

Usamos 12 facturas para escribir las instrucciones que utiliza hoy el lector. Después comparamos el prompt básico y el nuevo con las mismas 18 facturas reservadas, en sesiones separadas de Astra. [Prompt actual](prompts/factura.txt) · [Resultados de las 30 facturas](examples/evaluacion/30-facturas-reales/README.md)

En una factura de viajes, el básico marcó como utilizables dos sumas correctas que no figuraban impresas como totales. El nuevo dejó esos dos campos pendientes. En otra factura los totales sí aparecían y el nuevo evitó una revisión. En conjunto, los campos aceptados que debían revisarse bajaron de **2 a 0**, y las revisiones innecesarias de facturas bajaron de **4 a 3**. Ninguna de las 30 tenía una retención aplicada.

## Probar con un PDF

```sh
python lector.py examples/bar-kramer/tique.pdf
```

Puedes sustituir la ruta por la de tu factura en euros. Cada ejecución hace una lectura nueva y puede responder de otra manera. Esta prueba reproduce la decisión de Python con las dos respuestas guardadas:

```sh
python -m unittest test_relectura.RelecturaSelectiva.test_tique_del_bar_kramer
```

**Instalación.** Se ha probado con Python 3.12, Poppler (`pdftoppm`) y Codex CLI con la sesión iniciada. El lector envía al modelo las imágenes de las páginas. En macOS puedes instalar Poppler con `brew install poppler`. En Debian y Ubuntu, el paquete es `poppler-utils`. [Instalación de Codex CLI](https://developers.openai.com/codex/cli/)

Prepara el entorno desde la carpeta del repositorio.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Cómo interpretar el resultado

La retención se expresa en euros como importe positivo que se descuenta del pago. Si un campo es dudoso, queda en `null`. Si los importes de una factura simple contradicen el total o un porcentaje impreso por más de un céntimo, los campos implicados quedan pendientes de revisión. Los valores leídos se conservan como `candidato` en `revision_campos` y `motivos` explica la discrepancia. Un conflicto entre cifras permite seguir usando un nombre y un NIF legibles y sin incidencias.

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
