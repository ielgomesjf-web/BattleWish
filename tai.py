"""TAI: o lutador de sumô (nome dado pelo Gomes).

Aparência: grandão, cinto de sumô (mawashi) azul-marinho, coque no cabelo. Mais largo que todo mundo.
  E      PISÃO (shiko): bate o pé e manda uma onda de choque rasteira (10) — pulando escapa
  Q      AGARRA e arremessa pro alto (20) — agarrão não dá pra defender
  R      TAPAS de sumô: 8 tapas de 2
  SHIFT  INVESTIDA de barriga (12): empurra o oponente até a parede
  Z      ULTIMATE: YOKOZUNA — agarra, levanta, pula e cai SENTADO em cima (40)
  Passiva: PESO PESADO — 120 de vida e soco/chute normal não fazem ele recuar (mas é o mais lento)
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

POSES_TAI = {
    "parado": dict(pt=(-30, 0), jt=(-24, 28), pf=(28, 0), jf=(24, 28), qd=(0, 50), pc=(4, 88), cb=(8, 108),
                   ct=(-14, 74), mt=(-4, 58), cf=(24, 76), mf=(36, 66)),
    "andar1": dict(pt=(-34, 2), jt=(-26, 28), pf=(30, 0), jf=(26, 28), qd=(-2, 48), pc=(2, 86), cb=(6, 106),
                   ct=(-16, 72), mt=(-6, 56), cf=(22, 74), mf=(34, 64)),
    "andar2": dict(pt=(-24, 6), jt=(-20, 30), pf=(26, 0), jf=(22, 28), qd=(0, 52), pc=(4, 90), cb=(8, 110),
                   ct=(-12, 76), mt=(-2, 60), cf=(26, 78), mf=(38, 68)),
    "andar3": dict(pt=(-28, 0), jt=(-22, 28), pf=(34, 2), jf=(28, 28), qd=(2, 48), pc=(6, 86), cb=(10, 106),
                   ct=(-12, 72), mt=(-2, 56), cf=(26, 74), mf=(38, 64)),
    "andar4": dict(pt=(-30, 0), jt=(-24, 28), pf=(24, 6), jf=(22, 30), qd=(0, 52), pc=(4, 90), cb=(8, 110),
                   ct=(-14, 76), mt=(-4, 60), cf=(24, 78), mf=(36, 68)),
    "t_shiko": dict(pt=(-26, 0), jt=(-20, 28), pf=(40, 70), jf=(30, 48), qd=(-4, 52), pc=(-6, 88), cb=(-6, 108),
                    ct=(-24, 72), mt=(-30, 54), cf=(20, 78), mf=(30, 60)),
    "t_pisao": dict(pt=(-32, 0), jt=(-22, 24), pf=(34, 0), jf=(30, 26), qd=(0, 40), pc=(6, 78), cb=(10, 98),
                    ct=(-12, 66), mt=(-6, 48), cf=(30, 62), mf=(38, 46)),
    "t_agarra": dict(pt=(-32, 0), jt=(-22, 26), pf=(30, 0), jf=(28, 28), qd=(0, 48), pc=(14, 86), cb=(20, 104),
                     ct=(26, 86), mt=(50, 90), cf=(30, 80), mf=(54, 82)),
    "t_levanta": dict(pt=(-28, 0), jt=(-22, 28), pf=(28, 0), jf=(22, 28), qd=(0, 52), pc=(0, 92), cb=(-2, 110),
                      ct=(-4, 114), mt=(-2, 142), cf=(8, 114), mf=(10, 142)),
    "t_tapa_a": dict(pt=(-30, 0), jt=(-22, 26), pf=(30, 0), jf=(28, 28), qd=(0, 48), pc=(10, 86), cb=(16, 104),
                     ct=(-10, 74), mt=(0, 64), cf=(32, 92), mf=(60, 98)),
    "t_tapa_b": dict(pt=(-30, 0), jt=(-22, 26), pf=(30, 0), jf=(28, 28), qd=(0, 48), pc=(10, 86), cb=(16, 104),
                     ct=(32, 90), mt=(60, 94), cf=(12, 72), mf=(16, 60)),
    "t_investida": dict(pt=(-38, 4), jt=(-22, 26), pf=(24, 0), jf=(28, 28), qd=(0, 44), pc=(24, 76), cb=(36, 90),
                        ct=(30, 70), mt=(52, 74), cf=(38, 72), mf=(58, 76)),
    "t_senta": dict(pt=(40, 4), jt=(24, 16), pf=(46, 6), jf=(30, 18), qd=(0, 22), pc=(0, 60), cb=(2, 80),
                    ct=(-20, 44), mt=(-30, 30), cf=(20, 48), mf=(36, 40)),
    "t_sal": dict(pt=(-28, 0), jt=(-22, 28), pf=(28, 0), jf=(24, 28), qd=(0, 52), pc=(2, 90), cb=(4, 110),
                  ct=(-10, 72), mt=(-4, 58), cf=(18, 104), mf=(26, 128)),
}
proporcionar(POSES_TAI)

TERRA = (170, 140, 100)


# =====================================================================
# E: PISÃO — onda de choque rasteira
# =====================================================================
class Onda(Projetil):
    """A onda de choque: corre pelo chão (quem pula, escapa)."""

    def __init__(self, dono):
        super().__init__(dono, dono.x + 40 * dono.s * dono.dir, CHAO - 14, dono.dir, GOLPES["tai_onda"])

    def update(self):
        self.t += 1
        self.x += self.vx
        if self.x < -40 or self.x > LARGURA + 40 or self.t > 70:
            self.vivo = False

    def desenhar(self, tela):
        d = 1 if self.vx > 0 else -1
        for i in range(4):  # ondinhas de terra
            x = self.x - d * i * 14
            h = 26 - i * 5 + math.sin(self.t * 0.8 + i) * 3
            pygame.draw.arc(tela, TERRA if i % 2 else (210, 180, 130), (x - 14, CHAO - h, 28, 2 * h), 0, math.pi, 4)
        for i in range(3):
            pygame.draw.circle(tela, (200, 170, 120), (int(self.x - d * i * 18 + random.uniform(-3, 3)),
                                                      int(CHAO - 4 - random.uniform(0, 12))), 3)


def pisao(l, jogo):
    jogo.projeteis.append(Onda(l))
    som.tocar("queda")
    som.tocar("terra", 0.6)
    jogo.tremer(8)
    fumaca(jogo, l.x + 30 * l.s * l.dir, CHAO - 4, 8, (170, 140, 100), 3, -1.2)


# =====================================================================
# Q: AGARRA E ARREMESSA PRO ALTO
# =====================================================================
def agarra_efeito(l, tela):
    if l.acertou and l.t < 40:  # um brilhinho nas mãos quando pega
        p = l.pose_vista or l.pose_atual()
        x, y = l.ponto(p, "mf")
        brilho(tela, (int(x), int(y)), int(16 * l.s), (255, 230, 160), 120)


# =====================================================================
# R: TAPAS (8)
# =====================================================================
T_INI, T_INTERVALO, T_HITS = 8, 5, 8


def tapas(l, outro, jogo):
    t = l.t
    l.vx = 0.8 * l.dir if T_INI <= t < T_INI + T_HITS * T_INTERVALO else 0
    if T_INI <= t < T_INI + T_HITS * T_INTERVALO and (t - T_INI) % T_INTERVALO == 0:
        som.tocar("soco", 0.5)
    l.fisica(jogo)
    if t >= T_INI + T_HITS * T_INTERVALO + 12:
        return "fim"


def tapas_quadros():
    q = [(0, "parado"), (T_INI - 2, "t_tapa_b")]
    for k in range(T_HITS):
        q.append((T_INI + k * T_INTERVALO + 2, "t_tapa_a" if k % 2 == 0 else "t_tapa_b"))
    q.append((T_INI + T_HITS * T_INTERVALO + 12, "parado"))
    return q


# =====================================================================
# SHIFT: INVESTIDA — empurra até a parede
# =====================================================================
I_INI, I_CORRE, I_EMPURRA = 8, 26, 100  # (empurra até a parede: dá tempo de atravessar a tela)


def investida(l, outro, jogo):
    t = l.t
    m = l.memo
    if l.acertou and "pegou" not in m and outro.estado == "golpeado":
        m["pegou"] = t
    if "pegou" in m:  # empurrando o outro na frente da barriga
        u = t - m["pegou"]
        na_parede = outro.x <= PAREDE_E + 2 or outro.x >= PAREDE_D - 2
        if u < I_EMPURRA and not na_parede and "parede" not in m:
            l.vx = 9 * l.dir
            outro.vx = 9 * l.dir
            outro.stun = max(outro.stun, 8)
            if t % 4 == 0:
                fumaca(jogo, l.x - 20 * l.dir, CHAO - 4, 1, (170, 140, 100), 1, -0.4)
        else:
            if na_parede and "parede" not in m:  # BAM na parede
                m["parede"] = t
                jogo.tremer(12)
                som.tocar("queda")
                jogo.faisca(outro.x, outro.y - 60 * outro.s, False, True)
            l.vx *= 0.6
            if t - m.get("parede", t) > 14 or u > I_EMPURRA + 14:
                l.fisica(jogo)
                return "fim"
        l.fisica(jogo)
        return
    if I_INI <= t < I_CORRE:
        l.vx = 9 * l.dir
    else:
        l.vx *= 0.7
    l.fisica(jogo)
    if t >= I_CORRE + 16:
        return "fim"


# =====================================================================
# Z: ULTIMATE — YOKOZUNA
# =====================================================================
U_PEGA, U_LEVANTA, U_PULA, U_SOLTA = 10, 22, 26, 38
U_DANO = 40


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    if "pegou" in m:
        return yokozuna(l, outro, jogo, t - m["pegou"])
    if l.acertou and "parou" not in m:
        if outro.estado == "golpeado" and outro.no_chao():  # AGARROU
            m["pegou"] = t
            l.inv = 999
            outro.mudar("agarrado")
            outro.golpe = None
            outro.sobrepor = dict(outro.poses["golpeado"])
            som.tocar("puf", 0.5)
            return
        m["parou"] = t
    l.vx = 0
    l.fisica(jogo)
    if t >= U_PEGA + 30:  # errou o agarrão: fica aberto
        return "fim"


def yokozuna(l, outro, jogo, u):
    m = l.memo
    d = l.dir
    if u < U_LEVANTA:  # levantando o oponente acima da cabeça
        k = suave(u / U_LEVANTA)
        l.sobrepor = misturar(POSES_TAI["t_agarra"], POSES_TAI["t_levanta"], k)
        outro.x = l.x + (40 - 36 * k) * l.s * d
        outro.y = l.y - 150 * l.s * k
        outro.sobrepor = dict(outro.poses["voando"])
        outro.angulo = -0.6 * d * k
        return
    if u == U_PULA:  # PULA com ele lá em cima
        l.vy = -13
        som.tocar("vento")
    if u < U_SOLTA:
        l.sobrepor = dict(POSES_TAI["t_levanta"])
        if u >= U_PULA:
            l.fisica(jogo)
        outro.x = l.x + 4 * l.s * d
        outro.y = l.y - 150 * l.s
        return
    if u == U_SOLTA:  # joga ele no chão... e cai SENTADO em cima
        outro.y = CHAO
        outro.angulo = 0
        outro.sobrepor = dict(outro.poses["caido"])
        jogo.tremer(10)
        som.tocar("queda")
    if "sentou" not in m:
        l.sobrepor = dict(POSES_TAI["t_senta"])
        l.x += (outro.x - l.x) * 0.3
        l.fisica(jogo)
        if l.no_chao() and u > U_SOLTA:
            m["sentou"] = u
            outro.levar(U_DANO, l, GOLPES["tai_ultimate"])
            outro.tremor_hit = 14
            jogo.tremer(26)
            jogo.parada = 10
            som.tocar("explosao")
            som.tocar("queda")
            for _ in range(30):  # terremoto: poeira pra todo lado
                a = random.uniform(math.pi, math.tau)
                v = random.uniform(3, 9)
                jogo.faiscas.append([l.x + random.uniform(-40, 40), CHAO - 4, math.cos(a) * v, math.sin(a) * v,
                                     random.randint(16, 28), random.choice((TERRA, (210, 180, 130))), 6])
        return
    s = u - m["sentou"]
    l.sobrepor = dict(POSES_TAI["t_senta"]) if s < 20 else \
        misturar(POSES_TAI["t_senta"], POSES_TAI["parado"], suave((s - 20) / 16))
    if s == 20:  # levanta e solta
        outro.sobrepor = {}
        outro.mudar("caido")
        l.inv = 0
        l.x -= 30 * l.s * d
    if s >= 40:
        l.sobrepor = {}
        return "fim"


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


_registra("tai_pisao", ini=16, ativo=1, rec=18, dano=10, hit=0, defe=0, emp=0, nivel="baixo", ia="longe",
          ao_usar=pisao, quadros=[(0, "parado"), (8, "t_shiko"), (14, "t_shiko"), (17, "t_pisao"), (35, "parado")])
_registra("tai_onda", ini=0, ativo=1, rec=0, proj=True, raio=16, vel=8, dano=10, hit=16, defe=10, emp=3, nivel="baixo")
_registra("tai_agarra", ini=8, ativo=5, rec=26, janelas=((8, 13),), caixa=(10, 30, 62, 110), dano=20, hit=24,
          defe=0, emp=1, nivel="medio", lanca=18, imbloqueavel=True, efeito=agarra_efeito, ia="perto",
          quadros=[(0, "parado"), (6, "t_agarra"), (14, "t_agarra"), (20, "t_levanta"), (39, "parado")])
_registra("tai_tapas", ini=T_INI, ativo=T_HITS * T_INTERVALO, rec=12,
          janelas=tuple((T_INI + k * T_INTERVALO, T_INI + k * T_INTERVALO + 3) for k in range(T_HITS)),
          caixa=(10, 50, 92, 122), dano=2, hit=9, defe=6, emp=1, nivel="medio", logica=tapas, ia="perto",
          quadros=tapas_quadros())
_registra("tai_investida", ini=I_INI, ativo=I_CORRE - I_INI, rec=16, janelas=((I_INI, I_CORRE),),
          caixa=(0, 20, 64, 120), dano=12, hit=24, defe=12, emp=2, nivel="medio", logica=investida, ia="medio",
          som="vento", quadros=[(0, "parado"), (I_INI - 2, "t_investida"), (60, "t_investida"), (70, "parado")])
GOLPES["tai_investida"]["total"] = 9999
_registra("tai_ultimate", ini=U_PEGA, ativo=6, rec=0, janelas=((U_PEGA, U_PEGA + 6),), caixa=(10, 30, 66, 110),
          dano=0, hit=60, defe=0, emp=0, nivel="medio", ultimate=True, imbloqueavel=True, logica=ultimate,
          ia="ultimate", quadros=[(0, "parado"), (U_PEGA - 2, "t_agarra"), (U_PEGA + 30, "t_agarra")])
GOLPES["tai_ultimate"]["total"] = 9999

GOLPES_TAI = {"E": "tai_pisao", "Q": "tai_agarra", "R": "tai_tapas", "SHIFT": "tai_investida", "Z": "tai_ultimate"}

# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  p P q pele  m M n mawashi (cinto)  h cabelo preto  e olho
#   (+ as cores escondidas da roupa SHREK: a A Q camisa, v V w colete, i I j calça, f F g botas, x botões,
#    z y coque; as orelhas do Shrek são desenhadas: orelhas_shrek)
PALETA = {
    "k": (20, 14, 12), "p": (236, 190, 150), "P": (250, 214, 178), "q": (196, 146, 108),
    "m": (40, 52, 110), "M": (80, 96, 170), "n": (24, 30, 70), "h": (24, 22, 28), "e": (20, 20, 24),
    # as "cores escondidas" (no Tai normal = pele / contorno / cabelo; None = não aparece). A roupa SHREK pinta elas.
    "a": (236, 190, 150), "A": (250, 214, 178), "Q": (196, 146, 108),   # camisa
    "v": (236, 190, 150), "V": (250, 214, 178), "w": (196, 146, 108),   # colete
    "i": (236, 190, 150), "I": (250, 214, 178), "j": (196, 146, 108),   # calça
    "f": (236, 190, 150), "F": (250, 214, 178), "g": (196, 146, 108),   # botas
    "x": (20, 14, 12),                                                   # botões (= contorno)
    "z": (20, 14, 12), "y": (24, 22, 28),                                # o coque (None no Shrek: careca)
}
S_REF = 1.5 / 3

TRONCO = Peca([
    ".....kkkkkkkkkkkk.....",
    "..xvvvaaaaaaaaaavwwx..",
    ".kVVvvaaaaaaaaaavvwwk.",
    "kVVVvvaaaaaaaaaavvwwwk",
    "kVVvvvxaaaaaaaaxvvvwwk",
    "kVVvvvaaaaaaaaaavvvwwk",
    "kVVvvvaaaaaaaaaavvvwwk",
    "kVVvvvaaaaaaaaaavvvwwk",
    "kVVvvvaaaaaaaaaavvvwwk",
    "kVVvvvaaaaaaaaaavvvwwk",
    "kVVvvvaaaaxxaaaavvvwwk",
    "kVVVvvaaaaaaaaaavvwwwk",
    ".kVVvvaaaaaaaaaavvwwk.",
    ".kmmmmmmmmmmmmmmmmmmk.",
    "kMMMmmmmmmmmmmmmmmMMMk",
    "kmmmmmmmmnnnnmmmmmmmmk",
    ".kmmmmmmmnnnnmmmmmmmk.",
    "..kmmmmmmnnnnmmmmmmk..",
    "....kmmmmnnnnmmmmk....",
    "......kkkkkkkkkk......",
], PALETA, a=(11, 18), b=(11, 1))

CABECA = Peca([
    "....zzz......",
    "...zyyyz.....",
    "...kkykkkk...",
    "..khhhhhhhk..",
    ".khhhhhhhhhk.",
    ".khhpppppppk.",
    ".khppppkepppk",
    ".kpppppppPppk",
    ".kppqpppppppk",
    "..kpppqqpppk.",
    "...kkpppppk..",
    ".....kkkkk...",
], PALETA, a=(7, 7), b=(7, 0), estica=False)

COXA = Peca([
    ".kkkkkkkkk.",
    "kIIiiiiijjk",
    "kIIiiiiijjk",
    "kIIiiiiijjk",
    "kIIiiiiijjk",
    ".kIiiiiijk.",
    ".kIiiiiijk.",
    ".kIiiiiijk.",
    ".kIIiiijjk.",
    ".kIIiiijjk.",
    "..kIiiijk..",
    "..kkkkkkk..",
], PALETA, a=(5, 0), b=(5, 11))

CANELA = Peca([
    "kkkkkkkk",
    "kIIiijjk",
    "kIIiijjk",
    "kIIiijjk",
    ".kIiijk.",
    ".kIiijk.",
    ".kIiijk.",
    ".kIiijk.",
    ".kIiijk.",
    ".kIiijk.",
    ".kkkkkk.",
], PALETA, a=(4, 0), b=(4, 10))

PE = Peca([
    ".kkkk......",
    "kfFFfkkkk..",
    "kffffffffk.",
    "kgggggggggk",
    ".kkkkkkkkk.",
], PALETA, a=(3, 1), b=(9, 1), estica=False)

BRACO = Peca([
    ".kkkkkkk.",
    "kAAaaaQQk",
    "kAAaaaQQk",
    "kAAaaaQQk",
    "kAAaaaQQk",
    ".kAaaaQk.",
    ".kAaaaQk.",
    ".kAaaaQk.",
    ".kkkkkkk.",
], PALETA, a=(4, 0), b=(4, 8))

ANTEBRACO = Peca([
    ".kkkkkk.",
    "kAAaaQQk",
    "kAAaaQQk",
    "kAAaaQQk",
    ".kAaaQk.",
    ".kAaaQk.",
    ".kAaaQk.",
    ".kAaaQk.",
    ".kkkkkk.",
], PALETA, a=(4, 0), b=(4, 8))

MAO = Peca([
    ".kkkkkk.",
    "kpPPpppk",
    "kpPPpppk",
    "kpppppqk",
    "kqqqqqqk",
    ".kkkkkk.",
], PALETA, a=(4, 0), b=(4, 5), estica=False)


def desenhar_tai(l, tela, p, branco):
    esc = l.s / S_REF
    d = l.lado()
    espelho = d < 0
    perto_v = "branco" if branco else "normal"
    longe_v = "branco" if branco else "escuro"

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

    braco("ct", "mt", longe_v)
    perna("pt", "jt", longe_v)
    perna("pf", "jf", perto_v)
    c, cb = P("pc"), P("cb")
    TRONCO.desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    u, _ = cabeca_eixos(c, cb, d)
    na_cabeca = CABECA.desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    if l.f.get("orelhas") and not branco:
        orelhas_shrek(tela, na_cabeca, esc)
    braco("cf", "mf", perto_v)


def orelhas_shrek(tela, P, esc):
    """As orelhinhas de trombeta do SHREK (roupa do Tai): uma na frente, atrás do olho, e a outra
    aparecendo atrás da cabeça. P leva um ponto da cabeça (em pixels do desenho) pra tela."""
    verde, escuro, borda = (150, 190, 70), (96, 130, 40), (20, 14, 12)
    for base, ponta in (((1.8, 5.6), (0.0, 4.4)), ((4.4, 6.6), (3.2, 4.8))):  # (a de trás, a da frente)
        b, p = P(*base), P(*ponta)
        dx, dy = p[0] - b[0], p[1] - b[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        w1, w2 = 0.8 * esc, 1.3 * esc  # fininha na cabeça, abre na ponta (trombeta)
        pts = [(b[0] + nx * w1, b[1] + ny * w1), (p[0] + nx * w2, p[1] + ny * w2),
               (p[0] - nx * w2, p[1] - ny * w2), (b[0] - nx * w1, b[1] - ny * w1)]
        pygame.draw.polygon(tela, borda, pts)
        pygame.draw.polygon(tela, verde, pts)
        pygame.draw.polygon(tela, borda, pts, max(1, int(esc * 0.6)))
        pygame.draw.circle(tela, escuro, (int(p[0]), int(p[1])), max(1, int(w2 * 0.7)))  # o buraco da orelha
        pygame.draw.circle(tela, borda, (int(p[0]), int(p[1])), max(1, int(w2 * 0.7)), max(1, int(esc * 0.4)))


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Tai grande: o coque e o cinto."""
    cb, qd = P("cb"), P("qd")
    pygame.draw.circle(q, (240, 240, 240) if branco else (24, 22, 28), (int(cb[0] - 3 * s * d), int(cb[1] - 9 * s)),
                       max(2, int(3 * s)))
    pygame.draw.rect(q, (40, 52, 110), (qd[0] - 12 * s, qd[1] - 6 * s, 24 * s, 8 * s))


