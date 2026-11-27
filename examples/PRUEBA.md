# Una factura legible y un fallo observado

Estos ejemplos son ficticios. La copia borrosa se hizo a partir del mismo original, por lo que se conocen los cinco valores antes de ejecutar el modelo.

| PDF | Emisor | NIF | Base | IVA | Retención |
| --- | --- | --- | ---: | ---: | ---: |
| [Factura de Lucía](lucia-240.pdf) | Lucía Martín | 12345678Z | 240,00 € | 50,40 € | 36,00 € |
| [Factura de Nuria](nuria-original.pdf) y [copia borrosa](nuria-110px.pdf) | Nuria Beltrán Llopis | 30847612N | 187,65 € | 39,41 € | 28,15 € |

## Qué ocurrió

Se redujo la factura de Nuria de 720 a 110 píxeles de ancho y se volvió a ampliar al tamaño original. GPT-6.2 Astra leyó la imagen de la página tres veces, cada vez en una sesión nueva y sin acceso al original ni a la tabla. En orden, devolvió «Nuria», «Núria» y «María». En la tercera lectura dejó el NIF vacío y acertó los tres importes. La [respuesta completa](lectura-original.json) se conserva tal como la devolvió el modelo en esa prueba exploratoria. Una ejecución nueva puede dar otra respuesta.

## Cómo detectarlo

La única alerta del modelo en aquella lectura se refería al NIF ilegible. Los importes cuadraban hasta el céntimo. El error en el nombre se comprobó al cotejar «María» con «Nuria» en el original nítido. En una factura nueva, un NIF ilegible basta para pedir revisión y solicitar una copia más clara antes de asociar el gasto a un proveedor. Pedro planteó otra pregunta: ¿qué pasaría si se pudiera leer el NIF y solo fallara el nombre? [Prueba con NIF legible y revisión por campo](identidad/README.md)

## Relectura selectiva

La primera lectura extrae los cinco campos. El programa vuelve a consultar las mismas páginas si el nombre o el NIF quedan sin identificar con claridad, si el NIF contradice el QR fiscal o si el nombre discrepa de la ficha verificada para ese NIF. Una diferencia de importes por sí sola se resuelve con los controles aritméticos. La primera aparición de un proveedor con ambos datos legibles puede requerir un alta en el directorio, algo que una segunda lectura del nombre no resolvería.

La segunda consulta recibe las imágenes y una pregunta sobre el nombre, sin ver la respuesta anterior. Ante dos nombres distintos, el campo `emisor` queda en `null`. Las transcripciones se pueden consultar en `relectura_emisor.lecturas`. Si las dos primeras lecturas solo difieren en un acento agudo, el lector hace un último intento para distinguir una variante de escritura de un cambio de nombre. Incluso si dos respuestas de tres coinciden, la discrepancia queda pendiente. Si falta un nombre o alguna lectura lo considera dudoso, también se pide revisión. Si la relectura falla, se conserva el resto de la primera lectura. Dos lecturas iguales nunca levantan un bloqueo anterior.

Se ejecutó el lector con GPT-6.2 Astra una vez por PDF y se comparó con el original nítido después. Las relecturas de la tabla las decidió el programa.

| PDF | Llamadas | Nombres devueltos | Resultado |
| --- | ---: | --- | --- |
| [Original nítido](nuria-original.pdf) | 1 | Nuria Beltrán Llopis | Cinco campos utilizables. |
| [Página borrosa](nuria-110px.pdf) | 2 | Nuria Beltrán Llopis en ambas | El NIF ilegible motivó la relectura y sigue pendiente. Los importes coincidieron con el original. |
| [Solo el nombre borroso](identidad/nombre-borroso.pdf) | 2 | Ninguna lectura pudo confirmar el nombre | Nombre pendiente. NIF y tres importes utilizables. |

En una comprobación aparte, se pasaron por la regla las tres respuestas guardadas del experimento anterior. «Nuria» y «Núria» dieron lugar a la tercera lectura. Al aparecer «María», el lector dejó el nombre pendiente con el estado `distintos` y conservó los tres importes. [Resultados de las ejecuciones nuevas, respuestas históricas y reproducción](identidad/relectura-selectiva.json)

Se puede repetir la prueba desde el repositorio con `python lector.py examples/nuria-110px.pdf --model gpt-6.2-astra`. La regla se basa en señales de identidad. En concreto, las versiones de la serie de desenfoque se ampliaron de nuevo al mismo tamaño final. Contar los píxeles del archivo habría dado el mismo resultado para imágenes con distintos niveles de detalle.

## Instrucción de la prueba exploratoria

Read only the attached receipt image. No tools, files, or web. Return a plain JSON object with: issuer (legal merchant name as printed), issuer_tax_id (printed issuer fiscal/tax registration ID, exclude ordinary company registration IDs), base (aggregate printed taxable base before VAT/GST), vat (printed VAT/GST amount, use positive amounts unless this is a credit), withholding (printed income tax withheld, positive magnitude), printed_total (printed final invoice amount payable). Use the original currency, numbers for amounts and null for any missing, ambiguous, or unreadable value. Ordinary sales tax is distinct from VAT/GST. Extract printed amounts, do not calculate missing amounts or infer a currency conversion. Include issues as a short list of source inconsistencies or missing/illegible fields.
