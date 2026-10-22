"""CRÁQUEN: o capitão pirata fantasma (criado com o Gomes).

Aparência: fantasma azul-esverdeado meio transparente, chapéu de capitão pirata, barba de algas e, no lugar das
pernas, uma CAUDA DE FANTASMA (ele flutua).
  E      ÂNCORA ACORRENTADA: joga a âncora e PUXA o oponente pra perto (9)
  Q      TENTÁCULO: um tentáculo do polvo gigante sai do chão e joga pra cima (11) — dá combo aéreo
  R      ESPADA FANTASMA: 4 cortes (3 cada)
  SHIFT  ATRAVESSAR: vira névoa, aparece atrás do oponente e dá um SUSTO que deixa tonto (8)
  Z      ULTIMATE: O NAVIO FANTASMA surge do fundo e dispara uma rajada de canhões (32)
  Passiva: INTANGÍVEL — parado 2 segundos (era 1: nerf do Gomes), fica bem transparente e o próximo golpe que levar ATRAVESSA (sem dano).
  Entrada: sobe do chão num redemoinho de névoa.
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from corpo import cabeca_eixos, eixos, mais
from golpes import GOLPES, misturar, proporcionar, suave
from max10 import brilho, fumaca
import pecas
from pecas import Peca

NEVOA = (170, 230, 220)
ALFA_NORMAL, ALFA_INTANGIVEL, ALFA_NEVOA = 200, 90, 40
PARADO_PRA_SUMIR = 120  # quadros parado pra ficar INTANGÍVEL

POSES_CRAQUEN = {
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
    "q_joga": dict(pt=(-28, 0), jt=(-18, 26), pf=(26, 0), jf=(28, 28), qd=(0, 50), pc=(10, 86), cb=(16, 102),
                   ct=(-12, 76), mt=(-24, 82), cf=(30, 88), mf=(56, 92)),
    "q_puxa": dict(pt=(-28, 0), jt=(-18, 26), pf=(26, 0), jf=(28, 28), qd=(-4, 50), pc=(-6, 86), cb=(-4, 104),
                   ct=(-18, 74), mt=(-6, 80), cf=(4, 80), mf=(16, 82)),
    "q_comanda": dict(pt=(-22, 0), jt=(-14, 26), pf=(22, 0), jf=(24, 28), qd=(0, 52), pc=(6, 88), cb=(10, 106),
                      ct=(-8, 72), mt=(-2, 60), cf=(24, 96), mf=(46, 112)),
    "q_corte_a": dict(pt=(-28, 0), jt=(-18, 26), pf=(28, 0), jf=(30, 28), qd=(0, 48), pc=(10, 84), cb=(16, 100),
                      ct=(-6, 72), mt=(2, 82), cf=(26, 98), mf=(50, 108)),
    "q_corte_b": dict(pt=(-28, 0), jt=(-18, 26), pf=(28, 0), jf=(30, 28), qd=(0, 48), pc=(12, 82), cb=(18, 98),
                      ct=(-6, 72), mt=(2, 82), cf=(28, 78), mf=(52, 64)),
    "q_buu": dict(pt=(-14, 0), jt=(-8, 28), pf=(14, 0), jf=(14, 28), qd=(0, 56), pc=(6, 94), cb=(12, 114),
                  ct=(-4, 104), mt=(8, 126), cf=(22, 104), mf=(40, 122)),
    "q_espera": dict(pt=(-20, 0), jt=(-14, 26), pf=(20, 0), jf=(20, 28), qd=(0, 52), pc=(2, 88), cb=(4, 106),
                     ct=(-10, 72), mt=(-6, 58), cf=(16, 84), mf=(12, 100)),
    "q_ri": dict(pt=(-20, 0), jt=(-16, 28), pf=(20, 0), jf=(18, 28), qd=(0, 56), pc=(-2, 92), cb=(-6, 110),
                 ct=(-10, 72), mt=(-4, 58), cf=(16, 104), mf=(20, 128)),
    # (o tentáculo: chama com a mão perto do chão e LEVANTA com força — pedido do Gomes: mais fluido)
    "q_comanda_prep": dict(pt=(-22, 0), jt=(-14, 24), pf=(22, 0), jf=(24, 24), qd=(0, 46), pc=(8, 82), cb=(12, 100),
                           ct=(-8, 68), mt=(-4, 56), cf=(22, 64), mf=(34, 52)),
    "q_comanda_forte": dict(pt=(-22, 0), jt=(-14, 26), pf=(22, 0), jf=(24, 28), qd=(0, 54), pc=(2, 90), cb=(4, 108),
                            ct=(-10, 74), mt=(-6, 62), cf=(20, 104), mf=(32, 124)),
}
proporcionar(POSES_CRAQUEN)


def nevoa(jogo, x, y, n=8, forca=3):
    fumaca(jogo, x, y, n, NEVOA, forca, -0.8)


# =====================================================================
# A passiva INTANGÍVEL e a transparência (a névoa)
# =====================================================================
def todo_quadro(l, jogo):
    x = l.extra
    if x.get("atravessou", 0) > 0:
        x["atravessou"] -= 1
    if not x.get("intangivel"):
        x["parado_t"] = x.get("parado_t", 0) + 1 if l.estado == "parado" else 0
        if x["parado_t"] >= PARADO_PRA_SUMIR and l.f.get("habilidade") == "intangivel":
            x["intangivel"] = True
            nevoa(jogo, l.x, l.y - 60 * l.s, 6, 2)
            som.tocar("puf", 0.4)
    alfa = ALFA_INTANGIVEL if x.get("intangivel") else ALFA_NORMAL
    if l.estado == "ataque" and l.nome_golpe == "craquen_atravessa" and S_NEVOA <= l.t < S_TELE + 3:
        alfa = ALFA_NEVOA
    x["alfa"] = alfa


def atravessar_golpe(l):
    """INTANGÍVEL: o golpe atravessou (chamado no receber do lutador). Volta a precisar ficar parado."""
    x = l.extra
    x["intangivel"] = False
    x["parado_t"] = 0
    x["atravessou"] = 40
    l.inv = max(l.inv, 10)
    som.tocar("puf", 0.6)


def desenhar_sempre(l, tela):
    if l.extra.get("atravessou", 0) > 0:
        from efeitos import texto_grande
        k = 40 - l.extra["atravessou"]
        texto_grande(tela, "ATRAVESSOU!", 20, NEVOA, (int(l.x), int(l.y - 150 * l.s - k)), contorno=(10, 40, 50))


# =====================================================================
# E: A ÂNCORA ACORRENTADA (puxa pra perto)
# =====================================================================
E_SAI, E_VAI, E_VEL, E_ALCANCE = 8, 22, 16, 300


def ancora(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t == E_SAI:
        m["ax"] = l.x + l.dir * 30 * l.s
        som.tocar("vento", 0.6)
    if "ax" not in m:
        return
    if l.acertou and "pegou" not in m:
        m["pegou"] = t
        som.tocar("chute", 0.6)
    if "pegou" in m:  # PUXANDO: o oponente vem junto com a âncora
        alvo = l.x + l.dir * 76 * l.s
        outro.x += (alvo - outro.x) * 0.25
        outro.vx = 0
        m["ax"] = outro.x
        m["caixa"] = None
        if t - m["pegou"] > 18 or abs(outro.x - alvo) < 6:
            return "fim"
        return
    if t < E_SAI + E_VAI and abs(m["ax"] - l.x) < E_ALCANCE:  # indo
        m["ax"] = max(PAREDE_E, min(PAREDE_D, m["ax"] + E_VEL * l.dir))
        rel = (m["ax"] - l.x) * l.dir / l.s
        m["caixa"] = (rel - 14, 50, rel + 16, 100)
    else:  # errou: volta pra mão
        m["caixa"] = None
        m["ax"] += (l.x + l.dir * 30 * l.s - m["ax"]) * 0.3
        if abs(m["ax"] - (l.x + l.dir * 30 * l.s)) < 10:
            return "fim"


def desenha_ancora(tela, x, y, s, d, branco=False):
    cor, borda = ((230, 230, 236) if branco else (120, 140, 150)), (12, 20, 26)
    pts = [(x, y - 14 * s), (x, y + 10 * s)]
    pygame.draw.line(tela, borda, pts[0], pts[1], max(3, int(5 * s)))
    pygame.draw.line(tela, cor, pts[0], pts[1], max(2, int(3 * s)))
    pygame.draw.arc(tela, borda, (x - 12 * s, y - 4 * s, 24 * s, 18 * s), math.pi, 2 * math.pi, max(3, int(5 * s)))
    pygame.draw.arc(tela, cor, (x - 12 * s, y - 4 * s, 24 * s, 18 * s), math.pi, 2 * math.pi, max(2, int(3 * s)))
    for k in (-1, 1):
        pygame.draw.polygon(tela, cor, [(x + k * 12 * s, y + 4 * s), (x + k * 16 * s, y), (x + k * 10 * s, y)])
    pygame.draw.circle(tela, borda, (int(x), int(y - 16 * s)), max(2, int(4 * s)), max(1, int(2 * s)))
    pygame.draw.line(tela, cor, (x - 7 * s, y - 8 * s), (x + 7 * s, y - 8 * s), max(1, int(2 * s)))


def ancora_efeito(l, tela):
    m = l.memo
    if "ax" not in m:
        return
    p = l.pose_vista or l.pose_atual()
    mao = l.ponto(p, "mf")
    ay = l.y - 76 * l.s
    for k in range(14):  # a corrente
        q = k / 14
        x = mao[0] + (m["ax"] - mao[0]) * q
        y = mao[1] + (ay - mao[1]) * q + math.sin(q * math.pi) * 8 * l.s
        pygame.draw.circle(tela, (12, 20, 26), (int(x), int(y)), max(2, int(2.6 * l.s)))
        pygame.draw.circle(tela, (150, 170, 176), (int(x), int(y)), max(1, int(1.6 * l.s)))
    desenha_ancora(tela, m["ax"], ay, l.s * 1.3, l.dir)


# =====================================================================
# Q: O TENTÁCULO (sai do chão e joga pra cima)
# =====================================================================
Q_INI, Q_ATIVO = 12, 8


def tentaculo_efeito(l, tela):
    t = l.t
    if t < 6:
        return
    x0 = l.x + l.dir * 92 * l.s
    if t < Q_INI:
        k = (t - 6) / (Q_INI - 6) * 0.25
    elif t < Q_INI + Q_ATIVO + 4:
        k = 0.25 + 0.75 * suave(min(1, (t - Q_INI) / 6))
    else:
        k = max(0.0, 1 - (t - Q_INI - Q_ATIVO - 4) / 10)
    if k <= 0:
        return
    altura = 140 * l.s * k
    borda, roxo, ventosa = (20, 10, 26), (120, 60, 130), (220, 170, 200)
    pts_e, pts_d = [], []
    for i in range(13):
        q = i / 12
        y = CHAO - altura * q
        curva = math.sin(q * 3 + t * 0.3) * 12 * l.s * q
        larg = (16 - 13 * q) * l.s
        pts_e.append((x0 + curva - larg, y))
        pts_d.append((x0 + curva + larg, y))
    forma = pts_e + pts_d[::-1]
    pygame.draw.polygon(tela, borda, forma)
    pygame.draw.polygon(tela, roxo, [(x + (x0 - x) * 0.12, y) for x, y in forma])
    for i in range(1, 10, 2):  # as ventosas
        q = i / 12
        cx = (pts_e[i][0] + pts_d[i][0]) / 2 - l.dir * (16 - 13 * q) * l.s * 0.5
        pygame.draw.circle(tela, ventosa, (int(cx), int(pts_e[i][1])), max(1, int((4 - 2.5 * q) * l.s)))
    pygame.draw.ellipse(tela, (60, 40, 30), (x0 - 30 * l.s, CHAO - 6 * l.s, 60 * l.s, 12 * l.s))  # o buraco


# =====================================================================
# R: A ESPADA FANTASMA (4 cortes)
# =====================================================================
R_INI, R_INTERVALO, R_HITS = 8, 8, 4


def espada(l, outro, jogo):
    t = l.t
    l.vx = 0.8 * l.dir if R_INI <= t < R_INI + R_HITS * R_INTERVALO else 0
    if R_INI <= t < R_INI + R_HITS * R_INTERVALO and (t - R_INI) % R_INTERVALO == 0:
        som.tocar("vento", 0.5)
    l.fisica(jogo)
    if t >= R_INI + R_HITS * R_INTERVALO + 12:
        return "fim"


def espada_efeito(l, tela):
    u = l.t - R_INI
    if 0 <= u < R_HITS * R_INTERVALO and u % R_INTERVALO < 3:  # o rastro do corte
        cima = (u // R_INTERVALO) % 2 == 0
        r = 44 * l.s
        cx, cy = l.x + 36 * l.s * l.dir, l.y - 88 * l.s
        a0 = -0.9 if cima else 0.2
        if l.dir < 0:
            a0 = math.pi - a0 - 1.0
        pygame.draw.arc(tela, NEVOA, (cx - r, cy - r, 2 * r, 2 * r), a0, a0 + 1.0, max(2, int(5 * l.s)))


def espada_quadros():
    q = [(0, "parado"), (R_INI - 3, "q_corte_b")]
    for k in range(R_HITS):
        a, b = ("q_corte_a", "q_corte_b") if k % 2 == 0 else ("q_corte_b", "q_corte_a")
        q.append((R_INI + k * R_INTERVALO + 1, a))
        q.append((R_INI + k * R_INTERVALO + 5, b))
    q.append((R_INI + R_HITS * R_INTERVALO + 12, "parado"))
    return q


# =====================================================================
# SHIFT: ATRAVESSAR (vira névoa, aparece atrás e dá um SUSTO)
# =====================================================================
S_NEVOA, S_TELE, S_SUSTO = 6, 16, 20


def atravessa(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t == S_NEVOA:
        nevoa(jogo, l.x, l.y - 60 * l.s, 10, 4)
        som.tocar("vento", 0.5)
        m["de"] = l.x
        lado = 1 if outro.x > l.x else -1
        m["para"] = max(PAREDE_E, min(PAREDE_D, outro.x + lado * 70 * outro.s))
    if S_NEVOA <= t < S_TELE:
        l.inv = max(l.inv, 2)
    if t == S_TELE:  # do outro lado!
        l.x = m["para"]
        l.dir = 1 if outro.x > l.x else -1
        nevoa(jogo, l.x, l.y - 60 * l.s, 10, 4)
    if t == S_SUSTO:
        som.tocar("ultimate", 0.4)
    if l.acertou and "assustou" not in m:  # BUUU! fica TONTO
        m["assustou"] = True
        outro.mudar("tonto")
        outro.tonto_tempo = 50
        outro.vx = 0
    if t >= S_SUSTO + 22:
        return "fim"


def atravessa_efeito(l, tela):
    m = l.memo
    t = l.t
    if "de" in m and S_NEVOA <= t < S_TELE + 2:  # o rastro de névoa passando
        k = (t - S_NEVOA) / (S_TELE - S_NEVOA)
        x = m["de"] + (m["para"] - m["de"]) * min(1, k)
        for i in range(5):
            xx = x - (m["para"] - m["de"]) * 0.06 * i
            pygame.draw.circle(tela, NEVOA, (int(xx), int(l.y - (70 - i * 6) * l.s)), max(2, int((14 - i * 2) * l.s)))
    if S_SUSTO <= t < S_SUSTO + 16:
        from efeitos import texto_grande
        texto_grande(tela, "BUUU!", 26, (220, 255, 240), (int(l.x + l.dir * 40 * l.s), int(l.y - 150 * l.s)),
                     contorno=(10, 40, 50))


# =====================================================================
# Z: ULTIMATE — O NAVIO FANTASMA (rajada de canhões)
# =====================================================================
U_MIRA, U_SURGE, U_ESPERA, U_TIROS, U_INTERVALO, U_DANO = 8, 12, 34, 8, 9, 4  # 8 x 4 = 32 (nerf do Gomes)
U_FIM = U_MIRA + U_ESPERA + U_TIROS * U_INTERVALO + 40


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t == 4:
        som.tocar("carga")
    if t == U_SURGE:
        som.tocar("terra")
        jogo.tremer(6)
        m["navio_x"] = l.x - l.dir * 120 * l.s
    if t == U_MIRA:  # os TENTÁCULOS agarram (defender não adianta: só quem já está no ar escapa)
        m["alvo"] = (outro.x, outro.y - 50 * outro.s)
        livre = outro.no_chao() and outro.estado not in ("caido", "agarrado") and outro.inv == 0
        if livre:
            m["pegou"] = t
            outro.mudar("agarrado")
            outro.golpe = None
            outro.sobrepor = dict(outro.poses["golpeado"])
            outro.y, outro.vx, outro.vy = CHAO, 0, 0
            l.inv = 999
        else:
            m["errou"] = t
    u = t - U_MIRA - U_ESPERA
    if 0 <= u < U_TIROS * U_INTERVALO and u % U_INTERVALO == 0:  # FOGO!
        som.tocar("explosao", 0.5)
        if "pegou" in m:
            ultimo = u // U_INTERVALO == U_TIROS - 1
            outro.levar(U_DANO, l, GOLPES["craquen_ultimate"])
            if not ultimo:
                outro.vida = max(1, outro.vida)
            outro.tremor_hit = 6
            jogo.faisca(outro.x + random.uniform(-20, 20), outro.y - random.uniform(30, 90) * outro.s, False, ultimo)
            jogo.tremer(5)
    if "pegou" in m and u == U_TIROS * U_INTERVALO + 4:
        outro.sobrepor = {}
        outro.mudar("voando")
        outro.vx, outro.vy = 6 * l.dir, -9
        l.inv = 0
    if "errou" in m and t >= U_MIRA + 30:
        return "fim"
    if t >= U_FIM:
        return "fim"


def desenha_navio(tela, x, base, s, d, k, t):
    """O navio fantasma (k = quanto já subiu do chão, 0 a 1)."""
    alfa = int(170 * k)
    if alfa <= 4:
        return
    sup = pygame.Surface((int(320 * s), int(300 * s)), pygame.SRCALPHA)
    w, h = sup.get_size()
    casco = [(w * 0.05, h * 0.62), (w * 0.95, h * 0.62), (w * 0.82, h * 0.92), (w * 0.18, h * 0.92)]
    pygame.draw.polygon(sup, (40, 90, 96, 255), casco)
    pygame.draw.polygon(sup, (120, 200, 200, 255), casco, max(2, int(3 * s)))
    for i in range(4):  # as janelinhas dos canhões
        cx = w * (0.25 + i * 0.16)
        pygame.draw.circle(sup, (10, 20, 24, 255), (int(cx), int(h * 0.74)), max(3, int(7 * s)))
    pygame.draw.line(sup, (90, 150, 150, 255), (w * 0.5, h * 0.62), (w * 0.5, h * 0.05), max(3, int(6 * s)))
    for y0, larg in ((0.1, 0.32), (0.34, 0.4)):  # as velas rasgadas
        vela = [(w * (0.5 - larg / 2), h * y0), (w * (0.5 + larg / 2), h * y0),
                (w * (0.5 + larg / 2 - 0.04), h * (y0 + 0.2)), (w * 0.55, h * (y0 + 0.17)),
                (w * 0.48, h * (y0 + 0.22)), (w * (0.5 - larg / 2 + 0.03), h * (y0 + 0.19))]
        pygame.draw.polygon(sup, (190, 230, 220, 255), vela)
    sup.set_alpha(alfa)
    if d < 0:
        sup = pygame.transform.flip(sup, True, False)
    y = base - h + (1 - k) * h * 0.8 + math.sin(t * 0.08) * 4 * s
    tela.blit(sup, (x - w / 2, y))


def ultimate_efeito(l, tela):
    m = l.memo
    t = l.t
    if "navio_x" not in m:
        return
    k = min(1.0, (t - U_SURGE) / 20) if t < U_FIM - 15 else max(0.0, (U_FIM - t) / 15)
    desenha_navio(tela, m["navio_x"], CHAO + 30, l.s * 1.4, l.dir, k, t)
    if "pegou" in m and t < U_MIRA + U_ESPERA + U_TIROS * U_INTERVALO + 4:  # os tentáculos segurando
        ax = m["alvo"][0]
        for i, dx in enumerate((-30, 0, 30)):
            kk = min(1.0, (t - U_MIRA) / 6)
            x0 = ax + dx * l.s
            topo = CHAO - (40 + 30 * (i == 1)) * l.s * kk
            pts = [(x0 - 7 * l.s, CHAO), (x0 + math.sin(t * 0.3 + i) * 6 * l.s, topo), (x0 + 7 * l.s, CHAO)]
            pygame.draw.polygon(tela, (20, 10, 26), pts)
            pygame.draw.polygon(tela, (120, 60, 130), [(x + (x0 - x) * 0.25, y) for x, y in pts])
    if "alvo" in m:
        u = t - U_MIRA - U_ESPERA
        for i in range(U_TIROS):  # as balas de canhão voando até o alvo
            v = u - i * U_INTERVALO
            if 0 <= v < 10:
                q = v / 10
                ox, oy = m["navio_x"] + l.dir * (40 + (i % 4) * 22) * l.s, CHAO - 40 * l.s
                ax, ay = m["alvo"]
                x = ox + (ax - ox) * q
                y = oy + (ay - oy) * q - math.sin(q * math.pi) * 60 * l.s
                pygame.draw.circle(tela, (10, 12, 16), (int(x), int(y)), max(3, int(7 * l.s)))
                pygame.draw.circle(tela, (60, 70, 80), (int(x - 2), int(y - 2)), max(1, int(3 * l.s)))
            if 0 <= v < 4:
                ox = m["navio_x"] + l.dir * (40 + (i % 4) * 22) * l.s
                brilho(tela, (int(ox), int(CHAO - 40 * l.s)), int(24 * l.s), (255, 220, 120), 160)


def ultimate_quadros():
    return [(0, "parado"), (6, "q_comanda"), (U_MIRA + U_ESPERA, "q_comanda"), (U_MIRA + U_ESPERA + 8, "q_ri"),
            (U_FIM - 10, "q_ri"), (U_FIM, "parado")]


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


_registra("craquen_ancora", ini=E_SAI, ativo=E_VAI, rec=14, janelas=((E_SAI + 1, E_SAI + E_VAI),), dano=9, hit=34,
          defe=10, emp=0, nivel="medio", logica=ancora, efeito=ancora_efeito, ia="longe",
          quadros=[(0, "parado"), (5, "q_joga"), (E_SAI + 6, "q_joga"), (E_SAI + E_VAI, "q_puxa"),
                   (E_SAI + E_VAI + 16, "parado")])
GOLPES["craquen_ancora"]["total"] = 9999
_registra("craquen_tentaculo", ini=Q_INI, ativo=Q_ATIVO, rec=20, caixa=(58, 0, 128, 140), dano=11, hit=24, defe=12,
          emp=2, nivel="medio", lanca=17, efeito=tentaculo_efeito, ia="anti", som="terra",
          quadros=[(0, "parado"), (5, "q_comanda_prep"), (Q_INI - 2, "q_comanda_prep"), (Q_INI + 1, "q_comanda"),
                   (Q_INI + 5, "q_comanda_forte"), (Q_INI + Q_ATIVO + 8, "q_comanda_forte"),
                   (Q_INI + Q_ATIVO + 20, "parado")])
_registra("craquen_espada", ini=R_INI, ativo=R_HITS * R_INTERVALO, rec=12,
          janelas=tuple((R_INI + k * R_INTERVALO, R_INI + k * R_INTERVALO + 3) for k in range(R_HITS)),
          caixa=(12, 40, 96, 124), dano=3, hit=11, defe=7, emp=1, nivel="medio", logica=espada,
          efeito=espada_efeito, ia="perto", quadros=espada_quadros())
_registra("craquen_atravessa", ini=S_SUSTO, ativo=5, rec=17, janelas=((S_SUSTO, S_SUSTO + 5),),
          caixa=(6, 30, 84, 126), dano=8, hit=20, defe=10, emp=1, nivel="medio", logica=atravessa,
          efeito=atravessa_efeito, ia="medio",
          quadros=[(0, "parado"), (S_NEVOA, "parado"), (S_TELE, "parado"), (S_SUSTO - 1, "q_buu"),
                   (S_SUSTO + 12, "q_buu"), (S_SUSTO + 22, "parado")])
_registra("craquen_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=ultimate, efeito=ultimate_efeito, ia="ultimate", quadros=ultimate_quadros())
GOLPES["craquen_ultimate"]["total"] = 9999

GOLPES_CRAQUEN = {"E": "craquen_ancora", "Q": "craquen_tentaculo", "R": "craquen_espada",
                  "SHIFT": "craquen_atravessa", "Z": "craquen_ultimate"}

# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  c C v casaco  g dourado  w camisa  b cinto  p P q pele de fantasma  e olho  a A barba de alga
PALETA = {
    "k": (8, 26, 34), "c": (34, 84, 104), "C": (60, 122, 144), "v": (18, 52, 66), "g": (226, 196, 90),
    "w": (180, 226, 226), "b": (40, 30, 24), "p": (164, 226, 226), "P": (204, 246, 246), "q": (110, 180, 188),
    "e": (230, 255, 150), "a": (60, 150, 110), "A": (90, 190, 140),
}
S_REF = 1.36 / 3


def _m(linhas, w):
    return [linha.ljust(w, ".")[:w] for linha in linhas]


TRONCO = Peca(_m([
    "...kkkkkkkk...",
    "..kcCcwwcccvk.",
    ".kcCCcwwccccvk",
    ".kcCgcwwcgccvk",
    ".kcCccwwccccvk",
    ".kcCgcwwcgccvk",
    ".kcCccwwccccvk",
    "..kcCgwwgccvk.",
    "..kcCcwwcccvk.",
    "..kbbbbbbbbbk.",
    "..kbbbgbbbbbk.",
    "..kcccccccvvk.",
    "..kccccccccvk.",
    "...kcccccvk...",
    "....kkkkkk....",
], 14), PALETA, a=(7, 13), b=(7, 1))

CABECA = Peca(_m([
    "...kkkkkk.....",
    "..kppppppkk...",
    ".kpppppppppk..",
    "kpppppppppppk.",
    "kpppkppppepk..",
    "kppppppppppk..",
    ".kpPpppppPpk..",
    ".kaaaaaaaaak..",
    "..kaAaaaAaak..",
    "..kaaaAaaak...",
    "...kaaaAak....",
    "...kaAaak.....",
    "....kaak......",
    ".....kk.......",
], 14), PALETA, a=(6, 7), b=(6, 0), estica=False)

BRACO = Peca(_m([
    ".kkkk.",
    "kcCcvk",
    "kcCcvk",
    "kcccvk",
    "kcccvk",
    "kcccvk",
    ".kkkk.",
], 6), PALETA, a=(2, 0), b=(2, 6))

ANTEBRACO = Peca(_m([
    ".kkk.",
    "kcCvk",
    "kccvk",
    "kccvk",
    "kccvk",
    "kgggk",
    "kwwwk",
    ".kkk.",
], 5), PALETA, a=(2, 0), b=(2, 7))

MAO = Peca(_m([
    ".kkkk.",
    "kpPPqk",
    "kpPpqk",
    "kqqqqk",
    ".kkkk.",
], 6), PALETA, a=(2, 0), b=(2, 4), estica=False)


def _cor(letra):
    return (pecas.TROCA or {}).get(letra, PALETA[letra])


def cauda_fantasma(tela, l, P, esc, d, branco):
    """No lugar das pernas: a cauda de fantasma, lisa e ondulando. Nos CHUTES (e na rasteira) é a cauda que bate:
    a ponta vai até onde estaria o pé que chuta."""
    q = P("qd")
    chutando = l.estado == "ataque" and l.golpe and ("chute" in l.nome_golpe or l.golpe.get("pose", "").endswith("chute"))
    if chutando:
        ponta = P("pf")
    else:
        pes = ((P("pt")[0] + P("pf")[0]) / 2, max(P("pt")[1], P("pf")[1]))
        ponta = (pes[0] - d * 16 * esc + math.sin(l.t * 0.12) * 5 * esc, pes[1] - 6 * esc)
    ctrl = (q[0] - d * 4 * esc, (q[1] + ponta[1]) / 2 + 6 * esc)  # (a curva da cauda)
    esq, dir_ = [], []
    n = 16
    for k in range(n + 1):
        u = k / n
        x = (1 - u) ** 2 * q[0] + 2 * (1 - u) * u * ctrl[0] + u * u * ponta[0]
        y = (1 - u) ** 2 * q[1] + 2 * (1 - u) * u * ctrl[1] + u * u * ponta[1]
        tx = 2 * (1 - u) * (ctrl[0] - q[0]) + 2 * u * (ponta[0] - ctrl[0])
        ty = 2 * (1 - u) * (ctrl[1] - q[1]) + 2 * u * (ponta[1] - ctrl[1])
        tn = math.hypot(tx, ty) or 1
        nx, ny = -ty / tn, tx / tn
        larg = (11 * (1 - u) ** 0.8 + 0.8) * esc + math.sin(l.t * 0.2 + u * 9) * 1.2 * esc * u
        esq.append((x + nx * larg, y + ny * larg))
        dir_.append((x - nx * larg, y - ny * larg))
    forma = esq + dir_[::-1]
    cor = (245, 245, 250) if branco else _cor("c")
    pygame.draw.polygon(tela, _cor("k") if not branco else (150, 150, 160), forma)
    pygame.draw.lines(tela, _cor("k") if not branco else (150, 150, 160), True, forma, max(2, int(esc * 1.2)))
    pygame.draw.polygon(tela, cor, forma)
    meio = [(a[0] * 0.6 + b[0] * 0.4, a[1] * 0.6 + b[1] * 0.4) for a, b in zip(esq, dir_)]
    pygame.draw.lines(tela, _cor("C") if not branco else cor, False, meio[:-2], max(1, int(esc)))  # o brilho
    pygame.draw.circle(tela, cor, (int(ponta[0]), int(ponta[1])), max(1, int(esc * 1.4)))  # a pontinha
    if l.f.get("estilo") == "mumia" and not branco:  # MÚMIA: as faixas enroladas na cauda (e a ponta solta)
        for k in range(2, n - 1, 3):
            pygame.draw.line(tela, _cor("k"), esq[k], dir_[k + 1], max(1, int(esc * 0.9)))
            pygame.draw.line(tela, (236, 222, 184), esq[k], dir_[k + 1], max(1, int(esc * 0.5)))
        solta = [ponta]
        for k in range(1, 6):
            solta.append((ponta[0] - d * k * 4 * esc, ponta[1] - k * 1.5 * esc + math.sin(l.t * 0.25 + k) * 2.4 * esc))
        pygame.draw.lines(tela, _cor("k"), False, solta, max(2, int(esc * 1.8)))
        pygame.draw.lines(tela, (230, 214, 170), False, solta, max(1, int(esc * 1.1)))


def saia_casaco(tela, P, esc, d, branco):
    """O casaco abrindo na cintura (emenda o corpo na cauda, sem quina)."""
    q, c = P("qd"), P("pc")
    (ux, uy), _ = eixos(q, c)
    nx, ny = -uy, ux
    pts = [(q[0] + nx * 9 * esc + ux * 10 * esc, q[1] + ny * 9 * esc + uy * 10 * esc),
           (q[0] - nx * 9 * esc + ux * 10 * esc, q[1] - ny * 9 * esc + uy * 10 * esc),
           (q[0] - nx * 13 * esc - ux * 9 * esc, q[1] - ny * 13 * esc - uy * 9 * esc),
           (q[0] - ux * 13 * esc, q[1] - uy * 13 * esc),
           (q[0] + nx * 13 * esc - ux * 9 * esc, q[1] + ny * 13 * esc - uy * 9 * esc)]
    cor = (245, 245, 250) if branco else _cor("v")
    pygame.draw.polygon(tela, _cor("k") if not branco else (150, 150, 160), pts)
    meio = (sum(x for x, _ in pts) / 5, sum(y for _, y in pts) / 5)
    pygame.draw.polygon(tela, cor, [(x + (meio[0] - x) * 0.12, y + (meio[1] - y) * 0.12) for x, y in pts])


def faixas_mumia(tela, P, Pc, esc, branco=False):
    """MÚMIA (roupa secreta, código MAGICCREATURES): a cabeça enrolada em ataduras e faixas no peito."""
    if branco:
        return
    borda, faixa, sombra = (40, 30, 18), (236, 222, 184), (196, 178, 136)
    for y0, inclina in ((-0.6, 0.6), (1.2, -0.4), (2.8, 0.5), (6.4, -0.3)):  # as voltas em volta da cabeça
        a, b = P(-0.6, y0 + inclina), P(12.6, y0 - inclina)
        pygame.draw.line(tela, borda, a, b, max(2, int(esc * 1.8)))
        pygame.draw.line(tela, faixa if y0 < 6 else sombra, a, b, max(1, int(esc * 1.1)))
    ponta = [P(0, 1), P(-3, 3.2), P(-5, 5.5), P(-6.4, 8.5)]  # a pontinha solta atrás da cabeça
    pygame.draw.lines(tela, borda, False, ponta, max(2, int(esc * 1.6)))
    pygame.draw.lines(tela, faixa, False, ponta, max(1, int(esc * 0.9)))
    q, c = Pc("qd"), Pc("pc")
    for k in (0.3, 0.6, 0.85):  # faixas cruzando o peito (seguindo o tronco)
        x1, y1 = q[0] + (c[0] - q[0]) * k, q[1] + (c[1] - q[1]) * k
        a, b = (x1 - 5 * esc, y1 + 2 * esc), (x1 + 5 * esc, y1 - 2 * esc)
        pygame.draw.line(tela, borda, a, b, max(2, int(esc * 1.6)))
        pygame.draw.line(tela, faixa, a, b, max(1, int(esc * 0.9)))


def chapeu_pirata(tela, P, esc, branco=False):
    """O tricórnio de capitão (com a caveirinha)."""
    preto, dourado, borda = ((240, 240, 244) if branco else (22, 30, 40)), (226, 196, 90), (6, 10, 14)
    aba = [P(-2.5, 2.4), P(1, -0.4), P(6.5, 0.6), P(12, -0.4), P(15, 2.4), P(6.5, 3.4)]
    copa = [P(1.5, 1), P(3, -4.4), P(6.5, -6), P(10, -4.4), P(11.5, 1)]
    for pts in (copa, aba):
        pygame.draw.polygon(tela, borda, pts)
        pygame.draw.polygon(tela, borda, pts, max(2, int(esc * 1.1)))
    pygame.draw.polygon(tela, preto, copa)
    pygame.draw.polygon(tela, preto, aba)
    pygame.draw.lines(tela, dourado, False, [P(-2, 2.2), P(1, -0.1), P(6.5, 0.9), P(12, -0.1), P(14.5, 2.2)],
                      max(1, int(esc * 0.6)))
    c = P(6.5, -2.4)
    pygame.draw.circle(tela, (240, 240, 236), (int(c[0]), int(c[1])), max(1, int(esc * 1.1)))  # a caveirinha


def espada_na_mao(tela, l, P, esc, branco=False):
    m, c = P("mf"), P("cf")
    (dx, dy), _ = eixos(c, m)
    ponta = (m[0] + dx * 26 * esc / 2.2, m[1] + dy * 26 * esc / 2.2)
    curva = (m[0] + dx * 14 * esc / 2.2 - dy * 3 * esc / 2.2, m[1] + dy * 14 * esc / 2.2 + dx * 3 * esc / 2.2)
    pygame.draw.lines(tela, (8, 26, 34), False, [m, curva, ponta], max(3, int(esc * 1.4)))
    pygame.draw.lines(tela, (240, 240, 244) if branco else (200, 245, 240), False, [m, curva, ponta],
                      max(2, int(esc * 0.8)))
    pygame.draw.circle(tela, (226, 196, 90), (int(m[0]), int(m[1])), max(2, int(esc * 0.9)))


def desenhar_craquen(l, tela, p, branco):
    esc = l.s / S_REF
    d = l.lado()
    espelho = d < 0
    perto_v = "branco" if branco else "normal"
    longe_v = "branco" if branco else "escuro"
    guarda_y = l.y
    l.y -= (10 + 4 * math.sin(l.t * 0.08)) * l.s  # FLUTUANDO

    def P(k):
        return l.ponto(p, k)

    def braco(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)

    vampiro = l.f.get("estilo") == "vampiro" and not branco
    try:
        if vampiro:  # VAMPIRO (Halloween): a CAPA (atrás de tudo), com a gola alta
            capa_vampiro(tela, P, esc, d)
        braco("ct", "mt", longe_v)
        cauda_fantasma(tela, l, P, esc, d, branco)
        c, cb = P("pc"), P("cb")
        TRONCO.desenhar(tela, P("qd"), c, esc, espelho, perto_v)
        u, _ = cabeca_eixos(c, cb, d)
        pygame.draw.line(tela, _cor("k"), c, mais(cb, u, -3 * esc), max(3, int(5 * esc)))
        pygame.draw.line(tela, _cor("P") if not branco else (240, 240, 240), c, mais(cb, u, -3 * esc),
                         max(1, int(3 * esc)))
        na_cabeca = CABECA.desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
        mumia = l.f.get("estilo") == "mumia"
        if mumia:
            faixas_mumia(tela, na_cabeca, P, esc, branco)
        else:
            chapeu_pirata(tela, na_cabeca, esc, branco)
        olho = na_cabeca(9.5, 4.5)
        if not branco:  # o olho brilhando (na MÚMIA: olho fundo, igual o Husk)
            if mumia:
                pygame.draw.circle(tela, (40, 28, 18), (int(olho[0]), int(olho[1])), max(1, int(esc * 1.3)))
                pygame.draw.circle(tela, (255, 170, 60), (int(olho[0]), int(olho[1])), max(1, int(esc * 0.5)))
            else:
                pygame.draw.circle(tela, (230, 255, 150), (int(olho[0]), int(olho[1])), max(1, int(esc * 0.9)))
        if vampiro:  # as PRESAS
            for x in (8.2, 10.0):
                pygame.draw.polygon(tela, (250, 250, 250), [na_cabeca(x, 6.9), na_cabeca(x + 1.0, 6.9),
                                                            na_cabeca(x + 0.5, 8.6)])
        braco("cf", "mf", perto_v)
        if not (l.estado == "ataque" and l.nome_golpe in ("craquen_ancora", "craquen_ultimate")):
            espada_na_mao(tela, l, P, esc, branco)
        if vampiro:  # os MORCEGOS voando em volta dele (só desenho)
            import eventos
            for k in range(3):
                a = l.t * 0.05 + k * math.tau / 3
                eventos.morcego(tela, l.x + math.cos(a) * 46 * l.s, l.y - 80 * l.s + math.sin(a * 2) * 22 * l.s,
                                l.t + k * 7, 0.55 * l.s / 1.36)
    finally:
        l.y = guarda_y


def capa_vampiro(tela, P, esc, d):
    """A capa do VAMPIRO: preta por fora, vermelha por dentro, com a gola alta atrás da cabeça."""
    c, q, cb = P("pc"), P("qd"), P("cb")
    k = (12, 4, 8)
    fora = [(c[0] + d * 4 * esc, c[1] - 1 * esc), (c[0] - d * 8 * esc, c[1]), (q[0] - d * 20 * esc, q[1] + 26 * esc),
            (q[0] - d * 2 * esc, q[1] + 30 * esc), (q[0] + d * 8 * esc, q[1] + 24 * esc)]
    pygame.draw.polygon(tela, k, fora)
    pygame.draw.polygon(tela, (34, 10, 18), [(x * 0.94 + c[0] * 0.06, y * 0.94 + c[1] * 0.06) for x, y in fora])
    pygame.draw.polygon(tela, (150, 20, 32), [(c[0] - d * 2 * esc, c[1] + 2 * esc), (q[0] - d * 14 * esc, q[1] + 22 * esc),
                                               (q[0] - d * 4 * esc, q[1] + 25 * esc)])
    for lado in (-1, 1):  # a gola alta (duas pontas atrás da cabeça)
        base = (c[0] - d * 2 * esc + lado * 4 * esc, c[1])
        pygame.draw.polygon(tela, k, [base, (cb[0] - d * 6 * esc + lado * 6 * esc, cb[1] - 9 * esc),
                                      (base[0] - d * 3 * esc, base[1] - 2 * esc)])
        pygame.draw.polygon(tela, (150, 20, 32), [(base[0], base[1] - 1 * esc),
                                                   (cb[0] - d * 6 * esc + lado * 5 * esc, cb[1] - 7 * esc),
                                                   (base[0] - d * 2 * esc, base[1] - 2 * esc)])


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Cráquen grande: o chapéu de pirata."""
    cb = P("cb")
    pygame.draw.polygon(q, (22, 30, 40), [(cb[0] - 14 * s, cb[1] - 6 * s), (cb[0] + 14 * s, cb[1] - 6 * s),
                                          (cb[0], cb[1] - 18 * s)])


