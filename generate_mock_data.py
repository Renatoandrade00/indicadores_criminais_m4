import pandas as pd
import numpy as np
import os

dps = [
    "022 DP - São Miguel Paulista", "024 DP - Ponte Rasa", "032 DP - Itaquera",
    "050 DP - Itaim Paulista", "059 DP - Jardim Noemia", "062 DP - Ermelino Matarazzo",
    "063 DP - Vila Jacuí", "064 DP - Cidade A E Carvalho", "065 DP - Artur Alvim",
    "067 DP - Jardim Robru", "068 DP - Lajeado", "103 DP - Cohab Itaquera"
]

indicadores = [
    "FURTO OUTROS", "FURTO VEÍCULO", "ROUBO OUTROS", 
    "ROUBO VEÍCULO", "ROUBO DE CARGA", "HOMICÍDIO DOLOSO"
]

meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho"]
anos = [2023, 2024]

data = []

np.random.seed(42)

for dp in dps:
    for ind in indicadores:
        for ano in anos:
            for mes in meses:
                valor = np.random.randint(0, 50)
                if ind == "HOMICÍDIO DOLOSO":
                    valor = np.random.randint(0, 5) # Homicídios são mais baixos
                
                data.append({
                    "DELEGACIA": dp,
                    "INDICADOR": ind,
                    "ANO": ano,
                    "MES": mes,
                    "QUANTIDADE": valor
                })

df = pd.DataFrame(data)

os.makedirs("data", exist_ok=True)
df.to_csv("data/mock_criminais.csv", index=False)
print("Dados mockados gerados em data/mock_criminais.csv")
