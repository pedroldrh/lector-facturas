import json
import unittest
from pathlib import Path

from lector import revisar


class RevisionDeFactura(unittest.TestCase):
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
        self.assertEqual(resultado["emisor"], "María Beltrán Llopis")
        self.assertEqual(resultado["estado"], "revisar")
        self.assertTrue(any("nif" in s.lower() for s in resultado["motivos"]))

    def test_importes_erroneos_que_cuadran(self):
        # Al borrarse el primer dígito, la base y el total pierden 100 € cada uno.
        lectura = {
            "emisor": "Nuria Beltrán Llopis", "nif": "30847612N",
            "base": 87.65, "iva": 39.41, "retencion": 28.15, "importe_total": 98.91,
            "tipo_iva": 21, "tipo_retencion": 15, "total_simple": True,
            "incidencias": [],
        }
        resultado = revisar(lectura)
        self.assertEqual(resultado["total_impreso"], 98.91)
        self.assertEqual(resultado["estado"], "revisar")
        self.assertTrue(any("iva" in s.lower() for s in resultado["motivos"]))

    def test_sin_retencion_aplicable(self):
        lectura = {
            "emisor": "Estudio Olivo, S.L.", "nif": "B12345674",
            "base": 100, "iva": 21, "retencion": None, "importe_total": 121,
            "tipo_iva": 21, "tipo_retencion": None, "total_simple": True,
            "incidencias": [],
        }
        resultado = revisar(lectura)
        self.assertIsNone(resultado["retencion"])
        self.assertEqual(resultado["estado"], "leido")


if __name__ == "__main__":
    unittest.main()
