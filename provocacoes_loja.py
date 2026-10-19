"""PROVOCAÇÕES DA LOJA (2 por lutador, escolhidas pelo Gomes). Cada uma tem a frase, o gesto e um desenho.
Duram PROVOCA_TEMPO quadros (dentro do golpe "provocar"). Tudo aqui é só visual, menos o que já é da provocação
(encher a barra no fim). Quando uma provocação mexe no visual do lutador (pose própria, some pra aparecer em outro
lugar), ela marca l.extra["prov_vis"] e o ult2.todo_quadro desfaz tudo se ele apanhar no meio.
"""
import math
import random

import pygame

import extras
import som
from config import *  # noqa: F401,F403
from golpes import proporcionar, suave
from max10 import brilho, fumaca

PRECO, PRECO_CAPRICHADA = 60, 80
T = PROVOCA_TEMPO

# poses de gente (servem pra quem tem o corpo normal)
SENTADO = dict(pt=(-4, 4), jt=(16, 18), pf=(8, 4), jf=(-14, 18), qd=(0, 16), pc=(2, 52), cb=(4, 70),
               ct=(-6, 38), mt=(6, 30), cf=(14, 38), mf=(22, 32))
PRANCHA = dict(pt=(-40, 2), jt=(-20, 7), pf=(-40, 0), jf=(-20, 6), qd=(0, 12), pc=(36, 20), cb=(52, 24),
               ct=(34, 10), mt=(36, 0), cf=(38, 10), mf=(40, 0))
PRANCHA_BAIXO = dict(PRANCHA, qd=(0, 8), pc=(36, 10), cb=(52, 12), ct=(26, 16), cf=(30, 16))
POSES_EXTRA = {"sentado": SENTADO, "prancha": PRANCHA, "prancha_baixo": PRANCHA_BAIXO}
proporcionar(POSES_EXTRA)


# ---- ajudantes ----
def pose(l):
    return l.pose_vista or l.pose_atual()


def ponto(l, k):
    return l.ponto(pose(l), k)


def alvo(l):
    """O adversário (na luta); na loja, um ponto de mentira na frente."""
    o = getattr(l, "_alvo_marujos", None)
    if o is not None and o is not l:
        return o.x, o.y, o.s
    return l.x + l.dir * 260, l.y, l.s


def usa_pose(l, nome_ou_dict):
    l.extra["prov_vis"] = True
    l.sobrepor = dict(POSES_EXTRA[nome_ou_dict] if isinstance(nome_ou_dict, str) else nome_ou_dict)


def solta(l):
    l.sobrepor = {}
    l.esconde = False
    l.extra.pop("prov_vis", None)
    l.extra.pop("lobo_some", None)


def fim_pose(l):
    if l.t >= T - 6:
        solta(l)
        return True
    return False


def sprite(l, pose_=None, escala=1.0):
    """O desenho DE VERDADE do lutador numa imagem separada (pra cortar em pedaços, fazer cópia, sumir...).
    Devolve (imagem, (x, y) do pé dele dentro da imagem)."""
    import pecas
    s = l.s * escala
    w, h = int(240 * s), int(220 * s)
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    guarda = l.x, l.y, l.s, l.angulo
    try:
        l.x, l.y, l.s, l.angulo = w / 2, h - 10 * s, s, 0
        pecas.usar_troca((l.disfarce or l.f).get("troca"))
        l.f["desenho"](l, sup, pose_ or l.pose_vista or l.pose_atual(), False)
    finally:
        pecas.usar_troca(None)
        l.x, l.y, l.s, l.angulo = guarda
    return sup, (w / 2, h - 10 * s)


def onda(k):
    return math.sin(k * math.pi)


def quadros(*q):
    return [(0, "parado")] + list(q) + [(T - 6, q[-1][1]), (T, "parado")]


# =====================================================================
# MAX-10
# =====================================================================
def max_escaneia_passo(l, jogo):
    if l.t == 8:
        som.tocar("laser", 0.25)
    if l.t == 56:
        som.tocar("blip", 0.5)


def max_escaneia(l, tela):
    t = l.t
    if not 8 <= t < 60:
        return
    ox, oy, os_ = alvo(l)
    k = (t - 8) / 46
    k = min(1, k)
    topo, base = oy - 130 * os_, oy
    y = topo + (base - topo) * k
    cb = ponto(l, "cb")
    olho = (cb[0] + l.dir * 6 * l.s, cb[1])
    larg = 40 * os_
    for dx in (-larg, larg):  # o laser: duas linhas finas do olho até a linha de varredura
        pygame.draw.line(tela, (255, 70, 50), olho, (ox + dx, y), 1)
    brilho(tela, (int(olho[0]), int(olho[1])), 10, (255, 60, 40), 220)
    grade = pygame.Surface((int(larg * 2 + 20), int(base - topo + 10)), pygame.SRCALPHA)
    gw, gh = grade.get_size()
    for i in range(0, gw, 8):  # a grade em cima dele (só onde já passou)
        pygame.draw.line(grade, (255, 80, 60, 70), (i, 0), (i, min(gh, y - topo)), 1)
    for j in range(0, int(min(gh, y - topo)), 8):
        pygame.draw.line(grade, (255, 80, 60, 70), (0, j), (gw, j), 1)
    tela.blit(grade, (ox - gw / 2, topo))
    brilho(tela, (int(ox), int(y)), int(larg), (255, 80, 60), 90)
    pygame.draw.line(tela, (255, 230, 220), (ox - larg, y), (ox + larg, y), 3)  # a linha de varredura
    for c in ((ox - larg - 6, topo - 6), (ox + larg + 6, topo - 6), (ox - larg - 6, base + 2), (ox + larg + 6, base + 2)):
        pygame.draw.circle(tela, (255, 80, 60), (int(c[0]), int(c[1])), 3, 1)  # os cantinhos da mira


def max_lanche_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(l.poses["parado"])
    cb = p["cb"]
    if l.t >= 14:  # a lata na boca (o braço sobe até a cabeça)
        p["cf"] = (cb[0] + 6, cb[1] - 14)
        p["mf"] = (cb[0] + 10, cb[1] + 2)
        p["cb"] = (cb[0] - 2, cb[1] + 2)
    usa_pose(l, p)
    if l.t == 20:
        som.tocar("lingua", 0.3)
    if l.t == 52:  # "AHH": um bafo de vapor
        fumaca(jogo, ponto(l, "cb")[0] + l.dir * 12, ponto(l, "cb")[1], 6, (230, 230, 236), 2, -1)
        som.tocar("puf", 0.4)


def max_lanche(l, tela):
    t = l.t
    mx, my = ponto(l, "mf")
    a = 0 if t < 18 else -min(1.6, (t - 18) / 12)  # vira a lata na boca
    w, h = 15 * l.s, 24 * l.s
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    c, s = math.cos(a * l.dir), math.sin(a * l.dir)
    lata = [(mx + x * c - y * s, my + x * s + y * c) for x, y in pts]
    pygame.draw.polygon(tela, (20, 20, 24), lata)
    pygame.draw.polygon(tela, (60, 120, 70), [(x + (mx - x) * 0.15, y + (my - y) * 0.15) for x, y in lata])
    pygame.draw.line(tela, (230, 200, 60), lata[0], lata[1], 2)
    pygame.draw.line(tela, (220, 220, 220), lata[2], lata[3], 2)
    if 24 <= t < 50 and t % 3 == 0:  # o óleo escorrendo
        cb = ponto(l, "cb")
        for i in range(2):
            pygame.draw.circle(tela, (30, 30, 20), (int(cb[0] + l.dir * 6 * l.s), int(cb[1] + 6 * l.s + i * 6 + (t % 6))), 2)


# =====================================================================
# RIB
# =====================================================================
def rib_medita_passo(l, jogo):
    if not fim_pose(l):
        usa_pose(l, "sentado")
    if l.t == 30:
        som.tocar("blip", 0.3)


def rib_medita(l, tela):
    t = l.t
    if 30 <= t < T - 6:  # o "Zzz" do bocejo
        from efeitos import texto
        cb = ponto(l, "cb")
        for i in range(3):
            k = ((t - 30) * 0.03 + i * 0.33) % 1
            texto(tela, "z", int(12 + i * 4), (220, 230, 255), (int(cb[0] - l.dir * (10 + k * 30)), int(cb[1] - 20 - k * 50)))


