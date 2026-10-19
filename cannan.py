"""CANNAN: o soldado do canhão (criado pelo Gomes).

Aparência: soldado de guerra com um canhão no braço (tipo Armarouge/Mega Man), cicatrizes, coletão preto,
cabelo meio longo (que balança!). Chega voando com o canhão e desce bala no chão pra aterrissar.
  E      pistola da cintura: 3 tiros de 5
  Q      coronhada (5) + soco pra cima com o canhão (15, joga pra cima)
  R      canhão pra frente: 7 mini explosões de perto (2 cada, a última 6)
  SHIFT  corre que nem um doido (10)
  Z      ULTIMATE: pistola + canhão atirando que nem maluco: 20 tiros de 2 e fica 5s sem agir.
         Segurando o Z por 5 segundos: 50 de dano, mas fica 7s sem agir.
  Passiva: COLETE À PROVA DE BALAS — 50% menos dano de ataques de média e longa distância
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from corpo import cabeca_eixos, eixos, frente_do_pe, mais
from golpes import GOLPES, misturar, proporcionar, suave
from lutador import Projetil
from max10 import brilho, fogo, fumaca
from pecas import Peca

POSES_CANNAN = {
    "parado": dict(pt=(-24, 0), jt=(-14, 26), pf=(22, 0), jf=(26, 28), qd=(0, 50), pc=(4, 86), cb=(8, 104),
                   ct=(-8, 68), mt=(-6, 56), cf=(20, 78), mf=(42, 82)),
    "andar1": dict(pt=(-26, 2), jt=(-14, 26), pf=(26, 0), jf=(28, 28), qd=(0, 48), pc=(4, 84), cb=(8, 102),
                   ct=(-10, 66), mt=(-4, 54), cf=(20, 76), mf=(42, 80)),
    "andar2": dict(pt=(4, 10), jt=(14, 30), pf=(2, 0), jf=(10, 28), qd=(0, 52), pc=(4, 88), cb=(8, 106),
                   ct=(-8, 70), mt=(-8, 58), cf=(20, 80), mf=(42, 84)),
    "andar3": dict(pt=(24, 0), jt=(28, 28), pf=(-24, 2), jf=(-12, 26), qd=(0, 48), pc=(4, 84), cb=(8, 102),
                   ct=(-6, 66), mt=(-10, 54), cf=(20, 76), mf=(42, 80)),
    "andar4": dict(pt=(2, 0), jt=(10, 28), pf=(4, 10), jf=(14, 30), qd=(0, 52), pc=(4, 88), cb=(8, 106),
                   ct=(-8, 70), mt=(-8, 58), cf=(20, 80), mf=(42, 84)),
    "c_pistola": dict(pt=(-26, 0), jt=(-16, 26), pf=(24, 0), jf=(26, 28), qd=(0, 50), pc=(8, 86), cb=(12, 104),
                      ct=(20, 88), mt=(46, 90), cf=(6, 72), mf=(14, 54)),
    "c_coronhada": dict(pt=(-26, 0), jt=(-16, 26), pf=(26, 0), jf=(28, 28), qd=(2, 48), pc=(14, 82), cb=(20, 98),
                        ct=(24, 92), mt=(44, 78), cf=(4, 70), mf=(10, 52)),
    "c_upper": dict(pt=(-14, 4), jt=(-8, 30), pf=(12, 0), jf=(14, 28), qd=(0, 56), pc=(8, 92), cb=(14, 108),
                    ct=(-8, 76), mt=(-2, 62), cf=(18, 112), mf=(24, 140)),
    "c_canhao": dict(pt=(-32, 0), jt=(-22, 26), pf=(26, 0), jf=(30, 28), qd=(-4, 48), pc=(6, 82), cb=(10, 100),
                     ct=(16, 74), mt=(28, 76), cf=(30, 82), mf=(56, 84)),
    "c_corre1": dict(pt=(-34, 14), jt=(-18, 30), pf=(30, 0), jf=(28, 30), qd=(0, 48), pc=(20, 80), cb=(28, 96),
                     ct=(4, 76), mt=(-18, 90), cf=(30, 70), mf=(44, 84)),
    "c_corre2": dict(pt=(30, 0), jt=(28, 30), pf=(-34, 14), jf=(-18, 30), qd=(0, 48), pc=(20, 80), cb=(28, 96),
                     ct=(30, 70), mt=(44, 84), cf=(4, 76), mf=(-18, 90)),
    "c_ult": dict(pt=(-34, 0), jt=(-24, 26), pf=(28, 0), jf=(32, 28), qd=(-4, 48), pc=(6, 82), cb=(10, 100),
                  ct=(22, 86), mt=(48, 90), cf=(26, 80), mf=(54, 80)),
    "c_cansado": dict(pt=(-22, 0), jt=(-8, 22), pf=(20, 0), jf=(30, 24), qd=(0, 38), pc=(14, 66), cb=(22, 78),
                      ct=(6, 46), mt=(14, 30), cf=(22, 40), mf=(32, 16)),
    "c_voa": dict(pt=(-8, 6), jt=(-6, 32), pf=(8, 0), jf=(8, 30), qd=(0, 56), pc=(2, 92), cb=(6, 110),
                  ct=(-14, 80), mt=(-22, 96), cf=(10, 70), mf=(14, 44)),
    "c_continencia": dict(pt=(-18, 0), jt=(-14, 28), pf=(18, 0), jf=(16, 28), qd=(0, 56), pc=(2, 92), cb=(4, 110),
                          ct=(14, 98), mt=(10, 110), cf=(12, 76), mf=(10, 52)),
}
proporcionar(POSES_CANNAN)


# =====================================================================
# Ajudas: boca do canhão, mão da pistola, tiros
# =====================================================================
def boca_canhao(l):
    p = l.pose_vista or l.pose_atual()
    c, m = l.ponto(p, "cf"), l.ponto(p, "mf")
    (dx, dy), _ = eixos(c, m)
    return (m[0] + dx * 10 * l.s, m[1] + dy * 10 * l.s), math.atan2(dy, dx)


def mao_pistola(l):
    p = l.pose_vista or l.pose_atual()
    c, m = l.ponto(p, "ct"), l.ponto(p, "mt")
    (dx, dy), _ = eixos(c, m)
    return (m[0] + dx * 8 * l.s, m[1] + dy * 8 * l.s), math.atan2(dy, dx)


def desenha_bala(p, tela):
    pygame.draw.line(tela, (255, 230, 140), (p.x - p.vx * 1.5, p.y), (p.x, p.y), 4)
    pygame.draw.circle(tela, (255, 250, 220), (int(p.x), int(p.y)), 3)


def desenha_bala_canhao(p, tela):
    brilho(tela, (int(p.x), int(p.y)), 12, (120, 220, 255), 150)
    pygame.draw.circle(tela, (220, 245, 255), (int(p.x), int(p.y)), 5)


def atira(l, jogo, golpe, de_onde="pistola", espalha=0.0):
    (x, y), _ = mao_pistola(l) if de_onde == "pistola" else boca_canhao(l)
    b = Projetil(l, x, y + random.uniform(-espalha, espalha), l.dir, GOLPES[golpe])
    jogo.projeteis.append(b)
    brilho_tiro = (x, y)
    jogo.faiscas.append([brilho_tiro[0], brilho_tiro[1], l.dir * 2, 0, 6, (255, 230, 150), 6])
    som.tocar("tiro", 0.6)


# =====================================================================
# E: PISTOLA (3 tiros)
# =====================================================================
def pistola(l, outro, jogo):
    l.vx = 0
    l.fisica(jogo)
    if l.t in (10, 17, 24):
        atira(l, jogo, "cannan_bala")
    if l.t >= 38:
        return "fim"


# =====================================================================
# Q: CORONHADA + SOCO PRA CIMA COM O CANHÃO
# =====================================================================
def coronhada(l, outro, jogo):
    t = l.t
    l.memo["g_hit"] = GOLPES["cannan_coronhada"] if t < 13 else GOLPES["cannan_upper"]
    l.memo["caixa"] = (10, 60, 70, 110) if t < 13 else (0, 70, 56, 170)
    l.vx = 2 * l.dir if t < 18 else 0
    l.fisica(jogo)
    if t >= 40:
        return "fim"


# =====================================================================
# R: 7 MINI EXPLOSÕES DE PERTO
# =====================================================================
R_INI, R_INTERVALO, R_TIROS = 10, 7, 7


def canhao_perto(l, outro, jogo):
    t = l.t
    k = t - R_INI
    if 0 <= k < R_TIROS * R_INTERVALO and k % R_INTERVALO == 0:
        (x, y), _ = boca_canhao(l)
        for _ in range(8):  # mini explosão na boca do canhão
            a = random.uniform(0, math.tau)
            jogo.faiscas.append([x + l.dir * 20, y, math.cos(a) * 3 + l.dir * 3, math.sin(a) * 3, 12,
                                 random.choice(((255, 200, 90), (255, 130, 50), (120, 220, 255))), 7])
        som.tocar("explosao", 0.35)
        jogo.tremer(3)
        ultimo = k // R_INTERVALO == R_TIROS - 1
        l.memo["g_hit"] = GOLPES["cannan_explosao_final"] if ultimo else GOLPES["cannan_explosao"]
    l.vx = -0.5 * l.dir if R_INI <= t < R_INI + R_TIROS * R_INTERVALO else 0  # o coice empurra pra trás
    l.fisica(jogo)
    if t >= R_INI + R_TIROS * R_INTERVALO + 14:
        return "fim"


# =====================================================================
# SHIFT: CORRE QUE NEM UM DOIDO
# =====================================================================
def corre_doido(l, outro, jogo):
    t = l.t
    m = l.memo
    if l.acertou and "bateu" not in m:
        m["bateu"] = t
    if "bateu" in m or t >= 46:
        l.vx *= 0.7
        m["caixa"] = None
        l.fisica(jogo)
        if t - m.get("bateu", 46) > 16:
            return "fim"
        return
    if t < 6:
        l.vx = 0
    else:
        l.vx = 10.5 * l.dir
        m["caixa"] = (0, 20, 56, 120)
        if t % 3 == 0:
            fumaca(jogo, l.x - 20 * l.dir, CHAO - 4, 1, (170, 150, 130), 1, -0.3)
    l.fisica(jogo)


def corre_quadros():
    q = [(0, "parado"), (5, "c_corre1")]
    for k in range(1, 14):
        q.append((5 + k * 3, "c_corre2" if k % 2 else "c_corre1"))
    q.append((70, "parado"))
    return q


# =====================================================================
# Z: ULTIMATE — atira que nem maluco (dá pra CARREGAR segurando o Z)
# =====================================================================
U_CARGA_MAX, U_TIROS, U_INTERVALO = 180, 20, 5  # (carga máxima em 3 segundos: pedido do Gomes, era 5)
U_CANSADO, U_CANSADO_FORTE = 300, 420  # 5 e 7 segundos sem agir


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    e = getattr(l, "entrada_atual", None)
    segurando = bool(e and getattr(e, "segura_ult", False))
    if "atirando" not in m:  # carregando enquanto segura o Z (até 3 segundos)
        m["carga"] = t
        l.vx = 0
        l.fisica(jogo)
        if t % 20 == 0 and t > 8:
            som.tocar("carga", 0.4)
        if not segurando or t >= U_CARGA_MAX:
            m["atirando"] = t
            m["forte"] = t >= U_CARGA_MAX
            if m["forte"]:
                som.tocar("ultimate")
                jogo.tremer(10)
        return
    k = t - m["atirando"] - 1  # o primeiro tiro sai logo no quadro seguinte
    if k < U_TIROS * U_INTERVALO:
        if k % U_INTERVALO == 0:
            golpe = "cannan_ult_forte" if m["forte"] else "cannan_ult"
            atira(l, jogo, golpe, "pistola" if (k // U_INTERVALO) % 2 == 0 else "canhao", espalha=10)
            jogo.tremer(3)
        l.vx = -0.4 * l.dir
        l.fisica(jogo)
        return
    # acabou: cansado (superaquecido) e sem agir por 5 ou 7 segundos
    l.mudar("tonto")
    l.tonto_tempo = U_CANSADO_FORTE if m.get("forte") else U_CANSADO
    l.superaquecido = True
    l.golpe = None


def ultimate_efeito(l, tela):
    m = l.memo
    if "atirando" not in m:  # o canhão brilhando cada vez mais enquanto carrega
        k = min(1.0, l.t / U_CARGA_MAX)
        (x, y), _ = boca_canhao(l)
        brilho(tela, (int(x), int(y)), int((10 + 40 * k) * l.s), (120, 220, 255), int(100 + 120 * k))
        if k >= 1 and (l.t // 4) % 2:
            brilho(tela, (int(x), int(y)), int(30 * l.s), (255, 255, 255), 200)


def cansado_efeito(l, tela):
    """Superaquecido: fumaça saindo do canhão."""
    (x, y), _ = boca_canhao(l)
    for i in range(3):
        k = ((l.t * 2 + i * 13) % 40) / 40
        pygame.draw.circle(tela, (150, 150, 150), (int(x + i * 4), int(y - k * 50 * l.s)), int((4 + k * 10) * l.s / 1.4))


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


_registra("cannan_bala", ini=0, ativo=1, rec=0, dano=5, hit=10, defe=8, emp=2, nivel="medio", proj=True, raio=5, vel=16,
          desenho_proj=desenha_bala)
_registra("cannan_pistola", ini=10, ativo=16, rec=12, dano=5, hit=10, defe=8, emp=2, nivel="medio", logica=pistola,
          ia="longe", quadros=[(0, "parado"), (8, "c_pistola"), (30, "c_pistola"), (38, "parado")])
_registra("cannan_coronhada", ini=6, ativo=4, rec=0, janelas=((6, 10), (14, 20)), dano=5, hit=18, defe=10, emp=1,
          nivel="medio", logica=coronhada, ia="perto", som="vento",
          quadros=[(0, "parado"), (5, "c_coronhada"), (11, "c_coronhada"), (14, "c_upper"), (24, "c_upper"),
                   (40, "parado")])
GOLPES["cannan_coronhada"]["total"] = 40
GOLPES["cannan_upper"] = dict(GOLPES["cannan_coronhada"], dano=15, lanca=16, emp=2)
_registra("cannan_canhao", ini=R_INI, ativo=R_TIROS * R_INTERVALO, rec=14,
          janelas=tuple((R_INI + k * R_INTERVALO, R_INI + k * R_INTERVALO + 3) for k in range(R_TIROS)),
          caixa=(18, 34, 116, 126), dano=2, hit=10, defe=7, emp=1, nivel="medio", logica=canhao_perto, ia="medio",
          quadros=[(0, "parado"), (R_INI - 2, "c_canhao"), (R_INI + R_TIROS * R_INTERVALO, "c_canhao"),
                   (R_INI + R_TIROS * R_INTERVALO + 14, "parado")])
GOLPES["cannan_explosao"] = GOLPES["cannan_canhao"]
GOLPES["cannan_explosao_final"] = dict(GOLPES["cannan_canhao"], dano=6, emp=7, hit=16)
_registra("cannan_corre", ini=6, ativo=40, rec=16, janelas=((6, 46),), caixa=(0, 20, 56, 120), dano=10, hit=18, defe=12,
          emp=8, nivel="medio", derruba=True, voo=(7, 8), logica=corre_doido, ia="medio", som="vento",
          quadros=corre_quadros())
_registra("cannan_ult", ini=0, ativo=1, rec=0, dano=2, hit=14, defe=8, emp=1, nivel="medio", proj=True, raio=6, vel=15,
          especial=True, ultimate=True, desenho_proj=desenha_bala_canhao, varios=True)
GOLPES["cannan_ult_forte"] = dict(GOLPES["cannan_ult"], dano=2.5)
_registra("cannan_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=ultimate, efeito=ultimate_efeito, ia="ultimate",
          quadros=[(0, "parado"), (8, "c_ult"), (999, "c_ult")])
GOLPES["cannan_ultimate"]["total"] = 9999

GOLPES_CANNAN = {"E": "cannan_pistola", "Q": "cannan_coronhada", "R": "cannan_canhao", "SHIFT": "cannan_corre",
                 "Z": "cannan_ultimate"}

# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  o O verde-oliva  x X colete preto  p P q pele  s cicatriz  h H cabelo  c C m canhão  g brilho  b bota
PALETA = {
    "k": (16, 16, 14), "o": (96, 104, 60), "O": (128, 136, 80), "x": (34, 34, 38), "X": (70, 70, 78),
    "p": (226, 178, 140), "P": (196, 146, 110), "q": (150, 104, 76), "s": (170, 80, 70),
    "h": (92, 60, 36), "H": (130, 90, 56), "c": (140, 150, 160), "C": (190, 200, 210), "m": (80, 88, 98),
    "g": (130, 220, 255), "b": (40, 32, 26), "e": (20, 20, 20),
    # remodel do Gomes: o CINTO DE MUNIÇÃO cruzado no peito (balas douradas)
    "y": (214, 172, 64), "Y": (250, 222, 130),
}
S_REF = 1.38 / 3

TRONCO = Peca([
    "...kkkkkkkk...",
    "..kxXXxxxYyk..",
    ".kxXXxkxYykxk.",
    ".kxXxxkYykxxk.",
    ".kxXxxYykpxxk.",
    ".kxXxYykxxxxk.",
    ".kXXYykkkXXxk.",
    ".kxYykxxkXXxk.",
    ".kYykkkkkoOkk.",
    "..ykxxxxkoOok.",
    "..kxXXkkkook..",
    "..kxXXkkXXxk..",
    "..kxxxxxxxxk..",
    "..kooooooooOk.",
    "..kbbbbbbbbbk.",
    "..koooooooook.",
    "..kOooooooook.",
    "..kOooooooook.",
    "..koooooooook.",
    "..koooooooook.",
    "..koooooooook.",
    "...kooooooook.",
    "....kkkkkkk...",
], PALETA, a=(7, 20), b=(7, 1))

TRONCO_COSTAS = Peca([
    "...kkkkkkkk...",
    "..kyYxxxxxxk..",
    ".kxyYxxxxxxxk.",
    ".kxXyYxxxxxxk.",
    ".kxXxyYxxxxxk.",
    ".kxxxxyYxxxxk.",
    ".kxXXxxyYXXxk.",
    ".kxXXxxxyYXxk.",
    ".kxxxxxxxyYxk.",
    "..kxxxxxxxxk..",
    "..kxxxxxxxxk..",
    "..kxxxxxxxxk..",
    "..kxxxxxxxxk..",
    "..kooooooooOk.",
    "..kbbbbbbbbbk.",
    "..koooooooook.",
    "..kOooooooook.",
    "..kOooooooook.",
    "..koooooooook.",
    "..koooooooook.",
    "..koooooooook.",
    "...kooooooook.",
    "....kkkkkkk...",
], PALETA, a=(7, 20), b=(7, 1))

CABECA = Peca([
    "...kkkkk....",
    "..khHHhhk...",
    ".khHhhhhhk..",
    "khhhhhhhhhk.",
    "khhkpppppkk.",
    "khkpppkepk..",
    "khkpspppppk.",
    ".kkppsppPpk.",
    "..kpppppppk.",
    "..kkppPppk..",
    "...kkpppk...",
    "....kkkk....",
], PALETA, a=(6, 6), b=(6, 0), estica=False)

CABECA_COSTAS = Peca([
    "...kkkkk....",
    "..khHHhhk...",
    ".khHhhhhhk..",
    "khhhhhhhhhk.",
    "khhhhhhhhhk.",
    "khhhhhhhhk..",
    "khhhhhhhhhk.",
    ".khhhhhhhhk.",
    "..khhhhhhk..",
    "..kkpppppk..",
    "...kkpppk...",
    "....kkkk....",
], PALETA, a=(6, 6), b=(6, 0), estica=False)

COXA = Peca([
    ".kkkkkk.",
    "koOooook",
    "kOooooqk",
    "kOooooqk",
    "kooooook",
    "kooooook",
    "koooooqk",
    "koooooqk",
    "kooooqqk",
    ".kooqqk.",
    ".kooqqk.",
    ".koqqqk.",
    "..kqqk..",
    "..kkkk..",
], PALETA, a=(3, 0), b=(3, 13))

CANELA = Peca([
    ".kkkkk.",
    "koOoook",
    "koooook",
    "koooook",
    "kooooqk",
    "kooooqk",
    "kooooqk",
    "kkkkkkk",
    "kbbbbbk",
    "kbXbbbk",
    "kbbbbbk",
    "kbbbbbk",
    ".kbbbk.",
    "..kkk..",
], PALETA, a=(3, 0), b=(3, 13))

BOTA = Peca([
    ".kkkkk.....",
    "kbXbbbkkkk.",
    "kbbbbbbbbbk",
    "kbbbbbbbbbk",
    "kkkkkkkkkkk",
], PALETA, a=(3, 1), b=(9, 1), estica=False)

BRACO = Peca([
    ".kkkk.",
    "kpPPqk",
    "kpPsqk",
    "kpPsqk",
    "kpPPqk",
    "kpPPqk",
    "kpsPqk",
    "kppsqk",
    "kpPPqk",
    "kpqqqk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 10))

ANTEBRACO = Peca([
    ".kkk.",
    "kpPqk",
    "kpPqk",
    "kpsqk",
    "kpPqk",
    "kpPqk",
    "kspqk",
    "kpPqk",
    "kpqqk",
    "kpqqk",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 10))

MAO = Peca([
    ".kkkk.",
    "kpPPqk",
    "kpPpqk",
    "kqqqqk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 4), estica=False)

TRONCO_LISO = Peca([
    "...kkkkkkkk...",
    "..kxXXxxxxxk..",
    ".kxXXxxkxxxxk.",
    ".kxXxxkpkxxxk.",
    ".kxXxxkpkxxxk.",
    ".kxxxxxkxxxxk.",
    ".kxXXkkkkXXxk.",
    ".kxXXkxxkXXxk.",
    ".kxxxkkkkxxxk.",
    "..kxxxxxxxxk..",
    "..kxXXkkXXxk..",
    "..kxXXkkXXxk..",
    "..kxxxxxxxxk..",
    "..kooooooooOk.",
    "..kbbbbbbbbbk.",
    "..koooooooook.",
    "..kOooooooook.",
    "..kOooooooook.",
    "..koooooooook.",
    "..koooooooook.",
    "..koooooooook.",
    "...kooooooook.",
    "....kkkkkkk...",
], PALETA, a=(7, 20), b=(7, 1))

TRONCO_COSTAS_LISO = Peca([
    "...kkkkkkkk...",
    "..kxXXxxxxxk..",
    ".kxXXxxxxxxxk.",
    ".kxXxxxxxxxxk.",
    ".kxXxxxxxxxxk.",
    ".kxxxxxxxxxxk.",
    ".kxXXxxxxXXxk.",
    ".kxXXxxxxXXxk.",
    ".kxxxxxxxxxxk.",
    "..kxxxxxxxxk..",
    "..kxxxxxxxxk..",
    "..kxxxxxxxxk..",
    "..kxxxxxxxxk..",
    "..kooooooooOk.",
    "..kbbbbbbbbbk.",
    "..koooooooook.",
    "..kOooooooook.",
    "..kOooooooook.",
    "..koooooooook.",
    "..koooooooook.",
    "..koooooooook.",
    "...kooooooook.",
    "....kkkkkkk...",
], PALETA, a=(7, 20), b=(7, 1))

CANHAO = Peca([
    "..kkkkkkk..",
    ".kmcCCCcmk.",
    "kmcCCCCCcmk",
    "kmcCgggCcmk",
    "kmcCCCCCcmk",
    "kmkkkkkkkmk",
    "kmcCCCCCcmk",
    "kmcgCCCgcmk",
    "kmcCCCCCcmk",
    "kmkkkkkkkmk",
    "kmcCCCCCcmk",
    "kmcCgggCcmk",
    "kmmmmmmmmmk",
    "kkmkmkmkmkk",
    "kkgggggggkk",
    ".kkgggggkk.",
    "..kkkkkkk..",
], PALETA, a=(5, 0), b=(5, 15))


def _cabelo(l, tela, cb, u, f, esc, branco):
    """O cabelo meio longo balançando (vai pra trás quando corre e sobe quando cai)."""
    vel = max(-1.5, min(1.5, l.vx / 5))
    for i in range(5):
        base = mais(mais(cb, u, (4 - i * 1.5) * esc), f, -3 * esc)
        pts = [base]
        for k in range(1, 6):
            onda = math.sin(l.t * 0.12 + i * 0.9 + k * 0.6) * k * 0.4 * esc
            atras = (1.2 + abs(vel) * 0.8) * k * esc
            cai = (1.6 - abs(vel) * 0.6 + (l.vy / 12 if l.vy < 0 else 0)) * k * esc
            pts.append((base[0] - f[0] * atras + onda, base[1] + cai + f[1] * atras))
        cor = (240, 240, 240) if branco else PALETA["h"]
        pygame.draw.lines(tela, PALETA["k"], False, pts, max(2, int(3 * esc)))
        pygame.draw.lines(tela, cor, False, pts, max(1, int(1.6 * esc)))


def _pistola(tela, mao, ang, esc):
    c, s = math.cos(ang), math.sin(ang)
    fim = (mao[0] + c * 7 * esc, mao[1] + s * 7 * esc)
    pygame.draw.line(tela, PALETA["k"], mao, fim, max(3, int(4 * esc)))
    pygame.draw.line(tela, (110, 110, 118), mao, fim, max(1, int(2 * esc)))


def _armadura(peca):
    """A mesma peça, mas com a pele virando armadura (braços da MEGA-CANNON)."""
    mapa = [linha.translate(str.maketrans({"p": "X", "P": "x", "q": "x", "s": "x"})) for linha in peca.mapa]
    return Peca(mapa, PALETA, a=(peca.a[0] - 0.5, peca.a[1] - 0.5), b=(peca.b[0] - 0.5, peca.b[1] - 0.5),
                estica=peca.estica)


BRACO_MEGA, ANTEBRACO_MEGA, MAO_MEGA = _armadura(BRACO), _armadura(ANTEBRACO), _armadura(MAO)


def mega(l):
    """A roupa MEGA-CANNON (código): armadura azul lisa, CAPACETE e o canhão de ponta redonda."""
    return l.f.get("roupa") == "megacannon"


def capacete(tela, P, esc, branco):
    """O CAPACETE da MEGA-CANNON: cúpula azul, faixa clara no meio e o disco redondo na orelha."""
    import pecas
    troca_ = pecas.TROCA or {}
    k = (150, 150, 160) if branco else PALETA["k"]
    azul = (245, 245, 250) if branco else troca_.get("x", PALETA["x"])
    claro = (245, 245, 250) if branco else troca_.get("X", PALETA["X"])
    brilho_ = (245, 245, 250) if branco else troca_.get("C", PALETA["C"])
    cupula = [P(-0.6, 5.6), P(-0.4, 2.6), P(1.6, 0.4), P(5, -0.6), P(8.4, 0.2), P(10.4, 2.2), P(10.8, 4.6),
              P(9.6, 4.6), P(8.6, 5.2), P(2.6, 5.4), P(1.6, 8.4), P(-0.2, 8.6)]
    pygame.draw.polygon(tela, k, cupula)
    pygame.draw.polygon(tela, azul, [(x * 0.86 + P(5, 4)[0] * 0.14, y * 0.86 + P(5, 4)[1] * 0.14) for x, y in cupula])
    faixa = [P(3.6, -0.2), P(6.4, -0.4), P(6.6, 4.6), P(3.8, 4.8)]
    pygame.draw.polygon(tela, claro, faixa)
    pygame.draw.line(tela, brilho_, P(4.6, 0.2), P(4.8, 3.6), max(1, int(0.8 * esc)))
    orelha = P(1.4, 6.2)
    r = max(2, int(2.0 * esc))
    pygame.draw.circle(tela, k, (round(orelha[0]), round(orelha[1])), r + max(1, int(0.6 * esc)))
    pygame.draw.circle(tela, claro, (round(orelha[0]), round(orelha[1])), r)
    pygame.draw.circle(tela, brilho_, (round(orelha[0] - 0.5 * esc), round(orelha[1] - 0.5 * esc)), max(1, r // 2))


def ponta_buster(tela, no_canhao, esc, branco):
    """A ponta REDONDA do canhão da MEGA-CANNON (com o brilho carregando)."""
    import pecas
    k = (150, 150, 160) if branco else PALETA["k"]
    luz = (245, 245, 250) if branco else (pecas.TROCA or {}).get("g", PALETA["g"])
    x, y = no_canhao(5.5, 15.5)
    r = max(3, int(4.6 * esc))
    pygame.draw.circle(tela, k, (round(x), round(y)), r + max(1, int(0.8 * esc)))
    pygame.draw.circle(tela, (245, 245, 250) if branco else (pecas.TROCA or {}).get("c", PALETA["c"]), (round(x), round(y)), r)
    pygame.draw.circle(tela, k, (round(x), round(y)), max(2, r - int(1.4 * esc)))
    pygame.draw.circle(tela, luz, (round(x), round(y)), max(1, r - int(2.2 * esc)))


def desenhar_cannan(l, tela, p, branco):
    esc = l.s / S_REF
    eh_mega = mega(l)
    d = l.lado()
    espelho = d < 0
    perto_v = "branco" if branco else "normal"
    longe_v = "branco" if branco else "escuro"
    costas = l.vira

    def P(k):
        return l.ponto(p, k)

    def perna(pe, joelho, var):
        q, j, e = P("qd"), P(joelho), P(pe)
        CANELA.desenhar(tela, j, e, esc, espelho, var)
        fr, _ = frente_do_pe(j, e, d)
        BOTA.desenhar(tela, e, mais(e, fr, 9), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    BRACO_, ANTEBRACO_, MAO_ = (BRACO_MEGA, ANTEBRACO_MEGA, MAO_MEGA) if eh_mega else (BRACO, ANTEBRACO, MAO)

    def braco_pistola(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        ANTEBRACO_.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO_.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        BRACO_.desenhar(tela, o, c, esc, espelho, var)
        arma = l.estado == "ataque" and l.nome_golpe in ("cannan_pistola", "cannan_coronhada", "cannan_ultimate")
        if arma:
            _pistola(tela, mais(m, dm, 3), math.atan2(dm[1], dm[0]), esc)

    def braco_canhao(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        BRACO_.desenhar(tela, o, c, esc, espelho, var)
        dm, _ = eixos(c, m)
        no_canhao = CANHAO.desenhar(tela, mais(c, dm, -2), mais(m, dm, 8), esc, espelho, var)
        if eh_mega:
            ponta_buster(tela, no_canhao, esc, branco)
        if not branco and (l.t // 12) % 3 == 0:  # (as luzinhas piscando: o canhão high-tech está ligado)
            import pecas
            luz = (pecas.TROCA or {}).get("g", PALETA["g"])
            for yy in (3.5, 7.5, 11.5):
                x, y = no_canhao(5.5, yy)
                pygame.draw.circle(tela, (255, 255, 255), (round(x), round(y)), max(1, int(0.9 * esc)))
                pygame.draw.circle(tela, luz, (round(x), round(y)), max(2, int(1.6 * esc)), 1)

    # braço da frente = canhão; braço de trás = pistola (troca quando está de costas)
    if costas:
        braco_canhao("cf", "mf", longe_v)
    else:
        braco_pistola("ct", "mt", longe_v)
    perna("pf" if costas else "pt", "jf" if costas else "jt", longe_v)
    c, cb = P("pc"), P("cb")
    u, f = cabeca_eixos(c, cb, d)
    if not eh_mega:  # (na MEGA-CANNON o cabelo fica dentro do capacete)
        _cabelo(l, tela, cb, u, f, esc, branco)
    tronco = (TRONCO_COSTAS_LISO if costas else TRONCO_LISO) if eh_mega else (TRONCO_COSTAS if costas else TRONCO)
    tronco.desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    perna("pt" if costas else "pf", "jt" if costas else "jf", perto_v)
    pygame.draw.line(tela, PALETA["k"], c, mais(cb, u, -3 * esc), max(3, int(5 * esc)))
    pygame.draw.line(tela, PALETA["P"] if not branco else (240, 240, 240), c, mais(cb, u, -3 * esc), max(1, int(3 * esc)))
    na_cabeca = (CABECA_COSTAS if costas else CABECA).desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    if eh_mega:
        capacete(tela, na_cabeca, esc, branco)
    if costas:
        braco_pistola("ct", "mt", perto_v)
    else:
        braco_canhao("cf", "mf", perto_v)
    if not costas and not eh_mega:  # 2 GRANADAS penduradas no cinto (colete tático do remodel)
        granadas(l, tela, p, esc, branco)


def granadas(l, tela, p, esc, branco):
    import pecas
    troca = pecas.TROCA or {}
    k = (150, 150, 160) if branco else PALETA["k"]
    cor = (245, 245, 250) if branco else troca.get("O", PALETA["O"])
    escura = (245, 245, 250) if branco else troca.get("o", PALETA["o"])
    qd, pc = p["qd"], p["pc"]
    for j, dx in enumerate((5, 10)):
        u = (qd[0] + dx, qd[1] + (pc[1] - qd[1]) * 0.12 + 2)
        x, y = l.ponto({"_": u}, "_")
        r = max(2, int(2.2 * esc))
        pygame.draw.circle(tela, k, (round(x), round(y)), r + max(1, int(0.7 * esc)))
        pygame.draw.circle(tela, escura, (round(x), round(y)), r)
        pygame.draw.circle(tela, cor, (round(x - 0.6 * esc), round(y - 0.6 * esc)), max(1, r // 2))
        pygame.draw.line(tela, k, (x - r, y), (x + r, y), 1)  # o gomo da granada
        pino = (x + 0.4 * esc, y - r - 1.2 * esc)
        pygame.draw.circle(tela, (200, 200, 210), (round(pino[0]), round(pino[1])), max(1, int(0.9 * esc)), 1)


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Cannan grande: o canhão no braço e o cabelo."""
    from corpo import membro
    c, m = P("cf"), P("mf")
    membro(q, [(c, 6 * s), ((m[0] + (m[0] - c[0]) * 0.3, m[1] + (m[1] - c[1]) * 0.3), 6.5 * s)], (150, 160, 170), cont,
           borda=2.5, brilho=0.4, sombra=0.4)
    cb = P("cb")
    for i in range(4):
        pygame.draw.line(q, (92, 60, 36), (cb[0] - 4 * s * d, cb[1] - 6 * s + i * 3 * s),
                         (cb[0] - (14 + i * 2) * s * d, cb[1] + (2 + i * 4) * s), max(2, int(2 * s)))


