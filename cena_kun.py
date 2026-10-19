"""CENAS DE ANIME do KUN (loja): a entrada EMBARALHADO e a vitória SOFÁ.

Tudo no MAPA da luta, com a SKIN dele e o OPONENTE de verdade. O Kun aparece com o desenho do jogo (montado na
escala do jogo e a câmera amplia). As CARTAS grandes, as mãos embaralhando, o SOFÁ e o HOMEM DE CARTAS são
ilustrados. A vitória é ideia do Gomes: close na cara, saca a carta, joga, a câmera ATRAVESSA a carta (igual o olho
do Magnus) e ele está deitado no sofá com um homem de cartas abanando com um leque de cartas.
"""
import math
import random

import pygame

import cutscene
import kun
from cena_max import fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, proporcionar, suave
from max10 import brilho

BORDA = (16, 14, 20)
XK, XO = LARGURA * 0.32, LARGURA * 0.74  # o Kun e o oponente, no mapa
VERMELHO, PRETO_C, PAPEL, VERSO, DOURADO = (200, 30, 44), (24, 22, 28), (246, 244, 236), (170, 36, 50), (226, 186, 80)
COR_NOME = (190, 40, 50)


def pal(c):
    return {k: c.cor(k, v) for k, v in kun.PALETA.items()}


def pose(c, nome):
    if nome == "deitado":
        return dict(DEITADO_SOFA)
    return c.l.poses.get(nome) or c.l.poses["parado"]