def rib_bunshin_passo(l, jogo):
    ox, oy, _ = alvo(l)
    if l.t == 6:
        fumaca(jogo, ox + l.dir * 85, oy - 40, 16, (235, 235, 245), 4, -1)
        som.tocar("puf", 0.5)
    if l.t == T - 10:
        fumaca(jogo, ox + l.dir * 85, oy - 40, 16, (235, 235, 245), 4, -1)
        som.tocar("puf", 0.5)


def rib_bunshin(l, tela):
    t = l.t
    if not 8 <= t < T - 10:
        return
    ox, oy, _ = alvo(l)
    p = l.poses.get("r_cruzado") or l.poses.get("r_selo") or l.poses["parado"]
    guarda = l.x, l.y, l.dir
    try:  # o clone do lado do ADVERSÁRIO (de braços cruzados, olhando pra ele)
        l.x, l.y, l.dir = ox + guarda[2] * 85, oy, -guarda[2]
        l.f["desenho"](l, tela, p, False)
    finally:
        l.x, l.y, l.dir = guarda


# =====================================================================
# TRAFO
# =====================================================================
def trafo_pulga_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(POSES_EXTRA["sentado"])  # sentado igual cachorro
    if 10 <= l.t < T - 10:  # a pata de trás coçando atrás da orelha (bem rápido)
        cb = p["cb"]
        p["pf"] = (cb[0] - 8 + (l.t % 4) * 4, cb[1] - 4 + (l.t % 3) * 4)
        p["jf"] = ((p["qd"][0] + p["pf"][0]) / 2 + 18, (p["qd"][1] + p["pf"][1]) / 2 + 8)
    usa_pose(l, p)


