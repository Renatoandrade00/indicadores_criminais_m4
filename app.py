import streamlit as st
import pandas as pd
import plotly.express as px
import time
import base64
import os
import altair as alt
from data_loader import load_data

st.set_page_config(page_title="Indicadores Criminais CPA/M-4", layout="wide", page_icon="🚓")

class DashboardData:
    """Encapsula as regras de negócio de manipulação de dados e filtros."""
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
        if not self.df.empty:
            self.df = self.df.sort_values(by=['ANO', 'MES_INT'])
            self.anos_disponiveis = sorted(self.df['ANO'].unique().tolist())
            self.meses_nomes = self.df['MES'].unique().tolist()
            self.todos_indicadores = self.df['INDICADOR'].unique().tolist()
            
            self.ultimo_ano = self.df['ANO'].max()
            self.ultimo_mes_int = self.df[self.df['ANO'] == self.ultimo_ano]['MES_INT'].max()
            self.ultimo_mes_nome = self.df[(self.df['ANO'] == self.ultimo_ano) & (self.df['MES_INT'] == self.ultimo_mes_int)]['MES'].iloc[0]
        else:
            self.anos_disponiveis = []
            self.meses_nomes = []
            self.todos_indicadores = []
            self.ultimo_ano = None
            self.ultimo_mes_int = None
            self.ultimo_mes_nome = None

    def get_batalhoes(self):
        return ["CPA/M-4 (Todos)"] + sorted([b for b in self.df['BATALHAO'].unique() if b != "Desconhecido"])

    def get_cias(self, bpm="CPA/M-4 (Todos)"):
        if bpm == "CPA/M-4 (Todos)":
            return sorted([c for c in self.df['CIA'].unique() if c != "Desconhecido"])
        return sorted([c for c in self.df[self.df['BATALHAO'] == bpm]['CIA'].unique() if c != "Desconhecido"])

    def get_mes_int(self, mes_nome):
        resultado = self.df[self.df['MES'] == mes_nome]['MES_INT']
        return resultado.iloc[0] if not resultado.empty else 1
        
    def get_mes_nome(self, mes_int):
        resultado = self.df[self.df['MES_INT'] == mes_int]['MES']
        return resultado.iloc[0] if not resultado.empty else "Janeiro"

    def filter_periodo(self, bpm, cias, inds, ano, mes):
        df_f = self.df.copy()
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

    def filter_acumulado(self, bpm, cias, inds, ano, mes_max_int):
        df_f = self.df.copy()
        if bpm != "CPA/M-4 (Todos)":
            df_f = df_f[df_f['BATALHAO'] == bpm]
        if cias:
            df_f = df_f[df_f['CIA'].isin(cias)]
        if inds:
            df_f = df_f[df_f['INDICADOR'].isin(inds)]
        if ano:
            df_f = df_f[df_f['ANO'] == ano]
        df_f = df_f[df_f['MES_INT'] <= mes_max_int]
        return df_f

    @staticmethod
    def calculate_variation(current, prev):
        if prev == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - prev) / prev) * 100


