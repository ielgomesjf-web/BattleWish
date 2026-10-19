"""CENAS DE ANIME do SPHYRUS (loja): a entrada TANQUE QUEBRADO e a vitória BARBATANA EM CÍRCULO.

Tudo no MAPA da luta, com a SKIN dele e o OPONENTE de verdade. O Sphyrus aparece com o desenho do jogo (montado na
escala do jogo e a câmera amplia; a boca e a linha acesa são as do próprio desenho). Os closes de detalhe (o olho na
ponta do martelo, o vidro rachando, a barbatana vindo na câmera) são ilustrados nas cores da skin.
"""
import math
import random

import pygame

import cutscene
import sphyrus
from cena_max import cores_do_mapa, chao_perto, fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

BORDA = (10, 10, 16)
XS, XO = LARGURA * 0.32, LARGURA * 0.72  # o Sphyrus e o oponente, no mapa
AGUA, AGUA_ESC = (60, 140, 190), (20, 56, 96)
METAL, METAL_ESC = (120, 128, 140), (70, 76, 88)
TERRA, TERRA_ESC = (140, 112, 82), (60, 44, 30)
COR_NOME = (60, 150, 200)


def pal(c):
    return {k: c.cor(k, v) for k, v in sphyrus.PALETA.items()}


def pose(c, nome):
    return c.l.poses.get(nome) or c.l.poses["parado"]


def sph(c, base, p, x, y=CHAO, boca=None, aceso=False, d=1):
    """Põe o Sphyrus (desenho do jogo) no mapa, com a boca e a linha do jeito pedido."""
    l = c.lutador()
    l.extra.pop("boca", None)
    l.extra.pop("sente", None)
    if boca is not None:
        l.extra["boca"] = boca
    if aceso:
        l.extra["sente"] = 10
    c.por(base, p, 1.0, x, y, d, guardar=False)


def barbatana(c, q, x, y, esc, d, t):
    """Só a BARBATANA (com o código de barras) cortando o chão: o desenho do próprio jogo."""
    import pecas
    l = c.lutador()
    guarda = l.x, l.y, l.dir, l.s, l.t
    try:
        l.x, l.y, l.dir, l.s, l.t = x, y, d, c.l.s * esc, t
        pecas.usar_troca(c.ficha.get("troca"))
        sphyrus.desenhar_barbatana(l, q)
    finally:
        pecas.usar_troca(None)
        l.x, l.y, l.dir, l.s, l.t = guarda


def noite(q, f=0.55, cor=(30, 50, 110)):
    """Escurece a tela (luz apagada do laboratório / a noite), puxando pro azul."""
    sup = pygame.Surface(q.get_size())
    sup.fill(tuple(int(255 * (1 - f) + v * f) for v in cor))
    q.blit(sup, (0, 0), special_flags=pygame.BLEND_RGB_MULT)


def sirene(q, x, y, t, alcance=900):
    """A luz VERMELHA da sirene girando (o feixe varrendo o cenário)."""
    a = t * 0.18
    sup = pygame.Surface(q.get_size(), pygame.SRCALPHA)
    for lado in (0, math.pi):
        aa = a + lado
        pts = [(x, y), (x + math.cos(aa - 0.22) * alcance, y + math.sin(aa - 0.22) * alcance * 0.5),
               (x + math.cos(aa + 0.22) * alcance, y + math.sin(aa + 0.22) * alcance * 0.5)]
        pygame.draw.polygon(sup, (255, 40, 30, 60), pts)
    q.blit(sup, (0, 0))
    brilho(q, (int(x), int(y)), 30, (255, 60, 40), 220)


