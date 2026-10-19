"""CENAS DE ANIME do TROMOS (loja), com as ideias do Gomes.

ENTRADA (OVO): close nele todo ENROLADO dentro do ovo... ele ACORDA, dá um RUGIDAÇO (a segunda boca pra fora),
RACHA o ovo e sai.
VITÓRIA (CASULO): PISA em cima do adversário e começa a CUSPIR a gosma, que vai cobrindo a TELA do adversário (a
câmera é a dele)... e no fim o adversário fica preso no CASULO.
O Tromos aparece com o desenho do jogo (de lado; de frente na câmera do derrotado, com o desenho de frente do
remodel); o ovo, a gosma e o casulo são ilustrados.
"""
import math
import random

import pygame

import cutscene
import xeno
from cena_max import fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

BORDA = (8, 8, 12)
XT, XO = LARGURA * 0.34, LARGURA * 0.7  # o Tromos (e o ovo) e o oponente, no mapa
GOSMA, GOSMA_ESC, GOSMA_CLARA = (110, 200, 50), (40, 90, 20), (200, 250, 140)
CASCA, CASCA_ESC, CASCA_CLARA = (96, 88, 70), (54, 48, 38), (150, 140, 112)
COR_NOME = (60, 140, 40)


def pal(c):
    return {k: c.cor(k, v) for k, v in xeno.PALETA.items()}


def pose(c, nome):
    return c.l.poses.get(nome) or c.l.poses["parado"]


def enrolado(c, respira=0.0):
    """ENROLADO dentro do ovo: o 'rastejando' encolhido (os joelhos no peito, a cabeça baixa)."""
    base = pose(c, "x_rasteja")
    f = 0.55 + 0.03 * respira
    p = {k: (v[0] * 0.55, v[1] * f) for k, v in base.items()}
    qd = p["qd"]
    p["cb"] = (qd[0] + 16, qd[1] - 2)  # (a cabeça encolhida, pra baixo)
    return p


def cauda_enrolada(l, p):
    """A CAUDA enrolada em volta do corpo (mesmo número de pontos da cauda do jogo)."""
    qx, qy = p["qd"]
    pts = []
    for i in range(13):
        a = math.pi * (0.7 + 1.5 * i / 12)
        r = 30 - i * 1.2
        pts.append((qx + math.cos(a) * r, max(1, qy * 0.6) + math.sin(a) * r * 0.7))
    return pts


def tromos(c, base, p, x, y=CHAO, d=1, enrolada=False, boca=False, cor=None):
    """Põe o Tromos (desenho do jogo). enrolada = a cauda enrolada; boca = a SEGUNDA BOCA pra fora;
    cor = pinta de uma cor só (o vulto dentro do ovo)."""
    l = c.lutador()
    orig = xeno.pontos_cauda
    estado, tl = l.estado, l.t
    if enrolada:
        xeno.pontos_cauda = cauda_enrolada
    if boca:  # (a segunda boca sai no 'vitoria' entre 30 e 60)
        l.estado, l.t = "vitoria", 45
    try:
        img, pe = c.corpo(p, 1.0, d, guardar=False)
    finally:
        xeno.pontos_cauda = orig
        l.estado, l.t = estado, tl
    if cor:
        img = img.copy()
        img.fill((*cor, 255), special_flags=pygame.BLEND_RGBA_MULT)
    base.blit(img, (int(x - pe[0]), int(y - pe[1])))


# =====================================================================
# O OVO
# =====================================================================
OVO_L, OVO_A = 120, 150


