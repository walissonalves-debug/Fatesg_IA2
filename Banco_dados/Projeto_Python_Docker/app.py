# ============================================================
# API simples com Flask: soma de dois números via URL (GET)
# Exemplo de uso:
#   http://localhost:5000/soma?a=10&b=20
# Resposta:
#   {"resultado": 30.0}
# ============================================================

from flask import Flask, request, jsonify
# Flask   -> cria a aplicação web (o "servidor" que recebe requisições)
# request -> representa a requisição que chegou (dados da URL, headers, corpo etc.)
# jsonify -> ajuda a devolver respostas em JSON (padrão de APIs)

# ------------------------------------------------------------
# 1) Criando a aplicação
# ------------------------------------------------------------
app = Flask(__name__)
# Flask(__name__) cria a aplicação.
# __name__ é uma variável especial do Python:
# - quando este arquivo é executado diretamente, __name__ vale "__main__"
# - o Flask usa isso para saber onde está o app e localizar recursos.

# ------------------------------------------------------------
# 2) Criando uma rota/endpoint
# ------------------------------------------------------------
@app.route("/funcaoexponencial", methods=["GET"])
# @app.route(...) é um "decorator" (uma forma de configurar a função abaixo)
# Ele diz: "quando alguém acessar /soma usando o método GET,
# execute a função soma()".
#
# "/soma" -> caminho da URL
# methods=["GET"] -> diz quais métodos HTTP esse endpoint aceita.
# GET é usado quando queremos "buscar" algo, sem enviar corpo (normalmente).

def funcaoexponencial():
    # Essa função roda quando alguém chama: /soma?a=...&b=...

    try:
        # ------------------------------------------------------------
        # 3) Lendo parâmetros da URL (query string)
        # ------------------------------------------------------------

        # request.args -> é um "dicionário" (tipo um mapa/chave-valor)
        # com os parâmetros que vêm na URL depois do "?".
        #
        # Exemplo:
        # /soma?a=10&b=20
        # request.args terá algo como:
        # {"a": "10", "b": "20"}

        # request.args.get("a", 0)
        # - "a" é o nome do parâmetro que queremos pegar
        # - 0 é o valor padrão (default) se "a" não existir na URL
        #
        # Por que usar default 0?
        # - Se o aluno chamar /soma sem "a", não dá erro, assume 0.
        # - Ex.: /soma?b=5 -> a vira 0, b vira 5, resultado 5.

        a_str = request.args.get("a", "0")
        # Aqui a gente pega "a" como texto (string).
        # Observação: parâmetros da URL sempre chegam como texto.

        b_str = request.args.get("b", "0")
        # Mesma coisa para "b".

        # ------------------------------------------------------------
        # 4) Convertendo texto para número
        # ------------------------------------------------------------
        # float(...) converte string para número decimal (ex.: "10" -> 10.0)
        # Se vier algo errado (ex.: "abc"), o float vai dar erro.
        a = float(a_str)
        b = float(b_str)

        # ------------------------------------------------------------
        # 5) Retornando resposta em JSON
        # ------------------------------------------------------------
        # jsonify(...) transforma o dicionário em JSON e já define o
        # content-type correto (application/json).
        return jsonify({"resultado": a ** b})

    except Exception as e:
        # ------------------------------------------------------------
        # 6) Tratando erro
        # ------------------------------------------------------------
        # "Exception" é um tipo genérico de erro.
        # "as e" significa: "guarde esse erro dentro da variável e"
        # Assim conseguimos mostrar a mensagem do erro para entender o que ocorreu.
        #
        # Exemplo: se a=abc, float("abc") dá erro.
        # A mensagem pode ser algo como "could not convert string to float: 'abc'"

        return jsonify({"erro": str(e)}), 400
        # Aqui devolvemos:
        # - um JSON com a mensagem do erro
        # - e o código HTTP 400 (Bad Request), que significa:
        #   "a requisição do cliente veio com dados inválidos"

# ------------------------------------------------------------
# 7) Rodando o servidor
# ------------------------------------------------------------
if __name__ == "__main__":
    # Esse bloco só roda quando você executa este arquivo diretamente:
    # python app.py
    #
    # Se esse arquivo for importado por outro (ex.: via gunicorn),
    # esse trecho não roda.

    app.run(host="0.0.0.0", port=5000)
    # host="0.0.0.0" -> significa "aceitar conexões de qualquer lugar".
    # Isso é essencial quando está em Docker, senão só acessa de dentro.
    #
    # port=5000 -> porta onde o Flask vai escutar.