# Lector de facturas

Dado un PDF de una factura en euros, el lector devuelve en JSON el nombre y el NIF del emisor, la base imponible, el IVA y la retención. También devuelve el total impreso y los motivos por los que una factura necesita revisión.

## Probarlo

Necesitas Python 3, Poppler (el comando `pdftoppm`) y Codex CLI con una sesión iniciada. El lector envía las imágenes de las páginas al modelo que tengas disponible en Codex. [Instalación de Codex CLI](https://developers.openai.com/codex/cli/)

En macOS, Homebrew instala Poppler con `brew install poppler`. En Debian y Ubuntu, el paquete se llama `poppler-utils`.

Prueba la factura de Lucía desde la carpeta del repositorio.

```sh
python3 lector.py examples/lucia-240.pdf
```

En esta factura deben salir Lucía Martín, NIF 12345678Z, base de 240 €, IVA de 50,40 € y retención de 36 €. La retención se expresa como cantidad positiva que se descuenta del pago.

## El caso que falló

En una lectura de una factura borrosa, el modelo devolvió «María Beltrán Llopis». El original decía «Nuria Beltrán Llopis». Acertó los tres importes y dejó vacío el NIF. El programa puede usar ese NIF ilegible para pedir revisión. Hace falta una referencia fiable, como la copia nítida, para comprobar el nombre correcto. [PDF original, copia borrosa y respuesta guardada](examples/PRUEBA.md)

Este comando inicia una lectura nueva de la copia borrosa.

```sh
python3 lector.py examples/nuria-110px.pdf
```

## Cómo se usó la IA

Pedro propuso salir de los ejemplos fáciles, probar documentos publicados y deteriorar copias del mismo original. Codex generó los PDFs de prueba, organizó las lecturas independientes, comparó los resultados con las referencias y escribió el lector. La respuesta guardada en este repositorio procede de una de esas lecturas. El experimento y el código del lector se hicieron en ese orden.

## Verificar los controles

`python3 -m unittest -v` ejecuta tres comprobaciones locales con datos guardados. Cubren el NIF ilegible de la lectura «María», una lectura con dos importes erróneos que aun así cuadran y una factura sin retención aplicable.

El estado `revisar` conserva los valores leídos y explica el motivo. En una factura simple se comprueba el total y, cuando constan los tipos, las cuotas. Se admite un céntimo de diferencia por redondeo. `leido` indica que estos controles pasaron. La comprobación de la identidad legal del proveedor requiere una referencia externa fiable.