def ovo(c, base, x, t, rachado=0.0, pulsa=0.0, dentro=True, acorda=0.0, ruge=0.0):
    """O OVO (casca de couro com veias, a boca em cruz em cima, a névoa na base) com ELE enrolado lá dentro (vulto
    escuro que aparece com a luz de dentro). rachado: 0..1 (as rachaduras); acorda: os olhos amarelos acendendo."""
    w, h = OVO_L * (1 + 0.04 * pulsa), OVO_A * (1 + 0.03 * pulsa)
    caixa = pygame.Rect(0, 0, w, h)
    caixa.midbottom = (int(x), int(CHAO + 6))
    sup = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(sup, BORDA, caixa.inflate(6, 6))
    pygame.draw.ellipse(sup, CASCA, caixa)
    pygame.draw.ellipse(sup, CASCA_CLARA, (caixa.x + w * 0.18, caixa.y + h * 0.1, w * 0.3, h * 0.35))
    luz = 0.4 + 0.3 * pulsa  # a LUZ de dentro (mostra o vulto)
    janela = caixa.inflate(-w * 0.22, -h * 0.2)
    pygame.draw.ellipse(sup, (120, 120, 60, int(150 * luz)), janela)
    base.blit(sup, (0, 0))
    if dentro:
        vulto = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        if ruge:  # (RUGINDO lá dentro: se estica, a cabeça pra cima, a SEGUNDA BOCA pra fora)
            p_r = misturar(enrolado(c, 1), pose(c, "x_vitoria"), 0.35 + 0.15 * math.sin(t * 0.8))
            tromos(c, vulto, p_r, x - 4, CHAO - 6, enrolada=True, boca=True, cor=(70, 80, 50))
        else:
            tromos(c, vulto, enrolado(c, pulsa), x - 4, CHAO - h * 0.12, enrolada=True, cor=(30, 34, 20))
        mascara = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        pygame.draw.ellipse(mascara, (255, 255, 255, 220 if ruge else 170), janela)
        vulto.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        base.blit(vulto, (0, 0))
        if acorda > 0:  # os OLHOS amarelos acendendo lá dentro
            ox, oy = x + 18, CHAO - h * 0.32
            brilho(base, (int(ox), int(oy)), int(18 * acorda) + 2, pal(c)["y"], int(230 * acorda))
            pygame.draw.circle(base, pal(c)["Y"], (int(ox), int(oy)), max(1, int(3 * acorda)))
    rnd = random.Random(4)
    for i in range(7):  # as VEIAS
        a0 = rnd.uniform(0, math.tau)
        pts = []
        for j in range(5):
            a = a0 + j * 0.25
            pts.append((x + math.cos(a) * w * (0.2 + j * 0.06), caixa.centery + math.sin(a) * h * (0.2 + j * 0.06)))
        pygame.draw.lines(base, CASCA_ESC, False, pts, 2)
    topo = (x, caixa.y + 6)  # a "boca" em cruz no alto (de onde ele sai)
    for a in (0.7, 2.4):
        pygame.draw.line(base, BORDA, (topo[0] - math.cos(a) * 18, topo[1] + 4 - math.sin(a) * 6),
                         (topo[0] + math.cos(a) * 18, topo[1] + 4 + math.sin(a) * 6), 3)
    if rachado > 0:  # as RACHADURAS (com a gosma brilhando nas frestas)
        rnd = random.Random(9)
        for i in range(int(4 + 10 * rachado)):
            a = rnd.uniform(0, math.tau)
            comp = rnd.uniform(0.2, 0.5) * w * rachado
            sx, sy = x + math.cos(a) * w * 0.2, caixa.centery + math.sin(a) * h * 0.25
            pts = [(sx, sy)]
            for j in range(3):
                pts.append((pts[-1][0] + math.cos(a + rnd.uniform(-0.6, 0.6)) * comp / 3, pts[-1][1] + math.sin(a + rnd.uniform(-0.6, 0.6)) * comp / 3))
            pygame.draw.lines(base, GOSMA, False, pts, 4)
            pygame.draw.lines(base, BORDA, False, pts, 2)
    for i in range(5):  # a névoa na base
        v = (t * 0.8 + i * 13) % 50
        nev = pygame.Surface((80, 50), pygame.SRCALPHA)
        pygame.draw.ellipse(nev, (190, 200, 180, int(90 * (1 - v / 50))), (0, 10, 80, 30))
        base.blit(nev, (x - 40 + (i - 2) * 34 + v * (1 if i % 2 else -1) * 0.6, CHAO - 26 - v * 0.3))


# =====================================================================
# ENTRADA: OVO
# =====================================================================
def e1_ovo(c, q, t, k):
    """1) CLOSE no OVO pulsando devagar (tum... tum...), ele lá dentro, ENROLADO, só o vulto."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    pulsa = max(0, math.sin(t * 0.18)) ** 3
    ovo(c, base, XT, t, pulsa=pulsa)
    c.mapa_frente(base, t)
    c.camera(q, base, (XT, CHAO - 80), 2.4 + 0.4 * suave(k), pixel=True)
    if pulsa > 0.6:
        texto_pow(q, "tum...", (int(w * 0.72), int(h * 0.3)), 36, (200, 220, 160), int(t % 17))


def e2_acorda(c, q, t, k):
    """2) Bem de perto: os OLHOS amarelos ACENDEM lá dentro do ovo."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 60)
    ovo(c, base, XT, t, pulsa=0.5, acorda=suave(min(1, max(0, t - 8) / 10)))
    c.mapa_frente(base, t + 60)
    c.camera(q, base, (XT + 18, CHAO - 50), 4.4, pixel=True)
    if t >= 18 and t % 6 < 3:
        c.tremor = max(c.tremor, 2)


