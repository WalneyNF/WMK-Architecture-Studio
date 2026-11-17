# Pesquisa de necessidades de arquitetos e escritórios — Suíte WMK

**Data:** 16/11/2026 · **Escopo:** CAD 2D, BIM, interoperabilidade e uso assistido de IA.  
**Autoria da pesquisa e integração:** Walney Moreira Klein — walneyk@hotmail.com.

> **Método:** revisão documental de estudos e instituições profissionais (AIA, RIBA/NBS, CAU/BR, FAU-USP, buildingSMART, artigos científicos), mais leitura dos README e do código dos forks. **Não realizamos entrevistas, testes de campo nem pesquisa própria com arquitetos.** As propostas abaixo são **hipóteses de produto**, não requisitos validados por usuários locais. Os dados internacionais não devem ser tratados como estatísticas sobre o Brasil.

## 1. Resumo executivo — o que o profissional precisa

O arquiteto acompanha um ciclo: levantamento e programa de necessidades → estudo preliminar → anteprojeto → documentação para licenciamento → projeto executivo → coordenação de disciplinas → revisões. Não há uma única planta baixa que resolva sozinha todas essas fases.

**Problemas de maior impacto:**
1. **Tempo e retrabalho:** redesenhar uma planta ou repetir informações em 2D, 3D, planilhas e pranchas.
2. **Precisão e documentação:** cotas, unidades, layers, espessuras, hachuras, blocos, folhas, escalas, impressão e histórico.
3. **Coordenação:** importar desenhos de terceiros, identificar diferenças, sincronizar revisões e evitar perda silenciosa de dados.
4. **Curva de aprendizado:** aprender CAD e BIM sem semanas de treinamento para ações simples; manuais pt-BR e assistentes contextuais.
5. **Interoperabilidade:** trocar DXF/DWG e IFC sem transformar objetos inteligentes em linhas inutilizáveis ou perder informações.
6. **Adoção acessível:** custo, hardware limitado, instalação local, confiabilidade e compatibilidade.
7. **IA verificável:** ler textos/cotas, sugerir elementos e automatizar tarefas, mas permitir revisão humana e rastreabilidade.

### Evidências externas verificadas

