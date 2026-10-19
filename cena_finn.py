"""CENAS DE ANIME do FINN (loja), com as ideias do Gomes.

ENTRADA (TORNADO DE FOGO): câmera em PRIMEIRA PESSOA no Finn lendo o LIVRO DE MAGIA... ele bate o CAJADO no chão e
sai uma LUZ que cobre a tela... a luz sai, o FOGO cobre a tela... aparece o TORNADO DE FOGO, que fica lá, dá um
"boostzinho" e some... e lá está o Finn FECHANDO e GUARDANDO o livro.
VITÓRIA (TRONO DE PEDRA): bate o cajado no chão, o GOLEM DE PEDRA aparece, vira o TRONO, ele senta... aparece o
DRAGÃOZINHO, pousa no ombro dele, e ele fica fazendo CARINHO no dragãozinho.
O Finn aparece com o desenho do jogo; o golem é o do jogo (ult2), o trono é o da vitória antiga; o livro (de perto),
as mãos, o tornado e o dragãozinho são ilustrados.
"""
import math
import random

import pygame

import cutscene
import finn
from cena_max import fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

BORDA = (18, 12, 26)
XF, XO = LARGURA * 0.34, LARGURA * 0.74  # o Finn e o oponente, no mapa
RUNA = (90, 230, 255)
COR_NOME = (120, 70, 180)
FOGO = ((255, 120, 30), (255, 200, 90))


def pal(c):
    return {k: c.cor(k, v) for k, v in finn.PALETA.items()}


def pose(c, nome):
    if nome == "sentado":
        import vitorias_loja
        return vitorias_loja.p_(c.l, "sentado")
    return c.l.poses.get(nome) or c.l.poses["parado"]


def lendo(c, t):
    """LENDO com uma mão só (o livro na frente do rosto) e a OUTRA PRA TRÁS (nas costas)."""
    p = dict(pose(c, "parado"))
    pc, qd = p["pc"], p["qd"]
    p["ct"], p["mt"] = (qd[0] - 8, qd[1] + 20), (qd[0] - 14, qd[1] + 4)       # (a mão nas costas)
    p["cf"], p["mf"] = (pc[0] + 12, pc[1] - 16), (pc[0] + 22, pc[1] + 2 + math.sin(t * 0.05))  # (o livro na frente)
    return p


def na_torre(c, q, t, centro, zoom, escurece=40):
    """O fundo da TORRE DO MAGO (a casa dele), desfocado — seja qual for o mapa da luta."""
    real = c.cenario_nome
    c.cenario_nome = "TORRE DO MAGO"
    try:
        fundo_desfocado(c, q, t, centro, zoom, escurece)
    finally:
        c.cenario_nome = real


def e2b_guarda(c, q, t, k):
    """2b) Na TORRE (de fora): ele PRENDE o cajado na cintura... e a LUZ do cajado cresce e cobre a tela."""
    w, h = q.get_size()
    base = c._tela_aux()
    real = c.cenario_nome
    c.cenario_nome = "TORRE DO MAGO"
    try:
        c.mapa(base, t + 60)
    finally:
        c.cenario_nome = real
    guarda = t >= 12
    p = pose(c, "f_cajado_b") if t < 12 else misturar(pose(c, "f_cajado_b"), lendo(c, t), suave(min(1, (t - 12) / 8)))
    finn_por(c, base, p, LARGURA * 0.45, cajado=not guarda)
    c.camera(q, base, (LARGURA * 0.45 + 20, CHAO - 110), 2.2, pixel=True)
    if t >= 14:  # a LUZ cobrindo a tela
        u = min(1, (t - 14) / 12)
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(sup, (255, 255, 240, int(255 * min(1, u * 1.4))), (int(w * 0.5), int(h * 0.45)), int(40 + 1100 * u ** 1.5))
        q.blit(sup, (0, 0))
    if 10 <= t < 20:
        texto_pow(q, "click.", (int(w * 0.62), int(h * 0.6)), 36, (240, 240, 250), t - 10)


