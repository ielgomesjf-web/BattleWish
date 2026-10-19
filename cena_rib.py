"""CENAS DE ANIME do RIB (loja): a entrada CHUVA DE SHURIKENS e a vitória BAMBU (as duas com as ideias do Gomes).

ENTRADA: só o VULTO dele correndo num cenário que combina com o MAPA (floresta no pântano/selva, caverna no
deserto, telhados na cidade...), depois pulando de plataforma em plataforma, puxa as shurikens no ar, arremessa no
oponente (já no mapa de verdade) e cai numa POSE NINJA (agachado, mão no chão, braço pra trás).
VITÓRIA: KAWARIMI (puf, fica um tronco), ele aparece num BAMBUZAL como vulto de braços cruzados no alto de um bambu,
a câmera vai chegando... e termina num CLOSE da cara dele, colorida.
O Rib é sempre o desenho do jogo (vulto = o próprio desenho pintado de preto); só o close do rosto é ilustrado.
"""
import math
import random

import pygame

import cutscene
import rib
import ult2
from cena_max import para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

BORDA = (16, 24, 14)
VULTO = (10, 12, 16)
XR, XO = LARGURA * 0.3, LARGURA * 0.74  # o Rib e o oponente, no mapa
COR_NOME = (70, 150, 60)

POSE_NINJA = dict(  # a POSE NINJA do pouso (tipo o Greninja / o Homem-Aranha): bem baixo e inclinado pra frente,
    # a MÃO da frente apoiada no chão, o braço de trás erguido, a perna de trás esticada e o joelho da frente dobrado.
    # (montada com os comprimentos de osso do próprio Rib, por ângulo: os pés e a mão ficam no chão)
    qd=(0, 18.6), pc=(32.2, 45.6), cb=(41.4, 58.7),
    cf=(36.4, 22.0), mf=(36.4, 0.0), ct=(16.8, 64.0), mt=(-2.2, 75.0),
    jt=(-30.1, 7.7), pt=(-60.6, 2.3), jf=(29.7, 30.6), pf=(25.4, 0.0))


def pal(c):
    return {k: c.cor(k, v) for k, v in rib.PALETA.items()}


def pose(c, nome):
    if nome == "ninja":
        return dict(POSE_NINJA)
    return c.l.poses.get(nome) or c.l.poses["parado"]


def rib_por(c, base, p, x, y=CHAO, d=1):
    c.por(base, p, 1.0, x, y, d, guardar=False)


def vulto(c, q, p, escala, x, y, ang=0.0, cor=VULTO):
    """O Rib como VULTO (o desenho do jogo, todo pintado de uma cor só), com o pé em (x, y), girando ang graus."""
    img, pe = c.corpo(p, escala, guardar=False)
    img = img.copy()
    img.fill((*cor, 255), special_flags=pygame.BLEND_RGBA_MIN)
    if ang:
        r = img.get_bounding_rect()
        img = img.subsurface(r)
        cx, cy = r.centerx - pe[0], r.centery - pe[1]  # (o meio do corpo, em relação ao pé)
        img = pygame.transform.rotate(img, ang)
        q.blit(img, (int(x + cx - img.get_width() / 2), int(y + cy - img.get_height() / 2)))
        return
    q.blit(img, (int(x - pe[0]), int(y - pe[1])))


def folhas(q, t, n=14, semente=3, vel=1.0, cor=(90, 170, 60)):
    """Folhinhas voando com o vento."""
    w, h = q.get_size()
    rnd = random.Random(semente)
    for i in range(n):
        x = (rnd.uniform(0, w) + t * 6 * vel * rnd.uniform(0.6, 1.4)) % (w + 60) - 30
        y = (rnd.uniform(0, h) + math.sin(t * 0.08 + i) * 30 + t * 1.2) % h
        a = t * 0.15 + i
        pts = [(x + math.cos(a) * 9, y + math.sin(a) * 4), (x + math.cos(a + 2.4) * 4, y + math.sin(a + 2.4) * 4),
               (x - math.cos(a) * 9, y - math.sin(a) * 4), (x + math.cos(a - 2.4) * 4, y + math.sin(a - 2.4) * 4)]
        pygame.draw.polygon(q, cor if i % 3 else tuple(int(v * 0.7) for v in cor), pts)


