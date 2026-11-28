#!/usr/bin/env python3
"""Lee una factura PDF en euros y comprueba los importes de las facturas simples."""

import argparse
import json
import math
import subprocess
import sys
import tempfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from confianza import cargar_proveedores, esquema_confianza, evaluar_campos
from qr_fiscal import contrastar, leer_qr

CAMPOS = {
    "emisor": "string", "nif": "string", "base": "number", "iva": "number",
    "retencion": "number", "importe_total": "number", "tipo_iva": "number",
    "tipo_retencion": "number",
}
CAMPOS_QR = {
    "numero_factura": "string", "fecha_expedicion": "string", "total_fiscal_impreso": "number",
}
PREGUNTA = (Path(__file__).resolve().parent / "prompts" / "factura.txt").read_text(encoding="utf-8")


def _conflictos_de_importes(lectura):
    """Indica qué campos intervienen en cada comprobación que falla."""
    base, iva, retencion, total = [
        Decimal(str(lectura[k])) if lectura[k] is not None else None
        for k in ("base", "iva", "retencion", "importe_total")
    ]
    if retencion is not None and retencion < 0:
        raise ValueError("La retención debe expresarse como magnitud positiva.")
    if lectura["tipo_retencion"] not in (None, 0) and retencion is None:
        yield ("retencion",), "Figura un tipo de retención sin cuota verificable."

    if not lectura["total_simple"] or base is None:
        return

    legibilidad_retencion = lectura.get("confianza_por_campo", {}).get("retencion")
    sin_retencion = lectura["tipo_retencion"] in (None, 0) and legibilidad_retencion in (None, "no_aplica")
    if iva is not None and total is not None and (retencion is not None or sin_retencion):
        calculado = base + iva - (retencion or Decimal(0))
        if abs(calculado - total) > Decimal("0.01"):
            campos = ("base", "iva") if retencion is None else ("base", "iva", "retencion")
            yield campos, f"Total impreso {total} €, total calculado {calculado} €."

    for campo, cuota, etiqueta in (("iva", iva, "IVA"), ("retencion", retencion, "Retención")):
        tipo = lectura["tipo_" + campo]
        if tipo is None or cuota is None:
            continue
        esperada = (base * Decimal(str(tipo)) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if abs(esperada - cuota) > Decimal("0.01"):
            yield ("base", campo), (
                f"{etiqueta} de {cuota} € en la factura. El {tipo}% de {base} € serían {esperada} €."
            )


def revisar(lectura, qr=None, proveedores=None):
    """Valida una lectura bruta y decide si requiere revisión."""
    if not isinstance(lectura, dict):
        raise ValueError("Se esperaba un objeto JSON.")
    for campo, tipo in {**CAMPOS, **CAMPOS_QR}.items():
        if campo not in lectura and campo in CAMPOS:
            raise ValueError(f"Falta el campo {campo} en la respuesta.")
        valor = lectura.get(campo)
        if valor is None:
            continue
        if tipo == "string":
            valido = isinstance(valor, str) and bool(valor.strip())
        else:
            valido = type(valor) in (int, float) and math.isfinite(valor)
        if not valido:
            raise ValueError(f"El campo {campo} tiene un valor no válido.")
    incidencias = lectura.get("incidencias")
    if not isinstance(incidencias, list) or not all(isinstance(m, str) for m in incidencias):
        raise ValueError("Se esperaba una lista de incidencias.")
    if type(lectura.get("total_simple")) is not bool:
        raise ValueError("total_simple debe ser booleano.")
    motivos = [m.strip() for m in incidencias if m.strip()]
    resultado, revision, motivos_campos = evaluar_campos(lectura, proveedores)
    motivos.extend(motivos_campos)

    for campos, motivo in _conflictos_de_importes(lectura):
        motivos.append(motivo)
        for campo in campos:
            detalle = revision[campo]
            if detalle["decision"] == "no_aplica":
                continue
            detalle["decision"] = "revisar"
            detalle.setdefault("motivos", []).append(motivo)
            if lectura[campo] is not None:
                detalle["candidato"] = lectura[campo]
            resultado[campo] = None

    if qr is not None:
        cotejo, diferencias = contrastar(lectura, qr)
        resultado["qr_fiscal"] = cotejo
        motivos.extend(diferencias)
        if "nif" in cotejo.get("discrepancias", []):
            revision["nif"].update(decision="revisar", candidato=lectura["nif"])
            resultado["nif"] = None
            if proveedores is not None:
                emisor = revision["emisor"]
                emisor.update(decision="revisar", contraste_directorio="nif_en_conflicto")
                emisor.pop("nombre_directorio", None)
                if lectura["emisor"] is not None:
                    emisor["candidato"] = lectura["emisor"]
                resultado["emisor"] = None
                motivos.append("El NIF en conflicto impide confirmar el vínculo con el proveedor.")
    resultado["revision_campos"] = revision
    return dict(resultado, total_impreso=lectura["importe_total"],
                estado="revisar" if motivos else "leido", motivos=motivos)


def _consultar_modelo(paginas, modelo, pregunta, esquema):
    """Lee todas las páginas de la factura juntas en una sesión nueva."""
    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp)
        ruta_esquema = carpeta / "esquema.json"
        ruta_esquema.write_text(json.dumps(esquema), encoding="utf-8")
        respuesta = carpeta / "respuesta.json"
        aislado = carpeta / "sesion"
        aislado.mkdir()
        cmd = ["codex", "-a", "never", "exec", "--ephemeral", "--ignore-user-config",
               "--skip-git-repo-check", "-s", "read-only", "-C", str(aislado),
               "--disable", "shell_tool", "--disable", "apps", "--disable", "browser_use",
               "-c", 'web_search="disabled"', "--output-schema", str(ruta_esquema),
               "-o", str(respuesta)]
        if modelo:
            cmd.extend(["--model", modelo])
        for pagina in paginas:
            cmd.extend(["-i", str(pagina)])
        subprocess.run(cmd + ["--", pregunta], check=True, capture_output=True,
                       stdin=subprocess.DEVNULL, cwd=aislado, timeout=180)
        return json.loads(respuesta.read_text(encoding="utf-8"))


