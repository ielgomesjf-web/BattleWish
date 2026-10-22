"""KING RIP: o tio-avô mestre do nunchaku (criado pelo Gomes).

Aparência: tio-avô com nunchaku, uniforme azul de treino, faixa preta na cintura, cabelo tipo o do Paragus
(Dragon Ball Super: Broly). Entrada tipo o Batman: joga a capa pra trás e tira ela.
  E      nunchaku BUMERANGUE (5 de dano na ida e 5 na volta)
  Q      CHUTE ACROBÁTICO: meia estrelinha esticando a perna (15, joga pra cima)
  R      NUNCHAKU GIRATÓRIO: 10 hits de 2
  SHIFT  finca o nunchaku na terra e sai girando dando estrelinha
  Z      ULTIMATE: joga o nunchaku pra cima e faz um monte de acrobacia batendo, depois arremessa pro outro lado
  Passiva: MAESTRIA DE COMBATE — combos mais longos (18 golpes em vez de 12)
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from corpo import cabeca_eixos, eixos, frente_do_pe, mais
from golpes import GOLPES, misturar, proporcionar, suave
from lutador import Projetil
from max10 import brilho, fumaca
from pecas import Peca

# =====================================================================
# Poses (postura de kung fu)
# =====================================================================
POSES_KING = {
    "parado": dict(pt=(-24, 0), jt=(-14, 26), pf=(22, 0), jf=(26, 28), qd=(0, 50), pc=(4, 86), cb=(8, 104),
                   ct=(-8, 70), mt=(-2, 84), cf=(22, 74), mf=(34, 88)),
    "andar1": dict(pt=(-26, 2), jt=(-14, 26), pf=(26, 0), jf=(28, 28), qd=(0, 48), pc=(4, 84), cb=(8, 102),
                   ct=(-8, 68), mt=(-2, 82), cf=(22, 72), mf=(34, 86)),
    "andar2": dict(pt=(4, 10), jt=(14, 30), pf=(2, 0), jf=(10, 28), qd=(0, 52), pc=(4, 88), cb=(8, 106),
                   ct=(-8, 72), mt=(-2, 86), cf=(22, 76), mf=(34, 90)),
    "andar3": dict(pt=(24, 0), jt=(28, 28), pf=(-24, 2), jf=(-12, 26), qd=(0, 48), pc=(4, 84), cb=(8, 102),
                   ct=(-8, 68), mt=(-2, 82), cf=(22, 72), mf=(34, 86)),
    "andar4": dict(pt=(2, 0), jt=(10, 28), pf=(4, 10), jf=(14, 30), qd=(0, 52), pc=(4, 88), cb=(8, 106),
                   ct=(-8, 72), mt=(-2, 86), cf=(22, 76), mf=(34, 90)),
    "k_arremesso": dict(pt=(-28, 0), jt=(-18, 26), pf=(26, 0), jf=(28, 28), qd=(2, 48), pc=(12, 84), cb=(18, 100),
                        ct=(-12, 74), mt=(-24, 80), cf=(34, 88), mf=(60, 92)),
    "k_estrela": dict(pt=(-34, 2), jt=(-18, 28), pf=(34, 2), jf=(18, 28), qd=(0, 54), pc=(0, 90), cb=(0, 108),
                      ct=(-18, 100), mt=(-34, 116), cf=(18, 100), mf=(34, 116)),
    "k_chute_alto": dict(pt=(-10, 0), jt=(-6, 28), pf=(58, 110), jf=(32, 84), qd=(0, 56), pc=(-20, 84), cb=(-26, 100),
                         ct=(-30, 66), mt=(-40, 48), cf=(-20, 66), mf=(-28, 46)),
    "k_gira": dict(pt=(-30, 0), jt=(-20, 26), pf=(26, 0), jf=(30, 28), qd=(0, 48), pc=(8, 84), cb=(12, 100),
                   ct=(-8, 72), mt=(2, 80), cf=(28, 88), mf=(42, 94)),
    "k_planta": dict(pt=(-24, 0), jt=(-6, 18), pf=(22, 0), jf=(32, 20), qd=(0, 34), pc=(20, 60), cb=(30, 72),
                     ct=(10, 46), mt=(18, 32), cf=(36, 34), mf=(48, 6)),
    "k_capa": dict(pt=(-18, 0), jt=(-14, 28), pf=(18, 0), jf=(16, 28), qd=(0, 56), pc=(2, 92), cb=(4, 110),
                   ct=(12, 80), mt=(-4, 88), cf=(14, 78), mf=(0, 86)),
    "k_joga_capa": dict(pt=(-22, 0), jt=(-18, 28), pf=(20, 0), jf=(18, 28), qd=(0, 56), pc=(4, 92), cb=(8, 110),
                        ct=(-20, 92), mt=(-38, 104), cf=(-14, 94), mf=(-30, 108)),
    "k_cotovelo": dict(pt=(-26, 0), jt=(-16, 26), pf=(26, 0), jf=(28, 28), qd=(2, 50), pc=(14, 86), cb=(20, 102),
                       ct=(-6, 74), mt=(4, 84), cf=(36, 92), mf=(16, 98)),
    "k_costas": dict(pt=(-22, 0), jt=(-16, 26), pf=(22, 0), jf=(24, 28), qd=(0, 52), pc=(2, 88), cb=(6, 106),
                     ct=(-14, 72), mt=(-4, 62), cf=(-10, 74), mf=(-2, 64)),
    "k_bastao": dict(pt=(-24, 0), jt=(-16, 26), pf=(24, 0), jf=(26, 28), qd=(0, 52), pc=(4, 88), cb=(8, 106),
                     ct=(-10, 74), mt=(-2, 86), cf=(16, 108), mf=(22, 128)),
    "k_arremessa": dict(pt=(-28, 0), jt=(-20, 26), pf=(24, 0), jf=(28, 28), qd=(-2, 50), pc=(-6, 86), cb=(-10, 104),
                        ct=(-16, 100), mt=(-26, 118), cf=(-10, 102), mf=(-18, 122)),
    # (o corpo balançando junto com o nunchaku no R — pedido do Gomes: mais fluido)
    "k_gira2": dict(pt=(-30, 0), jt=(-20, 26), pf=(26, 0), jf=(30, 28), qd=(0, 48), pc=(6, 86), cb=(10, 102),
                    ct=(-8, 72), mt=(2, 80), cf=(24, 80), mf=(40, 74)),
}
proporcionar(POSES_KING)


# =====================================================================
# O nunchaku (desenhado na mão, de verdade)
# =====================================================================
MADEIRA, MADEIRA_ESC, CORRENTE, CONT = (176, 116, 58), (110, 66, 30), (170, 172, 180), (18, 16, 24)


def aragorn(l):
    """Roupa ARAGORN (código DESTEMIBLEWARRIOR): no lugar do nunchaku, a ESPADA."""
    return l is not None and l.f.get("estilo") == "aragorn"


def desenha_espada(tela, mao, a1, esc, girando=False):
    """A espada do Aragorn: cabo na mão, guarda e a lâmina comprida na direção a1."""
    if girando:  # girando rápido: um círculo prateado
        r = int(24 * esc)
        pygame.draw.circle(tela, (120, 124, 136), (int(mao[0]), int(mao[1])), r, max(1, int(3 * esc)))
        pygame.draw.circle(tela, (230, 232, 240), (int(mao[0]), int(mao[1])), max(1, r - int(2 * esc)), 1)
        return
    c, s = math.cos(a1), math.sin(a1)
    nx, ny = -s, c
    cabo_ini = (mao[0] - c * 4 * esc, mao[1] - s * 4 * esc)
    guarda = (mao[0] + c * 3 * esc, mao[1] + s * 3 * esc)
    ponta = (mao[0] + c * 30 * esc, mao[1] + s * 30 * esc)
    w = max(2, int(2.6 * esc))
    lamina = [(guarda[0] + nx * w * 0.6, guarda[1] + ny * w * 0.6), (ponta[0], ponta[1]),
              (guarda[0] - nx * w * 0.6, guarda[1] - ny * w * 0.6)]
    pygame.draw.polygon(tela, CONT, [(x + (x - mao[0]) * 0.02, y + (y - mao[1]) * 0.02) for x, y in lamina])
    pygame.draw.polygon(tela, CONT, lamina, max(2, int(esc)))
    pygame.draw.polygon(tela, (214, 218, 228), lamina)
    pygame.draw.line(tela, (250, 250, 255), guarda, ponta, 1)
    pygame.draw.line(tela, CONT, cabo_ini, guarda, w + 2)
    pygame.draw.line(tela, (86, 56, 34), cabo_ini, guarda, w)
    g1, g2 = (guarda[0] + nx * 5 * esc, guarda[1] + ny * 5 * esc), (guarda[0] - nx * 5 * esc, guarda[1] - ny * 5 * esc)
    pygame.draw.line(tela, CONT, g1, g2, w + 2)
    pygame.draw.line(tela, (200, 170, 90), g1, g2, w)


def desenha_nunchaku(tela, mao, a1, a2, esc, girando=False, l=None):
    """mao = onde a mão segura; a1 = direção do bastão da mão; a2 = direção do bastão solto."""
    if aragorn(l):
        return desenha_espada(tela, mao, a1, esc, girando)
    comp = 13 * esc
    if girando:  # girando rápido: vira um borrão redondo
        r = int(comp * 1.6)
        pygame.draw.circle(tela, MADEIRA_ESC, (int(mao[0]), int(mao[1])), r, max(1, int(3 * esc)))
        pygame.draw.circle(tela, MADEIRA, (int(mao[0]), int(mao[1])), max(1, r - int(2 * esc)), 1)
        pygame.draw.circle(tela, (240, 196, 60), (int(mao[0]), int(mao[1])), max(1, r // 3), 1)  # (a corrente dourada)
        return
    p1 = (mao[0] + math.cos(a1) * comp, mao[1] + math.sin(a1) * comp)
    elo = (p1[0] + math.cos(a2) * 3 * esc, p1[1] + math.sin(a2) * 3 * esc)
    p2 = (elo[0] + math.cos(a2) * comp, elo[1] + math.sin(a2) * comp)
    w = max(2, int(3 * esc))
    for a, b in ((mao, p1), (elo, p2)):
        pygame.draw.line(tela, CONT, a, b, w + 2)
        pygame.draw.line(tela, MADEIRA, a, b, w)
    # a CORRENTE DOURADA (remodel do Gomes): 3 elos grossinhos
    for i in range(3):
        a = (p1[0] + (elo[0] - p1[0]) * i / 3, p1[1] + (elo[1] - p1[1]) * i / 3)
        b = (p1[0] + (elo[0] - p1[0]) * (i + 1) / 3, p1[1] + (elo[1] - p1[1]) * (i + 1) / 3)
        pygame.draw.line(tela, CONT, a, b, max(2, int(1.8 * esc)))
        pygame.draw.line(tela, (250, 206, 70) if i % 2 == 0 else (196, 150, 40), a, b, max(1, int(1.0 * esc)))


# =====================================================================
# E: NUNCHAKU BUMERANGUE (bate na ida e na volta)
# =====================================================================
class Bumerangue(Projetil):
    def __init__(self, dono, x, y, d):
        super().__init__(dono, x, y, d, GOLPES["king_bumerangue"])
        self.voltando = False
        self.pode_acertar = True
        dono.extra["nunchaku_fora"] = True

    def update(self):
        self.t += 1
        if not self.voltando:
            self.x += self.vx
            if self.t >= 30 or self.x < PAREDE_E or self.x > PAREDE_D:
                self.voltando = True
                self.pode_acertar = True  # na volta pode acertar de novo
        else:  # volta pra mão do dono
            mx, my = self.dono.x, self.dono.y - 80 * self.dono.s
            dx, dy = mx - self.x, my - self.y
            d = math.hypot(dx, dy) or 1
            v = min(14, 6 + self.t * 0.15)
            self.x += dx / d * v
            self.y += dy / d * v
            if d < 26:
                self.vivo = False
                self.dono.extra["nunchaku_fora"] = False

    def desenhar(self, tela):
        a = self.t * 0.6
        esc = self.dono.s * 3 / 1.36 / 2.2
        mx, my = self.x - math.cos(a) * 14 * esc, self.y - math.sin(a) * 14 * esc
        desenha_nunchaku(tela, (mx, my), a, a, esc * 1.4, l=self.dono)


def tem_nunchaku(l):
    return not l.extra.get("nunchaku_fora")


def joga_bumerangue(l, jogo):
    jogo.projeteis.append(Bumerangue(l, l.x + 40 * l.s * l.dir, l.y - 84 * l.s, l.dir))
    som.tocar("vento")


# =====================================================================
# Q: CHUTE ACROBÁTICO (meia estrelinha esticando a perna)
# =====================================================================
def chute_acrobatico(l, outro, jogo):
    t = l.t
    if t < 8:
        l.angulo = 0
    elif t < 22:  # tomba de lado na meia estrelinha (perna lá no alto, bem esticada)
        l.angulo = -0.75 * suave((t - 8) / 8)
        l.vx = 2.5 * l.dir
    else:
        l.angulo = -0.75 * (1 - suave((t - 22) / 12))
        l.vx *= 0.7
    l.fisica(jogo)
    if t >= 38:
        l.angulo = 0
        return "fim"


# =====================================================================
# R: NUNCHAKU GIRATÓRIO (10 hits)
# =====================================================================
G_INI, G_INTERVALO, G_HITS = 10, 6, 10


def giratorio(l, outro, jogo):
    l.vx = 0.9 * l.dir if l.t < G_INI + G_HITS * G_INTERVALO else 0
    if l.t % 6 == 0 and G_INI <= l.t < G_INI + G_HITS * G_INTERVALO:
        som.tocar("vento", 0.5)
    l.fisica(jogo)
    if l.t >= G_INI + G_HITS * G_INTERVALO + 14:
        return "fim"


# =====================================================================
# SHIFT: finca o nunchaku e sai girando de estrelinha
# =====================================================================
S_PLANTA, S_VOA, S_FIM = 8, 34, 46


def salto(l, outro, jogo):
    t = l.t
    m = l.memo
    if t < S_PLANTA:
        l.vx = 0
        if t == 6:
            m["pino"] = (l.x + 46 * l.s * l.dir, CHAO)
            fumaca(jogo, m["pino"][0], CHAO - 4, 4, (150, 130, 100), 2, -1)
    elif t < S_VOA:
        k = (t - S_PLANTA) / (S_VOA - S_PLANTA)
        l.angulo = -l.dir * 0 + math.tau * 2 * k  # duas estrelinhas
        l.vx = 9 * l.dir
        l.y = CHAO - 46 * l.s * math.sin(k * math.pi)
        l.x = max(PAREDE_E, min(PAREDE_D, l.x + l.vx))
        return
    elif t == S_VOA:
        l.angulo, l.y = 0, CHAO
        fumaca(jogo, l.x, CHAO - 4, 6, (150, 130, 100), 3, -1)
    l.vx *= 0.7
    l.fisica(jogo)
    if t >= S_FIM:
        return "fim"


# =====================================================================
# Z: ULTIMATE — acrobacias com o nunchaku e arremesso pro outro lado
# =====================================================================
U_JOGA, U_CORRE_ATE = 6, 34
U_PARTES = [  # (duração, pose, dano)  — estrelinha, gira, passa nas costas, bastão, cotovelada, arremesso
    (14, "k_estrela", 4), (14, "k_gira", 4), (12, "k_costas", 0), (18, "k_bastao", 6), (14, "k_cotovelo", 6),
    (24, "k_arremessa", 10)]


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    if t == 1:
        m["nunchaku_cima"] = 0
        som.tocar("vento")
    if "pegou" in m:
        return sequencia(l, outro, jogo, t - m["pegou"])
    if l.acertou and "parou" not in m:
        if outro.estado == "golpeado":  # acertou a estrelinha voadora: começa a acrobacia
            m["pegou"] = t
            l.inv = 999
            outro.mudar("agarrado")
            outro.golpe = None
            outro.sobrepor = dict(outro.poses["golpeado"])
            l.angulo = 0
            return
        m["parou"] = t
    if "parou" in m:
        l.angulo *= 0.7
        l.vx *= 0.75
        l.fisica(jogo)
        if t - m["parou"] > 30:
            l.angulo = 0
            return "fim"
        return
    if U_JOGA <= t < U_CORRE_ATE:  # estrelinha voadora pra frente
        k = (t - U_JOGA) / (U_CORRE_ATE - U_JOGA)
        l.angulo = math.tau * k
        l.vx = 9 * l.dir
        m["caixa"] = (-10, 10, 50, 120)
    elif t >= U_CORRE_ATE:
        m["parou"] = t
    l.fisica(jogo)


def sequencia(l, outro, jogo, u):
    d = l.dir
    ini = 0
    l.vx = 0
    for i, (dur, pose, dano) in enumerate(U_PARTES):
        if u < ini + dur:
            k = (u - ini) / dur
            l.sobrepor = dict(POSES_KING[pose])
            l.angulo = math.tau * k if pose in ("k_estrela",) else 0
            l.vira = pose == "k_cotovelo" and (u // 4) % 2 == 1
            l.memo["girando"] = pose in ("k_gira", "k_bastao")
            if u == ini + dur // 2 and dano:
                outro.levar(dano * (1 if i < len(U_PARTES) - 1 else 1), l, GOLPES["king_ultimate"])
                outro.vida = max(1, outro.vida) if i < len(U_PARTES) - 1 else outro.vida
                outro.tremor_hit = 8
                jogo.faisca(outro.x - 20 * outro.s * d, outro.y - 80 * outro.s, False, dano >= 6)
                jogo.tremer(6)
                som.tocar("chute" if dano >= 6 else "soco")
                outro.x = max(PAREDE_E, min(PAREDE_D, outro.x + 6 * d))
            if pose == "k_arremessa" and u == ini + dur // 2:  # ARREMESSA pro outro lado da tela
                outro.sobrepor = {}
                outro.mudar("voando")
                outro.vx, outro.vy = -16 * d, -15
                outro.giro_voo = -0.3 * d
                outro.y = CHAO - 60
                l.inv = 0
                jogo.tremer(14)
            return
        ini += dur
    l.sobrepor, l.vira, l.angulo = {}, False, 0
    l.memo["girando"] = False
    if u >= ini + 12:
        return "fim"


def ultimate_efeito(l, tela):
    """O nunchaku que foi jogado pra cima (gira lá no alto) e volta pra mão."""
    m = l.memo
    t = l.t
    if "pegou" not in m and t < U_CORRE_ATE + 30:
        k = min(1, t / 20)
        x, y = l.x, l.y - (120 + 160 * math.sin(min(math.pi, t / 40 * math.pi))) * l.s
        desenha_nunchaku(tela, (x, y), t * 0.5, t * 0.5 + 1, l.s * 1.2, l=l)


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


_registra("king_bumerangue", pose="k_arremesso", ini=8, ativo=1, rec=13, proj=True, varios=True, raio=14, vel=10,
          dano=5, hit=12, defe=8, emp=3, nivel="medio", ia="longe", pode=tem_nunchaku, ao_usar=joga_bumerangue,
          bumerangue=True,
          quadros=[(0, "parado"), (6, "k_gira"), (9, "k_arremesso"), (16, "k_arremesso"), (22, "parado")])
# o bumerangue sai pelo ao_usar (não pelo jeito normal de bola)
GOLPES["king_bumerangue"]["proj"] = False
_registra("king_chute", ini=12, ativo=8, rec=18, janelas=((13, 21),), caixa=(16, 60, 104, 170), dano=15, hit=20,
          defe=12, emp=2, nivel="medio", lanca=16, logica=chute_acrobatico, ia="perto", som="vento",
          quadros=[(0, "parado"), (8, "k_estrela"), (14, "k_chute_alto"), (24, "k_chute_alto"), (38, "parado")])
def giro_quadros():
    """O R: o corpo vai e volta junto com cada pancada do nunchaku."""
    q = [(0, "parado"), (G_INI - 2, "k_gira")]
    for k in range(G_HITS):
        t = G_INI + k * G_INTERVALO
        q += [(t + 1, "k_gira"), (t + G_INTERVALO // 2 + 1, "k_gira2")]
    fim = G_INI + G_HITS * G_INTERVALO
    return q + [(fim, "k_gira"), (fim + 14, "parado")]


_registra("king_giro", ini=G_INI, ativo=G_HITS * G_INTERVALO, rec=14,
          janelas=tuple((G_INI + k * G_INTERVALO, G_INI + k * G_INTERVALO + 3) for k in range(G_HITS)),
          caixa=(0, 40, 92, 130), dano=2, hit=8, defe=6, emp=1, nivel="medio", logica=giratorio, ia="medio",
          pode=tem_nunchaku, quadros=giro_quadros())
_registra("king_salto", ini=S_PLANTA, ativo=S_VOA - S_PLANTA, rec=S_FIM - S_VOA, janelas=((S_PLANTA + 2, S_VOA),),
          caixa=(-24, 0, 40, 120), dano=6, hit=16, defe=10, emp=7, nivel="medio", logica=salto, ia="medio",
          pode=tem_nunchaku, som="vento",
          quadros=[(0, "parado"), (S_PLANTA - 2, "k_planta"), (S_PLANTA + 3, "k_estrela"), (S_VOA, "k_estrela"),
                   (S_FIM, "parado")])
_registra("king_ultimate", ini=U_JOGA, ativo=U_CORRE_ATE - U_JOGA, rec=30, janelas=((U_JOGA, U_CORRE_ATE),),
          dano=0, hit=60, defe=20, emp=0, nivel="medio", ultimate=True, logica=ultimate, efeito=ultimate_efeito,
          ia="ultimate", pode=tem_nunchaku,
          quadros=[(0, "parado"), (U_JOGA - 2, "k_bastao"), (U_JOGA + 2, "k_estrela"), (U_CORRE_ATE + 30, "parado")])

GOLPES_KING = {"E": "king_bumerangue", "Q": "king_chute", "R": "king_giro", "SHIFT": "king_salto", "Z": "king_ultimate"}

# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  B b v uniforme azul (claro -> escuro)  p P q pele  h H j cabelo/barba cinza  x X faixa preta  e olho
PALETA = {
    "k": (18, 16, 24), "B": (118, 156, 232), "b": (62, 98, 182), "v": (36, 58, 120),
    "p": (236, 196, 160), "P": (204, 160, 124), "q": (150, 108, 80),
    "h": (214, 214, 222), "H": (240, 240, 246), "j": (130, 132, 144), "x": (26, 24, 30), "X": (74, 72, 82),
    "e": (20, 20, 24),
    # remodel do Gomes: DRAGÃO bordado dourado, BANDAGEM nas mãos, OMBREIRA de couro, COLAR de contas
    "y": (236, 190, 64), "Y": (255, 230, 140), "w": (232, 226, 210), "W": (186, 178, 160),
    "c": (126, 78, 44), "C": (168, 110, 64), "o": (176, 40, 34), "O": (226, 184, 120),
}
S_REF = 1.36 / 3

TRONCO = Peca([
    "...kkkkkkkk...",
    "..kbBBpPbbbk..",
    ".kbBBbpPbbbvk.",
    ".kbBbbkpkbbvk.",
    ".kbBbbbkkYyvk.",
    ".kbBbbbbkbyvk.",
    ".kbbbbbbbkyvk.",
    ".kbbbbbbyykvk.",
    ".kbbbbbyybbvk.",
    "..kbbbbbyybk..",
    "..kbbbbbbyyk..",
    "..kbbbbbbvvk..",
    "..kxxxXxxxxk..",
    "..kxXxxxxXxk..",
    "..kbkxxxkbvk..",
    "..kbbkxkbbvk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbvvk..",
    "..kbbbbbbvvk..",
    "..kbbbbbvvvk..",
    "...kbbbbvvk...",
    "....kkkkkk....",
], PALETA, a=(7, 20), b=(7, 1))

TRONCO_COSTAS = Peca([
    "...kkkkkkkk...",
    "..kbBBBbbbbk..",
    ".kbBYYybbbbvk.",
    ".kbByyyyybbvk.",
    ".kbBbbbyyybvk.",
    ".kbBbbyyybbvk.",
    ".kbbbyyybbbvk.",
    ".kbbyyybbbbvk.",
    ".kbbyyyyybbvk.",
    "..kbbbbyyyvk..",
    "..kbbbbbyyvk..",
    "..kbbbbbbvvk..",
    "..kxxxxxxxxk..",
    "..kxXxxxxxxk..",
    "..kxxxxxxxxk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbvvk..",
    "..kbbbbbbvvk..",
    "..kbbbbbvvvk..",
    "...kbbbbvvk...",
    "....kkkkkk....",
], PALETA, a=(7, 20), b=(7, 1))

CABECA = Peca([
    "....kkk......",
    "..kkhHhk.kk..",
    ".khHHHhkkhHk.",
    "khHHhhhhhhHk.",
    "kHhhhhhhhhhk.",
    "kjhhkkkkkkhk.",
    "kjhkpppkepk..",
    ".kjkpppppppk.",
    ".kjkppppPppk.",
    "..kkhhhhhpk..",
    "..khhhhhhhk..",
    "...khhhhhk...",
    "....kkkkk....",
], PALETA, a=(6, 7), b=(6, 0), estica=False)

CABECA_COSTAS = Peca([
    "....kkk......",
    "..kkhHhk.kk..",
    ".khHHHhkkhHk.",
    "khHHhhhhhhHk.",
    "kHhhhhhhhhhk.",
    "kjhhhhhhhhhk.",
    "kjhhhhhhhhk..",
    ".kjhhhhhhhk..",
    ".kjhhhhhhhk..",
    "..kkhhhhpk...",
    "..kpppppk....",
    "...kpppk.....",
    "....kkk......",
], PALETA, a=(6, 7), b=(6, 0), estica=False)

COXA = Peca([
    ".kkkkkk.",
    "kbBbbbvk",
    "kBbbbbvk",
    "kBbbbbvk",
    "kbbbbbvk",
    "kbbbbbvk",
    "kbbbbvvk",
    "kbbbbvvk",
    "kbbbvvvk",
    ".kbbvvk.",
    ".kbbvvk.",
    ".kbvvvk.",
    "..kvvk..",
    "..kkkk..",
], PALETA, a=(3, 0), b=(3, 13))

CANELA = Peca([
    ".kkkkk.",
    "kbbbbvk",
    "kbbbbvk",
    "kbbbbvk",
    "kbbbvvk",
    "kbbbvvk",
    "kbbbvvk",
    "kbbvvvk",
    "kbbvvvk",
    "kbvvvvk",
    "kkkkkkk",
    ".kpPqk.",
    ".kpPqk.",
    "..kkk..",
], PALETA, a=(3, 0), b=(3, 13))

PE = Peca([
    ".kkkk......",
    "kpPPqkkkk..",
    "kpppppPPpk.",
    "kqqqqqqqqk.",
    ".kkkkkkkk..",
], PALETA, a=(3, 1), b=(9, 1), estica=False)

BRACO = Peca([
    ".kkkk.",
    "kbBbvk",
    "kbBbvk",
    "kbbbvk",
    "kbbbvk",
    "kbbbvk",
    "kbbvvk",
    "kbbvvk",
    "kbvvvk",
    "kkkkkk",
    ".kpqk.",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 11))

ANTEBRACO = Peca([
    ".kkk.",
    "kpPqk",
    "kpPqk",
    "kpPqk",
    "kppqk",
    "kwWwk",
    "kWwWk",
    "kwWwk",
    "kWwWk",
    "kwWwk",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 10))

MAO = Peca([
    ".kkkk.",
    "kwWWwk",
    "kWwWwk",
    "kpqqqk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 4), estica=False)

OMBREIRA = Peca([
    "..kkkkkk..",
    ".kCCCcccck",
    "kCCcccccck",
    "kCcoOcccck",
    "kccccccock",
    "kkkkkkkkkk",
    "..kxk.kxk.",
], PALETA, a=(5, 2), b=(5, 8), estica=False)


TRONCO_ANTIGO = Peca([
    "...kkkkkkkk...",
    "..kbBBpPbbbk..",
    ".kbBBbpPbbbvk.",
    ".kbBbbkpkbbvk.",
    ".kbBbbbkkbbvk.",
    ".kbBbbbbkbbvk.",
    ".kbbbbbbbkbvk.",
    ".kbbbbbbbbkvk.",
    ".kbbbbbbbbbvk.",
    "..kbbbbbbbvk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbvvk..",
    "..kxxxxxxxxk..",
    "..kxXxxxxxxk..",
    "..kbkxxxkbvk..",
    "..kbbkxkbbvk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbvvk..",
    "..kbbbbbbvvk..",
    "..kbbbbbvvvk..",
    "...kbbbbvvk...",
    "....kkkkkk....",
], PALETA, a=(7, 20), b=(7, 1))

TRONCO_COSTAS_ANTIGO = Peca([
    "...kkkkkkkk...",
    "..kbBBBbbbbk..",
    ".kbBBbbbbbbvk.",
    ".kbBbbbbbbbvk.",
    ".kbBbbbbbbbvk.",
    ".kbBbbbbbbbvk.",
    ".kbbbbbbbbbvk.",
    ".kbbbbbbbbbvk.",
    ".kbbbbbbbbbvk.",
    "..kbbbbbbbvk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbvvk..",
    "..kxxxxxxxxk..",
    "..kxXxxxxxxk..",
    "..kxxxxxxxxk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbbvk..",
    "..kbbbbbbvvk..",
    "..kbbbbbbvvk..",
    "..kbbbbbvvvk..",
    "...kbbbbvvk...",
    "....kkkkkk....",
], PALETA, a=(7, 20), b=(7, 1))

CABECA_ANTIGO = Peca([
    "....kkk......",
    "..kkhHhk.kk..",
    ".khHHHhkkhHk.",
    "khHHhhhhhhHk.",
    "kHhhhhhhhhhk.",
    "kjhhkkkkkkhk.",
    "kjhkpppkepk..",
    ".kjkpppppppk.",
    ".kjkppppPppk.",
    "..kkhhhhhpk..",
    "..khhhhhhhk..",
    "...khhhhhk...",
    "....kkkkk....",
], PALETA, a=(6, 7), b=(6, 0), estica=False)

CABECA_COSTAS_ANTIGO = Peca([
    "....kkk......",
    "..kkhHhk.kk..",
    ".khHHHhkkhHk.",
    "khHHhhhhhhHk.",
    "kHhhhhhhhhhk.",
    "kjhhhhhhhhhk.",
    "kjhhhhhhhhk..",
    ".kjhhhhhhhk..",
    ".kjhhhhhhhk..",
    "..kkhhhhpk...",
    "..kpppppk....",
    "...kpppk.....",
    "....kkk......",
], PALETA, a=(6, 7), b=(6, 0), estica=False)

COXA_ANTIGO = Peca([
    ".kkkkkk.",
    "kbBbbbvk",
    "kBbbbbvk",
    "kBbbbbvk",
    "kbbbbbvk",
    "kbbbbbvk",
    "kbbbbvvk",
    "kbbbbvvk",
    "kbbbvvvk",
    ".kbbvvk.",
    ".kbbvvk.",
    ".kbvvvk.",
    "..kvvk..",
    "..kkkk..",
], PALETA, a=(3, 0), b=(3, 13))

CANELA_ANTIGO = Peca([
    ".kkkkk.",
    "kbbbbvk",
    "kbbbbvk",
    "kbbbbvk",
    "kbbbvvk",
    "kbbbvvk",
    "kbbbvvk",
    "kbbvvvk",
    "kbbvvvk",
    "kbvvvvk",
    "kkkkkkk",
    ".kpPqk.",
    ".kpPqk.",
    "..kkk..",
], PALETA, a=(3, 0), b=(3, 13))

PE_ANTIGO = Peca([
    ".kkkk......",
    "kpPPqkkkk..",
    "kpppppPPpk.",
    "kqqqqqqqqk.",
    ".kkkkkkkk..",
], PALETA, a=(3, 1), b=(9, 1), estica=False)

BRACO_ANTIGO = Peca([
    ".kkkk.",
    "kbBbvk",
    "kbBbvk",
    "kbbbvk",
    "kbbbvk",
    "kbbbvk",
    "kbbvvk",
    "kbbvvk",
    "kbvvvk",
    "kkkkkk",
    ".kpqk.",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 11))

ANTEBRACO_ANTIGO = Peca([
    ".kkk.",
    "kpPqk",
    "kpPqk",
    "kpPqk",
    "kppqk",
    "kppqk",
    "kpPqk",
    "kpPqk",
    "kpqqk",
    "kpqqk",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 10))

MAO_ANTIGO = Peca([
    ".kkkk.",
    "kpPPqk",
    "kpPpqk",
    "kqqqqk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 4), estica=False)


def colar(tela, l, p, esc, branco):
    """O COLAR DE CONTAS (de monge): um U de contas grandes no peito, com uma conta maior embaixo."""
    def U(u):
        return l.ponto({"_": u}, "_")
    pc = p["pc"]
    k = (150, 150, 160) if branco else PALETA["k"]
    for i in range(7):
        a = math.pi * (0.15 + 0.7 * i / 6)
        u = (pc[0] + 9 + math.cos(a) * 5, pc[1] - 2 - math.sin(a) * 8)
        x, y = U(u)
        r = (2.0 if i == 3 else 1.5) * esc
        cor = (245, 245, 250) if branco else (PALETA["O"] if i % 2 else PALETA["o"])
        pygame.draw.circle(tela, k, (round(x), round(y)), max(2, round(r + 0.6 * esc)))
        pygame.draw.circle(tela, cor, (round(x), round(y)), max(1, round(r)))


def desenhar_king(l, tela, p, branco):
    if aragorn(l):  # (o GUARDIÃO ERRANTE é outra roupa: fica com o desenho antigo, sem dragão nem colar)
        return _desenhar_king(l, tela, p, branco, TRONCO_ANTIGO, TRONCO_COSTAS_ANTIGO, BRACO_ANTIGO, ANTEBRACO_ANTIGO,
                              MAO_ANTIGO, enfeites=False)
    return _desenhar_king(l, tela, p, branco, TRONCO, TRONCO_COSTAS, BRACO, ANTEBRACO, MAO, enfeites=True)


def _desenhar_king(l, tela, p, branco, TRONCO, TRONCO_COSTAS, BRACO, ANTEBRACO, MAO, enfeites):
    esc = l.s / S_REF
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
        PE.desenhar(tela, e, mais(e, fr, 9), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    def braco(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)

    longe, perto = (("cf", "mf", "pf", "jf"), ("ct", "mt", "pt", "jt")) if costas else \
        (("ct", "mt", "pt", "jt"), ("cf", "mf", "pf", "jf"))
    braco(longe[0], longe[1], longe_v)
    perna(longe[2], longe[3], longe_v)
    c, cb = P("pc"), P("cb")
    (TRONCO_COSTAS if costas else TRONCO).desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    perna(perto[2], perto[3], perto_v)
    u, _ = cabeca_eixos(c, cb, d)
    pygame.draw.line(tela, PALETA["k"], c, mais(cb, u, -3 * esc), max(3, int(5 * esc)))
    pygame.draw.line(tela, PALETA["P"] if not branco else (240, 240, 240), c, mais(cb, u, -3 * esc), max(1, int(3 * esc)))
    na_cabeca = (CABECA_COSTAS if costas else CABECA).desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    if aragorn(l) and not branco:  # ARAGORN: o cabelo comprido caindo até os ombros
        for k, (x0, x1) in enumerate(((0.6, -1.2), (2.2, 0.4), (3.6, 2.4))):
            pts = [na_cabeca(x0 - 0.8, 4), na_cabeca(x1 - 0.6, 14 + k), na_cabeca(x1 + 1.4, 14.5 + k),
                   na_cabeca(x0 + 1.6, 5)]
            pygame.draw.polygon(tela, PALETA["k"], pts)
            pygame.draw.polygon(tela, (70, 48, 32) if k % 2 == 0 else (96, 66, 44),
                                [(x + (sum(q[0] for q in pts) / 4 - x) * 0.25, y) for x, y in pts])
    braco(perto[0], perto[1], perto_v)
    if enfeites:  # a OMBREIRA DE COURO, só no ombro da frente
        OMBREIRA.desenhar(tela, (c[0] + 2 * esc * d, c[1] + 1 * esc), P(perto[0]), esc, espelho, perto_v)
        if not costas:  # o COLAR DE CONTAS (por cima de tudo, no pescoço e no peito)
            colar(tela, l, p, esc, branco)
    # o nunchaku na mão da frente
    jogado = l.extra.get("nunchaku_fora") or (l.estado == "ataque" and l.nome_golpe == "king_ultimate"
                                               and "pegou" not in l.memo)
    mostra = not jogado and (l.entrada_t is None or l.entrada_t > E_JOGA)
    if mostra:
        mao = P(perto[1])
        cot = P(perto[0])
        (dx, dy), _ = eixos(cot, mao)
        a1 = math.atan2(dy, dx)
        girando = (l.estado == "ataque" and l.nome_golpe == "king_giro" and l.t >= G_INI) or l.memo.get("girando")
        if l.estado == "ataque" and l.nome_golpe == "king_salto" and "pino" in l.memo and l.t < S_VOA:
            px, py = l.memo["pino"]
            desenha_nunchaku(tela, (px / (LARGURA / tela.get_width()), py / (ALTURA / tela.get_height()) - 1),
                             -math.pi / 2, -math.pi / 2, esc, l=l)
        else:
            a2 = math.pi / 2 + math.sin(l.t * 0.12) * 0.4  # o bastão solto balança
            desenha_nunchaku(tela, mao, a1, a2, esc, girando, l=l)


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Detalhe do King Rip grande: o cabelo cinza espetado pra trás e a barba."""
    cb = P("cb")
    cinza = (220, 220, 228)
    for i in range(4):
        base = (cb[0] - 2 * s * d, cb[1] - 4 * s + i * 2 * s)
        ponta = (cb[0] - (16 + i * 2) * s * d, cb[1] - (14 - i * 4) * s)
        pygame.draw.polygon(q, cinza, [base, ponta, (base[0] + 4 * s * d, base[1] + 4 * s)])
    pygame.draw.ellipse(q, cinza, (cb[0] - 2 * s + (2 * s * d), cb[1] + 2 * s, 8 * s, 7 * s))


