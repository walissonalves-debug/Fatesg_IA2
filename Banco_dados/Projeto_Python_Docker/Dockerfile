# 1. Começamos com uma imagem base do Python
FROM python:3.9-slim

# 2. Definimos a pasta onde tudo vai acontecer dentro do container
WORKDIR /app

# 3. Copiamos o arquivo de dependências para dentro do container
COPY requirements.txt .

# 4. Instalamos as bibliotecas listadas
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos o restante do nosso código
COPY . .

# 6. Informamos que a porta 5000 será usada
EXPOSE 5000

# 7. Comando para iniciar a aplicação
CMD ["python", "app.py"]