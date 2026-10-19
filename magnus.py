"""MAGNUS: o raptor-robô de fogo (criado pelo Gomes) — rival do MAX-10.

Aparência: dinossauro de fogo meio robô (tipo os dinos "X" do ARK), jeito de Velociraptor/Deinonychus. Sai fumaça
de vez em quando. As penas do pescoço (tipo o raptor do Jurassic Park 3) crescem e encolhem, e saem quando ele atira.
Lore: criado pra povoar uma área deserta e proteger uma base militar... mas fugiu (o "Experimento 13").
  E      tira os espinhos da nuca e ATIRA (6 hits de 2) — PRENDE o oponente meio segundo (não derruba)
  Q      DUAS RABADAS: uma rasteira e uma pro alto (2 hits de 5) — a segunda JOGA PRA CIMA (combo aéreo)
  R      O BOTE: pula, prende no chão e dá várias garradas (10 hits de 2, contando o bote) — derruba
  SHIFT  CORRIDA AGACHADO: se acertar (5), dá uma RABADA DE FOGO que PARALISA 1 segundo (10)
  Z      ULTIMATE: 3 bolas de fogo. Se uma acertar (15), abre uma fumaceira e ele dá a RABADA DE FOGO (20)
  Entrada: um fogo sai do canto da tela e ele entra farejando, andando devagarzinho.
  Passiva CORPO ÁGIL: 30 de vida a menos (70), mas a hitbox é METADE da dos outros e ele é 20% mais rápido.
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from golpes import GOLPES, misturar, proporcionar, suave
from lutador import Projetil
from max10 import brilho, fumaca
import xeno

POSES_MAGNUS = {k: dict(v) for k, v in xeno.POSES_XENO.items()}  # (o jeito de raptor curvado do Xeno)
POSES_MAGNUS.update({
    "m_espinhos": dict(pt=(-26, 0), jt=(-12, 30), pf=(20, 0), jf=(30, 30), qd=(-4, 54), pc=(14, 82), cb=(30, 92),
                       ct=(10, 64), mt=(28, 50), cf=(20, 92), mf=(26, 100)),
    "m_atira": dict(pt=(-28, 0), jt=(-14, 30), pf=(22, 0), jf=(32, 30), qd=(-4, 52), pc=(18, 80), cb=(36, 88),
                    ct=(10, 64), mt=(28, 50), cf=(32, 80), mf=(58, 86)),
    "m_fareja": dict(pt=(-24, 0), jt=(-10, 26), pf=(20, 0), jf=(30, 26), qd=(-4, 46), pc=(20, 66), cb=(42, 64),
                     ct=(16, 52), mt=(30, 40), cf=(28, 54), mf=(44, 42)),
    "m_ruge": dict(pt=(-24, 0), jt=(-10, 30), pf=(22, 0), jf=(30, 30), qd=(-4, 56), pc=(10, 90), cb=(22, 108),
                   ct=(4, 74), mt=(16, 62), cf=(22, 78), mf=(36, 66)),
})
proporcionar(POSES_MAGNUS)

METAL, METAL_ESC, METAL_CLARO = (78, 82, 92), (50, 52, 60), (120, 126, 138)
BRASA, BRASA_CLARA, BORDA = (255, 130, 40), (255, 210, 110), (10, 8, 10)
PALETA = {"m": METAL, "M": METAL_ESC, "c": METAL_CLARO, "b": BRASA, "B": BRASA_CLARA}  # (letras das roupas)
PENAS_VOLTAM = 120  # quadros pras penas crescerem de novo depois de atirar


def chama(jogo, x, y, n=3, forca=1.0):
    """Faíscas de fogo subindo."""
    for _ in range(n):
        cor = random.choice(((255, 220, 120), (255, 150, 40), (255, 90, 30)))
        jogo.faiscas.append([x + random.uniform(-5, 5), y, random.uniform(-1.4, 1.4) * forca,
                             random.uniform(-4, -1.5) * forca, random.randint(10, 18), cor, random.randint(3, 6)])


def todo_quadro(l, jogo):
    x = l.extra
    x.setdefault("penas", 1.0)
    if x["penas"] < 1:
        x["penas"] = min(1.0, x["penas"] + 1 / PENAS_VOLTAM)
    x["fuma"] = x.get("fuma", 0) + 1
    if x["fuma"] % 150 == 0 and l.f.get("estilo") != "blue":  # de vez em quando sai fumaça das costas
        fumaca(jogo, l.x - l.dir * 10 * l.s, l.y - 64 * l.s, 4, (110, 110, 116), 1.5, -1.4)


# =====================================================================
# E: OS ESPINHOS DA NUCA (6 tiros de 2, prendem meio segundo)
# =====================================================================
E_PEGA, E_ATIRA, E_TIROS, E_INTERVALO = 8, 12, 6, 3


def espinhos(l, outro, jogo):
    t = l.t
    l.vx = 0
    l.fisica(jogo)
    if t == E_PEGA:
        som.tocar("vento", 0.4)
    k = t - E_ATIRA
    if 0 <= k < E_TIROS * E_INTERVALO and k % E_INTERVALO == 0:
        tiro = Projetil(l, l.x + 40 * l.s * l.dir, l.y - (82 + (k // E_INTERVALO % 3 - 1) * 8) * l.s, l.dir,
                        GOLPES["magnus_espinho"])
        jogo.projeteis.append(tiro)
        som.tocar("shuriken", 0.4)
        l.extra["penas"] = max(0.0, 1 - (k // E_INTERVALO + 1) / E_TIROS)  # as penas vão saindo do pescoço
    if t >= E_ATIRA + E_TIROS * E_INTERVALO + 10:
        return "fim"


def desenha_espinho(p, tela):
    s = p.dono.s
    d = 1 if p.vx > 0 else -1
    ponta = (p.x + d * 10 * s, p.y)
    base = (p.x - d * 8 * s, p.y)
    pygame.draw.line(tela, BORDA, base, ponta, max(3, int(4 * s)))
    pygame.draw.line(tela, BRASA, base, ponta, max(2, int(2.4 * s)))
    pygame.draw.circle(tela, BRASA_CLARA, (int(ponta[0]), int(ponta[1])), max(1, int(1.6 * s)))


# =====================================================================
# Q: DUAS RABADAS (uma rasteira, uma pro alto)
# =====================================================================
Q_1, Q_2 = 10, 24


def rabadas(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t < Q_2 - 4:  # a primeira: rasteira (baixa, não derruba)
        m["g_hit"] = GOLPES["magnus_rasteira"]
        m["caixa"] = (0, 0, 96, 34)
        m["rabo"] = (suave(min(1, max(0, (t - 4) / 8))) * (1 - suave(max(0, (t - Q_1 - 6) / 6))), False)
    else:  # a segunda: pro alto (derruba)
        m["g_hit"] = GOLPES["magnus_rabada_alta"]
        m["caixa"] = (0, 50, 96, 150)
        m["rabo"] = (suave(min(1, max(0, (t - Q_2 + 6) / 6))) * (1 - suave(max(0, (t - Q_2 - 8) / 8))), True)
    if t in (Q_1 - 2, Q_2 - 2):
        som.tocar("vento", 0.6)
    if t >= Q_2 + 22:
        m["rabo"] = (0, False)
        return "fim"


# =====================================================================
# R: O BOTE (pula, prende no chão e dá 10 garradas)
# =====================================================================
R_PULA, R_GARRADAS, R_INTERVALO = 8, 9, 5  # (o bote já é a 1ª garrada: 10 hits de 2)
R_SOLTA = 8 + R_GARRADAS * R_INTERVALO


def bote(l, outro, jogo):
    t = l.t
    m = l.memo
    if "pegou" in m:
        u = t - m["pegou"]
        l.sobrepor = dict(POSES_MAGNUS["x_garra_a" if (u // 3) % 2 else "x_garra_b"])
        for k in range(R_GARRADAS):
            if u == 8 + k * R_INTERVALO:
                ultima = k == R_GARRADAS - 1
                outro.levar(2, l, GOLPES["magnus_bote"])
                if not ultima:
                    outro.vida = max(1, outro.vida)
                outro.tremor_hit = 5
                jogo.faisca(outro.x + random.uniform(-14, 14), outro.y - 10 * outro.s, False, ultima)
                som.tocar("soco", 0.5)
        if u == R_SOLTA:  # solta (fica caído) e pula pra trás
            outro.sobrepor = {}
            outro.mudar("caido")
            l.sobrepor = {}
            l.inv = 0
            l.vx, l.vy = -6 * l.dir, -7
        if u > R_SOLTA:
            l.fisica(jogo)
            if l.no_chao() and u > R_SOLTA + 8:
                l.vx = 0
                if u > R_SOLTA + 18:
                    return "fim"
        return
    if l.acertou and "parou" not in m:
        if outro.estado == "golpeado":  # PEGOU: prende no chão
            m["pegou"] = t
            l.inv = 999
            outro.mudar("agarrado")
            outro.golpe = None
            outro.sobrepor = dict(outro.poses["caido"])
            outro.y, outro.vx, outro.vy = CHAO, 0, 0
            l.x = outro.x - 20 * l.s * l.dir
            l.y, l.vx, l.vy = CHAO, 0, 0
            som.tocar("queda")
            jogo.tremer(8)
            return
        m["parou"] = t  # defendeu: errou
    if t < R_PULA:
        l.vx = 0
        l.fisica(jogo)
        return
    if t == R_PULA:
        dist = max(60, min(320, (outro.x - l.x) * l.dir))
        l.vy = -11
        l.vx = dist / 24 * l.dir
        som.tocar("vento")
    m["caixa"] = (0, 10, 74, 110) if "parou" not in m and not l.no_chao() else None
    l.fisica(jogo)
    if t > R_PULA + 3 and l.no_chao():
        m.setdefault("pousou", t)
        l.vx = 0
        if t - m["pousou"] > 22:
            return "fim"


def bote_efeito(l, tela):
    m = l.memo
    if "pegou" not in m:
        return
    u = l.t - m["pegou"]
    if 8 <= u < R_SOLTA and (u - 8) % R_INTERVALO < 2:  # os riscos das garras
        x = l.x + l.dir * 40 * l.s
        for k in range(3):
            pygame.draw.line(tela, (255, 240, 220), (x - 10 * l.s + k * 6 * l.s, CHAO - 34 * l.s),
                             (x + k * 6 * l.s, CHAO - 10 * l.s), 2)


# =====================================================================
# SHIFT: CORRIDA AGACHADO + RABADA DE FOGO (paralisa 1 s)
# =====================================================================
S_SAI, S_CORRE, S_VEL, S_FOGO = 6, 30, 11, 8


def corrida(l, outro, jogo):
    t = l.t
    m = l.memo
    if l.acertou and "bateu" not in m:
        m["bateu"] = t
        m["caixa"] = None
    if "bateu" in m:
        l.vx = 0
        u = t - m["bateu"]
        m["rabo"] = (suave(min(1, u / 6)) * (1 - suave(max(0, (u - 14) / 8))), True)
        m["rabo_fogo"] = u < 24
        if u < 20 and u % 2 == 0:
            chama(jogo, l.x - l.dir * 30 * l.s, l.y - 30 * l.s, 2)
        if u == S_FOGO:  # A RABADA DE FOGO
            som.tocar("explosao", 0.6)
            res = outro.receber(GOLPES["magnus_rabada_fogo"], l.dir, l, l.f["forca"])
            if res == "hit":
                outro.mudar("tonto")  # paralisado 1 segundo
                outro.tonto_tempo = 60
                outro.vx = 0
                jogo.faisca(outro.x, outro.y - 50 * outro.s, False, True)
                jogo.tremer(8)
        l.fisica(jogo)
        if u >= S_FOGO + 26:
            m["rabo"] = (0, False)
            return "fim"
        return
    if S_SAI <= t < S_SAI + S_CORRE:
        l.vx = S_VEL * l.dir
        m["caixa"] = (0, 0, 70, 64)
        if t % 3 == 0:
            fumaca(jogo, l.x - l.dir * 24 * l.s, CHAO - 4, 1, (170, 160, 140), 1, -0.3)
    else:
        l.vx *= 0.6
        m["caixa"] = None
    l.fisica(jogo)
    if t >= S_SAI + S_CORRE + 14:
        return "fim"


# =====================================================================
# Z: ULTIMATE — 3 BOLAS DE FOGO + (se acertar) FUMACEIRA E RABADA DE FOGO
# =====================================================================
U_BOLAS = (12, 28, 44)
U_ESPERA = 60  # depois da última bola, se nada acertou, acaba


def bola_acertou(dono, alvo, jogo, res):
    m = dono.memo
    if res == "hit" and dono.estado == "ataque" and dono.nome_golpe == "magnus_ultimate" and "pegou" not in m:
        m["pegou"] = dono.t
        m["alvo"] = alvo
        alvo.mudar("agarrado")
        alvo.golpe = None
        alvo.sobrepor = dict(alvo.poses["golpeado"])
        alvo.vx = alvo.vy = 0
        alvo.y = CHAO


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    if "pegou" not in m:
        if t in U_BOLAS:  # FOGO!
            jogo.projeteis.append(Projetil(l, l.x + 50 * l.s * l.dir, l.y - 90 * l.s, l.dir, GOLPES["magnus_bola"]))
            som.tocar("explosao", 0.5)
            chama(jogo, l.x + 50 * l.s * l.dir, l.y - 90 * l.s, 6)
        l.fisica(jogo)
        if t >= U_BOLAS[-1] + U_ESPERA:
            return "fim"
        return
    u = t - m["pegou"]
    if u == 4:  # a FUMACEIRA
        fumaca(jogo, outro.x, outro.y - 40 * outro.s, 24, (90, 90, 96), 5, -0.6)
        som.tocar("puf")
    if u == 10:  # aparece do lado dele no meio da fumaça
        l.x = max(PAREDE_E, min(PAREDE_D, outro.x - l.dir * 60 * l.s))
        l.inv = 999
    m["rabo"] = (suave(min(1, max(0, (u - 12) / 6))) * (1 - suave(max(0, (u - 26) / 8))), True)
    m["rabo_fogo"] = 10 <= u < 34
    if 12 <= u < 30 and u % 2 == 0:
        chama(jogo, l.x - l.dir * 30 * l.s, l.y - 30 * l.s, 2)
    if u == 18:  # A RABADA DE FOGO
        outro.levar(20, l, GOLPES["magnus_ultimate"])
        outro.sobrepor = {}
        outro.mudar("voando")
        outro.vx, outro.vy = 8 * l.dir, -9
        jogo.faisca(outro.x, outro.y - 50 * outro.s, False, True)
        jogo.tremer(14)
        som.tocar("ko", 0.6)
    l.fisica(jogo)
    if u >= 44:
        l.inv = 0
        m["rabo"] = (0, False)
        return "fim"


def desenha_bola(p, tela):
    t = p.t
    for i in range(6, 0, -1):
        x = p.x - p.vx * i * 1.2
        r = int(p.raio * (1 - i / 8))
        pygame.draw.circle(tela, (255, int(80 + 20 * (6 - i)), 30), (int(x), int(p.y + math.sin(t * 0.7 + i) * 3)),
                           max(2, r))
    brilho(tela, (int(p.x), int(p.y)), int(p.raio * 2.2), (255, 140, 40), 100)
    pygame.draw.circle(tela, (255, 220, 120), (int(p.x), int(p.y)), int(p.raio + math.sin(t * 0.9) * 2))


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


_registra("magnus_espinho", ini=0, ativo=1, rec=0, proj=True, varios=True, raio=7, vel=13, dano=2, hit=30, defe=8,
          emp=1, nivel="medio", desenho_proj=desenha_espinho)
_registra("magnus_espinhos", ini=E_ATIRA, ativo=E_TIROS * E_INTERVALO, rec=10, dano=0, hit=0, defe=0, emp=0,
          nivel="medio", logica=espinhos, ia="longe",
          quadros=[(0, "parado"), (4, "m_espinhos"), (E_ATIRA, "m_espinhos"), (E_ATIRA + 3, "m_atira"),
                   (E_ATIRA + E_TIROS * E_INTERVALO, "m_atira"), (E_ATIRA + E_TIROS * E_INTERVALO + 10, "parado")])
GOLPES["magnus_rasteira"] = dict(dano=5, hit=18, defe=8, emp=3, nivel="baixo",
                                 especial=True, derruba=False)
GOLPES["magnus_rabada_alta"] = dict(dano=5, hit=24, defe=10, emp=2, nivel="medio", especial=True,
                                    lanca=16)  # joga pra CIMA (dá pra pular atrás: combo aéreo)
_registra("magnus_rabadas", ini=Q_1, ativo=Q_2 + 5 - Q_1, rec=16, janelas=((Q_1, Q_1 + 5), (Q_2, Q_2 + 5)),
          caixa=(0, 0, 96, 34), dano=5, hit=18, defe=8, emp=2, nivel="medio", logica=rabadas, ia="perto",
          lanca_depois=True,
          quadros=[(0, "parado"), (4, "x_rabada"), (Q_2 + 14, "x_rabada"), (Q_2 + 22, "parado")])
_registra("magnus_bote", ini=R_PULA, ativo=30, rec=0, janelas=((R_PULA, R_PULA + 30),), dano=2, hit=40, defe=12,
          emp=0, nivel="medio", logica=bote, efeito=bote_efeito, ia="medio",
          quadros=[(0, "parado"), (R_PULA - 2, "x_rasteja"), (R_PULA + 2, "x_salto"), (R_PULA + 30, "x_salto")])
GOLPES["magnus_bote"]["total"] = 9999
GOLPES["magnus_rabada_fogo"] = dict(dano=10, hit=30, defe=12, emp=2, nivel="medio", especial=True)
_registra("magnus_corrida", base="agachado", ini=S_SAI, ativo=S_CORRE, rec=14, janelas=((S_SAI, S_SAI + S_CORRE),),
          caixa=(0, 0, 70, 64), dano=5, hit=24, defe=10, emp=0, nivel="medio", logica=corrida, ia="medio",
          quadros=[(0, "parado"), (S_SAI - 2, "x_rasteja"), (S_SAI + S_CORRE, "x_rasteja"),
                   (S_SAI + S_CORRE + 14, "parado")])
GOLPES["magnus_corrida"]["total"] = 9999
_registra("magnus_bola", ini=0, ativo=1, rec=0, proj=True, raio=14, vel=10, dano=15, hit=30, defe=14, emp=3,
          nivel="medio", ultimate=True, ao_acertar=bola_acertou, desenho_proj=desenha_bola)
_registra("magnus_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=ultimate, ia="ultimate",
          quadros=[(0, "parado"), (6, "m_ruge"), (U_BOLAS[0], "m_atira"), (U_BOLAS[-1] + 6, "m_atira"),
                   (U_BOLAS[-1] + 20, "parado")])
GOLPES["magnus_ultimate"]["total"] = 9999

GOLPES_MAGNUS = {"E": "magnus_espinhos", "Q": "magnus_rabadas", "R": "magnus_bote", "SHIFT": "magnus_corrida",
                 "Z": "magnus_ultimate"}


# =====================================================================
# Desenho: um RAPTOR-robô de fogo (raptor do Jurassic Park 3 + os dinos X do ARK), desenhado por código
# =====================================================================
def pontos_cauda(l, p, base):
    """A cauda de raptor: dura, reta pra trás e um pouco levantada (balança só na pontinha)."""
    qx, qy = base
    t = l.t
    pts = []
    for i in range(13):
        onda = math.sin(t * 0.1 + i * 0.5) * i * 0.25
        pts.append((qx - 6 - i * 8.4, qy + 3 + i * 1.3 + onda))
    if l.estado == "ataque" and l.nome_golpe == "magnus_corrida" and "bateu" not in l.memo:
        pts = [(qx - 6 - i * 8.6, qy + math.sin(t * 0.4 + i * 0.7) * 2) for i in range(13)]
    k, alto = l.memo.get("rabo", (0, False)) if l.estado == "ataque" else (0, False)
    if k > 0:  # a RABADA: passa por baixo e vai na frente (baixa = rasteira, alta = pro alto)
        c0, c1 = (qx - 6, qy + 2), (qx - 40, -6)
        c2, c3 = ((qx + 56, -16), (qx + 96, 112)) if alto else ((qx + 40, -4), (qx + 104, 10))
        balanco = []
        for i in range(13):
            u = i / 12
            b0, b1, b2, b3 = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
            balanco.append((b0 * c0[0] + b1 * c1[0] + b2 * c2[0] + b3 * c3[0],
                            b0 * c0[1] + b1 * c1[1] + b2 * c2[1] + b3 * c3[1]))
        pts = [(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k) for a, b in zip(pts, balanco)]
    return pts


def _cor(letra, padrao):
    import pecas
    return (pecas.TROCA or {}).get(letra, padrao)


def _ang(v):
    return math.atan2(v[1], v[0])


def esqueleto(l, p):
    """Transforma QUALQUER pose (até as de gente, tipo soco/caído) num corpo de RAPTOR:
    o tronco deitado (horizontal), o pescoço em S subindo do peito e a cabeça comprida apontando pra frente."""
    qd, pc, cb = p["qd"], p["pc"], p["cb"]
    a = _ang((pc[0] - qd[0], pc[1] - qd[1]))
    if 0.35 < a < 2.8:  # tronco de pé (de gente) -> deitado (de raptor); caído continua caído
        a = 0.12 + (a - 1.2) * 0.45
    peito = (qd[0] + math.cos(a) * 36, qd[1] + math.sin(a) * 36)
    b = _ang((cb[0] - pc[0], cb[1] - pc[1])) + 0.6
    alcance = p["mf"][0] - pc[0]
    if alcance > 30:  # SOCO de raptor = MORDIDA: o pescoço vai pra frente
        b -= min(0.8, (alcance - 30) * 0.03)
    b = max(a - 0.5, min(a + 1.9, b))
    meio = (peito[0] + math.cos(b) * 14 + 3, peito[1] + math.sin(b) * 14)
    nuca = (meio[0] + math.cos(b + 0.25) * 15, meio[1] + math.sin(b + 0.25) * 15)
    cabeca = b - 1.15 if b > a else a  # a cabeça fica quase deitada (olhando pra frente)
    return dict(quadril=qd, peito=peito, meio=meio, nuca=nuca, a=a, cabeca=cabeca)


def desenhar_magnus(l, tela, p, branco):
    s = l.s
    pele, pele_esc, metal = _cor("m", METAL), _cor("M", METAL_ESC), _cor("c", METAL_CLARO)
    brasa, brasa_clara = _cor("b", BRASA), _cor("B", BRASA_CLARA)
    if branco:
        pele = pele_esc = metal = brasa = brasa_clara = (245, 245, 250)
    e = esqueleto(l, p)
    H, C, N = e["quadril"], e["peito"], e["nuca"]
    blue = l.f.get("estilo") == "blue" and not branco  # BLUE (Jurassic World): raptor de verdade, sem robô e sem fogo

    def Q(pt):
        return xeno.Pt(l, pt[0], pt[1])

    def poly(pts, cor, contorno=True):
        tp = [Q(q) for q in pts]
        if contorno:
            pygame.draw.polygon(tela, BORDA, tp)
            pygame.draw.polygon(tela, BORDA, tp, max(2, int(1.6 * s)))
            meio = (sum(x for x, _ in tp) / len(tp), sum(y for _, y in tp) / len(tp))
            k = max(0.0, 1 - 1.6 * s / max(8.0, max(abs(x - meio[0]) + abs(y - meio[1]) for x, y in tp)))
            pygame.draw.polygon(tela, cor, [(meio[0] + (x - meio[0]) * k, meio[1] + (y - meio[1]) * k) for x, y in tp])
        else:
            pygame.draw.polygon(tela, cor, tp)

    def lados(pts, larg):
        esq, dir_ = [], []
        for i, (x, y) in enumerate(pts):
            a = pts[max(0, i - 1)]
            b = pts[min(len(pts) - 1, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            n = math.hypot(dx, dy) or 1
            nx, ny = -dy / n, dx / n
            esq.append((x + nx * larg[i][0], y + ny * larg[i][0]))
            dir_.append((x - nx * larg[i][1], y - ny * larg[i][1]))
        return esq, dir_

    def tubo(pts, larg, cor, borda=True):
        """Um 'tubo' arredondado seguindo os pontos (larg = (em cima, embaixo) em cada ponto)."""
        if borda:
            e1, d1 = lados(pts, [(a + 1.8, b + 1.8) for a, b in larg])
            pygame.draw.polygon(tela, BORDA, [Q(q) for q in e1 + d1[::-1]])
            for q, (a, b) in ((pts[0], larg[0]), (pts[-1], larg[-1])):
                pygame.draw.circle(tela, BORDA, Q(q), max(2, int((max(a, b) + 1.8) * s)))
        e1, d1 = lados(pts, larg)
        pygame.draw.polygon(tela, cor, [Q(q) for q in e1 + d1[::-1]])
        for q, (a, b) in ((pts[0], larg[0]), (pts[-1], larg[-1])):
            pygame.draw.circle(tela, cor, Q(q), max(1, int(max(a, b) * s)))
        return e1, d1

    def osso(a, b, w1, w2, cor):
        tubo([a, b], [(w1, w1), (w2, w2)], cor)

    def entre(a, b, k):
        return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)

    def perna(pe, joelho, cor, frente):
        """Perna de raptor: coxa grossa, canela pra trás, o 'pé comprido' e a GARRA DE FOICE."""
        P, J = p[pe], p[joelho]
        J = (J[0] + 6, J[1] + 2)
        tornozelo = (P[0] - 7, P[1] + 15)
        dedos = (P[0] + 12, P[1] + 1)
        osso(J, tornozelo, 4.2, 3.2, cor)
        osso(tornozelo, (P[0] + 1, P[1] + 3), 3.2, 2.6, cor)
        osso((P[0] + 1, P[1] + 3), dedos, 2.6, 1.4, cor)
        foice = [(P[0] + 1, P[1] + 5), (P[0] + 6, P[1] + 13), (P[0] + 9, P[1] + 8), (P[0] + 4, P[1] + 4)]
        poly(foice, (232, 228, 214) if not branco else cor)  # a garra de foice (Deinonychus)
        tubo([(H[0] - 2, H[1] + 2), entre(H, J, 0.55), J], [(11, 9), (8.5, 7), (5, 5)], cor)  # coxa
        if frente and not blue:  # o pistão robótico da coxa
            a, b = entre(H, J, 0.2), entre(H, J, 0.85)
            pygame.draw.line(tela, BORDA, Q(a), Q(b), max(3, int(3.4 * s)))
            pygame.draw.line(tela, metal, Q(a), Q(b), max(1, int(1.8 * s)))
            pygame.draw.line(tela, brasa, Q(entre(a, b, 0.4)), Q(entre(a, b, 0.6)), max(1, int(1.8 * s)))

    def braco(cot, mao, cor):
        ombro = (C[0] - 2, C[1] - 6)
        cotovelo = (ombro[0] + (p[cot][0] - p["pc"][0]) * 0.32, ombro[1] + (p[cot][1] - p["pc"][1]) * 0.32 - 2)
        punho = (cotovelo[0] + (p[mao][0] - p[cot][0]) * 0.4 + 3, cotovelo[1] + (p[mao][1] - p[cot][1]) * 0.4)
        osso(ombro, cotovelo, 3, 2.2, cor)
        osso(cotovelo, punho, 2.2, 1.5, cor)
        for k in (-1, 0, 1):  # as 3 garras da mão
            pygame.draw.line(tela, BORDA, Q(punho), Q((punho[0] + 5, punho[1] - 2 + k * 2)), max(1, int(1.4 * s)))

    fogo_rabo = l.estado == "ataque" and l.memo.get("rabo_fogo")
    perna("pt", "jt", pele_esc, False)
    braco("ct", "mt", pele_esc)
    # a CAUDA (dura, com anéis de fogo tipo as listras do raptor do JP3)
    cauda = pontos_cauda(l, p, H)
    larg = larg_cauda = [(max(1.2, 9 - i * 0.68), max(1.0, 8 - i * 0.62)) for i in range(len(cauda))]
    tubo(cauda, larg, pele)
    for i in range(2, len(cauda) - 1, 2):
        if blue:
            break
        a, b = lados([cauda[i - 1], cauda[i], cauda[i + 1]], [larg[i]] * 3)
        pygame.draw.line(tela, brasa, Q(a[1]), Q(b[1]), max(1, int(1.6 * s)))
    if not blue:
        pygame.draw.circle(tela, brasa_clara, Q(cauda[-1]), max(2, int(2.6 * s)))
    if fogo_rabo and not branco:  # a cauda pegando fogo
        for i in range(2, len(cauda), 2):
            brilho(tela, Q(cauda[i]), int((10 + i) * s), (255, 120, 30), 150)
    # o CORPO (deitado, de raptor) e o PESCOÇO em S, num tubo só
    espinha = [(H[0] - 8, H[1] + 2), H, entre(H, C, 0.5), C, e["meio"], N]
    larg = [(9, 8), (12, 12), (12.5, 14), (10, 12), (6, 6.5), (5.5, 5.5)]
    cima, baixo = tubo(espinha, larg, pele)
    barriga = [entre(q, r, 0.35) for q, r in zip(baixo, espinha)][1:4]
    pygame.draw.lines(tela, metal, False, [Q(q) for q in barriga], max(2, int(4 * s)))
    if blue:  # a LISTRA AZUL da Blue: do olho até a ponta da cauda
        faixa = [entre(cima[i], espinha[i], 0.55) for i in range(len(espinha) - 1, 0, -1)]
        faixa += [entre(q, c, 0.4) for q, c in zip(lados(cauda, larg_cauda)[0][:9], cauda[:9])]
        pygame.draw.lines(tela, brasa, False, [Q(q) for q in faixa], max(2, int(2.6 * s)))
    for i in range(1, 5):  # as LISTRAS que brilham (fogo por dentro)
        if blue:
            break
        a, b = entre(cima[i], espinha[i], 0.1), entre(cima[i], espinha[i], 0.7)
        c = (b[0] - 3, b[1] - 1)
        pygame.draw.lines(tela, brasa, False, [Q(a), Q(c), Q((c[0] + 1, c[1] - 3))], max(1, int(1.6 * s)))
    for i in range(4):  # as placas de METAL nas costas (os dinos X)
        if blue:
            break
        b = entre(cima[1], cima[3], i / 3.4)
        poly([(b[0] - 4, b[1] - 1), (b[0] - 1, b[1] + 4), (b[0] + 4, b[1] + 3), (b[0] + 3, b[1] - 1)], metal)
    # as PENAS/espinhos do pescoço e da cabeça (JP3): crescem, encolhem e SAEM quando ele atira
    penas = 0 if blue else l.extra.get("penas", 1.0) * (0.78 + 0.22 * math.sin(l.t * 0.06))
    if penas > 0.05:
        dx, dy = N[0] - C[0], N[1] - C[1]
        n = math.hypot(dx, dy) or 1
        for i in range(7):
            base = entre(C, N, 0.2 + i * 0.13)
            base = (base[0] - dy / n * 5.5, base[1] + dx / n * 5.5)  # em cima do pescoço
            tam = (11 + (i % 2) * 4 + i * 1.2) * penas
            ang = _ang((dx, dy)) + 2.35 - i * 0.04
            pt = (base[0] + math.cos(ang) * tam, base[1] + math.sin(ang) * tam)
            poly([(base[0] - 2, base[1]), pt, (base[0] + 2, base[1])], brasa if i % 2 else brasa_clara)
    # a CABEÇA de raptor (focinho comprido, crânio de metal, olho de fogo)
    ang = e["cabeca"]
    ca, sa = math.cos(ang), math.sin(ang)

    def L(f, u):
        f, u = f * 1.3, u * 1.3  # (cabeça grande, pra aparecer bem na pixel art)
        return (N[0] + f * ca - u * sa, N[1] + f * sa + u * ca)

    abre = 5 if l.estado == "ataque" and l.nome_golpe in ("magnus_ultimate", "magnus_espinhos") else 0
    if l.estado == "ataque" and p["mf"][0] - p["pc"][0] > 30:
        abre = 6  # mordida
    poly([L(-3, -2), L(25, -2 - abre * 0.5), L(23, -5 - abre), L(8, -7 - abre * 0.6), L(-3, -5)], pele_esc)
    for i in range(5):  # dentes de baixo
        x = 7 + i * 3.6
        pygame.draw.polygon(tela, (250, 248, 236), [Q(L(x, -2 - abre * 0.4)), Q(L(x + 1.6, -2 - abre * 0.4)),
                                                    Q(L(x + 0.8, 0.2 - abre * 0.4))])
    cranio = [L(-6, 2), L(-4, 7), L(4, 9), L(12, 8.5), L(20, 5.5), L(27, 3), L(30, 0.8), L(29, -1.2), L(4, -1.4),
              L(-6, -2)]
    poly(cranio, pele)
    for i in range(6):  # dentes de cima
        x = 6 + i * 3.8
        pygame.draw.polygon(tela, (250, 248, 236), [Q(L(x, -1)), Q(L(x + 1.8, -1)), Q(L(x + 0.9, -3.6))])
    if blue:  # a listra azul começa no olho e desce pelo pescoço
        pygame.draw.lines(tela, brasa, False, [Q(L(24, 2.6)), Q(L(10, 3.6)), Q(L(-4, 2))], max(2, int(2.4 * s)))
    else:
        poly([L(-4, 6), L(4, 9), L(13, 8.5), L(14, 5.6), L(2, 5)], metal)  # a placa de metal do crânio
        pygame.draw.line(tela, brasa, Q(L(14, 5.6)), Q(L(26, 2.6)), max(1, int(1.4 * s)))  # emenda do focinho
    olho = Q(L(10, 5))
    pygame.draw.circle(tela, BORDA, olho, max(2, int(2.6 * s)))
    pygame.draw.circle(tela, brasa_clara if not branco else (240, 240, 240), olho, max(1, int(1.7 * s)))
    pygame.draw.line(tela, BORDA, Q(L(6, 7.4)), Q(L(14, 7)), max(2, int(1.8 * s)))  # a sobrancelha brava
    pygame.draw.circle(tela, BORDA, Q(L(27, 1.6)), max(1, int(0.9 * s)))  # narina
    if penas > 0.05:  # a CRISTA de espinhos atrás da cabeça (igual o raptor macho do JP3)
        for i, (f, u, tam) in enumerate(((2, 8.6, 9), (-1, 7.6, 11), (-4, 5.6, 12))):
            b = L(f, u)
            ponta = (b[0] - ca * tam * penas + (-sa) * tam * 0.45 * penas,
                     b[1] - sa * tam * penas + ca * tam * 0.45 * penas)
            poly([L(f - 1.5, u), ponta, L(f + 1.5, u - 0.6)], brasa_clara if i % 2 else brasa)
    perna("pf", "jf", pele, True)
    braco("cf", "mf", pele)


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Magnus grande: o olho de fogo."""
    cb = P("cb")
    pygame.draw.circle(q, BRASA_CLARA, (int(cb[0] + 6 * s * d), int(cb[1] - 2 * s)), max(2, int(2 * s)))


