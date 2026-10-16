"""Roupas alternativas (compradas com as moedas do jogo).
Cada roupa troca cores da paleta do personagem: {letra da paleta: cor nova}.
Roupa com codigo="..." não se compra: só aparece com o código certo na tela de CÓDIGOS."""
import chapeus_ribbat
import save

ROUPAS = {
    "MAX-10": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="prata", nome="PRATA", preco=100, cor=(170, 174, 184), troca={
            "G": (236, 238, 244), "g": (184, 188, 198), "d": (126, 130, 142), "D": (78, 82, 94), "r": (60, 200, 255),
            "R": (200, 240, 255)}),
        dict(id="carmesim", nome="CARMESIM", preco=200, cor=(170, 40, 40), troca={
            "G": (236, 110, 100), "g": (190, 54, 50), "d": (130, 30, 32), "D": (80, 16, 20), "S": (60, 60, 66),
            "s": (40, 40, 46), "m": (24, 24, 28), "r": (255, 220, 60), "R": (255, 250, 200)}),
        dict(id="wartank", nome="WARTANK", preco=0, codigo="IRONMAN", cor=(200, 40, 36), troca={
            "G": (232, 64, 52), "g": (186, 34, 32), "d": (134, 20, 22), "D": (86, 10, 14),
            "S": (252, 216, 96), "s": (214, 168, 52), "m": (150, 108, 30),
            "r": (190, 246, 255), "R": (255, 255, 255), "w": (150, 236, 255), "b": (110, 220, 255),
            "y": (220, 250, 255)}),
    ],
    "RIB": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="venenoso", nome="SAPO VENENOSO", preco=100, cor=(40, 120, 220), troca={
            "G": (120, 200, 255), "g": (40, 130, 230), "d": (24, 80, 170), "D": (14, 44, 110), "c": (40, 40, 50),
            "C": (24, 24, 32), "y": (255, 120, 40), "Y": (255, 220, 170)}),
        dict(id="deserto", nome="SAPO DO DESERTO", preco=200, cor=(210, 140, 60), troca={
            "G": (250, 206, 130), "g": (214, 150, 70), "d": (160, 100, 44), "D": (104, 62, 26), "n": (110, 60, 40),
            "N": (150, 92, 60), "x": (210, 190, 150), "X": (240, 226, 190)}),
        dict(id="greninja", nome="GRENINJA", preco=0, codigo="FIGHTMON", cor=(40, 70, 170), troca={
            "G": (96, 150, 232), "g": (52, 100, 196), "d": (30, 64, 146), "D": (18, 38, 96),
            "c": (196, 232, 250), "C": (140, 190, 226), "n": (28, 36, 86), "N": (48, 62, 128),
            "x": (236, 96, 160), "X": (255, 170, 210), "s": (52, 76, 150), "m": (26, 40, 92),
            "b": (52, 76, 150), "B": (30, 46, 104), "t": (24, 30, 70)}),
    ],
    "TRAFO": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="lobo", nome="LOBO CINZA", preco=100, cor=(140, 140, 150), troca={
            "G": (210, 212, 220), "g": (150, 152, 162), "d": (104, 106, 116), "D": (66, 68, 78), "h": (80, 82, 92),
            "r": (60, 170, 255), "L": (150, 152, 162)}),
        dict(id="chocolate", nome="CHOCOLATE", preco=200, cor=(110, 70, 40), troca={
            "G": (170, 116, 70), "g": (120, 78, 42), "d": (84, 52, 26), "D": (54, 32, 14), "h": (40, 24, 10),
            "c": (230, 200, 160), "C": (190, 156, 116), "L": (120, 78, 42)}),
        dict(id="indoraptor", nome="INDORAPTOR", preco=0, codigo="DINOWOLF", cor=(40, 40, 46), troca={
            "G": (78, 78, 88), "g": (50, 50, 58), "d": (34, 34, 40), "D": (20, 20, 24),
            "h": (50, 50, 58), "L": (240, 176, 40), "c": (104, 104, 114), "C": (78, 78, 88), "r": (255, 200, 30)}),
    ],
    "KING RIP": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="vermelho", nome="MESTRE VERMELHO", preco=100, cor=(180, 50, 50), troca={
            "B": (236, 110, 100), "b": (180, 46, 44), "v": (110, 22, 26)}),
        dict(id="negro", nome="MESTRE DA NOITE", preco=200, cor=(40, 40, 50), troca={
            "B": (90, 90, 104), "b": (46, 46, 56), "v": (26, 26, 32), "x": (230, 230, 236), "X": (255, 255, 255)}),
    ],
    "CANNAN": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="deserto", nome="FARDA DO DESERTO", preco=100, cor=(190, 160, 110), troca={
            "o": (176, 146, 100), "O": (210, 182, 136), "x": (110, 88, 60), "X": (150, 124, 90)}),
        dict(id="artico", nome="FARDA DO ÁRTICO", preco=200, cor=(220, 224, 230), troca={
            "o": (214, 218, 226), "O": (244, 246, 250), "x": (70, 76, 90), "X": (110, 118, 134), "g": (255, 120, 60)}),
        dict(id="megacannon", nome="MEGA-CANNON", preco=0, codigo="MEGACANNON", cor=(40, 140, 240), troca={
            "o": (60, 170, 250), "O": (120, 210, 255), "x": (10, 80, 200), "X": (30, 120, 236),
            "h": (10, 80, 200), "H": (30, 120, 236), "b": (10, 60, 160),
            "c": (60, 170, 250), "C": (150, 224, 255), "m": (10, 80, 200), "g": (255, 236, 110)}),
    ],
    "FINN": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="branco", nome="MAGO BRANCO", preco=100, cor=(220, 220, 228), troca={
            "R": (250, 250, 255), "r": (214, 216, 226), "v": (150, 154, 170), "x": (120, 124, 140),
            "X": (170, 174, 190), "a": (200, 170, 70), "A": (240, 214, 120), "b": (200, 200, 210), "B": (150, 150, 164)}),
        dict(id="fogo", nome="MAGO DO FOGO", preco=200, cor=(180, 50, 30), troca={
            "R": (236, 110, 60), "r": (180, 50, 30), "v": (110, 24, 16), "a": (40, 34, 40), "A": (80, 70, 80),
            "b": (150, 40, 24), "B": (100, 24, 14), "o": (255, 200, 60)}),
    ],
    "KUN": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="ouros", nome="ÁS DE OUROS", preco=100, cor=(220, 180, 60), troca={
            "R": (250, 220, 110), "r": (214, 170, 50), "v": (150, 110, 24), "e": (210, 40, 40)}),
        dict(id="coringa", nome="CORINGA", preco=200, cor=(110, 50, 150), troca={  # (o Gomes pediu: mais Coringa)
            "R": (160, 90, 210), "r": (116, 52, 160), "v": (70, 28, 104),         # terno roxo
            "c": (104, 46, 146), "C": (140, 80, 186),                             # calça roxa
            "w": (240, 140, 40), "e": (60, 150, 70),                              # camisa laranja e colete verde
            "h": (60, 160, 70), "H": (120, 210, 110),                             # cabelo verde
            "p": (242, 242, 236), "P": (214, 214, 210), "q": (176, 176, 172),     # cara branca
            "b": (210, 20, 40), "B": (210, 20, 40),                               # o sorrisão vermelho
            "s": (120, 72, 40), "S": (84, 48, 24)}),                              # sapatos marrons
    ],
    "XENOMORPH": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="albino", nome="XENO ALBINO", preco=100, cor=(200, 200, 206), troca={
            "b": (150, 150, 158), "x": (196, 196, 204), "X": (230, 230, 236), "s": (255, 255, 255),
            "y": (230, 40, 40), "Y": (255, 160, 160)}),
        dict(id="fogo", nome="XENO DE FOGO", preco=200, cor=(140, 30, 20), troca={
            "b": (60, 10, 8), "x": (120, 24, 18), "X": (200, 60, 30), "s": (255, 150, 60),
            "y": (255, 255, 255), "Y": (255, 255, 255)}),
    ],
    "TAMER": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="noturno", nome="EXPLORADOR NOTURNO", preco=100, cor=(60, 80, 60), troca={
            "c": (70, 90, 66), "C": (100, 124, 92), "v": (44, 58, 42), "o": (40, 44, 40), "O": (66, 70, 64),
            "h": (50, 62, 46), "H": (80, 96, 72)}),
        dict(id="safari", nome="SAFÁRI", preco=200, cor=(230, 220, 190), troca={
            "c": (232, 222, 192), "C": (250, 244, 224), "v": (196, 180, 140), "o": (176, 150, 100),
            "O": (206, 182, 130), "h": (232, 222, 192), "H": (250, 244, 224)}),
        dict(id="zeus", nome="ZEUS (e o FENRIR)", preco=0, codigo="FENRIR", cor=(240, 240, 250), troca={
            "c": (238, 238, 246), "C": (255, 255, 255), "v": (190, 192, 210), "o": (226, 228, 238),
            "O": (250, 250, 255), "h": (214, 170, 56), "H": (252, 214, 100), "b": (190, 146, 44),
            "B": (240, 200, 90), "s": (200, 200, 210), "x": (214, 170, 56)},
             lobo=dict(olho=(255, 40, 30), tam=1.35)),  # Fenrir: olhos vermelhos e maior
    ],
    "TAI": [
        dict(id="padrao", nome="ORIGINAL", preco=0),
        dict(id="dourado", nome="MAWASHI DOURADO", preco=100, cor=(236, 190, 150), troca={
            "m": (210, 170, 50), "M": (250, 220, 110), "n": (150, 110, 24)}),
        dict(id="luchador", nome="SHREK", preco=200, cor=(140, 186, 70), troca={  # (era o Hawlucha; o Gomes pediu o Shrek)
            "p": (150, 190, 70), "P": (182, 214, 100), "q": (108, 146, 48), "h": (150, 190, 70), "e": (40, 30, 20),
            "z": None, "y": None,
            "a": (226, 214, 176), "A": (244, 236, 208), "Q": (186, 172, 132),
            "v": (112, 76, 42), "V": (142, 102, 58), "w": (80, 52, 26), "x": (150, 120, 80),
            "i": (160, 128, 84), "I": (186, 154, 106), "j": (118, 92, 58),
            "f": (74, 48, 28), "F": (100, 70, 42), "g": (50, 32, 18),
            "m": (96, 64, 34), "M": (128, 90, 50), "n": (60, 40, 20)}, orelhas=True),
    ],
}


