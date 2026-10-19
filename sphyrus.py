"""SPHYRUS: o tubarão-martelo + mosassauro de pé (criado pelo Gomes). O DPS do jogo: vidro que bate forte (80 de vida).

Aparência: tubarão-martelo esticado de pé, com mandíbula de mosassauro (abre ENORME, duas fileiras de dentes), olhos
amarelos nas pontas do martelo, guelras que abrem e fecham, barbatana dorsal rasgada com CÓDIGO DE BARRAS, linha
bioluminescente nos lados (azul; acende nos especiais; VERMELHA na Frenesi), braços com "asinha espinhosa" (tipo
peixe-leão), pernas de raptor, cauda em V, coleira de metal quebrada e cicatriz de pontos (experimento que fugiu).
  E      gira a cauda e solta uma ONDA DE AR (14)
  Q      MARTELADA pra cima (15) — joga pra cima
  R      CORTE DE BARBATANA em X com os braços (2 hits de 12)
  SHIFT  MERGULHO: afunda no chão e sai embaixo do adversário mordendo pra cima (10)
  Z      ULTIMATE: o chão vira MAR, ele nada em volta só com a barbatana e salta GIGANTE abocanhando (45)
  Passiva (escolhe na seleção com H): ELETRORRECEPÇÃO / NATAÇÃO (tecla X) / FRENESI.
  Bônus na água: no PÂNTANO, NAVIO FANTASMA e PRAIA DA ILHA anda um pouco mais rápido.
  Entrada: chega pelo chão só com a barbatana cortando e pula dando um RUGIDÃO.
"""
import math
import random

import pygame

import habilidades as hab
import som
from config import *  # noqa: F401,F403
from golpes import GOLPES, proporcionar, suave
from lutador import Projetil
from max10 import brilho, fumaca

PELE, PELE_ESC, BARRIGA = (124, 136, 156), (88, 98, 118), (214, 214, 132)  # (cinza-chumbo azulado mais claro)
LINHA, OLHO, BORDA = (80, 200, 255), (255, 214, 40), (10, 10, 16)
PALETA = {"m": PELE, "M": PELE_ESC, "a": BARRIGA, "l": LINHA, "o": OLHO}  # (letras das roupas)
VERMELHO = (255, 50, 50)
AGUA = ("PÂNTANO", "NAVIO FANTASMA", "PRAIA DA ILHA")  # BÔNUS NA ÁGUA

POSES_SPHYRUS = {
    "parado": dict(pt=(-22, 0), jt=(-10, 28), pf=(20, 0), jf=(30, 28), qd=(0, 52), pc=(10, 86), cb=(18, 104),
                   ct=(4, 68), mt=(22, 62), cf=(24, 70), mf=(40, 66)),
    "s_gira": dict(pt=(-24, 0), jt=(-10, 22), pf=(22, 0), jf=(32, 24), qd=(0, 34), pc=(14, 64), cb=(26, 80),
                   ct=(4, 50), mt=(20, 40), cf=(26, 52), mf=(40, 44)),
    "s_martelo": dict(pt=(-14, 4), jt=(-8, 30), pf=(12, 0), jf=(14, 28), qd=(0, 56), pc=(12, 92), cb=(26, 110),
                      ct=(-6, 80), mt=(-14, 66), cf=(24, 80), mf=(40, 70)),
    "s_corte_a": dict(pt=(-22, 0), jt=(-12, 28), pf=(20, 0), jf=(26, 28), qd=(0, 54), pc=(6, 90), cb=(12, 108),
                      ct=(14, 108), mt=(36, 124), cf=(22, 104), mf=(44, 118)),
    "s_corte_b": dict(pt=(-24, 0), jt=(-14, 26), pf=(24, 0), jf=(32, 26), qd=(0, 48), pc=(14, 82), cb=(24, 98),
                      ct=(30, 70), mt=(54, 46), cf=(28, 66), mf=(50, 40)),
    "s_ruge": dict(pt=(-22, 0), jt=(-10, 30), pf=(20, 0), jf=(28, 30), qd=(0, 56), pc=(-2, 92), cb=(-2, 112),
                   ct=(-20, 90), mt=(-34, 104), cf=(16, 90), mf=(34, 104)),
    "s_mergulho": dict(pt=(-30, 4), jt=(-16, 18), pf=(26, 0), jf=(20, 18), qd=(0, 26), pc=(28, 40), cb=(46, 44),
                       ct=(30, 24), mt=(48, 10), cf=(38, 26), mf=(58, 12)),
    "s_salto": dict(pt=(-34, 10), jt=(-16, 30), pf=(-6, 6), jf=(10, 28), qd=(0, 50), pc=(26, 70), cb=(46, 78),
                    ct=(36, 74), mt=(60, 82), cf=(38, 66), mf=(62, 66)),
}
proporcionar(POSES_SPHYRUS)


def Pt(l, x, y):
    return l.ponto({"o": (x, y)}, "o")


def outro_de(l, jogo):
    return jogo.L[1] if jogo.L[0] is l else jogo.L[0]


def dente_cai(l, jogo, x, y):
    """Às vezes cai um dentinho quando ele morde (e nasce outro depois)."""
    if random.random() < 0.5:
        jogo.faiscas.append([x, y, random.uniform(-1.5, 1.5), random.uniform(-3, -1), 40, (250, 250, 236), 3])
        l.extra["dente_falta"] = 120


# =====================================================================
# Todo quadro: guelras, ELETRORRECEPÇÃO, NATAÇÃO, FRENESI e o bônus na água
# =====================================================================
NADA_MAX, NADA_RECARGA = 8 * FPS, 6 * FPS
FRENESI_VIDA = 0.35
SENTE_TEMPO = 30


def todo_quadro(l, jogo):
    x = l.extra
    x.setdefault("s_base", l.s)
    outro = outro_de(l, jogo)
    cena = getattr(jogo, "cena", None)
    x["agua"] = bool(cena) and cena.nome in AGUA
    for k in ("sente", "ruge", "dente_falta", "nada_recarga", "passou"):
        if x.get(k, 0) > 0:
            x[k] -= 1
    hs = hab.ativas(l)
    # ELETRORRECEPÇÃO: sente o adversário começando um especial
    if "eletro" in hs and outro.estado == "ataque" and outro.golpe and outro.golpe.get("especial") and outro.t <= 1:
        x["sente"] = SENTE_TEMPO
        som.tocar("blip", 0.5)
    # FRENESI: o adversário sangrando (35% ou menos) = dano x2 e +30% de velocidade até o fim do round
    if "frenesi" in hs and not x.get("frenesi") and 0 < outro.vida <= outro.vida_max * FRENESI_VIDA:
        x["frenesi"] = True
        x["ruge"] = 50
        som.tocar("terra", 0.7)
        jogo.tremer(10)
    # NATAÇÃO: intangível, só a barbatana, passar por baixo derruba
    if x.get("nadando"):
        x["nada_t"] = x.get("nada_t", 0) + 1
        if x["nada_t"] >= NADA_MAX or l.estado not in ("parado", "andando", "agachado") or not l.no_chao():
            sair_da_agua(l)
        else:
            l.inv = max(l.inv, 2)
            lado = 1 if outro.x > l.x else -1
            if x.get("lado") and lado != x["lado"] and not x.get("passou") and outro.no_chao() \
                    and outro.estado not in ("caido", "voando", "agarrado") and abs(outro.x - l.x) < 50:
                res = outro.receber(GOLPES["sphyrus_passa"], -lado, l, l.f["forca"])
                if res == "hit":
                    jogo.faisca(outro.x, CHAO - 20, False, True)
                    som.tocar("explosao", 0.5)
                x["passou"] = 40
            x["lado"] = lado
            if l.t % 6 == 0:
                fumaca(jogo, l.x, CHAO - 2, 1, (200, 230, 255), 1.4, -0.4)


