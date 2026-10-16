"""O save do jogo: moedas, roupas compradas, roupa que cada um está usando e recordes.
Fica num arquivo battlewish_save.json do lado do .exe (ou deste arquivo, rodando pelo Python)."""
import json
import os
import sys


def pasta_do_jogo():
    """A pasta onde está o .exe (ou este arquivo, rodando pelo Python)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def arquivo():
    return os.environ.get("BW_SAVE") or os.path.join(pasta_do_jogo(), "battlewish_save.json")


NOVO = {"moedas": 0, "roupas": {}, "usando": {}, "recorde_sobrevivencia": 0, "desafios": [], "desafios_feitos": 0, "codigos": []}
dados = None


def carregar():
    global dados
    dados = json.loads(json.dumps(NOVO))
    try:
        with open(arquivo(), encoding="utf-8") as arq:
            lido = json.load(arq)
        if isinstance(lido, dict):
            dados.update({k: v for k, v in lido.items() if k in NOVO})
    except (OSError, ValueError):
        pass  # primeira vez jogando (ou arquivo estragado): começa do zero
    return dados


def d():
    return dados if dados is not None else carregar()


def salvar():
    try:
        with open(arquivo(), "w", encoding="utf-8") as arq:
            json.dump(d(), arq, ensure_ascii=False, indent=1)
    except OSError:
        pass  # não deu pra gravar (pasta protegida): o jogo continua mesmo assim


def moedas():
    return d()["moedas"]


def ganhar(n):
    d()["moedas"] = max(0, d()["moedas"] + int(n))
    salvar()


def tem_roupa(nome, roupa):
    return roupa == "padrao" or roupa in d()["roupas"].get(nome, [])


def comprar(nome, roupa, preco):
    """Compra a roupa se tiver moedas. Devolve True se comprou."""
    if tem_roupa(nome, roupa):
        return True
    if d()["moedas"] < preco:
        return False
    d()["moedas"] -= preco
    d()["roupas"].setdefault(nome, []).append(roupa)
    salvar()
    return True


def usando(nome):
    r = d()["usando"].get(nome, "padrao")
    return r if tem_roupa(nome, r) else "padrao"


def usar(nome, roupa):
    if tem_roupa(nome, roupa):
        d()["usando"][nome] = roupa
        salvar()


def recorde():
    return d()["recorde_sobrevivencia"]


def novo_recorde(n):
    """Guarda o recorde da Sobrevivência. Devolve True se bateu o recorde."""
    if n > d()["recorde_sobrevivencia"]:
        d()["recorde_sobrevivencia"] = n
        salvar()
        return True
    return False
