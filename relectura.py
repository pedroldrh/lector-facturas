"""Relectura selectiva del nombre del emisor cuando hay dudas de identidad."""

import unicodedata

from confianza import nombre_comparable


def motivos_relectura(lectura, resultado):
    """Usa las señales de identidad de la primera lectura y sus controles locales."""
    motivos = []
    campos = resultado["revision_campos"]
    if lectura["emisor"] is None or campos["emisor"]["legibilidad"] != "claro":
        motivos.append("La primera lectura no identifica con claridad el nombre del emisor.")
    if "nif" in resultado.get("qr_fiscal", {}).get("discrepancias", []):
        motivos.append("El NIF del emisor leído en la factura discrepa del QR fiscal.")
    elif lectura["nif"] is None or campos["nif"]["decision"] == "revisar":
        motivos.append("La primera lectura no permite usar el NIF del emisor.")
    if campos["emisor"].get("contraste_directorio") == "discrepancia":
        motivos.append("El nombre leído difiere del proveedor verificado para ese NIF.")
    return motivos


def observacion_nombre(lectura):
    return {"nombre": lectura["emisor"], "legibilidad": lectura["confianza_por_campo"]["emisor"]}


def comparar_nombres(observaciones):
    """Compara los nombres leídos y conserva diferencias como Peña frente a Pena."""
    nombres = {
        nombre_comparable(lectura["nombre"])
        for lectura in observaciones if lectura["nombre"] is not None
    }
    if len(nombres) > 1:
        sin_acento_agudo = {unicodedata.normalize("NFD", nombre).replace("\u0301", "") for nombre in nombres}
        return "variante_grafica" if len(sin_acento_agudo) == 1 else "distintos"

    if len(observaciones) < 2 or any(
        lectura["nombre"] is None or lectura["legibilidad"] != "claro" for lectura in observaciones
    ):
        return "sin_confirmar"
    return "coinciden"


def aplicar_relectura(resultado, observaciones, motivos, error=None):
    """Anota la comparación sin levantar una revisión previa ni cambiar otros campos."""
    if not motivos:
        estado = "no_necesaria"
    elif error is not None:
        estado = "error"
    else:
        estado = comparar_nombres(observaciones)
    resultado["relectura_emisor"] = {"estado": estado, "lecturas": observaciones, "motivos": motivos}

    avisos = {
        "distintos": "Las lecturas proponen nombres distintos para el emisor.",
        "variante_grafica": "Las lecturas difieren en la acentuación del nombre del emisor.",
        "sin_confirmar": "Las lecturas no han podido confirmar con claridad el nombre del emisor.",
        "error": "No se pudo completar la relectura del nombre del emisor.",
    }
    if estado in avisos:
        aviso = avisos[estado]
        detalle = resultado["revision_campos"]["emisor"]
        if resultado["emisor"] is not None:
            detalle["candidato"] = resultado["emisor"]
        detalle["decision"] = "revisar"
        detalle.setdefault("motivos", []).append(aviso)
        resultado["emisor"] = None
        resultado["estado"] = "revisar"
        resultado["motivos"].append(aviso)
    return resultado
