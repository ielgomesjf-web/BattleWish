"""CENAS DE ANIME do CRÁQUEN (loja).

ENTRADA (TENTÁCULO): o chão do mapa RACHA, a água sobe borbulhando... corte pro FUNDO DO MAR: ele subindo montado
no TENTÁCULO do polvo gigante (as bolhas, os raios de luz)... no mapa o tentáculo ESTOURA do chão com ele em cima,
o oponente recua... o tentáculo o põe no chão e afunda, e ele ri: HAR HAR HAR!
VITÓRIA (TESOURO): um BAÚ despenca do lado do derrotado... ele abre (a luz DOURADA no rosto dele, os olhos
brilhando)... mergulha as mãos e joga as MOEDAS pro alto (chovendo na câmera)... e fica rindo em cima da montanha
de ouro.
O Cráquen aparece com o desenho do jogo; o tentáculo é o do jogo (ult2), o baú é o da vitória antiga; o fundo do mar
e as moedas são ilustrados.
"""
import math
import random

import pygame

import cutscene
import ult2
from cena_max import fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

XC, XO = LARGURA * 0.34, LARGURA * 0.72  # o Cráquen e o oponente, no mapa
AGUA, AGUA_ESC = (70, 150, 200), (14, 40, 70)
OURO, OURO_ESC = (255, 210, 60), (150, 100, 20)
COR_NOME = (50, 130, 140)


def pose(c, nome):
    return c.l.poses.get(nome) or c.l.poses["parado"]


def craq(c, base, p, x, y=CHAO, d=1, escala=1.0):
    c.por(base, p, escala, x, y, d, guardar=False)


def em_cima(c, base, p, ponta, escala=1.0):
    """Põe o Cráquen com a PONTA DA CAUDA de fantasma (o fundo do desenho) em cima da ponta do tentáculo."""
    img, pe = c.corpo(p, escala, guardar=False)
    r = img.get_bounding_rect()
    base.blit(img, (int(ponta[0] - r.centerx), int(ponta[1] - r.bottom + 6 * escala)))


def bolhas(q, t, n=30, semente=2, vel=3.0, cor=(190, 230, 250)):
    w, h = q.get_size()
    rnd = random.Random(semente)
    for i in range(n):
        x = rnd.uniform(0, w) + math.sin(t * 0.06 + i) * 10
        y = h - ((t * vel * rnd.uniform(0.6, 1.4) + rnd.uniform(0, h)) % (h + 40))
        pygame.draw.circle(q, cor, (int(x), int(y)), 3 + i % 4 * 2, 2)


