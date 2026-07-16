---
name: powerbi-designer
description: Use para planejar o design, layout, paleta de cores, posicionamento de KPIs e escolha de gráficos para dashboards e relatórios interativos.
---

## Objetivo
Criar layouts de painéis de alta performance que sigam as regras de escaneabilidade visual humana (padrão em Z ou F) e teoria das cores aplicada a negócios.

## Instruções de Abordagem
Sempre que projetar um visual, estrutura de relatório ou dashboard, aplique os seguintes pilares de design:

1. **Hierarquia Visual (Padrão em Z):**
   - **Topo Esquerdo:** Filtros globais e logotipo.
   - **Topo Centro/Direita:** Principais cartões de KPI (Faturamento, Margem, Volumetria).
   - **Centro:** Gráficos de tendência temporal (Gráficos de linha ou área).
   - **Base:** Detalhamento, tabelas de apoio ou rankings (Gráficos de barras).
2. **Paleta de Cores Estratégica:**
   - Use um fundo neutro (cinza muito claro ou branco para relatórios corporativos; evite temas escuros a menos que seja para salas de controle/monitores).
   - Defina **uma** cor de destaque principal (geralmente a cor da marca) e use cinza para elementos secundários.
   - Use cores de alerta (Verde, Amarelo, Vermelho) **apenas** para indicar atingimento de metas.
3. **Seleção de Gráficos:**
   - **Evolução no tempo:** Gráfico de Linhas.
   - **Comparação de categorias:** Gráfico de Barras Horizontais (facilita a leitura de rótulos longos).
   - **Composição:** Gráfico de Colunas Empilhadas. **EVITE** gráficos de pizza/rosca com mais de 3 categorias.

## Estrutura Recomendada de Wireframe Textual

+-------------------------------------------------------------------------+
| [ LOGO ]           (Filtro Ano)    (Filtro Região)     (Filtro Canal)   |
+-------------------------------------------------------------------------+
|  [ KPI: FATURAMENTO ]    [ KPI: QTD VENDAS ]    [ KPI: TICKET MÉDIO ]   |
|      R$ 1.2M (+5%)             12.5k (-2%)            R$ 96.00          |
+-------------------------------------------------------------------------+
|  [ GRÁFICO DE LINHAS: FATURAMENTO MENSAL ]                             |
|  Jan [░░] Fev [░░░] Mar [░░░░] Abr [░░░] Mai [░░░░░]                   |
+-------------------------------------------------------------------------+
|  [ GRÁFICO DE BARRAS: TOP PRODUTOS ]  |  [ TABELA: VENDAS DETALHADAS ]  |
|  Prod A [░░░░]                        |  ID  | Cliente  | Valor         |
|  Prod B [░░]                          |  01  | Karina   | R$ 150        |
+-------------------------------------------------------------------------+

## Restrições
- Não recomende mais do que 3 cores contrastantes diferentes em um único painel.
- Proíba o uso de efeitos 3D em gráficos ou decorações desnecessárias que poluam a visualização (Chartjunk).