def e3_ruge(c, q, t, k):
    """3) O RUGIDAÇO: ele se estica lá dentro com a SEGUNDA BOCA pra fora, o ovo estufa e RACHA todo,
    linhas de impacto, a tela tremendo. O oponente tapa os ouvidos."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 90)
    c.por_oponente(base, "defesa" if t > 6 else "parado", 1.0, XO, CHAO)
    ovo(c, base, XT, t, rachado=min(1, t / 30), pulsa=0.6 + 0.4 * abs(math.sin(t * 0.5)), ruge=1.0)
    c.mapa_frente(base, t + 90)
    centro, z = (XT + 40, CHAO - 90), 2.4
    c.camera(q, base, centro, z, pixel=True)
    c.tremor = max(c.tremor, 7)
    ox, oy = para_tela(centro, z, (XT, CHAO - 90))
    cutscene.linhas_velocidade(q, (ox, oy), (255, 255, 255), n=26, r_dentro=230, grossura=4, semente=t // 2, alfa=70)
    texto_pow(q, "SKRAAAAAAAAAH!!", (int(w * 0.56), int(h * 0.2)), 68, (200, 250, 140), t % 8, giro=0.06)


def e4_racha(c, q, t, k):
    """4) O OVO ESTOURA: a casca voando em pedaços, a gosma espirrando... e ELE de pé, saindo."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 130)
    c.por_oponente(base, "defesa" if t < 18 else "parado", 1.0, XO, CHAO)
    rnd = random.Random(2)
    for i in range(16):  # os PEDAÇOS da casca
        vx, vy = rnd.uniform(-9, 9), rnd.uniform(-13, -4)
        px, py = XT + vx * t, CHAO - 80 + vy * t + 0.55 * t * t
        if py < CHAO - 4:
            a = t * 0.3 + i
            tam = 10 + i % 4 * 5
            pts = [(px + math.cos(a + j * 2.1) * tam, py + math.sin(a + j * 2.1) * tam * 0.7) for j in range(3)]
            pygame.draw.polygon(base, CASCA, pts)
            pygame.draw.polygon(base, BORDA, pts, 2)
        else:
            pygame.draw.ellipse(base, CASCA_ESC, (XT + vx * 20 - 10, CHAO - 6, 22, 9))
    for i in range(14):  # a GOSMA espirrando
        vx, vy = rnd.uniform(-7, 7), rnd.uniform(-11, -3)
        px, py = XT + vx * t, CHAO - 70 + vy * t + 0.5 * t * t
        if py < CHAO:
            pygame.draw.circle(base, GOSMA, (int(px), int(py)), 3 + i % 3)
    pygame.draw.ellipse(base, GOSMA_ESC, (XT - 60, CHAO - 4, 120, 12))  # a poça de gosma
    p = misturar(pose(c, "x_rasteja"), pose(c, "x_vitoria"), suave(min(1, t / 14)))
    tromos(c, base, p, XT)
    c.mapa_frente(base, t + 130)
    c.camera(q, base, (XT + 60, CHAO - 100), 1.9, pixel=True)
    if t == 0:
        c.inverte, c.tremor = 3, 24
    if t < 14:
        texto_pow(q, "KRAKK!!", (int(w * 0.3), int(h * 0.24)), 80, (230, 220, 190), t)


