"""CENAS DE ANIME do TAI (loja).

ENTRADA (CAINDO DO CÉU): lá do alto, acima das nuvens, o Tai DESPENCA na pose de SHIKO, pegando FOGO feito um
meteoro... no mapa a sombra cresce, o oponente olha pra cima... KABOOOM (cratera)... ele dá um PISÃO de sumô
(DOSUN!) e joga o SAL.
VITÓRIA (TROFÉU GIGANTE): um troféu GIGANTE cai do céu do lado dele... ele agacha, faz FORÇA e ERGUE o troféu
(câmera de baixo, brilho dourado, confete caindo).
O Tai aparece com o desenho do jogo; o fogo, o troféu (o da vitória antiga), o sal e o confete são ilustrados.
"""
import math
import random

import pygame

import cutscene
from cena_max import fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

XT, XO = LARGURA * 0.34, LARGURA * 0.72  # o Tai e o oponente, no mapa
COR_NOME = (40, 50, 110)


def pose(c, nome):
    return c.l.poses.get(nome) or c.l.poses["parado"]


def tai_por(c, base, p, x, y=CHAO, d=1, escala=1.0):
    c.por(base, p, escala, x, y, d, guardar=False)


def nuvens(q, t, vel_y=0.0, semente=3, n=10, alfa=200):
    """Nuvens (passando pra cima quando ele está caindo)."""
    w, h = q.get_size()
    rnd = random.Random(semente)
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(n):
        x = rnd.uniform(-100, w)
        y = (rnd.uniform(0, h + 300) - t * vel_y * rnd.uniform(0.7, 1.3)) % (h + 300) - 150
        for j in range(5):
            pygame.draw.ellipse(sup, (255, 255, 255, alfa), (x + j * 40, y - (j % 2) * 18, 130, 60))
    q.blit(sup, (0, 0))


# =====================================================================
# ENTRADA: CAINDO DO CÉU
# =====================================================================
def e1_ceu(c, q, t, k):
    """1) LÁ NO ALTO, acima das nuvens: o Tai despencando na pose de SHIKO, PEGANDO FOGO como um meteoro
    (as nuvens passando pra cima, as linhas de vento)."""
    w, h = q.get_size()
    cutscene.degrade(q, (0, 0, w, h), (40, 90, 170), (170, 210, 250))
    nuvens(q, t, vel_y=-28, alfa=210)
    x, y = w * 0.5 + math.sin(t * 0.1) * 10, h * 0.86
    fogo = min(1, t / 16)
    alto = 260  # (a altura dele nessa escala, mais ou menos)
    brilho(q, (int(x), int(y - alto * 0.5)), int(220 * fogo) + 2, (255, 140, 40), int(150 * fogo))  # a AURA de fogo
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(26):  # as LABAREDAS subindo pelos lados (ele caindo: o fogo vai pra cima)
        u = ((i / 26) + t * 0.07) % 1
        lado = -1 if i % 2 else 1
        fx = x + lado * (70 + 30 * math.sin(i)) * (1 - u * 0.4)
        fy = y - u * (alto + 240)
        r = (34 - 22 * u) * fogo
        cor = ((255, 240, 160), (255, 170, 60), (240, 90, 30))[i % 3]
        pygame.draw.circle(sup, (*cor, int(230 * (1 - u * 0.7))), (int(fx), int(fy)), int(max(2, r)))
    q.blit(sup, (0, 0))
    tai_por(c, q, pose(c, "t_shiko"), x, y, escala=2.0)
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(12):  # a FRENTE do meteoro (embaixo: o fogo batendo no ar)
        a = math.pi * (0.1 + 0.8 * i / 11)
        r = (40 + 10 * math.sin(t * 0.6 + i)) * fogo
        pygame.draw.circle(sup, (255, 200 - (i % 3) * 50, 80, 200), (int(x + math.cos(a) * 110), int(y - 10 + math.sin(a) * 30)), int(r))
    q.blit(sup, (0, 0))
    for i in range(16):  # as linhas de vento (verticais, subindo)
        lx = (i * 67 + 13) % w
        ly = (h - (t * 30 + i * 53) % (h + 200))
        pygame.draw.line(q, (255, 255, 255), (lx, ly), (lx, ly + 90), 2)
    if t > 20:
        texto_pow(q, "FUUUUUUU...", (int(w * 0.24), int(h * 0.2)), 44, (255, 230, 180), (t - 20) % 10, giro=0.08)