# =====================================================================
# ENTRADA: TENTÁCULO
# =====================================================================
def e1_racha(c, q, t, k):
    """1) No MAPA: o chão TREME e RACHA... a ÁGUA sobe borbulhando pelas rachaduras. O oponente estranha."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    u = min(1, t / 30)
    rnd = random.Random(4)
    for i in range(9):  # as RACHADURAS (com a água brilhando dentro)
        a = math.pi + rnd.uniform(0, math.pi)
        comp = (40 + rnd.uniform(0, 90)) * u
        pts = [(XC, CHAO)]
        for j in range(3):
            pts.append((pts[-1][0] + math.cos(a + rnd.uniform(-0.4, 0.4)) * comp / 3, CHAO + 2 + j))
        pygame.draw.lines(base, AGUA, False, pts, 4)
        pygame.draw.lines(base, AGUA_ESC, False, pts, 2)
    pygame.draw.ellipse(base, AGUA, (XC - 50 * u, CHAO - 4, 100 * u + 2, 10))
    for i in range(8):  # as bolhas e os jatinhos de água
        v = (t * 3 + i * 11) % 40
        if u > 0.3:
            pygame.draw.circle(base, (200, 240, 255), (int(XC + (i - 4) * 12), int(CHAO - v)), max(1, 4 - v // 12), 1)
    c.mapa_frente(base, t)
    c.camera(q, base, ((XC + XO) / 2 - 30, CHAO - 80), 1.8, pixel=True)
    c.tremor = max(c.tremor, int(4 * u))
    if t > 20:
        texto_pow(q, "BLUB BLUB...", (int(w * 0.32), int(h * 0.3)), 40, (200, 240, 255), (t - 20) % 10)


def e2_fundo(c, q, t, k):
    """2) O FUNDO DO MAR: lá do escuro, ele vem SUBINDO montado no TENTÁCULO gigante (as bolhas, os raios de luz
    vindo da superfície)."""
    w, h = q.get_size()
    cutscene.degrade(q, (0, 0, w, h), (40, 110, 160), AGUA_ESC)
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(6):  # os RAIOS DE LUZ da superfície
        x = w * (0.1 + i * 0.17) + math.sin(t * 0.03 + i) * 30
        pygame.draw.polygon(sup, (200, 240, 255, 40), [(x - 20, 0), (x + 30, 0), (x + 120, h), (x + 40, h)])
    q.blit(sup, (0, 0))
    bolhas(q, t, 40, vel=4)
    u = suave(k)
    topo = (w * 0.5 + math.sin(t * 0.1) * 30, h * 1.15 - h * 0.75 * u)
    ult2.tentaculo(q, (w * 0.4, h + 140), (topo[0], topo[1] + 24), 150, t, 0.4, enrola=0.2)
    em_cima(c, q, pose(c, "q_comanda"), topo, 1.25)
    if t > 20:
        texto_pow(q, "HAR HAR...", (int(w * 0.72), int(h * 0.24)), 44, (200, 240, 255), (t - 20) % 12, giro=0.06)


def e3_estoura(c, q, t, k):
    """3) No MAPA: o TENTÁCULO ESTOURA do chão (água pra todo lado, quadro de impacto) com ele em cima!
    O oponente se protege."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 60)
    c.por_oponente(base, "defesa" if t > 2 else "parado", 1.0, XO + min(30, t * 2), CHAO)
    sai = suave(min(1, t / 14))
    topo = (XC + 20 + math.sin(t * 0.12) * 10, CHAO + 30 - 190 * sai)
    ult2.tentaculo(base, (XC - 20, CHAO + 40), topo, 34, t, 0.5, enrola=sai)
    em_cima(c, base, pose(c, "q_comanda"), topo)
    rnd = random.Random(3)
    for i in range(26):  # a ÁGUA espirrando
        vx, vy = rnd.uniform(-9, 9), rnd.uniform(-15, -5)
        px, py = XC + vx * t, CHAO - 10 + vy * t + 0.55 * t * t
        if py < CHAO:
            pygame.draw.circle(base, (170, 220, 250), (int(px), int(py)), 3 + i % 3)
    pygame.draw.ellipse(base, AGUA, (XC - 120, CHAO - 6, 240, 14))
    c.mapa_frente(base, t + 60)
    c.camera(q, base, (XC + 60, CHAO - 170), 1.3, pixel=True)
    if t == 0:
        c.inverte, c.tremor = 3, 24
    if t < 16:
        texto_pow(q, "SPLOOOSH!!", (int(w * 0.62), int(h * 0.26)), 76, (200, 240, 255), t, giro=0.08)


