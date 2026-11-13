import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_status_ok(client):
    r = client.get("/api/status")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_soma(client):
    assert client.get("/api/soma?a=5&b=7").get_json()["resultado"] == 12


def test_soma_decimais(client):
    assert client.get("/api/soma?a=1.5&b=2.5").get_json()["resultado"] == 4


def test_soma_negativos(client):
    assert client.get("/api/soma?a=-3&b=3").get_json()["resultado"] == 0


def test_soma_parametro_ausente(client):
    assert client.get("/api/soma?a=5").status_code == 400


def test_soma_parametro_invalido(client):
    assert client.get("/api/soma?a=x&b=2").status_code == 400


def test_subtracao(client):
    assert client.get("/api/subtracao?a=10&b=4").get_json()["resultado"] == 6


def test_multiplicacao(client):
    assert client.get("/api/multiplicacao?a=3&b=4").get_json()["resultado"] == 12


def test_divisao(client):
    assert client.get("/api/divisao?a=10&b=4").get_json()["resultado"] == 2.5


def test_divisao_por_zero(client):
    assert client.get("/api/divisao?a=1&b=0").status_code == 400


# ---- Feature Flag: FEATURE_DESCONTO_PROMO ----

def test_desconto_ativado(client, monkeypatch):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "true")
    r = client.get("/api/desconto?valor=200&percentual=10")
    assert r.status_code == 200
    dados = r.get_json()
    assert dados["desconto"] == 20
    assert dados["valor_final"] == 180


def test_desconto_desativado(client, monkeypatch):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "false")
    r = client.get("/api/desconto?valor=200&percentual=10")
    assert r.status_code == 404


def test_desconto_desativado_por_padrao(client, monkeypatch):
    monkeypatch.delenv("FEATURE_DESCONTO_PROMO", raising=False)
    assert client.get("/api/desconto?valor=200&percentual=10").status_code == 404


def test_desconto_parametros_invalidos(client, monkeypatch):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "true")
    assert client.get("/api/desconto?valor=abc&percentual=10").status_code == 400
    assert client.get("/api/desconto?valor=100&percentual=150").status_code == 400


def test_status_reflete_flag(client, monkeypatch):
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "true")
    assert client.get("/api/status").get_json()["feature_desconto_promo"] is True
    monkeypatch.setenv("FEATURE_DESCONTO_PROMO", "false")
    assert client.get("/api/status").get_json()["feature_desconto_promo"] is False