# RIBBAT: os chapéus do jogo dele (todos com o código ULTRA-MEGA-SKINS)
ROUPAS["RIBBAT"] = [dict(id="padrao", nome="ORIGINAL", preco=0)] + [
    dict(id=c, nome=chapeus_ribbat.NOMES[c], preco=0, codigo="ULTRAMEGASKINS", cor=chapeus_ribbat.CORES[c], troca={},
         chapeu=c) for c in chapeus_ribbat.CHAPEUS]


# SOMBRA (código THEDARKESTDUMMY) e OURO (código BRUTEFORTUNE): pra TODO MUNDO.
# Não trocam cor por cor: pintam o desenho inteiro (a "tinta"), então funcionam em qualquer personagem.
for _lista in ROUPAS.values():
    _lista.append(dict(id="sombra", nome="SOMBRA", preco=0, codigo="THEDARKESTDUMMY", cor=(70, 50, 110), troca={},
                       tinta="sombra"))
    _lista.append(dict(id="ouro", nome="LENDÁRIA (OURO)", preco=0, codigo="BRUTEFORTUNE", cor=(240, 190, 60),
                       troca={}, tinta="ouro"))


def da(ficha):
    """As roupas desse personagem (só a original se ele não tiver nenhuma)."""
    nome = ficha.get("nome_base", ficha["nome"])
    return ROUPAS.get(nome, [dict(id="padrao", nome="ORIGINAL", preco=0)])