class FilterUI:
    """Gerencia a interface da barra lateral e armazena os filtros selecionados."""
    def __init__(self, data: DashboardData):
        self.data = data
        self.filters = {}

    def render(self):
        st.sidebar.header("Painel de Controle")

        with st.sidebar.expander("📍 Filtros de Localidade", expanded=True):
            bpm = st.selectbox("Selecione o Batalhão", self.data.get_batalhoes())
            cias = st.multiselect("Selecione a(s) Cia(s)", self.data.get_cias(bpm), default=[])
            
        with st.sidebar.expander("📊 Filtros de Indicador", expanded=False):
            inds = st.multiselect("Selecione os Indicadores", self.data.todos_indicadores, default=self.data.todos_indicadores)
            
        with st.sidebar.expander("📅 Filtros de Período", expanded=True):
            st.markdown("**Período de Análise (Atual)**")
            idx_ano1 = self.data.anos_disponiveis.index(self.data.ultimo_ano) if self.data.ultimo_ano in self.data.anos_disponiveis else 0
            ano_1 = st.selectbox("Ano", self.data.anos_disponiveis, index=idx_ano1, key="ano1")
            
            idx_mes1 = self.data.meses_nomes.index(self.data.ultimo_mes_nome) if self.data.ultimo_mes_nome in self.data.meses_nomes else 0
            mes_1 = st.selectbox("Mês", self.data.meses_nomes, index=idx_mes1, key="mes1")
            mes_1_int = self.data.get_mes_int(mes_1)

            st.markdown("---")
            st.markdown("**Comparar com:**")
            comparacao = st.radio(
                "Tipo de Comparação", 
                ["Mês Anterior", "Mesmo Mês do Ano Anterior", "Personalizado"],
                index=1,
                label_visibility="collapsed"
            )
            
            if comparacao == "Mês Anterior":
                if mes_1_int > 1:
                    mes_2_int = mes_1_int - 1
                    ano_2 = ano_1
                else:
                    mes_2_int = 12
                    ano_2 = ano_1 - 1
                mes_2 = self.data.get_mes_nome(mes_2_int)
                st.info(f"Comparando com: {mes_2} / {ano_2}")
                
            elif comparacao == "Mesmo Mês do Ano Anterior":
                ano_2 = ano_1 - 1
                mes_2 = mes_1
                mes_2_int = mes_1_int
                st.info(f"Comparando com: {mes_2} / {ano_2}")
                
            else:
                idx_ano_ant = self.data.anos_disponiveis.index(ano_1 - 1) if (ano_1 - 1) in self.data.anos_disponiveis else 0
                ano_2 = st.selectbox("Ano (Comparação)", self.data.anos_disponiveis, index=idx_ano_ant, key="ano2")
                mes_2 = st.selectbox("Mês (Comparação)", self.data.meses_nomes, index=idx_mes1, key="mes2")
                mes_2_int = self.data.get_mes_int(mes_2)

        self.filters = {
            'bpm': bpm, 'cias': cias, 'inds': inds,
            'ano_1': ano_1, 'mes_1': mes_1, 'mes_1_int': mes_1_int,
            'ano_2': ano_2, 'mes_2': mes_2, 'mes_2_int': mes_2_int,
            'comparacao': comparacao
        }
        return self.filters


