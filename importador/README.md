# WMK Architecture Studio — Importador de plantas v0.2 (experimental)

**Walney Moreira Klein — walneyk@hotmail.com**

Transforma plantas **JPG, PNG e primeira página PDF** em sugestões de segmentos 2D exportáveis como linhas CAD em DXF. É uma ferramenta acessível para estudos, **não interpreta a construção como um projeto arquitetônico pronto** nem gera BIM nesta versão. As três amostras de teste foram fornecidas para uso no protótipo.

![Logo WMK Architecture Studio](assets/logo-wmk-architecture.png)

## Como iniciar no Windows

1. Extraia o ZIP.
2. Dê dois cliques em `iniciar-windows.bat` (Python 3.11+ necessário). Ele prepara um ambiente virtual local e instala as dependências.
3. Clique em **Abrir JPG / PNG / PDF**, selecione uma planta.
4. Clique em **1. Reconhecer linhas**. O método `auto` escolhe entre paredes laranja saturadas e linhas escuras.
5. **Revise o resultado:** verde = selecionado; clique para descartar (vermelho); clique novamente para recuperar.
6. Use **Adicionar linha** e clique em dois pontos quando faltar um segmento.
7. Quando souber uma medida real, clique em **2. Calibrar escala**, marque os dois extremos e informe a distância em **metros**.
8. Clique em **3. Salvar DXF revisado**. Serão gerados `.dxf` (linhas editáveis), `.json` (origem e decisões) e `_previa.png`.
9. No **WMK CAD Studio**, abra o `.dxf` e confirme as linhas. A imagem JPG/PNG **não é embutida no CAD** por este exportador; a anexação de raster dentro do aplicativo CAD permanece pendente.

## Próximo passo opcional: testar no BIM Studio

Depois de **calibrar a escala** e conferir o DXF no WMK CAD Studio, você pode converter as linhas selecionadas em um script de paredes de teste usando a ponte deste repositório:

```powershell
py -3 ..\bridge\dxf_para_bim.py "projetos_gerados\planta\planta.dxf" "paredes.wmk.txt" --camada WMK_PAREDES_REVISADAS --unidade mm
```

A ponte bloqueia DXF sem unidade calibrada; confirme o script com a ferramenta **Testar** do WMK BIM Studio. A largura e altura das paredes ainda são hipóteses de modelagem.

## Como ler as três amostras

- **Planta 01:** paredes laranja; o filtro dá preferência a laranja **saturado e claro**, para evitar mesas de madeira.
- **Planta 02:** planta humanizada complexa; muitas linhas de móveis, árvores e texturas podem ser detectadas incorretamente. Revisão é essencial.
- **Planta 03:** plantas com paredes escuras e cotas; a detecção de retas pode encontrar cotas e contornos, não apenas paredes.

## Limitações importantes

- **Não identifica** com segurança paredes semânticas, portas, janelas ou a altura da edificação.
- **Não calcula escala automaticamente a partir de OCR**. Calibragem manual usa dois pontos conhecidos e uma distância real. Sem isso, o DXF fica com unidade **indefinida**.
- OCR do Tesseract é **opcional** e usado apenas para reduzir textos confundidos com linhas; se indisponível, continua sem OCR.
- PDF é rasterizado **somente na primeira página**. Ainda não há extração vetorial direta do PDF.
- **Clique para excluir** pode selecionar um segmento próximo; aproxime a janela ou confira a imagem de prévia.
- As sugestões em pixels devem ser conferidas antes de projetos de engenharia ou arquitetura. Nada é automaticamente validado como BIM.

## Arquitetura e integração

```text
PNG/JPG/PDF → OpenCV (segmentos candidatos)
                        ↓
              Revisão visual e escala
                        ↓
                DXF + JSON + PNG
                        ↓
         WMK CAD Studio (edição CAD)
                        ↓ futuro
   WMK Architecture Bridge → WMK BIM Studio
```

- [WMK CAD Studio](https://github.com/WalneyNF/WMK-CAD-Studio): editor CAD 2D; abre DXF.
- [WMK Architecture Studio](https://github.com/WalneyNF/WMK-Architecture-Studio): importador e integração.
- [WMK BIM Studio](https://github.com/WalneyNF/WMK-BIM-STUDIO): motor BIM 3D.

## Testes

```powershell
py -3 -m pip install -r requirements.txt
py -3 -m unittest discover -s tests -v
py -3 wmk_detector_planta.py amostras\planta-01-piscina.png --saida testes-piscina
```

Consulte o arquivo `LEIA-ME.txt` para um resumo simples.

**Autoria WMK:** Walney Moreira Klein — walneyk@hotmail.com. Preserve os avisos de licença dos motores CADCraft e BIMCraft ao redistribuir partes de código derivado.