- **CAU/BR (2025)** relata que **99%** dos profissionais participantes da 2ª Pesquisa sobre Digitalização na Indústria da Construção apontaram necessidade de capacitação para acompanhar mudanças tecnológicas. É pesquisa com público específico; não extrapolar a todos os arquitetos brasileiros. [Fonte](https://caubr.gov.br/pesquisa-bim-para-65-dos-profissionais-entidades-sao-referencia-em-inovacao/).
- **Dissertação FAU-USP (2024)** investiga adoção BIM em micro e pequenas empresas de arquitetura, relevante ao recorte de escritórios menores. [Fonte](https://teses.usp.br/teses/disponiveis/16/16132/tde-14012025-131658/pt-br.html).
- **NBS Digital Construction Report 2025**, repercutido pelo RIBA Journal: 74% dos profissionais de arquitetura participantes relatam uso de BIM; a pesquisa destaca que BIM ultrapassa visualização 3D e envolve processos e padronização. **Não é taxa do Brasil.** [Fonte](https://www.ribaj.com/intelligence/artificial-intelligence-ai-technology-uptake-digital-construction-report-2025).
- **AIA Firm Survey 2026:** amostra de quase 900 escritórios dos EUA; 74% informam uso de IA em operações do dia a dia. **Não significa que 74% já criem modelos BIM automaticamente com IA.** [Fonte](https://www.aia.org/about-aia/press/new-aia-firm-survey-report-reveals-trends-shaping-business-architecture).
- **AIA, estudo sobre especificações (2024):** aponta ineficiência em atualização de bibliotecas de produtos, estimativas e elaboração de especificações; oportunidade para automação focada em trabalho operacional. [Fonte](https://www.aia.org/sites/default/files/2025-01/2024-AIA-architects-journey-to-specification.pdf).
- **Interoperabilidade BIM (Buildings, 2025):** transferências de modelos entre especialidades podem perder dados ou exigir correções manuais. [Fonte](https://www.mdpi.com/2075-5309/15/24/4540).
- **buildingSMART:** padrões abertos **IFC** (modelo), **BCF** (issues/coordenação), **IDS** (requisitos verificáveis) e **bSDD** (terminologia). IFC é ISO 16739; não equivale a garantia de conversão perfeita. [Fonte](https://www.buildingsmart.org/about/OpenBIM/) e [IFC](https://www.buildingsmart.org/standards/bsi-standards/industry-foundation--classes/).
- **ABDI / Plataforma BIMBR:** disponibiliza guias nacionais sobre processo de projeto BIM, classificação, orçamento, contratação e implantação. [Fonte](https://plataformabimbr.abdi.com.br/guias-normas).
- **BIM Fórum Brasil, pesquisa 2025:** levantamento de maturidade digital de incorporadoras/construtoras; útil como contexto de mercado, mas não representa diretamente escritórios de arquitetura. [Fonte](https://bimforum.org.br/publicacoes-bfb/).

## 2. WMK CAD Studio — desenho técnico e plantas

**Repositório:** https://github.com/WalneyNF/WMK-CAD-Studio  
**Base:** CADCraft (Rust/egui). O README documenta linha de comando, geometria 2D, camadas, cotas, hachuras, blocos, arquivos DXF/DWG, layouts, CLI/MCP e interface pt-BR. **Maturidade:** pré-alfa segundo o roadmap; não homologado para entregas profissionais.

| Necessidade real | Já existe como base | O que avaliar/implementar |
|---|---|---|
| Traçado preciso | LINE, PLINE, SNAP, ORTHO, coordenadas | Testar precisão real, snapping e UX em desenhos de escritório |
| Paredes e espessuras no desenho | LINE, OFFSET, TRIM, layers | Camadas/tipos de parede por template, espessura e padrões de anotação |
| Cotas e unidades | DIM*, estilos, restrições | Conferência de unidade no importar/salvar; validação de escala de impressão |
| Plantas completas | Blocos, textos, hachuras, tabelas | Biblioteca editável pt-BR de símbolos arquitetônicos e templates |
| Compatibilidade | DXF/DWG | Teste de round-trip, relatório de entidades não suportadas, sem perda silenciosa |
| Pranchas | Layouts, viewports, PDF | A4/A3/A2/A1, carimbos, escalas e perfis de impressão |
| Revisões | Comandos e undo | Comparar versões, destacar geometria alterada, histórico de alterações |
| Acesso fácil | Interface, comandos, tradução pt-BR | Primeiro contato assistido, dicas por ferramenta, atalhos, tutoriais offline |

**Não fazer aqui:** reconstruir todo o BIM e seus objetos semânticos.

### Casos de uso prioritários no CAD
1. Abrir `examples/apartment.dxf`, medir área/quarto, alterar posição de porta, salvar DXF e reabrir.
2. Criar uma planta 2D simples em milímetros com `WMK_PAREDES`, `WMK_PORTAS`, `WMK_JANELAS`, `WMK_COTAS`.
3. Imprimir prancha A3 com escala verificável e exportar PDF legível.

## 3. WMK BIM Studio — modelo de construção

**Repositório:** https://github.com/WalneyNF/WMK-BIM-STUDIO  
**Base:** BIMCraft (Rust/egui). O código contém comandos `wall`, `door`, `window`, `floor`, `roof`, `room`, `sheet`, vistas/cortes, e testes/demonstração; importação raster nativa permanece parcial. **Nem todo recurso anunciado está validado para uso profissional.**

| Necessidade real | Base existente | Lacuna e prioridade |
|---|---|---|
| Paredes, portas e janelas inteligentes | Comandos semânticos de elementos | Confiabilidade de associações, espessuras, famílias e edição visual |
| Modelagem e visualização | Modelo 3D, vistas | Navegação fluida, vistas salvas, seleção consistente e desempenho |
| Pisos, coberturas, ambientes | Comandos e modelos próprios | Conferir união das geometrias, áreas, cotas e mudanças sincronizadas |
| Cortes, fachadas, folhas | Recursos de vistas e pranchas | Padrão documental, exportação e testes de consistência das vistas |
| Colaboração | IFC, comandos, MCP | Importar/exportar IFC com relatório do que foi perdido |
| Quantidades | Informações semânticas do modelo | Quantitativos auditáveis e transparência das regras de cálculo |
| Projeto executivo | Recursos de documentação | Revisão por profissional habilitado, normas e dados de especialidades |
| Facilidade | Interface pt-BR parcial | Assistente por etapa, projetos de exemplo, tutorial guiado |

**Não fazer aqui:** refazer uma plataforma completa de CAD 2D com os mesmos comandos do CADCraft.

### Casos de uso prioritários no BIM
1. Abrir o projeto demonstrativo e validar portas/janelas, vistas, cotas, ambientes, cortes e folhas.
2. Criar casa simples de 4 × 3 m a partir de comandos, inspecionar em 3D e salvar/reabrir.
3. Alterar espessura/posição de parede e conferir impacto em portas, vistas e quantitativos.
4. Exportar/importar IFC de teste e produzir relatório de divergências.

## 4. WMK Architecture Studio — por que existe

**Repositório:** https://github.com/WalneyNF/WMK-Architecture-Studio

Não é um terceiro CAD ou um terceiro BIM. É a **camada de integração e orquestração** que conduz o mesmo desenho entre as duas representações sem pedir ao usuário que reconstrua tudo.

### Diferença técnica fundamental
- No **CAD**, entidades são LINE, LWPOLYLINE, ARC, BLOCK etc., geralmente com coordenadas e camadas.
- No **BIM**, entidades têm **significado**, por exemplo parede, porta, janela, pavimento e propriedades.
- Uma linha não vira parede apenas por existir: precisamos identificar **classe**, **eixo/contorno**, **unidade**, **espessura**, **altura**, **aberturas** e relações.
- A conversão de volta para o CAD deve preservar o vínculo entre os IDs e declarar o que for perdido; não é uma transformação automaticamente reversível.

### Mapa de dados de integração proposto
```text
       WMK CAD Studio                WMK BIM Studio
  desenho DXF/DWG vetorial       objetos de construção
             |                          ^
             v                          |
       [Importador CAD]       [Adaptador de comandos BIM]
             |                          ^
             v                          |
      [Modelo intermediário versionado: unidade, geometria,
       semântica, IDs de origem, warnings, evidências, revisões]
             ^                          |
             |                          |
   OCR/visão para PNG/JPG/PDF     Regras e revisão humana

  WMK Architecture Studio: orquestra esse fluxo e registra resultados.
```

### O que o Architecture Studio **precisa entregar**
| Necessidade | Função da integração | Aceite proposto |
|---|---|---|
| Não redesenhar a mesma parede | DXF → paredes BIM | 4 paredes do DXF de teste viram 4 paredes BIM com coordenadas aferidas |
| Evitar escala errada | Unidades explícitas, cotas de controle | Erro se unidade desconhecida; não inventar metros |
| Não perder informação | Relatório por entidade | Contar importadas/ignoradas/alteradas e explicar o motivo |
| Revisar com segurança | Prévia e confirmação | Nunca alterar projeto sem mostrar impacto e opção de desfazer |
| Receber revisão de terceiros | Diff CAD/BIM | Mostrar paredes adicionadas/removidas/movidas |
| Integrar arquivos da equipe | DXF/DWG/IFC e metadados | Testes com vários arquivos e formatos, registrar incompatibilidades |
| Aproveitar planta antiga | OCR + detecção especializada | Paredes/cotas reconhecidas com confiança e revisão; falha explícita |
| Trabalhar em equipe | Histórico, questões, BCF (futuro) | ID do problema, responsável, estado e referência ao elemento |
| IA para não especialistas | Assistente orientado por intenção | Gerar comandos com validação e pedir dados faltantes, sem adivinhações |
| Evitar bloqueio por fornecedor | Interoperabilidade e formatos abertos | Round-trip aferido; preservar originais e exportações |

### Por que **não** juntar os dois motores agora
- Existem editores, histórico de undo, renderização, entidades e dependências diferentes.
- Mesclar fontes de dois programas dificulta atualizar os forks originais e depurar falhas.
- Um contrato intermediário testável fornece interoperabilidade **antes** de escolher interface única.
- A interface unificada pode chegar depois; a integração começa por importação/exportação, API e processos locais.

**Estado real em novembro de 2026:** um conversor experimental `bridge/dxf_para_bim.py` lê apenas entidades `LINE` em `WMK_PAREDES`, DXF ASCII, e gera comandos `wall`. Não processa DWG, polilinhas complexas, IA, portas ou janelas. Não há sincronização bidirecional.

## 5. Priorização de produto (hipótese inicial para validar com arquitetos)

| Prioridade | Entrega | Motor responsável | Métrica de teste |
|---|---|---|---|
| P0 | Abrir, editar, salvar/reabrir planta DXF sem perda | CAD | Arquivos de prova com entidades preservadas |
| P0 | Converter 4 segmentos de teste em 4 paredes reais | Architecture + BIM | Contagem, coordenadas, validação do modelo |
| P0 | Validar unidade e escala | Architecture | Rejeitar unidade ambígua/erro acima de tolerância |
| P0 | Não perder dados silenciosamente | Architecture | Relatório obrigatório de importação |
| P1 | Porta/janela e associação à parede | Architecture + BIM | Elementos e relações verificados em 3D |
| P1 | Pranchas, PDF e cotas profissionais | CAD + BIM | Testes de tamanho, escala e consistência |
| P1 | Assistente inicial e documentação pt-BR offline | Todos | Usuário leigo conclui cenário guiado |
| P1 | Round-trip IFC com testes de fidelidade | BIM + Architecture | Comparação de geometria, propriedades e IDs |
| P2 | OCR das cotas e textos em planta raster | Architecture + OCR existente | Precisão por campo com amostra rotulada |
| P2 | Detecção de paredes em plantas técnicas e humanizadas | Architecture + visão | Precision/recall por conjunto de plantas |
| P2 | Gestão de revisões, BCF e coordenação | Architecture | Issues vinculados a elementos e versões |
| P3 | Interface única / EXE unificado | Architecture | Não duplicar motores; testes de estabilidade |

## 6. Perguntas para entrevistas com profissionais (não respondidas ainda)

1. Você trabalha mais com casas, reformas, interiores, edifícios ou urbanismo?
2. Quais formatos recebe dos clientes e parceiros: JPG, PDF, DWG, DXF, IFC, RVT?
3. Em que atividades mais perde tempo: desenho, revisão, quantificação, pranchas, especificações, entrega?
4. O que precisa permanecer editável quando converte de CAD para BIM?
5. Em quais casos uma importação imperfeita causaria maior prejuízo?
6. Prefere dois programas conectados ou uma interface única? Por quê?
7. Quais regras de escritório, templates, padrões e normas usa?
8. Seu PC e sua conexão permitem modelos pesados ou precisa trabalhar offline?
9. Como valida precisão de medidas e coordena projeto estrutural/hidráulico/elétrico?
10. Aceitaria IA que apenas sugere elementos, mostrando incertezas e exigindo aprovação?

**Próxima pesquisa:** entrevistas com 5–10 profissionais em diferentes portes de escritório, coleta de arquivos de teste com permissão, análise de casos de uso, comparação entre soluções concorrentes. Não marcar hipóteses como necessidades confirmadas antes desse estudo.

## 7. Regras de segurança, normas e responsabilidade

- Ferramenta de software **não substitui responsabilidade técnica de profissional habilitado**, verificação de normas, legislação municipal, acessibilidade, segurança ou aprovação legal.
- Não anunciar geração automática de projeto executivo confiável a partir de fotografia/planta JPG.
- Não interpretar uma cota OCR como precisa sem conferir escala, coerência e evidência.
- Nunca remover entidades não suportadas em exportação sem emitir relatório; guardar arquivo original.
- Padrões e referências normativas devem ser revisados por profissional habilitado e conforme versão aplicável.
- Respeitar licenças, marcas, direitos autorais e origem dos forks utilizados.

## Referências e transparência

Fontes principais listadas nas seções anteriores; complementares:

- buildingSMART — [openBIM](https://www.buildingsmart.org/about/OpenBIM/).
- AIA — [Firm Survey 2026](https://www.aia.org/resource-center/aia-firm-survey-report).
- USP — [Adoção do BIM em micro e pequenas empresas de arquitetura](https://teses.usp.br/teses/disponiveis/16/16132/tde-14012025-131658/pt-br.html).
- CAU/BR — [Pesquisa BIM e capacitação](https://caubr.gov.br/pesquisa-bim-para-65-dos-profissionais-entidades-sao-referencia-em-inovacao/).
- ABDI — [Guias nacionais BIM](https://plataformabimbr.abdi.com.br/guias-normas).
- [WMK CAD Studio](https://github.com/WalneyNF/WMK-CAD-Studio), [WMK BIM Studio](https://github.com/WalneyNF/WMK-BIM-STUDIO) e [WMK Architecture Studio](https://github.com/WalneyNF/WMK-Architecture-Studio).

---

*Pesquisa de requisitos exploratória; não é parecer técnico de arquitetura ou engenharia.*  
**Walney Moreira Klein — walneyk@hotmail.com**
