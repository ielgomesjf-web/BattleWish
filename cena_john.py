"""CENAS DE ANIME do JOHN (loja).

ENTRADA (CAIXA DE MÁGICA): as LUZES DO PALCO acendem (holofote) em cima de uma caixa de mágica fechada no meio do
mapa... a caixa TREME (TOC TOC TOC)... o COELHINHO espia pela fresta... a caixa ABRE como uma flor (PUF, fumaça roxa,
confete) e o John salta e AGRADECE (reverência), com o coelhinho no ombro.
VITÓRIA (SERRADO DE BRINCADEIRA): o truque da CAIXA SERRADA (a do jogo): ele entra na caixa, o COELHINHO serra no
meio, as metades se SEPARAM (os pés mexendo do outro lado!)... juntam de novo, PUF, ele sai inteiro e os dois
agradecem com a plateia aplaudindo.
O John e o coelhinho aparecem com o desenho do jogo; o palco, os holofotes e a plateia são ilustrados.
"""
import math
import random

import pygame

import cutscene
import john
from cena_max import fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

BORDA = (20, 10, 30)
XJ, XO = LARGURA * 0.36, LARGURA * 0.74  # o John e o oponente, no mapa
ROXO, ROXO_ESC, OURO = (120, 50, 170), (80, 30, 120), (255, 220, 80)
COR_NOME = (110, 50, 160)


def pose(c, nome):
    return c.l.poses.get(nome) or c.l.poses["parado"]


def john_por(c, base, p, x, y=CHAO, d=1, coelho=True):
    """O John (desenho do jogo). coelho=False: sem o coelhinho do lado (ele está em outro lugar na cena)."""
    if coelho:
        c.por(base, p, 1.0, x, y, d, guardar=False)
        return
    orig = john.coelhinho
    john.coelhinho = lambda *a, **k: None
    try:
        c.por(base, p, 1.0, x, y, d, guardar=False)
    finally:
        john.coelhinho = orig


def coelhinho(base, x, chao, t, d=1, tam=0.36, s=1.36):
    """O COELHINHO do jogo (o do lado do John)."""
    john.desenha_coelho(base, x, chao, s * 1.6, d, t, tam)


def holofote(base, x, t, forca=1.0, cor=(255, 250, 220)):
    """Um HOLOFOTE vindo de cima (o cone de luz e o círculo no chão)."""
    sup = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(sup, (*cor, int(70 * forca)), [(x - 30, -20), (x + 30, -20), (x + 110, CHAO), (x - 110, CHAO)])
    pygame.draw.ellipse(sup, (*cor, int(110 * forca)), (x - 110, CHAO - 12, 220, 24))
    base.blit(sup, (0, 0))


def escurece(base, f=0.55):
    sup = pygame.Surface(base.get_size())
    sup.fill(tuple(int(255 * (1 - f) + v * f) for v in (20, 14, 40)))
    base.blit(sup, (0, 0), special_flags=pygame.BLEND_RGB_MULT)


def confete(q, t, t0, x, y, n=40, semente=4):
    rnd = random.Random(semente)
    cores = ((240, 60, 60), (60, 180, 240), (250, 210, 60), (120, 220, 90), (200, 120, 240))
    u = t - t0
    for i in range(n):
        vx, vy = rnd.uniform(-6, 6), rnd.uniform(-11, -4)
        px = x + vx * u + math.sin(u * 0.2 + i) * 6
        py = y + vy * u + 0.22 * u * u
        if py < CHAO:
            a = u * 0.3 + i
            pygame.draw.polygon(q, cores[i % 5], [(px + math.cos(a) * 5, py + math.sin(a) * 2), (px - math.cos(a) * 5, py - math.sin(a) * 2),
                                                  (px - math.cos(a) * 5 + 2, py - math.sin(a) * 2 + 4), (px + math.cos(a) * 5 + 2, py + math.sin(a) * 2 + 4)])


def fumaca_roxa(base, x, y, u, raio=90):
    rnd = random.Random(3)
    sup = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    for i in range(16):
        a = rnd.uniform(0, math.tau)
        d = raio * (0.2 + 0.8 * u) * rnd.uniform(0.4, 1)
        r = 20 + 34 * u * rnd.uniform(0.6, 1.2)
        pygame.draw.circle(sup, (200, 170, 240, int(220 * (1 - u))), (int(x + math.cos(a) * d), int(y + math.sin(a) * d * 0.7)), int(r))
    base.blit(sup, (0, 0))


