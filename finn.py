"""FINN: o mago (criado pelo Gomes).

Aparência: mago de D&D, roupas roxas/pretas, bota roxa, roupa azul por baixo do manto, barba branca e longa.
Se materializa com magia, dos pés à cabeça.
  E      BOLA DE FOGO (20)
  Q      LEVITAÇÃO: magia de média distância que levanta o oponente (10, joga pra cima)
  R      magia amarela na ponta do cajado + barrage: 5 hits de 4
  SHIFT  empurrão mágico pra frente (5)
  Z      ULTIMATE: cria em cima da cabeça um MINI SOL e lança (40)
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

POSES_FINN = {
    "parado": dict(pt=(-20, 0), jt=(-14, 28), pf=(20, 0), jf=(22, 28), qd=(0, 54), pc=(2, 90), cb=(4, 108),
                   ct=(-10, 70), mt=(-6, 56), cf=(18, 74), mf=(28, 82)),
    "andar1": dict(pt=(-24, 2), jt=(-14, 28), pf=(24, 0), jf=(26, 28), qd=(0, 52), pc=(2, 88), cb=(4, 106),
                   ct=(-12, 68), mt=(-6, 54), cf=(18, 72), mf=(28, 80)),
    "andar2": dict(pt=(4, 10), jt=(14, 32), pf=(2, 0), jf=(10, 30), qd=(0, 56), pc=(2, 92), cb=(4, 110),
                   ct=(-10, 72), mt=(-6, 58), cf=(18, 76), mf=(28, 84)),
    "andar3": dict(pt=(22, 0), jt=(26, 28), pf=(-22, 2), jf=(-12, 28), qd=(0, 52), pc=(2, 88), cb=(4, 106),
                   ct=(-8, 68), mt=(-4, 54), cf=(18, 72), mf=(28, 80)),
    "andar4": dict(pt=(2, 0), jt=(10, 30), pf=(4, 10), jf=(14, 32), qd=(0, 56), pc=(2, 92), cb=(4, 110),
                   ct=(-10, 72), mt=(-6, 58), cf=(18, 76), mf=(28, 84)),
    "f_carrega": dict(pt=(-24, 0), jt=(-16, 26), pf=(22, 0), jf=(24, 28), qd=(-2, 52), pc=(-4, 88), cb=(-6, 106),
                      ct=(8, 80), mt=(22, 86), cf=(10, 78), mf=(22, 84)),
    "f_lanca": dict(pt=(-28, 0), jt=(-18, 26), pf=(26, 0), jf=(28, 28), qd=(0, 50), pc=(8, 86), cb=(12, 104),
                    ct=(22, 88), mt=(48, 92), cf=(6, 72), mf=(12, 58)),
    "f_levita": dict(pt=(-22, 0), jt=(-16, 28), pf=(22, 0), jf=(24, 28), qd=(0, 54), pc=(4, 90), cb=(8, 108),
                     ct=(-10, 72), mt=(-4, 58), cf=(22, 96), mf=(38, 116)),
    "f_cajado_a": dict(pt=(-28, 0), jt=(-18, 26), pf=(28, 0), jf=(30, 28), qd=(0, 48), pc=(10, 84), cb=(16, 100),
                       ct=(-6, 72), mt=(4, 80), cf=(26, 84), mf=(52, 86)),
    "f_cajado_b": dict(pt=(-28, 0), jt=(-18, 26), pf=(28, 0), jf=(30, 28), qd=(0, 48), pc=(8, 84), cb=(14, 100),
                       ct=(-6, 74), mt=(2, 84), cf=(24, 96), mf=(44, 112)),
    "f_empurra": dict(pt=(-34, 6), jt=(-18, 28), pf=(26, 0), jf=(28, 28), qd=(0, 48), pc=(20, 82), cb=(28, 98),
                      ct=(30, 80), mt=(50, 84), cf=(-6, 74), mf=(-24, 70)),
    "f_ult": dict(pt=(-24, 0), jt=(-18, 28), pf=(24, 0), jf=(20, 28), qd=(0, 56), pc=(2, 92), cb=(2, 110),
                  ct=(-10, 108), mt=(-6, 128), cf=(10, 108), mf=(8, 128)),
    "f_ult_lanca": dict(pt=(-32, 0), jt=(-22, 26), pf=(28, 0), jf=(30, 28), qd=(-2, 50), pc=(8, 88), cb=(12, 106),
                        ct=(26, 98), mt=(50, 104), cf=(28, 100), mf=(52, 108)),
    "f_vitoria": dict(pt=(-20, 0), jt=(-16, 28), pf=(20, 0), jf=(18, 28), qd=(0, 56), pc=(2, 92), cb=(4, 110),
                      ct=(-12, 74), mt=(-22, 84), cf=(14, 102), mf=(20, 126)),
}
proporcionar(POSES_FINN)

ROXO_MAGIA = (190, 120, 255)
AMARELO_MAGIA = (255, 230, 110)


# =====================================================================
# O cajado (na mão da frente)
# =====================================================================
def cajado(l, p=None):
    """(ponta de baixo, ponta de cima) do cajado. Funciona no desenho pequeno e no grande."""
    p = p or l.pose_vista or l.pose_atual()
    esc = l.s / S_REF
    c, m = l.ponto(p, "cf"), l.ponto(p, "mf")
    apontado = l.estado == "ataque" and l.nome_golpe in ("finn_cajado", "finn_levita", "finn_empurra") \
        and l.t >= 6 or l.memo.get("cajado_frente")
    if apontado:  # apontando o cajado pra frente (pelo braço)
        (dx, dy), _ = eixos(c, m)
    else:  # em pé, do lado do corpo (inclina junto se o corpo girar)
        a = l.angulo * l.lado()
        dx, dy = math.sin(a), -math.cos(a)
    return (m[0] - dx * 34 * esc, m[1] - dy * 34 * esc), (m[0] + dx * 30 * esc, m[1] + dy * 30 * esc)


def chapeu_gandalf(tela, P, esc):
    """GANDALF (roupa do Finn): a aba larga do chapéu e a ponta entortada pra trás."""
    cinza, escuro, borda = (138, 138, 146), (104, 104, 112), (18, 12, 26)
    aba = [P(-4.5, 7.2), P(17.5, 7.2), P(17.5, 8.4), P(-4.5, 8.4)]
    pygame.draw.polygon(tela, borda, [P(-5.3, 6.4), P(18.3, 6.4), P(18.3, 9.2), P(-5.3, 9.2)])
    pygame.draw.polygon(tela, cinza, aba)
    pygame.draw.line(tela, escuro, P(-4.2, 8.2), P(17.2, 8.2), max(1, int(esc * 0.6)))
    ponta = [P(5.6, 0.6), P(7.4, 0.6), P(2.0, -4.6), P(0.6, -3.4)]  # a ponta caindo pra trás
    pygame.draw.polygon(tela, borda, ponta)
    pygame.draw.polygon(tela, cinza, [P(5.8, 0.8), P(7.0, 0.8), P(2.2, -4.0), P(1.2, -3.2)])


def chapeu_bruxo(tela, P, esc):
    """FINN BRUXO (Halloween): chapéu de bruxa roxo, bem alto e TORTO, com faixa laranja."""
    roxo, escuro, borda, laranja = (90, 52, 120), (58, 32, 80), (18, 12, 26), (240, 130, 30)
    pygame.draw.polygon(tela, borda, [P(-2.6, 6.2), P(15.6, 6.2), P(15.6, 9.0), P(-2.6, 9.0)])
    pygame.draw.polygon(tela, escuro, [P(-1.8, 7.0), P(14.8, 7.0), P(14.8, 8.2), P(-1.8, 8.2)])
    cone = [P(1.6, 7.2), P(11.6, 7.2), P(8.6, 0.0), P(7.4, -6.0), P(11.8, -9.4), P(5.6, -6.4), P(4.2, 0.4)]
    pygame.draw.polygon(tela, borda, cone)
    pygame.draw.polygon(tela, roxo, [P(2.4, 6.6), P(10.8, 6.6), P(8.0, 0.2), P(7.0, -5.4), P(10.0, -8.2),
                                     P(6.0, -5.8), P(4.8, 0.6)])
    pygame.draw.polygon(tela, laranja, [P(2.2, 6.6), P(11.0, 6.6), P(10.4, 5.2), P(2.8, 5.2)])  # a faixa
    pygame.draw.polygon(tela, (255, 220, 90), [P(6.0, 5.0), P(7.6, 5.0), P(7.6, 6.8), P(6.0, 6.8)], 1)  # a fivela


def desenha_vassoura(tela, l, p, esc):
    """FINN BRUXO: a VASSOURA no lugar do cajado (cabo de madeira e as palhas embaixo)."""
    baixo, cima = cajado(l, p)
    w = max(2, int(2.4 * esc))
    pygame.draw.line(tela, PALETA["k"], baixo, cima, w + 2)
    pygame.draw.line(tela, (130, 86, 46), baixo, cima, w)
    (dx, dy), _ = eixos(cima, baixo)  # (de cima pra baixo)
    nx, ny = -dy, dx
    base = (baixo[0] - dx * 12 * esc, baixo[1] - dy * 12 * esc)
    ponta = (baixo[0] + dx * 6 * esc, baixo[1] + dy * 6 * esc)
    palha = [(base[0] + nx * 2.4 * esc, base[1] + ny * 2.4 * esc), (ponta[0] + nx * 7 * esc, ponta[1] + ny * 7 * esc),
             (ponta[0] - nx * 7 * esc, ponta[1] - ny * 7 * esc), (base[0] - nx * 2.4 * esc, base[1] - ny * 2.4 * esc)]
    pygame.draw.polygon(tela, PALETA["k"], palha)
    meio = (sum(q[0] for q in palha) / 4, sum(q[1] for q in palha) / 4)
    pygame.draw.polygon(tela, (214, 172, 84), [(x * 0.86 + meio[0] * 0.14, y * 0.86 + meio[1] * 0.14) for x, y in palha])
    for k in (-0.6, -0.2, 0.2, 0.6):  # os fios de palha
        pygame.draw.line(tela, (160, 120, 50), (base[0] + nx * k * 3 * esc, base[1] + ny * k * 3 * esc),
                         (ponta[0] + nx * k * 9 * esc, ponta[1] + ny * k * 9 * esc), max(1, int(esc * 0.5)))
    amarra = (base[0] + dx * 2 * esc, base[1] + dy * 2 * esc)  # a amarração
    pygame.draw.line(tela, (120, 50, 120), (amarra[0] + nx * 3.4 * esc, amarra[1] + ny * 3.4 * esc),
                     (amarra[0] - nx * 3.4 * esc, amarra[1] - ny * 3.4 * esc), max(2, int(1.6 * esc)))


def desenha_cajado(tela, l, p, esc, branco):
    if l.f.get("estilo") == "bruxo" and not branco:
        return desenha_vassoura(tela, l, p, esc)
    baixo, cima = cajado(l, p)
    if l.f.get("estilo") == "gandalf" and not branco:  # GANDALF: cajado de madeira retorcida com luz branca
        w = max(2, int(2.6 * esc))
        pygame.draw.line(tela, PALETA["k"], baixo, cima, w + 2)
        pygame.draw.line(tela, (110, 74, 44), baixo, cima, w)
        (dx, dy), _ = eixos(baixo, cima)
        nx, ny = -dy, dx
        for k, (a, r) in enumerate(((0.0, 5), (1.6, 4), (3.4, 3))):  # os galhos enrolados em volta da luz
            ox = cima[0] + nx * math.cos(a) * r * esc + dx * math.sin(a) * r * esc
            oy = cima[1] + ny * math.cos(a) * r * esc + dy * math.sin(a) * r * esc
            pygame.draw.line(tela, PALETA["k"], cima, (ox, oy), max(2, int(2 * esc)))
            pygame.draw.line(tela, (130, 90, 56), cima, (ox, oy), max(1, int(1.2 * esc)))
        luz = AMARELO_MAGIA if l.estado == "ataque" and l.nome_golpe == "finn_cajado" else (250, 250, 255)
        brilho(tela, (int(cima[0]), int(cima[1])), int(9 * esc), luz, 120)
        pygame.draw.circle(tela, luz, (int(cima[0]), int(cima[1])), max(2, int(2.4 * esc)))
        return
    w = max(2, int(2.6 * esc))
    pygame.draw.line(tela, PALETA["k"], baixo, cima, w + 2)
    pygame.draw.line(tela, (240, 240, 240) if branco else (128, 84, 44), baixo, cima, w)
    gema = (110, 60, 200) if not branco else (240, 240, 240)
    if l.estado == "ataque" and l.nome_golpe == "finn_cajado":
        gema = AMARELO_MAGIA
    r = max(2, int(3 * esc))
    pygame.draw.circle(tela, PALETA["k"], (int(cima[0]), int(cima[1])), r + 1)
    pygame.draw.circle(tela, gema, (int(cima[0]), int(cima[1])), r)


# =====================================================================
# E: BOLA DE FOGO
# =====================================================================
def desenha_fogo(p, tela):
    t = p.t
    for i in range(6, 0, -1):  # rastro de fogo
        x = p.x - p.vx * i * 1.3
        y = p.y + math.sin(t * 0.7 + i) * 3
        r = int(p.raio * (1 - i / 8))
        cor = (255, int(90 + 20 * (6 - i)), 30)
        pygame.draw.circle(tela, cor, (int(x), int(y)), max(2, r))
    brilho(tela, (int(p.x), int(p.y)), int(p.raio * 2), (255, 140, 40), 90)
    r = p.raio + math.sin(t * 0.9) * 2
    pygame.draw.circle(tela, (255, 120, 30), (int(p.x), int(p.y)), int(r))
    pygame.draw.circle(tela, (255, 220, 100), (int(p.x), int(p.y)), int(r * 0.65))
    pygame.draw.circle(tela, (255, 255, 230), (int(p.x), int(p.y)), int(r * 0.3))


def solta_fogo(l, jogo):
    baixo, cima = cajado(l)
    for _ in range(10):
        a = random.uniform(0, math.tau)
        jogo.faiscas.append([l.x + 50 * l.s * l.dir, l.y - 84 * l.s, math.cos(a) * 3, math.sin(a) * 3, 12,
                             random.choice(((255, 200, 80), (255, 120, 40))), 5])
    som.tocar("explosao", 0.4)


# =====================================================================
# Q: LEVITAÇÃO (magia de média distância)
# =====================================================================
L_MIN, L_MAX = 140, 330        # onde a magia pode aparecer (distância à frente dele)
L_TRAVA, L_INI, L_FIM = 14, 22, 46


def levitar(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t < L_TRAVA:  # a magia segue o oponente... e trava um pouquinho antes de explodir pra cima
        dist = max(L_MIN, min(L_MAX, (outro.x - l.x) * l.dir))
        m["alvo_x"] = l.x + l.dir * dist
    rel = (m["alvo_x"] - l.x) * l.dir / l.s
    m["caixa"] = (rel - 24, 0, rel + 24, 150)
    if t == L_INI:
        som.tocar("puf", 0.6)
        som.tocar("vento")
    if t >= L_FIM:
        return "fim"


def levitar_efeito(l, tela):
    m = l.memo
    if "alvo_x" not in m or l.t < 4:
        return
    t = l.t
    x = m["alvo_x"]
    s = l.s
    pulso = 0.7 + 0.3 * math.sin(t * 0.5)
    r = int(36 * s)
    pygame.draw.ellipse(tela, ROXO_MAGIA, (x - r, CHAO - 9 * s, 2 * r, 18 * s), 3)
    pygame.draw.ellipse(tela, (230, 200, 255), (x - r * 0.6 * pulso, CHAO - 5 * s, 1.2 * r * pulso, 10 * s), 2)
    for k in range(6):  # runas girando
        a = t * 0.08 + k * math.tau / 6
        px, py = x + math.cos(a) * r * 0.8, CHAO + math.sin(a) * 6 * s
        pygame.draw.line(tela, (230, 200, 255), (px - 3, py), (px + 3, py), 2)
    if L_INI <= t < L_INI + 18:  # a coluna de magia subindo
        k = (t - L_INI) / 18
        alt = 170 * s * min(1, k * 3)
        coluna = pygame.Surface((int(2 * r), int(alt) + 2), pygame.SRCALPHA)
        coluna.fill((*ROXO_MAGIA, int(140 * (1 - k))))
        tela.blit(coluna, (x - r, CHAO - alt))
        for i in range(8):
            u = (t * 9 + i * 23) % int(alt + 1)
            pygame.draw.circle(tela, (240, 220, 255), (int(x - r * 0.8 + (i * 13) % (1.6 * r)), int(CHAO - u)), 2)


# =====================================================================
# R: CAJADO AMARELO + BARRAGE (5 hits)
# =====================================================================
B_INI, B_INTERVALO, B_HITS = 12, 7, 5


def barrage(l, outro, jogo):
    t = l.t
    l.vx = 1.0 * l.dir if B_INI <= t < B_INI + B_HITS * B_INTERVALO else 0
    if B_INI <= t < B_INI + B_HITS * B_INTERVALO and (t - B_INI) % B_INTERVALO == 0:
        som.tocar("vento", 0.5)
    l.fisica(jogo)
    if t >= B_INI + B_HITS * B_INTERVALO + 14:
        return "fim"


def barrage_efeito(l, tela):
    _, ponta = cajado(l)
    k = min(1, l.t / B_INI)
    brilho(tela, (int(ponta[0]), int(ponta[1])), int((8 + 14 * k) * l.s), AMARELO_MAGIA, int(120 + 80 * k))
    u = l.t - B_INI
    if 0 <= u < B_HITS * B_INTERVALO and u % B_INTERVALO < 3:  # risco amarelo em cada golpe
        pygame.draw.arc(tela, AMARELO_MAGIA, (ponta[0] - 30 * l.s, ponta[1] - 30 * l.s, 60 * l.s, 60 * l.s),
                        -1.2 if l.dir > 0 else 1.9, 1.2 if l.dir > 0 else 4.4, 3)


def barrage_quadros():
    q = [(0, "parado"), (B_INI - 4, "f_cajado_b")]
    for k in range(B_HITS):
        q.append((B_INI + k * B_INTERVALO + 2, "f_cajado_a"))
        q.append((B_INI + k * B_INTERVALO + 5, "f_cajado_b"))
    q.append((B_INI + B_HITS * B_INTERVALO + 14, "parado"))
    return q


# =====================================================================
# SHIFT: EMPURRÃO MÁGICO pra frente
# =====================================================================
S_INI, S_FIM = 6, 22


def empurrao(l, outro, jogo):
    t = l.t
    m = l.memo
    if l.acertou:
        m["parou"] = True
    if t < S_INI:
        l.vx = 0
    elif t < S_FIM and "parou" not in m:
        l.vx = 12 * l.dir
        if t % 2 == 0:
            jogo.faiscas.append([l.x - 30 * l.s * l.dir, l.y - random.uniform(20, 110) * l.s, -l.dir * 2, 0, 14,
                                 random.choice((ROXO_MAGIA, (230, 200, 255))), 4])
    else:
        l.vx *= 0.7
    l.fisica(jogo)
    if t >= S_FIM + 12:
        return "fim"


# =====================================================================
# Z: ULTIMATE — o MINI SOL
# =====================================================================
U_LANCA, U_FIM = 72, 140
SOL_RAIO = 44


def desenha_sol(tela, pos, r, t):
    x, y = int(pos[0]), int(pos[1])
    if r < 2:
        return
    brilho(tela, (x, y), int(r * 2.3), (255, 140, 40), 70)
    brilho(tela, (x, y), int(r * 1.6), (255, 190, 80), 110)
    for i in range(14):  # labaredas em volta
        a = i * math.tau / 14 + t * 0.05
        comp = r * (1.15 + 0.2 * math.sin(t * 0.4 + i * 1.7))
        pygame.draw.line(tela, (255, 150, 40), (x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8),
                         (x + math.cos(a) * comp, y + math.sin(a) * comp), max(2, int(r / 6)))
    pygame.draw.circle(tela, (255, 120, 30), (x, y), int(r))
    pygame.draw.circle(tela, (255, 200, 80), (x, y), int(r * 0.78))
    pygame.draw.circle(tela, (255, 245, 190), (x, y), int(r * 0.45))
    for i in range(3):  # manchas do sol
        a = t * 0.03 + i * 2.1
        pygame.draw.circle(tela, (255, 160, 50), (int(x + math.cos(a) * r * 0.5), int(y + math.sin(a) * r * 0.4)),
                           max(1, int(r * 0.12)))


class Sol(Projetil):
    """O Mini Sol: vai em linha reta na direção do oponente."""

    def __init__(self, dono, x, y, alvo):
        super().__init__(dono, x, y, dono.dir, GOLPES["finn_sol"])
        dx, dy = alvo[0] - x, alvo[1] - y
        d = math.hypot(dx, dy) or 1
        v = self.golpe["vel"]
        self.vx, self.vy = dx / d * v, dy / d * v
        self.raio = int(SOL_RAIO * dono.s / 1.4)

    def rect(self):
        r = self.raio * 0.8
        return pygame.Rect(self.x - r, self.y - r, 2 * r, 2 * r)

    def update(self):
        self.t += 1
        self.x += self.vx
        self.y += self.vy
        if self.y >= CHAO - self.raio * 0.3 or self.x < -80 or self.x > LARGURA + 80:
            self.vivo = False

    def desenhar(self, tela):
        desenha_sol(tela, (self.x, self.y), self.raio, self.t + 100)


def centro_sol(l):
    return l.x - 4 * l.s * l.dir, l.y - 190 * l.s


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t % 12 == 0 and t < U_LANCA:
        som.tocar("carga", 0.5)
    if t == U_LANCA:  # LANÇA o Mini Sol
        x, y = centro_sol(l)
        m["sol"] = Sol(l, x, y, (outro.x, outro.y - 60 * outro.s))
        jogo.projeteis.append(m["sol"])
        som.tocar("foguete")
        jogo.tremer(10)
    s = m.get("sol")
    if s and not s.vivo and "explodiu" not in m:  # explodiu (no oponente ou no chão)
        m["explodiu"] = t
        som.tocar("explosao")
        jogo.tremer(18)
        for _ in range(40):
            a = random.uniform(0, math.tau)
            v = random.uniform(3, 12)
            jogo.faiscas.append([s.x, s.y, math.cos(a) * v, math.sin(a) * v - 2, random.randint(16, 30),
                                 random.choice(((255, 230, 140), (255, 150, 40), (255, 90, 30))), 7])
        fumaca(jogo, s.x, min(s.y, CHAO - 10), 10, (120, 100, 90), 4, -1.5)
    if t >= U_FIM or ("explodiu" in m and t - m["explodiu"] > 20):
        return "fim"


def ultimate_efeito(l, tela):
    t = l.t
    if t >= U_LANCA:
        return
    k = suave(min(1, t / (U_LANCA - 10)))
    r = SOL_RAIO * l.s / 1.4 * k + math.sin(t * 0.6) * 2 * k
    x, y = centro_sol(l)
    for i in range(6):  # fogo entrando no sol
        a = t * 0.2 + i * math.tau / 6
        d = (1 - (t * 3 + i * 9) % 40 / 40) * 120 * l.s
        pygame.draw.circle(tela, (255, 170, 60), (int(x + math.cos(a) * d), int(y + math.sin(a) * d)), 3)
    desenha_sol(tela, (x, y), r, t)


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


_registra("finn_fogo", ini=18, ativo=1, rec=24, proj=True, raio=15, vel=8, dano=20, hit=22, defe=14, emp=5,
          nivel="medio", ia="longe", desenho_proj=desenha_fogo, ao_usar=solta_fogo,
          quadros=[(0, "parado"), (10, "f_carrega"), (17, "f_lanca"), (30, "f_lanca"), (43, "parado")])
_registra("finn_levita", ini=L_INI, ativo=8, rec=L_FIM - L_INI - 8, janelas=((L_INI, L_INI + 8),), dano=12, hit=20,
          defe=10, emp=0, nivel="medio", lanca=15, logica=levitar, efeito=levitar_efeito, ia="medio",
          quadros=[(0, "parado"), (8, "f_levita"), (L_FIM - 8, "f_levita"), (L_FIM, "parado")])
_registra("finn_cajado", ini=B_INI, ativo=B_HITS * B_INTERVALO, rec=14,
          janelas=tuple((B_INI + k * B_INTERVALO, B_INI + k * B_INTERVALO + 3) for k in range(B_HITS)),
          caixa=(10, 40, 92, 124), dano=5, hit=12, defe=8, emp=1, nivel="medio", logica=barrage,
          efeito=barrage_efeito, ia="perto", quadros=barrage_quadros())
_registra("finn_empurra", ini=S_INI, ativo=S_FIM - S_INI, rec=12, janelas=((S_INI, S_FIM),), caixa=(0, 20, 60, 120),
          dano=7, hit=16, defe=10, emp=4, nivel="medio", logica=empurrao, ia="medio", som="vento",
          quadros=[(0, "parado"), (S_INI - 1, "f_empurra"), (S_FIM, "f_empurra"), (S_FIM + 12, "parado")])
_registra("finn_sol", ini=0, ativo=1, rec=0, proj=True, raio=40, vel=9, dano=40, hit=40, defe=20, emp=6,
          nivel="medio", derruba=True, voo=(6, 10), ultimate=True, varios=True, atravessa=True)
_registra("finn_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=ultimate, efeito=ultimate_efeito, ia="ultimate",
          quadros=[(0, "parado"), (10, "f_ult"), (U_LANCA - 2, "f_ult"), (U_LANCA + 3, "f_ult_lanca"),
                   (U_LANCA + 30, "f_ult_lanca"), (U_LANCA + 46, "parado")])
GOLPES["finn_ultimate"]["total"] = 9999

GOLPES_FINN = {"E": "finn_fogo", "Q": "finn_levita", "R": "finn_cajado", "SHIFT": "finn_empurra",
               "Z": "finn_ultimate"}

# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  R r v manto roxo (claro -> escuro)  x X preto  a A roupa azul de baixo  p P q pele
#   h H barba/cabelo branco  e olho  o ouro  b B bota roxa
PALETA = {
    "k": (18, 12, 26), "R": (150, 96, 200), "r": (104, 58, 150), "v": (64, 32, 100), "x": (28, 22, 36),
    "X": (66, 56, 80), "a": (60, 100, 200), "A": (110, 150, 236), "p": (236, 196, 160), "P": (204, 160, 124),
    "q": (150, 108, 80), "h": (224, 224, 230), "H": (250, 250, 255), "e": (20, 20, 24), "o": (226, 186, 70),
    "b": (120, 64, 170), "B": (80, 40, 120),
}
S_REF = 1.36 / 3

TRONCO = Peca([
    "...kkkkkkkk...",
    "..kxXrrrrXxk..",
    ".kxrRraarrrxk.",
    ".kxRrraarrrvk.",
    ".kxRrraArrrvk.",
    ".kxrrraArrrvk.",
    ".kxrrraarrrvk.",
    ".kxrrraArrrvk.",
    ".kxrrraarrrvk.",
    "..kxrraArrvk..",
    "..kxrraarrvk..",
    "..kxrraArrvk..",
    "..kkoooooookk.",
    "..kxooXooooxk.",
    "..kxrraarrrvk.",
    "..kxrraArrrvk.",
    "..krrraarrrvk.",
    "..krrraarrrvk.",
    "..kRrraArrvvk.",
    "..kRrraarrvvk.",
    "..krrraarrvvk.",
    "...krraarvvk..",
    "....kkkkkkk...",
], PALETA, a=(7, 20), b=(7, 1))

TRONCO_COSTAS = Peca([
    "...kkkkkkkk...",
    "..kxXrrrrXxk..",
    ".kxrRrrrrrrxk.",
    ".kxRrrrrrrrvk.",
    ".kxRrrrrrrrvk.",
    ".kxrrrrrrrrvk.",
    ".kxrrrrrrrrvk.",
    ".kxrrrrrrrrvk.",
    ".kxrrrrrrrrvk.",
    "..kxrrrrrrvk..",
    "..kxrrrrrrvk..",
    "..kxrrrrrrvk..",
    "..kkoooooookk.",
    "..kxoooooooxk.",
    "..kxrrrrrrrvk.",
    "..kxrrrrrrrvk.",
    "..krrrrrrrrvk.",
    "..krrrrrrrrvk.",
    "..kRrrrrrrvvk.",
    "..kRrrrrrrvvk.",
    "..krrrrrrrvvk.",
    "...krrrrrvvk..",
    "....kkkkkkk...",
], PALETA, a=(7, 20), b=(7, 1))

CABECA = Peca([
    "......kk.....",
    ".....kRrk....",
    ".....krrk....",
    "....kRrrrk...",
    "....krrrvk...",
    "...kRrrrrvk..",
    "...krooorvk..",
    "kkkkkkkkkkkkk",
    "..khpppppepk.",
    "..khpppppppk.",
    "..khhpppPppk.",
    "..khhhhhhhhk.",
    "...khhhhhhHk.",
    "...khhHhhhk..",
    "....khhhhhk..",
    "....khhHhk...",
    ".....khhhk...",
    ".....khhk....",
    "......kk.....",
], PALETA, a=(6, 9), b=(6, 0), estica=False)

CABECA_COSTAS = Peca([
    "......kk.....",
    ".....kRrk....",
    ".....krrk....",
    "....kRrrrk...",
    "....krrrvk...",
    "...kRrrrrvk..",
    "...krooorvk..",
    "kkkkkkkkkkkkk",
    "..khhhhhhhhk.",
    "..khhhhhhhhk.",
    "..khhhhhhhhk.",
    "...khhhhhhk..",
    "....kpppppk..",
    ".....kkkkk...",
], PALETA, a=(6, 9), b=(6, 0), estica=False)

COXA = Peca([
    ".kkkkkk.",
    "kxXxxxxk",
    "kXxxxxxk",
    "kxxxxxxk",
    "kxxxxxxk",
    "kxxxxxxk",
    "kxxxxxxk",
    "kxxxxxxk",
    "kxxxxxxk",
    ".kxxxxk.",
    ".kxxxxk.",
    ".kxxxxk.",
    "..kxxk..",
    "..kkkk..",
], PALETA, a=(3, 0), b=(3, 13))

CANELA = Peca([
    ".kkkkk.",
    "kxXxxxk",
    "kxxxxxk",
    "kxxxxxk",
    "kxxxxxk",
    "kkkkkkk",
    "kbbbbBk",
    "kbBbbBk",
    "kbbbbBk",
    "kbbbbBk",
    "kbbbbBk",
    "kbbbbBk",
    ".kbbBk.",
    "..kkk..",
], PALETA, a=(3, 0), b=(3, 13))

BOTA = Peca([
    ".kkkkk.....",
    "kbbbbBkkk..",
    "kbbbbbbbBkk",
    "kBBBBBBBBBk",
    "kkkkkkkkkkk",
], PALETA, a=(3, 1), b=(9, 1), estica=False)

BRACO = Peca([
    ".kkkkk.",
    "krRrrvk",
    "krRrrvk",
    "krrrrvk",
    "krrrrvk",
    "krrrrvk",
    "krrrvvk",
    "krrrvvk",
    "krrvvvk",
    ".kkkkk.",
], PALETA, a=(3, 0), b=(3, 9))

ANTEBRACO = Peca([
    ".kkkkk.",
    "krRrrvk",
    "krrrrvk",
    "krrrrvk",
    "krrrvvk",
    "kRrrvvk",
    "krrrvvk",
    "kxxxxxk",
    "kxXxxxk",
    ".kkkkk.",
], PALETA, a=(3, 0), b=(3, 9))

MAO = Peca([
    ".kkkk.",
    "kpPPqk",
    "kpPpqk",
    "kqqqqk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 4), estica=False)


def _cor(letra):
    """A cor da paleta seguindo a roupa (o manto é desenhado por código)."""
    import pecas
    return (pecas.TROCA or {}).get(letra, PALETA[letra])


def _manto(tela, P, esc, branco, var):
    """A saia do manto (cobre as pernas até a canela) com a roupa azul aparecendo no meio."""
    q, jt, jf = P("qd"), P("jt"), P("jf")
    escuro = var == "escuro"
    baixo_y = max(jt[1], jf[1]) + 8 * esc
    esq = min(jt[0], jf[0], q[0] - 6 * esc) - 4 * esc
    dir_ = max(jt[0], jf[0], q[0] + 6 * esc) + 4 * esc
    pts = [(q[0] - 6 * esc, q[1] - 2 * esc), (q[0] + 6 * esc, q[1] - 2 * esc), (dir_, baixo_y), (esq, baixo_y)]
    cor = (240, 240, 240) if branco else _cor("r")
    pygame.draw.polygon(tela, cor, pts)
    if not branco:  # (as cores seguem a roupa: antes ficava roxo em todas)
        pygame.draw.line(tela, _cor("v"), pts[1], pts[2], max(1, int(2 * esc)))
        pygame.draw.line(tela, _cor("R"), pts[0], pts[3], max(1, int(1 * esc)))
        pygame.draw.line(tela, _cor("x"), pts[3], pts[2], max(1, int(2 * esc)))  # barra preta
        meio_baixo = ((pts[2][0] + pts[3][0]) / 2, baixo_y)
        pygame.draw.line(tela, _cor("a"), q, meio_baixo, max(1, int(2 * esc)))  # roupa azul por baixo


def finn_todo_quadro(l, jogo):
    """As passivas do Finn (ALQUIMIA e FEITIÇO DE CURA) rodam aqui."""
    import habilidades
    habilidades.finn_quadro(l, jogo)


def runas(tela, a, b, esc, t, branco):
    """RUNAS brilhando no braço (de a até b): 3 simbolozinhos que pulsam."""
    if branco:
        return
    brilho_ = 0.6 + 0.4 * math.sin(t * 0.1)
    cor = (int(255 * brilho_), int(230 * brilho_), int(110 * brilho_))
    for i, f in enumerate((0.25, 0.5, 0.75)):
        x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        r = 1.2 * esc
        if i == 0:  # um "V"
            pts = [(x - r, y - r), (x, y + r), (x + r, y - r)]
        elif i == 1:  # um "X"
            pygame.draw.line(tela, cor, (x - r, y - r), (x + r, y + r), max(1, int(0.6 * esc)))
            pts = [(x - r, y + r), (x + r, y - r)]
        else:  # um triângulo
            pts = [(x, y - r), (x + r, y + r), (x - r, y + r), (x, y - r)]
        pygame.draw.lines(tela, cor, False, pts, max(1, int(0.6 * esc)))


def cinto_alquimista(tela, l, p, esc, branco):
    """O LIVRO DE FEITIÇOS e as 3 POÇÕES pendurados no cinto."""
    def U(u):
        return l.ponto({"_": u}, "_")
    qd = p["qd"]
    k = (150, 150, 160) if branco else PALETA["k"]
    # o livro (do lado de trás do quadril)
    cantos = [U((qd[0] - 11, qd[1] + 3)), U((qd[0] - 4, qd[1] + 3)), U((qd[0] - 4, qd[1] - 7)), U((qd[0] - 11, qd[1] - 7))]
    pygame.draw.polygon(tela, k, cantos)
    capa = (245, 245, 250) if branco else (110, 60, 36)
    meio = (sum(c[0] for c in cantos) / 4, sum(c[1] for c in cantos) / 4)
    pygame.draw.polygon(tela, capa, [(x * 0.8 + meio[0] * 0.2, y * 0.8 + meio[1] * 0.2) for x, y in cantos])
    if not branco:
        pygame.draw.circle(tela, AMARELO_MAGIA, (round(meio[0]), round(meio[1])), max(1, int(1.1 * esc)))  # o fecho dourado
    # as poções (vermelha, azul, verde), na frente
    import habilidades
    for j, tipo in enumerate(habilidades.POCOES):
        x, y = U((qd[0] + 2 + j * 4, qd[1] - 4))
        cor = (245, 245, 250) if branco else habilidades.COR_POCAO[tipo]
        r = max(2, int(1.7 * esc))
        pygame.draw.circle(tela, k, (round(x), round(y + r)), r + max(1, int(0.6 * esc)))
        pygame.draw.circle(tela, cor, (round(x), round(y + r)), r)
        pygame.draw.line(tela, k, (x, y - r * 0.6), (x, y + r * 0.3), max(2, int(1.4 * esc)))  # gargalo
        pygame.draw.circle(tela, (255, 255, 255), (round(x - r * 0.35), round(y + r * 0.6)), max(1, r // 3))


def desenhar_finn(l, tela, p, branco):
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
        BOTA.desenhar(tela, e, mais(e, fr, 9), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    def braco(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)
        if var != "escuro":  # RUNAS brilhando no braço da frente
            runas(tela, c, m, esc, l.t, branco)

    longe, perto = (("cf", "mf", "pf", "jf"), ("ct", "mt", "pt", "jt")) if costas else \
        (("ct", "mt", "pt", "jt"), ("cf", "mf", "pf", "jf"))
    braco(longe[0], longe[1], longe_v)
    perna(longe[2], longe[3], longe_v)
    perna(perto[2], perto[3], perto_v)
    _manto(tela, P, esc, branco, perto_v)
    c, cb = P("pc"), P("cb")
    (TRONCO_COSTAS if costas else TRONCO).desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    cinto_alquimista(tela, l, p, esc, branco)
    u, _ = cabeca_eixos(c, cb, d)
    pygame.draw.line(tela, PALETA["k"], c, mais(cb, u, -3 * esc), max(3, int(5 * esc)))
    pygame.draw.line(tela, PALETA["P"] if not branco else (240, 240, 240), c, mais(cb, u, -3 * esc), max(1, int(3 * esc)))
    na_cabeca = (CABECA_COSTAS if costas else CABECA).desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    if l.f.get("estilo") == "gandalf" and not branco:
        chapeu_gandalf(tela, na_cabeca, esc)
    if l.f.get("estilo") == "bruxo" and not branco:
        chapeu_bruxo(tela, na_cabeca, esc)
    braco(perto[0], perto[1], perto_v)
    desenha_cajado(tela, l, p, esc, branco)
    efeitos_passiva(tela, l, p, esc, branco)


def efeitos_passiva(tela, l, p, esc, branco):
    """ALQUIMIA: o frasco na mão quando bebe + a aura da poção. FEITIÇO DE CURA: brilhinhos verdes subindo."""
    import habilidades
    x = l.extra
    if branco:
        return
    if x.get("bebendo", 0) > 0 and x.get("pocao"):
        cor = habilidades.COR_POCAO[x["pocao"]]
        boca = l.ponto({"_": (p["cb"][0] + 6, p["cb"][1] - 6)}, "_")
        pygame.draw.circle(tela, PALETA["k"], (round(boca[0]), round(boca[1])), max(3, int(2.6 * esc)))
        pygame.draw.circle(tela, cor, (round(boca[0]), round(boca[1])), max(2, int(2.0 * esc)))
    aura = "forca" if x.get("pocao_forca", 0) > 0 else "veloz" if x.get("pocao_veloz", 0) > 0 else None
    if aura and (l.t // 6) % 2 == 0:
        cor = habilidades.COR_POCAO[aura]
        for i in range(3):
            a = l.t * 0.15 + i * 2.1
            px, py = l.ponto({"_": (math.cos(a) * 14, 40 + math.sin(a * 1.3) * 30)}, "_")
            pygame.draw.circle(tela, cor, (round(px), round(py)), max(1, int(1.2 * esc)))
    if x.get("curando", 0) > 0:
        k = x["curando"] / 30
        for i in range(5):
            px, py = l.ponto({"_": (-14 + i * 7, 30 + (1 - k) * 60 + i * 6)}, "_")
            pygame.draw.line(tela, (110, 240, 120), (px - 1.4 * esc, py), (px + 1.4 * esc, py), max(1, int(0.8 * esc)))
            pygame.draw.line(tela, (110, 240, 120), (px, py - 1.4 * esc), (px, py + 1.4 * esc), max(1, int(0.8 * esc)))


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Finn grande: chapéu pontudo e a barba comprida."""
    cb = P("cb")
    roxo = (240, 240, 240) if branco else (104, 58, 150)
    pygame.draw.polygon(q, roxo, [(cb[0] - 14 * s, cb[1] - 6 * s), (cb[0] + 14 * s, cb[1] - 6 * s),
                                  (cb[0] - 6 * s * d, cb[1] - 34 * s)])
    pygame.draw.polygon(q, (240, 240, 245), [(cb[0] - 2 * s * d, cb[1] + 2 * s), (cb[0] + 9 * s * d, cb[1] + 2 * s),
                                             (cb[0] + 3 * s * d, cb[1] + 26 * s)])


