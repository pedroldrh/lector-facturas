import tempfile
import unittest
from pathlib import Path

from confianza import cargar_proveedores
from lector import revisar
from qr_fiscal import analizar_contenidos


NIF = "30847612N"
NOMBRE = "Nuria Beltrán Llopis"
CANDIDATO = "María Beltrán Llopis"
QR = analizar_contenidos([
    f"https://prewww2.aeat.es/wlpl/TIKE-CONT/ValidarQR?nif={NIF}"
    "&numserie=X-71&fecha=26-11-2026&importe=227.06"
])


def lectura_controlada():
    return {
        "emisor": NOMBRE, "nif": NIF, "base": 187.65, "iva": 39.41,
        "retencion": 28.15, "importe_total": 198.91, "tipo_iva": 21,
        "tipo_retencion": 15, "total_simple": True, "incidencias": [],
        "numero_factura": "X-71", "fecha_expedicion": "26-11-2026",
        "total_fiscal_impreso": 227.06,
        "confianza_por_campo": dict.fromkeys(("emisor", "nif", "base", "iva", "retencion"), "claro"),
    }


class RevisionPorCampo(unittest.TestCase):
    def test_nombre_dudoso_con_nif_y_qr_legibles(self):
        lectura = lectura_controlada()
        lectura["emisor"] = CANDIDATO
        lectura["confianza_por_campo"]["emisor"] = "dudoso"
        resultado = revisar(lectura, qr=QR)
        self.assertEqual(resultado["qr_fiscal"]["estado"], "coincide")
        self.assertEqual(resultado["estado"], "revisar")
        self.assertIsNone(resultado["emisor"])
        detalle = resultado["revision_campos"]["emisor"]
        self.assertEqual(detalle["decision"], "revisar")
        self.assertEqual(detalle["candidato"], CANDIDATO)
        for campo in ("nif", "base", "iva", "retencion"):
            self.assertEqual(resultado[campo], lectura[campo])

    def test_nombre_que_parece_claro_pero_discrepa_del_proveedor_verificado(self):
        lectura = lectura_controlada()
        lectura["emisor"] = CANDIDATO
        resultado = revisar(lectura, qr=QR, proveedores={NIF: NOMBRE})
        self.assertEqual(resultado["estado"], "revisar")
        self.assertEqual(resultado["nif"], NIF)
        self.assertIsNone(resultado["emisor"])
        detalle = resultado["revision_campos"]["emisor"]
        self.assertEqual(detalle["candidato"], CANDIDATO)
        self.assertEqual(detalle["nombre_directorio"], NOMBRE)
        self.assertEqual(detalle["contraste_directorio"], "discrepancia")

    def test_un_directorio_no_rellena_el_nombre_ilegible(self):
        lectura = lectura_controlada()
        lectura["emisor"] = None
        lectura["confianza_por_campo"]["emisor"] = "ilegible"
        resultado = revisar(lectura, proveedores={NIF: NOMBRE})
        self.assertIsNone(resultado["emisor"])
        self.assertEqual(resultado["estado"], "revisar")

    def test_nif_que_contradice_el_qr_no_autoriza_el_nombre_del_directorio(self):
        lectura = lectura_controlada()
        lectura["nif"] = "12345678Z"
        resultado = revisar(lectura, qr=QR, proveedores={"12345678Z": NOMBRE})
        self.assertEqual(resultado["estado"], "revisar")
        self.assertIsNone(resultado["emisor"])
        self.assertIsNone(resultado["nif"])
        self.assertEqual(resultado["revision_campos"]["nif"]["candidato"], "12345678Z")
        self.assertNotEqual(resultado["revision_campos"]["emisor"]["contraste_directorio"], "coincide")

    def test_nif_dudoso_no_permite_verificar_al_proveedor(self):
        lectura = lectura_controlada()
        lectura["confianza_por_campo"]["nif"] = "dudoso"
        resultado = revisar(lectura, proveedores={NIF: NOMBRE})
        self.assertIsNone(resultado["nif"])
        self.assertIsNone(resultado["emisor"])
        self.assertEqual(resultado["estado"], "revisar")
        self.assertEqual(resultado["revision_campos"]["emisor"]["contraste_directorio"],
                         "nif_no_utilizable")

    def test_nif_sin_alta_en_directorio_requiere_verificar_nombre(self):
        resultado = revisar(lectura_controlada(), proveedores={})
        self.assertEqual(resultado["estado"], "revisar")
        self.assertIsNone(resultado["emisor"])
        self.assertEqual(resultado["revision_campos"]["emisor"]["candidato"], NOMBRE)
        self.assertEqual(resultado["revision_campos"]["emisor"]["contraste_directorio"],
                         "sin_referencia")

    def test_lectura_antigua_no_inventa_confianza_para_el_nombre(self):
        lectura = lectura_controlada()
        lectura["emisor"] = CANDIDATO
        del lectura["confianza_por_campo"]
        resultado = revisar(lectura)
        self.assertEqual(resultado["estado"], "revisar")
        self.assertIsNone(resultado["emisor"])
        self.assertEqual(resultado["nif"], NIF)
        self.assertEqual(resultado["revision_campos"]["emisor"]["legibilidad"], "sin_evaluar")
        self.assertEqual(resultado["revision_campos"]["emisor"]["candidato"], CANDIDATO)

    def test_un_importe_dudoso_se_aparta_aunque_los_numeros_cuadren(self):
        lectura = lectura_controlada()
        lectura["confianza_por_campo"]["iva"] = "dudoso"
        resultado = revisar(lectura)
        self.assertIsNone(resultado["iva"])
        self.assertEqual(resultado["revision_campos"]["iva"]["candidato"], 39.41)
        self.assertEqual(resultado["estado"], "revisar")
        self.assertEqual(resultado["base"], lectura["base"])

    def test_ausencia_normal_y_retenida_pero_ilegible_se_distinguen(self):
        lectura = lectura_controlada()
        lectura.update(retencion=None, tipo_retencion=None, importe_total=227.06)
        lectura["confianza_por_campo"]["retencion"] = "no_aplica"
        resultado = revisar(lectura)
        self.assertEqual(resultado["estado"], "leido")
        self.assertEqual(resultado["revision_campos"]["retencion"]["decision"], "no_aplica")
        lectura["confianza_por_campo"]["retencion"] = "ilegible"
        self.assertEqual(revisar(lectura)["estado"], "revisar")

    def test_no_aplica_no_descarta_una_retencion_impresa(self):
        lectura = lectura_controlada()
        lectura["confianza_por_campo"]["retencion"] = "no_aplica"
        resultado = revisar(lectura)
        self.assertEqual(resultado["estado"], "revisar")
        self.assertIsNone(resultado["retencion"])
        self.assertEqual(resultado["revision_campos"]["retencion"]["candidato"], 28.15)

    def test_valor_ausente_no_se_acepta_aunque_se_califique_como_claro(self):
        lectura = lectura_controlada()
        lectura["emisor"] = None
        resultado = revisar(lectura)
        self.assertIsNone(resultado["emisor"])
        self.assertEqual(resultado["revision_campos"]["emisor"]["decision"], "revisar")
        self.assertEqual(resultado["estado"], "revisar")

    def test_bloque_de_confianza_parcial_o_invalido_no_se_acepta(self):
        for valor in (None, "no_aplica", "99%"):
            with self.subTest(valor=valor):
                lectura = lectura_controlada()
                if valor is None:
                    del lectura["confianza_por_campo"]["emisor"]
                else:
                    lectura["confianza_por_campo"]["emisor"] = valor
                with self.assertRaises(ValueError):
                    revisar(lectura)

    def test_proveedor_en_directorio_local(self):
        with tempfile.TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / "proveedores.json"
            archivo.write_text('{"ES 30847612-N":"Nuria Beltrán Llopis"}', encoding="utf-8")
            resultado = revisar(lectura_controlada(), proveedores=cargar_proveedores(archivo))
        self.assertEqual(resultado["estado"], "leido")
        self.assertEqual(resultado["emisor"], NOMBRE)
        self.assertEqual(resultado["revision_campos"]["emisor"]["contraste_directorio"], "coincide")


if __name__ == "__main__":
    unittest.main()
