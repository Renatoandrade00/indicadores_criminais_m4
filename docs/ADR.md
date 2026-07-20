# Architecture Decision Records — Indicadores Criminais CPA/M-4

> Registro das decisões arquiteturais do projeto, organizadas cronologicamente.
> Formato: [MADR (Markdown Any Decision Records)](https://adr.github.io/madr/).

---

## ADR-001 — Streamlit como framework full-stack

| Campo | Valor |
|---|---|
| **Status** | ✅ Aceito |
| **Data** | 2024 (commit inicial) |
| **Decisores** | Renato Andrade |

### Contexto

O projeto necessitava de uma ferramenta que permitisse a um único desenvolvedor construir um dashboard analítico completo — com backend, frontend e visualizações interativas — de forma ágil e sem a necessidade de manter dois repositórios (API + SPA).

### Opções Avaliadas

| Opção | Prós | Contras |
|---|---|---|
| **Streamlit** | Deploy single-file, widgets nativos, cache embutido, ecossistema Python, zero JS | Menos controle de layout, state management simplificado |
| **Dash (Plotly)** | Mais customizável, callbacks explícitos | Boilerplate maior, curva de aprendizado em callbacks |
| **Flask + React** | Máxima flexibilidade | Dois stacks, deploy complexo, overkill para o escopo |
| **Power BI** | Líder corporativo, drag-and-drop | Licenciamento, sem flexibilidade de código, dados proprietários |

### Decisão

**Streamlit** foi escolhido por:
1. **Velocidade de entrega** — protótipo funcional em horas.
2. **Stack unificado** — Python puro, sem necessidade de JavaScript.
3. **Cache nativo** — `@st.cache_data` resolve o problema de reprocessamento do ETL.
4. **Implantação trivial** — compatível com Render, Heroku e qualquer PaaS.
5. **Alinhamento com perfil do time** — desenvolvedor focado em Ciência de Dados / Python.

### Consequências

- (+) Toda a aplicação reside em **~500 linhas de Python** + um CSS inline mínimo.
- (+) Iterações rápidas: alterações visuais são testáveis em segundos com hot-reload.
- (−) Customizações de layout avançadas exigem injeção de HTML/CSS via `st.markdown(unsafe_allow_html=True)`.
- (−) Lógica de apresentação (carrossel) depende de `time.sleep()`, que bloqueia o thread Streamlit.

---

## ADR-002 — ETL local com Pandas (sem banco de dados)

| Campo | Valor |
|---|---|
| **Status** | ✅ Aceito |
| **Data** | 2024 (commit inicial) |
| **Decisores** | Renato Andrade |

### Contexto

Os dados de origem são planilhas Excel (`.xlsx`) publicadas mensalmente pela SSP-SP. O volume de dados é pequeno (dezenas de planilhas, dezenas de milhares de linhas no total consolidado). Era necessário decidir se os dados seriam armazenados em banco ou em flat file.

### Opções Avaliadas

| Opção | Prós | Contras |
|---|---|---|
| **CSV flat file** (via Pandas) | Zero infra, sem dependência externa, portável | Sem indexação, sem ACID |
| **SQLite** | Consultas SQL, indexação | Overhead para o volume atual |
| **PostgreSQL / MySQL** | Escalável, multi-user | Requer servidor, config de infra |
| **DuckDB** | Analítico, SQL nativo em arquivos | Dependência adicional |

### Decisão

**CSV flat file** como armazenamento de saída do ETL, por:
1. O volume total de dados consolidados cabe inteiramente em memória (~244 KB).
2. Elimina completamente a necessidade de infraestrutura de banco de dados.
3. O `@st.cache_data` do Streamlit faz as vezes de "cache de consulta" com TTL de 24 horas.
4. Portabilidade: o CSV é legível por qualquer ferramenta (Excel, Power BI, R).

### Consequências

- (+) Deploy simplificado: nenhum serviço de banco para provisionar.
- (+) Debugging fácil: basta abrir o CSV para verificar os dados.
- (−) Se o volume crescer significativamente (ex.: incluir todas as DPs do estado), será necessário migrar para DuckDB ou SQLite.
- (−) Sem controle de concorrência em escrita.

---

## ADR-003 — Mapeamento estático DP → Batalhão/Cia

| Campo | Valor |
|---|---|
| **Status** | ✅ Aceito |
| **Data** | 2024 (refatoração para BPM/Cia) |
| **Decisores** | Renato Andrade |

### Contexto

Os dados da SSP identificam ocorrências por **Delegacia de Polícia (DP)**, mas a análise operacional da PM organiza-se por **Batalhão (BPM/M) e Companhia (Cia)**. Era necessário traduzir a circunscrição civil (DP) para a estrutura militar (BPM/Cia) para que os filtros do dashboard refletissem a cadeia de comando.

### Decisão

Mapeamento implementado como **dicionário Python estático** (`MAP_MILITAR`) no módulo `etl.py`, contendo 12 entradas:

```
DP → { BPM: "Xº BPM/M", CIA: "Yª Cia - Bairro" }
```

### Justificativa

- A jurisdição DP↔BPM raramente muda (decreto estadual).
- Um dicionário hardcoded é mais simples e auditável que uma tabela externa.
- Caso haja alteração jurisdicional, basta atualizar o dicionário e re-executar o ETL.

### Consequências

- (+) Zero dependência externa para o mapeamento.
- (+) O ETL aplica o mapeamento automaticamente, sem intervenção manual.
- (−) Qualquer alteração na jurisdição exige modificação do código-fonte.

---

## ADR-004 — Altair como biblioteca de visualização principal

| Campo | Valor |
|---|---|
| **Status** | ✅ Aceito |
| **Data** | 2025 (migração pós-refatoração) |
| **Decisores** | Renato Andrade |

### Contexto

O dashboard utiliza gráficos agrupados (barras comparativas entre períodos) e gráficos de pizza com rótulos internos. A escolha da biblioteca de visualização impacta diretamente a qualidade visual e a manutenção do código.

### Opções Avaliadas

| Opção | Prós | Contras |
|---|---|---|
| **Altair** | API declarativa, composição elegante (camadas), `xOffset` nativo para agrupamento | Customização fina mais limitada |
| **Plotly** | Interatividade rica, suporte 3D | API mais verbosa, bundle JS maior |
| **Matplotlib** | Máxima customização | Não interativo, estética datada |
| **st.bar_chart** (nativo) | Zero config | Sem agrupamento, sem controle de cor |

### Decisão

**Altair** para gráficos que exigem agrupamento e composição de camadas (comparativos por período, pizza com texto). **`st.bar_chart`** mantido para visualizações simples (barras horizontais por localidade) onde a configuração mínima é vantajosa.

### Consequências

- (+) Gráficos agrupados com `xOffset='Período:N'` resolvem a comparação lado a lado de forma elegante.
- (+) Composição `mark_arc() + mark_text()` permite rótulos inteligentes dentro do gráfico de pizza.
- (−) Altair não consta no `requirements.txt` — é trazido como dependência transitiva do Streamlit, o que é um risco implícito de versão.

---

## ADR-005 — Deploy no Render (PaaS)

| Campo | Valor |
|---|---|
| **Status** | ✅ Aceito |
| **Data** | 2024 |
| **Decisores** | Renato Andrade |

### Contexto

O painel precisa estar acessível pela internet para consulta remota por comandantes e analistas do CPA/M-4.

### Opções Avaliadas

| Opção | Prós | Contras |
|---|---|---|
| **Render** | Gratuito (tier free), auto-deploy do GitHub | Cold start lento no free tier |
| **Streamlit Cloud** | Zero config para Streamlit | Menos controle, restrições de recursos |
| **Heroku** | Maduro, bem documentado | Free tier descontinuado |
| **VPS (EC2, DigitalOcean)** | Controle total | Gerenciamento manual, custo mensal |

### Decisão

**Render** por:
1. Tier gratuito suficiente para o tráfego esperado.
2. Auto-deploy integrado ao repositório GitHub.
3. Configuração simples via comandos `pip install` + `streamlit run`.

### Consequências

- (+) URL pública disponível: `https://indicadores-criminais-m4.onrender.com`.
- (+) Deploy automático a cada push na branch `main`.
- (−) Cold start de ~30s após inatividade no free tier.
- (−) O ETL é re-executado a cada restart do container (mitigado pelo cache de 24h).

---

## ADR-006 — Cache com TTL de 24 horas como estratégia de atualização

| Campo | Valor |
|---|---|
| **Status** | ✅ Aceito |
| **Data** | 2024 |
| **Decisores** | Renato Andrade |

### Contexto

Os dados são atualizados mensalmente pela SSP. Não há necessidade de refresh em tempo real, mas é importante que novas planilhas inseridas na pasta `data/raw_drive/` sejam detectadas automaticamente.

### Decisão

`@st.cache_data(ttl=86400)` no `data_loader.py`. A cada 24 horas, o cache expira, o ETL é re-executado e o CSV consolidado é regenerado.

### Consequências

- (+) Zero intervenção manual: basta adicionar a planilha nova na pasta e esperar o próximo ciclo.
- (+) Performance excelente durante o dia: todas as requisições leem do cache.
- (−) Se uma correção urgente de dados for necessária, o operador precisa reiniciar o app manualmente ou limpar o cache via Streamlit.

---

## ADR-007 — Arquitetura orientada a classes (MVC-like)

| Campo | Valor |
|---|---|
| **Status** | ✅ Aceito |
| **Data** | 2025 (refatoração) |
| **Decisores** | Renato Andrade |

### Contexto

O `app.py` inicial era procedural, dificultando a manutenção à medida que funcionalidades eram adicionadas (filtros, diagnóstico, carrossel). Era necessário organizar responsabilidades.

### Decisão

O código foi reorganizado em 4 classes no `app.py`:

| Classe | Responsabilidade | Padrão análogo |
|---|---|---|
| `DashboardData` | Regras de negócio, filtros, cálculos | **Model** |
| `FilterUI` | Gerenciamento da sidebar e estado dos filtros | **Controller** |
| `DashboardRenderer` | Renderização de todos os componentes visuais | **View** |
| `App` | Orquestração / Bootstrap | **Application Facade** |

### Consequências

- (+) Separação clara de responsabilidades.
- (+) Cada seção visual é um método isolado (`render_kpis`, `render_tables`, etc.), facilitando testes e manutenção.
- (−) `DashboardRenderer` é uma classe grande (~250 linhas). Futuras funcionalidades podem justificar decomposição em componentes menores.

---

## ADR-008 — Dados brutos mantidos fora do controle de versão

| Campo | Valor |
|---|---|
| **Status** | ✅ Aceito |
| **Data** | 2024 |
| **Decisores** | Renato Andrade |

### Contexto

As planilhas da SSP são arquivos Excel de 300-500 KB cada. Embora pequenas, são dados públicos que mudam mensalmente e não devem poluir o histórico do Git.

### Decisão

`data/raw_drive/` está no `.gitignore`. As planilhas são distribuídas por mecanismo externo (cópia manual ou script futuro de download).

### Consequências

- (+) Repositório leve (~30 KB sem as planilhas).
- (+) Nenhum dado sensível é versionado.
- (−) Novo contribuidor precisa obter as planilhas separadamente para rodar o ETL completo.
- (−) O script `generate_mock_data.py` existe como alternativa para desenvolvimento sem dados reais.

---

## ADR-009 — Ingestão automatizada via GitHub Actions e Google Drive API

| Campo | Valor |
|---|---|
| **Status** | ✅ Aceito |
| **Data** | Julho de 2026 |
| **Decisores** | Renato Andrade |

### Contexto

Os dados da SSP são publicados mensalmente em uma pasta pública do Google Drive. O processo manual de download e commit das planilhas ou de acionamento do ETL tornava-se repetitivo e sujeito a esquecimento. Era necessário automatizar esse fluxo.

### Opções Avaliadas

| Opção | Prós | Contras |
|---|---|---|
| **gdown + Streamlit (on-the-fly)** | Sem infra extra | Lento no carregamento da página do usuário, consome muita banda do servidor Render |
| **Cron Job no Render** | Usa o mesmo servidor | Free tier dorme (sleep mode), cron falharia |
| **GitHub Actions (Cron)** | Confiável, gratuito, permite commit do resultado | Requer configurar workflows e secrets |

### Decisão

Foi escolhida a opção de usar **GitHub Actions** agendado para rodar a cada 12 horas.
O workflow executa um novo script (`sync_ssp.py`) que usa a API do Google Drive para listar arquivos e o `gdown` para baixá-los, registrando os downloads no `sync_manifest.json`. Se houver arquivos novos, ele aciona o ETL e faz um commit automático do `dados_tratados.csv`.

### Consequências

- (+) O dashboard em produção lê apenas o CSV já processado, garantindo alta performance.
- (+) O processo é "set-and-forget", mantendo os dados atualizados sem intervenção humana.
- (−) Requer a manutenção de uma API Key do Google Cloud como *secret* no GitHub.

---

## ADR-010 — Layout dinâmico no Modo Apresentação

| Campo | Valor |
|---|---|
| **Status** | ✅ Aceito |
| **Data** | Julho de 2026 |
| **Decisores** | Renato Andrade |

### Contexto

O painel possui um botão de "Apresentação Automática" para rodar um carrossel em telões. No entanto, o Streamlit preservava o restante da página (KPIs, tabelas, cabeçalho), obrigando o usuário a rolar a tela, o que causava pulos (saltos) indesejados a cada `st.rerun()`.

### Decisão

Implementar um layout adaptativo via Python e JavaScript:
1. Quando ativado o modo apresentação, **ocultar** todos os gráficos, tabelas e cabeçalho da página (Brasão e Título), focando unicamente no carrossel.
2. Alterar dinamicamente o CSS (`padding-top`) de `4.5rem` para `1.5rem` para maximizar o espaço útil.
3. Injetar um pequeno script JavaScript para forçar o scroll da janela para o topo no momento do clique, garantindo o enquadramento perfeito no telão.

### Consequências

- (+) Experiência de apresentação muito mais fluida e limpa ("clean").
- (+) Resolução definitiva do bug visual do "pulo da tela".
- (−) O Streamlit não lida muito bem com scroll via Python, exigindo a injeção do JS (`window.parent.scrollTo(0,0)`).

---

## Registro de Decisões Pendentes

| ID | Tema | Status |
|---|---|---|
| ADR-011 | Migração para DuckDB se volume ultrapassar 1 MB consolidado | 🟡 Planejado |
| ADR-012 | Implementação de autenticação (Streamlit `secrets`) | 🟡 Planejado |
| ADR-013 | Inclusão de indicadores de produtividade policial (planilhas PRODUTIVIDADE) | 🟡 Planejado |

---

*Última atualização: Julho de 2026*
