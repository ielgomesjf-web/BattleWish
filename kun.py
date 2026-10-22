"""KUN: o mestre das cartas (criado pelo Gomes).

Aparência: japonês normal, roupa com um símbolo de carta no peito. Chega se teleportando pra uma carta.
  E      lança uma CARTA (5)
  Q      brinca com a carta e dá um SHORYUKEN de carta (25, joga pra cima)
  R      balança a carta que nem espada: 6 hits de 3
  SHIFT  lança uma carta no chão e se TELEPORTA pra ela (0)
  Z      ULTIMATE: carta no chão, saem MÓVEIS dela (cadeira, mesa, abajur, sofá, armário) e o Kun chuta tudo no oponente
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

POSES_KUN = {
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
    "k_lanca": dict(pt=(-28, 0), jt=(-18, 26), pf=(26, 0), jf=(28, 28), qd=(0, 50), pc=(10, 86), cb=(16, 102),
                    ct=(-12, 76), mt=(-24, 82), cf=(30, 88), mf=(56, 92)),
    "k_brinca": dict(pt=(-22, 0), jt=(-14, 26), pf=(22, 0), jf=(24, 28), qd=(0, 52), pc=(2, 88), cb=(4, 106),
                     ct=(12, 78), mt=(22, 90), cf=(18, 82), mf=(28, 96)),
    "k_shoryu": dict(pt=(-14, 4), jt=(-8, 30), pf=(12, 0), jf=(14, 28), qd=(0, 56), pc=(8, 92), cb=(14, 108),
                     ct=(-8, 76), mt=(-2, 62), cf=(18, 112), mf=(24, 140)),
    "k_espada_a": dict(pt=(-28, 0), jt=(-18, 26), pf=(28, 0), jf=(30, 28), qd=(0, 48), pc=(10, 84), cb=(16, 100),
                       ct=(-6, 72), mt=(2, 82), cf=(26, 98), mf=(50, 108)),
    "k_espada_b": dict(pt=(-28, 0), jt=(-18, 26), pf=(28, 0), jf=(30, 28), qd=(0, 48), pc=(12, 82), cb=(18, 98),
                       ct=(-6, 72), mt=(2, 82), cf=(28, 78), mf=(52, 64)),
    "k_chute": dict(pt=(-10, 0), jt=(-6, 28), pf=(62, 62), jf=(32, 60), qd=(0, 56), pc=(-14, 88), cb=(-18, 104),
                    ct=(-26, 70), mt=(-36, 56), cf=(-12, 72), mf=(-20, 58)),
    "k_agacha": dict(pt=(-20, 0), jt=(-4, 20), pf=(20, 0), jf=(30, 20), qd=(0, 34), pc=(16, 62), cb=(24, 76),
                     ct=(8, 46), mt=(18, 32), cf=(30, 40), mf=(46, 16)),
    "k_vitoria": dict(pt=(-20, 0), jt=(-16, 28), pf=(20, 0), jf=(18, 28), qd=(0, 56), pc=(2, 92), cb=(4, 110),
                      ct=(-10, 72), mt=(-4, 58), cf=(16, 104), mf=(20, 128)),
    # (as poses do meio: deixam os golpes FLUIDOS — pedido do Gomes)
    "k_lanca_prep": dict(pt=(-26, 0), jt=(-16, 26), pf=(24, 0), jf=(26, 28), qd=(0, 50), pc=(0, 88), cb=(4, 106),
                         ct=(10, 78), mt=(20, 84), cf=(-4, 96), mf=(-16, 108)),
    "k_lanca_fim": dict(pt=(-28, 0), jt=(-18, 26), pf=(28, 0), jf=(30, 28), qd=(0, 48), pc=(14, 84), cb=(20, 100),
                        ct=(-12, 74), mt=(-24, 80), cf=(32, 80), mf=(52, 70)),
}
proporcionar(POSES_KUN)

VERMELHO_CARTA = (210, 40, 40)


# =====================================================================
# A carta (na mão, voando, no chão)
# =====================================================================
def ash(l):
    """Roupa ASH (código CARD&FIGHT): as cartas que ele JOGA viram Pokébolas (na mão continua carta) e o boné."""
    return l is not None and l.f.get("estilo") == "ash"


def pokebola(tela, pos, ang, esc, brilha=False):
    """A Pokébola (no lugar da carta, na roupa ASH)."""
    r = max(3, int(5.4 * esc))
    x, y = int(pos[0]), int(pos[1])
    if brilha:
        brilho(tela, (x, y), int(12 * esc), (255, 230, 150), 120)
    pygame.draw.circle(tela, (16, 14, 20), (x, y), r + max(1, int(esc * 0.8)))
    pygame.draw.circle(tela, (250, 250, 250), (x, y), r)
    c, s = math.cos(ang), math.sin(ang)  # a metade vermelha (gira junto)
    meia = [(x + (math.cos(a) * c - math.sin(a) * s) * r, y + (math.cos(a) * s + math.sin(a) * c) * r)
            for a in [math.pi + k * math.pi / 10 for k in range(11)]]
    pygame.draw.polygon(tela, (226, 36, 40), meia)
    pygame.draw.line(tela, (16, 14, 20), (x - c * r, y - s * r), (x + c * r, y + s * r), max(1, int(esc * 1.1)))
    pygame.draw.circle(tela, (16, 14, 20), (x, y), max(2, int(1.8 * esc)))
    pygame.draw.circle(tela, (250, 250, 250), (x, y), max(1, int(1.1 * esc)))


def carta(tela, pos, ang, esc, largura=1.0, brilha=False, l=None):
    """Uma carta de baralho. 'largura' < 1 = virando (efeito de girar em 3D). (l = quem joga: no ASH é Pokébola)"""
    if ash(l):
        return pokebola(tela, pos, ang, esc, brilha)
    w, h = 5 * esc * max(0.15, abs(largura)), 7 * esc
    c, s = math.cos(ang), math.sin(ang)
    pts = [(pos[0] + x * c - y * s, pos[1] + x * s + y * c) for x, y in ((-w, -h), (w, -h), (w, h), (-w, h))]
    if brilha:
        brilho(tela, (int(pos[0]), int(pos[1])), int(12 * esc), (255, 230, 150), 120)
    pygame.draw.polygon(tela, (240, 240, 236) if largura > 0 else (170, 40, 50), pts)
    pygame.draw.polygon(tela, (20, 18, 24), pts, max(1, int(esc * 0.8)))
    if largura > 0.4:
        pygame.draw.circle(tela, VERMELHO_CARTA, (int(pos[0]), int(pos[1])), max(1, int(esc * 1.6)))


def carta_no_chao(tela, x, s, t, brilha=True, l=None):
    """Carta deitada no chão (achatada), brilhando. (ASH: uma Pokébola no chão)"""
    if ash(l):
        return pokebola(tela, (x, CHAO - 6 * s), 0, 2.2 * s, brilha)
    w, h = 20 * s, 6 * s
    if brilha:
        brilho(tela, (int(x), int(CHAO - 2)), int((26 + 4 * math.sin(t * 0.3)) * s), (255, 220, 140), 110)
    pygame.draw.ellipse(tela, (20, 18, 24), (x - w - 2, CHAO - h - 2, 2 * w + 4, 2 * h + 4))
    pygame.draw.ellipse(tela, (240, 240, 236), (x - w, CHAO - h, 2 * w, 2 * h))
    pygame.draw.circle(tela, VERMELHO_CARTA, (int(x), int(CHAO)), max(2, int(2.5 * s)))


def mao_carta(l):
    p = l.pose_vista or l.pose_atual()
    c, m = l.ponto(p, "cf"), l.ponto(p, "mf")
    (dx, dy), _ = eixos(c, m)
    return (m[0] + dx * 6 * l.s, m[1] + dy * 6 * l.s), math.atan2(dy, dx)


# =====================================================================
# E: LANÇA UMA CARTA
# =====================================================================
def desenha_carta_voando(p, tela):
    esc = 2.2
    for i in range(3):  # rastro
        x = p.x - p.vx * (i + 1) * 0.8
        pygame.draw.line(tela, (230, 220, 200), (x - 4, p.y), (x + 4, p.y), max(1, 3 - i))
    carta(tela, (p.x, p.y), p.t * 0.5 * (1 if p.vx > 0 else -1), esc, math.cos(p.t * 0.7), l=p.dono)


# =====================================================================
# Q: BRINCA COM A CARTA + SHORYUKEN DE CARTA
# =====================================================================
Q_BRINCA, Q_SOBE = 16, 12


def shoryuken(l, outro, jogo):
    t = l.t
    m = l.memo
    if t < Q_BRINCA:  # brincando com a carta (dá pra ver chegando)
        l.vx = 0
        l.fisica(jogo)
        return
    if t == Q_BRINCA:  # SHORYUKEN!
        l.vy = -14
        l.vx = 3.4 * l.dir
        som.tocar("vento")
    m["caixa"] = (0, 40, 64, 170)
    l.fisica(jogo)
    if t > Q_BRINCA + 4 and l.no_chao():
        m.setdefault("pousou", t)
        l.vx = 0
        if t - m["pousou"] > 14:  # caiu e fica um tempinho aberto (dá pra punir se errar)
            return "fim"


def shoryuken_efeito(l, tela):
    (x, y), ang = mao_carta(l)
    t = l.t
    if t < Q_BRINCA:  # a carta girando em volta da mão
        for i in range(3):
            a = t * 0.5 + i * math.tau / 3
            carta(tela, (x + math.cos(a) * 14 * l.s, y + math.sin(a) * 8 * l.s), a, 2.0 * l.s / 1.36,
                  math.cos(t * 0.4 + i))
    elif t < Q_BRINCA + Q_SOBE + 4:  # o rastro da carta subindo (meia-lua)
        k = (t - Q_BRINCA) / (Q_SOBE + 4)
        r = 46 * l.s
        cx = l.x + 10 * l.s * l.dir
        cy = l.y - 110 * l.s
        ini = math.pi * 0.5 if l.dir > 0 else math.pi * 0.5
        rect = (cx - r, cy - r, 2 * r, 2 * r)
        cor = (255, 240, 220) if (t // 2) % 2 else (255, 140, 120)
        pygame.draw.arc(tela, cor, rect, ini - 1.6 * (1 - k), ini + 1.6 * (1 - k), max(2, int(5 * l.s)))
        carta(tela, (x, y), ang, 2.2 * l.s / 1.36, 1, brilha=True)


# =====================================================================
# R: A CARTA QUE NEM ESPADA (6 hits)
# =====================================================================
R_INI, R_INTERVALO, R_HITS = 10, 7, 6


def espada(l, outro, jogo):
    t = l.t
    l.vx = 0.8 * l.dir if R_INI <= t < R_INI + R_HITS * R_INTERVALO else 0
    if R_INI <= t < R_INI + R_HITS * R_INTERVALO and (t - R_INI) % R_INTERVALO == 0:
        som.tocar("vento", 0.5)
    l.fisica(jogo)
    if t >= R_INI + R_HITS * R_INTERVALO + 12:
        return "fim"


def espada_efeito(l, tela):
    (x, y), ang = mao_carta(l)
    u = l.t - R_INI
    carta(tela, (x, y), ang, 2.4 * l.s / 1.36, 1, brilha=0 <= u < R_HITS * R_INTERVALO)
    if 0 <= u < R_HITS * R_INTERVALO and u % R_INTERVALO < 3:  # o corte
        cima = (u // R_INTERVALO) % 2 == 0
        r = 40 * l.s
        cx, cy = l.x + 40 * l.s * l.dir, l.y - 90 * l.s
        a0 = -0.9 if cima else 0.2
        if l.dir < 0:
            a0 = math.pi - a0 - 1.0
        pygame.draw.arc(tela, (255, 245, 230), (cx - r, cy - r, 2 * r, 2 * r), a0, a0 + 1.0, max(2, int(4 * l.s)))


def espada_quadros():
    q = [(0, "parado"), (R_INI - 3, "k_espada_b")]
    for k in range(R_HITS):
        a, b = ("k_espada_a", "k_espada_b") if k % 2 == 0 else ("k_espada_b", "k_espada_a")
        q.append((R_INI + k * R_INTERVALO + 1, a))
        q.append((R_INI + k * R_INTERVALO + 5, b))
    q.append((R_INI + R_HITS * R_INTERVALO + 12, "parado"))
    return q


# =====================================================================
# SHIFT: CARTA NO CHÃO + TELEPORTE
# =====================================================================
S_JOGA, S_TELE, S_FIM = 6, 22, 34
S_DIST = 300


def teleporte(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t == S_JOGA:
        m["de"] = l.x + 30 * l.s * l.dir
        m["alvo"] = max(PAREDE_E, min(PAREDE_D, l.x + S_DIST * l.dir))
        som.tocar("shuriken", 0.6)
    if S_JOGA <= t < S_TELE:
        k = suave((t - S_JOGA) / (S_TELE - 2 - S_JOGA))
        m["carta_x"] = m["de"] + (m["alvo"] - m["de"]) * min(1, k)
    if t == S_TELE:  # PUF: sumiu daqui e apareceu na carta
        fumaca(jogo, l.x, l.y - 60 * l.s, 8, (220, 220, 230), 4, -1)
        l.x = m["alvo"]
        l.inv = 12
        l.dir = 1 if outro.x > l.x else -1  # (se passou por trás, já vira de frente)
        fumaca(jogo, l.x, l.y - 60 * l.s, 8, (220, 220, 230), 4, -1)
        som.tocar("puf")
    if t >= S_FIM:
        return "fim"


def teleporte_efeito(l, tela):
    m = l.memo
    if "carta_x" in m and l.t < S_TELE + 4:
        carta_no_chao(tela, m["carta_x"], l.s / 1.36, l.t, l=l)


# =====================================================================
# Z: ULTIMATE — A CARTA DOS MÓVEIS
# =====================================================================
#  (tipo, dano)  — total 35
MOVEIS = (("cadeira", 6), ("mesa", 7), ("abajur", 5), ("sofa", 8), ("armario", 9))
U_JOGA, U_SAI, U_INTERVALO, U_SOBE, U_CHUTA = 10, 22, 24, 10, 14
U_FIM = U_SAI + len(MOVEIS) * U_INTERVALO + 24
_moveis_img = {}


def imagem_movel(tipo):
    """O desenho de cada móvel (feito uma vez e guardado)."""
    if tipo in _moveis_img:
        return _moveis_img[tipo]
    k = (24, 16, 12)
    madeira, madeira_esc = (150, 96, 50), (100, 60, 28)
    if tipo == "cadeira":
        sup = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.rect(sup, k, (4, 0, 10, 60))
        pygame.draw.rect(sup, madeira, (6, 2, 6, 56))
        pygame.draw.rect(sup, k, (4, 30, 34, 10))
        pygame.draw.rect(sup, madeira, (6, 32, 30, 6))
        pygame.draw.rect(sup, k, (30, 38, 8, 22))
        pygame.draw.rect(sup, madeira_esc, (32, 40, 4, 18))
    elif tipo == "mesa":
        sup = pygame.Surface((76, 46), pygame.SRCALPHA)
        pygame.draw.rect(sup, k, (0, 0, 76, 12))
        pygame.draw.rect(sup, madeira, (2, 2, 72, 8))
        for x in (6, 62):
            pygame.draw.rect(sup, k, (x, 10, 9, 36))
            pygame.draw.rect(sup, madeira_esc, (x + 2, 10, 5, 34))
    elif tipo == "abajur":
        sup = pygame.Surface((40, 66), pygame.SRCALPHA)
        pygame.draw.polygon(sup, k, [(8, 0), (32, 0), (40, 26), (0, 26)])
        pygame.draw.polygon(sup, (250, 214, 110), [(10, 2), (30, 2), (37, 24), (3, 24)])
        pygame.draw.rect(sup, k, (17, 24, 6, 34))
        pygame.draw.rect(sup, (200, 190, 170), (18, 24, 4, 32))
        pygame.draw.rect(sup, k, (6, 58, 28, 8))
        pygame.draw.rect(sup, (120, 110, 100), (8, 60, 24, 4))
    elif tipo == "sofa":
        sup = pygame.Surface((90, 48), pygame.SRCALPHA)
        pygame.draw.rect(sup, k, (0, 6, 90, 38), border_radius=8)
        pygame.draw.rect(sup, (170, 50, 60), (3, 9, 84, 32), border_radius=7)
        pygame.draw.rect(sup, (200, 80, 86), (14, 22, 62, 14), border_radius=4)
        pygame.draw.rect(sup, k, (6, 42, 8, 6))
        pygame.draw.rect(sup, k, (76, 42, 8, 6))
    else:  # armario
        sup = pygame.Surface((54, 96), pygame.SRCALPHA)
        pygame.draw.rect(sup, k, (0, 0, 54, 96))
        pygame.draw.rect(sup, madeira, (3, 3, 48, 90))
        pygame.draw.line(sup, k, (27, 6), (27, 90), 3)
        for x in (21, 31):
            pygame.draw.circle(sup, (230, 200, 90), (x, 48), 3)
        pygame.draw.rect(sup, madeira_esc, (6, 6, 18, 80), 2)
        pygame.draw.rect(sup, madeira_esc, (30, 6, 18, 80), 2)
    _moveis_img[tipo] = sup
    return sup


def desenha_movel(tela, tipo, pos, escala, giro):
    img = imagem_movel(tipo)
    if escala != 1:
        img = pygame.transform.scale(img, (max(1, int(img.get_width() * escala)), max(1, int(img.get_height() * escala))))
    if giro:
        img = pygame.transform.rotate(img, giro)
    tela.blit(img, img.get_rect(center=(int(pos[0]), int(pos[1]))))


class Movel(Projetil):
    """Um móvel chutado: vai reto, girando, e passa por cima de outros projéteis."""

    def __init__(self, dono, x, y, tipo):
        super().__init__(dono, x, y, dono.dir, GOLPES["kun_" + tipo])
        self.tipo = tipo
        self.esc = dono.s / 1.36 * 1.1

    def desenhar(self, tela):
        desenha_movel(tela, self.tipo, (self.x, self.y), self.esc, -self.t * 14 * (1 if self.vx > 0 else -1))


def _carta_x(l):
    return l.memo.get("carta_x", l.x + 70 * l.s * l.dir)


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t == U_JOGA:  # a carta no chão, do lado dele
        m["carta_x"] = max(PAREDE_E, min(PAREDE_D, l.x + 62 * l.s * l.dir))
        som.tocar("shuriken", 0.6)
    for i, (tipo, _) in enumerate(MOVEIS):
        sai = U_SAI + i * U_INTERVALO
        if t == sai:
            som.tocar("puf", 0.5)
        if t == sai + U_CHUTA:  # CHUTA!
            x = _carta_x(l)
            jogo.projeteis.append(Movel(l, x + 10 * l.s * l.dir, l.y - 56 * l.s, tipo))
            som.tocar("chute")
            jogo.tremer(4)
    if t >= U_FIM:
        return "fim"


def ultimate_efeito(l, tela):
    t = l.t
    if t < U_JOGA:
        return
    x = _carta_x(l)
    carta_no_chao(tela, x, l.s / 1.36, t, l=l)
    for i, (tipo, _) in enumerate(MOVEIS):
        u = t - (U_SAI + i * U_INTERVALO)
        if 0 <= u < U_CHUTA:  # o móvel saindo da carta
            k = suave(min(1, u / U_SOBE))
            y = CHAO - 56 * l.s * k
            desenha_movel(tela, tipo, (x, y), l.s / 1.36 * 1.1 * (0.3 + 0.7 * k), 0)
            if u < 4:
                brilho(tela, (int(x), int(CHAO - 20)), int(40 * l.s), (255, 230, 150), 160)


def ultimate_quadros():
    q = [(0, "parado"), (U_JOGA - 4, "k_lanca"), (U_JOGA + 4, "parado")]
    for i in range(len(MOVEIS)):
        sai = U_SAI + i * U_INTERVALO
        q += [(sai + U_CHUTA - 4, "parado"), (sai + U_CHUTA, "k_chute"), (sai + U_CHUTA + 6, "k_chute")]
    q.append((U_FIM, "parado"))
    return q


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


_registra("kun_carta", ini=7, ativo=1, rec=12, proj=True, varios=True, raio=8, vel=14, dano=5, hit=10, defe=8, emp=2,
          nivel="medio", ia="longe", som="shuriken", desenho_proj=desenha_carta_voando,
          quadros=[(0, "parado"), (4, "k_lanca_prep"), (7, "k_lanca"), (10, "k_lanca_fim"), (14, "k_lanca_fim"),
                   (20, "parado")])
_registra("kun_shoryuken", ini=Q_BRINCA, ativo=Q_SOBE, rec=30, janelas=((Q_BRINCA, Q_BRINCA + Q_SOBE),), dano=25,
          hit=24, defe=14, emp=2, nivel="medio", lanca=17, logica=shoryuken, efeito=shoryuken_efeito, ia="perto",
          quadros=[(0, "parado"), (4, "k_brinca"), (Q_BRINCA - 4, "k_brinca"), (Q_BRINCA - 1, "k_agacha"),
                   (Q_BRINCA + 2, "k_shoryu"), (Q_BRINCA + 26, "k_shoryu"), (Q_BRINCA + 32, "k_agacha"),
                   (Q_BRINCA + 44, "parado")])
GOLPES["kun_shoryuken"]["total"] = 9999
_registra("kun_espada", ini=R_INI, ativo=R_HITS * R_INTERVALO, rec=12,
          janelas=tuple((R_INI + k * R_INTERVALO, R_INI + k * R_INTERVALO + 3) for k in range(R_HITS)),
          caixa=(10, 40, 88, 128), dano=3, hit=10, defe=7, emp=1, nivel="medio", logica=espada, efeito=espada_efeito,
          ia="perto", quadros=espada_quadros())
_registra("kun_teleporte", ini=S_JOGA, ativo=1, rec=S_FIM - S_JOGA - 1, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=teleporte, efeito=teleporte_efeito, ia="medio",
          quadros=[(0, "parado"), (2, "k_lanca_prep"), (S_JOGA, "k_lanca"), (S_JOGA + 4, "k_lanca_fim"),
                   (S_TELE - 1, "parado"), (S_TELE + 1, "k_agacha"), (S_FIM, "parado")])
for _tipo, _dano in MOVEIS:
    _registra("kun_" + _tipo, ini=0, ativo=1, rec=0, proj=True, raio=26, vel=12, dano=_dano, hit=18, defe=10, emp=3,
              nivel="medio", varios=True, ultimate=True, atravessa=True, guarda_custo=10)
GOLPES["kun_armario"].update(derruba=True, voo=(7, 9))  # o último (armário) derruba
_registra("kun_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=ultimate, efeito=ultimate_efeito, ia="ultimate", quadros=ultimate_quadros())
GOLPES["kun_ultimate"]["total"] = U_FIM + 1

GOLPES_KUN = {"E": "kun_carta", "Q": "kun_shoryuken", "R": "kun_espada", "SHIFT": "kun_teleporte", "Z": "kun_ultimate"}

# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  R r v moletom vermelho (claro -> escuro)  w carta branca  e naipe preto  p P q pele
#   h H cabelo preto  c C calça  s S tênis  o olho
PALETA = {
    "k": (16, 14, 20), "R": (226, 84, 70), "r": (176, 44, 42), "v": (112, 24, 30), "w": (244, 242, 236),
    "e": (24, 22, 28), "p": (240, 206, 170), "P": (212, 172, 136), "q": (160, 120, 90), "h": (28, 26, 34),
    "H": (70, 68, 86), "c": (40, 40, 52), "C": (70, 72, 90), "s": (34, 32, 42), "S": (150, 150, 168),
    "o": (20, 20, 24),
    "b": (160, 120, 90), "B": (240, 206, 170),  # boca e cantinhos da boca (= pele; no CORINGA viram o sorriso vermelho)
    "g": (40, 170, 90), "G": (20, 100, 56),     # a VISEIRA verde de crupiê (transparente: a luz passa verde)
}
# (o remodel de CRUPIÊ, pedido do Gomes: colete, camisa de manga dobrada, gravata borboleta, ligas nos braços,
#  viseira verde, calça social e sapato. As letras são as mesmas de antes: as roupas da loja continuam valendo.)
S_REF = 1.36 / 3

TRONCO = Peca([
    ".....kkkkkkkk.....",
    "....kwwwkekwwwk...",
    "...kwwwkeeekwwwk..",
    "..kRRrwwkekwwrrvk.",
    ".kRRRrrrwwwwrrrvvk",
    ".kRRrrrrwwwwrrrrvk",
    ".kRRrrrrrwwrrrrrvk",
    ".kRrrrrrrwrrrrrrvk",
    ".kRrrrrrrerrrrrrvk",
    ".kRrrrrrrrrrrrrrvk",
    ".kRrrrrrrerrrrrrvk",
    ".kRrrrrrrrrrrrrrvk",
    "..kRrrrrrerrrrrvk.",
    "..kRrrrrrrrrrrrvk.",
    "..kRrrrrrrrrrrrvk.",
    "..kRrrrkkkkrrrrvk.",
    "..krrrkwwwwkrrrvk.",
    "..keeeeeSSeeeeeek.",
    "..kcccccccccccCCk.",
    "..kcCccccccccCCCk.",
    "...kccccccccccCk..",
    "...kcccccccccCCk..",
    "....kkkkkkkkkkk...",
], PALETA, a=(9, 20), b=(9, 1))

TRONCO_COSTAS = Peca([
    ".....kkkkkkkk.....",
    "....kwwwwwwwwk....",
    "...kwwwwwwwwwwk...",
    "..kRRrrrrrrrrrvk..",
    ".kRRrrrrrrrrrrrvk.",
    ".kRRrrrrrrrrrrrvvk",
    ".kRrrrrrrrrrrrrrvk",
    ".kRrrrrrrrrrrrrrvk",
    ".kRrrrrkkkkkrrrrvk",
    ".kRrrrrkeeekrrrrvk",
    ".kRrrrrkkkkkrrrrvk",
    ".kRrrrrrrrrrrrrrvk",
    "..kRrrrrrrrrrrrvk.",
    "..kRrrrrrrrrrrrvk.",
    "..kRrrrrrrrrrrrvk.",
    "..kRrrrrrrrrrrrvk.",
    "..krrrrrrrrrrrrvk.",
    "..keeeeeeeeeeeeek.",
    "..kcccccccccccCCk.",
    "..kcCccccccccCCCk.",
    "...kccccccccccCk..",
    "...kcccccccccCCk..",
    "....kkkkkkkkkkk...",
], PALETA, a=(9, 20), b=(9, 1))

CABECA = Peca([
    "....k.kk.k......",
    "...khkhhkhk.....",
    "..khhHhhHhhk....",
    ".khhHhhhhhhhk...",
    ".kggggggggggggk.",
    ".kGGGGGGGGGGGGGk",
    ".khhhhpppppk....",
    ".khhkppkkpppk...",
    ".khPpppkoopk....",
    ".khkppppppPk....",
    "..kppppppPpk....",
    "..kppBppBpk.....",
    "..kkppbbpk......",
    "...kkpppk.......",
    "....kkkk........",
], PALETA, a=(6, 9), b=(6, 2), estica=False)

CABECA_COSTAS = Peca([
    "....k.kk.k......",
    "...khkhhkhk.....",
    "..khhHhhHhhk....",
    ".khhHhhhhhhhk...",
    ".kgggggggggggk..",
    ".kGhhhhhhhhhGk..",
    ".khhhhhhhhhhk...",
    ".khhhhhhhhhhk...",
    ".khhhhhhhhhk....",
    ".khhhhhhhhhk....",
    "..khhhhhhhpk....",
    "..khhhhhhpk.....",
    "..kkpppppk......",
    "...kkpppk.......",
    "....kkkk........",
], PALETA, a=(6, 9), b=(6, 2), estica=False)

# (sem a viseira: pro TREINADOR, que usa o boné)
CABECA_SEM_VISEIRA = Peca([
    "....k.kk.k......",
    "...khkhhkhk.....",
    "..khhHhhHhhk....",
    ".khhHhhhhhhhk...",
    ".khhhhhhhhhhhk..",
    ".khhhhhhhhhhk...",
    ".khhhhpppppk....",
    ".khhkppkkpppk...",
    ".khPpppkoopk....",
    ".khkppppppPk....",
    "..kppppppPpk....",
    "..kppBppBpk.....",
    "..kkppbbpk......",
    "...kkpppk.......",
    "....kkkk........",
], PALETA, a=(6, 9), b=(6, 2), estica=False)

COXA = Peca([
    ".kkkkkkk.",
    "kcCccccCk",
    "kCcccccck",
    "kCcccccck",
    "kCccccCck",
    "kCcccccck",
    "kCcccccck",
    "kCccCccck",
    "kCcccccck",
    ".kCccccck",
    ".kCccccck",
    ".kCcccck.",
    "..kcccck.",
    "..kkkkk..",
], PALETA, a=(4, 0), b=(4, 13))

CANELA = Peca([
    ".kkkkkk.",
    "kcCcccck",
    "kCccccck",
    "kCcCccck",
    "kCccccck",
    "kCccccck",
    "kCccccck",
    "kCccccCk",
    "kCccccck",
    "kCccccck",
    "kCccccck",
    "kCccccck",
    ".kcccck.",
    "..kkkk..",
], PALETA, a=(3, 0), b=(3, 13))

TENIS = Peca([
    ".kkkk......",
    "ksSskkkk...",
    "kssssSSsk..",
    "kssssssssSk",
    "kkkkkkkkkkk",
], PALETA, a=(3, 1), b=(9, 1), estica=False)

BRACO = Peca([
    ".kkkkk.",
    "kwwwwwk",
    "kwwwwwk",
    "kwwwwwk",
    "kwwwwwk",
    "keeeeek",
    "kwwwwwk",
    "kwwwwwk",
    "kwwwwwk",
    ".kkkkk.",
], PALETA, a=(3, 0), b=(3, 9))

ANTEBRACO = Peca([
    ".kkkkk.",
    "kwwwwwk",
    "kwwwwwk",
    "kkkkkkk",
    "kppPPqk",
    "kppPqqk",
    "kpPPqqk",
    "kpPPqqk",
    "kpPqqqk",
    ".kkkkk.",
], PALETA, a=(3, 0), b=(3, 9))

MAO = Peca([
    ".kkkkk.",
    "kpPPpqk",
    "kpkPkqk",
    "kpPpPqk",
    "kqqqqqk",
    ".kkkkk.",
], PALETA, a=(3, 0), b=(3, 5), estica=False)


def desenhar_kun(l, tela, p, branco):
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
        TENIS.desenhar(tela, e, mais(e, fr, 9), esc, espelho, var)
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
    pescoco = (pecas.TROCA or {}).get("P", PALETA["P"])  # (segue a roupa: no CORINGA é branco)
    pygame.draw.line(tela, pescoco if not branco else (240, 240, 240), c, mais(cb, u, -3 * esc), max(1, int(3 * esc)))
    cabeca = CABECA_COSTAS if costas else (CABECA_SEM_VISEIRA if ash(l) else CABECA)
    na_cabeca = cabeca.desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    if ash(l) and not branco:
        bone_ash(tela, na_cabeca, esc)
    braco(perto[0], perto[1], perto_v)
    # a carta na mão da frente (quando não está fazendo golpe que desenha a dele)
    golpe_com_carta = l.estado == "ataque" and l.nome_golpe in ("kun_shoryuken", "kun_espada")
    if not golpe_com_carta and not branco:
        m, cot = P(perto[1]), P(perto[0])
        dm, _ = eixos(cot, m)
        carta(tela, mais(m, dm, 3), math.atan2(dm[1], dm[0]), esc * 0.45, 1)  # (na mão é carta até no ASH)


def bone_ash(tela, P, esc):
    """ASH: o boné vermelho com a frente branca e o símbolo verde."""
    borda = (16, 14, 20)
    copa = [P(0.2, 5.2), P(0.2, 2.6), P(2.4, 0.2), P(7, -0.8), P(10.6, 0.6), P(11.8, 3), P(11.8, 5.2)]
    aba = [P(9, 4.4), P(16, 5.0), P(16, 6.4), P(9, 6.2)]
    for pts in (copa, aba):
        pygame.draw.polygon(tela, borda, pts)
        pygame.draw.polygon(tela, borda, pts, max(2, int(esc * 1.2)))
    pygame.draw.polygon(tela, (220, 30, 40), copa)
    pygame.draw.polygon(tela, (250, 250, 250), [P(6.2, 0), P(10.4, 0.9), P(11.4, 4.6), P(6.6, 4.6)])
    pygame.draw.polygon(tela, (40, 160, 70), [P(7.6, 1.6), P(8.6, 1.6), P(8.6, 3.0), P(10, 3.0), P(10, 3.8),
                                              P(7.6, 3.8)])  # o símbolo verde
    pygame.draw.polygon(tela, (220, 30, 40), aba)


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Kun grande: cabelo preto espetado e a carta no peito."""
    cb, pc = P("cb"), P("pc")
    preto = (240, 240, 240) if branco else (28, 26, 34)
    for i in range(5):
        base = (cb[0] - 6 * s + i * 3 * s * d, cb[1] - 6 * s)
        pygame.draw.polygon(q, preto, [base, (base[0] - 4 * s * d, base[1] - 9 * s), (base[0] + 3 * s * d, base[1])])
    pygame.draw.rect(q, (244, 242, 236), (pc[0] - 4 * s, pc[1] + 6 * s, 8 * s, 10 * s))
    pygame.draw.circle(q, (24, 22, 28), (int(pc[0]), int(pc[1] + 11 * s)), max(2, int(2.4 * s)))


