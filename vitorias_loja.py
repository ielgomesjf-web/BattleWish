"""POSES DE VITÓRIA DA LOJA (2 por lutador, escolhidas pelo Gomes). Repetem enquanto a tela de vitória está aberta.
vitoria(l, t, jogo) mexe só no lutador que ganhou (a luta já acabou); vitoria_efeito(l, tela, t) desenha."""
import math
import random

import pygame

import extras
import som
from config import *  # noqa: F401,F403
from golpes import proporcionar, suave
from max10 import brilho, fogo, fumaca
from provocacoes_loja import POSES_EXTRA, alvo, ponto

PRECO, PRECO_CAPRICHADA = 80, 100

REVERENCIA = dict(pt=(-8, 0), jt=(-6, 28), pf=(8, 0), jf=(6, 28), qd=(0, 58), pc=(34, 80), cb=(48, 76),
                  ct=(32, 58), mt=(44, 66), cf=(34, 58), mf=(46, 68))  # bem curvado, punho na palma
SAUDACAO = dict(pt=(-8, 0), jt=(-6, 28), pf=(8, 0), jf=(6, 28), qd=(0, 58), pc=(2, 94), cb=(4, 112),
                ct=(12, 74), mt=(26, 84), cf=(14, 72), mf=(27, 86))  # em pé, pés juntos, punho na palma
DEITADO = dict(pt=(44, 34), jt=(22, 38), pf=(46, 38), jf=(24, 42), qd=(0, 36), pc=(-36, 42), cb=(-52, 48),
               ct=(-46, 56), mt=(-58, 56), cf=(-44, 58), mf=(-56, 60))
POSES_EXTRA.update({"reverencia": REVERENCIA, "saudacao": SAUDACAO, "deitado": DEITADO})
proporcionar(POSES_EXTRA)


def p_(l, nome):
    """Uma pose do lutador (ou uma das poses extras)."""
    return dict(l.poses.get(nome) or POSES_EXTRA.get(nome) or l.poses["vitoria"])


def balao(tela, l, txt, dy=150):
    import ult2
    ult2.balao(tela, txt, (l.x, l.y - dy * l.s))


def ciclo(t, n):
    return t % n


