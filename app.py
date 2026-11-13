import os

from flask import Flask, jsonify, request

app = Flask(__name__)


def feature_desconto_ativa():
    """Feature Flag lida a cada requisição (permite alternar sem novo deploy)."""
    return os.getenv("FEATURE_DESCONTO_PROMO", "false").strip().lower() == "true"


def _ler_numeros():
    a = request.args.get("a")
    b = request.args.get("b")
    if a is None or b is None:
        return None, None, "Parâmetros 'a' e 'b' são obrigatórios"
    try:
        return float(a), float(b), None
    except ValueError:
        return None, None, "Parâmetros 'a' e 'b' devem ser numéricos"


def _operacao(nome, funcao):
    a, b, erro = _ler_numeros()
    if erro:
        return jsonify({"erro": erro}), 400
    resultado, erro = funcao(a, b)
    if erro:
        return jsonify({"erro": erro}), 400
    if resultado == int(resultado):
        resultado = int(resultado)
    return jsonify({"operacao": nome, "resultado": resultado})


@app.route("/api/status")
def status():
    return jsonify(
        {
            "status": "ok",
            "servico": "FastOrder API",
            "feature_desconto_promo": feature_desconto_ativa(),
        }
    )


@app.route("/api/soma")
def soma():
    return _operacao("soma", lambda a, b: (a + b, None))


@app.route("/api/subtracao")
def subtracao():
    return _operacao("subtracao", lambda a, b: (a - b, None))


@app.route("/api/multiplicacao")
def multiplicacao():
    return _operacao("multiplicacao", lambda a, b: (a * b, None))


@app.route("/api/divisao")
def divisao():
    return _operacao(
        "divisao",
        lambda a, b: (None, "Divisão por zero não é permitida") if b == 0 else (a / b, None),
    )


@app.route("/api/desconto")
def desconto():
    # Dark launch: a rota existe no deploy, mas só responde se a flag estiver ligada
    if not feature_desconto_ativa():
        return jsonify({"erro": "Funcionalidade indisponível"}), 404

    try:
        valor = float(request.args.get("valor", ""))
        percentual = float(request.args.get("percentual", ""))
    except ValueError:
        return jsonify({"erro": "Parâmetros 'valor' e 'percentual' devem ser numéricos"}), 400

    if valor < 0 or not 0 <= percentual <= 100:
        return jsonify({"erro": "Valor deve ser >= 0 e percentual entre 0 e 100"}), 400

    valor_desconto = round(valor * percentual / 100, 2)
    return jsonify(
        {
            "valor_original": valor,
            "percentual": percentual,
            "desconto": valor_desconto,
            "valor_final": round(valor - valor_desconto, 2),
        }
    )


if __name__ == "__main__":
    # Correção do Bandit (B201/B104): debug e host controlados por ambiente,
    # com padrões seguros (debug desligado, somente localhost).
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