# =====================================================================
# O CENÁRIO DO VULTO (combina com o mapa da luta)
# =====================================================================
TEMA_DO_MAPA = {"PÂNTANO": "floresta", "SELVA": "floresta", "VILA DOS SAPOS": "floresta",
                "CERCADO DO DESERTO": "caverna", "TOCA": "caverna", "LABORATÓRIO": "caverna",
                "MONTANHA NEVADA": "neve", "PRAIA DA ILHA": "praia", "NAVIO FANTASMA": "praia",
                "CAMPO DE BATALHA": "ruinas", "FERRO-VELHO": "ruinas"}  # (o resto: TELHADOS da cidade)
TEMAS = {  # céu (em cima, embaixo), névoa (as camadas de longe), astro
    "floresta": dict(ceu=((40, 70, 64), (196, 220, 150)), nevoa=(120, 160, 110), astro=(250, 240, 200)),
    "caverna": dict(ceu=((24, 18, 26), (120, 70, 50)), nevoa=(90, 56, 46), astro=None),
    "telhados": dict(ceu=((30, 26, 70), (250, 140, 90)), nevoa=(150, 90, 110), astro=(255, 236, 200)),
    "neve": dict(ceu=((70, 90, 140), (220, 230, 245)), nevoa=(170, 186, 214), astro=(255, 255, 240)),
    "praia": dict(ceu=((40, 60, 120), (255, 170, 110)), nevoa=(140, 120, 150), astro=(255, 220, 150)),
    "ruinas": dict(ceu=((50, 30, 30), (230, 120, 70)), nevoa=(140, 80, 66), astro=(255, 200, 140)),
}


def tema(c):
    return TEMA_DO_MAPA.get(c.cenario_nome, "telhados")


def mistura(a, b, k):
    return tuple(int(x + (y - x) * k) for x, y in zip(a, b))


def forma(q, nome, x, chao, alto, cor, rnd):
    """Uma coisa do cenário (árvore, estalagmite, prédio...) com a base em (x, chao)."""
    if nome == "floresta":  # árvore: tronco e a copa de bolotas
        pygame.draw.rect(q, cor, (x - alto * 0.05, chao - alto, alto * 0.1, alto))
        for i in range(5):
            pygame.draw.circle(q, cor, (int(x + rnd.uniform(-1, 1) * alto * 0.2), int(chao - alto + rnd.uniform(-0.1, 0.15) * alto)),
                               int(alto * rnd.uniform(0.16, 0.26)))
    elif nome == "neve":  # pinheiro
        for i in range(3):
            larg = alto * (0.34 - i * 0.08)
            yb = chao - alto * (0.15 + i * 0.25)
            pygame.draw.polygon(q, cor, [(x - larg, yb), (x + larg, yb), (x, yb - alto * 0.42)])
        pygame.draw.rect(q, cor, (x - alto * 0.03, chao - alto * 0.18, alto * 0.06, alto * 0.18))
    elif nome == "caverna":  # estalagmite (e uma estalactite em cima)
        pygame.draw.polygon(q, cor, [(x - alto * 0.18, chao), (x + alto * 0.18, chao), (x + alto * 0.03, chao - alto * 0.6),
                                     (x - alto * 0.04, chao - alto * 0.66)])
        pygame.draw.polygon(q, cor, [(x - alto * 0.14 + 30, -10), (x + alto * 0.14 + 30, -10), (x + 34, alto * 0.5)])
    elif nome == "praia":  # rocha e um coqueiro
        pygame.draw.ellipse(q, cor, (x - alto * 0.3, chao - alto * 0.3, alto * 0.6, alto * 0.5))
        if rnd.random() < 0.6:
            tronco_ = [(x + alto * 0.1 * math.sin(k * 1.2) + k * alto * 0.04, chao - alto * 0.2 - k * alto * 0.2) for k in range(5)]
            pygame.draw.lines(q, cor, False, tronco_, max(3, int(alto * 0.05)))
            tx, ty = tronco_[-1]
            for a in range(6):
                ang = -math.pi + a * math.pi / 5
                pygame.draw.line(q, cor, (tx, ty), (tx + math.cos(ang) * alto * 0.3, ty + math.sin(ang) * alto * 0.12 + alto * 0.08),
                                 max(2, int(alto * 0.04)))
    elif nome == "ruinas":  # coluna quebrada / muro
        larg = alto * 0.2
        topo = chao - alto * rnd.uniform(0.5, 1.0)
        pygame.draw.polygon(q, cor, [(x - larg / 2, chao), (x + larg / 2, chao), (x + larg / 2, topo + 10),
                                     (x + larg * 0.1, topo), (x - larg / 2, topo + 18)])
    else:  # telhados: prédio com o telhado de beiral curvado
        larg = alto * 0.6
        topo = chao - alto * 0.7
        pygame.draw.rect(q, cor, (x - larg / 2, topo, larg, alto * 0.7 + 4))
        pygame.draw.polygon(q, cor, [(x - larg * 0.75, topo + 6), (x - larg * 0.5, topo - alto * 0.12), (x + larg * 0.5, topo - alto * 0.12),
                                     (x + larg * 0.75, topo + 6)])