# =====================================================================
# A CAIXA DE MÁGICA
# =====================================================================
def caixa(base, x, t, abre=0.0, treme=0.0):
    """A CAIXA DE MÁGICA roxa com estrelas douradas; abre (0..1) = as paredes caindo como uma flor."""
    w = 90
    tx = math.sin(t * 2) * 3 * treme
    if abre <= 0:
        r = pygame.Rect(0, 0, w, w)
        r.midbottom = (int(x + tx), CHAO)
        pygame.draw.rect(base, BORDA, r.inflate(6, 6), border_radius=4)
        pygame.draw.rect(base, ROXO, r, border_radius=4)
        pygame.draw.rect(base, ROXO_ESC, (r.x, r.bottom - 14, r.w, 14))
        pygame.draw.rect(base, OURO, r, 3, border_radius=4)
        tampa = pygame.Rect(r.x - 6, r.y - 10, r.w + 12, 12)
        pygame.draw.rect(base, BORDA, tampa.inflate(4, 4))
        pygame.draw.rect(base, ROXO_ESC, tampa)
        for k in range(3):  # as estrelas
            sx, sy = r.x + r.w * (0.22 + k * 0.28), r.y + r.h * (0.35 + (k % 2) * 0.22)
            pts = [(sx + math.cos(-math.pi / 2 + j * math.pi / 5) * (10 if j % 2 == 0 else 4),
                    sy + math.sin(-math.pi / 2 + j * math.pi / 5) * (10 if j % 2 == 0 else 4)) for j in range(10)]
            pygame.draw.polygon(base, OURO, pts)
        pygame.draw.line(base, (30, 10, 40), (r.centerx, r.y + 4), (r.centerx, r.bottom - 4), 2)  # a fresta
        return r
    for i, lado in enumerate((-1, 1)):  # as paredes caindo pros lados
        a = lado * abre * 1.45
        base_p = (x + lado * w / 2, CHAO)
        topo = (base_p[0] + math.sin(a) * w, base_p[1] - math.cos(a) * w)
        larg = (math.cos(a) * 8, math.sin(a) * 8)
        pts = [base_p, topo, (topo[0] - larg[0] * lado * 0, topo[1]), base_p]
        pygame.draw.line(base, BORDA, base_p, topo, 18)
        pygame.draw.line(base, ROXO, base_p, topo, 14)
        pygame.draw.line(base, OURO, base_p, topo, 2)
    pygame.draw.rect(base, BORDA, (x - w / 2 - 3, CHAO - 8, w + 6, 10))
    pygame.draw.rect(base, ROXO_ESC, (x - w / 2, CHAO - 6, w, 6))
    return None


# =====================================================================
# ENTRADA: CAIXA DE MÁGICA
# =====================================================================
def e1_luzes(c, q, t, k):
    """1) O mapa no ESCURO... TCHAK: o HOLOFOTE acende em cima da caixa de mágica."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    caixa(base, XJ, t)
    acende = 16
    escurece(base, 0.75 if t < acende else 0.5)
    if t >= acende:
        holofote(base, XJ, t, min(1, (t - acende) / 4))
    c.mapa_frente(base, t)
    c.camera(q, base, ((XJ + XO) / 2 - 40, CHAO - 110), 1.6, pixel=True)
    if acende <= t < acende + 12:
        texto_pow(q, "TCHAK!", (int(w * 0.3), int(h * 0.2)), 50, (255, 250, 220), t - acende)


def e2_treme(c, q, t, k):
    """2) A caixa TREME (TOC TOC TOC)... e o COELHINHO espia pela fresta da tampa!"""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 40)
    escurece(base, 0.5)
    holofote(base, XJ, t)
    r = caixa(base, XJ, t, treme=1.0 if t < 30 else 0.0)
    if t >= 30:  # o COELHINHO espiando (a cabeça e as orelhas saindo da tampa)
        sobe = suave(min(1, (t - 30) / 8))
        sup = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        coelhinho(sup, XJ + 8, r.y - 4 + 20 * (1 - sobe), t, d=1, tam=0.4)
        sup.fill((0, 0, 0, 0), (0, r.y - 2, LARGURA, ALTURA))  # (só o que está acima da tampa)
        base.blit(sup, (0, 0))
    c.mapa_frente(base, t + 40)
    c.camera(q, base, (XJ, CHAO - 70), 3.0, pixel=True)
    for b in (4, 12, 20):
        if b <= t < b + 6:
            c.tremor = max(c.tremor, 3)
            texto_pow(q, "TOC!", (int(w * (0.3 + (b - 4) * 0.02)), int(h * 0.3)), 44, (240, 230, 250), t - b, giro=0.1)
    if t >= 40:
        texto_pow(q, "?", (int(w * 0.62), int(h * 0.26)), 60, (255, 240, 200), t - 40)


ABRE = 10


def e3_abre(c, q, t, k):
    """3) A caixa ABRE como uma flor: PUF (fumaça roxa e confete)... e o John SALTA lá de dentro."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 90)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    escurece(base, 0.5)
    holofote(base, XJ, t)
    abre = suave(min(1, max(0, t - ABRE) / 8))
    caixa(base, XJ, t, abre=abre, treme=1.0 if t < ABRE else 0.0)
    if t >= ABRE:
        u = min(1, (t - ABRE) / 22)
        y = CHAO - math.sin(u * math.pi) * 120
        john_por(c, base, pose(c, "pulo") if u < 1 else pose(c, "parado"), XJ, y, coelho=False)
        fumaca_roxa(base, XJ, CHAO - 50, min(1, (t - ABRE) / 26))
        confete(base, t, ABRE, XJ, CHAO - 80)
    else:
        caixa(base, XJ, t, treme=1.0)
    c.mapa_frente(base, t + 90)
    c.camera(q, base, (XJ + 40, CHAO - 110), 2.0, pixel=True)
    if t == ABRE:
        c.inverte, c.tremor = 2, 10
    if ABRE <= t < ABRE + 16:
        texto_pow(q, "PUF!!", (int(w * 0.6), int(h * 0.24)), 70, (220, 190, 255), t - ABRE)


