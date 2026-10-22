"""FRIGANTUS: o yeti gigantopiteco (criado pelo Gomes) — o 15º, último da v2.0. TANQUE DE CONTROLE: lento, 120 de vida.

Aparência: macaco gigante pré-histórico curvado, BRAÇOS COMPRIDOS quase arrastando no chão, mãos e pés enormes,
pelo branco-neve com as pontas azuladas e pedaços de GELO presos nos braços e nas costas, rosto cinza-escuro,
sobrancelha grossa, olhos pequenos e fundos, bafo gelado saindo da boca e um colar de dentes.
  E      BOLA DE NEVE gigante (10): se acertar, CONGELA meio segundo
  Q      PISÃO: saem ESTACAS DE GELO do chão na frente, que jogam pra cima (12)
  R      soca o chão, sobe um BLOCO de gelo que vira 8 ESTACAS e elas quebram na cabeça dele (8 x 2);
         as 8 acertaram = empurra e PRENDE NA PAREDE 2 segundos
  SHIFT  ESCORREGÃO de barriga no gelo, atropelando (10)
  Z      ULTIMATE: AVALANCHE (40)
  Z2     2ª ULTIMATE: ERA DO GELO — a tela congela, ele dá um soco e o adversário ATRAVESSA 3 CENÁRIOS
  Passiva NEVASCA: cada golpe deixa o adversário mais lento; 3 seguidos = CONGELA 1 segundo
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from golpes import GOLPES, proporcionar, suave
from lutador import Projetil
from max10 import brilho, fumaca

PELO, PELO_SOMBRA, PELE, GELO = (236, 240, 248), (178, 196, 222), (86, 90, 100), (186, 228, 250)
BORDA = (16, 18, 26)
PALETA = {"m": PELO, "M": PELO_SOMBRA, "p": PELE, "c": GELO}  # (letras das roupas)

POSES_FRIGANTUS = {  # (curvado pra frente como gorila; os braços apoiam os nós dos dedos no chão)
    "parado": dict(pt=(-20, 0), jt=(-14, 24), pf=(20, 0), jf=(26, 24), qd=(0, 50), pc=(32, 78), cb=(48, 76),
                   ct=(36, 56), mt=(42, 30), cf=(46, 56), mf=(58, 30)),
    "andar1": dict(pt=(-26, 2), jt=(-16, 24), pf=(26, 0), jf=(30, 24), qd=(0, 48), pc=(32, 76), cb=(48, 74),
                   ct=(42, 56), mt=(52, 30), cf=(30, 56), mf=(24, 30)),
    "andar2": dict(pt=(-6, 6), jt=(4, 28), pf=(4, 0), jf=(14, 26), qd=(0, 52), pc=(32, 80), cb=(48, 78),
                   ct=(36, 56), mt=(38, 30), cf=(38, 56), mf=(40, 30)),
    "andar3": dict(pt=(24, 0), jt=(30, 24), pf=(-24, 2), jf=(-14, 24), qd=(0, 48), pc=(32, 76), cb=(48, 74),
                   ct=(28, 56), mt=(22, 30), cf=(44, 56), mf=(54, 30)),
    "andar4": dict(pt=(4, 0), jt=(14, 26), pf=(-4, 6), jf=(6, 28), qd=(0, 52), pc=(32, 80), cb=(48, 78),
                   ct=(36, 56), mt=(38, 30), cf=(38, 56), mf=(40, 30)),
    "fr_arremessa": dict(pt=(-26, 0), jt=(-14, 26), pf=(24, 0), jf=(30, 28), qd=(0, 52), pc=(10, 90), cb=(26, 92),
                         ct=(-2, 108), mt=(10, 130), cf=(4, 110), mf=(20, 132)),
    "fr_joga": dict(pt=(-26, 0), jt=(-14, 26), pf=(28, 0), jf=(34, 28), qd=(0, 50), pc=(30, 80), cb=(46, 78),
                    ct=(30, 70), mt=(54, 72), cf=(40, 74), mf=(66, 76)),
    "fr_pisao": dict(pt=(-22, 0), jt=(-10, 28), pf=(34, 42), jf=(30, 58), qd=(0, 56), pc=(14, 90), cb=(30, 90),
                     ct=(-10, 74), mt=(-26, 60), cf=(26, 76), mf=(44, 64)),
    "fr_soco_chao": dict(pt=(-24, 0), jt=(-12, 24), pf=(24, 0), jf=(32, 24), qd=(0, 44), pc=(24, 70), cb=(40, 66),
                         ct=(34, 46), mt=(48, 4), cf=(40, 48), mf=(56, 4)),
    "fr_barriga": dict(pt=(-50, 8), jt=(-28, 10), pf=(-50, 4), jf=(-28, 8), qd=(0, 14), pc=(40, 18), cb=(58, 22),
                       ct=(56, 12), mt=(78, 10), cf=(58, 14), mf=(82, 14)),
    "fr_peito_a": dict(pt=(-20, 0), jt=(-12, 28), pf=(20, 0), jf=(28, 28), qd=(0, 54), pc=(10, 92), cb=(24, 92),
                       ct=(22, 72), mt=(18, 88), cf=(32, 80), mf=(30, 96)),
    "fr_peito_b": dict(pt=(-20, 0), jt=(-12, 28), pf=(20, 0), jf=(28, 28), qd=(0, 54), pc=(10, 92), cb=(24, 92),
                       ct=(24, 80), mt=(22, 96), cf=(30, 72), mf=(28, 88)),
    "fr_ruge": dict(pt=(-24, 0), jt=(-12, 30), pf=(22, 0), jf=(30, 30), qd=(0, 56), pc=(4, 92), cb=(14, 106),
                    ct=(-22, 104), mt=(-36, 130), cf=(26, 104), mf=(42, 130)),
    "fr_soco": dict(pt=(-28, 0), jt=(-14, 26), pf=(30, 0), jf=(36, 28), qd=(0, 50), pc=(30, 80), cb=(46, 78),
                    ct=(10, 66), mt=(4, 44), cf=(48, 82), mf=(82, 86)),
    # (as poses do meio: deixam os golpes FLUIDOS — pedido do Gomes)
    "fr_pisao_bate": dict(pt=(-22, 0), jt=(-12, 18), pf=(26, 0), jf=(32, 18), qd=(0, 40), pc=(30, 66), cb=(46, 62),
                          ct=(30, 44), mt=(36, 18), cf=(48, 44), mf=(62, 20)),
    "fr_mergulha": dict(pt=(-30, 4), jt=(-16, 20), pf=(10, 0), jf=(20, 18), qd=(0, 34), pc=(36, 46), cb=(54, 44),
                        ct=(56, 40), mt=(76, 40), cf=(58, 42), mf=(80, 44)),
    "fr_levanta": dict(pt=(-36, 0), jt=(-20, 10), pf=(-20, 0), jf=(-6, 12), qd=(0, 24), pc=(30, 40), cb=(46, 40),
                       ct=(38, 22), mt=(44, 0), cf=(46, 22), mf=(54, 0)),
}
proporcionar(POSES_FRIGANTUS)


def _cor(letra, padrao):
    import pecas
    return (pecas.TROCA or {}).get(letra, padrao)


def entre(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def outro_de(l, jogo):
    return jogo.L[1] if jogo.L[0] is l else jogo.L[0]


# =====================================================================
# Todo quadro: o bafo gelado
# =====================================================================
def todo_quadro(l, jogo):
    x = l.extra
    x["bafo"] = x.get("bafo", 0) + 1
    if x["bafo"] % 70 < 14 and x["bafo"] % 3 == 0 and l.estado in ("parado", "andando"):
        p = l.pose_vista or l.pose_atual()
        cb = l.ponto(p, "cb")
        jogo.faiscas.append([cb[0] + l.dir * 20 * l.s, cb[1] + 18 * l.s, l.dir * random.uniform(0.6, 1.4),
                             random.uniform(-0.6, -0.1), 26, (225, 240, 255), 4])


# =====================================================================
# E: BOLA DE NEVE (congela meio segundo)
# =====================================================================
E_SOLTA = 18


def bola_neve(l, outro, jogo):
    t = l.t
    l.vx = 0
    l.fisica(jogo)
    if t == E_SOLTA:
        jogo.projeteis.append(Projetil(l, l.x + l.dir * 60 * l.s, l.y - 72 * l.s, l.dir, GOLPES["frigantus_bola"]))
        som.tocar("vento")
    if t >= E_SOLTA + 16:
        return "fim"


def bola_neve_efeito(l, tela):
    if l.t < E_SOLTA:  # a bola juntando nas mãos lá em cima
        p = l.pose_vista or l.pose_atual()
        mx, my = l.ponto(p, "mf")
        r = int((6 + l.t) * l.s * 0.7)
        pygame.draw.circle(tela, (210, 220, 236), (int(mx), int(my - r * 0.6)), r + 2)
        pygame.draw.circle(tela, (250, 252, 255), (int(mx), int(my - r * 0.6)), r)


def bola_acertou(dono, alvo, jogo, res):
    if res == "hit" and alvo.vida > 0:
        alvo.congelar(30)
        som.tocar("quebra", 0.5)


def desenha_bola(p, tela):
    r = p.raio
    pygame.draw.circle(tela, (180, 196, 220), (int(p.x), int(p.y)), r + 2)
    pygame.draw.circle(tela, (250, 252, 255), (int(p.x), int(p.y)), r)
    pygame.draw.circle(tela, (215, 228, 242), (int(p.x + r * 0.3), int(p.y + r * 0.3)), int(r * 0.55))
    for i in range(3):  # neve soltando
        a = p.t * 0.4 + i * 2
        pygame.draw.circle(tela, (240, 246, 255), (int(p.x - p.vx * (2 + i) + math.sin(a) * 4), int(p.y + math.cos(a) * 6)), 3)


# =====================================================================
# Q: PISÃO + ESTACAS DE GELO
# =====================================================================
Q_PISA, Q_ESTACAS, Q_CADA = 8, 8, 2


def pisao(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t == Q_PISA:
        som.tocar("terra")
        jogo.tremer(10)
        fumaca(jogo, l.x + l.dir * 30, CHAO - 4, 8, (230, 240, 255), 3, -1)
    k = (t - Q_PISA) // Q_CADA
    m["caixa"] = None
    if t >= Q_PISA and k < Q_ESTACAS:
        off = 30 + k * 30  # a estaca saindo agora (a caixa de acerto fica em cima dela)
        if (t - Q_PISA) % Q_CADA == 0:
            m.setdefault("estacas", []).append((l.x + l.dir * off * l.s, t))
            som.tocar("quebra", 0.25)
        m["caixa"] = (off - 22, 0, off + 22, 70)
        m["g_hit"] = GOLPES["frigantus_estaca"]
    if t >= Q_PISA + Q_ESTACAS * Q_CADA + 24:
        return "fim"


def estaca(tela, x, base, alto, s, w=10):
    if alto <= 1:
        return
    pts = [(x - w * s, base), (x, base - alto), (x + w * s, base)]
    pygame.draw.polygon(tela, (60, 100, 130), [(px, py + 2) for px, py in pts])
    pygame.draw.polygon(tela, GELO, pts)
    pygame.draw.line(tela, (245, 252, 255), (x - w * s * 0.4, base - 4), (x - 1, base - alto + 6), 2)


def pisao_efeito(l, tela):
    for x, t0 in l.memo.get("estacas", []):
        u = l.t - t0
        if 0 <= u < 24:
            alto = min(1, u / 3) * (1 - max(0, (u - 14) / 10)) * 70 * l.s
            estaca(tela, x, CHAO + 2, alto, l.s)


# =====================================================================
# R: BLOCO DE GELO -> 8 ESTACAS na cabeça (as 8: prende na parede 2 s)
# =====================================================================
R_SOCA, R_SOBE, R_PARTE, R_N, R_CADA = 14, 12, 8, 8, 5
R_ATIRA = R_SOCA + R_SOBE + R_PARTE
R_PRESO = 2 * FPS


def bloco(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t == R_SOCA:
        som.tocar("terra")
        jogo.tremer(10)
        m["bx"] = l.x + l.dir * 70 * l.s
    if t == R_SOCA + R_SOBE:
        som.tocar("quebra", 0.6)
    k = (t - R_ATIRA) // R_CADA
    if t >= R_ATIRA and (t - R_ATIRA) % R_CADA == 0 and k < R_N:  # uma estaca quebra na cabeça dele
        m.setdefault("quebras", []).append((t, outro.x, outro.y - 110 * outro.s))
        som.tocar("quebra", 0.4)
        if outro.inv <= 0 and outro.estado not in ("caido", "agarrado") and abs(outro.x - l.x) < 520:
            final = k == R_N - 1
            if final and m.get("acertos", 0) == R_N - 1:  # AS 8: prende na parede
                outro.receber(GOLPES["frigantus_estaca_cabeca"], l.dir, l, l.f["forca"])
                parede = PAREDE_D if l.dir > 0 else PAREDE_E
                outro.x = parede
                outro.y = CHAO
                outro.congelar(R_PRESO)
                jogo.tremer(14)
                som.tocar("ko", 0.5)
                m["preso"] = t
            else:
                res = outro.receber(GOLPES["frigantus_estaca_cabeca"], l.dir, l, l.f["forca"])
                if res == "hit":
                    m["acertos"] = m.get("acertos", 0) + 1
                    outro.stun = max(outro.stun, 14)
    if t >= R_ATIRA + R_N * R_CADA + 18:
        return "fim"


def bloco_efeito(l, tela):
    t = l.t
    m = l.memo
    bx = m.get("bx")
    if bx is None:
        return
    s = l.s
    if R_SOCA <= t < R_SOCA + R_SOBE + R_PARTE:  # o bloco subindo e se partindo
        sobe = suave(min(1, (t - R_SOCA) / R_SOBE))
        parte = max(0, (t - R_SOCA - R_SOBE) / R_PARTE)
        topo = CHAO - 80 * s * sobe
        for i in range(R_N):
            cx = bx + (i - 3.5) * 9 * s * (1 + parte * 1.8)
            cy = topo - parte * 60 * s - abs(i - 3.5) * parte * 6
            pygame.draw.rect(tela, (60, 100, 130), (cx - 5 * s, cy, 10 * s, 80 * s * sobe))
            pygame.draw.rect(tela, GELO, (cx - 4 * s, cy + 1, 8 * s, 80 * s * sobe - 2))
    if t >= R_SOCA + R_SOBE + R_PARTE:  # as estacas que ainda faltam, esperando no alto
        feitas = len(m.get("quebras", []))
        for i in range(feitas, R_N):
            cx = bx + (i - 3.5) * 25 * s
            estaca(tela, cx, CHAO - 140 * s, -40 * s, s, 6)
    for t0, x, y in m.get("quebras", []):  # os cacos na cabeça dele
        u = t - t0
        if 0 <= u < 10:
            for k in range(5):
                a = k * 1.25 + t0
                pygame.draw.line(tela, (230, 248, 255), (x, y), (x + math.cos(a) * u * 4, y + math.sin(a) * u * 3), 2)
    pr = m.get("preso")
    if pr is not None and t - pr < 30:
        from efeitos import texto_grande
        texto_grande(tela, "PRESO!", 30, (200, 240, 255), (int(l.x + l.dir * 200), int(l.y - 160 * s)), contorno=(10, 30, 60))


# =====================================================================
# SHIFT: ESCORREGÃO de barriga
# =====================================================================
S_SAI, S_VAI, S_VEL = 10, 32, 11


def escorregao(l, outro, jogo):
    t = l.t
    m = l.memo
    if S_SAI <= t < S_SAI + S_VAI and "bateu" not in m:
        l.vx = S_VEL * l.dir * (1 - 0.4 * (t - S_SAI) / S_VAI)
        m["caixa"] = (0, 0, 80, 40)
        if t % 3 == 0:
            jogo.faiscas.append([l.x - l.dir * 40, CHAO - 4, -l.dir * 2, -1, 18, (230, 244, 255), 4])
        if l.acertou:
            m["bateu"] = t
    else:
        l.vx *= 0.8
        m["caixa"] = None
    l.fisica(jogo)
    if t >= S_SAI + S_VAI + 18:
        return "fim"


def escorregao_efeito(l, tela):
    if S_SAI <= l.t < S_SAI + S_VAI:  # o rastro de gelo no chão
        pygame.draw.line(tela, (220, 240, 255), (l.x - l.dir * 120, CHAO + 2), (l.x, CHAO + 2), 4)


# =====================================================================
# Z: AVALANCHE
# =====================================================================
U_PEITO, U_RUGE, U_DESCE, U_BATE = 22, 34, 60, 64


def avalanche(l, outro, jogo):
    t = l.t
    m = l.memo
    m["tela_toda"] = True
    l.vx = 0
    l.fisica(jogo)
    if t < U_PEITO:
        l.sobrepor = dict(POSES_FRIGANTUS["fr_peito_a" if (t // 5) % 2 else "fr_peito_b"])
        if t % 5 == 0:
            som.tocar("soco", 0.4)
    elif t < U_DESCE:
        l.sobrepor = dict(POSES_FRIGANTUS["fr_ruge"])
        if t == U_PEITO:
            som.tocar("uivo", 0.8)
        if t % 6 == 0:
            jogo.tremer(6)
    else:
        l.sobrepor = {}
    if t == U_BATE:
        if outro.inv <= 0 and outro.estado != "agarrado":
            outro.levar(40, l, GOLPES["frigantus_avalanche"])
            outro.sobrepor = {}
            outro.mudar("voando")
            outro.vx, outro.vy = l.dir * 6, -6
            m["soterrou"] = outro.x
        som.tocar("terra")
        som.tocar("explosao", 0.6)
        jogo.tremer(22)
    if t >= U_BATE + 40:
        l.sobrepor = {}
        return "fim"


def avalanche_efeito(l, tela):
    t = l.t
    if t < U_RUGE:
        return
    alvo = getattr(l, "_alvo_marujos", None)
    ax = alvo.x if alvo is not None else l.x + l.dir * 260
    k = suave(min(1, (t - U_RUGE) / (U_BATE - U_RUGE)))
    some = 1 - suave(max(0, (t - U_BATE - 14) / 26))
    if some <= 0:
        return
    frente_y = -120 + (CHAO + 40) * k  # a parede de neve descendo
    rnd = random.Random(4)
    for i in range(40):
        x = ax + rnd.uniform(-220, 220)
        y = frente_y - rnd.uniform(0, 260)
        r = rnd.uniform(26, 50)
        cor = (240, 244, 252) if i % 3 else (206, 218, 236)
        pygame.draw.circle(tela, cor, (int(x), int(min(CHAO + 10, y))), int(r * some))
    for i in range(8):  # pedras de gelo rolando junto
        x = ax + rnd.uniform(-200, 200)
        y = frente_y - rnd.uniform(0, 120)
        pygame.draw.circle(tela, (120, 150, 180), (int(x), int(min(CHAO, y))), int(10 * some))


# =====================================================================
# Z2: ERA DO GELO (a tela congela, o soco, e ele atravessa 3 cenários)
# =====================================================================
G_RUGE, G_CONGELA, G_SOCO = 20, 44, 62
G_DANO_SOCO, G_DANO_PAREDE = 24, 12


def era_do_gelo(l, outro, jogo):
    t = l.t
    m = l.memo
    m["tela_toda"] = True
    l.vx = 0
    l.fisica(jogo)
    import ult2
    if t < G_RUGE:
        ult2.camera(jogo, 1.3, l.x, l.y - 90 * l.s)
        if t == 4:
            som.tocar("uivo", 0.9)
        return
    if t == G_RUGE:
        if outro.inv <= 0 and outro.estado not in ("caido", "voando", "agarrado") and outro.y > CHAO - 160:
            m["pegou"] = t
            ult2.pega(outro, "golpeado")
            som.tocar("quebra")
        else:
            m["errou"] = t
    if "errou" in m:
        return "fim" if t - m["errou"] > 20 else None
    ult2.camera(jogo, 1.15, (l.x + outro.x) / 2, l.y - 90 * l.s)
    if G_CONGELA <= t < G_SOCO:  # anda até ele, tudo congelado
        l.x += ((outro.x - l.dir * 70 * l.s) - l.x) * 0.2
        l.sobrepor = dict(POSES_FRIGANTUS["fr_ruge" if t < G_SOCO - 8 else "parado"])
    if t == G_SOCO - 8:
        l.sobrepor = dict(POSES_FRIGANTUS["parado"])
    if t == G_SOCO:  # O SOCO
        l.sobrepor = dict(POSES_FRIGANTUS["fr_soco"])
        outro.levar(G_DANO_SOCO, l, GOLPES["frigantus_ult2_soco"])
        outro.vida = max(1, outro.vida)
        outro.sobrepor = {}
        som.tocar("ko")
        ult2.impacto(jogo, 14, 26, 6)
        if hasattr(jogo, "cutscene"):  # e lá vai ele atravessando 3 cenários
            jogo.cutscene = EraDoGelo(jogo, outro, l, l.dir)
        m["socou"] = t
    if "socou" in m and t - m["socou"] > 2:
        l.sobrepor = {}
        return "fim"


def era_do_gelo_efeito(l, tela):
    t = l.t
    if "pegou" not in l.memo or t < G_RUGE:
        return
    k = min(1, (t - G_RUGE) / (G_CONGELA - G_RUGE))
    gelo = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    gelo.fill((170, 220, 255, int(70 * k)))
    for i in range(14):  # a geada crescendo das bordas
        a = i * 0.45
        for borda_x in (0, LARGURA):
            x0 = borda_x
            y0 = (i * 41) % ALTURA
            comp = 160 * k
            d = 1 if borda_x == 0 else -1
            pygame.draw.line(gelo, (235, 248, 255, 220), (x0, y0), (x0 + d * comp, y0 + math.sin(a) * 40), 3)
            pygame.draw.line(gelo, (235, 248, 255, 180), (x0 + d * comp * 0.5, y0 + math.sin(a) * 20),
                             (x0 + d * comp * 0.7, y0 + math.sin(a) * 20 - 30), 2)
    tela.blit(gelo, (0, 0))
    alvo = getattr(l, "_alvo_marujos", None)
    if alvo is not None and "socou" not in l.memo:  # ele dentro de um bloco de gelo
        alvo.desenhar_gelo(tela)


class EraDoGelo:
    """A cena: ele atravessa 3 paredes, passando voando por 2 cenários, e a luta continua no 3º."""
    BATE, VOA = 16, 34  # (cada cenário: quebra a parede e voa por ele)
    POR = BATE + VOA

    def __init__(self, partida, vitima, atacante, lado):
        import cenarios
        import transicao
        from lutador import Lutador
        self.p, self.vitima, self.atacante, self.lado = partida, vitima, atacante, lado
        self.t = 0
        nomes = []
        atual = partida.cena.nome
        for _ in range(3):
            prox = transicao.DESTINOS.get(atual) or random.Random(len(nomes)).choice(list(transicao.DESTINOS))
            if prox == atual or prox in nomes:
                prox = next(n for n in transicao.DESTINOS if n != atual and n not in nomes)
            nomes.append(prox)
            atual = prox
        self.cenas = [cenarios.cenario(n) for n in nomes]
        self.voador = Lutador(vitima.f, 0, -lado)
        self.voador.disfarce = vitima.disfarce
        self.voador.s = vitima.f["tam"] * 1.25
        self.voador.estado = "voando"
        self.voador.chao_sombra = 100_000
        self.fim_t = self.POR * 3 + 20

    @property
    def acabou(self):
        return self.t >= self.fim_t

    def passo(self):
        self.t += 1
        p = self.p
        u = (self.t - 1) % self.POR
        if u == 0 and self.t <= self.POR * 3:  # quebrou mais uma parede
            som.tocar("quebra")
            som.tocar("explosao", 0.6)
            p.tremer(18)
        if self.t == self.POR * 3:  # chegou no 3º cenário
            import clima
            import objetos
            p.cena = self.cenas[-1]
            p.objetos = objetos.criar(p.cena.nome)
            p.clima = clima.criar(p.cena.nome)
            v, a = self.vitima, self.atacante
            v.sobrepor = {}
            v.mudar("caido")
            v.x, v.y, v.vx, v.vy = LARGURA / 2 + self.lado * 170, CHAO, 0, 0
            v.malabar = v.quica = False
            v.rastro, a.rastro = [], []
            v.pose_vista = a.pose_vista = None
            a.golpe = None
            a.mudar("parado")
            a.x, a.y, a.vx, a.vy = LARGURA / 2 - self.lado * 100, CHAO, 0, 0
            a.dir = self.lado
            p.projeteis = []
            v.levar(G_DANO_PAREDE * 3, a, GOLPES["frigantus_ult2_soco"])
            som.tocar("queda")
            p.tremer(16)
            p.poeira(v.x)
            p.transicao_feita = True

    def desenhar(self, tela):
        from efeitos import texto_grande
        t = self.t
        if t >= self.POR * 3:
            self.p.desenhar_luta(tela)
            return
        i = (t - 1) // self.POR
        u = (t - 1) % self.POR
        cena = self.cenas[i]
        tela.blit(cena.fundo, (0, 0))  # o cenário que ele está atravessando
        k = u / self.POR
        v = self.voador
        v.t = t
        v.angulo = t * 0.4 * self.lado
        v.x = LARGURA / 2 - self.lado * 520 + self.lado * 1040 * k
        v.y = 380 - math.sin(k * math.pi) * 120
        for j in range(16):  # riscos de velocidade
            y = (j * 53 + t * 7) % ALTURA
            x = v.x - self.lado * (60 + j * 30)
            pygame.draw.line(tela, (255, 255, 255), (x, y), (x - self.lado * 160, y), 2)
        v.desenhar(tela)
        if u < self.BATE:  # a parede de entrada estourando
            x0 = 0 if self.lado > 0 else LARGURA
            rnd = random.Random(i * 7)
            for c in range(20):
                cx = x0 + self.lado * (u * 14 + rnd.uniform(0, 80))
                cy = rnd.uniform(60, ALTURA - 60) + u * u * 0.4
                pygame.draw.rect(tela, rnd.choice(((140, 130, 120), (100, 90, 80), (190, 230, 255))), (cx, cy, 12, 9))
            texto_grande(tela, ("CRASH!", "CRAAASH!", "CRAAAAASH!")[i], 70 + i * 12, (200, 240, 255),
                         (LARGURA // 2, 140), 1 + max(0, 6 - u) * 0.08, contorno=(10, 30, 60))
        if u < 4:
            branco = pygame.Surface((LARGURA, ALTURA))
            branco.fill((230, 245, 255))
            branco.set_alpha(220 - u * 50)
            tela.blit(branco, (0, 0))


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


_registra("frigantus_bola", ini=0, ativo=1, rec=0, proj=True, raio=18, vel=9, dano=10, hit=20, defe=10, emp=3,
          nivel="medio", ao_acertar=bola_acertou, desenho_proj=desenha_bola)
_registra("frigantus_neve", ini=E_SOLTA, ativo=1, rec=16, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=bola_neve, efeito=bola_neve_efeito, ia="longe",
          quadros=[(0, "parado"), (8, "fr_arremessa"), (E_SOLTA - 1, "fr_arremessa"), (E_SOLTA + 2, "fr_joga"),
                   (E_SOLTA + 14, "parado")])
GOLPES["frigantus_estaca"] = dict(dano=12, hit=24, defe=10, emp=2, nivel="baixo", especial=True, lanca=16)
_registra("frigantus_pisao", ini=Q_PISA, ativo=Q_ESTACAS * Q_CADA, rec=24, dano=0, hit=0, defe=0, emp=0,
          nivel="medio", logica=pisao, efeito=pisao_efeito, ia="perto", lanca_depois=True,
          quadros=[(0, "parado"), (6, "fr_pisao"), (Q_PISA - 2, "fr_pisao"), (Q_PISA + 1, "fr_pisao_bate"),
                   (Q_PISA + 10, "fr_pisao_bate"), (Q_PISA + 22, "parado")])
GOLPES["frigantus_pisao"]["total"] = 9999
GOLPES["frigantus_estaca_cabeca"] = dict(dano=2, hit=16, defe=6, emp=0, nivel="alto", especial=True)
_registra("frigantus_bloco", ini=R_SOCA, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=bloco, efeito=bloco_efeito, ia="medio",
          quadros=[(0, "parado"), (6, "fr_arremessa"), (R_SOCA - 2, "fr_arremessa"), (R_SOCA, "fr_soco_chao"),
                   (R_ATIRA, "fr_soco_chao"), (R_ATIRA + 6, "parado")])
GOLPES["frigantus_bloco"]["total"] = 9999
_registra("frigantus_escorregao", base="agachado", ini=S_SAI, ativo=S_VAI, rec=18, janelas=((S_SAI, S_SAI + S_VAI),),
          caixa=(0, 0, 80, 40), dano=10, hit=24, defe=10, emp=4, nivel="baixo", derruba=True, voo=(6, 8),
          logica=escorregao, efeito=escorregao_efeito, ia="medio",
          quadros=[(0, "parado"), (5, "fr_mergulha"), (S_SAI - 1, "fr_barriga"), (S_SAI + S_VAI, "fr_barriga"),
                   (S_SAI + S_VAI + 8, "fr_levanta"), (S_SAI + S_VAI + 16, "parado")])
GOLPES["frigantus_escorregao"]["total"] = 9999
GOLPES["frigantus_avalanche"] = dict(dano=40, hit=40, defe=20, emp=6, nivel="medio", especial=True, ultimate=True,
                                     derruba=True, voo=(6, 8))
_registra("frigantus_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=avalanche, efeito=avalanche_efeito, ia="ultimate", quadros=[(0, "parado")])
GOLPES["frigantus_ultimate"]["total"] = 9999
GOLPES["frigantus_ult2_soco"] = dict(dano=G_DANO_SOCO, hit=40, defe=20, emp=6, nivel="medio", especial=True,
                                     ultimate=True, ultimate2=True)
_registra("frigantus_ult2", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          ultimate2=True, logica=era_do_gelo, efeito=era_do_gelo_efeito, ia="ultimate2",
          quadros=[(0, "parado"), (4, "fr_ruge"), (G_RUGE, "fr_ruge"), (G_RUGE + 6, "parado")])
GOLPES["frigantus_ult2"]["total"] = 9999

GOLPES_FRIGANTUS = {"E": "frigantus_neve", "Q": "frigantus_pisao", "R": "frigantus_bloco",
                    "SHIFT": "frigantus_escorregao", "Z": "frigantus_ultimate", "Z2": "frigantus_ult2"}


# =====================================================================
# Desenho (por código, em cima dos pontos da pose)
# =====================================================================
def desenhar_frigantus(l, tela, p, branco):
    s = l.s
    pelo, sombra, pele, gelo = _cor("m", PELO), _cor("M", PELO_SOMBRA), _cor("p", PELE), _cor("c", GELO)
    if branco:
        pelo = sombra = pele = gelo = (245, 245, 250)
    floresta = l.f.get("estilo") == "pegrande" and not branco  # PÉ-GRANDE: folhas e galhos no lugar do gelo
    pelo_tras = mistura(pelo, sombra, 0.45)
    pele_escura = mistura(pele, BORDA, 0.45)

    # GORILA: o corpo vai mais pra baixo (pernas curtas) e a cabeça fica enfiada entre os ombros, na frente
    D = max(0, min(12, (p["qd"][1] - 30) * 0.6))
    P = dict(p)
    for k in ("qd", "pc", "cb", "ct", "mt", "cf", "mf"):
        P[k] = (p[k][0], p[k][1] - D)
    for k in ("jt", "jf"):
        P[k] = (p[k][0] + 2, p[k][1] - D * 0.5)
    qd, pc = P["qd"], P["pc"]
    dx, dy = pc[0] - qd[0], pc[1] - qd[1]
    n = math.hypot(dx, dy) or 1
    tdir = (dx / n, dy / n)
    costas = (-tdir[1], tdir[0])  # pra cima/trás do tronco
    cab = (pc[0] + tdir[0] * 4 + 14, pc[1] + tdir[1] * 4 - 9)
    cb = entre(P["cb"], cab, 0.75)

    def Q(q):
        return l.ponto({"o": q}, "o")

    def elip(c, w, h, cor, borda=True):
        x, y = Q(c)
        if borda:
            pygame.draw.ellipse(tela, BORDA, (x - (w / 2 + 1.6) * s, y - (h / 2 + 1.6) * s, (w + 3.2) * s, (h + 3.2) * s))
        pygame.draw.ellipse(tela, cor, (x - w / 2 * s, y - h / 2 * s, w * s, h * s))

    def bola(c, r, cor, borda=True):
        if borda:
            pygame.draw.circle(tela, BORDA, Q(c), int((r + 1.6) * s))
        pygame.draw.circle(tela, cor, Q(c), int(r * s))

    def tubo(a, b, w1, w2, cor, pelos=False, so_borda=False):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        if not so_borda:
            pts = [(a[0] + nx * w1, a[1] + ny * w1), (b[0] + nx * w2, b[1] + ny * w2),
                   (b[0] - nx * w2, b[1] - ny * w2), (a[0] - nx * w1, a[1] - ny * w1)]
            pygame.draw.polygon(tela, BORDA, [Q((x + nx * 0, y)) for x, y in pts])
            pygame.draw.polygon(tela, BORDA, [Q(q) for q in pts], max(2, int(3.2 * s)))
            pygame.draw.circle(tela, BORDA, Q(a), int((w1 + 1.6) * s))
            pygame.draw.circle(tela, BORDA, Q(b), int((w2 + 1.6) * s))
        inner = [(a[0] + nx * (w1 - 1), a[1] + ny * (w1 - 1)), (b[0] + nx * (w2 - 1), b[1] + ny * (w2 - 1)),
                 (b[0] - nx * (w2 - 1), b[1] - ny * (w2 - 1)), (a[0] - nx * (w1 - 1), a[1] - ny * (w1 - 1))]
        pygame.draw.polygon(tela, cor, [Q(q) for q in inner])
        pygame.draw.circle(tela, cor, Q(a), int(w1 * s))
        pygame.draw.circle(tela, cor, Q(b), int(w2 * s))
        if pelos:  # tufinhos de pelo macios (pontas azuladas), dos dois lados
            for lado in (1,):
                for k in range(2):
                    c = entre(a, b, 0.3 + k * 0.4)
                    w = (w1 + (w2 - w1) * (0.3 + k * 0.4)) * lado
                    base1 = (c[0] + nx * w - dx / n * 2.4, c[1] + ny * w - dy / n * 2.4)
                    base2 = (c[0] + nx * w + dx / n * 2.4, c[1] + ny * w + dy / n * 2.4)
                    ponta = (c[0] + nx * (w + 2.6 * lado) - dx / n * 1.5, c[1] + ny * (w + 2.6 * lado) - dy / n * 1.5)
                    pygame.draw.polygon(tela, BORDA, [Q(base1), Q(ponta), Q(base2)], max(1, int(s)))
                    pygame.draw.polygon(tela, sombra, [Q(base1), Q(ponta), Q(base2)])

    def cristal(c, tam=3.2):  # pedacinho de gelo preso no pelo
        if floresta:  # folha e galho
            pygame.draw.line(tela, (90, 60, 30), Q((c[0] - tam, c[1])), Q((c[0] + tam, c[1] + tam * 0.6)), max(1, int(s)))
            elip((c[0] + 1, c[1] + tam * 0.4), tam * 1.2, tam * 0.7, (70, 120, 50), False)
            return
        pts = [(c[0] - tam, c[1]), (c[0] - tam * 0.2, c[1] + tam * 1.1), (c[0] + tam, c[1] + tam * 0.1),
               (c[0] + tam * 0.2, c[1] - tam * 0.9)]
        pygame.draw.polygon(tela, BORDA, [Q(q) for q in pts])
        pygame.draw.polygon(tela, gelo, [Q((q[0] * 0.75 + c[0] * 0.25, q[1] * 0.75 + c[1] * 0.25)) for q in pts])
        pygame.draw.circle(tela, (255, 255, 255), Q((c[0] - tam * 0.2, c[1] + tam * 0.3)), max(1, int(s * 0.8)))

    def braco(cot, mao, cor_pelo, ombro):
        c = P[cot]
        m = P[mao]
        m = (c[0] + (m[0] - c[0]) * 1.7, c[1] + (m[1] - c[1]) * 1.7)  # BRAÇOS COMPRIDOS (mais que as pernas)
        if m[1] < 9:
            m = (m[0], 9)  # apoia os nós dos dedos no chão
        tubo(ombro, c, 12, 10.5, cor_pelo, True)
        tubo(c, m, 10.5, 9, cor_pelo, True)  # antebraço grosso de gorila
        for a_, b_, w_ in ((ombro, c, 11), (c, m, 9.5)):  # a sombra azulada atrás do braço (destaca do corpo)
            dx_, dy_ = b_[0] - a_[0], b_[1] - a_[1]
            n_ = math.hypot(dx_, dy_) or 1
            off = (dy_ / n_ * w_ * 0.55, -dx_ / n_ * w_ * 0.55)
            if off[0] > 0:
                off = (-off[0], -off[1])
            pygame.draw.line(tela, sombra, Q((a_[0] + off[0], a_[1] + off[1])), Q((b_[0] + off[0], b_[1] + off[1])),
                             max(2, int(w_ * 0.5 * s)))
        cristal(entre(ombro, c, 0.45), 3)
        cristal(entre(c, m, 0.55), 2.6)
        # a MÃOZONA (punho fechado, nós dos dedos pra baixo/frente)
        bola(m, 11, pele)
        for k in (-1, 0, 1):
            a = (m[0] + 3 + k * 1.5, m[1] + k * 3.8)
            pygame.draw.line(tela, BORDA, Q(a), Q((a[0] + 8, a[1] - 0.5)), max(2, int(1.8 * s)))
        elip((m[0] - 2, m[1] + 3), 6, 4, mistura(pele, (255, 255, 255), 0.15), False)

    def perna(pe, joelho, cor_pelo):
        tubo(qd, P[joelho], 14, 12, cor_pelo, True)  # coxa curta e grossa, de pelo
        tubo(P[joelho], P[pe], 12, 9.5, cor_pelo, True)
        pe_c = (P[pe][0] + 6, P[pe][1] + 3.5)
        elip(pe_c, 30, 11, pele)  # o pezão escuro
        for k in range(3):
            pygame.draw.circle(tela, pele_escura, Q((pe_c[0] + 8 + k * 2.2, pe_c[1] - 1.5 + k * 0.4)), max(1, int(1.4 * s)))

    ombro_tras = (pc[0] - tdir[0] * 3 + costas[0] * 4, pc[1] - tdir[1] * 3 + costas[1] * 4)
    ombro_frente = (pc[0] + 2 - costas[0] * 2, pc[1] - costas[1] * 2)
    braco("ct", "mt", pelo_tras, ombro_tras)
    perna("pt", "jt", pelo_tras)
    # TRONCO: cintura fina, peito e ombros ENORMES, e a corcunda nas costas
    tubo((qd[0] - 1, qd[1] - 2), pc, 14, 25, pelo, True)
    corcunda = (qd[0] + dx * 0.78 + costas[0] * 11, qd[1] + dy * 0.78 + costas[1] * 11)
    bola(corcunda, 18, pelo)
    bola(pc, 23, pelo, False)  # (tapa a emenda)
    tubo((qd[0] - 1, qd[1] - 2), pc, 14, 25, pelo, False, True)
    for c in (entre(qd, corcunda, 0.55), corcunda, (corcunda[0] + costas[0] * 10 + tdir[0] * 6, corcunda[1] + costas[1] * 10 + tdir[1] * 6)):
        cristal((c[0] + costas[0] * 6, c[1] + costas[1] * 6), 3.4)
    # o peito (pele cinza aparecendo no meio do pelo) com as cicatrizes de garra
    peito = (qd[0] + dx * 0.62 - costas[0] * 13, qd[1] + dy * 0.62 - costas[1] * 13)
    elip(peito, 22, 28, mistura(pelo, pele, 0.4), False)
    for k in range(3):
        a = (peito[0] - 5 + k * 4, peito[1] + 7)
        b = (peito[0] - 1 + k * 4, peito[1] - 6)
        pygame.draw.line(tela, (150, 80, 90), Q(a), Q(b), max(1, int(1.4 * s)))
    perna("pf", "jf", pelo)
    # o colar de dentes (no pescoço curtinho)
    for k in range(5):
        c = entre((pc[0] - 2, pc[1] - 12), (cb[0] - 2, cb[1] - 14), k / 4)
        pygame.draw.polygon(tela, BORDA, [Q((c[0] - 2.2, c[1] + 0.8)), Q((c[0] + 2.2, c[1] + 0.8)), Q((c[0], c[1] - 5.5))])
        pygame.draw.polygon(tela, (240, 236, 220), [Q((c[0] - 1.4, c[1])), Q((c[0] + 1.4, c[1])), Q((c[0], c[1] - 4.2))])
    # a CABEÇA de gorila: crânio de pelo, cara cinza-escura, sobrancelhona, olhinhos fundos e focinho grande
    bola((cb[0] - 6, cb[1] + 5), 16, pelo)
    for k in range(3):  # o topo do crânio (crista de pelo)
        a = math.pi / 2 + 0.5 - k * 0.45
        base = (cb[0] - 6 + math.cos(a) * 15, cb[1] + 5 + math.sin(a) * 15)
        pygame.draw.polygon(tela, sombra, [Q((base[0] - 3, base[1])), Q((base[0] + math.cos(a) * 4.5, base[1] + math.sin(a) * 4.5)),
                                           Q((base[0] + 3, base[1]))])
    elip((cb[0] + 3, cb[1] - 1), 24, 26, pele)  # a cara
    abre = 6 if l.estado in ("ataque", "vitoria") else 0
    elip((cb[0] + 12, cb[1] - 9 - abre * 0.3), 20, 15 + abre, pele)  # o FOCINHO/mandíbula pra frente
    pygame.draw.circle(tela, BORDA, Q((cb[0] + 19, cb[1] - 4)), max(2, int(2 * s)))  # narinas
    pygame.draw.circle(tela, BORDA, Q((cb[0] + 15, cb[1] - 4)), max(2, int(2 * s)))
    if abre:  # a boca aberta (rugindo)
        elip((cb[0] + 13, cb[1] - 12 - abre * 0.3), 15, 5 + abre, (70, 16, 26))
        pygame.draw.line(tela, (245, 240, 225), Q((cb[0] + 7, cb[1] - 9)), Q((cb[0] + 20, cb[1] - 9)), max(2, int(2 * s)))
    else:  # a boca larga fechada
        pygame.draw.line(tela, BORDA, Q((cb[0] + 4, cb[1] - 12)), Q((cb[0] + 21, cb[1] - 11)), max(2, int(2.2 * s)))
    # a SOBRANCELHA grossa saliente (passa da cara pra frente)
    sob = [(cb[0] - 5, cb[1] + 8), (cb[0] + 17, cb[1] + 6.5), (cb[0] + 16, cb[1] + 1), (cb[0] - 5, cb[1] + 2)]
    pygame.draw.polygon(tela, BORDA, [Q(q) for q in sob])
    pygame.draw.polygon(tela, pele_escura, [Q((q[0] * 0.92 + (cb[0] + 6) * 0.08, q[1] * 0.8 + (cb[1] + 4.5) * 0.2)) for q in sob])
    for ox in (6, 13):  # os olhinhos fundos (na sombra da sobrancelha), com brilho gelado
        pygame.draw.circle(tela, (8, 8, 12), Q((cb[0] + ox, cb[1] - 1)), max(2, int(2.6 * s)))
        pygame.draw.circle(tela, (150, 220, 255), Q((cb[0] + ox + 0.6, cb[1] - 0.6)), max(1, int(1.1 * s)))
    braco("cf", "mf", pelo, ombro_frente)


def mistura(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    cb = P("cb")
    pygame.draw.circle(q, PELE, (int(cb[0] + 6 * s * d), int(cb[1] + 2 * s)), max(2, int(5 * s)))


# =====================================================================
# ENTRADA BASE: congelado num cubo de gelo... e quebra o gelo
# =====================================================================
E_QUEBRA = 56


def entrada(l, t, jogo):
    l.x, l.y = l.extra["entrada_x"], CHAO
    if t < E_QUEBRA:
        l.sobrepor = dict(POSES_FRIGANTUS["parado"])
        if t in (20, 34, 46):
            som.tocar("defesa", 0.5)
            jogo.tremer(3)
    elif t < DURACAO_ENTRADA - 10:
        if t == E_QUEBRA:
            som.tocar("quebra")
            som.tocar("uivo", 0.7)
            jogo.tremer(14)
            for _ in range(24):
                jogo.faiscas.append([l.x + random.uniform(-60, 60), l.y - random.uniform(10, 170), random.uniform(-7, 7),
                                     random.uniform(-8, 1), random.randint(24, 40), (200, 236, 255), 5])
        l.sobrepor = dict(POSES_FRIGANTUS["fr_ruge"])
    else:
        l.sobrepor = {}
    l.t += 1


def entrada_efeito(l, tela, t):
    if t >= E_QUEBRA:
        return
    w, h = 150 * l.s, 190 * l.s
    cubo = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
    cubo.fill((170, 225, 255, 150))
    pygame.draw.rect(cubo, (235, 250, 255, 230), cubo.get_rect(), 4)
    pygame.draw.line(cubo, (255, 255, 255, 200), (10, 14), (w * 0.4, 8), 4)
    tela.blit(cubo, (l.x - w / 2, CHAO - h))
    rnd = random.Random(2)
    for k in range(min(4, max(0, (t - 16) // 10))):  # as rachaduras
        cx, cy = l.x + rnd.uniform(-w / 3, w / 3), CHAO - rnd.uniform(h * 0.3, h * 0.8)
        for _ in range(4):
            a = rnd.uniform(0, math.tau)
            pygame.draw.line(tela, (255, 255, 255), (cx, cy), (cx + math.cos(a) * 34, cy + math.sin(a) * 34), 2)


# =====================================================================
# VITÓRIA BASE: TOPO DO MUNDO (sobe numa pedra de gelo e ruge pro céu, com neve caindo)
# =====================================================================
def vitoria(l, t, jogo):
    l.y = CHAO - 46 * l.s * suave(min(1, t / 16))
    l.vy = 0
    l.sobrepor = dict(POSES_FRIGANTUS["fr_ruge" if t > 16 else "andar2"])
    if t == 18:
        som.tocar("uivo", 0.7)
    if t % 3 == 0:
        jogo.faiscas.append([random.uniform(0, LARGURA), -10, random.uniform(-1, 1), random.uniform(1.5, 3), 120,
                             (250, 252, 255), 3])


def vitoria_efeito(l, tela, t):
    x = l.x
    pts = [(x - 70, CHAO + 4), (x - 50, CHAO - 50 * l.s), (x - 10, CHAO - 56 * l.s), (x + 40, CHAO - 50 * l.s),
           (x + 72, CHAO + 4)]
    pygame.draw.polygon(tela, (60, 90, 120), [(px, py + 3) for px, py in pts])
    pygame.draw.polygon(tela, (190, 228, 250), pts)
    pygame.draw.line(tela, (250, 255, 255), pts[1], pts[2], 3)


# =====================================================================
# PROVOCAÇÃO BASE: batida no peito
# =====================================================================
PROVOCA_QUADROS = [(0, "parado")] + [(6 + k * 6, "fr_peito_a" if k % 2 else "fr_peito_b") for k in range(10)] + \
                  [(PROVOCA_TEMPO, "parado")]
