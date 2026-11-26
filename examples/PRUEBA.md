# Una factura legible y un fallo observado

Estos ejemplos son ficticios. La copia borrosa se hizo a partir del mismo original, por lo que se conocen los cinco valores antes de ejecutar el modelo.

| PDF | Emisor | NIF | Base | IVA | Retención |
| --- | --- | --- | ---: | ---: | ---: |
| [Factura de Lucía](lucia-240.pdf) | Lucía Martín | 12345678Z | 240,00 € | 50,40 € | 36,00 € |
| [Factura de Nuria](nuria-original.pdf) y [copia borrosa](nuria-110px.pdf) | Nuria Beltrán Llopis | 30847612N | 187,65 € | 39,41 € | 28,15 € |

## Qué ocurrió

Se redujo la factura de Nuria de 720 a 110 píxeles de ancho y se volvió a ampliar al tamaño original. GPT-6.2 Astra leyó la imagen de la página tres veces, cada vez en una sesión nueva y sin acceso al original ni a la tabla. En orden, devolvió «Nuria», «Núria» y «María». En la tercera lectura dejó el NIF vacío y acertó los tres importes. La [respuesta completa](lectura-original.json) se conserva tal como la devolvió el modelo en esa prueba exploratoria. Una ejecución nueva puede dar otra respuesta.

## Cómo detectarlo

La única alerta del modelo en aquella lectura se refería al NIF ilegible. Los importes cuadraban hasta el céntimo. El error en el nombre se comprobó al cotejar «María» con «Nuria» en el original nítido. En una factura nueva, un NIF ilegible basta para pedir revisión y solicitar una copia más clara antes de asociar el gasto a un proveedor.

## Instrucción de la prueba exploratoria

Read only the attached receipt image. No tools, files, or web. Return a plain JSON object with: issuer (legal merchant name as printed), issuer_tax_id (printed issuer fiscal/tax registration ID, exclude ordinary company registration IDs), base (aggregate printed taxable base before VAT/GST), vat (printed VAT/GST amount, use positive amounts unless this is a credit), withholding (printed income tax withheld, positive magnitude), printed_total (printed final invoice amount payable). Use the original currency, numbers for amounts and null for any missing, ambiguous, or unreadable value. Ordinary sales tax is distinct from VAT/GST. Extract printed amounts, do not calculate missing amounts or infer a currency conversion. Include issues as a short list of source inconsistencies or missing/illegible fields.