# =====================================================================
# ENTRADA: agachado coberto pela capa (balançando), levanta e tira a capa
# =====================================================================
POSES_KING["k_agacha"] = dict(pt=(-20, 0), jt=(-4, 20), pf=(20, 0), jf=(30, 20), qd=(0, 30), pc=(10, 58), cb=(16, 72),
                              ct=(4, 44), mt=(16, 40), cf=(8, 46), mf=(20, 42))
proporcionar(POSES_KING)
CAPA, CAPA_ESC, CAPA_CLARA = (130, 24, 34), (70, 10, 18), (176, 52, 60)
E_LEVANTA, E_JOGA, E_FIM = 46, 66, 120


def entrada(l, t, jogo):
    if t < E_LEVANTA:  # agachado, coberto
        l.sobrepor = dict(POSES_KING["k_agacha"])
    elif t < E_JOGA:  # levanta devagar, ainda coberto
        l.sobrepor = misturar(POSES_KING["k_agacha"], POSES_KING["k_capa"], suave((t - E_LEVANTA) / (E_JOGA - E_LEVANTA)))
    elif t < 86:  # JOGA a capa
        if t == E_JOGA:
            som.tocar("vento")
            som.tocar("puf", 0.4)
        l.sobrepor = dict(POSES_KING["k_joga_capa"])
    elif t < 104:
        l.sobrepor = misturar(POSES_KING["k_joga_capa"], POSES_KING["parado"], suave((t - 86) / 18))
    else:
        l.sobrepor = {}
    l.t += 1