class DashboardRenderer:
    """Controla todo o Output visual, tabelas e gráficos da tela."""
    def __init__(self, data: DashboardData, filters: dict):
        self.data = data
        self.f = filters
        
        self.df_periodo1 = self.data.filter_periodo(self.f['bpm'], self.f['cias'], self.f['inds'], self.f['ano_1'], self.f['mes_1'])
        self.df_periodo2 = self.data.filter_periodo(self.f['bpm'], self.f['cias'], self.f['inds'], self.f['ano_2'], self.f['mes_2'])
        
        self.df_acumulado_1 = self.data.filter_acumulado(self.f['bpm'], self.f['cias'], self.f['inds'], self.f['ano_1'], self.f['mes_1_int'])
        self.df_acumulado_2 = self.data.filter_acumulado(self.f['bpm'], self.f['cias'], self.f['inds'], self.f['ano_2'], self.f['mes_2_int'])
        
        self.total_periodo1 = self.df_periodo1['QUANTIDADE'].sum() if not self.df_periodo1.empty else 0
        self.total_periodo2 = self.df_periodo2['QUANTIDADE'].sum() if not self.df_periodo2.empty else 0

    @staticmethod
    def inject_css():
        st.markdown("""
            <style>
            .main { background-color: #f0f2f6; }
            .kpi-card {
                background-color: white; padding: 20px; border-radius: 10px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1); text-align: center;
            }
            .kpi-title { font-size: 14px; color: #666; margin-bottom: 10px; }
            .kpi-value { font-size: 28px; font-weight: bold; color: #333; }
            .kpi-variation-up { color: #d32f2f; font-weight: bold; font-size: 14px; }
            .kpi-variation-down { color: #388e3c; font-weight: bold; font-size: 14px; }
            .custom-table {
                width: 100%; border-collapse: collapse; text-align: center;
                background-color: white; color: black; margin-bottom: 20px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            }
            .custom-table th { background-color: #e0e0e0; border: 1px solid #000; padding: 10px; font-weight: bold; }
            .custom-table td { border: 1px solid #000; padding: 8px; }
            .bg-green { background-color: #92d050; }
            .bg-red { background-color: #ff0000; color: white; font-weight: bold; }
            </style>
        """, unsafe_allow_html=True)

    def render_header(self):
        img_base64 = None
        if os.path.exists("brasao.png"):
            with open("brasao.png", "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode()
        
        if img_base64:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img src="data:image/png;base64,{img_base64}" width="70">
                    <h1 style="margin: 0;">Painel de Indicadores Criminais - CPA/M-4</h1>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.title("Painel de Indicadores Criminais - CPA/M-4")
        st.markdown("Análise dos indicadores criminais da área do Comando de Policiamento.")

    def render_kpis(self):
        st.markdown(f"### Visão Geral: {self.f['mes_1']}/{self.f['ano_1']} vs {self.f['mes_2']}/{self.f['ano_2']}")
        col1, col2, col3 = st.columns(3)
        
        variacao_total = DashboardData.calculate_variation(self.total_periodo1, self.total_periodo2)

        with col1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Ocorrências ({self.f["mes_1"]}/{self.f["ano_1"]})</div><div class="kpi-value">{int(self.total_periodo1):,}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Ocorrências ({self.f["mes_2"]}/{self.f["ano_2"]})</div><div class="kpi-value">{int(self.total_periodo2):,}</div></div>', unsafe_allow_html=True)
        with col3:
            var_class = "kpi-variation-up" if variacao_total > 0 else "kpi-variation-down" if variacao_total < 0 else ""
            sinal = "+" if variacao_total > 0 else ""
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">Variação no Período</div><div class="kpi-value {var_class}">{sinal}{variacao_total:.2f}%</div></div>', unsafe_allow_html=True)
        
        st.divider()

    def _build_html_table(self, df_atual, df_anterior, titulo_atual, titulo_anterior):
        if df_atual.empty and df_anterior.empty:
            return "<p>Sem dados</p>"
        
        ind_atual = df_atual.groupby("INDICADOR")["QUANTIDADE"].sum()
        ind_ant = df_anterior.groupby("INDICADOR")["QUANTIDADE"].sum()
        
        html = '<table class="custom-table">'
        html += f'<tr><th>INDICADOR</th><th>{titulo_atual}</th><th>{titulo_anterior}</th><th>DIFERENÇA</th><th>%</th></tr>'
        
        for ind in self.data.todos_indicadores:
            if ind not in self.f['inds']:
                continue
            v_atual = ind_atual.get(ind, 0)
            v_ant = ind_ant.get(ind, 0)
            diff = v_atual - v_ant
            perc = DashboardData.calculate_variation(v_atual, v_ant)
            
            bg_class_diff = "bg-green" if diff <= 0 else "bg-red"
            bg_class_perc = "bg-green" if perc <= 0 else "bg-red"
            
            html += f'<tr><td><b>{ind}</b></td><td>{int(v_atual)}</td><td>{int(v_ant)}</td><td class="{bg_class_diff}">{int(diff)}</td><td class="{bg_class_perc}">{perc:.0f}%</td></tr>'
        html += '</table>'
        return html

    def render_tables(self):
        st.markdown("### Comparativo Quantitativo")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"**Acumulado até {self.f['mes_1']}**")
            tit_acum_1 = f"JAN a {self.f['mes_1'][:3].upper()} {str(self.f['ano_1'])[-2:]}"
            tit_acum_2 = f"JAN a {self.f['mes_2'][:3].upper()} {str(self.f['ano_2'])[-2:]}"
            st.markdown(self._build_html_table(self.df_acumulado_1, self.df_acumulado_2, tit_acum_1, tit_acum_2), unsafe_allow_html=True)
        with col_t2:
            st.markdown(f"**Mês Específico**")
            tit_mes_1 = f"{self.f['mes_1'][:3].upper()} {self.f['ano_1']}"
            tit_mes_2 = f"{self.f['mes_2'][:3].upper()} {self.f['ano_2']}"
            st.markdown(self._build_html_table(self.df_periodo1, self.df_periodo2, tit_mes_1, tit_mes_2), unsafe_allow_html=True)
        st.divider()

    def render_bar_charts(self):
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown(f"#### Ocorrências por Localidade ({self.f['mes_1']}/{self.f['ano_1']})")
            if not self.df_periodo1.empty:
                # Criando nova coluna para Batalhão + Cia para o eixo Y
                df_bar = self.df_periodo1.copy()
                df_bar['LOCALIDADE'] = df_bar['BATALHAO'] + " - " + df_bar['CIA']
                
                df_local = df_bar.groupby("LOCALIDADE")["QUANTIDADE"].sum().reset_index()
                df_local = df_local.sort_values(by="QUANTIDADE", ascending=True)
                
                df_local["QUANTIDADE"] = pd.to_numeric(df_local["QUANTIDADE"], errors="coerce").fillna(0).astype(int)
                st.bar_chart(df_local, x="LOCALIDADE", y="QUANTIDADE", horizontal=True)
            else:
                st.info("Sem dados para o período atual.")

        with col_chart2:
            st.markdown("#### Comparativo por Indicador")
            if not self.df_periodo1.empty or not self.df_periodo2.empty:
                df_ind1 = self.df_periodo1.groupby("INDICADOR")["QUANTIDADE"].sum().reset_index()
                df_ind1['Período'] = f"{self.f['mes_1']}/{self.f['ano_1']}"
                
                df_ind2 = self.df_periodo2.groupby("INDICADOR")["QUANTIDADE"].sum().reset_index()
                df_ind2['Período'] = f"{self.f['mes_2']}/{self.f['ano_2']}"
                
                df_ind_comp = pd.concat([df_ind1, df_ind2])
                df_ind_comp["QUANTIDADE"] = pd.to_numeric(df_ind_comp["QUANTIDADE"], errors="coerce").fillna(0).astype(int)
                
                chart_comp = alt.Chart(df_ind_comp).mark_bar().encode(
                    x=alt.X('INDICADOR:N', title=""),
                    y=alt.Y('QUANTIDADE:Q', title="Quantidade"),
                    color=alt.Color('Período:N', title="Período"),
                    xOffset='Período:N',
                    tooltip=['INDICADOR', 'Período', 'QUANTIDADE']
                )
                st.altair_chart(chart_comp, use_container_width=True)
            else:
                st.info("Sem dados para comparar.")
        st.divider()

    def render_diagnosis(self):
        st.markdown("### 💡 Diagnóstico Situacional")
        st.markdown("Análise tática das variações nos indicadores selecionados:")
        insights = []
        if not self.df_periodo1.empty and not self.df_periodo2.empty:
            ind_p1 = self.df_periodo1.groupby("INDICADOR")["QUANTIDADE"].sum()
            ind_p2 = self.df_periodo2.groupby("INDICADOR")["QUANTIDADE"].sum()
            variacoes_ind = {}
            for ind in self.f['inds']:
                v1 = ind_p1.get(ind, 0)
                v2 = ind_p2.get(ind, 0)
                variacoes_ind[ind] = DashboardData.calculate_variation(v1, v2)
                
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
        st.divider()

    def render_pie_charts(self):
        st.markdown("### 🥧 Distribuição por Batalhão/Companhia")
        col_pie1, col_pie2 = st.columns(2)
        with col_pie1:
            pie_indicador = st.selectbox("Selecione 1 Indicador para a Pizza", self.data.todos_indicadores)
        with col_pie2:
            pie_visao = st.radio("Nível de Visão (Pizza)", ["CPA (Todos os Batalhões)", "Batalhão Específico (Cias)"])
            if pie_visao == "Batalhão Específico (Cias)":
                pie_bpm = st.selectbox("Selecione o Batalhão (Pizza)", [b for b in self.data.get_batalhoes() if b != "CPA/M-4 (Todos)"])
        
        df_pie = self.df_periodo1[self.df_periodo1['INDICADOR'] == pie_indicador]
        if not df_pie.empty:
            if pie_visao == "CPA (Todos os Batalhões)":
                df_pie_group = df_pie.groupby("BATALHAO")["QUANTIDADE"].sum().reset_index()
                df_pie_group["QUANTIDADE"] = pd.to_numeric(df_pie_group["QUANTIDADE"], errors="coerce").fillna(0).astype(int)
                
                df_pie_group['Percentual'] = (df_pie_group['QUANTIDADE'] / df_pie_group['QUANTIDADE'].sum() * 100).round(1).astype(str) + '%'
                df_pie_group['Label'] = df_pie_group['BATALHAO'] + ' - ' + df_pie_group['Percentual']
                
                st.markdown(f"**Distribuição de {pie_indicador} por Batalhão ({self.f['mes_1']}/{self.f['ano_1']})**")
                
                base = alt.Chart(df_pie_group).encode(
                    theta=alt.Theta(field="QUANTIDADE", type="quantitative", stack=True),
                    color=alt.Color(field="BATALHAO", type="nominal", legend=alt.Legend(title="Batalhão")),
                    tooltip=['BATALHAO', 'QUANTIDADE', 'Percentual']
                )
                pie = base.mark_arc(innerRadius=0)
                text = base.mark_text(radius=85, size=11, fontWeight='bold').encode(
                    theta=alt.Theta(field="QUANTIDADE", type="quantitative", stack=True),
                    text='Label:N',
                    color=alt.value('white')
                )
                chart = (pie + text)
                st.altair_chart(chart, use_container_width=True)
            else:
                df_pie = df_pie[df_pie['BATALHAO'] == pie_bpm]
                df_pie_group = df_pie.groupby("CIA")["QUANTIDADE"].sum().reset_index()
                df_pie_group["QUANTIDADE"] = pd.to_numeric(df_pie_group["QUANTIDADE"], errors="coerce").fillna(0).astype(int)
                
                df_pie_group['Percentual'] = (df_pie_group['QUANTIDADE'] / df_pie_group['QUANTIDADE'].sum() * 100).round(1).astype(str) + '%'
                df_pie_group['Label'] = df_pie_group['CIA'] + ' - ' + df_pie_group['Percentual']
                
                st.markdown(f"**Distribuição de {pie_indicador} nas Cias do {pie_bpm} ({self.f['mes_1']}/{self.f['ano_1']})**")
                
                base = alt.Chart(df_pie_group).encode(
                    theta=alt.Theta(field="QUANTIDADE", type="quantitative", stack=True),
                    color=alt.Color(field="CIA", type="nominal", legend=alt.Legend(title="Cia")),
                    tooltip=['CIA', 'QUANTIDADE', 'Percentual']
                )
                pie = base.mark_arc(innerRadius=0)
                text = base.mark_text(radius=85, size=11, fontWeight='bold').encode(
                    theta=alt.Theta(field="QUANTIDADE", type="quantitative", stack=True),
                    text='Label:N',
                    color=alt.value('white')
                )
                chart = (pie + text)
                st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Sem dados para o gráfico de pizza neste período.")
        st.divider()

    def render_presentation_mode(self):
        st.markdown("### 📽️ Apresentação Automática")
        st.markdown("Inicie a apresentação para rodar um carrossel comparativo dos indicadores automaticamente na tela.")
        if 'slideshow_active' not in st.session_state:
            st.session_state.slideshow_active = False
            
        if st.button("Parar Apresentação" if st.session_state.slideshow_active else "Iniciar Apresentação", type="primary"):
            st.session_state.slideshow_active = not st.session_state.slideshow_active
            st.rerun()
            
        if st.session_state.slideshow_active:
            st.warning("Apresentação em andamento... Clique em 'Parar Apresentação' para interromper.")
            
            placeholder = st.empty()
            charts = []
            
            for ind in self.f['inds']:
                df_cpa_1 = self.df_periodo1[self.df_periodo1['INDICADOR'] == ind].groupby("BATALHAO")["QUANTIDADE"].sum().reset_index()
                df_cpa_2 = self.df_periodo2[self.df_periodo2['INDICADOR'] == ind].groupby("BATALHAO")["QUANTIDADE"].sum().reset_index()
                df_cpa_1['Período'] = f"{self.f['mes_1']}/{self.f['ano_1']}"
                df_cpa_2['Período'] = f"{self.f['mes_2']}/{self.f['ano_2']}"
                df_cpa_comp = pd.concat([df_cpa_1, df_cpa_2])
                if not df_cpa_comp.empty:
                    df_cpa_comp["QUANTIDADE"] = pd.to_numeric(df_cpa_comp["QUANTIDADE"], errors="coerce").fillna(0).astype(int)
                    charts.append({
                        "title": f"**{ind}** - Visão CPA (Comparativo de Períodos)",
                        "data": df_cpa_comp
                    })
                    
            if charts:
                for chart in charts:
                    with placeholder.container():
                        st.markdown(chart["title"])
                        
                        chart_alt = alt.Chart(chart["data"]).mark_bar().encode(
                            x=alt.X('BATALHAO:N', title=""),
                            y=alt.Y('QUANTIDADE:Q', title="Quantidade"),
                            color=alt.Color('Período:N', title="Período"),
                            xOffset='Período:N',
                            tooltip=['BATALHAO', 'Período', 'QUANTIDADE']
                        )
                        st.altair_chart(chart_alt, use_container_width=True)
                        
                        st.markdown("<p style='text-align: center; color: gray; margin-top: 20px;'>Desenvolvido por Renato Andrade</p>", unsafe_allow_html=True)
                    time.sleep(12)
                    
                with placeholder.container():
                    st.components.v1.iframe("https://docs.google.com/presentation/d/1N8zFSOhrqIfUx3iJctHm7-5vmoLT2s9GmneNejiVz2U/embed?start=true&loop=true&delayms=3000", height=600, scrolling=False)
                    st.markdown("<p style='text-align: center; color: gray; margin-top: 20px;'>Desenvolvido por Renato Andrade</p>", unsafe_allow_html=True)
                time.sleep(30)
                st.rerun()

