---
name: dax-modeling
description: Garante a modelagem correta em Star Schema e apoia a construção de códigos DAX limpos, complexos e performáticos.
---

## Objetivo
Garantir que a modelagem de dados no Power BI (ou soluções tabulares) siga o formato Star Schema (Fatos e Dimensões separadas) e que os códigos DAX criados sejam performáticos, legíveis e organizados.

## Instruções de Abordagem
Sempre que for feita uma pergunta sobre modelagem relacional, relacionamentos de tabelas ou como criar uma medida DAX complexa:

1. **Modelagem de Dados:**
   - Guie sempre o desenvolvimento para a modelagem no formato **Star Schema**, garantindo a clara separação entre tabelas Fato e Dimensão.
   - Obrigue o uso de uma tabela calendário dedicada (`dCalendario` ou equivalente).
2. **Escrita de DAX:**
   - Assegure que os códigos DAX sejam performáticos.
   - Utilize sempre variáveis (`VAR` e `RETURN`) para facilitar a leitura, o debugging e otimizar o tempo de processamento.
   - Forneça explicações sobre como o contexto de avaliação afeta as fórmulas como `CALCULATE` e sugira as melhores funções de filtro (`FILTER`, `KEEPFILTERS`, etc).
