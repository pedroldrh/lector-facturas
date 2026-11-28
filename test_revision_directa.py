import json
import unittest
from pathlib import Path
from unittest.mock import patch

from lector import leer
from test_lector import lectura_de_nuria


EJEMPLOS = Path(__file__).parent / "examples"
KRAMER = EJEMPLOS / "bar-kramer"


class RevisionDirecta(unittest.TestCase):
    def leer_una_vez(self, lectura, pdf=EJEMPLOS / "nuria-110px.pdf", proveedores=None, qr=None):
        def renderizar(cmd, **kwargs):
            self.assertEqual(cmd[0], "pdftoppm")
            Path(str(cmd[-1]) + "-1.png").touch()

        with patch("lector.subprocess.run", side_effect=renderizar), \
                patch("lector.leer_qr", return_value=qr or {"estado": "sin_qr_fiscal"}), \
                patch("lector._consultar_modelo", return_value=lectura) as modelo:
            resultado = leer(pdf, proveedores=proveedores)
        modelo.assert_called_once()
        self.assertNotIn("relectura_emisor", resultado)
        return resultado

    def test_tique_del_bar_kramer(self):
        primera = json.loads((KRAMER / "lecturas.json").read_text(encoding="utf-8"))[0]
        salida = self.leer_una_vez(primera, KRAMER / "tique.pdf")
        self.assertEqual(salida["estado"], "revisar")
        self.assertIsNone(salida["emisor"])
        self.assertEqual(salida["revision_campos"]["emisor"]["decision"], "revisar")
        self.assertEqual(salida["revision_campos"]["emisor"]["candidato"], "ROOMS AND HOST SERVICES SL")
        self.assertIn(primera["incidencias"][0], salida["motivos"])
        self.assertEqual(salida["nif"], "B98331887")
        self.assertEqual(salida["base"], 72.5)
        self.assertEqual(salida["iva"], 7.25)
        self.assertEqual(salida["revision_campos"]["retencion"]["decision"], "no_aplica")

    def test_kramer_si_el_modelo_se_equivoca_sin_dudar(self):
        primera = json.loads((KRAMER / "lecturas.json").read_text(encoding="utf-8"))[0]
        primera["confianza_por_campo"]["emisor"] = "claro"
        primera["incidencias"] = []
        tique = KRAMER / "tique.pdf"
        sin_ficha = self.leer_una_vez(primera, tique)
        self.assertEqual(sin_ficha["emisor"], "ROOMS AND HOST SERVICES SL")
        self.assertEqual(sin_ficha["estado"], "leido")

        con_ficha = self.leer_una_vez(primera, tique, proveedores={
            "B98331887": "Emprendimientos Hosteleros Valencia S.L.",
        })
        self.assertEqual(con_ficha["estado"], "revisar")
        self.assertIsNone(con_ficha["emisor"])
        self.assertEqual(con_ficha["revision_campos"]["emisor"]["contraste_directorio"], "discrepancia")

    def test_una_duda_en_cualquier_campo_pasa_al_gestor(self):
        for campo in ("emisor", "nif", "base", "iva", "retencion"):
            with self.subTest(campo=campo):
                lectura = lectura_de_nuria()
                lectura["confianza_por_campo"][campo] = "dudoso"
                resultado = self.leer_una_vez(lectura)
                self.assertEqual(resultado["estado"], "revisar")
                self.assertIsNone(resultado[campo])
                for nombre, detalle in resultado["revision_campos"].items():
                    if nombre == campo:
                        self.assertEqual(detalle["decision"], "revisar")
                        self.assertEqual(detalle["candidato"], lectura[campo])
                    else:
                        self.assertEqual(detalle["decision"], "usar")
                        self.assertEqual(resultado[nombre], lectura[nombre])

    def test_un_nif_en_conflicto_con_el_qr_pasa_al_gestor(self):
        qr = {"estado": "detectado", "campos": {
            "nif": "12345678Z", "numserie": "X-71", "fecha": "26-11-2026", "importe": "227.06",
        }}
        resultado = self.leer_una_vez(lectura_de_nuria(), qr=qr)
        self.assertEqual(resultado["estado"], "revisar")
        self.assertIsNone(resultado["nif"])
        self.assertEqual(resultado["revision_campos"]["nif"]["decision"], "revisar")


if __name__ == "__main__":
    unittest.main()
