import pandas as pd
import os
import re

# Constantes de filtro
DPS_CPAM4 = [
    "022 DP", "024 DP", "032 DP", "050 DP", "059 DP", "062 DP", 
    "063 DP", "064 DP", "065 DP", "067 DP", "068 DP", "103 DP"
]

# Mapeamento DP -> BPM/M e Cia
# Formato: "DP prefixo": {"BPM": "Nome BPM", "CIA": "Nome Cia"}
MAP_MILITAR = {
    "024 DP": {"BPM": "2º BPM/M", "CIA": "1ª Cia - Ponte Rasa"},
    "063 DP": {"BPM": "2º BPM/M", "CIA": "2ª Cia - Vila Jacuí"},
    "062 DP": {"BPM": "2º BPM/M", "CIA": "3ª Cia - Ermelino Matarazzo"},
    
    "050 DP": {"BPM": "29º BPM/M", "CIA": "1ª Cia - Itaim Paulista"},
    "022 DP": {"BPM": "29º BPM/M", "CIA": "2ª Cia - São Miguel Paulista"},
    "059 DP": {"BPM": "29º BPM/M", "CIA": "3ª Cia - Jardim Noemia"},
    
    "032 DP": {"BPM": "39º BPM/M", "CIA": "1ª Cia - Itaquera"},
    "065 DP": {"BPM": "39º BPM/M", "CIA": "2ª Cia - Artur Alvim"},
    "064 DP": {"BPM": "39º BPM/M", "CIA": "3ª Cia - Cidade A E Carvalho"},
    
    "067 DP": {"BPM": "48º BPM/M", "CIA": "1ª Cia - Jardim Robru"},
    "068 DP": {"BPM": "48º BPM/M", "CIA": "2ª Cia - Lajeado"},
    "103 DP": {"BPM": "48º BPM/M", "CIA": "3ª Cia - Cohab Itaquera"}
}

def formatar_indicador(nat):
    """
    Padroniza os nomes dos indicadores corrigindo problemas de encoding
    e mapeando para o nome oficial desejado no Dashboard.
    """
    if not isinstance(nat, str):
        return None
    
    nat_upper = nat.upper()
    
    if "FURTO - OUTROS" in nat_upper:
        return "FURTO OUTROS"
    if "FURTO DE VE" in nat_upper:
        return "FURTO VEÍCULO"
    if "ROUBO - OUTROS" in nat_upper:
        return "ROUBO OUTROS"
    if "ROUBO DE VE" in nat_upper:
        return "ROUBO VEÍCULO"
    if "ROUBO DE CARGA" in nat_upper:
        return "ROUBO DE CARGA"
    # Para homicídio doloso, evitar vítimas ou trânsito
    if "HOMIC" in nat_upper and "DOLOSO" in nat_upper:
        if "V" not in nat_upper and "TR" not in nat_upper: 
            return "HOMICÍDIO DOLOSO"
        
    return None

def limpar_dp(dp_str):
    if not isinstance(dp_str, str):
        return None
    
    match = re.search(r'^(\d{3})\s*DP', dp_str, re.IGNORECASE)
    if match:
        dp_number = match.group(1)
        return f"{dp_number} DP"
    return None

def map_mes(mes_val):
    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    if isinstance(mes_val, int) and 1 <= mes_val <= 12:
        return meses_pt[mes_val]
    elif isinstance(mes_val, str) and mes_val.isdigit():
        return meses_pt.get(int(mes_val), mes_val)
    return str(mes_val)