def trafo_pulga(l, tela):
    if 10 <= l.t < T - 10:
        cb = ponto(l, "cb")
        for i in range(3):  # os risquinhos do "coça-coça"
            a = -2.4 + i * 0.5
            pygame.draw.line(tela, (255, 255, 255), (cb[0] + math.cos(a) * 18, cb[1] + math.sin(a) * 18),
                             (cb[0] + math.cos(a) * 26, cb[1] + math.sin(a) * 26), 2)
        k = (l.t % 14) / 14  # a pulga pulando de um lado pro outro, na frente da cara
        ida = (l.t // 14) % 2
        x = cb[0] + l.dir * (30 + 26 * (k if ida else 1 - k))
        y = cb[1] + 4 - math.sin(k * math.pi) * 22
        pygame.draw.ellipse(tela, (20, 10, 6), (x - 6, y - 5, 12, 10))
        pygame.draw.ellipse(tela, (110, 60, 30), (x - 5, y - 4, 10, 8))
        for j in (-1, 1):
            pygame.draw.line(tela, (20, 10, 6), (x + j * 3, y + 3), (x + j * 7, y + 8), 2)


def trafo_olhos(l, tela):
    t = l.t
    if not 6 <= t < T - 6:
        return
    a, b = ponto(l, "mt"), ponto(l, "mf")
    cx, cy = (a[0] + b[0]) / 2 + l.dir * 14 * l.s, max(a[1], b[1])
    for i in range(3):  # 3 olhos extras no malabarismo (na frente do peito, abaixo do balão)
        k = ((t - 6) * 0.045 + i / 3) % 1
        x = cx + math.cos(k * math.tau) * 24 * l.s
        y = cy - 6 * l.s - abs(math.sin(k * math.pi)) * 34 * l.s
        pygame.draw.circle(tela, (20, 16, 10), (int(x), int(y)), int(11 * l.s))
        pygame.draw.circle(tela, (250, 245, 230), (int(x), int(y)), int(10 * l.s))
        pygame.draw.circle(tela, (230, 160, 30), (int(x + 2), int(y)), int(5 * l.s))
        pygame.draw.circle(tela, (10, 10, 10), (int(x + 2), int(y)), int(2.4 * l.s))
        pygame.draw.circle(tela, (255, 255, 255), (int(x - 2), int(y - 3)), 2)


# =====================================================================
# KING RIP
# =====================================================================
def cannan_pistola_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(l.poses.get("c_pistola") or l.poses["parado"])
    if l.t >= T - 22:  # assopra o cano e guarda no coldre
        p = dict(l.poses["parado"])
    usa_pose(l, p)
    if l.t % 10 == 0 and l.t < T - 22:
        som.tocar("vento", 0.2)
    if l.t == T - 22:
        som.tocar("defesa", 0.4)  # (CLEC no coldre)


def cannan_flexoes(l, tela):
    from efeitos import texto
    if not 8 <= l.t < T - 10:
        return
    n = (l.t - 8) // 12 + 1  # a contagem "1! 2! 3!..."
    k = ((l.t - 8) % 12) / 12
    cb = ponto(l, "cb")
    texto(tela, f"{n}!", int(22 + 8 * (1 - k)), (255, 230, 120), (int(cb[0] + l.dir * 60 * l.s), int(cb[1] - 10 * l.s - k * 20)))
    if (l.t // 5) % 2:  # gota de suor
        pygame.draw.circle(tela, (150, 210, 255), (int(cb[0] - l.dir * 8 * l.s), int(cb[1] - 6 * l.s + k * 10)), 3)


def finn_livro_passo(l, jogo):
    if fim_pose(l):
        return
    usa_pose(l, dict(l.poses.get("f_carrega") or l.poses["parado"]))
    if l.t % 10 == 0:
        som.tocar("vento", 0.15)  # (a página virando)


def king_cha_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(POSES_EXTRA["sentado"])
    gole = 22 <= l.t < 44  # (toma um GOLE: a xícara vai até a boca)
    if gole:
        cb = p["cb"]
        k = onda((l.t - 22) / 22)
        p["mf"] = (p["mf"][0] + (cb[0] + 8 - p["mf"][0]) * k, p["mf"][1] + (cb[1] - 6 - p["mf"][1]) * k)
        p["cf"] = (p["cf"][0] + 4 * k, p["cf"][1] + 10 * k)
    usa_pose(l, p)
    if l.t == 34:
        som.tocar("lingua", 0.25)
    if l.t == 48:  # "ahh..."
        cb = ponto(l, "cb")
        fumaca(jogo, cb[0] + l.dir * 14 * l.s, cb[1], 3, (240, 240, 245), 1, -0.6)


def king_cha(l, tela):
    s = l.s
    mx, my = ponto(l, "mf")
    mt = ponto(l, "mt")
    pires = pygame.Rect(0, 0, 30 * s, 6 * s)  # o PIRES na outra mão
    pires.center = (int(mt[0]), int(mt[1] - 2 * s))
    pygame.draw.ellipse(tela, (20, 18, 20), pires.inflate(4, 4))
    pygame.draw.ellipse(tela, (236, 236, 228), pires)
    pygame.draw.line(tela, (110, 160, 80), (pires.x + 6, pires.centery), (pires.right - 6, pires.centery), 1)
    x = pygame.Rect(0, 0, 20 * s, 15 * s)  # a XÍCARA (com alça e o chá verde)
    x.midbottom = (int(mx), int(my + 2 * s))
    alca = pygame.Rect(0, 0, 9 * s, 9 * s)
    alca.center = (x.right if l.dir > 0 else x.x, x.centery)
    pygame.draw.ellipse(tela, (20, 18, 20), alca, max(3, int(3 * s)))
    pygame.draw.ellipse(tela, (236, 236, 228), alca.inflate(-2, -2), max(1, int(1.6 * s)))
    pygame.draw.rect(tela, (20, 18, 20), x.inflate(4, 4), border_radius=int(5 * s))
    pygame.draw.rect(tela, (236, 236, 228), x, border_radius=int(5 * s))
    pygame.draw.rect(tela, (110, 170, 80), (x.x + 3, x.y + 2, x.w - 6, 4 * s), border_radius=2)
    pygame.draw.line(tela, (200, 60, 60), (x.x + 3, x.centery + 2), (x.right - 3, x.centery + 2), 2)  # a listra
    for i in range(3):  # o VAPOR subindo em curvinhas
        k = (l.t * 0.04 + i * 0.33) % 1
        vx = x.centerx + math.sin(k * 7 + i) * 6 * s
        vy = x.y - 4 - k * 34 * s
        pygame.draw.circle(tela, (240, 240, 248), (int(vx), int(vy)), max(2, int((3 - k * 2) * s)))


DANCA = ("k_gira", "k_estrela", "k_chute_alto", "k_bastao")


def king_danca_passo(l, jogo):
    from golpes import misturar
    if fim_pose(l):
        return
    i = (l.t // 9) % len(DANCA)
    j = (i + 1) % len(DANCA)
    k = suave(min(1, (l.t % 9) / 6))
    a = l.poses.get(DANCA[i]) or l.poses["vitoria"]
    b = l.poses.get(DANCA[j]) or l.poses["vitoria"]
    usa_pose(l, misturar(a, b, k))
    if l.t % 9 == 0:
        som.tocar("vento", 0.3)


def king_danca(l, tela):
    from efeitos import texto
    mx, my = ponto(l, "mf")
    a = l.t * 0.9
    for i in range(3):  # o borrão do nunchaku girando
        r = int((24 - i * 5) * l.s)
        pygame.draw.arc(tela, (255, 245, 210), (mx - r, my - r, 2 * r, 2 * r), a - i * 0.5, a - i * 0.5 + 1.7, 3 - i)
    for i in range(3):  # as notinhas de música
        k = (l.t * 0.03 + i * 0.33) % 1
        texto(tela, "♪♫"[i % 2], 22, (255, 230, 120), (int(l.x + (i - 1) * 46 * l.s + math.sin(k * 6) * 8),
                                                     int(l.y - 130 * l.s - k * 60)))


# =====================================================================
# CANNAN
# =====================================================================
def cannan_pistola(l, tela):
    t = l.t
    if t >= T - 22:
        return
    mx, my = ponto(l, "mt")  # (a pistola fica na mão de trás: a da frente é o canhão)
    a = t * 0.7 * l.dir
    e = l.s * 2.2
    for i in (2, 1):  # o rastro da pistola girando
        b = a - i * 0.5 * l.dir
        pygame.draw.arc(tela, (230, 230, 240), (mx - 16 * e, my - 16 * e, 32 * e, 32 * e), b, b + 0.6, 2)
    c, s = math.cos(a), math.sin(a)
    pts = [(-3, -2.4), (13, -2.4), (13, 1.6), (4, 1.6), (4.6, 8), (0, 8), (-1.4, 2), (-3, 2)]
    arma = [(mx + (x * c - y * s) * e, my + (x * s + y * c) * e) for x, y in pts]
    pygame.draw.polygon(tela, (12, 12, 14), arma)
    pygame.draw.polygon(tela, (60, 62, 70), [(x_ * 0.92 + mx * 0.08, y_ * 0.92 + my * 0.08) for x_, y_ in arma])
    pygame.draw.circle(tela, (180, 180, 190), (int(mx), int(my)), max(2, int(2 * e)))  # o dedo no gatilho
    if (t // 6) % 3 == 0:
        brilho(tela, (int(arma[1][0]), int(arma[1][1])), int(6 * e), (255, 255, 230), 160)


def cannan_flexoes_passo(l, jogo):
    if fim_pose(l):
        return
    baixo = 8 <= l.t < T - 10 and (l.t // 6) % 2 == 1
    usa_pose(l, "prancha_baixo" if baixo else "prancha")
    if 8 <= l.t < T - 10 and l.t % 12 == 6:
        som.tocar("pulo", 0.25)


# =====================================================================
# FINN
# =====================================================================
def finn_livro(l, tela):
    s = l.s
    a, b = ponto(l, "mt"), ponto(l, "mf")
    cx = (a[0] + b[0]) / 2 + l.dir * 10 * s
    cy = (a[1] + b[1]) / 2 - 10 * s - math.sin(l.t * 0.15) * 3 * s  # (flutuando um pouquinho)
    w, h = 64 * s, 40 * s
    brilho(tela, (int(cx), int(cy)), int(48 * s), (150, 110, 255), 90)
    pygame.draw.polygon(tela, (60, 30, 80), [(cx - w / 2 - 4, cy - h / 2 + 2), (cx + w / 2 + 4, cy - h / 2 + 2),
                                             (cx + w / 2 + 4, cy + h / 2 + 6), (cx - w / 2 - 4, cy + h / 2 + 6)])  # a capa
    for lado in (-1, 1):  # as 2 páginas abertas
        pag = [(cx, cy - h / 2 + 4), (cx + lado * w / 2, cy - h / 2), (cx + lado * w / 2, cy + h / 2),
               (cx, cy + h / 2 + 3)]
        pygame.draw.polygon(tela, (245, 238, 210), pag)
        pygame.draw.polygon(tela, (40, 24, 50), pag, 1)
        for i in range(4):
            y = cy - h / 3 + i * h / 6
            pygame.draw.line(tela, (150, 130, 110), (cx + lado * 5, y), (cx + lado * (w / 2 - 5), y - 1), 1)
    k = (l.t % 20) / 20  # a PÁGINA VIRANDO (vai de um lado pro outro)
    xv = cx + (w / 2) * math.cos(k * math.pi)
    pygame.draw.polygon(tela, (255, 250, 232), [(cx, cy - h / 2 + 4), (xv, cy - h / 2 - math.sin(k * math.pi) * 12 * s),
                                                (xv, cy + h / 2 - math.sin(k * math.pi) * 12 * s), (cx, cy + h / 2 + 3)])
    pygame.draw.line(tela, (40, 24, 50), (cx, cy - h / 2 + 4), (cx, cy + h / 2 + 3), 1)
    for i in range(4):  # as LETRAS MÁGICAS subindo do livro
        u = (l.t * 0.03 + i * 0.25) % 1
        lx = cx + (i - 1.5) * 14 * s + math.sin(u * 6 + i) * 6
        ly = cy - h / 2 - u * 60 * s
        cor = (190, 150, 255) if i % 2 else (255, 220, 120)
        pygame.draw.circle(tela, cor, (int(lx), int(ly)), max(2, int(3 * s * (1 - u))))
        pygame.draw.line(tela, cor, (lx - 4, ly), (lx + 4, ly), 1)


def finn_fogos_passo(l, jogo):
    if l.t in (10, 18, 26):
        som.tocar("explosao", 0.25)


def finn_fogos(l, tela):
    t = l.t
    topo = ponto(l, "mf")
    cx, cy = l.x + l.dir * 40 * l.s, l.y - 230 * l.s
    for i, t0 in enumerate((6, 14, 22)):
        u = t - t0
        if 0 <= u < 10:  # subindo
            k = u / 10
            pygame.draw.circle(tela, (255, 230, 150), (int(topo[0] + (cx - topo[0]) * k), int(topo[1] + (cy - topo[1]) * k)), 3)
    if t >= 32:  # a carinha rindo no céu (feita de faíscas coloridas)
        k = min(1, (t - 32) / 8)
        cores = ((255, 90, 90), (255, 230, 90), (120, 220, 255), (200, 120, 255))
        pts = []
        for i in range(14):  # o rosto
            a = i * math.tau / 14
            pts.append((cx + math.cos(a) * 46 * k, cy + math.sin(a) * 46 * k))
        for i in range(7):  # o sorriso
            a = 0.3 + i * 0.4
            pts.append((cx + math.cos(a) * 26 * k, cy + math.sin(a) * 22 * k))
        pts += [(cx - 16 * k, cy - 14 * k), (cx + 16 * k, cy - 14 * k)]  # os olhos
        for i, (x, y) in enumerate(pts):
            brilho(tela, (int(x), int(y)), 7, cores[i % 4], 140)
            pygame.draw.circle(tela, cores[i % 4], (int(x), int(y)), 2)


# =====================================================================
# KUN
# =====================================================================
def kun_castelo(l, tela):
    import kun
    t = l.t
    base_x, base_y = l.x + l.dir * 46 * l.s, l.y
    monta = min(1.0, t / 40)
    if t < 46:  # montando (andar por andar)
        n = int(monta * 6)
        pos = [(0, 0), (12, 0), (24, 0), (6, 1), (18, 1), (12, 2)]
        for i, (dx, andar) in enumerate(pos[:n]):
            x = base_x + (dx - 12) * l.s
            y = base_y - (8 + andar * 15) * l.s
            for lado in (-0.35, 0.35):
                kun.carta(tela, (x + lado * 8 * l.s, y), lado, 1.3 * l.s / 1.36, 1, l=l)
    else:  # SOPROU: desaba tudo
        u = t - 46
        for i in range(12):
            a = i * 0.5
            x = base_x + math.cos(a) * u * 4 * l.s + l.dir * u * 2
            y = base_y - 30 * l.s + u * u * 0.25 - math.sin(a) * 10
            kun.carta(tela, (x, min(base_y - 4, y)), u * 0.3 + i, 1.3 * l.s / 1.36, 1, l=l)


def kun_truco(l, tela):
    import kun
    t = l.t
    ox, oy, os_ = alvo(l)
    mx, my = ponto(l, "mf")
    ordem = [1, 0, 1, 1, 0, 0]  # 1 pra você, 1 pra mim, 2 pra você, 2 pra mim
    for i, pra_ele in enumerate(ordem):
        u = t - (8 + i * 8)
        if u < 0:
            continue
        k = min(1, u / 10)
        dx = (ox - mx) * 0.55 if pra_ele else -l.dir * 30 * l.s
        x = mx + dx * k + (i % 2) * 8
        y = my - math.sin(k * math.pi) * 50 - k * 10 + (i // 2) * 3
        kun.carta(tela, (x, y), (1 - k) * 4 + i * 0.1, 1.4 * l.s / 1.36, 1 if k > 0.5 else -1, l=l)


# =====================================================================
# TROMOS
# =====================================================================
def xeno_teto_passo(l, jogo):
    if fim_pose(l):
        return
    l.extra["prov_vis"] = True
    l.esconde = 8 <= l.t < T - 8


def xeno_teto(l, tela):
    t = l.t
    if not 8 <= t < T - 8:
        return
    k = suave(min(1, (t - 8) / 12)) * (1 - suave(max(0, (t - T + 20) / 12)))
    guarda = l.x, l.y, l.angulo
    try:  # pendurado de cabeça pra baixo lá em cima, olhando pro adversário
        l.y = CHAO - 300 * k
        l.angulo = math.pi * k
        l.f["desenho"](l, tela, l.poses.get("x_salto") or l.poses["parado"], False)
    finally:
        l.x, l.y, l.angulo = guarda
    if k > 0.9:  # a "parede invisível" que ele subiu: só os arranhões
        pygame.draw.line(tela, (120, 255, 120), (l.x - 20, CHAO - 280), (l.x - 14, CHAO - 250), 1)


def chafariz_topo(l):
    cb = ponto(l, "cb")
    return cb[0] + l.dir * 40 * l.s, cb[1] - 90 * l.s


def xeno_chafariz(l, tela):
    t = l.t
    if not 10 <= t < T - 6:
        return
    s = l.s
    cb = ponto(l, "cb")
    boca = (cb[0] + l.dir * 14 * s, cb[1])
    poca_x = l.x + l.dir * 90 * s
    forte = min(1, (t - 10) / 8) * (1 - max(0, (t - (T - 14)) / 8))
    pts = []  # o JATO de ácido em arco (sobe da boca e cai na poça)
    for i in range(16):
        k = i / 15
        x = boca[0] + (poca_x - boca[0]) * k
        y = boca[1] + (CHAO - boca[1]) * k * k - math.sin(k * math.pi) * 90 * s * forte
        pts.append((x + math.sin(t * 0.6 + i) * 2, y))
    if forte > 0.05:
        pygame.draw.lines(tela, (30, 60, 10), False, pts, max(4, int(8 * s * forte)))
        pygame.draw.lines(tela, (150, 240, 60), False, pts, max(2, int(5 * s * forte)))
        pygame.draw.lines(tela, (230, 255, 180), False, pts[:10], 1)
        brilho(tela, (int(pts[7][0]), int(pts[7][1])), int(26 * s), (150, 255, 80), 90)
    cresce = min(1, (t - 14) / 30)  # a POÇA borbulhando
    if cresce > 0:
        w = 70 * s * cresce
        pygame.draw.ellipse(tela, (30, 60, 10), (poca_x - w / 2 - 2, CHAO - 6, w + 4, 12))
        pygame.draw.ellipse(tela, (120, 210, 50), (poca_x - w / 2, CHAO - 5, w, 9))
        for i in range(4):
            u = (t + i * 7) % 14
            bx = poca_x + (i - 1.5) * w / 5
            pygame.draw.circle(tela, (200, 255, 140), (int(bx), int(CHAO - 2 - u * 0.8)), max(1, 3 - u // 5), 1)


def tai_sal(l, tela):
    if not 12 <= l.t < 46:
        return
    mx, my = ponto(l, "mf")
    k = (l.t - 12) / 34
    for i in range(6):  # o brilho do sal no ar (estrelinhas)
        a = i * 1.1 + l.t * 0.1
        x = mx + math.cos(a) * 50 * l.s * k + l.dir * 10
        y = my - 70 * l.s * math.sin(k * math.pi) + math.sin(a) * 20
        tam = 6 * (1 - k)
        if tam > 1:
            pygame.draw.line(tela, (255, 255, 255), (x - tam, y), (x + tam, y), 2)
            pygame.draw.line(tela, (255, 255, 255), (x, y - tam), (x, y + tam), 2)


def tamer_selfie_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(l.poses.get("t_aponta") or l.poses["parado"])
    cb = p["cb"]
    p["mf"] = (cb[0] + 26, cb[1] + 14)  # o celular esticado na frente, virado pra ele
    p["cf"] = (cb[0] + 14, cb[1] - 6)
    usa_pose(l, p)
    if l.t == 34:
        som.tocar("blip", 0.8)  # CLIC!


def xeno_chafariz_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(l.poses.get("x_vitoria") or l.poses["parado"])
    usa_pose(l, p)
    if 10 <= l.t < T - 12 and l.t % 3 == 0:  # as gotas espirrando de cima do jato
        x, y = chafariz_topo(l)
        jogo.faiscas.append([x, y, random.uniform(-2.5, 2.5), random.uniform(-3, -1), 26, (170, 250, 80), 3])
    if l.t == 10:
        som.tocar("lingua", 0.5)
    if 20 <= l.t < T - 12 and l.t % 10 == 0:
        som.tocar("puf", 0.15)  # (o chiado da poça)


# =====================================================================
# TAI
# =====================================================================
def tai_sal_passo(l, jogo):
    if fim_pose(l):
        return
    usa_pose(l, dict(l.poses.get("t_sal") or l.poses["parado"]))
    if l.t == 12:
        som.tocar("vento", 0.6)
        mx, my = ponto(l, "mf")
        for i in range(34):  # o SAL voando alto em leque... e caindo devagar
            a = -math.pi / 2 + (i / 33 - 0.5) * 1.6 + l.dir * 0.2
            v = 6 + (i % 5)
            jogo.faiscas.append([mx, my, math.cos(a) * v * 0.6, math.sin(a) * v, 56, (255, 255, 255), 4])


def tai_lanche_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(POSES_EXTRA["sentado"])
    if 10 <= l.t < T - 10 and (l.t // 8) % 2:  # o hashi vai até a boca
        cb = p["cb"]
        p["mf"] = (cb[0] + 10, cb[1] - 8)
        p["cf"] = (p["cf"][0] + 4, p["cf"][1] + 10)
    usa_pose(l, p)
    if 10 <= l.t < T - 10 and l.t % 16 == 8:
        som.tocar("lingua", 0.2)


def tai_lanche(l, tela):
    from efeitos import texto
    s = l.s
    a, b = ponto(l, "mt"), ponto(l, "mf")
    tig = pygame.Rect(0, 0, 34 * s, 16 * s)  # a TIGELA grandona de arroz
    tig.midtop = (int(a[0]), int(a[1] - 6 * s))
    pygame.draw.ellipse(tela, (250, 250, 245), (tig.x + 3, tig.y - 8 * s, tig.w - 6, 14 * s))  # o arroz
    for i in range(5):
        pygame.draw.circle(tela, (225, 225, 220), (int(tig.x + 6 + i * tig.w / 6), int(tig.y - 2 * s)), 2)
    pygame.draw.ellipse(tela, (20, 16, 14), tig.inflate(4, 4))
    pygame.draw.ellipse(tela, (190, 60, 50), tig)
    pygame.draw.arc(tela, (250, 220, 120), tig.inflate(-6, -4), 3.4, 6.0, 2)  # o desenho dourado
    for o in (0, 3):  # os HASHIS (com um bolinho de arroz na ponta)
        pygame.draw.line(tela, (20, 16, 14), (b[0] - l.dir * 4 * s, b[1] + o), (b[0] + l.dir * 22 * s, b[1] - 10 * s + o), 4)
        pygame.draw.line(tela, (190, 140, 80), (b[0] - l.dir * 4 * s, b[1] + o), (b[0] + l.dir * 22 * s, b[1] - 10 * s + o), 2)
    pygame.draw.circle(tela, (250, 250, 245), (int(b[0] + l.dir * 22 * s), int(b[1] - 9 * s)), max(2, int(3 * s)))
    if 10 <= l.t < T - 10 and (l.t // 8) % 2:
        cb = ponto(l, "cb")
        texto(tela, "nhom!", 15, (255, 240, 200), (int(cb[0] - l.dir * 30 * s), int(cb[1] - 20 * s)))


# =====================================================================
# TAMER
# =====================================================================
def tamer_busca_passo(l, jogo):
    l.extra["prov_vis"] = True
    l.extra["lobo_some"] = 10 <= l.t < T - 6
    if l.t == 8:
        som.tocar("vento", 0.4)
    if l.t >= T - 6:
        solta(l)


def tamer_busca(l, tela):
    import tamer
    t = l.t
    esc = l.s / tamer.S_REF
    lobo_x = l.extra.get("lobo_x", l.x - l.dir * 46)
    longe = l.x + l.dir * 380
    if 8 <= t < 30:  # o graveto voando
        k = (t - 8) / 22
        x = l.x + (longe - l.x) * k
        y = l.y - 90 * l.s - math.sin(k * math.pi) * 110
        pygame.draw.line(tela, (110, 76, 40), (x - 8, y - 3), (x + 8, y + 3), 4)
    if 10 <= t < T - 6:  # o lobo corre buscar e volta com o graveto na boca
        ida = suave(min(1, (t - 10) / 22))
        volta = suave(max(0, (t - 36) / 22))
        x = lobo_x + (longe - lobo_x) * ida - (longe - lobo_x) * volta
        d = l.dir if volta == 0 else -l.dir
        tamer.desenha_lobo(tela, x, l.y, esc, d, "corre", t * 2, tamer.cor_lobo(l), tamer.skin_lobo(l))
        if t >= 32:
            pygame.draw.line(tela, (110, 76, 40), (x + d * 26 * l.s, l.y - 40 * l.s), (x + d * 44 * l.s, l.y - 36 * l.s), 4)


def tamer_selfie(l, tela):
    t = l.t
    s = l.s
    mx, my = ponto(l, "mf")
    cel = pygame.Rect(0, 0, 14 * s, 24 * s)  # o CELULAR grandão
    cel.center = (int(mx), int(my - 8 * s))
    pygame.draw.rect(tela, (16, 16, 20), cel.inflate(4, 4), border_radius=4)
    pygame.draw.rect(tela, (40, 40, 48), cel, border_radius=3)
    tela_cel = cel.inflate(-4, -6)
    pygame.draw.rect(tela, (90, 170, 230) if t < 34 else (250, 250, 255), tela_cel, border_radius=2)
    pygame.draw.circle(tela, (16, 16, 20), (cel.centerx, cel.y + 3), 1)
    if 34 <= t < 40:  # FLASH!
        brilho(tela, cel.center, int(140 * s), (255, 255, 255), 240)
    if t >= 40:  # a FOTO saindo e flutuando (ele + o lobo fazendo careta)
        k = min(1, (t - 40) / 10)
        fx, fy = cel.centerx - l.dir * 40 * s * k, cel.y - 40 * s * k
        foto = pygame.Rect(0, 0, 34 * s, 30 * s)
        foto.center = (int(fx), int(fy))
        pygame.draw.rect(tela, (20, 20, 24), foto.inflate(4, 4))
        pygame.draw.rect(tela, (250, 250, 245), foto)
        dentro = foto.inflate(-6, -10).move(0, -2)
        pygame.draw.rect(tela, (140, 200, 230), dentro)
        pygame.draw.circle(tela, (200, 160, 110), (dentro.x + dentro.w // 3, dentro.centery + 2), max(2, int(5 * s)))
        pygame.draw.circle(tela, (240, 240, 245), (dentro.right - dentro.w // 3, dentro.centery + 3), max(2, int(5 * s)))
        pygame.draw.line(tela, (30, 30, 30), (dentro.x + dentro.w // 3 - 2, dentro.centery + 4),
                         (dentro.x + dentro.w // 3 + 2, dentro.centery + 4), 1)  # (o sorriso)


# =====================================================================
# JOHN
# =====================================================================
def pomba(tela, x, y, t, d):
    asa = math.sin(t * 0.8) * 8
    pygame.draw.ellipse(tela, (20, 20, 24), (x - 9, y - 5, 18, 10))
    pygame.draw.ellipse(tela, (250, 250, 250), (x - 8, y - 4, 16, 8))
    pygame.draw.polygon(tela, (240, 240, 245), [(x - 2, y - 2), (x - 10, y - 10 - asa), (x + 4, y - 3)])
    pygame.draw.circle(tela, (250, 250, 250), (int(x + d * 8), int(y - 4)), 4)
    pygame.draw.polygon(tela, (240, 170, 60), [(x + d * 11, y - 5), (x + d * 15, y - 4), (x + d * 11, y - 3)])


def john_pombas_passo(l, jogo):
    if l.t == 14:
        som.tocar("puf", 0.5)


def john_pombas(l, tela):
    t = l.t
    if t < 14:
        return
    mx, my = ponto(l, "mf")
    for i in range(5):
        u = t - 14 - i * 3
        if u < 0:
            continue
        x = mx + (i - 2) * 14 + math.sin(u * 0.2 + i) * 10 + l.dir * u * 2
        y = my - u * 4.5 - i * 4
        pomba(tela, x, y, u + i, l.dir)  # (as pombas)


def john_flores(l, tela):
    s = l.s
    mx, my = ponto(l, "mf")
    k = min(1, max(0, (l.t - 10) / 8))
    if k <= 0:
        return
    if 10 <= l.t < 18:  # o PUF da mágica
        brilho(tela, (int(mx), int(my)), int(30 * s * (1 - k) + 6), (255, 240, 200), 200)
    bx, by = mx + l.dir * 6 * s, my - 4 * s
    cone = [(bx, by + 4 * s), (bx + l.dir * 16 * s * k, by - 26 * s * k), (bx + l.dir * 30 * s * k, by - 12 * s * k)]
    pygame.draw.polygon(tela, (20, 16, 20), cone)
    pygame.draw.polygon(tela, (240, 230, 250), [(x * 0.9 + bx * 0.1, y * 0.9 + by * 0.1) for x, y in cone])  # o papel
    cores = ((255, 90, 120), (255, 220, 80), (200, 120, 255), (255, 150, 60), (120, 200, 255))
    for i in range(6):  # o BUQUÊ (6 flores)
        fx = bx + l.dir * (14 + (i % 3) * 8) * s * k
        fy = by - (24 + (i // 3) * 10 - (i % 3) * 3) * s * k
        r = int(6 * s * k)
        if r < 1:
            continue
        for p in range(5):
            a = p * 1.26 + l.t * 0.02
            pygame.draw.circle(tela, cores[i % 5], (int(fx + math.cos(a) * r * 0.8), int(fy + math.sin(a) * r * 0.8)), max(1, r // 2 + 1))
        pygame.draw.circle(tela, (255, 250, 220), (int(fx), int(fy)), max(1, r // 3))
    if l.t > 20 and (l.t // 6) % 2:  # brilhinho
        brilho(tela, (int(bx + l.dir * 20 * s), int(by - 30 * s)), int(10 * s), (255, 255, 255), 200)


# =====================================================================
# CRÁQUEN
# =====================================================================
def dente(tela, x, y, e, ang=0.0):
    pts = [(-3, -4), (3, -4), (2, 2), (0, 7), (-2, 2)]
    c, s = math.cos(ang), math.sin(ang)
    tp = [(x + (px * c - py * s) * e, y + (px * s + py * c) * e) for px, py in pts]
    pygame.draw.polygon(tela, (40, 30, 30), tp)
    pygame.draw.polygon(tela, (250, 250, 236), [(px * 0.85 + x * 0.15, py * 0.85 + y * 0.15) for px, py in tp])


def frig_picole_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(l.poses.get("fr_peito_a") or l.poses["parado"])
    if 12 <= l.t < T - 10:  # o picolé vai na boca (lambida) e volta
        cb = p["cb"]
        k = onda(((l.t - 12) % 16) / 16)
        p["mf"] = (p["mf"][0] + (cb[0] + 14 - p["mf"][0]) * k, p["mf"][1] + (cb[1] - 10 - p["mf"][1]) * k)
    usa_pose(l, p)
    if 12 <= l.t < T - 10 and (l.t - 12) % 16 == 8:
        som.tocar("lingua", 0.25)


def craquen_papagaio_passo(l, jogo):
    if fim_pose(l):
        return
    usa_pose(l, dict(l.poses.get("q_ri") or l.poses["parado"]))
    if l.t in (30, 42):
        som.tocar("blip", 0.6)  # (o papagaio grasnando "FRACO!")


def craquen_papagaio(l, tela):
    from efeitos import texto
    t = l.t
    s = l.s
    ombro = ponto(l, "pc")
    pousa = (ombro[0] - l.dir * 2 * s, ombro[1] - 18 * s)
    if t < 22:  # chegando voando (em curva)
        k = suave(t / 22)
        x = pousa[0] - l.dir * 160 * s * (1 - k)
        y = pousa[1] - 110 * s * (1 - k) + math.sin(k * math.pi) * 30 * s
    else:
        x, y = pousa
    e = 1.9 * s / 1.36
    sup = pygame.Surface((int(60 * e), int(60 * e)), pygame.SRCALPHA)
    cx, cy = 26 * e, 30 * e
    voando = t < 22 or 28 <= t < 34
    asa = math.sin(t * 0.9) * 12 * e if voando else 0
    cab = 0 if t < 22 else math.sin(t * 0.5) * 2 * e  # (balançando a cabeça)
    fantasma = (120, 240, 200, 170)
    pygame.draw.polygon(sup, (70, 180, 150, 160), [(cx - 8 * e, cy + 8 * e), (cx - 22 * e, cy + 24 * e),
                                                   (cx - 12 * e, cy + 24 * e), (cx - 2 * e, cy + 10 * e)])  # o rabo comprido
    pygame.draw.ellipse(sup, fantasma, (cx - 10 * e, cy - 8 * e, 22 * e, 26 * e))  # o corpo
    pygame.draw.polygon(sup, (90, 210, 175, 180), [(cx - 4 * e, cy), (cx - 20 * e, cy - 10 * e - asa),
                                                   (cx - 4 * e, cy + 12 * e)])  # a asa
    pygame.draw.circle(sup, fantasma, (int(cx + 6 * e), int(cy - 12 * e + cab)), int(10 * e))  # a cabeça
    pygame.draw.polygon(sup, (250, 230, 120, 220), [(cx + 13 * e, cy - 16 * e + cab), (cx + 22 * e, cy - 10 * e + cab),
                                                    (cx + 14 * e, cy - 6 * e + cab)])  # o bico curvo
    pygame.draw.circle(sup, (255, 255, 255, 230), (int(cx + 9 * e), int(cy - 15 * e + cab)), int(3.4 * e))
    pygame.draw.circle(sup, (20, 40, 40, 240), (int(cx + 10 * e), int(cy - 15 * e + cab)), int(1.8 * e))
    pygame.draw.circle(sup, (200, 255, 240, 160), (int(cx + 2 * e), int(cy - 19 * e + cab)), int(2 * e))  # o topete
    if l.dir < 0:
        sup = pygame.transform.flip(sup, True, False)
    brilho(tela, (int(x), int(y)), int(26 * s), (120, 240, 200), 70)
    tela.blit(sup, (x - sup.get_width() / 2, y - sup.get_height() / 2))
    if t >= 30 and (t // 12) % 2 == 0:
        texto(tela, "FRACO!", 15, (180, 255, 220), (int(x + l.dir * 40 * s), int(y - 30 * s)))


def craquen_bau(l, tela):
    t = l.t
    s = l.s
    bx, by = l.x + l.dir * 56 * s, l.y
    w, h = 62 * s, 36 * s
    borda, madeira, ouro = (30, 18, 10), (130, 80, 40), (240, 190, 60)
    abre = suave(min(1, max(0, (t - 8) / 10)))
    corpo = pygame.Rect(0, 0, w, h)
    corpo.midbottom = (int(bx), int(by))
    if abre > 0:  # o brilho lá de dentro
        brilho(tela, (corpo.centerx, corpo.y), int(60 * s * abre), (255, 220, 100), int(170 * abre))
    pygame.draw.rect(tela, borda, corpo.inflate(6, 6), border_radius=4)
    pygame.draw.rect(tela, madeira, corpo, border_radius=4)
    for k in range(1, 3):
        pygame.draw.line(tela, (96, 56, 26), (corpo.x + 3, corpo.y + k * h / 3), (corpo.right - 3, corpo.y + k * h / 3), 2)
    for fx in (0.15, 0.85):
        pygame.draw.rect(tela, ouro, (corpo.x + w * fx - 4, corpo.y, 8, h))
    if abre > 0:
        pygame.draw.ellipse(tela, (255, 210, 60), (corpo.x + 4, corpo.y - 5 * s, w - 8, 10 * s))  # as moedas lá dentro
    piv = (corpo.centerx - l.dir * w / 2, corpo.y)  # a TAMPA abrindo pra trás
    ang = abre * 1.4
    tampa = []
    for px, py in ((0, 0), (w, 0), (w, -14 * s), (w * 0.5, -20 * s), (0, -14 * s)):
        px *= l.dir
        c, sn = math.cos(ang * -l.dir), math.sin(ang * -l.dir)
        tampa.append((piv[0] + px * c - py * sn, piv[1] + px * sn + py * c))
    pygame.draw.polygon(tela, borda, tampa)
    pygame.draw.polygon(tela, madeira, [(x * 0.94 + tampa[3][0] * 0.06, y * 0.94 + tampa[3][1] * 0.06) for x, y in tampa])
    for i in range(6):  # as moedas pulando (ele contando)
        u = (t - 18 - i * 6)
        if 0 <= u < 18:
            x = corpo.centerx + (i - 2.5) * 9 * s
            y = corpo.y - math.sin(u / 18 * math.pi) * 60 * s
            pygame.draw.ellipse(tela, (130, 90, 20), (x - 6, y - 4, 12, 9))
            pygame.draw.ellipse(tela, (255, 215, 70), (x - 5, y - 3, 10, 7))


PIPOCA_SOBE, PIPOCA_NHAC = 12, 44


# =====================================================================
# MAGNUS
# =====================================================================
def magnus_pipoca_passo(l, jogo):
    if fim_pose(l):
        return
    usa_pose(l, dict(l.poses.get("m_ruge") or l.poses["parado"]))
    if l.t == PIPOCA_SOBE:
        som.tocar("explosao", 0.3)
    if l.t == PIPOCA_NHAC:
        som.tocar("soco", 0.5)
        cb = ponto(l, "cb")
        fumaca(jogo, cb[0] + l.dir * 24 * l.s, cb[1] - 6, 6, (120, 110, 100), 2, -1.2)


def magnus_pipoca(l, tela):
    from efeitos import texto
    t = l.t
    cb = ponto(l, "cb")
    boca = (cb[0] + l.dir * 26 * l.s, cb[1] + 2 * l.s)
    if PIPOCA_SOBE <= t < PIPOCA_NHAC:
        k = (t - PIPOCA_SOBE) / (PIPOCA_NHAC - PIPOCA_SOBE)
        for i in range(5, -1, -1):  # a bola de fogo subindo e caindo (com rastro)
            kk = max(0, k - i * 0.02)
            x = boca[0] + math.sin(kk * math.pi * 2) * 10
            y = boca[1] - math.sin(kk * math.pi) * 150 * l.s
            r = max(2, int((11 - i * 1.5) * l.s))
            pygame.draw.circle(tela, (255, 120 + i * 20, 40), (int(x), int(y)), r)
        x = boca[0] + math.sin(k * math.pi * 2) * 10
        y = boca[1] - math.sin(k * math.pi) * 150 * l.s
        brilho(tela, (int(x), int(y)), int(26 * l.s), (255, 150, 40), 180)
        pygame.draw.circle(tela, (255, 240, 170), (int(x), int(y)), max(2, int(6 * l.s)))
    if PIPOCA_NHAC <= t < PIPOCA_NHAC + 12:
        texto(tela, "NHAC!", int(26 - (t - PIPOCA_NHAC)), (255, 200, 90), (int(boca[0]), int(boca[1] - 40 * l.s)))
        brilho(tela, (int(boca[0]), int(boca[1])), int(24 * l.s), (255, 140, 40), 150)


def magnus_coceira_passo(l, jogo):
    if fim_pose(l):
        return
    p = dict(l.poses.get("m_fareja") or l.poses["parado"])
    if 12 <= l.t < T - 12:  # a pata de trás coçando o pescoço (rápido, igual cachorro)
        cb = p["cb"]
        p["pf"] = (cb[0] - 18 + (l.t % 4) * 4, cb[1] - 10 + (l.t % 3) * 4)
        p["jf"] = ((p["qd"][0] + p["pf"][0]) / 2 + 16, (p["qd"][1] + p["pf"][1]) / 2 - 6)
    usa_pose(l, p)
    if 12 <= l.t < T - 12 and l.t % 2 == 0:  # as faíscas do metal raspando
        cb = ponto(l, "cb")
        for _ in range(3):
            jogo.faiscas.append([cb[0] - l.dir * 10 * l.s, cb[1] + 6 * l.s, random.uniform(-4, 4), random.uniform(-5, -1),
                                 14, (255, 230, 120), 3])
        if l.t % 8 == 0:
            som.tocar("defesa", 0.2)


# =====================================================================
# SPHYRUS
# =====================================================================
def sphyrus_bolhas_passo(l, jogo):
    if fim_pose(l):
        return
    usa_pose(l, dict(l.poses.get("s_ruge") or l.poses["parado"]))
    l.extra["sente"] = 4  # (as guelras e a linha acesas)
    if l.t % 8 == 2:
        som.tocar("puf", 0.15)


def sphyrus_bolhas(l, tela):
    t = l.t
    cb = ponto(l, "cb")
    boca = (cb[0] + l.dir * 34 * l.s, cb[1] + 4 * l.s)  # (a boca fica na ponta da cabeça de perfil)
    for i in range(8):
        u = (t - 8 - i * 6)
        if not 0 <= u < 44:
            continue
        x = boca[0] + l.dir * u * 0.8 + math.sin(u * 0.3 + i) * 6
        y = boca[1] - u * 2.6
        r = int((4 + i % 3 * 2 + u * 0.08) * l.s)
        if u > 38:  # estoura
            for a in range(6):
                pygame.draw.circle(tela, (210, 240, 255), (int(x + math.cos(a) * r), int(y + math.sin(a) * r)), 1)
            continue
        pygame.draw.circle(tela, (40, 80, 120), (int(x), int(y)), r + 1, 1)
        pygame.draw.circle(tela, (210, 240, 255), (int(x), int(y)), r, 2)
        pygame.draw.circle(tela, (255, 255, 255), (int(x - r * 0.4), int(y - r * 0.4)), max(1, r // 3))


def sphyrus_dente_passo(l, jogo):
    if l.t == 10:
        l.extra["dente_falta"] = 50
        som.tocar("defesa", 0.3)


def sphyrus_dente(l, tela):
    t = l.t
    e = 1.6 * l.s
    cb = ponto(l, "cb")
    boca = (cb[0] + l.dir * 30 * l.s, cb[1] + 2 * l.s)
    if 10 <= t < 22:  # o dente caindo da boca
        k = (t - 10) / 12
        dente(tela, boca[0], boca[1] + k * k * 60 * l.s, e, k * 3)
    elif 22 <= t < 40:  # ele pega e olha (de pertinho)
        mx, my = ponto(l, "mf")
        dente(tela, mx, my - 6 * l.s, e)
    elif 40 <= t < 56:  # e joga fora por cima do ombro
        k = (t - 40) / 16
        mx, my = ponto(l, "mf")
        x, y = mx - l.dir * k * 140 * l.s, my - math.sin(k * math.pi) * 70 * l.s + k * 40 * l.s
        dente(tela, x, y, e, k * 8)
    if 44 <= t < 60:  # TCHANAM: o dente novo nasce brilhando
        brilho(tela, (int(boca[0]), int(boca[1])), int(18 * l.s), (255, 255, 230), 200)
        for a in range(4):
            r = 10 + (t - 44)
            pygame.draw.line(tela, (255, 255, 230), (boca[0], boca[1]),
                             (boca[0] + math.cos(a * 1.57 + 0.4) * r, boca[1] + math.sin(a * 1.57 + 0.4) * r), 2)


# =====================================================================
# RIBBAT (com os desenhos do jogo dele)
# =====================================================================
def ribbat_mosca(l, tela):
    import ribbat_lutador as rb
    t = l.t
    bx, by = rb.boca(l)
    alvo_x, alvo_y = l.x + l.dir * 90 * l.s, l.y - 50 * l.s
    if t < 30:  # a mosca passando zumbindo
        k = t / 30
        mx, my = alvo_x + l.dir * 140 * (1 - k), alvo_y - 60 * (1 - k) + math.sin(t * 0.6) * 8
    elif t < 38:
        mx, my = alvo_x, alvo_y
    else:
        k = min(1, (t - 38) / 10)
        mx, my = alvo_x + (bx - alvo_x) * k, alvo_y + (by - alvo_y) * k
    if 30 <= t < 48:  # a língua
        pygame.draw.line(tela, (120, 30, 50), (bx, by), (mx, my), int(6 * l.s))
        pygame.draw.line(tela, (235, 110, 140), (bx, by), (mx, my), int(3 * l.s))
    if t < 48:
        img = pygame.transform.smoothscale(rb._mosca_bruta(t), (int(30 * l.s), int(24 * l.s)))
        tela.blit(img, (mx - 15 * l.s, my - 14 * l.s))


def ribbat_mosca_passo(l, jogo):
    if l.t == 30:
        som.tocar("lingua")


def ribbat_chefao_passo(l, jogo):
    l.extra.setdefault("chefao", ("viuva", "besouro", "rainha", "gato", "aguia")[getattr(l, "golpe_id", 0) % 5])
    if l.t == 30:
        som.tocar("soco")
        jogo.tremer(6)
    if l.t == 38:
        cx = l.x + l.dir * 90 * l.s
        fumaca(jogo, cx, l.y - 40, 14, (230, 230, 240), 4, -1)
        som.tocar("puf")
    if l.t >= T - 4:
        l.extra.pop("chefao", None)


def ribbat_chefao(l, tela):
    import ribbat_lutador as rb
    t = l.t
    qual = l.extra.get("chefao", "viuva")
    if not 6 <= t < 38:
        return
    k = min(1, (t - 6) / 10)
    sup = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    cx = l.x + l.dir * 90 * l.s
    rb.DESENHOS[qual](sup, cx, l.y, 0.5, 1.0, -l.dir, t)
    sup.set_alpha(int(255 * k))
    tela.blit(sup, (0, 0))
    if 30 <= t < 36:  # o UM golpe
        brilho(tela, (int(cx), int(l.y - 40)), 60, (255, 255, 220), 200)


# =====================================================================
# A loja: 2 por lutador
# =====================================================================
def _p(lutador, ident, nome, frase, preco=PRECO, passo=None, desenho=None, quadros_=None):
    item = dict(id=ident, nome=nome, preco=preco, provocacao=frase)
    if passo:
        item["provocacao_passo"] = passo
    if desenho:
        item["provocacao_desenho"] = desenho
    if quadros_:
        item["provocacao_quadros"] = quadros_
    extras.registrar("provocacoes", lutador, **item)


_p("MAX-10", "escaneia", "ESCANEAMENTO", "ANÁLISE COMPLETA. NADA DETECTADO.", PRECO_CAPRICHADA, max_escaneia_passo,
   max_escaneia, quadros((6, "parado")))
_p("MAX-10", "lanche", "HORA DO LANCHE", "PAUSA PARA MANUTENÇÃO.", PRECO, max_lanche_passo, max_lanche)
_p("RIB", "medita", "MEDITAÇÃO NINJA", "Me acorda quando for lutar de verdade.", PRECO, rib_medita_passo, rib_medita)
_p("RIB", "bunshin", "BUNSHIN DE TREINO", "Será que pelo menos assim você faz alguma coisa?", PRECO_CAPRICHADA,
   rib_bunshin_passo, rib_bunshin, quadros((6, "r_selo")))
_p("TRAFO", "pulga", "PULGA", "Grrr... pulga!", PRECO, trafo_pulga_passo, trafo_pulga)
_p("TRAFO", "olhos", "MALABARISMO DE OLHOS", "AU! Quer ver mais um truque?", PRECO_CAPRICHADA, None, trafo_olhos,
   quadros((6, "t_olhos")))
_p("KING RIP", "cha", "HORA DO CHÁ", "Me avise quando ficar difícil.", PRECO, king_cha_passo, king_cha)
_p("KING RIP", "danca", "DANÇA DO NUNCHAKU", "Na minha época, isso era dança de festa!", PRECO, king_danca_passo,
   king_danca)
_p("CANNAN", "pistola", "PISTOLA GIRANDO", "Nem precisei recarregar.", PRECO, cannan_pistola_passo, cannan_pistola)
_p("CANNAN", "flexoes", "FLEXÕES", "Isso aqui é só o aquecimento.", PRECO, cannan_flexoes_passo, cannan_flexoes)
_p("FINN", "livro", "LIVRO DE MAGIA", "Capítulo 1: como vencer iniciantes.", PRECO, finn_livro_passo, finn_livro)
_p("FINN", "fogos", "FOGOS DO CAJADO", "Ho ho ho!", PRECO_CAPRICHADA, finn_fogos_passo, finn_fogos,
   quadros((6, "f_ult")))
_p("KUN", "castelo", "CASTELO DE CARTAS", "Igual a sua defesa.", PRECO_CAPRICHADA, None, kun_castelo,
   quadros((6, "k_agacha")))
_p("KUN", "truco", "TRUCO", "Bora um truco?", PRECO, None, kun_truco, quadros((6, "k_lanca")))
_p("TROMOS", "teto", "CABEÇA PRA BAIXO", "*clic-clic-clic*", PRECO_CAPRICHADA, xeno_teto_passo, xeno_teto)
_p("TROMOS", "chafariz", "CHAFARIZ DE ÁCIDO", "*Hssssss...*", PRECO, xeno_chafariz_passo, xeno_chafariz)
_p("TAI", "sal", "SAL DA SORTE", "Pra dar sorte... pra você vai precisar.", PRECO, tai_sal_passo, tai_sal)
_p("TAI", "lanche", "LANCHINHO", "Luta dá fome.", PRECO, tai_lanche_passo, tai_lanche)
_p("TAMER", "busca", "BUSCA, GAROTO!", "Pega, garoto!", PRECO_CAPRICHADA, tamer_busca_passo, tamer_busca,
   quadros((4, "t_aponta")))
_p("TAMER", "selfie", "SELFIE", "Essa vai pro documentário.", PRECO, tamer_selfie_passo, tamer_selfie)
_p("JOHN", "pombas", "POMBAS", "Ta-dá!", PRECO, john_pombas_passo, john_pombas, quadros((6, "j_tira")))
_p("JOHN", "flores", "FLORES", "Um consolo pro perdedor.", PRECO, None, john_flores, quadros((6, "j_magica")))
_p("CRÁQUEN", "papagaio", "PAPAGAIO FANTASMA", "Fraco! Fraco! Arrr!", PRECO_CAPRICHADA, craquen_papagaio_passo,
   craquen_papagaio)
_p("CRÁQUEN", "bau", "BAÚ DO TESOURO", "Mais um pro meu tesouro.", PRECO, None, craquen_bau, quadros((6, "q_ri")))
_p("MAGNUS", "pipoca", "PIPOCA DE FOGO", "*nhac!*", PRECO, magnus_pipoca_passo, magnus_pipoca)
_p("MAGNUS", "coceira", "COCEIRA DE ROBÔ", "*clank... clank...*", PRECO, magnus_coceira_passo)
_p("SPHYRUS", "bolhas", "BOLHAS", "*blub... blub...*", PRECO, sphyrus_bolhas_passo, sphyrus_bolhas)
_p("SPHYRUS", "dente", "DENTE NOVO", "*clac!*", PRECO, sphyrus_dente_passo, sphyrus_dente, quadros((6, "s_ruge")))
_p("RIBBAT", "mosca", "COMER UMA MOSCA", "Ribbit.", PRECO, ribbat_mosca_passo, ribbat_mosca)
_p("RIBBAT", "chefao", "CHEFÃO SURPRESA", "RIBBIT!", PRECO_CAPRICHADA, ribbat_chefao_passo, ribbat_chefao)


# =====================================================================
# FRIGANTUS
# =====================================================================
def frig_boneco(l, tela):
    t = l.t
    bx = l.x + l.dir * 60 * l.s
    o = getattr(l, "_alvo_marujos", None)
    cor = o.f.get("cor", (200, 120, 80)) if o is not None else (200, 120, 80)
    tomba = max(0, (t - 52) / 10)
    a = min(1.4, tomba) * l.dir
    bolas = [(0, 14, 16), (0, 38, 12), (0, 58, 9)]
    for i, (dx, dy, r) in enumerate(bolas):
        if t < 8 + i * 12:
            continue
        x = bx + math.sin(a) * dy * l.s
        y = CHAO - math.cos(a) * dy * l.s
        pygame.draw.circle(tela, (180, 196, 220), (int(x), int(y)), int((r + 1.5) * l.s))
        pygame.draw.circle(tela, (250, 252, 255), (int(x), int(y)), int(r * l.s))
        if i == 2:  # a cara do adversário (na cor dele)
            pygame.draw.circle(tela, cor, (int(x), int(y)), int(6 * l.s))
            pygame.draw.circle(tela, (20, 20, 20), (int(x + l.dir * 2 * l.s), int(y - 2 * l.s)), max(1, int(1.2 * l.s)))
    if 50 <= t < 54:  # o peteleco
        mx, my = ponto(l, "mf")
        pygame.draw.circle(tela, (255, 255, 255), (int(mx), int(my)), 6, 2)


def frig_picole(l, tela):
    s = l.s
    mx, my = ponto(l, "mf")
    k = min(1, max(0, (l.t - 6) / 8))
    if k <= 0:
        return
    pygame.draw.line(tela, (30, 20, 10), (mx, my + 4 * s), (mx, my - 10 * s), max(4, int(5 * s)))  # o palito
    pygame.draw.line(tela, (220, 180, 120), (mx, my + 4 * s), (mx, my - 10 * s), max(2, int(3 * s)))
    corpo = pygame.Rect(0, 0, 18 * s, 34 * s * k)
    corpo.midbottom = (int(mx), int(my - 8 * s))
    pygame.draw.rect(tela, (40, 80, 110), corpo.inflate(4, 4), border_top_left_radius=int(9 * s),
                     border_top_right_radius=int(9 * s))
    pygame.draw.rect(tela, (150, 210, 245), corpo, border_top_left_radius=int(8 * s), border_top_right_radius=int(8 * s))
    pygame.draw.rect(tela, (90, 160, 220), (corpo.x, corpo.y + corpo.h * 0.5, corpo.w, corpo.h * 0.5))  # 2 sabores
    pygame.draw.line(tela, (230, 250, 255), (corpo.x + 4, corpo.y + 6), (corpo.x + 4, corpo.bottom - 6), 2)  # brilho
    mordidas = min(2, max(0, (l.t - 20) // 16))  # as MORDIDAS (some um pedaço do topo)
    for i in range(mordidas):
        cx_, cy_ = corpo.right - 2, corpo.y + 6 * s + i * 8 * s
        pygame.draw.arc(tela, (40, 80, 110), (cx_ - 5 * s, cy_ - 5 * s, 10 * s, 10 * s), 1.6, 4.7, 2)
    if (l.t // 6) % 3 == 0:  # a gota derretendo
        pygame.draw.circle(tela, (150, 210, 245), (int(corpo.x + 3), int(corpo.bottom + 4 + (l.t % 6) * 2)), 2)


_p("FRIGANTUS", "boneco", "BONECO DE NEVE", "*UH-UH!*", PRECO_CAPRICHADA, None, frig_boneco,
   quadros((6, "fr_soco_chao"), (40, "fr_peito_a"), (50, "fr_soco")))
_p("FRIGANTUS", "picole", "PICOLÉ", "*Hmm...*", PRECO, frig_picole_passo, frig_picole)
