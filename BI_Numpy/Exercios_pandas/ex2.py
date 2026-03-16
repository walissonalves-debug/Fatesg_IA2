import pandas as pd

# 1. Criando a lista com cinco frutas
lista_frutas = ['Maçã', 'Banana', 'Laranja', 'Morango', 'Uva']

# 2. Convertendo a lista em uma Series do Pandas
series_frutas = pd.Series(lista_frutas)

# 3. Exibindo o resultado
print("Series de Frutas:")
print(series_frutas)