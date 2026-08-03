import pandas as pd
import os
import streamlit as st

from etl import run_etl

@st.cache_data(ttl=3600)
def _read_csv_cached(file_path: str, mtime: float) -> pd.DataFrame:
    """
    Função interna com cache vinculada à data de modificação (mtime) do arquivo.
    Se o arquivo for modificado (ex: novo commit do GitHub Actions), o cache invalida automaticamente.
    """
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding='latin1')

def load_data():
    """
    Carrega os dados criminais consolidados com invalidação automática de cache.
    """
    file_path = os.path.join("data", "dados_tratados.csv")
    
    # Se o arquivo não existir, executa o ETL para gerá-lo
    if not os.path.exists(file_path):
        try:
            run_etl()
        except Exception as e:
            print(f"Erro ao executar ETL automático: {e}")
            
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    mtime = os.path.getmtime(file_path)
    return _read_csv_cached(file_path, mtime)

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