# =====================================================================
# A CARTA GRANDE (ilustrada)
# =====================================================================
def carta_grande(q, cx, cy, w, ang=0.0, largura=1.0, valor="K", naipe="ouros", brilha=0.0):
    """Uma carta de baralho GRANDE (w = largura em pixels). largura < 0 = mostrando o VERSO (girando em 3D).
    ang em graus."""
    h = w * 1.4
    lw = max(4, int(w * abs(largura)))
    sup = pygame.Surface((int(w) + 12, int(h) + 12), pygame.SRCALPHA)
    r = pygame.Rect(0, 0, lw, int(h))
    r.center = (sup.get_width() // 2, sup.get_height() // 2)
    raio = max(2, int(w * 0.08))
    pygame.draw.rect(sup, BORDA, r.inflate(max(4, w * 0.04), max(4, w * 0.04)), border_radius=raio)
    if largura >= 0:
        pygame.draw.rect(sup, PAPEL, r, border_radius=raio)
        if largura > 0.35:
            cor = VERMELHO if naipe in ("ouros", "copas") else PRETO_C
            m = r.inflate(-w * 0.14 * largura, -h * 0.1)
            pygame.draw.rect(sup, cor, m, max(1, int(w * 0.012)), border_radius=raio)
            naipe_forma(sup, r.centerx, r.centery, w * 0.26 * largura, naipe, cor)
            if w > 60:
                from efeitos import texto_grande
                tam = int(w * 0.16)
                texto_grande(sup, valor, tam, cor, (int(r.x + w * 0.14 * largura), int(r.y + h * 0.1)), contorno=PAPEL)
                texto_grande(sup, valor, tam, cor, (int(r.right - w * 0.14 * largura), int(r.bottom - h * 0.1)), contorno=PAPEL)
                naipe_forma(sup, r.x + w * 0.14 * largura, r.y + h * 0.2, w * 0.06 * largura, naipe, cor)
                naipe_forma(sup, r.right - w * 0.14 * largura, r.bottom - h * 0.2, w * 0.06 * largura, naipe, cor)
    else:  # o VERSO (vermelho com losangos dourados)
        pygame.draw.rect(sup, VERSO, r, border_radius=raio)
        m = r.inflate(-w * 0.12 * abs(largura), -h * 0.08)
        pygame.draw.rect(sup, DOURADO, m, max(1, int(w * 0.015)), border_radius=raio)
        if abs(largura) > 0.3:
            passo = max(6, w * 0.16)
            yy = m.y + passo / 2
            while yy < m.bottom:
                xx = m.x + passo / 2
                while xx < m.right:
                    naipe_forma(sup, xx, yy, passo * 0.28, "ouros", DOURADO)
                    xx += passo
                yy += passo
    if ang:
        sup = pygame.transform.rotate(sup, ang)
    if brilha > 0:
        brilho(q, (int(cx), int(cy)), int(w * 0.7), (255, 240, 180), int(200 * brilha))
    q.blit(sup, (int(cx - sup.get_width() / 2), int(cy - sup.get_height() / 2)))


def naipe_forma(q, x, y, r, naipe, cor):
    """O NAIPE desenhado (ouros, copas, espadas, paus) centrado em (x, y), do tamanho r."""
    r = max(1.5, r)
    if naipe == "ouros":
        pygame.draw.polygon(q, cor, [(x, y - r * 1.3), (x + r, y), (x, y + r * 1.3), (x - r, y)])
    elif naipe == "copas":
        pygame.draw.circle(q, cor, (int(x - r * 0.5), int(y - r * 0.3)), int(r * 0.6))
        pygame.draw.circle(q, cor, (int(x + r * 0.5), int(y - r * 0.3)), int(r * 0.6))
        pygame.draw.polygon(q, cor, [(x - r * 1.08, y - r * 0.1), (x + r * 1.08, y - r * 0.1), (x, y + r * 1.2)])
    elif naipe == "espadas":
        pygame.draw.circle(q, cor, (int(x - r * 0.5), int(y + r * 0.2)), int(r * 0.6))
        pygame.draw.circle(q, cor, (int(x + r * 0.5), int(y + r * 0.2)), int(r * 0.6))
        pygame.draw.polygon(q, cor, [(x - r * 1.08, y + r * 0.1), (x + r * 1.08, y + r * 0.1), (x, y - r * 1.2)])
        pygame.draw.polygon(q, cor, [(x, y + r * 0.3), (x + r * 0.4, y + r * 1.2), (x - r * 0.4, y + r * 1.2)])
    else:  # paus
        for dx, dy in ((0, -0.55), (-0.6, 0.15), (0.6, 0.15)):
            pygame.draw.circle(q, cor, (int(x + dx * r), int(y + dy * r)), int(r * 0.55))
        pygame.draw.polygon(q, cor, [(x, y), (x + r * 0.4, y + r * 1.2), (x - r * 0.4, y + r * 1.2)])


DEITADO_SOFA = dict(  # DEITADO DE COSTAS no sofá: as mãos atrás da cabeça, uma perna esticada e a outra dobrada
    qd=(0, 10), pc=(-34, 16), cb=(-50, 24), ct=(-40, 22), mt=(-56, 30), cf=(-38, 24), mf=(-54, 32),
    jt=(22, 12), pt=(46, 10), jf=(16, 30), pf=(32, 12))
proporcionar({"d": DEITADO_SOFA})


def kun_por(c, base, p, x, y=CHAO, d=1):
    c.por(base, p, 1.0, x, y, d, guardar=False)


# =====================================================================
# ENTRADA: EMBARALHADO
# =====================================================================
def maos_embaralhando(c, q, w, h, t, fase):
    """CLOSE nas MÃOS de crupiê (manga branca com a LIGA no braço) embaralhando: as duas metades do baralho
    se dobram e as cartas vão intercalando (fase: 0..1 dentro de cada embaralhada)."""
    pk = pal(c)
    pele, pele_s, manga = pk["p"], pk["P"], pk["w"]
    cy = h * 0.6
    meio = w * 0.5
    for lado in (-1, 1):  # os ANTEBRAÇOS (manga branca dobrada, com a LIGA verde), vindo de baixo até as mãos
        mx = meio + lado * (200 - 60 * fase)
        cotovelo = (meio + lado * w * 0.46, h + 60)
        pygame.draw.line(q, BORDA, cotovelo, (mx + lado * 40, cy + 10), 118)
        pygame.draw.line(q, pele, cotovelo, (mx + lado * 40, cy + 10), 104)
        dobra_x, dobra_y = cotovelo[0] + (mx - cotovelo[0]) * 0.45, cotovelo[1] + (cy - cotovelo[1]) * 0.45
        pygame.draw.line(q, BORDA, cotovelo, (dobra_x, dobra_y), 140)  # a manga dobrada
        pygame.draw.line(q, manga, cotovelo, (dobra_x, dobra_y), 126)
        pygame.draw.circle(q, BORDA, (int(dobra_x), int(dobra_y)), 70)
        pygame.draw.circle(q, manga, (int(dobra_x), int(dobra_y)), 63)
        lx, ly = cotovelo[0] + (mx - cotovelo[0]) * 0.22, cotovelo[1] + (cy - cotovelo[1]) * 0.22
        pygame.draw.circle(q, pk["g"], (int(lx), int(ly)), 66, 14)  # a LIGA verde no braço
    dobra = math.sin(fase * math.pi)  # (as duas metades se curvam e soltam as cartas)
    for lado in (-1, 1):
        bx = meio + lado * (150 - 60 * fase)
        for i in range(10):  # a metade do baralho (as cartas empilhadas, curvando)
            yy = cy - i * 5 - dobra * 30 * (1 - abs(i - 5) / 5)
            ang = -lado * (8 + dobra * 18)
            carta_grande(q, bx, yy, 150, ang=ang, largura=-1)
    queda = int(fase * 18)
    for i in range(queda):  # as cartas que já caíram, intercalando no meio
        lado = -1 if i % 2 else 1
        carta_grande(q, meio + lado * 6, cy + 30 - i * 3, 150, ang=lado * 3, largura=-1)
    for lado in (-1, 1):  # as MÃOS (por cima)
        mx = meio + lado * (200 - 60 * fase)
        pygame.draw.ellipse(q, BORDA, (mx - 70, cy - 50, 140, 110))
        pygame.draw.ellipse(q, pele, (mx - 64, cy - 44, 128, 98))
        pygame.draw.ellipse(q, pele_s, (mx - 64, cy + 10, 128, 44))
        for j in range(3):  # os dedos (dobrados por cima do baralho)
            fx = mx - lado * (30 + j * 22)
            pygame.draw.line(q, BORDA, (mx, cy - 20 + j * 14), (fx, cy - 60 - dobra * 20 + j * 10), 26)
            pygame.draw.line(q, pele, (mx, cy - 20 + j * 14), (fx, cy - 60 - dobra * 20 + j * 10), 18)
        pygame.draw.line(q, BORDA, (mx, cy + 10), (mx - lado * 70, cy + 40), 28)  # o polegar
        pygame.draw.line(q, pele, (mx, cy + 10), (mx - lado * 70, cy + 40), 20)


def e1_embaralha(c, q, t, k):
    """1) CLOSE nas mãos dele EMBARALHANDO (FRRRRT!), duas vezes, com o mapa desfocado atrás."""
    w, h = q.get_size()
    fundo_desfocado(c, q, t, (XK, CHAO - 100), 2.2, 60)
    fase = (t % 22) / 22
    maos_embaralhando(c, q, w, h, t, fase)
    if fase < 0.6:
        texto_pow(q, "FRRRRRT!", (int(w * 0.5), int(h * 0.2)), 54, (255, 240, 220), int(fase * 20), giro=0.06)


def e2_explode(c, q, t, k):
    """2) Ele JOGA o baralho pro alto: as cartas EXPLODEM vindo pra câmera, girando (linhas de velocidade)."""
    w, h = q.get_size()
    fundo_desfocado(c, q, t, (XK, CHAO - 200), 1.8, 40)
    cutscene.linhas_velocidade(q, (w * 0.5, h * 0.55), (255, 255, 255), n=40, r_dentro=120, grossura=5, semente=t // 2,
                               alfa=110)
    rnd = random.Random(3)
    cartas = []
    for i in range(34):
        a = rnd.uniform(0, math.tau)
        vel = rnd.uniform(0.6, 1.4)
        u = min(1.4, t / 26 * vel)
        d = u * rnd.uniform(200, 700)
        tam = 20 + u * rnd.uniform(60, 260)
        cartas.append((tam, w * 0.5 + math.cos(a) * d, h * 0.55 + math.sin(a) * d * 0.7, rnd.uniform(-1, 1) * t * 18,
                       math.cos(t * 0.3 * vel + i), i))
    for tam, x, y, ang, larg, i in sorted(cartas):  # (as pequenas atrás, as grandes na frente)
        carta_grande(q, x, y, tam, ang=ang, largura=larg, valor="AKQJ"[i % 4], naipe=("ouros", "copas", "espadas", "paus")[i % 4])
    if t < 12:
        texto_pow(q, "SHAAA!", (int(w * 0.5), int(h * 0.22)), 64, (255, 230, 150), t)


def e3_redemoinho(c, q, t, k):
    """3) No MAPA: as cartas caem do céu e viram um REDEMOINHO onde ele vai estar, cada vez mais rápido e mais
    fechado. O oponente protege os olhos."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "defesa" if t > 20 else "parado", 1.0, XO, CHAO)
    fecha = suave(k)
    for i in range(46):  # o REDEMOINHO de cartas
        a = t * (0.12 + 0.25 * fecha) + i * 0.47
        cai = min(1, max(0, (t - (i % 12) * 2) / 18))
        r = (180 * (1 - fecha) + 26) * (0.6 + (i % 5) * 0.12)
        y = CHAO - 20 - (i % 9) * 18 * (0.7 + 0.3 * fecha)
        y = -40 + (y + 40) * cai
        kun.carta(base, (XK + math.cos(a) * r, y + math.sin(a) * r * 0.25), a, 2.6, math.cos(a))
    for i in range(3):  # o vento (riscos curvos)
        a0 = t * 0.3 + i * 2.1
        rr = 90 * (1 - fecha) + 40
        pygame.draw.arc(base, (240, 240, 250), (XK - rr, CHAO - 120 + i * 30, rr * 2, 40), a0, a0 + 2.0, 2)
    c.mapa_frente(base, t)
    c.camera(q, base, (XK + 110 - 80 * fecha, CHAO - 110), 1.7 + 0.5 * fecha, pixel=True)
    c.tremor = max(c.tremor, int(4 * fecha))
    if t > 20:
        texto_pow(q, "SHUFFLE!", (int(w * 0.68), int(h * 0.22)), 50, (255, 230, 150), (t - 20) % 10, giro=0.08)


def e4_forma(c, q, t, k):
    """4) As cartas se FECHAM nele num clarão... e ele aparece com a carta erguida. As últimas cartas caem em volta."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 50)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    junta = 8
    if t < junta:
        for i in range(30):
            a = t * 0.6 + i * 0.7
            r = 40 * (1 - t / junta) + 4
            kun.carta(base, (XK + math.cos(a) * r, CHAO - 60 - (i % 7) * 14 + math.sin(a) * r * 0.3), a, 1.6, math.cos(a))
    else:
        p = misturar(pose(c, "k_agacha"), pose(c, "k_vitoria"), suave(min(1, (t - junta) / 8)))
        kun_por(c, base, p, XK)
        rnd = random.Random(4)
        for i in range(16):  # as cartas que sobraram caindo devagar em volta
            u = t - junta
            x = XK + rnd.uniform(-160, 160) + math.sin(u * 0.15 + i) * 14
            y = CHAO - 220 + u * rnd.uniform(3, 6)
            if y < CHAO:
                kun.carta(base, (x, y), u * 0.2 + i, 1.4, math.cos(u * 0.25 + i))
    c.mapa_frente(base, t + 50)
    c.camera(q, base, (XK + 60, CHAO - 100), 2.0, pixel=True)
    if t == junta:
        c.inverte, c.tremor = 3, 12
    if t < junta + 4:
        flash = pygame.Surface((w, h))
        flash.fill((255, 250, 230))
        flash.set_alpha(max(0, 230 - abs(t - junta) * 40))
        q.blit(flash, (0, 0))