def e2_sombra(c, q, t, k):
    """2) No MAPA: o oponente olha pra cima (!?)... a SOMBRA no chão vai crescendo... e o brilho vem descendo."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 50)
    c.por_oponente(base, "parado" if t < 16 else "defesa", 1.0, XO, CHAO)
    u = suave(k)
    sombra = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra, (0, 0, 0, int(60 + 120 * u)), (XT - 20 - 70 * u, CHAO - 6 - 4 * u, 40 + 140 * u, 12 + 8 * u))
    base.blit(sombra, (0, 0))
    brilho(base, (int(XT), int(-40 + 140 * u)), int(30 + 60 * u), (255, 170, 60), int(120 + 100 * u))
    c.mapa_frente(base, t + 50)
    c.camera(q, base, ((XT + XO) / 2, CHAO - 110), 1.6, pixel=True)
    if 6 <= t < 26:
        texto_pow(q, "!?", (int(w * 0.76), int(h * 0.3)), 70, (255, 230, 120), t - 6)


def e3_kaboom(c, q, t, k):
    """3) KABOOOM: ele CAI (quadro de impacto, o anel de poeira, a cratera, as pedras voando)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 90)
    c.por_oponente(base, "defesa", 1.0, XO + min(30, t * 3), CHAO)
    pygame.draw.ellipse(base, (60, 44, 30), (XT - 90, CHAO - 8, 180, 20))  # a CRATERA
    pygame.draw.ellipse(base, (30, 20, 14), (XT - 66, CHAO - 4, 132, 12))
    tai_por(c, base, pose(c, "agachado"), XT)
    rnd = random.Random(5)
    for i in range(16):  # as pedras voando
        vx, vy = rnd.uniform(-10, 10), rnd.uniform(-14, -5)
        px, py = XT + vx * t, CHAO - 10 + vy * t + 0.6 * t * t
        if py < CHAO:
            pygame.draw.circle(base, (110, 92, 70), (int(px), int(py)), 3 + i % 4)
    poeira(base, XT, CHAO, min(1, t / 16), cor=(200, 180, 150), larg=260, semente=3)
    c.mapa_frente(base, t + 90)
    c.camera(q, base, (XT + 60, CHAO - 100), 1.7, pixel=True)
    if t == 0:
        c.inverte, c.tremor = 4, 30
    texto_pow(q, "KABOOOOM!!", (int(w * 0.5), int(h * 0.2)), 90, (255, 200, 90), t)


def e4_dosun(c, q, t, k):
    """4) A poeira baixa: ele na cratera, ergue a perna (SHIKO)... e PISA: DOSUN! (outra onda no chão)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 110)
    c.por_oponente(base, "parado", 1.0, XO + 30, CHAO)
    pygame.draw.ellipse(base, (60, 44, 30), (XT - 90, CHAO - 8, 180, 20))
    pygame.draw.ellipse(base, (30, 20, 14), (XT - 66, CHAO - 4, 132, 12))
    pisa = 28
    if t < pisa:
        p = misturar(pose(c, "agachado"), pose(c, "t_shiko"), suave(min(1, t / 14)))
    else:
        p = misturar(pose(c, "t_shiko"), pose(c, "t_pisao"), suave(min(1, (t - pisa) / 3)))
    tai_por(c, base, p, XT)
    if t >= pisa:  # a ONDA no chão
        u = (t - pisa) / 20
        for lado in (-1, 1):
            ox = XT + lado * (30 + 220 * u)
            pygame.draw.ellipse(base, (180, 160, 130), (ox - 30, CHAO - 10, 60, 14), 3)
        poeira(base, XT, CHAO, min(1, u), cor=(200, 180, 150), larg=120, semente=8)
    if t < 20:
        poeira(base, XT, CHAO, 0.6 + t / 50, cor=(200, 180, 150), larg=260, semente=3)
    c.mapa_frente(base, t + 110)
    c.camera(q, base, (XT + 40, CHAO - 110), 2.0, pixel=True)
    if t == pisa:
        c.tremor = 20
    if pisa <= t < pisa + 16:
        texto_pow(q, "DOSUN!!", (int(w * 0.66), int(h * 0.26)), 76, (255, 230, 200), t - pisa)


def sal(base, x, y, t, t0):
    """O SAL jogado pro alto (cristaizinhos brilhando, caindo em arco)."""
    rnd = random.Random(12)
    u = t - t0
    for i in range(30):
        vx, vy = rnd.uniform(1, 6), rnd.uniform(-10, -4)
        px, py = x + vx * u, y + vy * u + 0.32 * u * u
        if py < CHAO:
            brilha = (t + i) % 6 < 2
            pygame.draw.circle(base, (255, 255, 255) if brilha else (220, 230, 240), (int(px), int(py)), 2 if brilha else 1)


def e5_sal(c, q, t, k):
    """5) Ele joga o SAL (o ritual do sumô, brilhando no ar)... e fica em guarda. O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 150)
    c.por_oponente(base, "parado", 1.0, XO + 30, CHAO)
    pygame.draw.ellipse(base, (60, 44, 30), (XT - 90, CHAO - 8, 180, 20))
    p = misturar(pose(c, "t_pisao"), pose(c, "t_sal"), suave(min(1, t / 10))) if t < 40 else \
        misturar(pose(c, "t_sal"), pose(c, "parado"), suave(min(1, (t - 40) / 10)))
    tai_por(c, base, p, XT)
    if t >= 10:
        mao = c.ponto(pose(c, "t_sal"), "mf", 1.0, XT, CHAO)
        sal(base, mao[0], mao[1], t, 10)
    c.mapa_frente(base, t + 150)
    c.camera(q, base, (XT + 50, CHAO - 110), 2.0 - 0.2 * suave(min(1, t / 50)), pixel=True)
    if 10 <= t < 24:
        texto_pow(q, "HA!", (int(w * 0.62), int(h * 0.24)), 56, (255, 255, 255), t - 10)
    if t >= 26:
        faixa_nome(q, "TAI", "O YOKOZUNA.", COR_NOME, (t - 26) / 30)


