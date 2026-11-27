# Lector de facturas

Este agente lee una factura en PDF y devuelve cinco campos en JSON. Esta es la [salida del lector](examples/lucia-240.json) para la [factura ficticia de Lucía](examples/lucia-240.pdf).

| Emisor | NIF del emisor | Base imponible | IVA | Retención |
| --- | --- | ---: | ---: | ---: |
| Lucía Martín | 12345678Z | 240,00 € | 50,40 € | 36,00 € |

## El fallo de la factura borrosa

En una de las lecturas, el modelo devolvió **María Beltrán Llopis**, dejó el NIF en blanco y acertó los tres importes. El NIF ilegible dio motivo para revisar la factura. Al abrir el original nítido vimos que la emisora era **Nuria Beltrán Llopis**. La respuesta guardada permite inspeccionar ese fallo aunque una lectura nueva dé otro resultado.

[Copia borrosa](examples/nuria-110px.pdf) · [Respuesta del modelo](examples/lectura-original.json) · [Original nítido](examples/nuria-original.pdf) · [Cómo se hizo la prueba](examples/PRUEBA.md)

## Probar con un PDF

```sh
python lector.py examples/lucia-240.pdf
```

Sustituye la ruta por la de tu factura en euros. Para probar el escaneo borroso, usa `examples/nuria-110px.pdf`.

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

Pedro eligió los casos de prueba. Al ver el fallo de Nuria, quiso comprobar qué pasaría si el modelo leyera bien el NIF y se equivocara solo en el nombre. Esa pregunta llevó a evaluar cada campo por separado. Codex implementó el lector, generó las facturas ficticias y ejecutó las pruebas. [Prueba con el nombre borroso y el NIF legible](examples/identidad/README.md)

## Otras comprobaciones

- `python -m unittest -v` ejecuta las pruebas locales.
- Con `--proveedores proveedores.json` se cotejan el nombre y el NIF con un directorio local de proveedores verificados. [Ejemplo](examples/identidad/README.md)
- Si hay un QR fiscal compatible de la AEAT, se decodifica en local y se compara con los datos impresos. [Ejemplo de discrepancia](examples/qr/README.md)
- Se comparó el coste de una lectura y de añadir revisores en 24 facturas sintéticas. [Resultados](examples/evaluacion/README.md)
