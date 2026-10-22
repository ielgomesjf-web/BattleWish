"""CENAS DE ANIME do NOCTURNUS (loja, escolhas do Gomes): a entrada ECO NO ESCURO e a vitória PENDURADO NA LUA.

Tudo no MAPA da luta, com a SKIN dele e o OPONENTE de verdade, na escala do jogo e ampliado SEM borrar (pixel art).
O close do ROSTO é desenhado pequeno (1 pixel = 1 quadradinho) e ampliado, igual o resto do jogo.
"""
import math
import random

import pygame

import nocturnus
from cena_sphyrus import noite
from cenas_anime import CenaAnime, faixa_nome, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave

BORDA = (14, 10, 20)
XN, XO = LARGURA * 0.30, LARGURA * 0.70  # o Nocturnus e o oponente, no mapa
SONAR = (110, 200, 255)
COR_NOME = (110, 60, 160)


def pal(c):
    return {k: c.cor(k, v) for k, v in nocturnus.PALETA.items()}


def pose(c, nome):
    return c.l.poses.get(nome) or c.l.poses["parado"]


# =====================================================================
# o SONAR: a visão de eco (anéis azuis que mostram o mundo só onde passam)
# =====================================================================
def visao_eco(c, t, opo="parado"):
    """O mapa + o oponente pintados de AZUL ESCURO (o que o eco 'enxerga'), e o contorno do oponente."""
    if not hasattr(c, "_visao"):
        c._visao = pygame.Surface((LARGURA, ALTURA))
    v = c._visao
    c.mapa(v, t)
    c.por_oponente(v, opo, 1.0, XO, CHAO)
    c.mapa_frente(v, t)
    v.fill((70, 150, 255), special_flags=pygame.BLEND_RGB_MULT)  # (tudo AZUL e mais claro: o que o eco enxerga)
    v.fill((20, 50, 110), special_flags=pygame.BLEND_RGB_ADD)
    return v


def contorno_oponente(c, q, opo, cor, larg=2):
    """Só a BORDA do oponente (a silhueta que o eco desenha)."""
    chave = ("contorno", opo)
    if chave not in c._cache:
        sup = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        c.por_oponente(sup, opo, 1.0, XO, CHAO)
        pts = pygame.mask.from_surface(sup).outline()
        c._cache[chave] = pts
    pts = c._cache[chave]
    if len(pts) > 2:
        pygame.draw.lines(q, cor, True, pts, larg)