def e5_pose(c, q, t, k):
    """5) A POSE: gira a carta entre os dedos (o ÁS brilhando)... e o nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 80)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    p = misturar(pose(c, "k_vitoria"), pose(c, "k_brinca"), suave(min(1, t / 10)))
    kun_por(c, base, p, XK)
    c.mapa_frente(base, t + 80)
    mao = c.ponto(p, "mf", 1.0, XK, CHAO)
    centro, z = (XK + 40, CHAO - 120), 2.3 + 0.3 * suave(min(1, t / 40))
    c.camera(q, base, centro, z, pixel=True)
    mx, my = para_tela(centro, z, mao)
    gira = math.cos(t * 0.35) if t < 30 else 1.0  # (girando a carta... e para mostrando o ÁS)
    carta_grande(q, mx + 30, my - 70, 90, ang=-12, largura=gira, valor="A", naipe="espadas", brilha=0.6 if t >= 30 else 0)
    if 30 <= t < 42:
        texto_pow(q, "PLIM!", (int(mx + 140), int(my - 150)), 44, (255, 240, 180), t - 30)
    if t >= 26:
        faixa_nome(q, "KUN", "O MESTRE DAS CARTAS.", COR_NOME, (t - 26) / 30)


PLANOS = [
    (44, e1_embaralha, {0: ("vento", 0.4), 22: ("vento", 0.4)}),
    (30, e2_explode, {0: ("vento", 0.9)}),
    (60, e3_redemoinho, {0: ("vento", 0.5), 30: ("vento", 0.7)}),
    (34, e4_forma, {8: ("confirma", 0.7)}),
    (76, e5_pose, {30: ("blip", 0.6)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: SOFÁ (ideia do Gomes)
# =====================================================================
def v1_rosto(c, q, t, k):
    """1) No MAPA do lado do derrotado... a câmera CHEGA na cara dele (sorrisinho de quem ganhou)."""
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO - 30, CHAO)
    p = pose(c, "parado")
    kun_por(c, base, p, XK + 60)
    c.mapa_frente(base, t)
    cb = c.ponto(p, "cb", 1.0, XK + 60, CHAO)
    z = 1.6 + 3.0 * suave(k)
    centro = (XK + 160 + (cb[0] - XK - 160) * suave(k), CHAO - 90 + (cb[1] - CHAO + 90) * suave(k))
    c.camera(q, base, centro, z, pixel=True)


def v2_saca(c, q, t, k):
    """2) CLOSE: ele SACA uma carta, que surge brilhando entre os dedos (SHIK!)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 30)
    p = misturar(pose(c, "parado"), pose(c, "k_brinca"), suave(min(1, t / 8)))
    kun_por(c, base, p, XK + 60)
    c.mapa_frente(base, t + 30)
    cb = c.ponto(p, "cb", 1.0, XK + 60, CHAO)
    mao = c.ponto(p, "mf", 1.0, XK + 60, CHAO)
    centro, z = ((cb[0] + mao[0]) / 2 + 10, (cb[1] + mao[1]) / 2), 4.0
    c.camera(q, base, centro, z, pixel=True)
    if t >= 8:
        mx, my = para_tela(centro, z, mao)
        u = min(1, (t - 8) / 6)
        carta_grande(q, mx + 20, my - 60 * u, 40 + 60 * u, ang=-20, largura=math.cos((1 - u) * 6) if u < 1 else 1.0,
                     valor="K", naipe="ouros", brilha=1 - u * 0.5)
        if t < 22:
            pygame.draw.line(q, (255, 255, 255), (mx - 80, my - 120), (mx + 120, my + 20), 4)  # o risco de brilho
            texto_pow(q, "SHIK!", (int(mx - 160), int(my - 140)), 52, (255, 240, 180), t - 8, giro=0.1)


