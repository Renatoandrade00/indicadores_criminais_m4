import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data

st.set_page_config(page_title="Indicadores Criminais CPA/M-4", layout="wide", page_icon="🚓")

# CSS customizado para aparência de Power BI
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .kpi-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .kpi-title {
        font-size: 14px;
        color: #666;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        color: #333;
    }
    .kpi-variation-up {
        color: #d32f2f;
        font-weight: bold;
        font-size: 14px;
    }
    .kpi-variation-down {
        color: #388e3c;
        font-weight: bold;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚓 Painel de Indicadores Criminais - CPA/M-4")
st.markdown("Análise corporativa de indicadores criminais da área do Comando de Policiamento.")

# Carregar dados
df = load_data()

if df.empty:
    st.warning("Nenhum dado encontrado. Execute o ETL ou verifique os arquivos da pasta 'data/raw_drive'.")
    st.stop()

# Garantir ordenação correta para encontrar o último mês
df = df.sort_values(by=['ANO', 'MES_INT'])

# --- SIDEBAR (Filtros) ---
st.sidebar.header("Filtros Globais")

# 1. Filtro de Batalhão
todos_bpms = ["CPA/M-4 (Todos)"] + sorted([b for b in df['BATALHAO'].unique() if b != "Desconhecido"])
selected_bpm = st.sidebar.selectbox("Selecione o Batalhão", todos_bpms)

# Filtrar Cias com base no BPM selecionado
if selected_bpm == "CPA/M-4 (Todos)":
    todas_cias = sorted([c for c in df['CIA'].unique() if c != "Desconhecido"])
else:
    todas_cias = sorted([c for c in df[df['BATALHAO'] == selected_bpm]['CIA'].unique() if c != "Desconhecido"])

selected_cias = st.sidebar.multiselect("Selecione a(s) Cia(s) (Deixe vazio para todas)", todas_cias, default=[])

# 2. Filtro de Indicador
todos_indicadores = df['INDICADOR'].unique().tolist()
selected_indicadores = st.sidebar.multiselect("Selecione os Indicadores", todos_indicadores, default=todos_indicadores)

st.sidebar.divider()

# --- LÓGICA DE TEMPO PADRÃO ---
ultimo_ano = df['ANO'].max()
ultimo_mes_int = df[df['ANO'] == ultimo_ano]['MES_INT'].max()
mes_nome_ultimo = df[(df['ANO'] == ultimo_ano) & (df['MES_INT'] == ultimo_mes_int)]['MES'].iloc[0]

st.sidebar.header("Comparativo de Períodos")
anos_disponiveis = sorted(df['ANO'].unique().tolist())
meses_nomes_disponiveis = df['MES'].unique().tolist()

# Período 1 (Atual)
st.sidebar.subheader("Período de Análise (Atual)")
ano_1 = st.sidebar.selectbox("Ano (Atual)", anos_disponiveis, index=anos_disponiveis.index(ultimo_ano))
mes_1_idx = meses_nomes_disponiveis.index(mes_nome_ultimo) if mes_nome_ultimo in meses_nomes_disponiveis else 0
mes_1 = st.sidebar.selectbox("Mês (Atual)", meses_nomes_disponiveis, index=mes_1_idx)

# Período 2 (Anterior/Comparação)
st.sidebar.subheader("Período de Comparação")
ano_anterior = ultimo_ano - 1
idx_ano_ant = anos_disponiveis.index(ano_anterior) if ano_anterior in anos_disponiveis else 0
ano_2 = st.sidebar.selectbox("Ano (Comparação)", anos_disponiveis, index=idx_ano_ant)
mes_2 = st.sidebar.selectbox("Mês (Comparação)", meses_nomes_disponiveis, index=mes_1_idx)

# --- PROCESSAMENTO DOS DADOS FILTRADOS ---
def apply_filters(dataframe, bpm, cias, inds, ano, mes):
    df_f = dataframe.copy()
    if bpm != "CPA/M-4 (Todos)":
        df_f = df_f[df_f['BATALHAO'] == bpm]
    if cias:
        df_f = df_f[df_f['CIA'].isin(cias)]
    if inds:
        df_f = df_f[df_f['INDICADOR'].isin(inds)]
    if ano:
        df_f = df_f[df_f['ANO'] == ano]
    if mes:
        df_f = df_f[df_f['MES'] == mes]
    return df_f

df_periodo1 = apply_filters(df, selected_bpm, selected_cias, selected_indicadores, ano_1, mes_1)
df_periodo2 = apply_filters(df, selected_bpm, selected_cias, selected_indicadores, ano_2, mes_2)

total_periodo1 = df_periodo1['QUANTIDADE'].sum()
total_periodo2 = df_periodo2['QUANTIDADE'].sum()

def calculate_variation(current, prev):
    if prev == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - prev) / prev) * 100

