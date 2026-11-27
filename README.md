# Lector de facturas

Dado un PDF de una factura en euros, el lector devuelve en JSON el nombre y el NIF del emisor, la base imponible, el IVA y la retención. Python comprueba los importes. Si la factura lleva un QR fiscal de la AEAT compatible, el lector contrasta los datos impresos con los codificados y explica las discrepancias.

| Para ver el resultado | Ejemplo |
| --- | --- |
| Un error real del modelo | [El modelo leyó «María» donde el original decía «Nuria»](examples/PRUEBA.md). El NIF ilegible activó la revisión. |
| Un nombre dudoso aunque el NIF sea legible | [Revisión por campo y contraste con un proveedor conocido](examples/identidad/README.md). El gestor recibe el candidato dudoso por separado de los campos utilizables. |
| Un error en el propio documento | [El QR contiene el NIF del cliente](examples/qr/README.md). El IVA y el total cuadran y ambos NIF son plausibles. |
| El coste de pedir otra lectura | [Pruebas con 24 facturas y una comparación de dos instrucciones](examples/evaluacion/README.md). |

## Probarlo

Se ha probado con Python 3.12, Poppler (el comando `pdftoppm`) y Codex CLI con una sesión iniciada. El lector envía las imágenes de las páginas al modelo que tengas disponible en Codex. El QR se decodifica localmente. [Instalación de Codex CLI](https://developers.openai.com/codex/cli/)

En macOS, Homebrew instala Poppler con `brew install poppler`. En Debian y Ubuntu, el paquete se llama `poppler-utils`.

Desde la carpeta del repositorio, instala las dependencias de lectura del QR y prueba la factura de Lucía.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python lector.py examples/lucia-240.pdf
```

En esta factura deben salir Lucía Martín, NIF 12345678Z, base de 240 €, IVA de 50,40 € y retención de 36 €. La retención se expresa como cantidad positiva que se descuenta del pago.

Cada campo tiene su propia valoración de legibilidad. El lector aparta los valores dudosos y conserva los demás. Para exigir, además, una coincidencia entre nombre y NIF con el directorio verificado de tu empresa, pasa `--proveedores proveedores.json`. El archivo se consulta localmente. [Ejemplo de directorio y resultados](examples/identidad/README.md)

## El caso que falló

En una lectura de una factura borrosa, el modelo devolvió «María Beltrán Llopis». El original decía «Nuria Beltrán Llopis». Acertó los tres importes y dejó vacío el NIF. El programa puede usar ese NIF ilegible para pedir revisión. Hace falta una referencia fiable, como la copia nítida, para comprobar el nombre correcto. [PDF original, copia borrosa y respuesta guardada](examples/PRUEBA.md)

Este comando inicia una lectura nueva de la copia borrosa.

```sh
python3 lector.py examples/nuria-110px.pdf
```

## Cómo se usó la IA

Pedro propuso probar recibos publicados, deteriorar copias del mismo original y medir cuándo compensa añadir revisores. Eligió incorporar el cotejo con el QR fiscal y planteó evaluar cada campo por separado al ver que un NIF legible podría ocultar un nombre mal leído. Codex generó documentos sintéticos, ejecutó las lecturas, comparó los resultados con las referencias e implementó el lector y sus pruebas. La respuesta «María» se conserva tal como salió de una lectura exploratoria.

## Verificar los controles

`python -m unittest -v` ejecuta las pruebas locales. Cubren el NIF ilegible de la lectura «María», dos importes erróneos que aun así cuadran, una factura sin retención y el comportamiento del cotejo fiscal por QR.

El estado `revisar` indica que la factura necesita intervención humana. Si el modelo propone un valor dudoso, el campo principal queda en `null` y la propuesta se guarda solo como `candidato` en `revision_campos`. Los controles aritméticos comprueban los importes tal como se imprimieron. Se admite un céntimo de diferencia por redondeo. Sin directorio, un nombre marcado como claro sigue siendo una transcripción del modelo.
