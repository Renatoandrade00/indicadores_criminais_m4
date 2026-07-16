# Projeto Indicadores Criminais - CPA/M-4

## 📌 Visão Geral
Este projeto é um **Dashboard Interativo** desenvolvido em Python com Streamlit para a análise, monitoramento e apresentação tática de indicadores criminais referentes à área do Comando de Policiamento de Área Metropolitana 4 (CPA/M-4). O painel tem como objetivo facilitar a tomada de decisão através de recursos visuais dinâmicos, comparações de períodos e análises automatizadas.

## 📊 Fonte dos Dados
> **Aviso Importante:** Todos os dados processados, estruturados e exibidos nesta aplicação têm como origem exclusiva os **dados abertos disponibilizados publicamente pela Secretaria de Segurança Pública (SSP)**. O sistema atua apenas como uma ferramenta de Business Intelligence (BI) para facilitar a visualização de informações que já são de domínio público.

## 🚀 Funcionalidades Principais
- **Filtros Interativos Avançados**: Capacidade de filtrar as análises por Batalhões, Companhias (Cias), Múltiplos Indicadores Criminais e dois períodos de tempo distintos (Mês/Ano Atual vs Mês/Ano Anterior) para cruzamento de dados.
- **Cartões de KPI (Key Performance Indicators)**: Exibição imediata do volume total de ocorrências nos períodos selecionados e o cálculo automático da variação percentual.
- **Tabelas de Comparativo Quantitativo**: 
  - Visão do Acumulado do Ano (Janeiro até o mês de referência selecionado).
  - Visão do Mês Específico.
- **Visualizações Gráficas Modernas (Altair)**:
  - Gráficos de barras agrupados (*grouped bar charts*) com `xOffset` para fácil comparação lado a lado entre períodos.
  - Gráficos de pizza elegantes com rótulos internos inteligentes, evidenciando as fatias de distribuição de cada Batalhão/Cia perfeitamente adaptáveis aos temas Dark/Light do sistema.
- **Diagnóstico Situacional Tático**: Algoritmo inteligente que gera *insights* textuais automatizados alertando sobre pontos de atenção (indicadores com maiores altas) e parabenizando bons resultados (maiores quedas).
- **Modo Apresentação Automática**: Um carrossel que rotaciona de forma autônoma os gráficos de toda a área e integra apresentações externas, sendo ideal para exibição em televisores e monitores de acompanhamento contínuo nos gabinetes.

## 🛠️ Tecnologias Utilizadas
- **Python**: Linguagem base (Backend).
- **Streamlit**: Framework *Full-stack* veloz para a construção de toda a interface web (Frontend).
- **Pandas**: Motor analítico para manipulação de dataframes, transformação e agregação (ETL) da base de dados.
- **Altair**: Biblioteca declarativa estatística de visualização de dados, responsável por entregar renderizações fluídas, robustas e esteticamente agradáveis.

## 📂 Estrutura do Projeto Principal
- `app.py`: Arquivo "Coração" da aplicação. Orquestra a injeção de CSS, gerencia o estado da sessão, constrói a UI (Barra Lateral) e renderiza todos os componentes gráficos da classe `DashboardRenderer`.
- `data_loader.py`: Módulo focado no *Pipeline* de dados (Leitura, tratamento de nulos, tipagem e preparação da base em cache).
- `docs/`: Diretório que centraliza a documentação técnica, regras de negócio e de uso do projeto.

## ⚙️ Como Executar o Projeto Localmente

1. **Acesse a pasta do projeto.**
2. **Crie e ative um ambiente virtual (recomendado):**
   ```bash
   python -m venv .venv
   
   # No Windows: 
   .venv\Scripts\activate
   # No Linux/Mac:
   source .venv/bin/activate
   ```
3. **Instale as dependências (via requirements caso exista, ou manualmente):**
   ```bash
   pip install streamlit pandas altair
   ```
4. **Alimente os Dados:** Certifique-se de que as planilhas/tabelas da SSP estão inseridas no caminho de diretório de dados esperado pelo sistema (`data_loader.py`).
5. **Inicie o servidor local da aplicação:**
   ```bash
   streamlit run app.py
   ```
O painel abrirá automaticamente no seu navegador padrão (Geralmente no endereço `http://localhost:8501`).
