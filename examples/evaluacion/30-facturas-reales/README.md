# ¿Un prompt más específico mejora el lector de facturas?

En 18 facturas reales reservadas para la prueba, el prompt básico dio por utilizables dos importes calculados que no aparecían impresos. El nuevo prompt dejó ambos pendientes. Las revisiones innecesarias para los cinco campos de Albert bajaron de cuatro facturas a tres. Ningún prompt dejó pasar entera una factura con un valor incorrecto dado por bueno.

## Qué cambió en dos facturas reales

**Viajes Levante Tour.** El resumen fiscal mostraba dos bases, 8,47 € y 57,59 €, y dos cuotas de IVA, 1,53 € y 4,61 €. El básico devolvió 66,06 € de base y 6,14 € de IVA como datos utilizables. Son sumas correctas de las filas, pero esos dos totales no estaban impresos. El nuevo prompt dejó los dos campos vacíos para revisión. Ambas versiones ya enviaban la factura al gestor y advertían de un céntimo de diferencia entre el detalle y el resumen. Las líneas individuales suman 66,07 € de base y 6,13 € de IVA. Las dos maneras de agrupar dan 72,20 € en total. Esa diferencia es compatible con el redondeo por billete. La mejora fue impedir el uso de esos dos campos como si fueran transcripciones. Si el producto aceptara devolver agregados calculados e identificados como tales, los dos resultados empatarían en errores numéricos observados. [Factura H15, pág. 13](https://www.uv.es/opex/OPEX/VLC_Campus_inclusivo/facturas%20escaneadas1.pdf#page=13)

**Viajes El Corte Inglés.** También había dos tipos de IVA, pero aquí sí figuraban los totales de la base y del IVA, 66,46 € y 5,74 €. Las dos versiones leyeron bien los cinco campos. El prompt básico pidió revisión solo porque había dos tipos. El nuevo aceptó la factura. Esta fue la única revisión que se ahorró. [Factura H13, pág. 5](https://www.uv.es/opex/OPEX/VLC_Campus_inclusivo/facturas%20escaneadas1.pdf#page=5)

## Las 12 facturas del prompt básico

Cada fila corresponde a una factura que Astra leyó con el prompt básico. Las 12 proceden de ocho documentos públicos. Algunos reúnen varias facturas. El primer enlace abre el documento original en la página de la factura. El segundo abre la respuesta de aquella ejecución, con el modelo utilizado, su lectura de los cinco campos y la decisión del lector. El [prompt básico](prompt-basico.txt) fue el mismo en las doce.

| Factura | Proveedor o establecimiento | Fuente original | Respuesta guardada |
| --- | --- | --- | --- |
| D01 | Arsys | [PDF, pág. 4](https://www.valladolid.es/es/temas/hacemos/cuentas-grupos-politicos/justificacion-grupos-politicos-informe-intervencion-2022.ficheros/843768-CUENTAS%20MUNICIPAL%20VTLP%202022.pdf#page=4) | [Lectura de Astra](lecturas-desarrollo/D01-A.json) |
| D02 | Servicios de Prensa Comunicaplus | [PDF, pág. 5](https://www.valladolid.es/es/temas/hacemos/cuentas-grupos-politicos/justificacion-grupos-politicos-informe-intervencion-2022.ficheros/843768-CUENTAS%20MUNICIPAL%20VTLP%202022.pdf#page=5) | [Lectura de Astra](lecturas-desarrollo/D02-A.json) |
| D03 | Papelería de la Oficina | [PDF, pág. 21](https://www.valladolid.es/es/temas/hacemos/cuentas-grupos-politicos/justificacion-grupos-politicos-informe-intervencion-2022.ficheros/843768-CUENTAS%20MUNICIPAL%20VTLP%202022.pdf#page=21) | [Lectura de Astra](lecturas-desarrollo/D03-A.json) |
| D04 | La Pecera Novelda | [PDF, pág. 4](https://novelda.es/wp-content/uploads/2019/10/PUNTO-3.pdf#page=4) | [Lectura de Astra](lecturas-desarrollo/D04-A.json) |
| D05 | Cable Aireworld | [PDF, pág. 25](https://novelda.es/wp-content/uploads/2019/10/PUNTO-3.pdf#page=25) | [Lectura de Astra](lecturas-desarrollo/D05-A.json) |
| D06 | Restaurante Os Galegos (Cunca Blanca) | [PDF, pág. 1](https://roviraleaks.compromis.net/invoices/25-02-25-FACTURA-OsGalegos.pdf#page=1) | [Lectura de Astra](lecturas-desarrollo/D06-A.json) |
| D07 | Bar Kramer | [PDF, pág. 1](https://roviraleaks.compromis.net/invoices/24-03-25-FACTURA-Kramer.pdf#page=1) | [Lectura de Astra](lecturas-desarrollo/D07-A.json) |
| D08 | Prot Energía | [PDF, pág. 113](https://upcommons.upc.edu/server/api/core/bitstreams/fa158ab5-cc2b-4055-bf3d-b6cae005082b/content#page=113) | [Lectura de Astra](lecturas-desarrollo/D08-A.json) |
| D09 | Reprografía B.V. | [PDF, pág. 48](https://valenciasaludable2030.es/wp-content/uploads/2023/02/2020.2021-MEMORIA-ACTIVIDADES.pdf#page=48) | [Lectura de Astra](lecturas-desarrollo/D09-A.json) |
| D10 | Happy Flower Garden | [PDF, pág. 148](https://valenciasaludable2030.es/wp-content/uploads/2023/02/2020.2021-MEMORIA-ACTIVIDADES.pdf#page=148) | [Lectura de Astra](lecturas-desarrollo/D10-A.json) |
| D11 | Endesa · Llubí | [PDF, pág. 71](https://llubi.cat/sites/cilma_llubi/files/2023-02/PROY%20COMPLETO%20MARGET%2BCEMENTIRI%20-%20FIRMADO.pdf?download=1#page=71) | [Lectura de Astra](lecturas-desarrollo/D11-A.json) |
| D12 | Endesa · Las Palmas de Gran Canaria | [PDF, pág. 5](https://www.laspalmasgc.es/export/sites/laspalmasgc/.galleries/documentos-ayto-presupuestos/P2021_08.pdf#page=5) | [Lectura de Astra](lecturas-desarrollo/D12-A.json) |

En el Bar Kramer (D07), el modelo solo vio el tique de la página 1. El [justificante de la página 3](https://roviraleaks.compromis.net/invoices/24-03-25-FACTURA-Kramer.pdf#page=3) sirvió para comprobar el error después. [Copia del tique en el repositorio](../../bar-kramer/tique.pdf)

## Las 18 facturas reservadas

| Medida | Prompt básico | Prompt nuevo |
|---|---:|---:|
| Campos incorrectos dados por buenos (de 90) | 2 | 0 |
| Facturas con alguno de esos campos | 1 | 0 |
| Facturas aceptadas enteras que contenían un error | 0 | 0 |
| Campos acertados por el modelo que exigían revisión según la referencia | 0 | 0 |
| Revisiones evitables de facturas resolubles | 4 | 3 |
| Campos resolubles enviados a revisión | 1 | 1 |
| Facturas enviadas a revisión, en total | 6 | 5 |
| Revisiones justificadas, por factura | 2 | 2 |
| Facturas que necesitaban revisión y se aceptaron enteras | 0 | 0 |

## Resultado por factura

Los errores de la tabla son campos marcados para usar. Un documento puede estar en revisión por un campo y seguir ofreciendo otros como utilizables.

| Factura y fuente | Revisión de referencia | Errores aceptados A / B | Decisión A / B |
|---|---|---|---|
| [H01 · Unidad Editorial](https://www.valladolid.es/es/temas/hacemos/cuentas-grupos-politicos/justificacion-grupos-politicos-informe-intervencion-2022.ficheros/843768-CUENTAS%20MUNICIPAL%20VTLP%202022.pdf#page=14) | ninguna | 0 / 0 | usar / usar |
| [H02 · Ecologistas en Acción-CODA](https://www.valladolid.es/es/temas/hacemos/cuentas-grupos-politicos/justificacion-grupos-politicos-informe-intervencion-2022.ficheros/843768-CUENTAS%20MUNICIPAL%20VTLP%202022.pdf#page=22) | ninguna | 0 / 0 | usar / usar |
| [H03 · Datages Consulting](https://www.valladolid.es/es/temas/hacemos/cuentas-grupos-politicos/justificacion-grupos-politicos-informe-intervencion-2022.ficheros/843768-CUENTAS%20MUNICIPAL%20VTLP%202022.pdf#page=27) | ninguna | 0 / 0 | usar / usar |
| [H04 · Grupo SIFU Castilla y León](https://www.valladolid.es/es/temas/hacemos/cuentas-grupos-politicos/justificacion-grupos-politicos-informe-intervencion-2022.ficheros/843768-CUENTAS%20MUNICIPAL%20VTLP%202022.pdf#page=58) | ninguna | 0 / 0 | usar / usar |
| [H05 · El Cor de Aroa](https://roviraleaks.compromis.net/invoices/22-04-25-FACTURA-Pirineos.pdf#page=1) | ninguna | 0 / 0 | usar / usar |
| [H06 · La Taberna de Marisa](https://roviraleaks.compromis.net/invoices/14-04-25-FACTURA-TabernaMarisa.pdf#page=1) | ninguna | 0 / 0 | usar / usar |
| [H07 · Jualbo 2000](https://roviraleaks.compromis.net/invoices/18-11-24-FACTURA-Cerveceria-Erajoma.pdf#page=1) | ninguna | 0 / 0 | usar / usar |
| [H08 · El Verde EVB](https://roviraleaks.compromis.net/invoices/12-09-24-FACTURA-ElVerde.pdf#page=1) | ninguna | 0 / 0 | revisar / revisar |
| [H09 · Valensidra](https://roviraleaks.compromis.net/invoices/18-06-24-FACTURA-ELMolinon.pdf#page=1) | base, iva | 0 / 0 | revisar / revisar |
| [H10 · Media Markt Elche](https://novelda.es/wp-content/uploads/2019/10/PUNTO-3.pdf#page=2) | ninguna | 0 / 0 | usar / usar |
| [H11 · ONCE](https://www.uv.es/opex/OPEX/VLC_Campus_inclusivo/facturas%20escaneadas1.pdf#page=9) | ninguna | 0 / 0 | usar / usar |
| [H12 · Gestió de Projectes Universitaris FGUV](https://www.uv.es/opex/OPEX/VLC_Campus_inclusivo/facturas%20escaneadas1.pdf#page=10) | ninguna | 0 / 0 | usar / usar |
| [H13 · Viajes El Corte Inglés](https://www.uv.es/opex/OPEX/VLC_Campus_inclusivo/facturas%20escaneadas1.pdf#page=5) | ninguna | 0 / 0 | revisar / usar |
| [H14 · Fundación FESORD CV](https://www.uv.es/opex/OPEX/VLC_Campus_inclusivo/facturas%20escaneadas1.pdf#page=15) | ninguna | 0 / 0 | usar / usar |
| [H15 · Viajes Levante Tour](https://www.uv.es/opex/OPEX/VLC_Campus_inclusivo/facturas%20escaneadas1.pdf#page=13) | base, iva | base, iva / 0 | revisar / revisar |
| [H16 · VGA Servicios del Turia](https://valenciasaludable2030.es/wp-content/uploads/2023/02/2020.2021-MEMORIA-ACTIVIDADES.pdf#page=30) | ninguna | 0 / 0 | usar / usar |
| [H17 · Quadrum Digital](https://valenciasaludable2030.es/wp-content/uploads/2023/02/2020.2021-MEMORIA-ACTIVIDADES.pdf#page=55) | ninguna | 0 / 0 | revisar / revisar |
| [H18 · Montamar Sistemas Publicitarios](https://valenciasaludable2030.es/wp-content/uploads/2023/02/2020.2021-MEMORIA-ACTIVIDADES.pdf#page=84) | ninguna | 0 / 0 | revisar / revisar |


## Cómo se hicieron las pruebas

1. Usamos 12 facturas reales ya conocidas por el proyecto para desarrollar el prompt. Ejecutamos desde cero la versión básica de GPT-6.2 Astra en cada una. La referencia estaba fijada antes de esas llamadas. Se colaron dos campos en ese lote. En un tique del Bar Kramer se aceptó la empresa de privacidad como emisora. En otra factura el modelo sumó unas bases y presentó el resultado como si lo hubiera leído. También hubo dos revisiones evitables de facturas resolubles.
2. Mantuvimos el prompt básico y añadimos cuatro instrucciones sobre la relación entre nombre y venta, los importes que figuran en el documento, las casillas de retención vacías y los motivos que justifican revisión. Archivamos su huella antes de abrir las respuestas o resultados de evaluación. No ejecutamos el nuevo prompt en esas doce para puntuarlo. [Prompt básico](prompt-basico.txt) · [Prompt nuevo](../../../prompts/factura.txt)
3. Otros curadores prepararon las 18 facturas de evaluación y anotaron las respuestas esperadas. Los dos lotes no comparten operación, proveedor ni plantilla idéntica. Hay 18 proveedores en la evaluación, algunos con estilos de tique similares y documentos publicados en los mismos expedientes municipales o universitarios. Una auditoría independiente comprobó las fuentes y las referencias sin ver las predicciones.
4. Cada prompt leyó las mismas 18 facturas en orden mezclado. Hubo 48 llamadas efectivas en total, cada una en una sesión efímera independiente de Codex CLI, con directorio vacío, herramientas y búsqueda desactivadas. Usamos el mismo modelo, esfuerzo bajo, imágenes a 150 ppp, esquema JSON y controles en Python, sin directorio de proveedores ni segundas lecturas. Cada pareja de imágenes tenía la misma huella. Se hizo una ejecución por combinación y no hizo falta repetir ninguna por error técnico. [Versión de los controles del lector](https://github.com/pedroldrh/lector-facturas/tree/3aa369d2ab1a2f84ff2ebed9238970bf29990c56)

## Qué cuentan las cifras

Un error que se cuela es uno de los cinco campos que Python deja usar pese a contradecir la referencia o a estar presentado como transcripción sin constar en el original. Se cuenta aunque otro campo mande la factura a revisión. Una revisión sobrante es una factura marcada para revisión cuando los cinco campos eran resolubles y no había otra incidencia fiscal anotada. De las 18, 16 eran resolubles y dos requerían alguna revisión. Los dos prompts derivaron esas dos.

Tres documentos quedaron en revisión en ambos brazos aunque sus cinco campos se podían resolver según la referencia. En El Verde el nombre manuscrito estaba desvaído. Se consideró resoluble al ampliar el original, una decisión discutible. Si se considerara prudente revisarlo, los recuentos de revisiones sobrantes serían tres para A y dos para B. En las otras dos facturas, H17 y H18, los avisos afectaban al número, la fecha o la forma de pago. Esos datos podrían importar para otras tareas de una gestoría. Solo se califican de sobrantes respecto de los cinco campos del encargo.

Ninguna de las 30 facturas tenía una retención positiva. En este lote se comprobó si se inventaba una retención ausente. La capacidad de extraer una retención aplicada queda sin medir. Son pocos casos elegidos a mano y una sola ejecución por prompt y factura. En la evaluación no hubo una mejora observada en la identificación del proveedor. El efecto observado se concentró en las dos facturas de viajes descritas arriba.

[Comparación de cada campo en CSV](comparacion.csv) · [Evidencia descargable con las 48 lecturas, fuentes, referencias, protocolo y código](evidencia.zip)
