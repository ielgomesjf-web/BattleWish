"""ENTRADAS DA LOJA (2 por lutador, escolhidas pelo Gomes). Duram a entrada inteira (~1,8 s) e terminam com o
lutador parado no lugar dele. entrada(l, t, jogo) mexe no lutador; entrada_efeito(l, tela, t) desenha.
Toda entrada chama final() no fim (devolve o tamanho, a pose, o sumiço e o lugar), pra nada ficar preso na luta."""
import math
import random

import pygame

import extras
import som
from config import *  # noqa: F401,F403
from golpes import suave
from max10 import brilho, fogo, fumaca
from provocacoes_loja import POSES_EXTRA

PRECO = 100
FIM = DURACAO_ENTRADA - 10


def xf(l):
    return l.extra["entrada_x"]


def pz(l, nome):
    return dict(l.poses.get(nome) or POSES_EXTRA.get(nome) or l.poses["parado"])


def final(l, t):
    """Terminou: no lugar, tamanho normal, aparecendo, sem pose presa."""
    if t >= FIM:
        l.x, l.y = xf(l), CHAO
        l.s = l.f["tam"]
        l.angulo = 0
        l.esconde = False
        l.disfarce = None
        l.sobrepor = {}
        l.extra.pop("lobo_some", None)
        return True
    return False


def borda(l):
    """A borda da tela de onde ele vem (atrás dele)."""
    return (PAREDE_E - 70) if l.dir > 0 else (PAREDE_D + 70)


# =====================================================================
# MAX-10
# =====================================================================
CAP_CAI, CAP_ABRE, CAP_SAI, CAP_SOBE = 26, 44, 58, 76


def capsula_x(l):
    return xf(l) - l.dir * 46 * l.s


