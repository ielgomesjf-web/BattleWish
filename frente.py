"""LUTADORES DE FRENTE (v2.x, pedido do Gomes): o lutador desenhado OLHANDO PRA CÂMERA.
Feito pra vitória do TRAFO em primeira pessoa (DESFILE DE FORMAS): ele cai na frente da câmera, transformado,
e usa o E vindo reto na tela. Também serve pra qualquer cena que precise do lutador de frente.

  desenhar_frente(tela, ficha, x, y, escala, pose, t) -> {"olhos": (x, y), "mao": (x, y), "cabeca": (x, y)}

  (x, y)   onde fica o meio entre os pés
  escala   1.0 = mais ou menos a altura do sprite do jogo (l.s); a cena usa 3.0
  pose     "parado", "pulo" (caindo, braços e pernas abertos), "agachado" (o pouso) ou "ataque" (o E dele,
           vindo pra frente, na direção da câmera)
  t        quadro (só pra respirar/balançar: NÃO muda estado nenhum)

Usa as cores da ROUPA (a troca da ficha) e a tinta das skins (SOMBRA / OURO / HOLO), igual o sprite.
Desenho em pixel art: tudo é desenhado pequeno (1 ponto = 1 pixel do jogo) e ampliado sem borrar, com contorno.
"""
import math

import pygame

import pecas

PRETO = (16, 14, 20)
UNID = 3.0  # (1 pixel do jogo = 3 pixels da tela no tamanho normal do sprite)


# =====================================================================
# o ESQUELETO de frente (x pra direita da tela, y pra cima; o chão é y = 0)
# =====================================================================
def esqueleto(pose, t, largo=1.0):
    r = math.sin(t * 0.08) * 0.8  # respirando
    if pose == "pulo":
        e = dict(pe_e=(-20, 6), pe_d=(20, 6), jo_e=(-22, 24), jo_d=(22, 24), qu_e=(-8, 46), qu_d=(8, 46),
                 om_e=(-16, 84), om_d=(16, 84), co_e=(-28, 94), co_d=(28, 94), ma_e=(-34, 106), ma_d=(34, 106),
                 pe_coco=(0, 88), cab=(0, 99))
    elif pose == "agachado":
        e = dict(pe_e=(-15, 0), pe_d=(15, 0), jo_e=(-20, 20), jo_d=(20, 20), qu_e=(-8, 30), qu_d=(8, 30),
                 om_e=(-16, 66), om_d=(16, 66), co_e=(-22, 50), co_d=(22, 50), ma_e=(-18, 38), ma_d=(18, 38),
                 pe_coco=(0, 70), cab=(0, 81))
    else:  # parado / ataque
        e = dict(pe_e=(-11, 0), pe_d=(11, 0), jo_e=(-11, 25), jo_d=(11, 25), qu_e=(-8, 50), qu_d=(8, 50),
                 om_e=(-16, 82 + r), om_d=(16, 82 + r), co_e=(-21, 64 + r), co_d=(21, 64 + r),
                 ma_e=(-21, 48 + r), ma_d=(21, 48 + r), pe_coco=(0, 86 + r), cab=(0, 97 + r))
        if pose == "ataque":  # a mão da direita vem pra FRENTE (na direção da câmera): fica no meio e maior
            e.update(co_d=(14, 70 + r), ma_d=(5, 62 + r))
    if largo != 1.0:
        e = {k: (vx * largo if not k.startswith("pe_") or True else vx, vy) for k, (vx, vy) in e.items()}
        e["cab"] = (0, e["cab"][1])
        e["pe_coco"] = (0, e["pe_coco"][1])
    return e


