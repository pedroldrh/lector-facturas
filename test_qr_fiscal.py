import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from lector import revisar
from qr_fiscal import analizar_contenidos, leer_qr


EJEMPLOS = Path(__file__).resolve().parent / "examples"
NIF_EMISOR = "B00000018"
NIF_CLIENTE = "B00000026"
URL_AEAT = "https://prewww2.aeat.es/wlpl/TIKE-CONT/ValidarQR"
PARAMETROS = "?nif=B00000018&numserie=F-081&fecha=26-11-2026&importe=121.00"


def lectura_impresa():
    """Transcripción controlada de los dos PDF de prueba, idénticos en el papel."""
    return {
        "emisor": "Muestra Ámbar, S.L.", "nif": NIF_EMISOR,
        "base": 100, "iva": 21, "retencion": 0, "importe_total": 121,
        "tipo_iva": 21, "tipo_retencion": 0, "total_simple": True,
        "incidencias": [],
        "numero_factura": "F-081", "fecha_expedicion": "26-11-2026",
        "total_fiscal_impreso": 121,
        "confianza_por_campo": dict.fromkeys(("emisor", "nif", "base", "iva", "retencion"), "claro"),
    }


def renderizar(pdf, carpeta):
    prefijo = Path(carpeta) / pdf.stem
    subprocess.run(
        ["pdftoppm", "-f", "1", "-l", "1", "-singlefile", "-r", "150", "-png",
         str(pdf), str(prefijo)], check=True, capture_output=True, timeout=90,
    )
    return prefijo.with_suffix(".png")


def revisar_con_codigos(lectura, codigos):
    return revisar(lectura, analizar_contenidos(codigos))


class ContrasteDeIdentidad(unittest.TestCase):
    def test_el_nif_intercambiado_solo_se_detecta_con_el_qr(self):
        lectura = lectura_impresa()
        lectura["nif"] = NIF_CLIENTE
        self.assertEqual(revisar(lectura)["estado"], "leido")
        resultado = revisar_con_codigos(lectura, [URL_AEAT + PARAMETROS])
        self.assertEqual(resultado["estado"], "revisar")
        self.assertIsNone(resultado["nif"])
        self.assertEqual(resultado["revision_campos"]["nif"]["candidato"], NIF_CLIENTE)
        self.assertTrue(any("nif" in m.lower() for m in resultado["motivos"]))

    def test_conserva_el_nif_impreso_con_prefijo_y_separadores(self):
        lectura = lectura_impresa()
        lectura["nif"] = "ES B-00000018"
        resultado = revisar_con_codigos(lectura, [URL_AEAT + PARAMETROS])
        self.assertEqual(resultado["qr_fiscal"]["estado"], "coincide")
        self.assertEqual(resultado["nif"], "ES B-00000018")

    def test_paginas_con_el_mismo_qr_son_una_sola_referencia(self):
        codigo = URL_AEAT + PARAMETROS
        resultado = revisar_con_codigos(lectura_impresa(), [codigo, codigo])
        self.assertEqual(resultado["qr_fiscal"]["estado"], "coincide")
        self.assertEqual(resultado["estado"], "leido")

    def test_dos_referencias_distintas_quedan_para_revision(self):
        codigo = URL_AEAT + PARAMETROS
        otro = codigo.replace("F-081", "F-082")
        resultado = revisar_con_codigos(lectura_impresa(), [codigo, otro])
        self.assertEqual(resultado["qr_fiscal"]["estado"], "ambiguo")
        self.assertEqual(resultado["estado"], "revisar")

    def test_qr_ajeno_no_es_evidencia_fiscal(self):
        for codigos in ([], ["https://ejemplo.invalid/tienda" + PARAMETROS],
                        [URL_AEAT.replace("aeat.es/", "aeat.es.ejemplo.invalid/") + PARAMETROS]):
            with self.subTest(codigos=codigos):
                resultado = revisar_con_codigos(lectura_impresa(), codigos)
                self.assertEqual(resultado["qr_fiscal"]["estado"], "sin_qr_fiscal")
                self.assertEqual(resultado["estado"], "leido")

    def test_una_discrepancia_en_numero_fecha_o_importe_requiere_revision(self):
        for antes, despues in (("F-081", "F-082"), ("26-11-2026", "25-11-2026"),
                               ("121.00", "121.01")):
            with self.subTest(despues=despues):
                codigo = URL_AEAT + PARAMETROS.replace(antes, despues)
                resultado = revisar_con_codigos(lectura_impresa(), [codigo])
                self.assertEqual(resultado["qr_fiscal"]["estado"], "discrepancia")
                self.assertEqual(resultado["estado"], "revisar")

    def test_un_qr_fiscal_incompleto_no_puede_coincidir(self):
        codigo = URL_AEAT + PARAMETROS.replace("&numserie=F-081", "")
        resultado = revisar_con_codigos(lectura_impresa(), [codigo])
        self.assertEqual(resultado["qr_fiscal"]["estado"], "invalido")
        self.assertEqual(resultado["estado"], "revisar")

    def test_sin_fecha_impresa_el_qr_no_verifica_los_cuatro_campos(self):
        lectura = lectura_impresa()
        lectura.pop("fecha_expedicion")
        resultado = revisar_con_codigos(lectura, [URL_AEAT + PARAMETROS])
        self.assertEqual(resultado["qr_fiscal"]["estado"], "parcial")

    def test_retencion_sin_total_fiscal_impreso(self):
        lectura = lectura_impresa()
        lectura.update(retencion=15, tipo_retencion=15, importe_total=106,
                       total_fiscal_impreso=None)
        resultado = revisar_con_codigos(lectura, [URL_AEAT + PARAMETROS])
        self.assertEqual(resultado["qr_fiscal"]["estado"], "parcial")
        self.assertEqual(resultado["total_impreso"], 106)


@unittest.skipUnless(shutil.which("pdftoppm") and importlib.util.find_spec("PIL")
                     and importlib.util.find_spec("zxingcpp"),
                     "Requiere Poppler, Pillow y zxing-cpp")
class CodigosEnElPDF(unittest.TestCase):
    def test_lectura_de_los_ejemplos_tras_renderizarlos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            for nombre, nif_qr, nif_utilizable, esperado in (
                ("coincide", NIF_EMISOR, NIF_EMISOR, "leido"),
                ("conflicto-nif", NIF_CLIENTE, None, "revisar"),
            ):
                with self.subTest(nombre=nombre):
                    imagen = renderizar(EJEMPLOS / "qr" / (nombre + ".pdf"), carpeta)
                    qr = leer_qr([imagen])
                    self.assertEqual(qr["campos"]["nif"], nif_qr)
                    resultado = revisar(lectura_impresa(), qr)
                    self.assertEqual(resultado["estado"], esperado)
                    self.assertEqual(resultado["nif"], nif_utilizable)
