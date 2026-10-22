"""TAMER: o sobrevivente da selva e o seu lobo (criado pelo Gomes).

Aparência: igual aquelas pessoas de documentário de sobreviver na selva, sempre com um LOBO do lado.
  E      manda o LOBO avançar (15)
  Q      chute que lança o oponente NA PAREDE e faz ele subir (15 + 5 quando bate na parede)
  R      ele e o lobo combam juntos: 8 hits de 3
  SHIFT  monta no lobo e sai GALOPANDO (10)
  Z      ULTIMATE: o lobo uiva e chegam mais 3 lobos, que combam o oponente (35)
  Passiva: ENTENDIMENTO MÚTUO — X troca o lobo: BRANCO = +dano, PRETO = +velocidade
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from corpo import cabeca_eixos, eixos, frente_do_pe, mais
from golpes import GOLPES, misturar, proporcionar, suave
from max10 import brilho, fumaca
from pecas import Peca

POSES_TAMER = {
    "parado": dict(pt=(-24, 0), jt=(-14, 26), pf=(22, 0), jf=(26, 28), qd=(0, 50), pc=(4, 86), cb=(8, 104),
                   ct=(-6, 70), mt=(2, 84), cf=(18, 74), mf=(30, 84)),
    "andar1": dict(pt=(-26, 2), jt=(-14, 26), pf=(26, 0), jf=(28, 28), qd=(0, 48), pc=(4, 84), cb=(8, 102),
                   ct=(-8, 68), mt=(0, 82), cf=(18, 72), mf=(30, 82)),
    "andar2": dict(pt=(4, 10), jt=(14, 30), pf=(2, 0), jf=(10, 28), qd=(0, 52), pc=(4, 88), cb=(8, 106),
                   ct=(-6, 72), mt=(2, 86), cf=(18, 76), mf=(30, 86)),
    "andar3": dict(pt=(24, 0), jt=(28, 28), pf=(-24, 2), jf=(-12, 26), qd=(0, 48), pc=(4, 84), cb=(8, 102),
                   ct=(-4, 68), mt=(4, 82), cf=(18, 72), mf=(30, 82)),
    "andar4": dict(pt=(2, 0), jt=(10, 28), pf=(4, 10), jf=(14, 30), qd=(0, 52), pc=(4, 88), cb=(8, 106),
                   ct=(-6, 72), mt=(2, 86), cf=(18, 76), mf=(30, 86)),
    "t_aponta": dict(pt=(-24, 0), jt=(-14, 26), pf=(24, 0), jf=(26, 28), qd=(0, 50), pc=(6, 86), cb=(10, 104),
                     ct=(-10, 72), mt=(-14, 58), cf=(26, 90), mf=(54, 96)),
    "t_chute": dict(pt=(-14, 0), jt=(-8, 28), pf=(66, 60), jf=(34, 58), qd=(0, 56), pc=(-12, 88), cb=(-16, 104),
                    ct=(-24, 70), mt=(-34, 58), cf=(-8, 72), mf=(-16, 58)),
    "t_soco_a": dict(pt=(-28, 0), jt=(-18, 26), pf=(26, 0), jf=(28, 28), qd=(0, 48), pc=(10, 84), cb=(16, 100),
                     ct=(-6, 72), mt=(2, 82), cf=(30, 88), mf=(56, 90)),
    "t_soco_b": dict(pt=(-28, 0), jt=(-18, 26), pf=(26, 0), jf=(28, 28), qd=(0, 48), pc=(8, 84), cb=(14, 100),
                     ct=(28, 86), mt=(54, 88), cf=(10, 72), mf=(16, 60)),
    "t_monta": dict(pt=(16, 8), jt=(22, 30), pf=(-8, 8), jf=(-2, 30), qd=(0, 44), pc=(14, 78), cb=(22, 94),
                    ct=(26, 70), mt=(40, 62), cf=(30, 72), mf=(44, 66)),
    "t_grito": dict(pt=(-20, 0), jt=(-16, 28), pf=(20, 0), jf=(18, 28), qd=(0, 56), pc=(2, 92), cb=(4, 110),
                    ct=(-10, 104), mt=(-16, 124), cf=(14, 104), mf=(22, 124)),
    "t_carinho": dict(pt=(-20, 0), jt=(-4, 20), pf=(20, 0), jf=(30, 20), qd=(0, 34), pc=(14, 62), cb=(22, 76),
                      ct=(8, 48), mt=(18, 34), cf=(-6, 50), mf=(-30, 36)),
    # (as poses do meio: deixam os golpes FLUIDOS — pedido do Gomes)
    "t_assobia": dict(pt=(-24, 0), jt=(-14, 26), pf=(22, 0), jf=(26, 28), qd=(0, 50), pc=(4, 86), cb=(8, 104),
                      ct=(-6, 70), mt=(2, 84), cf=(14, 92), mf=(10, 100)),
    "t_aponta_firme": dict(pt=(-26, 0), jt=(-16, 26), pf=(26, 0), jf=(30, 26), qd=(0, 48), pc=(10, 84), cb=(14, 102),
                           ct=(-10, 70), mt=(-16, 56), cf=(30, 90), mf=(58, 94)),
    "t_chute_prep": dict(pt=(-16, 0), jt=(-10, 28), pf=(22, 30), jf=(26, 50), qd=(0, 54), pc=(-4, 88), cb=(-6, 104),
                         ct=(-18, 72), mt=(-24, 60), cf=(4, 76), mf=(-2, 62)),
    "t_chute_volta": dict(pt=(-16, 0), jt=(-10, 28), pf=(30, 36), jf=(30, 52), qd=(0, 54), pc=(-6, 88), cb=(-8, 104),
                          ct=(-20, 72), mt=(-28, 60), cf=(0, 74), mf=(-6, 60)),
    "t_monta_pula": dict(pt=(-20, 10), jt=(-8, 30), pf=(10, 20), jf=(16, 38), qd=(0, 56), pc=(8, 90), cb=(14, 106),
                         ct=(14, 96), mt=(26, 106), cf=(20, 96), mf=(34, 104)),
    "t_monta2": dict(pt=(18, 4), jt=(24, 26), pf=(-10, 4), jf=(-4, 26), qd=(0, 40), pc=(18, 72), cb=(28, 86),
                     ct=(28, 64), mt=(42, 56), cf=(32, 66), mf=(46, 60)),
}
proporcionar(POSES_TAMER)

# =====================================================================
# O LOBO (desenhado por código; anda do lado dele)
# =====================================================================
CORES_LOBO = {
    "branco": ((232, 234, 240), (182, 188, 202), (120, 126, 142), (90, 170, 255)),
    "preto": ((56, 56, 66), (36, 36, 44), (20, 20, 26), (255, 200, 60)),
    "cinza": ((150, 150, 158), (110, 110, 120), (70, 70, 80), (255, 210, 80)),
}


LOBO_MAIOR = 1.2  # (remodel do Gomes: o lobo maior, com destaque)


def desenha_lobo(tela, x, chao, esc, d, pose, t, cor="branco", skin=None):
    """O lobo de lado. pose: parado, corre, morde, uiva, montado.
    skin: dict(olho=cor, tam=escala) da roupa (ZEUS: o lobo vira o FENRIR, maior e de olho vermelho)."""
    c1, c2, c3, olho = (skin or {}).get("cores", {}).get(cor) or CORES_LOBO[cor]
    u = esc * 0.62 * LOBO_MAIOR
    if skin:
        olho = skin.get("olho", olho)
        u *= skin.get("tam", 1)

    def P(px, py):
        return x + d * px * u, chao - py * u

    corre = pose in ("corre", "montado", "morde")
    passo = t * (0.6 if corre else 0.1)
    corpo_y = 26 if pose != "uiva" else 22
    if pose == "uiva":  # sentado: corpo inclinado
        corpo = [P(-22, 14), P(-14, 30), P(10, 38), P(20, 30), P(18, 12)]
        pygame.draw.polygon(tela, c1, corpo)
    # pernas (as de trás atrás do corpo, um pouco mais escuras)
    for lado, base_x, fase in ((0, -14, 0), (0, 14, 1.6), (1, -18, 3.1), (1, 10, 4.7)):
        cor = c2 if lado == 0 else c1
        if pose == "uiva" and base_x < 0:
            pygame.draw.line(tela, cor, P(base_x, 16), P(base_x + 10, 2), max(2, int(5 * u)))
            continue
        bal = math.sin(passo + fase) * (12 if corre else 1)
        pe = P(base_x + bal, 0)
        if base_x < 0:  # perna de TRÁS: coxa grossa, joelho pra frente e o jarrete dobrado pra trás
            quadril = P(base_x + 2, corpo_y - 2)
            joelho = P(base_x + 6 + bal * 0.4, 13)
            jarrete = P(base_x - 3 + bal * 0.7, 6)
            pygame.draw.line(tela, cor, quadril, joelho, max(3, int(8 * u)))
            pygame.draw.line(tela, cor, joelho, jarrete, max(2, int(4.6 * u)))
            pygame.draw.line(tela, cor, jarrete, pe, max(2, int(3.6 * u)))
        else:  # perna da FRENTE: retinha
            joelho = P(base_x + bal * 0.5, 11)
            pygame.draw.line(tela, cor, P(base_x, corpo_y - 6), joelho, max(2, int(5.6 * u)))
            pygame.draw.line(tela, cor, joelho, pe, max(2, int(4.2 * u)))
        pygame.draw.ellipse(tela, c3, (pe[0] - 3 * u, pe[1] - 1.6 * u, 6 * u, 3.2 * u))  # a patinha
    if pose != "uiva":
        y0 = corpo_y
        corpo = [P(-26, y0 + 2), P(-20, y0 + 8), P(-6, y0 + 9), P(10, y0 + 10), P(22, y0 + 7), P(26, y0 - 1),
                 P(22, y0 - 11), P(12, y0 - 10), P(4, y0 - 5), P(-8, y0 - 5), P(-20, y0 - 7), P(-27, y0 - 3)]
        pygame.draw.polygon(tela, c1, corpo)  # peito fundo na frente, cintura fina, quadril atrás
        barriga = [P(-18, y0 - 4), P(-6, y0 - 3), P(4, y0 - 4), P(14, y0 - 8), P(22, y0 - 10), P(12, y0 - 11),
                   P(2, y0 - 6), P(-10, y0 - 6), P(-20, y0 - 7)]
        pygame.draw.polygon(tela, c2, barriga)  # a barriga na sombra
        claro = tuple(min(255, int(c + (255 - c) * 0.35)) for c in c1)
        pygame.draw.lines(tela, claro, False, [P(-22, y0 + 6), P(-6, y0 + 8), P(10, y0 + 9), P(20, y0 + 6)],
                          max(1, int(1.8 * u)))  # a luz no lombo
        for i in range(3):  # tufinhos macios no peito
            a = P(23 - i * 2, y0 - 2 - i * 3)
            pygame.draw.line(tela, c2, a, P(26 - i * 2, y0 - 5 - i * 3), max(1, int(1.2 * u)))
    # rabo
    abana = math.sin(t * (0.5 if not corre else 0.25)) * 6
    rabo = [P(-24, corpo_y + 3), P(-34, corpo_y + 6 + abana * 0.4), P(-42, corpo_y + 1 + abana), P(-46, corpo_y - 6 + abana)]
    for i, (a, b) in enumerate(zip(rabo, rabo[1:])):  # grosso no meio (peludo), fino na base
        pygame.draw.line(tela, c1, a, b, max(3, int((6 + 3 * (i == 1)) * u)))
    ponta = rabo[-1]
    pygame.draw.circle(tela, c1, (int(rabo[2][0]), int(rabo[2][1])), max(3, int(4.4 * u)))
    pygame.draw.circle(tela, tuple(min(255, int(c + (255 - c) * 0.5)) for c in c1), (int(ponta[0]), int(ponta[1])),
                       max(2, int(3.2 * u)))  # a pontinha clara
    # pescoço e cabeça
    if pose == "uiva":
        cab, focinho_dir = P(18, 50), (0.4, 1.0)  # cabeça pra cima
    elif pose == "morde":
        cab, focinho_dir = P(30, 28), (1.0, -0.2)
    else:
        cab, focinho_dir = P(26, 36 + math.sin(t * 0.1) * 0.6), (1.0, -0.15)
    pescoco = P(14, corpo_y + 4)
    pygame.draw.line(tela, c1, pescoco, cab, max(3, int(14 * u)))
    juba = [P(6, corpo_y + 12), P(12, corpo_y + 20), P(18, corpo_y + 14), P(22, corpo_y + 18), P(24, corpo_y + 6),
            P(18, corpo_y - 4), P(10, corpo_y - 2)]
    pygame.draw.polygon(tela, c1, juba)  # a juba de lobo no pescoço
    pygame.draw.lines(tela, c2, False, juba[:4], max(1, int(2 * u)))
    pygame.draw.ellipse(tela, c1, (cab[0] - 9 * u, cab[1] - 8 * u, 18 * u, 15 * u))
    fx, fy = focinho_dir
    ponta = (cab[0] + d * fx * 15 * u, cab[1] - fy * 15 * u + 3 * u)
    base1 = (cab[0] + d * 2 * u, cab[1] - 4 * u)
    base2 = (cab[0] + d * 2 * u, cab[1] + 5 * u)
    pygame.draw.polygon(tela, c1, [base1, ponta, base2])
    pygame.draw.line(tela, c2, (cab[0] + d * 4 * u, cab[1] + 4 * u), ponta, max(1, int(2 * u)))  # boca
    pygame.draw.circle(tela, c3, (int(ponta[0]), int(ponta[1])), max(1, int(2.2 * u)))  # nariz
    if pose == "morde" and (t // 3) % 2:  # boca aberta
        pygame.draw.polygon(tela, (150, 40, 50), [base2, ponta, (ponta[0], ponta[1] + 6 * u)])
    for oy in (0, 5):  # orelhas
        o = (cab[0] - d * (2 + oy * 0.6) * u, cab[1] - 6 * u)
        pygame.draw.polygon(tela, c2 if oy else c1, [o, (o[0] - d * 3 * u, o[1] - 9 * u), (o[0] + d * 4 * u, o[1] - 2 * u)])
    pygame.draw.circle(tela, olho, (int(cab[0] + d * 3 * u), int(cab[1] - 2 * u)), max(1, int(1.8 * u)))
    if not (skin and skin.get("corrente")):  # a COLEIRA vermelha com a PLAQUINHA dourada
        pm = ((pescoco[0] + cab[0]) / 2, (pescoco[1] + cab[1]) / 2)
        pygame.draw.line(tela, (20, 14, 10), (pm[0] - d * 5 * u, pm[1] - 4 * u), (pm[0] + d * 4 * u, pm[1] + 5 * u),
                         max(3, int(4.4 * u)))
        pygame.draw.line(tela, (190, 40, 36), (pm[0] - d * 5 * u, pm[1] - 4 * u), (pm[0] + d * 4 * u, pm[1] + 5 * u),
                         max(2, int(3 * u)))
        placa = (pm[0] + d * 1 * u, pm[1] + 5 * u + math.sin(t * 0.2) * u)
        pygame.draw.circle(tela, (20, 14, 10), (int(placa[0]), int(placa[1])), max(2, int(2.6 * u)))
        pygame.draw.circle(tela, (246, 200, 70), (int(placa[0]), int(placa[1])), max(1, int(1.9 * u)))
    if skin and skin.get("corrente"):  # FENRIR: a coleira de corrente quebrada (da lenda)
        pescoco_meio = ((pescoco[0] + cab[0]) / 2, (pescoco[1] + cab[1]) / 2)
        for k in range(5):
            a = k * 1.2
            elo = (pescoco_meio[0] + math.cos(a) * 7 * u, pescoco_meio[1] + math.sin(a) * 4 * u)
            pygame.draw.circle(tela, (40, 40, 48), (int(elo[0]), int(elo[1])), max(2, int(2.6 * u)), max(1, int(1.2 * u)))
        solto = [(pescoco_meio[0] - d * 2 * u, pescoco_meio[1] + 4 * u + k * 3.6 * u) for k in range(4)]
        for k, e in enumerate(solto):  # o pedaço da corrente que arrebentou, balançando
            ee = (e[0] + math.sin(t * 0.2 + k) * 2 * u, e[1])
            pygame.draw.circle(tela, (40, 40, 48), (int(ee[0]), int(ee[1])), max(2, int(2.2 * u)), max(1, int(1.1 * u)))
    if skin and "olho" in skin:  # o brilho do olho do Fenrir
        brilho = pygame.Surface((int(12 * u) + 2, int(12 * u) + 2), pygame.SRCALPHA)
        pygame.draw.circle(brilho, (*olho, 90), (brilho.get_width() // 2, brilho.get_height() // 2), int(6 * u))
        tela.blit(brilho, (cab[0] + d * 3 * u - brilho.get_width() // 2, cab[1] - 2 * u - brilho.get_height() // 2))
    if pose == "uiva" and (t // 8) % 2:  # as notinhas do uivo
        for k in range(3):
            r = (6 + k * 7) * u
            pygame.draw.arc(tela, (230, 230, 255), (ponta[0] - r, ponta[1] - r - 6 * u, 2 * r, 2 * r), 0.6, 2.4, 2)


def cor_lobo(l):
    return l.extra.get("lobo_cor", "branco")


GOLPES_COM_LOBO = ("tamer_lobo", "tamer_combo", "tamer_galope", "tamer_ultimate")


def todo_quadro(l, jogo):
    """O lobo segue o Tamer (fica do lado dele) quando não está atacando."""
    x = l.extra
    x.setdefault("lobo_x", l.x - l.dir * 46 * l.s)
    x.setdefault("lobo_cor", "branco")
    x.setdefault("lobo_troca", 0)
    if x["lobo_troca"] > 0:
        x["lobo_troca"] -= 1
    if l.estado == "ataque" and l.nome_golpe in GOLPES_COM_LOBO:
        return  # (o golpe controla o lobo)
    if l.estado == "vitoria" and x.get("lobo_vit"):
        return  # (a vitória da loja controla o lobo)
    alvo = l.x - l.dir * 46 * l.s * (skin_lobo(l) or {}).get("tam", 1) ** 3  # (lobo maior fica mais pra trás)
    dx = alvo - x["lobo_x"]
    x["lobo_x"] += dx * 0.18
    x["lobo_dir"] = l.dir
    x["lobo_pose"] = "corre" if abs(dx) > 6 else "parado"


LOBISOMEM = dict(olho=(255, 50, 30), tam=1.4, cores={  # LUA CHEIA (2ª ultimate): o lobo vira LOBISOMEM
    c: ((74, 66, 72), (52, 46, 54), (30, 26, 32), (255, 50, 30)) for c in ("branco", "preto", "cinza")})


def skin_lobo_f(ficha):
    """(o mesmo do skin_lobo, a partir da ficha: pro desenho de frente)"""
    return ficha.get("lobo")


def skin_lobo(l):
    return LOBISOMEM if l.extra.get("lobisomem", 0) > 0 else l.f.get("lobo")


def trocar_lobo(l):
    """ENTENDIMENTO MÚTUO: o lobo branco vira preto (e o preto vira branco)."""
    x = l.extra
    if x.get("lobo_troca", 0) > 0:
        return
    x["lobo_cor"] = "preto" if x.get("lobo_cor", "branco") == "branco" else "branco"
    x["lobo_troca"] = 30
    x["lobo_flash"] = 20
    som.tocar("puf", 0.6)


# =====================================================================
# E: O LOBO AVANÇA
# =====================================================================
E_SAI, E_FIM = 6, 40


def lobo_avanca(l, outro, jogo):
    t = l.t
    m = l.memo
    x = l.extra
    l.vx = 0
    l.fisica(jogo)
    if t == E_SAI:
        som.tocar("uivo", 0.3)
    if E_SAI <= t < E_FIM - 8 and "mordeu" not in m:
        x["lobo_x"] += 14 * l.dir
        x["lobo_pose"] = "corre"
        x["lobo_x"] = max(PAREDE_E, min(PAREDE_D, x["lobo_x"]))
    if l.acertou and "mordeu" not in m:
        m["mordeu"] = t
    if "mordeu" in m:
        x["lobo_pose"] = "morde"
    rel = (x["lobo_x"] - l.x) * l.dir / l.s
    m["caixa"] = (rel - 4, 0, rel + 44, 64)
    if t >= E_FIM:
        return "fim"


# =====================================================================
# Q: CHUTE NA PAREDE (bate na parede e sobe)
# =====================================================================
# (feito com os campos do golpe: derruba voando rápido pra parede, +5 na parede e "parede_sobe")

# =====================================================================
# R: COMBO EM DUPLA (8 hits: ele e o lobo alternando)
# =====================================================================
R_INI, R_INTERVALO, R_HITS = 8, 6, 8


def combo_dupla(l, outro, jogo):
    t = l.t
    x = l.extra
    k = (t - R_INI) // R_INTERVALO
    l.vx = 0.8 * l.dir if R_INI <= t < R_INI + R_HITS * R_INTERVALO else 0
    if R_INI <= t < R_INI + R_HITS * R_INTERVALO:
        if k % 2:  # a vez do lobo: pula na frente e morde
            x["lobo_x"] += (l.x + l.dir * 56 * l.s - x["lobo_x"]) * 0.5
            x["lobo_pose"] = "morde"
        else:
            x["lobo_x"] += (l.x - l.dir * 30 * l.s - x["lobo_x"]) * 0.3
            x["lobo_pose"] = "corre"
        if (t - R_INI) % R_INTERVALO == 0:
            som.tocar("soco" if k % 2 == 0 else "vento", 0.5)
    l.fisica(jogo)
    if t >= R_INI + R_HITS * R_INTERVALO + 12:
        return "fim"


def combo_quadros():
    q = [(0, "parado"), (R_INI - 2, "t_soco_b")]
    for k in range(R_HITS):
        q.append((R_INI + k * R_INTERVALO + 2, "t_soco_a" if k % 4 == 0 else "t_soco_b" if k % 4 == 2 else "parado"))
    q.append((R_INI + R_HITS * R_INTERVALO + 12, "parado"))
    return q


# =====================================================================
# SHIFT: MONTA NO LOBO E GALOPA
# =====================================================================
S_MONTA, S_FIM = 8, 42


def galope(l, outro, jogo):
    t = l.t
    m = l.memo
    x = l.extra
    if l.acertou:
        m["bateu"] = True
    if S_MONTA <= t < S_FIM and "bateu" not in m:
        l.vx = 11.5 * l.dir
        if t % 3 == 0:
            fumaca(jogo, l.x - 30 * l.dir, CHAO - 4, 1, (150, 130, 100), 1, -0.3)
    else:
        l.vx *= 0.7
    x["lobo_x"] = l.x
    x["lobo_pose"] = "montado" if t < S_FIM + 4 else "parado"
    l.fisica(jogo)
    if t >= S_FIM + 12:
        x["lobo_x"] = l.x - l.dir * 20 * l.s
        return "fim"


def montado(l):
    return l.estado == "ataque" and l.nome_golpe == "tamer_galope" and S_MONTA - 2 <= l.t < S_FIM + 4


# =====================================================================
# Z: ULTIMATE — A ALCATEIA (o lobo uiva, chegam mais 3)
# =====================================================================
U_UIVO, U_CHEGAM, U_MORDIDAS, U_INTERVALO, U_DANO = 40, 62, 7, 12, 5
U_FIM_PEGOU = U_CHEGAM + U_MORDIDAS * U_INTERVALO + 30


def alcateia(l, outro, jogo):
    t = l.t
    m = l.memo
    x = l.extra
    l.vx = 0
    l.fisica(jogo)
    x["lobo_x"] = l.x + l.dir * 30 * l.s
    x["lobo_pose"] = "uiva" if t < U_UIVO + 10 else "parado"
    if t == 4:
        som.tocar("uivo")
    if t == U_UIVO:
        som.tocar("uivo", 0.7)
        m["alvo"] = (outro.x, outro.y)
    if t == U_CHEGAM and "pegou" not in m and "errou" not in m:
        defende = outro.estado == "defendendo" or outro.pode_defender(GOLPES["tamer_ultimate"])
        livre = outro.no_chao() and not defende and outro.estado not in ("caido", "agarrado") and outro.inv == 0
        if livre:  # A ALCATEIA PEGOU
            m["pegou"] = t
            outro.mudar("agarrado")
            outro.golpe = None
            outro.sobrepor = dict(outro.poses["golpeado"])
            outro.y, outro.vx, outro.vy = CHAO, 0, 0
            l.inv = 999
            jogo.tremer(10)
        else:  # pulou ou defendeu: os lobos passam direto
            m["errou"] = t
    if "pegou" in m:
        u = t - m["pegou"]
        if u % U_INTERVALO == 6 and u // U_INTERVALO < U_MORDIDAS:
            ultima = u // U_INTERVALO == U_MORDIDAS - 1
            outro.levar(U_DANO, l, GOLPES["tamer_ultimate"])
            if not ultima:
                outro.vida = max(1, outro.vida)
            outro.tremor_hit = 8
            jogo.faisca(outro.x + random.uniform(-20, 20), outro.y - random.uniform(30, 90) * outro.s, False, ultima)
            jogo.tremer(5)
            som.tocar("chute" if ultima else "soco", 0.7)
        if u == U_MORDIDAS * U_INTERVALO + 6:
            outro.sobrepor = {}
            outro.mudar("voando")
            outro.vx, outro.vy = 5 * l.dir, -8
            l.inv = 0
        if t >= U_FIM_PEGOU:
            return "fim"
    elif "errou" in m and t >= U_CHEGAM + 40:
        return "fim"


def alcateia_efeito(l, tela):
    """Os 3 lobos (cinzas) chegando e combando."""
    m = l.memo
    t = l.t
    if t < U_UIVO or "alvo" not in m:
        return
    ax, ay = m["alvo"]
    esc = l.s / S_REF
    lugares = ((-1, -70), (1, 70), (1, 20))  # (de que lado vem, onde para em volta do alvo)
    for i, (lado, perto) in enumerate(lugares):
        de = ax + lado * 600
        k = min(1.0, (t - U_UIVO) / (U_CHEGAM - U_UIVO))
        if "errou" in m:  # passam direto e somem do outro lado
            k = (t - U_UIVO) / (U_CHEGAM - U_UIVO)
            x = de + (ax - lado * 600 - de) * min(1.4, k * 0.7)
            pose = "corre"
        else:
            x = de + (ax + perto - de) * suave(k)
            pose = "corre" if k < 1 else "morde"
            if "pegou" in m and pose == "morde":
                u = t - m["pegou"]
                x += math.sin(u * 0.5 + i * 2) * 10  # pulando em volta
        desenha_lobo(tela, x, ay - (12 if pose == "morde" and (t // 4 + i) % 2 else 0), esc, -lado, pose, t + i * 9,
                     "cinza", skin_lobo(l))


# =====================================================================
# Golpes
# =====================================================================
def galope_quadros():
    """Pula pra montar e SACODE no ritmo do galope (pedido do Gomes: mais fluido)."""
    q = [(0, "parado"), (3, "t_monta_pula"), (S_MONTA - 2, "t_monta")]
    t, k = S_MONTA + 3, 0
    while t < S_FIM:
        q.append((t, "t_monta2" if k % 2 == 0 else "t_monta"))
        t, k = t + 5, k + 1
    q += [(S_FIM + 2, "t_monta"), (S_FIM + 12, "parado")]
    return q


def _registra(nome, **g):
    g.setdefault("base", "parado")
    g.setdefault("pose", "parado")
    g.setdefault("caixa", None)
    g.setdefault("especial", True)
    g["total"] = g.get("total", g["ini"] + g["ativo"] + g.get("rec", 0))
    GOLPES[nome] = g


_registra("tamer_lobo", ini=E_SAI, ativo=E_FIM - E_SAI - 8, rec=8, janelas=((E_SAI + 2, E_FIM - 8),), dano=15, hit=18,
          defe=10, emp=4, nivel="medio", logica=lobo_avanca, ia="medio",
          quadros=[(0, "parado"), (3, "t_assobia"), (6, "t_assobia"), (9, "t_aponta"), (14, "t_aponta_firme"),
                   (E_FIM - 10, "t_aponta_firme"), (E_FIM, "parado")])
_registra("tamer_chute", ini=8, ativo=5, rec=20, caixa=(20, 40, 92, 104), dano=15, hit=24, defe=12, emp=3,
          nivel="medio", derruba=True, voo=(17, 1.5), parede=5, parede_sobe=True, ia="perto", som="vento",
          quadros=[(0, "parado"), (5, "t_chute_prep"), (9, "t_chute"), (16, "t_chute"), (21, "t_chute_volta"),
                   (33, "parado")])
_registra("tamer_combo", ini=R_INI, ativo=R_HITS * R_INTERVALO, rec=12,
          janelas=tuple((R_INI + k * R_INTERVALO, R_INI + k * R_INTERVALO + 3) for k in range(R_HITS)),
          caixa=(10, 20, 92, 112), dano=3, hit=10, defe=7, emp=1, nivel="medio", logica=combo_dupla, ia="perto",
          quadros=combo_quadros())
_registra("tamer_galope", ini=S_MONTA, ativo=S_FIM - S_MONTA, rec=12, janelas=((S_MONTA + 2, S_FIM),),
          caixa=(0, 0, 80, 110), dano=10, hit=22, defe=12, emp=7, nivel="medio", derruba=True, voo=(8, 8),
          logica=galope, ia="medio", som="vento",
          quadros=galope_quadros())
_registra("tamer_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=alcateia, efeito=alcateia_efeito, ia="ultimate",
          quadros=[(0, "parado"), (8, "t_grito"), (U_UIVO + 10, "t_grito"), (U_UIVO + 20, "parado")])
GOLPES["tamer_ultimate"]["total"] = 9999

GOLPES_TAMER = {"E": "tamer_lobo", "Q": "tamer_chute", "R": "tamer_combo", "SHIFT": "tamer_galope",
                "Z": "tamer_ultimate"}

# =====================================================================
# Desenho em pixel art (o Tamer)
# =====================================================================
#   k contorno  c C camisa cáqui  v colete/bolso  o O calça verde-oliva  b B bota  p P q pele  h H chapéu  s alça/cinto
PALETA = {
    "k": (22, 18, 12), "c": (176, 152, 100), "C": (212, 190, 136), "v": (128, 108, 70), "o": (96, 98, 64),
    "O": (126, 128, 86), "b": (86, 56, 32), "B": (120, 84, 50), "p": (214, 168, 124), "P": (186, 140, 100),
    "q": (140, 100, 68), "h": (150, 124, 78), "H": (190, 162, 108), "s": (70, 48, 28), "e": (20, 20, 20),
    "x": (60, 50, 40),
    "u": (22, 18, 12),  # os bolsos do peito (= contorno; na toga do ZEUS somem)
}
S_REF = 1.36 / 3

TRONCO = Peca([
    "...kkkkkkkk...",
    "..kcCCcccsck..",
    ".kcCCccccsccv.",
    ".kcCuuucscucv.",
    ".kcCuvucsuvcv.",
    ".kccuuusuuucv.",
    ".kcccccsccccv.",
    ".kccccsccccvk.",
    ".kcccscccccvk.",
    "..kcsccccccvk.",
    "..kscccccccvk.",
    "..kcccccccvk..",
    "..kssssssssk..",
    "..koooooooOk..",
    "..koooooooOk..",
    "..kooooooOOk..",
    "..kooooooOOk..",
    "...kooooOOk...",
    "....kkkkkk....",
], PALETA, a=(7, 16), b=(7, 1))

CABECA = Peca([
    "...kkkkkk.....",
    "..khHkHhhk....",
    "kkhbbbbbbbkkk.",
    "khhhhhhhhhhhhk",
    ".kkkppppppkkk.",
    "..kxpppkepk...",
    "..kxppppppk...",
    "..kkpppPppk...",
    "...kxxpppk....",
    "...kkxxxk.....",
    "....kkkk......",
], PALETA, a=(6, 6), b=(6, 0), estica=False)

COXA = Peca([
    ".kkkkkk.",
    "koOoooOk",
    "kOooooOk",
    "koovvoOk",
    "koovvook",
    "kooooook",
    "kooooook",
    ".kooook.",
    ".kooook.",
    ".kooook.",
    "..kook..",
    "..kkkk..",
], PALETA, a=(3, 0), b=(3, 11))

CANELA = Peca([
    ".kkkkk.",
    "koOoook",
    "koooook",
    "koooook",
    "koooook",
    "kkkkkkk",
    "kbBbbbk",
    "kbbbbbk",
    "kbbbbbk",
    ".kbbbk.",
    "..kkk..",
], PALETA, a=(3, 0), b=(3, 10))

BOTA = Peca([
    ".kkkkk.....",
    "kbBbbbkkkk.",
    "kbbbbbbbbbk",
    "kBBBBBBBBBk",
    "kkkkkkkkkkk",
], PALETA, a=(3, 1), b=(9, 1), estica=False)

BRACO = Peca([
    ".kkkk.",
    "kcCcvk",
    "kcCcvk",
    "kcccvk",
    "kcccvk",
    "kkkkkk",
    "kpPPqk",
    "kpPPqk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 8))

ANTEBRACO = Peca([
    ".kkk.",
    "kpPqk",
    "kpPqk",
    "kpPqk",
    "kpPqk",
    "kpPqk",
    "kpqqk",
    "kpqqk",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 8))

MAO = Peca([
    ".kkkk.",
    "kpPPqk",
    "kpPpqk",
    "kqqqqk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 4), estica=False)


def mochila(tela, l, p, esc, branco):
    """A MOCHILA do sobrevivente (atrás dele): com a corda enrolada e o cabo do facão."""
    def U(u):
        return l.ponto({"_": u}, "_")
    k = (150, 150, 160) if branco else PALETA["k"]
    pc, qd = p["pc"], p["qd"]
    topo = (pc[0] - 9, pc[1] - 2)
    cantos = [U((topo[0] - 6, topo[1])), U((topo[0] + 3, topo[1])), U((topo[0] + 3, topo[1] - 22)),
              U((topo[0] - 7, topo[1] - 20))]
    pygame.draw.polygon(tela, k, cantos)
    meio = (sum(c[0] for c in cantos) / 4, sum(c[1] for c in cantos) / 4)
    pygame.draw.polygon(tela, (245, 245, 250) if branco else PALETA["v"],
                        [(x * 0.82 + meio[0] * 0.18, y * 0.82 + meio[1] * 0.18) for x, y in cantos])
    if branco:
        return
    corda = U((topo[0] - 2, topo[1] + 2))  # a corda enrolada em cima
    pygame.draw.circle(tela, (196, 168, 110), (round(corda[0]), round(corda[1])), max(2, int(3.2 * esc)), max(1, int(1.2 * esc)))
    a, b = U((topo[0] + 1, topo[1] - 4)), U((topo[0] + 6, topo[1] + 6))  # o cabo do facão saindo
    pygame.draw.line(tela, k, a, b, max(2, int(2 * esc)))
    pygame.draw.line(tela, (96, 60, 34), a, b, max(1, int(1 * esc)))


def pele_de_lobo(tela, l, p, esc, branco, d):
    """A PELE DE LOBO nos ombros (cinza, com a cabecinha do lobo no ombro de trás)."""
    def U(u):
        return l.ponto({"_": u}, "_")
    k = (150, 150, 160) if branco else PALETA["k"]
    pele, escura = ((245, 245, 250), (245, 245, 250)) if branco else ((150, 150, 158), (104, 104, 114))
    pc = p["pc"]
    manto = [U((pc[0] - 10, pc[1] + 3)), U((pc[0] + 6, pc[1] + 4)), U((pc[0] + 7, pc[1] - 4)), U((pc[0] + 2, pc[1] - 8)),
             U((pc[0] - 4, pc[1] - 6)), U((pc[0] - 9, pc[1] - 10)), U((pc[0] - 12, pc[1] - 4))]
    pygame.draw.polygon(tela, k, manto)
    meio = (sum(c[0] for c in manto) / len(manto), sum(c[1] for c in manto) / len(manto))
    pygame.draw.polygon(tela, pele, [(x * 0.85 + meio[0] * 0.15, y * 0.85 + meio[1] * 0.15) for x, y in manto])
    for i in range(4):  # pelinhos
        a = U((pc[0] - 9 + i * 4, pc[1] - 5 - (i % 2) * 3))
        pygame.draw.line(tela, escura, a, (a[0] - d * 1.5 * esc, a[1] + 2.5 * esc), max(1, int(0.8 * esc)))
    # a cabecinha do lobo no ombro de trás
    cab = U((pc[0] - 10, pc[1] + 4))
    pygame.draw.circle(tela, k, (round(cab[0]), round(cab[1])), max(3, int(3.4 * esc)))
    pygame.draw.circle(tela, pele, (round(cab[0]), round(cab[1])), max(2, int(2.7 * esc)))
    orelha = [U((pc[0] - 12, pc[1] + 6)), U((pc[0] - 13, pc[1] + 10)), U((pc[0] - 9, pc[1] + 7))]
    pygame.draw.polygon(tela, escura, orelha)
    if not branco:
        o = U((pc[0] - 9, pc[1] + 4.5))
        pygame.draw.circle(tela, (40, 30, 30), (round(o[0]), round(o[1])), max(1, int(0.7 * esc)))


def colar_e_pintura(tela, l, p, na_cabeca, esc, branco):
    """COLAR DE DENTES no peito e a PINTURA DE GUERRA (2 riscos vermelhos na bochecha)."""
    if branco:
        return
    def U(u):
        return l.ponto({"_": u}, "_")
    pc = p["pc"]
    for i in range(5):  # os dentes (de lobo)
        bx, by = pc[0] + 1 + i * 2.2, pc[1] - 4 - abs(i - 2) * 1.2
        a, b, c = U((bx - 0.9, by)), U((bx + 0.9, by)), U((bx, by - 2.6))
        pygame.draw.polygon(tela, (20, 18, 12), [a, b, c])
        pygame.draw.polygon(tela, (240, 236, 214), [((a[0] + c[0]) / 2, (a[1] + c[1]) / 2), b, c])
    for i in range(2):  # a pintura de guerra: 2 riscos finos descendo na bochecha
        a, b = na_cabeca(6.4 + i * 1.3, 5.8), na_cabeca(6.0 + i * 1.3, 7.8)
        pygame.draw.line(tela, (150, 24, 24), a, b, 1)


def desenhar_tamer(l, tela, p, branco):
    esc = l.s / S_REF
    d = l.lado()
    espelho = d < 0
    perto_v = "branco" if branco else "normal"
    longe_v = "branco" if branco else "escuro"
    x = l.extra
    # o lobo (atrás dele quando está do lado; embaixo quando ele está montado)
    escala_mundo = l.s / l.f["tam"]  # (1 no mundo, 1/PIXEL no desenho pequeno)
    if "lobo_x" in x:  # na luta: onde o lobo está
        lobo_x, chao = x["lobo_x"] * escala_mundo, CHAO * escala_mundo
    else:  # (seleção, VS...: do lado dele)
        lobo_x, chao = l.x - l.dir * 46 * l.s * (skin_lobo(l) or {}).get("tam", 1) ** 3, l.y
    lobo_pose = "montado" if montado(l) else x.get("lobo_pose", "parado")
    lobo_d = x.get("lobo_dir", l.dir) if not montado(l) else l.dir
    if l.extra.get("lobisomem", 0) > 0 and "lobo_x" in x:  # LUA CHEIA (2ª ultimate): o LOBISOMEM em pé
        import ult2
        wx, garra, lado = ult2.lobisomem_onde(l)
        resta = l.extra["lobisomem"]
        cresce = min(1.0, (ult2.TEMPO_BUFF - resta) / 12 + 0.4) * min(1.0, resta / 20 + 0.3)
        ult2.desenha_lobisomem(tela, wx * escala_mundo, chao, l.s, lado or l.dir, l.t, garra, cresce)
    elif l.extra.get("lobo_some"):
        pass  # (provocação BUSCA, GAROTO!: o lobo saiu correndo atrás do graveto)
    elif not montado(l):
        desenha_lobo(tela, lobo_x, chao, esc, lobo_d, lobo_pose, l.t, cor_lobo(l), skin_lobo(l))
    else:
        desenha_lobo(tela, l.x, l.y, esc, l.dir, "corre", l.t * 2, cor_lobo(l), skin_lobo(l))
    guarda_y = l.y
    if montado(l):  # sentado em cima do lobo
        l.y -= 6 * l.s

    def P(k):
        return l.ponto(p, k)

    def perna(pe, joelho, var):
        q, j, e = P("qd"), P(joelho), P(pe)
        CANELA.desenhar(tela, j, e, esc, espelho, var)
        fr, _ = frente_do_pe(j, e, d)
        BOTA.desenhar(tela, e, mais(e, fr, 9), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    def braco(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)

    try:
        zeus = l.f.get("estilo") == "zeus"
        if not zeus:
            mochila(tela, l, p, esc, branco)
        braco("ct", "mt", longe_v)
        perna("pt", "jt", longe_v)
        c, cb = P("pc"), P("cb")
        TRONCO.desenhar(tela, P("qd"), c, esc, espelho, perto_v)
        perna("pf", "jf", perto_v)
        u, _ = cabeca_eixos(c, cb, d)
        pygame.draw.line(tela, PALETA["k"], c, mais(cb, u, -3 * esc), max(3, int(5 * esc)))
        pygame.draw.line(tela, PALETA["P"] if not branco else (240, 240, 240), c, mais(cb, u, -3 * esc),
                         max(1, int(3 * esc)))
        na_cabeca = CABECA.desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
        if zeus and not branco:
            cabeca_zeus(tela, na_cabeca, esc)
        if not zeus:
            colar_e_pintura(tela, l, p, na_cabeca, esc, branco)
            pele_de_lobo(tela, l, p, esc, branco, d)
        braco("cf", "mf", perto_v)
    finally:
        l.y = guarda_y


def cabeca_zeus(tela, P, esc):
    """ZEUS (roupa do Tamer, código FENRIR): o cabelão branco cobrindo o chapéu e a barba comprida."""
    borda, branco_, sombra, ouro, folha = (40, 40, 52), (246, 246, 250), (206, 208, 220), (226, 186, 60), (250, 214, 90)
    cabelo = [P(-0.4, 9.6), P(-1.2, 5), P(0, 1.6), P(3, -0.2), P(7, -0.6), P(10.4, 0.6), P(12.2, 2.6), P(11, 3.6),
              P(8.6, 3), P(5.4, 3.4), P(3.4, 4.2), P(2.6, 7.4), P(1.6, 10.4)]  # (cai pra trás até o pescoço)
    pygame.draw.polygon(tela, borda, cabelo)
    pygame.draw.polygon(tela, borda, cabelo, max(2, int(esc * 1.1)))
    pygame.draw.polygon(tela, branco_, cabelo)
    for x0 in (1.5, 4, 6.5, 9):  # os fios
        pygame.draw.line(tela, sombra, P(x0, 0.4), P(x0 - 1, 3.2), max(1, int(esc * 0.5)))
    barba = [P(3.2, 7.4), P(10.6, 7.4), P(10.4, 10.4), P(8.6, 14.6), P(6.6, 16.2), P(4.6, 14.4), P(3.2, 10.6)]
    pygame.draw.polygon(tela, borda, barba)
    pygame.draw.polygon(tela, borda, barba, max(2, int(esc * 1.1)))
    pygame.draw.polygon(tela, branco_, barba)
    pygame.draw.line(tela, sombra, P(6.5, 9), P(6.5, 15), max(1, int(esc * 0.5)))


def raio_zeus(tela, mao, esc, t):
    """ZEUS: o raio dourado na mão."""
    x, y = mao
    s = esc * 0.9
    pts = [(x - 2 * s, y - 14 * s), (x + 3 * s, y - 14 * s), (x, y - 5 * s), (x + 4 * s, y - 5 * s),
           (x - 3 * s, y + 9 * s), (x - 0.5 * s, y), (x - 4 * s, y)]
    brilho(tela, (int(x), int(y - 3 * s)), int(5 * s), (255, 240, 150), 50 + int(30 * math.sin(t * 0.3)))
    pygame.draw.polygon(tela, (40, 30, 10), pts)
    pygame.draw.polygon(tela, (40, 30, 10), pts, max(2, int(esc * 0.8)))
    pygame.draw.polygon(tela, (255, 220, 70), pts)


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Tamer grande: o chapéu de explorador."""
    cb = P("cb")
    pygame.draw.ellipse(q, (150, 124, 78), (cb[0] - 14 * s, cb[1] - 10 * s, 28 * s, 7 * s))
    pygame.draw.rect(q, (190, 162, 108), (cb[0] - 8 * s, cb[1] - 16 * s, 16 * s, 8 * s))


