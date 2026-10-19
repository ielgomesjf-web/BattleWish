"""CENAS DE ANIME do KING RIP (loja), com as ideias do Gomes.

ENTRADA (FOLHA CORTADA): imagem de CÂMERA GRAVANDO (balançando na mão, REC piscando): ele vem andando calmo com
as mãos pra trás, a câmera ABRE ESPAÇO pra ele passar... uma folha cai... e ele faz que nem ESPADACHIM (só puxa o
nunchaku e já corta): a folha cai em duas.
VITÓRIA (NUNCHAKU MESTRE): uma DANÇA de luta com o nunchaku (girando, passando pelas costas, por cima da cabeça)
e termina com um CHUTE (a câmera mostra o corpo inteiro dando o chute).
O King aparece com o desenho do jogo (o nunchaku é o dele, desenhado na mão).
"""
import math
import random

import pygame

import cutscene
import king
from cena_max import fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

BORDA = (16, 16, 24)
XK, XO = LARGURA * 0.36, LARGURA * 0.74  # o King e o oponente, no mapa
COR_NOME = (50, 90, 190)

MAOS_ATRAS = dict(pt=(-18, 0), jt=(-14, 28), pf=(18, 0), jf=(16, 28), qd=(0, 56), pc=(2, 92), cb=(4, 110),
                  ct=(-10, 74), mt=(-16, 58), cf=(-6, 76), mf=(-12, 60))  # (andando calmo, as mãos nas costas)


def pose(c, nome):
    if nome == "maos_atras":
        return dict(MAOS_ATRAS)
    return c.l.poses.get(nome) or c.l.poses["parado"]


def king_por(c, base, p, x, y=CHAO, d=1, girando=False, t=0):
    """O King (desenho do jogo, com o nunchaku dele na mão). girando = o nunchaku virando um borrão."""
    l = c.lutador()
    l.memo["girando"] = girando
    l.t = t
    c.por(base, p, 1.0, x, y, d, guardar=False)