def leer(pdf, modelo=None, proveedores=None):
    if not pdf.is_file():
        raise ValueError(f"No se encuentra el PDF: {pdf}")
    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp)
        subprocess.run(["pdftoppm", "-r", "150", "-png", str(pdf.resolve()),
                        str(carpeta / "pagina")], check=True, capture_output=True, timeout=120)
        paginas = sorted(carpeta.glob("pagina-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
        if not paginas:
            raise ValueError("El PDF no contiene páginas que se puedan leer.")
        propiedades = {k: {"type": [tipo, "null"]} for k, tipo in {**CAMPOS, **CAMPOS_QR}.items()}
        propiedades.update(confianza_por_campo=esquema_confianza(), total_simple={"type": "boolean"},
                           incidencias={"type": "array", "items": {"type": "string"}})
        esquema = {"type": "object", "properties": propiedades,
                   "required": list(propiedades), "additionalProperties": False}
        lectura = _consultar_modelo(paginas, modelo, PREGUNTA, esquema)
        if not isinstance(lectura, dict) or "confianza_por_campo" not in lectura:
            raise ValueError("La respuesta del modelo no contiene la legibilidad por campo.")
        return revisar(lectura, leer_qr(paginas), proveedores)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("pdf", type=Path, help="Factura PDF en euros")
    cli.add_argument("--model", help="Modelo disponible en tu sesión de Codex")
    cli.add_argument("--proveedores", type=Path, metavar="JSON",
                     help="Exige que el nombre y NIF concuerden con un directorio ya verificado.")
    args = cli.parse_args()
    try:
        proveedores = cargar_proveedores(args.proveedores) if args.proveedores else None
        print(json.dumps(leer(args.pdf, args.model, proveedores), ensure_ascii=False, indent=2))
    except FileNotFoundError as exc:
        print(f"No se encuentra el archivo o programa solicitado: {exc.filename}.", file=sys.stderr)
    except subprocess.CalledProcessError as exc:
        detalle = exc.stderr.decode(errors="replace").strip().splitlines()
        print(f"Falló {exc.cmd[0]}: {detalle[-1] if detalle else 'sin detalles'}", file=sys.stderr)
    except (ValueError, OSError, subprocess.TimeoutExpired, ArithmeticError) as exc:
        print(f"No se pudo leer la factura: {exc}", file=sys.stderr)
    else:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