def lobo_flash(l, tela):
    """Brilho quando o lobo troca de cor (ENTENDIMENTO MÚTUO)."""
    x = l.extra
    if x.get("lobo_flash", 0) > 0:
        x["lobo_flash"] -= 1
        k = 20 - x["lobo_flash"]
        cor = (240, 240, 255) if cor_lobo(l) == "branco" else (60, 60, 80)
        lx = x.get("lobo_x", l.x)
        pygame.draw.circle(tela, cor, (int(lx), int(l.y - 30 * l.s)), int((10 + k * 3) * l.s), 3)


# =====================================================================
# ENTRADA: chegam correndo os dois e o lobo uiva
# =====================================================================
def entrada(l, t, jogo):
    xf = l.extra["entrada_x"]
    x = l.extra
    if t < 40:
        k = suave(t / 40)
        l.x = xf - l.dir * 300 * (1 - k)
        x["lobo_x"] = l.x + l.dir * 40 * l.s
        x["lobo_pose"] = "corre"
        x["lobo_dir"] = l.dir
        l.sobrepor = {}
    elif t < 90:
        l.x = xf
        x["lobo_x"] = xf + l.dir * 40 * l.s
        x["lobo_pose"] = "uiva"
        if t == 44:
            som.tocar("uivo")
        l.sobrepor = dict(POSES_TAMER["t_carinho"]) if t < 80 else {}
    else:
        l.sobrepor = {}
    l.t += 1


# =====================================================================
# VITÓRIA: o lobo uiva e ele levanta o braço
# =====================================================================
def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES_TAMER["t_grito"] if t > 10 else POSES_TAMER["parado"])
    x = l.extra
    x["lobo_x"] = l.x + l.dir * 44 * l.s
    x["lobo_pose"] = "uiva"
    if t == 12:
        som.tocar("uivo")
