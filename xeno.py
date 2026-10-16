"""XENOMORPH: o monstro do jogo de terror do Gomes, agora no BATTLE WISH.

Aparência: preto, cabeça comprida com crista, olhos amarelos (os mesmos da floresta), tubos nas costas,
cauda com ferrão, curvado que nem aranha. E a SEGUNDA BOCA.
  E      cospe ÁCIDO (8) — onde cai fica uma poça que queima (1 por segundo, 3 segundos)
  Q      RABADA por baixo (15, joga pra cima)
  R      frenesi de GARRAS: 6 hits de 3
  SHIFT  RASTEJA de quatro bem baixo (6) — passa por baixo de tiro
  Z      ULTIMATE: SEGUNDA BOCA — pula, prende no chão e morde (35). Erra se o oponente pular.
  Passiva: SANGUE ÁCIDO — quem bate nele de perto leva 1 de dano
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from corpo import eixos, frente_do_pe, mais
from golpes import GOLPES, misturar, proporcionar, suave
from lutador import Projetil
from max10 import brilho, fumaca
from pecas import Peca

POSES_XENO = {
    "parado": dict(pt=(-26, 0), jt=(-12, 30), pf=(20, 0), jf=(30, 30), qd=(-4, 52), pc=(16, 80), cb=(34, 88),
                   ct=(10, 62), mt=(28, 46), cf=(26, 66), mf=(46, 52)),
    "andar1": dict(pt=(-30, 2), jt=(-14, 30), pf=(24, 0), jf=(32, 30), qd=(-4, 50), pc=(16, 78), cb=(34, 86),
                   ct=(8, 60), mt=(22, 42), cf=(26, 64), mf=(48, 50)),
    "andar2": dict(pt=(4, 8), jt=(16, 32), pf=(0, 0), jf=(14, 30), qd=(-4, 54), pc=(16, 82), cb=(34, 90),
                   ct=(12, 64), mt=(34, 50), cf=(24, 68), mf=(40, 54)),
    "andar3": dict(pt=(22, 0), jt=(30, 30), pf=(-28, 2), jf=(-12, 30), qd=(-4, 50), pc=(16, 78), cb=(34, 86),
                   ct=(10, 62), mt=(32, 50), cf=(26, 62), mf=(42, 46)),
    "andar4": dict(pt=(0, 0), jt=(14, 30), pf=(4, 8), jf=(16, 32), qd=(-4, 54), pc=(16, 82), cb=(34, 90),
                   ct=(10, 64), mt=(28, 48), cf=(26, 68), mf=(46, 54)),
    "x_cospe": dict(pt=(-28, 0), jt=(-14, 30), pf=(22, 0), jf=(32, 30), qd=(-6, 54), pc=(18, 84), cb=(44, 96),
                    ct=(4, 70), mt=(-8, 58), cf=(14, 72), mf=(2, 60)),
    "x_rabada": dict(pt=(-24, 0), jt=(-6, 22), pf=(22, 0), jf=(32, 22), qd=(-2, 40), pc=(18, 64), cb=(34, 68),
                     ct=(12, 48), mt=(26, 30), cf=(28, 50), mf=(46, 34)),
    "x_garra_a": dict(pt=(-28, 0), jt=(-14, 28), pf=(26, 0), jf=(34, 30), qd=(-2, 52), pc=(20, 82), cb=(38, 90),
                      ct=(30, 92), mt=(56, 100), cf=(34, 70), mf=(48, 52)),
    "x_garra_b": dict(pt=(-28, 0), jt=(-14, 28), pf=(26, 0), jf=(34, 30), qd=(-2, 52), pc=(22, 80), cb=(40, 86),
                      ct=(30, 66), mt=(52, 50), cf=(32, 94), mf=(58, 98)),
    "x_rasteja": dict(pt=(-36, 4), jt=(-20, 18), pf=(30, 0), jf=(22, 18), qd=(0, 26), pc=(26, 34), cb=(46, 36),
                      ct=(30, 20), mt=(48, 4), cf=(38, 22), mf=(60, 6)),
    "x_salto": dict(pt=(-34, 10), jt=(-16, 30), pf=(-6, 6), jf=(10, 28), qd=(0, 50), pc=(24, 72), cb=(46, 76),
                    ct=(36, 74), mt=(60, 80), cf=(38, 66), mf=(62, 64)),
    "x_morde": dict(pt=(-30, 0), jt=(-12, 26), pf=(24, 0), jf=(34, 26), qd=(-4, 44), pc=(24, 60), cb=(44, 54),
                    ct=(30, 40), mt=(44, 14), cf=(38, 40), mf=(58, 10)),
    "x_vitoria": dict(pt=(-22, 0), jt=(-10, 30), pf=(20, 0), jf=(28, 30), qd=(-2, 56), pc=(6, 94), cb=(14, 114),
                      ct=(-14, 104), mt=(-32, 118), cf=(24, 104), mf=(42, 118)),
}
proporcionar(POSES_XENO)

ACIDO = (150, 230, 60)
ACIDO_CLARO = (220, 255, 140)


def Pt(l, x, y):
    """Um ponto no 'espaço da pose' (x pra frente, y pra cima) levado pra tela (com giro, lado e escala)."""
    return l.ponto({"o": (x, y)}, "o")


# =====================================================================
# A cauda, os tubos das costas e a SEGUNDA BOCA (desenhados por código)
# =====================================================================
def pontos_cauda(l, p):
    qx, qy = p["qd"]
    t = l.t
    normal = []
    for i in range(13):
        onda = math.sin(t * 0.12 + i * 0.55) * i * 0.7
        normal.append((qx - 8 - i * 7.5, qy + 4 + i * 3.2 + onda))
    rabada = l.estado == "ataque" and l.nome_golpe == "xeno_rabada"
    rasteja = l.estado == "ataque" and l.nome_golpe == "xeno_rasteja"
    if rasteja:
        normal = [(qx - 8 - i * 8, qy + math.sin(t * 0.4 + i * 0.7) * 3) for i in range(13)]
    if rabada:  # a cauda passa por baixo e sobe na frente
        k = suave(min(1.0, max(0.0, (l.t - 6) / 10))) * (1 - suave(max(0.0, (l.t - 26) / 12)))
        c0, c1, c2, c3 = (qx - 8, qy + 2), (qx - 34, -6), (qx + 56, -16), (qx + 96, 112)  # por baixo e sobe na frente
        balanco = []
        for i in range(13):
            u = i / 12
            p0, p1, p2, p3 = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
            balanco.append((p0 * c0[0] + p1 * c1[0] + p2 * c2[0] + p3 * c3[0],
                            p0 * c0[1] + p1 * c1[1] + p2 * c2[1] + p3 * c3[1]))
        normal = [(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k) for a, b in zip(normal, balanco)]
    return normal


def desenha_cauda(tela, l, p, esc, branco):
    pts = [Pt(l, x, y) for x, y in pontos_cauda(l, p)]
    for i in range(len(pts) - 1):
        w = max(1, int((4.2 - i * 0.28) * esc))
        pygame.draw.line(tela, PALETA["k"], pts[i], pts[i + 1], w + 2)
        pygame.draw.line(tela, (240, 240, 240) if branco else (PALETA["x"] if i % 2 else PALETA["X"]),
                         pts[i], pts[i + 1], w)
    (dx, dy), _ = eixos(pts[-2], pts[-1])  # o ferrão
    a = pts[-1]
    nx, ny = -dy, dx
    ponta = (a[0] + dx * 9 * esc, a[1] + dy * 9 * esc)
    lam = [(a[0] + nx * 3 * esc, a[1] + ny * 3 * esc), ponta, (a[0] - nx * 3 * esc, a[1] - ny * 3 * esc)]
    pygame.draw.polygon(tela, PALETA["k"], lam)
    pygame.draw.polygon(tela, (240, 240, 240) if branco else PALETA["s"], lam, max(1, int(esc * 0.6)))


def desenha_tubos(tela, l, p, esc, branco):
    px, py = p["pc"]
    for i in range(3):  # os tubos das costas
        a = Pt(l, px - 6 - i * 5, py - 2 + i * 3)
        b = Pt(l, px - 16 - i * 6, py + 12 + i * 2)
        pygame.draw.line(tela, PALETA["k"], a, b, max(3, int(3.4 * esc)))
        pygame.draw.line(tela, (240, 240, 240) if branco else PALETA["X"], a, b, max(1, int(1.6 * esc)))


def desenha_segunda_boca(tela, l, p, esc, k):
    """A boca de dentro saindo da boca (k de 0 a 1)."""
    cx, cy = p["cb"]
    a = Pt(l, cx + 10, cy - 4)
    b = Pt(l, cx + 10 + 20 * k, cy - 4 - 6 * k)
    pygame.draw.line(tela, PALETA["k"], a, b, max(3, int(4 * esc)))
    pygame.draw.line(tela, (110, 90, 100), a, b, max(1, int(2 * esc)))
    pygame.draw.circle(tela, PALETA["d"], (int(b[0]), int(b[1])), max(1, int(1.6 * esc)))


# =====================================================================
# E: CUSPE DE ÁCIDO (e a poça)
# =====================================================================
POCA_TEMPO, POCA_MAX = 180, 3


class Acido(Projetil):
    """Cuspe de ácido: vai em arco e, onde cai, vira uma poça."""

    def __init__(self, dono, x, y):
        super().__init__(dono, x, y, dono.dir, GOLPES["xeno_acido"])
        self.vy = -4.5

    def update(self):
        self.t += 1
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.35
        if self.y >= CHAO - 4:
            self.vivo = False
            nova_poca(self.dono, self.x)
        elif self.x < -40 or self.x > LARGURA + 40:
            self.vivo = False

    def desenhar(self, tela):
        for i in range(3):
            pygame.draw.circle(tela, ACIDO, (int(self.x - self.vx * i * 0.7), int(self.y - self.vy * i * 0.7)),
                               max(2, 6 - i * 2))
        brilho(tela, (int(self.x), int(self.y)), 14, ACIDO, 90)
        pygame.draw.circle(tela, ACIDO_CLARO, (int(self.x), int(self.y)), 4)


def nova_poca(dono, x):
    pocas = dono.extra.setdefault("pocas", [])
    pocas.append(dict(x=max(PAREDE_E, min(PAREDE_D, x)), t=POCA_TEMPO))
    del pocas[:-POCA_MAX]


def cospe(l, jogo):
    p = l.pose_vista or l.pose_atual()
    x, y = Pt(l, p["cb"][0] + 12, p["cb"][1] - 4)
    jogo.projeteis.append(Acido(l, x, y))
    som.tocar("lingua", 0.7)


def acido_acertou(dono, alvo, jogo, resultado):
    if resultado in ("hit", "def"):
        nova_poca(dono, alvo.x)


def todo_quadro(l, jogo):
    """As poças: queimam quem estiver em cima (1 por segundo) e somem depois de 3 segundos."""
    pocas = l.extra.get("pocas")
    if not pocas:
        return
    outro = jogo.L[1] if jogo.L[0] is l else jogo.L[0]
    for p in pocas:
        p["t"] -= 1
        if p["t"] % 60 == 0 and outro.no_chao() and abs(outro.x - p["x"]) < 34 * l.s and outro.vida > 0 \
                and outro.estado not in ("caido", "agarrado"):
            outro.levar(1, l, GOLPES["xeno_poca"])
            outro.tremor_hit = 4
    l.extra["pocas"] = [p for p in pocas if p["t"] > 0]


def desenhar_pocas(l, tela):
    for p in l.extra.get("pocas", []):
        k = min(1.0, p["t"] / 30, (POCA_TEMPO - p["t"] + 6) / 12)
        w = 36 * l.s * k
        pygame.draw.ellipse(tela, (60, 110, 20), (p["x"] - w, CHAO - 6, 2 * w, 12))
        pygame.draw.ellipse(tela, ACIDO, (p["x"] - w * 0.8, CHAO - 4, 1.6 * w, 8))
        rng = random.Random(int(p["x"]))
        for i in range(3):  # bolhinhas
            u = ((l.t + rng.randint(0, 40)) % 40) / 40
            bx = p["x"] + rng.uniform(-w * 0.6, w * 0.6)
            pygame.draw.circle(tela, ACIDO_CLARO, (int(bx), int(CHAO - 2 - u * 14)), max(1, int(3 * (1 - u))))


# =====================================================================
# R: GARRAS (6 hits)   SHIFT: RASTEJA
# =====================================================================
G_INI, G_INTERVALO, G_HITS = 8, 6, 6
R_INI, R_FIM = 5, 27


def garras(l, outro, jogo):
    l.vx = 1.2 * l.dir if G_INI <= l.t < G_INI + G_HITS * G_INTERVALO else 0
    if G_INI <= l.t < G_INI + G_HITS * G_INTERVALO and (l.t - G_INI) % G_INTERVALO == 0:
        som.tocar("vento", 0.4)
    l.fisica(jogo)
    if l.t >= G_INI + G_HITS * G_INTERVALO + 12:
        return "fim"


def garras_quadros():
    q = [(0, "parado"), (G_INI - 2, "x_garra_b")]
    for k in range(G_HITS):
        a, b = ("x_garra_a", "x_garra_b") if k % 2 == 0 else ("x_garra_b", "x_garra_a")
        q.append((G_INI + k * G_INTERVALO + 1, a))
        q.append((G_INI + k * G_INTERVALO + 4, b))
    q.append((G_INI + G_HITS * G_INTERVALO + 12, "parado"))
    return q


def rasteja(l, outro, jogo):
    t = l.t
    if l.acertou:
        l.memo["bateu"] = True
    if R_INI <= t < R_FIM and "bateu" not in l.memo:
        l.vx = 11 * l.dir
    else:
        l.vx *= 0.7
    l.fisica(jogo)
    if t >= R_FIM + 12:
        return "fim"


# =====================================================================
# Z: ULTIMATE — SEGUNDA BOCA
# =====================================================================
U_PULA, U_MORDIDAS, U_INTERVALO, U_DANO = 12, 5, 14, 7
U_SOLTA = 10 + U_MORDIDAS * U_INTERVALO


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    if "pegou" in m:
        return devorar(l, outro, jogo, t - m["pegou"])
    if l.acertou and "parou" not in m:
        if outro.estado == "golpeado":  # PEGOU: prende no chão
            m["pegou"] = t
            l.inv = 999
            outro.mudar("agarrado")
            outro.golpe = None
            outro.sobrepor = dict(outro.poses["caido"])
            outro.y, outro.vx, outro.vy = CHAO, 0, 0
            l.x = outro.x - 26 * l.s * l.dir
            l.y, l.vx, l.vy = CHAO, 0, 0
            l.sobrepor = dict(POSES_XENO["x_morde"])
            som.tocar("queda")
            jogo.tremer(10)
            return
        m["parou"] = t  # defendeu ou deu parry: errou
    if t < U_PULA:
        l.vx = 0
        l.fisica(jogo)
        return
    if t == U_PULA:  # O BOTE
        dist = max(60, min(380, (outro.x - l.x) * l.dir))
        l.vy = -12
        l.vx = dist / 28 * l.dir
        som.tocar("vento")
    if "parou" not in m and not l.no_chao():
        m["caixa"] = (0, 10, 74, 110)
    else:
        m["caixa"] = None
    l.fisica(jogo)
    if t > U_PULA + 3 and l.no_chao():
        m.setdefault("pousou", t)
        l.vx = 0
        if t - m["pousou"] > 26:  # errou: fica um tempinho aberto
            return "fim"


def devorar(l, outro, jogo, u):
    m = l.memo
    l.sobrepor = dict(POSES_XENO["x_morde"])
    for k in range(U_MORDIDAS):
        if u == 10 + k * U_INTERVALO:  # a segunda boca ataca
            ultima = k == U_MORDIDAS - 1
            outro.levar(U_DANO, l, GOLPES["xeno_ultimate"])
            if not ultima:
                outro.vida = max(1, outro.vida)
            outro.tremor_hit = 8
            m["boca"] = u
            jogo.tremer(7)
            som.tocar("chute" if ultima else "soco")
            jogo.faisca(outro.x, outro.y - 20 * outro.s, False, ultima)
    if u == U_SOLTA:  # solta e pula pra trás
        outro.sobrepor = {}
        outro.mudar("caido")
        l.sobrepor = {}
        l.inv = 0
        l.vx, l.vy = -6 * l.dir, -7
    if u > U_SOLTA:
        l.fisica(jogo)
        if l.no_chao() and u > U_SOLTA + 8:
            l.vx = 0
            if u > U_SOLTA + 20:
                return "fim"


def ultimate_quadros():
    return [(0, "parado"), (8, "x_rabada"), (U_PULA, "x_salto"), (U_PULA + 30, "x_salto"), (U_PULA + 40, "parado")]


def boca_k(l):
    """O quanto a segunda boca está pra fora agora (0 = guardada)."""
    m = l.memo
    if l.estado == "ataque" and l.nome_golpe == "xeno_ultimate" and "boca" in m:
        u = l.t - m["pegou"] - m["boca"]
        if 0 <= u < 8:
            return math.sin(u / 8 * math.pi)
    if l.estado == "vitoria" and 30 <= l.t < 60:
        return math.sin((l.t - 30) / 30 * math.pi)
    if l.estado == "ataque" and l.nome_golpe == "provocar" and 10 <= l.t < 50:
        return math.sin((l.t - 10) / 40 * math.pi)
    return 0


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


_registra("xeno_cospe", ini=10, ativo=1, rec=18, dano=8, hit=14, defe=8, emp=2, nivel="medio", ia="longe",
          ao_usar=cospe, quadros=[(0, "parado"), (6, "x_cospe"), (20, "x_cospe"), (29, "parado")])
_registra("xeno_acido", ini=0, ativo=1, rec=0, proj=True, varios=True, raio=9, vel=9, dano=8, hit=14, defe=8, emp=2,
          nivel="medio", ao_acertar=acido_acertou)
_registra("xeno_poca", ini=0, ativo=1, rec=0, dano=1, hit=0, defe=0, emp=0, nivel="medio", ia="longe")
_registra("xeno_rabada", ini=12, ativo=8, rec=20, janelas=((12, 20),), caixa=(10, 0, 100, 120), dano=15, hit=20,
          defe=12, emp=2, nivel="medio", lanca=16, ia="perto", som="vento",
          quadros=[(0, "parado"), (8, "x_rabada"), (26, "x_rabada"), (40, "parado")])
_registra("xeno_garras", ini=G_INI, ativo=G_HITS * G_INTERVALO, rec=12,
          janelas=tuple((G_INI + k * G_INTERVALO, G_INI + k * G_INTERVALO + 3) for k in range(G_HITS)),
          caixa=(10, 30, 88, 112), dano=3, hit=10, defe=7, emp=1, nivel="medio", logica=garras, ia="perto",
          quadros=garras_quadros())
_registra("xeno_rasteja", base="agachado", ini=R_INI, ativo=R_FIM - R_INI, rec=12, janelas=((R_INI, R_FIM),),
          caixa=(0, 0, 64, 46), dano=6, hit=14, defe=8, emp=4, nivel="baixo", logica=rasteja, ia="medio", som="vento",
          quadros=[(0, "parado"), (R_INI - 1, "x_rasteja"), (R_FIM, "x_rasteja"), (R_FIM + 12, "parado")])
_registra("xeno_ultimate", ini=U_PULA, ativo=40, rec=0, janelas=((U_PULA, U_PULA + 40),), dano=0, hit=40, defe=20,
          emp=0, nivel="medio", ultimate=True,
          logica=ultimate, ia="ultimate", quadros=ultimate_quadros())
GOLPES["xeno_ultimate"]["total"] = 9999

GOLPES_XENO = {"E": "xeno_cospe", "Q": "xeno_rabada", "R": "xeno_garras", "SHIFT": "xeno_rasteja",
               "Z": "xeno_ultimate"}

# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  b x X s corpo preto (escuro -> brilho)  y Y olho amarelo  d dente
PALETA = {
    "k": (8, 8, 12), "b": (22, 24, 30), "x": (40, 42, 52), "X": (74, 78, 92), "s": (120, 126, 142),
    "y": (255, 210, 40), "Y": (255, 248, 170), "d": (204, 206, 196),
}
S_REF = 1.4 / 3

TRONCO = Peca([
    "...kkkkkk...",
    "..kbxXXxbk..",
    ".kbxXssXxbk.",
    ".kbxkXXkxbk.",
    ".kbxXkkXxbk.",
    ".kbkxXXxkbk.",
    ".kbxkkkkxbk.",
    ".kbxXXXXxbk.",
    ".kbkxxxxkbk.",
    "..kbkXXkbk..",
    "..kbxkkxbk..",
    "..kbxXXxbk..",
    "..kbkxxkbk..",
    "..kbxkkxbk..",
    "...kbxxbk...",
    "...kbXXbk...",
    "...kbkkbk...",
    "...kbxxbk...",
    "...kbXXbk...",
    "....kkkk....",
], PALETA, a=(6, 18), b=(6, 1))

CABECA = Peca([
    "....kkkkkk........",
    "..kkxXXXXxkkk.....",
    ".kxXsssXXXxxxkk...",
    "kbxXXXXXXXXxxxxkk.",
    ".kbbxxxxxxxxxyYxxk",
    "..kkbbbxxxxxkkyxdk",
    "....kkkbbbbkdkdkdk",
    ".......kkkkkkkkkk.",
], PALETA, a=(9, 4), b=(9, 0), estica=False)

COXA = Peca([
    ".kkkk.",
    "kxXxbk",
    "kXxxbk",
    "kxxxbk",
    "kxxbbk",
    "kxxbbk",
    "kxxbbk",
    ".kxbk.",
    ".kxbk.",
    ".kxbk.",
    ".kbbk.",
    "..kk..",
], PALETA, a=(2, 0), b=(2, 11))

CANELA = Peca([
    ".kkk.",
    "kxXbk",
    "kxxbk",
    "kxbbk",
    ".kxk.",
    ".kxk.",
    ".kxk.",
    ".kxk.",
    ".kbk.",
    ".kbk.",
    "kxXbk",
    "kxxbk",
    ".kbk.",
    "..k..",
], PALETA, a=(2, 0), b=(2, 13))

PE = Peca([
    ".kkk.....",
    "kxXbkkk..",
    "kxxbbbbkk",
    ".kkdkkdkd",
], PALETA, a=(2, 1), b=(7, 1), estica=False)

BRACO = Peca([
    ".kkk.",
    "kxXbk",
    "kxxbk",
    "kxxbk",
    ".kxk.",
    ".kxk.",
    ".kxk.",
    "kxxbk",
    "kxbbk",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 9))

ANTEBRACO = Peca([
    ".kkk.",
    "kxXbk",
    ".kxk.",
    ".kxk.",
    ".kxk.",
    ".kxk.",
    ".kxk.",
    ".kxk.",
    "kxxbk",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 9))

MAO = Peca([
    ".kkk...",
    "kxxbkk.",
    "kxkdkdk",
    ".kd.d..",
], PALETA, a=(2, 0), b=(2, 3), estica=False)


def desenhar_xeno(l, tela, p, branco):
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
        PE.desenhar(tela, e, mais(e, fr, 8), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    def braco(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)

    desenha_cauda(tela, l, p, esc, branco)
    braco("ct", "mt", longe_v)
    perna("pt", "jt", longe_v)
    c, cb = P("pc"), P("cb")
    TRONCO.desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    perna("pf", "jf", perto_v)
    desenha_tubos(tela, l, p, esc, branco)
    pescoco = Pt(l, (p["pc"][0] + p["cb"][0]) / 2, (p["pc"][1] + p["cb"][1]) / 2 + 2)
    pygame.draw.line(tela, PALETA["k"], c, cb, max(3, int(5 * esc)))
    pygame.draw.line(tela, (240, 240, 240) if branco else PALETA["x"], c, pescoco, max(1, int(3 * esc)))
    cima = Pt(l, p["cb"][0] - 3, p["cb"][1] + 10)  # a cabeça fica deitada pra frente (comprida)
    CABECA.desenhar(tela, cb, cima, esc, espelho, perto_v)
    k = boca_k(l)
    if k > 0.05:
        desenha_segunda_boca(tela, l, p, esc, k)
    braco("cf", "mf", perto_v)


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Xeno grande: a cabeça comprida pra trás e os olhos amarelos."""
    cb = P("cb")
    preto = (240, 240, 240) if branco else (30, 32, 40)
    pygame.draw.polygon(q, preto, [(cb[0] + 8 * s * d, cb[1]), (cb[0] - 24 * s * d, cb[1] - 10 * s),
                                   (cb[0] - 4 * s * d, cb[1] + 6 * s)])
    pygame.draw.circle(q, (255, 210, 40), (int(cb[0] + 6 * s * d), int(cb[1] - 1 * s)), max(2, int(2 * s)))