def vestir(ficha, roupa=None):
    """A ficha do personagem com a roupa (a que ele está usando no save, se não disser qual)."""
    nome = ficha.get("nome_base", ficha["nome"])
    if roupa is None:
        roupa = save.usando(nome)
    r = next((r for r in da(ficha) if r["id"] == roupa), None)
    if not r or r["id"] == "padrao":
        return dict(ficha, nome_base=nome, roupa="padrao", troca=ficha.get("troca_base"), lobo=None, chapeu=None,
                    tinta=None, orelhas=None)
    return dict(ficha, nome_base=nome, roupa=r["id"], troca=r["troca"] or None, cor=r.get("cor", ficha["cor"]),
                lobo=r.get("lobo"), chapeu=r.get("chapeu"), tinta=r.get("tinta"), orelhas=r.get("orelhas"))


def de_codigo():
    """{código: [(personagem, roupa), ...]} de todas as roupas secretas (um código pode dar várias)."""
    cods = {}
    for nome, lista in ROUPAS.items():
        for r in lista:
            if r.get("codigo"):
                cods.setdefault(r["codigo"], []).append((nome, r))
    return cods


def outra(ficha, menos):
    """Espelho (mesmo personagem dos dois lados): o adversário veste uma roupa diferente."""
    ids = [r["id"] for r in da(ficha)]
    i = ids.index(menos) if menos in ids else 0
    return vestir(ficha, ids[(i + 1) % len(ids)])
