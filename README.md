# 🚓 Painel de Indicadores Criminais - CPA/M-4

🔗 **Acesse o painel ao vivo aqui:** [Indicadores Criminais CPA/M-4](https://indicadores-criminais-m4.onrender.com/#painel-de-indicadores-criminais-cpa-m-4)

Este projeto é um painel interativo (dashboard) desenvolvido em **Python** e **Streamlit**, focado na extração, tratamento e visualização de dados de segurança pública das delegacias subordinadas ao Comando de Policiamento de Área Metropolitana 4 (CPA/M-4), no estado de São Paulo.

## 🎯 Objetivo
Automatizar a análise de produtividade e criminalidade da região. O sistema processa dezenas de planilhas locais para apresentar de forma unificada os principais indicadores (Furtos, Roubos, Homicídios) e comparar estatísticas entre diferentes meses e anos, simulando uma experiência de alto nível de Business Intelligence (BI) no formato de um aplicativo web moderno.

## 🏢 Delegacias Abrangidas (CPA/M-4)
O pipeline de dados cruza e recorta especificamente o escopo das seguintes unidades:
- 022 DP - São Miguel Paulista
- 024 DP - Ponte Rasa
- 032 DP - Itaquera
- 050 DP - Itaim Paulista
- 059 DP - Jardim Noemia
- 062 DP - Ermelino Matarazzo
- 063 DP - Vila Jacuí
- 064 DP - Cidade A. E. Carvalho
- 065 DP - Artur Alvim
- 067 DP - Jardim Robru
- 068 DP - Lajeado
- 103 DP - Cohab Itaquera

## 📊 Indicadores Mapeados
O sistema trata de erros de texto, consolida nomes divergentes e captura os seguintes indicadores para fins estatísticos:
- FURTO OUTROS
- FURTO VEÍCULO
- ROUBO OUTROS
- ROUBO VEÍCULO
- ROUBO DE CARGA
- HOMICÍDIO DOLOSO

## 🚀 Como Funciona o Pipeline (ETL)

O projeto possui um fluxo inteligente de dados:
1. **Extração:** Planilhas brutas baixadas da Secretaria de Segurança Pública são alocadas na pasta `/data/raw_drive`.
2. **Transformação (`etl.py`):** O script interroga dezenas de tabelas, filtra as linhas relativas às delegacias e naturezas alvo, faz a transposição (melt) dos anos e descarta informações desnecessárias.
3. **Carregamento (`data_loader.py`):** Utilizando `@st.cache_data`, o painel lê de um arquivo CSV final ultraleve, otimizando o processamento da interface gráfica. **A cada 24 horas**, o cache é invalidado forçando um novo ciclo ETL de forma transparente para manter as atualizações recentes.

## 💻 Instalação e Execução Local

### Pré-requisitos
- Python 3.9+
- Dependências gerenciadas via `pip`

### Passo a passo
1. Clone o repositório:
```bash
git clone https://github.com/Renatoandrade00/indicadores_criminais_m4.git
cd indicadores_criminais_m4
```

2. Instale as bibliotecas requeridas:
```bash
pip install -r requirements.txt
```

3. Inicie o servidor do dashboard:
```bash
streamlit run app.py
```
O painel abrirá automaticamente no seu navegador em `http://localhost:8501`.

## ☁️ Instruções para Deploy no Render

A aplicação está configurada para subir nativamente na infraestrutura de web services da [Render](https://render.com/). Para fazer deploy:
1. Conecte o repositório GitHub ao Render como um *Web Service*.
2. Defina a variável de ambiente (Build Command): `pip install -r requirements.txt`.
3. Defina o comando de inicialização (Start Command): `streamlit run app.py --server.port $PORT`.

---
*Desenvolvido focado em Ciência de Dados e Segurança Pública* 🚔

## 🤝 Conecte-se comigo

- **LinkedIn:** [Renato Andrade](www.linkedin.com/in/renato-andrade-a79570299)
- **DIO:** [Renato Andrade](https://web.dio.me/users/renatoandrade00)