# =====================================================================
# ENTRADA: se materializa com magia, dos pés à cabeça
# =====================================================================
E_SOBE, E_FIM = 76, 100


def entrada(l, t, jogo):
    alto = 132 * l.s
    if t < E_SOBE:
        l.sobrepor = {}
        k = suave(t / E_SOBE)
        l.cortar_acima = CHAO - alto * k
        if t % 2 == 0:  # brilhinhos na linha que vai subindo
            jogo.faiscas.append([l.x + random.uniform(-30, 30) * l.s, l.cortar_acima, random.uniform(-1, 1),
                                 random.uniform(-3, -1), random.randint(10, 18),
                                 random.choice((ROXO_MAGIA, (230, 200, 255), (255, 255, 255))), 4])
        if t % 16 == 0:
            som.tocar("carga", 0.35)
    else:
        l.cortar_acima = None
        if t == E_SOBE:
            som.tocar("puf")
            for _ in range(20):
                a = random.uniform(0, math.tau)
                jogo.faiscas.append([l.x, l.y - 60 * l.s, math.cos(a) * 5, math.sin(a) * 5, 18, ROXO_MAGIA, 5])
        l.sobrepor = dict(POSES_FINN["f_vitoria"]) if t < E_FIM else {}
    l.t += 1


def entrada_efeito(l, tela, t):
    if t >= E_SOBE + 10:
        return
    s = l.s
    r = int(54 * s)
    for k in range(3):  # círculo mágico no chão
        rr = r - k * 12 * s
        pygame.draw.ellipse(tela, ROXO_MAGIA if k != 1 else (230, 200, 255), (l.x - rr, CHAO - rr * 0.22, 2 * rr, rr * 0.44), 2)
    for k in range(8):
        a = t * 0.06 + k * math.tau / 8
        px, py = l.x + math.cos(a) * r * 0.85, CHAO + math.sin(a) * r * 0.19
        pygame.draw.circle(tela, (240, 220, 255), (int(px), int(py)), 3)
    if t < E_SOBE and l.cortar_acima is not None:  # a linha de luz
        y = l.cortar_acima
        pygame.draw.line(tela, (240, 220, 255), (l.x - 34 * s, y), (l.x + 34 * s, y), 3)
        brilho(tela, (int(l.x), int(y)), int(30 * s), ROXO_MAGIA, 110)


# =====================================================================
# VITÓRIA: levanta o cajado e solta fogos de magia
# =====================================================================
def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES_FINN["f_vitoria"] if t > 10 else POSES_FINN["f_levita"])
    if t in (20, 44, 68):
        _, ponta = cajado(l)
        som.tocar("puf", 0.5)
        x, y = ponta[0], ponta[1] - 60
        for _ in range(18):
            a = random.uniform(0, math.tau)
            v = random.uniform(2, 6)
            jogo.faiscas.append([x, y, math.cos(a) * v, math.sin(a) * v, 26,
                                 random.choice((ROXO_MAGIA, AMARELO_MAGIA, (255, 140, 60))), 5])