def e4_agradece(c, q, t, k):
    """4) Ele AGRADECE (a reverência com a cartola), o coelhinho do lado faz igual... o nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 130)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    escurece(base, 0.35)
    holofote(base, XJ, t)
    caixa(base, XJ - 90, t, abre=1.0)
    ida = (t % 50) / 50
    p = misturar(pose(c, "parado"), pose(c, "j_agradece"), suave(min(1, ida * 3)) * (1 - suave(max(0, (ida - 0.7) / 0.3))))
    john_por(c, base, p, XJ)
    c.mapa_frente(base, t + 130)
    c.camera(q, base, (XJ + 20, CHAO - 100), 2.2 - 0.3 * suave(min(1, t / 60)), pixel=True)
    if t >= 30:
        faixa_nome(q, "JOHN", "O GRANDE MÁGICO.", COR_NOME, (t - 30) / 30)


PLANOS = [
    (40, e1_luzes, {16: ("defesa", 0.6)}),
    (56, e2_treme, {4: ("soco", 0.4), 12: ("soco", 0.4), 20: ("soco", 0.4), 40: ("blip", 0.5)}),
    (44, e3_abre, {ABRE: ("puf", 1.0), ABRE + 1: ("confirma", 0.6)}),
    (90, e4_agradece, {0: ("confirma", 0.4)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: SERRADO DE BRINCADEIRA (a caixa serrada do jogo)
# =====================================================================
def serrado(c, base, t_vit):
    """A CAIXA SERRADA da vitória antiga (as 2 mesinhas, a cabeça de um lado e os pés do outro, o serrote), no
    quadro t_vit dela."""
    import vitorias_loja
    l = c.lutador()
    l.x, l.y, l.dir, l.s = XJ, CHAO, 1, c.l.s
    vitorias_loja.john_serrado_ef(l, base, t_vit)


def plateia(q, t, palmas=False):
    """A PLATEIA no escuro (cabecinhas na frente da câmera), batendo PALMAS."""
    w, h = q.get_size()
    rnd = random.Random(7)
    for i in range(18):
        x = i * w / 17 + rnd.uniform(-10, 10)
        y = h - 30 + rnd.uniform(-10, 10)
        r = rnd.uniform(34, 50)
        pygame.draw.circle(q, (14, 10, 22), (int(x), int(y)), int(r))
        if palmas and (t // 5 + i) % 2:
            for lado in (-1, 1):
                pygame.draw.ellipse(q, (24, 18, 32), (x + lado * r * 0.6 - 10, y - r - 16, 20, 26))


def v1_palco(c, q, t, k):
    """1) PUF: aparece a CAIXA (no palco, com o holofote) com ele DENTRO: a cabeça de um lado, os pés do outro."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO + 30, CHAO)
    escurece(base, 0.55)
    holofote(base, XJ, t)
    serrado(c, base, min(t, 19))
    if t < 16:
        fumaca_roxa(base, XJ, CHAO - 50, t / 16)
    coelhinho(base, XJ + 110, CHAO, t, d=-1)
    c.mapa_frente(base, t)
    c.camera(q, base, (XJ + 30, CHAO - 90), 2.0, pixel=True)
    plateia(q, t)
    if t < 12:
        texto_pow(q, "PUF!", (int(w * 0.6), int(h * 0.24)), 56, (220, 190, 255), t)