def nadando_agora(l):
    return l.extra.get("nadando") or (l.estado == "ataque" and l.memo.get("so_barbatana"))


def sair_da_agua(l):
    x = l.extra
    x["nadando"] = False
    x["nada_t"] = 0
    x["nada_recarga"] = NADA_RECARGA
    x["lado"] = 0
    l.inv = 0
    som.tocar("puf", 0.5)


def tecla_x(l):
    """NATAÇÃO (tecla X / L3): afunda e nada só com a barbatana (até 8 s). X de novo sai."""
    if "natacao" not in hab.ativas(l):
        return
    x = l.extra
    if x.get("nadando"):
        sair_da_agua(l)
    elif not x.get("nada_recarga") and l.estado in ("parado", "andando", "agachado") and l.no_chao():
        x["nadando"] = True
        x["nada_t"] = 0
        x["lado"] = 0
        som.tocar("puf", 0.6)


def pode_atacar(l):
    """Nadando ele NÃO ataca."""
    return not l.extra.get("nadando")


# =====================================================================
# E: ONDA DE AR (gira a cauda e solta)
# =====================================================================
E_SOLTA = 9


def onda(l, outro, jogo):
    t = l.t
    l.vx = 0
    l.memo["volta"] = suave(min(1, t / E_SOLTA))  # uma volta inteira, rápida como um pião (só desenho)
    if t == E_SOLTA:
        jogo.projeteis.append(Projetil(l, l.x + 40 * l.s * l.dir, l.y - 50 * l.s, l.dir, GOLPES["sphyrus_onda_ar"]))
        som.tocar("vento")
    l.fisica(jogo)
    if t >= E_SOLTA + 18:
        return "fim"


def desenha_onda(p, tela):
    s = p.dono.s
    d = 1 if p.vx > 0 else -1
    for i in range(3):
        r = (18 + i * 7) * s * 0.7
        rect = pygame.Rect(0, 0, r * 1.2, r * 2.4)
        rect.center = (int(p.x - d * i * 10), int(p.y))
        ini = -1.2 if d > 0 else math.pi - 1.2
        cor = (230, 250, 255) if i == 0 else (140, 210, 255)
        pygame.draw.arc(tela, cor, rect, ini, ini + 2.4, max(2, int((4 - i) * s * 0.8)))
    for k in range(3):  # os risquinhos de vento
        y = p.y + (k - 1) * 14 * s
        pygame.draw.line(tela, (200, 240, 255), (p.x - d * (30 + k * 6) * s, y), (p.x - d * (60 + k * 6) * s, y), 1)


# =====================================================================
# Q: MARTELADA pra cima
# =====================================================================
Q_PREP, Q_SOBE = 8, 16


def martelada(l, outro, jogo):
    t = l.t
    m = l.memo
    if t < Q_PREP:
        l.vx = 0
        l.fisica(jogo)
        return
    if t == Q_PREP:
        l.vy = -14
        l.vx = 3 * l.dir
        som.tocar("vento")
    if l.acertou and "mordeu" not in m:
        m["mordeu"] = True
        dente_cai(l, jogo, outro.x, outro.y - 80 * outro.s)
    m["caixa"] = (0, 50, 70, 176) if t < Q_PREP + Q_SOBE else None
    l.fisica(jogo)
    if t > Q_PREP + 4 and l.no_chao():
        m.setdefault("pousou", t)
        l.vx = 0
        if t - m["pousou"] > 4:
            return "fim"


# =====================================================================
# R: CORTE DE BARBATANA em X
# =====================================================================
R_1, R_2 = 12, 22


def corte_efeito(l, tela):
    for a in (R_1, R_2):
        k = l.t - a
        if 0 <= k < 7:
            cx, cy = l.x + l.dir * 56 * l.s, l.y - 80 * l.s
            r = 34 * l.s
            sinal = 1 if a == R_1 else -1
            cor = (255, 255, 255) if k < 3 else (140, 220, 255)
            pygame.draw.line(tela, cor, (cx - r * l.dir, cy - r * sinal), (cx + r * l.dir, cy + r * sinal),
                             max(2, int((5 - k * 0.6) * l.s)))


# =====================================================================
# SHIFT: MERGULHO (afunda e sai embaixo mordendo pra cima)
# =====================================================================
S_AFUNDA, S_NADA, S_VEL = 10, 46, 9


def mergulho(l, outro, jogo):
    t = l.t
    m = l.memo
    if "sobe" not in m or t - m["sobe"] < 4:
        l.inv = max(l.inv, 2)  # do 1º quadro até sair mordendo, ninguém pega ele
    if t == 6:
        fumaca(jogo, l.x, CHAO - 4, 8, (200, 230, 255), 3, -1.5)
        som.tocar("puf", 0.6)
    if t < S_AFUNDA:
        l.vx = 0
        l.fisica(jogo)
        return
    if "sobe" not in m:
        m["so_barbatana"] = True
        dx = outro.x - l.x
        l.vx = max(-S_VEL, min(S_VEL, dx * 0.3))
        if t % 4 == 0:
            fumaca(jogo, l.x, CHAO - 2, 1, (200, 230, 255), 1.2, -0.3)
        l.fisica(jogo)
        if abs(dx) < 12 or t >= S_AFUNDA + S_NADA:
            m["sobe"] = t
            l.vx = 0
        return
    u = t - m["sobe"]
    if u == 4:  # SAI DO CHÃO MORDENDO!
        m["so_barbatana"] = False
        l.inv = 0
        l.vy = -12
        fumaca(jogo, l.x, CHAO - 4, 10, (200, 230, 255), 4, -2)
        som.tocar("explosao", 0.5)
        if abs(outro.x - l.x) < 46 and outro.no_chao() and outro.inv <= 0 \
                and outro.estado not in ("caido", "voando", "agarrado"):
            res = outro.receber(GOLPES["sphyrus_mordida"], l.dir, l, l.f["forca"])
            if res == "hit":
                jogo.faisca(outro.x, outro.y - 40 * outro.s, False, True)
                dente_cai(l, jogo, outro.x, outro.y - 40 * outro.s)
                jogo.tremer(8)
    l.fisica(jogo)
    if u > 6 and l.no_chao():
        m.setdefault("pousou", t)
        if t - m["pousou"] > 14:
            return "fim"


