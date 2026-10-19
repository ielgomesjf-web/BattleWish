"""CENAS DE ANIME do MAGNUS (loja): a entrada JAULA ARREBENTADA e a vitória ESCULTURA DE VIDRO.

Tudo no MAPA da luta, com a SKIN dele e o OPONENTE de verdade. O Magnus aparece com o desenho do jogo (montado na
escala do jogo e a câmera amplia; as penas do pescoço são as do próprio desenho). Os closes de detalhe (o cadeado
derretendo, o vidro virando cristal) e o FOGO são ilustrados, nas cores da skin dele.
"""
import math
import random

import pygame

import magnus
from cena_max import cores_do_mapa, chao_perto, fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

BORDA = (10, 8, 10)
XG, XO = LARGURA * 0.32, LARGURA * 0.74  # o Magnus e o oponente, no mapa
GRADE, GRADE_ESC = (128, 132, 142), (40, 40, 46)
AREIA, AREIA_ESC = (222, 192, 128), (150, 118, 70)
COR_NOME = (230, 100, 30)


def pal(c):
    return {k: c.cor(k, v) for k, v in magnus.PALETA.items()}


def pose(c, nome):
    return c.l.poses.get(nome) or c.l.poses["parado"]


def mag(c, base, p, x, y=CHAO, penas=1.0, d=1, escuro=0.0, enrolado=False):
    """Põe o Magnus (desenho do jogo) no mapa, com as penas do pescoço do tamanho pedido.
    escuro: o quanto a NOITE escurece ele (igual ao resto do mapa). enrolado: a cauda enrolada no corpo."""
    c.lutador().extra["penas"] = penas
    original = magnus.pontos_cauda
    if enrolado:  # (só durante esse desenho: a cauda do jogo, só que enrolada)
        magnus.pontos_cauda = cauda_enrolada
    try:
        img, pe = c.corpo(p, 1.0, d, guardar=False)
    finally:
        magnus.pontos_cauda = original
    if not escuro:
        base.blit(img, (int(x - pe[0]), int(y - pe[1])))
        return
    img = img.copy()
    img.fill((*cor_noite(escuro), 255), special_flags=pygame.BLEND_RGBA_MULT)
    base.blit(img, (int(x - pe[0]), int(y - pe[1])))


def olhos(c, q, p, x, centro=None, z=1.0, forca=1.0, y=CHAO):
    """O brilho dos OLHOS no escuro (no ponto da cabeça do desenho)."""
    cb = c.ponto(p, "cb", 1.0, x, y)
    o = (cb[0] + 9 * c.l.s, cb[1] - 3 * c.l.s)
    if centro is not None:
        o = para_tela(centro, z, o)
    cor = pal(c)["b"]
    brilho(q, (int(o[0]), int(o[1])), int(14 * z * forca) + 2, cor, int(230 * forca))
    pygame.draw.circle(q, pal(c)["B"], (int(o[0]), int(o[1])), max(1, int(1.6 * z)))


NOITE = 0.72


def cor_noite(f=NOITE, cor=(36, 34, 90)):
    return tuple(int(255 * (1 - f) + v * f) for v in cor)


def noite(q, f=NOITE):
    """A NOITE (escurece puxando pro azul)."""
    sup = pygame.Surface(q.get_size())
    sup.fill(cor_noite(f))
    q.blit(sup, (0, 0), special_flags=pygame.BLEND_RGB_MULT)


def no_escuro(base, desenha, *a, **k):
    """Desenha (jaula, cacos...) numa camada e escurece ela igual à noite antes de pôr no mapa."""
    sup = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    desenha(sup, *a, **k)
    sup.fill((*cor_noite(), 255), special_flags=pygame.BLEND_RGBA_MULT)
    base.blit(sup, (0, 0))


def frente_noite(c, base, t):
    """A frente do mapa (cercas, plantas...) também de noite."""
    sup = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    c.mapa_frente(sup, t)
    sup.fill((*cor_noite(), 255), special_flags=pygame.BLEND_RGBA_MULT)
    base.blit(sup, (0, 0))


def fogo(q, p0, ang, comp, t, larg=1.0, cores=None, semente=0):
    """Um JATO DE FOGO saindo de p0 na direção ang (bolotas que crescem, sobem e mudam de cor)."""
    b, B = cores or (magnus.BRASA, magnus.BRASA_CLARA)
    sup = pygame.Surface(q.get_size(), pygame.SRCALPHA)
    rnd = random.Random(semente + t)
    for i in range(36):
        u = ((i / 36) + t * 0.05) % 1
        d = comp * u
        x = p0[0] + math.cos(ang) * d + rnd.uniform(-1, 1) * d * 0.12 * larg
        y = p0[1] + math.sin(ang) * d + rnd.uniform(-1, 1) * d * 0.12 * larg - u * u * comp * 0.12
        r = (12 + u * 34) * larg
        cor = B if u < 0.3 else b if u < 0.75 else (120, 60, 40)
        pygame.draw.circle(sup, (*cor, int(230 * (1 - u * 0.7))), (int(x), int(y)), int(r))
    q.blit(sup, (0, 0))
    brilho(q, (int(p0[0] + math.cos(ang) * comp * 0.3), int(p0[1] + math.sin(ang) * comp * 0.3)), int(comp * 0.5), b, 90)


def boca(c, p, x, y=CHAO):
    """A ponta do focinho: segue a direção do pescoço (do peito pra cabeça)."""
    cb, pc = c.ponto(p, "cb", 1.0, x, y), c.ponto(p, "pc", 1.0, x, y)
    dx, dy = cb[0] - pc[0], cb[1] - pc[1]
    n = math.hypot(dx, dy) or 1
    return cb[0] + dx / n * 26 * c.l.s + 10 * c.l.s, cb[1] + dy / n * 26 * c.l.s


