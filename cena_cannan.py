"""CENAS DE ANIME do CANNAN (loja), com as ideias do Gomes.

ENTRADA (RAPEL): close no HELICÓPTERO... close no Cannan SENTADO na bordinha da porta (as pernas balançando),
ele fala no radinho "ESTAMOS PERTO DO ALVO. CÂMBIO."... desce a CORDA, o helicóptero espera em cima e ele chega
na luta.
VITÓRIA (MISSÃO CUMPRIDA): "MISSÃO CUMPRIDA, GENERAL." no rádio... close no helicóptero chegando... a VISÃO DO
PILOTO vendo o Cannan acenando com o derrotado lá embaixo... a corda desce, ele sobe, senta na cadeirinha dele e
começa a bater um papo com o piloto.
O Cannan aparece com o desenho do jogo (poses novas montadas com os ossos dele); o helicóptero e o piloto são
ilustrados.
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

BORDA = (16, 16, 14)
XC, XO = LARGURA * 0.34, LARGURA * 0.74  # o Cannan e o oponente, no mapa
VERDE, VERDE_ESC, VERDE_CLARO = (92, 104, 58), (58, 66, 36), (128, 140, 80)
COR_NOME = (90, 110, 60)
OSSOS = dict(tronco=42, pescoco=16, coxa=32, canela=31, braco=24, ante=22)


def montar(tronco, cabeca, coxa_t, canela_t, coxa_f, canela_f, braco_t, ante_t, braco_f, ante_f, chao=True):
    """Monta uma POSE pelos ÂNGULOS (graus: 0 = pra frente, 90 = pra cima), com os comprimentos de osso do Cannan.
    chao=True: os pés ficam no chão (y = 0)."""
    def va(p, ang, comp):
        a = math.radians(ang)
        return (p[0] + math.cos(a) * comp, p[1] + math.sin(a) * comp)
    qd = (0.0, 0.0)
    pc = va(qd, tronco, OSSOS["tronco"])
    p = dict(qd=qd, pc=pc, cb=va(pc, cabeca, OSSOS["pescoco"]))
    p["jt"] = va(qd, coxa_t, OSSOS["coxa"])
    p["pt"] = va(p["jt"], canela_t, OSSOS["canela"])
    p["jf"] = va(qd, coxa_f, OSSOS["coxa"])
    p["pf"] = va(p["jf"], canela_f, OSSOS["canela"])
    p["ct"] = va(pc, braco_t, OSSOS["braco"])
    p["mt"] = va(p["ct"], ante_t, OSSOS["ante"])
    p["cf"] = va(pc, braco_f, OSSOS["braco"])
    p["mf"] = va(p["cf"], ante_f, OSSOS["ante"])
    base = -min(p["pt"][1], p["pf"][1]) if chao else 0.0
    return {k: (v[0], v[1] + base) for k, v in p.items()}


SENTADO = montar(95, 90, -2, -100, 2, -80, -20, 120, -70, -10)    # na bordinha: pernas pra fora, rádio na boca, canhão no colo
SENTADO_PAPO = montar(98, 92, 0, -95, 4, -85, -60, 20, -70, -10)  # na cadeirinha, à vontade (a mão no joelho)
RAPEL = montar(95, 85, -80, -100, -55, -115, 82, 92, 78, 88)        # pendurado na corda: as mãos lá em cima
RADIO = montar(92, 88, -100, -92, -78, -88, -20, 120, -60, -5)      # em pé, o rádio na boca
ACENA = montar(92, 88, -100, -92, -78, -88, 70, 100, -60, -5)       # em pé, ACENANDO (o antebraço balança)
ALTURA_ASSENTO = SENTADO["qd"][1]  # (do pé até o quadril, sentado: pra pôr o quadril em cima do assento)


def pose(c, nome):
    extra = {"sentado_cannan": SENTADO, "papo": SENTADO_PAPO, "rapel": RAPEL, "radio": RADIO, "acena": ACENA}
    if nome in extra:
        return dict(extra[nome])
    return c.l.poses.get(nome) or c.l.poses["parado"]


def acena(t):
    p = dict(ACENA)
    a = math.radians(100 + 30 * math.sin(t * 0.4))
    ct = p["ct"]
    p["mt"] = (ct[0] + math.cos(a) * OSSOS["ante"], ct[1] + math.sin(a) * OSSOS["ante"])
    return p


def can(c, base, p, x, y=CHAO, d=1):
    c.por(base, p, 1.0, x, y, d, guardar=False)


def balao(q, x, y, txt, k=1.0, lado=1, cor=(255, 255, 255)):
    """BALÃO DE FALA (o texto vai aparecendo letra por letra; k = 0..1). (x, y) = a pontinha do balão."""
    from efeitos import texto
    mostra = txt[:max(1, int(len(txt) * k))]
    larg = 30 + len(txt) * 17
    r = pygame.Rect(0, 0, larg, 66)
    r.midbottom = (int(x + lado * larg * 0.25), int(y - 26))
    r.clamp_ip(q.get_rect().inflate(-20, -100))
    pygame.draw.polygon(q, BORDA, [(x, y), (r.centerx - 12, r.bottom - 4), (r.centerx + 12, r.bottom - 4)])
    pygame.draw.rect(q, BORDA, r.inflate(8, 8), border_radius=22)
    pygame.draw.rect(q, cor, r, border_radius=20)
    pygame.draw.polygon(q, cor, [(x, y - 8), (r.centerx - 8, r.bottom - 6), (r.centerx + 8, r.bottom - 6)])
    texto(q, mostra, 26, BORDA, (r.centerx, r.centery), sombra=False)


def chiado(q, x, y, t):
    """O 'KSHH' do rádio (risquinhos em zigue-zague saindo do rádio)."""
    for i in range(3):
        r = 14 + i * 12 + (t % 6) * 2
        pygame.draw.arc(q, (230, 240, 255), (x - r, y - r, r * 2, r * 2), -0.6, 0.6, 2)


# =====================================================================
# O HELICÓPTERO (ilustrado; e = tamanho: 1 = o tamanho no mapa)
# =====================================================================
def helicoptero(q, x, y, e, t, d=1, porta=True, inclina=0.0, dentro=None):
    """O HELICÓPTERO militar de lado: corpo verde, cabine de vidro, cauda com o rotorzinho, os esquis, a PORTA aberta
    com a cadeirinha, e a HÉLICE girando (borrão). (x, y) = o meio do corpo. dentro(sup, porta_rect) desenha quem está
    na porta (o Cannan sentado), por dentro do helicóptero."""
    W, H = int(720 * e) + 20, int(260 * e) + 20  # (largo: a cauda e a hélice inteiras)
    sup = pygame.Surface((W, H), pygame.SRCALPHA)
    cx, cy = W * (0.58 if d > 0 else 0.42), H * 0.56

    def P(px, py):
        return cx + px * e * d, cy + py * e

    corpo = [P(-120, -10), P(-60, -46), P(60, -50), P(110, -36), P(150, -6), P(140, 30), P(80, 46), P(-80, 44), P(-120, 26)]
    cauda = [P(-118, -8), P(-300, -18), P(-310, -8), P(-300, 4), P(-118, 22)]
    for pts, cor in ((cauda, VERDE), (corpo, VERDE)):
        pygame.draw.polygon(sup, BORDA, pts)
        pygame.draw.polygon(sup, cor, [(px + (cx - px) * 0.02, py + (cy - py) * 0.02) for px, py in pts])
    pygame.draw.polygon(sup, VERDE_ESC, [P(-120, 14), P(140, 18), P(140, 30), P(80, 46), P(-80, 44), P(-120, 26)])
    pygame.draw.polygon(sup, VERDE_CLARO, [P(-60, -42), P(58, -46), P(100, -34), P(-50, -30)])
    pygame.draw.polygon(sup, BORDA, [P(-300, -18), P(-322, -64), P(-306, -64), P(-290, -14)])  # a aleta da cauda
    pygame.draw.polygon(sup, VERDE, [P(-300, -20), P(-318, -60), P(-308, -60), P(-293, -16)])
    vidro = [P(70, -46), P(108, -34), P(146, -6), P(138, 12), P(84, 12)]  # a CABINE de vidro
    pygame.draw.polygon(sup, BORDA, vidro)
    pygame.draw.polygon(sup, (120, 180, 210), [(px + (cx - px) * 0.03, py + (cy - py) * 0.03) for px, py in vidro])
    pygame.draw.polygon(sup, (200, 236, 250), [P(80, -40), P(100, -32), P(90, 4), P(84, 4)])
    if porta:  # a PORTA aberta (o lado de dentro escuro) com a cadeirinha
        pr = pygame.Rect(0, 0, 130 * e, 72 * e)
        pr.center = (int(P(-10, 2)[0]), int(P(-10, 2)[1]))
        pygame.draw.rect(sup, BORDA, pr.inflate(6, 6))
        pygame.draw.rect(sup, (34, 36, 30), pr)
        pygame.draw.rect(sup, (70, 60, 50), (pr.x + pr.w * 0.1, pr.y + pr.h * 0.35, pr.w * 0.22, pr.h * 0.5))  # a cadeirinha
        pygame.draw.line(sup, (150, 150, 140), (pr.x, pr.bottom - 2), (pr.right, pr.bottom - 2), max(2, int(4 * e)))  # a bordinha
        if dentro:
            dentro(sup, pr)
    else:
        pygame.draw.rect(sup, VERDE_ESC, (P(-70, -24)[0] if d > 0 else P(50, -24)[0], P(-70, -24)[1], 120 * e, 56 * e), max(1, int(2 * e)))
    from efeitos import texto
    texto(sup, "CN-01", max(10, int(18 * e)), (230, 230, 210), (int(P(-200, -4)[0]), int(P(-200, -4)[1])), sombra=False)
    for lado in (-1, 1):  # os ESQUIS
        pygame.draw.line(sup, BORDA, P(-60 * 1 + lado * 0, 44), P(-70, 70), max(2, int(5 * e)))
        pygame.draw.line(sup, BORDA, P(60, 44), P(70, 70), max(2, int(5 * e)))
    pygame.draw.line(sup, BORDA, P(-120, 70), P(130, 70), max(3, int(7 * e)))
    pygame.draw.line(sup, (90, 92, 84), P(-118, 69), P(128, 69), max(1, int(3 * e)))
    pygame.draw.line(sup, BORDA, P(0, -48), P(0, -66), max(3, int(8 * e)))  # o MASTRO e a HÉLICE (girando: borrão)
    for i in range(2):
        a = t * 1.3 + i * math.pi
        comp = 240 * e * (0.35 + 0.65 * abs(math.cos(a)))
        pygame.draw.line(sup, (30, 30, 28), (P(0, -66)[0] - comp, P(0, -66)[1]), (P(0, -66)[0] + comp, P(0, -66)[1]), max(2, int(5 * e)))
    borrao = pygame.Rect(0, 0, 480 * e, 22 * e)
    borrao.center = (int(P(0, -66)[0]), int(P(0, -66)[1]))
    pygame.draw.ellipse(sup, (200, 210, 220, 70), borrao)
    rot = (int(P(-308, -10)[0]), int(P(-308, -10)[1]))  # o rotorzinho da cauda
    pygame.draw.circle(sup, (200, 210, 220, 90), rot, int(26 * e))
    pygame.draw.line(sup, (30, 30, 28), (rot[0] + math.cos(t) * 24 * e, rot[1] + math.sin(t) * 24 * e),
                     (rot[0] - math.cos(t) * 24 * e, rot[1] - math.sin(t) * 24 * e), max(1, int(3 * e)))
    if inclina:
        sup = pygame.transform.rotate(sup, inclina)
    q.blit(sup, (int(x - sup.get_width() * (0.58 if d > 0 else 0.42)), int(y - sup.get_height() * 0.56)))
    return sup


def vento_helice(base, x, t, forca=1.0):
    """O VENTO da hélice no chão: poeira girando pros lados e a grama/terra tremendo."""
    rnd = random.Random(t // 3)
    sup = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    for i in range(14):
        lado = -1 if i % 2 else 1
        u = ((t * 3 + i * 17) % 60) / 60
        px = x + lado * (30 + 260 * u)
        py = CHAO - 6 - math.sin(u * math.pi) * 30
        pygame.draw.circle(sup, (210, 200, 180, int(170 * (1 - u) * forca)), (int(px), int(py)), int(8 + 24 * u))
    base.blit(sup, (0, 0))


# =====================================================================
# ENTRADA: RAPEL
# =====================================================================
def ceu(c, q, t, vel=1.0):
    """O céu (o alto do mapa, desfocado) com as nuvens passando rápido."""
    w, h = q.get_size()
    fundo_desfocado(c, q, t, (LARGURA * 0.5, 80), 1.3, 0)
    rnd = random.Random(3)
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(8):
        x = (rnd.uniform(0, w + 400) - t * 9 * vel * rnd.uniform(0.6, 1.4)) % (w + 400) - 200
        y = rnd.uniform(40, h - 60)
        for j in range(4):
            pygame.draw.ellipse(sup, (255, 255, 255, 140), (x + j * 50, y - j % 2 * 14, 140, 54))
    q.blit(sup, (0, 0))


def e1_helicoptero(c, q, t, k):
    """1) CLOSE no HELICÓPTERO voando (a hélice girando, as nuvens passando, TUCTUCTUC)."""
    w, h = q.get_size()
    ceu(c, q, t)
    helicoptero(q, w * 0.5 + math.sin(t * 0.05) * 20, h * 0.5 + math.sin(t * 0.08) * 8, 1.7, t, inclina=4)
    cutscene.linhas_horizontais(q, (255, 255, 255), int(h * 0.15), int(h * 0.85), 10, t, velocidade=40, alfa=60)
    texto_pow(q, "TUC TUC TUC TUC", (int(w * 0.5), int(h * 0.16)), 40, (240, 240, 230), t % 6, giro=-0.04)


def e2_radio(c, q, t, k):
    """2) CLOSE no Cannan SENTADO na bordinha da porta (as pernas balançando, o cabelo no vento), falando no
    radinho: "ESTAMOS PERTO DO ALVO. CÂMBIO." """
    w, h = q.get_size()
    ceu(c, q, t + 50, 1.4)

    def dentro(sup, pr):
        balanco = math.sin(t * 0.2) * 8
        p = pose(c, "sentado_cannan")
        p["pt"] = (p["pt"][0] + balanco * 0.4, p["pt"][1])
        p["pf"] = (p["pf"][0] - balanco * 0.4, p["pf"][1])
        img, pe = c.corpo(p, 1.9, guardar=False)
        quadril_y = pr.bottom - 2
        sup.blit(img, (int(pr.centerx - pe[0]), int(quadril_y + ALTURA_ASSENTO * c.l.s * 1.9 - pe[1])))

    helicoptero(q, w * 0.48, h * 0.42, 3.0, t, dentro=dentro)
    if t >= 8:
        balao(q, w * 0.4, h * 0.42, "ESTAMOS PERTO DO ALVO. CÂMBIO.", min(1, (t - 8) / 26))
    if 34 <= t < 50:
        chiado(q, int(w * 0.44), int(h * 0.5), t)
        texto_pow(q, "KSHH", (int(w * 0.62), int(h * 0.56)), 30, (230, 240, 255), t - 34)


def e3_desce(c, q, t, k):
    """3) No MAPA: o helicóptero parado no alto (a corda pendurada), o vento da hélice levantando poeira no chão,
    e ele DESCENDO de rapel. O oponente olha pra cima."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 100)
    c.por_oponente(base, "defesa" if t > 30 else "parado", 1.0, XO, CHAO)
    hx, hy = XC - 30, 178
    corda_topo = hy + 44
    u = suave(min(1, t / 60))
    y = corda_topo + 140 + (CHAO - corda_topo - 140) * u
    pygame.draw.line(base, (60, 50, 40), (XC, corda_topo), (XC, CHAO), 3)  # a CORDA
    pygame.draw.line(base, (170, 150, 110), (XC, corda_topo), (XC, CHAO), 1)
    if u < 1:
        can(c, base, pose(c, "rapel"), XC - 6, y)
    else:
        can(c, base, misturar(pose(c, "agachado"), pose(c, "parado"), suave(min(1, (t - 60) / 10))), XC)
    vento_helice(base, XC, t, 0.6 + 0.4 * u)
    helicoptero(base, hx, hy, 1.1, t + 100, porta=True)
    c.mapa_frente(base, t + 100)
    c.camera(q, base, (XC + 60, (hy - 80 + CHAO + 20) / 2), 1.25, pixel=True)  # (do helicóptero até o chão)
    if t == 60:
        c.tremor = 8
    if 60 <= t < 74:
        texto_pow(q, "TUM!", (int(w * 0.3), int(h * 0.6)), 50, (255, 240, 220), t - 60)


