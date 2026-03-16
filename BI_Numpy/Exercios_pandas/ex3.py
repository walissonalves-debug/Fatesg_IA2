import pandas as pd
import numpy as np

# 1. Criando o array Numpy com os valores desejados
dados = np.array([10, 20, 30, 40])

# 2. Criando a Series com índices personalizados ('A', 'B', 'C', 'D')
series_personalizada = pd.Series(dados, index=['A', 'B', 'C', 'D'])

# 3. Imprimindo a Series resultante
print("Series com índices personalizados:")
print(series_personalizada)