def run_etl():
    """
    Varre a pasta data/raw_drive, lê as planilhas criminais, 
    filtra as DPs e os indicadores e consolida tudo.
    """
    raw_dir = os.path.join("data", "raw_drive")
    if not os.path.exists(raw_dir):
        print(f"Diretório {raw_dir} não encontrado. ETL abortado.")
        return
    
    all_files = []
    for root, dirs, files in os.walk(raw_dir):
        for file in files:
            if "CRIMINAIS" in file.upper() and file.endswith((".xlsx", ".xls")):
                all_files.append(os.path.join(root, file))
                
    if not all_files:
        print("Nenhuma planilha de DADOS CRIMINAIS encontrada.")
        return

    print(f"Encontradas {len(all_files)} planilhas. Iniciando extração...")
    
    dfs_processados = []
    
    for f in all_files:
        try:
            df = pd.read_excel(f)
            
            col_nat = None
            if 'NATUREZA2' in df.columns:
                col_nat = 'NATUREZA2'
            elif 'AGRUPAMENTO_NATUREZA2' in df.columns:
                col_nat = 'AGRUPAMENTO_NATUREZA2'
            else:
                for c in df.columns:
                    if 'NATUREZA' in str(c).upper():
                        col_nat = c
                        break
            
            if not col_nat or 'DP' not in df.columns or 'MES' not in df.columns:
                print(f"Ignorando {os.path.basename(f)} - Colunas esperadas não encontradas.")
                continue
                
            df['INDICADOR_CLEAN'] = df[col_nat].apply(formatar_indicador)
            df['DP_CLEAN'] = df['DP'].apply(limpar_dp)
            
            df_filtered = df.dropna(subset=['INDICADOR_CLEAN', 'DP_CLEAN'])
            df_filtered = df_filtered[df_filtered['DP_CLEAN'].isin(DPS_CPAM4)]
            
            if df_filtered.empty:
                continue
                
            year_cols = []
            for col in df.columns:
                try:
                    if int(col) > 2000 and int(col) < 2050:
                        year_cols.append(col)
                except ValueError:
                    pass
            
            if not year_cols:
                continue
                
            df_melted = pd.melt(
                df_filtered, 
                id_vars=['DP_CLEAN', 'INDICADOR_CLEAN', 'MES'], 
                value_vars=year_cols,
                var_name='ANO', 
                value_name='QUANTIDADE'
            )
            
            df_melted['ANO'] = df_melted['ANO'].astype(int)
            df_melted['QUANTIDADE'] = pd.to_numeric(df_melted['QUANTIDADE'], errors='coerce').fillna(0).astype(int)
            df_melted['MES_NOME'] = df_melted['MES'].apply(map_mes)
            df_melted['MES_INT'] = df_melted['MES'].astype(int)
            
            # Aplicar o mapeamento Militar
            df_melted['BATALHAO'] = df_melted['DP_CLEAN'].apply(lambda x: MAP_MILITAR.get(x, {}).get("BPM", "Desconhecido"))
            df_melted['CIA'] = df_melted['DP_CLEAN'].apply(lambda x: MAP_MILITAR.get(x, {}).get("CIA", "Desconhecido"))
            
            df_final = df_melted[['BATALHAO', 'CIA', 'INDICADOR_CLEAN', 'ANO', 'MES_NOME', 'MES_INT', 'QUANTIDADE']].rename(
                columns={'INDICADOR_CLEAN': 'INDICADOR', 'MES_NOME': 'MES'}
            )
            
            dfs_processados.append(df_final)
            print(f"OK: {os.path.basename(f)}")
            
        except Exception as e:
            print(f"Erro ao processar {f}: {e}")

    if dfs_processados:
        df_consolidado = pd.concat(dfs_processados, ignore_index=True)
        
        df_consolidado = df_consolidado.groupby(
            ['BATALHAO', 'CIA', 'INDICADOR', 'ANO', 'MES', 'MES_INT']
        )['QUANTIDADE'].max().reset_index()
        
        df_consolidado = df_consolidado.sort_values(['ANO', 'MES_INT', 'BATALHAO', 'CIA'])
        
        # Manter MES_INT para podermos ordenar facilmente e descobrir o mais recente
        # Salvar o CSV final com MES_INT
        out_path = os.path.join("data", "dados_tratados.csv")
        df_consolidado.to_csv(out_path, index=False, encoding='utf-8')
        print(f"SUCESSO! ETL concluído. Dados consolidados salvos em: {out_path}")
    else:
        print("Aviso: Nenhum dado válido foi processado.")

if __name__ == "__main__":
    run_etl()
