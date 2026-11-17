# WMK Architecture Studio

**Integração experimental CAD ↔ BIM para Windows, em português.**

**Autor da integração:** Walney Moreira Klein — walneyk@hotmail.com

Este repositório **não é um terceiro clone dos editores**. Ele integra, em etapas, dois projetos independentes:

- [WMK CAD Studio](https://github.com/WalneyNF/WMK-CAD-Studio): desenho técnico 2D, camadas, cotas, DXF/DWG.
- [WMK BIM Studio](https://github.com/WalneyNF/WMK-BIM-STUDIO): paredes, portas, janelas, pisos, telhados, modelos BIM e comandos `wall`.

## O que funciona neste primeiro experimento

O arquivo `bridge/dxf_para_bim.py` (a ser mantido neste repositório) recebe um **DXF ASCII de teste** contendo linhas na camada **WMK_PAREDES** e gera um script de paredes que poderá ser executado no WMK BIM Studio. O conversor utiliza **apenas a biblioteca padrão do Python**, sem servidor e sem API de IA.

**Não confundir com integração completa:** este primeiro experimento não transforma automaticamente uma imagem em BIM, não detecta portas/janelas, nem sincroniza alterações entre aplicativos. É um teste de intercâmbio de geometria, com validação humana.

### Experimento no Windows

1. No WMK CAD Studio, desenhe segmentos na camada `WMK_PAREDES` em unidades de **milímetros**; exporte em formato **DXF ASCII**.
2. Abra o PowerShell na pasta deste repositório.
3. Execute:
   ```powershell
   py -3 bridge\dxf_para_bim.py entrada.dxf saida.wmk.txt --unidade mm
   ```
4. No WMK BIM Studio, abra um projeto de teste, entre em **Gerenciar → Executar script**, cole as linhas do arquivo TXT, clique em **Testar** e depois em **Executar** se o resultado estiver correto.
5. Confira a posição das paredes na vista 2D e 3D.

Para testar sem desenhar nada, use o DXF de exemplo incluso:
```powershell
py -3 bridge\dxf_para_bim.py exemplos\quarto.dxf paredes.wmk.txt --unidade mm
py -3 -m unittest discover -s tests -v
```

### Segurança e limitações

- O conversor só importa entidades `LINE` na camada `WMK_PAREDES`; outros elementos são ignorados.
- A unidade deve ser informada explicitamente (mm/m). O DXF pode ser exportado em outras unidades; confira.
- Paredes recebem tipo inicial `Interior - 100mm`, que é uma hipótese para ensaio, **não um dimensionamento profissional**.
- O script é gerado localmente, sem modificar o projeto automaticamente.
- Nunca execute scripts importados em um projeto importante sem conferir a origem e usar o botão **Testar**.

## Arquitetura proposta

```text
[WMK CAD Studio] --DXF--> [Bridge: validação + conversão] --script--> [WMK BIM Studio]
                                       ^
                          [OCR / IA, em fase posterior]
```

**Princípio:** manter os motores CAD e BIM em seus repositórios. O Architecture Studio controla formatos intermediários, testes, documentação, troca de dados e, só após validação, uma interface unificada.

## Próximas entregas

Veja [ROADMAP.md](ROADMAP.md). Prioridade: testar a conversão real de DXF em paredes do WMK BIM Studio antes de adicionar OCR/IA.

## Créditos e licenças

Integração original: **Walney Moreira Klein — walneyk@hotmail.com**. CADCraft e BIMCraft mantêm seus autores e licenças originais. Nenhum código do motor de terceiros é copiado neste projeto nesta fase.