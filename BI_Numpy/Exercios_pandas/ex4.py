import pandas as pd

# 1. Criando o dicionário original
dados_vendas = {'jan': 100, 'fev': 200}

# 2. Criando a Series e forçando um índice que inclui 'mar' (que não está no dicionário)
series_vendas = pd.Series(dados_vendas, index=['jan', 'fev', 'mar'])

# 3. Imprimindo o resultado
print("Series com dados de vendas:")
print(series_vendas)