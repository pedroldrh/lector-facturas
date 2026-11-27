# Una factura que cuadra y aun así pide revisión

Las dos facturas sintéticas muestran la misma operación. Muestra Ámbar, S.L. factura 100 € de base más 21 € de IVA a Muestra Índigo, S.L. La retención es cero. Ambas páginas imprimen el NIF del proveedor `B00000018`, el número `F-081` y la fecha 26/11/2026. Solo cambia el contenido del QR de pruebas.

| Documento | NIF impreso del proveedor | NIF en el QR | Resultado |
| --- | --- | --- | --- |
| [Factura con QR coincidente](coincide.pdf) | B00000018 | B00000018 | [Aceptada, cuatro campos coinciden](coincide.json) |
| [Factura con QR contradictorio](conflicto-nif.pdf) | B00000018 | B00000026 (cliente) | [A revisión por el NIF](conflicto-nif.json) |

La [versión anterior del lector](https://github.com/pedroldrh/lector-facturas/tree/11839320d01ce8ddf0842ff221cf9c77fd69c104) aceptó la segunda factura. Los cinco campos impresos estaban bien leídos y los 121 € cuadraban. [Salida guardada antes de incorporar el QR](antes-sin-qr.json)

Las tres salidas guardadas proceden de ejecuciones del lector con GPT-6.2 Astra. En la segunda factura, el lector actual dejó el NIF principal en `null`, conservó el NIF impreso en `revision_campos.nif.candidato` y mostró el valor del QR para que un gestor pudiera contrastarlos. En esta prueba el error se introdujo a propósito en el documento. El [caso de Nuria](../PRUEBA.md) recoge un error que sí cometió el modelo.

```sh
python lector.py examples/qr/coincide.pdf
python lector.py examples/qr/conflicto-nif.pdf
```

El QR fiscal de la AEAT contiene NIF, número y serie, fecha de expedición e importe total. El cotejo es local. Una coincidencia acredita que las dos representaciones concuerdan en los campos comparados. La consulta de un registro en Hacienda es otra operación. [Especificación española, artículo 21](https://www.boe.es/buscar/act.php?id=BOE-A-2024-22138) · [Documentación técnica de la AEAT](https://sede.agenciatributaria.gob.es/Sede/iva/sistemas-informaticos-facturacion-verifactu/informacion-tecnica/caracteristicas-qr-especificaciones-servicio-cotejo-factura.html)

El resultado enumera los campos comparados. Si falta un dato impreso para hacer el cotejo completo, figura `parcial`. Con retención, comparar el líquido a pagar con el total fiscal puede dar una alerta falsa. El lector solo contrasta el total cuando puede identificar una cifra comparable. `sin_qr_fiscal` indica que no se pudo leer ningún QR compatible. `no_disponible` indica que faltan las dependencias del decodificador.