def gravando(q, t):
    """A imagem de CÂMERA GRAVANDO: cantos do visor, REC piscando e o tempo correndo."""
    from efeitos import texto
    w, h = q.get_size()
    for cx, cy, dx, dy in ((60, 70, 1, 1), (w - 60, 70, -1, 1), (60, h - 70, 1, -1), (w - 60, h - 70, -1, -1)):
        pygame.draw.line(q, (255, 255, 255), (cx, cy), (cx + dx * 40, cy), 3)
        pygame.draw.line(q, (255, 255, 255), (cx, cy), (cx, cy + dy * 40), 3)
    if (t // 20) % 2 == 0:
        pygame.draw.circle(q, (230, 30, 30), (96, 104), 9)
    texto(q, "REC", 22, (255, 255, 255), (134, 104))
    seg = t // 60
    texto(q, f"00:0{seg}:{(t % 60) * 100 // 60:02d}", 20, (255, 255, 255), (w - 130, 104))
    pygame.draw.line(q, (255, 255, 255), (w / 2 - 14, h / 2), (w / 2 + 14, h / 2), 1)
    pygame.draw.line(q, (255, 255, 255), (w / 2, h / 2 - 14), (w / 2, h / 2 + 14), 1)


def balanca(t, forca=1.0):
    """O balanço da câmera na mão (respirando, passos)."""
    return (math.sin(t * 0.13) * 10 + math.sin(t * 0.31) * 4) * forca, (math.sin(t * 0.17 + 1) * 6 + math.sin(t * 0.4) * 2) * forca


def folha(q, x, y, tam, ang, cor=(110, 170, 60), metade=0, abre=0.0):
    """Uma FOLHA (inteira, ou metade=-1/+1: os dois pedaços depois do corte, se afastando com abre)."""
    pts = []
    for i in range(12):
        a = i / 11 * math.pi
        pts.append((math.cos(a) * tam, math.sin(a) * tam * 0.38))
    pts2 = [(-px, -py) for px, py in pts]
    forma = pts + pts2
    if metade:
        forma = [p for p in forma if (p[1] >= 0) == (metade > 0)] + [(-tam, 0), (tam, 0)]
        forma.sort(key=lambda p: math.atan2(p[1] - (0.1 if metade > 0 else -0.1), p[0]))
    c, s = math.cos(ang), math.sin(ang)
    off = (0, metade * abre)
    pts = [(x + (px + off[0]) * c - (py + off[1]) * s, y + (px + off[0]) * s + (py + off[1]) * c) for px, py in forma]
    if len(pts) >= 3:
        pygame.draw.polygon(q, BORDA, pts, 0)
        pygame.draw.polygon(q, cor, [(px + (x - px) * 0.06, py + (y - py) * 0.06) for px, py in pts])
    pygame.draw.line(q, tuple(int(v * 0.6) for v in cor), (x - c * tam, y - s * tam), (x + c * tam, y + s * tam), max(1, int(tam * 0.06)))


# =====================================================================
# ENTRADA: FOLHA CORTADA
# =====================================================================
def e1_anda(c, q, t, k):
    """1) CÂMERA GRAVANDO (na mão, balançando): ele vem ANDANDO calmo, mãos pra trás... quando chega perto,
    a câmera ABRE ESPAÇO (vira pro lado) e ele passa."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    x = XK - 220 + 3.2 * t
    fase = t * 0.12
    andar = ("andar1", "andar2", "andar3", "andar4")
    i = int(fase) % 4
    p = misturar(pose(c, andar[i]), pose(c, andar[(i + 1) % 4]), fase % 1)
    p = dict(p, ct=MAOS_ATRAS["ct"], mt=MAOS_ATRAS["mt"], cf=MAOS_ATRAS["cf"], mf=MAOS_ATRAS["mf"])  # (mãos nas costas)
    king_por(c, base, p, x, t=t)
    c.mapa_frente(base, t)
    abre = suave(min(1, max(0, t - 36) / 26))  # a câmera "dando licença": dá um passo pro lado e abre
    bx, by = balanca(t)
    centro = (x + 70 - 40 * abre + bx, CHAO - 100 - 10 * abre + by)
    c.camera(q, base, centro, 2.5 - 1.0 * abre, pixel=True)
    gravando(q, t)


def e2_folha(c, q, t, k):
    """2) A FOLHA caindo devagar entre ele e o oponente... ele PARA (olhos fechados). Silêncio."""
    w, h = q.get_size()
    fundo_desfocado(c, q, t, (XK + 60, CHAO - 120), 2.4, 30)
    base = c._tela_aux()
    c.mapa(base, t + 70)
    king_por(c, base, pose(c, "maos_atras"), XK, t=t)
    c.mapa_frente(base, t + 70)
    cb = c.ponto(pose(c, "maos_atras"), "cb", 1.0, XK, CHAO)
    c.camera(q, base, (cb[0] + 50, cb[1] + 14), 3.0, pixel=True)
    fx = w * 0.62 + math.sin(t * 0.09) * 60
    fy = -40 + t * 4.2
    folha(q, fx, fy, 48, math.sin(t * 0.08) * 0.8)


IAI = 8  # o quadro do CORTE (dentro do plano 3)


def e3_iai(c, q, t, k):
    """3) O CORTE de espadachim: tela parada... um CLARÃO, e ele já está do outro lado com o nunchaku esticado
    (a linha do corte atravessa a tela). SHING!"""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 110)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    if t < IAI:
        king_por(c, base, pose(c, "maos_atras"), XK, t=t)
    else:
        king_por(c, base, pose(c, "k_gira"), XK + 70, t=t)
    c.mapa_frente(base, t + 110)
    c.camera(q, base, (XK + 120, CHAO - 100), 2.0, pixel=True)
    fx, fy = w * 0.6, h * 0.42
    if t < IAI:
        folha(q, fx, fy, 30, 0.3)
        if t > 2:  # (o olho abre: um brilho)
            brilho(q, (int(w * 0.36), int(h * 0.3)), 20, (255, 255, 255), 200)
    else:
        u = min(1, (t - IAI) / 4)
        pygame.draw.line(q, (255, 255, 255), (-20, fy + 50), (-20 + (w + 40) * u, fy - 50), 6)  # a linha do corte
        pygame.draw.line(q, (200, 230, 255), (-20, fy + 54), (-20 + (w + 40) * u, fy - 46), 2)
        folha(q, fx, fy, 30, 0.3, metade=-1, abre=(t - IAI) * 1.5)
        folha(q, fx, fy, 30, 0.3, metade=1, abre=(t - IAI) * 1.5)
        if t == IAI:
            c.inverte, c.tremor = 3, 8
        texto_pow(q, "SHING!", (int(w * 0.5), int(h * 0.2)), 70, (255, 255, 255), t - IAI)


def e4_cai(c, q, t, k):
    """4) As duas METADES da folha caem devagar... ele guarda o nunchaku e fica em guarda. O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 130)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    p = misturar(pose(c, "k_gira"), pose(c, "k_bastao"), suave(min(1, max(0, t - 20) / 12)))
    king_por(c, base, p, XK + 70, t=t)
    c.mapa_frente(base, t + 130)
    c.camera(q, base, (XK + 120, CHAO - 100), 2.0 - 0.2 * suave(min(1, t / 60)), pixel=True)
    for lado in (-1, 1):  # as METADES caindo (cada uma pra um lado, rodando)
        fx = w * 0.6 + lado * (20 + t * 1.6) + math.sin(t * 0.1 + lado) * 20
        fy = h * 0.42 + t * 3.2
        if fy < h:
            folha(q, fx, fy, 30, 0.3 + lado * t * 0.05, metade=lado, abre=10)
    if t >= 30:
        faixa_nome(q, "KING RIP", "O MESTRE DO NUNCHAKU.", COR_NOME, (t - 30) / 30)


