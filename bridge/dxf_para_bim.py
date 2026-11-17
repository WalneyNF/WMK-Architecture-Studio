#!/usr/bin/env python3
"""WMK Architecture Studio: ponte DXF ASCII (LINE) -> script BIMCraft de paredes.
Sem dependências externas. Não realiza inferência arquitetônica.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


class ErroConversao(ValueError):
    pass


def pares_dxf(conteudo: str):
    linhas = conteudo.splitlines()
    if len(linhas) % 2:
        raise ErroConversao("DXF ASCII incompleto: número ímpar de linhas.")
    for i in range(0, len(linhas), 2):
        try:
            codigo = int(linhas[i].strip())
        except ValueError as exc:
            raise ErroConversao(f"Código DXF inválido na linha {i + 1}.") from exc
        yield codigo, linhas[i + 1].strip()


def unidade_dxf(conteudo: str) -> int | None:
    """Extrai INSUNITS da secao HEADER; None quando nao encontrado."""
    pares = list(pares_dxf(conteudo))
    secao = ""
    for i, (codigo, valor) in enumerate(pares):
        if codigo == 0 and valor.upper() == "SECTION":
            secao = ""
        elif codigo == 2 and secao == "":
            secao = valor.upper()
        elif codigo == 0 and valor.upper() == "ENDSEC":
            secao = ""
        elif secao == "HEADER" and codigo == 9 and valor.upper() == "$INSUNITS":
            if i + 1 < len(pares) and pares[i + 1][0] == 70:
                try:
                    return int(pares[i + 1][1])
                except ValueError as exc:
                    raise ErroConversao("INSUNITS invalido.") from exc
    return None


def extrair_linhas(conteudo: str, camada: str) -> list[tuple[float, float, float, float]]:
    pares = list(pares_dxf(conteudo))
    secao = ""
    elemento = None
    campos = []
    encontrados = []

    def finalizar():
        if elemento != "LINE":
            return
        props = {}
        for k, v in campos:
            if k not in props:
                props[k] = v
        if props.get(8, "0").upper() != camada.upper():
            return
        obrigatorios = (10, 20, 11, 21)
        if any(k not in props for k in obrigatorios):
            raise ErroConversao("Linha na camada de paredes sem coordenadas completas.")
        try:
            x1, y1, x2, y2 = (float(props[k]) for k in obrigatorios)
        except ValueError as exc:
            raise ErroConversao("Linha contém coordenadas inválidas.") from exc
        if not all(math.isfinite(c) for c in (x1, y1, x2, y2)):
            raise ErroConversao("Linha contém número não finito.")
        if math.hypot(x2 - x1, y2 - y1) < 1e-6:
            return
        encontrados.append((x1, y1, x2, y2))

    i = 0
    while i < len(pares):
        codigo, valor = pares[i]
        if codigo == 0 and valor == "SECTION":
            finalizar()
            elemento, campos = None, []
            if i + 1 < len(pares) and pares[i + 1][0] == 2:
                secao = pares[i + 1][1].upper()
                i += 1
        elif codigo == 0 and valor == "ENDSEC":
            finalizar()
            elemento, campos = None, []
            secao = ""
        elif codigo == 0 and secao == "ENTITIES":
            finalizar()
            elemento, campos = valor.upper(), []
        elif secao == "ENTITIES" and elemento:
            campos.append((codigo, valor))
        i += 1
    if secao == "ENTITIES":
        finalizar()
    return encontrados


def converter(texto: str, camada: str = "WMK_PAREDES", unidade: str = "mm") -> str:
    fator = {"mm": 1, "m": 1000}.get(unidade)
    if fator is None:
        raise ErroConversao("Unidade deve ser mm ou m.")
    # Linhas geradas pelo importador WMK precisam ter escala explicitamente
    # calibrada, pois caso contrario suas coordenadas sao pixels sem unidade.
    if camada.upper() == "WMK_PAREDES_REVISADAS":
        insunits = unidade_dxf(texto)
        if insunits != 4 or unidade != "mm":
            raise ErroConversao(
                "DXF do importador sem escala valida em milimetros. "
                "Use Calibrar escala (2 pontos + medida real) antes de enviar ao BIM."
            )
    segmentos = extrair_linhas(texto, camada)
    if not segmentos:
        raise ErroConversao(f"Nenhuma LINE encontrada na camada {camada!r}.")
    comandos = [
        "# WMK Architecture Studio | DXF -> script BIM",
        "# Revisar as linhas antes de executar. Espessura adotada para ensaio: 100 mm.",
        "# Cole em Gerenciar > Executar script; primeiro clique em Testar.",
    ]
    for x1, y1, x2, y2 in segmentos:
        coords = [[round(x1 * fator), round(y1 * fator)],
                  [round(x2 * fator), round(y2 * fator)]]
        if coords[0] == coords[1]:
            continue
        parametros = {"points": coords, "type": "Interior - 100mm"}
        comandos.append("wall " + json.dumps(parametros, ensure_ascii=False))
    if len(comandos) == 3:
        raise ErroConversao("Segmentos ficaram com comprimento zero após conversão em milímetros.")
    return "\n".join(comandos) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Converter linhas de parede em DXF ASCII para comandos do WMK BIM Studio.")
    parser.add_argument("entrada", type=Path, help="DXF ASCII")
    parser.add_argument("saida", type=Path, help="TXT contendo comandos wall")
    parser.add_argument("--camada", default="WMK_PAREDES", help="Nome exato da camada de paredes")
    parser.add_argument("--unidade", required=True, choices=["mm", "m"], help="Unidade usada no desenho DXF")
    args = parser.parse_args()
    try:
        dados = args.entrada.read_bytes()
        if b"AutoCAD Binary DXF" in dados[:32]:
            raise ErroConversao("DXF binário não aceito. Exporte DXF ASCII.")
        texto = dados.decode("utf-8-sig", errors="replace")
        resultado = converter(texto, args.camada, args.unidade)
        args.saida.write_text(resultado, encoding="utf-8")
        count = sum(line.startswith("wall ") for line in resultado.splitlines())
        print(f"OK: {count} paredes candidatas. Arquivo: {args.saida}")
        print("Abra projeto de teste no WMK BIM Studio e use Gerenciar > Executar script > Testar.")
        return 0
    except (OSError, ErroConversao) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
