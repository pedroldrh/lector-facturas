"""Decisiones por campo a partir de la legibilidad y de un directorio verificado."""

import json
import re
import unicodedata
from pathlib import Path


CAMPOS_LECTURA = ("emisor", "nif", "base", "iva", "retencion")
LEGIBILIDAD = ("claro", "dudoso", "ilegible", "no_consta")


def _estados(campo):
    return LEGIBILIDAD + ("no_aplica",) if campo == "retencion" else LEGIBILIDAD


def esquema_confianza():
    return {
        "type": "object",
        "properties": {
            campo: {"type": "string", "enum": list(_estados(campo))}
            for campo in CAMPOS_LECTURA
        },
        "required": list(CAMPOS_LECTURA),
        "additionalProperties": False,
    }


def normalizar_nif(valor):
    compacto = re.sub(r"[\s-]+", "", valor.upper())
    return compacto[2:] if len(compacto) == 11 and compacto.startswith("ES") else compacto


def _nombre_comparable(nombre):
    return " ".join(unicodedata.normalize("NFC", nombre).casefold().split())


def cargar_proveedores(path):
    """Lee un objeto JSON NIF → nombre previamente verificado por el usuario."""
    def construir_directorio(pares):
        directorio = {}
        for clave, nombre in pares:
            nif = normalizar_nif(clave)
            if not re.fullmatch(r"[A-Z0-9]{9}", nif):
                raise ValueError(f"NIF con formato inválido en el directorio: {clave!r}.")
            if not isinstance(nombre, str) or not nombre.strip():
                raise ValueError(f"Falta un nombre de proveedor válido para {clave!r}.")
            if nif in directorio:
                raise ValueError(f"NIF duplicado en el directorio de proveedores: {nif}.")
            directorio[nif] = nombre
        return directorio

    with Path(path).open(encoding="utf-8") as archivo:
        proveedores = json.load(archivo, object_pairs_hook=construir_directorio)
    if not isinstance(proveedores, dict):
        raise ValueError("El directorio de proveedores debe ser un objeto JSON NIF → nombre.")
    return proveedores


def evaluar_campos(lectura, proveedores=None):
    """Separa cada valor utilizable de los candidatos pendientes de revisión."""
    aprobados = {campo: lectura[campo] for campo in CAMPOS_LECTURA}
    if "confianza_por_campo" not in lectura:
        # Las lecturas históricas conservan las transcripciones. No acreditan el nombre.
        revision = {
            campo: {
                "legibilidad": "sin_evaluar",
                "decision": "usar" if valor is not None else "revisar",
            }
            for campo, valor in aprobados.items()
        }
        revision["emisor"]["decision"] = "revisar"
        revision["emisor"]["contraste_directorio"] = "no_consultado"
        if aprobados["emisor"] is not None:
            revision["emisor"]["candidato"] = aprobados["emisor"]
        aprobados["emisor"] = None
        motivos = ["Lectura anterior sin evaluación por campo. Releer el nombre del emisor."]
        for campo in ("emisor", "nif", "base", "iva"):
            if lectura[campo] is None:
                motivos.append(f"No se ha podido verificar el campo {campo}.")
        return aprobados, revision, motivos

    confianza = lectura["confianza_por_campo"]
    if not isinstance(confianza, dict) or set(confianza) != set(CAMPOS_LECTURA):
        raise ValueError("La legibilidad debe indicarse para cada uno de los cinco campos.")

    revision = {}
    motivos = []
    for campo in CAMPOS_LECTURA:
        legibilidad = confianza[campo]
        if legibilidad not in _estados(campo):
            raise ValueError(f"Legibilidad no válida para {campo}: {legibilidad!r}.")
        valor = lectura[campo]
        detalle = {"legibilidad": legibilidad, "decision": "usar"}
        revision[campo] = detalle
        if legibilidad == "claro" and valor is not None:
            continue
        if (legibilidad == "no_aplica" and valor in (None, 0)
                and lectura.get("tipo_retencion") in (None, 0)):
            detalle["decision"] = "no_aplica"
            continue

        detalle["decision"] = "revisar"
        aprobados[campo] = None
        if valor is not None:
            detalle["candidato"] = valor
        if legibilidad == "claro":
            motivos.append(f"El campo {campo} se calificó como claro, pero falta el valor.")
        elif legibilidad == "no_aplica":
            motivos.append("Se indicó que la retención no aplica, pero figura una cuota o un tipo.")
        else:
            motivos.append(f"Revisar el campo {campo}. Legibilidad declarada: {legibilidad}.")

    emisor = revision["emisor"]
    if proveedores is None:
        emisor["contraste_directorio"] = "no_consultado"
        return aprobados, revision, motivos

    motivo_identidad = None
    if aprobados["nif"] is None:
        emisor["contraste_directorio"] = "nif_no_utilizable"
        motivo_identidad = "El NIF impreso no permite contrastar el nombre con el directorio."
    else:
        registrado = proveedores.get(normalizar_nif(aprobados["nif"]))
        if registrado is None:
            emisor["contraste_directorio"] = "sin_referencia"
            motivo_identidad = "El NIF leído no figura en el directorio de proveedores verificados."
        else:
            emisor["nombre_directorio"] = registrado
            if aprobados["emisor"] is None:
                emisor["contraste_directorio"] = "nombre_no_utilizable"
            elif _nombre_comparable(aprobados["emisor"]) == _nombre_comparable(registrado):
                emisor["contraste_directorio"] = "coincide"
            else:
                emisor["contraste_directorio"] = "discrepancia"
                motivo_identidad = "El nombre del emisor difiere del proveedor verificado para ese NIF."

    if motivo_identidad:
        emisor["decision"] = "revisar"
        if aprobados["emisor"] is not None:
            emisor["candidato"] = aprobados["emisor"]
        aprobados["emisor"] = None
        motivos.append(motivo_identidad)

    return aprobados, revision, motivos