PLANOS = [
    (76, e1_anda, {0: ("vento", 0.3), 20: ("queda", 0.15), 40: ("queda", 0.15), 60: ("queda", 0.15)}),
    (50, e2_folha, {0: ("vento", 0.4)}),
    (30, e3_iai, {IAI: ("shuriken", 1.0), IAI + 1: ("vento", 0.8)}),
    (80, e4_cai, {20: ("blip", 0.4)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: NUNCHAKU MESTRE (a dança de luta e o CHUTE final)
# =====================================================================
KATA = [  # (quadros, pose, nunchaku girando) — a sequência da dança
    (10, "k_gira", True), (10, "k_cotovelo", False), (10, "k_costas", False), (10, "k_bastao", True),
    (10, "k_estrela", False), (10, "k_gira", True), (10, "k_cotovelo", False), (10, "k_arremessa", True),
]


def kata_pose(c, t):
    """A pose da dança no quadro t (desliza de uma pose pra outra) e se o nunchaku está girando."""
    tt = t
    for i, (dur, nome, gira) in enumerate(KATA):
        if tt < dur:
            prox = KATA[(i + 1) % len(KATA)][1]
            u = suave(max(0, (tt - dur * 0.55) / (dur * 0.45)))
            return misturar(pose(c, nome), pose(c, prox), u), gira and tt < dur * 0.7, nome
        tt -= dur
    return pose(c, KATA[-1][1]), False, KATA[-1][1]


def rastro(q, c, p, x, y, centro, z, cor=(255, 255, 255)):
    """O RASTRO do nunchaku (arco branco em volta da mão)."""
    mao = para_tela(centro, z, c.ponto(p, "mf", 1.0, x, y))
    r = 60 * z / 2
    pygame.draw.arc(q, cor, (mao[0] - r, mao[1] - r, r * 2, r * 2), 0.3, 2.6, 4)
    pygame.draw.arc(q, (200, 220, 255), (mao[0] - r * 0.8, mao[1] - r * 0.8, r * 1.6, r * 1.6), 0.6, 2.2, 2)


def v1_danca(c, q, t, k):
    """1) A DANÇA do nunchaku do lado do derrotado (girando, pelas costas, por cima da cabeça), WHOOSH."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    p, gira, nome = kata_pose(c, t)
    king_por(c, base, p, XK, girando=gira, t=t)
    c.mapa_frente(base, t)
    centro, z = (XK + 80 + math.sin(t * 0.04) * 30, CHAO - 100), 2.0
    c.camera(q, base, centro, z, pixel=True)
    if t % 10 < 6:
        rastro(q, c, p, XK, CHAO, centro, z)
    if t % 20 < 8:
        texto_pow(q, "WHOOSH!", (int(w * (0.25 if (t // 20) % 2 else 0.72)), int(h * 0.24)), 40, (230, 240, 255), t % 20,
                  giro=0.1)


def v2_perto(c, q, t, k):
    """2) MAIS PERTO, de baixo: o nunchaku virando um borrão, passando pelas costas... (a câmera gira em volta)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 80)
    p, gira, nome = kata_pose(c, t + 40)
    d = -1 if t < 20 else 1  # (a câmera "do outro lado" na metade: o King virado)
    king_por(c, base, p, XK, d=d, girando=gira, t=t)
    c.mapa_frente(base, t + 80)
    centro, z = (XK + 10, CHAO - 110), 3.2
    c.camera(q, base, centro, z, pixel=True)
    cutscene.linhas_velocidade(q, (w * 0.5, h * 0.45), (255, 255, 255), n=24, r_dentro=260, grossura=3, semente=t // 2, alfa=70)


CHUTE = 10  # o quadro em que o chute chega no ponto mais alto


def v3_chute(c, q, t, k):
    """3) O CHUTE FINAL: a câmera ABRE e mostra o CORPO INTEIRO esticado no chute... onda de ar no pé, HYAAA!"""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 120)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    if t < 6:
        p = misturar(pose(c, "k_arremessa"), pose(c, "k_agacha"), suave(t / 6))  # (a preparação)
    else:
        p = misturar(pose(c, "k_agacha"), pose(c, "k_chute_alto"), suave(min(1, (t - 6) / 4)))
    king_por(c, base, p, XK + 40, t=t)
    pe = c.ponto(p, "pf", 1.0, XK + 40, CHAO)
    if t >= CHUTE:  # a ONDA DE AR no pé
        u = min(1, (t - CHUTE) / 14)
        r = 10 + 60 * u
        pygame.draw.circle(base, (240, 248, 255), (int(pe[0] + 10), int(pe[1])), int(r), max(1, int(4 * (1 - u)) + 1))
        poeira(base, XK + 40, CHAO + 10, min(1, (t - CHUTE) / 20), cor=(220, 210, 190), n=6, larg=50, semente=6)
    c.mapa_frente(base, t + 120)
    centro, z = (XK + 70, CHAO - 110), 1.9  # (aberta: o corpo inteiro)
    c.camera(q, base, centro, z, pixel=True)
    if t == CHUTE:
        c.inverte, c.tremor = 3, 16
    if t >= CHUTE:
        px, py = para_tela(centro, z, pe)
        cutscene.linhas_velocidade(q, (px, py), (255, 255, 255), n=22, r_dentro=200, grossura=3, semente=t // 2,
                                   alfa=max(0, 90 - (t - CHUTE) * 5))
        texto_pow(q, "HYAAAA!!", (int(w * 0.3), int(h * 0.24)), 72, (255, 240, 200), t - CHUTE, giro=-0.08)


def v4_final(c, q, t, k):
    """4) Desce a perna devagar, gira o nunchaku uma última vez e fica na pose. O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 170)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    if t < 14:
        p = misturar(pose(c, "k_chute_alto"), pose(c, "parado"), suave(t / 14))
    else:
        p = misturar(pose(c, "parado"), pose(c, "k_bastao"), suave(min(1, (t - 14) / 10)))
    king_por(c, base, p, XK + 40, girando=14 <= t < 24, t=t)
    c.mapa_frente(base, t + 170)
    c.camera(q, base, ((XK + XO) / 2, CHAO - 100), 1.8, pixel=True)
    if t >= 24:
        faixa_nome(q, "KING RIP", "NUNCHAKU MESTRE.", COR_NOME, (t - 24) / 30)


PLANOS_NUNCHAKU = [
    (60, v1_danca, {0: ("vento", 0.5), 20: ("vento", 0.5), 40: ("vento", 0.5)}),
    (40, v2_perto, {0: ("vento", 0.6), 20: ("vento", 0.6)}),
    (40, v3_chute, {4: ("vento", 0.7), CHUTE: ("chute", 1.0)}),
    (80, v4_final, {14: ("vento", 0.4)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_NUNCHAKU, titulo, oponente)