# =====================================================================
# ENTRADA: joga sal pro alto e faz o pisão
# =====================================================================
E_SAL, E_SHIKO, E_PISA = 10, 44, 62


def entrada(l, t, jogo):
    if t < E_SHIKO:
        l.sobrepor = dict(POSES_TAI["t_sal"]) if t >= E_SAL - 6 else {}
        if t == E_SAL:  # o sal
            p = l.pose_vista or l.pose_atual()
            x, y = l.ponto(p, "mf")
            for _ in range(30):
                a = random.uniform(-2.6, -0.5)
                v = random.uniform(2, 6)
                jogo.faiscas.append([x, y, math.cos(a) * v * l.dir, math.sin(a) * v, random.randint(30, 50),
                                     (245, 245, 240), 3])
            som.tocar("puf", 0.4)
    elif t < E_PISA:
        l.sobrepor = misturar(POSES_TAI["parado"], POSES_TAI["t_shiko"], suave((t - E_SHIKO) / 12))
    else:
        if t == E_PISA:
            som.tocar("queda")
            jogo.tremer(14)
            fumaca(jogo, l.x + 30 * l.s * l.dir, CHAO - 4, 12, (170, 140, 100), 4, -1.3)
        l.sobrepor = dict(POSES_TAI["t_pisao"]) if t < E_PISA + 22 else {}
    l.t += 1


# =====================================================================
# VITÓRIA: pisões de sumô
# =====================================================================
def vitoria(l, t, jogo):
    u = t % 50
    l.sobrepor = dict(POSES_TAI["t_shiko"] if u < 30 else POSES_TAI["t_pisao"])
    if u == 30:
        som.tocar("queda", 0.6)
        jogo.tremer(6)
