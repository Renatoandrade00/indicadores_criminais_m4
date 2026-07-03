import pandas as pd
import os
import glob
import re

# Constantes de filtro
DPS_CPAM4 = [
    "022 DP", "024 DP", "032 DP", "050 DP", "059 DP", "062 DP", 
    "063 DP", "064 DP", "065 DP", "067 DP", "068 DP", "103 DP"
]

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
        if "V" not in nat_upper and "TR" not in nat_upper: # Evitar 'N DE VTIMAS' e 'TRNSITO'
            return "HOMICÍDIO DOLOSO"
        
    return None

def limpar_dp(dp_str):
    if not isinstance(dp_str, str):
        return None
    
    # Exemplo: "022 DP - São Miguel Paulista" -> "022 DP - São Miguel Paulista"
    # Se houver erro de encoding como "So Miguel", o regex a seguir pega os 3 digitos e a sigla
    match = re.search(r'^(\d{3})\s*DP', dp_str, re.IGNORECASE)
    if match:
        dp_number = match.group(1)
        # Retorna apenas o prefixo "022 DP" para facilitar o filtro e padronização
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
    
    # Encontrar todos os excels de DADOS CRIMINAIS iterando pelas subpastas
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
            
            # Localizar coluna de Natureza e DP
            col_nat = None
            if 'NATUREZA2' in df.columns:
                col_nat = 'NATUREZA2'
            elif 'AGRUPAMENTO_NATUREZA2' in df.columns:
                col_nat = 'AGRUPAMENTO_NATUREZA2'
            else:
                # Fallback, tenta achar alguma coluna que tenha 'NATUREZA'
                for c in df.columns:
                    if 'NATUREZA' in str(c).upper():
                        col_nat = c
                        break
            
            if not col_nat or 'DP' not in df.columns or 'MES' not in df.columns:
                print(f"Ignorando {os.path.basename(f)} - Colunas esperadas não encontradas.")
                continue
                
            # Padronizar nomes
            df['INDICADOR_CLEAN'] = df[col_nat].apply(formatar_indicador)
            df['DP_CLEAN'] = df['DP'].apply(limpar_dp)
            
            # Filtrar dados (apenas indicadores desejados e DPs do CPA/M-4)
            df_filtered = df.dropna(subset=['INDICADOR_CLEAN', 'DP_CLEAN'])
            df_filtered = df_filtered[df_filtered['DP_CLEAN'].isin(DPS_CPAM4)]
            
            if df_filtered.empty:
                continue
                
            # Descobrir quais são as colunas de Ano (normalmente são inteiros como 2022, 2023)
            # ou strings que representam anos ('2023', '2024')
            year_cols = []
            for col in df.columns:
                try:
                    if int(col) > 2000 and int(col) < 2050:
                        year_cols.append(col)
                except ValueError:
                    pass
            
            if not year_cols:
                continue
                
            # Melt para transformar as colunas de ano em linhas
            df_melted = pd.melt(
                df_filtered, 
                id_vars=['DP_CLEAN', 'INDICADOR_CLEAN', 'MES'], 
                value_vars=year_cols,
                var_name='ANO', 
                value_name='QUANTIDADE'
            )
            
            # Limpar e formatar o resultado
            df_melted['ANO'] = df_melted['ANO'].astype(int)
            df_melted['QUANTIDADE'] = pd.to_numeric(df_melted['QUANTIDADE'], errors='coerce').fillna(0).astype(int)
            df_melted['MES_NOME'] = df_melted['MES'].apply(map_mes)
            df_melted['MES_INT'] = df_melted['MES'].astype(int)
            
            # Renomear as colunas finais
            df_final = df_melted[['DP_CLEAN', 'INDICADOR_CLEAN', 'ANO', 'MES_NOME', 'MES_INT', 'QUANTIDADE']].rename(
                columns={'DP_CLEAN': 'DELEGACIA', 'INDICADOR_CLEAN': 'INDICADOR', 'MES_NOME': 'MES'}
            )
            
            dfs_processados.append(df_final)
            print(f"OK: {os.path.basename(f)}")
            
        except Exception as e:
            print(f"Erro ao processar {f}: {e}")

    if dfs_processados:
        # Concatenar todos os resultados
        df_consolidado = pd.concat(dfs_processados, ignore_index=True)
        
        # Como arquivos diferentes de anos diferentes podem trazer a mesma coluna de ano 
        # (ex: a planilha de 2024 traz 2023 e 2024. A de 2023 traz 2022 e 2023), pode haver duplicação.
        # Vamos agrupar (ou remover duplicatas mantendo o valor máximo/mais recente).
        # Agruparemos pela chave e manteremos o maior valor (geralmente atualizações consolidam para cima)
        df_consolidado = df_consolidado.groupby(
            ['DELEGACIA', 'INDICADOR', 'ANO', 'MES', 'MES_INT']
        )['QUANTIDADE'].max().reset_index()
        
        # Ordenar por Ano, Mês, Delegacia
        df_consolidado = df_consolidado.sort_values(['ANO', 'MES_INT', 'DELEGACIA'])
        
        # Remover a coluna de controle numérico de mês
        df_consolidado = df_consolidado.drop(columns=['MES_INT'])
        
        # Mapeamento do nome completo da DP para exibição bonita (Opcional, já que filtramos)
        dps_full_name = {
            "022 DP": "022 DP - São Miguel Paulista",
            "024 DP": "024 DP - Ponte Rasa",
            "032 DP": "032 DP - Itaquera",
            "050 DP": "050 DP - Itaim Paulista",
            "059 DP": "059 DP - Jardim Noemia",
            "062 DP": "062 DP - Ermelino Matarazzo",
            "063 DP": "063 DP - Vila Jacuí",
            "064 DP": "064 DP - Cidade A E Carvalho",
            "065 DP": "065 DP - Artur Alvim",
            "067 DP": "067 DP - Jardim Robru",
            "068 DP": "068 DP - Lajeado",
            "103 DP": "103 DP - Cohab Itaquera"
        }
        df_consolidado['DELEGACIA'] = df_consolidado['DELEGACIA'].map(dps_full_name)
        
        # Salvar o CSV final
        out_path = os.path.join("data", "dados_tratados.csv")
        df_consolidado.to_csv(out_path, index=False, encoding='utf-8')
        print(f"SUCESSO! ETL concluído. Dados consolidados salvos em: {out_path}")
    else:
        print("Aviso: Nenhum dado válido foi processado.")

if __name__ == "__main__":
    run_etl()