variacao_total = calculate_variation(total_periodo1, total_periodo2)

# --- KPIS (Métricas Superiores) ---
st.markdown(f"### Visão Geral: {mes_1}/{ano_1} vs {mes_2}/{ano_2}")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Ocorrências ({mes_1}/{ano_1})</div>
            <div class="kpi-value">{int(total_periodo1):,}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Ocorrências ({mes_2}/{ano_2})</div>
            <div class="kpi-value">{int(total_periodo2):,}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    if variacao_total > 0:
        var_class = "kpi-variation-up"
        sinal = "+"
    elif variacao_total < 0:
        var_class = "kpi-variation-down"
        sinal = ""
    else:
        var_class = ""
        sinal = ""
        
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Variação no Período</div>
            <div class="kpi-value {var_class}">{sinal}{variacao_total:.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- GRÁFICOS ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown(f"#### Ocorrências por Companhia ({mes_1}/{ano_1})")
    if not df_periodo1.empty:
        df_cia = df_periodo1.groupby("CIA")["QUANTIDADE"].sum().reset_index()
        df_cia = df_cia.sort_values(by="QUANTIDADE", ascending=True)
        # text_auto=True insere o valor sobre a barra
        fig_bar = px.bar(
            df_cia, x="QUANTIDADE", y="CIA", orientation='h', 
            color="QUANTIDADE", color_continuous_scale="Blues", text_auto=True
        )
        fig_bar.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        # Ajustar a formatação e posição do texto no gráfico
        fig_bar.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Sem dados para o período atual.")

with col_chart2:
    st.markdown("#### Comparativo por Indicador")
    if not df_periodo1.empty or not df_periodo2.empty:
        df_ind1 = df_periodo1.groupby("INDICADOR")["QUANTIDADE"].sum().reset_index()
        df_ind1['Período'] = f"{mes_1}/{ano_1}"
        
        df_ind2 = df_periodo2.groupby("INDICADOR")["QUANTIDADE"].sum().reset_index()
        df_ind2['Período'] = f"{mes_2}/{ano_2}"
        
        df_ind_comp = pd.concat([df_ind1, df_ind2])
        
        fig_ind = px.bar(
            df_ind_comp, x="INDICADOR", y="QUANTIDADE", color="Período", 
            barmode='group', color_discrete_sequence=['#1f77b4', '#ff7f0e'], text_auto=True
        )
        fig_ind.update_layout(margin=dict(l=0, r=0, t=30, b=0), xaxis_title="")
        fig_ind.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_ind, use_container_width=True)
    else:
        st.info("Sem dados para comparar.")

st.divider()

# --- INSIGHTS AUTOMÁTICOS ---
st.markdown("### 💡 Insights da Operação")
st.markdown("Análise tática das variações nos indicadores selecionados:")

insights = []

if not df_periodo1.empty and not df_periodo2.empty:
    ind_p1 = df_periodo1.groupby("INDICADOR")["QUANTIDADE"].sum()
    ind_p2 = df_periodo2.groupby("INDICADOR")["QUANTIDADE"].sum()
    
    variacoes_ind = {}
    for ind in selected_indicadores:
        v1 = ind_p1.get(ind, 0)
        v2 = ind_p2.get(ind, 0)
        var = calculate_variation(v1, v2)
        variacoes_ind[ind] = var
        
    if variacoes_ind:
        max_aumento = max(variacoes_ind.items(), key=lambda x: x[1])
        max_queda = min(variacoes_ind.items(), key=lambda x: x[1])
        
        if max_aumento[1] > 0:
            insights.append(f"⚠️ **Ponto de Atenção:** O indicador **{max_aumento[0]}** teve o maior crescimento da área, subindo **{max_aumento[1]:.1f}%**.")
        
        if max_queda[1] < 0:
            insights.append(f"✅ **Bons Resultados:** Houve forte redução no indicador **{max_queda[0]}**, caindo **{abs(max_queda[1]):.1f}%** em relação ao período anterior.")

if not insights:
    insights.append("Estabilidade nos indicadores: não foram identificadas altas ou baixas significativas com os filtros atuais.")

for ins in insights:
    st.markdown(f"- {ins}")