def e5_pose(c, q, t, k):
    """5) Ele se abaixa na pose de predador, a baba pingando... e o nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 160)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    pygame.draw.ellipse(base, GOSMA_ESC, (XT - 60, CHAO - 4, 120, 12))
    p = misturar(pose(c, "x_vitoria"), pose(c, "parado"), suave(min(1, t / 12)))
    tromos(c, base, p, XT + 20)
    cb = c.ponto(p, "cb", 1.0, XT + 20, CHAO)
    for i in range(2):  # a BABA pingando
        u = (t * 2 + i * 15) % 30
        pygame.draw.line(base, GOSMA_CLARA, (cb[0] + 18 + i * 4, cb[1] + 6), (cb[0] + 18 + i * 4, cb[1] + 6 + u * 0.6), 2)
    c.mapa_frente(base, t + 160)
    c.camera(q, base, (XT + 70, CHAO - 100), 2.0 - 0.2 * suave(min(1, t / 50)), pixel=True)
    if t >= 24:
        faixa_nome(q, "TROMOS", "O PREDADOR PERFEITO.", COR_NOME, (t - 24) / 30)


PLANOS = [
    (60, e1_ovo, {6: ("queda", 0.2), 40: ("queda", 0.2)}),
    (32, e2_acorda, {10: ("blip", 0.5)}),
    (44, e3_ruge, {0: ("uivo", 1.0), 2: ("terra", 0.6)}),
    (30, e4_racha, {0: ("quebra", 1.0), 1: ("explosao", 0.4)}),
    (70, e5_pose, {20: ("lingua", 0.3)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: CASULO
# =====================================================================
def pisa(c, t):
    """Em pé com o pé da frente EM CIMA do derrotado."""
    p = dict(pose(c, "x_vitoria" if t > 20 else "parado"))
    p["pf"] = (p["pf"][0] + 10, p["pf"][1] + 16)
    p["jf"] = (p["jf"][0] + 8, p["jf"][1] + 12)
    return p


def v1_pisa(c, q, t, k):
    """1) Ele vai até o derrotado... e PISA em cima dele (STOMP!)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    pisada = 22
    if t < pisada:
        fase = t * 0.25
        andar = ("andar1", "andar2", "andar3", "andar4")
        i = int(fase) % 4
        x = XT + (XO - 70 - XT) * suave(t / pisada)
        tromos(c, base, misturar(pose(c, andar[i]), pose(c, andar[(i + 1) % 4]), fase % 1), x)
    else:
        tromos(c, base, pisa(c, t), XO - 70)
    c.mapa_frente(base, t)
    c.camera(q, base, (XO - 40, CHAO - 100), 2.0, pixel=True)
    if t == pisada:
        c.tremor = 14
    if pisada <= t < pisada + 14:
        texto_pow(q, "STOMP!", (int(w * 0.6), int(h * 0.3)), 64, (220, 230, 200), t - pisada)


def splat(q, x, y, r, semente, t0, t):
    """Uma MANCHA de GOSMA grudada na tela (irregular, com brilho e escorrendo)."""
    rnd = random.Random(semente)
    pts = []
    for i in range(16):
        a = i * math.tau / 16
        k_ = r * rnd.uniform(0.7, 1.25)
        pts.append((x + math.cos(a) * k_, y + math.sin(a) * k_ * 0.85))
    pygame.draw.polygon(q, GOSMA_ESC, [(px + 4, py + 4) for px, py in pts])
    pygame.draw.polygon(q, GOSMA, pts)
    pygame.draw.ellipse(q, GOSMA_CLARA, (x - r * 0.5, y - r * 0.55, r * 0.35, r * 0.2))
    u = max(0, t - t0)
    for i in range(4):  # escorrendo
        gx = x + (i - 1.5) * r * 0.4
        comp = min(r * 1.6, u * rnd.uniform(1.2, 2.6))
        pygame.draw.line(q, GOSMA, (gx, y + r * 0.6), (gx, y + r * 0.6 + comp), max(3, int(r * 0.16)))
        pygame.draw.circle(q, GOSMA, (int(gx), int(y + r * 0.6 + comp)), max(2, int(r * 0.11)))


CUSPES = (20, 36, 52, 66, 78)  # (os quadros em que cada cuspe BATE na tela)


