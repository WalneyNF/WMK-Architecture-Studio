import sys
from pathlib import Path
import tempfile
import unittest

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wmk_detector_planta import detectar_linhas, exportar_dxf, carregar_imagem


class DetectorTests(unittest.TestCase):
    def test_uma_parede_colorida(self):
        img = np.full((300, 400, 3), 255, dtype=np.uint8)
        cv2.line(img, (30, 80), (355, 80), (0, 125, 235), 8)
        result = detectar_linhas(img, modo='laranja', minimo=40)
        self.assertGreaterEqual(len(result['linhas']), 1)
        self.assertTrue(any(x['orientacao'] == 'h' and x['fim_px'][0]-x['inicio_px'][0] > 200 for x in result['linhas']))

    def test_dxf_abre_e_possui_linhas(self):
        import ezdxf
        dados = {'altura': 300, 'linhas': [{'inicio_px': [10, 20], 'fim_px': [180, 20]}]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'teste.dxf'
            exportar_dxf(dados, path)
            doc = ezdxf.readfile(str(path))
            self.assertEqual(len(doc.modelspace().query('LINE')), 1)
            self.assertEqual(doc.header.get('$INSUNITS'), 0)

    def test_escala_mm_explicitamente(self):
        import ezdxf
        dados = {'altura': 300, 'linhas': [{'inicio_px': [10, 20], 'fim_px': [110, 20]}]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'teste.dxf'
            exportar_dxf(dados, path, mm_por_pixel=10)
            d = ezdxf.readfile(str(path))
            self.assertEqual(d.header.get('$INSUNITS'), 4)
            line = list(d.modelspace().query('LINE'))[0]
            self.assertAlmostEqual(line.dxf.end.x - line.dxf.start.x, 1000)


if __name__ == '__main__':
    unittest.main()

class WmkRegressionTests(unittest.TestCase):
    def test_autodeteccao_diferencia_laranja_de_madeira(self):
        img = np.full((320, 500, 3), 235, dtype=np.uint8)
        # parede laranja saturada conectada (emulando a primeira planta)
        cv2.rectangle(img, (15, 15), (310, 290), (0, 122, 245), 7)
        # mesa marrom com outro perfil tonal
        cv2.rectangle(img, (350, 110), (470, 170), (65, 90, 143), -1)
        result = detectar_linhas(img, modo='auto', minimo=35)
        self.assertEqual(result['modo_usado'], 'laranja')
        self.assertTrue(result['linhas'])
        self.assertTrue(all(max(l['inicio_px'][0], l['fim_px'][0]) <= 335 for l in result['linhas']))

    def test_exportacao_apenas_linhas_ativas(self):
        import ezdxf
        d = dict(altura=200, linhas=[
          dict(inicio_px=[10,20],fim_px=[170,20],ativo=True),
          dict(inicio_px=[10,30],fim_px=[170,30],ativo=False),
        ])
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'linhas-revisadas.dxf'
            exportar_dxf(d,file,mm_por_pixel=5,apenas_ativos=True)
            loaded=ezdxf.readfile(str(file))
            entities=list(loaded.modelspace().query('LINE'))
            self.assertEqual(len(entities), 1)
            self.assertEqual(entities[0].dxf.layer,'WMK_PAREDES_REVISADAS')
            self.assertAlmostEqual(entities[0].dxf.end.x-entities[0].dxf.start.x,800.0)

    def test_auto_na_planta_simples_usa_escuro(self):
        image=Path(__file__).resolve().parents[1]/'amostras'/'planta-03-simples.png'
        if not image.exists():
            self.skipTest('Planta de amostra não distribuída')
        result=detectar_linhas(carregar_imagem(image))
        self.assertEqual(result['modo_usado'], 'escuro')