def aneis(q, visao, centro, t, nasce, vel=9, banda=26):
    """Cada anel nasce num quadro de 'nasce', cresce, e onde ele PASSA aparece a visão de eco."""
    for t0 in nasce:
        u = t - t0
        if u < 0:
            continue
        r = u * vel
        if r > 1300:
            continue
        anel = pygame.Surface(q.get_size(), pygame.SRCALPHA)
        some = max(0.0, 1 - r / 1300)
        for i in range(banda // 2):  # (a banda: forte na frente, apagando pra trás — em degraus, sem borrar)
            a = int(255 * some * (1 - i / (banda / 2)))
            if r - i * 2 > 0:
                pygame.draw.circle(anel, (255, 255, 255, a), (int(centro[0]), int(centro[1])), int(r - i * 2), 2)
        anel.blit(visao, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        q.blit(anel, (0, 0))
        pygame.draw.circle(q, SONAR, (int(centro[0]), int(centro[1])), int(r), 2)  # a frente do anel


def pixelado(q, peq, zoom, centro):
    """Amplia a superfície pequena sem borrar e põe centrada."""
    g = pygame.transform.scale(peq, (peq.get_width() * zoom, peq.get_height() * zoom))
    q.blit(g, (int(centro[0] - g.get_width() / 2), int(centro[1] - g.get_height() / 2)))


# =====================================================================
# ENTRADA: ECO NO ESCURO
# =====================================================================
def e1_escuro(c, q, t, k):
    """1) TELA PRETA. ...pi. Um anel de sonar sai do escuro e, por onde passa, desenha o mapa e o oponente em azul."""
    w, h = q.get_size()
    q.fill((0, 0, 0))
    v = visao_eco(c, t)
    aneis(q, v, (XN, CHAO - 80), t, (14, 40))
    for t0 in (14, 40):
        u = t - t0
        if 0 <= u and abs(u * 9 - abs(XO - XN)) < 140:  # o anel passou por ele: a silhueta acende
            contorno_oponente(c, q, "parado", SONAR)
    if 14 <= t < 30:
        texto_pow(q, "...pi.", (int(w * 0.22), int(h * 0.24)), 28, SONAR, t - 14, giro=0.05)
    if 40 <= t < 56:
        texto_pow(q, "pi.", (int(w * 0.3), int(h * 0.3)), 28, SONAR, t - 40, giro=-0.05)


def e2_procura(c, q, t, k):
    """2) Perto do oponente, no escuro: os anéis passando cada vez mais rápido... ele olha pros lados. ?!"""
    w, h = q.get_size()
    base = c._tela_aux()
    base.fill((0, 0, 0))
    opo = "defesa" if t > 30 else "parado"
    v = visao_eco(c, t + 60, opo)
    aneis(base, v, (XN, CHAO - 80), t, (0, 12, 22, 30, 36, 41), vel=12)
    for t0 in (0, 12, 22, 30, 36, 41):
        u = t - t0
        if 0 <= u and abs(u * 12 - abs(XO - XN)) < 120:
            contorno_oponente(c, base, opo, SONAR)
    c.camera(q, base, (XO, CHAO - 100), 1.9, pixel=True)
    if t > 10:
        texto_pow(q, "?!" if t > 30 else "?", (int(w * 0.62), int(h * 0.24)), 70, (220, 230, 255), (t - 10) % 30)


def e3_olhos(c, q, t, k):
    """3) Silêncio. Tudo preto... e dois olhinhos azuis ABREM no escuro, atrás dele."""
    w, h = q.get_size()
    q.fill((0, 0, 0))
    abre = suave(min(1.0, max(0.0, (t - 12) / 6)))
    if abre > 0:
        peq = pygame.Surface((40, 12), pygame.SRCALPHA)
        e = pal(c)["e"]
        for cx in (11, 29):  # (os olhos bravos, puxados pra cima: em pixel)
            alto = max(1, int(5 * abre))
            pygame.draw.polygon(peq, e, [(cx - 5, 6 - alto // 2 + 1), (cx + 5, 6 - alto // 2 - 1),
                                         (cx + 4, 6 + alto // 2), (cx - 4, 6 + alto // 2)])
            peq.set_at((cx - 2, 6 - alto // 2 + 1), (255, 255, 255))
        pixelado(q, peq, 9, (w * 0.5, h * 0.46))
    if t == 18:
        c.tremor = 4


def rosto(c, abre_boca, t):
    """O ROSTO DELE DE FRENTE em PIXEL ART (pequeno: 72 x 56; quem chama amplia): as orelhonas ovais com os
    aparelhos azuis (a da direita CORTADA em cima), as marcas vermelhas, os olhos acesos e as presas."""
    p = pal(c)
    sup = pygame.Surface((72, 56), pygame.SRCALPHA)

    def oval(cx, cy, rx, ry, ang, corte=None):
        pts = []
        for i in range(28):
            a = i / 28 * math.tau
            x, y = math.cos(a) * rx, math.sin(a) * ry
            px, py = cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)
            if corte is not None:
                py = max(py, corte)
            pts.append((px, py))
        return pts

    for lado in (-1, 1):  # as ORELHONAS
        cx, cy, ang = 36 + lado * 22, 18, lado * 0.35
        corte = 6 if lado > 0 else None  # (a orelha CORTADA pelos cientistas)
        fora = oval(cx, cy, 10, 18, ang, corte)
        pygame.draw.polygon(sup, BORDA, oval(cx, cy, 11, 19, ang, None if corte is None else corte - 1))
        pygame.draw.polygon(sup, p["p"], fora)
        pygame.draw.polygon(sup, p["m"], oval(cx, cy + 2, 6, 13, ang, corte))  # (o miolo da orelha)
        if corte is not None:  # o corte em zigue-zague
            for i in range(-6, 7, 3):
                sup.set_at((int(cx + i), corte), BORDA)
                sup.set_at((int(cx + i + 1), corte + 1), BORDA)
        ax, ay = cx - lado * 1, cy + 6  # o APARELHO (a caixinha de som azul)
        pygame.draw.circle(sup, BORDA, (int(ax), int(ay)), 6)
        pygame.draw.circle(sup, p["b"], (int(ax), int(ay)), 5)
        pygame.draw.circle(sup, p["B"], (int(ax), int(ay)), 3)
        pygame.draw.circle(sup, BORDA, (int(ax), int(ay)), 1)
        if (t // 6) % 2:
            sup.set_at((int(ax + 2), int(ay - 3)), (255, 255, 255))
    # a CABEÇA
    pygame.draw.ellipse(sup, BORDA, (18, 16, 36, 36))
    pygame.draw.ellipse(sup, p["p"], (19, 17, 34, 34))
    pygame.draw.ellipse(sup, p["P"], (24, 18, 24, 10))
    pygame.draw.ellipse(sup, p["f"], (26, 34, 20, 15))  # o focinho
    for lado in (-1, 1):  # as MARCAS VERMELHAS (por cima dos olhos e na testa)
        pygame.draw.line(sup, p["r"], (36 + lado * 3, 21), (36 + lado * 8, 23))
        pygame.draw.line(sup, p["r"], (36 + lado * 11, 26), (36 + lado * 13, 30))
    sup.set_at((36, 20), p["r"])
    sup.set_at((36, 21), p["r"])
    for lado in (-1, 1):  # os OLHOS (bravos, acesos)
        ex = 36 + lado * 8
        pygame.draw.polygon(sup, BORDA, [(ex - 5, 27 - lado), (ex + 5, 27 + lado), (ex + 4, 32), (ex - 4, 32)])
        pygame.draw.polygon(sup, p["e"], [(ex - 4, 28 - lado), (ex + 4, 28 + lado), (ex + 3, 31), (ex - 3, 31)])
        sup.set_at((ex - lado, 29), (255, 255, 255))
    sup.set_at((34, 37), BORDA)  # o nariz
    sup.set_at((38, 37), BORDA)
    boca = int(2 + 7 * abre_boca)
    pygame.draw.ellipse(sup, BORDA, (29, 40, 14, boca + 2))
    if abre_boca > 0.2:
        pygame.draw.ellipse(sup, (120, 30, 50), (31, 42, 10, boca - 1))
    for lado in (-1, 1):  # as PRESAS
        fx = 36 + lado * 4
        pygame.draw.polygon(sup, p["w"], [(fx - 1, 41), (fx + 1, 41), (fx, 44 + int(abre_boca * 2))])
    pygame.draw.rect(sup, BORDA, (30, 50, 12, 3))  # o começo do peito (o código de barras)
    for i in range(5):
        sup.set_at((31 + i * 2, 51), p["c"])
    return sup


def e4_susto(c, q, t, k):
    """4) O ROSTO DELE COLADO NA CÂMERA: SKREEEE!! (as ondas de som saindo, a tela tremendo)."""
    w, h = q.get_size()
    q.fill((6, 4, 12))
    boca = suave(min(1.0, t / 5))
    for i in range(4):  # as ONDAS DE SOM (anéis duros) saindo da boca
        r = ((t * 22 + i * 90) % 520)
        pygame.draw.circle(q, SONAR, (int(w * 0.5), int(h * 0.62)), int(r), 6)
    img = c.tingir(rosto(c, boca, t))
    pixelado(q, img, 9 + (1 if t < 3 else 0), (w * 0.5, h * 0.48))
    if t == 0:
        c.inverte, c.tremor = 3, 24
    elif t % 3 == 0:
        c.tremor = max(c.tremor, 10)
    texto_pow(q, "SKREEEE!!", (int(w * 0.5), int(h * 0.15)), 70, SONAR, t % 8, giro=0.06)


def e5_luz(c, q, t, k):
    """5) A luz volta: ele está ali no mapa, de asas abertas, os anéis ainda saindo das orelhas. O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 200)
    c.por_oponente(base, "defesa" if t < 30 else "parado", 1.0, XO, CHAO)
    p = misturar(pose(c, "n_chama"), pose(c, "n_ri"), suave(min(1, max(0, t - 40) / 14)))
    c.por(base, p, 1.0, XN, CHAO, guardar=False)
    cb = c.ponto(p, "cb", 1.0, XN, CHAO)
    for i in range(2):  # o eco ainda saindo das orelhas
        r = (t * 3 + i * 30) % 60
        if r > 8:
            pygame.draw.arc(base, SONAR, (cb[0] - r, cb[1] - r, 2 * r, 2 * r), -0.7, 0.7, 1)
    c.mapa_frente(base, t + 200)
    noite(base, 0.35 * (1 - min(1, t / 20)))
    c.camera(q, base, (XN + 110, CHAO - 120), 1.7, pixel=True)
    if t >= 16:
        faixa_nome(q, "NOCTURNUS", "O ECO NO ESCURO.", COR_NOME, (t - 16) / 30)


PLANOS = [
    (66, e1_escuro, {14: ("blip", 0.4), 40: ("blip", 0.4)}),
    (50, e2_procura, {0: ("blip", 0.4), 12: ("blip", 0.45), 22: ("blip", 0.5), 30: ("blip", 0.55), 36: ("blip", 0.6),
                      41: ("blip", 0.7)}),
    (34, e3_olhos, {14: ("vento", 0.3)}),
    (40, e4_susto, {0: ("uivo", 1.0), 1: ("explosao", 0.5)}),
    (86, e5_luz, {0: ("puf", 0.6)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: PENDURADO NA LUA
# =====================================================================
def ceu_lua(q, t, lx, ly, r):
    """O céu da noite com a LUA CHEIA grandona (crateras) — em pixel, na escala do jogo."""
    q.fill((14, 12, 34))
    rnd = random.Random(4)
    for _ in range(90):  # estrelas
        x, y = rnd.uniform(0, LARGURA), rnd.uniform(0, ALTURA)
        if (t // 10 + int(x)) % 7:
            q.set_at((int(x), int(y)), (200, 200, 240))
    for i, cor in enumerate(((40, 38, 70), (60, 58, 96))):  # o halo em degraus
        pygame.draw.circle(q, cor, (int(lx), int(ly)), int(r * (1.5 - i * 0.22)))
    pygame.draw.circle(q, (236, 232, 200), (int(lx), int(ly)), int(r))
    for dx, dy, rr in ((-0.3, -0.2, 0.2), (0.25, 0.1, 0.14), (-0.05, 0.4, 0.12), (0.4, -0.35, 0.08)):  # crateras
        pygame.draw.circle(q, (204, 198, 168), (int(lx + dx * r), int(ly + dy * r)), int(rr * r))


def galho(q, x0, y, x1, grosso=10):
    """O GALHO seco (silhueta escura) atravessando a lua."""
    pts = [(x0, y + 6), (x0 + (x1 - x0) * 0.4, y), (x1, y - 8)]
    pygame.draw.lines(q, (10, 8, 16), False, pts, grosso)
    for i in range(4):  # os galhinhos
        bx = x0 + (x1 - x0) * (0.2 + i * 0.2)
        pygame.draw.line(q, (10, 8, 16), (bx, y + 2), (bx + 18, y - 22 + (i % 2) * 30), 4)


def bater_asas(c, t, vel=0.42):
    """A pose VOANDO DEITADO (a barriga pra baixo, quem chama gira -90: a cabeça vai pra frente): as asas sobem e
    descem de verdade em volta do ombro, as pernas esticadas pra trás balançando. Devolve (pose, quanto o corpo sobe)."""
    k = 0.5 + 0.5 * math.sin(t * vel)       # 0 = asa lá EMBAIXO, 1 = asa lá EM CIMA
    fi = math.radians(165 - 145 * k)         # (o ângulo da asa: 0 = pra cima no mundo, 90 = pra frente, 180 = pra baixo)
    ox, oy = 6, 76                           # o ombro
    def braco(comp, dobra, dy):
        ux, uy = -math.cos(fi), math.sin(fi)
        cot = (ox + ux * comp * 0.5 + uy * dobra, oy + dy + uy * comp * 0.5 - ux * dobra)
        mao = (ox + ux * comp, oy + dy + uy * comp)
        return cot, mao
    ct, mt = braco(34, 4, -3)
    cf, mf = braco(38, 5, 3)
    perna = math.sin(t * vel + 1.2) * 3
    p = dict(pt=(-3 + perna, 2), jt=(-1, 24), pf=(4 - perna, 4), jf=(5, 25), qd=(0, 46), pc=(4, 76), cb=(10, 92),
             ct=ct, mt=mt, cf=cf, mf=mf)
    return p, math.cos(t * vel) * 6  # (desce a asa = o corpo sobe)


DEITADO = -82  # (o giro do corpo voando: deitado, a cabeça um pouquinho pra cima)


def pendurado(c, t):
    """A pose PENDURADO respirando: o peito sobe e desce, a cabeça olha pros lados, os braços se ajeitam."""
    pd = pose(c, "n_pendura")
    resp = math.sin(t * 0.09)
    olha = math.sin(t * 0.04) * 3
    return dict(pd, pc=(pd["pc"][0], pd["pc"][1] + resp * 1.5), cb=(pd["cb"][0] + olha, pd["cb"][1] + resp * 2),
                mt=(pd["mt"][0] + resp, pd["mt"][1] + resp * 2), mf=(pd["mf"][0] - resp, pd["mf"][1] + resp * 2))


def ele(c, q, p, x, y, t, escala=1.0, ang=0.0, capa=None, sombra=None):
    """Põe ELE (o desenho do jogo, com a CAUDA balançando de verdade) com os pés em (x, y), girado ang graus em
    volta dos pés (180 = de ponta-cabeça). capa = quadro da 'vitória' (fecha as asas feito capa)."""
    l = c.lutador()
    l.t = t
    l.estado = "vitoria" if capa is not None else "parado"
    if capa is not None:
        l.t = capa
    img, (px, py) = c.corpo(p, escala, guardar=False)
    l.estado = "parado"
    if sombra:
        img = img.copy()
        img.fill((*sombra, 255), special_flags=pygame.BLEND_RGBA_MULT)
    if ang:
        cx, cy = img.get_width() / 2, img.get_height() / 2
        vx, vy = px - cx, py - cy
        img = pygame.transform.rotate(img, ang)
        a = math.radians(ang)
        px = img.get_width() / 2 + vx * math.cos(a) + vy * math.sin(a)
        py = img.get_height() / 2 - vx * math.sin(a) + vy * math.cos(a)
    q.blit(img, (int(x - px), int(y - py)))


def v1_decola(c, q, t, k):
    """1) No MAPA, de noite: o derrotado no chão. Ele abre as asas e DECOLA batendo as asas (a poeira levanta)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    if t < 14:  # agacha e abre as asas
        p = misturar(pose(c, "parado"), bater_asas(c, 0)[0], suave(t / 14))
        ele(c, base, p, XN, CHAO, t)
    else:  # sobe batendo as asas e vai DEITANDO, saindo pro lado
        u = t - 14
        p, sobe = bater_asas(c, u)
        deita = suave(min(1, u / 14))
        ele(c, base, p, XN + u * u * 0.3, CHAO - u * 6 - sobe, t, ang=DEITADO * deita)
    if t >= 14:
        for i in range(8):  # a poeira de cada batida
            a = i / 8 * math.pi
            r = 10 + (t - 14) * 5
            pygame.draw.rect(base, (120, 110, 130), (XN + math.cos(a) * r * 1.6 - 2, CHAO - math.sin(a) * r * 0.2 - 2, 4, 4))
    c.mapa_frente(base, t)
    noite(base, 0.5, (40, 40, 120))
    c.camera(q, base, (XN + 60, CHAO - 120), 1.6, pixel=True)
    if 14 <= t < 28:
        texto_pow(q, "FLAP!", (int(w * 0.3), int(h * 0.3)), 52, (220, 210, 255), t - 14)


def v2_lua(c, q, t, k):
    """2) A LUA CHEIA enorme: a SILHUETA dele passa voando na frente, batendo as asas (sozinho: ele sabe voar)."""
    base = c._tela_aux()
    ceu_lua(base, t, LARGURA * 0.5, ALTURA * 0.5, 170)
    x = -100 + (LARGURA + 200) * k
    p, sobe = bater_asas(c, t, 0.5)
    y = ALTURA * 0.5 + 80 + math.sin(k * math.pi * 2) * 24 - sobe
    ele(c, base, p, x - 90, y - 60, t, 1.2, ang=DEITADO + math.sin(t * 0.42) * 4, sombra=(10, 8, 16))
    c.camera(q, base, (LARGURA * 0.5, ALTURA * 0.5), 1.15, pixel=True)


GIRA = (14, 26)  # (no PLANO 3: chega no galho, gira de ponta-cabeça)


def v3_pendura(c, q, t, k):
    """3) Chega voando no GALHO na frente da lua, agarra com os pés, GIRA de ponta-cabeça, balança... e se enrola
    nas asas feito capa."""
    w, h = q.get_size()
    base = c._tela_aux()
    ly = ALTURA * 0.42
    ceu_lua(base, t + 50, LARGURA * 0.5, ly, 150)
    gy = ly - 40
    galho(base, -20, gy, LARGURA + 20)
    x = LARGURA * 0.5
    if t < GIRA[0]:  # chega DEITADO batendo as asas e EMPINA pra agarrar o galho
        p, sobe = bater_asas(c, t)
        u = suave(t / GIRA[0])
        ele(c, base, p, x - 260 * (1 - u), gy + 2 + 150 * (1 - u) - sobe * (1 - u), t, 1.3, ang=DEITADO * (1 - u))
    elif t < GIRA[1]:  # agarrou: GIRA em volta dos pés
        u = suave((t - GIRA[0]) / (GIRA[1] - GIRA[0]))
        p = misturar(bater_asas(c, GIRA[0])[0], pendurado(c, t), u)
        ele(c, base, p, x, gy + 2, t, 1.3, ang=180 * u)
    else:  # PENDURADO balançando (o balanço vai diminuindo) e fecha as asas
        u = t - GIRA[1]
        balanco = math.sin(u * 0.16) * 14 * math.exp(-u * 0.04)
        capa = u - 4 if u > 14 else None
        ele(c, base, pendurado(c, t), x, gy + 2, t, 1.3, ang=180 + balanco, capa=capa)
    c.camera(q, base, (x, gy + 150), 1.35, pixel=True)
    if t == GIRA[0]:
        c.tremor = 4
    if GIRA[0] <= t < GIRA[0] + 14:
        texto_pow(q, "tic.", (int(w * 0.62), int(h * 0.2)), 36, (230, 230, 240), t - GIRA[0])


def v4_embaixo(c, q, t, k):
    """4) Lá EMBAIXO, no mapa: o derrotado caído... e a SOMBRA dele pendurada aparece em cima, balançando."""
    base = c._tela_aux()
    c.mapa(base, t + 100)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    c.mapa_frente(base, t + 100)
    noite(base, 0.55, (40, 40, 120))
    desce = suave(min(1, t / 16))
    ele(c, base, pendurado(c, t + 100), XO, -40 + 70 * desce, t + 100, 1.0, ang=180 + math.sin(t * 0.1) * 8,
        capa=40, sombra=(6, 4, 12))
    c.camera(q, base, (XO, CHAO - 150), 1.5, pixel=True)


def v5_ri(c, q, t, k):
    """5) Close nele pendurado na frente da lua: ABRE as asas, dá o GRITINHO (as ondinhas)... hihihi! O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    ly = ALTURA * 0.42
    ceu_lua(base, t + 150, LARGURA * 0.5, ly, 150)
    gy = ly - 40
    galho(base, -20, gy, LARGURA + 20)
    x = LARGURA * 0.5
    pd = pendurado(c, t + 150)
    if t < 10:  # (ainda de capa: abre)
        p, capa = pd, 40 - t * 3
    elif t < 34:
        p, capa = misturar(pd, pose(c, "n_grito"), suave(min(1, (t - 10) / 6))), None
    else:  # ri balançando
        p, capa = misturar(pose(c, "n_grito"), pose(c, "n_ri"), suave(min(1, (t - 34) / 8))), None
    ri = math.sin(t * 0.5) * 4 if t >= 34 else 0
    ele(c, base, p, x, gy + 2, t + 150, 1.3, ang=180 + ri, capa=capa)
    if 12 <= t < 34:
        for i in range(3):
            r = ((t - 12) * 5 + i * 18) % 54
            pygame.draw.circle(base, SONAR, (int(x + 14), int(gy + 150)), int(r + 6), 2)
    c.camera(q, base, (x, gy + 150), 1.35, pixel=True)
    if 12 <= t < 34:
        texto_pow(q, "Iiiiih!!", (int(w * 0.7), int(h * 0.3)), 50, SONAR, t % 8, giro=-0.08)
    elif 34 <= t < 60:
        texto_pow(q, "hihihi...", (int(w * 0.72), int(h * 0.62)), 40, (230, 220, 255), t - 34, giro=0.06)
    if t >= 44:
        faixa_nome(q, "NOCTURNUS", "O DONO DA NOITE.", COR_NOME, (t - 44) / 30)


PLANOS_LUA = [
    (44, v1_decola, {14: ("vento", 0.6), 28: ("vento", 0.4)}),
    (56, v2_lua, {0: ("vento", 0.4)}),
    (50, v3_pendura, {14: ("defesa", 0.4)}),
    (40, v4_embaixo, {}),
    (104, v5_ri, {12: ("uivo", 0.5), 34: ("blip", 0.5)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_LUA, titulo, oponente)
