"""JOHN: o mágico (criado pelo Gomes).

Aparência: mágico clássico, de fraque e CARTOLA PRETA COM FAIXA ROXA. Tudo que ele faz solta FUMACINHA ROXA.
  E      joga a cartola pra cima, saem LÂMINAS dela e ele arremessa no oponente (15)
  Q      tira a cartola, faz a pose de dançarino agradecendo, TELEPORTA pra trás do oponente e dá uma BICUDA (10)
  R      a mesma pose, e da cartola sai uma BOCA DE CROCODILO que dá 3 mordidas (5 cada)
  SHIFT  tira um COELHO da cartola: ele corre, fica GIGANTE, atropela (20) e o John teleporta pro coelho
  Z      ULTIMATE: teleporta 3 DANÇARINOS que dão uma rasteira e dançam em cima do oponente (40).
         Quando ele põe a cartola de novo, eles somem.
  Passiva: ABRACADABRA — depois de cada teleporte, fica invisível por meio segundo.
  Entrada: aparece teleportando pra uma cartola que está na arena e faz carinho num gato preto (que foge).
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
import pecas
from pecas import Peca

ROXO = (170, 90, 230)
ROXO_CLARO = (220, 170, 255)
ABRACADABRA = 30  # quadros invisível depois de teleportar (meio segundo)

POSES_JOHN = {
    "parado": dict(pt=(-24, 0), jt=(-14, 26), pf=(22, 0), jf=(26, 28), qd=(0, 50), pc=(4, 86), cb=(8, 104),
                   ct=(-6, 70), mt=(4, 82), cf=(20, 76), mf=(34, 86)),
    "andar1": dict(pt=(-26, 2), jt=(-14, 26), pf=(26, 0), jf=(28, 28), qd=(0, 48), pc=(4, 84), cb=(8, 102),
                   ct=(-8, 68), mt=(2, 80), cf=(20, 74), mf=(34, 84)),
    "andar2": dict(pt=(4, 10), jt=(14, 30), pf=(2, 0), jf=(10, 28), qd=(0, 52), pc=(4, 88), cb=(8, 106),
                   ct=(-6, 72), mt=(4, 84), cf=(20, 78), mf=(34, 88)),
    "andar3": dict(pt=(24, 0), jt=(28, 28), pf=(-24, 2), jf=(-12, 26), qd=(0, 48), pc=(4, 84), cb=(8, 102),
                   ct=(-4, 68), mt=(6, 80), cf=(20, 74), mf=(34, 84)),
    "andar4": dict(pt=(2, 0), jt=(10, 28), pf=(4, 10), jf=(14, 30), qd=(0, 52), pc=(4, 88), cb=(8, 106),
                   ct=(-6, 72), mt=(4, 84), cf=(20, 78), mf=(34, 88)),
    # o agradecimento de dançarino: pernas juntas, corpo inclinado, a cartola pra frente
    "j_agradece": dict(pt=(-6, 0), jt=(-2, 28), pf=(8, 0), jf=(8, 28), qd=(0, 54), pc=(16, 86), cb=(26, 98),
                       ct=(-8, 72), mt=(-20, 62), cf=(32, 80), mf=(54, 78)),
    "j_agradece_b": dict(pt=(-6, 0), jt=(-2, 26), pf=(8, 0), jf=(8, 26), qd=(0, 50), pc=(20, 80), cb=(32, 88),
                         ct=(-6, 66), mt=(-22, 58), cf=(34, 74), mf=(56, 70)),
    "j_morde": dict(pt=(-14, 0), jt=(-6, 26), pf=(14, 0), jf=(16, 28), qd=(0, 52), pc=(20, 86), cb=(30, 98),
                    ct=(-4, 72), mt=(-18, 64), cf=(40, 84), mf=(66, 84)),
    "j_magica_b": dict(pt=(-24, 0), jt=(-14, 26), pf=(22, 0), jf=(26, 28), qd=(0, 50), pc=(6, 86), cb=(10, 104),
                       ct=(12, 72), mt=(28, 76), cf=(20, 92), mf=(26, 82)),
    "j_tira_b": dict(pt=(-22, 0), jt=(-16, 28), pf=(22, 0), jf=(20, 28), qd=(0, 58), pc=(0, 94), cb=(0, 112),
                     ct=(-12, 76), mt=(-14, 62), cf=(12, 108), mf=(12, 132)),
    "j_lanca": dict(pt=(-22, 0), jt=(-14, 26), pf=(22, 0), jf=(24, 28), qd=(0, 52), pc=(2, 88), cb=(4, 106),
                    ct=(-10, 72), mt=(-4, 58), cf=(16, 104), mf=(22, 128)),
    "j_arremessa": dict(pt=(-28, 0), jt=(-18, 26), pf=(26, 0), jf=(28, 28), qd=(0, 50), pc=(10, 86), cb=(16, 102),
                        ct=(-12, 76), mt=(-24, 82), cf=(30, 88), mf=(56, 92)),
    "j_bicuda": dict(pt=(-10, 0), jt=(-6, 28), pf=(48, 88), jf=(28, 66), qd=(0, 56), pc=(-14, 88), cb=(-18, 104),
                     ct=(-26, 70), mt=(-36, 56), cf=(-12, 72), mf=(-20, 58)),  # (chute pra CIMA: joga pro alto)
    "j_magica": dict(pt=(-24, 0), jt=(-14, 26), pf=(22, 0), jf=(26, 28), qd=(0, 50), pc=(6, 86), cb=(10, 104),
                     ct=(12, 72), mt=(28, 76), cf=(22, 86), mf=(30, 90)),
    "j_carinho": dict(pt=(-20, 0), jt=(-4, 20), pf=(20, 0), jf=(30, 20), qd=(0, 34), pc=(14, 62), cb=(22, 76),
                      ct=(8, 48), mt=(18, 34), cf=(30, 46), mf=(44, 30)),
    "j_tira": dict(pt=(-20, 0), jt=(-16, 28), pf=(20, 0), jf=(18, 28), qd=(0, 56), pc=(2, 92), cb=(4, 110),
                   ct=(-10, 72), mt=(-4, 58), cf=(16, 104), mf=(22, 126)),
    "j_poe": dict(pt=(-20, 0), jt=(-16, 28), pf=(20, 0), jf=(18, 28), qd=(0, 56), pc=(2, 92), cb=(4, 110),
                  ct=(-10, 72), mt=(-4, 58), cf=(22, 104), mf=(10, 118)),
}
proporcionar(POSES_JOHN)


def puf(jogo, x, y, n=10, forca=4):
    """A fumacinha roxa de mágica (tudo que o John faz tem)."""
    fumaca(jogo, x, y, n, ROXO, forca, -1)
    fumaca(jogo, x, y, n // 2, ROXO_CLARO, forca * 0.6, -1.4)


# =====================================================================
# A CARTOLA (desenhada: vai na cabeça, na mão, voando...)
# =====================================================================
def cartola(tela, centro, ang, esc, branco=False, aberta=False, listrada=False):
    """A cartola preta com faixa roxa. centro = meio da aba; ang = 0 em pé (copa pra cima).
    listrada = a do GATOLA DA CARTOLA (alta, listras vermelhas e brancas)."""
    if listrada:
        return cartola_listrada(tela, centro, ang, esc, branco)
    c, s = math.cos(ang), math.sin(ang)
    cx, cy = centro

    def P(x, y):
        return (cx + (x * c - y * s) * esc, cy + (x * s + y * c) * esc)

    preto = (240, 240, 244) if branco else (26, 24, 32)
    borda = (150, 150, 160) if branco else (8, 6, 12)
    faixa = (240, 240, 244) if branco else ((pecas.TROCA or {}).get("v", PALETA["v"]))
    copa = [P(-5, 0), P(5, 0), P(5.5, -11), P(-5.5, -11)]
    aba = [P(-8, 1.6), P(8, 1.6), P(8, -0.6), P(-8, -0.6)]
    for pts in (copa, aba):
        pygame.draw.polygon(tela, borda, pts)
    pygame.draw.polygon(tela, preto, copa)
    pygame.draw.polygon(tela, preto, aba)
    pygame.draw.polygon(tela, faixa, [P(-5.1, -1), P(5.1, -1), P(5.2, -3.4), P(-5.2, -3.4)])
    pygame.draw.polygon(tela, borda, copa, max(1, int(esc * 0.5)))
    pygame.draw.line(tela, (90, 86, 104) if not branco else borda, P(-3.5, -10), P(-3.5, -4), max(1, int(esc * 0.6)))
    if aberta:  # a boca da cartola (o buraco escuro de onde sai a mágica)
        pygame.draw.ellipse(tela, (8, 4, 14), pygame.Rect(0, 0, 1, 1).fit(
            pygame.Rect(min(P(-5, 0)[0], P(5, 0)[0]) - esc, min(P(-5, 0)[1], P(5, 0)[1]) - esc,
                        abs(P(5, 0)[0] - P(-5, 0)[0]) + 2 * esc, abs(P(5, 0)[1] - P(-5, 0)[1]) + 2 * esc)))


def cartola_listrada(tela, centro, ang, esc, branco=False):
    c, s = math.cos(ang), math.sin(ang)
    cx, cy = centro

    def P(x, y):
        return (cx + (x * c - y * s) * esc, cy + (x * s + y * c) * esc)

    borda = (150, 150, 160) if branco else (8, 6, 12)
    vermelho = (240, 240, 244) if branco else (220, 30, 40)
    def faixa(i):  # cada listra da copa (alta e entortando pra trás, igual a do livro)
        y0, y1 = -i * 3, -(i + 1) * 3
        k0, k1 = 5 + i * 0.25, 5 + (i + 1) * 0.25
        t0, t1 = -0.05 * i * i, -0.05 * (i + 1) * (i + 1)  # (a copa vai entortando)
        return [P(-k0 + t0, y0), P(k0 + t0, y0), P(k1 + t1, y1), P(-k1 + t1, y1)]

    for i in range(8):
        pygame.draw.polygon(tela, borda, [(x, y) for x, y in faixa(i)], 0)
    for i in range(8):
        pts = faixa(i)
        pygame.draw.polygon(tela, vermelho if i % 2 == 0 else (250, 250, 250),
                            [(x + (sum(q[0] for q in pts) / 4 - x) * 0.08, y) for x, y in pts])
    aba = [P(-8, 1.6), P(8, 1.6), P(8, -0.6), P(-8, -0.6)]
    pygame.draw.polygon(tela, borda, [P(-8.6, 2.2), P(8.6, 2.2), P(8.6, -1.2), P(-8.6, -1.2)])
    pygame.draw.polygon(tela, vermelho, aba)


def rabo_gato(tela, q, esc, d, t, branco=False):
    """GATOLA: o rabo de gato (preto, curvado e balançando)."""
    pts = []
    for i in range(8):
        k = i / 7
        pts.append((q[0] - d * (4 + 26 * k) * esc, q[1] - (2 + 18 * k * k - 6 * math.sin(t * 0.08 + k * 3) * k) * esc))
    pygame.draw.lines(tela, (8, 6, 12), False, pts, max(3, int(5 * esc)))
    pygame.draw.lines(tela, (240, 240, 244) if branco else (46, 44, 52), False, pts, max(2, int(3 * esc)))


def gravata_gatola(tela, c, esc, d, branco=False):
    """GATOLA: a gravata borboleta vermelha bem grande."""
    x, y = c[0] + d * 3 * esc, c[1] + 3 * esc
    vermelho = (240, 240, 244) if branco else (220, 30, 40)
    for sinal in (-1, 1):
        pts = [(x, y), (x + sinal * 9 * esc, y - 5 * esc), (x + sinal * 9 * esc, y + 5 * esc)]
        pygame.draw.polygon(tela, (8, 6, 12), [(px + (px - x) * 0.12, py + (py - y) * 0.15) for px, py in pts])
        pygame.draw.polygon(tela, vermelho, pts)
    pygame.draw.circle(tela, (8, 6, 12), (int(x), int(y)), max(2, int(2.6 * esc)))
    pygame.draw.circle(tela, vermelho, (int(x), int(y)), max(1, int(1.8 * esc)))


def listrada(l):
    return (l.f.get("estilo") == "gatola") if l is not None else False


def bigodes(tela, na_cabeca, esc, branco=False):
    """GATOLA: o focinho de gato e os bigodes."""
    nariz = na_cabeca(10.6, 7.6)
    pygame.draw.circle(tela, (230, 120, 150) if not branco else (150, 150, 160), (int(nariz[0]), int(nariz[1])),
                       max(1, int(esc * 0.9)))
    base = na_cabeca(9.6, 8.4)
    for dy in (-1.2, 0.2, 1.6):
        ponta = na_cabeca(14.5, 8.4 + dy * 1.4)
        pygame.draw.line(tela, (230, 230, 236) if not branco else (150, 150, 160), base, ponta, max(1, int(esc * 0.35)))


def onde_chapeu(l):
    """Onde está a cartola agora: 'cabeca', ('mao', ponto da pose, ângulo) ou None (voando / sumida)."""
    x = l.extra
    if x.get("chapeu_fora"):
        return None
    d = l.lado()
    pra_frente = -d * math.pi / 2  # (a boca da cartola virada pro oponente)
    if l.estado == "ataque":
        n, t = l.nome_golpe, l.t
        if n == "john_chapeu":
            return ("mao", "mf", 0.0) if t < E_SOBE else None
        if n == "john_bicuda":
            return ("mao", "mf", pra_frente) if t < Q_TELE else "cabeca"
        if n == "john_crocodilo":
            return ("mao", "mf", pra_frente)
        if n == "john_coelho":
            return ("mao", "mt", math.pi) if t < S_SAI + 6 else "cabeca"
        if n == "john_ultimate":
            return ("mao", "mf", 0.0) if t < m_poe(l) else "cabeca"
    if l.estado == "vitoria":
        return ("mao", "mf", 0.0)
    if l.estado == "parado" and l.pose_espera == "j_agradece":
        return ("mao", "mf", pra_frente)
    return "cabeca"


# =====================================================================
# E: A CARTOLA DE LÂMINAS
# =====================================================================
E_SOBE, E_LAMINAS, E_DESCE, E_JOGA = 5, 12, 18, 22


def chapeu_lancado(l, outro, jogo):
    t = l.t
    l.vx = 0
    l.fisica(jogo)
    if t == E_SOBE:
        som.tocar("vento", 0.5)
        puf(jogo, l.x, l.y - 120 * l.s, 4, 2)
    if t == E_LAMINAS:
        som.tocar("shuriken", 0.7)
    if t == E_JOGA:  # LÁ VAI A CARTOLA!
        l.extra["chapeu_fora"] = True  # (a cartola foi embora: volta quando o tiro acabar)
        l.projetil = Projetil(l, l.x + 58 * l.s * l.dir, l.y - 84 * l.s, l.dir, GOLPES["john_chapeu"])
        jogo.projeteis.append(l.projetil)
        som.tocar("shuriken")
    if t >= E_JOGA + 14:
        return "fim"


def chapeu_lancado_efeito(l, tela):
    """A cartola subindo, girando, as lâminas saindo dela e descendo pra mão."""
    t = l.t
    if not (E_SOBE <= t < E_JOGA):
        return
    esc = l.s * 2.2
    p = l.pose_vista or l.pose_atual()
    mao = l.ponto(p, "mf")
    if t < E_DESCE:
        k = suave((t - E_SOBE) / (E_DESCE - E_SOBE))
        y = mao[1] - 70 * l.s * math.sin(k * math.pi * 0.5 + 0.2)
    else:
        k = suave((t - E_DESCE) / (E_JOGA - E_DESCE))
        y = mao[1] - 70 * l.s * (1 - k)
    pos = (mao[0], y)
    ang = t * 0.5
    if t >= E_LAMINAS:
        laminas(tela, pos, ang, esc, min(1.0, (t - E_LAMINAS) / 4))
    cartola(tela, pos, ang, esc, listrada=listrada(l))


def laminas(tela, pos, ang, esc, k=1.0):
    """As 4 lâminas saindo da aba da cartola."""
    for i in range(4):
        a = ang + i * math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        base = (pos[0] + ca * 7 * esc, pos[1] + sa * 7 * esc)
        ponta = (pos[0] + ca * (7 + 9 * k) * esc, pos[1] + sa * (7 + 9 * k) * esc)
        lado = (-sa * 2.2 * esc, ca * 2.2 * esc)
        pts = [(base[0] + lado[0], base[1] + lado[1]), ponta, (base[0] - lado[0], base[1] - lado[1])]
        pygame.draw.polygon(tela, (12, 10, 18), pts)
        pygame.draw.polygon(tela, (226, 230, 240), pts)
        pygame.draw.line(tela, (255, 255, 255), base, ponta, 1)


def desenha_chapeu_voando(p, tela):
    esc = 2.2 * p.dono.s / 1.36
    ang = p.t * 0.6 * (1 if p.vx > 0 else -1)
    for i in range(3):  # rastro roxo
        x = p.x - p.vx * (i + 1) * 0.9
        pygame.draw.circle(tela, (120 - i * 30, 60, 170 - i * 30), (int(x), int(p.y)), max(2, int(10 - i * 3)))
    laminas(tela, (p.x, p.y), ang, esc)
    cartola(tela, (p.x, p.y), ang, esc, listrada=listrada(p.dono))


# =====================================================================
# Q: O AGRADECIMENTO + TELEPORTE + BICUDA
# =====================================================================
Q_TELE = 9


def teleportar(l, x, outro, jogo):
    """Some numa fumaça roxa e aparece em x (ABRACADABRA: fica invisível um pouquinho)."""
    puf(jogo, l.x, l.y - 60 * l.s)
    l.x = max(PAREDE_E, min(PAREDE_D, x))
    l.dir = 1 if outro.x > l.x else -1
    puf(jogo, l.x, l.y - 60 * l.s)
    som.tocar("puf")
    if l.f.get("habilidade") == "abracadabra":
        l.invisivel = ABRACADABRA
        l.flash_invisivel = 16


def bicuda(l, outro, jogo):
    t = l.t
    l.vx = 0
    if t == 4:
        som.tocar("confirma", 0.4)
    if t % 5 == 0 and t < Q_TELE:
        p = l.pose_vista or l.pose_atual()
        m = l.ponto(p, "mf")
        puf(jogo, m[0], m[1], 2, 1.5)
    if t == Q_TELE:  # PUF: atrás do oponente
        lado = 1 if outro.x > l.x else -1
        teleportar(l, outro.x + lado * 70 * outro.s, outro, jogo)
    l.fisica(jogo)
    if t >= Q_TELE + 26:
        return "fim"


# =====================================================================
# R: A BOCA DE CROCODILO (3 mordidas)
# =====================================================================
R_SAI, R_INI, R_INTERVALO, R_HITS = 3, 9, 12, 3


def crocodilo(l, outro, jogo):
    t = l.t
    l.vx = 0
    l.fisica(jogo)
    if t == R_SAI:
        p = l.pose_vista or l.pose_atual()
        m = l.ponto(p, "mf")
        puf(jogo, m[0], m[1], 5, 2)
        som.tocar("puf", 0.6)
    if R_INI <= t < R_INI + R_HITS * R_INTERVALO and (t - R_INI) % R_INTERVALO == 0:
        som.tocar("lingua", 0.5)
    if t >= R_INI + R_HITS * R_INTERVALO + 14:
        return "fim"


def crocodilo_efeito(l, tela):
    """A boca de crocodilo saindo da cartola: vai e volta e morde."""
    t = l.t
    if t < R_SAI:
        return
    p = l.pose_vista or l.pose_atual()
    m = l.ponto(p, "mf")
    d = l.dir
    fim = R_INI + R_HITS * R_INTERVALO + 6
    k = min(1.0, (t - R_SAI) / (R_INI - R_SAI)) if t < fim else max(0.0, 1 - (t - fim) / 8)
    comp = 62 * l.s * k
    if comp < 2:
        return
    u = (t - R_INI) % R_INTERVALO if t >= R_INI else R_INTERVALO - 1
    abre = 0.55 if u > 3 else 0.05  # fecha na hora da mordida
    x0, y0 = m[0] + d * 10 * l.s, m[1]
    verde, escuro, borda = (70, 150, 70), (40, 100, 44), (12, 24, 12)
    for sinal in (-1, 1):  # mandíbula de cima e de baixo
        a = -sinal * abre
        ponta = (x0 + d * comp * math.cos(a), y0 + comp * math.sin(a) * 0.9 + sinal * 0)
        grossura = 9 * l.s * (1 if sinal < 0 else 0.8)
        pts = [(x0, y0 + sinal * grossura * 0.2), ponta, (ponta[0] - d * 6 * l.s, ponta[1] + sinal * grossura * 0.6),
               (x0, y0 + sinal * grossura)]
        pygame.draw.polygon(tela, borda, [(px, py) for px, py in pts], 0)
        pygame.draw.polygon(tela, verde if sinal < 0 else escuro, pts)
        for i in range(1, 6):  # os dentes
            q = i / 6
            bx = x0 + (ponta[0] - x0) * q
            by = y0 + (ponta[1] - y0) * q
            pygame.draw.polygon(tela, (250, 250, 240), [(bx - 2 * l.s, by), (bx + 2 * l.s, by),
                                                         (bx, by - sinal * 4 * l.s)])
    olho = (x0 + d * comp * 0.35, y0 - 9 * l.s - abre * 18 * l.s)
    pygame.draw.circle(tela, (240, 220, 60), (int(olho[0]), int(olho[1])), max(2, int(3 * l.s)))
    pygame.draw.circle(tela, (10, 10, 10), (int(olho[0]), int(olho[1])), max(1, int(1.4 * l.s)))


def crocodilo_quadros():
    q = [(0, "parado"), (R_SAI + 2, "j_agradece")]
    for k in range(R_HITS):  # a cada mordida o corpo dá um tranco pra frente (e volta)
        q += [(R_INI + k * R_INTERVALO, "j_morde"), (R_INI + k * R_INTERVALO + 7, "j_agradece")]
    return q + [(R_INI + R_HITS * R_INTERVALO + 6, "j_agradece_b"), (R_INI + R_HITS * R_INTERVALO + 14, "parado")]


# =====================================================================
# SHIFT: O COELHO GIGANTE (e o John teleporta pra ele)
# =====================================================================
S_SAI, S_CRESCE, S_VEL, S_CORRIDA = 12, 18, 11, 44


def coelho(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t == S_SAI:  # sai da cartola!
        m["coelho_x"] = l.x + l.dir * 40 * l.s
        p = l.pose_vista or l.pose_atual()
        mt = l.ponto(p, "mt")
        puf(jogo, mt[0], mt[1], 6, 2)
        som.tocar("puf", 0.7)
    if "coelho_x" not in m:
        return
    if l.acertou and "bateu" not in m:
        m["bateu"] = t
        jogo.tremer(8)
    andando = "bateu" not in m and t < S_SAI + S_CORRIDA
    if andando:
        m["coelho_x"] = max(PAREDE_E, min(PAREDE_D, m["coelho_x"] + S_VEL * l.dir))
        if t % 4 == 0:
            fumaca(jogo, m["coelho_x"] - l.dir * 20, CHAO - 4, 1, (180, 170, 150), 1, -0.3)
    tam = tamanho_coelho(t)
    rel = (m["coelho_x"] - l.x) * l.dir / l.s
    m["caixa"] = (rel - 20 * tam, 0, rel + 22 * tam, 46 * tam)
    teleporta = m.get("bateu", S_SAI + S_CORRIDA - 8) + 8
    if t == teleporta:  # o John teleporta pro coelho (e o coelho some)
        teleportar(l, m["coelho_x"] - l.dir * 10 * l.s, outro, jogo)
        m["sumiu"] = True
        m["caixa"] = None
    if t >= teleporta + 14:
        return "fim"


def tamanho_coelho(t):
    return 0.45 + 1.75 * suave(min(1.0, max(0, t - S_SAI) / S_CRESCE))


def desenha_coelho(tela, x, chao, esc, d, t, tam, branco=False):
    """O coelho branco (pequeno saindo da cartola, depois GIGANTE)."""
    u = esc * tam
    corre = math.sin(t * 0.7)
    corpo = (245, 245, 248) if not branco else (255, 255, 255)
    sombra, borda, rosa = (206, 206, 216), (40, 36, 48), (240, 160, 180)

    def P(px, py):
        return x + d * px * u, chao - py * u

    pygame.draw.ellipse(tela, (0, 0, 0), (x - 14 * u, chao - 3 * u, 28 * u, 6 * u))  # sombra no chão
    for px, fase in ((-6, 0), (8, math.pi)):  # patas
        pe = P(px + corre * 5 * math.cos(fase), 0)
        pygame.draw.ellipse(tela, borda, (pe[0] - 5 * u, pe[1] - 4 * u, 10 * u, 5 * u))
        pygame.draw.ellipse(tela, sombra, (pe[0] - 4 * u, pe[1] - 3.5 * u, 8 * u, 3.5 * u))
    cx, cy = P(0, 12 + abs(corre) * 3)
    pygame.draw.ellipse(tela, borda, (cx - 15 * u, cy - 11 * u, 30 * u, 22 * u))
    pygame.draw.ellipse(tela, corpo, (cx - 14 * u, cy - 10 * u, 28 * u, 20 * u))
    pygame.draw.circle(tela, borda, (int(cx - d * 14 * u), int(cy - 4 * u)), max(2, int(5 * u)))  # rabinho
    pygame.draw.circle(tela, (255, 255, 255), (int(cx - d * 14 * u), int(cy - 4 * u)), max(1, int(4 * u)))
    hx, hy = cx + d * 13 * u, cy - 10 * u
    for k, inclina in ((0, -0.35), (1, -0.1)):  # orelhas
        base = (hx - d * (3 - k * 3) * u, hy - 6 * u)
        ponta = (base[0] - d * (6 + inclina * 10) * u, base[1] - 18 * u)
        pygame.draw.line(tela, borda, base, ponta, max(3, int(7 * u)))
        pygame.draw.line(tela, corpo, base, ponta, max(2, int(5 * u)))
        pygame.draw.line(tela, rosa, base, ponta, max(1, int(2 * u)))
    pygame.draw.circle(tela, borda, (int(hx), int(hy)), int(9 * u))
    pygame.draw.circle(tela, corpo, (int(hx), int(hy)), int(8 * u))
    pygame.draw.circle(tela, (210, 30, 50), (int(hx + d * 3 * u), int(hy - 2 * u)), max(1, int(2 * u)))
    pygame.draw.circle(tela, rosa, (int(hx + d * 8 * u), int(hy + 1 * u)), max(1, int(1.6 * u)))


def coelho_efeito(l, tela):
    m = l.memo
    if "coelho_x" not in m or m.get("sumiu"):
        return
    desenha_coelho(tela, m["coelho_x"], CHAO, l.s * 1.6, l.dir, l.t, tamanho_coelho(l.t))


# =====================================================================
# Z: ULTIMATE — OS 3 DANÇARINOS
# =====================================================================
U_CHEGAM, U_RASTEIRA, U_DANCA, U_PISOES, U_INTERVALO, U_DANO = 32, 40, 50, 8, 10, 5  # 8 x 5 = 40


def m_poe(l):
    """Quando ele põe a cartola de volta (e os dançarinos somem)."""
    m = l.memo
    if "pegou" in m:
        return U_DANCA + U_PISOES * U_INTERVALO + 8
    if "errou" in m:
        return U_CHEGAM + 40
    return 9999


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t < U_CHEGAM and t % 6 == 0:  # a mágica girando na cartola erguida
        p = l.pose_vista or l.pose_atual()
        mf = l.ponto(p, "mf")
        puf(jogo, mf[0], mf[1] - 20 * l.s, 2, 2)
    if t == 6:
        som.tocar("carga")
    if t == U_CHEGAM:
        m["alvo"] = (outro.x, CHAO)
        for dx in (-60, 0, 60):
            puf(jogo, outro.x + dx * outro.s, CHAO - 60, 8, 4)
        som.tocar("puf")
        defende = outro.estado == "defendendo" or outro.pode_defender(GOLPES["john_ultimate"])
        livre = outro.no_chao() and not defende and outro.estado not in ("caido", "agarrado") and outro.inv == 0
        if livre:
            m["pegou"] = t
            outro.mudar("agarrado")
            outro.golpe = None
            outro.sobrepor = dict(outro.poses["golpeado"])
            outro.y, outro.vx, outro.vy = CHAO, 0, 0
            l.inv = 999
        else:
            m["errou"] = t
    if "pegou" in m:
        if t == U_RASTEIRA:  # A RASTEIRA: cai no chão
            outro.sobrepor = dict(outro.poses["caido"])
            som.tocar("queda")
            jogo.tremer(6)
        u = t - U_DANCA
        if 0 <= u < U_PISOES * U_INTERVALO and u % U_INTERVALO == 0:  # dançando em cima (cada pisão dói)
            ultima = u // U_INTERVALO == U_PISOES - 1
            outro.levar(U_DANO, l, GOLPES["john_ultimate"])
            if not ultima:
                outro.vida = max(1, outro.vida)
            outro.tremor_hit = 6
            jogo.faisca(outro.x + random.uniform(-30, 30), CHAO - random.uniform(8, 30), False, ultima)
            som.tocar("chute" if ultima else "soco", 0.6)
    if t == m_poe(l):  # PÕE A CARTOLA: os dançarinos somem
        if "alvo" in m:
            for dx in (-60, 0, 60):
                puf(jogo, m["alvo"][0] + dx * l.s, CHAO - 60, 8, 4)
        som.tocar("puf")
        if "pegou" in m:
            outro.sobrepor = {}
            outro.mudar("voando")
            outro.vx, outro.vy = 4 * l.dir, -6
            l.inv = 0
    if t >= m_poe(l) + 20:
        return "fim"


def ultimate_quadros():
    q = [(0, "parado"), (8, "j_tira")]
    for k in range(3):  # gira a cartola no alto (a mágica carregando)
        q += [(12 + k * 8, "j_tira_b"), (16 + k * 8, "j_tira")]
    return q + [(U_CHEGAM + 4, "j_tira"), (U_CHEGAM + 14, "parado")]


def desenha_dancarino(tela, x, chao, esc, d, t, fase, cor=(150, 60, 200)):
    """Um dançarino de collant roxo e cartolinha, dançando can-can."""
    u = esc
    borda, pele = (20, 14, 28), (236, 196, 160)

    def P(px, py):
        return x + d * px * u, chao - py * u

    chute = math.sin(t * 0.35 + fase)
    quadril = P(0, 22)
    for i, sinal in enumerate((1, -1)):  # pernas: uma chuta pro alto, a outra fica
        alto = max(0, chute * sinal)
        pe = P(sinal * 4 + alto * 14 * sinal, alto * 22)
        pygame.draw.line(tela, borda, quadril, pe, max(3, int(4.4 * u)))
        pygame.draw.line(tela, (30, 26, 36), quadril, pe, max(2, int(3 * u)))
        pygame.draw.circle(tela, borda, (int(pe[0]), int(pe[1])), max(2, int(2.4 * u)))
    corpo = [P(-5, 20), P(5, 20), P(4, 38), P(-4, 38)]
    pygame.draw.polygon(tela, borda, corpo, 0)
    pygame.draw.polygon(tela, cor, [P(-4, 21), P(4, 21), P(3, 37), P(-3, 37)])
    saia = [P(-10, 22), P(10, 22), P(0, 28)]
    pygame.draw.polygon(tela, ROXO_CLARO, saia)
    for sinal in (-1, 1):  # braços pra cima
        mao = P(sinal * 12, 50 + math.sin(t * 0.3 + fase + sinal) * 3)
        pygame.draw.line(tela, borda, P(sinal * 4, 36), mao, max(2, int(3 * u)))
        pygame.draw.line(tela, pele, P(sinal * 4, 36), mao, max(1, int(1.8 * u)))
    cab = P(0, 44)
    pygame.draw.circle(tela, borda, (int(cab[0]), int(cab[1])), int(5.4 * u))
    pygame.draw.circle(tela, pele, (int(cab[0]), int(cab[1])), int(4.4 * u))
    cartola(tela, P(0, 48.5), 0, u * 0.55)


def ultimate_efeito(l, tela):
    m = l.memo
    t = l.t
    if "alvo" not in m or t >= m_poe(l):
        return
    ax, chao = m["alvo"]
    esc = l.s * 2.4
    for i, dx in enumerate((-46, 0, 46)):
        if "pegou" in m and t >= U_DANCA:  # dançando EM CIMA
            y = chao - 18 * l.s - abs(math.sin(t * 0.35 + i)) * 8 * l.s
            x = ax + dx * l.s * 0.8
        elif "pegou" in m and U_RASTEIRA - 6 <= t < U_RASTEIRA + 4:  # a rasteira: deslizando
            y, x = chao, ax + dx * l.s + (1 if dx <= 0 else -1) * 20 * l.s
        else:
            y, x = chao, ax + dx * l.s * 1.4
        desenha_dancarino(tela, x, y, esc, 1 if dx <= 0 else -1, t, i * 2.1)


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


_registra("john_chapeu", ini=E_JOGA, ativo=1, rec=13, raio=16, vel=11, dano=15, hit=16, defe=10, emp=4,
          nivel="medio", ia="longe", logica=chapeu_lancado, efeito=chapeu_lancado_efeito,
          desenho_proj=desenha_chapeu_voando,
          quadros=[(0, "parado"), (E_SOBE, "j_lanca"), (E_LAMINAS, "j_tira_b"), (E_DESCE, "j_lanca"),
                   (E_JOGA - 1, "j_arremessa"), (E_JOGA + 12, "parado")])
_registra("john_bicuda", ini=Q_TELE + 3, ativo=6, rec=17, janelas=((Q_TELE + 3, Q_TELE + 9),),
          caixa=(14, 30, 80, 126), dano=10, hit=24, defe=12, emp=2, nivel="medio", lanca=17,
          logica=bicuda, ia="perto", som="vento",
          quadros=[(0, "parado"), (4, "j_agradece"), (Q_TELE - 1, "j_agradece_b"), (Q_TELE + 1, "j_bicuda"),
                   (Q_TELE + 12, "j_bicuda"), (Q_TELE + 26, "parado")])
_registra("john_crocodilo", ini=R_INI, ativo=R_HITS * R_INTERVALO, rec=14,
          janelas=tuple((R_INI + k * R_INTERVALO, R_INI + k * R_INTERVALO + 4) for k in range(R_HITS)),
          caixa=(24, 50, 104, 120), dano=5, hit=14, defe=8, emp=2, nivel="medio", logica=crocodilo,
          efeito=crocodilo_efeito, ia="perto", quadros=crocodilo_quadros())
_registra("john_coelho", ini=S_SAI + 2, ativo=S_CORRIDA, rec=12, janelas=((S_SAI + 2, S_SAI + S_CORRIDA),),
          dano=20, hit=22, defe=12, emp=6, nivel="medio", derruba=True, voo=(10, 7), logica=coelho,
          efeito=coelho_efeito, ia="medio", som="chute",
          quadros=[(0, "parado"), (4, "j_magica"), (7, "j_magica_b"), (10, "j_magica"), (S_SAI, "j_magica_b"),
                   (S_SAI + 4, "j_tira"), (S_SAI + 10, "j_arremessa"), (S_SAI + 20, "parado")])
GOLPES["john_coelho"]["total"] = 9999
_registra("john_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=ultimate, efeito=ultimate_efeito, ia="ultimate", quadros=ultimate_quadros())
GOLPES["john_ultimate"]["total"] = 9999

GOLPES_JOHN = {"E": "john_chapeu", "Q": "john_bicuda", "R": "john_crocodilo", "SHIFT": "john_coelho",
               "Z": "john_ultimate"}


def todo_quadro(l, jogo):
    """A cartola volta pra cabeça (num puf roxo) quando a de lâminas acaba de voar.
    (E as passivas do John: TRUQUE DE CARTAS e COELHO AJUDANTE.)"""
    import habilidades
    habilidades.john_quadro(l, jogo)
    x = l.extra
    if x.get("chapeu_fora") and not (l.estado == "ataque" and l.nome_golpe == "john_chapeu"):
        tiro = getattr(l, "projetil", None)
        if tiro is None or not tiro.vivo:
            x["chapeu_fora"] = False
            puf(jogo, l.x, l.y - 116 * l.s, 5, 2)


# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  f F fraque preto  v faixa/lapela roxa  w camisa  g gravata borboleta  p P q pele
#   h H cabelo  m bigode  c C calça  s S sapato  l L luva  e olho
PALETA = {
    "k": (14, 12, 18), "f": (34, 30, 44), "F": (62, 56, 80), "v": (124, 60, 176), "w": (240, 240, 236),
    "g": (150, 70, 210), "p": (238, 204, 170), "P": (212, 172, 136), "q": (170, 124, 96), "h": (58, 40, 30),
    "H": (96, 70, 52), "m": (46, 32, 24), "c": (28, 26, 36), "C": (52, 48, 64), "s": (16, 14, 20),
    "S": (84, 80, 98), "l": (246, 246, 242), "L": (206, 206, 214), "e": (20, 18, 24),
}
S_REF = 1.36 / 3

TRONCO = Peca([
    "...kkkkkkkk...",
    "..kwwvwwvwwwk.",
    ".kwFFvggvffwk.",
    ".kwFfvwwvffwk.",
    ".kfFfvwwvfffk.",
    ".kfFffvwvfffk.",
    ".kfFfffwffffk.",
    ".kfFfffwffffk.",
    "..kfFffwfffk..",
    "..kfFffwfffk..",
    "..kffffwfffk..",
    "..kvvvvvvvvk..",
    "..kcccccccCk..",
    "..kcccccccCk..",
    "..kccccccCCk..",
    "...kcccccCk...",
    "....kkkkkk....",
], PALETA, a=(7, 15), b=(7, 1))

CABECA = Peca([
    "..kkkkkk.....",
    ".khhHhhhkk...",
    "khhHhhhhhhk..",
    "khhhhhhhhhhk.",
    "khhhhpppppk..",
    "khhkpppppepk.",
    ".khkpppppppk.",
    ".kkpppppPppk.",
    "..kppmmmmpk..",
    "..kpppqqpk...",
    "...kkpppk....",
    "....kkkk.....",
], PALETA, a=(6, 7), b=(6, 0), estica=False)

COXA = Peca([
    ".kkkkkk.",
    "kcCcccck",
    "kCccccck",
    "kcccccck",
    "kcccccck",
    "kcccccck",
    "kcccccck",
    "kcccccck",
    "kcccccck",
    ".kcccck.",
    ".kcccck.",
    ".kcccck.",
    "..kcck..",
    "..kkkk..",
], PALETA, a=(3, 0), b=(3, 13))

CANELA = Peca([
    ".kkkkk.",
    "kcCccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    ".kccck.",
    ".kccck.",
    "..kkk..",
], PALETA, a=(3, 0), b=(3, 13))

SAPATO = Peca([
    ".kkkkk.....",
    "ksSsskkkk..",
    "ksssssssSk.",
    "kssssssssSk",
    "kkkkkkkkkkk",
], PALETA, a=(3, 1), b=(9, 1), estica=False)

BRACO = Peca([
    ".kkkk.",
    "kwLwwk",
    "kwLwwk",
    "kwwwwk",
    "kwwwwk",
    "kwwwLk",
    "kwwwwk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 7))

ANTEBRACO = Peca([
    ".kkk.",
    "kwwwk",
    "kLwLk",
    "kkkkk",
    "kpPqk",
    "kpPqk",
    "kpPqk",
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


TRONCO_ANTIGO = Peca([
    "...kkkkkkkk...",
    "..kfFvwwvfffk.",
    ".kfFFvggvfffk.",
    ".kfFfvwwvfffk.",
    ".kfFfvwwvfffk.",
    ".kfFffvwvfffk.",
    ".kfFfffwffffk.",
    ".kfFfffwffffk.",
    "..kfFffwfffk..",
    "..kfFffwfffk..",
    "..kffffwfffk..",
    "..kvvvvvvvvk..",
    "..kcccccccCk..",
    "..kcccccccCk..",
    "..kccccccCCk..",
    "...kcccccCk...",
    "....kkkkkk....",
], PALETA, a=(7, 15), b=(7, 1))

CABECA_ANTIGO = Peca([
    "..kkkkkk.....",
    ".khhHhhhkk...",
    "khhHhhhhhhk..",
    "khhhhhhhhhhk.",
    "khhhhpppppk..",
    "khhkpppppepk.",
    ".khkpppppppk.",
    ".kkpppppPppk.",
    "..kppmmmmpk..",
    "..kpppqqpk...",
    "...kkpppk....",
    "....kkkk.....",
], PALETA, a=(6, 7), b=(6, 0), estica=False)

COXA_ANTIGO = Peca([
    ".kkkkkk.",
    "kcCcccck",
    "kCccccck",
    "kcccccck",
    "kcccccck",
    "kcccccck",
    "kcccccck",
    "kcccccck",
    "kcccccck",
    ".kcccck.",
    ".kcccck.",
    ".kcccck.",
    "..kcck..",
    "..kkkk..",
], PALETA, a=(3, 0), b=(3, 13))

CANELA_ANTIGO = Peca([
    ".kkkkk.",
    "kcCccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    "kccccck",
    ".kccck.",
    ".kccck.",
    "..kkk..",
], PALETA, a=(3, 0), b=(3, 13))

SAPATO_ANTIGO = Peca([
    ".kkkkk.....",
    "ksSsskkkk..",
    "ksssssssSk.",
    "kssssssssSk",
    "kkkkkkkkkkk",
], PALETA, a=(3, 1), b=(9, 1), estica=False)

BRACO_ANTIGO = Peca([
    ".kkkk.",
    "kfFffk",
    "kfFffk",
    "kffffk",
    "kffffk",
    "kffffk",
    "kffffk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 7))

ANTEBRACO_ANTIGO = Peca([
    ".kkk.",
    "kfFfk",
    "kfffk",
    "kfffk",
    "kfffk",
    "kfffk",
    "kwwwk",
    "kwwwk",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 8))

MAO_ANTIGO = Peca([
    ".kkkk.",
    "klLLlk",
    "kllllk",
    "kLLLLk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 4), estica=False)


def baralho_no_bolso(tela, no_tronco, esc, branco):
    """O BARALHO no bolso do colete (mágico de rua)."""
    if branco:
        return
    cantos = [no_tronco(9.6, 6.6), no_tronco(11.4, 6.6), no_tronco(11.4, 9.0), no_tronco(9.6, 9.0)]
    pygame.draw.polygon(tela, PALETA["k"], cantos)
    pygame.draw.polygon(tela, (246, 244, 236), [(x * 0.8 + cantos[0][0] * 0.2, y * 0.8 + cantos[0][1] * 0.2) for x, y in cantos])
    c = no_tronco(10.5, 7.6)
    pygame.draw.circle(tela, (200, 30, 40), (round(c[0]), round(c[1])), max(1, int(0.6 * esc)))


def aneis(tela, mao, esc, branco):
    """ANÉIS dourados brilhando na mão da frente."""
    if branco:
        return
    for k in (-1, 1):
        pygame.draw.circle(tela, (250, 210, 70), (round(mao[0] + k * 1.2 * esc), round(mao[1])), max(1, int(0.8 * esc)))


def coelhinho(tela, l, branco):
    """O COELHINHO ASSISTENTE: sempre do lado dele (pulando de leve). Na passiva COELHO AJUDANTE ele morde/bloqueia."""
    x = l.extra
    if l.estado == "ataque" and l.nome_golpe == "john_coelho" and "coelho_x" in l.memo:
        return  # (no SHIFT ele é o coelho que vira gigante)
    k = l.s / l.f["tam"]  # (1 no mundo, 1/PIXEL no desenho pequeno)
    anim = x.get("coelho_anim", 0)
    if anim > 0 and "coelho_onde" in x:  # pulando no adversário / na frente do tiro
        cx, cy = x["coelho_onde"]
        cx, chao = cx * k, cy * k
        pulo = math.sin(min(1.0, (24 - anim) / 10) * math.pi) * 18 * l.s
        desenha_coelho(tela, cx, chao - pulo, l.s * 1.6, x.get("coelho_dir", l.dir), l.t, 0.42, branco)
        return
    d = l.dir
    pula = abs(math.sin(l.t * 0.12)) * 4 * l.s
    desenha_coelho(tela, l.x - d * 36 * l.s, CHAO * k - pula, l.s * 1.6, d, 0, 0.36, branco)


def desenhar_john(l, tela, p, branco):
    if listrada(l):  # (o GATOLA continua com o fraque e as luvas)
        return _desenhar_john(l, tela, p, branco, TRONCO_ANTIGO, BRACO_ANTIGO, ANTEBRACO_ANTIGO, MAO_ANTIGO, rua=False)
    coelhinho(tela, l, branco)
    cartas_no_alvo(l, tela)
    return _desenhar_john(l, tela, p, branco, TRONCO, BRACO, ANTEBRACO, MAO, rua=True)


def _desenhar_john(l, tela, p, branco, TRONCO, BRACO, ANTEBRACO, MAO, rua):
    esc = l.s / S_REF
    d = l.lado()
    espelho = d < 0
    perto_v = "branco" if branco else "normal"
    longe_v = "branco" if branco else "escuro"
    troca = pecas.TROCA or {}

    def P(k):
        return l.ponto(p, k)

    def perna(pe, joelho, var):
        q, j, e = P("qd"), P(joelho), P(pe)
        CANELA.desenhar(tela, j, e, esc, espelho, var)
        fr, _ = frente_do_pe(j, e, d)
        SAPATO.desenhar(tela, e, mais(e, fr, 9), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    def braco(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)

    def cauda():  # as abas do fraque, penduradas atrás
        q, c = P("qd"), P("pc")
        (ux, uy), _ = eixos(q, c)
        pontos = [(q[0] - d * 3 * esc - ux * 2 * esc, q[1] - uy * 2 * esc),
                  (q[0] - d * 13 * esc + ux * 16 * esc, q[1] + 18 * esc),
                  (q[0] - d * 6 * esc + ux * 16 * esc, q[1] + 20 * esc),
                  (q[0] + d * 2 * esc, q[1] + 4 * esc)]
        cor = (245, 245, 250) if branco else troca.get("f", PALETA["f"])
        pygame.draw.polygon(tela, PALETA["k"], pontos)
        pygame.draw.polygon(tela, cor, [(x + (q[0] - x) * 0.12, y + (q[1] - y) * 0.12) for x, y in pontos])

    onde = onde_chapeu(l)
    gatola = listrada(l)
    if gatola:
        rabo_gato(tela, P("qd"), esc, d, l.t, branco)
    braco("ct", "mt", longe_v)
    perna("pt", "jt", longe_v)
    if not gatola and not rua:  # (as abas do fraque: só no Gatola não; no mágico de rua é colete)
        cauda()
    c, cb = P("pc"), P("cb")
    no_tronco = TRONCO.desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    if rua:
        baralho_no_bolso(tela, no_tronco, esc, branco)
    perna("pf", "jf", perto_v)
    u, _ = cabeca_eixos(c, cb, d)
    pygame.draw.line(tela, PALETA["k"], c, mais(cb, u, -3 * esc), max(3, int(5 * esc)))
    pescoco = troca.get("P", PALETA["P"])
    pygame.draw.line(tela, pescoco if not branco else (240, 240, 240), c, mais(cb, u, -3 * esc), max(1, int(3 * esc)))
    na_cabeca = CABECA.desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    if gatola:
        bigodes(tela, na_cabeca, esc, branco)
        gravata_gatola(tela, c, esc, d, branco)
    if onde == "cabeca":  # a cartola em cima da cabeça
        topo, cima = na_cabeca(6.5, 1.0), na_cabeca(6.5, -6)
        ang = math.atan2(cima[0] - topo[0], -(cima[1] - topo[1]))
        cartola(tela, topo, ang, esc * 0.9, branco, listrada=gatola)
    braco("cf", "mf", perto_v)
    if rua:
        aneis(tela, P("mf"), esc, branco)
    if isinstance(onde, tuple):  # a cartola na mão
        _, ponto, ang = onde
        m = P(ponto)
        cartola(tela, (m[0] - math.sin(ang) * 2 * esc, m[1] + math.cos(ang) * 2 * esc), ang, esc * 0.9, branco,
                listrada=gatola)


def cartas_no_alvo(l, tela):
    """TRUQUE DE CARTAS: as cartas marcadas girando em volta do adversário (efeito do John)."""
    x = l.extra
    n = x.get("cartas_n", 0)
    if not n or "cartas_alvo" not in x:
        return
    k = l.s / l.f["tam"]
    ax, ay = x["cartas_alvo"]
    ax, ay = ax * k, ay * k
    for i in range(n):
        a = l.t * 0.08 + i * math.tau / 3
        cx, cy = ax + math.cos(a) * 26 * l.s, ay + math.sin(a) * 8 * l.s
        w, h = 5 * l.s, 7 * l.s
        pygame.draw.rect(tela, (20, 18, 24), (cx - w / 2 - 1, cy - h / 2 - 1, w + 2, h + 2))
        pygame.draw.rect(tela, (246, 244, 236), (cx - w / 2, cy - h / 2, w, h))
        pygame.draw.circle(tela, (200, 30, 40), (int(cx), int(cy)), max(1, int(1.2 * l.s)))


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """John grande: a cartola com a faixa roxa."""
    cb = P("cb")
    cartola(q, (cb[0], cb[1] - 4 * s), 0, s * 1.2, branco)


# =====================================================================
# ENTRADA: uma cartola no chão, PUF, ele sai dela e faz carinho num gato preto (que foge)
# =====================================================================
E_PUF, E_CARINHO, E_FOGE = 34, 44, 84


def entrada(l, t, jogo):
    if t < E_PUF:
        l.esconde = True
        if t % 10 == 0:
            puf(jogo, l.x, CHAO - 10, 2, 1.5)
    else:
        if t == E_PUF:
            l.esconde = False
            puf(jogo, l.x, l.y - 60 * l.s, 14, 5)
            som.tocar("puf")
        if E_CARINHO <= t < E_FOGE + 6:
            l.sobrepor = dict(POSES_JOHN["j_carinho"])
        elif t >= E_FOGE + 6:
            l.sobrepor = misturar(POSES_JOHN["j_carinho"], POSES_JOHN["parado"], suave(min(1, (t - E_FOGE - 6) / 14)))
            if t >= E_FOGE + 20:
                l.sobrepor = {}
        else:
            l.sobrepor = {}
    if t == E_FOGE:
        som.tocar("vento", 0.5)
    l.t += 1


def desenha_gato(tela, x, chao, esc, d, t, correndo):
    """O gato preto (sentadinho, ou correndo pra longe)."""
    u = esc
    preto, borda = (24, 20, 30), (8, 6, 12)

    def P(px, py):
        return x + d * px * u, chao - py * u

    if correndo:
        pata = math.sin(t * 0.8) * 4
        pygame.draw.ellipse(tela, preto, pygame.Rect(0, 0, 1, 1).move(P(-10, 12)).inflate(22 * u, 9 * u))
        for px in (-8, 6):
            pygame.draw.line(tela, preto, P(px, 8), P(px + pata, 0), max(2, int(2.4 * u)))
        cab = P(10, 14)
    else:
        pygame.draw.ellipse(tela, preto, (P(-6, 16)[0] - 6 * u, P(-6, 16)[1], 14 * u, 16 * u))
        cab = P(2, 20)
    pygame.draw.line(tela, preto, P(-10, 6), P(-18, 16 + math.sin(t * 0.2) * 4), max(2, int(2.4 * u)))  # rabo
    pygame.draw.circle(tela, borda, (int(cab[0]), int(cab[1])), int(5.6 * u))
    pygame.draw.circle(tela, preto, (int(cab[0]), int(cab[1])), int(5 * u))
    for k in (-1, 1):  # orelhas
        o = (cab[0] + k * 3 * u, cab[1] - 3 * u)
        pygame.draw.polygon(tela, preto, [(o[0] - 2.4 * u, o[1]), (o[0] + 2.4 * u, o[1]), (o[0], o[1] - 5 * u)])
    pygame.draw.circle(tela, (240, 220, 60), (int(cab[0] + d * 2 * u), int(cab[1] - 1 * u)), max(1, int(1.4 * u)))


def entrada_efeito(l, tela, t):
    s = l.s
    if t < E_PUF + 2:  # a cartola no chão, soltando fumaça roxa
        brilho(tela, (int(l.x), int(CHAO - 12 * s)), int((22 + 3 * math.sin(t * 0.3)) * s), ROXO, 110)
        cartola(tela, (l.x, CHAO - 1), 0, 2.4 * s, listrada=listrada(l))
    gx0 = l.x + l.dir * 46 * s
    if t < E_FOGE:  # o gato sentado na frente dele
        desenha_gato(tela, gx0, CHAO, 1.8 * s, -l.dir, t, False)
    elif t < E_FOGE + 40:  # e foge correndo
        k = (t - E_FOGE) / 40
        desenha_gato(tela, gx0 + l.dir * 520 * k * k, CHAO, 1.8 * s, l.dir, t, True)


# =====================================================================
# VITÓRIA: tira a cartola pra plateia (e sai uma pombinha... de fumaça roxa)
# =====================================================================
def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES_JOHN["j_tira"] if t > 8 else POSES_JOHN["parado"])
    if t == 12:
        som.tocar("confirma", 0.5)
        p = l.pose_vista or l.pose_atual()
        m = l.ponto(p, "mf")
        puf(jogo, m[0], m[1] - 30 * l.s, 10, 3)


def vitoria_efeito(l, tela, t):
    if t < 12:
        return
    p = l.pose_vista or l.pose_atual()
    m = l.ponto(p, "mf")
    for i in range(5):  # estrelinhas roxas saindo da cartola
        k = ((t - 12) * 0.03 + i / 5) % 1
        x = m[0] + math.sin(k * 6 + i) * 30 * l.s * k
        y = m[1] - 30 * l.s - k * 90 * l.s
        r = max(1, int(4 * l.s * (1 - k)))
        pygame.draw.circle(tela, ROXO_CLARO if i % 2 else (255, 240, 160), (int(x), int(y)), r)