# =====================================================================
# Z: ULTIMATE — O MAR (nada em volta e salta GIGANTE abocanhando)
# =====================================================================
U_MAR, U_NADA, U_SALTO, U_FIM = 18, 70, 24, 30
U_DANO = 45


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    m["tela_toda"] = True
    x = l.extra
    if t < U_MAR:  # RUGE e o chão vira mar
        m["mar"] = t / U_MAR
        l.vx = 0
        l.fisica(jogo)
        if t == 2:
            som.tocar("terra", 0.7)
        return
    if t == U_MAR:
        if outro.no_chao() and outro.estado not in ("caido", "voando") and outro.inv <= 0:
            m["pegou"] = t
            outro.mudar("agarrado")
            outro.golpe = None
            outro.sobrepor = dict(outro.poses["golpeado"])
            outro.vx = outro.vy = 0
            outro.y = CHAO
        fumaca(jogo, l.x, CHAO - 4, 10, (200, 230, 255), 4, -1.5)
        som.tocar("puf")
    m["mar"] = 1.0
    if "pegou" not in m:  # (pulou: escapou) o mar volta
        u = t - U_MAR
        m["mar"] = max(0.0, 1 - u / 20)
        if u >= 24:
            return "fim"
        return
    u = t - m["pegou"]
    l.inv = 999
    if u < U_NADA:  # nada em volta só com a barbatana
        m["so_barbatana"] = True
        ang = u * 0.16
        l.x = max(PAREDE_E, min(PAREDE_D, outro.x + math.sin(ang) * 150))
        l.y = CHAO
        l.vx = l.vy = 0
        if u % 3 == 0:
            fumaca(jogo, l.x, CHAO - 2, 1, (210, 236, 255), 1.4, -0.5)
        return
    k = (u - U_NADA) / U_SALTO
    if u == U_NADA:  # O SALTO GIGANTE
        m["so_barbatana"] = False
        m["de"] = outro.x - 110 * l.dir
        l.s = x["s_base"] * 1.8
        som.tocar("terra", 0.9)
        fumaca(jogo, m["de"], CHAO - 4, 16, (210, 236, 255), 6, -3)
    if u < U_NADA + U_SALTO:
        l.x = max(PAREDE_E, min(PAREDE_D, m["de"] + 200 * l.dir * k))  # (perto da parede não sai da tela)
        l.y = CHAO + 60 - math.sin(k * math.pi) * 230
        l.sobrepor = dict(POSES_SPHYRUS["s_salto"])
        if u == U_NADA + U_SALTO // 2:  # CHOMP!
            outro.levar(U_DANO, l, GOLPES["sphyrus_ultimate"])
            outro.sobrepor = {}
            outro.mudar("voando")
            outro.vx, outro.vy = 7 * l.dir, -10
            jogo.faisca(outro.x, outro.y - 60 * outro.s, False, True)
            dente_cai(l, jogo, outro.x, outro.y - 60 * outro.s)
            jogo.tremer(18)
            som.tocar("ko", 0.7)
        return
    v = u - U_NADA - U_SALTO
    if v == 0:  # caiu de volta (no tamanho normal)
        l.s = x["s_base"]
        l.sobrepor = {}
        l.x = max(PAREDE_E, min(PAREDE_D, l.x))
        l.y = CHAO
        fumaca(jogo, l.x, CHAO - 4, 12, (210, 236, 255), 5, -2)
    m["mar"] = max(0.0, 1 - v / 20)
    l.vx = 0
    l.fisica(jogo)
    if v >= U_FIM:
        l.inv = 0
        return "fim"


def mar_efeito(l, tela):
    k = l.memo.get("mar", 0)
    if k <= 0:
        return
    alto = 70 * k
    agua = pygame.Surface((LARGURA, int(alto) + 30), pygame.SRCALPHA)
    agua.fill((30, 110, 190, 150))
    for i in range(0, LARGURA, 40):  # as ondinhas
        y = 6 + math.sin(l.t * 0.2 + i * 0.05) * 4
        pygame.draw.line(agua, (210, 240, 255, 220), (i, y), (i + 24, y), 3)
    tela.blit(agua, (0, CHAO - alto + 20))


# =====================================================================
# Golpes
# =====================================================================
def _registra(nome, **g):
    g.setdefault("base", "parado")
    g.setdefault("pose", "parado")
    g.setdefault("caixa", None)
    g.setdefault("especial", True)
    g.setdefault("pode", pode_atacar)
    g["total"] = g.get("total", g["ini"] + g["ativo"] + g.get("rec", 0))
    GOLPES[nome] = g


_registra("sphyrus_onda_ar", ini=0, ativo=1, rec=0, proj=True, raio=18, vel=11, dano=14, hit=18, defe=10, emp=4,
          nivel="medio", desenho_proj=desenha_onda)
_registra("sphyrus_onda", ini=E_SOLTA, ativo=1, rec=18, dano=0, hit=0, defe=0, emp=0, nivel="medio", logica=onda,
          ia="longe", quadros=[(0, "parado"), (6, "s_gira"), (E_SOLTA + 6, "s_gira"), (E_SOLTA + 16, "parado")])
_registra("sphyrus_martelada", ini=Q_PREP, ativo=Q_SOBE, rec=30, janelas=((Q_PREP, Q_PREP + Q_SOBE),), dano=15,
          hit=24, defe=12, emp=2, nivel="medio", lanca=17, logica=martelada, ia="perto",
          quadros=[(0, "parado"), (4, "s_gira"), (Q_PREP + 1, "s_martelo"), (Q_PREP + 24, "s_martelo"),
                   (Q_PREP + 40, "parado")])
GOLPES["sphyrus_martelada"]["total"] = 9999
_registra("sphyrus_corte", ini=R_1, ativo=R_2 + 4 - R_1, rec=16, janelas=((R_1, R_1 + 4), (R_2, R_2 + 4)),
          caixa=(10, 30, 96, 130), dano=12, hit=18, defe=9, emp=2, nivel="medio", efeito=corte_efeito, ia="perto",
          som="vento",
          quadros=[(0, "parado"), (6, "s_corte_a"), (R_1, "s_corte_b"), (R_1 + 5, "s_corte_a"), (R_2, "s_corte_b"),
                   (R_2 + 10, "s_corte_b"), (R_2 + 20, "parado")])
GOLPES["sphyrus_mordida"] = dict(dano=10, hit=24, defe=10, emp=2, nivel="medio", especial=True, lanca=15,
                                 imbloqueavel=True)
_registra("sphyrus_mergulho", ini=S_AFUNDA, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", inv=3,
          logica=mergulho, ia="medio",
          quadros=[(0, "parado"), (4, "s_mergulho"), (S_AFUNDA + S_NADA + 8, "s_mergulho"),
                   (S_AFUNDA + S_NADA + 9, "s_martelo")])
GOLPES["sphyrus_mergulho"]["total"] = 9999
GOLPES["sphyrus_passa"] = dict(dano=8, hit=20, defe=0, emp=2, nivel="baixo", especial=True, derruba=True,
                               voo=(4, 8), imbloqueavel=True)
_registra("sphyrus_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=ultimate, efeito=mar_efeito, ia="ultimate",
          quadros=[(0, "parado"), (4, "s_ruge"), (U_MAR, "s_ruge"), (U_MAR + 4, "parado")])
GOLPES["sphyrus_ultimate"]["total"] = 9999

GOLPES_SPHYRUS = {"E": "sphyrus_onda", "Q": "sphyrus_martelada", "R": "sphyrus_corte", "SHIFT": "sphyrus_mergulho",
                  "Z": "sphyrus_ultimate"}


# =====================================================================
# Desenho (por código, em cima dos pontos da pose)
# =====================================================================
def _cor(letra, padrao):
    import pecas
    return (pecas.TROCA or {}).get(letra, padrao)


def _ang(v):
    return math.atan2(v[1], v[0])


