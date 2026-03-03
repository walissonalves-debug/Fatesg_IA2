# 1) Escolhe a imagem base do container
# - "python:3.11-slim" já vem com o Python 3.11 instalado
# - "slim" = versão mais leve (menos pacotes), imagem menor e download mais rápido
FROM python:3.11-slim


# 2) Define a pasta "padrão" dentro do container onde vamos trabalhar
# - É como dar "cd /app" e deixar isso fixo para os próximos comandos
# - Tudo que vier depois (COPY, RUN, CMD) será executado relativo a /app
WORKDIR /app


# 3) Copia o arquivo requirements.txt do seu PC (host) para dentro do container
# - Origem: requirements.txt (na mesma pasta do Dockerfile)
# - Destino: /app/requirements.txt (por causa do WORKDIR)
COPY requirements.txt .


# 4) Instala as dependências do Python dentro do container
# - pip install -r requirements.txt instala tudo que sua aplicação precisa (Flask, etc.)
# - --no-cache-dir evita guardar cache do pip, deixando a imagem menor
RUN pip install --no-cache-dir -r requirements.txt


# 5) Copia o seu código para dentro do container
# - app.py do seu computador vai para /app/app.py dentro do container
COPY app.py .


# 6) Informa que o container "usa" a porta 5000
# - Importante: EXPOSE NÃO abre a porta para fora sozinho
# - Ele serve como documentação e ajuda ferramentas (ex.: compose) a entenderem a intenção
EXPOSE 5000


# 7) Comando padrão que roda quando o container inicia
# - Ao dar "docker run ..." (ou docker compose up), ele executa:
#   python app.py
# - Forma em lista (JSON) evita problemas com aspas e shell
CMD ["python", "app.py"]