def v2_serra(c, q, t, k):
    """2) O COELHINHO SERRA no meio (o serrote indo e voltando, a serragem)... e as METADES se SEPARAM!
    Os pés mexem do outro lado. A plateia: OOOH!"""
    w, h = q.get_size()
    import vitorias_loja
    base = c._tela_aux()
    c.mapa(base, t + 40)
    escurece(base, 0.55)
    holofote(base, XJ, t)
    t_vit = vitorias_loja.SERRA_COMECA + t  # (do começo da serra até separar e mexer os pés)
    serrado(c, base, min(t_vit, vitorias_loja.SERRA_JUNTA - 2))
    pula = abs(math.sin(t * 0.5)) * 6
    if t_vit < vitorias_loja.SERRA_SEPARA:  # (serrando: em cima da caixa, segurando o serrote)
        coelhinho(base, XJ + 20, CHAO - 104 - pula, t, d=-1)
    else:  # (depois: pulando de alegria no chão, do lado)
        coelhinho(base, XJ + 150, CHAO - pula * 2, t, d=-1)
    c.mapa_frente(base, t + 40)
    c.camera(q, base, (XJ + 30, CHAO - 80), 2.0, pixel=True)
    plateia(q, t)
    if t_vit < vitorias_loja.SERRA_SEPARA:
        texto_pow(q, "ZIC ZIC ZIC", (int(w * 0.66), int(h * 0.22)), 44, (230, 220, 200), t % 8, giro=0.05)
    elif t_vit > vitorias_loja.SERRA_SEPARA + 6:
        texto_pow(q, "OOOOOH!", (int(w * 0.5), int(h * 0.16)), 60, (255, 240, 200), (t_vit - vitorias_loja.SERRA_SEPARA) % 12)


def v3_inteiro(c, q, t, k):
    """3) As metades JUNTAM, PUF... ele sai INTEIRO e AGRADECE com o coelhinho no ombro, a plateia aplaudindo
    (CLAP CLAP), o confete caindo. O nome."""
    w, h = q.get_size()
    import vitorias_loja
    base = c._tela_aux()
    c.mapa(base, t + 80)
    c.por_oponente(base, "caido", 1.0, XO + 30, CHAO)
    escurece(base, 0.4)
    holofote(base, XJ, t)
    sai = 20
    if t < sai:
        serrado(c, base, vitorias_loja.SERRA_JUNTA + t)
    else:
        ida = ((t - sai) % 50) / 50
        p = misturar(pose(c, "parado"), pose(c, "j_agradece"), suave(min(1, ida * 3)) * (1 - suave(max(0, (ida - 0.7) / 0.3))))
        john_por(c, base, p, XJ)
        if t - sai < 22:
            fumaca_roxa(base, XJ, CHAO - 60, (t - sai) / 22)
        confete(base, t, sai, XJ, CHAO - 120, n=60)
    c.mapa_frente(base, t + 80)
    c.camera(q, base, (XJ + 30, CHAO - 100), 2.0 - 0.2 * suave(min(1, t / 60)), pixel=True)
    plateia(q, t, palmas=t >= sai)
    if t == sai:
        c.tremor = 6
    if t >= sai:
        texto_pow(q, "CLAP CLAP CLAP!", (int(w * 0.5), int(h * 0.16)), 48, (255, 240, 200), (t - sai) % 10, giro=-0.04)
    if t >= 50:
        faixa_nome(q, "JOHN", "E O SHOW ACABOU!", COR_NOME, (t - 50) / 30)


PLANOS_SERRADO = [
    (34, v1_palco, {0: ("puf", 0.8)}),
    (64, v2_serra, {0: ("vento", 0.4), 12: ("vento", 0.4), 24: ("vento", 0.4), 30: ("confirma", 0.5)}),
    (110, v3_inteiro, {10: ("defesa", 0.4), 20: ("puf", 0.9), 22: ("confirma", 0.7)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_SERRADO, titulo, oponente)
