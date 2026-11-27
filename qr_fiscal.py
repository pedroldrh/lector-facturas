"""Contraste local con el contenido de un QR de facturación de la AEAT."""

import re
from datetime import datetime
from decimal import Decimal
from urllib.parse import parse_qsl, urlsplit

from confianza import normalizar_nif


SERVIDORES = {"www2.agenciatributaria.gob.es", "prewww2.aeat.es"}
RUTAS = {"/wlpl/TIKE-CONT/ValidarQR", "/wlpl/TIKE-CONT/ValidarQRNoVerifactu"}
CLAVES = ("nif", "numserie", "fecha", "importe")


def analizar_contenidos(contenidos):
    """Deduplica el mismo QR repetido en varias páginas. Nunca abre los enlaces."""
    distintos = []
    for texto in contenidos:
        try:
            url = urlsplit(texto)
        except ValueError:
            continue
        if url.hostname not in SERVIDORES or url.path not in RUTAS:
            continue
        try:
            if (url.scheme != "https" or url.netloc.lower() != url.hostname or url.fragment
                    or re.search(r"%(?![0-9A-Fa-f]{2})", url.query)):
                raise ValueError
            pares = parse_qsl(url.query, keep_blank_values=True, strict_parsing=True,
                              errors="strict", max_num_fields=16)
            params = dict(pares)
            if len(pares) != len(params):
                raise ValueError
            datos = {k: params[k] for k in CLAVES}
            if (not re.fullmatch(r"[A-Z0-9]{9}", datos["nif"])
                    or not datos["numserie"].strip()
                    or not datos["numserie"].isprintable()
                    or not re.fullmatch(r"[0-9]{2}-[0-9]{2}-[0-9]{4}", datos["fecha"])
                    or not re.fullmatch(r"-?[0-9]{1,12}(?:\.[0-9]{1,2})?", datos["importe"])):
                raise ValueError
            datetime.strptime(datos["fecha"], "%d-%m-%Y")
            datos["importe"] = format(Decimal(datos["importe"]), ".2f")
        except (KeyError, ValueError):
            return {"estado": "invalido"}
        if datos not in distintos:
            distintos.append(datos)

    if not distintos:
        return {"estado": "sin_qr_fiscal"}
    if len(distintos) != 1:
        return {"estado": "ambiguo"}
    return {"estado": "detectado", "campos": distintos[0]}


def leer_qr(paginas):
    try:
        import zxingcpp
        from PIL import Image
    except ImportError:
        return {"estado": "no_disponible"}

    contenidos = []
    for pagina in paginas:
        with Image.open(pagina) as imagen:
            codigos = zxingcpp.read_barcodes(imagen, formats=zxingcpp.BarcodeFormat.QRCode)
            contenidos.extend(codigo.text for codigo in codigos if codigo.valid)
    return analizar_contenidos(contenidos)


def contrastar(lectura, qr):
    """Devuelve la evidencia comparada y los motivos que requieren revisión."""
    if qr["estado"] != "detectado":
        motivos = {"invalido": "El QR fiscal contiene datos incompletos o inválidos.",
                   "ambiguo": "Hay más de un QR fiscal distinto en el PDF."}
        motivo = motivos.get(qr["estado"])
        return qr, [motivo] if motivo else []

    total = lectura.get("total_fiscal_impreso")
    if (total is None and lectura["total_simple"] and lectura["retencion"] in (None, 0)
            and lectura["tipo_retencion"] in (None, 0)):
        total = lectura["importe_total"]
    impresos = {"nif": lectura["nif"], "numserie": lectura.get("numero_factura"),
                "fecha": lectura.get("fecha_expedicion"), "importe": total}
    comparados = []
    discrepancias = []
    motivos = []
    for campo, valor in impresos.items():
        if valor is None:
            continue
        qr_valor = qr["campos"][campo]
        if campo == "importe":
            coincide = Decimal(str(valor)) == Decimal(qr_valor)
        elif campo == "nif":
            coincide = normalizar_nif(valor) == qr_valor
        else:
            coincide = valor.strip() == qr_valor
        comparados.append(campo)
        if not coincide:
            discrepancias.append(campo)
            motivos.append(f"El campo {campo} difiere: lectura «{valor}», QR fiscal «{qr_valor}».")
    estado = "coincide" if len(comparados) == len(impresos) else "parcial"
    return {**qr, "estado": "discrepancia" if motivos else estado,
            "comparados": comparados, "discrepancias": discrepancias}, motivos