def v2_cospe(c, q, t, k):
    """2) A CÂMERA DO DERROTADO (deitado, olhando pra cima): ele por cima, de FRENTE, CUSPINDO a gosma...
    cada cuspe GRUDA na tela, até cobrir tudo."""
    w, h = q.get_size()
    fundo_desfocado(c, q, t, (XO, CHAO - 180), 1.4, 60)
    usou_frente = False
    try:
        import frente
        if frente.tem_frente(c.ficha):
            prog = ((t + 8) % 16) / 16
            frente.desenhar_frente(q, c.ficha, w * 0.5, h + 160, 3.8, "ataque", t, prog=prog)
            usou_frente = True
    except ImportError:
        pass
    if not usou_frente:
        img, pe = c.corpo("x_cospe", 3.0, -1, guardar=False)
        q.blit(img, (int(w * 0.5 - pe[0]), int(h + 140 - pe[1])))
    for i, tb in enumerate(CUSPES):  # cada CUSPE: voando... e GRUDA
        rnd = random.Random(i + 7)
        alvo = (w * rnd.uniform(0.2, 0.8), h * rnd.uniform(0.25, 0.75))
        if tb - 8 <= t < tb:  # (voando: vem crescendo)
            u = (t - tb + 8) / 8
            sx, sy = w * 0.5 + (alvo[0] - w * 0.5) * u, h * 0.32 + (alvo[1] - h * 0.32) * u
            pygame.draw.circle(q, GOSMA, (int(sx), int(sy)), int(8 + 50 * u))
        elif t >= tb:
            splat(q, alvo[0], alvo[1], 110 + i * 30, i, tb, t)
            if t == tb:
                c.tremor = 8
    if t >= CUSPES[-1]:  # (cobriu tudo: a tela fica toda GOSMA)
        u = min(1, (t - CUSPES[-1]) / 12)
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        sup.fill((*GOSMA_ESC, int(255 * u)))
        q.blit(sup, (0, 0))
    if any(0 <= t - tb < 6 for tb in CUSPES):
        texto_pow(q, "SPLURT!", (int(w * 0.5), int(h * 0.16)), 56, GOSMA_CLARA, min(t - tb for tb in CUSPES if t >= tb))


def casulo(base, x, t, k=1.0):
    """O CASULO de gosma em cima do derrotado (fios esticados, bolhas, só os pés de fora mexendo)."""
    w_, h_ = 150 * k, 56 * k
    r = pygame.Rect(0, 0, w_, h_)
    r.midbottom = (int(x), CHAO + 4)
    pygame.draw.ellipse(base, BORDA, r.inflate(6, 6))
    pygame.draw.ellipse(base, GOSMA_ESC, r)
    pygame.draw.ellipse(base, (70, 130, 34), r.inflate(-20, -16))
    pygame.draw.ellipse(base, GOSMA_CLARA, (r.x + r.w * 0.2, r.y + 6, r.w * 0.3, 8))
    for i in range(6):  # os FIOS grudando no chão
        fx = r.x + r.w * (0.1 + i * 0.16)
        pygame.draw.line(base, GOSMA, (fx, r.centery), (fx + (i - 2.5) * 10, CHAO + 2), 2)
    for i in range(4):  # as bolhas
        v = (t * 2 + i * 9) % 20
        pygame.draw.circle(base, GOSMA_CLARA, (int(r.x + r.w * (0.25 + i * 0.17)), int(r.y + 10 - v * 0.3)), max(1, 4 - v // 6), 1)
    if k >= 1:  # os pés de fora, mexendo
        for i in range(2):
            pe = (r.right - 4, r.centery + i * 8 + math.sin(t * 0.5 + i) * 3)
            pygame.draw.ellipse(base, (90, 60, 40), (pe[0], pe[1] - 5, 16, 10))


def v3_casulo(c, q, t, k):
    """3) De fora: o derrotado preso no CASULO de gosma... e ele em cima, RUGINDO com a segunda boca. O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 80)
    casulo(base, XO, t)
    p = pisa(c, 30)
    ruge = 10 <= t < 50
    tromos(c, base, p, XO - 70, boca=ruge)
    c.mapa_frente(base, t + 80)
    c.camera(q, base, (XO - 50, CHAO - 100), 2.0 - 0.2 * suave(min(1, t / 60)), pixel=True)
    if t < 8:  # (saindo da gosma da tela)
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        sup.fill((*GOSMA_ESC, 255 - t * 32))
        q.blit(sup, (0, 0))
    if ruge:
        c.tremor = max(c.tremor, 4)
        texto_pow(q, "SKREEEEE!!", (int(w * 0.3), int(h * 0.22)), 60, GOSMA_CLARA, t % 8, giro=-0.06)
    if t >= 40:
        faixa_nome(q, "TROMOS", "CAPTURADO.", COR_NOME, (t - 40) / 30)


PLANOS_CASULO = [
    (44, v1_pisa, {0: ("queda", 0.2), 22: ("queda", 1.0)}),
    (96, v2_cospe, {tb: ("puf", 0.7) for tb in CUSPES}),
    (100, v3_casulo, {10: ("uivo", 0.9)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_CASULO, titulo, oponente)
