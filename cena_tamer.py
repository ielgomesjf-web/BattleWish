"""CENAS DE ANIME do TAMER (loja).

ENTRADA (MONTADO NO LOBO): a câmera no chão: as PATAS do lobo galopando... o Tamer MONTADO, gritando de braços pra
cima... o lobo FREIA derrapando, ele SALTA dando uma cambalhota... faz CARINHO no lobo e o lobo UIVA.
VITÓRIA (FOGUEIRA): cai a NOITE: ele bate as pedras (faísca!) e acende a FOGUEIRA... o MARSHMALLOW tostando...
ele DIVIDE com o lobo (nham!)... e o lobo UIVA pra lua.
O Tamer e o lobo aparecem com o desenho do jogo (o lobo desenhado à parte, pra correr/frear/sentar); o fogo, o
marshmallow, a noite e os vagalumes são ilustrados.
"""
import math
import random

import pygame

import cutscene
import tamer
from cena_max import cores_do_mapa, chao_perto, fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

XT, XO = LARGURA * 0.34, LARGURA * 0.74  # o Tamer e o oponente, no mapa
COR_NOME = (150, 120, 60)


def pose(c, nome):
    if nome == "sentado":
        import vitorias_loja
        return vitorias_loja.p_(c.l, "sentado")
    return c.l.poses.get(nome) or c.l.poses["parado"]


def tamer_por(c, base, p, x, y=CHAO, d=1, ang=0.0):
    """O Tamer SEM o lobo do desenho (o lobo é desenhado à parte, com lobo())."""
    l = c.lutador()
    l.extra["lobo_some"] = True
    try:
        img, pe = c.corpo(p, 1.0, d, guardar=False)
    finally:
        l.extra["lobo_some"] = False
    if ang:
        r = img.get_bounding_rect()
        img = img.subsurface(r)
        cx, cy = r.centerx - pe[0], r.centery - pe[1]
        img = pygame.transform.rotate(img, ang)
        base.blit(img, (int(x + cx - img.get_width() / 2), int(y + cy - img.get_height() / 2)))
        return
    base.blit(img, (int(x - pe[0]), int(y - pe[1])))


def montado(c, braco="t_monta"):
    """SENTADO nas costas do lobo (as pernas abertas pros lados do corpo do lobo) e os braços da pose 'braco'."""
    p = dict(pose(c, "sentado"))
    b = pose(c, braco) if isinstance(braco, str) else braco
    qd_b, qd_s = b["qd"], p["qd"]
    for k_ in ("ct", "mt", "cf", "mf", "pc", "cb"):  # (o tronco e os braços da outra pose, presos no quadril sentado)
        p[k_] = (b[k_][0] - qd_b[0] + qd_s[0], b[k_][1] - qd_b[1] + qd_s[1])
    return p


def costas_lobo(c, chao=CHAO, escala=1.0):
    """A altura das COSTAS do lobo (onde ele senta)."""
    u = c.l.s / tamer.S_REF * escala * 0.62 * tamer.LOBO_MAIOR
    return chao - 30 * u


def tamer_montado(c, base, braco, x, t, chao=CHAO, pula=0.0):
    """O Tamer SENTADO no lobo: o quadril em cima das costas dele."""
    p = montado(c, braco)
    qd_y = p["qd"][1] * c.l.s
    tamer_por(c, base, p, x - 6, costas_lobo(c, chao) + qd_y - pula)


def lobo(c, base, x, pose_lobo, t, d=1, chao=CHAO, escala=1.0):
    """O LOBO do jogo (o da cor e da roupa do Tamer)."""
    esc = c.l.s / tamer.S_REF * escala
    tamer.desenha_lobo(base, x, chao, esc, d, pose_lobo, t, c.lutador().extra.get("lobo_cor", "branco"),
                       tamer.skin_lobo_f(c.ficha))