PLANOS = [
    (50, e1_ceu, {0: ("vento", 0.9), 20: ("foguete", 0.6)}),
    (34, e2_sombra, {6: ("blip", 0.5), 20: ("vento", 0.6)}),
    (24, e3_kaboom, {0: ("explosao", 1.0), 1: ("terra", 1.0)}),
    (50, e4_dosun, {28: ("terra", 0.9), 29: ("queda", 0.8)}),
    (76, e5_sal, {10: ("vento", 0.4)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: TROFÉU GIGANTE
# =====================================================================
XTR = XT + 110  # onde o troféu cai
ESC_TROFEU = 1.7


def trofeu(base, x, y, s=ESC_TROFEU):
    import vitorias_loja
    vitorias_loja.trofeu(base, x, y, s)


def confete(q, t, n=60, semente=4):
    w, h = q.get_size()
    rnd = random.Random(semente)
    cores = ((240, 60, 60), (60, 180, 240), (250, 210, 60), (120, 220, 90), (230, 120, 220))
    for i in range(n):
        x = (rnd.uniform(0, w) + math.sin(t * 0.08 + i) * 30) % w
        y = (rnd.uniform(-h, 0) + t * rnd.uniform(3, 6)) % (h + 40) - 20
        a = t * 0.2 + i
        pygame.draw.polygon(q, cores[i % 5], [(x + math.cos(a) * 6, y + math.sin(a) * 3), (x - math.cos(a) * 6, y - math.sin(a) * 3),
                                              (x - math.cos(a) * 6 + 2, y - math.sin(a) * 3 + 5), (x + math.cos(a) * 6 + 2, y + math.sin(a) * 3 + 5)])


def v1_cai(c, q, t, k):
    """1) Do lado do derrotado: um brilho no céu... o TROFÉU GIGANTE despenca do lado dele: BONK!"""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO + 20, CHAO)
    tai_por(c, base, pose(c, "parado"), XT)
    cai = 26
    if t < cai:
        u = (t / cai) ** 2
        trofeu(base, XTR, -200 + (CHAO + 200) * u)
        brilho(base, (int(XTR), int(-200 + (CHAO + 200) * u - 60)), 50, (255, 230, 120), 160)
    else:
        trofeu(base, XTR, CHAO + 2)
        if t - cai < 20:
            poeira(base, XTR, CHAO, (t - cai) / 20, cor=(210, 200, 170), larg=120, semente=6)
    c.mapa_frente(base, t)
    c.camera(q, base, ((XT + XTR) / 2, CHAO - 110), 1.8, pixel=True)
    if t == cai:
        c.tremor = 16
    if cai <= t < cai + 14:
        texto_pow(q, "BONK!!", (int(w * 0.66), int(h * 0.26)), 70, (255, 230, 120), t - cai)


def v2_forca(c, q, t, k):
    """2) Ele AGACHA, segura o troféu... e faz FORÇA (NNNGH!), tremendo, o suor voando."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 50)
    trofeu(base, XTR, CHAO + 2)
    treme = math.sin(t * 2.4) * 1.5
    tai_por(c, base, pose(c, "t_agarra"), XTR - 60 + treme)
    c.mapa_frente(base, t + 50)
    cb = c.ponto(pose(c, "t_agarra"), "cb", 1.0, XTR - 60, CHAO)
    centro, z = (cb[0] + 30, cb[1] + 40), 2.8
    c.camera(q, base, centro, z, pixel=True)
    c.tremor = max(c.tremor, 2)
    sx, sy = para_tela(centro, z, cb)
    for i in range(3):  # o SUOR voando
        u = (t * 0.08 + i / 3) % 1
        gx, gy = sx - 60 - u * 120, sy - 30 + u * 60 - i * 20
        pygame.draw.polygon(q, (150, 210, 255), [(gx, gy - 10), (gx + 6, gy + 3), (gx - 6, gy + 3)])
        pygame.draw.circle(q, (150, 210, 255), (int(gx), int(gy + 3)), 6)
    texto_pow(q, "NNNNGH!!", (int(w * 0.64), int(h * 0.22)), 56, (255, 220, 200), t % 8, giro=0.08)


def v3_ergue(c, q, t, k):
    """3) Câmera de BAIXO: ele ERGUE o troféu acima da cabeça (o brilho dourado, os raios de luz)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 90)
    u = suave(min(1, t / 14))
    p = misturar(pose(c, "t_agarra"), pose(c, "t_levanta"), u)
    tai_por(c, base, p, XTR - 60)
    m1, m2 = c.ponto(p, "mt", 1.0, XTR - 60, CHAO), c.ponto(p, "mf", 1.0, XTR - 60, CHAO)
    mx, my = (m1[0] + m2[0]) / 2, (m1[1] + m2[1]) / 2
    trofeu(base, mx + 4, my + 14 * ESC_TROFEU * (1 - u) * 0 + 6)
    c.mapa_frente(base, t + 90)
    centro, z = (XTR - 50, CHAO - 205), 1.35
    c.camera(q, base, centro, z, pixel=True)
    if u >= 1:
        tx, ty = para_tela(centro, z, (mx, my - 60))
        for i in range(10):  # os RAIOS de luz saindo do troféu
            a = t * 0.02 + i * math.tau / 10
            pygame.draw.line(q, (255, 240, 170), (tx + math.cos(a) * 60, ty + math.sin(a) * 60),
                             (tx + math.cos(a) * 300, ty + math.sin(a) * 300), 3)
        brilho(q, (int(tx), int(ty)), 140, (255, 220, 100), 140)
    if t == 14:
        c.tremor = 10
    if t >= 14:
        texto_pow(q, "UOOOOH!!", (int(w * 0.28), int(h * 0.24)), 60, (255, 230, 120), (t - 14) % 10, giro=-0.06)


