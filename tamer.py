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
from max10 import fumaca
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


def desenha_lobo(tela, x, chao, esc, d, pose, t, cor="branco", skin=None):
    """O lobo de lado. pose: parado, corre, morde, uiva, montado.
    skin: dict(olho=cor, tam=escala) da roupa (ZEUS: o lobo vira o FENRIR, maior e de olho vermelho)."""
    c1, c2, c3, olho = CORES_LOBO[cor]
    u = esc * 0.62
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
        joelho = P(base_x + bal * 0.5, 10)
        pe = P(base_x + bal, 0)
        pygame.draw.line(tela, cor, P(base_x, corpo_y - 6), joelho, max(2, int(5 * u)))
        pygame.draw.line(tela, cor, joelho, pe, max(2, int(4 * u)))
        pygame.draw.circle(tela, c3, (int(pe[0]), int(pe[1])), max(1, int(2.6 * u)))
    if pose != "uiva":
        cx, cy = P(0, corpo_y)
        w, h = 48 * u, 22 * u
        pygame.draw.ellipse(tela, c1, (cx - w / 2, cy - h / 2, w, h))
        pygame.draw.ellipse(tela, c2, (cx - w / 2 + 4 * u, cy, w - 8 * u, h / 2))  # barriga na sombra
    # rabo
    abana = math.sin(t * (0.5 if not corre else 0.25)) * 6
    rabo = [P(-22, corpo_y + 2), P(-34, corpo_y + 10 + abana * 0.5), P(-42, corpo_y + 6 + abana)]
    pygame.draw.lines(tela, c1, False, rabo, max(3, int(7 * u)))
    pygame.draw.circle(tela, c2, (int(rabo[-1][0]), int(rabo[-1][1])), max(2, int(3.5 * u)))
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
    alvo = l.x - l.dir * 46 * l.s
    dx = alvo - x["lobo_x"]
    x["lobo_x"] += dx * 0.18
    x["lobo_dir"] = l.dir
    x["lobo_pose"] = "corre" if abs(dx) > 6 else "parado"


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
                     "cinza", l.f.get("lobo"))


# =====================================================================
# Golpes
# =====================================================================
def _registra(nome, **g):
    g.setdefault("base", "parado")
    g.setdefault("pose", "parado")
    g.setdefault("caixa", None)
    g.setdefault("especial", True)
    g["total"] = g.get("total", g["ini"] + g["ativo"] + g.get("rec", 0))
    GOLPES[nome] = g


_registra("tamer_lobo", ini=E_SAI, ativo=E_FIM - E_SAI - 8, rec=8, janelas=((E_SAI + 2, E_FIM - 8),), dano=15, hit=18,
          defe=10, emp=4, nivel="medio", logica=lobo_avanca, ia="medio",
          quadros=[(0, "parado"), (4, "t_aponta"), (E_FIM - 10, "t_aponta"), (E_FIM, "parado")])
_registra("tamer_chute", ini=8, ativo=5, rec=20, caixa=(20, 40, 92, 104), dano=15, hit=24, defe=12, emp=3,
          nivel="medio", derruba=True, voo=(17, 1.5), parede=5, parede_sobe=True, ia="perto", som="vento",
          quadros=[(0, "parado"), (6, "t_chute"), (16, "t_chute"), (33, "parado")])
_registra("tamer_combo", ini=R_INI, ativo=R_HITS * R_INTERVALO, rec=12,
          janelas=tuple((R_INI + k * R_INTERVALO, R_INI + k * R_INTERVALO + 3) for k in range(R_HITS)),
          caixa=(10, 20, 92, 112), dano=3, hit=10, defe=7, emp=1, nivel="medio", logica=combo_dupla, ia="perto",
          quadros=combo_quadros())
_registra("tamer_galope", ini=S_MONTA, ativo=S_FIM - S_MONTA, rec=12, janelas=((S_MONTA + 2, S_FIM),),
          caixa=(0, 0, 80, 110), dano=10, hit=22, defe=12, emp=7, nivel="medio", derruba=True, voo=(8, 8),
          logica=galope, ia="medio", som="vento",
          quadros=[(0, "parado"), (S_MONTA - 2, "t_monta"), (S_FIM + 2, "t_monta"), (S_FIM + 12, "parado")])
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
}
S_REF = 1.36 / 3

TRONCO = Peca([
    "...kkkkkkkk...",
    "..kcCCcccsck..",
    ".kcCCccccsccv.",
    ".kcCkkkcsckcv.",
    ".kcCkvkcskvcv.",
    ".kcckkkskkkcv.",
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
    "..khHHHhhk....",
    "kkhhhhhhhhkkk.",
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
        lobo_x, chao = l.x - l.dir * 46 * l.s, l.y
    lobo_pose = "montado" if montado(l) else x.get("lobo_pose", "parado")
    lobo_d = x.get("lobo_dir", l.dir) if not montado(l) else l.dir
    if not montado(l):
        desenha_lobo(tela, lobo_x, chao, esc, lobo_d, lobo_pose, l.t, cor_lobo(l), l.f.get("lobo"))
    else:
        desenha_lobo(tela, l.x, l.y, esc, l.dir, "corre", l.t * 2, cor_lobo(l), l.f.get("lobo"))
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
        braco("ct", "mt", longe_v)
        perna("pt", "jt", longe_v)
        c, cb = P("pc"), P("cb")
        TRONCO.desenhar(tela, P("qd"), c, esc, espelho, perto_v)
        perna("pf", "jf", perto_v)
        u, _ = cabeca_eixos(c, cb, d)
        pygame.draw.line(tela, PALETA["k"], c, mais(cb, u, -3 * esc), max(3, int(5 * esc)))
        pygame.draw.line(tela, PALETA["P"] if not branco else (240, 240, 240), c, mais(cb, u, -3 * esc),
                         max(1, int(3 * esc)))
        CABECA.desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
        braco("cf", "mf", perto_v)
    finally:
        l.y = guarda_y


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
