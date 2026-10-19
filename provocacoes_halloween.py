"""PROVOCAÇÕES DE HALLOWEEN: prêmio do PASSE DO EVENTO (uma por lutador das skins).
Ficam na loja só pra quem ganhou no passe (extras.tem olha o passe). Tudo que muda o lutador passa pelo
usa_pose/solta (o ult2.todo_quadro desfaz se ele apanhar no meio); o resto é só desenho."""
import math

import pygame

import extras
import som
from config import *  # noqa: F401,F403
from golpes import suave
from max10 import brilho, fumaca
from provocacoes_loja import T, fim_pose, onda, ponto, sprite, usa_pose

EVENTO = "halloween"


# =====================================================================
# SPHYRUS: BOLHAS ASSOMBRADAS (as bolhas sobem e viram caveirinhas)
# =====================================================================
def sphyrus_bolhas_passo(l, jogo):
    if fim_pose(l):
        return
    usa_pose(l, dict(l.poses.get("s_ruge") or l.poses["parado"]))
    if l.t in (8, 18, 28):
        som.tocar("puf", 0.3)
    if l.t == 44:
        som.tocar("lingua", 0.4)


def sphyrus_bolhas(l, tela):
    cb = ponto(l, "cb")
    boca = (cb[0] + l.dir * 30 * l.s, cb[1] + 4 * l.s)
    for i in range(3):  # 3 bolhas, uma atrás da outra
        u = l.t - (8 + i * 10)
        if u < 0 or u > 52:
            continue
        x = boca[0] + l.dir * u * 0.9 + math.sin(u * 0.25 + i) * 6
        y = boca[1] - u * 2.0
        r = int(min(14, 4 + u * 0.5) * l.s / 1.36)
        if u < 34:  # bolha (transparente, com reflexo)
            pygame.draw.circle(tela, (200, 240, 255), (int(x), int(y)), r, 2)
            pygame.draw.circle(tela, (255, 255, 255), (int(x - r * 0.4), int(y - r * 0.4)), max(1, r // 4))
        else:  # vira CAVEIRINHA verde-fantasma (e some)
            k = (u - 34) / 18
            cor = (int(170 + 60 * (1 - k)), 255, int(190 + 40 * (1 - k)))
            brilho(tela, (int(x), int(y)), r + 6, (120, 255, 160), int(150 * (1 - k)))
            pygame.draw.circle(tela, cor, (int(x), int(y)), r)
            pygame.draw.rect(tela, cor, (x - r * 0.55, y + r * 0.4, r * 1.1, r * 0.7))
            for o in (-0.4, 0.4):
                pygame.draw.circle(tela, (20, 30, 24), (int(x + o * r), int(y - r * 0.05)), max(1, int(r * 0.28)))
            pygame.draw.line(tela, (20, 30, 24), (x - r * 0.3, y + r * 0.75), (x + r * 0.3, y + r * 0.75), 1)


# =====================================================================
# FINN: VOO DE VASSOURA (o Finn de verdade some e uma cópia dá uma volta voando)
# =====================================================================
def finn_vassoura_passo(l, jogo):
    if fim_pose(l):
        return
    usa_pose(l, dict(l.poses.get("f_levita") or l.poses["parado"]))
    l.esconde = 6 <= l.t < T - 10
    if l.t == 6:
        som.tocar("vento", 0.5)
        fumaca(jogo, l.x, CHAO - 8, 8, (200, 170, 240), 3, -1)
    if l.t == T - 10:
        som.tocar("queda", 0.4)


def finn_vassoura(l, tela):
    if not 6 <= l.t < T - 10:
        return
    k = (l.t - 6) / (T - 16)
    a = k * math.tau  # uma volta inteira (subindo pela frente, descendo por trás)
    x = l.x + math.sin(a) * 60 * l.s
    y = l.y - onda(k) * 90 * l.s - math.sin(a) * 10 * l.s
    vai = 1 if math.cos(a) >= 0 else -1  # (vira pra onde está voando)
    img, (px, py) = sprite(l, l.poses.get("f_levita") or l.poses["parado"])
    if vai * l.dir < 0:
        img = pygame.transform.flip(img, True, False)
        px = img.get_width() - px
    base_y = y - 18 * l.s
    for i in range(3):  # o rastro de estrelinhas
        tx = x - vai * l.dir * (30 + i * 16) * l.s
        brilho(tela, (int(tx), int(base_y + 6)), int((10 - i * 3) * l.s), (255, 200, 90), 160 - i * 40)
    d = vai * l.dir
    cabo0, cabo1 = (x - d * 40 * l.s, base_y + 4 * l.s), (x + d * 34 * l.s, base_y - 4 * l.s)
    pygame.draw.line(tela, (18, 12, 26), cabo0, cabo1, max(4, int(5 * l.s)))  # a VASSOURA (deitada)
    pygame.draw.line(tela, (130, 86, 46), cabo0, cabo1, max(2, int(3 * l.s)))
    palha = [(cabo0[0], cabo0[1] - 3 * l.s), (cabo0[0] - d * 22 * l.s, cabo0[1] - 9 * l.s),
             (cabo0[0] - d * 24 * l.s, cabo0[1] + 9 * l.s), (cabo0[0], cabo0[1] + 4 * l.s)]
    pygame.draw.polygon(tela, (18, 12, 26), palha)
    pygame.draw.polygon(tela, (214, 172, 84), [(px_ * 0.9 + cabo0[0] * 0.1, py_ * 0.9 + cabo0[1] * 0.1) for px_, py_ in palha])
    tela.blit(img, (x - px, base_y - py + 6 * l.s))


# =====================================================================
# CRÁQUEN: VIRA MORCEGO (PUF, um morcegão dá uma volta, PUF, volta)
# =====================================================================
def craquen_morcego_passo(l, jogo):
    if fim_pose(l):
        return
    usa_pose(l, dict(l.poses["parado"]))
    l.esconde = 10 <= l.t < T - 12
    if l.t in (10, T - 12):
        som.tocar("puf", 0.7)
        fumaca(jogo, l.x, l.y - 60 * l.s, 12, (90, 60, 110), 4, -0.6)
    if l.t == 24:
        som.tocar("uivo", 0.3)


def morcegao(tela, x, y, t, s, d):
    bate = math.sin(t * 0.8)
    k, cor, asa = (10, 6, 12), (40, 26, 46), (64, 40, 74)
    for lado in (-1, 1):  # as asas (com as pontas recortadas)
        pts = [(x, y), (x + lado * 18 * s, y - (14 + 10 * bate) * s), (x + lado * 34 * s, y - (8 + 12 * bate) * s),
               (x + lado * 30 * s, y + 2 * s), (x + lado * 22 * s, y - 2 * s), (x + lado * 14 * s, y + 6 * s)]
        pygame.draw.polygon(tela, k, pts)
        pygame.draw.polygon(tela, asa, [(px * 0.9 + x * 0.1, py * 0.9 + y * 0.1) for px, py in pts])
    pygame.draw.ellipse(tela, k, (x - 9 * s, y - 8 * s, 18 * s, 18 * s))
    pygame.draw.ellipse(tela, cor, (x - 7 * s, y - 6 * s, 14 * s, 14 * s))
    for o in (-1, 1):  # orelhas e olhos vermelhos
        pygame.draw.polygon(tela, cor, [(x + o * 3 * s, y - 5 * s), (x + o * 7 * s, y - 13 * s), (x + o * 7 * s, y - 4 * s)])
        pygame.draw.circle(tela, (255, 50, 50), (int(x + o * 3 * s + d * 1.5 * s), int(y - 1 * s)), max(1, int(1.6 * s)))
    pygame.draw.polygon(tela, (250, 250, 250), [(x - 2 * s, y + 4 * s), (x - 0.5 * s, y + 4 * s), (x - 1.2 * s, y + 7 * s)])
    pygame.draw.polygon(tela, (250, 250, 250), [(x + 0.5 * s, y + 4 * s), (x + 2 * s, y + 4 * s), (x + 1.2 * s, y + 7 * s)])


def craquen_morcego(l, tela):
    if not 10 <= l.t < T - 12:
        return
    k = (l.t - 10) / (T - 22)
    a = k * math.tau
    x = l.x + math.sin(a) * 70 * l.s
    y = l.y - 90 * l.s - math.sin(a * 2) * 26 * l.s
    morcegao(tela, x, y, l.t, 1.3 * l.s / 1.36, l.dir)


# =====================================================================
# MAX-10: CURTO-CIRCUITO (faíscas verdes dos parafusos do pescoço, BZZT!)
# =====================================================================
def max_curto_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(l.poses["parado"])
    if 10 <= l.t < T - 12:  # tremendo inteiro, de choque
        tr = 3 if l.t % 2 else -3
        p = {k: (x + tr * 0.5, y + (1 if l.t % 4 < 2 else -1)) for k, (x, y) in p.items()}
    usa_pose(l, p)
    if l.t % 6 == 0 and 10 <= l.t < T - 12:
        cb = ponto(l, "cb")
        for lado in (-1, 1):
            for _ in range(3):
                jogo.faiscas.append([cb[0] + lado * 10 * l.s, cb[1] + 12 * l.s, lado * 2.5 + (l.t % 3 - 1),
                                     -3 - (l.t % 5) * 0.5, 16, (150, 255, 110), 3])
        som.tocar("defesa", 0.2)
    if l.t == T - 12:
        fumaca(jogo, ponto(l, "cb")[0], ponto(l, "cb")[1] - 10, 6, (90, 100, 90), 2, -1.2)


def max_curto(l, tela):
    if not 10 <= l.t < T - 12:
        return
    cb = ponto(l, "cb")
    for lado in (-1, 1):  # os raios pulando de um parafuso pro outro, por cima da cabeça
        pts = [(cb[0] + lado * 10 * l.s, cb[1] + 10 * l.s)]
        for i in range(1, 5):
            pts.append((cb[0] + lado * (10 - i * 2.5) * l.s + ((l.t + i) % 3 - 1) * 5, cb[1] - i * 8 * l.s))
        pygame.draw.lines(tela, (120, 255, 100), False, pts, 3)
        pygame.draw.lines(tela, (240, 255, 230), False, pts, 1)
    brilho(tela, (int(cb[0]), int(cb[1] - 20 * l.s)), int(30 * l.s), (150, 255, 120), 120)
    if (l.t // 8) % 2:
        from efeitos import texto
        texto(tela, "BZZT!", 18, (190, 255, 140), (int(cb[0] + l.dir * 40 * l.s), int(cb[1] - 40 * l.s)))


# =====================================================================
# RIB ZUMBI: O BRAÇO CAIU (cai no chão, ele olha, pega e encaixa de novo)
# =====================================================================
BRACO_CAI, BRACO_PEGA, BRACO_ENCAIXA = 10, 36, 52


def rib_braco_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(l.poses["parado"])
    pc = p["pc"]
    if BRACO_CAI <= l.t < BRACO_ENCAIXA:  # sem o braço da frente (encolhido atrás do ombro)
        p["cf"], p["mf"] = (pc[0] - 2, pc[1] - 3), (pc[0] - 3, pc[1] - 5)
    if BRACO_PEGA - 10 <= l.t < BRACO_PEGA + 4:  # se abaixa pra pegar (com o outro braço)
        p["mt"] = (p["mt"][0] + 26, 6)
        p["ct"] = (p["ct"][0] + 14, 34)
        p["cb"] = (p["cb"][0] + 10, p["cb"][1] - 10)
    usa_pose(l, p)
    if l.t == BRACO_CAI + 8:
        som.tocar("queda", 0.4)
    if l.t == BRACO_ENCAIXA:
        som.tocar("defesa", 0.6)  # (CLEC! encaixou)


def rib_braco(l, tela):
    t = l.t
    if not BRACO_CAI <= t < BRACO_ENCAIXA:
        return
    s = l.s
    chao_x = l.x + l.dir * 36 * s
    if t < BRACO_CAI + 8:  # caindo do ombro
        k = (t - BRACO_CAI) / 8
        c = ponto(l, "pc")
        x, y = c[0] + (chao_x - c[0]) * k, c[1] + (CHAO - 6 - c[1]) * k * k
        ang = k * 1.6
    elif t < BRACO_PEGA:  # largado no chão (os dedos ainda mexendo)
        x, y, ang = chao_x, CHAO - 6, 1.6
    else:  # na mão de trás, voltando pro ombro
        k = suave(min(1, (t - BRACO_PEGA) / (BRACO_ENCAIXA - BRACO_PEGA)))
        m, c = ponto(l, "mt"), ponto(l, "pc")
        x, y, ang = m[0] + (c[0] - m[0]) * k, m[1] + (c[1] - m[1]) * k, 1.6 * (1 - k)
    comp = 34 * s
    dx, dy = math.sin(ang) * comp * l.dir, math.cos(ang) * comp
    fim = (x + dx, y + dy)
    pygame.draw.line(tela, (16, 24, 14), (x, y), fim, max(5, int(8 * s)))
    pygame.draw.line(tela, (112, 132, 72), (x, y), fim, max(3, int(5 * s)))
    pygame.draw.circle(tela, (16, 24, 14), (int(fim[0]), int(fim[1])), int(6 * s))
    pygame.draw.circle(tela, (150, 172, 104), (int(fim[0]), int(fim[1])), int(4.6 * s))
    if BRACO_CAI + 8 <= t < BRACO_PEGA and (t // 4) % 2:  # os dedinhos mexendo sozinhos
        pygame.draw.line(tela, (150, 172, 104), fim, (fim[0] + 6, fim[1] - 4), 2)
    pygame.draw.circle(tela, (150, 110, 80), (int(x), int(y)), int(4 * s))  # o remendo da ponta


def _h(lutador, ident, nome, frase, passo, desenho):
    extras.registrar("provocacoes", lutador, id=ident, nome=nome, preco=0, evento=EVENTO, provocacao=frase,
                     provocacao_passo=passo, provocacao_desenho=desenho)


_h("SPHYRUS", "hw_bolhas", "BOLHAS ASSOMBRADAS", "GLUB GLUB... BUUU!", sphyrus_bolhas_passo, sphyrus_bolhas)
_h("FINN", "hw_vassoura", "VOO DE VASSOURA", "Hehehe! Pega se puder!", finn_vassoura_passo, finn_vassoura)
_h("CRÁQUEN", "hw_morcego", "VIRA MORCEGO", "Eu vou sugar sua coragem!", craquen_morcego_passo, craquen_morcego)
_h("MAX-10", "hw_curto", "CURTO-CIRCUITO", "ERRO. ERRO. ESTÁ VIVO!", max_curto_passo, max_curto)
_h("RIB", "hw_braco", "O BRAÇO CAIU", "Opa... peraí. Pronto!", rib_braco_passo, rib_braco)