def v3_joga(c, q, t, k):
    """3) Ele JOGA a carta NO CHÃO (girando em arco)... ela cai deitada e BRILHA... e a câmera MERGULHA nela."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 60)
    c.por_oponente(base, "caido", 1.0, XO - 30, CHAO)
    p = misturar(pose(c, "k_brinca"), pose(c, "k_lanca"), suave(min(1, t / 5)))
    kun_por(c, base, p, XK + 60)
    s = c.l.s
    xc = XK + 170  # onde a carta cai
    cai = 16
    if 3 <= t < cai:  # a carta voando em arco, girando
        u = (t - 3) / (cai - 3)
        mao = c.ponto(p, "mf", 1.0, XK + 60, CHAO)
        x = mao[0] + (xc - mao[0]) * u
        y = mao[1] + (CHAO - 6 - mao[1]) * u - math.sin(u * math.pi) * 40
        kun.carta(base, (x, y), t * 0.7, 2.2, math.cos(t * 0.9))
    elif t >= cai:  # deitada no chão, BRILHANDO
        kun.carta_no_chao(base, xc, s, t)
        if t < cai + 10:
            brilho(base, (int(xc), int(CHAO - 4)), int(30 + (t - cai) * 4), (255, 230, 150), 200 - (t - cai) * 18)
    c.mapa_frente(base, t + 60)
    mergulha = suave(min(1, max(0, t - cai - 4) / 16))  # a câmera indo pra carta no chão
    centro = (XK + 100 + (xc - XK - 100) * mergulha, CHAO - 100 + 96 * mergulha)
    z = 2.0 + 6.0 * mergulha ** 1.5
    c.camera(q, base, centro, z, pixel=True)
    if t == cai:
        c.tremor = 4
    if cai <= t < cai + 12:
        cx, cy = para_tela(centro, z, (xc, CHAO))
        texto_pow(q, "PLAFT!", (int(cx), int(cy - 90)), 46, (255, 240, 200), t - cai)


def v4_atravessa(c, q, t, k):
    """4) A câmera ATRAVESSA a carta: entra no losango vermelho do meio... e sai do outro lado (clarão)."""
    w, h = q.get_size()
    e = 1 + 26 * suave(k) ** 2.4
    cx, cy = w * 0.5, h * 0.5
    if e < 1.6:  # (de começo: a carta inteira tomando a tela)
        q.fill(BORDA)
        carta_grande(q, cx, cy, 400 * e, largura=1.0, valor="K", naipe="ouros")
    else:  # (depois: só o pedaço que cabe na tela, desenhado direto — a carta gigante não cabe na memória)
        q.fill(PAPEL)
        lw, lh = 400 * e, 560 * e
        moldura = pygame.Rect(0, 0, lw * 0.86, lh * 0.9)
        moldura.center = (int(cx), int(cy))
        if moldura.w < w * 4:
            pygame.draw.rect(q, VERMELHO, moldura, max(2, int(e * 2)))
        naipe_forma(q, cx, cy, 104 * e, "ouros", VERMELHO)
    if k > 0.55:  # o losango tomando a tela... vira um túnel de luz
        u = (k - 0.55) / 0.45
        brilho(q, (int(w * 0.5), int(h * 0.5)), int(300 + 300 * u), (255, 220, 160), int(220 * u))
        for i in range(6):
            r = ((t * 14 + i * 60) % 360) * (0.6 + u)
            pygame.draw.circle(q, (255, 240, 210), (int(w * 0.5), int(h * 0.5)), int(r), 3)
    if k > 0.85:
        flash = pygame.Surface((w, h))
        flash.fill((255, 250, 240))
        flash.set_alpha(int(255 * (k - 0.85) / 0.15))
        q.blit(flash, (0, 0))


def sofa(q, x, y, s):
    """O SOFÁ vermelho capitonê (o mesmo da vitória de antes), do tamanho s."""
    w, h = 150 * s, 52 * s
    borda, cor, esc, clara = (34, 8, 14), (176, 40, 52), (130, 26, 38), (214, 80, 90)
    encosto = pygame.Rect(0, 0, w * 0.86, h * 0.9)
    encosto.midbottom = (int(x - 4 * s), int(y - h * 0.42))
    pygame.draw.rect(q, borda, encosto.inflate(6, 6), border_radius=int(14 * s))
    pygame.draw.rect(q, esc, encosto, border_radius=int(12 * s))
    for i in range(3):  # os botões do capitonê
        pygame.draw.circle(q, borda, (int(encosto.x + encosto.w * (0.25 + i * 0.25)), int(encosto.centery)), 2)
    assento = pygame.Rect(0, 0, w * 0.86, h * 0.36)
    assento.midbottom = (int(x), int(y - h * 0.16))
    pygame.draw.rect(q, borda, assento.inflate(6, 6), border_radius=int(8 * s))
    pygame.draw.rect(q, cor, assento, border_radius=int(8 * s))
    pygame.draw.line(q, clara, (assento.x + 8, assento.y + 4), (assento.right - 8, assento.y + 4), 3)
    pygame.draw.line(q, borda, (assento.centerx, assento.y + 2), (assento.centerx, assento.bottom - 2), 2)
    for lado in (-1, 1):  # os braços gordinhos
        br = pygame.Rect(0, 0, w * 0.16, h * 0.62)
        br.midbottom = (int(x + lado * w * 0.45), int(y - h * 0.14))
        pygame.draw.rect(q, borda, br.inflate(6, 6), border_radius=int(10 * s))
        pygame.draw.rect(q, cor, br, border_radius=int(10 * s))
        pygame.draw.rect(q, clara, (br.x + 3, br.y + 3, br.w - 6, 5), border_radius=3)
    for lado in (-1, 1):  # os pezinhos dourados
        pygame.draw.rect(q, (200, 160, 60), (x + lado * w * 0.38 - 4, y - h * 0.16, 8, h * 0.16))


def homem_de_cartas(q, x, y, s, t):
    """O SOLDADO DE BARALHO (o mordomo do Kun): o corpo é uma CARTA grande (rei de copas), a cabeça redonda com
    carinha, bracinhos e perninhas pretos com luvas brancas... abanando com um LEQUE DE CARTAS.
    (x, y) = os pés; s = o tamanho do jogo. Devolve onde está o leque."""
    def P(px, py):
        return x + px * s, y - py * s

    g = max(2, int(2.6 * s))
    for lado in (-1, 1):  # as PERNINHAS e os sapatos
        pygame.draw.line(q, BORDA, P(lado * 6, 42), P(lado * 7, 4), g)
        pygame.draw.ellipse(q, BORDA, (*P(lado * 7 - 6 + lado * 2, 6), 12 * s, 6 * s))
    for lado in (-1,):  # o braço de trás, na cintura
        pygame.draw.lines(q, BORDA, False, [P(-14, 78), P(-24, 64), P(-16, 54)], g)
        pygame.draw.circle(q, PAPEL, P(-16, 54), max(2, int(4 * s)))
        pygame.draw.circle(q, BORDA, P(-16, 54), max(2, int(4 * s)), 1)
    carta_grande(q, *P(0, 62), 38 * s, largura=1.0, valor="K", naipe="copas")  # o CORPO
    pygame.draw.line(q, BORDA, P(0, 88), P(0, 93), g)  # o pescoço
    cab = P(0, 102)  # a CABEÇA
    r = 10 * s
    pygame.draw.circle(q, BORDA, (int(cab[0]), int(cab[1])), int(r + 2))
    pygame.draw.circle(q, (244, 214, 184), (int(cab[0]), int(cab[1])), int(r))
    pygame.draw.arc(q, (60, 40, 30), (cab[0] - r, cab[1] - r - 1, r * 2, r * 1.4), 0.3, math.pi - 0.3, max(2, int(3 * s)))
    for lado in (-1, 1):  # olhinhos fechados de contente e bochecha
        pygame.draw.arc(q, BORDA, (cab[0] + lado * 4 * s - 2.4 * s, cab[1] - 1 * s, 4.8 * s, 3.4 * s), 0.2, math.pi - 0.2,
                        max(1, int(s)))
        pygame.draw.circle(q, (250, 160, 150), (int(cab[0] + lado * 6 * s), int(cab[1] + 3 * s)), max(1, int(1.8 * s)))
    pygame.draw.arc(q, BORDA, (cab[0] - 3 * s, cab[1] + 1 * s, 6 * s, 5 * s), math.pi + 0.3, math.tau - 0.3, max(1, int(s)))
    abana = math.sin(t * 0.28) * 0.5  # o braço da frente ABANANDO o leque, na direção do Kun
    ombro = P(14, 80)
    cot = (ombro[0] + 12 * s, ombro[1] - 8 * s)
    mao = (cot[0] + math.cos(-1.0 + abana) * 14 * s, cot[1] + math.sin(-1.0 + abana) * 14 * s)
    pygame.draw.lines(q, BORDA, False, [ombro, cot, mao], g)
    for i in range(7):  # o LEQUE DE CARTAS (aberto, girando com o abano)
        a = -math.pi / 2 - 0.95 + i * 0.32 + abana
        cx, cy = mao[0] + math.cos(a) * 15 * s, mao[1] + math.sin(a) * 15 * s
        carta_grande(q, cx, cy, 15 * s, ang=-math.degrees(a + math.pi / 2), largura=1.0, valor="",
                     naipe=("copas", "ouros", "espadas", "paus")[i % 4])
    pygame.draw.circle(q, PAPEL, (int(mao[0]), int(mao[1])), max(2, int(4 * s)))  # a luva
    pygame.draw.circle(q, BORDA, (int(mao[0]), int(mao[1])), max(2, int(4 * s)), 1)
    return mao


def v5_sofa(c, q, t, k):
    """5) Saindo do clarão: ele DEITADO no SOFÁ (mãos atrás da cabeça), o HOMEM DE CARTAS abanando com o leque,
    o vento balançando o cabelo... o derrotado caído do lado. E o nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 120)
    s = c.l.s
    xs = XK + 40
    c.por_oponente(base, "caido", 1.0, xs + 250, CHAO)
    sofa(base, xs, CHAO, s)
    respira = math.sin(t * 0.1)
    p = pose(c, "deitado")
    p["pc"] = (p["pc"][0], p["pc"][1] + respira * 1.2)
    kun_por(c, base, p, xs + 10 * s, CHAO - 32 * s)
    mao = homem_de_cartas(base, xs - 128 * s, CHAO, s * 0.95, t)
    for i in range(3):  # o VENTINHO do leque indo nele
        u = (t * 0.06 + i / 3) % 1
        x0 = mao[0] + 20 + u * 90
        pygame.draw.arc(base, (240, 240, 255), (x0, mao[1] + 10 + i * 8, 40, 16), 0.2, 2.6, 2)
    c.mapa_frente(base, t + 120)
    z = 2.2 - 0.4 * suave(min(1, t / 60))
    c.camera(q, base, (xs + 10, CHAO - 80), z, pixel=True)
    cb = c.ponto(p, "cb", 1.0, xs + 10 * s, CHAO - 32 * s)
    zx, zy = para_tela((xs + 10, CHAO - 80), z, cb)
    if t < 6:
        flash = pygame.Surface((w, h))
        flash.fill((255, 250, 240))
        flash.set_alpha(255 - t * 42)
        q.blit(flash, (0, 0))
    from efeitos import texto
    if 14 < t < 60:
        texto_pow(q, "Aaaahh~", (int(zx + 40), int(zy - 90)), 40, (255, 240, 220), (t - 14) % 12, giro=0.08)
    if t >= 30:
        for i in range(2):
            u = (t * 0.02 + i * 0.5) % 1
            texto(q, "z", 18 + i * 6, (230, 230, 250), (int(zx + 20 + u * 40), int(zy - 40 - u * 80)))
    if t >= 50:
        faixa_nome(q, "KUN", "A CASA SEMPRE GANHA.", COR_NOME, (t - 50) / 30)


PLANOS_SOFA = [
    (36, v1_rosto, {}),
    (30, v2_saca, {8: ("blip", 0.6)}),
    (40, v3_joga, {4: ("vento", 0.8), 16: ("puf", 0.5), 20: ("carga", 0.5)}),
    (30, v4_atravessa, {0: ("vento", 0.7), 22: ("carga", 0.6)}),
    (120, v5_sofa, {0: ("puf", 0.7), 14: ("vento", 0.3)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_SOFA, titulo, oponente)
