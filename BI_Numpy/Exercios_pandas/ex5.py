import pandas as pd

# Sintaxe completa do construtor DataFrame
df = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)

# Criando um DataFrame básico usando os parâmetros estudados
dados = [[100, 'Norte'], [200, 'Sul']]
colunas = ['Vendas', 'Regiao']
indices = ['Loja A', 'Loja B']

df_bi = pd.DataFrame(data=dados, index=indices, columns=colunas)

print(df_bi)