def finn_por(c, base, p, x, y=CHAO, d=1, cajado=True):
    """O Finn (desenho do jogo). cajado=False: o cajado NÃO fica na mão — fica PRESO NA CINTURA, atravessado
    nas costas (desenhado antes dele, por trás)."""
    if cajado:
        c.por(base, p, 1.0, x, y, d, guardar=False)
        return
    s = c.l.s
    qd, pc = c.ponto(p, "qd", 1.0, x, y, d), c.ponto(p, "pc", 1.0, x, y, d)
    baixo = (qd[0] + 22 * s * d, qd[1] + 18 * s)  # (atravessado: a ponta de baixo pra frente, a bola atrás do ombro)
    cima = (pc[0] - 24 * s * d, pc[1] - 34 * s)
    pygame.draw.line(base, BORDA, baixo, cima, max(3, int(5 * s)))
    pygame.draw.line(base, (130, 84, 44), baixo, cima, max(2, int(3 * s)))
    pk = pal(c)
    pygame.draw.circle(base, BORDA, (int(cima[0]), int(cima[1])), int(6 * s))
    pygame.draw.circle(base, pk["b"], (int(cima[0]), int(cima[1])), int(5 * s))
    original = finn.desenha_cajado
    finn.desenha_cajado = lambda *a, **k: None  # (só nesse desenho: sem o cajado na mão)
    try:
        c.por(base, p, 1.0, x, y, d, guardar=False)
    finally:
        finn.desenha_cajado = original
    pygame.draw.line(base, (226, 186, 70), (qd[0] - 6 * s, qd[1] + 2 * s), (qd[0] + 8 * s, qd[1] + 2 * s), max(2, int(3 * s)))  # a presilha


def livro(q, x, y, e, abre=1.0, ang=0.0, pk=None, t=0):
    """O LIVRO DE FEITIÇOS (capa roxa com o canto dourado; aberto = as páginas com runas brilhando).
    abre: 0 = fechado ... 1 = aberto. (x, y) = o meio da lombada."""
    pk = pk or finn.PALETA
    sup = pygame.Surface((int(70 * e) + 8, int(46 * e) + 8), pygame.SRCALPHA)
    cx, cy = sup.get_width() / 2, sup.get_height() / 2
    larg = 30 * e * (0.15 + 0.85 * abre)
    for lado in (-1, 1):  # as duas metades (a capa e as páginas)
        if abre < 0.05 and lado < 0:
            continue
        r = pygame.Rect(0, 0, larg, 40 * e)
        r.midleft = (cx, cy) if lado > 0 else (cx - larg, cy)
        if lado < 0:
            r.right = cx
        pygame.draw.rect(sup, BORDA, r.inflate(4, 4), border_radius=int(3 * e))
        pygame.draw.rect(sup, pk["v"], r, border_radius=int(3 * e))
        if abre > 0.3:  # as PÁGINAS com as runas
            pg = r.inflate(-4 * e, -4 * e)
            pygame.draw.rect(sup, (240, 228, 196), pg)
            for i in range(5):
                yy = pg.y + 5 * e + i * 6 * e
                pygame.draw.line(sup, (140, 110, 160), (pg.x + 3 * e, yy), (pg.right - 3 * e, yy), max(1, int(e)))
            for i in range(2):
                gx = pg.centerx + math.sin(t * 0.1 + i + lado) * 4 * e
                pygame.draw.circle(sup, RUNA, (int(gx), int(pg.y + 10 * e + i * 14 * e)), max(1, int(2.5 * e)))
        else:
            pygame.draw.rect(sup, pk["o"], (r.right - 7 * e, r.y, 7 * e, 7 * e))  # o canto dourado
            pygame.draw.circle(sup, pk["o"], r.center, max(2, int(5 * e)), max(1, int(e)))
    if ang:
        sup = pygame.transform.rotate(sup, ang)
    q.blit(sup, (int(x - sup.get_width() / 2), int(y - sup.get_height() / 2)))