def max_capsula(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.y = CHAO
    if t < CAP_SAI:  # dentro da cápsula
        l.esconde = True
        l.x = capsula_x(l)
    else:  # sai andando pra frente
        l.esconde = False
        k = suave(min(1, (t - CAP_SAI) / 18))
        l.x = capsula_x(l) + (xf(l) - capsula_x(l)) * k
        l.sobrepor = pz(l, ("andar1", "andar2", "andar3", "andar4")[(t // 5) % 4]) if k < 1 else pz(l, "vitoria")
        if k >= 1 and t > CAP_SOBE + 14:
            l.sobrepor = {}
    if t == CAP_CAI:
        som.tocar("queda")
        som.tocar("explosao", 0.5)
        jogo.tremer(16)
        fumaca(jogo, capsula_x(l), CHAO - 4, 18, (200, 196, 190), 6, -1.2)
    if CAP_CAI < t < CAP_ABRE and t % 4 == 0:  # o vapor chiando pelas frestas
        for lado in (-1, 1):
            fumaca(jogo, capsula_x(l) + lado * 34 * l.s, CHAO - 50 * l.s, 1, (236, 236, 242), 2.5, -0.6)
    if t == CAP_ABRE:
        som.tocar("defesa", 0.7)
        fumaca(jogo, capsula_x(l), CHAO - 70 * l.s, 12, (240, 240, 246), 4, -1.5)
    if t == CAP_SOBE:
        som.tocar("foguete", 0.6)
    l.t += 1


def max_capsula_ef(l, tela, t):
    s = l.s
    x = capsula_x(l)
    if t < CAP_CAI:
        k = t / CAP_CAI
        y = -60 + (CHAO + 60) * k * k
    elif t < CAP_SOBE:
        y = CHAO
    else:  # vai embora pro céu
        u = t - CAP_SOBE
        y = CHAO - u * u * 1.3
    if y < -200:
        return
    w, h = 74 * s, 132 * s
    if t < CAP_CAI or t >= CAP_SOBE:  # o fogo do foguete embaixo
        for i in range(3):
            fy = y + 6 + i * 10 + (t % 3) * 3
            brilho(tela, (int(x), int(fy)), int((22 - i * 5) * s), (255, 160, 60), 180)
        pygame.draw.polygon(tela, (255, 220, 120), [(x - 14 * s, y), (x + 14 * s, y), (x, y + 40 * s + (t % 4) * 4)])
    corpo = pygame.Rect(0, 0, w, h * 0.72)
    corpo.midbottom = (int(x), int(y))
    topo = pygame.Rect(0, 0, w, h * 0.56)
    topo.midbottom = (int(x), int(corpo.y + h * 0.2))
    pygame.draw.rect(tela, (20, 22, 28), corpo.inflate(6, 6), border_radius=10)
    pygame.draw.ellipse(tela, (20, 22, 28), topo.inflate(6, 6))
    pygame.draw.ellipse(tela, (150, 156, 168), topo)
    pygame.draw.rect(tela, (150, 156, 168), corpo, border_radius=8)
    pygame.draw.line(tela, (196, 200, 210), (corpo.x + 8, corpo.y - 10), (corpo.x + 8, corpo.bottom - 10), 4)  # brilho
    for k in range(4):  # a faixa amarela e preta
        pygame.draw.rect(tela, (230, 190, 40) if k % 2 else (30, 30, 34), (corpo.x + k * w / 4, corpo.bottom - 18 * s, w / 4, 8 * s))
    for rx in (0.15, 0.85):  # rebites
        for ry in (0.2, 0.6):
            pygame.draw.circle(tela, (90, 94, 104), (int(corpo.x + w * rx), int(corpo.y + corpo.h * ry)), 3)
    # a porta da frente (gira abrindo) e a janela com os olhos vermelhos
    porta = pygame.Rect(0, 0, w * 0.56, h * 0.62)
    porta.midbottom = (int(x), int(y - 20 * s))
    abre = suave(min(1, max(0, (t - CAP_ABRE) / 10)))
    if abre < 1:
        pygame.draw.rect(tela, (12, 12, 16), porta, border_radius=12)
        if t < CAP_SAI:  # os olhos dele lá dentro
            brilho(tela, (int(x + l.dir * 6 * s), int(porta.y + 26 * s)), int(14 * s), (255, 40, 30), 200)
        largura = porta.w * (1 - abre)
        p2 = pygame.Rect(0, 0, max(2, largura), porta.h)
        p2.midbottom = (int(porta.x + (porta.w - largura / 2) if l.dir > 0 else porta.x + largura / 2), porta.bottom)
        pygame.draw.rect(tela, (120, 126, 138), p2, border_radius=12)
        pygame.draw.rect(tela, (20, 22, 28), p2, 3, border_radius=12)
        if largura > 20:
            janela = (p2.centerx, p2.y + 24 * s)
            pygame.draw.circle(tela, (20, 22, 28), janela, int(12 * s))
            pygame.draw.circle(tela, (90, 160, 200), janela, int(10 * s))
            pygame.draw.circle(tela, (200, 240, 255), (janela[0] - 3, janela[1] - 3), int(3 * s))
    else:
        pygame.draw.rect(tela, (12, 12, 16), porta, border_radius=12)


MONTA_PECAS = ((0.70, 1.00, (-520, 140), 8), (0.42, 0.70, (560, 60), 22), (0.20, 0.42, (-420, -260), 36),
               (0.00, 0.20, (80, -420), 50))
MONTA_PRONTO = 64


def max_montagem(l, t, jogo):
    l.x, l.y = xf(l), CHAO
    if not final(l, t):
        l.esconde = t < MONTA_PRONTO
        l.sobrepor = pz(l, "vitoria") if MONTA_PRONTO <= t < 86 else {}
    for (_, _, _, t0) in MONTA_PECAS:
        if t == t0 + 10:
            som.tocar("defesa", 0.6)
            jogo.tremer(3)
    if t == MONTA_PRONTO:
        som.tocar("carga")
        jogo.tremer(6)
    l.t += 1


def max_montagem_ef(l, tela, t):
    from provocacoes_loja import sprite
    if t >= MONTA_PRONTO:
        if t < MONTA_PRONTO + 16:  # os olhos acendendo vermelhos
            cb = l.ponto(l.pose_vista or l.pose_atual(), "cb")
            brilho(tela, (int(cb[0] + l.dir * 6 * l.s), int(cb[1])), int(34 - (t - MONTA_PRONTO) * 1.5), (255, 40, 30), 230)
        return
    img, (px, py) = sprite(l, l.poses["parado"])
    w, h = img.get_size()
    for (a, b, (dx, dy), t0) in MONTA_PECAS:  # os pedaços de verdade do robô voando e se encaixando
        k = suave(min(1, max(0, (t - t0) / 12)))
        if k <= 0:
            continue
        faixa = img.subsurface(pygame.Rect(0, int(a * h), w, max(1, int((b - a) * h))))
        x = xf(l) - px + dx * (1 - k) * l.dir
        y = CHAO - py + a * h + dy * (1 - k)
        if k < 1:
            faixa = pygame.transform.rotate(faixa, (1 - k) * 90 * (1 if dx > 0 else -1))
        tela.blit(faixa, (x, y))
        if 0.9 < k < 1 or t - t0 in (12, 13):  # a faísca do encaixe
            brilho(tela, (int(xf(l)), int(CHAO - py + b * h)), 20, (255, 230, 150), 200)


# =====================================================================
# RIB
# =====================================================================
def rib_shurikens(l, t, jogo):
    l.x = xf(l)
    if not final(l, t):
        if t < 36:
            l.esconde, l.y = True, CHAO
        else:
            k = min(1, (t - 36) / 30)
            l.esconde = False
            l.y = -80 + (CHAO + 80) * suave(k)
            l.angulo = (1 - k) * math.tau * 2
            l.sobrepor = pz(l, "pulo" if k < 1 else "agachado")
    if t == 66:
        som.tocar("queda", 0.6)
        fumaca(jogo, l.x, CHAO - 4, 8, (200, 200, 210), 3, -1)
    if t in (6, 12, 18, 24, 30):
        som.tocar("shuriken", 0.3)
    l.t += 1


def rib_shurikens_ef(l, tela, t):
    import ult2
    x = xf(l)
    for i, dx in enumerate((-80, -40, 40, 80, 120)):
        t0 = 6 + i * 6
        if t < t0:
            continue
        k = min(1, (t - t0) / 8)
        sx = x + dx * l.s - (1 - k) * 60
        sy = -40 + (CHAO - 8 + 40) * k
        if t >= 100:
            continue
        if k < 1:  # o rastro caindo
            pygame.draw.line(tela, (220, 230, 245), (sx + 60 * 0.4, sy - 80), (sx, sy), 2)
        ult2.desenha_shuriken(tela, sx, sy, 16 * l.s, 0.6 if k >= 1 else t * 0.8)
        if k >= 1 and t - t0 < 12:  # TUC: fincou
            pygame.draw.circle(tela, (240, 240, 250), (int(sx), int(CHAO - 4)), int(4 + (t - t0 - 8) * 2), 1)


def rib_cipo(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    piv = (xf(l) - l.dir * 60, -20)
    comp = CHAO - 150
    if t < 40:  # balançando no cipó (vem lá de trás, de fora da tela)
        a = (-1.25 + 1.45 * suave(t / 40)) * l.dir
        l.x = piv[0] + math.sin(a) * comp
        l.y = piv[1] + math.cos(a) * comp + 110 * l.s
        l.sobrepor = pz(l, "r_puxa_ar" if l.poses.get("r_puxa_ar") else "pulo")
    elif t < 56:  # soltou: cai
        k = (t - 40) / 16
        l.x = xf(l)
        l.y = (CHAO - 50) + 50 * k * k
        l.sobrepor = pz(l, "pulo")
    else:
        l.x, l.y = xf(l), CHAO
        l.sobrepor = pz(l, "agachado") if t < 70 else {}
        if t == 56:
            som.tocar("queda", 0.6)
            fumaca(jogo, l.x, CHAO - 4, 6, (170, 150, 110), 2, -1)
    l.t += 1


def rib_cipo_ef(l, tela, t):
    if t >= 52:
        return
    piv = (xf(l) - l.dir * 60, -20)
    if t >= 40:  # soltou: o cipó volta balançando sozinho
        k = (t - 40) / 12
        mx, my = piv[0] + math.sin(0.2 * l.dir * (1 - k)) * (CHAO - 150), piv[1] + (CHAO - 150)
    else:
        mx, my = l.x, l.y - 110 * l.s
    pygame.draw.line(tela, (40, 70, 20), piv, (mx, my), 5)
    pygame.draw.line(tela, (90, 150, 50), piv, (mx, my), 3)


# =====================================================================
# TRAFO
# =====================================================================
def trafo_contrario(l, t, jogo):
    from personagens import PERSONAGENS
    if "falso" not in l.extra:
        outros = [f for f in PERSONAGENS if f["nome"] != "TRAFO"]
        l.extra["falso"] = random.Random(getattr(jogo, "t_total", 0) + 5).choice(outros)
    if final(l, t):
        l.t += 1
        return
    de = borda(l)
    if t < 40:  # chega andando disfarçado
        l.x = de + (xf(l) - de) * suave(t / 40)
        l.disfarce = l.extra["falso"]
        l.sobrepor = pz(l, ("andar1", "andar2", "andar3", "andar4")[(t // 8) % 4])
    elif t < 62:
        l.x = xf(l)
        l.sobrepor = pz(l, "parado")
    else:
        if t == 62:  # e vira o Trafo rosnando
            l.disfarce = None
            fumaca(jogo, l.x, l.y - 60, 14, (200, 220, 160), 4, -1)
            som.tocar("puf")
            som.tocar("uivo", 0.5)
        l.sobrepor = pz(l, "t_agacha")
    l.t += 1


def trafo_contrario_ef(l, tela, t):
    if 44 <= t < 62:  # o sorrisinho
        import ult2
        ult2.balao(tela, "hehe...", (l.x, l.y - 140 * l.s))


def trafo_parede(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    parede = PAREDE_E - 10 if l.dir > 0 else PAREDE_D + 10
    if t < 30:  # correndo PARA CIMA pela parede, de lado
        l.x = parede
        l.y = CHAO - suave(t / 30) * 220
        l.angulo = -l.dir * math.pi / 2
        l.sobrepor = pz(l, ("t_corre1", "t_corre2")[(t // 5) % 2])
    elif t < 58:  # salta da parede e cai no lugar
        k = (t - 30) / 28
        l.angulo = -l.dir * math.pi / 2 * (1 - k)
        l.x = parede + (xf(l) - parede) * k
        l.y = (CHAO - 220) + 220 * k * k - math.sin(k * math.pi) * 60
        l.sobrepor = pz(l, "t_pulo")
    else:
        if t == 58:
            som.tocar("queda", 0.7)
            fumaca(jogo, xf(l), CHAO - 4, 8, (150, 130, 100), 3, -1)
        l.angulo = 0
        l.x, l.y = xf(l), CHAO
        l.sobrepor = pz(l, "t_agacha") if t < 80 else {}
    l.t += 1


# =====================================================================
# KING RIP
# =====================================================================
def king_medita(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x = xf(l)
    if t < 54:
        l.y = CHAO
        l.sobrepor = pz(l, "sentado")
    elif t < 72:  # levanta num salto
        k = (t - 54) / 18
        l.y = CHAO - math.sin(k * math.pi) * 90
        l.sobrepor = pz(l, "pulo")
        if t == 54:
            som.tocar("vento")
    else:
        l.y = CHAO
        l.sobrepor = pz(l, "k_gira" if t < 90 else "k_bastao")
    l.t += 1


def king_medita_ef(l, tela, t):
    if t < 54:
        cb = l.ponto(l.pose_vista or l.pose_atual(), "cb")
        brilho(tela, (int(cb[0]), int(cb[1])), 30, (180, 220, 255), 50 + int(30 * math.sin(t * 0.2)))
    if t == 52 or t == 53:  # abre os olhos
        cb = l.ponto(l.pose_vista or l.pose_atual(), "cb")
        brilho(tela, (int(cb[0]), int(cb[1])), 40, (255, 255, 255), 220)


def king_folha(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x, l.y = xf(l), CHAO
    l.sobrepor = pz(l, "k_bastao" if not 58 <= t < 70 else "k_gira")
    if t == 60:
        som.tocar("vento", 0.8)
    l.t += 1


def folha(tela, x, y, a, metade=0, e=3.0):
    """A folha GRANDE (com contorno e as nervuras). metade = -1/1: só aquela metade (cortada)."""
    c, s = math.cos(a), math.sin(a)
    pts = [(0, -10), (5, -6), (6, -2), (5, 4), (4, 8), (0, 12), (-4, 8), (-5, 4), (-6, -2), (-5, -6)]
    if metade:
        pts = [p for p in pts if p[0] * metade >= 0] + [(0, 12), (0, -10)] if metade > 0 else \
            [(0, -10)] + [p for p in pts if p[0] * metade >= 0] + [(0, 12)]
    tp = [(x + (px * c - py * s) * e, y + (px * s + py * c) * e) for px, py in pts]
    pygame.draw.polygon(tela, (60, 140, 50), tp)
    pygame.draw.polygon(tela, (20, 50, 16), tp, 2)
    for k in (-6, 0, 6):  # as nervuras
        a1 = (x + (0 * c - k * s) * e, y + (0 * s + k * c) * e)
        a2 = (x + ((3 if metade >= 0 else -3) * c - (k - 3) * s) * e, y + ((3 if metade >= 0 else -3) * s + (k - 3) * c) * e)
        pygame.draw.line(tela, (40, 100, 34), a1, a2, 1)
    pygame.draw.line(tela, (30, 80, 26), (x + 10 * s * e, y - 10 * c * e), (x - 12 * s * e, y + 12 * c * e), 2)


def king_folha_ef(l, tela, t):
    x0 = xf(l) + l.dir * 40 * l.s
    if t < 60:
        k = t / 60
        folha(tela, x0 + math.sin(t * 0.15) * 30, -20 + (CHAO - 120 * l.s + 20) * k, math.sin(t * 0.2) * 0.8)
    elif t < 100:
        u = t - 60
        for lado in (-1, 1):  # as duas metades caindo
            folha(tela, x0 + lado * (6 + u * 1.2), CHAO - 120 * l.s + u * u * 0.08, u * 0.2 * lado, lado)
        if u < 8:  # o CORTE (risco branco em arco, bem rápido)
            k = u / 8
            pygame.draw.arc(tela, (255, 255, 255), (x0 - 70, CHAO - 120 * l.s - 50, 140, 100), 0.2 + k, 2.6 + k, 4)
            pygame.draw.line(tela, (255, 255, 230), (x0 - 50, CHAO - 140 * l.s), (x0 + 50, CHAO - 100 * l.s), 2)


# =====================================================================
# CANNAN
# =====================================================================
def cannan_rapel(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x = xf(l)
    if t < 64:
        l.y = -60 + (CHAO + 60) * suave(t / 64)
        p = pz(l, "pulo")
        pc = p["pc"]
        p["cf"], p["mf"] = (pc[0] + 6, pc[1] + 22), (pc[0] + 6, pc[1] + 44)  # pendurado na corda pela mão
        l.sobrepor = p
    else:
        l.y = CHAO
        if t == 64:
            som.tocar("queda", 0.6)
            fumaca(jogo, l.x, CHAO - 4, 6, (170, 160, 140), 2, -1)
        l.sobrepor = pz(l, "c_continencia") if t < 90 else {}
    l.t += 1


def cannan_rapel_ef(l, tela, t):
    if t >= 90:
        return
    if t < 64:  # a corda até a MÃO dele (descendo junto)
        m = l.ponto(l.pose_vista or l.pose_atual(), "mf")
        x, fim = m[0], m[1]
    else:  # soltou: a corda balança e sobe embora
        x = xf(l) + l.dir * 6 * l.s + math.sin(t * 0.4) * 8 * (1 - (t - 64) / 26)
        fim = CHAO - 140 * l.s - (t - 64) * 14
    if fim > 0:
        pygame.draw.line(tela, (30, 24, 14), (x, 0), (x, fim), 6)
        pygame.draw.line(tela, (150, 120, 70), (x, 0), (x, fim), 3)
        for y in range(8, int(fim), 14):  # a trança da corda
            pygame.draw.line(tela, (110, 86, 46), (x - 2, y), (x + 2, y + 5), 1)


def cannan_caixa(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x, l.y = xf(l), CHAO
    l.sobrepor = pz(l, "parado" if t < 40 else "chute" if t < 50 else "c_canhao" if t < 86 else "parado")
    if t == 30:
        som.tocar("queda")
        jogo.tremer(8)
    if t == 44:
        som.tocar("chute")
    l.t += 1


def cannan_caixa_ef(l, tela, t):
    x = xf(l) + l.dir * 60 * l.s
    w = 46 * l.s
    if t < 30:
        y = -60 + (CHAO + 60) * suave(t / 30)
        pygame.draw.ellipse(tela, (90, 120, 70), (x - 40 * l.s, y - 110 * l.s, 80 * l.s, 40 * l.s))
        for fx in (-30, 0, 30):
            pygame.draw.line(tela, (220, 220, 210), (x + fx * l.s, y - 92 * l.s), (x, y - w), 1)
    else:
        y = CHAO
    caixa = pygame.Rect(0, 0, w, w * 0.8)
    caixa.midbottom = (int(x), int(y))
    pygame.draw.rect(tela, (30, 34, 20), caixa.inflate(4, 4))
    pygame.draw.rect(tela, (90, 110, 60), caixa)
    pygame.draw.line(tela, (60, 74, 40), caixa.topleft, caixa.bottomright, 3)
    pygame.draw.line(tela, (60, 74, 40), caixa.topright, caixa.bottomleft, 3)
    if t >= 46:  # a tampa voando
        u = t - 46
        tx, ty = x + l.dir * u * 6, caixa.y - u * 5 + u * u * 0.3
        if ty < CHAO:
            pygame.draw.rect(tela, (90, 110, 60), (tx - w / 2, ty - 4, w, 8))


# =====================================================================
# FINN
# =====================================================================
def finn_golem(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    de = borda(l)
    gx = de + (xf(l) + l.dir * 40 - de) * suave(min(1, t / 50))
    if t < 60:  # no ombro do golem
        l.x = gx - l.dir * 10
        l.y = CHAO - 150 * l.s
        l.sobrepor = pz(l, "sentado")
    elif t < 72:  # o golem põe ele no chão
        k = (t - 60) / 12
        l.x = gx - l.dir * 10 - l.dir * 40 * k
        l.y = CHAO - 150 * l.s * (1 - k)
        l.sobrepor = pz(l, "pulo")
    else:
        l.x, l.y = xf(l), CHAO
        l.sobrepor = pz(l, "f_carrega") if t < 92 else {}
    l.extra["golem_x"] = gx
    if t % 14 == 0 and t < 50:
        som.tocar("terra", 0.3)
        jogo.tremer(3)
    l.t += 1


def finn_golem_ef(l, tela, t):
    import ult2
    gx = l.extra.get("golem_x")
    if gx is None or t >= 100:
        return
    afunda = suave(max(0, (t - 74) / 22))
    ult2.desenha_golem(l, tela, gx, afunda)


def finn_tornado(l, t, jogo):
    l.x, l.y = xf(l), CHAO
    if not final(l, t):
        l.esconde = t < 64
        l.sobrepor = pz(l, "f_ult") if t >= 64 else {}
    if t % 4 == 0 and t < 64:
        fogo(jogo, l.x + random.uniform(-30, 30), CHAO - random.uniform(0, 140), 0.8)
    if t == 64:
        som.tocar("explosao", 0.6)
    l.t += 1


def finn_tornado_ef(l, tela, t):
    if t >= 72:
        return
    k = min(1, t / 20) * (1 - max(0, (t - 60) / 12))
    x = xf(l)
    for i in range(12):  # o redemoinho de fogo
        y = CHAO - 8 - i * 16 * k
        r = (16 + i * 7) * k
        a = t * 0.5 + i * 0.7
        caixa = pygame.Rect(0, 0, r * 2, r * 0.45)
        caixa.center = (int(x + math.sin(t * 0.2 + i * 0.5) * i), int(y))
        pygame.draw.arc(tela, ((255, 220, 90), (255, 140, 30), (220, 60, 20))[i % 3], caixa, a, a + 2.6, 4)
    brilho(tela, (int(x), int(CHAO - 90 * k)), int(90 * k), (255, 140, 40), int(90 * k))


# =====================================================================
# KUN
# =====================================================================
def kun_embaralhado(l, t, jogo):
    l.x, l.y = xf(l), CHAO
    if not final(l, t):
        l.esconde = t < 62
        l.sobrepor = pz(l, "k_vitoria") if 62 <= t < 86 else {}
    if t == 62:
        som.tocar("confirma", 0.6)
    l.t += 1


def kun_embaralhado_ef(l, tela, t):
    import kun
    if t >= 70:
        return
    x = xf(l)
    k = min(1, t / 62)
    for i in range(30):  # as cartas girando em redemoinho e fechando no corpo
        a = t * 0.25 + i * 0.6
        r = (220 * (1 - k) + 20) * (0.6 + (i % 5) * 0.1)
        y = CHAO - 60 * l.s - (i % 6 - 3) * 18 * l.s * k
        kun.carta(tela, (x + math.cos(a) * r, y + math.sin(a) * r * 0.4), a, 1.5 * l.s / 1.36, math.cos(a), l=l)
    if t >= 60:
        brilho(tela, (int(x), int(CHAO - 60 * l.s)), 80, (255, 240, 200), 200)


def kun_mesa(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x = xf(l)
    l.y = CHAO
    l.sobrepor = pz(l, "sentado" if t < 56 else "chute" if t < 70 else "k_vitoria")
    if t == 60:
        som.tocar("chute")
        jogo.tremer(6)
    l.t += 1


def kun_mesa_ef(l, tela, t):
    import kun
    x = xf(l) + l.dir * 50 * l.s
    if t < 60:
        y, ang = CHAO, 0
    else:
        u = t - 60
        x += l.dir * u * 9
        y = CHAO - u * 6 + u * u * 0.25
        ang = u * 0.25 * l.dir
    if y > CHAO + 40 or t >= 100:
        return
    w = 90 * l.s
    c, s = math.cos(ang), math.sin(ang)

    def R(px, py):
        return x + px * c - py * s, y + px * s + py * c

    pygame.draw.polygon(tela, (40, 24, 14), [R(-6 * l.s, -36 * l.s), R(6 * l.s, -36 * l.s), R(10 * l.s, 0),
                                             R(-10 * l.s, 0)])  # o pé (coluna)
    pygame.draw.polygon(tela, (60, 36, 20), [R(-24 * l.s, 0), R(24 * l.s, 0), R(18 * l.s, -6 * l.s), R(-18 * l.s, -6 * l.s)])
    borda_m = [R(-w / 2 - 4, -44 * l.s), R(w / 2 + 4, -44 * l.s), R(w / 2 + 4, -34 * l.s), R(-w / 2 - 4, -34 * l.s)]
    pygame.draw.polygon(tela, (20, 10, 6), borda_m)
    pygame.draw.polygon(tela, (120, 70, 36), [R(-w / 2 - 2, -43 * l.s), R(w / 2 + 2, -43 * l.s), R(w / 2 + 2, -35 * l.s),
                                              R(-w / 2 - 2, -35 * l.s)])  # a borda de madeira
    pygame.draw.polygon(tela, (30, 130, 60), [R(-w / 2 + 4, -45 * l.s), R(w / 2 - 4, -45 * l.s), R(w / 2 - 8, -42 * l.s),
                                              R(-w / 2 + 8, -42 * l.s)])  # o feltro verde
    pts = borda_m
    for i, cor in enumerate(((220, 40, 40), (40, 80, 220), (240, 240, 240))):  # as pilhas de fichas
        for k in range(3 - i % 2):
            fx, fy = R(-w * 0.3 + i * 12 * l.s, -47 * l.s - k * 3 * l.s)
            pygame.draw.ellipse(tela, (20, 10, 6), (fx - 6 * l.s, fy - 2 * l.s, 12 * l.s, 5 * l.s))
            pygame.draw.ellipse(tela, cor, (fx - 5 * l.s, fy - 2 * l.s, 10 * l.s, 4 * l.s))
    for i in range(2):  # 2 cartas abertas
        cx_, cy_ = R(w * 0.18 + i * 12 * l.s, -46 * l.s)
        pygame.draw.rect(tela, (20, 10, 6), (cx_ - 5 * l.s, cy_ - 3 * l.s, 10 * l.s, 5 * l.s))
        pygame.draw.rect(tela, (250, 250, 245), (cx_ - 4 * l.s, cy_ - 2.5 * l.s, 8 * l.s, 4 * l.s))
    for lado in (-1, 1):
        a = (lado * w * 0.4, -32 * l.s)
        b = (lado * w * 0.4, 0)
        pygame.draw.line(tela, (80, 50, 30), (x + a[0] * c - a[1] * s, y + a[0] * s + a[1] * c),
                         (x + b[0] * c - b[1] * s, y + b[0] * s + b[1] * c), 4)
    if t < 56:  # embaralhando
        mx, my = l.ponto(l.pose_vista or l.pose_atual(), "mf")
        kun.carta(tela, (mx, my - (t % 8) * 2), (t % 8) * 0.3, 1.4 * l.s / 1.36, 1, l=l)


# =====================================================================
# TROMOS
# =====================================================================
def xeno_duto(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x = xf(l)
    if t < 26:
        l.esconde = True
        l.y = CHAO
    elif t < 78:  # descendo do teto de cabeça pra baixo
        l.esconde = False
        k = suave((t - 26) / 52)
        l.y = 40 + (CHAO - 40) * k
        l.angulo = math.pi * (1 - max(0, (t - 66) / 12))
        l.sobrepor = pz(l, "x_rasteja")
    else:
        l.angulo = 0
        l.y = CHAO
        l.sobrepor = pz(l, "x_vitoria") if t < 92 else {}
    if t == 20:
        som.tocar("defesa")
        som.tocar("queda", 0.6)
    l.t += 1


def xeno_duto_ef(l, tela, t):
    x = xf(l) + l.dir * 60
    if t < 20:
        y = 20
    else:
        y = 20 + min(1, (t - 20) / 12) ** 2 * (CHAO - 20)
    if t >= 100:
        return
    grade = pygame.Rect(0, 0, 70, 46)
    grade.center = (int(x), int(min(CHAO - 23, y)))
    pygame.draw.rect(tela, (70, 74, 80), grade)
    for i in range(5):
        pygame.draw.line(tela, (30, 32, 36), (grade.x + 6 + i * 14, grade.y + 4), (grade.x + 6 + i * 14, grade.bottom - 4), 3)
    pygame.draw.rect(tela, (20, 20, 24), grade, 2)
    if t < 26:  # o buraco do duto lá em cima
        pygame.draw.rect(tela, (10, 10, 14), (xf(l) - 40, 0, 80, 20))


def xeno_ovo(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x, l.y = xf(l), CHAO
    l.esconde = t < 50
    if t >= 50:
        k = suave(min(1, (t - 50) / 30))
        l.s = l.f["tam"] * (0.3 + 0.7 * k)
        l.sobrepor = pz(l, "x_rasteja" if k < 1 else "x_vitoria")
    if t == 50:
        som.tocar("quebra", 0.7)
        som.tocar("lingua")
    l.t += 1


def xeno_ovo_ef(l, tela, t):
    if t >= 64:
        return
    x = xf(l)
    treme = math.sin(t * 1.3) * 3 * min(1, t / 40)
    if t < 50:
        ovo = pygame.Rect(0, 0, 50 * l.s, 64 * l.s)
        ovo.midbottom = (int(x + treme), CHAO)
        pygame.draw.ellipse(tela, (20, 24, 18), ovo.inflate(4, 4))
        pygame.draw.ellipse(tela, (90, 110, 70), ovo)
        for i in range(3):  # as veias
            pygame.draw.line(tela, (60, 80, 40), (ovo.x + 10 + i * 12, ovo.y + 12), (ovo.x + 6 + i * 14, ovo.bottom - 10), 2)
        if t > 34:  # rachando
            pygame.draw.lines(tela, (20, 24, 18), False, [(ovo.centerx - 10, ovo.y + 6), (ovo.centerx, ovo.y + 20),
                                                          (ovo.centerx - 6, ovo.y + 32)], 2)
    else:  # as cascas abertas no chão
        for lado in (-1, 1):
            pygame.draw.ellipse(tela, (90, 110, 70), (x + lado * 30 - 18, CHAO - 18, 36, 18))


# =====================================================================
# TAI
# =====================================================================
def tai_ceu(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x = xf(l)
    if t < 34:
        l.y = -100 + (CHAO + 100) * (t / 34) ** 2
        l.sobrepor = pz(l, "t_shiko")
    else:
        l.y = CHAO
        if t == 34:
            som.tocar("terra")
            som.tocar("queda")
            jogo.tremer(22)
            fumaca(jogo, l.x, CHAO - 4, 24, (170, 150, 120), 7, -1.5)
        l.esconde = 34 <= t < 50
        l.sobrepor = pz(l, "agachado" if t < 64 else "t_sal" if t < 90 else "parado")
    l.t += 1


def tai_ceu_ef(l, tela, t):
    if t >= 34:  # a cratera
        x = xf(l)
        pygame.draw.ellipse(tela, (60, 44, 30), (x - 80, CHAO - 8, 160, 18))
        pygame.draw.ellipse(tela, (30, 20, 14), (x - 60, CHAO - 4, 120, 10))


def tai_pedra(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    de = borda(l)
    if t < 50:
        l.x = de + (xf(l) - de) * suave(t / 50)
        l.sobrepor = pz(l, ("andar1", "andar2", "andar3", "andar4")[(t // 9) % 4])
    else:
        l.x = xf(l)
        l.sobrepor = pz(l, "parado" if t < 70 else "vitoria")
        if t == 54:
            som.tocar("terra")
            jogo.tremer(14)
            fumaca(jogo, l.x - l.dir * 60, CHAO - 4, 10, (160, 140, 110), 4, -1)
        if t == 72:
            som.tocar("soco", 0.5)
    l.t += 1


def tai_pedra_ef(l, tela, t):
    if t >= 100:
        return
    if t < 52:  # nas costas
        x, y = l.x - l.dir * 14 * l.s, l.y - 140 * l.s
    else:  # largou do lado
        x, y = xf(l) - l.dir * 70 * l.s, CHAO - 40 * l.s
    pts = [(x - 46, y + 10), (x - 30, y - 34), (x + 6, y - 42), (x + 40, y - 20), (x + 46, y + 20), (x + 10, y + 38),
           (x - 34, y + 34)]
    pygame.draw.polygon(tela, (40, 36, 30), pts)
    pygame.draw.polygon(tela, (130, 124, 112), [(px + (x - px) * 0.08, py + (y - py) * 0.08) for px, py in pts])
    pygame.draw.line(tela, (90, 84, 76), (x - 20, y - 10), (x + 10, y + 6), 3)


# =====================================================================
# TAMER
# =====================================================================
def tamer_galope(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    de = borda(l)
    l.extra["lobo_some"] = t < 70
    if t < 50:
        l.x = de + (xf(l) - de) * suave(t / 50)
        l.y = CHAO - 30 * l.s
        l.sobrepor = pz(l, "t_monta")
    elif t < 70:  # freia derrapando e pula pro chão
        k = (t - 50) / 20
        l.x = xf(l)
        l.y = CHAO - 30 * l.s - math.sin(k * math.pi) * 60 + 30 * l.s * k
        l.sobrepor = pz(l, "pulo")
        if t == 50:
            som.tocar("vento")
            fumaca(jogo, xf(l), CHAO - 4, 10, (170, 150, 110), 4, -0.8)
    else:
        l.x, l.y = xf(l), CHAO
        l.sobrepor = pz(l, "t_carinho") if t < 90 else {}
    l.t += 1


def tamer_galope_ef(l, tela, t):
    import tamer
    if t >= 70:
        return
    esc = l.s / tamer.S_REF
    x = l.x if t < 50 else xf(l) + l.dir * 10
    tamer.desenha_lobo(tela, x, CHAO, esc, l.dir, "corre" if t < 50 else "parado", t * 2, tamer.cor_lobo(l),
                       tamer.skin_lobo(l))


def tamer_mata(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    de = borda(l) + l.dir * 90
    l.extra["lobo_some"] = t < 50
    l.esconde = t < 40
    if t >= 40:
        k = suave(min(1, (t - 40) / 40))
        l.x = de + (xf(l) - de) * k
        l.sobrepor = pz(l, ("andar1", "andar2", "andar3", "andar4")[(t // 8) % 4]) if k < 1 else {}
    if t % 10 == 0 and t < 40:
        som.tocar("vento", 0.2)
    l.t += 1


def tamer_mata_ef(l, tela, t):
    import tamer
    de = borda(l) + l.dir * 90
    mexe = math.sin(t * 0.8) * (4 if t < 50 else 0)
    for i in range(4):  # o arbusto
        bx = de + (i - 1.5) * 24
        pygame.draw.circle(tela, (30, 70, 30), (int(bx + mexe), int(CHAO - 30 - (i % 2) * 14)), 30)
        pygame.draw.circle(tela, (60, 120, 50), (int(bx + mexe), int(CHAO - 32 - (i % 2) * 14)), 26)
    if 10 <= t < 50:  # o lobo saindo farejando
        esc = l.s / tamer.S_REF
        k = suave((t - 10) / 40)
        wx = de + l.dir * 160 * k
        tamer.desenha_lobo(tela, wx, CHAO, esc, l.dir, "corre" if k < 0.95 else "parado", t, tamer.cor_lobo(l),
                           tamer.skin_lobo(l))


# =====================================================================
# JOHN
# =====================================================================
def john_caixa(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x = xf(l)
    l.esconde = t < 52
    if t >= 52:
        k = (t - 52) / 18
        l.y = CHAO - math.sin(min(1, k) * math.pi) * 90
        l.sobrepor = pz(l, "pulo" if k < 1 else "j_agradece")
    if t in (20, 30, 40):
        som.tocar("soco", 0.4)
    if t == 52:
        som.tocar("puf")
    l.t += 1


def john_caixa_ef(l, tela, t):
    if t >= 100:
        return
    x = xf(l)
    w = 64 * l.s
    treme = math.sin(t * 2) * 3 if 18 <= t < 46 and (t // 4) % 2 else 0
    abre = suave(min(1, max(0, (t - 48) / 10)))
    for i, ang in enumerate((-1, 1, -0.5, 0.5)):  # as paredes abrindo como uma flor
        if i >= 2 and abre < 0.3:
            continue
        a = ang * abre * 1.4
        base = (x + ang * w * 0.5 * (1 if i < 2 else 0.4), CHAO)
        topo = (base[0] + math.sin(a) * w + treme, base[1] - math.cos(a) * w)
        lado = w * (0.5 if i < 2 else 0.6)
        painel = [(base[0], base[1]), (base[0] - math.copysign(lado, ang), base[1]),
                  (topo[0] - math.copysign(lado, ang), topo[1]), topo]
        pygame.draw.polygon(tela, (20, 10, 30), [(px, py + 2) for px, py in painel])
        pygame.draw.polygon(tela, (120, 50, 170) if i < 2 else (100, 40, 150), painel)
        sx, sy = (painel[0][0] + painel[2][0]) / 2, (painel[0][1] + painel[2][1]) / 2
        pygame.draw.circle(tela, (255, 220, 80), (int(sx), int(sy)), 4)
    if abre < 1:
        tampa = pygame.Rect(0, 0, w * 1.05, 10)
        tampa.midbottom = (int(x + treme), int(CHAO - w - abre * 60))
        pygame.draw.rect(tela, (90, 30, 130), tampa)
    if 48 <= t < 60:
        brilho(tela, (int(x), int(CHAO - w / 2)), 70, (220, 180, 255), 180)


def john_pombas(l, t, jogo):
    l.x, l.y = xf(l), CHAO
    if not final(l, t):
        l.esconde = t < 44
        l.sobrepor = pz(l, "j_agradece") if 44 <= t < 80 else {}
    if t == 8:
        som.tocar("vento")
    l.t += 1


def john_pombas_ef(l, tela, t):
    from provocacoes_loja import pomba
    if t >= 70:
        return
    for i in range(22):  # a revoada passando na frente dele
        k = (t - i * 1.5) / 50
        if k < 0 or k > 1.2:
            continue
        x = xf(l) - l.dir * 300 + l.dir * 600 * k + math.sin(i * 1.7) * 30
        y = CHAO - 40 - (i % 7) * 20 - math.sin(k * 6 + i) * 10
        pomba(tela, x, y, t + i, l.dir)


# =====================================================================
# CRÁQUEN
# =====================================================================
def craquen_tentaculo(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x = xf(l)
    if t < 30:
        l.y = CHAO - 220 * suave(t / 30)
    elif t < 60:
        l.y = CHAO - 220 * (1 - suave((t - 30) / 30))
    else:
        l.y = CHAO
    l.sobrepor = pz(l, "q_comanda" if t < 60 else "q_ri" if t < 86 else "parado")
    if t == 4:
        som.tocar("terra", 0.6)
        fumaca(jogo, l.x + l.dir * 40, CHAO - 4, 10, (170, 210, 220), 4, -1.5)
    l.t += 1


def craquen_tentaculo_ef(l, tela, t):
    import ult2
    if t >= 90:
        return
    sai = min(1, t / 10) * (1 - suave(max(0, (t - 62) / 24)))
    base = (xf(l) + l.dir * 50, CHAO + 30)
    ponta = (l.x + l.dir * 6, l.y - 60 * l.s)
    if sai > 0:
        ult2.tentaculo(tela, base, (base[0] + (ponta[0] - base[0]) * sai, base[1] + (ponta[1] - base[1]) * sai),
                       30, t, 0.5, enrola=sai)


def craquen_ancora(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x = xf(l) - l.dir * 10
    if t < 26:
        l.esconde = True
    else:
        l.esconde = False
        k = suave(min(1, (t - 26) / 44))
        l.y = -60 + (CHAO + 60) * k
        l.sobrepor = pz(l, "q_comanda" if k < 1 else "q_ri")
    if t == 22:
        som.tocar("terra")
        jogo.tremer(14)
        fumaca(jogo, xf(l), CHAO - 4, 12, (170, 160, 150), 4, -1)
    l.t += 1


def craquen_ancora_ef(l, tela, t):
    if t >= 100:
        return
    x = xf(l) + l.dir * 10
    y = min(CHAO + 10, -80 + (CHAO + 90) * (t / 22) ** 2) if t < 22 else CHAO + 10
    for i in range(0, int(y), 14):  # a corrente
        pygame.draw.ellipse(tela, (60, 60, 66), (x - 4, i, 8, 14), 2)
    pygame.draw.line(tela, (50, 50, 56), (x, y - 70), (x, y), 8)  # a âncora
    pygame.draw.arc(tela, (50, 50, 56), (x - 34, y - 40, 68, 50), math.pi, math.tau, 8)
    pygame.draw.line(tela, (50, 50, 56), (x - 18, y - 58), (x + 18, y - 58), 6)
    pygame.draw.circle(tela, (50, 50, 56), (int(x), int(y - 74)), 7, 3)


# =====================================================================
# MAGNUS
# =====================================================================
def magnus_jaula(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x, l.y = xf(l), CHAO
    l.sobrepor = pz(l, "m_fareja" if t < 40 else "x_rabada" if t < 54 else "m_ruge" if t < 90 else "parado")
    if t == 46:
        som.tocar("quebra")
        jogo.tremer(10)
    if t == 60:
        som.tocar("uivo", 0.6)
    l.t += 1


def magnus_jaula_ef(l, tela, t):
    x = xf(l)
    w, h = 170 * l.s, 150 * l.s
    if t < 46:
        for i in range(8):  # as grades
            bx = x - w / 2 + i * w / 7
            pygame.draw.line(tela, (30, 30, 34), (bx, CHAO), (bx, CHAO - h), 6)
            pygame.draw.line(tela, (140, 144, 154), (bx, CHAO), (bx, CHAO - h), 3)
        pygame.draw.line(tela, (140, 144, 154), (x - w / 2, CHAO - h), (x + w / 2, CHAO - h), 6)
    elif t < 90:  # as grades voando
        u = t - 46
        for i in range(8):
            bx = x - w / 2 + i * w / 7 + (i - 3.5) * u * 5
            by = CHAO - h / 2 - u * 8 + u * u * 0.5
            a = u * 0.2 * (1 if i % 2 else -1)
            pygame.draw.line(tela, (140, 144, 154), (bx - math.sin(a) * h / 2, by - math.cos(a) * h / 2),
                             (bx + math.sin(a) * h / 2, by + math.cos(a) * h / 2), 3)


def magnus_cerca(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    cerca = xf(l) - l.dir * 150
    de = borda(l)
    if t < 20:
        l.esconde = True
        l.x, l.y = de, CHAO
    elif t < 50:  # o pulo por cima da cerca
        l.esconde = False
        k = (t - 20) / 30
        l.x = de + (xf(l) - de) * k
        l.y = CHAO - math.sin(k * math.pi) * 210
        l.sobrepor = pz(l, "x_salto")
    else:
        l.x, l.y = xf(l), CHAO
        l.sobrepor = pz(l, "m_fareja" if t < 80 else "parado")
        if t == 50:
            som.tocar("queda", 0.7)
        if 54 <= t < 80 and t % 3 == 0:  # sacudindo as faíscas
            for _ in range(3):
                jogo.faiscas.append([l.x + random.uniform(-40, 40), l.y - 50, random.uniform(-4, 4),
                                     random.uniform(-5, -1), 12, (180, 220, 255), 2])
    l.extra["cerca_x"] = cerca
    l.t += 1


def magnus_cerca_ef(l, tela, t):
    x = l.extra.get("cerca_x", xf(l))
    if t >= 100:
        return
    for dx in (-30, 30):
        pygame.draw.rect(tela, (70, 72, 78), (x + dx - 5, CHAO - 170, 10, 170))
    for i in range(5):
        y = CHAO - 30 - i * 32
        pygame.draw.line(tela, (60, 60, 66), (x - 30, y), (x + 30, y), 2)
    if (t // 3) % 3 == 0:  # a eletricidade
        pygame.draw.lines(tela, (180, 230, 255), False, [(x - 30, CHAO - 120), (x - 10, CHAO - 130), (x + 8, CHAO - 112),
                                                         (x + 30, CHAO - 124)], 2)


# =====================================================================
# SPHYRUS
# =====================================================================
def sphyrus_tanque(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x, l.y = xf(l), CHAO
    l.sobrepor = pz(l, "parado" if t < 56 else "s_ruge" if t < 86 else "parado")
    if t in (20, 34, 46):
        som.tocar("defesa", 0.5)
    if t == 56:
        som.tocar("quebra")
        jogo.tremer(10)
        fumaca(jogo, l.x, CHAO - 4, 16, (190, 230, 250), 6, -1.5)
        for _ in range(16):
            jogo.faiscas.append([l.x + random.uniform(-60, 60), CHAO - random.uniform(20, 160), random.uniform(-6, 6),
                                 random.uniform(-6, 0), 30, (200, 235, 250), 3])
    l.t += 1


def sphyrus_tanque_ef(l, tela, t):
    x = xf(l)
    w, h = 150 * l.s, 200 * l.s
    if t < 56:
        vidro = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
        vidro.fill((120, 200, 230, 110))
        nivel = h * 0.1
        pygame.draw.rect(vidro, (24, 70, 120, 170), (0, nivel, w, h - nivel))  # a água escura (ele lá dentro, só o vulto)
        for i in range(8):  # as bolhas subindo
            bx = (i * 37 + 11) % int(w)
            by = h - ((t * 3 + i * 41) % int(h - nivel))
            pygame.draw.circle(vidro, (200, 240, 255, 200), (bx, int(by)), 3 + i % 3, 1)
        pygame.draw.line(vidro, (230, 250, 255, 120), (10, 12), (10, h - 12), 4)  # o reflexo do vidro
        tela.blit(vidro, (x - w / 2, CHAO - h))
        pygame.draw.rect(tela, (180, 230, 250), (x - w / 2, CHAO - h, w, h), 3)
        pygame.draw.rect(tela, (80, 86, 96), (x - w / 2 - 6, CHAO - h - 10, w + 12, 12))
        pygame.draw.rect(tela, (80, 86, 96), (x - w / 2 - 6, CHAO - 10, w + 12, 12))
        for i in range(6):  # o código de barras do tanque
            pygame.draw.line(tela, (20, 20, 24), (x + w / 2 - 30 + i * 4, CHAO - 40), (x + w / 2 - 30 + i * 4, CHAO - 24),
                             1 + i % 2)
        rnd = random.Random(9)
        for k in range(min(3, (t - 14) // 12 + 1) if t >= 14 else 0):  # as rachaduras
            cx, cy = x + rnd.uniform(-w / 3, w / 3), CHAO - rnd.uniform(h * 0.3, h * 0.8)
            for _ in range(4):
                a = rnd.uniform(0, math.tau)
                pygame.draw.line(tela, (240, 250, 255), (cx, cy), (cx + math.cos(a) * 30, cy + math.sin(a) * 30), 2)
    elif t < 90:  # a água vazando pelo chão
        u = t - 56
        pygame.draw.ellipse(tela, (90, 170, 220), (x - 40 - u * 5, CHAO - 6, 80 + u * 10, 12))


def sphyrus_esgoto(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x = xf(l)
    if t < 16:
        l.esconde = True
    elif t < 56:  # salta de dentro girando
        l.esconde = False
        k = (t - 16) / 40
        l.y = CHAO + 40 - math.sin(k * math.pi) * 230 - 40 * k
        l.angulo = k * math.tau * 1.5 * l.dir
        l.sobrepor = pz(l, "s_salto")
    else:
        l.angulo = 0
        l.y = CHAO
        l.sobrepor = pz(l, "s_ruge" if t < 86 else "parado")
        if t == 56:
            som.tocar("queda", 0.7)
    if t == 12:
        som.tocar("defesa")
        som.tocar("explosao", 0.4)
        fumaca(jogo, l.x, CHAO - 4, 10, (150, 160, 140), 3, -1.5)
    l.t += 1


def sphyrus_esgoto_ef(l, tela, t):
    x = xf(l)
    if t >= 100:
        return
    pygame.draw.ellipse(tela, (10, 10, 12), (x - 34, CHAO - 6, 68, 14))  # o buraco
    if t < 12:
        y, a = CHAO, 0
    else:
        u = t - 12
        y = CHAO - u * 14 + u * u * 0.45
        a = u * 0.3
    if y < CHAO + 5 or t < 12:
        w = 34 * abs(math.cos(a))
        pygame.draw.ellipse(tela, (60, 62, 66), (x + (t - 12) * 2 * (t >= 12) - 34, y - max(3, w * 0.3), 68, max(6, w * 0.6)))


# =====================================================================
# A loja: 2 por lutador
# =====================================================================
def _e(lutador, ident, nome, ent, ef):
    extras.registrar("entradas", lutador, id=ident, nome=nome, preco=PRECO, entrada=ent, entrada_efeito=ef)


_e("MAX-10", "capsula", "CÁPSULA", max_capsula, max_capsula_ef)
_e("MAX-10", "montagem", "MONTAGEM", max_montagem, max_montagem_ef)
_e("RIB", "shurikens", "CHUVA DE SHURIKENS", rib_shurikens, rib_shurikens_ef)
_e("RIB", "cipo", "CIPÓ", rib_cipo, rib_cipo_ef)
_e("TRAFO", "contrario", "TRANSFORMAÇÃO AO CONTRÁRIO", trafo_contrario, trafo_contrario_ef)
_e("TRAFO", "parede", "PULÃO DA PAREDE", trafo_parede, None)
_e("KING RIP", "medita", "MEDITANDO", king_medita, king_medita_ef)
_e("KING RIP", "folha", "FOLHA CORTADA", king_folha, king_folha_ef)
_e("CANNAN", "rapel", "RAPEL", cannan_rapel, cannan_rapel_ef)
_e("CANNAN", "caixa", "CAIXA DE SUPRIMENTOS", cannan_caixa, cannan_caixa_ef)
_e("FINN", "golem", "GOLEM DE CARONA", finn_golem, finn_golem_ef)
_e("FINN", "tornado", "TORNADO DE FOGO", finn_tornado, finn_tornado_ef)
_e("KUN", "embaralhado", "EMBARALHADO", kun_embaralhado, kun_embaralhado_ef)
_e("KUN", "mesa", "MESA DE CASSINO", kun_mesa, kun_mesa_ef)
_e("TROMOS", "duto", "DUTO DE AR", xeno_duto, xeno_duto_ef)
_e("TROMOS", "ovo", "OVO", xeno_ovo, xeno_ovo_ef)
_e("TAI", "ceu", "CAINDO DO CÉU", tai_ceu, tai_ceu_ef)
_e("TAI", "pedra", "CARREGANDO A PEDRA", tai_pedra, tai_pedra_ef)
_e("TAMER", "galope", "MONTADO NO LOBO", tamer_galope, tamer_galope_ef)
_e("TAMER", "mata", "DA MATA", tamer_mata, tamer_mata_ef)
_e("JOHN", "caixa", "CAIXA DE MÁGICA", john_caixa, john_caixa_ef)
_e("JOHN", "pombas", "NUVEM DE POMBAS", john_pombas, john_pombas_ef)
_e("CRÁQUEN", "tentaculo", "TENTÁCULO", craquen_tentaculo, craquen_tentaculo_ef)
_e("CRÁQUEN", "ancora", "ÂNCORA", craquen_ancora, craquen_ancora_ef)
_e("MAGNUS", "jaula", "JAULA ARREBENTADA", magnus_jaula, magnus_jaula_ef)
_e("MAGNUS", "cerca", "PULO DA CERCA", magnus_cerca, magnus_cerca_ef)
_e("SPHYRUS", "tanque", "TANQUE QUEBRADO", sphyrus_tanque, sphyrus_tanque_ef)
_e("SPHYRUS", "esgoto", "PELO ESGOTO", sphyrus_esgoto, sphyrus_esgoto_ef)


# =====================================================================
# FRIGANTUS
# =====================================================================
def frig_gorila(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    de = borda(l)
    if t < 56:  # corre de quatro igual gorila, levantando neve
        l.x = de + (xf(l) - de) * suave(t / 56)
        l.sobrepor = pz(l, ("andar1", "andar3")[(t // 6) % 2])
        if t % 6 == 0:
            fumaca(jogo, l.x - l.dir * 20, CHAO - 4, 2, (230, 240, 255), 2, -0.8)
            som.tocar("soco", 0.3)
    else:  # para e bate no peito
        l.x = xf(l)
        l.sobrepor = pz(l, "fr_peito_a" if (t // 6) % 2 else "fr_peito_b") if t < 90 else {}
        if t % 6 == 0 and t < 90:
            som.tocar("soco", 0.4)
    l.t += 1


def frig_barril(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x, l.y = xf(l), CHAO
    l.sobrepor = pz(l, "parado" if t < 30 else "fr_arremessa" if t < 46 else "fr_joga" if t < 70 else "fr_peito_a")
    if t == 46:
        som.tocar("vento")
    if t == 62:
        som.tocar("ko", 0.5)
        jogo.tremer(10)
    l.t += 1


def frig_barril_ef(l, tela, t):
    s = l.s
    cx = xf(l) + l.dir * 230
    if t < 62:  # o caçador chegando com a rede
        k = min(1, t / 30)
        hx = cx + l.dir * 200 * (1 - k)
        hy = CHAO
        voa_a = 0
    else:
        u = t - 62
        hx = cx + l.dir * u * 14
        hy = CHAO - u * 10 + u * u * 0.2
        voa_a = u * 0.4
    if hy < CHAO + 60 and t < 100:
        c, sn = math.cos(voa_a), math.sin(voa_a)

        def R(px, py):
            return (hx + px * c - py * sn, hy + px * sn + py * c)
        pygame.draw.line(tela, (60, 70, 40), R(-6, 0), R(-4, -30), 6)
        pygame.draw.line(tela, (60, 70, 40), R(6, 0), R(4, -30), 6)
        pygame.draw.line(tela, (110, 90, 50), R(0, -30), R(0, -62), 12)
        pygame.draw.circle(tela, (230, 190, 150), [int(v) for v in R(0, -70)], 8)
        pygame.draw.rect(tela, (70, 50, 30), (*R(-10, -82), 20, 6))
        pygame.draw.line(tela, (120, 100, 70), R(6, -50), R(-l.dir * 26, -72), 3)  # a rede
    if 30 <= t < 62:  # o barril: arrancado (nas mãos) e voando
        if t < 46:
            bx, by = l.ponto(l.pose_vista or l.pose_atual(), "mf")
        else:
            k = (t - 46) / 16
            mx, my = l.x + l.dir * 40 * s, l.y - 120 * s
            bx, by = mx + (cx - mx) * k, my + (CHAO - 60 - my) * k - math.sin(k * math.pi) * 50
        caixa = pygame.Rect(0, 0, 30 * s, 38 * s)
        caixa.center = (int(bx), int(by))
        pygame.draw.rect(tela, (40, 24, 12), caixa.inflate(4, 4), border_radius=8)
        pygame.draw.rect(tela, (140, 90, 40), caixa, border_radius=8)
        for f in (0.25, 0.75):
            y = caixa.y + caixa.h * f
            pygame.draw.line(tela, (60, 60, 64), (caixa.x, y), (caixa.right, y), 3)


_e("FRIGANTUS", "gorila", "CORRIDA DE GORILA", frig_gorila, None)
_e("FRIGANTUS", "barril", "O BARRIL", frig_barril, frig_barril_ef)


# =====================================================================
# NOCTURNUS: ECO NO ESCURO (escondido, 3 anéis de sonar saem de onde ele está, e PUF: aparece de asas abertas)
# =====================================================================
ECO_ANEIS, ECO_SURGE = (0, 20, 40), 50


def noct_eco(l, t, jogo):
    if final(l, t):
        l.t += 1
        return
    l.x, l.y = xf(l), CHAO
    l.esconde = t < ECO_SURGE
    l.sobrepor = pz(l, "n_chama" if t < ECO_SURGE + 34 else "parado")
    if t in ECO_ANEIS:
        som.tocar("laser", 0.3)
    if t == ECO_SURGE:
        som.tocar("vento", 0.7)
        fumaca(jogo, l.x, CHAO - 70 * l.s, 12, (40, 30, 56), 4, -0.6)
    l.t += 1


def noct_eco_ef(l, tela, t):
    cx, cy = xf(l), CHAO - 70 * l.s
    for nasce in ECO_ANEIS:  # os anéis de SONAR azuis (crescendo e sumindo)
        u = t - nasce
        if 0 <= u < 36:
            r = int(10 + u * 7)
            cor = (110, 200, 255) if u < 24 else (60, 120, 170)
            pygame.draw.circle(tela, cor, (int(cx), int(cy)), r, 3 if u < 24 else 2)


_e("NOCTURNUS", "eco", "ECO NO ESCURO", noct_eco, noct_eco_ef)


# =====================================================================
# CUTSCENES: a entrada mais elaborada de cada lutador vira cena de anime (e custa mais)
# (lutador, id) -> (clímax, fim, foco do clímax, fundo, foco do fim)
# =====================================================================
PRECO_CENA = 150
ANIME = {("MAX-10", "capsula"): "cena_max:entrada", ("FRIGANTUS", "barril"): "cena_frigantus:entrada",
         ("SPHYRUS", "tanque"): "cena_sphyrus:entrada", ("MAGNUS", "jaula"): "cena_magnus:entrada",
         ("KUN", "embaralhado"): "cena_kun:entrada",
         ("RIB", "shurikens"): "cena_rib:entrada", ("TRAFO", "contrario"): "cena_trafo:entrada",
         ("KING RIP", "folha"): "cena_king:entrada", ("CANNAN", "rapel"): "cena_cannan:entrada",
         ("FINN", "tornado"): "cena_finn:entrada", ("TROMOS", "ovo"): "cena_tromos:entrada",
         ("TAI", "ceu"): "cena_tai:entrada", ("TAMER", "galope"): "cena_tamer:entrada",
         ("JOHN", "caixa"): "cena_john:entrada",
         ("CRÁQUEN", "tentaculo"): "cena_craquen:entrada", ("NOCTURNUS", "eco"): "cena_nocturnus:entrada"}  # as que já viraram CENA DE ANIME desenhada (arquivo da cena)
CENAS = {
    ("MAX-10", "capsula"): (CAP_ABRE, 100, "corpo", "ceu", "geral"),
    ("RIB", "shurikens"): (50, 100, "corpo", "noite", "corpo"),
    ("TRAFO", "contrario"): (60, 105, "corpo", "luz", "corpo"),
    ("KING RIP", "folha"): (60, 100, "corpo", "noite", "corpo"),
    ("CANNAN", "rapel"): (64, 100, "corpo", "ceu", "corpo"),
    ("FINN", "tornado"): (55, 105, "corpo", "noite", "corpo"),
    ("KUN", "embaralhado"): (55, 100, "corpo", "luz", "corpo"),
    ("TROMOS", "ovo"): (55, 105, "corpo", "noite", "corpo"),
    ("TAI", "ceu"): (52, 100, "corpo", "ceu", "corpo"),
    ("TAMER", "galope"): (45, 100, "corpo", "ceu", "corpo"),
    ("JOHN", "caixa"): (50, 100, "corpo", "luz", "corpo"),
    ("CRÁQUEN", "tentaculo"): (45, 100, "corpo", "noite", "corpo"),
    ("MAGNUS", "jaula"): (40, 100, "corpo", "noite", "corpo"),
    ("SPHYRUS", "tanque"): (56, 105, "corpo", "noite", "corpo"),
    ("FRIGANTUS", "barril"): (50, 100, "corpo", "noite", "corpo"),
    ("NOCTURNUS", "eco"): (ECO_SURGE, 100, "corpo", "noite", "corpo"),
}


def _ligar_cenas():
    import cenas_loja
    for (lutador, ident), cena in CENAS.items():
        it = extras.item("entradas", lutador, ident)
        assert it["id"] == ident, (lutador, ident)
        it["entrada_cutscene"] = ANIME.get((lutador, ident)) or cenas_loja.planos_auto(*cena)
        it["preco"] = PRECO_CENA


_ligar_cenas()
