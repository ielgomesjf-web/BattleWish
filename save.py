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


NOVO = {"moedas": 0, "roupas": {}, "usando": {}, "recorde_sobrevivencia": 0, "desafios": [], "desafios_feitos": 0, "codigos": [],
        "combos": {}, "regras": [], "maestria": {},              # desafios de combo feitos, MODOS MALUCOS ligados, MAESTRIA
        "estatisticas": {}, "missoes": {}, "trofeus": [],        # PERFIL (estatísticas e troféus) e MISSÕES DO DIA
        "rivais": {}, "passivas": {}, "rei_arena": {},
        "extras": {}, "extras_usando": {},                       # LOJA NOVA: entradas, vitórias e provocações
        "doces": 0, "doces_ano": 0, "passe": {}, "album": {},    # EVENTOS: doces, PASSE DO EVENTO e o ÁLBUM de figurinhas
        "favorito": None,                                        # o LUTADOR FAVORITO (escolhido no perfil; luta no menu)
        "natal": {},                                             # NATAL: as meias de cada cenário e o GORRINHO
        "vol_musica": 100, "vol_efeitos": 100, "vibrar": True}  # CONFIGURAÇÕES
# (só as chaves daqui são lidas do arquivo: coisa nova no save TEM que entrar aqui, senão some ao fechar o jogo)
dados = None


NOMES_TROCADOS = {"XENOMORPH": "TROMOS"}  # lutador que mudou de nome: o save antigo passa pro nome novo


def _renomear(v):
    """Troca o nome antigo pelo novo em tudo do save (chaves e textos), pra ninguém perder roupa, maestria..."""
    if isinstance(v, str):
        for velho, novo in NOMES_TROCADOS.items():
            v = v.replace(velho, novo)
        return v
    if isinstance(v, list):
        return [_renomear(x) for x in v]
    if isinstance(v, dict):
        return {_renomear(k): _renomear(x) for k, x in v.items()}
    return v


def _tipo_certo(valor, padrao):
    """Só aceita do arquivo o que tem o tipo certo (um null ou texto no lugar do volume não quebra o jogo)."""
    if padrao is None:  # (padrão vazio, tipo "favorito": aceita um nome ou nada)
        return valor is None or isinstance(valor, str)
    if isinstance(padrao, bool) or isinstance(valor, bool):
        return isinstance(valor, bool) and isinstance(padrao, bool)
    if isinstance(padrao, (int, float)):
        return isinstance(valor, (int, float))
    return isinstance(valor, type(padrao))


def carregar():
    global dados
    dados = json.loads(json.dumps(NOVO))
    try:
        with open(arquivo(), encoding="utf-8") as arq:
            lido = json.load(arq)
        if isinstance(lido, dict):
            dados.update({k: _renomear(v) for k, v in lido.items() if k in NOVO and _tipo_certo(v, NOVO[k])})
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
    return roupa == "padrao" or roupa in d()["roupas"].get(nome, []) or _do_passe(nome, roupa)


def _do_passe(nome, roupa):
    """Skin de EVENTO: é dele se ganhou no PASSE DO EVENTO (fica pra sempre).
    HOLOGRÁFICA: é dele se completou a página do lutador no ÁLBUM."""
    import roupas
    r = next((r for r in roupas.ROUPAS.get(nome, []) if r["id"] == roupa), None)
    if r and r.get("album"):
        import figurinhas
        return nome in figurinhas.holograficas()
    if not r or not r.get("evento"):
        return False
    import passe
    return passe.tem(nome, "skin", r["evento"].upper())


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