def e4_ri(c, q, t, k):
    """4) O tentáculo o PÕE no chão e afunda de volta... ele RI com a espada no alto: HAR HAR HAR! O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 100)
    c.por_oponente(base, "parado", 1.0, XO + 30, CHAO)
    desce = suave(min(1, t / 20))
    afunda = suave(min(1, max(0, t - 20) / 20))
    topo = (XC + 20, CHAO - 160 * (1 - desce) + 120 * afunda)
    if afunda < 1:
        clip = base.get_clip()
        base.set_clip((0, 0, LARGURA, CHAO + 2))
        ult2.tentaculo(base, (XC - 20, CHAO + 40), (topo[0] + 40 * desce, topo[1]), 34, t, 0.5, enrola=1 - afunda)
        base.set_clip(clip)
    pygame.draw.ellipse(base, AGUA, (XC - 90 + 60 * afunda, CHAO - 5, 180 - 120 * afunda, 12))
    if t < 20:
        em_cima(c, base, pose(c, "q_comanda"), (topo[0] + 40 * desce, topo[1]))
    else:
        craq(c, base, misturar(pose(c, "q_comanda"), pose(c, "q_ri"), suave(min(1, (t - 20) / 8))), XC + 60)
    c.mapa_frente(base, t + 100)
    c.camera(q, base, (XC + 60, CHAO - 160 + 50 * desce), 1.4 + 0.4 * desce, pixel=True)
    if 26 <= t < 70:
        texto_pow(q, "HAR HAR HAR!", (int(w * 0.66), int(h * 0.24)), 60, (200, 240, 255), (t - 26) % 10, giro=0.06)
    if t >= 40:
        faixa_nome(q, "CRÁQUEN", "O CAPITÃO FANTASMA.", COR_NOME, (t - 40) / 30)


PLANOS = [
    (40, e1_racha, {0: ("terra", 0.5), 20: ("puf", 0.3)}),
    (50, e2_fundo, {0: ("vento", 0.4), 20: ("lingua", 0.4)}),
    (36, e3_estoura, {0: ("explosao", 0.6), 1: ("puf", 1.0)}),
    (100, e4_ri, {26: ("uivo", 0.4)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: TESOURO
# =====================================================================
XB = XC + 110  # onde o baú cai


def bau(c, base, t_vit, x=XB):
    """O BAÚ do tesouro da vitória antiga (cai, abre, a montanha de moedas), no quadro t_vit dela."""
    import vitorias_loja
    l = c.lutador()
    l.x, l.dir, l.s = x - 60 * c.l.s, 1, c.l.s
    vitorias_loja.craquen_tesouro_ef(l, base, min(t_vit, vitorias_loja.TESOURO_JORRA + 50))  # (sem o balão de fala)


def moeda(q, x, y, r, giro):
    """Uma MOEDA de ouro (girando: fica fininha e volta), com a caveirinha."""
    larg = max(2, int(r * 2 * abs(math.cos(giro))))
    caixa = pygame.Rect(0, 0, larg, int(r * 2))
    caixa.center = (int(x), int(y))
    pygame.draw.ellipse(q, OURO_ESC, caixa.inflate(4, 4))
    pygame.draw.ellipse(q, OURO, caixa)
    if larg > r:
        pygame.draw.ellipse(q, (255, 240, 160), caixa.inflate(-larg * 0.5, -r * 0.8).move(-r * 0.2, -r * 0.3))
        pygame.draw.circle(q, OURO_ESC, caixa.center, max(1, int(r * 0.35)), max(1, int(r * 0.1)))


def chuva_moedas(q, t, t0, n=40):
    """MOEDAS chovendo NA FRENTE da câmera (grandes, girando)."""
    w, h = q.get_size()
    rnd = random.Random(9)
    for i in range(n):
        x = rnd.uniform(0, w)
        vel = rnd.uniform(6, 12)
        y = -60 + ((t - t0) * vel + rnd.uniform(0, h)) % (h + 120)
        moeda(q, x, y, rnd.uniform(10, 26), t * 0.3 + i)


def v1_bau(c, q, t, k):
    """1) Do lado do derrotado: um BAÚ despenca do céu: BONK! (ele olha, os olhos brilhando)."""
    import vitorias_loja
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO + 30, CHAO)
    craq(c, base, pose(c, "q_espera"), XC)
    bau(c, base, min(t, vitorias_loja.TESOURO_CAI + 10) if t < 30 else vitorias_loja.TESOURO_CAI + 10)
    c.mapa_frente(base, t)
    c.camera(q, base, ((XC + XB) / 2, CHAO - 90), 2.0, pixel=True)
    if t == vitorias_loja.TESOURO_CAI:
        c.tremor = 12
    if vitorias_loja.TESOURO_CAI <= t < vitorias_loja.TESOURO_CAI + 14:
        texto_pow(q, "BONK!", (int(w * 0.66), int(h * 0.26)), 60, (255, 230, 150), t - vitorias_loja.TESOURO_CAI)


def v2_abre(c, q, t, k):
    """2) CLOSE no rosto dele: o baú ABRE e a LUZ DOURADA ilumina a cara do fantasma (os olhos viram moedas $$)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 40)
    p = pose(c, "q_espera")
    craq(c, base, p, XC + 20)
    c.mapa_frente(base, t + 40)
    cb = c.ponto(p, "cb", 1.0, XC + 20, CHAO)
    centro, z = (cb[0] + 10, cb[1] + 10), 4.6
    c.camera(q, base, centro, z, pixel=True)
    luz = suave(min(1, max(0, t - 10) / 10))
    if luz > 0:  # a LUZ DOURADA vindo de baixo (do baú)
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(10):
            pygame.draw.rect(sup, (255, 210, 80, int(16 * luz * (i + 1))), (0, h - (i + 1) * h / 10, w, h / 10))
        q.blit(sup, (0, 0))
        brilho(q, (int(w * 0.5), h + 60), 400, (255, 220, 100), int(160 * luz))
    if t >= 22:  # os OLHOS viram MOEDAS
        ox, oy = para_tela(centro, z, (cb[0] + 4, cb[1] - 2))
        for dx in (-26, 26):
            moeda(q, ox + dx, oy, 22, t * 0.4)
    if t >= 26:
        texto_pow(q, "OUROOOO!!", (int(w * 0.5), int(h * 0.16)), 64, OURO, t - 26)


