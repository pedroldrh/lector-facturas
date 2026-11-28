# Lector de facturas

El lector extrae de un PDF el nombre del emisor, su NIF, la base imponible, el IVA y la retención. Pedí a Codex que buscara facturas reales publicadas en internet y me ayudara a construir y probar este pequeño agente. Astra lee cada PDF una vez. Python comprueba los datos y marca qué campos debe revisar un gestor.

## El Bar Kramer y el nombre equivocado

**El fallo.** Con el prompt básico, Astra leyó bien el NIF del Bar Kramer, **B-98331887**, pero identificó a **ROOMS AND HOST SERVICES SL** como proveedor. Ese nombre solo aparecía en el aviso de privacidad. Arriba del tique figuraban la marca *Bar Kramer* y el NIF. [Tique que vio el agente](examples/bar-kramer/tique.pdf) · [Respuesta del prompt básico](examples/bar-kramer/prompt-basico.json)

**Cómo comprobé quién había vendido la comida.** En la página 3 del expediente público, un justificante identifica a **Emprendimientos Hosteleros Valencia** como proveedor. Coinciden el número de factura, el NIF y los 79,75 €. El agente solo recibió la página 1. Usamos la página 3 después para comprobar la respuesta. [Justificante, página 3](https://roviraleaks.compromis.net/invoices/24-03-25-FACTURA-Kramer.pdf#page=3)

**Qué cambié.** El prompt básico ya pedía indicar la confianza por campo. Aun así, Astra había marcado como seguro el nombre equivocado. Le pedí que comprobara qué parte del tique identificaba a esa empresa como quien hizo la venta. Al repetir la prueba, Astra explicó que la empresa solo figuraba como responsable de los datos personales. El lector dejó el nombre pendiente para el gestor y conservó el NIF y los importes. [Prompt básico](examples/evaluacion/30-facturas-reales/prompt-basico.txt) · [Prompt del lector actual](prompts/factura.txt)

| Emisor | NIF del emisor | Base imponible | IVA | Retención |
| --- | --- | ---: | ---: | --- |
| Pendiente de revisión | B-98331887 | 72,50 € | 7,25 € | No aplica |

Esta salida se obtuvo al ejecutar el lector actual con Astra sobre el tique. Hizo una llamada. [Ver el resultado y el motivo de la duda](examples/bar-kramer/una-lectura.json)

**Cómo funcionan los niveles de confianza.** Para cada campo, Astra indica si lo ve seguro (`claro` en la salida), dudoso, ilegible o ausente. Una retención que no corresponde tiene su propia etiqueta, `no_aplica`. Python deja los datos dudosos pendientes, indica el motivo y conserva los que pasan las comprobaciones. En un ensayo anterior una segunda lectura llegó a repetir el mismo nombre equivocado con más seguridad. Por eso el lector deja el campo para revisión humana desde la primera duda. [Las dos respuestas del ensayo anterior](examples/bar-kramer/lecturas.json)

## Qué cambió al probar el prompt en 30 facturas reales

Probé el prompt básico con **12 facturas reales** y usé sus errores para ajustar las instrucciones. [Abrir las 12 facturas y sus respuestas de Astra](examples/evaluacion/30-facturas-reales/README.md#las-12-facturas-del-prompt-básico)

Después comparé ambas versiones con las mismas **18 facturas nuevas**. Cada versión recibía las mismas páginas en una sesión independiente de Astra, con los mismos controles de Python. [Comparación completa, respuestas y fuentes](examples/evaluacion/30-facturas-reales/README.md)

| Resultado en las 18 facturas | Básico | Nuevo |
| --- | ---: | ---: |
| Campos que se dieron por buenos y debían revisarse | 2 | 0 |
| Facturas enviadas a revisión sin necesidad | 4 | 3 |
| Facturas que necesitaban revisión y fueron marcadas | 2 de 2 | 2 de 2 |

Los **dos errores de interpretación** afectaban a la base y al IVA de una factura de Viajes Levante Tour. El prompt básico sumó bien las filas y presentó 66,06 € y 6,14 € como si fueran totales impresos. El nuevo dejó pendientes ambos campos. La **revisión que se evitó** era de otra factura, de Viajes El Corte Inglés. Tenía dos tipos de IVA y los totales se leían bien. En estas 18 facturas ambos prompts acertaron por igual en identificar al proveedor. Ninguna de las 30 llevaba una retención aplicada. [Detalle de las dos facturas](examples/evaluacion/30-facturas-reales/README.md#qué-cambió-en-dos-facturas-reales)

## Qué construiría en el equipo de IA y agentes de Melso

Mi propuesta es construir un sistema de mejora continua a partir de las correcciones de los gestores. El experimento con 30 facturas públicas sirve como primera prueba del método.

1. **Recoger las correcciones.** Guardaría el dato que propuso el lector y lo que verificó el gestor. Incluiría también facturas correctas para medir cuántas veces pedimos una revisión que sobra.
2. **Proponer y probar un cambio.** El sistema agruparía los fallos que se repiten y propondría un ajuste concreto al prompt. Antes de adoptarlo, probaría automáticamente las dos versiones sobre las mismas facturas reservadas, cuyas respuestas ya conoce el gestor.
3. **Decidir con los resultados.** Compararía cuántos datos erróneos se aceptan y cuántas facturas correctas acaban en revisión. Para saber si el cambio reduce costes en Melso, mediría también el tiempo de los gestores y el coste de las lecturas antes y después de aplicarlo.

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

Yo planteé la pregunta de si el lector podía acertar el NIF y aun así equivocarse de proveedor. Pedí usar facturas tal como se publicaron y comparar las dos versiones con documentos reservados. Codex implementó el lector y ejecutó las pruebas. Astra recibió las páginas de cada factura. Las respuestas de referencia se usaron después para evaluar sus lecturas. [Protocolo y resultados](examples/evaluacion/30-facturas-reales/README.md#cómo-se-hicieron-las-pruebas)

## Otros dos ejemplos

- **Una factura con los cinco campos.** Lucía Martín factura 240,00 € de base, 50,40 € de IVA y 36,00 € de retención. [PDF](examples/lucia-240.pdf) · [Salida del lector](examples/lucia-240.json)
- **Una factura borrosa.** En una lectura de un PDF degradado para la prueba, el modelo propuso *María* donde el original decía *Nuria*. El NIF ilegible activó la revisión. [Copia borrosa](examples/nuria-110px.pdf) · [Lectura observada](examples/lectura-original.json) · [Comparación con el original](examples/PRUEBA.md)

## Otras comprobaciones

- `python -m unittest -v` ejecuta las pruebas locales.
- Con `--proveedores proveedores.json` se cotejan el nombre y el NIF con un directorio local de proveedores verificados. [Ejemplo](examples/identidad/README.md)
- Si hay un QR fiscal compatible de la AEAT, se decodifica en local y se compara con los datos impresos. [Ejemplo de discrepancia](examples/qr/README.md)
- Se comparó el coste de una lectura y de añadir revisores en 24 facturas sintéticas. [Resultados](examples/evaluacion/README.md)
