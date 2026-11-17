"""WMK Architecture Studio — protótipo verificável de vetorização de planta.

Importa imagens JPG/PNG ou primeira página PDF, encontra retas candidatas
por cor/limiarização e exporta DXF. Não é segmentação semântica/BIM.
Copyright (c) 2026 Walney Moreira Klein.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cv2
import numpy as np


def carregar_imagem(path: str | Path) -> np.ndarray:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo inexistente: {path}")
    if path.suffix.lower() == '.pdf':
        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError("PDF requer PyMuPDF: pip install pymupdf") from exc
        doc = fitz.open(str(path))
        if not len(doc):
            raise ValueError('PDF vazio')
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        raw = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
        return cv2.cvtColor(raw, cv2.COLOR_RGB2BGR)
    raw = np.fromfile(str(path), np.uint8)
    image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError('Imagem inválida ou formato não suportado')
    return image


def gerar_mascara(image: np.ndarray, modo: str = 'auto') -> tuple[np.ndarray, str]:
    if modo not in ('auto', 'laranja', 'escuro'):
        raise ValueError('modo: auto, laranja ou escuro')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    orangemask = cv2.inRange(hsv, np.array([4, 135, 170]), np.array([24, 255, 255]))
    orange_ratio = cv2.countNonZero(orangemask) / (image.shape[0] * image.shape[1])
    if modo == 'auto':
        # A planta com paredes coloridas possui pelo menos um bloco
        # longo e conectado de tinta laranja. Madeiras/estofados geram
        # pequenas ilhas e não devem acionar o modo automaticamente.
        components = cv2.connectedComponentsWithStats(orangemask)[2]
        largest = max((int(c[cv2.CC_STAT_AREA]) for c in components[1:]), default=0)
        modo = 'laranja' if 0.006 < orange_ratio < 0.12 and largest > image.size/3*0.002 else 'escuro'
    if modo == 'laranja':
        mask = orangemask
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Realça linhas escuras. A remoção de pequenas manchas ocorre no Hough.
        mask = cv2.inRange(gray, 0, 165)
        # Remove traços finos de letras/cotas quando há paredes mais espessas.
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    return mask, modo


def ler_textos(image: np.ndarray) -> list[dict]:
    try:
        import pytesseract
        from pytesseract import Output
        data = pytesseract.image_to_data(image, config='--psm 11', output_type=Output.DICT)
    except (ImportError, OSError, RuntimeError, Exception):
        return []
    result = []
    for i, item in enumerate(data.get('text', [])):
        item = item.strip()
        if not item:
            continue
        conf = float(data['conf'][i])
        if conf < 55:
            continue
        result.append({'texto': item, 'confianca': round(conf, 1),
                       'bbox': [int(data[k][i]) for k in ('left', 'top', 'width', 'height')]})
    return result


def detectar_linhas(image: np.ndarray, modo: str = 'auto', minimo: int | None = None) -> dict:
    h, w = image.shape[:2]
    if w < 80 or h < 80:
        raise ValueError('Imagem pequena demais; precisa ter no mínimo 80 × 80 pixels')
    fator = min(1.0, 1900 / max(w, h))
    img = cv2.resize(image, (round(w * fator), round(h * fator))) if fator < 1 else image
    hh, ww = img.shape[:2]
    mask, usado = gerar_mascara(img, modo)
    length = minimo or max(28, round(min(ww, hh) * (0.10 if usado == 'escuro' else 0.045)))
    raw = cv2.HoughLinesP(mask, rho=1, theta=np.pi/180, threshold=max(20, length//2),
                          minLineLength=length, maxLineGap=10)
    lines = []
    for entry in (raw[:, 0].tolist() if raw is not None else []):
        x1, y1, x2, y2 = entry
        dx, dy = x2-x1, y2-y1
        angle = math.atan2(dy, dx)
        # Planta técnica: foco nas retas horizontais/verticais; evita muitas diagonais de móveis.
        if abs(dy) <= abs(dx) * 0.14:
            direction = 'h'
            pos = (y1+y2)/2
            start, end = sorted((x1, x2))
        elif abs(dx) <= abs(dy) * 0.14:
            direction = 'v'
            pos = (x1+x2)/2
            start, end = sorted((y1, y2))
        else:
            continue
        if end - start < length:
            continue
        lines.append((direction, pos, float(start), float(end)))
    # Une fragmentos colineares e pistas paralelas próximas da mesma faixa espessa.
    lines.sort(key=lambda a: (a[0], round(a[1]/8), a[2]))
    merged = []
    for direction, pos, start, end in sorted(lines, key=lambda a: a[3]-a[2], reverse=True):
        found = None
        for seg in merged:
            if seg[0] != direction or abs(seg[1]-pos) > (7 if usado == 'laranja' else 5):
                continue
            if start > seg[3] + 12 or end < seg[2] - 12:
                continue
            found = seg
            break
        if found:
            # Uma média ponderada reduz linhas duplicadas em paredes espessas.
            found[1] = (found[1] * found[4] + pos) / (found[4] + 1)
            found[4] += 1
            found[2] = min(found[2], start)
            found[3] = max(found[3], end)
        else:
            merged.append([direction, pos, start, end, 1])
    result = []
    for direction, pos, start, end, count in merged:
        if end - start < length:
            continue
        if direction == 'h':
            p1, p2 = [start/fator, pos/fator], [end/fator, pos/fator]
        else:
            p1, p2 = [pos/fator, start/fator], [pos/fator, end/fator]
        result.append({'inicio_px': [round(v, 2) for v in p1], 'fim_px': [round(v, 2) for v in p2],
                       'orientacao': direction, 'suportes': count})
    result.sort(key=lambda x: (x['orientacao'], x['inicio_px']))
    # OCR opcional para evitar transformar letras e números em paredes.
    textos = ler_textos(image)
    blocos_texto = [t for t in textos if t['confianca'] >= 60 and len(t['texto'].strip()) >= 2]
    sem_texto = []
    for line in result:
        a, b = line['inicio_px'], line['fim_px']
        conflito = False
        for t in blocos_texto:
            x, y, tw, th = t['bbox']
            if line['orientacao'] == 'h':
                overlap = max(0, min(b[0], x+tw) - max(a[0], x))
                if y-3 <= a[1] <= y+th+3 and overlap > min(22, tw*.35):
                    conflito = True
                    break
            else:
                overlap = max(0, min(b[1], y+th) - max(a[1], y))
                if x-3 <= a[0] <= x+tw+3 and overlap > min(16, th*.35):
                    conflito = True
                    break
        if not conflito:
            sem_texto.append(line)
    result = sem_texto
    # Classificação preliminar, nunca é confirmação de parede.
    # Trechos mais longos/interligados costumam merecer revisão primeiro;
    # pequenos fragmentos isolados podem vir de móveis e textos.
    gap = max(10.0, min(w, h) * 0.022)
    def near(p, q):
        return math.dist(p, q) <= gap
    for idx, line in enumerate(result):
        a,b=line['inicio_px'],line['fim_px']
        ligacoes=sum(1 for j,other in enumerate(result) if j!=idx and any(
            near(p,q) for p in (a,b) for q in (other['inicio_px'],other['fim_px'])))
        extensao=math.dist(a,b)
        confianca=min(90, 30 + min(35, 30 * extensao / max(40, min(w,h)*0.35)) + min(25,ligacoes*9))
        line['pontuacao_heuristica']=round(confianca)
        line['conexoes']=ligacoes
        line['revisado']=False
        line['ativo']=True
    return {'largura': w, 'altura': h, 'modo_usado': usado, 'linhas': result, 'textos_ocr': textos,
            'observacao': 'Linhas candidatas; podem incluir móveis, cotas ou contornos errados.'}


def exportar_dxf(dados: dict, destino: str | Path, mm_por_pixel: float | None = None, apenas_ativos: bool = False) -> None:
    import ezdxf
    dwg = ezdxf.new('R2010')
    dwg.layers.new('WMK_PAREDES_SUGERIDAS', dxfattribs={'color': 3})
    dwg.layers.new('WMK_PAREDES_REVISADAS', dxfattribs={'color': 4})
    if mm_por_pixel is not None:
        if not math.isfinite(mm_por_pixel) or mm_por_pixel <= 0:
            raise ValueError('mm_por_pixel deve ser positivo')
        dwg.header['$INSUNITS'] = 4  # milímetros
        scale = mm_por_pixel
    else:
        dwg.header['$INSUNITS'] = 0  # sem unidade declarada, evita falsas medidas
        scale = 1.0
    model = dwg.modelspace()
    for l in dados['linhas']:
        if apenas_ativos and not l.get('ativo', True):
            continue
        a, b = l['inicio_px'], l['fim_px']
        # Inverte Y: pixels para baixo -> CAD para cima
        model.add_line((a[0]*scale, (dados['altura']-a[1])*scale),
                       (b[0]*scale, (dados['altura']-b[1])*scale),
                       dxfattribs={'layer': 'WMK_PAREDES_REVISADAS' if apenas_ativos else 'WMK_PAREDES_SUGERIDAS'})
    dwg.saveas(str(destino))


def salvar_previa(image: np.ndarray, dados: dict, path: str | Path):
    preview = image.copy()
    for l in dados['linhas']:
        if not l.get('ativo', True):
            continue
        a = tuple(round(v) for v in l['inicio_px'])
        b = tuple(round(v) for v in l['fim_px'])
        cv2.line(preview, a, b, (25, 245, 40), thickness=max(2, round(min(image.shape[:2])/350)))
    cv2.imencode('.png', preview)[1].tofile(str(path))


def executar(entrada: str | Path, saida: str | Path, modo: str = 'auto', mm_por_pixel: float | None = None) -> dict:
    entrada = Path(entrada)
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    img = carregar_imagem(entrada)
    dados = detectar_linhas(img, modo=modo)
    dados.update({'origem': entrada.name, 'unidades': 'milimetros' if mm_por_pixel else 'indefinidas',
                  'mm_por_pixel': mm_por_pixel})
    exportar_dxf(dados, saida / (entrada.stem + '.dxf'), mm_por_pixel)
    salvar_previa(img, dados, saida / (entrada.stem + '_previa.png'))
    (saida / (entrada.stem + '.json')).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding='utf-8')
    return dados


def main():
    p = argparse.ArgumentParser(description='WMK: reconhecer segmentos em planta JPG/PNG/PDF e gerar DXF')
    p.add_argument('imagem', type=Path)
    p.add_argument('--saida', type=Path, default=Path('saida'))
    p.add_argument('--modo', choices=['auto', 'laranja', 'escuro'], default='auto')
    p.add_argument('--mm-por-pixel', type=float, default=None, help='Escala REAL confirmada, em mm/pixel')
    args = p.parse_args()
    d = executar(args.imagem, args.saida, args.modo, args.mm_por_pixel)
    print(f"WMK: {len(d['linhas'])} linhas candidatas | modo={d['modo_usado']} | unidade={d['unidades']}")
    print('Confira a imagem _previa.png. DXF não representa ainda um projeto BIM.')


if __name__ == '__main__':
    main()