def v3_joga(c, q, t, k):
    """3) Ele MERGULHA as mãos nas moedas e JOGA pro alto... a chuva de ouro cai NA FRENTE da câmera."""
    import vitorias_loja
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 80)
    c.por_oponente(base, "caido", 1.0, XO + 30, CHAO)
    p = pose(c, "q_puxa" if (t // 10) % 2 else "q_joga")
    craq(c, base, p, XC)
    bau(c, base, vitorias_loja.TESOURO_JORRA + t)
    rnd = random.Random(t // 3)
    for i in range(10):  # o chafariz de moedas saindo do baú
        u = ((t * 0.04) + i / 10) % 1
        mx = XB + rnd.uniform(-1, 1) * 40 * u
        my = CHAO - 50 - math.sin(u * math.pi) * 140
        moeda(base, mx, my, 5, t * 0.4 + i)
    c.mapa_frente(base, t + 80)
    c.camera(q, base, ((XC + XB) / 2 + 10, CHAO - 110), 1.8, pixel=True)
    chuva_moedas(q, t, 10)
    if t % 20 < 10:
        texto_pow(q, "CLING CLING!", (int(w * 0.3), int(h * 0.22)), 46, OURO, t % 20, giro=-0.06)


def v4_rico(c, q, t, k):
    """4) Ele em cima da MONTANHA DE OURO, rindo de espada no alto (a moeda brilhando). O nome."""
    import vitorias_loja
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 120)
    c.por_oponente(base, "caido", 1.0, XO + 30, CHAO)
    bau(c, base, vitorias_loja.TESOURO_JORRA + 50)
    rnd = random.Random(5)
    for i in range(80):  # a MONTANHA de moedas
        x = XC + rnd.uniform(-90, 90)
        alto = max(0, 1 - abs(x - XC) / 95) * 50
        y = CHAO - rnd.uniform(0, alto)
        moeda(base, x, y, 5, i)
    craq(c, base, pose(c, "q_ri"), XC, CHAO - 40)
    c.mapa_frente(base, t + 120)
    c.camera(q, base, ((XC + XB) / 2, CHAO - 150), 1.6 - 0.15 * suave(min(1, t / 60)), pixel=True)
    for i in range(4):  # os brilhinhos
        fase = (t + i * 9) % 30
        if fase < 10:
            bx, by = w * (0.3 + i * 0.12), h * (0.4 + (i % 2) * 0.12)
            r = 20 * math.sin(fase / 10 * math.pi)
            pygame.draw.line(q, (255, 255, 230), (bx - r, by), (bx + r, by), 3)
            pygame.draw.line(q, (255, 255, 230), (bx, by - r), (bx, by + r), 3)
    if t < 60:
        texto_pow(q, "HAR HAR HAR!", (int(w * 0.72), int(h * 0.3)), 60, OURO, t % 10, giro=0.06)
    if t >= 30:
        faixa_nome(q, "CRÁQUEN", "O TESOURO É MEU!", COR_NOME, (t - 30) / 30)


PLANOS_TESOURO = [
    (40, v1_bau, {0: ("vento", 0.4), 16: ("queda", 0.9)}),
    (44, v2_abre, {10: ("confirma", 0.7), 22: ("blip", 0.5)}),
    (60, v3_joga, {0: ("blip", 0.3), 12: ("blip", 0.3), 24: ("blip", 0.3), 36: ("blip", 0.3), 48: ("blip", 0.3)}),
    (96, v4_rico, {0: ("uivo", 0.4)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_TESOURO, titulo, oponente)