# =====================================================================
# MAX-10
# =====================================================================
def max_desliga(l, t, jogo):
    from golpes import misturar
    p = p_(l, "parado")
    mole = dict(p)  # desligado: joelhos dobrados, braços caídos, cabeça baixa
    mole.update(qd=(p["qd"][0], p["qd"][1] - 8), pc=(p["pc"][0] + 8, p["pc"][1] - 14),
                cb=(p["pc"][0] + 18, p["pc"][1] - 12), jt=(p["jt"][0] + 6, p["jt"][1] - 2),
                jf=(p["jf"][0] + 6, p["jf"][1] - 2), ct=(p["pc"][0] + 4, p["pc"][1] - 34),
                mt=(p["pc"][0] + 6, p["pc"][1] - 58), cf=(p["pc"][0] + 12, p["pc"][1] - 34),
                mf=(p["pc"][0] + 14, p["pc"][1] - 58))
    k = suave(min(1, max(0, (t - 30) / 50)))
    if 30 <= t < 80 and (t // 3) % 4 == 0:  # dá umas travadinhas enquanto desliga
        k = max(0, k - 0.12)
    l.sobrepor = misturar(p, mole, k)
    if t == 30:
        som.tocar("carga", 0.4)
    if t in (50, 64, 76):
        cb = ponto(l, "cb")
        for _ in range(4):  # faíscas saindo da nuca
            jogo.faiscas.append([cb[0] - l.dir * 6, cb[1], random.uniform(-3, 3), random.uniform(-4, -1), 12,
                                 (255, 230, 140), 2])
        som.tocar("defesa", 0.25)
    if t > 80 and t % 20 == 0:
        fumaca(jogo, ponto(l, "cb")[0], ponto(l, "cb")[1] - 6, 1, (170, 170, 176), 1, -0.8)


def max_desliga_ef(l, tela, t):
    cb = ponto(l, "cb")
    olho = (int(cb[0] + l.dir * 6 * l.s), int(cb[1]))
    if t < 80:  # o olho piscando e apagando
        forte = 1 - max(0, (t - 40) / 40)
        if (t // 3) % 5 or t < 40:
            brilho(tela, olho, int(10 * l.s), (255, 40, 30), int(200 * forte))
    else:
        pygame.draw.circle(tela, (24, 24, 28), olho, max(2, int(3 * l.s)))
    if t > 10:
        balao(tela, l, "MISSÃO CUMPRIDA." if t < 70 else "DESLIGANDO...", 160)
    if t > 80:  # o simbolozinho de desligado
        x, y = l.x + l.dir * 40 * l.s, l.y - 150 * l.s
        pygame.draw.arc(tela, (230, 230, 240), (x - 10, y - 10, 20, 20), 2.2, 7.2, 3)
        pygame.draw.line(tela, (230, 230, 240), (x, y - 12), (x, y - 2), 3)


def max_voa_ef(l, tela, t):
    """Depois que some lá em cima: um pontinho cruzando o céu... e brilha (TING!)."""
    if not 70 <= t < 130:
        return
    k = min(1, (t - 70) / 36)
    x0 = l.extra.get("voa_x", l.x)
    x, y = x0 + l.dir * 220 * k, 240 - 70 * k
    if k < 1:
        for i in range(1, 8):  # o rastro de fumaça fininho
            kk = max(0, k - i * 0.03)
            pygame.draw.circle(tela, (230, 230, 236), (int(x0 + l.dir * 220 * kk), int(240 - 70 * kk)), max(1, 4 - i // 2))
        brilho(tela, (int(x), int(y)), 8, (255, 200, 120), 220)
        pygame.draw.circle(tela, (255, 255, 255), (int(x), int(y)), 2)
    else:  # a estrelinha do TING!
        u = t - 106
        tam = 22 * math.sin(min(1, u / 24) * math.pi)
        if tam > 1:
            for a, f in ((0, 1), (math.pi / 2, 1), (math.pi / 4, 0.45), (3 * math.pi / 4, 0.45)):
                dx, dy = math.cos(a) * tam * f, math.sin(a) * tam * f
                pygame.draw.line(tela, (255, 255, 230), (x - dx, y - dy), (x + dx, y + dy), 3 if f == 1 else 2)
            brilho(tela, (int(x), int(y)), int(tam), (255, 240, 180), 180)


def max_voa(l, t, jogo):
    if t == 107:
        som.tocar("blip", 0.6)  # TING!
    if t == 26:
        l.extra["voa_x"] = l.x
    if t < 26:  # pose de herói, os jatos esquentando
        l.sobrepor = p_(l, "vitoria")
        if t > 8:
            fogo(jogo, l.x - 6 * l.s, l.y, 0.6)
            fogo(jogo, l.x + 6 * l.s, l.y, 0.6)
        if t == 10:
            som.tocar("carga", 0.6)
        return
    l.sobrepor = p_(l, "m_voo")
    sobe = t - 26
    l.y = CHAO - sobe * sobe * 0.3
    l.vy = 0
    if l.y > -120:
        fogo(jogo, l.x - 6 * l.s, l.y, 1.6)
        fogo(jogo, l.x + 6 * l.s, l.y, 1.6)
        if t % 2 == 0:
            fumaca(jogo, l.x, l.y + 12, 2, (210, 210, 216), 2.5, 0.6)
    if t == 26:
        som.tocar("foguete")
        jogo.tremer(10)
        fumaca(jogo, l.x, CHAO - 4, 14, (210, 210, 216), 5, -0.6)


# =====================================================================
# RIB
# =====================================================================
def rib_shuriken(l, t, jogo):
    l.sobrepor = p_(l, "r_arma" if ciclo(t, 90) < 60 else "r_cruzado")


def rib_shuriken_ef(l, tela, t):
    import ult2
    u = ciclo(t, 90)
    mx, my = ponto(l, "mf")
    if u < 30:  # girando no dedo (com o borrão de tão rápido)
        pygame.draw.circle(tela, (230, 236, 250), (int(mx), int(my - 12 * l.s)), int(15 * l.s), 1)
        ult2.desenha_shuriken(tela, mx, my - 12 * l.s, 13 * l.s, u * 0.9)
    elif u < 56:  # joga pro alto e pega
        k = (u - 30) / 26
        y = my - 12 * l.s - math.sin(k * math.pi) * 140
        pygame.draw.line(tela, (230, 236, 250), (mx, y + (16 if k < 0.5 else -16)), (mx, y), 2)
        ult2.desenha_shuriken(tela, mx, y, 13 * l.s, u * 0.6)


BAMBU = 110


def rib_bambu(l, t, jogo):
    l.x = l.extra.setdefault("bambu_x", l.x) + math.sin(t * 0.05) * 6  # o bambu balançando com ele em cima
    l.y = CHAO - BAMBU * l.s * suave(min(1, t / 16))
    l.vy = 0
    l.sobrepor = p_(l, "r_cruzado" if t > 14 else "pulo")


def rib_bambu_ef(l, tela, t):
    base_x = l.extra.get("bambu_x", l.x)
    topo = CHAO - BAMBU * l.s
    n = 5
    for i in range(n):  # o bambu (curvando um pouquinho com o balanço)
        k0, k1 = i / n, (i + 1) / n
        x0 = base_x + (l.x - base_x) * k0 * k0
        x1 = base_x + (l.x - base_x) * k1 * k1
        y0, y1 = CHAO - BAMBU * l.s * k0, CHAO - BAMBU * l.s * k1
        pygame.draw.line(tela, (30, 50, 20), (x0, y0), (x1, y1), 14)
        pygame.draw.line(tela, (90, 160, 60), (x0, y0), (x1, y1), 10)
        pygame.draw.line(tela, (50, 90, 30), (x1 - 7, y1), (x1 + 7, y1), 3)
    for lado in (-1, 1):  # as folhas
        pygame.draw.polygon(tela, (80, 150, 60), [(l.x, topo + 24), (l.x + lado * 30, topo + 14), (l.x + lado * 6, topo + 32)])
    if t > 14:  # o cachecol balançando no vento
        cb = ponto(l, "cb")
        pts = [(cb[0] - l.dir * (4 + i * 8), cb[1] + 8 + math.sin(t * 0.3 + i * 0.8) * 4 + i) for i in range(6)]
        pygame.draw.lines(tela, (20, 10, 10), False, pts, 6)
        pygame.draw.lines(tela, (200, 40, 40), False, pts, 4)


# =====================================================================
# TRAFO
# =====================================================================
def trafo_rabo(l, t, jogo):
    l.sobrepor = p_(l, "sentado")


def trafo_rabo_ef(l, tela, t):
    qd, pc, cb = ponto(l, "qd"), ponto(l, "pc"), ponto(l, "cb")
    for i in range(4):  # as patas extras (cada uma num ritmo)
        bx = qd[0] + (pc[0] - qd[0]) * (0.3 + i * 0.15)
        by = qd[1] + (pc[1] - qd[1]) * (0.3 + i * 0.15)
        a = math.sin(t * (0.3 + i * 0.13) + i) * 0.8
        ex, ey = bx + l.dir * math.cos(a + 1.2) * 34 * l.s, by + math.sin(a + 1.2) * 34 * l.s
        pygame.draw.line(tela, (30, 24, 10), (bx, by), (ex, ey), int(10 * l.s))
        pygame.draw.line(tela, (176, 140, 60), (bx, by), (ex, ey), int(7 * l.s))
        pygame.draw.circle(tela, (30, 24, 10), (int(ex), int(ey)), int(5 * l.s))
    a = math.sin(t * 0.8) * 0.9  # o rabo abanando
    tx, ty = qd[0] - l.dir * math.cos(a) * 46 * l.s, qd[1] - 24 * l.s - math.sin(a) * 26 * l.s
    pygame.draw.line(tela, (30, 24, 10), qd, (tx, ty), int(11 * l.s))
    pygame.draw.line(tela, (176, 140, 60), qd, (tx, ty), int(8 * l.s))
    for i in range(3):  # o abano (riscos de movimento)
        pygame.draw.arc(tela, (255, 255, 255), (tx - 20, ty - 20, 40, 40), a + i * 0.3, a + i * 0.3 + 0.5, 2)
    boca = (cb[0] + l.dir * 10 * l.s, cb[1] + 4 * l.s)  # a língua comprida demais
    pts = [(boca[0] + l.dir * i * 6 * l.s, boca[1] + i * i * 1.6 * l.s + math.sin(t * 0.4 + i) * 2) for i in range(5)]
    pygame.draw.lines(tela, (120, 30, 50), False, pts, int(6 * l.s))
    pygame.draw.lines(tela, (235, 110, 140), False, pts, int(4 * l.s))


def trafo_desfile(l, t, jogo):
    from personagens import PERSONAGENS
    if "desfile" not in l.extra:
        outros = [f for f in PERSONAGENS if f["nome"] != "TRAFO"]
        rnd = random.Random(getattr(jogo, "t_total", 0))
        l.extra["desfile"] = rnd.sample(outros, 3)
    fase = ciclo(t, 120) // 30
    if ciclo(t, 30) == 0:
        fumaca(jogo, l.x, l.y - 60, 10, (200, 220, 160), 3, -1)
        som.tocar("puf", 0.5)
    if fase < 3:
        f = l.extra["desfile"][fase]
        l.disfarce = f
        poses = dict(l.poses)
        poses.update(f.get("poses", {}))
        l.sobrepor = dict(poses.get("vitoria") or poses["parado"])
    else:
        l.disfarce = None
        l.sobrepor = p_(l, "t_olhos")


# =====================================================================
# KING RIP
# =====================================================================
def king_reverencia(l, t, jogo):
    from golpes import misturar
    u = ciclo(t, 120)
    junta = suave(min(1, u / 14))  # 1) junta os pés e põe o punho na palma
    curva = suave(min(1, max(0, (u - 24) / 16))) * (1 - suave(max(0, (u - 70) / 16)))  # 2) curva bem devagar
    sai = suave(max(0, (u - 100) / 20))  # 3) volta pra base de luta
    p = misturar(misturar(p_(l, "parado"), POSES_EXTRA["saudacao"], junta), POSES_EXTRA["reverencia"], curva)
    l.sobrepor = misturar(p, p_(l, "parado"), sai)
    if u == 24:
        som.tocar("defesa", 0.3)  # (o tapa do punho na palma)


def king_nunchaku(l, t, jogo):
    from golpes import misturar
    seq = ("k_gira", "k_estrela", "k_arremesso", "k_gira", "k_chute_alto", "k_bastao")
    u = ciclo(t, 130)
    i = min(len(seq) - 1, u // 14)
    j = min(len(seq) - 1, i + 1)
    k = suave(min(1, (u % 14) / 8)) if i < len(seq) - 1 and u // 14 < len(seq) - 1 else 0
    l.sobrepor = misturar(p_(l, seq[i]), p_(l, seq[j]), k) if u < 14 * (len(seq) - 1) else p_(l, seq[-1])
    if u % 14 == 0 and u // 14 < len(seq) - 1:
        som.tocar("vento", 0.4)


def king_nunchaku_ef(l, tela, t):
    u = ciclo(t, 130)
    if u >= 14 * 5:
        return
    mx, my = ponto(l, "mf")
    a = u * 0.9
    for i in range(3):  # o borrão do nunchaku girando
        r = int((26 - i * 5) * l.s)
        pygame.draw.arc(tela, (255, 245, 210), (mx - r, my - r, 2 * r, 2 * r), a - i * 0.5, a - i * 0.5 + 1.6, 3 - i)


# =====================================================================
# CANNAN
# =====================================================================
POSES_CANNAN_V = {
    "sopra": dict(pt=(-18, 0), jt=(-14, 30), pf=(16, 1), jf=(16, 32), qd=(0, 59), pc=(4, 100), cb=(6, 116),
                  ct=(-8, 80), mt=(2, 62), cf=(20, 98), mf=(16, 124)),        # canhão de pé do lado da cara
    "ombro": dict(pt=(-20, 0), jt=(-14, 30), pf=(18, 1), jf=(16, 32), qd=(0, 59), pc=(2, 100), cb=(4, 116),
                  ct=(-6, 80), mt=(6, 62), cf=(22, 104), mf=(-4, 120)),       # canhão apoiado no ombro
    "pendura": dict(pt=(-8, 2), jt=(-4, 30), pf=(8, 6), jf=(10, 32), qd=(0, 60), pc=(2, 102), cb=(4, 118),
                    ct=(4, 124), mt=(6, 146), cf=(18, 86), mf=(26, 70)),      # pendurado na escada (mão pra cima)
}
proporcionar(POSES_CANNAN_V)


def ponta_canhao(l):
    c, m = ponto(l, "cf"), ponto(l, "mf")
    dx, dy = m[0] - c[0], m[1] - c[1]
    n = math.hypot(dx, dy) or 1
    return m[0] + dx / n * 16 * l.s, m[1] + dy / n * 16 * l.s


def cannan_fumega(l, t, jogo):
    from golpes import misturar
    if t < 30:  # 1) acabou de atirar: o canhão ainda apontado, SOLTANDO FUMAÇA
        l.sobrepor = p_(l, "c_canhao")
        if t % 3 == 0:
            x, y = ponta_canhao(l)
            fumaca(jogo, x, y, 2, (196, 196, 202), 1.2, -1.4)
    elif t < 70:  # 2) levanta do lado da cara e SOPRA (fuuu~)
        k = suave(min(1, (t - 30) / 10))
        l.sobrepor = misturar(p_(l, "c_canhao"), POSES_CANNAN_V["sopra"], k)
        if 44 <= t < 60 and t % 2 == 0:
            x, y = ponta_canhao(l)
            fumaca(jogo, x - l.dir * 8, y - 4, 2, (220, 220, 226), 1.5, -2.2)
        if t == 44:
            som.tocar("vento", 0.5)
    else:  # 3) apoia o canhão no ombro, todo convencido
        k = suave(min(1, (t - 70) / 12))
        l.sobrepor = misturar(POSES_CANNAN_V["sopra"], POSES_CANNAN_V["ombro"], k)
        if t == 76:
            som.tocar("defesa", 0.35)
        if t > 90 and t % 14 == 0:
            x, y = ponta_canhao(l)
            fumaca(jogo, x, y, 1, (200, 200, 206), 0.6, -0.8)


def cannan_fumega_ef(l, tela, t):
    if 30 <= t < 30 + 44:  # o brilho quente na ponta do canhão (vai esfriando)
        x, y = ponta_canhao(l)
        brilho(tela, (int(x), int(y)), int(14 * l.s), (255, 150, 60), int(200 * (1 - (t - 30) / 44)))
    elif t < 30:
        x, y = ponta_canhao(l)
        brilho(tela, (int(x), int(y)), int(16 * l.s), (255, 170, 70), 210)
    if 44 <= t < 66:
        from efeitos import texto
        cb = ponto(l, "cb")
        texto(tela, "fuuu~", 16, (240, 240, 250), (int(cb[0] + l.dir * 34 * l.s), int(cb[1] - 30 * l.s - (t - 44))))
    if t > 90:  # o sorrisinho convencido
        balao(tela, l, "Fácil demais.", 160)


HELI_CHEGA, HELI_ESCADA, HELI_PEGA, HELI_SOBE = 44, 64, 78, 86


def heli_pos(l, t):
    """Onde está o helicóptero (o mesmo cálculo no movimento e no desenho)."""
    x0 = l.extra.get("heli_x", l.x)
    alto = CHAO - 236 * l.s
    if t < HELI_CHEGA:  # chega voando de trás
        k = suave(t / HELI_CHEGA)
        return x0 - l.dir * 560 * (1 - k), alto + 40 * (1 - k)
    if t < HELI_SOBE:
        return x0, alto + math.sin(t * 0.15) * 4
    u = t - HELI_SOBE  # vai embora pra frente e pra cima, levando ele
    return x0 + l.dir * u * u * 0.12, alto - u * u * 0.05


def escada_fim(l, t):
    hx, hy = heli_pos(l, t)
    k = suave(min(1, max(0, (t - HELI_ESCADA + 14) / 14)))
    comprimento = 236 * l.s - 150 * l.s - 20  # (do helicóptero parado até a mão dele)
    return hx, hy + 20 + comprimento * k


def cannan_missao(l, t, jogo):
    from golpes import misturar
    if t == 0 or "heli_x" not in l.extra:
        l.extra["heli_x"] = l.x - l.dir * 30 * l.s
        l.extra["chao_x"] = l.x
    if t < HELI_PEGA - 6:
        l.sobrepor = p_(l, "c_continencia")
    else:
        l.sobrepor = misturar(p_(l, "c_continencia"), POSES_CANNAN_V["pendura"], suave(min(1, (t - HELI_PEGA + 6) / 6)))
    if t < HELI_PEGA:  # anda até ficar embaixo da escada
        l.x = l.extra["chao_x"] + (l.extra["heli_x"] - l.extra["chao_x"]) * suave(min(1, max(0, (t - HELI_ESCADA) / 12)))
        l.y = CHAO
    else:  # pendurado: vai junto com a escada
        ex, ey = escada_fim(l, t)
        l.x, l.y = ex, ey + 146 * l.s
    l.vy = 0
    if t % 5 == 0 and t < HELI_SOBE + 40:
        som.tocar("vento", 0.15)  # (o barulho da hélice)
    if t == HELI_PEGA:
        som.tocar("pulo", 0.5)
    if t == HELI_CHEGA:
        hx, _ = heli_pos(l, t)
        fumaca(jogo, hx, CHAO - 4, 10, (190, 180, 160), 4, -0.8)  # a poeira que a hélice levanta


def cannan_missao_ef(l, tela, t):
    s = l.s
    hx, hy = heli_pos(l, t)
    d = l.dir
    if hy < -120:
        return
    if t >= HELI_ESCADA - 14:  # a escada de corda
        ex, ey = escada_fim(l, t)
        for lado in (-6, 6):
            pygame.draw.line(tela, (60, 46, 30), (hx + lado, hy + 20), (ex + lado, ey), 2)
        n = int((ey - hy - 20) / 12)
        for i in range(1, n + 1):
            y = hy + 20 + i * 12
            pygame.draw.line(tela, (120, 90, 54), (hx - 6 + (ex - hx) * i / max(1, n), y),
                             (hx + 6 + (ex - hx) * i / max(1, n), y), 2)
    # o HELICÓPTERO (verde do exército)
    cor, esc_, vid = (78, 100, 62), (44, 58, 36), (150, 210, 236)
    borda = (16, 20, 14)
    cauda = [(hx - d * 30, hy - 6), (hx - d * 110, hy - 12), (hx - d * 110, hy - 4), (hx - d * 30, hy + 6)]
    pygame.draw.polygon(tela, borda, [(x, y) for x, y in cauda], 0)
    pygame.draw.polygon(tela, cor, [(x - d * 0, y + (1 if i < 2 else -1)) for i, (x, y) in enumerate(cauda)])
    pygame.draw.polygon(tela, borda, cauda, 2)
    rot = abs(math.sin(t * 1.1)) * 14  # hélice de trás
    pygame.draw.ellipse(tela, (60, 60, 60), (hx - d * 110 - 4, hy - 8 - rot, 8, rot * 2 + 2))
    corpo = pygame.Rect(0, 0, 96, 44)
    corpo.center = (int(hx), int(hy))
    pygame.draw.ellipse(tela, borda, corpo.inflate(6, 6))
    pygame.draw.ellipse(tela, cor, corpo)
    pygame.draw.ellipse(tela, esc_, (corpo.x + 6, corpo.centery + 4, corpo.w - 12, 14))  # sombra embaixo
    vidro = pygame.Rect(0, 0, 34, 24)
    vidro.center = (int(hx + d * 26), int(hy - 4))
    pygame.draw.ellipse(tela, borda, vidro.inflate(4, 4))
    pygame.draw.ellipse(tela, vid, vidro)
    pygame.draw.ellipse(tela, (230, 250, 255), (vidro.x + 6, vidro.y + 4, 10, 6))
    pygame.draw.circle(tela, (240, 240, 240), (int(hx - d * 14), int(hy)), 7)  # a estrela do exército
    pygame.draw.circle(tela, esc_, (int(hx - d * 14), int(hy)), 4)
    for lado in (-1, 1):  # os esquis
        pygame.draw.line(tela, borda, (hx + lado * 18, hy + 22), (hx + lado * 18, hy + 30), 3)
    pygame.draw.line(tela, borda, (hx - 40, hy + 31), (hx + 40, hy + 31), 4)
    pygame.draw.line(tela, borda, (hx, hy - 22), (hx, hy - 30), 5)  # o eixo e a HÉLICE girando (borrão)
    pa = 90
    pygame.draw.ellipse(tela, (40, 40, 40), (hx - pa, hy - 34, pa * 2, 8), 2)
    a = math.sin(t * 0.9)
    pygame.draw.line(tela, (20, 20, 20), (hx - pa * a, hy - 30), (hx + pa * a, hy - 30), 4)
    if 6 < t < HELI_ESCADA:
        balao(tela, l, "Missão cumprida, base!", 160)


# =====================================================================
# FINN
# =====================================================================
TRONO_SOBE, TRONO_SENTA = 14, 40


def finn_trono(l, t, jogo):
    from golpes import misturar
    if t < TRONO_SOBE:  # bate o cajado no chão
        l.sobrepor = p_(l, "f_cajado_a" if t < 6 else "f_cajado_b")
        l.y = CHAO
    elif t < TRONO_SENTA:  # o trono sobe atrás dele... e ele senta
        k = suave(max(0, (t - TRONO_SENTA + 12) / 12))
        l.sobrepor = misturar(p_(l, "parado"), p_(l, "sentado"), k)
        l.y = CHAO - 30 * l.s * k
    else:
        l.sobrepor = p_(l, "sentado")
        l.y = CHAO - 30 * l.s
    l.vy = 0
    if t == 6:
        som.tocar("terra", 0.8)
        jogo.tremer(8)
    if TRONO_SOBE <= t < TRONO_SOBE + 20 and t % 3 == 0:  # poeira e pedrinhas subindo junto
        x = l.x - l.dir * 26 * l.s
        fumaca(jogo, x + random.uniform(-30, 30), CHAO - 4, 1, (150, 140, 126), 2, -1)
        jogo.faiscas.append([x + random.uniform(-26, 26), CHAO - 6, random.uniform(-2, 2), random.uniform(-5, -2), 18,
                             (110, 104, 96), 3])
    if t == TRONO_SOBE + 20:
        som.tocar("queda", 0.5)


def finn_trono_atras(l, tela, t):
    if t < TRONO_SOBE:
        return
    s = l.s
    sobe = suave(min(1, (t - TRONO_SOBE) / 20))
    x = l.x - l.dir * 6 * s
    alto = 170 * s
    base = CHAO + alto * (1 - sobe)  # sai DE DENTRO do chão (o que está embaixo não aparece)
    camada = pygame.Surface((int(150 * s) + 12, int(alto) + 8), pygame.SRCALPHA)
    w, h = camada.get_size()
    cx = w // 2
    pedra, escura, clara, borda = (128, 122, 114), (92, 88, 82), (162, 156, 146), (28, 26, 24)
    runa = (90, 230, 255) if t > TRONO_SENTA else (70, 90, 100)

    def bloco(r, cor=pedra, raio=4):
        pygame.draw.rect(camada, borda, r.inflate(6, 6), border_radius=raio)
        pygame.draw.rect(camada, cor, r, border_radius=raio)
        pygame.draw.rect(camada, clara, (r.x + 3, r.y + 3, r.w - 6, max(2, int(5 * s))), border_radius=3)

    # o ENCOSTO alto com a ponta e os 2 pináculos
    enc = pygame.Rect(0, 0, int(84 * s), int(alto - 26 * s))
    enc.midbottom = (cx, h - 4)
    ponta = [(enc.x, enc.y), (cx, enc.y - 22 * s), (enc.right, enc.y)]
    pygame.draw.polygon(camada, borda, [(px, py - 3) for px, py in ponta] + [(enc.right + 3, enc.y + 4), (enc.x - 3, enc.y + 4)])
    pygame.draw.polygon(camada, pedra, ponta + [(enc.right, enc.y + 4), (enc.x, enc.y + 4)])
    bloco(enc)
    pygame.draw.rect(camada, escura, enc.inflate(-int(22 * s), -int(30 * s)).move(0, -int(6 * s)), 3, border_radius=4)
    for lado in (-1, 1):
        pin = pygame.Rect(0, 0, int(14 * s), int(30 * s))
        pin.midbottom = (cx + lado * int(42 * s), enc.y + 4)
        bloco(pin, escura, 3)
        pygame.draw.circle(camada, borda, (pin.centerx, pin.y - 2), int(8 * s))
        pygame.draw.circle(camada, pedra, (pin.centerx, pin.y - 2), int(6 * s))
    pygame.draw.circle(camada, borda, (cx, int(enc.y + 22 * s)), int(13 * s))  # o círculo das runas
    pygame.draw.circle(camada, escura, (cx, int(enc.y + 22 * s)), int(11 * s))
    for a in range(3):
        ang = a * math.tau / 3 + 0.5
        pygame.draw.line(camada, runa, (cx, enc.y + 22 * s), (cx + math.cos(ang) * 9 * s, enc.y + 22 * s + math.sin(ang) * 9 * s), 3)
    for i in range(2):
        ry = enc.y + (48 + i * 26) * s
        pygame.draw.line(camada, runa, (cx - 8 * s, ry), (cx + 8 * s, ry + 10 * s), 3)
        pygame.draw.line(camada, runa, (cx + 8 * s, ry), (cx - 2 * s, ry + 12 * s), 3)
    pygame.draw.ellipse(camada, (80, 120, 60), (enc.x + 2, enc.bottom - 30 * s, 22 * s, 10 * s))  # musgo
    # o ASSENTO (largo, aparece dos dois lados dele) e os BRAÇOS com bolotas
    assento = pygame.Rect(0, 0, int(118 * s), int(46 * s))
    assento.midbottom = (cx, h - 4)
    bloco(assento)
    for lado in (-1, 1):
        br = pygame.Rect(0, 0, int(20 * s), int(76 * s))
        br.midbottom = (cx + lado * int(58 * s), h - 4)
        bloco(br, escura, 6)
        pygame.draw.circle(camada, borda, (br.centerx, br.y), int(12 * s))
        pygame.draw.circle(camada, pedra, (br.centerx, br.y), int(10 * s))
        pygame.draw.circle(camada, clara, (br.centerx - 3, br.y - 3), int(3 * s))
    rect = camada.get_rect(midbottom=(int(x), int(base)))
    rect_vis = rect.clip(pygame.Rect(0, 0, tela.get_width(), CHAO + 2))
    if rect_vis.h > 0:
        tela.blit(camada, rect_vis, pygame.Rect(rect_vis.x - rect.x, rect_vis.y - rect.y, rect_vis.w, rect_vis.h))
    if t > TRONO_SENTA:
        brilho(tela, (int(x), int(CHAO - alto * 0.62)), int(46 * s), (90, 230, 255), int(60 + 40 * math.sin(t * 0.1)))


def dragaozinho(tela, x, y, t, d, s=1.0):
    """Um dragãozinho de verdade: corpo, asas batendo, rabo, chifrinhos e olho."""
    borda, cor, barriga, asa_c = (40, 14, 8), (220, 80, 30), (250, 190, 90), (180, 50, 30)
    bate = math.sin(t * 0.6)
    for lado, k in ((-1, 0.75), (1, 1.0)):  # as asas (a de trás mais escura)
        ponta = (x - d * 6 * s, y - (22 + 10 * bate) * s * k)
        meio = (x - d * 20 * s, y - (8 + 6 * bate) * s * k)
        pts = [(x - d * 2 * s, y - 2 * s), ponta, meio, (x - d * 12 * s, y + 2 * s)]
        pygame.draw.polygon(tela, borda, pts)
        pygame.draw.polygon(tela, asa_c if lado > 0 else (130, 36, 24), [(px * 0.9 + x * 0.1, py * 0.9 + y * 0.1) for px, py in pts])
    rabo = [(x - d * (10 + i * 5) * s, y + (2 + math.sin(t * 0.3 + i) * 2 + i * 1.2) * s) for i in range(4)]
    pygame.draw.lines(tela, borda, False, [(x, y)] + rabo, max(3, int(5 * s)))
    pygame.draw.lines(tela, cor, False, [(x, y)] + rabo, max(2, int(3 * s)))
    pygame.draw.polygon(tela, cor, [rabo[-1], (rabo[-1][0] - d * 5 * s, rabo[-1][1] - 3 * s),
                                    (rabo[-1][0] - d * 4 * s, rabo[-1][1] + 4 * s)])
    corpo = pygame.Rect(0, 0, int(24 * s), int(14 * s))
    corpo.center = (int(x), int(y))
    pygame.draw.ellipse(tela, borda, corpo.inflate(4, 4))
    pygame.draw.ellipse(tela, cor, corpo)
    pygame.draw.ellipse(tela, barriga, (corpo.x + 4, corpo.centery, corpo.w - 8, corpo.h // 2 - 1))
    cab = (int(x + d * 13 * s), int(y - 7 * s))
    pygame.draw.circle(tela, borda, cab, int(8 * s))
    pygame.draw.circle(tela, cor, cab, int(6.5 * s))
    pygame.draw.ellipse(tela, cor, (cab[0] + (0 if d > 0 else -9 * s), cab[1] - 1, 9 * s, 6 * s))  # focinho
    for k in (-1, 1):  # chifrinhos
        pygame.draw.line(tela, (250, 230, 190), (cab[0] - d * 2 * s + k * 2, cab[1] - 5 * s),
                         (cab[0] - d * 6 * s + k * 2, cab[1] - 11 * s), 2)
    pygame.draw.circle(tela, (255, 240, 120), (int(cab[0] + d * 2 * s), int(cab[1] - 2 * s)), max(2, int(2 * s)))
    pygame.draw.circle(tela, (10, 10, 10), (int(cab[0] + d * 2.5 * s), int(cab[1] - 2 * s)), 1)


DRAGAO_POUSA = 90


def finn_dragao(l, t, jogo):
    from golpes import misturar
    if t < 20:  # levanta o cajado e chama
        l.sobrepor = p_(l, "f_vitoria" if l.poses.get("f_vitoria") else "vitoria")
    elif t < DRAGAO_POUSA:
        l.sobrepor = p_(l, "f_vitoria" if l.poses.get("f_vitoria") else "vitoria")
    else:  # o braço desce, o dragãozinho no ombro
        l.sobrepor = misturar(p_(l, "f_vitoria"), p_(l, "parado"), suave(min(1, (t - DRAGAO_POUSA) / 12)))
    if t == 14:
        som.tocar("carga", 0.6)
    if t in (60, 64, 68):  # cospe um foguinho pro alto
        x, y = dragao_pos(l, t)
        fogo(jogo, x + l.dir * 20 * l.s, y - 10 * l.s, 0.8)
        if t == 60:
            som.tocar("explosao", 0.25)
    if t == DRAGAO_POUSA + 10:
        som.tocar("blip", 0.5)


def dragao_pos(l, t):
    s = l.s
    if t < 20:
        return None
    if t < 34:  # sai de uma faísca na ponta do cajado e cresce
        m = ponto(l, "mf")
        return m[0], m[1] - 30 * s
    if t < DRAGAO_POUSA:  # voa em volta dele
        a = (t - 34) * 0.11
        return l.x + math.cos(a) * 80 * s, l.y - 120 * s + math.sin(a * 2) * 26 * s
    ombro = ponto(l, "pc")
    k = suave(min(1, (t - DRAGAO_POUSA) / 14))
    a = (DRAGAO_POUSA - 34) * 0.11
    x0, y0 = l.x + math.cos(a) * 80 * s, l.y - 120 * s + math.sin(a * 2) * 26 * s
    return x0 + (ombro[0] - l.dir * 4 * s - x0) * k, y0 + (ombro[1] - 18 * s - y0) * k


def finn_dragao_ef(l, tela, t):
    pos = dragao_pos(l, t)
    if pos is None:
        return
    x, y = pos
    if t < 34:  # a faísca mágica que vira dragão
        k = (t - 20) / 14
        brilho(tela, (int(x), int(y)), int((10 + 30 * k) * l.s), (255, 170, 60), 220)
        if t < 28:
            return
    if t < DRAGAO_POUSA:
        a = (t - 34) * 0.11
        d = 1 if -math.sin(a) > 0 else -1  # vira pra onde está voando
    else:
        d = l.dir
    tam = l.s * (0.4 + 0.6 * min(1, max(0, (t - 28) / 10))) * 1.5
    dragaozinho(tela, x, y, t, d, tam)
    if t in range(60, 72):  # o foguinho
        bx, by = x + d * 26 * tam, y - 8 * tam
        brilho(tela, (int(bx), int(by)), int(18 * tam), (255, 140, 40), 200)


# =====================================================================
# KUN
# =====================================================================
SOFA_SURGE, SOFA_DEITA = 18, 34


def kun_sofa(l, t, jogo):
    from golpes import misturar
    if t < SOFA_SURGE:  # joga uma carta no chão...
        l.sobrepor = p_(l, "k_lanca")
        l.y = CHAO
    else:  # ...que vira um SOFÁ, e ele se joga deitado
        k = suave(min(1, max(0, (t - SOFA_SURGE) / (SOFA_DEITA - SOFA_SURGE))))
        l.sobrepor = misturar(p_(l, "parado"), p_(l, "deitado"), k)
        l.y = CHAO - (32 * l.s) * k - math.sin(k * math.pi) * 30 * l.s
    l.vy = 0
    if t == 8:
        som.tocar("vento", 0.5)
    if t == SOFA_SURGE:
        som.tocar("puf", 0.7)
        fumaca(jogo, l.x - l.dir * 10 * l.s, CHAO - 20, 14, (230, 220, 240), 4, -1)
    if t == SOFA_DEITA:
        som.tocar("queda", 0.3)


def kun_sofa_atras(l, tela, t):
    import kun
    s = l.s
    if t < SOFA_SURGE:
        k = min(1, t / 10)
        kun.carta_no_chao(tela, l.x - l.dir * (10 + 60 * (1 - k)) * s, s, t, l=l)
        return
    cresce = min(1, (t - SOFA_SURGE) / 6)
    x, y = l.x - l.dir * 10 * s, CHAO
    w, h = 150 * s * cresce, 52 * s * cresce
    if w < 4:
        return
    borda, cor, esc, clara = (34, 8, 14), (176, 40, 52), (130, 26, 38), (214, 80, 90)
    encosto = pygame.Rect(0, 0, w * 0.86, h * 0.9)
    encosto.midbottom = (int(x - l.dir * 4 * s), int(y - h * 0.42))
    pygame.draw.rect(tela, borda, encosto.inflate(6, 6), border_radius=int(14 * s))
    pygame.draw.rect(tela, esc, encosto, border_radius=int(12 * s))
    for i in range(3):  # os botões do capitonê
        pygame.draw.circle(tela, borda, (int(encosto.x + encosto.w * (0.25 + i * 0.25)), int(encosto.centery)), 2)
    assento = pygame.Rect(0, 0, w * 0.86, h * 0.36)
    assento.midbottom = (int(x), int(y - h * 0.16))
    pygame.draw.rect(tela, borda, assento.inflate(6, 6), border_radius=int(8 * s))
    pygame.draw.rect(tela, cor, assento, border_radius=int(8 * s))
    pygame.draw.line(tela, clara, (assento.x + 8, assento.y + 4), (assento.right - 8, assento.y + 4), 3)
    pygame.draw.line(tela, borda, (assento.centerx, assento.y + 2), (assento.centerx, assento.bottom - 2), 2)  # 2 almofadas
    for lado in (-1, 1):  # os braços gordinhos
        br = pygame.Rect(0, 0, w * 0.16, h * 0.62)
        br.midbottom = (int(x + lado * w * 0.45), int(y - h * 0.14))
        pygame.draw.rect(tela, borda, br.inflate(6, 6), border_radius=int(10 * s))
        pygame.draw.rect(tela, cor, br, border_radius=int(10 * s))
        pygame.draw.rect(tela, clara, (br.x + 3, br.y + 3, br.w - 6, 5), border_radius=3)
    for lado in (-1, 1):  # os pezinhos dourados
        pygame.draw.rect(tela, (200, 160, 60), (x + lado * w * 0.38 - 4, y - h * 0.16, 8, h * 0.16))


def kun_sofa_ef(l, tela, t):
    if t > SOFA_DEITA + 10:  # o "ZzZ" de quem está à vontade
        from efeitos import texto
        cb = ponto(l, "cb")
        for i in range(3):
            u = (t + i * 20) % 60
            texto(tela, "z" if i % 2 else "Z", 12 + i * 3, (230, 230, 250),
                  (int(cb[0] - l.dir * 4 + u * 0.4 * l.dir), int(cb[1] - 20 - u)))


def kun_as(l, t, jogo):
    from golpes import misturar
    if t < 70:  # puxa as cartas da manga, uma atrás da outra, como mágico
        l.sobrepor = misturar(p_(l, "parado"), p_(l, "k_lanca"), 0.5 + 0.5 * math.sin(t * 0.3))
        if t % 6 == 0:
            som.tocar("vento", 0.2)
    else:  # e no fim: o ÁS lá em cima, na mão
        l.sobrepor = p_(l, "k_vitoria")
        if t == 70:
            som.tocar("confirma", 0.6)


def kun_as_ef(l, tela, t):
    import kun
    s = l.s
    manga = ponto(l, "mt")
    if t < 76:  # o chafariz de cartas saindo da manga (sobem, viram e caem)
        for i in range(12):
            nasce = i * 6
            u = t - nasce
            if not 0 <= u < 40:
                continue
            vx = l.dir * (2.2 + (i % 3) * 0.8) * s
            x = manga[0] + vx * u
            y = manga[1] - 7 * s * u + 0.32 * u * u
            if y > CHAO - 6:
                continue
            kun.carta(tela, (x, y), u * 0.25 * l.dir, 1.1 * s / 1.36, abs(math.cos(u * 0.25)) + 0.1, l=l)
    else:  # o ÁS gigante virando na mão levantada
        m = ponto(l, "mf")
        k = min(1, (t - 76) / 14)
        brilho(tela, (int(m[0]), int(m[1] - 30 * s)), int(46 * s * k), (255, 230, 120), 170)
        kun.carta(tela, (m[0], m[1] - 30 * s), 0, 3.2 * s / 1.36, max(0.1, abs(math.cos((1 - k) * math.pi * 1.5))),
                  brilha=True, l=l)
        if t > 90:
            balao(tela, l, "Sempre tenho um ás na manga!", 170)


# =====================================================================
# TROMOS
# =====================================================================
TETO_PULA, TETO_GRUDA = 12, 30
GOTAS = 34  # de quanto em quanto tempo cai uma gota de baba ácida


def xeno_teto(l, t, jogo):
    from golpes import misturar
    s = l.s
    topo = 100 * s + 70  # (de ponta-cabeça, os pés ficam grudados no alto da tela)
    if t < TETO_PULA:  # se agacha...
        l.sobrepor = p_(l, "x_rasteja")
        l.y, l.angulo = CHAO, 0
    elif t < TETO_GRUDA:  # ...pula girando...
        k = suave((t - TETO_PULA) / (TETO_GRUDA - TETO_PULA))
        l.sobrepor = p_(l, "x_salto")
        l.y = CHAO + (topo - CHAO) * k
        l.angulo = math.pi * k
    else:  # ...e fica PENDURADO NO TETO, de cabeça pra baixo, babando
        l.sobrepor = misturar(p_(l, "x_salto"), p_(l, "parado"), suave(min(1, (t - TETO_GRUDA) / 8)))
        l.y, l.angulo = topo, math.pi
    l.vy = 0
    if t == TETO_PULA:
        som.tocar("pulo", 0.6)
    if t == TETO_GRUDA:
        som.tocar("queda", 0.4)
        jogo.tremer(4)
    if t == TETO_GRUDA + 10:
        som.tocar("lingua", 0.5)  # (o chiado)
    u = t - TETO_GRUDA - 10
    if u > 0 and u % GOTAS == GOTAS - 1:  # a gota chegou no chão: chiado de ácido
        x, _ = gota_pos(l, u // GOTAS, GOTAS - 1)
        fumaca(jogo, x, CHAO - 4, 5, (150, 230, 90), 2, -1.2)
        som.tocar("puf", 0.3)


def gota_pos(l, i, u):
    cb = ponto(l, "cb")
    y0 = cb[1] + 10 * l.s
    k = u / (GOTAS - 1)
    return cb[0] + l.dir * 6 * l.s, y0 + (CHAO - y0) * k * k


def xeno_teto_ef(l, tela, t):
    u = t - TETO_GRUDA - 10
    if u < 0:
        return
    i, v = u // GOTAS, u % GOTAS
    cb = ponto(l, "cb")
    if v < 10:  # a baba esticando antes de cair
        boca = (cb[0] + l.dir * 6 * l.s, cb[1] + 8 * l.s)
        pygame.draw.line(tela, (150, 230, 90), boca, (boca[0], boca[1] + v * 2), 3)
        pygame.draw.circle(tela, (180, 255, 120), (int(boca[0]), int(boca[1] + v * 2)), 3)
    else:
        x, y = gota_pos(l, i, v)
        pygame.draw.circle(tela, (40, 80, 20), (int(x), int(y)), 5)
        pygame.draw.circle(tela, (170, 250, 100), (int(x), int(y)), 4)
        pygame.draw.circle(tela, (240, 255, 220), (int(x - 1), int(y - 1)), 1)
    for j in range(max(0, i - 2), i):  # as poças de ácido no chão (chiando)
        x, _ = gota_pos(l, j, GOTAS - 1)
        pygame.draw.ellipse(tela, (40, 70, 20), (x - 13, CHAO - 4, 26, 7))
        pygame.draw.ellipse(tela, (140, 220, 70), (x - 11, CHAO - 3, 22, 5))


CASULO_CHEGA, CASULO_CUSPE, CASULO_PRONTO = 30, 34, 84


def xeno_casulo(l, t, jogo):
    from golpes import misturar
    ox, oy, os_ = alvo(l)
    if t == 0 or "casulo_x" not in l.extra:
        l.extra["casulo_x"] = l.x
    if t < CASULO_CHEGA:  # vai andando até o derrotado
        k = suave(t / CASULO_CHEGA)
        l.x = l.extra["casulo_x"] + ((ox - l.dir * 90 * l.s) - l.extra["casulo_x"]) * k
        l.sobrepor = p_(l, ("andar1", "andar2", "andar3", "andar4")[(t // 5) % 4])
    elif t < CASULO_PRONTO:  # cospe a gosma várias vezes por cima dele
        l.sobrepor = p_(l, "x_cospe" if (t - CASULO_CUSPE) % 12 < 6 else "parado")
        if (t - CASULO_CUSPE) % 12 == 0 and t >= CASULO_CUSPE:
            som.tocar("lingua", 0.4)
    else:  # pronto: o troféu dele (de pé do lado, se exibindo)
        l.sobrepor = misturar(p_(l, "parado"), p_(l, "x_vitoria"), suave(min(1, (t - CASULO_PRONTO) / 10)))
        if t == CASULO_PRONTO:
            som.tocar("confirma", 0.4)


def xeno_casulo_ef(l, tela, t):
    ox, oy, os_ = alvo(l)
    if t >= CASULO_CUSPE and t < CASULO_PRONTO:  # o jato de gosma em arco
        u = (t - CASULO_CUSPE) % 12
        if u < 8:
            cb = ponto(l, "cb")
            boca = (cb[0] + l.dir * 14 * l.s, cb[1])
            alvo_ = (ox + math.sin(t) * 30 * os_, CHAO - 26 * os_)
            pts = []
            for i in range(12):
                k = i / 11 * min(1, (u + 1) / 4)
                pts.append((boca[0] + (alvo_[0] - boca[0]) * k, boca[1] + (alvo_[1] - boca[1]) * k - math.sin(k * math.pi) * 40))
            if len(pts) > 1:
                pygame.draw.lines(tela, (20, 30, 16), False, pts, 6)
                pygame.draw.lines(tela, (120, 170, 80), False, pts, 3)
    k = suave(min(1.0, max(0, (t - CASULO_CUSPE) / (CASULO_PRONTO - CASULO_CUSPE))))
    if k <= 0:
        return
    # o CASULO de gosma (cobre o derrotado deitado: vai crescendo a cada cuspida)
    w, h = (60 + 90 * k) * os_, (14 + 40 * k) * os_
    r = pygame.Rect(0, 0, w, h)
    r.midbottom = (int(ox), int(CHAO + 2))
    escuro, gosma, brilho_c = (14, 18, 14), (54, 66, 48), (150, 180, 130)
    pygame.draw.ellipse(tela, escuro, r.inflate(8, 8))
    pygame.draw.ellipse(tela, gosma, r)
    for i in range(5):  # as dobras/veias da gosma endurecida
        x = r.x + r.w * (0.15 + i * 0.17)
        pygame.draw.arc(tela, escuro, (x - 10, r.y + 4, 20, r.h - 8), 1.2, 5.0, 2)
    pygame.draw.ellipse(tela, (78, 94, 70), (r.x + 8, r.y + 4, r.w - 16, r.h * 0.4))  # brilho molhado
    pygame.draw.arc(tela, brilho_c, (r.x + r.w * 0.15, r.y + 4, r.w * 0.4, r.h * 0.6), 1.7, 2.9, 3)
    for i in range(4):  # fios de gosma grudando no chão
        x = r.x + r.w * (0.1 + i * 0.27)
        pygame.draw.line(tela, gosma, (x, r.bottom - 6), (x + (i - 1.5) * 8, CHAO + 2), 3)
    if k > 0.9:  # uma mão saindo, se mexendo (ele está lá dentro!)
        mx = r.right - 18 * os_
        a = math.sin(t * 0.4) * 0.5
        pygame.draw.line(tela, (230, 190, 150), (mx, r.y + 10), (mx + math.sin(a) * 10, r.y - 10 * os_), 4)
        pygame.draw.circle(tela, (230, 190, 150), (int(mx + math.sin(a) * 10), int(r.y - 10 * os_)), 4)


# =====================================================================
# TAI
# =====================================================================
DESCANSO_SENTA = 18


def tai_descanso(l, t, jogo):
    from golpes import misturar
    k = suave(min(1, t / DESCANSO_SENTA))
    l.sobrepor = misturar(p_(l, "parado"), p_(l, "t_senta"), k)
    if t == DESCANSO_SENTA:  # PLOFT! (senta pesado)
        som.tocar("queda", 0.7)
        jogo.tremer(6)
        fumaca(jogo, l.x, CHAO - 4, 10, (190, 170, 140), 4, -0.6)
    if t > DESCANSO_SENTA and t % 24 == 0:  # o vapor saindo da cabeça
        cb = ponto(l, "cb")
        fumaca(jogo, cb[0], cb[1] - 16 * l.s, 1, (240, 240, 244), 1, -1)


def tai_descanso_ef(l, tela, t):
    if t < DESCANSO_SENTA:
        return
    s = l.s
    mx, my = ponto(l, "mf")
    a = math.sin(t * 0.35) * 0.45  # o LEQUE abanando (grande, com as varetas)
    pts = [(mx + math.cos(-2.2 + a + i * 0.2) * 34 * s, my + math.sin(-2.2 + a + i * 0.2) * 34 * s) for i in range(8)]
    pygame.draw.polygon(tela, (40, 16, 16), [(mx, my)] + pts)
    pygame.draw.polygon(tela, (226, 64, 54), [(mx + (x - mx) * 0.96, my + (y - my) * 0.96) for x, y in pts] + [(mx, my)])
    for x, y in pts[::2]:
        pygame.draw.line(tela, (120, 30, 26), (mx, my), (x, y), 1)
    pygame.draw.lines(tela, (250, 220, 120), False, [(mx + (x - mx) * 0.8, my + (y - my) * 0.8) for x, y in pts], 2)
    for i in range(2):  # as gotas de suor escorrendo
        u = (t + i * 23) % 46
        cb = ponto(l, "cb")
        x = cb[0] - l.dir * (8 - i * 14) * s
        y = cb[1] - 8 * s + u * 0.5
        pygame.draw.circle(tela, (150, 210, 255), (int(x), int(y)), 3)
        pygame.draw.circle(tela, (230, 250, 255), (int(x - 1), int(y - 1)), 1)
    if (t // 50) % 2:
        balao(tela, l, "Ufa... ganhei.", 150)


TROFEU_CAI, TROFEU_PEGA, TROFEU_ERGUE = 24, 40, 56


def tai_trofeu(l, t, jogo):
    from golpes import misturar
    if t < TROFEU_PEGA:
        l.sobrepor = p_(l, "parado")
    elif t < TROFEU_ERGUE:  # agacha e pega (pesado!)
        l.sobrepor = p_(l, "t_agarra")
    else:  # ERGUE o troféu gigante
        l.sobrepor = misturar(p_(l, "t_agarra"), p_(l, "vitoria"), suave(min(1, (t - TROFEU_ERGUE) / 12)))
    if t == TROFEU_CAI:
        som.tocar("queda")
        jogo.tremer(12)
        fumaca(jogo, l.x + l.dir * 60 * l.s, CHAO - 4, 12, (200, 190, 160), 5, -0.8)
    if t == TROFEU_ERGUE + 10:
        som.tocar("confirma", 0.7)


def trofeu(tela, x, y, s):
    """A taça gigante (dourada, com alças, brilho e plaquinha Nº1). (x, y) = embaixo da base."""
    borda, ouro, ouro_esc, luz = (60, 40, 8), (250, 200, 60), (200, 140, 30), (255, 245, 200)
    base = pygame.Rect(0, 0, 44 * s, 14 * s)
    base.midbottom = (int(x), int(y))
    pygame.draw.rect(tela, borda, base.inflate(4, 4), border_radius=3)
    pygame.draw.rect(tela, (110, 70, 30), base, border_radius=3)
    pygame.draw.rect(tela, (230, 220, 200), (base.centerx - 9 * s, base.y + 3 * s, 18 * s, 8 * s))  # a plaquinha
    haste = pygame.Rect(0, 0, 10 * s, 22 * s)
    haste.midbottom = base.midtop
    pygame.draw.rect(tela, borda, haste.inflate(4, 2))
    pygame.draw.rect(tela, ouro_esc, haste)
    copa = [(x - 32 * s, y - 86 * s), (x + 32 * s, y - 86 * s), (x + 22 * s, y - 46 * s), (x + 6 * s, y - 36 * s),
            (x - 6 * s, y - 36 * s), (x - 22 * s, y - 46 * s)]
    for lado in (-1, 1):  # as alças
        pygame.draw.arc(tela, borda, (x + lado * 30 * s - 13 * s, y - 84 * s, 26 * s, 30 * s),
                        -1.6 if lado > 0 else 1.5, 1.6 if lado > 0 else 4.7, max(4, int(6 * s)))
        pygame.draw.arc(tela, ouro, (x + lado * 30 * s - 12 * s, y - 83 * s, 24 * s, 28 * s),
                        -1.6 if lado > 0 else 1.5, 1.6 if lado > 0 else 4.7, max(2, int(4 * s)))
    pygame.draw.polygon(tela, borda, copa)
    pygame.draw.polygon(tela, ouro, [(px + (x - px) * 0.06, py + (y - 60 * s - py) * 0.06) for px, py in copa])
    pygame.draw.polygon(tela, ouro_esc, [(x + 8 * s, y - 84 * s), (x + 29 * s, y - 84 * s), (x + 20 * s, y - 48 * s),
                                         (x + 6 * s, y - 39 * s)])
    pygame.draw.line(tela, luz, (x - 20 * s, y - 80 * s), (x - 14 * s, y - 50 * s), max(2, int(4 * s)))
    pygame.draw.ellipse(tela, borda, (x - 32 * s, y - 90 * s, 64 * s, 10 * s))  # a boca da taça
    pygame.draw.ellipse(tela, ouro_esc, (x - 29 * s, y - 89 * s, 58 * s, 7 * s))
    estrela = [(x + math.cos(a) * r * s, y - 64 * s + math.sin(a) * r * s)
               for i in range(10) for a, r in [(-math.pi / 2 + i * math.pi / 5, 9 if i % 2 == 0 else 4)]]
    pygame.draw.polygon(tela, luz, estrela)


def tai_trofeu_ef(l, tela, t):
    s = 1.8 * l.s / 1.36
    if t < TROFEU_PEGA:
        x = l.x + l.dir * 60 * l.s
        y = -80 + (CHAO + 80) * suave(min(1, t / TROFEU_CAI))
        trofeu(tela, x, y, s)
    else:
        m1, m2 = ponto(l, "mt"), ponto(l, "mf")
        x, y = (m1[0] + m2[0]) / 2, min(m1[1], m2[1]) + 8 * s  # (a base em cima das mãos)
        if t < TROFEU_ERGUE:
            x, y = l.x + l.dir * 60 * l.s, CHAO
        trofeu(tela, x, y, s)
    if t > TROFEU_ERGUE + 10:  # chuva de confete
        for i in range(30):
            u = (t * 2 + i * 37) % 300
            cx = l.x + ((i * 53) % 400) - 200 + math.sin(t * 0.1 + i) * 10
            cy = u * 1.6 - 40
            cor = ((255, 80, 80), (80, 200, 255), (255, 220, 60), (120, 230, 120))[i % 4]
            pygame.draw.rect(tela, cor, (cx, cy, 5, 3 + (t + i) % 3))


# =====================================================================
# TAMER
# =====================================================================
def tamer_carinho(l, t, jogo):
    from golpes import misturar
    x = l.extra
    x["lobo_vit"] = True  # (a vitória é que controla o lobo)
    alvo_x = l.x + l.dir * 58 * l.s
    if t < 20:  # o lobo vem correndo pra frente dele
        x["lobo_x"] = x.get("lobo_x", l.x) + (alvo_x - x.get("lobo_x", l.x)) * 0.2
        x["lobo_pose"] = "corre"
        x["lobo_dir"] = l.dir
        l.sobrepor = p_(l, "parado")
    else:  # senta virado pra ele e ganha carinho (e de vez em quando uiva de alegria)
        x["lobo_x"] = alvo_x
        x["lobo_dir"] = -l.dir
        x["lobo_pose"] = "uiva" if ciclo(t - 20, 90) > 60 else "parado"
        l.sobrepor = misturar(p_(l, "parado"), p_(l, "t_carinho"), suave(min(1, (t - 20) / 10)))
    if t > 20 and ciclo(t - 20, 90) == 61:
        som.tocar("uivo", 0.4)


def tamer_carinho_ef(l, tela, t):
    from efeitos import texto
    if t < 24:
        return
    lx = l.extra.get("lobo_x", l.x)
    for i in range(3):  # os coraçõezinhos subindo
        k = ((t - 24) * 0.018 + i / 3) % 1
        texto(tela, "♥", 16 + i * 4, (255, 110, 140),
              (int(lx + math.sin(k * 6 + i) * 14), int(CHAO - 70 * l.s - k * 60)))


def tamer_fogueira(l, t, jogo):
    from golpes import misturar
    x = l.extra
    x["lobo_vit"] = True
    fx = l.x + l.dir * 64 * l.s
    x["lobo_x"] = fx + l.dir * 64 * l.s  # o lobo do outro lado do fogo, olhando pra ele
    x["lobo_dir"] = -l.dir
    x["lobo_pose"] = "parado"
    l.sobrepor = misturar(p_(l, "parado"), p_(l, "sentado"), suave(min(1, t / 14)))
    if t % 2 == 0:
        fogo(jogo, fx + random.uniform(-8, 8), CHAO - 20, 0.5)
    if t % 9 == 0:  # as fagulhas subindo
        jogo.faiscas.append([fx + random.uniform(-10, 10), CHAO - 40, random.uniform(-0.6, 0.6), -3.5, 30,
                             (255, 200, 90), 2])
    if t % 30 == 0:
        som.tocar("puf", 0.15)  # (o estalo da lenha)


def tamer_fogueira_atras(l, tela, t):
    fx = l.x + l.dir * 64 * l.s
    brilho(tela, (int(fx), int(CHAO - 30)), int(150 + math.sin(t * 0.3) * 8), (255, 150, 60), 60)  # a luz quente
    pygame.draw.ellipse(tela, (255, 170, 80), (fx - 110, CHAO - 6, 220, 14))  # o chão iluminado


def tamer_fogueira_ef(l, tela, t):
    s = l.s
    fx = l.x + l.dir * 64 * s
    for i in range(7):  # o círculo de pedras
        a = math.pi * (i / 6)
        px = fx + math.cos(a) * 30 * s
        pygame.draw.ellipse(tela, (30, 26, 24), (px - 8 * s, CHAO - 9 * s, 16 * s, 11 * s))
        pygame.draw.ellipse(tela, (130, 124, 116), (px - 7 * s, CHAO - 8 * s, 14 * s, 9 * s))
    for a in (-0.5, 0.5, 0.0):  # as toras cruzadas
        x1, y1 = fx - math.cos(a) * 26 * s, CHAO - 4 * s
        x2, y2 = fx + math.cos(a) * 26 * s, CHAO - 4 * s - (16 * s if a == 0 else 10 * s)
        pygame.draw.line(tela, (36, 20, 10), (x1, y1), (x2, y2), max(6, int(9 * s)))
        pygame.draw.line(tela, (110, 70, 36), (x1, y1), (x2, y2), max(4, int(6 * s)))
        pygame.draw.circle(tela, (200, 150, 90), (int(x2), int(y2)), max(2, int(3 * s)))
    for i in range(4):  # as chamas (em camadas, dançando)
        h = (54 - i * 10 + math.sin(t * 0.45 + i * 1.7) * 9) * s
        w = (24 - i * 5) * s
        cor = ((200, 50, 20), (250, 120, 30), (255, 190, 60), (255, 245, 180))[i]
        topo = (fx + math.sin(t * 0.3 + i) * 5 * s, CHAO - 10 * s - h)
        pygame.draw.polygon(tela, cor, [(fx - w, CHAO - 10 * s), (fx - w * 0.6, CHAO - 10 * s - h * 0.5), topo,
                                        (fx + w * 0.6, CHAO - 10 * s - h * 0.55), (fx + w, CHAO - 10 * s)])
    # o graveto com o marshmallow tostando
    m = ponto(l, "mf")
    ponta = (fx - l.dir * 4 * s, CHAO - 50 * s)
    pygame.draw.line(tela, (70, 44, 22), m, ponta, 3)
    tost = min(1, t / 120)
    pygame.draw.circle(tela, (40, 30, 20), (int(ponta[0]), int(ponta[1])), int(7 * s))
    pygame.draw.circle(tela, (int(250 - 90 * tost), int(240 - 130 * tost), int(230 - 170 * tost)),
                       (int(ponta[0]), int(ponta[1])), int(6 * s))


# =====================================================================
# JOHN
# =====================================================================
SERRA_PUF, SERRA_COMECA, SERRA_SEPARA, SERRA_JUNTA, SERRA_SAI = 0, 20, 46, 76, 96


def john_serrado(l, t, jogo):
    from golpes import misturar
    s = l.s
    l.esconde = t < SERRA_SAI  # (dentro da caixa: só a cabeça e os pés pra fora)
    if t == 2 or t == SERRA_SAI:  # PUF de mágica (a caixa aparece / some)
        fumaca(jogo, l.x, CHAO - 50 * s, 16, (200, 170, 240), 5, -1)
        som.tocar("puf", 0.8)
    if SERRA_COMECA <= t < SERRA_SEPARA and (t - SERRA_COMECA) % 6 == 0:  # serrando! (e a serragem)
        som.tocar("vento", 0.35)
        for _ in range(3):
            jogo.faiscas.append([l.x + random.uniform(-4, 4), CHAO - 76 * s, random.uniform(-2.5, 2.5),
                                 random.uniform(-2, 0), 20, (220, 190, 130), 2])
    if t == SERRA_SEPARA:
        som.tocar("confirma", 0.5)
    if t == SERRA_JUNTA + 10:
        som.tocar("defesa", 0.4)
    if t >= SERRA_SAI:  # saiu inteiro! e agradece
        l.sobrepor = misturar(p_(l, "parado"), p_(l, "j_agradece"), suave(min(1, (t - SERRA_SAI) / 12)))


def john_serrado_ef(l, tela, t):
    if t >= SERRA_SAI:
        return
    s = l.s
    d = l.dir
    cresce = suave(min(1, t / 6))
    separa = 56 * s * suave(min(1, max(0, (t - SERRA_SEPARA) / 12))) * (1 - suave(max(0, (t - SERRA_JUNTA) / 12)))
    mesa_y = CHAO - 42 * s
    borda, roxo, roxo_esc, ouro = (20, 10, 30), (120, 50, 170), (80, 30, 120), (255, 220, 80)
    w, h = 132 * s * cresce, 44 * s * cresce
    for lado in (-1, 1):  # as 2 mesinhas (cada metade tem a sua)
        mx = l.x + lado * (w / 4 + separa / 2)
        pygame.draw.rect(tela, borda, (mx - w / 4 - 2, mesa_y - 2, w / 2 + 4, 8))
        pygame.draw.rect(tela, (120, 80, 50), (mx - w / 4, mesa_y, w / 2, 5))
        for k in (-1, 1):
            pygame.draw.line(tela, (70, 46, 30), (mx + k * w / 6, mesa_y + 4), (mx + k * w / 6, CHAO), 4)
    for i, lado in enumerate((-d, d)):  # as 2 metades da caixa (cabeça de um lado, pés do outro)
        cx = l.x + lado * (w / 4 + separa / 2)
        caixa = pygame.Rect(0, 0, w / 2, h)
        caixa.midbottom = (int(cx), int(mesa_y))
        if i == 0:  # a CABEÇA com a cartola, sorrindo
            hx, hy = caixa.centerx - d * (w / 4 + 9 * s), caixa.centery
            pygame.draw.circle(tela, borda, (int(hx), int(hy)), int(11 * s))
            pygame.draw.circle(tela, (236, 204, 172), (int(hx), int(hy)), int(9.5 * s))
            pygame.draw.circle(tela, (20, 20, 20), (int(hx + d * 3 * s), int(hy - 2 * s)), max(1, int(1.6 * s)))
            pygame.draw.arc(tela, (60, 20, 20), (hx - 2 * s, hy - 1 * s, 8 * s, 6 * s), 3.4, 6.0, 2)
            pygame.draw.rect(tela, borda, (hx - 12 * s, hy - 12 * s, 24 * s, 4 * s))  # a cartola
            pygame.draw.rect(tela, borda, (hx - 8 * s, hy - 26 * s, 16 * s, 15 * s))
            pygame.draw.rect(tela, (150, 40, 60), (hx - 8 * s, hy - 15 * s, 16 * s, 3 * s))
        else:  # os PÉS mexendo (sapatos pretos)
            px = caixa.centerx + d * (w / 4 + 4 * s)
            for k, o in enumerate((-8, 6)):
                mexe = math.sin(t * 0.5 + k * 2) * 4 * s if t > SERRA_SEPARA else 0
                pygame.draw.ellipse(tela, borda, (px - 4 * s + d * 4 * s, caixa.centery + o * s - 5 * s + mexe, 14 * s, 8 * s))
                pygame.draw.ellipse(tela, (40, 36, 44), (px - 3 * s + d * 4 * s, caixa.centery + o * s - 4 * s + mexe, 12 * s, 6 * s))
        pygame.draw.rect(tela, borda, caixa.inflate(6, 6), border_radius=4)
        pygame.draw.rect(tela, roxo, caixa, border_radius=4)
        pygame.draw.rect(tela, roxo_esc, (caixa.x, caixa.bottom - 10 * s, caixa.w, 10 * s))
        pygame.draw.rect(tela, ouro, caixa, 2, border_radius=4)
        for k in range(2):  # as estrelas douradas
            sx, sy = caixa.x + caixa.w * (0.3 + k * 0.4), caixa.y + caixa.h * (0.35 + k * 0.2)
            pts = [(sx + math.cos(-math.pi / 2 + j * math.pi / 5) * (7 if j % 2 == 0 else 3) * s,
                    sy + math.sin(-math.pi / 2 + j * math.pi / 5) * (7 if j % 2 == 0 else 3) * s) for j in range(10)]
            pygame.draw.polygon(tela, ouro, pts)
        if SERRA_SEPARA <= t < SERRA_JUNTA + 12:  # o corte por dentro (escuro) aparecendo
            corte_x = caixa.right if lado < 0 else caixa.x
            pygame.draw.line(tela, (30, 10, 40), (corte_x, caixa.y), (corte_x, caixa.bottom), 3)
    if SERRA_COMECA <= t < SERRA_SEPARA:  # o SERROTE descendo e indo e voltando
        k = (t - SERRA_COMECA) / (SERRA_SEPARA - SERRA_COMECA)
        vai = math.sin(t * 1.1) * 16 * s
        topo = mesa_y - h - 30 * s + k * (h + 10 * s)
        lam = [(l.x - 46 * s + vai, topo), (l.x + 46 * s + vai, topo), (l.x + 46 * s + vai, topo + 14 * s),
               (l.x - 46 * s + vai, topo + 20 * s)]
        pygame.draw.polygon(tela, borda, lam)
        pygame.draw.polygon(tela, (206, 210, 222), [(px, py + (1 if j < 2 else -1)) for j, (px, py) in enumerate(lam)])
        for j in range(10):  # os dentes
            dx = l.x - 44 * s + vai + j * 9 * s
            pygame.draw.polygon(tela, (150, 154, 166), [(dx, topo + 16 * s), (dx + 4 * s, topo + 22 * s), (dx + 8 * s, topo + 15 * s)])
        cabo = pygame.Rect(0, 0, 22 * s, 18 * s)
        cabo.midleft = (int(l.x + 44 * s + vai), int(topo + 8 * s))
        pygame.draw.rect(tela, borda, cabo.inflate(4, 4), border_radius=5)
        pygame.draw.rect(tela, (150, 90, 40), cabo, border_radius=5)
    if SERRA_SEPARA + 6 <= t < SERRA_JUNTA:
        balao(tela, l, "TA-DÁ!", 120)


def cartola(tela, x, y, s, d):
    """A cartola de cabeça pra baixo (de onde sai o coelho)."""
    borda = (16, 14, 20)
    pygame.draw.rect(tela, borda, (x - 12 * s, y - 2 * s, 24 * s, 22 * s), border_radius=3)
    pygame.draw.rect(tela, (34, 30, 40), (x - 10 * s, y, 20 * s, 18 * s), border_radius=3)
    pygame.draw.rect(tela, (150, 40, 60), (x - 10 * s, y + 10 * s, 20 * s, 4 * s))
    pygame.draw.ellipse(tela, borda, (x - 17 * s, y - 5 * s, 34 * s, 8 * s))
    pygame.draw.ellipse(tela, (10, 8, 12), (x - 14 * s, y - 4 * s, 28 * s, 5 * s))


COELHO_SAI, COELHO_COLO = 30, 46


def john_coelho(l, t, jogo):
    from golpes import misturar
    if t < COELHO_SAI:  # mostra a cartola vazia... mexe a varinha...
        l.sobrepor = p_(l, "j_magica" if (t // 8) % 2 else "j_magica_b")
    elif t < COELHO_COLO:  # ...e PUXA o coelho pelas orelhas!
        l.sobrepor = p_(l, "j_tira")
    else:  # e faz carinho nele
        l.sobrepor = misturar(p_(l, "j_tira"), p_(l, "j_carinho"), suave(min(1, (t - COELHO_COLO) / 10)))
    if t == COELHO_SAI:
        som.tocar("puf", 0.6)
        mx, my = ponto(l, "mf")
        for i in range(8):  # as estrelinhas da mágica
            a = i * math.tau / 8
            jogo.faiscas.append([mx, my - 20, math.cos(a) * 3, math.sin(a) * 3 - 1, 18, (255, 230, 120), 3])


def john_coelho_ef(l, tela, t):
    s = l.s
    mx, my = ponto(l, "mf")
    mt = ponto(l, "mt")
    if t < COELHO_COLO:
        cartola(tela, mt[0], mt[1] + 2 * s, s, l.dir)
    if COELHO_SAI <= t < COELHO_COLO:  # saindo da cartola, pendurado pelas orelhas
        k = suave((t - COELHO_SAI) / (COELHO_COLO - COELHO_SAI))
        x = mt[0] + (mx - mt[0]) * k
        y = mt[1] - 10 * s - 34 * s * math.sin(k * math.pi) + (my - mt[1]) * k
        coelho(tela, x, y + 14 * s, s * (0.6 + 0.4 * k), t, l.dir)
    elif t >= COELHO_COLO:
        coelho(tela, mx, my, s, t, l.dir)
        from efeitos import texto
        for i in range(2):
            k = ((t - COELHO_COLO) * 0.02 + i / 2) % 1
            texto(tela, "♥", 16, (255, 110, 140), (int(mx + i * 10), int(my - 40 * s - k * 40)))


def coelho(tela, x, y, s, t, d):
    borda = (30, 30, 34)
    pygame.draw.ellipse(tela, borda, (x - 14 * s, y - 11 * s, 28 * s, 22 * s))
    pygame.draw.ellipse(tela, (250, 250, 250), (x - 12 * s, y - 9 * s, 24 * s, 18 * s))
    pygame.draw.circle(tela, (250, 250, 250), (int(x - d * 12 * s), int(y - 2 * s)), int(4 * s))  # o rabinho
    hx = x + d * 10 * s
    pygame.draw.circle(tela, borda, (int(hx), int(y - 10 * s)), int(9.5 * s))
    pygame.draw.circle(tela, (250, 250, 250), (int(hx), int(y - 10 * s)), int(8 * s))
    for o in (-3, 3):  # as orelhas (mexendo)
        mexe = math.sin(t * 0.2 + o) * 2
        pygame.draw.ellipse(tela, borda, (hx + o * s - 3.5 * s + mexe, y - 31 * s, 7 * s, 18 * s))
        pygame.draw.ellipse(tela, (250, 250, 250), (hx + o * s - 2.5 * s + mexe, y - 30 * s, 5 * s, 16 * s))
        pygame.draw.ellipse(tela, (250, 180, 200), (hx + o * s - 1.2 * s + mexe, y - 27 * s, 2.4 * s, 10 * s))
    pygame.draw.circle(tela, borda, (int(hx + d * 3 * s), int(y - 11 * s)), max(1, int(1.8 * s)))
    nariz = 1 + (t // 4) % 2 * 0.4  # o narizinho mexendo
    pygame.draw.circle(tela, (250, 140, 170), (int(hx + d * 7 * s), int(y - 9 * s)), max(1, int(1.5 * s * nariz)))


# =====================================================================
# CRÁQUEN
# =====================================================================
BANDEIRA_FINCA = 18


def craquen_bandeira(l, t, jogo):
    from golpes import misturar
    if t < BANDEIRA_FINCA - 6:  # levanta a bandeira bem alto...
        l.sobrepor = p_(l, "q_puxa")
    elif t < BANDEIRA_FINCA + 8:  # ...e FINCA no chão
        l.sobrepor = p_(l, "q_joga")
    else:  # e ri, segurando o mastro
        l.sobrepor = misturar(p_(l, "q_joga"), p_(l, "q_ri"), suave(min(1, (t - BANDEIRA_FINCA - 8) / 10)))
    if t == BANDEIRA_FINCA:
        som.tocar("queda", 0.8)
        jogo.tremer(10)
        fumaca(jogo, l.x + l.dir * 56 * l.s, CHAO - 4, 12, (180, 170, 150), 4, -1)
    if t == BANDEIRA_FINCA + 18:
        som.tocar("lingua", 0.3)


def craquen_bandeira_ef(l, tela, t):
    s = l.s
    d = l.dir
    if t < BANDEIRA_FINCA:  # o mastro na mão, subindo e descendo pra fincar
        m = ponto(l, "mf")
        k = suave(max(0, (t - BANDEIRA_FINCA + 6) / 6))
        base = (m[0] + (l.x + d * 56 * s - m[0]) * k, m[1] + 30 * s + (CHAO - m[1] - 30 * s) * k)
    else:
        base = (l.x + d * 56 * s, CHAO)
    alto = 190 * s
    topo = (base[0], base[1] - alto)
    pygame.draw.line(tela, (30, 18, 10), base, topo, max(6, int(8 * s)))
    pygame.draw.line(tela, (110, 74, 40), base, topo, max(4, int(5 * s)))
    pygame.draw.circle(tela, (30, 18, 10), (int(topo[0]), int(topo[1])), int(6 * s))
    pygame.draw.circle(tela, (230, 190, 60), (int(topo[0]), int(topo[1])), int(4.5 * s))
    # a BANDEIRA (pano balançando, com a ponta rasgada)
    cols, lins = 7, 4
    larg, alt = 92 * s, 60 * s

    def P(i, j):
        onda = math.sin(t * 0.22 - i * 0.7) * (i / cols) * 9 * s
        return topo[0] + d * (4 * s + i * larg / cols), topo[1] + 6 * s + j * alt / lins + onda

    contorno = [P(i, 0) for i in range(cols + 1)]
    for j in range(1, lins + 1):
        x, y = P(cols, j)
        contorno.append((x - d * (10 * s if j % 2 else 0), y))  # (a ponta rasgada)
    contorno += [P(i, lins) for i in range(cols, -1, -1)]
    pygame.draw.polygon(tela, (8, 8, 10), contorno)
    pygame.draw.polygon(tela, (26, 24, 28), [(x, y + 2) for x, y in contorno[1:cols]] + [P(cols - 1, 2), P(1, 2)])
    pygame.draw.lines(tela, (60, 56, 64), True, contorno, 2)
    cx, cy = P(cols / 2, 1.6)  # a CAVEIRA e os ossos cruzados
    for a in (0.6, -0.6):
        dx, dy = math.cos(a) * 20 * s, math.sin(a) * 20 * s
        pygame.draw.line(tela, (236, 232, 220), (cx - dx, cy + 12 * s - dy), (cx + dx, cy + 12 * s + dy), max(3, int(4 * s)))
        for px, py in ((cx - dx, cy + 12 * s - dy), (cx + dx, cy + 12 * s + dy)):
            pygame.draw.circle(tela, (236, 232, 220), (int(px), int(py)), max(2, int(3 * s)))
    pygame.draw.circle(tela, (236, 232, 220), (int(cx), int(cy)), int(11 * s))
    pygame.draw.rect(tela, (236, 232, 220), (cx - 6 * s, cy + 4 * s, 12 * s, 8 * s))
    for o in (-4, 4):
        pygame.draw.circle(tela, (8, 8, 10), (int(cx + o * s), int(cy - 1 * s)), max(2, int(3 * s)))
    pygame.draw.polygon(tela, (8, 8, 10), [(cx, cy + 2 * s), (cx - 2 * s, cy + 5 * s), (cx + 2 * s, cy + 5 * s)])
    if t > BANDEIRA_FINCA + 10:
        balao(tela, l, "Har har har! Esse navio é MEU!", 160)


TESOURO_CAI, TESOURO_ABRE, TESOURO_JORRA = 16, 30, 40


def craquen_tesouro(l, t, jogo):
    from golpes import misturar
    s = l.s
    bx = l.x + l.dir * 60 * s
    if t < TESOURO_ABRE:
        l.sobrepor = p_(l, "q_espera")
    elif t < TESOURO_JORRA + 50:  # mergulha as mãos nas moedas e joga pro alto
        l.sobrepor = p_(l, "q_puxa" if (t // 10) % 2 else "q_joga")
    else:
        l.sobrepor = misturar(p_(l, "q_joga"), p_(l, "q_ri"), suave(min(1, (t - TESOURO_JORRA - 50) / 10)))
    if t == TESOURO_CAI:
        som.tocar("queda", 0.8)
        jogo.tremer(10)
        fumaca(jogo, bx, CHAO - 4, 10, (190, 180, 160), 4, -0.8)
    if t == TESOURO_ABRE:
        som.tocar("confirma", 0.7)
    if TESOURO_JORRA <= t < TESOURO_JORRA + 50 and t % 4 == 0:  # o chafariz de moedas
        for _ in range(3):
            jogo.faiscas.append([bx + random.uniform(-14, 14) * s, CHAO - 40 * s, random.uniform(-4, 4),
                                 random.uniform(-10, -6), 44, (255, 210, 60), 4])
        if t % 12 == 0:
            som.tocar("blip", 0.25)


def craquen_tesouro_ef(l, tela, t):
    s = l.s
    bx = l.x + l.dir * 60 * s
    if t < TESOURO_CAI:
        y = -60 + (CHAO + 60) * suave(t / TESOURO_CAI)
    else:
        y = CHAO
    monte = min(1, max(0, (t - TESOURO_JORRA) / 60))
    rnd = random.Random(7)
    for i in range(int(60 * monte)):  # a montanha de moedas crescendo em volta do baú
        x = bx + rnd.uniform(-80, 80) * s
        h = max(0, 1 - abs(x - bx) / (84 * s)) * 30 * s * monte
        cy = CHAO - rnd.uniform(0, max(1, h)) - 3
        pygame.draw.ellipse(tela, (130, 90, 20), (x - 6, cy - 4, 12, 8))
        pygame.draw.ellipse(tela, (255, 210, 60), (x - 5, cy - 3, 10, 6))
    if monte > 0:
        brilho(tela, (int(bx), int(CHAO - 30 * s)), int(90 * s), (255, 220, 100), 70)
    # o BAÚ (madeira com faixas douradas)
    w, h = 64 * s, 40 * s
    caixa = pygame.Rect(0, 0, w, h)
    caixa.midbottom = (int(bx), int(y))
    borda, madeira, mad_esc, ouro = (30, 18, 8), (130, 80, 40), (96, 56, 26), (240, 190, 60)
    pygame.draw.rect(tela, borda, caixa.inflate(6, 6), border_radius=4)
    pygame.draw.rect(tela, madeira, caixa, border_radius=4)
    for k in range(1, 4):
        pygame.draw.line(tela, mad_esc, (caixa.x + 3, caixa.y + k * h / 4), (caixa.right - 3, caixa.y + k * h / 4), 2)
    for fx in (0.15, 0.85):
        pygame.draw.rect(tela, ouro, (caixa.x + w * fx - 4, caixa.y, 8, h))
    abre = suave(min(1, max(0, (t - TESOURO_ABRE) / 8)))
    if abre > 0:  # o brilho lá de dentro
        brilho(tela, (int(bx), int(caixa.y)), int(50 * s * abre), (255, 230, 120), 200)
        for k in range(5):  # os raios de luz
            a = -math.pi / 2 + (k - 2) * 0.3
            pygame.draw.line(tela, (255, 240, 170), (bx, caixa.y), (bx + math.cos(a) * 80 * s * abre, caixa.y + math.sin(a) * 80 * s * abre), 2)
        pygame.draw.ellipse(tela, (255, 210, 60), (caixa.x + 4, caixa.y - 6 * s, w - 8, 12 * s))
    # a TAMPA (gira pra trás abrindo)
    piv = (caixa.centerx - l.dir * w / 2, caixa.y)
    ang = abre * 1.45
    tampa = []
    for px, py in ((0, 0), (w, 0), (w, -16 * s), (w * 0.5, -22 * s), (0, -16 * s)):
        px *= l.dir
        c, sn = math.cos(ang * -l.dir), math.sin(ang * -l.dir)
        tampa.append((piv[0] + px * c - py * sn, piv[1] + px * sn + py * c))
    pygame.draw.polygon(tela, borda, tampa)
    pygame.draw.polygon(tela, madeira, [(px + (piv[0] + l.dir * w / 2 - px) * 0.06, py + 1) for px, py in tampa])
    if abre < 0.5:  # a fechadura
        pygame.draw.rect(tela, ouro, (bx - 6 * s, caixa.y - 4 * s, 12 * s, 12 * s), border_radius=2)
        pygame.draw.circle(tela, borda, (int(bx), int(caixa.y + 1 * s)), max(1, int(2 * s)))
    if t > TESOURO_JORRA + 50:
        balao(tela, l, "Tudo meu! Har har!", 160)


# =====================================================================
# MAGNUS
# =====================================================================
FARO_CHEGA, FARO_AR, FARO_RUGE = 50, 74, 96


def magnus_faro(l, t, jogo):
    from golpes import misturar
    ox, oy, os_ = alvo(l)
    if t == 0 or "faro_x" not in l.extra:
        l.extra["faro_x"] = l.x
    if t < FARO_CHEGA:  # vem farejando o chão, devagar (sem pisar nele)
        k = suave(t / FARO_CHEGA)
        l.x = l.extra["faro_x"] + ((ox - l.dir * 130 * l.s) - l.extra["faro_x"]) * k
        l.sobrepor = misturar(p_(l, "m_fareja"), p_(l, ("andar1", "andar2", "andar3", "andar4")[(t // 6) % 4]), 0.35)
        if t % 10 == 0:
            cb = ponto(l, "cb")
            fumaca(jogo, cb[0] + l.dir * 20 * l.s, CHAO - 4, 2, (190, 180, 160), 1, -0.5)
            som.tocar("puf", 0.12)
    elif t < FARO_AR:  # levanta a cabeça e fareja o ar
        l.sobrepor = p_(l, "parado" if (t // 4) % 2 else "m_fareja")
    elif t < FARO_RUGE:  # achou... e RUGE pro céu
        l.sobrepor = p_(l, "m_ruge")
        if t == FARO_AR + 4:
            som.tocar("uivo", 0.6)
            jogo.tremer(10)
    else:
        l.sobrepor = misturar(p_(l, "m_ruge"), p_(l, "parado"), suave(min(1, (t - FARO_RUGE) / 12)))


def magnus_faro_ef(l, tela, t):
    from efeitos import texto
    cb = ponto(l, "cb")
    if t < FARO_CHEGA and (t // 10) % 2:
        texto(tela, "snif", 12, (240, 240, 240), (int(cb[0] + l.dir * 30 * l.s), int(cb[1] - 24 * l.s)))
    if FARO_CHEGA <= t < FARO_AR:
        texto(tela, "snif snif...", 13, (240, 240, 240), (int(cb[0] + l.dir * 20 * l.s), int(cb[1] - 40 * l.s)))
    if FARO_AR <= t < FARO_RUGE:  # as ondas de calor do rugido
        for i in range(3):
            r = int(((t - FARO_AR) * 6 + i * 22) % 80 + 10)
            pygame.draw.arc(tela, (255, 160, 80), (cb[0] + l.dir * 14 - r, cb[1] - r, 2 * r, 2 * r),
                            -0.8 if l.dir > 0 else 2.3, 0.8 if l.dir > 0 else 3.9, 3)


AREIA_JUNTA, AREIA_FOGO, AREIA_VIDRO = 30, 60, 78


def magnus_vidro(l, t, jogo):
    import magnus
    from golpes import misturar
    s = l.s
    ax = l.x + l.dir * 84 * s
    if t < AREIA_JUNTA:  # cava e junta a areia com as patas
        l.sobrepor = p_(l, "x_garra_a" if (t // 6) % 2 else "x_garra_b")
        if t % 3 == 0:
            jogo.faiscas.append([ax + random.uniform(-16, 16), CHAO - 6, random.uniform(-2, 2), random.uniform(-5, -2), 22,
                                 (220, 190, 120), 3])
    elif t < AREIA_FOGO:  # cospe FOGO na areia
        l.sobrepor = p_(l, "m_ruge")
        if t % 2 == 0:
            cb = ponto(l, "cb")
            magnus.chama(jogo, cb[0] + l.dir * 30 * s, cb[1] + 10 * s, 2, 1.2)
        if t == AREIA_JUNTA:
            som.tocar("foguete", 0.5)
    else:  # admira a estátua de vidro
        l.sobrepor = misturar(p_(l, "m_ruge"), p_(l, "m_fareja"), suave(min(1, (t - AREIA_FOGO) / 12)))
        if t == AREIA_VIDRO:
            som.tocar("confirma", 0.6)


def magnus_vidro_ef(l, tela, t):
    s = l.s
    ax = l.x + l.dir * 84 * s
    d = l.dir
    if t < AREIA_VIDRO:  # o monte de areia (vai ficando em brasa com o fogo)
        k = min(1, t / AREIA_JUNTA)
        quente = suave(min(1, max(0, (t - AREIA_JUNTA) / (AREIA_FOGO - AREIA_JUNTA))))
        cor = (int(214 + 41 * quente), int(184 - 40 * quente + 60 * quente * quente), int(110 - 60 * quente + 120 * quente * quente))
        derrete = suave(max(0, (t - AREIA_FOGO) / (AREIA_VIDRO - AREIA_FOGO)))
        w, h = 70 * s * k * (1 - derrete * 0.3), 30 * s * k * (1 + derrete)
        r = pygame.Rect(0, 0, max(2, w), max(2, h))
        r.midbottom = (int(ax), int(CHAO + 2))
        pygame.draw.ellipse(tela, (60, 40, 20), r.inflate(4, 4))
        pygame.draw.ellipse(tela, cor, r)
        if quente > 0:
            brilho(tela, r.center, int(50 * s * quente), (255, 140, 40), int(160 * quente))
        return
    # a ESCULTURA DE VIDRO (um cacho de cristais transparentes, brilhando)
    u = t - AREIA_VIDRO
    esfria = min(1, u / 20)
    camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
    vidro = (int(255 - 90 * esfria), int(170 + 70 * esfria), int(90 + 165 * esfria), 170)
    cristais = ((0, 86, 0.0, 15), (-22, 58, -0.35, 12), (22, 64, 0.3, 12), (-38, 34, -0.6, 9), (36, 38, 0.6, 9))
    contornos = []
    for dx, alto, ang, larg in cristais:
        bx = ax + d * dx * s * 0.6
        c, sn = math.cos(ang * d), math.sin(ang * d)

        def R(px, py):
            return bx + (px * c - py * sn) * s, CHAO - (px * sn + py * c) * s

        pts = [R(-larg, 0), R(-larg, alto * 0.75), R(0, alto), R(larg, alto * 0.75), R(larg, 0)]
        pygame.draw.polygon(camada, vidro, pts)
        pygame.draw.polygon(camada, (255, 255, 255, 70), [R(-larg, 0), R(-larg, alto * 0.75), R(0, alto), R(0, 0)])
        contornos.append((pts, R(0, alto), R(0, 0)))
    tela.blit(camada, (0, 0))
    for pts, pico, pe in contornos:
        pygame.draw.polygon(tela, (220, 245, 255), pts, 2)
        pygame.draw.line(tela, (200, 235, 250), pico, pe, 1)
    brilha = (u * 3) % 120  # o reflexo subindo
    if brilha < 90:
        y = CHAO - brilha * s
        pygame.draw.line(tela, (255, 255, 255), (ax - 30 * s, y + 8), (ax + 30 * s, y - 8), 2)
    if esfria >= 1 and (u // 10) % 3 == 0:  # estrelinha de brilho
        brilho(tela, (int(ax), int(CHAO - 86 * s)), 16, (255, 255, 255), 230)


# =====================================================================
# SPHYRUS
# =====================================================================
CIRC_AFUNDA, CIRC_SAI, CIRC_POUSA = 16, 100, 124


def circ_pos(l, t):
    """Onde a barbatana está no círculo em volta do derrotado (o mesmo no movimento e no desenho)."""
    ox, oy, os_ = alvo(l)
    a = (t - CIRC_AFUNDA) * 0.075 + math.pi
    return ox + math.cos(a) * 100 * l.s, a


def sphyrus_circulo(l, t, jogo):
    from golpes import misturar
    s = l.s
    if t == 0 or "circ_x" not in l.extra:
        l.extra["circ_x"] = l.x
    if t < CIRC_AFUNDA:  # 1) pula de cabeça e MERGULHA na terra
        k = suave(t / CIRC_AFUNDA)
        l.sobrepor = p_(l, "s_mergulho")
        l.cortar_chao = True
        l.y = CHAO + 140 * s * k - math.sin(k * math.pi) * 40 * s
        if t == CIRC_AFUNDA - 4:
            som.tocar("terra", 0.7)
            fumaca(jogo, l.x, CHAO - 4, 12, (150, 120, 90), 4, -1.4)
    elif t < CIRC_SAI:  # 2) só a BARBATANA, rodando em volta do derrotado, levantando terra
        l.esconde = True
        x, a = circ_pos(l, t)
        l.x = x
        if t % 3 == 0:
            fumaca(jogo, x, CHAO - 2, 2, (150, 124, 96), 1.6, -0.6)
        if t % 20 == 0:
            som.tocar("terra", 0.25)
    else:  # 3) SAI DO CHÃO num salto e cai rugindo
        l.esconde = False
        u = t - CIRC_SAI
        k = min(1, u / (CIRC_POUSA - CIRC_SAI))
        l.cortar_chao = k < 0.25
        l.y = CHAO - math.sin(k * math.pi) * 120 * s + (1 - min(1, k * 4)) * 60 * s
        l.sobrepor = p_(l, "s_martelo") if k < 1 else misturar(p_(l, "s_martelo"), p_(l, "s_ruge"),
                                                                   suave(min(1, (t - CIRC_POUSA) / 8)))
        if u == 0:
            som.tocar("explosao", 0.6)
            jogo.tremer(12)
            fumaca(jogo, l.x, CHAO - 4, 18, (150, 120, 90), 6, -2)
        if t == CIRC_POUSA:
            l.y = CHAO
            som.tocar("queda", 0.6)
            jogo.tremer(8)
        if t >= CIRC_POUSA:
            l.y = CHAO
            l.extra["boca"] = 1.0 if t < CIRC_POUSA + 40 else 0.0
        if t == CIRC_POUSA + 4:
            som.tocar("uivo", 0.5)
    l.vy = 0


def sphyrus_circulo_ef(l, tela, t):
    import sphyrus
    if not CIRC_AFUNDA <= t < CIRC_SAI:
        return
    x, a = circ_pos(l, t)
    vai = -1 if math.sin(a) > 0 else 1  # (pra onde ela está nadando)
    for i in range(1, 8):  # a ONDA DE TERRA atrás da barbatana
        xa, _ = circ_pos(l, t - i * 2)
        h = (8 - i) * 1.4 * l.s
        pygame.draw.ellipse(tela, (60, 44, 30), (xa - 8 * l.s, CHAO - h - 2, 16 * l.s, h * 2 + 4))
        pygame.draw.ellipse(tela, (140, 112, 82), (xa - 6 * l.s, CHAO - h, 12 * l.s, h * 2))
    guarda = l.x, l.y, l.dir, l.s
    try:
        l.x, l.y, l.dir, l.s = x, CHAO, vai, l.s * 1.4  # (barbatana maior: aparece bem)
        sphyrus.desenhar_barbatana(l, tela)
    finally:
        l.x, l.y, l.dir, l.s = guarda
    pygame.draw.ellipse(tela, (60, 44, 30), (x - 30 * l.s, CHAO - 5, 60 * l.s, 10))  # o rasgo na terra


MAND_ABRE, MAND_CLAC = 34, 40


def sphyrus_mandibula(l, t, jogo):
    u = ciclo(t, 90)
    l.sobrepor = p_(l, "s_ruge")
    if u < MAND_ABRE:  # abre devagar... ENORME
        l.extra["boca"] = 1.25 * suave(u / MAND_ABRE)
    elif u < MAND_CLAC:  # treme com a boca escancarada
        l.extra["boca"] = 1.25 + (0.05 if u % 2 else -0.05)
    else:  # CLAC! e fica sorrindo
        l.extra["boca"] = 0.0
    if u == MAND_CLAC:
        som.tocar("soco")
        som.tocar("quebra", 0.4)
        jogo.tremer(16)
        cb = ponto(l, "cb")
        for i in range(10):  # as lascas voando do CLAC
            a = -math.pi / 2 + (i - 4.5) * 0.3
            jogo.faiscas.append([cb[0] + l.dir * 40 * l.s, cb[1], math.cos(a) * 5, math.sin(a) * 5, 14,
                                 (255, 250, 230), 3])
    if u == 6:
        som.tocar("lingua", 0.3)


def sphyrus_mandibula_ef(l, tela, t):
    u = ciclo(t, 90)
    cb = ponto(l, "cb")
    boca = (cb[0] + l.dir * 36 * l.s, cb[1] - 2 * l.s)
    if 10 < u < MAND_CLAC:  # a baba escorrendo
        for i in range(2):
            y0 = boca[1] + 6
            pygame.draw.line(tela, (200, 230, 240), (boca[0] - l.dir * i * 14, y0), (boca[0] - l.dir * i * 14,
                                                                                       y0 + (u - 10) * 0.8), 2)
    if MAND_CLAC <= u < MAND_CLAC + 12:  # o CLAC! (riscos de impacto e o texto)
        from efeitos import texto_grande
        k = (u - MAND_CLAC) / 12
        for i in range(10):
            a = i * math.tau / 10
            r1, r2 = 20 + k * 30, 40 + k * 50
            pygame.draw.line(tela, (255, 250, 220), (boca[0] + math.cos(a) * r1, boca[1] + math.sin(a) * r1),
                             (boca[0] + math.cos(a) * r2, boca[1] + math.sin(a) * r2), 3)
        texto_grande(tela, "CLAC!", int(30 + 14 * (1 - k)), (255, 240, 200), (int(l.x), int(l.y - 175 * l.s)),
                     contorno=(40, 10, 10))


# =====================================================================
# A loja: 2 por lutador
# =====================================================================
def _v(lutador, ident, nome, vit, ef=None, preco=PRECO, atras=None):
    item = dict(id=ident, nome=nome, preco=preco, vitoria=vit)
    if ef:
        item["vitoria_efeito"] = ef
    if atras:
        item["vitoria_atras"] = atras  # (desenhado atrás do lutador)
    extras.registrar("vitorias", lutador, **item)


_v("MAX-10", "desliga", "DESLIGANDO", max_desliga, max_desliga_ef)
_v("MAX-10", "voa", "SAIR VOANDO", max_voa, max_voa_ef, PRECO_CAPRICHADA)
_v("RIB", "shuriken", "SHURIKEN NO DEDO", rib_shuriken, rib_shuriken_ef)
_v("RIB", "bambu", "NINJA NO BAMBU", rib_bambu, rib_bambu_ef, PRECO_CAPRICHADA)
_v("TRAFO", "rabo", "ABANANDO O RABO", trafo_rabo, trafo_rabo_ef)
_v("TRAFO", "desfile", "DESFILE DE FORMAS", trafo_desfile, None, PRECO_CAPRICHADA)
_v("KING RIP", "reverencia", "REVERÊNCIA DE MESTRE", king_reverencia)
_v("KING RIP", "nunchaku", "NUNCHAKU MESTRE", king_nunchaku, king_nunchaku_ef, PRECO_CAPRICHADA)
_v("CANNAN", "fumega", "CANHÃO FUMEGANDO", cannan_fumega, cannan_fumega_ef)
_v("CANNAN", "missao", "MISSÃO CUMPRIDA", cannan_missao, cannan_missao_ef, PRECO_CAPRICHADA)
_v("FINN", "trono", "TRONO DE PEDRA", finn_trono, None, PRECO_CAPRICHADA, finn_trono_atras)
_v("FINN", "dragao", "DRAGÃOZINHO", finn_dragao, finn_dragao_ef)
_v("KUN", "sofa", "SOFÁ DO CAMPEÃO", kun_sofa, kun_sofa_ef, PRECO_CAPRICHADA, kun_sofa_atras)
_v("KUN", "as", "ÁS NA MANGA", kun_as, kun_as_ef)
_v("TROMOS", "teto", "NO TETO", xeno_teto, xeno_teto_ef)
_v("TROMOS", "casulo", "CASULO", xeno_casulo, xeno_casulo_ef, PRECO_CAPRICHADA)
_v("TAI", "descanso", "DESCANSO", tai_descanso, tai_descanso_ef)
_v("TAI", "trofeu", "TROFÉU GIGANTE", tai_trofeu, tai_trofeu_ef, PRECO_CAPRICHADA)
_v("TAMER", "carinho", "CARINHO NO LOBO", tamer_carinho, tamer_carinho_ef)
_v("TAMER", "fogueira", "FOGUEIRA", tamer_fogueira, tamer_fogueira_ef, PRECO_CAPRICHADA, tamer_fogueira_atras)
_v("JOHN", "serrado", "SERRADO DE BRINCADEIRA", john_serrado, john_serrado_ef, PRECO_CAPRICHADA)
_v("JOHN", "coelho", "COELHO NO COLO", john_coelho, john_coelho_ef)
_v("CRÁQUEN", "bandeira", "BANDEIRA PIRATA", craquen_bandeira, craquen_bandeira_ef)
_v("CRÁQUEN", "tesouro", "TESOURO", craquen_tesouro, craquen_tesouro_ef, PRECO_CAPRICHADA)
_v("MAGNUS", "faro", "FARO DE CAÇADOR", magnus_faro, magnus_faro_ef)
_v("MAGNUS", "vidro", "AREIA EM VIDRO", magnus_vidro, magnus_vidro_ef, PRECO_CAPRICHADA)
_v("SPHYRUS", "circulo", "BARBATANA EM CÍRCULO", sphyrus_circulo, sphyrus_circulo_ef, PRECO_CAPRICHADA)
_v("SPHYRUS", "mandibula", "MANDÍBULA ABERTA", sphyrus_mandibula, sphyrus_mandibula_ef)


# =====================================================================
# FRIGANTUS
# =====================================================================
NEVE_ROLA, NEVE_ERGUE, NEVE_JOGA, NEVE_SPLAT = 34, 48, 54, 72


def neve_bola(l, t):
    """(x, y, raio) da bola de neve gigante em cada momento."""
    ox, oy, os_ = alvo(l)
    s = l.s
    if t < NEVE_ROLA:  # rolando no chão na frente dele, crescendo
        r = (8 + 22 * t / NEVE_ROLA) * s
        return l.x + l.dir * (50 * s + r), CHAO - r, r
    r = 30 * s
    if t < NEVE_JOGA:  # erguida em cima da cabeça
        m1, m2 = ponto(l, "mt"), ponto(l, "mf")
        return (m1[0] + m2[0]) / 2, min(m1[1], m2[1]) - r * 0.6, r
    k = min(1, (t - NEVE_JOGA) / (NEVE_SPLAT - NEVE_JOGA))  # voando em arco até o derrotado
    m1, m2 = ponto(l, "mt"), ponto(l, "mf")
    x0, y0 = l.x + l.dir * 20 * s, l.y - 150 * s
    return x0 + (ox - x0) * k, y0 + (CHAO - 20 * s - y0) * k - math.sin(k * math.pi) * 80 * s, r


def frig_guerra(l, t, jogo):
    from golpes import misturar
    if t < NEVE_ROLA:  # empurra a bola rolando (curvado, com os braços)
        l.sobrepor = p_(l, ("andar1", "andar2", "andar3", "andar4")[(t // 6) % 4])
        if t % 5 == 0:
            x, y, r = neve_bola(l, t)
            jogo.faiscas.append([x, CHAO - 4, -l.dir * 1.5, -2, 14, (240, 246, 255), 3])
    elif t < NEVE_JOGA:  # levanta a bola em cima da cabeça
        l.sobrepor = p_(l, "fr_arremessa")
        if t == NEVE_ROLA:
            som.tocar("carga", 0.5)
    elif t < NEVE_SPLAT + 10:  # ARREMESSA
        l.sobrepor = p_(l, "fr_joga")
        if t == NEVE_JOGA:
            som.tocar("vento", 0.7)
    else:  # bate no peito (UH-UH-UH!)
        l.sobrepor = p_(l, "fr_peito_a" if (t // 6) % 2 else "fr_peito_b")
        if t % 12 == 0:
            som.tocar("soco", 0.3)
    if t == NEVE_SPLAT:  # SPLAT! (o derrotado some debaixo da neve)
        ox, oy, os_ = alvo(l)
        som.tocar("puf", 0.9)
        som.tocar("queda", 0.5)
        jogo.tremer(10)
        fumaca(jogo, ox, CHAO - 20, 20, (240, 246, 255), 6, -1.2)


def frig_guerra_ef(l, tela, t):
    ox, oy, os_ = alvo(l)
    if t < NEVE_SPLAT:
        x, y, r = neve_bola(l, t)
        pygame.draw.circle(tela, (120, 140, 170), (int(x), int(y)), int(r) + 2)
        pygame.draw.circle(tela, (246, 250, 255), (int(x), int(y)), int(r))
        pygame.draw.circle(tela, (200, 214, 236), (int(x + r * 0.25), int(y + r * 0.3)), int(r * 0.55))
        pygame.draw.circle(tela, (255, 255, 255), (int(x - r * 0.35), int(y - r * 0.35)), max(2, int(r * 0.18)))
    else:  # o MONTE DE NEVE em cima do derrotado (só os pés pra fora, mexendo)
        k = min(1, (t - NEVE_SPLAT) / 6)
        w, h = 130 * os_, 46 * os_ * k
        r = pygame.Rect(0, 0, w, max(2, h))
        r.midbottom = (int(ox), int(CHAO + 2))
        pygame.draw.ellipse(tela, (120, 140, 170), r.inflate(6, 6))
        pygame.draw.ellipse(tela, (246, 250, 255), r)
        pygame.draw.ellipse(tela, (214, 226, 244), (r.x + 10, r.centery, r.w - 20, r.h // 2))
        for i in range(3):  # bolotas no topo
            pygame.draw.circle(tela, (246, 250, 255), (int(r.x + r.w * (0.3 + i * 0.2)), int(r.y + 4)), int(10 * os_))
        if k >= 1:
            pe = (r.right - 6, r.centery + math.sin(t * 0.4) * 4)
            pygame.draw.ellipse(tela, (90, 60, 40), (pe[0], pe[1] - 5, 16 * os_, 10 * os_))
    if t > NEVE_SPLAT + 10:
        balao(tela, l, "*UH-UH-UH!*")


SONECA_SENTA = 30


def frig_soneca(l, t, jogo):
    from golpes import misturar
    if t < 18:  # BOCEJO enorme, se espreguiçando
        l.sobrepor = p_(l, "fr_ruge")
        if t == 4:
            som.tocar("uivo", 0.3)
    elif t < SONECA_SENTA:  # senta pesado
        l.sobrepor = misturar(p_(l, "fr_ruge"), p_(l, "sentado"), suave((t - 18) / (SONECA_SENTA - 18)))
    else:
        l.sobrepor = p_(l, "sentado")
    if t == SONECA_SENTA:
        som.tocar("queda", 0.5)
        fumaca(jogo, l.x, CHAO - 4, 10, (240, 246, 255), 3, -0.6)
    if t > SONECA_SENTA and t % 3 == 0:  # nevando em cima dele
        jogo.faiscas.append([l.x + ((t * 37) % 160 - 80) * l.s, l.y - 200 * l.s, 0.2, 0.2, 60, (250, 252, 255), 2])
    if t > SONECA_SENTA and ciclo(t, 50) == 20:  # o vapor do ronco
        cb = ponto(l, "cb")
        fumaca(jogo, cb[0] + l.dir * 24 * l.s, cb[1] + 14 * l.s, 3, (230, 240, 255), 1, -0.6)
        som.tocar("vento", 0.15)


def frig_soneca_ef(l, tela, t):
    from efeitos import texto
    if t <= SONECA_SENTA:
        return
    cb = ponto(l, "cb")
    nariz = (cb[0] + l.dir * 26 * l.s, cb[1] + 10 * l.s)
    u = ciclo(t, 50)  # a BOLHA DE RONCO crescendo e estourando
    if u < 40:
        r = int(3 + u * 0.35)
        pygame.draw.circle(tela, (200, 230, 255), (int(nariz[0] + l.dir * r), int(nariz[1])), r, 2)
        pygame.draw.circle(tela, (255, 255, 255), (int(nariz[0] + l.dir * r - r * 0.4), int(nariz[1] - r * 0.4)), 2)
    elif u < 44:
        for i in range(6):
            a = i * math.tau / 6
            pygame.draw.circle(tela, (220, 240, 255), (int(nariz[0] + l.dir * 16 + math.cos(a) * 12),
                                                       int(nariz[1] + math.sin(a) * 12)), 2)
    acumula = min(1, (t - SONECA_SENTA) / 120)  # a neve juntando na cabeça e nos ombros
    if acumula > 0.1:
        topo = (cb[0] - l.dir * 4 * l.s, cb[1] - 6 * l.s)
        pygame.draw.ellipse(tela, (250, 252, 255), (topo[0] - 16 * l.s * acumula, topo[1] - 8 * l.s * acumula,
                                                    32 * l.s * acumula, 12 * l.s * acumula))
    for i in range(3):
        k = (t * 0.02 + i * 0.33) % 1
        texto(tela, "Z", int(14 + i * 5), (220, 230, 255), (int(cb[0] - l.dir * (14 + k * 30)), int(cb[1] - 30 - k * 60)))


_v("FRIGANTUS", "guerra", "GUERRA DE NEVE", frig_guerra, frig_guerra_ef, PRECO_CAPRICHADA)
_v("FRIGANTUS", "soneca", "SONECA DE INVERNO", frig_soneca, frig_soneca_ef)


# =====================================================================
# NOCTURNUS: PENDURADO NA LUA (sobe batendo as asas e fica pairando lá no alto, rindo, com a lua cheia atrás)
# =====================================================================
LUA_SOBE, LUA_PARA = 16, 60


def noct_lua_y(l, t):
    if t < LUA_SOBE:
        return CHAO
    k = suave(min(1, (t - LUA_SOBE) / (LUA_PARA - LUA_SOBE)))
    return CHAO - 250 * k + (math.sin((t - LUA_PARA) * 0.12) * 8 if t >= LUA_PARA else 0)


def noct_lua(l, t, jogo):
    l.y = noct_lua_y(l, t)
    l.vy = 0
    l.sobrepor = p_(l, "n_ri" if t >= LUA_PARA + 10 and (t // 30) % 2 else "n_voa" if t >= LUA_SOBE else "parado")
    if t == LUA_SOBE:
        som.tocar("vento", 0.6)
    if t == LUA_PARA + 10:
        som.tocar("blip", 0.4)


def noct_lua_atras(l, tela, t):
    if t < LUA_SOBE:
        return
    k = min(1, (t - LUA_SOBE) / 30)
    x, y = int(l.x), int(CHAO - 250 - 60 * l.s)
    r = int(70 * k)
    if r < 3:
        return
    brilho(tela, (x, y), int(r * 1.6), (230, 230, 200), 90)
    pygame.draw.circle(tela, (246, 242, 214), (x, y), r)
    for dx, dy, cr in ((-0.3, -0.2, 0.18), (0.25, 0.15, 0.12), (-0.05, 0.4, 0.1)):  # as crateras
        pygame.draw.circle(tela, (220, 214, 184), (int(x + dx * r), int(y + dy * r)), max(1, int(cr * r)))


_v("NOCTURNUS", "lua", "PENDURADO NA LUA", noct_lua, None, PRECO_CAPRICHADA, noct_lua_atras)


# =====================================================================
# CUTSCENES (as caprichadas viram cena de anime): (lutador, id) -> (clímax, fim, foco do clímax, fundo)
# =====================================================================
CENAS = {
    ("MAX-10", "voa"): (26, 120, "corpo", "ceu"),
    ("RIB", "bambu"): (16, 90, "corpo", "noite", "alto"),
    ("TRAFO", "desfile"): (90, 120, "corpo", "luz"),
    ("KING RIP", "nunchaku"): (56, 100, "corpo", "luz"),
    ("CANNAN", "missao"): (HELI_PEGA, 130, "corpo", "ceu", "corpo"),
    ("FINN", "trono"): (TRONO_SENTA, 90, "corpo", "luz"),
    ("KUN", "sofa"): (SOFA_SURGE, 90, "corpo", "luz"),
    ("TROMOS", "casulo"): (CASULO_PRONTO, 120, "alvo", "noite"),
    ("TAI", "trofeu"): (TROFEU_ERGUE, 110, "corpo", "ceu", "alto"),
    ("TAMER", "fogueira"): (30, 120, "corpo", "noite"),
    ("JOHN", "serrado"): (SERRA_SEPARA, 120, "corpo", "luz"),
    ("CRÁQUEN", "tesouro"): (TESOURO_ABRE, 110, "corpo", "noite"),
    ("MAGNUS", "vidro"): (AREIA_VIDRO, 120, "corpo", "luz"),
    ("SPHYRUS", "circulo"): (CIRC_SAI, 140, "corpo", "noite"),
    ("FRIGANTUS", "guerra"): (NEVE_SPLAT, 110, "alvo", "ceu"),
    ("NOCTURNUS", "lua"): (LUA_PARA, 120, "corpo", "noite"),
}


ANIME = {("MAX-10", "voa"): "cena_max:vitoria", ("FRIGANTUS", "guerra"): "cena_frigantus:vitoria",
         ("SPHYRUS", "circulo"): "cena_sphyrus:vitoria", ("MAGNUS", "vidro"): "cena_magnus:vitoria",
         ("KUN", "sofa"): "cena_kun:vitoria",
         ("RIB", "bambu"): "cena_rib:vitoria", ("TRAFO", "desfile"): "cena_trafo:vitoria",
         ("KING RIP", "nunchaku"): "cena_king:vitoria", ("CANNAN", "missao"): "cena_cannan:vitoria",
         ("FINN", "trono"): "cena_finn:vitoria", ("TROMOS", "casulo"): "cena_tromos:vitoria",
         ("TAI", "trofeu"): "cena_tai:vitoria", ("TAMER", "fogueira"): "cena_tamer:vitoria",
         ("JOHN", "serrado"): "cena_john:vitoria",
         ("CRÁQUEN", "tesouro"): "cena_craquen:vitoria", ("NOCTURNUS", "lua"): "cena_nocturnus:vitoria"}  # as que já viraram CENA DE ANIME desenhada


def _ligar_cenas():
    import cenas_loja
    for (lutador, ident), cena in CENAS.items():
        it = extras.item("vitorias", lutador, ident)
        assert it["id"] == ident, (lutador, ident)
        it["vitoria_cutscene"] = ANIME.get((lutador, ident)) or cenas_loja.planos_auto(*cena)


_ligar_cenas()
