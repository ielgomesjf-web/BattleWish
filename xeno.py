"""TROMOS (TROMOSTOU ERGATITIRIOU; era o "Xenomorph"): o monstro do jogo de terror do Gomes, agora no BATTLE WISH.

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
    for i in range(13):  # (remodel do Gomes: a cauda CURVADA, subindo na ponta)
        onda = math.sin(t * 0.12 + i * 0.55) * i * 0.5
        curva = max(0, i - 6) ** 2 * 1.1
        normal.append((qx - 8 - i * 6.2 + max(0, i - 8) * 2.6, qy + 4 + i * 4.2 - curva + onda))
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


def cor(letra):
    """A cor da paleta, seguindo a roupa (o rabo, os tubos e o ferrão são desenhados por código)."""
    import pecas
    return (pecas.TROCA or {}).get(letra, PALETA[letra])


def desenha_cauda(tela, l, p, esc, branco):
    pts = [Pt(l, x, y) for x, y in pontos_cauda(l, p)]
    indominus = l.f.get("estilo") == "indominus"
    for i in range(len(pts) - 1):
        w = max(1, int((4.2 - i * 0.28) * esc))
        pygame.draw.line(tela, PALETA["k"], pts[i], pts[i + 1], w + 2)
        if indominus:  # INDOMINUS: a cauda branca com listras cinza-escuras
            c = (78, 80, 88) if i % 2 else cor("X")
        else:
            c = cor("x") if i % 2 else cor("X")
        pygame.draw.line(tela, (240, 240, 240) if branco else c, pts[i], pts[i + 1], w)
    (dx, dy), _ = eixos(pts[-2], pts[-1])  # o ferrão
    a = pts[-1]
    nx, ny = -dy, dx
    ponta = (a[0] + dx * 9 * esc, a[1] + dy * 9 * esc)
    lam = [(a[0] + nx * 3 * esc, a[1] + ny * 3 * esc), ponta, (a[0] - nx * 3 * esc, a[1] - ny * 3 * esc)]
    pygame.draw.polygon(tela, PALETA["k"], lam)
    pygame.draw.polygon(tela, (240, 240, 240) if branco else cor("s"), lam, max(1, int(esc * 0.6)))


def desenha_tubos(tela, l, p, esc, branco):
    px, py = p["pc"]
    if l.f.get("estilo") == "indominus" and not branco:  # INDOMINUS: os espinhos (osteodermos) nas costas
        for i in range(5):
            base = Pt(l, px - 4 - i * 4, py + 4 - i * 6)
            ponta = Pt(l, px - 12 - i * 4, py + 10 - i * 6)
            lado = Pt(l, px - 2 - i * 4, py - 2 - i * 6)
            pygame.draw.polygon(tela, PALETA["k"], [base, ponta, lado])
            pygame.draw.polygon(tela, (96, 98, 106), [base, ponta, lado], 0)
        return
    for i in range(3):  # os tubos das costas
        a = Pt(l, px - 6 - i * 5, py - 2 + i * 3)
        b = Pt(l, px - 16 - i * 6, py + 12 + i * 2)
        pygame.draw.line(tela, PALETA["k"], a, b, max(3, int(3.4 * esc)))
        pygame.draw.line(tela, (240, 240, 240) if branco else cor("X"), a, b, max(1, int(1.6 * esc)))


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
    """As poças: queimam quem estiver em cima (1 por segundo) e somem depois de 3 segundos.
    (E as passivas do Tromos: EMBOSCADA e REGENERAÇÃO.)"""
    import habilidades
    habilidades.tromos_quadro(l, jogo)
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
U_PULA, U_MORDIDAS, U_INTERVALO, U_DANO = 12, 5, 14, 5
U_CURA = 3  # (pedido do Gomes: menos dano, mas cada mordida RECUPERA vida dele: 5 x 5 = 25, +15 de vida)
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
            l.vida = min(l.vida_max, l.vida + U_CURA)  # a mordida cura o Xeno
            l.vida_vista = max(l.vida_vista, l.vida)
            m.setdefault("curas", []).append(u)
            from max10 import fumaca
            fumaca(jogo, l.x, l.y - 60 * l.s, 5, (120, 255, 140), 2, -1.5)
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


def cura_efeito(l, tela):
    """O '+3' verde subindo em cima do Xeno a cada mordida da SEGUNDA BOCA."""
    m = l.memo
    if "pegou" not in m:
        return
    u = l.t - m["pegou"]
    from efeitos import texto_grande
    for c in m.get("curas", []):
        k = u - c
        if 0 <= k < 30:
            texto_grande(tela, f"+{U_CURA}", 22, (120, 255, 140), (int(l.x), int(l.y - (130 + k * 1.5) * l.s)),
                         contorno=(10, 50, 20))


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


_registra("xeno_cospe", ini=10, ativo=1, rec=18, dano=9, hit=14, defe=8, emp=2, nivel="medio", ia="longe",
          ao_usar=cospe, quadros=[(0, "parado"), (6, "x_cospe"), (20, "x_cospe"), (29, "parado")])
_registra("xeno_acido", ini=0, ativo=1, rec=0, proj=True, varios=True, raio=9, vel=9, dano=9, hit=14, defe=8, emp=2,
          nivel="medio", ao_acertar=acido_acertou)
_registra("xeno_poca", ini=0, ativo=1, rec=0, dano=1, hit=0, defe=0, emp=0, nivel="medio", ia="longe")
_registra("xeno_rabada", ini=12, ativo=8, rec=20, janelas=((12, 20),), caixa=(10, 0, 100, 120), dano=15, hit=20,
          defe=12, emp=2, nivel="medio", lanca=16, ia="perto", som="vento",
          quadros=[(0, "parado"), (8, "x_rabada"), (26, "x_rabada"), (40, "parado")])
_registra("xeno_garras", ini=G_INI, ativo=G_HITS * G_INTERVALO, rec=12,
          janelas=tuple((G_INI + k * G_INTERVALO, G_INI + k * G_INTERVALO + 3) for k in range(G_HITS)),
          caixa=(10, 30, 88, 112), dano=4, hit=10, defe=7, emp=1, nivel="medio", logica=garras, ia="perto",
          quadros=garras_quadros())
_registra("xeno_rasteja", base="agachado", ini=R_INI, ativo=R_FIM - R_INI, rec=12, janelas=((R_INI, R_FIM),),
          caixa=(0, 0, 64, 46), dano=8, hit=14, defe=8, emp=4, nivel="baixo", logica=rasteja, ia="medio", som="vento",
          quadros=[(0, "parado"), (R_INI - 1, "x_rasteja"), (R_FIM, "x_rasteja"), (R_FIM + 12, "parado")])
_registra("xeno_ultimate", ini=U_PULA, ativo=40, rec=0, janelas=((U_PULA, U_PULA + 40),), dano=0, hit=40, defe=20,
          emp=0, nivel="medio", ultimate=True,
          logica=ultimate, efeito=cura_efeito, ia="ultimate", quadros=ultimate_quadros())
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
    "....kkkkkk..........",
    "..kkxXXXXxkkk.......",
    ".kxXsssXXXxxxkk.....",
    "kbxXXXXXXXXxxxxkkk..",
    ".kbbxxxxxxxxxyYxxxkk",
    "..kkbbbxxxxxkkyxxxbk",
    "....kkkbbbbkdkdkdkbk",
    ".......kkkkkkkkkkdkk",
    ".................kk.",
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


# =====================================================================
# INDOMINUS REX (roupa secreta do Xenomorph, código UNTAMABLE): um dinossauro desenhado inteiro,
# em cima dos mesmos pontos da pose (a hitbox e os golpes são os mesmos do Xeno)
# =====================================================================
def desenhar_indominus(l, tela, p, branco):
    s = l.s
    pele, sombra, listra = (226, 224, 216), (182, 180, 172), (84, 86, 94)
    barriga, borda, escuro = (242, 240, 232), (8, 8, 12), (150, 148, 140)
    if branco:
        pele = sombra = listra = barriga = escuro = (245, 245, 250)

    def Q(pt):  # ponto da pose -> tela
        return Pt(l, pt[0], pt[1])

    def poly(pts, cor, contorno=True):
        tela_pts = [Q(q) for q in pts]
        if contorno:
            pygame.draw.polygon(tela, borda, tela_pts)
            meio = (sum(x for x, _ in tela_pts) / len(tela_pts), sum(y for _, y in tela_pts) / len(tela_pts))
            k = max(0.0, 1 - 1.6 * s / max(8.0, max(abs(x - meio[0]) + abs(y - meio[1]) for x, y in tela_pts)))
            pygame.draw.polygon(tela, cor, [(meio[0] + (x - meio[0]) * k, meio[1] + (y - meio[1]) * k)
                                            for x, y in tela_pts])
        else:
            pygame.draw.polygon(tela, cor, tela_pts)

    def osso(a, b, w1, w2, cor):  # um pedaço grosso (coxa, canela, pescoço...) de a até b
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        poly([(a[0] + nx * w1, a[1] + ny * w1), (b[0] + nx * w2, b[1] + ny * w2),
              (b[0] - nx * w2, b[1] - ny * w2), (a[0] - nx * w1, a[1] - ny * w1)], cor)

    def mais_p(a, b, k):
        return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)

    def bola(pt, r, cor, contorno=True):  # junta redonda (pra não ficar tudo quadrado)
        c = Q(pt)
        if contorno:
            pygame.draw.circle(tela, borda, (int(c[0]), int(c[1])), max(2, int((r + 1.6) * s)))
        pygame.draw.circle(tela, cor, (int(c[0]), int(c[1])), max(1, int(r * s)))

    qd, pc, cb = p["qd"], p["pc"], p["cb"]

    # a CAUDA grossa (mesmos pontos do rabo do Xeno), com listras
    cauda = pontos_cauda(l, p)

    def gomo(i, folga):  # um pedaço da cauda (folga > 0 = o contorno, um pouco maior)
        a, b = cauda[i], cauda[i + 1]
        w1, w2 = max(1.5, 11 - i * 0.8) + folga, max(1.2, 11 - (i + 1) * 0.8) + folga
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        ex, ey = dx / n * folga * 0.5, dy / n * folga * 0.5  # (encosta no próximo: sem fresta)
        return [Q((a[0] + nx * w1 - ex, a[1] + ny * w1 - ey)), Q((b[0] + nx * w2 + ex, b[1] + ny * w2 + ey)),
                Q((b[0] - nx * w2 + ex, b[1] - ny * w2 + ey)), Q((a[0] - nx * w1 - ex, a[1] - ny * w1 - ey))]

    for i in range(len(cauda) - 1):  # primeiro o contorno da cauda inteira, depois as cores (fica lisa)
        pygame.draw.polygon(tela, borda, gomo(i, 1.6))
    for i in range(len(cauda) - 1):
        pygame.draw.polygon(tela, listra if i % 3 == 1 else pele, gomo(i, 0.3))

    def perna(pe, joelho, cor):
        tornozelo = (p[pe][0] - 2, p[pe][1] + 6)
        bola(p[joelho], 5.5, cor)
        osso(qd, p[joelho], 11, 6, cor)  # coxa forte
        bola(qd, 10.5, cor, False)
        osso(p[joelho], tornozelo, 5, 3, cor)
        bola(p[joelho], 4.5, cor, False)
        for k, dx in enumerate((10, 13, 9)):  # o pé com 3 garras
            dedo = (tornozelo[0] + dx, p[pe][1] + (0 if k != 1 else 1))
            osso(tornozelo, dedo, 2.4, 1.4, cor)
            pygame.draw.line(tela, borda, Q(dedo), Q((dedo[0] + 3, dedo[1] - 1)), max(1, int(1.6 * s)))
        osso((qd[0] + 2, qd[1] + 4), mais_p(qd, p[joelho], 0.5), 2, 1.5, listra)  # listra na coxa

    def braco(cot, mao, cor):
        ombro = (pc[0] - 2, pc[1] - 8)
        cotovelo = mais_p(ombro, p[cot], 0.7)
        punho = mais_p(cotovelo, p[mao], 0.55)
        osso(ombro, cotovelo, 3, 2.4, cor)
        osso(cotovelo, punho, 2.4, 1.6, cor)
        for dy in (1.5, -1.5):  # 2 garras
            pygame.draw.line(tela, borda, Q(punho), Q((punho[0] + 5, punho[1] + dy - 2)), max(1, int(1.6 * s)))

    perna("pt", "jt", sombra)
    braco("ct", "mt", sombra)
    # o CORPO (do quadril até o peito)
    dx, dy = pc[0] - qd[0], pc[1] - qd[1]
    n = math.hypot(dx, dy) or 1
    nx, ny = -dy / n, dx / n
    corpo = [(qd[0] + nx * 14 - dx * 0.15, qd[1] + ny * 14 - dy * 0.15), (pc[0] + nx * 12, pc[1] + ny * 12),
             (pc[0] + dx * 0.25, pc[1] + dy * 0.25), (pc[0] - nx * 11, pc[1] - ny * 11),
             (qd[0] - nx * 12, qd[1] - ny * 12), (qd[0] - dx * 0.3, qd[1] - dy * 0.3)]
    bola(qd, 13, pele)
    bola(pc, 11.5, pele)
    poly(corpo, pele)
    bola(qd, 11.2, pele, False)  # (arredonda o quadril e o peito por cima das quinas)
    bola(pc, 9.8, pele, False)
    poly([(pc[0] - nx * 9, pc[1] - ny * 9), (qd[0] - nx * 9, qd[1] - ny * 9),
          (qd[0] - nx * 4, qd[1] - ny * 4), (pc[0] - nx * 4, pc[1] - ny * 4)], barriga, False)  # a barriga clara
    for k in (0.15, 0.4, 0.65, 0.9):  # as listras escuras nas costas
        a = (qd[0] + dx * k + nx * 13, qd[1] + dy * k + ny * 13)
        b = (qd[0] + dx * (k - 0.12) + nx * 3, qd[1] + dy * (k - 0.12) + ny * 3)
        osso(a, b, 1.8, 0.8, listra)
    # o PESCOÇO e a CABEÇA (com a boca que abre na mordida e no ultimate)
    bola((cb[0] - 2, cb[1]), 7.5, pele)
    osso((pc[0] + 2, pc[1] + 2), (cb[0] - 2, cb[1]), 9, 7.5, pele)
    bola((pc[0] + 2, pc[1] + 2), 8.4, pele, False)
    abre = boca_k(l) * 8 + (5 if l.estado == "ataque" and l.nome_golpe in ("xeno_cospe", "xeno_garras") else 0)
    hx, hy = cb
    cabeca = [(hx - 7, hy + 3), (hx - 5, hy + 7), (hx - 1, hy + 9.5), (hx + 6, hy + 10.5), (hx + 12, hy + 9.5),
              (hx + 18, hy + 7), (hx + 23, hy + 5), (hx + 27, hy + 3.2), (hx + 29.5, hy + 1.2), (hx + 29.5, hy - 0.4),
              (hx + 27, hy - 1.2), (hx + 4, hy - 1.2), (hx - 4, hy - 2.6), (hx - 7, hy - 1)]  # (crânio arredondado)
    queixo = [(hx - 2, hy - 1), (hx + 26, hy - 2 - abre * 0.4), (hx + 25.5, hy - 4 - abre * 0.8),
              (hx + 22, hy - 6 - abre), (hx + 10, hy - 7.5 - abre * 0.6), (hx + 2, hy - 6.5 - abre * 0.3),
              (hx - 2, hy - 4)]
    poly(queixo, sombra)
    for i in range(5):  # dentes de baixo
        x = hx + 6 + i * 4
        pygame.draw.polygon(tela, (250, 250, 240), [Q((x, hy - 2 - abre * 0.4 * (i / 5))),
                                                    Q((x + 2, hy - 2 - abre * 0.4 * (i / 5))),
                                                    Q((x + 1, hy + 1 - abre * 0.4 * (i / 5)))])
    poly(cabeca, pele)
    for i in range(6):  # dentes de cima
        x = hx + 5 + i * 4
        pygame.draw.polygon(tela, (250, 250, 240), [Q((x, hy - 1)), Q((x + 2, hy - 1)), Q((x + 1, hy - 4))])
    poly([(hx + 4, hy + 9.6), (hx + 9, hy + 12.4), (hx + 15, hy + 9.6), (hx + 10, hy + 10.6)], listra)  # crista
    for i in range(3):  # listras na cabeça
        osso((hx - 4 + i * 5, hy + 7), (hx - 1 + i * 5, hy + 2), 1, 0.6, listra)
    olho = Q((hx + 12, hy + 5))
    pygame.draw.circle(tela, borda, (int(olho[0]), int(olho[1])), max(2, int(2.6 * s)))
    pygame.draw.circle(tela, (240, 240, 240) if branco else (230, 30, 30), (int(olho[0]), int(olho[1])),
                       max(1, int(1.8 * s)))
    pygame.draw.circle(tela, borda, (int(olho[0] + 0.6 * s), int(olho[1])), max(1, int(0.8 * s)))
    # os espinhos (osteodermos) nas costas, do pescoço até a cauda
    ux, uy = dx / n, dy / n  # (ao longo das costas)
    for k in range(6):  # cada espinho sai pra FORA das costas (na direção da curva), inclinado pra trás
        b = mais_p((pc[0] + nx * 10.5, pc[1] + ny * 10.5), (qd[0] + nx * 12.5, qd[1] + ny * 12.5), k / 5)
        alto = 6.5 - abs(k - 2.5) * 0.9
        poly([(b[0] + ux * 2.6, b[1] + uy * 2.6), (b[0] + nx * alto - ux * 2.2, b[1] + ny * alto - uy * 2.2),
              (b[0] - ux * 2.6, b[1] - uy * 2.6)], escuro)
    perna("pf", "jf", pele)
    braco("cf", "mf", pele)


def desenhar_xeno(l, tela, p, branco):
    if l.f.get("estilo") == "indominus":  # INDOMINUS REX: o desenho inteiro é outro (a hitbox não muda)
        return desenhar_indominus(l, tela, p, branco)
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
    na_cabeca = CABECA.desenhar(tela, cb, cima, esc, espelho, perto_v)
    if l.f.get("estilo") == "indominus" and not branco:  # INDOMINUS: os chifrinhos em cima do olho
        for x0 in (11.0, 13.2):
            pts = [na_cabeca(x0, 3.6), na_cabeca(x0 + 1.2, 1.6), na_cabeca(x0 + 1.8, 3.6)]
            pygame.draw.polygon(tela, PALETA["k"], pts)
            pygame.draw.polygon(tela, (96, 98, 106), [na_cabeca(x0 + 0.4, 3.4), na_cabeca(x0 + 1.2, 2.2),
                                                      na_cabeca(x0 + 1.5, 3.4)])
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