# =====================================================================
# A JAULA (escala do jogo)
# =====================================================================
JAULA_L, JAULA_A = 220, 150


def jaula(q, x, base, t, quebrou=-1, cadeado_calor=0.0):
    """A jaula de aço reforçada: grades grossas, cantoneiras, correntes, a placa EXP-13 e o cadeado.
    quebrou >= 0: quantos quadros desde que a rabada arrebentou (as grades voam)."""
    w, h = JAULA_L, JAULA_A
    x0 = x - w / 2
    if quebrou < 0:
        for i in range(9):  # as GRADES
            bx = x0 + i * w / 8
            pygame.draw.line(q, GRADE_ESC, (bx, base), (bx, base - h), 8)
            pygame.draw.line(q, GRADE, (bx, base), (bx, base - h), 4)
            pygame.draw.line(q, (200, 204, 214), (bx - 1, base - 4), (bx - 1, base - h + 4), 1)
        for yy in (base - h, base - h * 0.5, base - 6):  # as barras de travessa
            pygame.draw.rect(q, GRADE_ESC, (x0 - 6, yy - 6, w + 12, 12))
            pygame.draw.rect(q, GRADE, (x0 - 4, yy - 4, w + 8, 8))
        for cx in (x0, x0 + w):  # as cantoneiras com rebites
            pygame.draw.rect(q, GRADE_ESC, (cx - 8, base - h - 8, 16, h + 12))
            for j in range(5):
                pygame.draw.circle(q, (180, 184, 194), (int(cx), int(base - h + j * h / 4.5)), 2)
        placa = pygame.Rect(0, 0, 54, 26)  # a PLACA: perigo, EXP-13
        placa.center = (int(x0 + w * 0.3), int(base - h * 0.74))
        pygame.draw.rect(q, BORDA, placa.inflate(4, 4))
        pygame.draw.rect(q, (240, 200, 40), placa)
        for i in range(5):
            pygame.draw.line(q, BORDA, (placa.x + i * 12, placa.bottom), (placa.x + i * 12 + 8, placa.y + 16), 3)
        from efeitos import texto
        texto(q, "EXP-13", 11, BORDA, (placa.centerx, placa.y + 7), sombra=False)
        cad = (x0 + w * 0.72, base - h * 0.5)  # o CADEADO e a corrente
        for j in range(5):
            a = j * 0.9
            pygame.draw.ellipse(q, GRADE_ESC, (cad[0] - 14 + j * 6, cad[1] - 8 + math.sin(a) * 4, 10, 14), 3)
        quente = tuple(int(v + (w_ - v) * cadeado_calor) for v, w_ in zip((150, 120, 50), (255, 120, 40)))
        pygame.draw.rect(q, BORDA, (cad[0] + 2, cad[1] - 2, 18, 16), border_radius=3)
        pygame.draw.rect(q, quente, (cad[0] + 4, cad[1], 14, 12), border_radius=3)
        pygame.draw.arc(q, BORDA, (cad[0] + 4, cad[1] - 10, 14, 16), 0, math.pi, 3)
        if cadeado_calor > 0:
            brilho(q, (int(cad[0] + 11), int(cad[1] + 6)), int(22 * cadeado_calor) + 2, (255, 120, 40), 200)
        return
    u = quebrou  # as GRADES VOANDO (e as travessas caindo)
    rnd = random.Random(13)
    for i in range(9):
        bx = x0 + i * w / 8 + (i - 4) * u * rnd.uniform(4, 9)
        by = base - h / 2 - u * rnd.uniform(5, 11) + u * u * 0.5
        if by > base - 4:
            by = base - 4
            a = math.pi / 2
        else:
            a = u * 0.25 * (1 if i % 2 else -1)
        dx, dy = math.sin(a) * h / 2, math.cos(a) * h / 2
        pygame.draw.line(q, GRADE_ESC, (bx - dx, by - dy), (bx + dx, by + dy), 8)
        pygame.draw.line(q, GRADE, (bx - dx, by - dy), (bx + dx, by + dy), 4)


def metal_quente(calor):
    """A cor do metal esquentando: cinza -> vermelho -> laranja -> amarelo quase branco."""
    pontos = ((0.0, GRADE), (0.35, (200, 50, 30)), (0.7, (255, 140, 40)), (1.0, (255, 236, 170)))
    for (a, ca), (b, cb) in zip(pontos, pontos[1:]):
        if calor <= b:
            u = (calor - a) / (b - a)
            return tuple(int(x + (y - x) * u) for x, y in zip(ca, cb))
    return pontos[-1][1]