# =====================================================================
# ENTRADA: sobe do chão num redemoinho de névoa
# =====================================================================
E_SOBE, E_RI = 46, 64


def entrada(l, t, jogo):
    if t < E_SOBE:
        k = suave(t / E_SOBE)
        l.cortar_chao = True
        l.y = CHAO + 150 * l.s * (1 - k)
        if t % 4 == 0:
            nevoa(jogo, l.x + math.cos(t * 0.5) * 40 * l.s, CHAO - 10, 2, 2)
    else:
        l.cortar_chao = False
        l.y = CHAO
        if t == E_RI:
            som.tocar("ultimate", 0.4)
        l.sobrepor = dict(POSES_CRAQUEN["q_ri"]) if E_RI <= t < E_RI + 30 else {}
    l.t += 1


def entrada_efeito(l, tela, t):
    if t < E_SOBE + 10:  # o redemoinho de névoa
        for i in range(10):
            a = t * 0.3 + i * math.tau / 10
            r = (40 + 20 * math.sin(t * 0.1 + i)) * l.s
            x, y = l.x + math.cos(a) * r, CHAO - 10 * l.s - (i * 10 + t) % 120 * l.s
            pygame.draw.circle(tela, NEVOA, (int(x), int(y)), max(2, int(6 * l.s)))


# =====================================================================
# VITÓRIA: ri de capitão pirata com a espada pro alto
# =====================================================================
def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES_CRAQUEN["q_ri"] if t > 8 else POSES_CRAQUEN["parado"])
    if t == 10:
        som.tocar("ultimate", 0.5)


def vitoria_efeito(l, tela, t):
    if 10 <= t < 70 and (t // 8) % 2:
        from efeitos import texto_grande
        texto_grande(tela, "HAR HAR HAR!", 20, NEVOA, (int(l.x), int(l.y - 160 * l.s)), contorno=(10, 40, 50))
