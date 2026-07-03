import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data, filter_data, calculate_variation

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
st.markdown("Análise comparativa de dados criminais das delegacias subordinadas.")

# Carregar dados
df = load_data()

if df.empty:
    st.warning("Nenhum dado encontrado. Certifique-se de que os arquivos de dados estão na pasta 'data'.")
    st.stop()

# --- SIDEBAR (Filtros) ---
st.sidebar.header("Filtros Globais")

# Filtro de Delegacia
todas_dps = df['DELEGACIA'].unique().tolist()
selected_dps = st.sidebar.multiselect("Selecione as Delegacias (DP)", todas_dps, default=todas_dps)

# Filtro de Indicador
todos_indicadores = df['INDICADOR'].unique().tolist()
selected_indicadores = st.sidebar.multiselect("Selecione os Indicadores", todos_indicadores, default=todos_indicadores)

st.sidebar.divider()

# Comparativo de Períodos
st.sidebar.header("Comparativo de Períodos")
anos_disponiveis = sorted(df['ANO'].unique().tolist())
meses_disponiveis = df['MES'].unique().tolist()

# Período 1 (Atual)
st.sidebar.subheader("Período de Análise (Atual)")
ano_1 = st.sidebar.selectbox("Ano (Atual)", anos_disponiveis, index=len(anos_disponiveis)-1)
meses_1 = st.sidebar.multiselect("Meses (Atual)", meses_disponiveis, default=meses_disponiveis)

# Período 2 (Anterior/Comparação)
st.sidebar.subheader("Período de Comparação")
ano_2 = st.sidebar.selectbox("Ano (Comparação)", anos_disponiveis, index=0)
meses_2 = st.sidebar.multiselect("Meses (Comparação)", meses_disponiveis, default=meses_disponiveis)

# --- PROCESSAMENTO DOS DADOS ---
df_periodo1 = filter_data(df, selected_dps, selected_indicadores, ano_1, meses_1)
df_periodo2 = filter_data(df, selected_dps, selected_indicadores, ano_2, meses_2)

total_periodo1 = df_periodo1['QUANTIDADE'].sum()
total_periodo2 = df_periodo2['QUANTIDADE'].sum()

variacao_total = calculate_variation(total_periodo1, total_periodo2)

# --- KPIS (Métricas Superiores) ---
st.markdown("### Resumo Geral")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total de Ocorrências ({ano_1})</div>
            <div class="kpi-value">{int(total_periodo1):,}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total de Ocorrências ({ano_2})</div>
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
            <div class="kpi-title">Variação Percentual</div>
            <div class="kpi-value {var_class}">{sinal}{variacao_total:.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- GRÁFICOS ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown(f"#### Ocorrências por DP ({ano_1})")
    if not df_periodo1.empty:
        df_dp = df_periodo1.groupby("DELEGACIA")["QUANTIDADE"].sum().reset_index()
        df_dp = df_dp.sort_values(by="QUANTIDADE", ascending=True)
        fig_bar = px.bar(df_dp, x="QUANTIDADE", y="DELEGACIA", orientation='h', color="QUANTIDADE", color_continuous_scale="Blues")
        fig_bar.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Sem dados para o período atual.")

with col_chart2:
    st.markdown("#### Comparativo por Indicador")
    if not df_periodo1.empty or not df_periodo2.empty:
        df_ind1 = df_periodo1.groupby("INDICADOR")["QUANTIDADE"].sum().reset_index()
        df_ind1['Período'] = str(ano_1)
        
        df_ind2 = df_periodo2.groupby("INDICADOR")["QUANTIDADE"].sum().reset_index()
        df_ind2['Período'] = str(ano_2)
        
        df_ind_comp = pd.concat([df_ind1, df_ind2])
        
        fig_ind = px.bar(df_ind_comp, x="INDICADOR", y="QUANTIDADE", color="Período", barmode='group', color_discrete_sequence=['#1f77b4', '#ff7f0e'])
        fig_ind.update_layout(margin=dict(l=0, r=0, t=30, b=0), xaxis_title="")
        st.plotly_chart(fig_ind, use_container_width=True)
    else:
        st.info("Sem dados para comparar.")

st.divider()

# --- INSIGHTS AUTOMÁTICOS ---
st.markdown("### 💡 Insights Automáticos")
st.markdown("Resumo do comportamento criminal com base nos filtros selecionados:")

insights = []

# Analisando o indicador que mais cresceu/caiu
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
            insights.append(f"⚠️ **Atenção:** O indicador **{max_aumento[0]}** apresentou o maior aumento no período ({max_aumento[1]:.1f}%).")
        
        if max_queda[1] < 0:
            insights.append(f"✅ **Ponto Positivo:** O indicador **{max_queda[0]}** teve a maior queda no período ({max_queda[1]:.1f}%).")

if not insights:
    insights.append("Não foi possível gerar insights significativos com os dados atuais.")

for ins in insights:
    st.markdown(f"- {ins}")