def jaula_derretendo(q, x, base, t, k, esfria=0.0):
    """A JAULA DERRETENDO (k: 0 = em brasa e inteira ... 1 = virou uma POÇA de metal no chão).
    As grades amolecem e entortam, o topo afunda, pinga metal... e fica a poça brilhando (esfria: 0..1)."""
    w, h = JAULA_L, JAULA_A
    x0 = x - w / 2
    cor = metal_quente((0.5 + 0.5 * k) * (1.0 - 0.6 * esfria))  # (vai ficando mais quente enquanto derrete)
    escura = tuple(int(v * 0.55) for v in cor)
    alto = h * (1 - k) ** 1.4  # (o quanto as grades ainda estão de pé)
    if alto > 3:
        for i in range(9):
            bx = x0 + i * w / 8
            curva = math.sin(i * 1.7) * 22 * k  # (cada grade entorta pra um lado)
            pts = []
            for j in range(7):
                u = j / 6
                pts.append((bx + curva * u * u + math.sin(t * 0.2 + i) * 2 * k, base - alto * u))
            pygame.draw.lines(q, escura, False, pts, 9)
            pygame.draw.lines(q, cor, False, pts, 5)
            gota = (t * 3 + i * 17) % 40  # os PINGOS de metal derretido
            if k > 0.05:
                pygame.draw.circle(q, cor, (int(pts[-1][0]), int(pts[-1][1] + gota)), 3)
        topo = [(x0 - 4 + i * (w + 8) / 6, base - alto - math.sin(i * 1.3 + 1) * 10 * k) for i in range(7)]
        pygame.draw.lines(q, escura, False, topo, 11)
        pygame.draw.lines(q, cor, False, topo, 6)
    poca = pygame.Rect(0, 0, w * (0.5 + 0.9 * k), 10 + 14 * k)  # a POÇA no chão
    poca.center = (int(x), int(base + 2))
    pygame.draw.ellipse(q, escura, poca.inflate(8, 6))
    pygame.draw.ellipse(q, cor, poca)
    pygame.draw.ellipse(q, metal_quente((0.6 + 0.4 * k) * (1.0 - 0.7 * esfria)), poca.inflate(-poca.w * 0.4, -poca.h * 0.5))
    for i in range(4):  # as bolhas na poça
        v = (t * 2 + i * 9) % 18
        if esfria < 0.8:
            pygame.draw.circle(q, metal_quente(1.0), (int(poca.x + poca.w * (0.2 + i * 0.2)), int(poca.centery - v * 0.3)),
                               max(1, 4 - v // 5), 1)
    if esfria < 1:
        brilho(q, poca.center, int(90 * (1 - esfria) * (0.5 + k)) + 2, (255, 120, 40), int(180 * (1 - esfria)))


# =====================================================================
# ENTRADA: JAULA ARREBENTADA
# =====================================================================
def base_noite(c, t, opo="parado"):
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, opo, 1.0, XO, CHAO)
    noite(base)
    return base


def dormindo(c, respira=0.0):
    """A pose DORMINDO: deitado de barriga, rente ao chão, ENROLADO (pra caber na jaula): as patas dobradas
    embaixo do corpo e a CABEÇA abaixada encostada no peito. (A cauda enrolada vem do mag(..., enrolado=True).)"""
    base = pose(c, "x_rasteja")
    f = 0.36 + 0.03 * respira
    p = {k: (v[0] * 0.62, v[1] * f) for k, v in base.items()}
    qx = p["qd"][0]
    p["pc"] = (qx + 14, p["qd"][1] + 4 + 2 * respira)  # (o pescoço curvado pra baixo)
    p["cb"] = (qx + 22, 7 + respira)                    # (a cabeça deitada no chão, na frente do peito)
    p["mt"], p["mf"] = (qx + 22, 3), (qx + 28, 3)       # (os braços recolhidos embaixo da cabeça)
    p["ct"], p["cf"] = (qx + 14, 8), (qx + 18, 8)
    return p


def cauda_enrolada(l, p, base):
    """A CAUDA ENROLADA em volta do corpo (dormindo): sai pra trás, desce até o chão e volta pela frente,
    em volta das patas. (Mesmo número de pontos da cauda do jogo: o desenho dela continua o mesmo.)"""
    qx, qy = base
    cx, cy = qx + 4, max(6, qy * 0.55)
    rx, ry = 46, max(6, qy * 0.55 - 1)
    pts = []
    for i in range(13):
        a = math.pi * (0.8 + 1.15 * i / 12)
        pts.append((cx + math.cos(a) * rx, cy + math.sin(a) * ry))
    return pts


def e1_dorme(c, q, t, k):
    """1) No MAPA, de noite: a JAULA (placa EXP-13)... e ele lá dentro DORMINDO, deitado, respirando devagar
    (Zzz). A câmera vai chegando. O oponente olha."""
    from efeitos import texto
    base = base_noite(c, t)
    respira = math.sin(t * 0.12)
    p = dormindo(c, respira)
    mag(c, base, p, XG - 36, penas=0.3, escuro=NOITE * 0.45, enrolado=True)
    no_escuro(base, jaula, XG, CHAO, t)
    cb = c.ponto(p, "cb", 1.0, XG - 36, CHAO)
    if respira > 0.6:  # a fumacinha saindo do nariz quando ele solta o ar
        for i in range(2):
            sup = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(sup, (130, 120, 120, 120), (20, 20), 6 + i * 4)
            base.blit(sup, (cb[0] + i * 10, cb[1] - 24 - i * 8))
    frente_noite(c, base, t)
    centro, z = (XG + 120 * (1 - suave(k)), CHAO - 70), 1.5 + 0.7 * suave(k)
    c.camera(q, base, centro, z, pixel=True)
    zx, zy = para_tela(centro, z, (cb[0] + 10, cb[1] - 30))
    for i in range(3):  # Zzz
        u = (t * 0.03 + i * 0.33) % 1
        texto(q, "Z", int(18 + i * 8 + 10 * z), (210, 210, 240), (int(zx + u * 60), int(zy - u * 120)))


def narina_close(c, q, w, h, t, cheira):
    """CLOSE no FOCINHO de metal (de lado): as placas, as listras em brasa, os dentes... e a NARINA.
    cheira: 0..1 (a narina abre e o ar entra)."""
    pb = pal(c)
    fundo_desfocado(c, q, t, (XG + 40, CHAO - 30), 2.6, 150)
    noite(q, 0.5)
    cx, cy = w * 0.62, h * 0.5
    focinho = [(-700, -150), (40, -120), (240, -60), (290, 0), (250, 60), (60, 90), (-700, 120)]
    pts = [(cx + x, cy + y) for x, y in focinho]
    pygame.draw.polygon(q, BORDA, [(x + 8, y + 8) for x, y in pts])
    pygame.draw.polygon(q, pb["m"], pts)
    pygame.draw.polygon(q, pb["M"], [(cx - 700, cy + 40), (cx + 60, cy + 50), (cx + 250, cy + 60), (cx + 60, cy + 90),
                                     (cx - 700, cy + 120)])
    pygame.draw.polygon(q, pb["c"], [(cx - 600, cy - 130), (cx + 30, cy - 104), (cx + 150, cy - 74), (cx - 600, cy - 100)])
    for i in range(4):  # as emendas das placas (com rebites)
        x = cx - 520 + i * 150
        pygame.draw.line(q, BORDA, (x, cy - 140 + i * 8), (x + 20, cy + 110), 4)
        for j in range(3):
            pygame.draw.circle(q, pb["c"], (int(x + 6 + j * 6), int(cy - 100 + j * 70)), 5)
    for i in range(3):  # as LISTRAS em brasa
        x = cx - 460 + i * 150
        pygame.draw.line(q, pb["b"], (x + 40, cy - 110), (x + 70, cy + 20), 7)
    pygame.draw.polygon(q, BORDA, pts, 8)
    for i in range(7):  # os dentes pra fora, embaixo
        x = cx - 380 + i * 80
        pygame.draw.polygon(q, BORDA, [(x - 4, cy + 86), (x + 30, cy + 86), (x + 12, cy + 150)])
        pygame.draw.polygon(q, (240, 238, 228), [(x, cy + 88), (x + 26, cy + 88), (x + 12, cy + 140)])
    nx, ny = cx + 190, cy - 10  # a NARINA
    abre = 1 + 0.6 * cheira
    nar = pygame.Rect(0, 0, int(70 * abre), int(34 * abre))
    nar.center = (int(nx), int(ny))
    pygame.draw.ellipse(q, BORDA, nar.inflate(14, 14))
    pygame.draw.ellipse(q, (14, 10, 12), nar)
    if cheira > 0:  # o AR sendo puxado pra dentro da narina (riscos e poeirinha)
        for i in range(14):
            u = 1 - ((t * 0.08 + i / 14) % 1)
            a = -0.9 + (i % 7) * 0.3
            d = 60 + u * 520
            px, py = nx + math.cos(a) * d, ny + math.sin(a) * d * 0.6
            pygame.draw.line(q, (220, 220, 235), (px, py), (px + math.cos(a) * 40 * u, py + math.sin(a) * 24 * u), 3)
            pygame.draw.circle(q, (200, 190, 170), (int(px), int(py)), 3)


def e2_narina(c, q, t, k):
    """2) CLOSE na NARINA: ela solta o ar devagar... aí ele CHEIRA (o ar entra rápido, a narina abre)."""
    w, h = q.get_size()
    cheira = 0.0 if t < 14 else suave(min(1, (t - 14) / 6)) * (1 if t < 34 else max(0, 1 - (t - 34) / 6))
    narina_close(c, q, w, h, t, cheira)
    if t < 12:  # (soltando o ar: fumacinha)
        for i in range(3):
            v = t * 3 + i * 8
            sup = pygame.Surface((160, 160), pygame.SRCALPHA)
            pygame.draw.circle(sup, (150, 140, 140, max(0, 140 - v * 3)), (80, 80), int(20 + v * 1.5))
            q.blit(sup, (w * 0.62 + 250 + v * 4 - 80, h * 0.5 - 10 - v - 80))
    if t >= 14:
        texto_pow(q, "SNIIIIF!!", (int(w * 0.3), int(h * 0.24)), 66, (230, 230, 240), t - 14, giro=0.08)
    if t == 16:
        c.tremor = 6


def fogo_tela(q, t, k, pb):
    """O FOGO tomando a TELA TODA (k = quanto já tomou): labaredas subindo."""
    w, h = q.get_size()
    if k <= 0:
        return
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    if k > 0.5:
        sup.fill((*pb["b"], int(255 * min(1, (k - 0.5) * 2))))
    cores = ((120, 30, 10), pb["b"], pb["B"], (255, 245, 210))
    rnd = random.Random(7)
    for i in range(90):
        u = ((t * 0.035 + i / 90) % 1)
        x = rnd.uniform(-60, w + 60) + math.sin(t * 0.2 + i) * 20
        y = h + 80 - u * (h + 220)
        r = (40 + rnd.uniform(0, 70)) * (1 - u * 0.6) * (0.5 + k)
        cor = cores[min(3, int((1 - u) * 3.6))]
        pygame.draw.circle(sup, (*cor, int(255 * min(1, k * 1.3))), (int(x), int(y)), int(r))
    q.blit(sup, (0, 0))


def olho_close(c, q, t, abre, chama, e, centro):
    """O OLHO dele (ilustrado): a placa de metal em volta, a pálpebra, a íris em brasa, a pupila fininha e,
    lá dentro, um FOGUINHO (chama: 0..1). e = o tamanho (a câmera entrando no olho aumenta); centro = a pupila."""
    pb = pal(c)
    cx, cy = centro

    def P(x, y):
        return cx + x * e, cy + y * e

    q.fill(tuple(int(v * 0.4) for v in pb["M"]))
    placa = [P(-260, -110), P(240, -130), P(300, 0), P(240, 120), P(-260, 100)]
    pygame.draw.polygon(q, pb["M"], placa)
    pygame.draw.polygon(q, pb["m"], [P(-240, -96), P(220, -114), P(270, -20), P(-240, -10)])
    for i in range(3):  # as listras em brasa
        pygame.draw.line(q, pb["b"], P(-220 + i * 70, -100), P(-180 + i * 70, -20), max(2, int(5 * e)))
    pygame.draw.ellipse(q, BORDA, (*P(-120, -70), 240 * e, 140 * e))  # o buraco do olho
    aberto = suave(abre)
    if aberto > 0.02:
        iris = pygame.Rect(0, 0, 200 * e, 120 * e * aberto)
        iris.center = (int(cx), int(cy))
        pygame.draw.ellipse(q, pb["b"], iris)
        pygame.draw.ellipse(q, pb["B"], iris.inflate(-iris.w * 0.45, -iris.h * 0.45))
        pupila = pygame.Rect(0, 0, max(2, 26 * e), max(2, 116 * e * aberto))
        pupila.center = (int(cx), int(cy))
        pygame.draw.ellipse(q, (8, 4, 6), pupila)
        if chama > 0:  # o FOGUINHO lá dentro da pupila
            pe = cy + 30 * e * aberto
            for i in range(5):
                fx = cx + (i - 2) * 4 * e
                alt = (14 + 10 * math.sin(t * 0.7 + i * 1.3)) * e * chama
                cor = pb["b"] if i % 2 else pb["B"]
                pygame.draw.polygon(q, cor, [(fx - 5 * e, pe), (fx + 5 * e, pe), (fx + math.sin(t * 0.9 + i) * 3 * e, pe - alt)])
            brilho(q, (int(cx), int(cy)), int(30 * e * chama) + 2, pb["b"], int(min(255, 160 * chama)))
        pygame.draw.circle(q, (255, 255, 255), (int(cx - 50 * e), int(cy - 24 * e * aberto)), max(2, int(9 * e)))
    tampa = 70 * e * (1 - aberto)  # as PÁLPEBRAS de metal
    if tampa > 0:
        pygame.draw.rect(q, pb["M"], (cx - 130 * e, cy - 75 * e, 260 * e, tampa + 4))
        pygame.draw.rect(q, pb["M"], (cx - 130 * e, cy + 75 * e - tampa - 4, 260 * e, tampa + 4))
    pygame.draw.line(q, BORDA, P(-130, -70 + (1 - aberto) * 70), P(130, -70 + (1 - aberto) * 70), max(3, int(6 * e)))


OLHO_ABRE, OLHO_CHAMA, OLHO_ENTRA, OLHO_FIM = 6, 16, 24, 48


def e3_olho(c, q, t, k):
    """3) O OLHO abre e BRILHA, com um foguinho bem apagadinho lá dentro... a câmera ENTRA no olho, o fogo
    cresce e toma a TELA TODA."""
    w, h = q.get_size()
    pb = pal(c)
    abre = min(1, max(0, t - OLHO_ABRE) / 8)
    chama = 0.0 if t < OLHO_CHAMA else min(1, (t - OLHO_CHAMA) / 8) * 0.5
    entra = max(0, t - OLHO_ENTRA) / (OLHO_FIM - OLHO_ENTRA)
    e = 1.6 * (1 + 22 * entra ** 2.2)  # (a câmera mergulhando na pupila)
    if entra > 0:
        chama = 0.5 + 1.5 * entra
    olho_close(c, q, t, abre, chama, e, (w * 0.5, h * 0.5))
    fogo_tela(q, t, max(0, (entra - 0.45) / 0.55), pb)


def e4_cospe(c, q, t, k):
    """4) O fogo da tela SE ABRE... e ele já está de BOCA ABERTA cuspindo FOGO na jaula: as grades ficam em BRASA,
    amolecem, entortam e DERRETEM até virar uma poça. O oponente se protege do calor."""
    w, h = q.get_size()
    pb = pal(c)
    base = base_noite(c, t + 40, "defesa" if 2 < t < 34 else "parado")
    p = pose(c, "x_cospe")
    mag(c, base, p, XG - 30, penas=1.0, escuro=NOITE * 0.3)
    esquenta, derrete = 12, 30
    if t < esquenta:  # esquentando: cinza -> vermelho -> laranja
        calor = t / esquenta
        sup = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        jaula(sup, XG, CHAO, t)
        quente = metal_quente(calor)
        sup.fill((*tuple(min(255, int(v * (1 + calor))) for v in quente), 255), special_flags=pygame.BLEND_RGBA_MULT)
        base.blit(sup, (0, 0))
        brilho(base, (int(XG + 40), int(CHAO - 70)), int(120 * calor) + 2, (255, 120, 40), int(200 * calor))
    else:
        jaula_derretendo(base, XG, CHAO, t, suave(min(1, (t - esquenta) / (derrete - esquenta))))
    bx, by = boca(c, p, XG - 30)
    fogo(base, (bx, by), 0.05, 260 if t < derrete + 4 else 260 * max(0, 1 - (t - derrete - 4) / 6), t, 0.8,
         (pb["b"], pb["B"]))
    frente_noite(c, base, t + 40)
    c.camera(q, base, (XG + 110, CHAO - 90), 1.7, pixel=True)
    fogo_tela(q, t, max(0, 1 - t / 8), pb)  # (o fogo da tela se abrindo)
    if 4 <= t < derrete + 4:
        c.tremor = max(c.tremor, 3)
    if 4 <= t < esquenta + 4:
        texto_pow(q, "FWOOOOSH!!", (int(w * 0.66), int(h * 0.22)), 74, pb["B"], (t - 4) % 8, giro=0.08)
    elif esquenta + 4 <= t:
        texto_pow(q, "SHHHHHHH...", (int(w * 0.62), int(h * 0.22)), 60, metal_quente(0.8), (t - esquenta - 4) % 10,
                  giro=0.05)


def pegada(base, x, idade, pb):
    """A PEGADA EM BRASA no chão (vai apagando)."""
    f = max(0, 1 - idade / 50)
    if f <= 0:
        return
    for dx in (-6, 0, 6):  # os 3 dedos
        pygame.draw.line(base, tuple(int(v * f + 40 * (1 - f)) for v in pb["b"]), (x, CHAO + 2), (x + dx * 1.6, CHAO + 6), 3)
    if f > 0.4:
        sup = pygame.Surface((30, 40), pygame.SRCALPHA)
        hh = int(14 * f)
        pygame.draw.polygon(sup, (*pb["B"], int(200 * f)), [(9, 36), (15, 36 - hh - 6), (21, 36)])
        pygame.draw.polygon(sup, (*pb["b"], int(220 * f)), [(6, 38), (15, 38 - hh), (24, 38)])
        base.blit(sup, (x - 15, CHAO - 32))


def e5_pisa(c, q, t, k):
    """5) Câmera BAIXA nas garras: ele sai da jaula pisando, e cada pegada fica EM BRASA no chão."""
    base = base_noite(c, t + 70)
    pb = pal(c)
    jaula_derretendo(base, XG - 70, CHAO, t + 40, 1.0, esfria=min(1, 0.45 + t / 40))
    fase = t * 0.2
    x = XG - 30 + 3.0 * t
    passos = [i for i in range(0, t + 1, 8)]
    for i in passos:  # as pegadas que ficaram
        pegada(base, XG - 30 + 3.0 * i + (12 if (i // 8) % 2 else -8), t - i, pb)
    andar = ("andar1", "andar2", "andar3", "andar4")
    i = int(fase) % 4
    p = misturar(pose(c, andar[i]), pose(c, andar[(i + 1) % 4]), fase % 1)
    mag(c, base, p, x, escuro=NOITE)
    frente_noite(c, base, t + 70)
    c.camera(q, base, (x + 20, CHAO - 34), 3.2, pixel=True)
    if t % 8 == 0:
        c.tremor = max(c.tremor, 3)


def e7_ruge(c, q, t, k):
    """7) O RUGIDO com FOGO pro céu (as penas todas eriçadas, a tela tremendo)... e o nome."""
    w, h = q.get_size()
    base = base_noite(c, t + 150, "defesa" if t < 30 else "parado")
    x = XG + 90
    p = misturar(pose(c, "m_fareja"), pose(c, "m_ruge"), suave(min(1, t / 8)))
    mag(c, base, p, x, penas=1.0, escuro=NOITE)
    if 6 <= t < 48:  # o JATO DE FOGO pra cima
        pb = pal(c)
        bx, by = boca(c, p, x)
        fogo(base, (bx, by), -1.05, 240 * min(1, (t - 6) / 8), t, 0.9, (pb["b"], pb["B"]))
    frente_noite(c, base, t + 150)
    centro, z = (x + 70, CHAO - 150), 1.6
    c.camera(q, base, centro, z, pixel=True)
    if 6 <= t < 46:
        if t % 4 == 0:
            c.tremor = max(c.tremor, 7)
        texto_pow(q, "GRRAAAAWR!!", (int(w * 0.6), int(h * 0.3)), 60, pal(c)["B"], t % 8, giro=0.1)
    if t >= 32:
        faixa_nome(q, "MAGNUS", "EXPERIMENTO 13.", COR_NOME, (t - 32) / 30)


PLANOS = [
    (44, e1_dorme, {0: ("vento", 0.3), 24: ("vento", 0.2)}),
    (40, e2_narina, {14: ("vento", 0.9)}),
    (48, e3_olho, {6: ("blip", 0.4), 16: ("carga", 0.6), 26: ("foguete", 0.7)}),
    (44, e4_cospe, {0: ("foguete", 1.0), 14: ("puf", 0.7), 22: ("lingua", 0.5)}),
    (36, e5_pisa, {0: ("queda", 0.4), 16: ("queda", 0.4), 32: ("queda", 0.4)}),
    (70, e7_ruge, {6: ("uivo", 1.0), 7: ("foguete", 0.8)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: ESCULTURA DE VIDRO
# =====================================================================
XA = XG + 120  # onde ele junta a areia


def monte(base, k, quente=0.0, derrete=0.0):
    """O monte de areia (vai ficando em brasa)."""
    cor = tuple(int(a + (b - a) * quente) for a, b in zip(AREIA, (255, 170, 80)))
    w_, h_ = 80 * k * (1 - derrete * 0.3), 34 * k * (1 + derrete)
    r = pygame.Rect(0, 0, max(2, w_), max(2, h_))
    r.midbottom = (int(XA), int(CHAO + 2))
    pygame.draw.ellipse(base, AREIA_ESC, r.inflate(4, 4))
    pygame.draw.ellipse(base, cor, r)
    if quente > 0:
        brilho(base, r.center, int(60 * quente) + 2, (255, 140, 40), int(180 * quente))


def cristais(q, ax, base_y, e, esfria, t, alfa=170):
    """A ESCULTURA DE VIDRO: um cacho de cristais (laranja quente -> transparente azulado), com brilho."""
    camada = pygame.Surface(q.get_size(), pygame.SRCALPHA)
    vidro = (int(255 - 90 * esfria), int(170 + 70 * esfria), int(90 + 165 * esfria), alfa)
    pecas_ = ((0, 86, 0.0, 15), (-22, 58, -0.35, 12), (22, 64, 0.3, 12), (-38, 34, -0.6, 9), (36, 38, 0.6, 9))
    contornos = []
    for dx, alto, ang, larg in pecas_:
        bx = ax + dx * e * 0.6
        c, sn = math.cos(ang), math.sin(ang)

        def R(px, py):
            return bx + (px * c - py * sn) * e, base_y - (px * sn + py * c) * e

        pts = [R(-larg, 0), R(-larg, alto * 0.75), R(0, alto), R(larg, alto * 0.75), R(larg, 0)]
        pygame.draw.polygon(camada, vidro, pts)
        pygame.draw.polygon(camada, (255, 255, 255, 80), [R(-larg, 0), R(-larg, alto * 0.75), R(0, alto), R(0, 0)])
        contornos.append((pts, R(0, alto), R(0, 0)))
    q.blit(camada, (0, 0))
    for pts, pico, pe in contornos:
        pygame.draw.polygon(q, (220, 245, 255), pts, max(1, int(e * 1.2)))
        pygame.draw.line(q, (200, 235, 250), pico, pe, max(1, int(e * 0.6)))
    if esfria < 1:
        brilho(q, (int(ax), int(base_y - 40 * e)), int(70 * e * (1 - esfria)) + 2, (255, 140, 40), int(200 * (1 - esfria)))


def v1_cava(c, q, t, k):
    """1) No MAPA, do lado do derrotado: ele CAVA e junta a areia com as garras (a areia voando)."""
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    p = pose(c, "x_garra_a" if (t // 5) % 2 else "x_garra_b")
    mag(c, base, p, XG)
    monte(base, min(1, t / 40))
    rnd = random.Random(t // 2)
    for i in range(6):  # a areia voando pra trás
        u = (t * 2 + i * 7) % 20
        px = XA - 20 - u * rnd.uniform(3, 6)
        py = CHAO - 6 - u * 3 + u * u * 0.2
        pygame.draw.circle(base, AREIA, (int(px), int(py)), 3)
    c.mapa_frente(base, t)
    c.camera(q, base, ((XG + XO) / 2, CHAO - 80), 1.7, pixel=True)


def v2_areia(c, q, t, k):
    """2) CÂMERA NO CHÃO: as garras cavando de pertinho, a areia espirrando NA CÂMERA."""
    w, h = q.get_size()
    hz = int(h * 0.42)
    if not hasattr(c, "_fundo_chao"):
        c._fundo_chao = pygame.Surface((w, h))
        fundo_desfocado(c, c._fundo_chao, 0, (LARGURA * 0.5, CHAO - h * 0.22), 1.6, 30)
    chao_perto(q, t, hz, cores=cores_do_mapa(c), fundo=c._fundo_chao)
    pb = pal(c)
    cresce = min(1, t / 30)
    r = pygame.Rect(0, 0, int(520 * cresce) + 20, int(220 * cresce) + 10)  # o MONTE crescendo
    r.midbottom = (int(w * 0.5), int(h * 0.98))
    pygame.draw.ellipse(q, AREIA_ESC, r.inflate(10, 10))
    pygame.draw.ellipse(q, AREIA, r)
    pygame.draw.ellipse(q, tuple(min(255, v + 20) for v in AREIA), (r.x + r.w * 0.2, r.y + 10, r.w * 0.4, r.h * 0.3))
    for lado in (-1, 1):  # as MÃOS de metal (3 dedos com as unhas curvas) cavando, alternando
        fase = (t * 0.45 + (0 if lado < 0 else math.pi))
        gx = w * 0.5 + lado * w * 0.27 + math.sin(fase) * 40 * lado
        gy = h * 0.6 + math.cos(fase) * 46
        pygame.draw.line(q, BORDA, (gx - lado * 120, -40), (gx, gy - 40), 64)  # o braço (vem de cima)
        pygame.draw.line(q, pb["M"], (gx - lado * 120, -40), (gx, gy - 40), 50)
        pygame.draw.line(q, pb["b"], (gx - lado * 120 - 10, -40), (gx - 10, gy - 50), 5)  # (a listra em brasa)
        mao = pygame.Rect(0, 0, 120, 80)
        mao.center = (int(gx), int(gy - 20))
        pygame.draw.ellipse(q, BORDA, mao.inflate(12, 12))
        pygame.draw.ellipse(q, pb["m"], mao)
        pygame.draw.ellipse(q, pb["c"], (mao.x + 18, mao.y + 10, 50, 18))  # (o brilho do metal)
        for dedo in (-1, 0, 1):  # os dedos abertos e as UNHAS curvas
            a = math.pi / 2 + dedo * 0.45
            x0, y0 = gx + dedo * 30, gy + 6
            x1, y1 = x0 + math.cos(a) * 46 + dedo * 8, y0 + math.sin(a) * 46
            pygame.draw.line(q, BORDA, (x0, y0), (x1, y1), 34)
            pygame.draw.line(q, pb["m"], (x0, y0), (x1, y1), 24)
            unha = [(x1 - 14, y1 - 4), (x1 + 14, y1 - 4), (x1 + dedo * 18 + 6, y1 + 46), (x1 + dedo * 14 - 2, y1 + 40)]
            pygame.draw.polygon(q, BORDA, [(x + 0, y + 3) for x, y in unha])
            pygame.draw.polygon(q, (240, 238, 228), unha)
            pygame.draw.line(q, (255, 255, 255), (x1 - 6, y1), (x1 + dedo * 12, y1 + 34), 3)
    rnd = random.Random(t)
    for i in range(22):  # a AREIA espirrando na câmera
        a = rnd.uniform(-math.pi, 0)
        d = rnd.uniform(40, 520) * ((t % 6) / 6 + 0.3)
        px, py = w * 0.5 + math.cos(a) * d, h * 0.8 + math.sin(a) * d * 0.7
        pygame.draw.circle(q, AREIA if i % 3 else AREIA_ESC, (int(px), int(py)), int(3 + rnd.uniform(0, 1) * d * 0.03))
    if t > 6:
        texto_pow(q, "SCRITCH SCRITCH", (int(w * 0.5), int(h * 0.16)), 36, (240, 220, 170), t % 8, giro=-0.05)


def v3_fogo(c, q, t, k):
    """3) Ele COSPE FOGO no monte de areia: FWOOOSH! O monte fica em BRASA."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 60)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    p = misturar(pose(c, "parado"), pose(c, "m_fareja"), suave(min(1, t / 6)))
    mag(c, base, p, XG)
    quente = suave(min(1, max(0, t - 6) / 26))
    monte(base, 1.0, quente)
    if t >= 6:
        pb = pal(c)
        bx, by = boca(c, p, XG)
        ang = math.atan2(CHAO - 14 - by, XA - bx)
        fogo(base, (bx, by), ang, math.hypot(XA - bx, CHAO - by) * min(1, (t - 6) / 5) + 10, t, 0.5, (pb["b"], pb["B"]))
    c.mapa_frente(base, t + 60)
    c.camera(q, base, ((XG + XA) / 2 + 10, CHAO - 70), 2.4, pixel=True)
    if t > 6:
        texto_pow(q, "FWOOOOSH!!", (int(w * 0.68), int(h * 0.24)), 60, pal(c)["B"], t % 8, giro=0.08)
        c.tremor = max(c.tremor, 2)


def v4_vira_vidro(c, q, t, k):
    """4) CLOSE no monte: a areia DERRETE em brasa... sobe em CRISTAIS... e vai esfriando até virar VIDRO."""
    w, h = q.get_size()
    fundo_desfocado(c, q, t, (XA, CHAO - 60), 2.6, 90)
    derrete = suave(min(1, t / 14))
    sobe = suave(min(1, max(0, t - 10) / 16))
    esfria = suave(min(1, max(0, t - 24) / 18))
    base_y = h * 0.86
    if sobe < 1:  # a POÇA derretida borbulhando
        r = pygame.Rect(0, 0, int(560 - 200 * sobe), int(120 * (1 - sobe) + 20))
        r.midbottom = (int(w * 0.5), int(base_y + 20))
        pygame.draw.ellipse(q, (255, 140, 40), r)
        pygame.draw.ellipse(q, (255, 220, 140), r.inflate(-r.w * 0.4, -r.h * 0.4))
        brilho(q, r.center, 260, (255, 140, 40), int(200 * derrete))
        for i in range(6):
            bx = r.x + r.w * (0.15 + i * 0.14)
            v = (t * 2 + i * 7) % 16
            pygame.draw.circle(q, (255, 240, 190), (int(bx), int(r.centery - v)), max(1, 8 - v // 2), 2)
    if sobe > 0:
        cristais(q, w * 0.5, base_y + 20, 3.8 * sobe, esfria, t, alfa=200)
    if esfria >= 1 or t > 36:  # brilhinhos
        for i in range(4):
            fase = (t + i * 9) % 28
            if fase < 10:
                px, py = w * (0.38 + i * 0.08), h * (0.24 + (i % 2) * 0.2)
                r_ = 30 * math.sin(fase / 10 * math.pi)
                pygame.draw.line(q, (255, 255, 255), (px - r_, py), (px + r_, py), 3)
                pygame.draw.line(q, (255, 255, 255), (px, py - r_), (px, py + r_), 3)
    if t > 30:
        texto_pow(q, "PLING!", (int(w * 0.76), int(h * 0.26)), 52, (200, 240, 255), t - 30, giro=-0.08)


def v5_final(c, q, t, k):
    """5) No MAPA: a ESCULTURA DE VIDRO brilhando do lado do derrotado... ele admira, fareja... e ergue a cabeça. O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 100)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    if t < 30:
        p = pose(c, "m_fareja")
    else:
        p = misturar(pose(c, "m_fareja"), pose(c, "vitoria"), suave(min(1, (t - 30) / 10)))
    mag(c, base, p, XG - 20)
    cristais(base, XA + 10, CHAO, 1.5, 1.0, t)
    brilha = (t * 3) % 160  # o reflexo subindo
    if brilha < 130:
        y = CHAO - brilha
        pygame.draw.line(base, (255, 255, 255), (XA - 34, y + 8), (XA + 54, y - 10), 2)
    if (t // 10) % 3 == 0:
        brilho(base, (int(XA + 10), int(CHAO - 129)), 18, (255, 255, 255), 230)
    c.mapa_frente(base, t + 100)
    c.camera(q, base, ((XG + XO) / 2 - 10, CHAO - 90), 1.75, pixel=True)
    if t >= 40:
        faixa_nome(q, "MAGNUS", "ARTE FORJADA NO FOGO.", COR_NOME, (t - 40) / 30)


PLANOS_VIDRO = [
    (44, v1_cava, {0: ("terra", 0.4), 20: ("terra", 0.4)}),
    (32, v2_areia, {0: ("terra", 0.6), 14: ("terra", 0.6)}),
    (40, v3_fogo, {6: ("foguete", 0.9)}),
    (48, v4_vira_vidro, {0: ("puf", 0.5), 30: ("confirma", 0.7)}),
    (90, v5_final, {30: ("uivo", 0.5)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_VIDRO, titulo, oponente)
