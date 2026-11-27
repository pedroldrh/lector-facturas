# ¿Y si se lee bien el NIF, pero se confunde «Nuria» con «María»?

El NIF y el nombre se evalúan por separado. Un QR fiscal puede corroborar el NIF. El nombre legal del proveedor no figura en ese QR.

## Lo que pasó al leer los PDF

En la [factura de prueba](nombre-borroso.pdf) solo se difuminó el comienzo de «Nuria». El NIF y los importes se conservan como en el [original nítido](../nuria-original.pdf). El directorio del ejemplo es ficticio y refleja el nombre que se conoce a partir del original. El modelo solo recibe la imagen. Python consulta el directorio después de la lectura.

| Lectura con GPT-6.2 Astra y el directorio de ejemplo | Nombre utilizable | NIF | Base | IVA | Retención |
| --- | --- | --- | ---: | ---: | ---: |
| [Original nítido](nombre-original.json) | Nuria Beltrán Llopis | 30847612N | 187,65 € | 39,41 € | 28,15 € |
| [Nombre borroso, NIF legible](nombre-borroso.json) | Pendiente de revisión | 30847612N | 187,65 € | 39,41 € | 28,15 € |

El lector anterior también dejó en blanco el nombre en cuatro lecturas nuevas, dos por variante de desenfoque. En las cuatro leyó bien el NIF y los importes. Estas lecturas sirven de control. El fallo real «María» se observó en la [prueba anterior con toda la página borrosa](../PRUEBA.md). [Cuatro salidas del lector anterior](lecturas-anteriores.json)

## Qué pasa si el modelo sí propone «María»

Para probar la regla de decisión sin depender del azar del modelo, se le pasó una lectura controlada con «María», el NIF correcto, importes que cuadran y ninguna otra incidencia. En las pruebas de la versión actual también coincide el QR sintético. [Entrada y resultados del ensayo controlado](contraprueba.json)

| Condición | Qué sale en `emisor` |
| --- | --- |
| Regla anterior | María Beltrán Llopis. La factura pasa. |
| El modelo señala dudas sobre el nombre | `null`. «María» queda solo como candidato para revisión. |
| El modelo llama «claro» al nombre y no hay directorio | María Beltrán Llopis. Una lectura segura todavía puede equivocarse. |
| El modelo llama «claro» al nombre y el NIF figura como «Nuria» en un directorio verificado | `null`. Se conservan la propuesta y el nombre de referencia para el gestor. |

Para reproducir la lectura con un directorio local desde la raíz del repositorio:

```sh
python lector.py examples/identidad/nombre-borroso.pdf --proveedores examples/identidad/proveedores-ejemplo.json
```

`--proveedores` activa un cotejo estricto. Un NIF nuevo o dudoso, un NIF que contradice el QR, un nombre ilegible o una discrepancia con el directorio dejan el nombre sin aceptar. El directorio debe proceder de una fuente ya comprobada por el usuario, por ejemplo una ficha de proveedor revisada por un gestor. Un nombre de referencia nunca sustituye automáticamente al nombre del PDF. Las etiquetas de legibilidad expresan el juicio del modelo sobre cada campo. Para asignarles probabilidades haría falta medir su acierto en facturas etiquetadas y representativas.