def pano(tela, topo, larg_topo, larg_base, alt, t, onda, giro=0.0, n=10):
    """Desenha um pano (capa) que ondula: as bordas são feitas de vários pontinhos que balançam."""
    cx, cy = topo
    c, s = math.cos(giro), math.sin(giro)

    def P(px, py):
        return (cx + px * c - py * s, cy + px * s + py * c)

    esq, dire = [], []
    for i in range(n + 1):
        k = i / n
        y = alt * k
        w = larg_topo + (larg_base - larg_topo) * k ** 0.8
        mexe = math.sin(t * 0.22 - i * 0.8) * onda * k
        esq.append(P(-w + mexe, y))
        dire.append(P(w + mexe * 0.8, y))
    barra = []  # a barra de baixo tremulando
    for i in range(1, n):
        k = i / n
        x = -larg_base + 2 * larg_base * k + math.sin(t * 0.22 - n * 0.8) * onda
        barra.append(P(x, alt + math.sin(t * 0.35 + i * 1.3) * onda * 0.5))
    pts = esq + barra + dire[::-1]
    pygame.draw.polygon(tela, CAPA, pts)
    for f in (-0.5, 0.0, 0.5):  # dobras do pano
        dobra = []
        for i in range(n + 1):
            k = i / n
            w = larg_topo + (larg_base - larg_topo) * k ** 0.8
            dobra.append(P(w * f + math.sin(t * 0.22 - i * 0.8) * onda * k * 0.9, alt * k))
        pygame.draw.lines(tela, CAPA_ESC, False, dobra, 2)
    pygame.draw.lines(tela, CAPA_CLARA, False, esq, 2)
    pygame.draw.polygon(tela, (30, 4, 8), pts, 2)