# =====================================================================
# ENTRADA: chega voando com o canhão e desce bala no chão pra pousar
# =====================================================================
def entrada(l, t, jogo):
    xf = l.extra["entrada_x"]
    if t < 64:
        k = suave(t / 64)
        l.x = xf
        l.y = -120 + (CHAO + 120) * k
        l.sobrepor = dict(POSES_CANNAN["c_voa"])
        (bx, by), _ = boca_canhao(l)
        fogo(jogo, bx, by, 0.8)
        if t % 4 == 0 and t > 10:  # bala no chão
            alvo = xf + random.uniform(-60, 60)
            jogo.faiscas.append([alvo, CHAO - 6, 0, -2, 14, (255, 220, 140), 6])
            fumaca(jogo, alvo, CHAO - 4, 2, (170, 150, 130), 3, -1.5)
            som.tocar("tiro", 0.4)
    elif t == 64:
        l.y = CHAO
        l.sobrepor = dict(POSES_CANNAN["c_cansado"])
        som.tocar("queda")
        jogo.tremer(10)
        fumaca(jogo, l.x, CHAO - 4, 16, (170, 150, 130), 6, -1.5)
    elif t < 96:
        l.sobrepor = misturar(POSES_CANNAN["c_cansado"], POSES_CANNAN["parado"], suave((t - 70) / 26)) if t >= 70 \
            else dict(POSES_CANNAN["c_cansado"])
    else:
        l.sobrepor = {}
    l.t += 1


def entrada_efeito(l, tela, t):
    if t < 64 and t > 10 and t % 4 < 2:  # rajada saindo do canhão pra baixo
        (bx, by), _ = boca_canhao(l)
        pygame.draw.line(tela, (255, 230, 150), (bx, by), (bx + random.uniform(-40, 40), CHAO), 3)


# =====================================================================
# VITÓRIA: dá um tiro de canhão pro alto e bate continência
# =====================================================================
def vitoria(l, t, jogo):
    if t < 30:
        l.sobrepor = dict(POSES_CANNAN["c_upper"])
        if t == 10:
            (bx, by), _ = boca_canhao(l)
            som.tocar("explosao", 0.6)
            for _ in range(14):
                a = random.uniform(-2.4, -0.7)
                jogo.faiscas.append([bx, by, math.cos(a) * 6, math.sin(a) * 6, 20, (130, 220, 255), 6])
    else:
        l.sobrepor = dict(POSES_CANNAN["c_continencia"])