# =====================================================================
# ENTRADA: TORNADO DE FOGO
# =====================================================================
def maos_livro(c, q, w, h, t, desce=0.0, vira=0.0):
    """PRIMEIRA PESSOA: as mãos (mangas roxas com a barra dourada) segurando o LIVRO aberto de perto.
    desce: o livro abaixando (0..1); vira: a página virando (0..1)."""
    pk = pal(c)
    by = h * 0.62 + desce * h * 0.6
    bx = w * 0.46
    pag = pygame.Rect(0, 0, w * 0.3, h * 0.5)
    for lado in (-1, 1):  # as duas páginas
        r = pag.copy()
        if lado < 0:
            r.topright = (bx, by - h * 0.25)
        else:
            r.topleft = (bx, by - h * 0.25)
        pygame.draw.rect(q, BORDA, r.inflate(16, 16), border_radius=10)
        pygame.draw.rect(q, pk["v"], r.inflate(10, 10), border_radius=8)
        pygame.draw.rect(q, (240, 228, 196), r)
        for i in range(9):  # o texto (linhas) e as RUNAS brilhando
            yy = r.y + 24 + i * 26
            pygame.draw.line(q, (150, 120, 170), (r.x + 22, yy), (r.right - 22 - (i * 37) % 60, yy), 3)
        rx, ry = r.centerx, r.y + r.h * 0.7
        brilho(q, (int(rx), int(ry)), 60, RUNA, 120 + int(60 * math.sin(t * 0.2 + lado)))
        for i in range(6):
            a = t * 0.05 * lado + i * math.tau / 6
            pygame.draw.line(q, RUNA, (rx + math.cos(a) * 18, ry + math.sin(a) * 18), (rx + math.cos(a) * 34, ry + math.sin(a) * 34), 3)
        pygame.draw.circle(q, RUNA, (int(rx), int(ry)), 40, 3)
    if 0 < vira < 1:  # a PÁGINA virando (fica fininha no meio e cai do outro lado)
        larg = pag.w * math.cos(vira * math.pi)
        r = pygame.Rect(0, 0, abs(larg), pag.h)
        if larg >= 0:
            r.topleft = (bx, by - h * 0.25)
        else:
            r.topright = (bx, by - h * 0.25)
        pygame.draw.rect(q, BORDA, r.inflate(4, 4))
        pygame.draw.rect(q, (250, 240, 214), r)
    pygame.draw.line(q, BORDA, (bx, by - h * 0.25), (bx, by - h * 0.25 + pag.h), 6)  # a lombada
    for lado in (-1, 1):  # as MÃOS segurando por baixo e as mangas
        mx = bx + lado * pag.w * 0.85
        manga = [(mx + lado * 40, h + 40), (mx - lado * 120, h + 40), (mx - lado * 50, by + 30), (mx + lado * 60, by + 10)]
        pygame.draw.polygon(q, BORDA, manga)
        pygame.draw.polygon(q, pk["r"], [(px + (mx - px) * 0.05, py + 4) for px, py in manga])
        pygame.draw.line(q, pk["o"], manga[2], manga[3], 10)  # a barra dourada da manga
        pygame.draw.ellipse(q, BORDA, (mx - 46, by - 40, 92, 84))
        pygame.draw.ellipse(q, pk["p"], (mx - 40, by - 34, 80, 72))
        pygame.draw.ellipse(q, pk["P"], (mx - 40, by + 4, 80, 32))
        for j in range(3):  # os dedos por cima da página
            fx = mx - lado * (20 + j * 18)
            pygame.draw.line(q, BORDA, (fx, by - 20), (fx - lado * 10, by - 64), 22)
            pygame.draw.line(q, pk["p"], (fx, by - 20), (fx - lado * 10, by - 64), 15)


def cajado_pov(c, q, w, h, t, bate=0.0):
    """O CAJADO na direita (a mão segurando, a bola roxa em cima). bate: 0..1 (o cajado batendo no chão)."""
    pk = pal(c)
    x = w * 0.84
    topo = h * 0.04 + bate * h * 0.18
    pygame.draw.line(q, BORDA, (x, topo + 60), (x + 30, h + 60), 30)
    pygame.draw.line(q, (130, 84, 44), (x, topo + 60), (x + 30, h + 60), 22)
    pygame.draw.line(q, (170, 116, 64), (x - 5, topo + 60), (x + 25, h + 60), 5)
    pygame.draw.circle(q, BORDA, (int(x), int(topo + 30)), 46)
    pygame.draw.circle(q, pk["b"], (int(x), int(topo + 30)), 40)
    pygame.draw.circle(q, (200, 160, 240), (int(x - 12), int(topo + 18)), 12)
    brilho(q, (int(x), int(topo + 30)), 70, pk["b"], 120)
    my = topo + h * 0.5
    pygame.draw.ellipse(q, BORDA, (x - 44, my - 30, 96, 76))  # a mão no cajado
    pygame.draw.ellipse(q, pk["p"], (x - 38, my - 24, 84, 64))
    for j in range(4):
        pygame.draw.line(q, pk["P"], (x - 30, my - 10 + j * 14), (x + 40, my - 6 + j * 14), 3)