def entrada_efeito(l, tela, t):
    """A capa: cobrindo ele (balançando), acompanhando quando levanta, e voando mole quando ele joga."""
    if t >= E_FIM:
        return
    s = l.s
    if t < E_JOGA:
        p = l.pose_vista or l.pose_atual()
        cabeca = l.ponto(p, "cb")
        alt = l.y - cabeca[1] + 16 * s
        topo = (l.x + (cabeca[0] - l.x) * 0.45, cabeca[1] - 13 * s)  # no meio do corpo, cobrindo tudo
        pano(tela, topo, 13 * s, 50 * s, alt, t, 5 * s)
    else:
        u = t - E_JOGA
        cx = l.x - l.dir * (30 + u * 6) * s
        cy = l.y - 130 * s - u * 4.5 * s + u * u * 0.22 * s
        giro = -l.dir * min(1.2, u * 0.05)
        abre = min(1.0, u / 10)
        pano(tela, (cx, cy), (9 + 14 * abre) * s, (34 + 10 * abre) * s, (110 - 30 * abre) * s, t, (5 + 10 * abre) * s, giro)


# =====================================================================
# VITÓRIA: gira o nunchaku e faz pose
# =====================================================================
def vitoria(l, t, jogo):
    if t < 40:
        l.sobrepor = dict(POSES_KING["k_gira"])
        l.memo["girando"] = True
        if t % 10 == 0:
            som.tocar("vento", 0.4)
    else:
        l.memo["girando"] = False
        l.sobrepor = dict(POSES_KING["k_bastao"])


def vitoria_efeito(l, tela, t):
    pass