# =====================================================================
# ferramentas de desenho (no "pequeno": 1 ponto = 1 pixel do jogo)
# =====================================================================
class Pincel:
    def __init__(self, sup, ox, oy, k):
        self.sup, self.ox, self.oy, self.k = sup, ox, oy, k

    def P(self, u):
        return (self.ox + u[0] * self.k, self.oy - u[1] * self.k)

    def osso(self, a, b, larg, cor, clara=None):
        """Um membro (cápsula) de a até b, largura em unidades."""
        pa, pb = self.P(a), self.P(b)
        w = max(1, round(larg * self.k))
        pygame.draw.line(self.sup, cor, pa, pb, w)
        for q in (pa, pb):
            pygame.draw.circle(self.sup, cor, (round(q[0]), round(q[1])), max(1, w // 2))
        if clara and w >= 3:  # um filete de luz no lado esquerdo
            dx, dy = pb[0] - pa[0], pb[1] - pa[1]
            n = math.hypot(dx, dy) or 1
            ox, oy = -dy / n * w * 0.25, dx / n * w * 0.25
            pygame.draw.line(self.sup, clara, (pa[0] - abs(ox), pa[1] + oy), (pb[0] - abs(ox), pb[1] + oy), max(1, w // 4))

    def poli(self, pts, cor):
        pygame.draw.polygon(self.sup, cor, [self.P(q) for q in pts])

    def oval(self, c, rx, ry, cor):
        cx, cy = self.P(c)
        pygame.draw.ellipse(self.sup, cor, (cx - rx * self.k, cy - ry * self.k, 2 * rx * self.k, 2 * ry * self.k))

    def bola(self, c, r, cor):
        cx, cy = self.P(c)
        pygame.draw.circle(self.sup, cor, (round(cx), round(cy)), max(1, round(r * self.k)))

    def linha(self, a, b, cor, larg=1.0):
        pygame.draw.line(self.sup, cor, self.P(a), self.P(b), max(1, round(larg * self.k)))

    def ponto(self, c, cor):
        x, y = self.P(c)
        self.sup.set_at((int(x), int(y)), cor) if 0 <= int(x) < self.sup.get_width() and 0 <= int(y) < self.sup.get_height() else None


def _paleta(mod):
    pal = getattr(mod, "PALETA", {})

    def cor(letra, padrao=(200, 0, 200)):
        return (pecas.TROCA or {}).get(letra, pal.get(letra, padrao)) or padrao
    return cor


def _escura(c, k=0.72):
    return tuple(int(v * k) for v in c[:3])


def _clara(c, k=0.3):
    return tuple(min(255, int(v + (255 - v) * k)) for v in c[:3])


# =====================================================================
# o HUMANO de frente (corpo base; cada lutador escolhe as cores e põe os enfeites)
# =====================================================================
def humano(b, e, c, pose, t):
    """c = dict de cores: pele, tronco, tronco2 (lado/sombra), calca, bota, manga, mao, cabelo, cinto."""
    # pernas
    for lado in ("e", "d"):
        b.osso(e[f"qu_{lado}"], e[f"jo_{lado}"], 9, c["calca"], _clara(c["calca"], 0.15))
        b.osso(e[f"jo_{lado}"], e[f"pe_{lado}"], 8, c["calca"])
        px, py = e[f"pe_{lado}"]
        b.oval((px + (2 if lado == "d" else -2), py + 2), 6, 3, c["bota"])
    # braço de trás (o esquerdo, quando a mão da direita vem pra frente)
    for lado in ("e", "d"):
        if pose == "ataque" and lado == "d":
            continue
        b.osso(e[f"om_{lado}"], e[f"co_{lado}"], 7, c["manga"], _clara(c["manga"], 0.15))
        b.osso(e[f"co_{lado}"], e[f"ma_{lado}"], 6, c.get("antebraco", c["manga"]))
        b.bola(e[f"ma_{lado}"], 3.6, c["mao"])
    # tronco (mais largo no ombro, afina na cintura)
    oe, od, qe, qd = e["om_e"], e["om_d"], e["qu_e"], e["qu_d"]
    tronco = [(oe[0] - 2, oe[1] + 2), (od[0] + 2, od[1] + 2), (od[0] + 1, od[1] - 12), (qd[0] + 3, qd[1] + 2),
              (qe[0] - 3, qe[1] + 2), (oe[0] - 1, oe[1] - 12)]
    b.poli(tronco, c["tronco"])
    b.poli([(od[0] + 2, od[1] + 2), (od[0] + 1, od[1] - 12), (qd[0] + 3, qd[1] + 2), (qd[0] - 2, qd[1] + 2),
            (od[0] - 4, od[1] - 10)], c.get("tronco2", _escura(c["tronco"])))
    b.osso((qe[0] - 2, qe[1] + 2), (qd[0] + 2, qd[1] + 2), 4, c.get("cinto", _escura(c["calca"], 0.6)))
    # pescoço e cabeça
    b.osso((0, e["pe_coco"][1] - 4), e["pe_coco"], 6, c["pele"])
    cab = e["cab"]
    b.oval(cab, 9.5, 11, c["pele"])
    return cab


def olhos_simples(b, cab, cor=(20, 18, 24), dy=0.0, abertura=3.4):
    for s in (-1, 1):
        b.oval((cab[0] + s * abertura, cab[1] + dy), 1.3, 1.6, cor)


def mao_frente(b, e, c, t):
    """ATAQUE: o braço da direita vem pra frente (encurtado) e a mão fica GRANDE no meio do corpo."""
    b.osso(e["om_d"], e["co_d"], 8, c["manga"])
    b.osso(e["co_d"], e["ma_d"], 8, c.get("antebraco", c["manga"]))
    b.bola(e["ma_d"], 6.5, c["mao"])
    b.bola((e["ma_d"][0] - 1.5, e["ma_d"][1] + 1.5), 2.2, _clara(c["mao"], 0.25))
    return e["ma_d"]


# =====================================================================
# cada LUTADOR
# =====================================================================
# ---- MAX-10, PIXEL POR PIXEL ----
def _pecas_max():
    import max10
    from pecas import Peca
    pal = max10.PALETA
    return dict(
        cabeca=Peca([
            "....kkkkkk....",
            "..kkGGGGggkk..",
            ".kGGGGgggggdk.",
            ".kGGggggggddk.",
            "kSkGggggggdkSk",
            "kSkmmmmmmmmkSk",
            "kmkmrRmmrRmkmk",
            "kmkmmmmmmmmkmk",
            ".kkGggggggdkk.",
            "..kgggSSgddk..",
            "..kgdSmmSddk..",
            "...kdddDDdk...",
            "....kmmmmk....",
            ".....kkkk.....",
        ], pal, a=(7, 12), b=(7, 0), estica=False),
        tronco=Peca([
            "....kkkkkkkk....",
            "...kGGGGggggggk.",
            "..kGGGGgggggggdk",
            ".kGGGggkkkkggddk",
            ".kGGgggkSSkgggdk",
            ".kGgggkSrrSkggdk",
            ".kGgggkSrrSkggdk",
            ".kGggggkSSkgggdk",
            ".kgggggkkkkgggdk",
            ".kgggggggggggddk",
            "..kgggggggggddk.",
            "..kdddddddddDDk.",
            "...kmmmmmmmmmk..",
            "...kmwmbmymwmk..",
            "...kwmbmymwmbk..",
            "..kmmmmmmmmmmmk.",
            "..kSSSssssssmmk.",
            "..kSssssssssmmk.",
            "...kssssssmmmk..",
            "....kkkkkkkkk...",
        ], pal, a=(8, 17), b=(8, 1)),
        braco=Peca([
            ".kkkk.",
            "kSSsmk",
            "kmssmk",
            ".kmmk.",
            "kgGggk",
            "kgGggk",
            "kgggdk",
            "kgggdk",
            "kggddk",
            ".kmmk.",
            "kmssmk",
            ".kkkk.",
        ], pal, a=(2, 0), b=(2, 11)),
        antebraco=Peca([
            ".kkkk.",
            "kgGggk",
            "kgGggk",
            "kgggdk",
            "kgggdk",
            "kggddk",
            "kggddk",
            "kmmmmk",
            "kSssmk",
            ".kkkk.",
        ], pal, a=(2, 0), b=(2, 9)),
        mao=Peca([
            ".kkkk.",
            "kSSsmk",
            "kSssmk",
            "kssmmk",
            ".kkkk.",
        ], pal, a=(2, 0), b=(2, 4), estica=False),
        coxa=max10.COXA,
        canela=max10.CANELA,
        sapato=Peca([
            "..kkkkk..",
            ".kmSSSmk.",
            "kmsssssmk",
            "kmmmmmmmk",
            ".kkkkkkk.",
        ], pal, a=(4, 0), b=(4, 4), estica=False),
    )


def _max10(b, e, pose, t, f, prog=None):
    import max10
    pc = _peca("MAX-10", _pecas_max)
    cab = e["cab"]
    k = None
    if pose == "ataque":  # o E: o LASER DOS OLHOS
        k = (t % 60) / 60 if prog is None else max(0.0, min(1.0, prog))
        if k < 0.4:  # CARREGA: abaixadinha
            a = k / 0.4
            e = {n: (v[0], v[1] - 4 * a * (1 if not n.startswith("pe_") else 0)) for n, v in e.items()}
        elif k < 0.8:  # DISPARA: o tranco pra trás (sobe um pouco)
            e = {n: (v[0], v[1] + (1.5 if not n.startswith("pe_") else 0)) for n, v in e.items()}
        cab = e["cab"]
    montar_pecas(b, e, pc, "parado" if pose == "ataque" else pose)
    # as OMBREIRAS (do desenho do Gomes)
    for lado, esp in (("e", True), ("d", False)):
        om = b.P(e[f"om_{lado}"])
        max10.OMBREIRA.desenhar(b.sup, (om[0], om[1] - 1), (om[0], om[1] + 4), 1, esp)
    # o lança-mísseis no antebraço da direita
    co, ma = b.P(e["co_d"]), b.P(e["ma_d"])
    max10.LANCA_MISSEIS.desenhar(b.sup, co, ma, 1, False)
    # o QR CODE na testa (por cima do capacete)
    cx, cy = b.P((cab[0], cab[1] + 9))
    for i, linha in enumerate(("101", "010", "111")):
        for j, ch in enumerate(linha):
            x, y = int(cx - 1 + j), int(cy + i)
            if 0 <= x < b.sup.get_width() and 0 <= y < b.sup.get_height():
                b.sup.set_at((x, y), (20, 18, 22) if ch == "1" else (240, 240, 236))
    olhos = (cab[0], cab[1] + 3.5)
    res = dict(olhos=olhos, mao=olhos, cabeca=cab)
    if k is not None:
        ox, oy = b.P(olhos)
        if k < 0.4:  # os olhos acendendo + faísquinhas
            a = k / 0.4
            r = int(1 + 3 * a)
            pygame.draw.circle(b.sup, (255, 46, 36), (int(ox), int(oy)), r)
            pygame.draw.circle(b.sup, (255, 200, 180), (int(ox), int(oy)), max(1, r - 2))
            for i in range(3):
                if (t + i * 7) % 6 < 3:
                    ang = t * 0.7 + i * 2.1
                    b.sup.set_at((int(ox + math.cos(ang) * (r + 3)), int(oy + math.sin(ang) * (r + 3))), (255, 220, 120))
        elif k < 0.45:  # TRAVA: pisca branco
            pygame.draw.circle(b.sup, (255, 255, 255), (int(ox), int(oy)), 4)
        elif k < 0.8:  # DISPARA: o raio vindo na câmera (um círculo grosso pulsando)
            r = int(6 + 2 * math.sin(t * 1.3))
            pygame.draw.circle(b.sup, (200, 20, 20), (int(ox), int(oy)), r + 2)
            pygame.draw.circle(b.sup, (255, 70, 50), (int(ox), int(oy)), r)
            pygame.draw.circle(b.sup, (255, 230, 210), (int(ox), int(oy)), max(1, r - 3))
            for i in range(8):  # os raios em volta
                ang = i * math.tau / 8 + t * 0.2
                pygame.draw.line(b.sup, (255, 120, 80), (ox + math.cos(ang) * (r + 2), oy + math.sin(ang) * (r + 2)),
                                 (ox + math.cos(ang) * (r + 5), oy + math.sin(ang) * (r + 5)), 1)
        else:  # ESFRIA: fumacinha saindo do visor
            a = (k - 0.8) / 0.2
            for i in range(3):
                b.sup.set_at((int(ox - 3 + i * 3), int(oy - 4 - a * 6 - i)), (170, 170, 176))
        res["soltou"] = k >= 0.45
    return res


# ---- KUN, PIXEL POR PIXEL (o 1º refeito do jeito certo: peças de pixel art presas no esqueleto de frente) ----
def _pecas_kun():
    import kun
    from pecas import Peca
    pal = kun.PALETA
    return dict(
        cabeca=Peca([
            "...k.k..k.k...",
            "..khkhkkhkhk..",
            ".khhHhhhhHhhk.",
            "khhhhhhhhhhhhk",
            "kgggggggggggGk",
            "kGGGGGGGGGGGGk",
            "khhppppppppkhk",
            "kPhpkkpppkkphk",
            "kPppoopppoopPk",
            ".kpppppPpppPk.",
            ".kpppppPPpppk.",
            "..kppqqqqppk..",
            "..kpppbbpppk..",
            "...kkpppkkk...",
            "....kkkkk.....",
        ], pal, a=(7, 13), b=(7, 0), estica=False),
        tronco=Peca([
            "....kkkkkkkk....",
            "...kwwwkeekwwwk.",
            "..kwwwwkeekwwwwk",
            ".kwwRRkwwwwkRRwk",
            ".kwRRrrkwwkrrRwk",
            ".kRRrrrrkkrrrrvk",
            ".kRrrrrrekrrrrvk",
            ".kRrrrrrrrrrrrvk",
            ".kRrrrrrekrrrrvk",
            ".kRrrrrrrrrrrrvk",
            ".kRrrrrrekrrrvvk",
            ".kRrrrrrrrrrrvvk",
            ".kvRrrrrrrrrrvvk",
            ".kvvRrrrkkrrrvvk",
            ".keeeeeeSSeeeeek",
            ".kcccccccccccCCk",
            ".kcCcccccccccCCk",
            ".kcccccckccccCCk",
            "..kccccckcccCCk.",
            "..kkkkkkkkkkkkk.",
        ], pal, a=(8, 16), b=(8, 1)),
        braco=Peca([
            # manga branca (de frente)
            ".kkkkk.",
            "kwwwwwk",
            "kwwwwwk",
            "kwwwwwk",
            "kwwwwwk",
            "keeeeek",
            "kwwwwwk",
            "kwwwwwk",
            "kwwwwwk",
            ".kkkkk.",
        ], pal, a=(3, 0), b=(3, 9)),
        antebraco=Peca([
            ".kkkkk.",
            "kwwwwwk",
            "kkkkkkk",
            "kppPPqk",
            "kppPqqk",
            "kppPqqk",
            "kpPPqqk",
            "kpPqqqk",
            ".kkkkk.",
        ], pal, a=(3, 0), b=(3, 8)),
        mao=Peca([
            ".kkkk.",
            "kpPPqk",
            "kpPPqk",
            "kpkkqk",
            ".kkkk.",
        ], pal, a=(2, 0), b=(2, 4), estica=False),
        coxa=Peca([
            ".kkkkkkk.",
            "kcCccccck",
            "kCcccccck",
            "kCcccccck",
            "kCcccccCk",
            "kCcccccck",
            "kCcccccck",
            "kCcccccck",
            "kCcccccCk",
            ".kCccccck",
            ".kCcccck.",
            ".kccccck.",
            "..kkkkk..",
        ], pal, a=(4, 0), b=(4, 12)),
        canela=Peca([
            ".kkkkkk.",
            "kCccccck",
            "kCccccck",
            "kCccccck",
            "kCccccck",
            "kCccccck",
            "kCccccck",
            "kCccccck",
            "kCccccck",
            "kCccccck",
            ".kcccck.",
            "..kkkk..",
        ], pal, a=(3, 0), b=(3, 11)),
        cabeca_costas=Peca([
            "...k.k..k.k...",
            "..khkhkkhkhk..",
            ".khhHhhhhHhhk.",
            "khhhhhhhhhhhhk",
            "kGGGGGGGGGGGGk",
            "khhhhhhhhhhhhk",
            "khhhHhhhhHhhhk",
            "khhhhhhhhhhhhk",
            "kPhhhhhhhhhhPk",
            ".khhhhhhhhhhk.",
            ".kkhhhhhhhhkk.",
            "..kppppppppk..",
            "..kppppppppk..",
            "...kkpppkkk...",
            "....kkkkk.....",
        ], pal, a=(7, 13), b=(7, 0), estica=False),
        tronco_costas=Peca([
            "....kkkkkkkk....",
            "...kwwwwwwwwwwk.",
            "..kwwwwwwwwwwwwk",
            ".kwwRRRRRRRRRRwk",
            ".kwRRrrrrrrrrRwk",
            ".kRRrrrrrrrrrrvk",
            ".kRrrrrrrrrrrrvk",
            ".kRrrrrrvrrrrrvk",
            ".kRrrrrrvrrrrrvk",
            ".kRrrrrrvrrrrrvk",
            ".kRrrrrrrrrrrvvk",
            ".kRrrrrrrrrrrvvk",
            ".kvRrrrrrrrrrvvk",
            ".kvvRrrrrrrrrvvk",
            ".keeeeeeeeeeeeek",
            ".kcccccccccccCCk",
            ".kcCcccccccccCCk",
            ".kcccccckccccCCk",
            "..kccccckcccCCk.",
            "..kkkkkkkkkkkkk.",
        ], pal, a=(8, 16), b=(8, 1)),
        sapato=Peca([
            "..kkkkk..",
            ".ksSsssk.",
            "kssSsssSk",
            "kSSSSSSSk",
            ".kkkkkkk.",
        ], pal, a=(4, 0), b=(4, 4), estica=False),
    )


_PECAS = {}


def _peca(nome_lutador, fabrica):
    if nome_lutador not in _PECAS:
        _PECAS[nome_lutador] = fabrica()
    return _PECAS[nome_lutador]


def montar_pecas(b, e, pc, pose, var="normal", costas=False, sem_braco_d=False):
    """Monta um lutador de frente com as PEÇAS de pixel art (igual o sprite de lado, só que de frente).
    costas=True: mostra as costas (no meio de um GIRO)."""
    P = b.P
    for lado, espelho in (("e", True), ("d", False)):  # pernas
        q, j, pe = P(e[f"qu_{lado}"]), P(e[f"jo_{lado}"]), P(e[f"pe_{lado}"])
        pc["canela"].desenhar(b.sup, j, pe, 1, espelho, var)
        pc["coxa"].desenhar(b.sup, q, j, 1, espelho, var)
        pc["sapato"].desenhar(b.sup, (pe[0], pe[1] - 2), (pe[0], pe[1] + 2), 1, espelho, var)
    meio_q = P(((e["qu_e"][0] + e["qu_d"][0]) / 2, (e["qu_e"][1] + e["qu_d"][1]) / 2))
    tr = "tronco_costas" if costas and "tronco_costas" in pc else "tronco"
    pc[tr].desenhar(b.sup, meio_q, P(e["pe_coco"]), 1, False, var)
    pescoco = P(e["pe_coco"])
    cb = "cabeca_costas" if costas and "cabeca_costas" in pc else "cabeca"
    pc[cb].desenhar(b.sup, (pescoco[0], pescoco[1] + 1), (pescoco[0], pescoco[1] - 10), pc.get("_esc_cab", 1), False, var)
    for lado, espelho in (("e", True), ("d", False)):  # braços (por cima do tronco)
        if (pose == "ataque" or sem_braco_d) and lado == "d":
            continue
        o, c, m = P(e[f"om_{lado}"]), P(e[f"co_{lado}"]), P(e[f"ma_{lado}"])
        pc["antebraco"].desenhar(b.sup, c, m, 1, espelho, var)
        pc["mao"].desenhar(b.sup, m, (m[0] + (m[0] - c[0]) * 0.2, m[1] + 4), 1, espelho, var)
        pc["braco"].desenhar(b.sup, o, c, 1, espelho, var)


def _kun(b, e, pose, t, f, prog=None):
    pc = _peca("KUN", _pecas_kun)
    cab = e["cab"]
    if pose != "ataque":
        montar_pecas(b, e, pc, pose)
        mao = e["ma_d"]
        _carta(b, b.P(mao), 3, -4)
        return dict(olhos=(cab[0], cab[1] - 1), mao=mao, cabeca=cab)
    # ---- o E: PREPARA (0-.3) -> GIRA (.3-.55) -> TACA (.55-.7) -> FINALIZA (.7-1) ----
    k = (t % 60) / 60 if prog is None else max(0.0, min(1.0, prog))
    soltou = k >= 0.6
    if k < 0.3:  # puxa o braço com a carta por cima do ombro
        a = k / 0.3
        e2 = dict(e, co_d=(18 + 4 * a, 80 + 6 * a), ma_d=(10 + 12 * a, 92 + 8 * a))
        montar_pecas(b, e2, pc, "parado", sem_braco_d=True)
        _braco_d(b, e2, pc)
        mao = e2["ma_d"]
        _carta(b, b.P(mao), -2, -6, brilha=a)
    elif k < 0.55:  # o GIRO: o corpo "achata" e vira (aparece as costas no meio)
        g = (k - 0.3) / 0.25
        ang = g * math.tau
        largura = abs(math.cos(ang))
        costas = math.cos(ang) < 0
        e2 = dict(e, co_d=(20, 86), ma_d=(26, 96))
        temp = pygame.Surface(b.sup.get_size(), pygame.SRCALPHA)
        b2 = Pincel(temp, b.ox, b.oy, b.k)
        montar_pecas(b2, e2, pc, "parado", costas=costas, sem_braco_d=True)
        if not costas:
            _braco_d(b2, e2, pc)
        w = max(2, int(temp.get_width() * (0.25 + 0.75 * largura)))
        achatado = pygame.transform.scale(temp, (w, temp.get_height()))
        b.sup.blit(achatado, (b.ox - w / 2, 0))
        mao = (math.sin(ang) * 26, 96)
        if not costas:
            _carta(b, b.P(mao), -2, -6, brilha=1)
    elif k < 0.7:  # TACA: o braço vem esticado pra frente (na direção da câmera)
        e2 = dict(e, co_d=(12, 72), ma_d=(4, 66))
        montar_pecas(b, e2, pc, "parado", sem_braco_d=True)
        _braco_d(b, e2, pc, grande=True)
        mao = e2["ma_d"]
        if not soltou:
            _carta(b, b.P(mao), -2, -8, brilha=1)
    else:  # finaliza: o braço ainda esticado, voltando devagar
        a = (k - 0.7) / 0.3
        e2 = dict(e, co_d=(12 + 6 * a, 72 - 6 * a), ma_d=(4 + 14 * a, 66 - 14 * a))
        montar_pecas(b, e2, pc, "parado", sem_braco_d=True)
        _braco_d(b, e2, pc, grande=a < 0.5)
        mao = e2["ma_d"]
    return dict(olhos=(cab[0], cab[1] - 1), mao=mao, cabeca=cab, soltou=soltou)


def _braco_d(b, e, pc, grande=False):
    """O braço da direita desenhado por cima (no ataque); grande = vindo na direção da câmera."""
    o, c, m = b.P(e["om_d"]), b.P(e["co_d"]), b.P(e["ma_d"])
    pc["braco"].desenhar(b.sup, o, c, 1, False)
    pc["antebraco"].desenhar(b.sup, c, m, 1, False)
    if grande:  # (vindo na direção da câmera: a mão fica maior)
        pc["mao"].desenhar(b.sup, (m[0], m[1] - 3), (m[0], m[1] + 3), 1.5, False)
    else:
        pc["mao"].desenhar(b.sup, m, (m[0], m[1] + 4), 1, False)


def _carta(b, ponto, dx, dy, brilha=0.0):
    """A CARTA do Kun (branca com o naipe vermelho); brilha 0..1 = carregando."""
    mx, my = ponto
    if brilha > 0.3:  # carregando: estrelinhas piscando em volta da carta
        cx, cy = mx + dx + 2, my + dy + 3
        for i, (ox, oy) in enumerate(((-5, -4), (5, -3), (-4, 5), (5, 4))):
            if (i + int(brilha * 6)) % 2 == 0:
                for qx, qy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    px, py = int(cx + ox + qx), int(cy + oy + qy)
                    if 0 <= px < b.sup.get_width() and 0 <= py < b.sup.get_height():
                        b.sup.set_at((px, py), (255, 240, 160))
    carta = pygame.Surface((5, 7), pygame.SRCALPHA)
    carta.fill((246, 244, 236))
    pygame.draw.rect(carta, (16, 14, 20), (0, 0, 5, 7), 1)
    carta.set_at((2, 3), (200, 30, 40))
    b.sup.blit(carta, (mx + dx, my + dy))


# ---- RIB, PIXEL POR PIXEL ----
def _pecas_rib():
    import rib
    from pecas import Peca
    pal = rib.PALETA
    return dict(
        cabeca=Peca([
            "..kkk......kkk..",
            ".kyyyk....kyyyk.",
            ".kypYk....kYpyk.",
            ".kyyykkkkkkyyyk.",
            "kGkkkGGGGGGkkkGk",
            "kGGgggggggggggGk",
            "kGggggggDgggggdk",
            "kNNNNNNNNNNNNNNk",
            "knnnnnnnNnnnnnnk",
            "knnnnnnnnnnnnnnk",
            ".knnnnnnnnnnnnk.",
            "..knnnNnnnnnnk..",
            "..kkxxxxxxxxkk..",
            "...kxXXxxXXxk...",
        ], pal, a=(8, 12), b=(8, 0), estica=False),
        tronco=Peca([
            "..kkkkkkkkkk...",
            ".kGGGggggggggk.",
            "kGGggcccccggdk.",
            "kGggcccCccccgdk",
            "kGgccccccccCgdk",
            "kGgcccCcccccgdk",
            "kggccccccCccgdk",
            "kggcccccccccdk.",
            "kgDcccCccccgdk.",
            "kggcccccccDgdk.",
            "kgdcccccccgddk.",
            "kttttttttttttk.",
            ".ktsmttttsmttk.",
            "kttttttttttttk.",
            "knnnnnnnnnnnnk.",
            "kNnnnnnnnnnNnk.",
            "kNnnnnnnnnnnnk.",
            ".knnnnnnnnnnnk.",
            ".kkkkkkkkkkkk..",
        ], pal, a=(7, 15), b=(7, 1)),
        braco=rib.BRACO,
        antebraco=rib.ANTEBRACO,
        mao=rib.MAO,
        coxa=rib.COXA,
        canela=rib.CANELA,
        sapato=Peca([
            ".kkkkkkk.",
            "kgGgggggk",
            "kdgdgdgdk",
            ".k.k.k.k.",
        ], pal, a=(4, 0), b=(4, 3), estica=False),
    )


def _shuriken(b, ponto, ang, r=4):
    """A SHURIKEN (estrela de 4 pontas, aço) girando."""
    x, y = ponto
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.35
        pts.append((x + math.cos(ang + i * math.pi / 4) * rr, y + math.sin(ang + i * math.pi / 4) * rr))
    pygame.draw.polygon(b.sup, (40, 44, 52), [(px + (px - x) * 0.25, py + (py - y) * 0.25) for px, py in pts])
    pygame.draw.polygon(b.sup, (204, 210, 220), pts)
    b.sup.set_at((int(x), int(y)), (110, 116, 128))


def _cachecol_frente(b, e, t):
    """As pontas RASGADAS do cachecol, saindo do pescoço pro lado e balançando."""
    x0, y0 = b.P((e["pe_coco"][0] - 3, e["pe_coco"][1] - 1))
    for i, (comp, abre) in enumerate(((10, -3), (13, 0), (8, 3))):
        pts = [(x0, y0)]
        for j in range(1, 4):
            onda = math.sin(t * 0.25 + i + j * 0.8) * j * 0.6
            pts.append((x0 - comp * j / 3, y0 + abre * j / 3 + onda + j))
        pygame.draw.lines(b.sup, (22, 22, 28), False, pts, 2)


def postura_ninja(t):
    """A POSTURA NINJA do Rib (pedido do Gomes): agachado baixo, pernas bem abertas e UMA MÃO NO CHÃO
    (igual o pouso do herói-aranha), a outra mão pronta na frente do peito."""
    r = math.sin(t * 0.08) * 0.6
    return dict(pe_e=(-24, 0), pe_d=(24, 0), jo_e=(-26, 18), jo_d=(26, 18), qu_e=(-8, 30), qu_d=(8, 30),
                om_e=(-15, 60 + r), om_d=(15, 60 + r), co_e=(-24, 34), co_d=(18, 48 + r), ma_e=(-28, 3), ma_d=(6, 50 + r),
                pe_coco=(0, 64 + r), cab=(0, 74 + r))


def _rib(b, e, pose, t, f, prog=None):
    pc = _peca("RIB", _pecas_rib)
    if pose in ("parado", "ataque"):
        e = postura_ninja(t)
    cab = e["cab"]
    k = None
    if pose == "ataque":
        k = (t % 60) / 60 if prog is None else max(0.0, min(1.0, prog))
    _cachecol_frente(b, e, t)
    if k is None:
        montar_pecas(b, e, pc, pose)
        mao = e["ma_d"]
        return dict(olhos=(cab[0], cab[1] + 7), mao=mao, cabeca=cab)
    soltou = k >= 0.55
    if k < 0.45:  # PREPARA: cruza o braço na frente do peito, a shuriken girando na mão
        a = min(1.0, k / 0.3)
        e2 = dict(e, co_d=(4 - 6 * a, 50 + 4 * a), ma_d=(-6 - 8 * a, 60 + 4 * a))
        montar_pecas(b, e2, pc, "parado")
        mao = e2["ma_d"]
        _shuriken(b, b.P(mao), t * 0.6, 3 + a)
    elif k < 0.65:  # ARREMESSO: o braço chicoteia pra frente (na câmera)
        a = (k - 0.45) / 0.2
        e2 = dict(e, co_d=(10, 52), ma_d=(4 + 6 * a, 46 - 2 * a))
        montar_pecas(b, e2, pc, "parado", sem_braco_d=True)
        o, c, m_ = b.P(e2["om_d"]), b.P(e2["co_d"]), b.P(e2["ma_d"])
        pc["braco"].desenhar(b.sup, o, c, 1, False)
        pc["antebraco"].desenhar(b.sup, c, m_, 1, False)
        pc["mao"].desenhar(b.sup, (m_[0], m_[1] - 3), (m_[0], m_[1] + 3), 1.5, False)
        mao = e2["ma_d"]
        if not soltou:
            _shuriken(b, b.P(mao), t * 0.9, 5)
        else:  # o risco do arremesso
            mx, my = b.P(mao)
            pygame.draw.line(b.sup, (220, 230, 255), (mx - 10, my - 6), (mx - 3, my - 2), 1)
    else:  # FINALIZA: a mão estendida, o cachecol ainda balançando
        e2 = dict(e, co_d=(16, 48), ma_d=(20, 40))
        montar_pecas(b, e2, pc, "parado")
        mao = e2["ma_d"]
    return dict(olhos=(cab[0], cab[1] + 7), mao=mao, cabeca=cab, soltou=soltou)


# ---- KING RIP, PIXEL POR PIXEL ----
def _pecas_king():
    import king
    from pecas import Peca
    pal = king.PALETA
    return dict(
        cabeca=Peca([
            "...kkkkkkkk...",
            "..khHHHHHhhk..",
            ".khHHhhhhhhhk.",
            "khhhkkkkkhhhk.",
            "khhkpppppppkhk",
            "khkphhppphhpkk",
            "khkpekppkepkk.",
            ".kkpppppPpppk.",
            "..kpppPPPppk..",
            ".khhhhhhhhhk..",
            ".khhhhpphhhhk.",
            ".khhhhhhhhhk..",
            "..khhhhhhhk...",
            "...khhhhhk....",
            "....khhhk.....",
            "......kk......",
        ], pal, a=(7, 10), b=(7, 0), estica=False),
        tronco=Peca([
            "..kkkkkkkkkk..",
            ".kBBbppppbbvk.",
            "kBBbbpppbbbvk.",
            "kBbbbppbbybbvk",
            "kBbbbbpbbYybvk",
            "kBbbbbbbbybbvk",
            "kBbbbbbbyybbvk",
            "kBbbbbbyybbbvk",
            "kBbbbbbybbbbvk",
            "kBbbbbbbbbbbvk",
            "kxxxxxXxxxxxxk",
            "kxxxxkXkxxxxxk",
            "kbbbxkkkxbbbvk",
            "kBbbxbbbxbbbvk",
            "kBbbbbbbbbbbvk",
            "kBbbbbbbbbbvvk",
            "kbbbbbbbbbbvk.",
            ".kkkkkkkkkkkk.",
        ], pal, a=(7, 14), b=(7, 1)),
        braco=king.BRACO,
        antebraco=king.ANTEBRACO,
        mao=king.MAO,
        coxa=king.COXA,
        canela=king.CANELA,
        sapato=Peca([
            ".kkkkk.",
            "kpPPPqk",
            "kpPpPqk",
            ".kkkkk.",
        ], pal, a=(3, 0), b=(3, 3), estica=False),
    )


def postura_kungfu(t):
    """A base de KUNG FU do King: pernas abertas e dobradas, a mão da esquerda na frente (guarda)."""
    r = math.sin(t * 0.08) * 0.6
    return dict(pe_e=(-22, 0), pe_d=(22, 0), jo_e=(-24, 20), jo_d=(24, 20), qu_e=(-8, 38), qu_d=(8, 38),
                om_e=(-15, 72 + r), om_d=(15, 72 + r), co_e=(-16, 58 + r), co_d=(22, 58 + r),
                ma_e=(-6, 66 + r), ma_d=(24, 46 + r), pe_coco=(0, 76 + r), cab=(0, 86 + r))


def _enfeites_king(b, e, pal):
    """O COLAR de contas e a OMBREIRA de couro (um ombro só)."""
    pc_ = e["pe_coco"]
    for i in range(7):
        a = math.pi * (0.15 + 0.7 * i / 6)
        x, y = b.P((math.cos(a) * 6, pc_[1] - 5 - math.sin(a) * 5))
        pygame.draw.circle(b.sup, pal["o"] if i % 2 else pal["O"], (int(x), int(y)), 1)
    ox, oy = b.P(e["om_d"])
    pygame.draw.ellipse(b.sup, pal["c"], (ox - 3, oy - 2, 7, 5))
    b.sup.set_at((int(ox), int(oy)), pal["O"])


def _nunchaku(b, mao, ang, girando=False):
    """O NUNCHAKU (2 bastões de madeira e a corrente dourada); girando = o borrão redondo."""
    x, y = mao
    madeira, escura = (150, 96, 50), (90, 56, 28)
    if girando:
        pygame.draw.circle(b.sup, escura, (int(x), int(y)), 8, 2)
        pygame.draw.circle(b.sup, (240, 196, 60), (int(x), int(y)), 3, 1)
        return
    p1 = (x + math.cos(ang) * 6, y + math.sin(ang) * 6)
    p2 = (p1[0] + math.cos(ang + 1.2) * 2, p1[1] + math.sin(ang + 1.2) * 2)
    p3 = (p2[0] + math.cos(ang + 0.6) * 6, p2[1] + math.sin(ang + 0.6) * 6)
    for a_, b_ in (((x, y), p1), (p2, p3)):
        pygame.draw.line(b.sup, madeira, a_, b_, 2)
    pygame.draw.line(b.sup, (240, 196, 60), p1, p2, 1)


def _king(b, e, pose, t, f, prog=None):
    import king
    pc = _peca("KING RIP", _pecas_king)
    pal = king.PALETA
    if pose in ("parado", "ataque"):
        e = postura_kungfu(t)
    cab = e["cab"]
    if pose != "ataque":
        montar_pecas(b, e, pc, pose)
        _enfeites_king(b, e, pal)
        mao = e["ma_d"]
        _nunchaku(b, b.P(mao), math.pi / 2 + math.sin(t * 0.12) * 0.4)
        return dict(olhos=(cab[0], cab[1] + 2), mao=mao, cabeca=cab)
    k = (t % 60) / 60 if prog is None else max(0.0, min(1.0, prog))
    soltou = k >= 0.5
    if k < 0.4:  # GIRA o nunchaku por cima da cabeça
        a = min(1.0, k / 0.12)
        e2 = dict(e, co_d=(20, 72 + 10 * a), ma_d=(10, 84 + 16 * a))
        montar_pecas(b, e2, pc, "parado")
        _enfeites_king(b, e2, pal)
        mao = e2["ma_d"]
        _nunchaku(b, b.P(mao), t * 0.8, girando=a >= 1)
    elif k < 0.6:  # ARREMESSA pra frente (na câmera)
        a = (k - 0.4) / 0.2
        e2 = dict(e, co_d=(14, 66), ma_d=(6 - 2 * a, 60 - 2 * a))
        montar_pecas(b, e2, pc, "parado", sem_braco_d=True)
        o, c, m_ = b.P(e2["om_d"]), b.P(e2["co_d"]), b.P(e2["ma_d"])
        pc["braco"].desenhar(b.sup, o, c, 1, False)
        pc["antebraco"].desenhar(b.sup, c, m_, 1, False)
        pc["mao"].desenhar(b.sup, (m_[0], m_[1] - 3), (m_[0], m_[1] + 3), 1.5, False)
        _enfeites_king(b, e2, pal)
        mao = e2["ma_d"]
        if not soltou:
            _nunchaku(b, b.P(mao), 0, girando=True)
    else:  # espera o nunchaku VOLTAR (mão aberta pronta pra pegar)
        e2 = dict(e, co_d=(20, 66), ma_d=(16, 74))
        montar_pecas(b, e2, pc, "parado")
        _enfeites_king(b, e2, pal)
        mao = e2["ma_d"]
    return dict(olhos=(cab[0], cab[1] + 2), mao=mao, cabeca=cab, soltou=soltou)


# ---- CANNAN, PIXEL POR PIXEL ----
def _pecas_cannan():
    import cannan
    from pecas import Peca
    pal = cannan.PALETA
    meio_t = 6
    return dict(
        cabeca=Peca([
            "...kkkkkkkk...",
            "..khHHHhhhhk..",
            ".khHhhhhhhhhk.",
            "khhhhhhhhhhhk.",
            "khhhppppppphhk",
            "khhpkkpppkkphk",
            "khhpepppppephk",
            "khhpppppPppphk",
            "khhppppPPpphk.",
            "khhpppssspphk.",
            "khhkpppppkhhk.",
            "khhkkpppkkhhk.",
            ".khh.kkk.hhk..",
            "..kk.....kk...",
        ], pal, a=(7, 11), b=(7, 0), estica=False),
        tronco=Peca([
            ".kkkkkkkkkk..",
            ".kppxXxxxxpk.",
            "kppxXXxxxYpk.",
            "kxxXXxxxYyxk.",
            "kxXXxxxYyxxxk",
            "kxXxxxYyxXXxk",
            "kxXxxYykXXXxk",
            "kxxxYyxkXXXxk",
            "kxxYyxxkkkkxk",
            "kxYyxxxxxxxxk",
            "kYyxxxxxxxxxk",
            "kbbbbbXXbbbbk",
            "koooooooooOk.",
            "kOoooooooOOk.",
            "kOooooooooOk.",
            ".koooooooOOk.",
            ".kkkkkkkkkk..",
        ], pal, a=(meio_t, 13), b=(meio_t, 1)),
        tronco_liso=Peca([
            ".kkkkkkkkkk..",
            ".kxxXXxxxxxk.",
            "kxXXxxxxxxxk.",
            "kxXxxxxxxxXk.",
            "kxXxxxxxxxXXk",
            "kxXxxxxxxxXXk",
            "kxXxxxxxxxXXk",
            "kxxxxxxxxxXXk",
            "kxxxxxxxxxXXk",
            "kxxxxxxxxxxXk",
            "kxxxxxxxxxxxk",
            "kbbbbbXXbbbbk",
            "koooooooooOk.",
            "kOoooooooOOk.",
            "kOooooooooOk.",
            ".koooooooOOk.",
            ".kkkkkkkkkk..",
        ], pal, a=(meio_t, 13), b=(meio_t, 1)),
        braco=cannan.BRACO,
        antebraco=cannan.ANTEBRACO,
        mao=cannan.MAO,
        coxa=cannan.COXA,
        canela=cannan.CANELA,
        sapato=Peca([
            ".kkkkkk.",
            "kbXbbbbk",
            "kbbbbbbk",
            "kbbbbbbk",
            "kkkkkkkk",
        ], pal, a=(3, 0), b=(3, 4), estica=False),
        canhao=cannan.CANHAO,
        braco_mega=cannan.BRACO_MEGA, antebraco_mega=cannan.ANTEBRACO_MEGA, mao_mega=cannan.MAO_MEGA,
    )


def postura_soldado(t):
    """Cannan de pé, firme: pernas afastadas, o CANHÃO no braço da esquerda, a pistola na da direita."""
    r = math.sin(t * 0.08) * 0.6
    return dict(pe_e=(-15, 0), pe_d=(15, 0), jo_e=(-15, 24), jo_d=(15, 24), qu_e=(-8, 48), qu_d=(8, 48),
                om_e=(-15, 80 + r), om_d=(15, 80 + r), co_e=(-20, 64 + r), co_d=(20, 62 + r),
                ma_e=(-18, 48 + r), ma_d=(18, 46 + r), pe_coco=(0, 84 + r), cab=(0, 95 + r))


def _pistola(b, mao, mirando, coice=0.0):
    """A PISTOLA: de lado na mão (abaixada) ou MIRANDO NA CÂMERA (o cano vira um buraco escuro)."""
    x, y = mao
    if mirando:
        y -= coice * 3
        pygame.draw.rect(b.sup, (16, 14, 20), (x - 3, y - 6, 7, 6))
        pygame.draw.rect(b.sup, (110, 110, 118), (x - 2, y - 5, 5, 4))
        pygame.draw.circle(b.sup, (8, 8, 10), (int(x + 0.5), int(y - 3)), 1)
    else:
        pygame.draw.line(b.sup, (16, 14, 20), (x, y), (x + 1, y + 5), 3)
        pygame.draw.line(b.sup, (110, 110, 118), (x, y), (x + 1, y + 5), 1)


def _cannan(b, e, pose, t, f, prog=None):
    import cannan
    pc = _peca("CANNAN", _pecas_cannan)
    mega = f.get("roupa") == "megacannon"
    pal = cannan.PALETA
    if pose in ("parado", "ataque"):
        e = postura_soldado(t)
    cab = e["cab"]
    pecas_ = dict(pc)
    if mega:  # a armadura lisa (sem cinto de munição) e os braços de armadura
        pecas_.update(tronco=pc["tronco_liso"], braco=pc["braco_mega"], antebraco=pc["antebraco_mega"], mao=pc["mao_mega"])
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    tiros = (0.3, 0.5, 0.7)
    mirando = k is not None and 0.2 <= k < 0.85
    if k is not None and k < 0.2:  # SACA: a mão sobe do quadril
        a = k / 0.2
        e = dict(e, co_d=(20 - 6 * a, 62 + 6 * a), ma_d=(18 - 12 * a, 46 + 18 * a))
    elif mirando:
        e = dict(e, co_d=(12, 70), ma_d=(4, 66))
    montar_pecas(b, e, pecas_, "parado" if pose == "ataque" else pose, sem_braco_d=mirando)
    # o CANHÃO no braço da esquerda (apontando pra baixo, com as luzinhas)
    co, ma = b.P(e["co_e"]), b.P(e["ma_e"])
    pc["canhao"].desenhar(b.sup, co, (ma[0], ma[1] + 4), 1, True)
    if mega:  # o CAPACETE da Mega-Cannon (cúpula, faixa clara e o disco na orelha)
        cx, cy = b.P((cab[0], cab[1] + 4))
        troca = pecas.TROCA or {}
        azul, claro = troca.get("x", pal["x"]), troca.get("X", pal["X"])
        pygame.draw.ellipse(b.sup, azul, (cx - 7, cy - 6, 15, 10))
        pygame.draw.rect(b.sup, claro, (cx - 1, cy - 6, 3, 9))
        for sx in (-1, 1):
            pygame.draw.circle(b.sup, claro, (int(cx + sx * 7), int(cy + 3)), 2)
    if mirando:  # o braço vindo na câmera e a mão grande segurando a pistola
        o, c, m_ = b.P(e["om_d"]), b.P(e["co_d"]), b.P(e["ma_d"])
        pecas_["braco"].desenhar(b.sup, o, c, 1, False)
        pecas_["antebraco"].desenhar(b.sup, c, m_, 1, False)
        pecas_["mao"].desenhar(b.sup, (m_[0], m_[1] - 3), (m_[0], m_[1] + 3), 1.5, False)
    mao = e["ma_d"]
    tiro_agora = k is not None and any(0 <= k - x < 0.035 for x in tiros)
    coice = 1.0 if tiro_agora else 0.0
    _pistola(b, b.P(mao), mirando, coice)
    res = dict(olhos=(cab[0], cab[1]), mao=mao, cabeca=cab)
    if k is not None:
        res["soltou"] = k >= tiros[0]
        res["tiro"] = tiro_agora  # (True no quadrinho de CADA um dos 3 tiros)
        if tiro_agora:  # o CLARÃO no cano + a cápsula pulando
            x, y = b.P(mao)
            y -= 6
            for i in range(8):
                ang = i * math.tau / 8
                rr = 5 if i % 2 == 0 else 3
                pygame.draw.line(b.sup, (255, 230, 120), (x, y), (x + math.cos(ang) * rr, y + math.sin(ang) * rr), 1)
            pygame.draw.circle(b.sup, (255, 255, 230), (int(x), int(y)), 2)
            b.sup.set_at((int(x + 6), int(y - 3)), (230, 190, 70))
    return res


# ---- FINN, PIXEL POR PIXEL ----
def _pecas_finn():
    import finn
    from pecas import Peca
    pal = finn.PALETA
    return dict(
        cabeca=Peca([
            "...........kkk....",
            "..........kRRk....",
            ".........kRrk.....",
            "........kRrrk.....",
            "........kRRrrk....",
            ".......kRrorrk....",
            "......kRRrrrrk....",
            "......kRRrrrvk....",
            ".....kRRrrorrvk...",
            "....kRRrrrrrrvk...",
            "...kRRrrrrrrrrvk..",
            "..kooooooooooook..",
            "kkkkkkkkkkkkkkkkkk",
            "kRRRrrrrrrrrrrrvvk",
            "kkkkkkkkkkkkkkkkkk",
            "..khHpppppppHhk...",
            "..kHHHkpppkHHHk...",
            "..khpepppppephk...",
            "..khpppppPpppphk..",
            "..kHhhhPPPhhhHk...",
            "..khhhhhhhhhhhk...",
            "...khhhhhhhhhhk...",
            "...khhhhHhhhhk....",
            "....khhhhhhhhk....",
            "....khhhHhhhk.....",
            ".....khhhhhhk.....",
            ".....khhhhhk......",
            "......khhhk.......",
            "........kk........",
        ], pal, a=(9, 22), b=(9, 0), estica=False),
        tronco=Peca([
            ".kkkkkkkkkkkk..",
            ".kooRrrarrRook.",
            "kooRrrrarrrook.",
            "kRRrrrrarrrrvk.",
            "kRrrorrarrrrvk.",
            "kRrrrrrarrrorvk",
            "kRrrrrrarrrrvk.",
            "kRrrrrrarrrvvk.",
            "kRrorrrarrrvvk.",
            "koooooooooooook",
            "kRrrrrrarrrvvk.",
            "kRrrrrrarrorvk.",
            ".kRrrrrrarrrvk.",
            ".kkkkkkkkkkkkk.",
        ], pal, a=(7, 12), b=(7, 1)),
        braco=finn.BRACO,
        antebraco=finn.ANTEBRACO,
        mao=finn.MAO,
        coxa=finn.COXA,
        canela=finn.CANELA,
        sapato=Peca([
            ".kkkkk.",
            "kbBbbbk",
            "kbbbbbk",
            ".kkkkk.",
        ], pal, a=(3, 0), b=(3, 3), estica=False),
    )


def _manto_frente(b, e, pal):
    """A SAIA DO MANTO (cobre as pernas até a canela) com a faixa azul no meio e a barra escura."""
    troca = pecas.TROCA or {}
    roxo, escuro, faixa, barra = (troca.get(c, pal[c]) for c in ("r", "v", "a", "x"))
    qe, qd = b.P(e["qu_e"]), b.P(e["qu_d"])
    pe_e, pe_d = b.P(e["pe_e"]), b.P(e["pe_d"])
    baixo = max(pe_e[1], pe_d[1]) - 3
    pts = [(qe[0] - 2, qe[1]), (qd[0] + 2, qd[1]), (pe_d[0] + 4, baixo), (pe_e[0] - 4, baixo)]
    pygame.draw.polygon(b.sup, roxo, pts)
    pygame.draw.line(b.sup, escuro, pts[1], pts[2], 2)
    pygame.draw.line(b.sup, barra, (pts[3][0], baixo), (pts[2][0], baixo), 2)
    meio = ((qe[0] + qd[0]) / 2, qe[1])
    pygame.draw.line(b.sup, faixa, meio, (meio[0], baixo - 1), 1)


def _cajado_frente(b, e, t, aceso=False):
    """O CAJADO na mão da esquerda, com a bola roxa brilhando em cima."""
    mx, my = b.P(e["ma_e"])
    topo = (mx, my - 26)
    pygame.draw.line(b.sup, (60, 36, 18), (mx, my + 10), topo, 3)
    pygame.draw.line(b.sup, (120, 76, 40), (mx, my + 10), topo, 1)
    r = 3 + (1 if aceso and (t // 4) % 2 else 0)
    pygame.draw.circle(b.sup, (190, 120, 255), (int(topo[0]), int(topo[1] - 2)), r)
    b.sup.set_at((int(topo[0] - 1), int(topo[1] - 3)), (240, 220, 255))


def _pocoes_livro(b, e):
    """As 3 POÇÕES e o LIVRO no cinto (do remodel do Finn)."""
    qd = b.P(e["qu_d"])
    for i, c in enumerate(((230, 50, 40), (60, 170, 255), (80, 220, 90))):
        x, y = qd[0] - 1 - i * 3, qd[1] - 3
        pygame.draw.circle(b.sup, (16, 12, 26), (int(x), int(y)), 2)
        b.sup.set_at((int(x), int(y)), c)
    qe = b.P(e["qu_e"])
    pygame.draw.rect(b.sup, (16, 12, 26), (qe[0] - 1, qe[1] - 5, 4, 5))
    pygame.draw.rect(b.sup, (110, 60, 36), (qe[0], qe[1] - 4, 2, 3))


def _fogo(b, ponto, r, t):
    """A BOLA DE FOGO (tremulando)."""
    x, y = ponto
    tre = math.sin(t * 0.9) * 0.6
    pygame.draw.circle(b.sup, (200, 60, 20), (int(x), int(y)), int(r + 1 + tre))
    pygame.draw.circle(b.sup, (255, 140, 40), (int(x), int(y)), int(r + tre))
    pygame.draw.circle(b.sup, (255, 230, 120), (int(x), int(y)), max(1, int(r * 0.5)))
    for i in range(3):  # as linguinhas de fogo em cima
        ang = -math.pi / 2 + (i - 1) * 0.6 + math.sin(t * 0.5 + i) * 0.2
        b.sup.set_at((int(x + math.cos(ang) * (r + 2)), int(y + math.sin(ang) * (r + 2))), (255, 200, 80))


def _finn(b, e, pose, t, f, prog=None):
    import finn
    pc = _peca("FINN", _pecas_finn)
    pal = finn.PALETA
    cab = e["cab"]
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    if k is None:
        _desenha_finn(b, e, pc, pal, pose, t)
        return dict(olhos=(cab[0], cab[1] + 2), mao=e["ma_d"], cabeca=cab)
    soltou = k >= 0.5
    if k < 0.35:  # JUNTA o fogo na mão (ela sobe na frente do peito)
        a = k / 0.35
        e2 = dict(e, co_d=(20, 66 + 4 * a), ma_d=(10, 66 + 6 * a))
        _desenha_finn(b, e2, pc, pal, "parado", t, aceso=True)
        mao = e2["ma_d"]
        _fogo(b, b.P((mao[0] - 2, mao[1] + 5)), 1.5 + 3 * a, t)
    elif k < 0.55:  # EMPURRA a palma pra frente (na câmera)
        e2 = dict(e, co_d=(12, 70), ma_d=(4, 66))
        _desenha_finn(b, e2, pc, pal, "parado", t, aceso=True, braco_frente=True)
        mao = e2["ma_d"]
        if not soltou:
            _fogo(b, b.P((mao[0], mao[1] + 2)), 6, t)
    else:  # a mão ainda estendida, soltando fumacinha
        a = (k - 0.55) / 0.45
        e2 = dict(e, co_d=(12 + 6 * a, 70 - 4 * a), ma_d=(4 + 8 * a, 66 - 10 * a))
        _desenha_finn(b, e2, pc, pal, "parado", t, braco_frente=a < 0.4)
        mao = e2["ma_d"]
        x, y = b.P(mao)
        for i in range(2):
            b.sup.set_at((int(x + i * 2), int(y - 4 - a * 6 - i)), (170, 170, 176))
    return dict(olhos=(cab[0], cab[1] + 2), mao=mao, cabeca=cab, soltou=soltou)


def _manga_larga(b, c, m_, pal):
    """A MANGA LARGA de mago: abre em sino perto do pulso."""
    troca = pecas.TROCA or {}
    roxo, escuro = troca.get("r", pal["r"]), troca.get("v", pal["v"])
    dx, dy = m_[0] - c[0], m_[1] - c[1]
    n = math.hypot(dx, dy) or 1
    px, py = -dy / n, dx / n
    base = (c[0] + dx * 0.55, c[1] + dy * 0.55)
    ponta = (c[0] + dx * 0.9, c[1] + dy * 0.9)
    pts = [(base[0] + px * 2, base[1] + py * 2), (base[0] - px * 2, base[1] - py * 2),
           (ponta[0] - px * 4, ponta[1] - py * 4), (ponta[0] + px * 4, ponta[1] + py * 4)]
    pygame.draw.polygon(b.sup, roxo, pts)
    pygame.draw.line(b.sup, escuro, pts[2], pts[3], 1)


def _desenha_finn(b, e, pc, pal, pose, t, aceso=False, braco_frente=False):
    montar_pecas(b, e, pc, pose, sem_braco_d=braco_frente)
    _manto_frente(b, e, pal)
    _pocoes_livro(b, e)
    # (o tronco e a cabeça por cima da saia: redesenha os dois)
    meio_q = b.P(((e["qu_e"][0] + e["qu_d"][0]) / 2, (e["qu_e"][1] + e["qu_d"][1]) / 2))
    pc["tronco"].desenhar(b.sup, meio_q, b.P(e["pe_coco"]), 1, False)
    _pocoes_livro(b, e)
    pescoco = b.P(e["pe_coco"])
    pc["cabeca"].desenhar(b.sup, (pescoco[0], pescoco[1] + 1), (pescoco[0], pescoco[1] - 10), 1, False)
    for lado, esp in (("e", True), ("d", False)):
        if braco_frente and lado == "d":
            continue
        o, c, m_ = b.P(e[f"om_{lado}"]), b.P(e[f"co_{lado}"]), b.P(e[f"ma_{lado}"])
        pc["antebraco"].desenhar(b.sup, c, m_, 1, esp)
        pc["mao"].desenhar(b.sup, m_, (m_[0], m_[1] + 4), 1, esp)
        pc["braco"].desenhar(b.sup, o, c, 1, esp)
        _manga_larga(b, c, m_, pal)
    if braco_frente:
        o, c, m_ = b.P(e["om_d"]), b.P(e["co_d"]), b.P(e["ma_d"])
        pc["braco"].desenhar(b.sup, o, c, 1, False)
        pc["antebraco"].desenhar(b.sup, c, m_, 1, False)
        pc["mao"].desenhar(b.sup, (m_[0], m_[1] - 3), (m_[0], m_[1] + 3), 1.5, False)
    _cajado_frente(b, e, t, aceso)


# ---- TAI, PIXEL POR PIXEL ----
def _pecas_tai():
    import tai
    from pecas import Peca
    pal = tai.PALETA
    return dict(
        cabeca=Peca([
            "......kk......",
            ".....kzzk.....",
            "....kzyyzk....",
            ".....kzzk.....",
            "...kkkkkkkk...",
            "..khhhhhhhhk..",
            ".khhhhhhhhhhk.",
            ".khhpppppphhk.",
            "kPhpkkppkkphPk",
            "kPppekppkeppPk",
            "kpppppPPpppppk",
            "kppppPPPPppppk",
            "kpppqqqqqqpppk",
            "kpppppppppppk.",
            ".kkpppppppkk..",
            "...kkkkkkk....",
        ], pal, a=(7, 14), b=(7, 0), estica=False),
        tronco=Peca([
            "....kkkkkkkkkkkk....",
            "...kvVaaaaaaaavwk...",
            "..kVVvaaaaaaaaavwk..",
            ".kVvvaaaaaaaaaaavwk.",
            "kVvaaaaaaaaaaaaavwk.",
            "kVvaaxaaaaaaaaxaavwk",
            "kVvaaaaaaaaaaaaaavwk",
            "kVvaaaaAAAAAaaaaavwk",
            "kVvaaaaAaaaaaaaaavwk",
            "kVvaaaaaaaxaaaaaavwk",
            "kVvaaaaaaaaaaaaaavwk",
            "kvvaaaaaaaaaaaaavvk.",
            "kmmmmmmmmmmmmmmmmmmk",
            "kMMMmmmmmmmmmmmmMMMk",
            "kmmmmmmmmnnnnmmmmmmk",
            ".kmmmmmmmnnnnmmmmmk.",
            ".kkmmmmmnnnnmmmmkk..",
            "...kkkkknnnnkkkkk...",
        ], pal, a=(10, 15), b=(10, 1)),
        braco=tai.BRACO,
        antebraco=tai.ANTEBRACO,
        mao=tai.MAO,
        coxa=tai.COXA,
        canela=tai.CANELA,
        sapato=tai.PE,
    )


def postura_sumo(t):
    """O TAI agachado de sumô: pernas bem abertas, mãos nos joelhos, pronto pro choque."""
    r = math.sin(t * 0.08) * 0.8
    return dict(pe_e=(-24, 0), pe_d=(24, 0), jo_e=(-26, 18), jo_d=(26, 18), qu_e=(-11, 34), qu_d=(11, 34),
                om_e=(-19, 70 + r), om_d=(19, 70 + r), co_e=(-27, 52 + r), co_d=(27, 52 + r),
                ma_e=(-23, 34 + r), ma_d=(23, 34 + r), pe_coco=(0, 74 + r), cab=(0, 86 + r))


def _onda_tatuagem(b, e):
    """A TATUAGEM DE ONDA na lateral (do remodel)."""
    if (pecas.TROCA or {}).get("a"):  # (na roupa de camisa não aparece)
        return
    x, y = b.P((e["om_e"][0] + 5, (e["om_e"][1] + e["qu_e"][1]) / 2 + 2))
    azul, claro = (40, 90, 170), (110, 170, 230)
    for i in range(5):
        b.sup.set_at((int(x + i), int(y - round(math.sin(i * 1.2)))), azul)
    b.sup.set_at((int(x + 4), int(y - 2)), claro)


def _tai(b, e, pose, t, f, prog=None):
    pc = _peca("TAI", _pecas_tai)
    if pose in ("parado", "ataque"):
        e = postura_sumo(t)
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    soltou = k is not None and k >= 0.5
    if k is not None:  # o E: PULÃO e cai com tudo (pedido do Gomes, no lugar do shiko)
        if k < 0.15:  # abaixa pra pegar impulso
            a = k / 0.15
            e = {n: (v[0], v[1] - (5 * a if not n.startswith("pe_") else 0)) for n, v in e.items()}
        elif k < 0.5:  # no AR: sobe e desce (as pernas encolhidas, os braços pra cima)
            a = (k - 0.15) / 0.35
            alt = 46 * math.sin(a * math.pi)
            e = {n: (v[0], v[1] + alt) for n, v in e.items()}
            e.update(jo_e=(-22, e["qu_e"][1] - 6), jo_d=(22, e["qu_d"][1] - 6),
                     pe_e=(-14, e["qu_e"][1] - 16), pe_d=(14, e["qu_d"][1] - 16),
                     co_e=(-30, e["om_e"][1] + 8), co_d=(30, e["om_d"][1] + 8),
                     ma_e=(-30, e["om_e"][1] + 22), ma_d=(30, e["om_d"][1] + 22))
        elif k < 0.7:  # CAI: o corpo amassa no chão (o peso!) e volta
            a = (k - 0.5) / 0.2
            d = 8 * math.sin((1 - a) * math.pi / 2)
            e = {n: (v[0] * (1 + 0.06 * d / 8), v[1] - (d if not n.startswith("pe_") else 0)) for n, v in e.items()}
    cab = e["cab"]
    montar_pecas(b, e, pc, "parado" if pose == "ataque" else pose)
    _onda_tatuagem(b, e)
    chao = (0, 0)
    if k is not None and 0.5 <= k < 0.75:  # a RACHADURA e a poeira onde ele caiu
        x, y = b.P((0, 0))
        a = (k - 0.5) / 0.25
        for i in range(4):
            ang = math.pi + i * 0.35
            b.sup.set_at((int(x + math.cos(ang) * (3 + 6 * a)), int(y + 1)), (60, 40, 20))
        for i in range(3):
            b.sup.set_at((int(x - 4 + i * 4), int(y - 2 - a * 4 - i)), (180, 160, 130))
    res = dict(olhos=(cab[0], cab[1] + 3), mao=chao, cabeca=cab)
    if k is not None:
        res["soltou"] = soltou
    return res


# ---- TAMER, PIXEL POR PIXEL (e o LOBO vindo de frente) ----
def _pecas_tamer():
    import tamer
    from pecas import Peca
    pal = tamer.PALETA
    return dict(
        cabeca=Peca([
            ".....kkkkkk.....",
            "....khHHHhhk....",
            "...khHkHhhhhk...",
            "kkkkksssssskkkkk",
            "khHHHHhhhhhhhhhk",
            "kkkkkkkkkkkkkkkk",
            "..kxpppppppxk...",
            ".kxpkkpppkkpxk..",
            ".kxpepppppepxk..",
            ".kpppppPpppppk..",
            ".kxpppPPPpppxk..",
            ".kxxppqqqppxxk..",
            ".kxxxpppppxxxk..",
            "...kxxxxxxxxk...",
            ".....kkkkkk.....",
        ], pal, a=(8, 13), b=(8, 0), estica=False),
        cabeca_grito=Peca([
            ".....kkkkkk.....",
            "....khHHHhhk....",
            "...khHkHhhhhk...",
            "kkkkksssssskkkkk",
            "khHHHHhhhhhhhhhk",
            "kkkkkkkkkkkkkkkk",
            "..kxpppppppxk...",
            ".kxpkkpppkkpxk..",
            ".kxpepppppepxk..",
            ".kpppppPpppppk..",
            ".kxpppPPPpppxk..",
            ".kxxpkeeekpxxk..",
            ".kxxxpkkkpxxxk..",
            "...kxxxxxxxxk...",
            ".....kkkkkk.....",
        ], pal, a=(8, 13), b=(8, 0), estica=False),
        tronco=Peca([
            ".kkkkkkkkkkk..",
            ".kcCCcppcccvk.",
            "kcCCccppcccvk.",
            "kcCuuucccuuuvk",
            "kcCuvucccuvuvk",
            "kcCuuucccuuuvk",
            "kcCcccccccccvk",
            "kcCccccsccccvk",
            "kcCcccscccccvk",
            "kcccccccccccvk",
            "kccccccccccvvk",
            "kssssssssssssk",
            "ksssssBBsssssk",
            ".koooooooooOk.",
            "kOooooooooOOk.",
            ".kOooooooooOk.",
            ".kkkkkkkkkkk..",
        ], pal, a=(7, 14), b=(7, 1)),
        braco=tamer.BRACO,
        antebraco=tamer.ANTEBRACO,
        mao=tamer.MAO,
        coxa=tamer.COXA,
        canela=tamer.CANELA,
        sapato=Peca([
            ".kkkkkk.",
            "kbBbbbbk",
            "kbbbbbbk",
            "kBBBBBBk",
            "kkkkkkkk",
        ], pal, a=(3, 0), b=(3, 4), estica=False),
    )


_LOBO_TOPO = ['.k........k.', 'k3k......k3k', 'k32k....k23k', 'k22kkkkkk22k', 'k2222112222k', 'k2221111222k', 'k2kk2112kk2k', 'k1oek11keo1k', 'k1111111111k', '.k11111111k.', '.k111kk111k.', '.kk1kkkk1kk.']
_LOBO_FECHADA = ['..k111111k..', '..k1kkkk1k..', '..kcccccck..', '...kkggkk...']
_LOBO_ABERTA = ['..kkkkkkkk..', '..kwrrrrwk..', '..krrrrrrk..', '..kwrrrrwk..', '...kkkkkk...', '..kcccccck..', '...kkggkk...']
_LOBO_PX = {}
LOBO_W, LOBO_H, LOBO_CX = 32, 42, 16  # (a superfície do lobo; o chão é a última linha)


def cores_lobo(f):
    """As cores do lobo (cor escolhida + skin do lobo, se tiver)."""
    import tamer
    cor = f.get("lobo_cor", "branco")
    skin = tamer.skin_lobo_f(f) or {}
    c1, c2, c3, olho = skin.get("cores", {}).get(cor) or tamer.CORES_LOBO.get(cor, tamer.CORES_LOBO["branco"])
    return c1, c2, c3, skin.get("olho", olho)


def _perna(sup, a_, b_, c, k_):
    pygame.draw.line(sup, k_, a_, b_, 5)
    pygame.draw.line(sup, c, a_, b_, 3)


def _pata(sup, p_, c, k_, garras=0, branco=(245, 245, 236)):
    x, y = p_
    pygame.draw.rect(sup, k_, (x - 3, y - 1, 7, 3))
    pygame.draw.rect(sup, c, (x - 2, y, 5, 1))
    if garras:  # as GARRAS: pontinhas brancas na frente dos dedos
        for d in (-2, 0, 2):
            sup.set_at((x + d, y - 2), branco)
            sup.set_at((x + d, y - 3), k_)


def _lobo_pixel(cores, aberta, pose):
    """O LOBO DE FRENTE em PIXEL ART, no mesmo tamanho de pixel do Tamer (1 px = 1 pixel do jogo).
    pose: "em_pe", "agachado", "bote1" ou "bote2" (o pulo, com as patas da frente subindo e as garras).
    Devolve (superfície, (x, y) do meio da cabeça)."""
    chave = (cores, aberta, pose)
    if chave not in _LOBO_PX:
        c1, c2, c3, olho = cores
        k_ = (20, 18, 24)
        pal = {"k": k_, "1": c1, "2": c2, "3": c3, "o": olho, "e": (10, 10, 14),
               "w": (245, 245, 236), "r": (150, 36, 46), "c": (190, 40, 36), "g": (246, 200, 70)}
        sup = pygame.Surface((LOBO_W, LOBO_H), pygame.SRCALPHA)
        cx = LOBO_CX
        if pose == "em_pe":
            y0 = 4
            _perna(sup, (cx - 8, 29), (cx - 9, 39), c3, k_)  # as de trás (aparecendo dos lados)
            _perna(sup, (cx + 8, 29), (cx + 9, 39), c3, k_)
            pygame.draw.ellipse(sup, k_, (cx - 9, 14, 18, 20))
            pygame.draw.ellipse(sup, c2, (cx - 8, 15, 16, 18))
            pygame.draw.ellipse(sup, c1, (cx - 4, 15, 8, 17))
            for d in (-3, 3):  # as da frente, retinhas
                _perna(sup, (cx + d, 26), (cx + d, 39), c2, k_)
                _pata(sup, (cx + d, 40), c1, k_)
            for i in range(4):  # o rabo
                sup.set_at((cx + 8 + i, 26 - i * 2), c2)
                sup.set_at((cx + 8 + i, 27 - i * 2), k_)
        elif pose == "agachado":  # se abaixa pra pegar impulso
            y0 = 10
            _perna(sup, (cx - 8, 33), (cx - 10, 40), c3, k_)
            _perna(sup, (cx + 8, 33), (cx + 10, 40), c3, k_)
            pygame.draw.ellipse(sup, k_, (cx - 10, 20, 20, 16))
            pygame.draw.ellipse(sup, c2, (cx - 9, 21, 18, 14))
            pygame.draw.ellipse(sup, c1, (cx - 4, 22, 8, 12))
            for s_ in (-1, 1):  # as da frente, dobradas pra fora
                _perna(sup, (cx + s_ * 3, 30), (cx + s_ * 6, 35), c2, k_)
                _perna(sup, (cx + s_ * 6, 35), (cx + s_ * 5, 39), c2, k_)
                _pata(sup, (cx + s_ * 5, 40), c1, k_)
        else:  # o BOTE: corpo curtinho atrás (vem na nossa direção), patas da frente na altura do queixo
            g = 1 if pose == "bote1" else 2
            y0 = 2
            _perna(sup, (cx - 4, 24), (cx - 3, 29), c3, k_)  # as de trás, encolhidas
            _perna(sup, (cx + 4, 24), (cx + 3, 29), c3, k_)
            pygame.draw.ellipse(sup, k_, (cx - 8, 11, 16, 16))
            pygame.draw.ellipse(sup, c2, (cx - 7, 12, 14, 14))
            pygame.draw.ellipse(sup, c1, (cx - 3, 13, 6, 12))
            for s_ in (-1, 1):
                pata = (cx + s_ * (8 + 2 * g), 19 - 2 * g)
                _perna(sup, (cx + s_ * 4, 18), pata, c2, k_)
                _pata(sup, pata, c1, k_, garras=g)
        mapa = _LOBO_TOPO + (_LOBO_ABERTA if aberta else _LOBO_FECHADA)
        for y, linha in enumerate(mapa):
            for x, ch in enumerate(linha):
                if ch != ".":
                    sup.set_at((cx - 6 + x, y0 + y), pal[ch])
        _LOBO_PX[chave] = (sup, (cx, y0 + 7))
    return _LOBO_PX[chave]


def lobo_de_frente(tela, x, y, esc, t, cores, boca=1.0, garras=1.0):
    """O LOBO VINDO DE FRENTE (dando o bote na câmera), em pixel art.
    (x, y) = o meio da cabeça na tela; esc = tamanho de 1 pixel do jogo na tela (começa = UNID * escala, o
    mesmo do Tamer, e vai aumentando); boca > 0.4 = de boca aberta; garras 0..1 = as patas subindo.
    cores = cores_lobo(ficha)."""
    pose = "agachado" if garras <= 0 else "bote1" if garras < 0.6 else "bote2"
    sup, (hx, hy) = _lobo_pixel(cores, boca > 0.4, pose)
    img = pygame.transform.scale(sup, (round(LOBO_W * esc), round(LOBO_H * esc)))  # (pixels quadradinhos)
    tela.blit(img, (round(x - hx * esc), round(y - hy * esc)))


def _lobo_do_lado(b, f, pose, desenha=True):
    """O lobo de frente em pé (ou agachado) do lado do Tamer, no chão: desenha (se desenha=True)
    e devolve o meio da cabeça (unidades)."""
    sup, (hx, hy) = _lobo_pixel(cores_lobo(f), False, pose)
    x0, y0 = b.ox + LOBO_X * b.k - LOBO_CX, b.oy - LOBO_H + 1
    if desenha:
        b.sup.blit(sup, (round(x0), round(y0)))
    return ((x0 + hx - b.ox) / b.k, (b.oy - (y0 + hy)) / b.k)

def _tamer(b, e, pose, t, f, prog=None):
    import tamer
    pc = _peca("TAMER", _pecas_tamer)
    pal = tamer.PALETA
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    soltou = k is not None and k >= 0.45
    # o LOBO de frente do lado dele (em pé; no E se abaixa pra pular; quando pula, quem desenha é a cena)
    cabeca_lobo = _lobo_do_lado(b, f, "agachado" if k is not None and k >= 0.3 else "em_pe", desenha=not soltou)
    if k is not None:  # APONTA pra câmera e dá o comando
        a = min(1.0, k / 0.25)
        e = dict(e, co_d=(18 + 8 * a, 64 + 8 * a), ma_d=(20 + 20 * a, 48 + 26 * a))
    cab = e["cab"]
    grito = k is not None and 0.2 <= k < 0.6  # GRITANDO o comando (boca aberta)
    pc_ = dict(pc, cabeca=pc["cabeca_grito"]) if grito else pc
    montar_pecas(b, e, pc_, "parado" if pose == "ataque" else pose, sem_braco_d=k is not None and k >= 0.25)
    if k is not None and k >= 0.25:  # o braço vindo pra frente, com o dedo apontando
        o, c, m_ = b.P(e["om_d"]), b.P(e["co_d"]), b.P(e["ma_d"])
        pc["braco"].desenhar(b.sup, o, c, 1, False)
        pc["antebraco"].desenhar(b.sup, c, m_, 1, False)
        pc["mao"].desenhar(b.sup, m_, (m_[0] + 4, m_[1] - 1), 1, False)
        pygame.draw.line(b.sup, (20, 18, 12), (m_[0] + 3, m_[1] - 2), (m_[0] + 7, m_[1] - 3), 3)  # o DEDO apontando
        pygame.draw.line(b.sup, pal["p"], (m_[0] + 3, m_[1] - 2), (m_[0] + 6, m_[1] - 3), 1)
    # a pele de lobo nos ombros e o colar de dentes
    for lado in ("e", "d"):
        ox, oy = b.P(e[f"om_{lado}"])
        pygame.draw.ellipse(b.sup, (150, 150, 158), (ox - 3, oy - 2, 7, 5))
        b.sup.set_at((int(ox), int(oy - 1)), (104, 104, 114))
    cx, cy = b.P((0, e["pe_coco"][1] - 4))
    for i in range(5):
        b.sup.set_at((int(cx - 4 + i * 2), int(cy + abs(i - 2) * 0.5)), (240, 236, 214))
    res = dict(olhos=(cab[0], cab[1]), mao=cabeca_lobo if k is not None else e["ma_d"], cabeca=cab)
    if k is not None:
        res["soltou"] = soltou
    return res


LOBO_X = 48


def _lobo_atras(b, pose, t, f):
    """O LOBO do Tamer, do lado e ATRÁS dele (desenhado antes); no E ele vem mordendo."""
    import tamer
    tamer.desenha_lobo(b.sup, b.ox + LOBO_X * b.k, b.oy, f.get("tam", 1.36) / 1.36, -1,
                       "morde" if pose == "ataque" else "corre" if pose == "pulo" else "parado", t,
                       f.get("lobo_cor", "branco"), tamer.skin_lobo_f(f))


# ---- JOHN, PIXEL POR PIXEL (e a CARTOLA DE LÂMINAS) ----
def _pecas_john(gatola=False):
    import john
    from pecas import Peca
    pal = dict(john.PALETA, r=(220, 30, 40), W=(250, 250, 250), a=(236, 150, 176))
    if gatola:  # (o GATOLA: gravata borboleta vermelha)
        pal["g"] = (220, 30, 40)
    cartola = [
            "...kkkkkkkkk...",
            "...krrrrrrrk...",
            "...kWWWWWWWk...",
            "...krrrrrrrk...",
            "...kWWWWWWWk...",
            "...krrrrrrrk...",
            "...kWWWWWWWk...",
            "...krrrrrrrk...",
            "...kWWWWWWWk...",
            "kkkkkkkkkkkkkkk",
            "krrrrrrrrrrrrrk",
            "kkkkkkkkkkkkkkk",
        ] if gatola else [
            "...kkkkkkkkk...",
            "...kfFfffffk...",
            "...kfFfffffk...",
            "...kfFfffffk...",
            "...kfFfffffk...",
            "...kvvvvvvvk...",
            "...kvvvvvvvk...",
            "kkkkkkkkkkkkkkk",
            "kfFfffffffffffk",
            "kkkkkkkkkkkkkkk",
        ]
    return dict(
        cabeca=Peca([
            "...kkkkkkk...",
            "..khhHhhhhk..",
            ".khhhhhHhhhk.",
            "khppppppppphk",
            "khpkkpppkkphk",
            "khppepppepphk",
            "kPpppppPpppPk",
            "kppmmmmmmppk.",
            ".kpmmpppmmpk.",
            "..kppqqqppk..",
            "...kppppPk...",
            "....kkkkk....",
        ], pal, a=(6, 11), b=(6, 0), estica=False),
        tronco=Peca([
            "..kkkkkkkkkk..",
            ".kffvwwwwvffk.",
            "kfFfvwggwvfFfk",
            "kfFfvwggwvfFfk",
            "kfFffvwwvffFfk",
            "kfFfffwwfffFfk",
            "kfFfffkkfffFfk",
            "kfFfffwwfffFfk",
            "kfFfffkkfffFfk",
            ".kfFffwwffFfk.",
            ".kfFffwwffFfk.",
            ".kvvvvvvvvvvk.",
            ".kcccccccccck.",
            ".kcccccccccck.",
            "..kcccccccck..",
            "...kkkkkkkk...",
        ], pal, a=(7, 14), b=(7, 1)),
        braco=john.BRACO,
        antebraco=john.ANTEBRACO,
        mao=john.MAO,
        coxa=john.COXA,
        canela=john.CANELA,
        sapato=Peca([
            ".kkkkk.",
            "kssSssk",
            "kkkkkkk",
        ], pal, a=(3, 0), b=(3, 2), estica=False),
        cartola=Peca(cartola, pal, a=(7, len(cartola) - 1), b=(7, 0), estica=False),
        coelho=Peca([
            "..k....k..",
            ".kwk..kwk.",
            ".kak..kak.",
            ".kak..kak.",
            ".kwk..kwk.",
            "..kwkkwk..",
            ".kwwwwwwk.",
            "kwwewwewwk",
            "kwwwaawwwk",
            ".kwwwwwwk.",
            ".kwLwwLwk.",
            "kwwLwwLwwk",
            "kwwwwwwwwk",
            ".kwwkkwwk.",
            "..kk..kk..",
        ], pal, a=(5, 14), b=(5, 0), estica=False),
    )


def _cartola_px(sup, centro, ang, pc, laminas=0.0):
    """A CARTOLA em pixel art girando (ang em radianos, 0 = em pé) com o centro em 'centro';
    laminas 0..1 = as 4 lâminas saindo da aba."""
    peca = pc["cartola"]
    meia = (peca.h - 1) / 2
    ux, uy = math.sin(ang), -math.cos(ang)  # (o "pra cima" da cartola)
    if laminas > 0:
        for i in range(4):
            a = ang + math.pi / 4 + i * math.pi / 2
            ca, sa = math.cos(a), math.sin(a)
            base = (centro[0] + ca * 5, centro[1] + sa * 5)
            ponta = (centro[0] + ca * (5 + 6 * laminas), centro[1] + sa * (5 + 6 * laminas))
            lado = (-sa * 1.6, ca * 1.6)
            pygame.draw.polygon(sup, (196, 202, 216), [(base[0] + lado[0], base[1] + lado[1]), ponta,
                                                       (base[0] - lado[0], base[1] - lado[1])])
            pygame.draw.line(sup, (255, 255, 255), base, ponta, 1)
    ini = (centro[0] - ux * meia, centro[1] - uy * meia)
    fim = (centro[0] + ux * meia, centro[1] + uy * meia)
    peca.desenhar(sup, ini, fim, 1, False)


def cartola_voando(tela, x, y, esc, ang, ficha, laminas=1.0):
    """A CARTOLA DE LÂMINAS voando na câmera, em pixel art (pra cena): (x, y) = o centro na tela;
    esc = tamanho de 1 pixel do jogo na tela (começa = UNID * escala e vai aumentando); ang = o giro
    (ela vem DE LADO, girando como um disco, com as lâminas passando na frente e atrás)."""
    gatola = ficha.get("estilo") == "gatola"
    pc = _peca("JOHN_G" if gatola else "JOHN", lambda: _pecas_john(gatola))
    pecas.usar_troca(ficha.get("troca"))
    try:
        peq = pygame.Surface((40, 40), pygame.SRCALPHA)
        # vem DE LADO: em pé (copa pra cima) girando em volta de si mesma, como um disco;
        # as lâminas saem da aba e passam por trás e pela frente enquanto gira
        peca = pc["cartola"]
        aba = (20, 20 + (peca.h - 1) / 2 - 1)
        def lamina(fase):
            ca, sa = math.cos(fase), math.sin(fase)
            base = (aba[0] + ca * 7, aba[1] + sa * 1.2)
            ponta = (aba[0] + ca * (7 + 7 * laminas), aba[1] + sa * 2.2)
            pygame.draw.polygon(peq, (196, 202, 216), [(base[0], base[1] - 1.5), ponta, (base[0], base[1] + 1.5)])
            pygame.draw.line(peq, (255, 255, 255), base, ponta, 1)
        fases = [ang + i * math.pi / 2 for i in range(4)]
        for fase in fases:  # as de TRÁS primeiro
            if math.sin(fase) < 0:
                lamina(fase)
        peca.desenhar(peq, (20, 20 + (peca.h - 1) / 2), (20, 20 - (peca.h - 1) / 2), 1, False)
        for fase in fases:  # e as da FRENTE por cima
            if math.sin(fase) >= 0:
                lamina(fase)
    finally:
        pecas.usar_troca(None)
    sil = pygame.mask.from_surface(peq, 60).to_surface(setcolor=(*PRETO, 255), unsetcolor=(0, 0, 0, 0))
    final = pygame.Surface((40, 40), pygame.SRCALPHA)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        final.blit(sil, (dx, dy))
    final.blit(peq, (0, 0))
    img = pygame.transform.scale(final, (round(40 * esc), round(40 * esc)))  # (pixels quadradinhos)
    tela.blit(img, (round(x - 20 * esc), round(y - 20 * esc)))


def _john(b, e, pose, t, f, prog=None):
    gatola = f.get("estilo") == "gatola"
    pc = _peca("JOHN_G" if gatola else "JOHN", lambda: _pecas_john(gatola))
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    soltou = k is not None and k >= 0.55
    pc_y = e["pe_coco"][1]
    if not gatola:  # o COELHINHO assistente do lado (pulando de leve)
        x, y = b.P((-34, 0))
        pc["coelho"].desenhar(b.sup, (x, y - round(abs(math.sin(t * 0.12)) * 2)), (x, y - 20), 1, False)
    no_ar = None  # (onde a cartola está, se não está na cabeça: centro em unidades, giro, lâminas)
    braco_frente = False
    if k is not None:
        if k < 0.15:  # a mão vai até a cartola
            a = k / 0.15
            e = dict(e, co_d=(22, 70 + 8 * a), ma_d=(16 - 10 * a, 50 + (pc_y + 14 - 50) * a))
        elif k < 0.45:  # JOGA pra cima: ela sobe girando e as lâminas saem da aba
            a = (k - 0.15) / 0.3
            e = dict(e, co_d=(26, pc_y + 6), ma_d=(16, pc_y + 22))  # (o braço ERGUIDO, a mão aberta embaixo dela)
            no_ar = ((14, pc_y + 30 + 20 * math.sin(a * math.pi)), a * 4 * math.pi, max(0.0, (a - 0.35) / 0.4))
        elif k < 0.55:  # pega e puxa pra trás (pegando impulso)
            a = (k - 0.45) / 0.1
            e = dict(e, co_d=(26, 74), ma_d=(16 + 8 * a, 70 + 4 * a))
            no_ar = ((e["ma_d"][0], e["ma_d"][1] + 4), 4 * math.pi + a * 3, 1.0)
        else:  # ARREMESSA na câmera (o braço vem pra frente)
            e = dict(e, co_d=(12, 70), ma_d=(4, 66))
            braco_frente = k < 0.8
    na_cabeca = k is None or k < 0.15
    montar_pecas(b, e, pc, "parado" if pose == "ataque" else pose, sem_braco_d=braco_frente)
    pescoco = b.P(e["pe_coco"])
    if na_cabeca:  # a CARTOLA na cabeça
        pc["cartola"].desenhar(b.sup, (pescoco[0], pescoco[1] - 8), (pescoco[0], pescoco[1] - 20), 1, False)
    elif no_ar:
        _cartola_px(b.sup, b.P(no_ar[0]), no_ar[1], pc, no_ar[2])
    if braco_frente:
        o, c, m_ = b.P(e["om_d"]), b.P(e["co_d"]), b.P(e["ma_d"])
        pc["braco"].desenhar(b.sup, o, c, 1, False)
        pc["antebraco"].desenhar(b.sup, c, m_, 1, False)
        pc["mao"].desenhar(b.sup, (m_[0], m_[1] - 3), (m_[0], m_[1] + 3), 1.5, False)
    cab = e["cab"]
    res = dict(olhos=(cab[0], cab[1] + 1), mao=e["ma_d"], cabeca=cab)
    if k is not None:
        res["soltou"] = soltou
    return res


LUTADORES = {
    "MAX-10": _max10, "KUN": _kun, "RIB": _rib, "KING RIP": _king, "CANNAN": _cannan, "FINN": _finn, "TAI": _tai,
    "TAMER": _tamer, "JOHN": _john,
}
LARGO = {"TAI": 1.25, "KING RIP": 1.0}


def tem_frente(ficha):
    return ficha.get("nome_base", ficha.get("nome")) in LUTADORES



# =====================================================================
# os BICHOS (corpo próprio, mas seguindo as juntas do esqueleto pra mexer nas 4 poses)
# =====================================================================
def _pernas(b, e, cor, cor2, larg=8):
    for lado in ("e", "d"):
        b.osso(e[f"qu_{lado}"], e[f"jo_{lado}"], larg + 1, cor, _clara(cor, 0.15))
        b.osso(e[f"jo_{lado}"], e[f"pe_{lado}"], larg, cor2)


def _bracos(b, e, cor, cor2, pose, larg=6, garra=None):
    for lado in ("e", "d"):
        if pose == "ataque" and lado == "d":
            continue
        b.osso(e[f"om_{lado}"], e[f"co_{lado}"], larg + 1, cor, _clara(cor, 0.15))
        b.osso(e[f"co_{lado}"], e[f"ma_{lado}"], larg, cor2)
        mx, my = e[f"ma_{lado}"]
        if garra:
            for k in (-1, 0, 1):
                b.linha((mx, my), (mx + k * 2, my - 4), garra, 0.9)


# ---- TROMOS, PIXEL POR PIXEL ----
def _pecas_tromos():
    import xeno
    from pecas import Peca
    pal = xeno.PALETA
    return dict(
        cabeca=Peca([
            "...kkkkk...",
            "..kxXXXxk..",
            ".kxXbbbXxk.",
            ".kxbbXbbxk.",
            "kxbbbXbbbxk",
            "kxbbbXbbbxk",
            "kxbbbXbbbxk",
            "kxbbbbbbbxk",
            "kbbbbbbbbbk",
            "kbyYbbbYybk",
            "kbbybbbybbk",
            ".kbbbbbbbk.",
            ".kbdkdkdbk.",
            "..kdkdkdk..",
            "...kkkkk...",
        ], pal, a=(5, 13), b=(5, 0), estica=False),
        cabeca_aberta=Peca([
            "...kkkkk...",
            "..kxXXXxk..",
            ".kxXbbbXxk.",
            ".kxbbXbbxk.",
            "kxbbbXbbbxk",
            "kxbbbXbbbxk",
            "kxbbbXbbbxk",
            "kxbbbbbbbxk",
            "kbbbbbbbbbk",
            "kbyYbbbYybk",
            "kbbybbbybbk",
            ".kdkkkkkdk.",
            ".kkkkkkkkk.",
            ".kdkkkkkdk.",
            "..kdkdkdk..",
            "...kkkkk...",
        ], pal, a=(5, 14), b=(5, 0), estica=False),
        tronco=xeno.TRONCO,
        braco=xeno.BRACO,
        antebraco=xeno.ANTEBRACO,
        mao=xeno.MAO,
        coxa=xeno.COXA,
        canela=xeno.CANELA,
        sapato=xeno.PE,
        _esc_cab=1.3,  # (um pouco mais CABEÇUDO: pedido do Gomes)
    )


def postura_predador(t):
    """O TROMOS curvado igual predador: pernas abertas e dobradas, garras pra frente, cabeça baixa."""
    r = math.sin(t * 0.1) * 0.8
    return dict(pe_e=(-18, 0), pe_d=(18, 0), jo_e=(-21, 22), jo_d=(21, 22), qu_e=(-7, 40), qu_d=(7, 40),
                om_e=(-13, 66 + r), om_d=(13, 66 + r), co_e=(-23, 56 + r), co_d=(23, 56 + r),
                ma_e=(-13, 48 + r), ma_d=(13, 48 + r), pe_coco=(0, 70 + r), cab=(0, 80 + r))


def _cauda_tromos(b, e, t):
    """A CAUDA CURVADA (do Tromos do Roblox) saindo pro lado, com o ferrão."""
    import xeno
    troca = pecas.TROCA or {}
    cor, escura, ferrao = troca.get("x", xeno.PALETA["x"]), troca.get("b", xeno.PALETA["b"]), troca.get("s", xeno.PALETA["s"])
    qd = e["qu_d"]
    pts = []
    for i in range(9):
        onda = math.sin(t * 0.12 + i * 0.5) * 0.8
        pts.append(b.P((qd[0] + 4 + i * 4, qd[1] - 4 + i * 2.6 - max(0, i - 4) ** 2 * 1.2 + onda)))
    for i, (a_, c_) in enumerate(zip(pts, pts[1:])):
        pygame.draw.line(b.sup, escura if i % 2 else cor, a_, c_, max(1, 3 - i // 3))
    x, y = pts[-1]
    pygame.draw.polygon(b.sup, ferrao, [(x - 2, y), (x + 2, y), (x, y + 4)])


def _tubos_tromos(b, e):
    """Os TUBOS das costas, aparecendo por cima dos ombros."""
    import xeno
    cor = (pecas.TROCA or {}).get("X", xeno.PALETA["X"])
    for lado, s_ in (("e", -1), ("d", 1)):
        om = e[f"om_{lado}"]
        for i in range(2):
            a_ = b.P((om[0] - s_ * 2, om[1] + 1))
            c_ = b.P((om[0] + s_ * (4 + i * 3), om[1] + 10 + i * 3))
            pygame.draw.line(b.sup, (8, 8, 12), a_, c_, 3)
            pygame.draw.line(b.sup, cor, a_, c_, 1)


def _acido(b, ponto, r, t, fios=False):
    """O ÁCIDO (gosma): forma irregular que tremelica, bolhas, brilho e fios de baba entre os dentes."""
    x, y = ponto
    escuro, verde, claro = (30, 80, 16), (120, 220, 50), (210, 255, 150)
    if fios:  # os fios de gosma esticando entre os dentes de cima e de baixo
        for dx in (-2, 0, 2):
            pygame.draw.line(b.sup, verde, (x + dx, y - r - 2), (x + dx * 0.6, y + r + 2), 1)
    pts = []
    for i in range(10):  # a bolha irregular (tremelicando)
        a = i * math.tau / 10
        rr = r * (1 + 0.22 * math.sin(t * 0.6 + i * 1.7))
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.9))
    pygame.draw.polygon(b.sup, escuro, [(px + (px - x) * 0.25, py + (py - y) * 0.25) for px, py in pts])
    pygame.draw.polygon(b.sup, verde, pts)
    if r >= 2:
        b.sup.set_at((int(x - r * 0.4), int(y - r * 0.4)), claro)  # o brilho
        if (t // 4) % 3 == 0:
            b.sup.set_at((int(x + r * 0.3), int(y + r * 0.1)), claro)  # uma bolha
    if (t // 3) % 2:  # pingando
        b.sup.set_at((int(x), int(y + r + 2)), verde)


def _tromos(b, e, pose, t, f, prog=None):
    pc = _peca("TROMOS", _pecas_tromos)
    if pose in ("parado", "ataque"):
        e = postura_predador(t)
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    soltou = k is not None and k >= 0.5
    aberta = k is not None and 0.3 <= k < 0.7
    if k is not None and k < 0.3:  # joga a cabeça pra TRÁS (puxando o ácido)
        a = k / 0.3
        e = dict(e, pe_coco=(e["pe_coco"][0], e["pe_coco"][1] + 3 * a), cab=(e["cab"][0], e["cab"][1] + 5 * a))
    elif k is not None and k < 0.55:  # e vem pra FRENTE cuspindo (a cabeça desce)
        e = dict(e, cab=(e["cab"][0], e["cab"][1] - 2))
    cab = e["cab"]
    _cauda_tromos(b, e, t)
    pc_ = dict(pc, cabeca=pc["cabeca_aberta"] if aberta else pc["cabeca"])
    montar_pecas(b, e, pc_, "parado" if pose == "ataque" else pose)
    _tubos_tromos(b, e)
    boca = (cab[0], cab[1] - 9)
    if k is not None and 0.3 <= k < 0.5:  # o ácido aparecendo na boca aberta
        _acido(b, b.P(boca), 1 + 2 * (k - 0.3) / 0.2, t, fios=True)
    res = dict(olhos=(cab[0], cab[1] - 2), mao=boca, cabeca=cab)
    if k is not None:
        res["soltou"] = soltou
    return res


# ---- CRÁQUEN, PIXEL POR PIXEL (o fantasma pirata, e a ÂNCORA) ----
def _pecas_craquen():
    import craquen
    from pecas import Peca
    pal = dict(craquen.PALETA, h=(22, 30, 40), W=(240, 240, 236), m=(150, 170, 178), M=(100, 118, 128),
               f=(236, 222, 184), F=(196, 178, 136), o=(255, 170, 60))
    return dict(
        cabeca=Peca([
            "......kkk......",
            "....kkhhhkk....",
            "kk.khhWWWhhk.kk",
            "khkhhhWkWhhhkhk",
            "khhhhhhWhhhhhhk",
            ".kgghhhhhhhggk.",
            "..kkgggggggkk..",
            "...kpppppppk...",
            "..kpPpppppPpk..",
            "..kpeepppeepk..",
            "..kppppPppppk..",
            "..kaaaaaaaaak..",
            "..kaAaaAaaAak..",
            "...kaAaaaAak...",
            "....kaaAaak....",
            ".....kaAak.....",
            "......kak......",
            ".......k.......",
        ], pal, a=(7, 11), b=(7, 0), estica=False),
        mumia=Peca([
            "....kkkkkkk....",
            "...kfffFfffk...",
            "..kFfffffFffk..",
            ".kffFffffffFk..",
            ".kfffffFffffk..",
            ".kFfffffffFfk..",
            "..kffFfffFffk..",
            "..kfffffffffk..",
            "..kfoofffoofk..",
            "..kffffFffffk..",
            "..kFfffffFfk...",
            "...kfffFffk....",
            "....kkkkkk.....",
        ], pal, a=(7, 12), b=(7, 0), estica=False),
        tronco=Peca([
            "..kkkkkkkkkk..",
            ".kcCcwwwwcCck.",
            "kcCcvwwwwvcCck",
            "kcCgvwwwwvgCck",
            "kcCccvwwvccCck",
            "kcCgccwwccgCck",
            "kcCcccwwcccCck",
            "kcCgccwwccgCck",
            "kcCcccwwcccCck",
            ".kbbbbbbbbbbk.",
            ".kbbbbggbbbbk.",
            ".kcccccccccck.",
            ".kcccccccccck.",
            "..kcccccccck..",
            "...kkkkkkkk...",
        ], pal, a=(7, 13), b=(7, 1)),
        braco=craquen.BRACO,
        antebraco=craquen.ANTEBRACO,
        mao=craquen.MAO,
        ancora=Peca([
            ".....mmm.....",
            "....m...m....",
            "....m...m....",
            ".....mmm.....",
            "...mmmWmmm...",
            "...MMMmMMM...",
            ".....WmM.....",
            ".....WmM.....",
            ".....WmM.....",
            ".....WmM.....",
            "W....WmM....M",
            "Wm...WmM...mM",
            ".Wm..WmM..mM.",
            "..WmmWmMmmM..",
            "...mmmmmmm...",
            ".....mmm.....",
        ], pal, a=(6, 1), b=(6, 15), estica=False),
        ancora_ponta=Peca([
            "WW.................WW",
            "WmW...............WmW",
            "mmmm.............mmmm",
            "..mm.....MMM.....mm..",
            "...mm...M...M...mm...",
            "....mm...MMM...mm....",
            ".....mmm..M..mmm.....",
            ".......mmmWmmm.......",
            "........mWWWm........",
            ".........mmm.........",
        ], pal, a=(0, 5), b=(20, 5), estica=False),  # (vindo com as UNHAS apontando pra câmera)
    )


def _cauda_craquen(b, e, t):
    """No lugar das pernas: a CAUDA DE FANTASMA, afinando e ondulando até uma pontinha."""
    import craquen
    troca = pecas.TROCA or {}
    cor, escura, clara = (troca.get(c, craquen.PALETA[c]) for c in ("c", "v", "C"))
    qe, qd = b.P(e["qu_e"]), b.P(e["qu_d"])
    topo = ((qe[0] + qd[0]) / 2, (qe[1] + qd[1]) / 2 - 2)
    ponta = (topo[0] + 8 + math.sin(t * 0.12) * 2, b.oy - 3)
    ctrl = (topo[0] - 5, (topo[1] + ponta[1]) / 2)
    esq, dir_ = [], []
    for i in range(13):
        u = i / 12
        x = (1 - u) ** 2 * topo[0] + 2 * (1 - u) * u * ctrl[0] + u * u * ponta[0]
        y = (1 - u) ** 2 * topo[1] + 2 * (1 - u) * u * ctrl[1] + u * u * ponta[1]
        larg = 8 * (1 - u) ** 0.8 + 0.6 + math.sin(t * 0.2 + u * 9) * 0.8 * u
        esq.append((x - larg, y))
        dir_.append((x + larg, y))
    pygame.draw.polygon(b.sup, cor, esq + dir_[::-1])
    pygame.draw.lines(b.sup, escura, False, dir_[:-1], 2)  # a sombra do lado
    pygame.draw.lines(b.sup, clara, False, [(x + 2, y) for x, y in esq[1:-3]], 1)  # o brilho


def _capa_vampiro_frente(b, e):
    """VAMPIRO: a capa preta (vermelha por dentro) atrás dele, com a gola alta."""
    oe, od = b.P(e["om_e"]), b.P(e["om_d"])
    baixo = b.oy - 6
    pygame.draw.polygon(b.sup, (20, 14, 20), [(oe[0] - 3, oe[1] - 6), (od[0] + 3, od[1] - 6), (od[0] + 9, baixo),
                                              (oe[0] - 9, baixo)])
    pygame.draw.polygon(b.sup, (150, 20, 30), [(oe[0], oe[1]), (od[0], od[1]), (od[0] + 5, baixo - 2),
                                               (oe[0] - 5, baixo - 2)])


def _ancora_px(sup, pc, ini, fim):
    """A âncora em pixel: o anel em 'ini', apontando pra 'fim'."""
    pc["ancora"].desenhar(sup, ini, fim, 1, False)


def _corrente(sup, a_, b_, n=None):
    n = n or max(2, int(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) / 2))
    for i in range(n + 1):
        u = i / n
        x, y = a_[0] + (b_[0] - a_[0]) * u, a_[1] + (b_[1] - a_[1]) * u
        sup.set_at((int(x), int(y)), (150, 170, 176) if i % 2 else (90, 104, 112))


def ancora_voando(tela, x, y, esc, ficha, giro=0.0):
    """A ÂNCORA vindo na câmera, em pixel art (pra cena): (x, y) = o meio dela na tela;
    esc = tamanho de 1 pixel do jogo na tela (começa = UNID * escala e vai aumentando);
    ela vem com as UNHAS apontando pra câmera, sem girar (giro não é usado)."""
    pc = _peca("CRÁQUEN", _pecas_craquen)
    # vem com as UNHAS APONTANDO PRA CÂMERA (escolha do Gomes): a coroa embaixo no meio, as unhas subindo
    # pros lados num "U" até as pontas largas, e o anel pequeno lá atrás
    peq = pygame.Surface((28, 28), pygame.SRCALPHA)
    pc["ancora_ponta"].desenhar(peq, (14 - 10, 14), (14 + 10, 14), 1, False)
    sil = pygame.mask.from_surface(peq, 60).to_surface(setcolor=(*PRETO, 255), unsetcolor=(0, 0, 0, 0))
    final = pygame.Surface((28, 28), pygame.SRCALPHA)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        final.blit(sil, (dx, dy))
    final.blit(peq, (0, 0))
    img = pygame.transform.scale(final, (round(28 * esc), round(28 * esc)))  # (pixels quadradinhos)
    tela.blit(img, (round(x - 14 * esc), round(y - 14 * esc)))


def _craquen(b, e, pose, t, f, prog=None):
    pc = _peca("CRÁQUEN", _pecas_craquen)
    estilo = f.get("estilo")
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    soltou = k is not None and k >= 0.5
    sobe = 8 + 2 * math.sin(t * 0.08)  # FLUTUANDO
    e = {n: (v[0], v[1] + sobe) for n, v in e.items()}
    ancora = None  # (mão, anel, ponta) da âncora girando, em pixels
    atras = False  # (na metade da volta em que ela passa por TRÁS do corpo)
    if k is not None:
        if k < 0.4:  # GIRA a âncora na corrente, do lado dele
            e = dict(e, co_d=(30, 64 + sobe), ma_d=(36, 74 + sobe))
            ang = k / 0.4 * 4 * math.pi
            mao = b.P(e["ma_d"])
            r = 8 + 4 * min(1.0, k / 0.15)
            ca, sa = math.cos(ang) * 0.45, math.sin(ang)  # (girando do LADO do corpo: a roda fica estreita)
            anel = (mao[0] + 3 + ca * r, mao[1] + sa * r)
            ancora = (mao, anel, (anel[0] + ca * 14, anel[1] + sa * 14))
            atras = ca < 0
        elif not soltou:  # leva o braço lá atrás e vem pra frente
            a = (k - 0.4) / 0.1
            e = dict(e, co_d=(24, 78 + sobe), ma_d=(26 - 18 * a, 92 + sobe - 20 * a))
            mao = b.P(e["ma_d"])
            ancora = (mao, (mao[0], mao[1] - 3), (mao[0], mao[1] - 17))
        else:  # SOLTOU: o braço esticado pra frente segurando a corrente (e depois PUXA)
            a = max(0.0, (k - 0.8) / 0.2)
            e = dict(e, co_d=(12 + 10 * a, 70 + sobe), ma_d=(4 + 16 * a, 66 + sobe - 6 * a))
    if ancora and atras:  # passando por trás dele
        _corrente(b.sup, ancora[0], ancora[1])
        _ancora_px(b.sup, pc, ancora[1], ancora[2])
    if estilo == "vampiro":
        _capa_vampiro_frente(b, e)
    _cauda_craquen(b, e, t)
    P = b.P
    meio_q = P(((e["qu_e"][0] + e["qu_d"][0]) / 2, (e["qu_e"][1] + e["qu_d"][1]) / 2))
    pc["tronco"].desenhar(b.sup, meio_q, P(e["pe_coco"]), 1, False)
    pescoco = P(e["pe_coco"])
    mumia = estilo == "mumia"
    pc["mumia" if mumia else "cabeca"].desenhar(b.sup, (pescoco[0], pescoco[1] + 1), (pescoco[0], pescoco[1] - 10), 1, False)
    if estilo == "vampiro":  # as PRESAS
        for dx in (-2, 2):
            b.sup.set_at((int(pescoco[0] + dx), int(pescoco[1] - 1)), (250, 250, 250))
    frente_d = soltou and k < 0.8
    for lado, esp in (("e", True), ("d", False)):
        if lado == "d" and frente_d:
            continue
        o, c, m_ = P(e[f"om_{lado}"]), P(e[f"co_{lado}"]), P(e[f"ma_{lado}"])
        pc["antebraco"].desenhar(b.sup, c, m_, 1, esp)
        pc["mao"].desenhar(b.sup, m_, (m_[0] + (m_[0] - c[0]) * 0.2, m_[1] + 4), 1, esp)
        pc["braco"].desenhar(b.sup, o, c, 1, esp)
    if k is None:  # a ESPADA fantasma na mão (fora do E)
        mx, my = P(e["ma_d"])
        pygame.draw.line(b.sup, (8, 26, 34), (mx + 1, my + 2), (mx + 7, my - 12), 3)
        pygame.draw.line(b.sup, (200, 245, 240), (mx + 1, my + 2), (mx + 7, my - 12), 1)
        pygame.draw.rect(b.sup, (226, 196, 90), (mx - 1, my, 4, 2))
    if ancora and not atras:  # a âncora girando na corrente (passando na frente)
        _corrente(b.sup, ancora[0], ancora[1])
        _ancora_px(b.sup, pc, ancora[1], ancora[2])
    if frente_d:  # o braço vindo pra frente (mão grande) com a corrente saindo na direção da câmera
        o, c, m_ = P(e["om_d"]), P(e["co_d"]), P(e["ma_d"])
        pc["braco"].desenhar(b.sup, o, c, 1, False)
        pc["antebraco"].desenhar(b.sup, c, m_, 1, False)
        _corrente(b.sup, m_, (m_[0] - 3, m_[1] + 12))
        pc["mao"].desenhar(b.sup, (m_[0], m_[1] - 3), (m_[0], m_[1] + 3), 1.5, False)
    elif soltou:  # puxando: a corrente esticada voltando
        m_ = P(e["ma_d"])
        _corrente(b.sup, m_, (m_[0] - 10, m_[1] + 6))
    cab = e["cab"]
    res = dict(olhos=(cab[0], cab[1] + 1), mao=e["ma_d"], cabeca=cab)
    if k is not None:
        res["soltou"] = soltou
    return res


# ---- MAGNUS, PIXEL POR PIXEL (o raptor-robô de fogo, e os ESPINHOS da nuca) ----
def _pecas_magnus():
    import magnus
    from pecas import Peca
    pal = dict(magnus.PALETA, k=(10, 8, 10), w=(250, 248, 236), r=(60, 20, 24))
    return dict(
        cabeca=Peca([
            "....kkkkkkk....",
            "...kccMMMcck...",
            "..kmccMMMccmk..",
            ".kmmmcbbbcmmmk.",
            "kkmmmmmmmmmmmkk",
            "kBBkmmmmmmmkBBk",
            "kMkMmmmmmmmMkMk",
            ".kMMmmmmmmmMMk.",
            "..kMmkmmmkmMk..",
            "..kwMmmmmmMwk..",
            "..kwwrrrrrwwk..",
            "...kwrrrrrwk...",
            "...kMwMwMwMk...",
            "....kMMMMMk....",
            ".....kkkkk.....",
        ], pal, a=(7, 14), b=(7, 0), estica=False),
        tronco=Peca([
            "....kkkkkkk....",
            "....kmmcmmk....",
            "...kmMmcmMmk...",
            "..kmMbmcmbMmk..",
            ".kmmmbcccbmmmk.",
            "kmMmmcccccmmMmk",
            "kmMbmcccccmbMmk",
            "kmmmbcccccbmmmk",
            "kmMmmcccccmmMmk",
            "kmMbmcccccmbMmk",
            "kmmmmcccccmmmmk",
            ".kmmmmcccmmmmk.",
            "..kMmmmmmmmMk..",
            "...kkkkkkkkk...",
        ], pal, a=(7, 12), b=(7, 1)),
        braco=Peca([
            ".kk.",
            "kmmk",
            "kmMk",
            "kmMk",
            ".kk.",
        ], pal, a=(2, 0), b=(2, 4)),
        antebraco=Peca([
            ".kk.",
            "kMmk",
            "kMmk",
            "kMmk",
            ".kk.",
        ], pal, a=(2, 0), b=(2, 4)),
        mao=Peca([
            "kmmmk",
            "wkwkw",
            "w.w.w",
        ], pal, a=(2, 0), b=(2, 2), estica=False),
        coxa=Peca([
            "kkkkkk",
            "kmmcmk",
            "kmbmck",
            "kmbmmk",
            "kMbmmk",
            ".kMmk.",
            ".kkkk.",
        ], pal, a=(3, 0), b=(3, 6)),
        canela=Peca([
            ".kk.",
            "kMMk",
            "kMMk",
            "kMMk",
            "kMMk",
            ".kk.",
        ], pal, a=(2, 0), b=(2, 5)),
        sapato=Peca([
            "..kkk..",
            ".kMMMk.",
            "kMMMMMk",
            "wkwkwkw",
        ], pal, a=(3, 0), b=(3, 3), estica=False),
    )


def postura_raptor(t):
    """O MAGNUS de frente: agachado de raptor, pernas abertas e dobradas, bracinhos encolhidos, pescoço comprido."""
    r = math.sin(t * 0.1) * 0.8
    return dict(pe_e=(-17, 0), pe_d=(17, 0), jo_e=(-21, 20), jo_d=(21, 20), qu_e=(-9, 38), qu_d=(9, 38),
                om_e=(-11, 62 + r), om_d=(11, 62 + r), co_e=(-17, 54 + r), co_d=(17, 54 + r),
                ma_e=(-11, 48 + r), ma_d=(11, 48 + r), pe_coco=(0, 66 + r), cab=(0, 88 + r))


def _cores_magnus():
    import magnus
    troca = pecas.TROCA or {}
    return {c: troca.get(c, magnus.PALETA[c]) for c in "mMcbB"}


def _cauda_magnus(b, e, t, blue):
    """A CAUDA saindo pro lado (atrás dele), dura, com anéis de brasa e a ponta acesa."""
    c = _cores_magnus()
    q = b.P(((e["qu_e"][0] + e["qu_d"][0]) / 2 + 4, e["qu_d"][1] - 2))
    pts = []
    for i in range(8):
        onda = math.sin(t * 0.08 + i * 0.4) * 0.8
        pts.append((q[0] + 3 + i * 2.8, q[1] + 4 + i * 0.4 - max(0, i - 4) ** 2 * 0.7 + onda))
    for i, (a_, c_) in enumerate(zip(pts, pts[1:])):
        pygame.draw.line(b.sup, c["m"], a_, c_, max(1, 5 - i // 2))
        if i % 2 == 1 and not blue:
            pygame.draw.line(b.sup, c["b"], (a_[0], a_[1] - 1), (a_[0], a_[1] + 1), 1)
    if not blue:
        b.sup.set_at((int(pts[-1][0]), int(pts[-1][1])), c["B"])


def _crista_magnus(b, centro, penas, t, sobra=6):
    """A CRISTA de espinhos de fogo em cima da cabeça (vista de frente é um TUFO estreito pra cima, tipo moicano —
    não uma juba em volta). penas 0..1 = tamanho; sobra = quantos ainda estão lá (os de fora saem primeiro)."""
    c = _cores_magnus()
    x, y = centro
    ordem = (2, 3, 1, 4, 0, 5)  # (do meio pra fora: os de fora saem primeiro nos tiros)
    for n_, i in enumerate(ordem):
        if n_ >= sobra:
            continue
        lado = i - 2.5
        a = -math.pi / 2 + lado * 0.05  # (em pé, bem juntinhos)
        tam = (8 - abs(lado) * 1.3) * penas * (0.92 + 0.08 * math.sin(t * 0.1 + i))  # (baixinha: pedido do Gomes)
        base = (round(x + lado * 1.2), y - 5)
        ponta = (base[0] + math.cos(a) * tam, base[1] + math.sin(a) * tam)
        pygame.draw.line(b.sup, c["b"] if i % 2 else c["B"], base, ponta, 1)  # (...e fininho na ponta)
        b.sup.set_at((int(ponta[0]), int(ponta[1])), c["B"])


E_TIROS_MAGNUS = (0.22, 0.3, 0.38, 0.46, 0.54, 0.62)


def espinho_voando(tela, x, y, esc, ficha, lado=1):
    """Um ESPINHO de fogo vindo na câmera, em pixel art (pra cena): (x, y) = o meio dele na tela;
    esc = tamanho de 1 pixel do jogo (começa = UNID * escala e vai aumentando).
    Vem com a PONTA reta pra câmera: um CONE de fogo visto de frente (ponta acesa no meio, anéis de brasa
    em volta). (lado não é usado.)"""
    import magnus
    troca = (ficha.get("troca") or {})
    cores = {"b": troca.get("b", magnus.BRASA), "B": troca.get("B", magnus.BRASA_CLARA), "W": (255, 244, 210)}
    # (um CONE de fogo visto de frente — escolha do Gomes: a ponta acesa no meio e anéis de brasa em volta,
    # escurecendo até a borda)
    peq = pygame.Surface((11, 11), pygame.SRCALPHA)
    escura = tuple(max(0, int(v * 0.62)) for v in cores["b"])
    pygame.draw.circle(peq, escura, (5, 5), 5)
    pygame.draw.circle(peq, cores["b"], (5, 5), 4)
    for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):  # as "faces" da ponta (riscos do meio pra borda)
        for r in (2, 3, 4):
            peq.set_at((5 + dx * r, 5 + dy * r), escura)
    for px, py in ((5, 4), (5, 6), (4, 5), (6, 5)):
        peq.set_at((px, py), cores["B"])
    peq.set_at((5, 5), cores["W"])  # a PONTA acesa
    sil = pygame.mask.from_surface(peq, 60).to_surface(setcolor=(*PRETO, 255), unsetcolor=(0, 0, 0, 0))
    final = pygame.Surface((13, 13), pygame.SRCALPHA)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        final.blit(sil, (1 + dx, 1 + dy))
    final.blit(peq, (1, 1))
    img = pygame.transform.scale(final, (round(13 * esc), round(13 * esc)))
    tela.blit(img, (round(x - 6.5 * esc), round(y - 6.5 * esc)))


def _magnus(b, e, pose, t, f, prog=None):
    pc = _peca("MAGNUS", _pecas_magnus)
    blue = f.get("estilo") == "blue"
    if pose in ("parado", "ataque"):
        e = postura_raptor(t)
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    penas, sobra, tiro = (0.0 if blue else 0.8 + 0.2 * math.sin(t * 0.06)), 6, False
    if k is not None and not blue:
        if k < 0.2:  # ARREPIA a crista (os espinhos crescem) e abaixa a cabeça
            a = k / 0.2
            penas = 1.0 + 0.3 * a
            e = dict(e, cab=(e["cab"][0], e["cab"][1] - 3 * a), pe_coco=(0, e["pe_coco"][1] - 1.5 * a))
        else:  # ATIRA: cada tiro, um espinho sai da crista
            penas = 1.3
            sobra = 6 - sum(1 for st in E_TIROS_MAGNUS if k >= st)
            tiro = any(st <= k < st + 0.03 for st in E_TIROS_MAGNUS)
            tranco = 1.5 if tiro else 0  # (a cabeça dá um tranco a cada tiro)
            e = dict(e, cab=(e["cab"][0], e["cab"][1] - 3 + tranco))
    _cauda_magnus(b, e, t, blue)
    P = b.P
    for lado, esp in (("e", True), ("d", False)):  # pernas de raptor
        q, j, pe = P(e[f"qu_{lado}"]), P(e[f"jo_{lado}"]), P(e[f"pe_{lado}"])
        pc["canela"].desenhar(b.sup, j, pe, 1, esp)
        pc["coxa"].desenhar(b.sup, q, j, 1, esp)
        pc["sapato"].desenhar(b.sup, (pe[0], pe[1] - 3), (pe[0], pe[1] + 1), 1, esp)
    meio_q = P(((e["qu_e"][0] + e["qu_d"][0]) / 2, (e["qu_e"][1] + e["qu_d"][1]) / 2))
    pc["tronco"].desenhar(b.sup, meio_q, P(e["pe_coco"]), 1, False)
    c = _cores_magnus()
    pescoco, cab = P(e["pe_coco"]), P(e["cab"])
    pygame.draw.line(b.sup, c["m"], pescoco, (cab[0], cab[1] + 5), 5)  # o PESCOÇO comprido
    pygame.draw.line(b.sup, c["c"], pescoco, (cab[0], cab[1] + 5), 1)
    if penas > 0.05:
        _crista_magnus(b, (cab[0], cab[1] - 2), penas, t, sobra)
    pc["cabeca"].desenhar(b.sup, (cab[0], cab[1] + 7), (cab[0], cab[1] - 7), 1, False)
    for lado, esp in (("e", True), ("d", False)):  # os bracinhos com 3 garras
        o, co, ma = P(e[f"om_{lado}"]), P(e[f"co_{lado}"]), P(e[f"ma_{lado}"])
        pc["antebraco"].desenhar(b.sup, co, ma, 1, esp)
        pc["mao"].desenhar(b.sup, ma, (ma[0], ma[1] + 2), 1, esp)
        pc["braco"].desenhar(b.sup, o, co, 1, esp)
    res = dict(olhos=(e["cab"][0], e["cab"][1] + 2), mao=(e["cab"][0], e["cab"][1] + 6), cabeca=e["cab"])
    if k is not None:
        res["soltou"] = k >= E_TIROS_MAGNUS[0]
        res["tiro"] = tiro
    return res


# ---- SPHYRUS, PIXEL POR PIXEL (o martelo de frente, e a ONDA DE AR) ----
def _pecas_sphyrus():
    import sphyrus
    from pecas import Peca
    pal = dict(sphyrus.PALETA, k=(10, 10, 16), w=(250, 250, 236), r=(110, 20, 30), b=(180, 180, 104),
               x=(140, 70, 70))
    return dict(
        cabeca=Peca([
            ".......kkkkkkkkkkkkk.......",
            "...kkkkmmmmmmmmmmmmmkkkk...",
            ".kkmmmmmmmmmmmmmmmmmmmmmkk.",
            "kooMmmmmmmmmmmmmmmmmmmmMook",
            "kokMMmmmmmmmmmmmmmmmmmMMkok",
            ".kkkkMMmmmmmmmmmmmmmMMkkkk.",
            "......kMmmmmmmmmmmmMk......",
            "......kMmmmmmmmmmmmMk......",
            "......kMmmmmkmkmmmmMk......",
            "......kwwmmmmmmmmmwwk......",
            "......krwwwwwwwwwwwrk......",
            "......krrrrrrrrrrrrrk......",
            "......kawawawawawawak......",
            ".......kaaaaaaaaaaak.......",
            "........kaaaaaaaaak........",
            ".........kkkkkkkkk.........",
        ], pal, a=(13, 15), b=(13, 0), estica=False),
        cabeca_costas=Peca([
            ".......kkkkkkkkkkkkk.......",
            "...kkkkmmmmmmmmmmmmmkkkk...",
            ".kkmmmmmmmmmmmmmmmmmmmmmkk.",
            "kooMmmmmmmmmmmmmmmmmmmmMook",
            "kokMMmmmmmmmmmmmmmmmmmMMkok",
            ".kkkkMMmmmmmmmmmmmmmMMkkkk.",
            "......kMmmmmmmmmmmmMk......",
            "......kMmmmmmmmmmmmMk......",
            "......kMmmmmmmmmmmmMk......",
            "......kMmmmmmmmmmmmMk......",
            "......kMmmmmmmmmmmMk.......",
            ".......kMmmmmmmmmmMk.......",
            ".......kMmmmmmmmmMk........",
            "........kMmmmmmmMk.........",
            ".........kMmmmmMk..........",
            "..........kkkkkkk..........",
        ], pal, a=(13, 15), b=(13, 0), estica=False),
        mega=Peca([
            ".........kkkkkkk.........",
            "........kmmmmmmmk........",
            ".......kmmmmmmmmmk.......",
            "......kkkmmmmmmmkkk......",
            "......kkkmmmmmmmkkk......",
            "......kmmmmmmmmmmmk......",
            ".......kwkwkwkwkwk.......",
            ".......krrrrrrrrrk.......",
            ".......kwkwkwkwkwk.......",
            "........kaaaaaaak........",
            ".........kkkkkkk.........",
        ], pal, a=(12, 10), b=(12, 0), estica=False),
        tronco=Peca([
            "..kkkkkkkkkkk..",
            ".kMmmmaaammmMk.",
            "kMkmlmaaamlmkMk",
            "kMkmlmbbbmlmkMk",
            "kMkmlmaaamlmkMk",
            "kMmmlmaxamlmmMk",
            "kMmmlmbbbmlmmMk",
            ".kMmlmaaamlmMk.",
            ".kMmlmaaamlmMk.",
            ".kMmmlbbblmmMk.",
            ".kMmmmaaammmMk.",
            ".kMmmmmammmmMk.",
            ".kMmmmmmmmmmMk.",
            "..kkkkkkkkkkk..",
        ], pal, a=(7, 12), b=(7, 1)),
        tronco_costas=Peca([
            "..kkkkkkkkkkk..",
            ".kMmmmmmmmmmMk.",
            "kMmmlmmmmmlmmMk",
            "kMmmlmmmmmlmmMk",
            "kMmmlmmmmmlmmMk",
            "kMmmlmmmmmlmmMk",
            "kMmmlmmmmmlmmMk",
            ".kMmlmmmmmlmMk.",
            ".kMmlmmmmmlmMk.",
            ".kMmmlmmmlmmMk.",
            ".kMmmmmmmmmmMk.",
            ".kMmmmmmmmmmMk.",
            ".kMmmmmmmmmmMk.",
            "..kkkkkkkkkkk..",
        ], pal, a=(7, 12), b=(7, 1)),
        costelas=Peca([
            "...kkkkkkkkk...",
            "...kmaamaamk...",
            "..kmmmmmmmmmk..",
            ".kmaaaamaaaamk.",
            ".kmmmmmmmmmmmk.",
            ".kaaaaamaaaaak.",
            ".kmmmmmmmmmmmk.",
            ".kaaaaamaaaaak.",
            ".kmmmmmmmmmmmk.",
            ".kaaaaamaaaak..",
            ".kaaaaamaaaak..",
            "..kaaaamaaak...",
            "...kammmmmak...",
            "....kkkkkkk....",
        ], pal, a=(7, 12), b=(7, 1)),
        braco=Peca([
            ".kk.",
            "kmmk",
            "kmMk",
            "kmMk",
            ".kk.",
        ], pal, a=(2, 0), b=(2, 4)),
        antebraco=Peca([
            ".kk.",
            "kmMk",
            "kmMk",
            "kmMk",
            ".kk.",
        ], pal, a=(2, 0), b=(2, 4)),
        mao=Peca([
            "kmmmk",
            "wkwkw",
            "w.w.w",
        ], pal, a=(2, 0), b=(2, 2), estica=False),
        coxa=Peca([
            "kkkkkk",
            "kmmmMk",
            "kmmmMk",
            "kmmmMk",
            "kmmMMk",
            ".kmMk.",
            ".kkkk.",
        ], pal, a=(3, 0), b=(3, 6)),
        canela=Peca([
            ".kk.",
            "kmMk",
            "kmMk",
            "kmMk",
            "kmMk",
            ".kk.",
        ], pal, a=(2, 0), b=(2, 5)),
        sapato=Peca([
            "..kkk..",
            ".kmmmk.",
            "kmmmmmk",
            "wkwkwkw",
        ], pal, a=(3, 0), b=(3, 3), estica=False),
    )


def _cores_sphyrus():
    import sphyrus
    troca = pecas.TROCA or {}
    return {c: troca.get(c, sphyrus.PALETA[c]) for c in "mMalo"}


def _cauda_sphyrus(b, e, t, giro=0.0):
    """A CAUDA EM V atrás (aparece pro lado, entre as pernas). giro: no E ela chicoteia em volta."""
    c = _cores_sphyrus()
    q = b.P((0, e["qu_d"][1] - 2))
    ang = 0.5 + math.sin(t * 0.08) * 0.08 + giro
    dx = math.cos(ang)
    base = (q[0] + 2 * dx, q[1] + 2)
    ponta = (q[0] + 16 * dx, q[1] + 10)
    pygame.draw.line(b.sup, c["m"], base, ponta, 5)
    pygame.draw.line(b.sup, c["l"], base, (ponta[0] - 2 * dx, ponta[1] - 1), 1)
    sx = 1 if dx >= 0 else -1
    pygame.draw.polygon(b.sup, c["m"], [(ponta[0], ponta[1] - 2), (ponta[0] + 9 * sx, ponta[1] - 11),
                                        (ponta[0] + 5 * sx, ponta[1] + 1)])  # o V: o lobo de cima (maior)
    pygame.draw.polygon(b.sup, c["M"], [(ponta[0], ponta[1] + 1), (ponta[0] + 7 * sx, ponta[1] + 7),
                                        (ponta[0] + 5 * sx, ponta[1] + 1)])  # e o de baixo


def _espinhos_braco(b, om, co, lado):
    """Os ESPINHOS de peixe-leão saindo do braço (pra fora), no lugar da asinha."""
    o, k_ = b.P(om), b.P(co)
    for u in (0.35, 0.8):
        x, y = o[0] + (k_[0] - o[0]) * u, o[1] + (k_[1] - o[1]) * u
        pygame.draw.line(b.sup, (230, 230, 220), (x + lado * 2, y), (x + lado * 6, y - 4), 1)


def _desenha_sphyrus(b, e, pc, t, f, costas=False, giro_cauda=0.0, onda=0.0):
    estilo = f.get("estilo")
    c = _cores_sphyrus()
    P = b.P
    _cauda_sphyrus(b, e, t, giro_cauda)
    for lado, esp in (("e", True), ("d", False)):  # pernas de raptor
        q, j, pe = P(e[f"qu_{lado}"]), P(e[f"jo_{lado}"]), P(e[f"pe_{lado}"])
        pc["canela"].desenhar(b.sup, j, pe, 1, esp)
        pc["coxa"].desenhar(b.sup, q, j, 1, esp)
        pc["sapato"].desenhar(b.sup, (pe[0], pe[1] - 3), (pe[0], pe[1] + 1), 1, esp)
    meio_q = P(((e["qu_e"][0] + e["qu_d"][0]) / 2, (e["qu_e"][1] + e["qu_d"][1]) / 2))
    tr = "tronco_costas" if costas else ("costelas" if estilo == "esqueleto" else "tronco")
    pc[tr].desenhar(b.sup, meio_q, P(e["pe_coco"]), 1, False)
    pescoco, cab = P(e["pe_coco"]), P(e["cab"])
    nome_cab = "cabeca_costas" if costas else ("mega" if estilo == "megalodonte" else "cabeca")
    # (sem pescoço comprido: a cabeça vai direto em cima do corpo, igual tubarão)
    pc[nome_cab].desenhar(b.sup, (pescoco[0], pescoco[1] + 3), (pescoco[0], pescoco[1] - 8), 1, False)
    if costas:  # a BARBATANA DORSAL rasgada (com o CÓDIGO DE BARRAS), no meio das costas, por cima de tudo
        x0, y0 = pescoco[0], pescoco[1] + 16
        pygame.draw.polygon(b.sup, c["M"], [(x0 - 3, y0), (x0 + 3, y0), (x0 + 1, y0 - 16), (x0 - 1, y0 - 13)])
        pygame.draw.line(b.sup, c["m"], (x0 - 1, y0), (x0, y0 - 14), 1)
        for i in range(3):  # o código de barras
            b.sup.set_at((int(x0 - 1 + i), int(y0 - 5)), (10, 10, 16))
            b.sup.set_at((int(x0 - 1 + i * 2), int(y0 - 7)), (10, 10, 16))
    if not costas:  # a COLEIRA de metal quebrada (os dois pedaços)
        pygame.draw.line(b.sup, (150, 156, 166), (pescoco[0] - 6, pescoco[1] + 4), (pescoco[0] - 2, pescoco[1] + 4), 2)
        pygame.draw.line(b.sup, (150, 156, 166), (pescoco[0] + 2, pescoco[1] + 5), (pescoco[0] + 5, pescoco[1] + 4), 2)
    for lado, esp in (("e", True), ("d", False)):  # os braços com 3 garras
        o, co, ma = P(e[f"om_{lado}"]), P(e[f"co_{lado}"]), P(e[f"ma_{lado}"])
        pc["antebraco"].desenhar(b.sup, co, ma, 1, esp)
        pc["mao"].desenhar(b.sup, ma, (ma[0], ma[1] + 2), 1, esp)
        pc["braco"].desenhar(b.sup, o, co, 1, esp)
        _espinhos_braco(b, e[f"om_{lado}"], e[f"co_{lado}"], -1 if esp else 1)


def postura_sphyrus(t):
    """O SPHYRUS de frente: de pé, pernas de raptor abertas, braços meio abertos (as asinhas aparecendo)."""
    r = math.sin(t * 0.09) * 0.8
    return dict(pe_e=(-16, 0), pe_d=(16, 0), jo_e=(-19, 22), jo_d=(19, 22), qu_e=(-8, 40), qu_d=(8, 40),
                om_e=(-13, 60 + r), om_d=(13, 60 + r), co_e=(-20, 50 + r), co_d=(20, 50 + r),
                ma_e=(-17, 40 + r), ma_d=(17, 40 + r), pe_coco=(0, 70 + r), cab=(0, 84 + r))


def onda_de_ar(tela, x, y, esc, t=0):
    """A ONDA DE AR vindo na câmera, em pixel art (pra cena): um anel de vento (2 arcos + risquinhos).
    (x, y) = o meio na tela; esc = tamanho de 1 pixel do jogo na tela (vai aumentando)."""
    peq = pygame.Surface((33, 17), pygame.SRCALPHA)
    pygame.draw.ellipse(peq, (140, 210, 255), (0, 0, 33, 17), 2)
    pygame.draw.ellipse(peq, (230, 250, 255), (4, 3, 25, 11), 1)
    for i in range(4):  # os risquinhos de vento girando
        a = t * 0.3 + i * math.pi / 2
        px, py = 16 + math.cos(a) * 12, 8 + math.sin(a) * 5
        peq.set_at((int(px), int(py)), (255, 255, 255))
        peq.set_at((int(px) + 1, int(py)), (200, 240, 255))
    img = pygame.transform.scale(peq, (round(33 * esc), round(17 * esc)))
    tela.blit(img, (round(x - 16.5 * esc), round(y - 8.5 * esc)))


def _sphyrus(b, e, pose, t, f, prog=None):
    pc = _peca("SPHYRUS", _pecas_sphyrus)
    if pose in ("parado", "ataque"):
        e = postura_sphyrus(t)
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    if k is None or k >= 0.55:
        _desenha_sphyrus(b, e, pc, t, f)
    elif k < 0.15:  # se ABAIXA pra pegar impulso
        a = k / 0.15
        e = {n: (v[0], v[1] - (3 * a if not n.startswith("pe_") else 0)) for n, v in e.items()}
        _desenha_sphyrus(b, e, pc, t, f)
    else:  # GIRA UMA VOLTA inteira, como um pião (de lado ele fica fininho; no meio mostra as costas)
        volta = (k - 0.15) / 0.4
        volta = volta * volta * (3 - 2 * volta)
        K = math.cos(volta * math.tau)
        tmp = pygame.Surface(b.sup.get_size(), pygame.SRCALPHA)
        b2 = Pincel(tmp, b.ox, b.oy, b.k)
        _desenha_sphyrus(b2, e, pc, t, f, costas=K < 0, giro_cauda=volta * math.tau * 0.5)
        larg = max(1, round(tmp.get_width() * max(0.2, abs(K))))
        fino = pygame.transform.scale(tmp, (larg, tmp.get_height()))
        if K < 0:
            fino = pygame.transform.flip(fino, True, False)
        b.sup.blit(fino, (round(b.ox - b.ox * larg / tmp.get_width()), 0))
        if 0.15 < volta < 0.95:  # o VENTO girando em volta da cauda
            cx, cy = b.P((0, 30))
            for j in range(10):
                a = volta * math.tau * 2 + j * 0.35
                b.sup.set_at((int(cx + math.cos(a) * 18), int(cy + math.sin(a) * 4)), (200, 235, 255) if j % 2 else (255, 255, 255))
    cab = e["cab"]
    res = dict(olhos=(cab[0], cab[1] + 3), mao=(0, 30), cabeca=cab)
    if k is not None:
        res["soltou"] = k >= 0.5
    return res


# ---- FRIGANTUS, PIXEL POR PIXEL (o gorila-yeti, e a BOLA DE NEVE) ----
def _pecas_frigantus():
    import frigantus
    from pecas import Peca
    pal = dict(frigantus.PALETA, k=(16, 18, 26), e=(8, 8, 12), o=(150, 220, 255), w=(245, 240, 225),
               r=(70, 16, 26), x=(150, 80, 90), P=(56, 58, 66), q=(110, 114, 124))
    return dict(
        cabeca=Peca([
            "....kkkkkkk....",
            "...kmMmmmMmk...",
            "..kmmmmmmmmmk..",
            ".kmmMmmmmmMmmk.",
            "kmmkkkkkkkkkmmk",
            "kmkPPPPPPPPPkmk",
            "kmkpoepppeopkmk",
            "kmkpppppppppkmk",
            "kmkpqqqqqqqpkmk",
            "kmkpqkqqqkqpkmk",
            "kmkpqqqqqqqpkmk",
            "kmkpkkkkkkkpkmk",
            "kmmkpppppppkmmk",
            "kmmmkkkkkkkmmmk",
            "kkkkkkkkkkkkkkk",
        ], pal, a=(7, 13), b=(7, 0), estica=False),
        cabeca_ruge=Peca([
            "....kkkkkkk....",
            "...kmMmmmMmk...",
            "..kmmmmmmmmmk..",
            ".kmmMmmmmmMmmk.",
            "kmmkkkkkkkkkmmk",
            "kmkPPPPPPPPPkmk",
            "kmkpoepppeopkmk",
            "kmkpppppppppkmk",
            "kmkpqqqqqqqpkmk",
            "kmkpqkqqqkqpkmk",
            "kmkqrrrrrrrqkmk",
            "kmkpwrrrrrwpkmk",
            "kmmkpppppppkmmk",
            "kmmmkkkkkkkmmmk",
            "kkkkkkkkkkkkkkk",
        ], pal, a=(7, 13), b=(7, 0), estica=False),
        tronco=Peca([
            "...kkkkkkkkkkkkkkkkkkk...",
            ".kkmmmmmmmmmmmmmmmmmmmkk.",
            "kmmcmmmmmmmmmmmmmmmmmcmmk",
            "kmccmmmmmmmmmmmmmmmmmccmk",
            "kMmmmmMpppppppppppMmmmmMk",
            "kMmmmmMpppxpppxpppMmmmmMk",
            "kMmmmmMppxpppxppppMmmmmMk",
            "kMmmmmMpxpppxpppppMmmmmMk",
            "kMmmmmMpppppppppppMmmmmMk",
            "..kMmmmMpppppppppMmmmMk..",
            "...kMmmmmpppppppmmmmMk...",
            "....kMmmmmmmmmmmmmmMk....",
            "....kMmmmmmmmmmmmmmMk....",
            ".....kkkkkkkkkkkkkkk.....",
        ], pal, a=(12, 12), b=(12, 1)),
        braco=Peca([
            "kkkkkkkk",
            "kmmmmmMk",
            "kmmcmmMk",
            "kmccmmMk",
            "kmmmmmMk",
            "kmmmmmMk",
            "kmmmmmMk",
            "kkkkkkkk",
        ], pal, a=(4, 0), b=(4, 7)),
        antebraco=Peca([
            ".kkkkkk.",
            "kmmmmmMk",
            "kmmmmmMk",
            "kmmmcmMk",
            "kmmmmmMk",
            "kmmmmmMk",
            ".kkkkkk.",
        ], pal, a=(4, 0), b=(4, 6)),
        mao=Peca([
            ".kkkkkkk.",
            "kpppppppk",
            "kpkpkpkpk",
            "kqqqqqqqk",
            ".kkkkkkk.",
        ], pal, a=(4, 0), b=(4, 4), estica=False),
        coxa=Peca([
            "kkkkkkkkk",
            "kmmmmmmMk",
            "kmmmmmmMk",
            "kmmmmmmMk",
            "kmmmmmMMk",
            ".kkkkkkk.",
        ], pal, a=(4, 0), b=(4, 5)),
        canela=Peca([
            ".kkkkkk.",
            "kmmmmmMk",
            "kmmmmmMk",
            "kmmmmmMk",
            "kmmmmMMk",
            ".kkkkkk.",
        ], pal, a=(4, 0), b=(4, 5)),
        sapato=Peca([
            "..kkkkkkk..",
            ".kpppppppk.",
            "kpppppppppk",
            "kpkpkpkpkpk",
            "kkkkkkkkkkk",
        ], pal, a=(5, 0), b=(5, 4), estica=False),
    )


def postura_gorila(t):
    """O FRIGANTUS de frente: ombrões, pernas curtas, a cabeça afundada e os braços COMPRIDOS até o chão
    (apoiando os punhos)."""
    r = math.sin(t * 0.07) * 0.8
    return dict(pe_e=(-15, 0), pe_d=(15, 0), jo_e=(-17, 14), jo_d=(17, 14), qu_e=(-10, 28), qu_d=(10, 28),
                om_e=(-26, 66 + r), om_d=(26, 66 + r), co_e=(-36, 38 + r), co_d=(36, 38 + r),
                ma_e=(-34, 10), ma_d=(34, 10), pe_coco=(0, 70 + r), cab=(0, 80 + r))


def bola_de_neve(tela, x, y, esc, t=0):
    """A BOLA DE NEVE vindo na câmera, em pixel art (pra cena): (x, y) = o meio na tela;
    esc = tamanho de 1 pixel do jogo na tela (vai aumentando)."""
    peq = pygame.Surface((17, 17), pygame.SRCALPHA)
    pygame.draw.circle(peq, (16, 18, 26), (8, 8), 8)
    pygame.draw.circle(peq, (196, 210, 232), (8, 8), 7)
    pygame.draw.circle(peq, (250, 252, 255), (7, 7), 6)
    pygame.draw.circle(peq, (255, 255, 255), (5, 5), 2)
    for px, py in ((10, 11), (12, 8), (6, 12)):  # os torrões de neve
        peq.set_at((px, py), (210, 222, 240))
    img = pygame.transform.scale(peq, (round(17 * esc), round(17 * esc)))
    tela.blit(img, (round(x - 8.5 * esc), round(y - 8.5 * esc)))


def _frigantus(b, e, pose, t, f, prog=None):
    pc = _peca("FRIGANTUS", _pecas_frigantus)
    if pose in ("parado", "ataque"):
        e = postura_gorila(t)
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    soltou = k is not None and k >= 0.5
    bola = None  # (centro e raio da bola de neve nas mãos, em pixels)
    frente_mao = False
    if k is not None:
        if k < 0.4:  # LEVANTA os braços e a bola vai crescendo lá em cima
            a = min(1.0, k / 0.25)
            for lado, s_ in (("e", -1), ("d", 1)):
                e = dict(e, **{f"co_{lado}": (s_ * (36 - 6 * a), 38 + 70 * a), f"ma_{lado}": (s_ * (34 - 26 * a), 10 + 112 * a)})
            if k > 0.1:
                bola = (b.P((0, 128)), 2 + 7 * min(1.0, (k - 0.1) / 0.3))
        elif not soltou:  # JOGA: os braços descem pra frente com a bola
            a = (k - 0.4) / 0.1
            for lado, s_ in (("e", -1), ("d", 1)):
                e = dict(e, **{f"co_{lado}": (s_ * 28, 108 - 40 * a), f"ma_{lado}": (s_ * 8, 122 - 54 * a)})
            bola = (b.P((0, 128 - 54 * a)), 9)
        else:  # soltou: as mãos ficam pra frente, abertas
            for lado, s_ in (("e", -1), ("d", 1)):
                e = dict(e, **{f"co_{lado}": (s_ * 26, 60), f"ma_{lado}": (s_ * 12, 56)})
            frente_mao = k < 0.8
    P = b.P
    for lado, esp in (("e", True), ("d", False)):  # pernas curtas e grossas
        q, j, pe = P(e[f"qu_{lado}"]), P(e[f"jo_{lado}"]), P(e[f"pe_{lado}"])
        pc["canela"].desenhar(b.sup, j, pe, 1, esp)
        pc["coxa"].desenhar(b.sup, q, j, 1, esp)
        pc["sapato"].desenhar(b.sup, (pe[0], pe[1] - 4), (pe[0], pe[1] + 1), 1, esp)
    meio_q = P(((e["qu_e"][0] + e["qu_d"][0]) / 2, (e["qu_e"][1] + e["qu_d"][1]) / 2))
    pc["tronco"].desenhar(b.sup, meio_q, P(e["pe_coco"]), 1, False)
    pescoco = P(e["pe_coco"])
    for i in range(5):  # o COLAR DE DENTES
        x = pescoco[0] - 6 + i * 3
        y = pescoco[1] + 3 + abs(i - 2)
        b.sup.set_at((int(x), int(y)), (240, 236, 220))
        b.sup.set_at((int(x), int(y) + 1), (240, 236, 220))
    ruge = k is not None and k < 0.6
    pc["cabeca_ruge" if ruge else "cabeca"].desenhar(b.sup, (pescoco[0], pescoco[1] + 4), (pescoco[0], pescoco[1] - 9), 1, False)
    for lado, esp in (("e", True), ("d", False)):  # os BRAÇOS compridos com as mãozonas
        o, co, ma = P(e[f"om_{lado}"]), P(e[f"co_{lado}"]), P(e[f"ma_{lado}"])
        pc["antebraco"].desenhar(b.sup, co, ma, 1, esp)
        if frente_mao:  # (vindo pra câmera: a mão maior)
            pc["mao"].desenhar(b.sup, (ma[0], ma[1] - 3), (ma[0], ma[1] + 3), 1.4, esp)
        else:
            pc["mao"].desenhar(b.sup, ma, (ma[0] + (ma[0] - co[0]) * 0.2, ma[1] + 4), 1, esp)
        pc["braco"].desenhar(b.sup, o, co, 1, esp)
    if bola:  # a BOLA DE NEVE entre as mãos
        (bx, by), r = bola
        pygame.draw.circle(b.sup, (196, 210, 232), (int(bx), int(by)), int(r))
        pygame.draw.circle(b.sup, (250, 252, 255), (int(bx - 1), int(by - 1)), max(1, int(r) - 1))
        b.sup.set_at((int(bx - r * 0.4), int(by - r * 0.4)), (255, 255, 255))
    cab = e["cab"]
    res = dict(olhos=(cab[0], cab[1]), mao=(0, 62) if soltou else (0, 128), cabeca=cab)
    if k is not None:
        res["soltou"] = soltou
    return res


# ---- INAZUMANEKO, PIXEL POR PIXEL (o tigre samurai, e a MEIA-LUA de vento) ----
def _pecas_inazumaneko():
    import inazumaneko
    from pecas import Peca
    pal = inazumaneko.PALETA
    return dict(
        cabeca=Peca([
            ".kk.......kk.",
            ".ksk.....ksk.",
            ".kswkkkkkwsk.",
            "kwwwswswswwwk",
            "kwwwwwswwwwwk",
            "kswwwwwwwwwsk",
            "kwkkwwwwwckwk",
            "kwkoewwweokwk",
            "kswwwwlwwcwsk",
            "klwwwlllwwwlk",
            "kllwlnnnlwllk",
            "kllllklkllllk",
            ".klllllllllk.",
            "..kkkkkkkkk..",
        ], pal, a=(6, 12), b=(6, 0), estica=False),
        tronco=Peca([
            "...kkkkkkkkkk...",
            "..kGgwwwwwwgGk..",
            ".kGggwwllwwggGk.",
            ".kGgggwllwgggGk.",
            ".kGrrrrrrrrrrGk.",
            ".kGddddddddddGk.",
            ".kGrrrrrrrrrrGk.",
            ".kGddddddddddGk.",
            ".kGrrrrrrrrrrGk.",
            "..kGggggggggGk..",
            "..kbbbbbbbbbbk..",
            "..kbbbbddbbbbk..",
            "..khhhhhhhhhhk..",
            ".kHhhhhhhhhhhHk.",
            ".kkkkkkkkkkkkkk.",
        ], pal, a=(8, 13), b=(8, 1)),
        braco=inazumaneko.BRACO,
        antebraco=inazumaneko.ANTEBRACO,
        mao=inazumaneko.MAO,
        coxa=inazumaneko.COXA,
        canela=inazumaneko.CANELA,
        sapato=Peca([
            ".kkkkk.",
            "kwwwwwk",
            "klklklk",
            ".kkkkk.",
        ], pal, a=(3, 0), b=(3, 3), estica=False),
    )


def postura_samurai(t):
    """O INAZUMANEKO de frente: base firme, a mão da direita no cabo da katana (na cintura, do lado esquerdo)."""
    r = math.sin(t * 0.08) * 0.6
    return dict(pe_e=(-17, 0), pe_d=(17, 0), jo_e=(-19, 22), jo_d=(19, 22), qu_e=(-9, 40), qu_d=(9, 40),
                om_e=(-15, 68 + r), om_d=(15, 68 + r), co_e=(-22, 56 + r), co_d=(14, 54 + r),
                ma_e=(-14, 44 + r), ma_d=(-6, 46 + r), pe_coco=(0, 72 + r), cab=(0, 88 + r))


def _rabo_tigre(b, e, t):
    """O RABO saindo pro lado (atrás), cinza com anéis e a ponta preta virada pra cima."""
    import inazumaneko
    troca = pecas.TROCA or {}
    cinza, preto = troca.get("w", inazumaneko.PALETA["w"]), troca.get("s", inazumaneko.PALETA["s"])
    q = b.P((e["qu_d"][0] + 2, e["qu_d"][1] - 4))
    pts = []
    for i in range(8):
        k = i / 7
        pts.append((q[0] + 3 + 14 * k, q[1] + 2 - 14 * k ** 2.2 + math.sin(t * 0.08 + k * 3) * k))
    for i, (a_, c_) in enumerate(zip(pts, pts[1:])):
        pygame.draw.line(b.sup, preto if (i >= 5 or i in (1, 3)) else cinza, a_, c_, max(1, 3 - i // 3))


def _cabos(b, e):
    """Os DOIS cabos das katanas na cintura (do lado esquerdo dele), saindo das bainhas."""
    x, y = b.P((e["qu_e"][0] - 2, e["qu_e"][1] + 6))
    for i in range(2):
        pygame.draw.line(b.sup, (16, 14, 20), (x - i * 2, y - i), (x - 7 - i * 2, y - 4 - i), 3)
        pygame.draw.line(b.sup, (60, 44, 50), (x - i * 2, y - i), (x - 7 - i * 2, y - 4 - i), 1)
        b.sup.set_at((int(x - i * 2), int(y - i)), (226, 186, 74))


def _katana_frente(b, mao, ponta, brilho_cor=None):
    """A katana na mão (de frente): lâmina clara com a guarda dourada; a mão vai POR CIMA do cabo."""
    pygame.draw.line(b.sup, (16, 14, 20), mao, ponta, 3)
    pygame.draw.line(b.sup, (226, 232, 242), mao, ponta, 1)
    dx, dy = ponta[0] - mao[0], ponta[1] - mao[1]
    n = math.hypot(dx, dy) or 1
    g = (mao[0] + dx / n * 3, mao[1] + dy / n * 3)
    pygame.draw.line(b.sup, (226, 186, 74), (g[0] - dy / n * 2, g[1] + dx / n * 2), (g[0] + dy / n * 2, g[1] - dx / n * 2), 1)
    if brilho_cor:
        b.sup.set_at((int(ponta[0]), int(ponta[1])), brilho_cor)


def crescente_voando(tela, x, y, esc, t=0):
    """A MEIA-LUA de vento vindo na câmera, em pixel art (pra cena): um arco em pé (o corte foi vertical).
    (x, y) = o meio na tela; esc = tamanho de 1 pixel do jogo na tela (vai aumentando)."""
    pal = {"k": (40, 70, 120), "A": (255, 255, 255), "a": (170, 220, 255)}
    mapa = [
            "....kkkk",
            "..kkAAak",
            ".kAAak..",
            ".kAak...",
            "kAAk....",
            "kAak....",
            "kAak....",
            "kAak....",
            "kAak....",
            "kAAk....",
            ".kAak...",
            ".kAAak..",
            "..kkAAak",
            "....kkkk",
        ]
    peq = pygame.Surface((8, 14), pygame.SRCALPHA)
    for yy, linha in enumerate(mapa):
        for xx, ch in enumerate(linha):
            if ch != ".":
                peq.set_at((xx, yy), pal[ch])
    img = pygame.transform.scale(peq, (round(8 * esc), round(14 * esc)))
    tela.blit(img, (round(x - 4 * esc), round(y - 7 * esc)))


def _inazumaneko(b, e, pose, t, f, prog=None):
    pc = _peca("INAZUMANEKO", _pecas_inazumaneko)
    import inazumaneko
    import habilidades as hab
    if pose in ("parado", "ataque"):
        e = postura_samurai(t)
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    soltou = k is not None and k >= 0.45
    lamina = None  # (ponta da katana, em unidades)
    if k is not None:
        if k < 0.15:  # a mão no cabo
            pass
        elif k < 0.35:  # SACA e levanta com as duas mãos lá em cima
            a = min(1.0, (k - 0.15) / 0.12)
            e = dict(e, co_d=(14, 56 + 44 * a), ma_d=(-6 + 10 * a, 46 + 72 * a),
                     co_e=(-22 + 8 * a, 56 + 44 * a), ma_e=(-14 + 10 * a, 44 + 74 * a))
            lamina = (2, 118 + 34 * a)
        elif k < 0.5:  # o CORTE VERTICAL (de cima pra baixo)
            a = (k - 0.35) / 0.15
            y = 118 - 58 * a
            e = dict(e, co_d=(14, 100 - 34 * a), ma_d=(4, y), co_e=(-14, 100 - 34 * a), ma_e=(-4, y))
            lamina = (0, y + 34 - 60 * a)
        elif k < 0.8:  # parada embaixo, a lâmina apontando pro chão
            e = dict(e, co_d=(14, 66), ma_d=(4, 60), co_e=(-14, 66), ma_e=(-4, 60))
            lamina = (6, 30)
        else:  # GUARDA (volta a mão pro cabo)
            a = (k - 0.8) / 0.2
            e = dict(e, co_d=(14, 66 - 12 * a), ma_d=(4 - 10 * a, 60 - 14 * a), co_e=(-14 - 8 * a, 66 - 10 * a),
                     ma_e=(-4 - 10 * a, 60 - 16 * a))
    _rabo_tigre(b, e, t)
    montar_pecas(b, e, pc, "parado")
    if f.get("estilo") == "oni":  # ONI (skin secreta): a máscara de demônio com chifres, de frente
        px, py = b.P(e["pe_coco"])

        def H(x, y):  # (um pixel da cabeça de frente -> a superfície)
            return (px - 6 + x, py + 1 - 12 + y)
        for base, ponta in (((2, 1), (0, -5)), ((10, 1), (12, -5))):  # os chifres
            pygame.draw.polygon(b.sup, (232, 222, 192), [H(base[0] - 1, base[1]), H(*ponta), H(base[0] + 1, base[1])])
        for base, ponta in (((2, 1), (0, -5)), ((10, 1), (12, -5))):  # a sombra dos chifres (do lado de fora)
            pygame.draw.line(b.sup, (176, 164, 136), H(base[0] - 1, base[1]), H(*ponta), 1)
        pygame.draw.polygon(b.sup, (200, 36, 40), [H(1, 6), H(12, 6), H(12, 10), H(10, 12), H(3, 12), H(1, 10)])
        pygame.draw.polygon(b.sup, (128, 18, 26), [H(1, 10), H(12, 10), H(10, 12), H(3, 12)])  # a sombra embaixo
        pygame.draw.line(b.sup, (226, 186, 74), H(2, 6), H(5, 7), 1)  # a SOBRANCELHA DOURADA brava (em V)
        pygame.draw.line(b.sup, (226, 186, 74), H(11, 6), H(8, 7), 1)
        for x in (3.5, 8.5):
            b.sup.set_at((int(H(x, 8)[0]), int(H(x, 8)[1])), (20, 8, 12))  # o buraco do olho...
            b.sup.set_at((int(H(x, 8)[0]), int(H(x, 8)[1]) - 1), (255, 70, 56))  # ...com o brilho vermelho
        for x in (4, 6, 8):  # a boca com as PRESAS
            b.sup.set_at((int(H(x, 10.5)[0]), int(H(x, 10.5)[1])), (246, 242, 232))
            b.sup.set_at((int(H(x + 1, 10.5)[0]), int(H(x + 1, 10.5)[1])), (20, 8, 12))
    if lamina is None:
        _cabos(b, e)
    else:  # a katana na mão (e as mãos por cima do cabo)
        cor = hab.COR_STATUS.get(f.get("_poder")) if False else None
        mao = b.P(((e["ma_d"][0] + e["ma_e"][0]) / 2, (e["ma_d"][1] + e["ma_e"][1]) / 2))
        _katana_frente(b, mao, b.P(lamina), cor)
        for lado, esp in (("e", True), ("d", False)):
            m_ = b.P(e[f"ma_{lado}"])
            pc["mao"].desenhar(b.sup, m_, (m_[0], m_[1] + 4), 1, esp)
        x, y = b.P((e["qu_e"][0] - 2, e["qu_e"][1] + 6))  # (a bainha vazia)
        pygame.draw.line(b.sup, (16, 14, 20), (x, y), (x - 7, y - 4), 3)
    cab = e["cab"]
    res = dict(olhos=(cab[0], cab[1] + 3), mao=(0, 70) if k is not None else e["ma_d"], cabeca=cab)
    if k is not None:
        res["soltou"] = soltou
    return res


LUTADORES.update({"TROMOS": _tromos, "CRÁQUEN": _craquen, "MAGNUS": _magnus, "SPHYRUS": _sphyrus,
                  "FRIGANTUS": _frigantus})
LARGO.update({"FRIGANTUS": 1.2})
LUTADORES.update({"INAZUMANEKO": _inazumaneko})

# =====================================================================
# o desenho
# =====================================================================
_cache_tinta = {}


def desenhar_frente(tela, ficha, x, y, escala, pose="parado", t=0, prog=None):
    """prog (0..1, opcional): em que ponto da animação do ATAQUE ele está (sem prog, roda em loop pelo t).
    Quem tem animação de ataque devolve também "soltou": True depois que o golpe saiu da mão."""
    nome = ficha.get("nome_base", ficha.get("nome"))
    fn = LUTADORES.get(nome)
    if fn is None:
        return None
    tam = ficha.get("tam", 1.36)
    k = tam / UNID  # (1 unidade da pose = k pixels do jogo)
    W, H = int(190 * k) + 8, int(170 * k) + 8
    pequeno = pygame.Surface((W, H), pygame.SRCALPHA)
    ox, oy = W / 2, H - 4
    b = Pincel(pequeno, ox, oy, k)
    e = esqueleto(pose, t, LARGO.get(nome, 1.0))
    pecas.usar_troca(ficha.get("troca"))
    try:
        import inspect
        pts = fn(b, e, pose, t, ficha, prog) if "prog" in inspect.signature(fn).parameters else fn(b, e, pose, t, ficha)
    finally:
        pecas.usar_troca(None)
    # contorno de 1 pixel (igual o sprite)
    mascara = pygame.mask.from_surface(pequeno, 60)
    sil = mascara.to_surface(setcolor=(*PRETO, 255), unsetcolor=(0, 0, 0, 0))
    final = pygame.Surface((W, H), pygame.SRCALPHA)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        final.blit(sil, (dx, dy))
    final.blit(pequeno, (0, 0))
    # a TINTA das skins (SOMBRA / OURO / HOLO / fantasma), usando o próprio lutador (igual o sprite)
    if ficha.get("tinta") or ficha.get("sombra") or ficha.get("fantasma"):
        from lutador import Lutador
        falso = Lutador(ficha, 0, 1)
        falso.t = t
        falso.aplicar_tinta(final, False)
    amplia = UNID * escala
    grande = pygame.transform.scale(final, (round(W * amplia), round(H * amplia)))
    gx, gy = x - ox * amplia, y - oy * amplia
    tela.blit(grande, (gx, gy))

    def tela_de(u):
        return (gx + (ox + u[0] * k) * amplia, gy + (oy - u[1] * k) * amplia)
    return {nome_p: (tela_de(u) if isinstance(u, tuple) else u) for nome_p, u in pts.items()}


# ---- NOCTURNUS, PIXEL POR PIXEL (o mutante morcego-escorpião, e a BOLA DE ECO) ----
def _pecas_nocturnus():
    import nocturnus
    from pecas import Peca
    pal = nocturnus.PALETA
    return dict(
        tronco=Peca([
            "...kkkkkkkk...",
            "..kfFfFfFfFk..",
            ".kpfFfFfFfFpk.",
            "kppfffffffffpk",
            "kpppckckckpppk",
            "kpppckckckpppk",
            "kPppckckckppPk",
            "kPpppffffpppPk",
            ".kPppffffppPk.",
            ".kPpppffpppPk.",
            "..kPppppppPk..",
            "..kPppppppPk..",
            "...kkkkkkkk...",
        ], pal, a=(7, 12), b=(7, 0)),
        braco=nocturnus.BRACO,
        antebraco=nocturnus.ANTEBRACO,
        mao=nocturnus.MAO,
        coxa=nocturnus.COXA,
        canela=nocturnus.CANELA,
        sapato=Peca([
            ".kkkkkkk.",
            "kpppppppk",
            "kwkwkwkwk",
            ".w.w.w.w.",
        ], pal, a=(4, 0), b=(4, 3), estica=False),
    )


def _cor_noct(letra):
    import nocturnus
    return (pecas.TROCA or {}).get(letra, nocturnus.PALETA[letra])


def postura_morcego(t):
    """O NOCTURNUS de frente: CURVADO, pernas grossas abertas, as ASAS meio abertas dos lados (feito capa aberta)."""
    r = math.sin(t * 0.08) * 0.8
    return dict(pe_e=(-15, 0), pe_d=(15, 0), jo_e=(-17, 20), jo_d=(17, 20), qu_e=(-8, 38), qu_d=(8, 38),
                om_e=(-12, 62 + r), om_d=(12, 62 + r), co_e=(-26, 58 + r), co_d=(26, 58 + r),
                ma_e=(-34, 44 + r), ma_d=(34, 44 + r), pe_coco=(0, 66 + r), cab=(0, 78 + r))


def _cauda_escorpiao(b, e, t):
    """A CAUDA DE ESCORPIÃO saindo de trás do quadril e subindo em ARCO do lado dele, com a ponta curvada por cima do
    ombro: gomos (claro/escuro), a bolsa de veneno e o FERRÃO vermelho apontando pra frente."""
    borda, cor, claro = (16, 12, 22), _cor_noct("p"), _cor_noct("P")
    pts = []
    bal = math.sin(t * 0.07) * 2
    c0, c1, c2, c3 = (8, 36), (44, 34), (46 + bal, 104), (22 + bal, 100)  # (o arco: sai pro lado, sobe e curva)
    for i in range(12):
        k = i / 11
        u = 1 - k
        x = u ** 3 * c0[0] + 3 * u * u * k * c1[0] + 3 * u * k * k * c2[0] + k ** 3 * c3[0]
        y = u ** 3 * c0[1] + 3 * u * u * k * c1[1] + 3 * u * k * k * c2[1] + k ** 3 * c3[1]
        pts.append(b.P((x, y)))
    for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
        pygame.draw.line(b.sup, borda, p0, p1, 4 if i < 7 else 3)
    for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
        pygame.draw.line(b.sup, claro if i % 2 else cor, p0, p1, 2 if i < 7 else 1)
    fx, fy = pts[-1]
    pygame.draw.circle(b.sup, borda, (int(fx), int(fy)), 3)
    pygame.draw.circle(b.sup, claro, (int(fx), int(fy)), 2)
    dx, dy = fx - pts[-2][0], fy - pts[-2][1]
    n = math.hypot(dx, dy) or 1
    ponta = (fx + dx / n * 5, fy + dy / n * 5 + 2)
    pygame.draw.line(b.sup, borda, (fx, fy), ponta, 3)
    pygame.draw.line(b.sup, _cor_noct("r"), (fx, fy), ponta, 1)
    b.sup.set_at((int(ponta[0]), int(ponta[1])), _cor_noct("v"))


def _asa_frente(b, e, lado, abre=1.0):
    """A ASA de frente: a MEMBRANA do ombro até a mão e descendo pelos 3 dedos compridos até o quadril."""
    P = b.P
    s = -1 if lado == "e" else 1
    o, c, m = e[f"om_{lado}"], e[f"co_{lado}"], e[f"ma_{lado}"]
    q = (s * 6, 40)
    dedos = [(m[0] + s * (3 + 6 * abre), m[1] - 8 - 6 * abre), (m[0] + s * 1, m[1] - 18 - 6 * abre),
             (m[0] - s * (4 + 4 * abre), m[1] - 24 - 4 * abre)]
    borda = (16, 12, 22)
    contorno = [P(o), P(c), P(m)] + [P(d) for d in dedos] + [P(q)]
    pygame.draw.polygon(b.sup, _cor_noct("m"), contorno)
    meio = ((c[0] + q[0]) / 2, (c[1] + q[1]) / 2)
    pygame.draw.polygon(b.sup, _cor_noct("M"), [P(meio), P(dedos[1]), P(dedos[2]), P(q)])
    for d in dedos:  # os DEDOS (ossos da asa)
        pygame.draw.line(b.sup, borda, P(m), P(d), 1)
    pygame.draw.polygon(b.sup, borda, contorno, 1)


def _cabeca_morcego(b, cab, t, boca=0.0):
    """A CABEÇA de frente em pixel: as ORELHONAS de morcego (pontudas, abertas pros lados, uma CORTADA em cima) com
    o aparelhinho azul embaixo, as marcas vermelhas, os olhos azuis acesos, o focinho curto e as presas."""
    sup, borda = b.sup, (16, 12, 22)
    cx, cy = b.P(cab)
    cx, cy = int(cx), int(cy)
    p, P_, m = _cor_noct("p"), _cor_noct("P"), _cor_noct("m")
    for s_ in (-1, 1):  # as ORELHONAS (gota pontuda, inclinada pra fora)
        base = [(cx + s_ * 2, cy - 4), (cx + s_ * 7, cy - 1)]
        ponta = (cx + s_ * 11, cy - 19)
        if s_ > 0:  # a CORTADA: a ponta reta, em zigue-zague
            orelha = [base[0], (cx + s_ * 4, cy - 14), (cx + s_ * 7, cy - 15), (cx + s_ * 9, cy - 14),
                      (cx + s_ * 10, cy - 15), base[1]]
        else:
            orelha = [base[0], (cx + s_ * 4, cy - 15), ponta, (cx + s_ * 11, cy - 10), base[1]]
        pygame.draw.polygon(sup, p, orelha)
        dentro = [((x - cx) * 0.6 + cx + s_ * 1.5, (y - cy) * 0.7 + cy - 1) for x, y in orelha]
        pygame.draw.polygon(sup, m, dentro)
        pygame.draw.polygon(sup, borda, orelha, 1)
        ax, ay = cx + s_ * 6, cy - 4  # o APARELHINHO azul (embaixo da orelha)
        pygame.draw.rect(sup, borda, (ax - 1, ay - 1, 3, 3))
        sup.set_at((ax, ay), _cor_noct("b"))
        if (t // 8) % 2:
            sup.set_at((ax, ay), _cor_noct("B"))
    pygame.draw.ellipse(sup, borda, (cx - 6, cy - 7, 13, 13))  # a CABEÇA
    pygame.draw.ellipse(sup, p, (cx - 5, cy - 6, 11, 11))
    pygame.draw.line(sup, P_, (cx - 2, cy - 5), (cx + 2, cy - 5))
    pygame.draw.ellipse(sup, P_, (cx - 2, cy + 1, 5, 4))  # o focinho curto
    for s_ in (-1, 1):
        sup.set_at((cx + s_ * 1, cy - 4), _cor_noct("r"))  # as marcas vermelhas (em cima dos olhos)
        sup.set_at((cx + s_ * 4, cy - 3), _cor_noct("r"))
        for x in (2, 3):  # os OLHOS azuis acesos (2x2, puxados)
            sup.set_at((cx + s_ * x, cy - 2 + (1 if x == 2 else 0)), _cor_noct("e"))
            sup.set_at((cx + s_ * x, cy - 1), _cor_noct("e"))
    sup.set_at((cx, cy + 1), borda)  # o nariz
    abre = int(round(boca * 3))
    pygame.draw.line(sup, borda, (cx - 2, cy + 3), (cx + 2, cy + 3))
    if abre:
        pygame.draw.rect(sup, (120, 30, 50), (cx - 2, cy + 3, 5, abre))
        pygame.draw.rect(sup, borda, (cx - 3, cy + 2, 7, abre + 2), 1)
    sup.set_at((cx - 1, cy + 4 + abre // 2), _cor_noct("w"))  # as PRESAS
    sup.set_at((cx + 1, cy + 4 + abre // 2), _cor_noct("w"))


def _desenha_nocturnus(b, e, pc, t, boca=0.0, abre=1.0):
    P = b.P
    _cauda_escorpiao(b, e, t)
    for lado in ("e", "d"):
        _asa_frente(b, e, lado, abre)
    for lado, esp in (("e", True), ("d", False)):  # as PERNAS grossas com garras
        q, j, pe = P(e[f"qu_{lado}"]), P(e[f"jo_{lado}"]), P(e[f"pe_{lado}"])
        pc["canela"].desenhar(b.sup, j, pe, 1, esp)
        pc["coxa"].desenhar(b.sup, q, j, 1, esp)
        pc["sapato"].desenhar(b.sup, (pe[0], pe[1] - 3), (pe[0], pe[1]), 1, esp)
    meio_q = P(((e["qu_e"][0] + e["qu_d"][0]) / 2, (e["qu_e"][1] + e["qu_d"][1]) / 2))
    pc["tronco"].desenhar(b.sup, meio_q, P(e["pe_coco"]), 1, False)
    for lado, esp in (("e", True), ("d", False)):  # os braços (o osso da asa) por cima da membrana
        o, co, ma = P(e[f"om_{lado}"]), P(e[f"co_{lado}"]), P(e[f"ma_{lado}"])
        pc["braco"].desenhar(b.sup, o, co, 1, esp)
        pc["antebraco"].desenhar(b.sup, co, ma, 1, esp)
        pc["mao"].desenhar(b.sup, ma, (ma[0], ma[1] - 2), 1, esp)
    _cabeca_morcego(b, e["cab"], t, boca)


def bola_eco_voando(tela, x, y, esc, t=0):
    """A BOLA DE ECO vindo na câmera, em pixel art (pra cena): anéis azuis de distorção girando (não é uma bola
    sólida: o ar tremendo)."""
    peq = pygame.Surface((19, 19), pygame.SRCALPHA)
    for i, (r, cor) in enumerate(((9, (70, 160, 255)), (6, (150, 220, 255)), (3, (230, 250, 255)))):
        rr = r - (1 if (t // 3 + i) % 2 else 0)
        pygame.draw.circle(peq, cor, (9, 9), rr, 1)
    for i in range(4):  # o redemoinho
        a = t * 0.35 + i * math.pi / 2
        peq.set_at((int(9 + math.cos(a) * 7), int(9 + math.sin(a) * 7)), (255, 255, 255))
    img = pygame.transform.scale(peq, (round(19 * esc), round(19 * esc)))
    tela.blit(img, (round(x - 9.5 * esc), round(y - 9.5 * esc)))


def _suave_noct(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def _nocturnus(b, e, pose, t, f, prog=None):
    pc = _peca("NOCTURNUS", _pecas_nocturnus)
    if pose in ("parado", "ataque"):
        e = postura_morcego(t)
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    boca, abre = 0.0, 0.6
    if k is not None:
        if k < 0.3:  # PUXA O AR: as asas sobem e abrem, a cabeça vai pra trás
            a = _suave_noct(k / 0.3)
            e = dict(e, co_e=(-28, 58 + 12 * a), co_d=(28, 58 + 12 * a), ma_e=(-38, 44 + 30 * a),
                     ma_d=(38, 44 + 30 * a), cab=(0, 78 + 2 * a))
            abre = 0.6 + 0.4 * a
        elif k < 0.6:  # o GRITO: curva pra frente e solta a bola de eco
            a = _suave_noct((k - 0.3) / 0.3)
            e = dict(e, co_e=(-28, 70 - 14 * a), co_d=(28, 70 - 14 * a), ma_e=(-38, 74 - 30 * a),
                     ma_d=(38, 74 - 30 * a), cab=(0, 80 - 4 * a), pe_coco=(0, 66 - 2 * a))
            boca, abre = 1.0, 1.0
        else:  # volta
            a = _suave_noct((k - 0.6) / 0.4)
            e = dict(e, cab=(0, 76 + 2 * a), pe_coco=(0, 64 + 2 * a))
            boca, abre = max(0.0, 1 - a * 2), 1.0 - 0.4 * a
    _desenha_nocturnus(b, e, pc, t, boca, abre)
    cab = e["cab"]
    res = dict(olhos=(cab[0], cab[1] + 1), mao=(0, cab[1] - 4), cabeca=cab)
    if k is not None:
        res["soltou"] = k >= 0.45
    return res


LUTADORES.update({"NOCTURNUS": _nocturnus})
LARGO.update({"NOCTURNUS": 1.3})


# ---- SILVANUS, PIXEL POR PIXEL (a planta carnívora de frente, e a SEMENTE voando na câmera) ----
def _cor_silv(letra):
    import silvanus
    return (pecas.TROCA or {}).get(letra, silvanus.PALETA[letra])


def _folha_frente(sup, base, comp, larg, ang, cor, veia):
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux
    pts = []
    for i in range(7):
        k = i / 6
        w = math.sin(k * math.pi) * larg
        pts.append((base[0] + ux * comp * k + nx * w, base[1] + uy * comp * k + ny * w))
    for i in range(6, -1, -1):
        k = i / 6
        w = math.sin(k * math.pi) * larg * 0.7
        pts.append((base[0] + ux * comp * k - nx * w, base[1] + uy * comp * k - ny * w))
    pygame.draw.polygon(sup, cor, pts)
    pygame.draw.polygon(sup, (16, 22, 14), pts, 1)
    pygame.draw.line(sup, veia, base, (base[0] + ux * comp * 0.8, base[1] + uy * comp * 0.8))


def _cabeca_planta_frente(sup, cx, cy, r, boca, t, runa):
    """A CABEÇONA de planta carnívora OLHANDO PRA CÂMERA: bola roxa com a boca no meio (fechada = dentes
    trançados; aberta = buraco escuro com dentes em cima e embaixo e a língua)."""
    borda = (16, 22, 14)
    for lado in (-1, 1):  # as folhinhas da gola (atrás da cabeça, aparecendo dos lados)
        _folha_frente(sup, (cx + lado * (r - 2), cy - 1), r * 0.9, 2.2, math.pi / 2 + lado * 1.9 + math.pi,
                      _cor_silv("g"), _cor_silv("G"))
    pygame.draw.circle(sup, borda, (int(cx), int(cy)), int(r) + 1)
    pygame.draw.circle(sup, _cor_silv("p"), (int(cx), int(cy)), int(r))
    pygame.draw.ellipse(sup, _cor_silv("P"), (cx - r * 0.6, cy - r * 0.85, r * 1.2, r * 0.5))  # o brilho de cima
    for ox, oy in ((-4, -5), (3, -6), (5, -3)):  # as pintinhas
        sup.set_at((int(cx + ox), int(cy + oy)), _cor_silv("P"))
    abre = int(round(boca * r * 0.9))
    w = int(r * 1.5)
    if abre >= 2:  # BOCA ABERTA: o buraco escuro, a língua e os dentes
        pygame.draw.ellipse(sup, borda, (cx - w / 2 - 1, cy - abre / 2 - 1, w + 2, abre + 2))
        pygame.draw.ellipse(sup, _cor_silv("q"), (cx - w / 2, cy - abre / 2, w, abre))
        pygame.draw.ellipse(sup, _cor_silv("r"), (cx - w / 4, cy + abre / 2 - 3, w / 2, 3))
        for i in range(5):
            x = cx - w / 2 + 2 + i * (w - 4) / 4
            pygame.draw.polygon(sup, _cor_silv("w"), [(x - 1, cy - abre / 2), (x + 1, cy - abre / 2), (x, cy - abre / 2 + 2)])
            pygame.draw.polygon(sup, _cor_silv("w"), [(x - 1, cy + abre / 2), (x + 1, cy + abre / 2), (x, cy + abre / 2 - 2)])
    else:  # FECHADA: a linha da boca com os dentes trançados
        pygame.draw.line(sup, borda, (cx - w / 2, cy + 1), (cx + w / 2, cy + 1))
        for i in range(6):
            x = cx - w / 2 + 1 + i * (w - 2) / 5
            sup.set_at((int(x), int(cy + (0 if i % 2 else 2))), _cor_silv("w"))
    if runa:  # a RUNA na testa
        cor = _cor_silv("y")
        for ox, oy in ((0, -r + 3), (-1, -r + 4), (1, -r + 4), (0, -r + 5)):
            sup.set_at((int(cx + ox), int(cy + oy)), cor)


def _desenha_silvanus_frente(b, t, boca=0.0, recua=0.0, avanca=0.0, runa=False):
    sup, borda = b.sup, (16, 22, 14)
    bx, by = (int(v) for v in b.P((0, 0)))
    # as RAÍZES espalhadas no chão (pros lados e vindo na direção da câmera)
    for i, (dx, dy, larg) in enumerate(((-22, 1, 3), (22, 1, 3), (-15, 3, 3), (15, 3, 3), (-8, 4, 2), (8, 4, 2),
                                        (-27, -1, 2), (27, -1, 2))):
        ondula = math.sin(t * 0.06 + i) * 0.6
        meio = (bx + dx * 0.5, by - 2 + ondula)
        fim = (bx + dx, by + dy)
        pygame.draw.lines(sup, borda, False, [(bx, by - 3), meio, fim], larg + 2)
        pygame.draw.lines(sup, _cor_silv("T" if i % 3 == 0 else "t"), False, [(bx, by - 3), meio, fim], larg)
    # as FOLHAS grandes da base
    bal = math.sin(t * 0.1) * 0.1
    for lado in (-1, 1):
        _folha_frente(sup, (bx + lado * 3, by - 5), 19, 4.5, math.pi / 2 + lado * (1.25 + bal) + math.pi,
                      _cor_silv("g" if lado < 0 else "d"), _cor_silv("G"))
    # o BULBO (corpo curto e grosso)
    pygame.draw.ellipse(sup, borda, (bx - 9, by - 23, 18, 21))
    pygame.draw.ellipse(sup, _cor_silv("g"), (bx - 8, by - 22, 16, 19))
    pygame.draw.ellipse(sup, _cor_silv("d"), (bx - 8, by - 20, 5, 15))
    pygame.draw.line(sup, _cor_silv("G"), (bx + 4, by - 18), (bx + 5, by - 8))
    for ox, oy in ((-3, -12), (2, -15), (0, -8)):  # as RUNAS
        sup.set_at((bx + ox, by + oy), _cor_silv("y") if runa else _cor_silv("Y"))
    for fx, fy in ((bx - 6, by - 18), (bx + 6, by - 12)):  # as florzinhas
        for ox, oy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            sup.set_at((int(fx + ox), int(fy + oy)), _cor_silv("f"))
        sup.set_at((int(fx), int(fy)), _cor_silv("F"))
    # o PESCOÇO: sobe fazendo um S e a cabeça cai pra FRENTE (na câmera)
    topo = (bx + 6 * (1 - recua), by - 48 - 6 * recua)
    cab = (bx + 2 * (1 - avanca), by - 40 - 6 * recua + 10 * avanca)
    pts = [(bx, by - 21), (bx - 5, by - 32), (topo[0], topo[1]), (cab[0], cab[1] - 6)]
    pygame.draw.lines(sup, borda, False, pts, 6)
    pygame.draw.lines(sup, _cor_silv("g"), False, pts, 4)
    pygame.draw.lines(sup, _cor_silv("G"), False, [(x - 1, y) for x, y in pts[:3]], 1)
    r = 9 * (1 + 0.35 * avanca) * (1 - 0.1 * recua)  # (vindo na câmera = maior)
    _cabeca_planta_frente(sup, cab[0], cab[1], r, boca, t, runa)
    return cab, r


def semente_voando(tela, x, y, esc, t=0):
    """A SEMENTE cuspida vindo na câmera, em pixel art (pra cena): a sementinha marrom com o brotinho, girando."""
    peq = pygame.Surface((9, 9), pygame.SRCALPHA)
    pygame.draw.ellipse(peq, (16, 22, 14), (1, 2, 7, 7))
    pygame.draw.ellipse(peq, (104, 82, 52), (2, 3, 5, 5))
    peq.set_at((3, 4), (146, 116, 74))
    pygame.draw.line(peq, (72, 150, 60), (4, 2), (5, 0))
    peq.set_at((6, 0), (124, 200, 92))
    peq = pygame.transform.rotate(peq, (t * 25) % 360 // 90 * 90)
    img = pygame.transform.scale(peq, (round(9 * esc), round(9 * esc)))
    tela.blit(img, (round(x - 4.5 * esc), round(y - 4.5 * esc)))


def _silvanus(b, e, pose, t, f, prog=None):
    k = None if pose != "ataque" else ((t % 60) / 60 if prog is None else max(0.0, min(1.0, prog)))
    boca = recua = avanca = 0.0
    if k is not None:
        if k < 0.35:  # RECOLHE o pescoço (enche as bochechas)
            recua = _suave_noct(k / 0.35)
        elif k < 0.6:  # COSPE: a cabeça vem pra câmera de boca aberta
            a = _suave_noct((k - 0.35) / 0.1)
            recua, avanca, boca = 1 - a, a, 1.0
        else:
            a = _suave_noct((k - 0.6) / 0.4)
            avanca, boca = 1 - a, max(0.0, 1 - a * 3)
    cab, r = _desenha_silvanus_frente(b, t, boca, recua, avanca, runa=k is not None)

    def unid(px):
        return ((px[0] - b.ox) / b.k, (b.oy - px[1]) / b.k)
    res = dict(olhos=unid(cab), mao=unid(cab), cabeca=unid(cab))
    if k is not None:
        res["soltou"] = k >= 0.45
    return res


LUTADORES.update({"SILVANUS": _silvanus})
LARGO.update({"SILVANUS": 1.2})