def camada(q, nome, scroll, par, cor, chao, alto, n, semente):
    """Uma CAMADA do fundo (parallax): as formas se repetem e andam mais devagar quanto mais longe."""
    w = q.get_width()
    vao = (w + 300) / n
    deslo = (scroll * par) % vao
    base = int(scroll * par // vao)
    for i in range(-1, n + 2):
        r2 = random.Random(semente * 1000 + base + i)
        x = i * vao - deslo + r2.uniform(-vao * 0.3, vao * 0.3)
        forma(q, nome, x, chao, alto * r2.uniform(0.8, 1.2), cor, r2)
    pygame.draw.rect(q, cor, (0, chao, w, q.get_height() - chao))


def cenario_vulto(c, q, scroll, t, perto=True):
    """O cenário inteiro em silhueta: céu, astro, 2 camadas de longe na névoa e a de perto (preta)."""
    w, h = q.get_size()
    nome = tema(c)
    T = TEMAS[nome]
    cutscene.degrade(q, (0, 0, w, h), *T["ceu"])
    if T["astro"]:
        brilho(q, (int(w * 0.66), int(h * 0.34)), 220, T["astro"], 90)
        pygame.draw.circle(q, T["astro"], (int(w * 0.66), int(h * 0.34)), 90)
    if nome == "caverna":  # a luz da boca da caverna lá no fundo
        brilho(q, (int(w * 0.7), int(h * 0.5)), 300, (255, 170, 110), 110)
    camada(q, nome, scroll, 0.15, mistura(T["nevoa"], T["ceu"][1], 0.35), int(h * 0.72), 260, 5, 1)
    camada(q, nome, scroll, 0.4, mistura(T["nevoa"], VULTO, 0.45), int(h * 0.78), 230, 6, 2)
    if perto:
        camada(q, nome, scroll, 1.0, VULTO, int(h * 0.86), 300, 3, 3)


def plataforma(q, nome, x, topo, chao):
    """Onde ele pisa no meio do pulo (galho, pedra, telhado...), em silhueta preta."""
    if nome in ("floresta", "neve"):  # o tronco e um GALHO saindo
        pygame.draw.rect(q, VULTO, (x + 30, topo - 260, 34, chao - topo + 260))
        pygame.draw.polygon(q, VULTO, [(x - 70, topo), (x + 40, topo - 8), (x + 40, topo + 14), (x - 70, topo + 6)])
        for i in range(3):
            pygame.draw.circle(q, VULTO, (int(x - 70 + i * 18), int(topo - 6)), 9)
    elif nome in ("caverna", "praia", "ruinas"):  # uma PEDRA alta (topo achatado)
        pygame.draw.polygon(q, VULTO, [(x - 60, chao), (x - 46, topo + 6), (x - 20, topo), (x + 30, topo + 2), (x + 54, topo + 12),
                                       (x + 70, chao)])
    else:  # um TELHADO
        pygame.draw.rect(q, VULTO, (x - 70, topo + 10, 140, chao - topo))
        pygame.draw.polygon(q, VULTO, [(x - 100, topo + 14), (x - 70, topo - 6), (x + 70, topo - 6), (x + 100, topo + 14)])


# =====================================================================
# ENTRADA: o VULTO correndo, pulando, as shurikens... e a POSE NINJA
# =====================================================================
VEL = 15        # a velocidade do cenário (px por quadro) enquanto ele corre
RX = 0.36       # onde ele fica na tela (ele parado, o mundo passando)
ESC_VULTO = 1.5
PULOS = ((0, 16, 0.86, 0.78), (16, 34, 0.78, 0.7), (34, 52, 0.7, 0.64))  # (de, até, altura de saída, altura de chegada)


def e1_corre(c, q, t, k):
    """1) O VULTO CORRENDO (o cenário passando em parallax, linhas de velocidade, a poeira dos passos)."""
    w, h = q.get_size()
    cenario_vulto(c, q, t * VEL, t)
    fase = t * 0.32
    p = misturar(pose(c, "r_corre1"), pose(c, "r_corre2"), (math.sin(fase) + 1) / 2)
    y = h * 0.86 - abs(math.sin(fase)) * 8
    vulto(c, q, p, ESC_VULTO, w * RX, y)
    cutscene.linhas_horizontais(q, (255, 255, 255), int(h * 0.2), int(h * 0.8), 14, t, velocidade=60, alfa=70)
    for i in range(4):  # a poeirinha dos passos
        u = (t * 2 + i * 9) % 36
        pygame.draw.circle(q, (60, 60, 64), (int(w * RX - 30 - u * 6), int(h * 0.86 - 4 - u * 0.6)), max(1, 8 - u // 5))


def e2_pula(c, q, t, k):
    """2) Começa a PULAR de plataforma em plataforma (galho, pedra, telhado...), com mortal no meio."""
    w, h = q.get_size()
    scroll = (56 + t) * VEL
    nome = tema(c)
    cenario_vulto(c, q, scroll, t, perto=False)
    chao = int(h * 0.86)
    for de, ate, y0, y1 in PULOS:  # as plataformas onde ele vai pousar (elas chegam da direita)
        x_mundo = (56 + ate) * VEL + w * RX
        plataforma(q, nome, x_mundo - scroll, h * y1, chao + 100)
    pygame.draw.rect(q, VULTO, (0, chao, w, h - chao))
    p, y, ang = pose(c, "pulo"), h * 0.86, 0.0
    for i, (de, ate, y0, y1) in enumerate(PULOS):
        if de <= t < ate:
            u = (t - de) / (ate - de)
            y = h * (y0 + (y1 - y0) * u) - math.sin(u * math.pi) * 80
            p = pose(c, "pulo") if u < 0.85 else misturar(pose(c, "pulo"), pose(c, "agachado"), (u - 0.85) / 0.15)
            ang = -360 * suave(u) if i == 1 else 0.0  # (o MORTAL no 2º pulo)
    if t >= PULOS[-1][1]:
        y = h * PULOS[-1][3]
        p = pose(c, "agachado")
    vulto(c, q, p, ESC_VULTO, w * RX, y, ang)
    cutscene.linhas_horizontais(q, (255, 255, 255), int(h * 0.15), int(h * 0.8), 10, t, velocidade=50, alfa=50)


def ceu_perto(c, q, t, scroll):
    """O céu do tema, com o astro grande atrás dele (pros planos no ar)."""
    w, h = q.get_size()
    nome = tema(c)
    T = TEMAS[nome]
    cutscene.degrade(q, (0, 0, w, h), *T["ceu"])
    if T["astro"]:
        brilho(q, (int(w * 0.6), int(h * 0.42)), 320, T["astro"], 100)
        pygame.draw.circle(q, T["astro"], (int(w * 0.6), int(h * 0.42)), 170)
    camada(q, nome, scroll, 0.4, mistura(T["nevoa"], VULTO, 0.5), int(h * 0.92), 200, 6, 2)


def e3_puxa(c, q, t, k):
    """3) NO AR, mais perto (câmera lenta): o vulto contra o céu PUXA as shurikens da cintura... elas BRILHAM."""
    w, h = q.get_size()
    ceu_perto(c, q, t, 900 + t * 2)
    x, y = w * 0.46, h * 0.95 - t * 1.0
    p = misturar(pose(c, "pulo"), pose(c, "r_arma"), suave(min(1, t / 10)))
    vulto(c, q, p, 1.7, x, y)
    mao = c.ponto(p, "mt", 1.7, x, y)
    if t >= 10:  # as SHURIKENS em leque na mão (prateadas, brilhando)
        for i in range(4):
            a = math.pi * 1.1 + i * 0.32
            sx, sy = mao[0] + math.cos(a) * 34, mao[1] + math.sin(a) * 34
            ult2.desenha_shuriken(q, sx, sy, 22, 0.4 + i * 0.3, brilha=150)
        f = max(0.0, 1 - abs(t - 18) / 6)
        if f > 0:  # o brilho correndo nelas (TCHING)
            pygame.draw.line(q, (255, 255, 255), (mao[0] - 90 * f, mao[1] - 40), (mao[0] + 90 * f, mao[1] - 40), 4)
            brilho(q, (int(mao[0]), int(mao[1] - 40)), int(40 * f) + 2, (220, 240, 255), 230)
    if t >= 14:
        texto_pow(q, "TCHING!", (int(w * 0.76), int(h * 0.24)), 50, (230, 240, 255), t - 14)


def e4_arremessa(c, q, t, k):
    """4) ARREMESSA: o vulto gira o braço e as shurikens SAEM voando com rastro (linhas de velocidade)."""
    w, h = q.get_size()
    ceu_perto(c, q, t, 960 + t * 2)
    cutscene.linhas_velocidade(q, (w * 0.3, h * 0.5), (255, 255, 255), n=30, r_dentro=240, grossura=4, semente=t // 2, alfa=90)
    x, y = w * 0.46, h * 0.95 - (32 + t) * 1.0
    p = misturar(pose(c, "r_arma"), pose(c, "r_arremesso"), suave(min(1, t / 4)))
    vulto(c, q, p, 1.7, x, y)
    mao = c.ponto(p, "mf", 1.7, x, y)
    for i in range(4):
        t0 = 3 + i * 2
        if t < t0:
            continue
        u = (t - t0) * 70
        a = 0.15 + i * 0.12
        sx, sy = mao[0] + math.cos(a) * u, mao[1] + math.sin(a) * u
        pygame.draw.line(q, (220, 236, 255), (mao[0] + math.cos(a) * max(0, u - 220), mao[1] + math.sin(a) * max(0, u - 220)),
                         (sx, sy), 5)
        ult2.desenha_shuriken(q, sx, sy, 26, t * 1.1 + i, brilha=150)
    if t >= 3:
        texto_pow(q, "SHING SHING!!", (int(w * 0.7), int(h * 0.2)), 52, (230, 240, 255), (t - 3) % 8, giro=-0.06)


SHURI = (-70, -34, 30, 66)  # onde elas fincam, em volta do pé do oponente


def e5_fincam(c, q, t, k):
    """5) No MAPA (colorido): as shurikens FINCAM em volta do oponente (TUC TUC TUC TUC). Ele se defende."""
    base = c._tela_aux()
    c.mapa(base, t + 60)
    c.por_oponente(base, "defesa" if t > 6 else "parado", 1.0, XO, CHAO)
    for i, dx in enumerate(SHURI):
        t0 = 2 + i * 4
        if t < t0:
            continue
        u = min(1, (t - t0) / 4)
        sx = XO + dx
        x, y = sx - (1 - u) * 180, CHAO - 12 - (1 - u) * 120
        if u < 1:
            pygame.draw.line(base, (220, 230, 245), (x - 90, y - 60), (x, y), 2)
        ult2.desenha_shuriken(base, x, y, 20, t * 0.9 if u < 1 else 0.6)
        if u >= 1 and t - t0 < 10:
            pygame.draw.circle(base, (240, 240, 250), (int(sx), int(CHAO - 2)), int(4 + (t - t0 - 4) * 3), 1)
        if t - t0 == 4:
            c.tremor = max(c.tremor, 4)
    c.mapa_frente(base, t + 60)
    centro, z = (XO - 10, CHAO - 80), 2.2
    c.camera(q, base, centro, z, pixel=True)
    for i, dx in enumerate(SHURI):
        t0 = 2 + i * 4 + 4
        if 0 <= t - t0 < 8:
            cx, cy = para_tela(centro, z, (XO + dx, CHAO - 30))
            texto_pow(q, "TUC!", (int(cx), int(cy - 70 - i * 10)), 40, (240, 240, 250), t - t0, giro=0.1 * (1 if i % 2 else -1))


def e6_pose(c, q, t, k):
    """6) Ele CAI do alto... e POUSA na POSE NINJA (mão no chão, braço pra trás), a poeira sobe, as folhas voam,
    os olhos brilham. O nome."""
    base = c._tela_aux()
    c.mapa(base, t + 90)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    for dx in SHURI:
        ult2.desenha_shuriken(base, XO + dx, CHAO - 12, 20, 0.6)
    cai = 12
    if t < cai:
        u = t / cai
        c.por(base, pose(c, "pulo"), 1.0, XR - 120 * (1 - u), CHAO - 300 * (1 - u) ** 1.5, 1, guardar=False)
    else:
        rib_por(c, base, pose(c, "ninja"), XR)
        if t - cai < 22:
            poeira(base, XR, CHAO, (t - cai) / 22, cor=(200, 196, 190), larg=120, semente=5)
            for i in range(8):  # as rachadinhas do impacto
                a = math.pi + i * math.pi / 7
                pygame.draw.line(base, (60, 50, 40), (XR + 20, CHAO), (XR + 20 + math.cos(a) * 30, CHAO + 2), 1)
    c.mapa_frente(base, t + 90)
    centro, z = (XR + 50, CHAO - 70), 2.4 - 0.3 * suave(min(1, max(0, t - cai) / 50))
    c.camera(q, base, centro, z, pixel=True)
    if t == cai:
        c.inverte, c.tremor = 2, 14
    folhas(q, t, 12)
    if t >= cai + 16:
        cb = c.ponto(pose(c, "ninja"), "cb", 1.0, XR, CHAO)
        ox, oy = para_tela(centro, z, (cb[0] + 4, cb[1] - 4))
        f = max(0.0, 1 - abs(t - cai - 22) / 6)
        if f > 0:
            pygame.draw.line(q, (255, 255, 230), (ox - 90 * f, oy), (ox + 90 * f, oy), 3)
            brilho(q, (int(ox), int(oy)), int(30 * f) + 2, pal(c)["y"], 220)
    if t >= cai + 24:
        faixa_nome(q, "RIB", "O SAPO NINJA.", COR_NOME, (t - cai - 24) / 30)


PLANOS = [
    (56, e1_corre, {0: ("vento", 0.6), 14: ("queda", 0.15), 28: ("queda", 0.15), 42: ("queda", 0.15)}),
    (56, e2_pula, {0: ("vento", 0.5), 16: ("queda", 0.3), 34: ("queda", 0.3), 52: ("queda", 0.3)}),
    (32, e3_puxa, {10: ("shuriken", 0.5), 16: ("blip", 0.5)}),
    (22, e4_arremessa, {3: ("shuriken", 0.6), 7: ("shuriken", 0.6)}),
    (24, e5_fincam, {6: ("soco", 0.3), 10: ("soco", 0.3), 14: ("soco", 0.3), 18: ("soco", 0.3)}),
    (80, e6_pose, {12: ("queda", 0.8), 34: ("shuriken", 0.4)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: KAWARIMI -> o BAMBUZAL -> o close colorido
# =====================================================================
def tronco(q, x, y, ang):
    """O TRONCO do Kawarimi (o que fica no lugar dele)."""
    sup = pygame.Surface((90, 40), pygame.SRCALPHA)
    pygame.draw.rect(sup, (60, 36, 20), (0, 4, 90, 32), border_radius=8)
    pygame.draw.rect(sup, (130, 86, 48), (2, 6, 86, 28), border_radius=7)
    for i in range(4):
        pygame.draw.line(sup, (96, 60, 32), (8 + i * 20, 10), (16 + i * 20, 30), 2)
    pygame.draw.ellipse(sup, (60, 36, 20), (70, 4, 20, 32))
    pygame.draw.ellipse(sup, (200, 160, 110), (73, 8, 14, 24))
    pygame.draw.ellipse(sup, (150, 110, 70), (77, 14, 6, 12), 1)
    sup = pygame.transform.rotate(sup, ang)
    q.blit(sup, (int(x - sup.get_width() / 2), int(y - sup.get_height() / 2)))


def v1_kawarimi(c, q, t, k):
    """1) No MAPA do lado do derrotado: o SELO DE MÃO... POOF! (fumaça) e no lugar dele cai um TRONCO."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO - 30, CHAO)
    puf = 20
    x = XR + 80
    if t < puf:
        p = misturar(pose(c, "parado"), pose(c, "r_selo"), suave(min(1, t / 8)))
        rib_por(c, base, p, x)
    else:
        u = t - puf
        cai = min(1, u / 8)
        tronco(base, x, CHAO - 80 + 62 * cai ** 2, 30 * (1 - cai))  # o TRONCO caindo no lugar dele
        if u < 26:  # a FUMAÇA do puf
            rnd = random.Random(4)
            sup = pygame.Surface(base.get_size(), pygame.SRCALPHA)
            for i in range(12):
                a = rnd.uniform(0, math.tau)
                d = (10 + u * 3) * rnd.uniform(0.4, 1)
                r = (16 + u * 1.4) * rnd.uniform(0.7, 1.2)
                pygame.draw.circle(sup, (236, 236, 240, max(0, 230 - u * 9)),
                                   (int(x + math.cos(a) * d), int(CHAO - 60 + math.sin(a) * d * 0.8)), int(r))
            base.blit(sup, (0, 0))
    c.mapa_frente(base, t)
    c.camera(q, base, (x + 60, CHAO - 80), 2.2, pixel=True)
    if puf <= t < puf + 14:
        texto_pow(q, "POOF!", (int(w * 0.36), int(h * 0.24)), 66, (240, 240, 250), t - puf)
    if t == puf:
        c.tremor = 6


def bambu_vulto(q, x, chao, alto, larg, cor, balanco, t):
    """Um BAMBU em silhueta (gomos e nós, curvando com o vento) e o tufo de folhas no alto. Devolve o topo."""
    n = 9
    pts = [(x + balanco * (i / n) ** 2, chao - alto * i / n) for i in range(n + 1)]
    pygame.draw.lines(q, cor, False, pts, max(1, int(larg)))
    for px, py in pts[1:-1]:
        pygame.draw.line(q, cor, (px - larg * 0.8, py), (px + larg * 0.8, py), max(2, int(larg * 0.3)))
    topo = pts[-1]
    for i in range(7):  # as folhas compridas
        a = -math.pi / 2 + (i - 3) * 0.45 + math.sin(t * 0.07 + i) * 0.08
        comp = larg * 7
        fx, fy = topo[0] + math.cos(a) * comp, topo[1] + math.sin(a) * comp * 0.5 + comp * 0.3
        pygame.draw.polygon(q, cor, [(topo[0], topo[1] + larg), (fx, fy), (topo[0] + math.cos(a) * comp * 0.4, topo[1] + larg * 2)])
    return topo


def bambuzal(c, q, t, foco, z):
    """O BAMBUZAL ao entardecer (céu laranja e roxo, o sol, 3 camadas de bambu balançando) com o VULTO dele
    de braços cruzados no alto do bambu do meio. foco/z = a câmera chegando."""
    w, h = q.get_size()
    fx, fy = foco

    def S(x, y):  # (o mundo -> a tela, com a câmera)
        return w / 2 + (x - fx) * z, h / 2 + (y - fy) * z

    cutscene.degrade(q, (0, 0, w, h), (54, 30, 80), (255, 150, 90))
    sx, sy = S(w * 0.66, h * 0.44)
    brilho(q, (int(sx), int(sy)), int(160 * z), (255, 220, 160), 120)
    pygame.draw.circle(q, (255, 226, 170), (int(sx), int(sy)), int(70 * z))
    for par, cor, n, larg, semente in ((0.3, (150, 80, 100), 14, 8, 1), (0.6, (90, 46, 70), 10, 12, 2), (1.0, VULTO, 6, 16, 3)):
        rnd = random.Random(semente)
        zz = 1 + (z - 1) * par
        for i in range(n):
            bx = (i + 0.5) * w / n + rnd.uniform(-20, 20)
            alto = h * rnd.uniform(0.7, 1.05)
            if par == 1.0 and abs(bx - w * 0.5) < w / n * 0.6:
                continue  # (o do meio é o dele)
            bx2 = w / 2 + (bx - fx) * zz
            balanco = math.sin(t * 0.04 + i) * 16 * zz
            bambu_vulto(q, bx2, h / 2 + (h + 40 - fy) * zz, alto * zz, larg * zz, cor, balanco, t)
    balanco = math.sin(t * 0.04 + 7) * 12 * z  # o bambu DELE (no meio) e ele em cima
    bx, chao = S(w * 0.5, h + 40)
    topo = bambu_vulto(q, bx, chao, h * 0.6 * z, 18 * z, VULTO, balanco, t)
    vulto(c, q, pose(c, "r_cruzado"), 1.25 * z, topo[0], topo[1] + 6 * z)
    return topo


def v2_bambuzal(c, q, t, k):
    """2) O BAMBUZAL: ele aparece como VULTO de braços cruzados no alto de um bambu... a câmera vai CHEGANDO."""
    w, h = q.get_size()
    z = 1 + 0.95 * suave(k) ** 1.4
    alvo = (w * 0.5, h * 0.4 + 40 - 120)  # (o meio do corpo dele, no topo do bambu)
    foco = (w * 0.5, h * 0.5 + (alvo[1] - h * 0.5) * suave(k))
    bambuzal(c, q, t, foco, z)
    folhas(q, t, 18, vel=1.4, cor=(40, 26, 40))
    if t < 10:  # (chegando do puf: um restinho de fumaça)
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        sup.fill((240, 240, 245, 220 - t * 22))
        q.blit(sup, (0, 0))


def rosto_close(c, q, w, h, t, luz):
    """O CLOSE NA CARA DELE, colorida (a luz do pôr do sol chegando): os olhos de gato, a bandana, o cachecol."""
    p = pal(c)
    cutscene.degrade(q, (0, 0, w, h), (54, 30, 80), (255, 150, 90))
    cx, cy = w * 0.5, h * 0.62
    cab = pygame.Rect(0, 0, 640, 470)  # a cabeça de sapo (larga)
    cab.center = (int(cx), int(cy))
    pygame.draw.ellipse(q, BORDA, cab.inflate(16, 16))
    pygame.draw.ellipse(q, p["g"], cab)
    pygame.draw.ellipse(q, p["G"], (cab.x + 60, cab.y + 30, cab.w * 0.55, cab.h * 0.32))
    for i in range(9):  # as manchinhas
        rnd = random.Random(i)
        pygame.draw.circle(q, p["d"], (int(cab.x + rnd.uniform(0.15, 0.85) * cab.w), int(cab.y + rnd.uniform(0.1, 0.5) * cab.h)),
                           int(rnd.uniform(8, 16)))
    band = pygame.Rect(cab.x - 10, cy + 10, cab.w + 20, cab.h * 0.5)  # a BANDANA cobrindo a boca
    pygame.draw.rect(q, BORDA, band.inflate(0, 14), border_radius=30)
    pygame.draw.rect(q, p["n"], band, border_radius=30)
    for i in range(5):
        pygame.draw.line(q, p["N"], (band.x + 80 + i * 110, band.y + 20), (band.x + 120 + i * 110, band.bottom), 7)
    for lado in (-1, 1):  # os OLHOS (bolas saltadas, amarelos com a pupila fininha)
        ox, oy = cx + lado * 190, cab.y + 40
        pygame.draw.circle(q, BORDA, (int(ox), int(oy)), 118)
        pygame.draw.circle(q, p["G"], (int(ox), int(oy)), 110)
        olho = pygame.Rect(0, 0, 180, 150)
        olho.center = (int(ox), int(oy + 10))
        pygame.draw.ellipse(q, BORDA, olho.inflate(12, 12))
        pygame.draw.ellipse(q, p["y"], olho)
        pygame.draw.ellipse(q, p["Y"], olho.inflate(-90, -76).move(-24, -20))
        pygame.draw.ellipse(q, (6, 6, 6), (ox - 12, oy - 60, 24, 140))
        pygame.draw.circle(q, (255, 255, 255), (int(ox - 40), int(oy - 26)), 13)
    cach = [(cx + 330, cy + 90), (cx + 420, cy + 60 + math.sin(t * 0.3) * 20), (cx + 520, cy + 90 + math.sin(t * 0.3 + 1) * 30),
            (cx + 620, cy + 70 + math.sin(t * 0.3 + 2) * 40)]  # o cachecol voando
    pygame.draw.lines(q, BORDA, False, cach, 60)
    pygame.draw.lines(q, (30, 30, 36), False, cach, 46)
    if luz < 1:  # (no começo ainda é vulto: a luz vai chegando, da esquerda pra direita)
        sombra = pygame.Surface((w, h), pygame.SRCALPHA)
        borda_luz = w * (luz * 1.4 - 0.2)
        for i in range(24):
            pygame.draw.rect(sombra, (*VULTO, min(255, 60 + i * 12)), (borda_luz + i * 20, 0, 22, h))
        pygame.draw.rect(sombra, (*VULTO, 255), (borda_luz + 480, 0, w, h))
        q.blit(sombra, (0, 0))


def v3_close(c, q, t, k):
    """3) CLOSE NA CARA DELE: a luz chega e mostra ele COLORIDO... os olhos brilham (SHING!). O nome."""
    w, h = q.get_size()
    luz = suave(min(1, t / 26))
    rosto_close(c, q, w, h, t, luz)
    folhas(q, t, 12, vel=1.4)
    if 28 <= t < 44:
        f = max(0.0, 1 - abs(t - 32) / 6)
        for lado in (-1, 1):
            ox, oy = w * 0.5 + lado * 190 + 30, h * 0.62 - 225
            pygame.draw.line(q, (255, 255, 255), (ox - 90 * f, oy), (ox + 90 * f, oy), 4)
        texto_pow(q, "SHING!", (int(w * 0.5), int(h * 0.12)), 56, (255, 255, 230), t - 28)
    if t >= 40:
        faixa_nome(q, "RIB", "VITÓRIA SILENCIOSA.", COR_NOME, (t - 40) / 30)


PLANOS_BAMBU = [
    (46, v1_kawarimi, {6: ("blip", 0.5), 20: ("puf", 0.9), 28: ("queda", 0.4)}),
    (90, v2_bambuzal, {0: ("vento", 0.6), 50: ("vento", 0.4)}),
    (96, v3_close, {28: ("shuriken", 0.6)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_BAMBU, titulo, oponente)
