import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from lector import leer
from test_lector import lectura_de_nuria


PDF = Path(__file__).parent / "examples" / "nuria-110px.pdf"
NURIA = "Nuria Beltrán Llopis"
NURIA_CON_TILDE = "Núria Beltrán Llopis"
MARIA = "María Beltrán Llopis"


def sin_nif():
    lectura = lectura_de_nuria(nif=None)
    lectura["confianza_por_campo"]["nif"] = "ilegible"
    return lectura


def nombre_leido(nombre, legibilidad="claro"):
    return {"nombre": nombre, "legibilidad": legibilidad}


class RelecturaSelectiva(unittest.TestCase):
    def leer_con_respuestas(self, *respuestas, proveedores=None, qr=None):
        def renderizar(cmd, **kwargs):
            self.assertEqual(cmd[0], "pdftoppm")
            Path(str(cmd[-1]) + "-1.png").touch()

        if qr is None:
            qr = {"estado": "sin_qr_fiscal"}
        with patch("lector.subprocess.run", side_effect=renderizar) as render, \
                patch("lector.leer_qr", return_value=qr), \
                patch("lector._consultar_modelo", side_effect=respuestas) as modelo:
            salida = leer(PDF, proveedores=proveedores)
        render.assert_called_once()
        self.assertEqual(modelo.call_count, len(respuestas))
        return salida

    def test_una_sola_lectura_si_la_identidad_esta_clara(self):
        for lectura, directorio, estado in (
            (lectura_de_nuria(), None, "leido"),
            (lectura_de_nuria(importe_total=210), None, "revisar"),
            (lectura_de_nuria(), {}, "revisar"),
        ):
            with self.subTest(estado=estado, directorio=directorio):
                salida = self.leer_con_respuestas(lectura, proveedores=directorio)
                self.assertEqual(salida["estado"], estado)
                self.assertEqual(salida["relectura_emisor"]["estado"], "no_necesaria")

    def test_reproduce_las_tres_grafias_de_la_prueba_de_nuria(self):
        salida = self.leer_con_respuestas(
            sin_nif(), nombre_leido(NURIA_CON_TILDE), nombre_leido(MARIA)
        )
        auditoria = salida["relectura_emisor"]
        self.assertEqual(auditoria["estado"], "distintos")
        self.assertEqual([v["nombre"] for v in auditoria["lecturas"]], [NURIA, NURIA_CON_TILDE, MARIA])
        self.assertEqual(salida["revision_campos"]["emisor"]["decision"], "revisar")
        self.assertIsNone(salida["emisor"])
        self.assertIsNone(salida["nif"])
        self.assertEqual([salida[k] for k in ("base", "iva", "retencion")], [187.65, 39.41, 28.15])

    def test_desacuerdo_directo_o_relectura_ilegible_apartan_el_nombre(self):
        for observacion, estado in (
            (nombre_leido(MARIA), "distintos"),
            (nombre_leido(None, "ilegible"), "sin_confirmar"),
        ):
            with self.subTest(estado=estado):
                salida = self.leer_con_respuestas(sin_nif(), observacion)
                self.assertEqual(salida["relectura_emisor"]["estado"], estado)
                self.assertIsNone(salida["emisor"])
                self.assertEqual(salida["revision_campos"]["emisor"]["decision"], "revisar")

    def test_una_mayoria_no_resuelve_una_tilde(self):
        salida = self.leer_con_respuestas(
            sin_nif(), nombre_leido(NURIA_CON_TILDE), nombre_leido(NURIA)
        )
        self.assertEqual(salida["relectura_emisor"]["estado"], "variante_grafica")
        self.assertIsNone(salida["emisor"])

    def test_no_confunde_la_enie_con_un_cambio_de_acento(self):
        lectura = sin_nif()
        lectura["emisor"] = "Ana Peña"
        salida = self.leer_con_respuestas(lectura, nombre_leido("Ana Pena"))
        self.assertEqual(salida["relectura_emisor"]["estado"], "distintos")
        self.assertIsNone(salida["emisor"])

    def test_el_acuerdo_no_levanta_una_revision_previa(self):
        dudoso = lectura_de_nuria()
        dudoso["confianza_por_campo"]["emisor"] = "dudoso"
        for lectura, directorio, nombre_esperado in (
            (sin_nif(), None, NURIA),
            (lectura_de_nuria(), {"30847612N": MARIA}, None),
            (dudoso, None, None),
        ):
            with self.subTest(lectura=lectura, directorio=directorio):
                salida = self.leer_con_respuestas(lectura, nombre_leido(NURIA), proveedores=directorio)
                self.assertEqual(salida["emisor"], nombre_esperado)
                self.assertEqual(salida["nif"], lectura["nif"])
                self.assertEqual(salida["estado"], "revisar")

    def test_nif_en_conflicto_con_el_qr_sigue_pendiente_aunque_el_nombre_coincida(self):
        qr = {"estado": "detectado", "campos": {
            "nif": "12345678Z", "numserie": "X-71", "fecha": "26-11-2026", "importe": "227.06",
        }}
        salida = self.leer_con_respuestas(lectura_de_nuria(), nombre_leido(NURIA), qr=qr)
        self.assertEqual(salida["relectura_emisor"]["estado"], "coinciden")
        self.assertIsNone(salida["nif"])
        self.assertEqual(salida["revision_campos"]["nif"]["decision"], "revisar")

    def test_un_fallo_del_segundo_intento_no_descarta_los_importes(self):
        salida = self.leer_con_respuestas(sin_nif(), subprocess.TimeoutExpired("codex", 180))
        self.assertIsNone(salida["emisor"])
        self.assertEqual(salida["revision_campos"]["emisor"]["decision"], "revisar")
        self.assertEqual(salida["estado"], "revisar")
        self.assertEqual(salida["base"], 187.65)
        self.assertEqual(salida["relectura_emisor"]["lecturas"][0]["nombre"], NURIA)


if __name__ == "__main__":
    unittest.main()