def e1_le(c, q, t, k):
    """1) PRIMEIRA PESSOA, na TORRE dele: o Finn LENDO o livro de magia (as runas brilhando, uma página virando)."""
    w, h = q.get_size()
    na_torre(c, q, t, (LARGURA * 0.35, CHAO - 120), 2.0, 60)
    vira = min(1, max(0, (t - 26) / 14)) if t >= 26 else 0.0
    maos_livro(c, q, w, h, t, vira=vira if vira < 1 else 0)
    cajado_pov(c, q, w, h, t)
    if 6 <= t < 24:
        from efeitos import texto
        texto(q, "...ignis... turbo...", 26, (230, 220, 250), (int(w * 0.46), int(h * 0.12)))


def e2_bate(c, q, t, k):
    """2) Ele SEGURA o cajado (o livro desce) e BATE no chão: TOC! (a bola acende)."""
    w, h = q.get_size()
    na_torre(c, q, t + 40, (LARGURA * 0.35, CHAO - 120), 2.0, 60)
    bate = suave(min(1, max(0, t - 8) / 6))
    maos_livro(c, q, w, h, t, desce=0.5 * suave(min(1, t / 10)))
    cajado_pov(c, q, w, h, t, bate)
    if t == 14:
        c.tremor = 12
    if t >= 14:
        brilho(q, (int(w * 0.84), int(h * 0.04 + h * 0.18 + 30)), 60 + (t - 14) * 10, (255, 255, 240), 220)
        if t < 26:
            texto_pow(q, "TOC!", (int(w * 0.66), int(h * 0.3)), 60, (255, 255, 240), t - 14)