def v4_festa(c, q, t, k):
    """4) De longe: ele com o troféu lá em cima, o CONFETE caindo, o derrotado no chão. O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 130)
    c.por_oponente(base, "caido", 1.0, XO + 20, CHAO)
    p = pose(c, "t_levanta")
    pula = abs(math.sin(t * 0.15)) * 6
    tai_por(c, base, p, XTR - 60, CHAO - pula)
    m1, m2 = c.ponto(p, "mt", 1.0, XTR - 60, CHAO - pula), c.ponto(p, "mf", 1.0, XTR - 60, CHAO - pula)
    trofeu(base, (m1[0] + m2[0]) / 2 + 4, (m1[1] + m2[1]) / 2 + 6)
    c.mapa_frente(base, t + 130)
    c.camera(q, base, ((XTR + XO) / 2 - 40, CHAO - 195), 1.3, pixel=True)
    confete(q, t)
    if t >= 30:
        faixa_nome(q, "TAI", "CAMPEÃO YOKOZUNA.", COR_NOME, (t - 30) / 30)


PLANOS_TROFEU = [
    (46, v1_cai, {0: ("vento", 0.5), 26: ("terra", 1.0), 27: ("defesa", 0.8)}),
    (40, v2_forca, {0: ("carga", 0.6)}),
    (44, v3_ergue, {14: ("confirma", 0.9)}),
    (96, v4_festa, {0: ("confirma", 0.5)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_TROFEU, titulo, oponente)
