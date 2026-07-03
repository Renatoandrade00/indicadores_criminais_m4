import pandas as pd
import os
import streamlit as st

from etl import run_etl

# st.cache_data recarrega os dados e roda a função a cada 24 horas (ttl=86400)
@st.cache_data(ttl=86400)
def load_data():
    """
    Carrega os dados criminais.
    Atualiza automaticamente executando o ETL diariamente.
    """
    # Executa o processo de tratamento (ETL) a cada 24 horas 
    # para garantir que novas planilhas sejam lidas
    try:
        run_etl()
    except Exception as e:
        print(f"Erro ao executar ETL automático: {e}")
        
    file_path = os.path.join("data", "dados_tratados.csv")
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    df = pd.read_csv(file_path)
    return df

def filter_data(df, dps, indicadores, ano, meses):
    """
    Filtra o dataframe com base nas seleções do usuário.
    """
    filtered_df = df.copy()
    
    if dps:
        filtered_df = filtered_df[filtered_df['DELEGACIA'].isin(dps)]
    
    if indicadores:
        filtered_df = filtered_df[filtered_df['INDICADOR'].isin(indicadores)]
        
    if ano:
        filtered_df = filtered_df[filtered_df['ANO'] == ano]
        
    if meses:
        filtered_df = filtered_df[filtered_df['MES'].isin(meses)]
        
    return filtered_df

def calculate_variation(current_value, previous_value):
    """
    Calcula a variação percentual entre dois períodos.
    """
    if previous_value == 0:
        if current_value == 0:
            return 0.0
        return 100.0 # Crescimento infinito (de 0 para algo)
    
    return ((current_value - previous_value) / previous_value) * 100