# =====================================================================
# ENTRADA: olhos no escuro... e ele desce do teto pela cauda
# =====================================================================
E_OLHOS, E_DESCE, E_CAI, E_FIM = 40, 78, 92, 108


def entrada(l, t, jogo):
    xf = l.extra["entrada_x"]
    l.x = xf
    if t < E_OLHOS:
        l.esconde = True
    elif t < E_DESCE:  # pendurado de cabeça pra baixo, descendo devagar
        l.esconde = False
        k = suave((t - E_OLHOS) / (E_DESCE - E_OLHOS))
        l.angulo = math.pi
        l.y = 40 + 200 * k
        l.sobrepor = dict(POSES_XENO["x_salto"])
    elif t < E_CAI:  # solta a cauda e cai girando
        k = (t - E_DESCE) / (E_CAI - E_DESCE)
        l.angulo = math.pi * (1 - k)
        l.y = 240 + (CHAO - 240) * k * k
    else:
        if t == E_CAI:
            som.tocar("queda")
            jogo.tremer(8)
            fumaca(jogo, l.x, CHAO - 4, 10, (90, 90, 100), 4, -1)
        l.angulo = 0
        l.y = CHAO
        l.sobrepor = dict(POSES_XENO["x_rabada"]) if t < E_FIM else {}
    l.t += 1


def entrada_efeito(l, tela, t):
    if t < E_OLHOS:  # só os olhos amarelos lá no alto, piscando
        aberto = not (18 <= t < 22)
        if aberto:
            for ox in (0, 22):
                x, y = l.x + (ox - 10) * l.dir, 150
                brilho(tela, (int(x), y), 16, (255, 210, 40), 140)
                pygame.draw.ellipse(tela, (255, 230, 90), (x - 6, y - 3, 12, 6))
    elif t < E_CAI:  # a cauda presa no teto
        if t < E_DESCE:
            p = l.pose_vista or l.pose_atual()
            q = l.ponto(p, "qd")
            pygame.draw.line(tela, (8, 8, 12), (q[0], q[1]), (q[0] + 10, 0), 6)
            pygame.draw.line(tela, (60, 64, 76), (q[0], q[1]), (q[0] + 10, 0), 3)


# =====================================================================
# VITÓRIA: fica de pé, abre os braços e mostra a segunda boca
# =====================================================================
def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES_XENO["x_vitoria"] if t > 12 else POSES_XENO["x_rabada"])
    if t == 30:
        som.tocar("uivo", 0.5)