# =====================================================================
# ENTRADA: um fogo no canto da tela e ele entra farejando, devagarzinho
# =====================================================================
E_ANDA = 96


def entrada(l, t, jogo):
    xf = l.extra["entrada_x"]
    de = (PAREDE_E - 60) if l.dir > 0 else (PAREDE_D + 60)
    if t < 6:  # o fogo no canto
        for _ in range(3):
            chama(jogo, de + l.dir * 30, CHAO - 20, 3, 1.4)
    if t < E_ANDA:
        k = t / E_ANDA
        l.x = de + (xf - de) * k
        quadro = ("andar1", "andar2", "andar3", "andar4")[(t // 10) % 4]
        cheira = (t // 24) % 2
        l.sobrepor = dict(POSES_MAGNUS["m_fareja"] if cheira else POSES_MAGNUS[quadro])
        if t % 24 == 12:
            som.tocar("vento", 0.2)
    else:
        l.x = xf
        l.sobrepor = {}
    l.t += 1


def entrada_efeito(l, tela, t):
    if t < 60:  # o fogo queimando no canto da tela
        de = (PAREDE_E - 30) if l.dir > 0 else (PAREDE_D + 30)
        for i in range(6):
            h = (40 + 30 * math.sin(t * 0.4 + i)) * l.s * max(0, 1 - t / 60)
            pygame.draw.polygon(tela, (255, 140, 40), [(de - 20 + i * 8, CHAO), (de - 16 + i * 8, CHAO - h),
                                                       (de - 12 + i * 8, CHAO)])


# =====================================================================
# VITÓRIA: ruge soltando fogo pro alto
# =====================================================================
def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES_MAGNUS["m_ruge"] if t > 6 else POSES_MAGNUS["parado"])
    if t == 10:
        som.tocar("ultimate", 0.5)
    if 10 <= t < 50 and t % 2 == 0:
        p = l.pose_vista or l.pose_atual()
        c = xeno.Pt(l, p["cb"][0] + 22, p["cb"][1] + 2)
        chama(jogo, c[0], c[1], 2, 1.4)


def vitoria_efeito(l, tela, t):
    if 10 <= t < 60 and (t // 8) % 2:
        from efeitos import texto_grande
        texto_grande(tela, "RRRAAAWR!", 22, (255, 170, 80), (int(l.x), int(l.y - 150 * l.s)), contorno=(40, 10, 0))
