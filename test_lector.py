import json
import unittest
from pathlib import Path

from lector import revisar


def lectura_de_nuria(**cambios):
    return {
        "emisor": "Nuria Beltrán Llopis", "nif": "30847612N",
        "base": 187.65, "iva": 39.41, "retencion": 28.15, "importe_total": 198.91,
        "tipo_iva": 21, "tipo_retencion": 15, "total_simple": True, "incidencias": [],
        "confianza_por_campo": dict.fromkeys(("emisor", "nif", "base", "iva", "retencion"), "claro"),
        **cambios,
    }


class RevisionDeFactura(unittest.TestCase):
    def comprobar_campos_en_revision(self, lectura, resultado, campos):
        self.assertEqual(resultado["estado"], "revisar")
        for campo, legibilidad in lectura["confianza_por_campo"].items():
            detalle = resultado["revision_campos"][campo]
            self.assertEqual(detalle["legibilidad"], legibilidad, campo)
            if campo in campos:
                self.assertIsNone(resultado[campo], campo)
                self.assertEqual(detalle["decision"], "revisar", campo)
                self.assertEqual(detalle["candidato"], lectura[campo], campo)
                self.assertTrue(detalle["motivos"], campo)
                self.assertTrue(set(detalle["motivos"]).issubset(resultado["motivos"]), campo)
            else:
                self.assertEqual(resultado[campo], lectura[campo], campo)
                decision = "no_aplica" if legibilidad == "no_aplica" else "usar"
                self.assertEqual(detalle["decision"], decision, campo)

    def test_fallo_de_nombre_guardado(self):
        ruta = Path(__file__).parent / "examples" / "lectura-original.json"
        original = json.loads(ruta.read_text(encoding="utf-8"))
        # Se trasladan los cinco campos del experimento al formato actual. Los tipos
        # y el total simple se comprueban en la factura nítida del mismo ejemplo.
        lectura = {
            "emisor": original["issuer"], "nif": original["issuer_tax_id"],
            "base": original["base"], "iva": original["vat"],
            "retencion": original["withholding"], "importe_total": original["printed_total"],
            "tipo_iva": 21, "tipo_retencion": 15, "total_simple": True,
            "incidencias": [],
        }
        resultado = revisar(lectura)
        self.assertIsNone(resultado["emisor"])
        self.assertEqual(resultado["revision_campos"]["emisor"]["candidato"], original["issuer"])
        self.assertEqual(resultado["estado"], "revisar")
        self.assertTrue(any("nif" in s.lower() for s in resultado["motivos"]))

    def test_importes_erroneos_que_cuadran(self):
        # Al borrarse el primer dígito, la base y el total pierden 100 € cada uno.
        lectura = lectura_de_nuria(base=87.65, importe_total=98.91)
        resultado = revisar(lectura)
        self.assertEqual(resultado["total_impreso"], 98.91)
        self.assertTrue(any("iva" in s.lower() for s in resultado["motivos"]))
        self.comprobar_campos_en_revision(lectura, resultado, {"base", "iva", "retencion"})

    def test_una_cuota_incompatible_aparta_solo_la_base_y_esa_cuota(self):
        for campo, cuota, total in (("iva", 40.41, 199.91), ("retencion", 29.15, 197.91)):
            with self.subTest(campo=campo):
                lectura = lectura_de_nuria(importe_total=total)
                lectura[campo] = cuota
                self.comprobar_campos_en_revision(lectura, revisar(lectura), {"base", campo})

    def test_total_incompatible_aparta_los_importes_que_intervienen(self):
        lectura = lectura_de_nuria(importe_total=199.91)
        lectura["confianza_por_campo"]["iva"] = "dudoso"
        resultado = revisar(lectura)
        self.assertEqual(resultado["total_impreso"], 199.91)
        self.comprobar_campos_en_revision(lectura, resultado, {"base", "iva", "retencion"})

    def test_total_incompatible_con_retencion_no_aplicable(self):
        for retencion in (None, 0):
            with self.subTest(retencion=retencion):
                lectura = lectura_de_nuria(retencion=retencion, tipo_retencion=None, importe_total=228.06)
                lectura["confianza_por_campo"]["retencion"] = "no_aplica"
                self.comprobar_campos_en_revision(lectura, revisar(lectura), {"base", "iva"})

    def test_un_centimo_de_redondeo_permite_usar_los_importes(self):
        lectura = lectura_de_nuria(iva=39.42, importe_total=198.93)
        resultado = revisar(lectura)
        self.assertEqual(resultado["estado"], "leido")
        for campo in ("base", "iva", "retencion"):
            self.assertEqual(resultado[campo], lectura[campo])
            self.assertEqual(resultado["revision_campos"][campo]["decision"], "usar")

    def test_retencion_ilegible_no_se_toma_por_cero_al_comprobar_el_total(self):
        lectura = lectura_de_nuria(retencion=None, tipo_retencion=None)
        lectura["confianza_por_campo"]["retencion"] = "ilegible"
        resultado = revisar(lectura)
        self.assertEqual(resultado["revision_campos"]["retencion"]["decision"], "revisar")
        for campo in ("base", "iva"):
            self.assertEqual(resultado["revision_campos"][campo]["decision"], "usar")
            self.assertEqual(resultado[campo], lectura[campo])

    def test_sin_retencion_aplicable(self):
        lectura = {
            "emisor": "Estudio Olivo, S.L.", "nif": "B12345674",
            "base": 100, "iva": 21, "retencion": None, "importe_total": 121,
            "tipo_iva": 21, "tipo_retencion": None, "total_simple": True,
            "incidencias": [],
            "confianza_por_campo": {
                "emisor": "claro", "nif": "claro", "base": "claro", "iva": "claro",
                "retencion": "no_aplica",
            },
        }
        resultado = revisar(lectura)
        self.assertIsNone(resultado["retencion"])
        self.assertEqual(resultado["estado"], "leido")


if __name__ == "__main__":
    unittest.main()
