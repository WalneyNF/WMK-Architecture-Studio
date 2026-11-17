# Roadmap — WMK Architecture Studio

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