def tornado(q, x, k, t, forca=1.0, pk=None):
    """O TORNADO DE FOGO (espiral de chamas girando, o miolo brilhando, brasas subindo). k = 0..1 (o tamanho)."""
    if k <= 0:
        return
    sup = pygame.Surface(q.get_size(), pygame.SRCALPHA)
    for i in range(16):
        y = CHAO - 6 - i * 14 * k * forca
        r = (14 + i * 6.5) * k * forca
        a = t * 0.55 + i * 0.6
        caixa = pygame.Rect(0, 0, r * 2, max(4, r * 0.45))
        caixa.center = (int(x + math.sin(t * 0.18 + i * 0.5) * i * 1.2), int(y))
        cor = ((255, 236, 140), (255, 160, 40), (230, 70, 20))[i % 3]
        pygame.draw.arc(sup, (*cor, 240), caixa, a, a + 3.4, max(3, int(6 * k)))
        pygame.draw.arc(sup, (*cor, 120), caixa.inflate(10, 4), a + 3.4, a + 5.2, max(2, int(3 * k)))
    q.blit(sup, (0, 0))
    brilho(q, (int(x), int(CHAO - 100 * k * forca)), int(110 * k * forca), (255, 150, 40), int(140 * k))
    rnd = random.Random(t // 2)
    for i in range(10):  # as brasas
        bx = x + rnd.uniform(-60, 60) * k
        by = CHAO - ((t * 4 + i * 23) % int(240 * k * forca + 1))
        pygame.draw.circle(q, (255, 200, 90), (int(bx), int(by)), 2)


def e3_fogo(c, q, t, k):
    """3) A luz sai... e o FOGO cobre a tela."""
    import cena_magnus
    w, h = q.get_size()
    q.fill((255, 255, 240))
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    cena_magnus.fogo_tela(sup, t, min(1, t / 10), {"b": FOGO[0], "B": FOGO[1]})
    q.blit(sup, (0, 0))


TOR_BOOST, TOR_SOME = 34, 50


def e4_tornado(c, q, t, k):
    """4) No MAPA: o fogo da tela se abre... o TORNADO DE FOGO girando, dá um BOOSTZINHO (cresce, FWOOOSH!)...
    e some (vira fumaça), mostrando o Finn lá dentro."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 60)
    c.por_oponente(base, "defesa" if 10 < t < 56 else "parado", 1.0, XO, CHAO)
    if t >= TOR_SOME - 6:
        p = lendo(c, t)
        finn_por(c, base, p, XF, cajado=False)
        mao = c.ponto(p, "mf", 1.0, XF, CHAO)
        livro(base, mao[0] + 4, mao[1] - 4, 0.8, 1.0, 0, pal(c), t)
    if t < TOR_BOOST:
        k_ = min(1, t / 10)
        forca = 1.0
    elif t < TOR_SOME:
        u = (t - TOR_BOOST) / (TOR_SOME - TOR_BOOST)
        k_, forca = 1.0, 1.0 + 0.5 * math.sin(u * math.pi)  # o BOOSTZINHO
    else:
        k_, forca = max(0, 1 - (t - TOR_SOME) / 12), 1.0
    tornado(base, XF, k_, t, forca)
    if t >= TOR_SOME:  # a FUMAÇA de quando some
        poeira(base, XF, CHAO, min(1, (t - TOR_SOME) / 24), cor=(120, 110, 120), larg=110, semente=4)
    c.mapa_frente(base, t + 60)
    c.camera(q, base, (XF + 110, CHAO - 150), 1.35, pixel=True)
    if t < 8:  # (o fogo da tela se abrindo)
        import cena_magnus
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        cena_magnus.fogo_tela(sup, t, 1 - t / 8, {"b": FOGO[0], "B": FOGO[1]})
        q.blit(sup, (0, 0))
    if TOR_BOOST <= t < TOR_SOME:
        c.tremor = max(c.tremor, 5)
        texto_pow(q, "FWOOOOSH!!", (int(w * 0.66), int(h * 0.24)), 66, FOGO[1], (t - TOR_BOOST) % 8, giro=0.08)


def e5_lendo(c, q, t, k):
    """5) Ele continua LENDO, tranquilo, com uma mão só e a outra nas costas (vira uma página). O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 130)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    p = lendo(c, t)
    finn_por(c, base, p, XF, cajado=False)
    mao = c.ponto(p, "mf", 1.0, XF, CHAO)
    vira = 1.0 if not 20 <= t < 30 else abs(math.cos((t - 20) / 10 * math.pi))  # (a página virando)
    livro(base, mao[0] + 4, mao[1] - 4, 0.8, vira, 0, pal(c), t)
    c.mapa_frente(base, t + 130)
    c.camera(q, base, (XF + 30, CHAO - 125), 2.2 - 0.3 * suave(min(1, t / 50)), pixel=True)
    if t >= 34:
        faixa_nome(q, "FINN", "O MAGO DO FOGO.", COR_NOME, (t - 34) / 30)


