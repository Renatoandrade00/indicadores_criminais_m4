---
name: data-wrangling
description: Use para tarefas de limpeza de dados, engenharia de recursos (feature engineering), tratamento de valores nulos, duplicatas ou preparação de bases de dados em Python (Pandas/Polars) e SQL.
---

## Objetivo
Garantir que os dados brutos sejam limpos, tipados corretamente, otimizados e prontos para modelagem ou visualização de forma performática e sem vieses.

## Instruções de Abordagem
Ao receber uma requisição de tratamento de dados, execute ou proponha scripts seguindo estes padrões:

1. **Análise Exploratória Inicial (EDA):** Verifique tipos de dados, contagem de nulos, valores únicos e estatísticas descritivas básicas.
2. **Sanitização de Dados:**
   - Padronize nomes de colunas usando `snake_case` e remova caracteres especiais ou acentos.
   - Trate valores nulos de forma explícita (removendo ou imputando por mediana/moda, justificando a decisão).
   - Identifique e remova linhas duplicadas.
3. **Conversão de Tipos:** Garanta que datas estejam em formato datetime (`YYYY-MM-DD`), IDs como strings, e métricas financeiras como floats.
4. **Otimização:** No Pandas, utilize tipos categóricos para colunas de baixa cardinalidade para economizar memória. No SQL, evite `SELECT *` e use CTEs (*Common Table Expressions*) legíveis.

## Exemplo de Código Esperado (Pandas)
```python
import pandas as pd

def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Padronizar colunas
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # 2. Tipar dados
    df['data_venda'] = pd.to_datetime(df['data_venda'])
    df['id_cliente'] = df['id_cliente'].astype(str)
    
    # 3. Tratar nulos no faturamento substituindo pela mediana
    mediana_faturamento = df['faturamento'].median()
    df['faturamento'] = df['faturamento'].fillna(mediana_faturamento)
    
    return df
```

## Restrições
- NUNCA apague linhas com dados faltantes sem alertar o usuário sobre o impacto estatístico da perda de dados.
- Não utilize loops for no Pandas quando operações vetorizadas estiverem disponíveis.
