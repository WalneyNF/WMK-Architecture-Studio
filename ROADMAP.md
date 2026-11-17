# Roadmap — WMK Architecture Studio

## Status do importador experimental — v0.2

- [x] Importar JPG/PNG e rasterizar **primeira página** PDF via PDFium.
- [x] Reconhecer segmentos candidatos por saturação de cor/limiares e Hough; selecionar modo automático, laranja ou escuro.
- [x] Revisão visual: ativar/desativar segmentos e adicionar manualmente linhas que faltaram.
- [x] Calibrar escala em milímetros por pixel usando dois pontos e medida conhecida, com conferência humana.
- [x] Exportar DXF editável, JSON de auditoria e prévia PNG preservando o original.
- [x] Disponibilizar código e logo WMK na pasta [importador/](importador/).
- [x] Adicionar testes automatizados do detector: 6 cenários locais aprovados em 17/11/2026.
- [ ] Confirmar compilação Windows e funcionamento do EXE na máquina do usuário; [GitHub Actions](../../actions).
- [ ] Integrar anexação de raster **dentro da área de desenho do WMK CAD Studio**. No momento o importador é um aplicativo auxiliar.
- [ ] Calcular cotas automaticamente com OCR de forma confiável, com limites de confiança.
- [ ] Criar entidades de parede BIM com posição e escala verificadas, incluindo portas/janelas.

## Base da priorização

[Pesquisa de necessidades de arquitetos (16/11/2026)](pesquisa/necessidades-arquitetos-2026.md) reúne evidências, limitações, requisitos por ferramenta, casos de uso e critérios de aceite. **A pesquisa não representa entrevistas com arquitetos e não comprova maturidade profissional dos forks.**

### Entregas orientadas a necessidades reais

**P0 — provar que a integração tem valor**
- [ ] Validar que o WMK CAD Studio abre, altera, salva e reabre um DXF de planta **sem perder as entidades utilizadas**.
- [ ] Validar no WMK BIM Studio a criação de quatro paredes a partir do DXF de exemplo.
- [ ] Exibir **relatório de importação**: entidades recebidas, convertidas, ignoradas e erros.
- [ ] Testar unidade de desenho e impedir importação com escala/unidade indefinida.

**P1 — dar suporte ao projeto arquitetônico básico**
- [ ] Converter polilinhas CAD em eixos/contornos de paredes com conferência do usuário.
- [ ] Criar portas, janelas e pisos/ambientes associados às paredes.
- [ ] Fazer casos de teste de cotas, áreas e documentação em PDF.
- [ ] Adicionar tutorial guiado em português, com modos iniciante e avançado.
- [ ] Implantar testes de ida e volta de DXF/IFC com relatório de perda de dados.

**P2 — reduzir retrabalho e coordenar revisões**
- [ ] Comparar duas versões da planta e sinalizar alterações de geometria e medidas.
- [ ] Introduzir IDs de origem estáveis e correspondência CAD ↔ BIM.
- [ ] Examinar suporte a BCF e IDS conforme buildingSMART.
- [ ] Pesquisar bibliotecas de símbolos/objetos BIM, especificações e quantitativos.

**P3 — reconhecer plantas raster com IA**
- [ ] Pipeline OCR para cotas e nomes de cômodos com confiança/posição.
- [ ] Reconhecedor de paredes treinado para plantas técnicas e humanizadas.
- [ ] Prévia editável e relatório das dimensões inferidas/não conhecidas.
- [ ] Testes com amostras autorizadas e medidas de precisão/recall.

**Validação de mercado (ainda pendente)**
- [ ] Entrevistar 5–10 arquitetos, incluindo autônomos e pequenos escritórios.
- [ ] Obter, com permissão, projetos reais DXF/DWG/IFC e plantas escaneadas.
- [ ] Validar requisitos brasileiros, práticas de entrega e padrões de pranchas com profissional habilitado.

## Marco 0 — Fundação do integrador
- [x] Criar repositório independente, sem copiar os dois motores.
- [x] Documentar a finalidade dos forks CAD e BIM.
- [x] Criar primeira ponte: DXF ASCII `LINE` na camada `WMK_PAREDES` → script `wall` do BIMCraft.
- [x] Adicionar exemplo de quarto de 4 m × 3 m e testes automatizados.
- [ ] Rodar testes no GitHub Actions e confirmar execução no Windows.
- [ ] Confirmar no aplicativo WMK BIM Studio que as quatro paredes do exemplo são criadas sem erros.

## Marco 1 — Intercâmbio confiável CAD → BIM
- [ ] Exportação assistida do WMK CAD Studio em camada específica.
- [ ] Preservar dados de unidades e converter a escala de forma verificável.
- [ ] Suportar `LWPOLYLINE`, polilinhas conectadas, fechamento de perímetro.
- [ ] Detectar linhas duplicadas, sobreposições e segmentos quase desconectados.
- [ ] Gerar prévia 2D e relatório de validação com alerta de linhas falsas.
- [ ] Comando de integração real que não exija copiar/colar em um script.
- [ ] Documentar contratos de transformação, IDs estáveis e idempotência.

## Marco 2 — Recursos de construção
- [ ] Converter camadas de portas e janelas em objetos BIM com associação a paredes.
- [ ] Gerar ambientes/pisos e permitir definição de altura e espessura.
- [ ] Importar/exportar IFC com testes de fidelidade e informações perdidas.
- [ ] Salvar um projeto integrado e recarregá-lo sem perda de dados.

## Marco 3 — Imagem → interpretação
- [ ] Importar JPG/PNG/PDF como referência no aplicativo principal.
- [ ] Integrar OCR existente apenas para textos e cotas, com indicação de confiança.
- [ ] Integrar detecção de paredes com modelos específicos para plantas arquitetônicas.
- [ ] Apresentar conferência das medidas antes da conversão para BIM.
- [ ] Trabalhar com imagens humanizadas e plantas técnicas, sem inventar dimensões.
- [ ] Testar precisão em conjunto variado de plantas com anotações verificadas.

## Marco 4 — Produto integrado
- [ ] Escolher API/IPC ou bibliotecas Rust compartilhadas com base em benchmarks.
- [ ] Projeto unificado com visão CAD, visão BIM e histórico coerente de alterações.
- [ ] Interface pt-BR com tutoriais, atalhos, logs, modo leigo e modo avançado.
- [ ] Compilar EXE Windows portátil via Actions e fornecer release testado.
- [ ] Revisar licenças, créditos e compatibilidade de dependências.

**Critério de avanço:** um marco só é concluído com testes reproduzíveis. O integrador não é um software de projeto executivo de engenharia ou arquitetura certificado.

**Créditos:** Walney Moreira Klein — walneyk@hotmail.com