# =====================================================================
# ENTRADA: MONTADO NO LOBO
# =====================================================================
def e1_patas(c, q, t, k):
    """1) CÂMERA NO CHÃO: o lobo vem GALOPANDO pra cima da câmera (as patas, a poeira subindo)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    x = -100 + (XT + 60) * suave(k)
    lobo(c, base, x, "corre", t * 2)
    tamer_montado(c, base, "t_monta", x, t)
    for i in range(6):  # a poeira dos passos
        u = (t * 3 + i * 9) % 30
        pygame.draw.circle(base, (190, 170, 130), (int(x - 40 - u * 3), int(CHAO - 4 - u * 0.4)), max(2, 10 - u // 4))
    c.mapa_frente(base, t)
    c.camera(q, base, (x + 30, CHAO - 30), 3.2, pixel=True)
    c.tremor = max(c.tremor, 2 if (t // 4) % 2 else 0)
    texto_pow(q, "TUDUM TUDUM", (int(w * 0.7), int(h * 0.2)), 40, (240, 230, 200), t % 8, giro=0.05)


def e2_monta(c, q, t, k):
    """2) De lado, acompanhando: o Tamer MONTADO, gritando de BRAÇOS PRA CIMA, o vento, a poeira."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 40)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    x = XT - 80 + 90 * k
    pula = abs(math.sin(t * 0.3)) * 6
    lobo(c, base, x, "corre", t * 2, chao=CHAO - pula * 0.3)
    p = misturar(pose(c, "t_monta"), pose(c, "t_grito"), suave(min(1, max(0, t - 8) / 8)))
    tamer_montado(c, base, p, x, t, CHAO - pula * 0.3, pula)
    c.mapa_frente(base, t + 40)
    c.camera(q, base, (x + 30, CHAO - 135), 1.9, pixel=True)
    cutscene.linhas_horizontais(q, (255, 255, 255), int(h * 0.2), int(h * 0.8), 10, t, velocidade=50, alfa=70)
    if t > 10:
        texto_pow(q, "IIIIRRRAAA!!", (int(w * 0.62), int(h * 0.22)), 58, (255, 230, 160), (t - 10) % 8, giro=0.06)


def e3_freia(c, q, t, k):
    """3) O lobo FREIA derrapando (poeira!) e o Tamer SALTA dando uma CAMBALHOTA... e cai do lado dele."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 80)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    xl = XT + 10 + 30 * suave(min(1, t / 10))
    lobo(c, base, xl, "corre" if t < 10 else "parado", t * 2)
    if t < 10:
        poeira(base, xl - 20, CHAO, t / 10, cor=(190, 170, 130), larg=60, semente=2)
    else:
        poeira(base, xl - 20, CHAO, min(1, 0.5 + (t - 10) / 30), cor=(190, 170, 130), larg=90, semente=2)
    salta = 4
    u = min(1, max(0, (t - salta) / 22))
    if u < 1:
        x = xl - 4 + 60 * u
        if u <= 0:
            tamer_montado(c, base, "t_monta", xl, t)
        else:
            y = costas_lobo(c) * (1 - u) + CHAO * u - math.sin(u * math.pi) * 110
            tamer_por(c, base, pose(c, "pulo"), x, y, ang=-360 * suave(u))
    else:
        tamer_por(c, base, misturar(pose(c, "agachado"), pose(c, "parado"), suave(min(1, (t - salta - 22) / 8))), xl + 56)
    c.mapa_frente(base, t + 80)
    c.camera(q, base, (xl + 40, CHAO - 120), 1.9, pixel=True)
    if t == 2:
        c.tremor = 6
    if t < 14:
        texto_pow(q, "SKRRRT!", (int(w * 0.3), int(h * 0.62)), 50, (230, 210, 170), t, giro=-0.08)


def e4_carinho(c, q, t, k):
    """4) CARINHO no lobo... e o lobo UIVA (AUUUU!). O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 120)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    xl = XT + 40
    uiva = t >= 30
    lobo(c, base, xl, "uiva" if uiva else "parado", t)
    if t < 30:  # (virado pro lobo, fazendo carinho na cabeça dele)
        tamer_por(c, base, pose(c, "t_carinho"), xl + 78, d=-1)
    else:  # (e se vira pro oponente, apontando)
        tamer_por(c, base, misturar(pose(c, "parado"), pose(c, "t_aponta"), suave(min(1, (t - 30) / 10))), xl + 92)
    c.mapa_frente(base, t + 120)
    c.camera(q, base, (xl + 50, CHAO - 100), 2.2 - 0.3 * suave(min(1, t / 60)), pixel=True)
    if uiva and t < 64:
        texto_pow(q, "AUUUUUUU!", (int(w * 0.3), int(h * 0.22)), 60, (230, 240, 255), (t - 30) % 10, giro=-0.06)
    if t >= 40:
        faixa_nome(q, "TAMER", "O DOMADOR DA SELVA.", COR_NOME, (t - 40) / 30)