def entre(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def mistura(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


def cor_linha(l):
    """A linha bioluminescente: azul; forte nos especiais; VERMELHA na Frenesi."""
    if l.extra.get("frenesi"):
        return VERMELHO, True
    g = l.golpe if l.estado == "ataque" else None
    forte = bool(g and (g.get("especial") or g.get("ultimate"))) or l.extra.get("sente", 0) > 0
    return _cor("l", LINHA), forte


def rugindo(l):
    if l.extra.get("ruge", 0) > 0 or l.estado == "vitoria":
        return True
    return bool(l.sobrepor) and l.sobrepor.get("cb") == POSES_SPHYRUS["s_ruge"]["cb"]


def desenhar_barbatana(l, tela, branco=False):
    """Só a barbatana cortando o chão (nadando / mergulho / entrada / ultimate)."""
    s, d = l.s, l.lado()
    x, y = l.x, l.y + 2 * s  # (l.x/l.y/l.s já vêm na escala da imagem: na pixel art é tudo dividido)
    t = l.t
    pele = _cor("m", PELE)
    fin = [(x - 16 * s * d, y), (x - 10 * s * d, y - 22 * s), (x - 2 * s * d, y - 36 * s), (x + 1 * s * d, y - 31 * s),
           (x + 3 * s * d, y - 30 * s), (x + 14 * s * d, y)]
    pygame.draw.polygon(tela, BORDA, fin)
    pygame.draw.polygon(tela, pele, [(px + (x - px) * 0.12, py + (y - 12 * s - py) * 0.12) for px, py in fin])
    for i in range(5):  # o código de barras
        bx = x - (10 - i * 2.4) * s * d
        pygame.draw.line(tela, BORDA, (bx, y - 4 * s), (bx, y - (12 - (i % 2) * 3) * s), max(1, int((1 + i % 2) * s * 0.6)))
    for i in range(2):  # a espuma dos lados
        k = math.sin(t * 0.4 + i * 2)
        pygame.draw.line(tela, (230, 248, 255), (x - (22 + i * 10) * s * d, y - s), (x - (32 + i * 10 + k * 4) * s * d, y - s),
                         max(1, int(1.4 * s)))
        pygame.draw.line(tela, (230, 248, 255), (x + (18 + i * 8) * s * d, y - s), (x + (24 + i * 8) * s * d, y - s),
                         max(1, int(1.4 * s)))


def desenhar_esqueleto(l, tela, p, branco):
    """SPHYRUS ESQUELETO (Halloween): SÓ OS OSSOS (dá pra ver o fundo entre eles). Coluna com vértebras,
    caixa torácica, ossos dos braços e pernas com as juntas, raios das barbatanas com farrapos de membrana
    e o CRÂNIO de perfil com a órbita vazia brilhando verde."""
    s = l.s
    osso_c = (236, 230, 210) if not branco else (250, 250, 252)
    sombra = (176, 170, 150) if not branco else (230, 230, 236)
    verde = _cor("l", LINHA) if not branco else (250, 250, 252)
    t = l.t

    volta = l.memo.get("volta", 0) if l.estado == "ataque" and l.nome_golpe == "sphyrus_onda" else 0
    K = math.cos(volta * math.tau)
    if abs(K) < 0.18:
        K = 0.18 if K >= 0 else -0.18

    def Q(q):
        return Pt(l, q[0] * K, q[1])

    def osso(a, b, w, cor=osso_c, juntas=True):
        """Um osso comprido (contorno escuro) com as 'bolinhas' das juntas nas pontas."""
        wa = max(2, int((w + 1.4) * s))
        pygame.draw.line(tela, BORDA, Q(a), Q(b), wa * 2 - 1)
        pygame.draw.line(tela, cor, Q(a), Q(b), max(1, int(w * s)) * 2 - 1)
        if juntas:
            for q in (a, b):
                pygame.draw.circle(tela, BORDA, Q(q), max(2, int((w + 2.2) * s)))
                pygame.draw.circle(tela, cor, Q(q), max(1, int((w + 1.0) * s)))

    def garras(base, direcao, comp=6):
        a0 = _ang(direcao)
        for k in (-0.5, 0, 0.5):
            g = (base[0] + math.cos(a0 + k) * comp, base[1] + math.sin(a0 + k) * comp)
            pygame.draw.line(tela, BORDA, Q(base), Q(g), max(2, int(2.2 * s)))
            pygame.draw.line(tela, osso_c, Q(base), Q(g), max(1, int(1.2 * s)))

    def membrana(pts):  # farrapo de membrana rasgada (bem transparente)
        tp = [Q(q) for q in pts]
        xs, ys = [x for x, _ in tp], [y for _, y in tp]
        r = pygame.Rect(min(xs), min(ys), max(xs) - min(xs) + 2, max(ys) - min(ys) + 2)
        if r.w < 2 or r.h < 2:
            return
        sup = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.polygon(sup, (*sombra, 70), [(x - r.x, y - r.y) for x, y in tp])
        tela.blit(sup, r.topleft)

    qd, pc, cb = p["qd"], p["pc"], p["cb"]

    def perna(pe, joelho, cor):
        P, J = p[pe], p[joelho]
        J = (J[0] + 5, J[1] + 2)
        tornozelo = (P[0] - 7, P[1] + 14)
        osso(qd, J, 2.6, cor)  # fêmur
        osso(J, tornozelo, 2.2, cor)  # canela
        osso(tornozelo, (P[0] + 1, P[1] + 3), 1.8, cor)
        garras((P[0] + 1, P[1] + 3), (1, -0.15), 9)

    def braco(cot, mao, cor):
        ombro = entre(pc, qd, 0.12)
        cot_p, mao_p = p[cot], p[mao]
        osso(ombro, cot_p, 2.0, cor)
        osso(cot_p, mao_p, 1.7, cor)
        garras(mao_p, (mao_p[0] - cot_p[0], mao_p[1] - cot_p[1]), 6)
        atras = entre(pc, qd, 0.55)  # os RAIOS da asinha (sem a membrana cheia)
        ponta = entre(cot_p, mao_p, 0.75)
        fora = []
        for k in range(5):
            r = entre(atras, ponta, k / 4)
            dx, dy = r[0] - cot_p[0], r[1] - cot_p[1]
            n = math.hypot(dx, dy) or 1
            fora.append((r[0] + dx / n * 12, r[1] + dy / n * 12))
            pygame.draw.line(tela, cor, Q(cot_p), Q(fora[-1]), max(1, int(s)))
        membrana([cot_p, fora[1], (fora[1][0] * 0.6 + fora[2][0] * 0.4, fora[1][1] * 0.6 + fora[2][1] * 0.4 - 3)])

    # --- de trás pra frente ---
    braco("ct", "mt", sombra)
    perna("pt", "jt", sombra)
    # a CAUDA: vértebras uma por uma e os raios do rabo em V
    cauda = [(qd[0] - 6 - i * 6.6, qd[1] - 4 - i * 2.6 + math.sin(t * 0.08 + i * 0.5) * i * 0.3) for i in range(9)]
    pygame.draw.lines(tela, BORDA, False, [Q(q) for q in [qd] + cauda], max(3, int(3.4 * s)))
    pygame.draw.lines(tela, osso_c, False, [Q(q) for q in [qd] + cauda], max(1, int(1.6 * s)))
    for i, q in enumerate(cauda):
        r = max(1, 3.6 - i * 0.28)
        pygame.draw.circle(tela, BORDA, Q(q), max(2, int((r + 1.2) * s)))
        pygame.draw.circle(tela, osso_c, Q(q), max(1, int(r * s)))
        if i % 2 == 0 and i < 8:  # os espinhos de cima e de baixo de cada vértebra
            for sinal in (1, -1):
                pygame.draw.line(tela, osso_c, Q(q), Q((q[0] - 2, q[1] + sinal * (5 - i * 0.3))), max(1, int(s)))
    ponta = cauda[-1]
    dirc = _ang((ponta[0] - cauda[-2][0], ponta[1] - cauda[-2][1]))
    for k, (da, comp) in enumerate(((0.9, 22), (0.6, 18), (-0.5, 12), (-0.8, 14))):  # o rabo em V (só os raios)
        fim = (ponta[0] + math.cos(dirc + da) * comp, ponta[1] + math.sin(dirc + da) * comp)
        osso(ponta, fim, 1.0, osso_c, False)
    membrana([ponta, (ponta[0] + math.cos(dirc + 0.9) * 20, ponta[1] + math.sin(dirc + 0.9) * 20),
              (ponta[0] + math.cos(dirc + 0.6) * 12, ponta[1] + math.sin(dirc + 0.6) * 12)])
    # a COLUNA do quadril até o pescoço (vértebras)
    coluna = [entre(qd, pc, k / 6) for k in range(7)] + [entre(pc, cb, k / 3) for k in (1, 2)]
    pygame.draw.lines(tela, BORDA, False, [Q(q) for q in coluna], max(3, int(3.6 * s)))
    pygame.draw.lines(tela, osso_c, False, [Q(q) for q in coluna], max(1, int(1.8 * s)))
    for q in coluna:
        pygame.draw.circle(tela, BORDA, Q(q), max(2, int(3.6 * s)))
        pygame.draw.circle(tela, osso_c, Q(q), max(1, int(2.6 * s)))
    # a BACIA
    pygame.draw.polygon(tela, BORDA, [Q((qd[0] - 6, qd[1] + 3)), Q((qd[0] + 6, qd[1] + 4)), Q((qd[0] + 4, qd[1] - 6)),
                                      Q((qd[0] - 5, qd[1] - 5))])
    pygame.draw.polygon(tela, sombra, [Q((qd[0] - 4, qd[1] + 2)), Q((qd[0] + 4, qd[1] + 3)), Q((qd[0] + 3, qd[1] - 4)),
                                       Q((qd[0] - 3, qd[1] - 3))])
    # a DORSAL: raios de osso em leque saindo da coluna, com farrapos
    dx, dy = pc[0] - qd[0], pc[1] - qd[1]
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    nx, ny = -uy, ux  # (pra trás do corpo)
    pico = (qd[0] + dx * 0.6 + nx * 44 + ux * 10, qd[1] + dy * 0.6 + ny * 44 + uy * 10)
    raios = []
    for k in range(5):
        base = entre(qd, pc, 0.3 + k * 0.13)
        fim = entre(base, pico, 0.55 + 0.45 * (1 - abs(k - 2) / 2))
        raios.append(fim)
        osso(base, fim, 0.9, osso_c, False)
    membrana([entre(qd, pc, 0.43), raios[1], raios[2], (raios[2][0] - 3, raios[2][1] - 9), entre(qd, pc, 0.56)])
    # a CAIXA TORÁCICA: costelas curvas pra baixo/frente (o vão entre elas é vazio)
    if not branco:
        brilho(tela, Q(entre(qd, pc, 0.55)), int(18 * s), verde, 70 + int(30 * math.sin(t * 0.1)))  # a luz lá dentro
    for k in range(6):
        base = entre(qd, pc, 0.28 + k * 0.12)
        comp = 15 - abs(k - 2.5) * 2
        meio = (base[0] - nx * comp * 0.6 + ux * 3, base[1] - ny * comp * 0.6 + uy * 3)
        fim = (base[0] - nx * comp + ux * 0.5, base[1] - ny * comp + uy * 0.5)
        pts = [Q(base), Q(meio), Q(fim)]
        pygame.draw.lines(tela, BORDA, False, pts, max(3, int(3.2 * s)))
        pygame.draw.lines(tela, osso_c, False, pts, max(1, int(1.6 * s)))
    pygame.draw.line(tela, BORDA, Q(entre(qd, pc, 0.25)), Q(entre(qd, pc, 0.9)), 1)
    perna("pf", "jf", osso_c)
    # o CRÂNIO de perfil (mesmo jeito da cabeça nova: lâmina comprida, um olho na ponta)
    ang = (_ang((cb[0] - pc[0], cb[1] - pc[1])) - math.pi / 2) * 0.6 + (0.55 if rugindo(l) else 0)
    hc, hs = math.cos(ang), math.sin(ang)

    def L(f, u):
        f, u = f * 1.35, u * 1.35
        return (cb[0] + 2 + f * hc - u * hs, cb[1] + f * hs + u * hc)

    abre = 0.0
    if l.estado == "ataque" and l.nome_golpe in ("sphyrus_martelada", "sphyrus_mergulho", "sphyrus_ultimate"):
        abre = 0.75
    if rugindo(l):
        abre = 0.9
    if "boca" in l.extra:
        abre = l.extra["boca"]

    def queixo(f, u):
        a = -abre
        f0, u0 = -3, -1
        df, du = f - f0, u - u0
        return L(f0 + df * math.cos(a) - du * math.sin(a), u0 + df * math.sin(a) + du * math.cos(a))

    def contornado(pts, cor):
        tp = [Q(q) for q in pts]
        pygame.draw.polygon(tela, cor, tp)
        pygame.draw.polygon(tela, BORDA, tp, 1)

    # a MANDÍBULA separada (osso fino em L) com os dentes pontudos
    contornado([queixo(-4, -1), queixo(28, -1.6), queixo(26, -3.6), queixo(6, -4.6), queixo(-3, -3.6)], sombra)
    for i in range(6):
        x = 5 + i * 3.8
        pygame.draw.polygon(tela, osso_c, [Q(queixo(x, -1.6)), Q(queixo(x + 1.8, -1.6)), Q(queixo(x + 0.9, 1.4))])
    # o crânio de cima
    cranio = [(-6, -1.2), (-7, 4), (-4, 9), (4, 11.6), (18, 9.6), (30, 7.6), (37, 5.6), (39, 3.4), (36.5, 0.8),
              (28, -1.2), (4, -1.4)]
    contornado([L(*q) for q in cranio], osso_c)
    for i in range(7):  # os dentes de cima
        x = 4 + i * 3.8
        pygame.draw.polygon(tela, osso_c, [Q(L(x, -1.2)), Q(L(x + 1.8, -1.2)), Q(L(x + 0.9, -4))])
    pygame.draw.lines(tela, sombra, False, [Q(L(*q)) for q in ((8, 6.0), (24, 4.2), (37, 2.6))], 1)
    for a, b, c in (((6, 9), (10, 6), (9, 3)), ((20, 8.6), (23, 6.2), (26, 7))):  # as RACHADURAS
        pygame.draw.lines(tela, BORDA, False, [Q(L(*a)), Q(L(*b)), Q(L(*c))], 1)
    for f, u, r in ((-2, 4, 2.2), (31, 2.4, 1.0)):  # buracos (atrás do crânio e a narina)
        pygame.draw.circle(tela, (24, 22, 30), Q(L(f, u)), max(1, int(r * s)))
    c = Q(L(35.6, 4.6))  # a ÓRBITA vazia com a luzinha verde lá no fundo
    pygame.draw.circle(tela, BORDA, c, max(2, int(4.4 * s)))
    pygame.draw.circle(tela, (24, 22, 30), c, max(2, int(3.6 * s)))
    if not branco:
        brilho(tela, c, int(9 * s), verde, 150)
        pygame.draw.circle(tela, verde, c, max(1, int(1.3 * s)))
    braco("cf", "mf", osso_c)


def desenhar_sphyrus(l, tela, p, branco):
    if nadando_agora(l) or (l.extra.get("entrada_fin") and getattr(l, "entrada_t", None) is not None):
        return desenhar_barbatana(l, tela, branco)
    if l.f.get("estilo") == "esqueleto":  # (roupa de Halloween: o desenho inteiro é outro, só os ossos)
        return desenhar_esqueleto(l, tela, p, branco)
    s = l.s
    pele, pele_esc, barriga = _cor("m", PELE), _cor("M", PELE_ESC), _cor("a", BARRIGA)
    linha, forte = cor_linha(l)
    olho_cor = _cor("o", OLHO)
    if branco:
        pele = pele_esc = barriga = linha = olho_cor = (245, 245, 250)

    volta = l.memo.get("volta", 0) if l.estado == "ataque" and l.nome_golpe == "sphyrus_onda" else 0
    ang_v = volta * math.tau
    K = math.cos(ang_v)  # o corpo girando: fica fino de lado e espelhado de costas
    if abs(K) < 0.18:
        K = 0.18 if K >= 0 else -0.18

    def Q(q):
        return Pt(l, q[0] * K, q[1])

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

    def tubo(pts, larg, cor):
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

    qd, pc, cb = p["qd"], p["pc"], p["cb"]
    mega = l.f.get("estilo") == "megalodonte" and not branco  # (roupa MEGALODONTE)

    def perna(pe, joelho, cor):
        """Perna de raptor (dobrada pra trás) com a nadadeirinha no tornozelo."""
        P, J = p[pe], p[joelho]
        J = (J[0] + 5, J[1] + 2)
        tornozelo = (P[0] - 7, P[1] + 14)
        dedos = (P[0] + 12, P[1] + 1)
        poly([tornozelo, (tornozelo[0] - 9, tornozelo[1] + 4), (tornozelo[0] - 2, tornozelo[1] - 4)], cor)  # nadadeirinha
        osso(J, tornozelo, 4.4, 3.2, cor)
        osso(tornozelo, (P[0] + 1, P[1] + 3), 3.2, 2.6, cor)
        osso((P[0] + 1, P[1] + 3), dedos, 2.6, 1.4, cor)
        tubo([(qd[0] - 2, qd[1] + 2), entre(qd, J, 0.55), J], [(10, 9), (8, 7), (5, 5)], cor)

    def braco(cot, mao, cor, nadadeira):
        ombro = entre(pc, qd, 0.12)
        cot_p, mao_p = p[cot], p[mao]
        if nadadeira:  # a ASINHA ESPINHOSA (membrana com raios de espinho, tipo peixe-leão)
            atras = entre(pc, qd, 0.55)
            ponta = entre(cot_p, mao_p, 0.75)
            raios = [entre(atras, ponta, k / 4) for k in range(5)]
            fora = []
            for k, r in enumerate(raios):
                dx, dy = r[0] - cot_p[0], r[1] - cot_p[1]
                n = math.hypot(dx, dy) or 1
                fora.append((r[0] + dx / n * 13, r[1] + dy / n * 13))
            memb = [cot_p] + fora[::-1] + [atras]
            tp = [Q(q) for q in memb]
            pygame.draw.polygon(tela, BORDA, tp)
            pygame.draw.polygon(tela, mistura(cor, (180, 200, 220), 0.3), tp, 0)
            for f in fora:
                pygame.draw.line(tela, BORDA, Q(cot_p), Q(f), max(1, int(1.4 * s)))
        osso(ombro, cot_p, 4, 3.2, cor)
        dx, dy = cot_p[0] - mao_p[0], cot_p[1] - mao_p[1]
        n = math.hypot(dx, dy) or 1
        poly([(cot_p[0] + dy / n * 2, cot_p[1] - dx / n * 2), (cot_p[0] + dx / n * 9 - dy / n * 2, cot_p[1] + dy / n * 9 + 4),
              (cot_p[0] - dy / n * 2, cot_p[1] + dx / n * 2)], (230, 230, 220))  # o espinho do cotovelo
        osso(cot_p, mao_p, 3.2, 2.4, cor)
        a = _ang((mao_p[0] - cot_p[0], mao_p[1] - cot_p[1]))
        for k in (-0.5, 0, 0.5):  # 3 garras
            g = (mao_p[0] + math.cos(a + k) * 6, mao_p[1] + math.sin(a + k) * 6)
            pygame.draw.line(tela, BORDA, Q(mao_p), Q(g), max(2, int(1.8 * s)))
            pygame.draw.line(tela, (236, 236, 224), Q(entre(mao_p, g, 0.4)), Q(g), max(1, int(s)))

    # --- de trás pra frente ---
    braco("ct", "mt", pele_esc, False)
    perna("pt", "jt", pele_esc)
    # a CAUDA (em V, com anel de espinhos na base)
    t = l.t
    cauda = []
    for i in range(9):  # (curta e levantada: rabo de tubarão, não de lagarto)
        q = (qd[0] - 6 - i * 6.6, qd[1] - 4 - i * 2.6 + math.sin(t * 0.08 + i * 0.5) * i * 0.3)
        if 0 < volta < 1:  # E: a cauda fica reta pra trás e CHICOTEIA atrasada (curva seguindo o giro)
            q = (qd[0] - 6 - i * 7.4, qd[1] - 6 - i * 0.6)
            q = (q[0] * math.cos(ang_v - i * 0.16) / K, q[1])
        cauda.append(q)
    if 0.1 < volta < 1:  # o borrão da ponta da cauda girando
        for j in range(1, 5):
            a_ = ang_v - j * 0.4
            x_ = (qd[0] - 66) * math.cos(a_ - 1.3)
            y_ = qd[1] - 12
            pygame.draw.circle(tela, (200, 235, 255), Pt(l, x_, y_), max(2, int((12 - j * 2.2) * s)), max(1, int(2 * s)))
        pts_ = [Pt(l, (qd[0] - 66) * math.cos(ang_v - 1.3 - k * 0.15), qd[1] - 12) for k in range(10)]
        pygame.draw.lines(tela, (230, 248, 255), False, pts_, max(2, int(3 * s)))
    larg_c = [(max(1.6, 8 - i * 0.6), max(1.4, 7 - i * 0.55)) for i in range(len(cauda))]
    ponta = cauda[-1]
    dirc = _ang((ponta[0] - cauda[-2][0], ponta[1] - cauda[-2][1]))
    lobo1 = (ponta[0] + math.cos(dirc + 0.9) * 22, ponta[1] + math.sin(dirc + 0.9) * 22)  # lobo de cima (maior)
    lobo2 = (ponta[0] + math.cos(dirc - 0.8) * 14, ponta[1] + math.sin(dirc - 0.8) * 14)
    if l.lado() * (lobo1[1] - lobo2[1]) < 0 and False:
        lobo1, lobo2 = lobo2, lobo1
    poly([ponta, lobo1, entre(ponta, entre(lobo1, lobo2, 0.5), 0.5), lobo2], pele)
    ce, cd = tubo(cauda, larg_c, pele)
    for k in range(4):  # o anel de espinhos na base da cauda
        b = entre(ce[1], cd[1], k / 3)
        poly([(b[0] - 1.5, b[1]), (b[0] - 3, b[1] + 6 - k), (b[0] + 1.5, b[1])], (226, 226, 214))
    pygame.draw.lines(tela, linha, False, [Q(entre(a, c, 0.5)) for a, c in zip(ce[:9], cauda[:9])],
                      max(1, int(1.6 * s)))
    # o TRONCO: barbatana dorsal atrás, corpo, barriga de escamas
    dx, dy = pc[0] - qd[0], pc[1] - qd[1]
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    nx, ny = -uy, ux  # (pra trás do corpo)
    b1 = (qd[0] + dx * 0.25 + nx * 9, qd[1] + dy * 0.25 + ny * 9)
    b2 = (qd[0] + dx * 0.85 + nx * 9, qd[1] + dy * 0.85 + ny * 9)
    pico = (qd[0] + dx * 0.6 + nx * 46 + ux * 10, qd[1] + dy * 0.6 + ny * 46 + uy * 10)
    rasgo = entre(pico, b2, 0.25)
    fin = [b1, pico, (rasgo[0] - nx * 4, rasgo[1] - ny * 4), (rasgo[0] + ux * 4 + nx, rasgo[1] + uy * 4 + ny), b2]
    poly(fin, pele)
    if mega:  # cicatriz de batalha na barbatana
        pygame.draw.line(tela, (180, 180, 176), Q(entre(b1, pico, 0.4)), Q(entre(b2, pico, 0.55)), max(1, int(1.4 * s)))
    for i in range(6):  # CÓDIGO DE BARRAS na barbatana
        a = entre(entre(b1, pico, 0.25), entre(b2, pico, 0.25), 0.2 + i * 0.1)
        c = entre(a, entre(b1, b2, 0.2 + i * 0.1), 0.6)
        pygame.draw.line(tela, BORDA, Q(a), Q(c), max(1, int((0.8 + (i % 3 == 0)) * s)))
    tronco = [(qd[0] - ux * 4, qd[1] - uy * 4), qd, entre(qd, pc, 0.5), pc]
    te, td = tubo(tronco, [(10, 10), (11, 12), (11, 12.5), (9, 10.5)], pele)
    frente = [entre(q, r, 1.35) for q, r in zip(td, tronco)]  # (a barriga amarela bem aparecendo)
    tp = [Q(q) for q in td[1:] + frente[1:][::-1]]
    pygame.draw.polygon(tela, barriga, tp)
    for i in range(1, 4):  # as placas de escama (mosassauro)
        pygame.draw.line(tela, mistura(barriga, BORDA, 0.35), Q(entre(td[i], frente[i], 0.1)), Q(frente[i]),
                         max(1, int(s)))
    ca, cc = entre(td[1], frente[1], 0.3), entre(td[2], frente[2], 0.4)  # a cicatriz de pontos
    pygame.draw.line(tela, (140, 70, 70), Q(ca), Q(cc), max(1, int(1.2 * s)))
    for k in range(4):
        m = entre(ca, cc, (k + 0.5) / 4)
        pygame.draw.line(tela, BORDA, Q((m[0] - 2, m[1] - 1.5)), Q((m[0] + 2, m[1] + 1.5)), max(1, int(s)))
    lin = [entre(a, c, 0.5) for a, c in zip(te, tronco)]  # a LINHA BIOLUMINESCENTE
    if forte and not branco:
        for q in lin[1:]:
            brilho(tela, Q(q), int(10 * s), linha, 90)
    pygame.draw.lines(tela, linha, False, [Q(q) for q in lin], max(2, int(2.8 * s)))
    if mega:  # as cicatrizes de batalha no corpo
        for k, (a_, b_) in enumerate(((0.3, 0.55), (0.6, 0.8), (0.15, 0.3))):
            pa, pb = entre(te[1], td[1], a_), entre(te[2 + k % 2], td[2 + k % 2], b_)
            pygame.draw.line(tela, (178, 176, 170), Q(pa), Q(pb), max(1, int(1.3 * s)))
    perna("pf", "jf", pele)
    # o PESCOÇO: guelras, coleira quebrada
    osso(pc, cb, 8, 7, pele)
    abre_guelra = (l.estado == "ataque") or math.sin(t * 0.08) > 0.6
    for k in (0.3, 0.48, 0.66):
        a = entre(pc, cb, k)
        pygame.draw.line(tela, (150, 30, 40) if abre_guelra else BORDA, Q((a[0] - 3, a[1] + 1)),
                         Q((a[0] + 1, a[1] - 3)), max(1, int((2.2 if abre_guelra else 1.2) * s)))
    c0 = entre(pc, cb, 0.15)
    dxn, dyn = cb[0] - pc[0], cb[1] - pc[1]
    nn = math.hypot(dxn, dyn) or 1
    px_, py_ = -dyn / nn, dxn / nn
    col_a, col_b = (c0[0] + px_ * 9, c0[1] + py_ * 9), (c0[0] - px_ * 6, c0[1] - py_ * 6)
    pygame.draw.line(tela, BORDA, Q(col_a), Q(col_b), max(3, int(4.6 * s)))
    pygame.draw.line(tela, (150, 156, 166), Q(col_a), Q(entre(col_a, col_b, 0.45)), max(2, int(2.8 * s)))
    pygame.draw.line(tela, (150, 156, 166), Q(entre(col_a, col_b, 0.62)), Q(col_b), max(2, int(2.8 * s)))  # quebrada
    # a CABEÇA: mandíbula de mosassauro + o MARTELO
    ang = (_ang((cb[0] - pc[0], cb[1] - pc[1])) - math.pi / 2) * 0.6 + (0.55 if rugindo(l) else 0)
    hc, hs = math.cos(ang), math.sin(ang)

    def L(f, u):
        f, u = f * 1.35, u * 1.35
        return (cb[0] + 2 + f * hc - u * hs, cb[1] + f * hs + u * hc)

    def contornado(pts, cor):  # (preenche e contorna fininho por igual: no pixel art a ponta não vira borrão preto)
        tp = [Q(q) for q in pts]
        pygame.draw.polygon(tela, cor, tp)
        pygame.draw.polygon(tela, BORDA, tp, 1)

    abre = 0.0
    if l.estado == "ataque" and l.nome_golpe in ("sphyrus_martelada", "sphyrus_mergulho", "sphyrus_ultimate"):
        abre = 0.75
    if rugindo(l):
        abre = 0.9
    if "boca" in l.extra:  # (pose de vitória MANDÍBULA ABERTA controla a boca)
        abre = l.extra["boca"]
    dente_falta = l.extra.get("dente_falta", 0) > 0

    def queixo(f, u):  # a mandíbula de baixo gira pra baixo (abre ENORME)
        a = -abre
        f0, u0 = -3, -1
        df, du = f - f0, u - u0
        return L(f0 + df * math.cos(a) - du * math.sin(a), u0 + df * math.sin(a) + du * math.cos(a))

    if abre > 0:  # o céu da boca (vermelho escuro)
        tp = [Q(L(-3, -1)), Q(L(30, -1.4)), Q(queixo(28, -1.6)), Q(queixo(-3, -1))]
        pygame.draw.polygon(tela, (110, 20, 30), tp)
    for fila, cor_d in ((1.4, (214, 214, 200)), (0, (250, 250, 236))):  # DUAS fileiras de dentes (embaixo)
        for i in range(6):
            x = 5 + i * 3.8 + fila
            pygame.draw.polygon(tela, cor_d, [Q(queixo(x, -1.6)), Q(queixo(x + 1.8, -1.6)),
                                              Q(queixo(x + 0.9, 1.2 - fila * 0.5))])
    contornado([queixo(-4, -1), queixo(30, -1.6), queixo(27, -4.6), queixo(10, -6.2), queixo(-3, -4.4)], barriga)
    for fila, cor_d in ((1.4, (214, 214, 200)), (0, (250, 250, 236))):  # DUAS fileiras (em cima)
        for i in range(7):
            if dente_falta and fila == 0 and i == 3:
                continue  # (caiu um dentinho: já já nasce outro)
            x = 4 + i * 3.8 + fila
            pygame.draw.polygon(tela, cor_d, [Q(L(x, -1)), Q(L(x + 1.8, -1)), Q(L(x + 0.9, -4 + fila * 0.5))])
    if mega:  # MEGALODONTE (roupa): cabeçona de tubarão comum, focinho cônico, dentões e olho preto
        poly([L(-7, 2), L(-4, 9), L(10, 11), L(26, 7), L(36, 2.5), L(38, 0), L(34, -1.6), L(4, -1.8), L(-7, -1.8)], pele)
        poly([L(-5, 7), L(6, 10.5), L(20, 8.5), L(14, 6)], mistura(pele, (255, 255, 255), 0.12), False)
        for i in range(6):  # os DENTÕES triangulares serrilhados
            x = 6 + i * 4.6
            pygame.draw.polygon(tela, (246, 244, 232), [Q(L(x, -1.4)), Q(L(x + 3.4, -1.4)), Q(L(x + 1.7, -6.5))])
            pygame.draw.line(tela, (190, 186, 170), Q(L(x + 0.8, -2.6)), Q(L(x + 2.6, -2.6)), 1)
        for k in range(3):  # as guelras na cabeça
            pygame.draw.line(tela, BORDA, Q(L(-3 - k * 2.2, 6)), Q(L(-2 - k * 2.2, 0.5)), max(1, int(1.2 * s)))
        c = Q(L(14, 5.4))
        pygame.draw.circle(tela, (8, 8, 10), c, max(2, int(1.6 * s)))  # olho preto, pequeno e redondo
        pygame.draw.circle(tela, (90, 90, 96), (c[0] - 1, c[1] - 1), 1)
        pygame.draw.line(tela, (190, 190, 186), Q(L(18, 8)), Q(L(26, 5)), max(1, int(1.2 * s)))  # cicatriz
    else:
        # a CABEÇA DE PERFIL (pedido do Gomes): o martelo visto DE LADO vira uma lâmina comprida e achatada
        # apontando pra frente, e só UM olho aparece, lá na ponta
        cabeca = [(-6, -1.6), (-7, 4), (-4, 9), (4, 11.6), (18, 9.6), (30, 7.6), (37, 5.6), (39, 3.4), (36.5, 0.8),
                  (28, -1.2), (4, -1.4)]
        contornado([L(*q) for q in cabeca], pele)
        lamina = [(6, 10.4), (22, 8.8), (34, 7.0), (40, 5.0), (40.6, 3.2), (37, 2.4), (24, 4.6), (6, 6.4)]
        contornado([L(*q) for q in lamina], mistura(pele, (255, 255, 255), 0.18))  # o MARTELO de lado (a borda clara)
        pygame.draw.lines(tela, pele_esc, False, [Q(L(*q)) for q in ((8, 6.0), (24, 4.2), (37, 2.6))],
                          1)  # a sombra embaixo do martelo
        pygame.draw.lines(tela, mistura(pele, (255, 255, 255), 0.45), False,
                          [Q(L(*q)) for q in ((8, 9.6), (22, 8.2), (34, 6.4))], max(1, int(1.2 * s)))  # o brilho
        pygame.draw.circle(tela, BORDA, Q(L(31, 2.4)), max(1, int(0.9 * s)))  # a narina
        for k in range(3):  # as guelras atrás da cabeça
            pygame.draw.line(tela, BORDA, Q(L(-2 - k * 2.4, 6)), Q(L(-1 - k * 2.4, 1)), max(1, int(1.1 * s)))
        olhos_fortes = l.extra.get("frenesi") or l.extra.get("sente", 0) > 0
        piscando = l.extra.get("sente", 0) > 0 and (l.extra["sente"] // 4) % 2
        r = 3.6
        c = Q(L(35.6, 4.6))  # o OLHO (um só, na ponta do martelo)
        if not branco:
            brilho(tela, c, int((8 if olhos_fortes else 5) * s * r / 2.2), olho_cor, 140 if olhos_fortes else 80)
        pygame.draw.circle(tela, BORDA, c, max(2, int((r + 0.9) * s)))
        pygame.draw.circle(tela, (255, 255, 255) if piscando else olho_cor, c, max(1, int(r * s)))
        pygame.draw.circle(tela, BORDA, (c[0] + int(l.lado() * 0.8 * s), c[1]), max(1, int(r * 0.4 * s)))  # a pupila
        pygame.draw.circle(tela, (255, 255, 255), (c[0] - int(l.lado() * 0.8 * s), c[1] - int(0.9 * s)), 1)
    braco("cf", "mf", pele, True)


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Sphyrus grande: os olhos amarelos."""
    cb = P("cb")
    pygame.draw.circle(q, OLHO, (int(cb[0] + 10 * s * d), int(cb[1] - 10 * s)), max(2, int(2 * s)))


# =====================================================================
# ENTRADA: a barbatana cortando o chão... e ele pula dando um RUGIDÃO
# =====================================================================
E_NADA, E_PULA, E_FIM = 64, 20, 110


def entrada(l, t, jogo):
    xf = l.extra["entrada_x"]
    de = (PAREDE_E - 40) if l.dir > 0 else (PAREDE_D + 40)
    if t < E_NADA:
        l.extra["entrada_fin"] = True
        l.x = de + (xf - de) * suave(t / E_NADA)
        l.y = CHAO
        if t % 4 == 0:
            fumaca(jogo, l.x, CHAO - 2, 1, (210, 236, 255), 1.2, -0.4)
    elif t < E_NADA + E_PULA:
        if t == E_NADA:
            l.extra["entrada_fin"] = False
            fumaca(jogo, l.x, CHAO - 4, 12, (210, 236, 255), 4, -2)
            som.tocar("puf", 0.7)
        k = (t - E_NADA) / E_PULA
        l.x = xf
        l.y = CHAO - math.sin(k * math.pi) * 130
        l.sobrepor = dict(POSES_SPHYRUS["s_salto"])
    else:
        l.x, l.y = xf, CHAO
        if t == E_NADA + E_PULA:
            som.tocar("queda")
            som.tocar("terra", 0.8)
            jogo.tremer(10)
        l.sobrepor = dict(POSES_SPHYRUS["s_ruge"]) if t < E_FIM else {}
    l.t += 1


# =====================================================================
# VITÓRIA: RUGIDÃO com a linha acesa
# =====================================================================
def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES_SPHYRUS["s_ruge"] if t > 8 else POSES_SPHYRUS["parado"])
    l.extra["sente"] = 10  # (a linha e os olhos acesos)
    if t == 10:
        som.tocar("terra", 0.6)


def vitoria_efeito(l, tela, t):
    if 10 <= t < 60 and (t // 8) % 2:
        from efeitos import texto_grande
        texto_grande(tela, "GROOOAR!", 22, (140, 220, 255), (int(l.x), int(l.y - 160 * l.s)), contorno=(0, 20, 40))