def e4_chega(c, q, t, k):
    """4) Ele SOLTA a corda, o helicóptero sobe e vai embora (a corda subindo junto)... CONTINÊNCIA. O nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 170)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    sobe = suave(min(1, t / 50))
    hx, hy = XC - 30 + 500 * sobe, 178 - 360 * sobe
    pygame.draw.line(base, (60, 50, 40), (hx + 30, hy + 44), (hx + 30, hy + 44 + 220 * (1 - sobe)), 3)
    p = misturar(pose(c, "parado"), pose(c, "c_continencia"), suave(min(1, max(0, t - 10) / 10)))
    can(c, base, p, XC)
    if sobe < 0.7:
        vento_helice(base, XC, t, 1 - sobe)
    helicoptero(base, hx, hy, 1.1, t + 170, porta=True, inclina=-8 * sobe)
    c.mapa_frente(base, t + 170)
    c.camera(q, base, (XC + 80, CHAO - 150), 1.4, pixel=True)
    if t >= 24:
        faixa_nome(q, "CANNAN", "O SOLDADO DO CANHÃO.", COR_NOME, (t - 24) / 30)


PLANOS = [
    (50, e1_helicoptero, {0: ("vento", 0.6), 25: ("vento", 0.4)}),
    (64, e2_radio, {8: ("blip", 0.5), 34: ("vento", 0.3)}),
    (80, e3_desce, {0: ("vento", 0.5), 60: ("queda", 0.7)}),
    (80, e4_chega, {0: ("vento", 0.5), 12: ("blip", 0.4)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: MISSÃO CUMPRIDA
# =====================================================================
def v1_general(c, q, t, k):
    """1) Do lado do derrotado, no rádio: "MISSÃO CUMPRIDA, GENERAL." """
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    p = misturar(pose(c, "parado"), pose(c, "radio"), suave(min(1, t / 8)))
    can(c, base, p, XC + 80)
    c.mapa_frente(base, t)
    cb = c.ponto(p, "cb", 1.0, XC + 80, CHAO)
    centro, z = (cb[0] + 20, cb[1] + 40), 2.6
    c.camera(q, base, centro, z, pixel=True)
    bx, by = para_tela(centro, z, (cb[0] + 4, cb[1] - 6))
    if t >= 8:
        balao(q, bx, by, "MISSÃO CUMPRIDA, GENERAL.", min(1, (t - 8) / 22))
    if t >= 34:
        chiado(q, int(bx + 30), int(by + 40), t)


def v2_chega(c, q, t, k):
    """2) CLOSE no HELICÓPTERO CHEGANDO (vem de longe, crescendo, freando e inclinando)."""
    w, h = q.get_size()
    ceu(c, q, t + 60, 0.6)
    u = suave(k)
    helicoptero(q, w * (1.1 - 0.6 * u), h * (0.3 + 0.2 * u), 0.8 + 1.6 * u, t, d=-1, inclina=10 * (1 - u) - 4)
    texto_pow(q, "TUC TUC TUC", (int(w * 0.32), int(h * 0.2)), 40, (240, 240, 230), t % 6, giro=0.05)


def v3_piloto(c, q, t, k):
    """3) A VISÃO DO PILOTO: a cabine (o painel, o manche), e lá embaixo pela janela o Cannan ACENANDO, do lado do
    derrotado."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 100)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    can(c, base, acena(t), XC + 80)
    vento_helice(base, XC + 80, t, 0.7)
    c.mapa_frente(base, t + 100)
    balanco = math.sin(t * 0.06) * 10
    base = base.copy()  # (o fundo desfocado usa a mesma tela auxiliar: guarda a cena antes)
    fundo_desfocado(c, q, t + 100, (LARGURA * 0.5, 100), 1.0, 0)  # (o céu em volta)
    e = 0.42  # (o mapa inteiro, BEM LÁ EMBAIXO: pequenininho, com o chão acima do painel)
    pequeno = pygame.transform.scale(base, (int(LARGURA * e), int(ALTURA * e)))
    iw, ih = pequeno.get_size()
    x0, y0 = int(w / 2 - iw / 2 - w * 0.1 + balanco), int(h * 0.64 - CHAO * e)  # (ele fora da coluna do meio)
    so_mapa = pygame.Surface((LARGURA, ALTURA))  # (os lados: só o CENÁRIO espelhado, sem os personagens)
    c.mapa(so_mapa, t + 100)
    c.mapa_frente(so_mapa, t + 100)
    espelho = pygame.transform.flip(pygame.transform.scale(so_mapa, (iw, ih)), True, False)
    for i in range(-2, 3):
        q.blit(pequeno if i % 2 == 0 else espelho, (x0 + i * iw, y0))
    if y0 > 0:  # (o céu de cima: a primeira linha do cenário esticada)
        q.blit(pygame.transform.scale(pequeno.subsurface((0, 0, iw, 2)), (w, y0)), (0, 0))
    cab = pygame.Surface((w, h), pygame.SRCALPHA)  # a CABINE (moldura, coluna do meio, painel)
    pygame.draw.polygon(cab, (30, 32, 28), [(0, 0), (w, 0), (w, h * 0.22), (w * 0.75, h * 0.12), (w * 0.25, h * 0.12), (0, h * 0.22)])
    pygame.draw.polygon(cab, (30, 32, 28), [(0, 0), (w * 0.07, h * 0.2), (w * 0.05, h * 0.8), (0, h)])
    pygame.draw.polygon(cab, (30, 32, 28), [(w, 0), (w * 0.93, h * 0.2), (w * 0.95, h * 0.8), (w, h)])
    pygame.draw.polygon(cab, (30, 32, 28), [(w * 0.49, h * 0.12), (w * 0.51, h * 0.12), (w * 0.52, h * 0.7), (w * 0.48, h * 0.7)])
    pygame.draw.rect(cab, (46, 48, 42), (0, h * 0.7, w, h * 0.3))  # o PAINEL
    pygame.draw.rect(cab, (70, 74, 64), (0, h * 0.7, w, 8))
    for i in range(6):  # os relógios do painel
        gx, gy = w * (0.14 + i * 0.145), h * 0.82
        pygame.draw.circle(cab, (14, 14, 12), (int(gx), int(gy)), 30)
        pygame.draw.circle(cab, (200, 230, 200), (int(gx), int(gy)), 26, 2)
        a = t * 0.05 * (1 + i % 3) + i
        pygame.draw.line(cab, (240, 120, 60), (gx, gy), (gx + math.cos(a) * 20, gy + math.sin(a) * 20), 3)
    for i in range(8):  # as luzinhas
        pygame.draw.circle(cab, (60, 230, 90) if (t // 10 + i) % 3 else (230, 60, 60), (int(w * 0.3 + i * 40), int(h * 0.74 + 4)), 4)
    pygame.draw.line(cab, (20, 20, 18), (w * 0.5, h), (w * 0.5 + balanco * 2, h * 0.76), 22)  # o MANCHE
    pygame.draw.circle(cab, (20, 20, 18), (int(w * 0.5 + balanco * 2), int(h * 0.76)), 18)
    for lado in (-1, 1):  # as luvas do piloto no manche
        pygame.draw.circle(cab, (70, 64, 50), (int(w * 0.5 + balanco * 2 + lado * 20), int(h * 0.78)), 16)
    reflexo = pygame.Surface((w, h), pygame.SRCALPHA)  # o reflexo no vidro
    pygame.draw.polygon(reflexo, (255, 255, 255, 30), [(w * 0.1, h * 0.2), (w * 0.2, h * 0.2), (w * 0.1, h * 0.65), (w * 0.06, h * 0.65)])
    q.blit(reflexo, (0, 0))
    q.blit(cab, (0, 0))
    if t >= 20:
        texto_pow(q, "Olha ele lá!", (int(w * 0.7), int(h * 0.3)), 34, (240, 240, 230), (t - 20) % 12, giro=0.04)


def v4_sobe(c, q, t, k):
    """4) No MAPA: a CORDA desce do helicóptero, ele SEGURA e SOBE (o vento da hélice, a poeira)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 160)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    xc = XC + 80
    hx, hy = xc - 30, 178
    topo = hy + 44
    desce = suave(min(1, t / 16))
    pygame.draw.line(base, (60, 50, 40), (xc, topo), (xc, topo + (CHAO - topo) * desce), 3)
    pygame.draw.line(base, (170, 150, 110), (xc, topo), (xc, topo + (CHAO - topo) * desce), 1)
    if t < 22:
        can(c, base, misturar(acena(t), pose(c, "rapel"), suave(max(0, (t - 14) / 8))), xc - 6)
    else:
        u = suave(min(1, (t - 22) / 36))
        can(c, base, pose(c, "rapel"), xc - 6, CHAO - (CHAO - topo - 120) * u)
    vento_helice(base, xc, t, 1.0)
    helicoptero(base, hx, hy, 1.1, t + 160, porta=True)
    c.mapa_frente(base, t + 160)
    c.camera(q, base, (xc + 40, (hy - 80 + CHAO + 20) / 2), 1.25, pixel=True)  # (do helicóptero até o chão)


PAPO = ("cannan", "piloto", "cannan", "piloto", "cannan", "piloto")  # (quem fala, de 24 em 24 quadros: só as boquinhas)


def cabeca_costas(q, x, y, e, olha, falando, t, cannan, pk):
    """A CABEÇA vista de TRÁS (por cima do encosto), virando pro lado do outro (olha: -1 = pra esquerda,
    +1 = pra direita, 0 = pra frente): de perfil aparece o rosto e a BOQUINHA mexendo quando fala."""
    vira = abs(olha)
    if cannan:  # o Cannan: cabelo castanho meio comprido
        pele, cabelo = pk.get("p", (226, 178, 140)), pk.get("h", (92, 60, 36))
    else:  # o piloto: capacete verde
        pele, cabelo = (226, 180, 140), VERDE
    cab = pygame.Rect(0, 0, 62 * e, 70 * e)
    cab.center = (int(x), int(y))
    pygame.draw.ellipse(q, BORDA, cab.inflate(6, 6))
    pygame.draw.ellipse(q, pele, cab)
    if cannan:  # o CABELO por cima (de trás), caindo até a nuca, mexendo com o vento
        nuca = [(x - 34 * e, y - 6 * e), (x - 30 * e, y - 36 * e), (x, y - 42 * e), (x + 30 * e, y - 36 * e), (x + 34 * e, y - 6 * e)]
        lado = -olha * 14 * e
        pontas = [(x + 34 * e + lado, y + 26 * e), (x + 16 * e + lado, y + 40 * e + math.sin(t * 0.3) * 3 * e),
                  (x + lado, y + 34 * e), (x - 16 * e + lado, y + 42 * e + math.sin(t * 0.3 + 1) * 3 * e), (x - 34 * e + lado, y + 26 * e)]
        pygame.draw.polygon(q, BORDA, [(px, py - 2) for px, py in nuca + pontas])
        pygame.draw.polygon(q, cabelo, nuca + pontas)
        for i in range(5):  # as mechas
            mx = x - 24 * e + i * 12 * e + lado * 0.5
            pygame.draw.line(q, tuple(max(0, v - 30) for v in cabelo), (mx, y - 30 * e), (mx + lado * 0.4, y + 30 * e), max(1, int(2 * e)))
    else:  # o CAPACETE do piloto (de trás) e o fone
        capa = pygame.Rect(0, 0, 70 * e, 56 * e)
        capa.midtop = (int(x), int(y - 40 * e))
        pygame.draw.ellipse(q, BORDA, capa.inflate(6, 6))
        pygame.draw.ellipse(q, VERDE, capa)
        pygame.draw.ellipse(q, VERDE_CLARO, (capa.x + capa.w * 0.25, capa.y + 6 * e, capa.w * 0.3, capa.h * 0.3))
        pygame.draw.rect(q, BORDA, (x - 34 * e, y + 2 * e, 68 * e, 6 * e))  # a tira do fone
        for lado in (-1, 1):
            pygame.draw.circle(q, BORDA, (int(x + lado * 32 * e), int(y + 4 * e)), int(10 * e))
    if vira > 0.05:  # o ROSTO de PERFIL, saindo pro lado (por cima do cabelo/capacete): olho, nariz e a BOQUINHA
        fx = x + olha * 30 * e
        pygame.draw.ellipse(q, BORDA, (fx - 15 * e, y - 22 * e, 30 * e, 46 * e))
        pygame.draw.ellipse(q, pele, (fx - 13 * e, y - 20 * e, 26 * e, 42 * e))
        pygame.draw.polygon(q, pele, [(fx + olha * 10 * e, y - 4 * e), (fx + olha * 19 * e, y + 4 * e), (fx + olha * 10 * e, y + 7 * e)])  # o nariz
        pygame.draw.lines(q, BORDA, False, [(fx + olha * 11 * e, y - 4 * e), (fx + olha * 19 * e, y + 4 * e), (fx + olha * 10 * e, y + 7 * e)], max(1, int(e)))
        pygame.draw.circle(q, BORDA, (int(fx + olha * 5 * e), int(y - 7 * e)), max(2, int(3.4 * e)))  # o olho
        if cannan:
            pygame.draw.line(q, pk.get("s", (170, 80, 70)), (fx - olha * 2 * e, y + 2 * e), (fx + olha * 5 * e, y - 3 * e), max(1, int(2 * e)))  # a cicatriz
            pygame.draw.polygon(q, cabelo, [(fx - 14 * e, y - 22 * e), (fx + olha * 12 * e, y - 24 * e), (fx - olha * 8 * e, y - 6 * e)])  # a franja
        bx, by = fx + olha * 9 * e, y + 13 * e  # a BOQUINHA
        if falando and (t // 4) % 2:
            pygame.draw.ellipse(q, (110, 30, 30), (bx - 4 * e, by - 3 * e, 8 * e, 9 * e))
            pygame.draw.ellipse(q, BORDA, (bx - 4 * e, by - 3 * e, 8 * e, 9 * e), max(1, int(e)))
        else:
            pygame.draw.line(q, BORDA, (bx - 4 * e, by), (bx + 3 * e, by), max(1, int(2 * e)))


def v5_papo(c, q, t, k):
    """5) A CÂMERA LÁ ATRÁS, dentro do helicóptero: os dois bancos da frente, o PILOTO e o CANNAN sentados lado a
    lado, o céu passando pelo para-brisa... e eles batendo papo (sem texto: só viram a cabeça e as BOQUINHAS mexem)."""
    w, h = q.get_size()
    ceu(c, q, t, 1.2)
    balanco = math.sin(t * 0.07) * 4
    sup = pygame.Surface((w, h), pygame.SRCALPHA)  # a CABINE: o teto, as colunas e o painel embaixo do para-brisa
    pygame.draw.polygon(sup, (40, 44, 34), [(0, 0), (w, 0), (w, h * 0.16), (0, h * 0.16)])
    pygame.draw.polygon(sup, (40, 44, 34), [(0, 0), (w * 0.08, h * 0.16), (w * 0.06, h), (0, h)])
    pygame.draw.polygon(sup, (40, 44, 34), [(w, 0), (w * 0.92, h * 0.16), (w * 0.94, h), (w, h)])
    pygame.draw.polygon(sup, (40, 44, 34), [(w * 0.49, h * 0.16), (w * 0.51, h * 0.16), (w * 0.52, h * 0.55), (w * 0.48, h * 0.55)])
    pygame.draw.rect(sup, (50, 54, 44), (0, h * 0.52, w, h * 0.5))  # o painel
    for i in range(10):
        pygame.draw.circle(sup, (60, 230, 90) if (t // 10 + i) % 3 else (230, 60, 60), (int(w * 0.14 + i * w * 0.08), int(h * 0.56)), 4)
    q.blit(sup, (0, 0))
    pk = {k_: c.cor(k_, v) for k_, v in __import__("cannan").PALETA.items()}
    i = min(len(PAPO) - 1, t // 24)
    fala = PAPO[i]
    cx_p, cx_c = w * 0.3, w * 0.7  # (o piloto na esquerda, o Cannan na direita)
    for cx, quem in ((cx_p, "piloto"), (cx_c, "cannan")):
        banco = pygame.Rect(0, 0, w * 0.28, h * 0.52)  # o ENCOSTO do banco (de trás)
        banco.midtop = (int(cx), int(h * 0.62 + balanco))
        pygame.draw.rect(q, BORDA, banco.inflate(8, 8), border_radius=24)
        pygame.draw.rect(q, (64, 70, 50), banco, border_radius=22)
        pygame.draw.rect(q, (80, 86, 62), (banco.x + 14, banco.y + 12, banco.w - 28, 14), border_radius=6)
        for j in range(4):  # o estofado
            pygame.draw.line(q, (52, 58, 40), (banco.x + 20, banco.y + 40 + j * 30), (banco.right - 20, banco.y + 40 + j * 30), 3)
        if quem == "cannan":  # o CANHÃO no braço, aparecendo do lado do banco
            pygame.draw.rect(q, BORDA, (banco.right - 10, banco.y + 30, 54, 90), border_radius=12)
            pygame.draw.rect(q, pk.get("c", (140, 150, 160)), (banco.right - 6, banco.y + 34, 46, 82), border_radius=10)
            for j in range(4):
                pygame.draw.line(q, pk.get("g", (130, 220, 255)), (banco.right + 2, banco.y + 46 + j * 18), (banco.right + 32, banco.y + 46 + j * 18), 3)
        olha = (1 if quem == "piloto" else -1) * (0.9 if fala == quem or (t % 24) > 6 else 0.4)
        cabeca_costas(q, cx, h * 0.52 + balanco, 2.2, olha, fala == quem, t, quem == "cannan", pk)
    if t >= 110:
        faixa_nome(q, "CANNAN", "MISSÃO CUMPRIDA.", COR_NOME, (t - 110) / 30)


PLANOS_MISSAO = [
    (50, v1_general, {8: ("blip", 0.5), 34: ("vento", 0.2)}),
    (44, v2_chega, {0: ("vento", 0.6)}),
    (60, v3_piloto, {0: ("vento", 0.4)}),
    (60, v4_sobe, {0: ("vento", 0.5)}),
    (146, v5_papo, {0: ("vento", 0.3)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_MISSAO, titulo, oponente)