PLANOS = [
    (44, e1_patas, {0: ("queda", 0.3), 10: ("queda", 0.3), 20: ("queda", 0.3), 30: ("queda", 0.3)}),
    (44, e2_monta, {10: ("uivo", 0.4)}),
    (40, e3_freia, {2: ("vento", 0.8), 26: ("queda", 0.6)}),
    (100, e4_carinho, {30: ("uivo", 0.9)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: FOGUEIRA
# =====================================================================
FX = XT + 90  # onde fica a fogueira


def noite(q, f=0.7):
    sup = pygame.Surface(q.get_size())
    sup.fill(tuple(int(255 * (1 - f) + v * f) for v in (30, 34, 80)))
    q.blit(sup, (0, 0), special_flags=pygame.BLEND_RGB_MULT)


def estrelas_noite(q, t, alto):
    rnd = random.Random(8)
    for i in range(60):
        x, y = rnd.uniform(0, q.get_width()), rnd.uniform(0, alto)
        b = 160 + int(90 * abs(math.sin(t * 0.05 + i)))
        q.set_at((int(x), int(y)), (b, b, 255))
    pygame.draw.circle(q, (250, 248, 220), (int(q.get_width() * 0.78), 70), 26)  # a LUA
    pygame.draw.circle(q, (225, 222, 196), (int(q.get_width() * 0.78) + 8, 64), 6)


def fogueira(base, x, t, acesa):
    """A FOGUEIRA: o círculo de pedras, as toras e as CHAMAS (acesa 0..1)."""
    s = 1.3
    if acesa > 0:
        brilho(base, (int(x), int(CHAO - 30)), int(170 * acesa), (255, 150, 60), int(90 * acesa))
        pygame.draw.ellipse(base, (255, 170, 80), (x - 110, CHAO - 6, 220, 14))
    for i in range(7):  # as pedras
        a = math.pi * (i / 6)
        px = x + math.cos(a) * 30 * s
        pygame.draw.ellipse(base, (30, 26, 24), (px - 8 * s, CHAO - 9 * s, 16 * s, 11 * s))
        pygame.draw.ellipse(base, (130, 124, 116), (px - 7 * s, CHAO - 8 * s, 14 * s, 9 * s))
    for a in (-0.5, 0.5, 0.0):  # as toras
        x1, y1 = x - math.cos(a) * 26 * s, CHAO - 4 * s
        x2, y2 = x + math.cos(a) * 26 * s, CHAO - 4 * s - (16 * s if a == 0 else 10 * s)
        pygame.draw.line(base, (36, 20, 10), (x1, y1), (x2, y2), max(6, int(9 * s)))
        pygame.draw.line(base, (110, 70, 36), (x1, y1), (x2, y2), max(4, int(6 * s)))
    if acesa > 0:
        for i in range(4):  # as CHAMAS dançando
            hh = (54 - i * 10 + math.sin(t * 0.45 + i * 1.7) * 9) * s * acesa
            ww = (24 - i * 5) * s
            cor = ((200, 50, 20), (250, 120, 30), (255, 190, 60), (255, 245, 180))[i]
            topo = (x + math.sin(t * 0.3 + i) * 5 * s, CHAO - 10 * s - hh)
            pygame.draw.polygon(base, cor, [(x - ww, CHAO - 10 * s), (x - ww * 0.6, CHAO - 10 * s - hh * 0.5), topo,
                                            (x + ww * 0.6, CHAO - 10 * s - hh * 0.55), (x + ww, CHAO - 10 * s)])
        for i in range(5):  # as fagulhas subindo
            u = ((t * 0.03) + i / 5) % 1
            pygame.draw.circle(base, (255, 200, 90), (int(x + math.sin(i * 2 + t * 0.1) * 14), int(CHAO - 60 - u * 120)), 2)


def cena_noite(c, t, acesa, lobo_pose="parado", lobo_x=None):
    """O mapa de NOITE com a fogueira, o lobo e o derrotado lá longe."""
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO + 40, CHAO)
    noite(base, 0.7)
    estrelas_noite(base, t, CHAO - 260)
    lobo(c, base, lobo_x if lobo_x is not None else FX + 150, lobo_pose, t, d=-1, escala=0.8)
    fogueira(base, FX, t, acesa)
    return base


def v1_acende(c, q, t, k):
    """1) Cai a NOITE... ele bate as PEDRAS (TIC! TIC! faísca)... e a FOGUEIRA pega: FWOOSH!"""
    w, h = q.get_size()
    acende = 30
    base = cena_noite(c, t, 0 if t < acende else min(1, (t - acende) / 8))
    p = misturar(pose(c, "parado"), pose(c, "agachado"), suave(min(1, t / 10)))
    tamer_por(c, base, p, FX - 60)
    mao = c.ponto(p, "mf", 1.0, FX - 50, CHAO)
    for b in (14, 22):  # as FAÍSCAS das pedras
        if b <= t < b + 6:
            for i in range(8):
                a = -math.pi / 2 + (i - 3.5) * 0.3
                r = (t - b) * 6
                pygame.draw.line(base, (255, 230, 120), (mao[0] + math.cos(a) * r, mao[1] + math.sin(a) * r),
                                 (mao[0] + math.cos(a) * (r + 6), mao[1] + math.sin(a) * (r + 6)), 2)
    c.camera(q, base, (FX, CHAO - 80), 2.3, pixel=True)
    for b, txt in ((14, "TIC!"), (22, "TIC!")):
        if b <= t < b + 8:
            texto_pow(q, txt, (int(w * 0.4), int(h * 0.3)), 44, (255, 240, 180), t - b)
    if acende <= t < acende + 14:
        c.tremor = max(c.tremor, 3)
        texto_pow(q, "FWOOSH!", (int(w * 0.62), int(h * 0.26)), 60, (255, 200, 90), t - acende)


def marshmallow(q, x, y, r, tost):
    """O MARSHMALLOW (branquinho -> douradinho -> tostado)."""
    cor = (int(250 - 90 * tost), int(240 - 130 * tost), int(230 - 170 * tost))
    pygame.draw.circle(q, (40, 30, 20), (int(x), int(y)), int(r) + 3)
    pygame.draw.circle(q, cor, (int(x), int(y)), int(r))
    pygame.draw.circle(q, tuple(min(255, v + 30) for v in cor), (int(x - r * 0.3), int(y - r * 0.3)), int(r * 0.35))


def v2_marsh(c, q, t, k):
    """2) CLOSE: o MARSHMALLOW no graveto, tostando em cima do fogo (fica douradinho)."""
    w, h = q.get_size()
    fundo_desfocado(c, q, t, (FX, CHAO - 60), 3.0, 140)
    noite(q, 0.55)
    brilho(q, (int(w * 0.5), int(h * 0.9)), 360, (255, 140, 40), 160)
    for i in range(5):  # as chamas de pertinho, embaixo
        hh = 200 + math.sin(t * 0.4 + i * 1.3) * 40 - i * 20
        ww = 220 - i * 30
        cor = ((200, 50, 20), (250, 120, 30), (255, 190, 60), (255, 245, 180), (255, 255, 230))[i]
        pygame.draw.polygon(q, cor, [(w * 0.5 - ww, h), (w * 0.5 + math.sin(t * 0.3 + i) * 30, h - hh), (w * 0.5 + ww, h)])
    gx, gy = w * 0.5 + math.sin(t * 0.08) * 20, h * 0.42  # o graveto e o marshmallow girando
    pygame.draw.line(q, (40, 26, 14), (-20, h * 0.1), (gx, gy), 16)
    pygame.draw.line(q, (110, 72, 40), (-20, h * 0.1), (gx, gy), 10)
    marshmallow(q, gx + 10, gy + 10, 46, min(1, t / 40))
    if t > 28:
        texto_pow(q, "hmmm~", (int(w * 0.74), int(h * 0.26)), 46, (255, 230, 200), (t - 28) % 12)


def v3_divide(c, q, t, k):
    """3) Ele DIVIDE com o lobo: estende o graveto... o lobo abocanha (NHAM!) e abana o rabo."""
    w, h = q.get_size()
    base = cena_noite(c, t + 40, 1.0, "morde" if 20 <= t < 34 else "parado", FX + 150)
    p = pose(c, "sentado")
    sy = CHAO - 30 * c.l.s * 0.6
    tamer_por(c, base, p, FX - 60, sy)
    estende = suave(min(1, t / 16))
    mao = c.ponto(p, "mf", 1.0, FX - 60, sy)
    ponta = (mao[0] + 70 + 110 * estende, mao[1] - 20 + 10 * estende)
    pygame.draw.line(base, (70, 44, 22), mao, ponta, 3)
    if t < 26:
        marshmallow(base, ponta[0], ponta[1], 6, 1.0)
    c.camera(q, base, (FX + 40, CHAO - 80), 2.0, pixel=True)
    if 22 <= t < 36:
        texto_pow(q, "NHAM!", (int(w * 0.66), int(h * 0.3)), 56, (255, 240, 220), t - 22)
    if t >= 36:  # coraçãozinho
        hx, hy = w * 0.68, h * 0.34 - (t - 36) * 2
        pygame.draw.circle(q, (240, 90, 120), (int(hx - 8), int(hy)), 10)
        pygame.draw.circle(q, (240, 90, 120), (int(hx + 8), int(hy)), 10)
        pygame.draw.polygon(q, (240, 90, 120), [(hx - 17, hy + 3), (hx + 17, hy + 3), (hx, hy + 22)])


def vagalumes(q, t, n=14):
    w, h = q.get_size()
    rnd = random.Random(6)
    for i in range(n):
        x = (rnd.uniform(0, w) + math.sin(t * 0.03 + i) * 40) % w
        y = rnd.uniform(h * 0.3, h * 0.8) + math.sin(t * 0.05 + i * 2) * 20
        if (t // 6 + i) % 4:
            brilho(q, (int(x), int(y)), 10, (220, 255, 120), 200)
            pygame.draw.circle(q, (240, 255, 180), (int(x), int(y)), 2)


def v4_uiva(c, q, t, k):
    """4) De longe: a noite, a lua, a fogueira estalando, ele sentado... e o LOBO UIVANDO pra lua. O nome."""
    w, h = q.get_size()
    base = cena_noite(c, t + 90, 1.0, "uiva" if t >= 16 else "parado", FX + 150)
    tamer_por(c, base, pose(c, "sentado"), FX - 60, CHAO - 30 * c.l.s * 0.6)
    c.camera(q, base, ((FX + XO) / 2 - 60, CHAO - 160), 1.4, pixel=True)
    vagalumes(q, t)
    if 16 <= t < 60:
        texto_pow(q, "AUUUUUUUUU~", (int(w * 0.62), int(h * 0.2)), 50, (230, 240, 255), (t - 16) % 12, giro=-0.05)
    if t >= 40:
        faixa_nome(q, "TAMER", "NOITE NA SELVA.", COR_NOME, (t - 40) / 30)


PLANOS_FOGUEIRA = [
    (46, v1_acende, {14: ("soco", 0.3), 22: ("soco", 0.3), 30: ("foguete", 0.7)}),
    (48, v2_marsh, {0: ("puf", 0.2), 24: ("puf", 0.2)}),
    (50, v3_divide, {22: ("lingua", 0.6)}),
    (100, v4_uiva, {16: ("uivo", 0.9), 60: ("puf", 0.2)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_FOGUEIRA, titulo, oponente)
