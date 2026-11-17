"""Testes básicos de leitura e geração do intercâmbio CAD -> BIM."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bridge_dxf", ROOT / "bridge" / "dxf_para_bim.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class TestPonte(unittest.TestCase):
    def setUp(self):
        self.sample = (ROOT / "exemplos" / "quarto.dxf").read_text(encoding="utf-8")

    def test_quatro_paredes_e_nao_importa_mobiliario(self):
        text = bridge.converter(self.sample, unidade="mm")
        self.assertEqual(text.count("\nwall "), 4)
        self.assertIn("[4000, 3000]", text)
        self.assertNotIn("[400, 400]", text)

    def test_converter_unidade_metro(self):
        text = self.sample.replace("\n4000\n", "\n4\n").replace("\n3000\n", "\n3\n")
        result = bridge.converter(text, unidade="m")
        self.assertIn("[4000, 3000]", result)

    def test_camada_inexistente_da_erro(self):
        with self.assertRaises(bridge.ErroConversao):
            bridge.converter(self.sample, camada="CAMADA_ERRADA", unidade="mm")

    def test_dxf_truncado_da_erro(self):
        with self.assertRaises(bridge.ErroConversao):
            bridge.converter(self.sample + "\n10", unidade="mm")

    def test_zero_comprimento_ignorado(self):
        data = """0
SECTION
2
ENTITIES
0
LINE
8
WMK_PAREDES
10
0
20
0
11
0
21
0
0
ENDSEC
0
EOF
"""
        with self.assertRaises(bridge.ErroConversao):
            bridge.converter(data, unidade="mm")


if __name__ == "__main__":
    unittest.main()