PLANOS = [
    (50, e1_le, {26: ("vento", 0.2)}),
    (28, e2_bate, {14: ("terra", 0.6), 16: ("carga", 0.7)}),
    (30, e2b_guarda, {10: ("defesa", 0.4)}),
    (16, e3_fogo, {0: ("foguete", 0.9)}),
    (70, e4_tornado, {0: ("vento", 0.8), TOR_BOOST: ("foguete", 1.0), TOR_SOME: ("puf", 0.7)}),
    (76, e5_lendo, {20: ("vento", 0.2)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: TRONO DE PEDRA (o golem vira o trono, e o DRAGÃOZINHO)
# =====================================================================
DRAGAO, DRAGAO_ESC, DRAGAO_BARRIGA = (220, 96, 56), (160, 58, 36), (250, 210, 140)


def dragaozinho(q, x, y, e, t, d=1, voando=True, feliz=0.0):
    """O DRAGÃOZINHO de estimação do Finn: corpinho laranja-avermelhado, barriga clara, cabeção com dois chifrinhos,
    olhão, asinhas de morcego (batendo), rabinho com a pontinha de chama. (x, y) = o pé. feliz: os olhinhos fechados."""
    def P(px, py):
        return x + px * e * d, y - py * e
    asa = math.sin(t * (0.9 if voando else 0.25)) * (1.0 if voando else 0.3)
    for lado in (1, -1):  # as ASINHAS (a de trás mais escura)
        cor = DRAGAO_ESC if lado < 0 else DRAGAO
        base_a = P(-2 + lado, 13)
        ponta = P(-10 - lado * 2, 22 + 9 * asa)
        meio = P(-14, 14 + 4 * asa)
        pygame.draw.polygon(q, BORDA, [base_a, ponta, meio, P(-6, 10)])
        pygame.draw.polygon(q, cor, [base_a, ponta, meio, P(-6, 10)], 0)
    cauda = [P(-6, 6), P(-12, 4), P(-16, 7), P(-18, 11)]  # o rabinho com a chama
    pygame.draw.lines(q, BORDA, False, cauda, max(2, int(3 * e)))
    pygame.draw.lines(q, DRAGAO, False, cauda, max(1, int(2 * e)))
    brilho(q, (int(cauda[-1][0]), int(cauda[-1][1])), int(4 * e) + 1, (255, 170, 60), 220)
    corpo = pygame.Rect(0, 0, 14 * e, 12 * e)
    corpo.center = (int(P(-2, 8)[0]), int(P(-2, 8)[1]))
    pygame.draw.ellipse(q, BORDA, corpo.inflate(3, 3))
    pygame.draw.ellipse(q, DRAGAO, corpo)
    pygame.draw.ellipse(q, DRAGAO_BARRIGA, corpo.inflate(-5 * e, -4 * e).move(int(2 * e * d), int(1 * e)))
    for px in (-5, 1):  # as perninhas
        pygame.draw.line(q, BORDA, P(px, 3), P(px, 0), max(2, int(2.4 * e)))
    cab = P(5, 16)  # a CABEÇA (grande, fofa)
    pygame.draw.circle(q, BORDA, (int(cab[0]), int(cab[1])), int(7 * e))
    pygame.draw.circle(q, DRAGAO, (int(cab[0]), int(cab[1])), int(6 * e))
    pygame.draw.ellipse(q, DRAGAO, (*P(8 if d > 0 else 14, 16), 6 * e, 5 * e))  # o focinho
    for i, px in enumerate((2, 6)):  # os chifrinhos
        pygame.draw.polygon(q, (250, 230, 190), [P(px, 21), P(px + 1.5, 21), P(px - 1, 25 + i)])
    olho = P(7, 17)
    if feliz > 0.5:  # (^ ^ de contente)
        pygame.draw.arc(q, BORDA, (olho[0] - 2.5 * e, olho[1] - 1 * e, 5 * e, 4 * e), 0.3, math.pi - 0.3, max(1, int(e)))
    else:
        pygame.draw.circle(q, BORDA, (int(olho[0]), int(olho[1])), max(2, int(2.2 * e)))
        pygame.draw.circle(q, (255, 255, 255), (int(olho[0] - 0.6 * e * d), int(olho[1] - 0.8 * e)), max(1, int(0.8 * e)))
    pygame.draw.circle(q, (250, 140, 130), (int(P(6, 14)[0]), int(P(6, 14)[1])), max(1, int(1.4 * e)))  # a bochecha


def bate_cajado(c, base, t, x):
    """Bate o cajado no chão: o CÍRCULO DE RUNAS acende."""
    p = pose(c, "f_cajado_a" if t < 5 else "f_cajado_b")
    finn_por(c, base, p, x)
    if t >= 5:
        k = min(1, (t - 5) / 8)
        caixa = pygame.Rect(0, 0, 160 * k, 36 * k)
        caixa.center = (int(x + 90), CHAO)
        brilho(base, caixa.center, int(80 * k) + 1, RUNA, 120)
        pygame.draw.ellipse(base, RUNA, caixa, 2)
        for i in range(8):
            a = t * 0.08 + i * math.tau / 8
            px, py = caixa.centerx + math.cos(a) * caixa.w * 0.42, caixa.centery + math.sin(a) * caixa.h * 0.42
            pygame.draw.line(base, (220, 250, 255), (px - 3, py - 2), (px + 3, py + 2), 2)


XG = XF + 140  # onde o golem sai (e o trono fica)


def golem(c, base, x, afunda, acao, u):
    """O GOLEM DE PEDRA do jogo (o desenho do ult2), em x, afundando (0 = em pé ... 1 = dentro da terra)."""
    import ult2
    l = c.lutador()
    l.extra["golem_acao"] = (acao, u)
    l.extra["golem"] = 999
    l.x, l.dir = x - 40, 1
    clip = base.get_clip()
    base.set_clip((0, 0, LARGURA, CHAO + 4))
    ult2.desenha_golem(l, base, x, afunda)
    base.set_clip(clip)


def trono(c, base, x, sobe, aceso):
    """O TRONO DE PEDRA (o da vitória antiga), subindo da terra (sobe 0..1); aceso = as runas acesas."""
    import vitorias_loja
    l = c.lutador()
    l.x, l.dir, l.s = x + 6 * c.l.s, 1, c.l.s
    t_fake = vitorias_loja.TRONO_SOBE + int(20 * sobe) if sobe < 1 else (vitorias_loja.TRONO_SENTA + 1 if aceso else 30)
    vitorias_loja.finn_trono_atras(l, base, t_fake)


def v1_cajado(c, q, t, k):
    """1) Do lado do derrotado: bate o CAJADO no chão (TOC!) e o círculo de runas acende."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO + 20, CHAO)
    bate_cajado(c, base, t, XF)
    c.mapa_frente(base, t)
    c.camera(q, base, (XF + 70, CHAO - 100), 2.0, pixel=True)
    if t == 5:
        c.tremor = 8
    if 5 <= t < 18:
        texto_pow(q, "TOC!", (int(w * 0.36), int(h * 0.26)), 56, (240, 240, 255), t - 5)


def v2_golem(c, q, t, k):
    """2) O GOLEM DE PEDRA sai da terra (o chão tremendo, as pedras caindo dele)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 30)
    c.por_oponente(base, "caido", 1.0, XO + 20, CHAO)
    finn_por(c, base, pose(c, "parado"), XF)
    sai = suave(min(1, t / 26))
    golem(c, base, XG, 1 - sai, "sobe", t)
    if t < 30:
        poeira(base, XG, CHAO, min(1, t / 30), cor=(150, 140, 126), larg=120, semente=7)
        c.tremor = max(c.tremor, 4)
    c.mapa_frente(base, t + 30)
    c.camera(q, base, (XG - 20, CHAO - 120), 1.7, pixel=True)
    if t >= 30:
        texto_pow(q, "GROOOM...", (int(w * 0.7), int(h * 0.24)), 46, (200, 190, 170), (t - 30) % 10, giro=0.06)


def v3_trono(c, q, t, k):
    """3) O golem BRILHA... se desmancha pra dentro da terra... e o TRONO sobe no lugar dele."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 80)
    c.por_oponente(base, "caido", 1.0, XO + 20, CHAO)
    finn_por(c, base, pose(c, "parado"), XF)
    muda = 12
    if t < muda + 10:
        golem(c, base, XG, suave(max(0, (t - muda) / 10)), "sobe", 99)
        if t >= 4:
            brilho(base, (int(XG), int(CHAO - 80)), int(60 + t * 4), RUNA, min(220, t * 14))
    if t >= muda:
        trono(c, base, XG, suave(min(1, (t - muda) / 18)), False)
    if t == muda:
        c.inverte, c.tremor = 2, 10
    c.mapa_frente(base, t + 80)
    c.camera(q, base, (XG - 20, CHAO - 120), 1.7, pixel=True)


def v4_senta(c, q, t, k):
    """4) Ele SENTA no trono (as runas do trono acendem)."""
    base = c._tela_aux()
    c.mapa(base, t + 120)
    c.por_oponente(base, "caido", 1.0, XO + 20, CHAO)
    trono(c, base, XG, 1.0, t > 16)
    u = suave(min(1, t / 16))
    x = XF + (XG - XF) * u
    y = CHAO - 30 * c.l.s * u - math.sin(u * math.pi) * 20
    finn_por(c, base, misturar(pose(c, "parado"), pose(c, "sentado"), u), x, y)
    c.mapa_frente(base, t + 120)
    c.camera(q, base, (XG + 20, CHAO - 110), 1.8, pixel=True)


def sentado_carinho(c, t, faz):
    """A pose SENTADO com a mão da frente fazendo CARINHO no dragãozinho do ombro (vai e volta)."""
    p = dict(pose(c, "sentado"))
    if faz:
        pc = p["pc"]
        a = math.radians(70 + 14 * math.sin(t * 0.25))
        p["cf"] = (pc[0] + 10, pc[1] - 4)
        p["mf"] = (pc[0] + 10 + math.cos(a) * 18, pc[1] - 4 + math.sin(a) * 18)
    return p


def v5_dragao(c, q, t, k):
    """5) O DRAGÃOZINHO chega voando (batendo as asinhas) e POUSA no ombro dele."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 140)
    c.por_oponente(base, "caido", 1.0, XO + 20, CHAO)
    trono(c, base, XG, 1.0, True)
    y = CHAO - 30 * c.l.s
    p = pose(c, "sentado")
    finn_por(c, base, p, XG, y)
    ombro = c.ponto(p, "pc", 1.0, XG, y)
    u = suave(min(1, t / 34))
    dx = ombro[0] + 6 + (LARGURA + 60 - ombro[0]) * (1 - u)
    dy = ombro[1] - 2 - 140 * (1 - u) + math.sin(t * 0.4) * 10 * (1 - u)
    dragaozinho(base, dx, dy, 1.6, t, d=-1, voando=u < 1)
    c.mapa_frente(base, t + 140)
    c.camera(q, base, ((XG + ombro[0]) / 2 + 60 * (1 - u), ombro[1] + 20), 2.4, pixel=True)
    if u >= 1 and t < 46:
        texto_pow(q, "pi!", (int(w * 0.62), int(h * 0.3)), 40, (255, 230, 200), t - 34)