# =====================================================================
# O TANQUE de laboratório (escala do jogo: e = 1)
# =====================================================================
def tanque(c, q, x, base, e, t, rachado=0, vulto=True):
    """O tanque de vidro com água, ELE lá dentro (só o vulto escuro, boiando), bolhas, as tampas de metal,
    a etiqueta com o código de barras e a sirene em cima."""
    w, h = 110 * e, 190 * e
    topo = base - h
    agua = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
    agua.fill((*AGUA_ESC, 220))
    pygame.draw.rect(agua, (*AGUA, 120), (0, 0, w, h * 0.12))
    if vulto:  # o VULTO dele boiando (o desenho do jogo, escurecido)
        img, pe = c.corpo("s_mergulho", 0.62 * e)
        img = img.copy()
        img.fill((20, 40, 70, 255), special_flags=pygame.BLEND_RGBA_MULT)
        agua.blit(img, (int(w / 2 - pe[0] + 6 * e), int(h * 0.78 - pe[1] + math.sin(t * 0.08) * 5 * e)))
    for i in range(10):  # as bolhas
        bx = (i * 29 + 7) % int(max(1, w - 10)) + 5
        by = h - ((t * 2.4 + i * 37) % int(h * 0.88))
        pygame.draw.circle(agua, (200, 240, 255, 200), (int(bx), int(by)), int((2 + i % 3) * e), max(1, int(e)))
    q.blit(agua, (x - w / 2, topo))
    pygame.draw.line(q, (220, 245, 255), (x - w / 2 + 10 * e, topo + 14 * e), (x - w / 2 + 10 * e, base - 14 * e),
                     max(2, int(4 * e)))  # o reflexo do vidro
    pygame.draw.rect(q, (170, 220, 240), (x - w / 2, topo, w, h), max(2, int(3 * e)))
    for yy, hh in ((topo - 12 * e, 14 * e), (base - 12 * e, 14 * e)):  # as tampas de metal com rebites
        pygame.draw.rect(q, BORDA, (x - w / 2 - 8 * e, yy - 1, w + 16 * e, hh + 2))
        pygame.draw.rect(q, METAL, (x - w / 2 - 7 * e, yy, w + 14 * e, hh))
        pygame.draw.rect(q, METAL_ESC, (x - w / 2 - 7 * e, yy + hh * 0.6, w + 14 * e, hh * 0.4))
        for i in range(5):
            pygame.draw.circle(q, (200, 204, 214), (int(x - w / 2 + (i + 0.5) * w / 5), int(yy + hh * 0.35)), max(1, int(1.6 * e)))
    et = pygame.Rect(0, 0, 34 * e, 20 * e)  # a etiqueta: "SPH-01" e o código de barras
    et.center = (int(x + w * 0.22), int(base - 40 * e))
    pygame.draw.rect(q, (236, 232, 210), et)
    pygame.draw.rect(q, BORDA, et, 1)
    for i in range(9):
        pygame.draw.line(q, BORDA, (et.x + 3 * e + i * 3.2 * e, et.y + 3 * e), (et.x + 3 * e + i * 3.2 * e, et.y + 13 * e),
                         max(1, int((1 + i % 2) * e * 0.7)))
    pygame.draw.rect(q, BORDA, (x - 6 * e, topo - 26 * e, 12 * e, 14 * e))  # a SIRENE
    pygame.draw.rect(q, (220, 40, 30) if (t // 8) % 2 else (140, 20, 20), (x - 5 * e, topo - 25 * e, 10 * e, 12 * e))
    rnd = random.Random(9)
    for k in range(rachado):  # as rachaduras
        cx, cy = x + rnd.uniform(-w / 3, w / 3), topo + rnd.uniform(h * 0.3, h * 0.75)
        for _ in range(6):
            a = rnd.uniform(0, math.tau)
            comp = rnd.uniform(18, 40) * e
            mx, my = cx + math.cos(a) * comp * 0.5 + rnd.uniform(-4, 4), cy + math.sin(a) * comp * 0.5
            pygame.draw.lines(q, (240, 252, 255), False, [(cx, cy), (mx, my), (cx + math.cos(a) * comp, cy + math.sin(a) * comp)],
                              max(1, int(1.5 * e)))
    return topo


# =====================================================================
# ENTRADA: TANQUE QUEBRADO
# =====================================================================
def base_noite(c, t, opo="parado"):
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, opo, 1.0, XO, CHAO)
    noite(base, 0.6)
    return base


def e1_tanque(c, q, t, k):
    """1) No MAPA, no escuro: um TANQUE de laboratório, a sirene vermelha girando, ELE boiando lá dentro.
    O oponente olha. A câmera vai chegando."""
    w, h = q.get_size()
    base = base_noite(c, t)
    topo = tanque(c, base, XS, CHAO, 1.0, t)
    sirene(base, XS, topo - 20, t)
    c.mapa_frente(base, t)
    z = 1.5 + 0.5 * suave(k)
    c.camera(q, base, (XS + 150 * (1 - suave(k)), CHAO - 110), z, pixel=True)
    if t > 14:
        texto_pow(q, "BIIIP... BIIIP...", (int(w * 0.72), int(h * 0.2)), 26, (255, 120, 110), (t - 14) % 20, giro=0.04)


def olho_close(c, q, w, h, abre, linha, t):
    """CLOSE (dentro da água) na ponta do MARTELO: o olho amarelo abre (pupila fininha)... e a LINHA
    bioluminescente acende correndo pelo corpo."""
    p = pal(c)
    cutscene.degrade(q, (0, 0, w, h), AGUA_ESC, (8, 22, 44))
    for i in range(16):  # bolhas
        bx = (i * 131) % w
        by = h - ((t * 5 + i * 67) % (h + 40))
        pygame.draw.circle(q, (150, 210, 240), (int(bx), int(by)), 4 + i % 4 * 3, 2)
    cx, cy = w * 0.58, h * 0.5
    martelo = [(-460, -60), (90, -110), (210, -74), (250, -10), (210, 50), (90, 80), (-460, 40)]  # (a ponta do martelo)
    pts = [(cx + x, cy + y) for x, y in martelo]
    pygame.draw.polygon(q, BORDA, [(x + 6, y + 6) for x, y in pts])
    pygame.draw.polygon(q, p["m"], pts)
    pygame.draw.polygon(q, p["M"], [(cx - 460, cy + 10), (cx + 100, cy + 30), (cx + 210, cy + 50), (cx + 90, cy + 80),
                                    (cx - 460, cy + 40)])
    pygame.draw.polygon(q, BORDA, pts, 6)
    for i in range(4):  # (os pontos sensoriais na pele)
        pygame.draw.circle(q, p["M"], (int(cx - 300 + i * 70), int(cy - 50 + i * 4)), 5)
    for i in range(6):  # a CICATRIZ de pontos
        sx = cx - 380 + i * 22
        pygame.draw.line(q, BORDA, (sx, cy - 30), (sx + 10, cy - 6), 4)
    pygame.draw.line(q, BORDA, (cx - 384, cy - 18), (cx - 250, cy - 18), 3)
    ox, oy = cx + 150, cy - 10
    pygame.draw.circle(q, BORDA, (int(ox), int(oy)), 58)
    aberto = suave(abre)
    if aberto > 0.05:
        if aberto > 0.7:
            brilho(q, (int(ox), int(oy)), 120, p["o"], 120)
        pygame.draw.circle(q, p["o"], (int(ox), int(oy)), 50)
        pygame.draw.circle(q, tuple(min(255, v + 50) for v in p["o"]), (int(ox - 12), int(oy - 14)), 22)
        pygame.draw.ellipse(q, BORDA, (ox - 6 - 4 * aberto, oy - 40, 12 + 8 * aberto * (1 - aberto), 80))  # a pupila fininha
        pygame.draw.circle(q, (255, 255, 255), (int(ox - 20), int(oy - 22)), 8)
    pal_alto = int(50 * (1 - aberto))  # as pálpebras (fechando por cima e por baixo)
    if pal_alto > 0:
        pygame.draw.rect(q, p["M"], (ox - 60, oy - 60, 120, pal_alto + 10))
        pygame.draw.rect(q, p["M"], (ox - 60, oy + 50 - pal_alto, 120, pal_alto + 10))
        pygame.draw.line(q, BORDA, (ox - 50, oy - 50 + pal_alto + 8), (ox + 50, oy - 50 + pal_alto + 8), 5)
    if linha > 0:  # a LINHA AZUL acendendo, correndo do olho pra trás
        fim = cx + 100 - 600 * linha
        brilho(q, (int(fim), int(cy + 20)), 70, p["l"], 160)
        pygame.draw.line(q, p["l"], (cx + 100, cy + 20), (fim, cy + 20 + (cx + 100 - fim) * 0.02), 12)
        pygame.draw.line(q, (230, 250, 255), (cx + 100, cy + 20), (fim, cy + 20 + (cx + 100 - fim) * 0.02), 4)


def e2_olho(c, q, t, k):
    """2) Close na água: o olho na ponta do martelo ABRE... e a linha bioluminescente ACENDE."""
    w, h = q.get_size()
    olho_close(c, q, w, h, min(1, max(0, t - 8) / 8), min(1, max(0, t - 20) / 10), t)
    if t == 16:
        c.tremor = 4


def cabeca_frente(q, cx, cy, e, p):
    """A CABEÇA dele DE FRENTE (o martelo com os olhos amarelos nas pontas, a mandíbula, a coleira quebrada),
    ilustrada nas cores da skin."""
    def P(x, y):
        return cx + x * e, cy + y * e
    martelo = [P(-230, -22), P(-60, -34), P(60, -34), P(230, -22), P(238, 4), P(210, 18), P(50, 20), P(-50, 20),
               P(-210, 18), P(-238, 4)]
    queixo = [P(-48, 14), P(48, 14), P(36, 92), P(0, 112), P(-36, 92)]
    pescoco = [P(-34, 96), P(34, 96), P(46, 170), P(-46, 170)]
    for pts, cor in ((pescoco, p["M"]), (queixo, p["m"]), (martelo, p["m"])):
        pygame.draw.polygon(q, BORDA, [(x + 5, y + 5) for x, y in pts])
        pygame.draw.polygon(q, cor, pts)
        pygame.draw.polygon(q, BORDA, pts, max(3, int(2 * e)))
    pygame.draw.polygon(q, p["M"], [P(-236, 4), P(236, 4), P(210, 18), P(-210, 18)])  # (a sombra de baixo do martelo)
    pygame.draw.polygon(q, p["a"], [P(-30, 40), P(30, 40), P(22, 90), P(0, 104), P(-22, 90)])  # (a barriga do queixo)
    pygame.draw.line(q, BORDA, P(-44, 16), P(44, 16), max(3, int(3 * e)))  # a boca fechada, com os dentes pra fora
    for i in range(9):
        x = -40 + i * 10
        pygame.draw.polygon(q, (250, 250, 236), [P(x, 16), P(x + 5, 16), P(x + 2.5, 24)])
    for i in range(5):  # a CICATRIZ de pontos na testa
        sx = -60 + i * 14
        pygame.draw.line(q, BORDA, P(sx, -30), P(sx + 6, -14), max(2, int(2 * e)))
    pygame.draw.line(q, BORDA, P(-64, -22), P(8, -22), max(2, int(1.4 * e)))
    pygame.draw.rect(q, BORDA, (*P(-50, 128), 100 * e, 20 * e))  # a COLEIRA de metal quebrada
    pygame.draw.rect(q, METAL, (*P(-48, 130), 96 * e, 16 * e))
    pygame.draw.polygon(q, BORDA, [P(10, 128), P(18, 148), P(24, 128)])
    pygame.draw.line(q, p["l"], P(-20, 150), P(-26, 170), max(3, int(4 * e)))  # a linha acesa descendo
    for lado in (-1, 1):  # os OLHOS amarelos nas pontas do martelo
        o = P(lado * 214, -6)
        brilho(q, (int(o[0]), int(o[1])), int(36 * e), p["o"], 200)
        pygame.draw.circle(q, BORDA, (int(o[0]), int(o[1])), int(13 * e))
        pygame.draw.circle(q, p["o"], (int(o[0]), int(o[1])), int(11 * e))
        pygame.draw.ellipse(q, BORDA, (o[0] - 2 * e, o[1] - 9 * e, 4 * e, 18 * e))


def e3_vidro(c, q, t, k):
    """3) TELA PRETA (tipo o Gohan virando super saiyajin 2): só a CABEÇA dele, faíscas estalando em volta...
    CABEÇADA no vidro (TUM!), outra (TUM!!), e um RAIO corta a tela a cada batida... CRAAACK!"""
    w, h = q.get_size()
    p = pal(c)
    q.fill((0, 0, 0))
    batidas = (8, 20, 32)
    n = sum(1 for b in batidas if t >= b)
    u = t - batidas[n - 1] if n else 99
    # (ele chega pra trás e vem com tudo: antes de cada batida recua, na batida encosta no vidro)
    prox = [b for b in batidas if b >= t]
    recua = 0.0
    if prox:
        falta = prox[0] - t
        recua = min(1, falta / 6) if falta < 6 else 1.0
    e = 1.55 + 0.35 * (1 - recua) - (0.05 if u < 3 else 0)
    cx, cy = w * 0.5, h * 0.42 + recua * 10
    brilho(q, (int(cx), int(cy + 30)), 380, p["l"], 30 + int(20 * math.sin(t * 0.7)))  # a aura fraquinha
    cabeca_frente(q, cx, cy, e, p)
    faiscas_eletricas(q, cx, cy + 20, 250, t, p["l"], n=4 + n)
    pygame.draw.line(q, (60, 90, 110), (w * 0.08, 0), (w * 0.02, h), 10)  # (o reflexo do vidro, no escuro)
    rnd = random.Random(5)
    for j in range(n):  # as RACHADURAS no vidro (na frente dele; cada batida, mais)
        ix, iy = w * (0.5 + (j - 1) * 0.08), h * (0.46 + (j % 2) * 0.06)
        for _ in range(8 + j * 6):
            a = rnd.uniform(0, math.tau)
            comp = rnd.uniform(80, 220 + j * 160)
            pts = [(ix, iy)]
            for s_ in range(1, 4):
                pts.append((ix + math.cos(a) * comp * s_ / 3 + rnd.uniform(-14, 14),
                            iy + math.sin(a) * comp * s_ / 3 + rnd.uniform(-14, 14)))
            pygame.draw.lines(q, (235, 248, 255), False, pts, 2 if j < 2 else 3)
        pygame.draw.circle(q, (235, 248, 255), (int(ix), int(iy)), 10 + j * 6, 3)
    for i, b in enumerate(batidas):
        v = t - b
        if v == 0:
            c.tremor = 10 if i < 2 else 24
            if i == 2:
                c.inverte = 3
        if 0 <= v < 5:  # o RAIO GRANDE atravessando a tela, e o clarão
            flash = pygame.Surface((w, h))
            flash.fill(p["l"])
            flash.set_alpha(140 - v * 28)
            q.blit(flash, (0, 0))
            lado = 1 if i % 2 == 0 else -1
            raio(q, (w * 0.5 - lado * w * 0.45, -20), (w * 0.5 + lado * w * 0.3, h + 20), b + i, 7 + i * 2, p["l"], 3 + i)
    if n:
        txt = ("TUM!", "TUM!!", "CRAAACK!!")[n - 1]
        pos = ((0.24, 0.24), (0.76, 0.28), (0.5, 0.18))[n - 1]
        texto_pow(q, txt, (int(w * pos[0]), int(h * pos[1])), 52 if n < 3 else 84, (230, 246, 255), u,
                  giro=(0.1, -0.1, 0.06)[n - 1])


def e4_explode(c, q, t, k):
    """4) No MAPA: o tanque EXPLODE (vidro e água pra todo lado), ele cai agachado na água, e a onda corre pelo chão.
    O oponente se protege."""
    w, h = q.get_size()
    base = base_noite(c, t + 40, "defesa" if 2 < t < 30 else "parado")
    u = t
    if u == 0:
        c.inverte, c.tremor = 3, 24
    poca = min(1, u / 14)  # a ÁGUA espalhando no chão
    pygame.draw.ellipse(base, AGUA_ESC, (XS - 40 - 260 * poca, CHAO - 6, 80 + 520 * poca, 18))
    pygame.draw.ellipse(base, AGUA, (XS - 30 - 250 * poca, CHAO - 4, 60 + 500 * poca, 12))
    for lado in (-1, 1):  # a ONDA correndo
        ox = XS + lado * (40 + 300 * poca)
        pygame.draw.ellipse(base, (200, 236, 255), (ox - 30, CHAO - 14 + 8 * poca, 60, 20 - 8 * poca))
    for yy, hh in ((CHAO - 12, 14),):  # o que sobrou do tanque: a base de metal
        pygame.draw.rect(base, BORDA, (XS - 63, yy - 1, 126, hh + 2))
        pygame.draw.rect(base, METAL, (XS - 62, yy, 124, hh))
    queda = min(1, u / 8)
    p = misturar(pose(c, "s_salto"), pose(c, "s_mergulho"), suave(queda))
    sph(c, base, p, XS, CHAO - 80 * (1 - queda), aceso=True)
    rnd = random.Random(2)
    for i in range(30):  # os CACOS de vidro
        vx, vy = rnd.uniform(-10, 10), rnd.uniform(-12, -2)
        px, py = XS + vx * u, CHAO - 100 + vy * u + 0.45 * u * u
        if py < CHAO:
            tam = 3 + i % 4 * 2
            pygame.draw.polygon(base, (210, 240, 255), [(px, py - tam), (px + tam * 0.6, py), (px - tam * 0.3, py + tam * 0.8)])
    for i in range(16):  # as gotas
        vx, vy = rnd.uniform(-7, 7), rnd.uniform(-14, -6)
        px, py = XS + vx * u, CHAO - 80 + vy * u + 0.5 * u * u
        if py < CHAO:
            pygame.draw.circle(base, (150, 210, 245), (int(px), int(py)), 3)
    poeira(base, XS, CHAO, min(1, u / 24), cor=(190, 230, 250), larg=180, semente=8)
    c.mapa_frente(base, t + 40)
    c.camera(q, base, (XS + 110, CHAO - 100), 1.7, pixel=True)
    if u < 16:
        texto_pow(q, "SPLASH!!", (int(w * 0.38), int(h * 0.24)), 72, (190, 236, 255), u, giro=0.1)


def e5_pisa(c, q, t, k):
    """5) Câmera BAIXA nos pés de raptor: ele se levanta e dá um passo pesado na água (SPLASH), os cacos no chão."""
    base = base_noite(c, t + 80)
    pygame.draw.ellipse(base, AGUA_ESC, (XS - 300, CHAO - 6, 600, 18))
    pygame.draw.ellipse(base, AGUA, (XS - 290, CHAO - 4, 580, 12))
    rnd = random.Random(4)
    for i in range(16):  # cacos no chão (brilhando)
        px = XS + rnd.uniform(-200, 240)
        pygame.draw.polygon(base, (220, 244, 255), [(px, CHAO - 3), (px + 5, CHAO), (px - 2, CHAO + 2)])
    sobe = suave(min(1, t / 14))
    p = misturar(pose(c, "s_mergulho"), pose(c, "parado"), sobe)
    x = XS + 30 * suave(min(1, max(0, t - 14) / 10))
    sph(c, base, p, x, aceso=True)
    if t >= 22:  # o SPLASH do passo
        u = t - 22
        for i in range(10):
            a = math.pi + i * math.pi / 9
            r = 8 + u * 3
            pygame.draw.circle(base, (200, 236, 255), (int(x + 20 + math.cos(a) * r), int(CHAO + math.sin(a) * r * 0.6)),
                               max(1, 3 - u // 6))
        if t == 22:
            c.tremor = 6
    c.mapa_frente(base, t + 80)
    c.camera(q, base, (XS + 30, CHAO - 40), 3.0, pixel=True)


def raio(q, p0, p1, semente, grosso=6, cor=(150, 220, 255), galhos=3):
    """Um RAIO em zigue-zague de p0 até p1 (o brilho largo, o miolo branco e uns galhinhos)."""
    rnd = random.Random(semente)
    pts = [p0, p1]
    desvio = math.dist(p0, p1) * 0.22
    for _ in range(5):  # (divide no meio e empurra pro lado, várias vezes)
        novos = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            dx, dy = b[0] - a[0], b[1] - a[1]
            n = math.hypot(dx, dy) or 1
            d = rnd.uniform(-desvio, desvio)
            novos += [(mx - dy / n * d, my + dx / n * d), b]
        pts = novos
        desvio *= 0.5
    sup = pygame.Surface(q.get_size(), pygame.SRCALPHA)
    pygame.draw.lines(sup, (*cor, 70), False, pts, grosso * 4)
    pygame.draw.lines(sup, (*cor, 160), False, pts, grosso * 2)
    q.blit(sup, (0, 0))
    pygame.draw.lines(q, (255, 255, 255), False, pts, max(1, grosso // 2 + 1))
    for _ in range(galhos):
        i = rnd.randrange(4, len(pts) - 4)
        a = pts[i]
        b = (a[0] + rnd.uniform(-1, 1) * desvio * 60, a[1] + rnd.uniform(0.2, 1) * desvio * 60)
        raio(q, a, b, rnd.random(), max(1, grosso // 2), cor, 0)


def faiscas_eletricas(q, cx, cy, raio_, t, cor=(150, 220, 255), n=5):
    """As FAÍSCAS estalando em volta (igual quando vira super saiyajin 2): trocam de lugar a cada 2 quadros."""
    rnd = random.Random(t // 2)
    for _ in range(n):
        a = rnd.uniform(0, math.tau)
        r1 = raio_ * rnd.uniform(0.6, 1.1)
        p0 = (cx + math.cos(a) * r1, cy + math.sin(a) * r1 * 0.8)
        a2 = a + rnd.uniform(-0.8, 0.8)
        r2 = r1 + rnd.uniform(40, 110)
        raio(q, p0, (cx + math.cos(a2) * r2, cy + math.sin(a2) * r2 * 0.8), rnd.random(), 2, cor, 1)


def e6_boca(c, q, t, k):
    """6) A MANDÍBULA: abre devagar... ENORME (a baba escorrendo)."""
    w, h = q.get_size()
    base = base_noite(c, t + 120)
    p = pose(c, "s_ruge")
    sph(c, base, p, XS + 30, boca=1.25 * suave(min(1, t / 22)), aceso=True)
    cb = c.ponto(p, "cb", 1.0, XS + 30, CHAO)
    c.mapa_frente(base, t + 120)
    centro, z = (cb[0] + 30, cb[1] + 10), 3.4 + 0.4 * suave(k)
    c.camera(q, base, centro, z, pixel=True)
    if t > 10:  # a baba
        bx, by = para_tela(centro, z, (cb[0] + 34, cb[1] + 8))
        for i in range(3):
            pygame.draw.line(q, (210, 236, 246), (bx - i * 40, by), (bx - i * 40, by + (t - 10) * 4 + i * 10), 5)


def e7_ruge(c, q, t, k):
    """7) O RUGIDÃO: linhas de impacto, a linha acesa, a água tremendo... e o nome."""
    w, h = q.get_size()
    base = base_noite(c, t + 160, "defesa" if t < 30 else "parado")
    pygame.draw.ellipse(base, AGUA_ESC, (XS - 300, CHAO - 6, 600, 18))
    pygame.draw.ellipse(base, AGUA, (XS - 290, CHAO - 4, 580, 12))
    p = pose(c, "s_ruge")
    x = XS + 30
    sph(c, base, p, x, boca=1.25 if t < 46 else 0.0, aceso=True)
    for i in range(3):  # as ONDINHAS de tremor na água
        r = ((t * 4 + i * 30) % 90)
        pygame.draw.ellipse(base, (200, 236, 255), (x - r * 2, CHAO - 3, r * 4, 6), 2)
    cb = c.ponto(p, "cb", 1.0, x, CHAO)
    c.mapa_frente(base, t + 160)
    centro, z = (x + 60, CHAO - 110), 2.1 - 0.2 * suave(k)
    c.camera(q, base, centro, z, pixel=True)
    if t < 40:
        if t % 4 == 0:
            c.tremor = max(c.tremor, 8)
        cutscene.linhas_velocidade(q, para_tela(centro, z, cb), (255, 255, 255), n=28, r_dentro=240, grossura=4,
                                   semente=t // 2, alfa=90)
        texto_pow(q, "GROOOOAR!!", (int(w * 0.68), int(h * 0.24)), 66, pal(c)["l"], t % 8, giro=0.1)
    if t >= 30:
        faixa_nome(q, "SPHYRUS", "EXPERIMENTO FUGITIVO.", COR_NOME, (t - 30) / 30)


PLANOS = [
    (44, e1_tanque, {0: ("blip", 0.4), 20: ("blip", 0.4)}),
    (36, e2_olho, {8: ("carga", 0.5), 20: ("ultimate", 0.4)}),
    (48, e3_vidro, {0: ("ultimate", 0.4), 8: ("defesa", 0.8), 20: ("defesa", 1.0), 32: ("quebra", 1.0)}),
    (34, e4_explode, {0: ("explosao", 0.6), 2: ("puf", 0.8)}),
    (34, e5_pisa, {22: ("queda", 0.6)}),
    (34, e6_boca, {4: ("lingua", 0.4)}),
    (70, e7_ruge, {0: ("uivo", 1.0), 2: ("terra", 0.6)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: BARBATANA EM CÍRCULO
# =====================================================================
def circ(t, raio=110):
    """A barbatana rodando em volta do derrotado."""
    a = t * 0.075 + math.pi
    return XO + math.cos(a) * raio, a


def rasgo(base, x, cor=TERRA):
    pygame.draw.ellipse(base, TERRA_ESC, (x - 30, CHAO - 5, 60, 10))


def v1_mergulha(c, q, t, k):
    """1) No MAPA, do lado do derrotado: pula de cabeça e MERGULHA na terra (o chão espirra)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    x0 = XO - 170
    afunda = 20
    if t < 14:
        sph(c, base, misturar(pose(c, "parado"), pose(c, "s_salto"), suave(t / 14)), x0)
    elif t < afunda + 6:
        u = (t - 14) / (afunda + 6 - 14)
        img, pe = c.corpo("s_mergulho", 1.0)
        img = img.subsurface(img.get_bounding_rect())  # (só o corpo: gira em volta do meio dele)
        img = pygame.transform.rotate(img, -75 * u)
        y = CHAO - 70 - 70 * math.sin(u * math.pi) + 130 * u * u  # (o meio do corpo: sobe e entra de cabeça na terra)
        clip = base.get_clip()
        base.set_clip((0, 0, LARGURA, CHAO))
        base.blit(img, (int(x0 + 40 * u - img.get_width() / 2), int(y - img.get_height() / 2)))
        base.set_clip(clip)
    if t >= afunda:  # a TERRA espirrando
        u = t - afunda
        rnd = random.Random(3)
        for i in range(18):
            vx, vy = rnd.uniform(-6, 6), rnd.uniform(-11, -4)
            px, py = x0 + 40 + vx * u, CHAO - 4 + vy * u + 0.5 * u * u
            if py < CHAO:
                pygame.draw.circle(base, TERRA, (int(px), int(py)), 3 + i % 3)
        poeira(base, x0 + 40, CHAO, min(1, u / 20), cor=TERRA, larg=90, semente=2)
        rasgo(base, x0 + 40)
        if u == 0:
            c.tremor = 10
    c.mapa_frente(base, t)
    c.camera(q, base, (XO - 90, CHAO - 80), 1.9, pixel=True)
    if t >= afunda and t < afunda + 14:
        texto_pow(q, "TCHUF!", (int(w * 0.3), int(h * 0.26)), 56, (230, 200, 160), t - afunda)


def v2_roda(c, q, t, k):
    """2) Só a BARBATANA rodando em volta do derrotado, abrindo um sulco na terra... (tum... tum... tum)"""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 40)
    tt = t + 20
    for i in range(1, 10):  # a ONDA DE TERRA atrás
        xa, _ = circ(tt - i * 2)
        hh = (10 - i) * 1.6
        pygame.draw.ellipse(base, TERRA_ESC, (xa - 9, CHAO - hh - 2, 18, hh * 2 + 4))
        pygame.draw.ellipse(base, TERRA, (xa - 7, CHAO - hh, 14, hh * 2))
    x, a = circ(tt)
    vai = -1 if math.sin(a) > 0 else 1
    atras = math.sin(a) < 0  # (do lado de lá do derrotado: desenha antes dele)
    if atras:
        barbatana(c, base, x, CHAO, 1.4, vai, t)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    if not atras:
        barbatana(c, base, x, CHAO, 1.4, vai, t)
    rasgo(base, x)
    c.mapa_frente(base, t + 40)
    c.camera(q, base, (XO, CHAO - 60), 2.2, pixel=True)
    if t % 22 < 8:
        texto_pow(q, "tum...", (int(w * (0.2 + 0.6 * ((t // 22) % 2))), int(h * 0.24)), 44, (230, 230, 240), t % 22, giro=0.05)


def barbatana_grande(c, q, cx, base_y, e, t):
    """A BARBATANA vista de frente/perto, ilustrada GRANDE (nas cores da skin), com o código de barras."""
    p = pal(c)
    fin = [(-40, 0), (-24, -70), (-4, -120), (4, -104), (10, -100), (40, 0)]
    pts = [(cx + x * e, base_y + y * e) for x, y in fin]
    pygame.draw.polygon(q, BORDA, [(x + 4, y + 4) for x, y in pts])
    pygame.draw.polygon(q, p["m"], pts)
    pygame.draw.polygon(q, p["M"], [(cx, base_y), (cx - 4 * e, base_y - 120 * e), (cx + 40 * e, base_y)])
    pygame.draw.polygon(q, BORDA, pts, max(3, int(e * 1.2)))
    for i in range(6):  # o CÓDIGO DE BARRAS
        bx = cx + (-22 + i * 6) * e
        pygame.draw.line(q, BORDA, (bx, base_y - 14 * e), (bx, base_y - (34 - (i % 2) * 6) * e), max(2, int((1 + i % 2) * e * 1.2)))
    for i in range(3):  # os rasgos na ponta (barbatana rasgada)
        rx = cx + (-6 + i * 5) * e
        pygame.draw.polygon(q, BORDA, [(rx, base_y - (108 - i * 6) * e), (rx + 3 * e, base_y - (96 - i * 6) * e),
                                       (rx + 6 * e, base_y - (106 - i * 6) * e)])


def v3_vem(c, q, t, k):
    """3) CÂMERA NO CHÃO: a barbatana vem RASGANDO a terra direto pra câmera (a terra jorrando dos lados)."""
    w, h = q.get_size()
    hz = int(h * 0.48)
    if not hasattr(c, "_fundo_chao"):
        c._fundo_chao = pygame.Surface((w, h))
        fundo_desfocado(c, c._fundo_chao, 0, (LARGURA * 0.5, CHAO - h * 0.22), 1.6, 30)
    cores = cores_do_mapa(c)
    chao_perto(q, t, hz, cores=cores, fundo=c._fundo_chao)
    u = suave(k) ** 1.5
    e = 0.6 + u * 5.5
    by = hz + 10 + u * (h * 0.62)
    cx = w * 0.5 + math.sin(t * 0.3) * 20 * (1 - u)
    pygame.draw.polygon(q, tuple(int(v * 0.5) for v in cores[0]), [(cx - 30, hz + 8), (cx + 30, hz + 8), (cx + 50 * e, by + 4),
                                                                   (cx - 50 * e, by + 4)])  # o SULCO aberto
    rnd = random.Random(t // 2)
    for i in range(18):  # a terra jorrando dos dois lados
        lado = -1 if i % 2 else 1
        px = cx + lado * (40 * e + rnd.uniform(0, 70) * e * 0.4)
        py = by - rnd.uniform(0, 60) * e * 0.5
        pygame.draw.circle(q, cores[0] if i % 3 else TERRA_ESC, (int(px), int(py)), int(3 + 3 * e * rnd.uniform(0.3, 1)))
    barbatana_grande(c, q, cx, by, e, t)
    c.tremor = max(c.tremor, 2 + int(4 * u))
    if t > 8:
        texto_pow(q, "SHHHHRRRK", (int(w * 0.72), int(h * 0.2)), 36, (240, 220, 190), (t - 8) % 8, giro=-0.08)


def v4_medo(c, q, t, k):
    """4) CLOSE no derrotado: o chão treme em volta... !!"""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 80)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    for i in range(5):  # as rachaduras se abrindo embaixo dele
        a = math.pi + i * math.pi / 4
        comp = min(1, t / 14) * 60
        pygame.draw.line(base, TERRA_ESC, (XO, CHAO + 1), (XO + math.cos(a) * comp, CHAO + 2 + abs(math.sin(a)) * 3), 2)
    c.mapa_frente(base, t + 80)
    c.camera(q, base, (XO, CHAO - 40), 2.8, pixel=True)
    c.tremor = max(c.tremor, 3)
    if t > 6:
        texto_pow(q, "!!", (int(w * 0.56), int(h * 0.26)), 90, (255, 230, 120), t - 6)


def v5_salta(c, q, t, k):
    """5) Ele EXPLODE do chão de boca ESCANCARADA, num salto gigante (quadro de impacto, terra pra todo lado)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 120)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    x = XO - 120
    u = min(1, t / 24)
    y = CHAO + 60 * (1 - min(1, u * 3)) - math.sin(u * math.pi) * 90
    clip = base.get_clip()
    base.set_clip((0, 0, LARGURA, CHAO + 2))
    sph(c, base, pose(c, "s_martelo") if u < 0.5 else misturar(pose(c, "s_martelo"), pose(c, "s_ruge"), suave((u - 0.5) * 2)),
        x, y, boca=1.25, aceso=True)
    base.set_clip(clip)
    rnd = random.Random(6)
    for i in range(26):
        vx, vy = rnd.uniform(-9, 9), rnd.uniform(-14, -5)
        px, py = x + vx * t, CHAO - 4 + vy * t + 0.45 * t * t
        if py < CHAO:
            pygame.draw.circle(base, TERRA if i % 3 else TERRA_ESC, (int(px), int(py)), 3 + i % 4)
    poeira(base, x, CHAO, min(1, t / 26), cor=TERRA, larg=160, semente=5)
    rasgo(base, x)
    c.mapa_frente(base, t + 120)
    c.camera(q, base, (x + 40, CHAO - 110), 2.0, pixel=True)
    if t == 0:
        c.inverte, c.tremor = 3, 22
    if t < 16:
        texto_pow(q, "CHOOOMP!!", (int(w * 0.66), int(h * 0.26)), 70, (255, 120, 110), t, giro=0.1)


def v6_final(c, q, t, k):
    """6) Pousa do lado do derrotado e RUGE (a linha acesa)... CLAC! fecha a boca e sorri. O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 160)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    x = XO - 120
    rasgo(base, x)
    pygame.draw.ellipse(base, TERRA_ESC, (x - 50, CHAO - 6, 100, 14))
    clac = 44
    p = pose(c, "s_ruge") if t < clac + 16 else misturar(pose(c, "s_ruge"), pose(c, "parado"), suave(min(1, (t - clac - 16) / 10)))
    boca = 1.2 if t < clac else 0.0
    sph(c, base, p, x, boca=boca, aceso=True)
    cb = c.ponto(p, "cb", 1.0, x, CHAO)
    c.mapa_frente(base, t + 160)
    centro, z = ((x + XO) / 2, CHAO - 100), 1.9
    c.camera(q, base, centro, z, pixel=True)
    if t < clac:
        if t % 5 == 0:
            c.tremor = max(c.tremor, 6)
        texto_pow(q, "GROOOAR!", (int(w * 0.3), int(h * 0.22)), 58, pal(c)["l"], t % 8, giro=-0.08)
    elif t < clac + 12:
        if t == clac:
            c.tremor = 14
        bx, by = para_tela(centro, z, (cb[0] + 36, cb[1]))
        texto_pow(q, "CLAC!", (int(bx + 40), int(by - 70)), 60, (255, 240, 200), t - clac)
    if t >= 50:
        faixa_nome(q, "SPHYRUS", "O PREDADOR DO TOPO.", COR_NOME, (t - 50) / 30)


PLANOS_CIRCULO = [
    (44, v1_mergulha, {12: ("vento", 0.5), 20: ("terra", 0.8)}),
    (66, v2_roda, {0: ("terra", 0.3), 22: ("terra", 0.3), 44: ("terra", 0.3)}),
    (36, v3_vem, {0: ("terra", 0.7)}),
    (24, v4_medo, {6: ("blip", 0.5)}),
    (30, v5_salta, {0: ("explosao", 0.7), 2: ("soco", 0.6)}),
    (86, v6_final, {0: ("uivo", 0.9), 44: ("soco", 0.7)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_CIRCULO, titulo, oponente)