# =====================================================================
# ENTRADA: uma carta cai do céu e ele se teleporta pra ela
# =====================================================================
E_CAI, E_PUF, E_FIM = 34, 50, 90


def entrada(l, t, jogo):
    if t < E_PUF:
        l.esconde = True
    else:
        if t == E_PUF:
            l.esconde = False
            fumaca(jogo, l.x, l.y - 60 * l.s, 12, (230, 230, 240), 5, -1)
            som.tocar("puf")
        l.sobrepor = dict(POSES_KUN["k_vitoria"]) if t < E_FIM - 20 else \
            misturar(POSES_KUN["k_vitoria"], POSES_KUN["parado"], suave((t - (E_FIM - 20)) / 20))
    if t < E_CAI and t % 12 == 0:
        som.tocar("vento", 0.3)
    l.t += 1


def entrada_efeito(l, tela, t):
    s = l.s / 1.36
    if t < E_CAI:  # a carta caindo girando
        k = t / E_CAI
        y = -40 + (CHAO - 20 + 40) * k
        x = l.x + math.sin(t * 0.25) * 30 * (1 - k)
        carta(tela, (x, y), t * 0.3, 3.0 * s, math.cos(t * 0.4), brilha=True, l=l)
    elif t < E_PUF + 8:
        carta_no_chao(tela, l.x, s, t, l=l)


# =====================================================================
# VITÓRIA: embaralha as cartas no ar e mostra a carta
# =====================================================================
def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES_KUN["k_brinca"] if t < 50 else POSES_KUN["k_vitoria"])
    if t == 50:
        som.tocar("confirma", 0.5)


def vitoria_efeito(l, tela, t):
    if t >= 50:
        return
    p = l.pose_vista or l.pose_atual()
    a, b = l.ponto(p, "mt"), l.ponto(p, "mf")
    for i in range(6):  # cartas pulando de uma mão pra outra
        k = ((t * 0.08) + i / 6) % 1
        x = a[0] + (b[0] - a[0]) * k
        y = a[1] + (b[1] - a[1]) * k - math.sin(k * math.pi) * 50 * l.s
        carta(tela, (x, y), k * 3, 2.0 * l.s / 1.36, math.cos(k * 6), l=l)
