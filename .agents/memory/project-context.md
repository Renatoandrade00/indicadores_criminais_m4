---
type: project
created: 2026-10-07
updated: 2026-10-07
---

# Contexto do Projeto - Indicadores Criminais CPA/M-4

## 1. Visão Geral
Dashboard analítico em Streamlit para visualização, acompanhamento e apresentação executiva dos indicadores criminais da área do Comando de Policiamento de Área Metropolitana Quatro (CPA/M-4), cobrindo os batalhões 2º BPM/M, 29º BPM/M, 39º BPM/M e 48º BPM/M (e respectivas Companhias e DPs).

## 2. Arquitetura e Fluxo de Dados
1. **Fonte dos Dados**: Google Drive da SSP-SP contendo planilhas Excel mensais (`DADOS CRIMINAIS_...xlsx` e `DADOS PRODUTIVIDADE_...xlsx`).
2. **Sincronização (`sync_ssp.py`)**: Script executado via GitHub Actions (`.github/workflows/sync-ssp.yml`) ou manualmente. Conecta via Google Drive API v3 e `gdown`, controlando downloads por `data/sync_manifest.json`.
3. **ETL (`etl.py`)**: Extrai, padroniza nomes de indicadores e delegacias, filtra as 12 DPs da área do CPA/M-4, mapeia para Batalhão e Companhia Militar (`MAP_MILITAR`), derrete as colunas de anos e consolida tudo em `data/dados_tratados.csv`.
4. **Aplicação Web (`app.py` + `data_loader.py`)**:
   - `load_data()`: Carrega `data/dados_tratados.csv` com cache inteligente invalidado pelo `mtime` do arquivo.
   - `DashboardData`: Regras de negócio, mapeamento de meses, filtros de período e acumulado.
   - `FilterUI`: Barra lateral com Batalhão, Cias, Indicadores, Período de Análise e Modo de Comparação.
   - `DashboardRenderer`: Cards de KPIs, Tabelas comparativas (Acumulado e Mês Específico), Gráficos de barras horizontais, Diagnóstico automatizado, Gráfico de pizza (participação por batalhão) e Modo Apresentação (slideshow com iframe Google Slides).

## 3. Indicadores Monitorados
- FURTO OUTROS
- FURTO VEÍCULO
- HOMICÍDIO DOLOSO
- ROUBO DE CARGA
- ROUBO OUTROS
- ROUBO VEÍCULO

## 4. Batalhões e Companhias Mapeadas
- **2º BPM/M**: 1ª Cia (Ponte Rasa / 024 DP), 2ª Cia (Vila Jacuí / 063 DP), 3ª Cia (Ermelino Matarazzo / 062 DP)
- **29º BPM/M**: 1ª Cia (Itaim Paulista / 050 DP), 2ª Cia (São Miguel Paulista / 022 DP), 3ª Cia (Jardim Noemia / 059 DP)
- **39º BPM/M**: 1ª Cia (Itaquera / 032 DP), 2ª Cia (Artur Alvim / 065 DP), 3ª Cia (Cidade A E Carvalho / 064 DP)
- **48º BPM/M**: 1ª Cia (Jardim Robru / 067 DP), 2ª Cia (Lajeado / 068 DP), 3ª Cia (Cohab Itaquera / 103 DP)