def v6_carinho(c, q, t, k):
    """6) Ele fica fazendo CARINHO no dragãozinho (que fecha os olhinhos de contente e solta fumacinha). O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 180)
    c.por_oponente(base, "caido", 1.0, XO + 20, CHAO)
    trono(c, base, XG, 1.0, True)
    y = CHAO - 30 * c.l.s
    p = sentado_carinho(c, t, True)
    ombro = c.ponto(p, "pc", 1.0, XG, y)
    finn_por(c, base, p, XG, y)
    dragaozinho(base, ombro[0] + 6, ombro[1] - 2, 1.6, t, d=-1, voando=False, feliz=1.0 if (t // 30) % 3 else 0.0)
    if t % 40 < 16:  # a fumacinha do nariz (de contente)
        v = t % 40
        sup = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(sup, (220, 220, 230, max(0, 180 - v * 11)), (20, 20), int(3 + v * 0.5))
        base.blit(sup, (ombro[0] - 6 - v - 20, ombro[1] - 18 - v * 0.6 - 20))
    c.mapa_frente(base, t + 180)
    centro, z = (ombro[0] + 10, ombro[1] + 30), 2.2 - 0.4 * suave(min(1, t / 60))
    c.camera(q, base, centro, z, pixel=True)
    for i in range(3):  # coraçõezinhos subindo
        u = ((t * 0.02) + i / 3) % 1
        hx, hy = para_tela(centro, z, (ombro[0] + (i - 1) * 10, ombro[1] - 20 - u * 40))
        r = 6 + 4 * (1 - u)
        pygame.draw.circle(q, (240, 90, 120), (int(hx - r * 0.5), int(hy)), int(r * 0.6))
        pygame.draw.circle(q, (240, 90, 120), (int(hx + r * 0.5), int(hy)), int(r * 0.6))
        pygame.draw.polygon(q, (240, 90, 120), [(hx - r, hy + 1), (hx + r, hy + 1), (hx, hy + r * 1.2)])
    if t >= 40:
        faixa_nome(q, "FINN", "O ARQUIMAGO.", COR_NOME, (t - 40) / 30)


PLANOS_TRONO = [
    (30, v1_cajado, {5: ("terra", 0.7), 7: ("carga", 0.5)}),
    (44, v2_golem, {0: ("terra", 0.9), 20: ("queda", 0.5)}),
    (40, v3_trono, {4: ("carga", 0.6), 12: ("terra", 0.8)}),
    (24, v4_senta, {16: ("confirma", 0.5)}),
    (50, v5_dragao, {0: ("vento", 0.4), 34: ("blip", 0.5)}),
    (100, v6_carinho, {}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_TRONO, titulo, oponente)