class App:
    """Classe principal de orquestração do Dashboard."""
    def __init__(self):
        pass
        
    def run(self):
        DashboardRenderer.inject_css()
        
        img_base64 = None
        if os.path.exists("brasao.png"):
            with open("brasao.png", "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode()
        
        if img_base64:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img src="data:image/png;base64,{img_base64}" width="70">
                    <h1 style="margin: 0;">Painel de Indicadores Criminais - CPA/M-4</h1>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.title("Painel de Indicadores Criminais - CPA/M-4")
        st.markdown("Análise dos indicadores criminais da área do Comando de Policiamento.")

        with st.spinner("Carregando base de dados e executando ETL (isso pode demorar na primeira vez)..."):
            self.df = load_data()
        
        if self.df.empty:
            st.warning("Nenhum dado encontrado. Execute o ETL ou verifique os arquivos da pasta 'data/raw_drive'.")
            return
            
        data = DashboardData(self.df)
        ui_filter = FilterUI(data)
        filters = ui_filter.render()
        
        renderer = DashboardRenderer(data, filters)
        
        if 'slideshow_active' not in st.session_state:
            st.session_state.slideshow_active = False
            
        if not st.session_state.slideshow_active:
            renderer.render_kpis()
            renderer.render_tables()
            renderer.render_bar_charts()
            renderer.render_diagnosis()
            renderer.render_pie_charts()
            
        renderer.render_presentation_mode()
        
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: gray;'>Desenvolvido por Renato Andrade</p>", unsafe_allow_html=True)
        
if __name__ == "__main__":
    app = App()
    app.run()
