"""CENAS DE ANIME do TRAFO (loja), com as ideias do Gomes.

ENTRADA (TRANSFORMAÇÃO AO CONTRÁRIO): ele começa DISFARÇADO de um lutador sorteado... o oponente fala "EU SEI QUE É
VOCÊ, TRAFO.", o falso dá uma risadinha, se DESTRANSFORMA e entra na pose de batalha.
VITÓRIA (DESFILE DE FORMAS): vira um lutador sorteado e usa o golpe do E DELE (laser do Max, shuriken do Rib, bola de
neve do Frigantus...) — mostrado em PRIMEIRA PESSOA, pelos olhos do derrotado, caído no chão.
Os lutadores aparecem com o desenho do jogo; os golpes que vêm na câmera são ilustrados.
"""
import math
import random

import pygame

import cutscene
import ult2
from cena_max import fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

BORDA = (14, 10, 8)
XT, XO = LARGURA * 0.32, LARGURA * 0.72  # o Trafo e o oponente, no mapa
PODER = (196, 36, 28)  # a energia vermelha da transformação
COR_NOME = (170, 120, 40)


def pose(c, nome):
    return c.l.poses.get(nome) or c.l.poses["parado"]


def sortear_falso(oponente):
    """O lutador que ele vai IMITAR (sorteado; nunca ele mesmo nem o oponente)."""
    from personagens import PERSONAGENS
    nomes = {"TRAFO", (oponente or {}).get("nome_base", (oponente or {}).get("nome"))}
    candidatos = [f for f in PERSONAGENS if f.get("nome_base", f["nome"]) not in nomes]
    return random.Random().choice(candidatos)  # (só a imagem: um random à parte, sem mexer no da luta)


def lut(c, ficha):
    """Um Lutador pra desenhar outra ficha (o falso), guardado na cena."""
    from lutador import Lutador
    if not hasattr(c, "_luts"):
        c._luts = {}
    if ficha["nome"] not in c._luts:
        c._luts[ficha["nome"]] = Lutador(ficha, 0, 1)
    return c._luts[ficha["nome"]]


def por_ficha(c, q, ficha, nome_pose, escala, x, y, d=1, cor=None):
    """Desenha o lutador da FICHA (o disfarce) com o pé em (x, y). cor = pinta de uma cor só (vulto/brilho)."""
    from provocacoes_loja import sprite
    l = lut(c, ficha)
    p = nome_pose if isinstance(nome_pose, dict) else (l.poses.get(nome_pose) or l.poses["parado"])
    img, pe = sprite(l, p, escala)
    if l.tem_tinta():
        l.aplicar_tinta(img, False)
    if d < 0:
        img = pygame.transform.flip(img, True, False)
        pe = (img.get_width() - pe[0], pe[1])
    if cor:
        img.fill(cor, special_flags=pygame.BLEND_RGB_MAX)  # (só a cor: o fundo transparente continua transparente)
    q.blit(img, (int(x - pe[0]), int(y - pe[1])))
    return l, p


def ponto_ficha(c, ficha, nome_pose, k, escala, x, y, d=1):
    l = lut(c, ficha)
    p = l.poses.get(nome_pose) or l.poses["parado"]
    s = l.s * escala
    return x + p[k][0] * s * d, y - p[k][1] * s


def balao(q, x, y, txt, k=1.0, lado=1):
    """BALÃO DE FALA (o texto vai aparecendo letra por letra; k = 0..1). (x, y) = a pontinha do balão."""
    from efeitos import texto
    mostra = txt[:max(1, int(len(txt) * k))]
    larg = 30 + len(txt) * 19
    r = pygame.Rect(0, 0, larg, 74)
    r.midbottom = (int(x + lado * larg * 0.25), int(y - 28))
    pygame.draw.polygon(q, BORDA, [(x, y), (r.centerx - lado * 10 - 12, r.bottom - 4), (r.centerx - lado * 10 + 12, r.bottom - 4)])
    pygame.draw.rect(q, BORDA, r.inflate(8, 8), border_radius=24)
    pygame.draw.rect(q, (255, 255, 255), r, border_radius=22)
    pygame.draw.polygon(q, (255, 255, 255), [(x + lado * 2, y - 8), (r.centerx - lado * 10 - 8, r.bottom - 6), (r.centerx - lado * 10 + 8, r.bottom - 6)])
    r.clamp_ip(q.get_rect().inflate(-20, -100))
    texto(q, mostra, 30, BORDA, (r.centerx, r.centery), sombra=False)


def fumaca_transforma(q, x, y, u, raio=110, cor=(230, 220, 210)):
    """A FUMAÇA da transformação (redemoinho de bolotas que cresce e some) e a ENERGIA vermelha."""
    rnd = random.Random(8)
    sup = pygame.Surface(q.get_size(), pygame.SRCALPHA)
    for i in range(18):
        a = rnd.uniform(0, math.tau) + u * 3
        d = raio * (0.3 + 0.7 * u) * rnd.uniform(0.5, 1)
        r = 24 + 40 * u * rnd.uniform(0.6, 1.2)
        pygame.draw.circle(sup, (*cor, int(230 * (1 - u))), (int(x + math.cos(a) * d), int(y + math.sin(a) * d * 0.7)), int(r))
    q.blit(sup, (0, 0))
    brilho(q, (int(x), int(y)), int(raio * (1 - u * 0.5)), PODER, int(200 * (1 - u)))


# =====================================================================
# ENTRADA: TRANSFORMAÇÃO AO CONTRÁRIO
# =====================================================================
def e1_falso(c, q, t, k):
    """1) No MAPA: um lutador (o FALSO, sorteado) parado na frente do oponente. A câmera chega."""
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    por_ficha(c, base, c.falso, "parado", 1.0, XT, CHAO)
    c.mapa_frente(base, t)
    c.camera(q, base, ((XT + XO) / 2, CHAO - 90), 1.5 + 0.3 * suave(k), pixel=True)


def e2_sei(c, q, t, k):
    """2) CLOSE no OPONENTE (desconfiado): "EU SEI QUE É VOCÊ, TRAFO." """
    base = c._tela_aux()
    c.mapa(base, t + 40)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    c.mapa_frente(base, t + 40)
    if c.oponente:
        cb = ponto_ficha(c, c.oponente, "parado", "cb", 1.0, XO, CHAO, -1)
    else:
        cb = (XO, CHAO - 160)
    centro, z = (cb[0] - 60, cb[1] + 10), 2.6
    c.camera(q, base, centro, z, pixel=True)
    bx, by = para_tela(centro, z, (cb[0] - 14, cb[1] - 6))
    if t >= 6:
        balao(q, bx - 30, by - 10, "EU SEI QUE É VOCÊ, TRAFO.", min(1, (t - 6) / 24), -1)


def e3_risada(c, q, t, k):
    """3) CLOSE no FALSO: gota de suor... e uma RISADINHA (os ombros tremendo: hehehe...)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 80)
    treme = math.sin(t * 1.6) * 2 if t > 12 else 0
    por_ficha(c, base, c.falso, "parado", 1.0, XT, CHAO - abs(treme))
    c.mapa_frente(base, t + 80)
    cb = ponto_ficha(c, c.falso, "parado", "cb", 1.0, XT, CHAO)
    centro, z = (cb[0] + 10, cb[1] + 30), 3.0
    c.camera(q, base, centro, z, pixel=True)
    gx, gy = para_tela(centro, z, (cb[0] + 14, cb[1] - 14))
    if t < 14:  # a GOTA de suor
        yy = gy + t * 3
        pygame.draw.polygon(q, (150, 210, 255), [(gx, yy - 22), (gx + 12, yy + 4), (gx - 12, yy + 4)])
        pygame.draw.circle(q, (150, 210, 255), (int(gx), int(yy + 4)), 12)
        pygame.draw.circle(q, (255, 255, 255), (int(gx - 4), int(yy)), 3)
    else:
        texto_pow(q, "hehehe...", (int(w * 0.66), int(h * 0.26)), 46, (255, 240, 200), (t - 14) % 10, giro=0.08)


def e4_destransforma(c, q, t, k):
    """4) A DESTRANSFORMAÇÃO: brilho vermelho no contorno, o corpo PISCA entre o falso e o Trafo (cada vez mais
    Trafo), a fumaça girando... POOF!"""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 120)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    u = min(1, t / 30)
    pisca = (t // 2) % 2 == 0
    trafo = u > 0.85 or (pisca and random.Random(t).random() < u)
    if t < 30:
        brilho(base, (int(XT), int(CHAO - 70)), 120, PODER, int(160 * u))
    if trafo:
        c.por(base, "parado", 1.0, XT, CHAO, 1, guardar=False)
    else:
        por_ficha(c, base, c.falso, "parado", 1.0, XT, CHAO, cor=tuple(int(v * u) for v in PODER))
    if 22 <= t < 44:
        fumaca_transforma(base, XT, CHAO - 70, (t - 22) / 22)
    c.mapa_frente(base, t + 120)
    c.camera(q, base, (XT + 30, CHAO - 90), 2.2, pixel=True)
    if t % 3 == 0 and t < 30:
        c.tremor = max(c.tremor, 2)
    if t == 22:
        c.inverte, c.tremor = 2, 12
    if 22 <= t < 36:
        texto_pow(q, "POOF!", (int(w * 0.62), int(h * 0.24)), 70, (255, 230, 200), t - 22)


def e5_pose(c, q, t, k):
    """5) O TRAFO de verdade, na POSE DE BATALHA (abaixa rosnando), e o nome."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 170)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    p = misturar(pose(c, "parado"), pose(c, "t_agacha"), suave(min(1, t / 10)))
    c.por(base, p, 1.0, XT, CHAO, 1, guardar=False)
    c.mapa_frente(base, t + 170)
    c.camera(q, base, (XT + 60, CHAO - 80), 2.3 - 0.3 * suave(min(1, t / 50)), pixel=True)
    if 8 <= t < 34:
        texto_pow(q, "GRRRR...", (int(w * 0.62), int(h * 0.26)), 52, (255, 200, 150), (t - 8) % 10, giro=0.06)
        if t % 4 == 0:
            c.tremor = max(c.tremor, 2)
    if t >= 24:
        faixa_nome(q, "TRAFO", "O METAMORFO.", COR_NOME, (t - 24) / 30)


PLANOS = [
    (44, e1_falso, {}),
    (56, e2_sei, {6: ("blip", 0.5)}),
    (40, e3_risada, {14: ("blip", 0.3), 22: ("blip", 0.3)}),
    (48, e4_destransforma, {0: ("carga", 0.6), 22: ("puf", 0.9)}),
    (70, e5_pose, {8: ("uivo", 0.5)}),
]


def entrada(ficha, titulo="", oponente=None):
    c = CenaAnime(ficha, PLANOS, titulo, oponente)
    c.falso = sortear_falso(oponente)
    return c


# =====================================================================
# VITÓRIA: DESFILE DE FORMAS (em PRIMEIRA PESSOA, pelos olhos do derrotado)
# =====================================================================
GOLPE_E = {  # o golpe do E de cada um, vindo na CÂMERA: (o que vem, o que acontece quando bate)
    "MAX-10": ("laser", "queima"), "RIB": ("shuriken", "racha"), "KING RIP": ("nunchaku", "racha"),
    "CANNAN": ("tiros", "furos"), "FINN": ("fogo", "queima"), "KUN": ("carta", "racha"),
    "TROMOS": ("acido", "suja"), "TAI": ("onda", "treme"), "TAMER": ("lobo", "preto"),
    "JOHN": ("cartola", "racha"), "CRÁQUEN": ("ancora", "racha"), "MAGNUS": ("espinhos", "furos"),
    "SPHYRUS": ("ar", "treme"), "FRIGANTUS": ("neve", "suja"),
}


def golpe_do(ficha):
    return GOLPE_E.get(ficha.get("nome_base", ficha["nome"]), ("fogo", "queima"))


def palpebras(q, abre):
    """As PÁLPEBRAS (abre 0 = olho fechado ... 1 = aberto), com a borda borrada, e a vinheta."""
    w, h = q.get_size()
    if abre < 1:
        tampa = h * 0.5 * (1 - abre)
        pygame.draw.rect(q, (0, 0, 0), (0, 0, w, tampa))
        pygame.draw.rect(q, (0, 0, 0), (0, h - tampa, w, tampa))
        pygame.draw.ellipse(q, (0, 0, 0), (-w * 0.1, tampa - 40, w * 1.2, 80))
        pygame.draw.ellipse(q, (0, 0, 0), (-w * 0.1, h - tampa - 40, w * 1.2, 80))
    vin = pygame.Surface((w, h), pygame.SRCALPHA)  # a vinheta (a visão meio zonza nos cantos)
    for i in range(10):
        pygame.draw.ellipse(vin, (0, 0, 0, 14 + i * 4), (-i * 40, -i * 30, w + i * 80, h + i * 60), 30)
    q.blit(vin, (0, 0))


def objeto_vindo(c, q, tipo, x, y, tam, t, falso):
    """O golpe vindo NA CÂMERA (ilustrado), centro (x, y), do tamanho tam."""
    if tipo == "shuriken":  # (DE LADO, pedido do Gomes: deitada, girando como um disco, as pontas passando)
        larg = int(tam * 0.8) + 8
        alt = max(3, int(larg * 0.16))
        sup = pygame.Surface((larg, alt + 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sup, (40, 44, 52), (0, 3, larg, alt))
        pygame.draw.ellipse(sup, (204, 210, 220), (2, 4, larg - 4, alt - 2))
        for i in range(4):
            fase = (t * 0.9 + i * math.pi / 2) % math.tau
            px = larg / 2 + math.cos(fase) * larg * 0.48
            pygame.draw.polygon(sup, (204, 210, 220), [(px - 3 - larg * 0.02, 3 + alt / 2), (px, 0), (px + 3 + larg * 0.02, 3 + alt / 2)])
        pygame.draw.ellipse(sup, (110, 116, 128), (larg / 2 - larg * 0.08, 3 + alt * 0.25, larg * 0.16, alt * 0.5))
        q.blit(sup, sup.get_rect(center=(int(x), int(y))))
        for i in range(3):  # os riscos de vento atrás
            yy = y - 3 + i * 3
            pygame.draw.line(q, (220, 230, 255), (x - larg / 2 - 14 - i * 10, yy), (x - larg / 2 - 4 - i * 10, yy), 2)
    elif tipo == "carta":  # (DE LADO, pedido do Gomes: deitada, girando como um disco, bem fina)
        larg = int(tam * 0.9) + 8
        alt = max(3, int(larg * (0.12 + 0.08 * abs(math.sin(t * 0.9)))))
        carta = pygame.Surface((larg, alt), pygame.SRCALPHA)
        pygame.draw.ellipse(carta, (16, 14, 20), (0, 0, larg, alt))
        pygame.draw.ellipse(carta, (246, 244, 236), (2, 1, larg - 4, alt - 2))
        if (t // 2) % 2:  # (o verso vermelho aparecendo enquanto gira)
            pygame.draw.ellipse(carta, (200, 40, 40), (larg // 4, 1, larg // 2, alt - 2))
        carta = pygame.transform.rotate(carta, math.sin(t * 0.3) * 8)
        q.blit(carta, carta.get_rect(center=(int(x), int(y))))
        for i in range(3):  # os riscos de vento atrás
            yy = y - alt / 2 + i * alt / 2
            pygame.draw.line(q, (220, 230, 255), (x - larg / 2 - 14 - i * 10, yy), (x - larg / 2 - 4 - i * 10, yy), 2)
    elif tipo == "neve":
        import cena_frigantus
        cena_frigantus.bola_neve(q, x, y, tam * 0.5, giro=t * 0.3)
    elif tipo == "fogo":
        for i in range(6):
            r = tam * (0.5 - i * 0.06)
            cor = ((255, 120, 30), (255, 170, 60), (255, 220, 120), (255, 245, 200), (255, 255, 255), (255, 255, 255))[i]
            pygame.draw.circle(q, cor, (int(x + math.sin(t + i) * 4), int(y)), max(1, int(r)))
        brilho(q, (int(x), int(y)), int(tam), (255, 140, 40), 160)
    elif tipo == "acido":  # (GOSMA: irregular, tremelicando, com brilho, bolhas e gotas caindo)
        rr = tam * 0.45
        pts = []
        for i in range(14):
            a = i * math.tau / 14
            k_ = rr * (1 + 0.18 * math.sin(t * 0.7 + i * 1.9))
            pts.append((x + math.cos(a) * k_, y + math.sin(a) * k_ * 0.85))
        pygame.draw.polygon(q, (30, 80, 16), [(px + (px - x) * 0.06, py + (py - y) * 0.06) for px, py in pts])
        pygame.draw.polygon(q, (120, 220, 50), pts)
        pygame.draw.ellipse(q, (210, 255, 150), (x - rr * 0.5, y - rr * 0.55, rr * 0.35, rr * 0.22))
        for i in range(3):  # bolhas
            bx = x + math.cos(i * 2.1 + t * 0.1) * rr * 0.45
            by = y + math.sin(i * 2.1 + t * 0.1) * rr * 0.35
            pygame.draw.circle(q, (160, 240, 90), (int(bx), int(by)), max(2, int(rr * 0.08)), 1)
        for i in range(3):  # gotas caindo atrás
            gx = x + (i - 1) * rr * 0.5
            gy = y + rr * 0.8 + ((t * 3 + i * 9) % 30)
            pygame.draw.circle(q, (120, 220, 50), (int(gx), int(gy)), max(2, int(rr * 0.06)))
    elif tipo == "nunchaku":  # (DE LADO: girando deitado, os bastões encolhem e esticam)
        L = 8 + tam * 0.55
        ang = t * 0.7
        dx, dy = math.cos(ang) * L, math.sin(ang) * L * 0.15
        for sx in (-1, 1):
            a_ = (x + sx * dx * 0.12, y + sx * dy * 0.12)
            b_ = (x + sx * dx, y + sx * dy)
            pygame.draw.line(q, (60, 36, 18), a_, b_, max(4, int(L / 9)))
            pygame.draw.line(q, (150, 96, 50), a_, b_, max(2, int(L / 14)))
        pygame.draw.circle(q, (240, 196, 60), (int(x), int(y)), max(2, int(L / 18)))
        for i in range(3):
            pygame.draw.line(q, (220, 230, 255), (x - L - 12 - i * 8, y - 3 + i * 3), (x - L - 3 - i * 8, y - 3 + i * 3), 2)
    elif tipo == "cartola":
        a = t * 0.5
        sup = pygame.Surface((int(tam * 1.4) + 4, int(tam * 1.4) + 4), pygame.SRCALPHA)
        m = sup.get_width() / 2
        pygame.draw.ellipse(sup, (20, 20, 26), (m - tam * 0.6, m + tam * 0.05, tam * 1.2, tam * 0.3))
        pygame.draw.rect(sup, (30, 30, 38), (m - tam * 0.32, m - tam * 0.5, tam * 0.64, tam * 0.65))
        pygame.draw.rect(sup, (180, 30, 40), (m - tam * 0.32, m - tam * 0.05, tam * 0.64, tam * 0.1))
        for i in range(8):  # as lâminas na aba
            b = i * math.tau / 8
            pygame.draw.polygon(sup, (220, 225, 235), [(m + math.cos(b) * tam * 0.55, m + tam * 0.2 + math.sin(b) * tam * 0.14),
                                                      (m + math.cos(b + 0.25) * tam * 0.7, m + tam * 0.2 + math.sin(b + 0.25) * tam * 0.18),
                                                      (m + math.cos(b + 0.4) * tam * 0.55, m + tam * 0.2 + math.sin(b + 0.4) * tam * 0.14)])
        sup = pygame.transform.rotate(sup, math.degrees(math.sin(a)) * 0.6)
        q.blit(sup, (int(x - sup.get_width() / 2), int(y - sup.get_height() / 2)))
    elif tipo == "ancora":
        cor, esc = (120, 126, 136), (60, 64, 72)
        pygame.draw.line(q, esc, (x, y - tam * 0.5), (x, y + tam * 0.4), int(tam * 0.14) + 2)
        pygame.draw.line(q, cor, (x, y - tam * 0.5), (x, y + tam * 0.4), int(tam * 0.1) + 1)
        pygame.draw.circle(q, esc, (int(x), int(y - tam * 0.56)), int(tam * 0.12), max(2, int(tam * 0.05)))
        pygame.draw.arc(q, cor, (x - tam * 0.45, y - tam * 0.2, tam * 0.9, tam * 0.7), math.pi * 1.05, math.pi * 1.95, int(tam * 0.1) + 1)
        pygame.draw.line(q, cor, (x - tam * 0.3, y - tam * 0.3), (x + tam * 0.3, y - tam * 0.3), int(tam * 0.08) + 1)
        pygame.draw.line(q, (70, 70, 76), (x, y - tam * 0.68), (x - tam * 2, y - tam * 2), max(2, int(tam * 0.04)))  # a corrente
    elif tipo == "espinhos":
        for i in range(5):
            a = i * math.tau / 5 + 0.3
            sx, sy = x + math.cos(a) * tam * 0.35, y + math.sin(a) * tam * 0.3
            pygame.draw.polygon(q, (255, 150, 50), [(sx, sy - tam * 0.12), (sx + tam * 0.06, sy + tam * 0.06), (sx - tam * 0.06, sy + tam * 0.06)])
            brilho(q, (int(sx), int(sy)), int(tam * 0.12) + 1, (255, 140, 40), 150)
    elif tipo == "ar":
        for i in range(4):
            r = tam * (0.3 + i * 0.2)
            pygame.draw.ellipse(q, (220, 240, 255), (x - r, y - r * 0.6, r * 2, r * 1.2), max(2, int(tam * 0.03)))
    elif tipo == "onda":  # (o PISÃO do Tai: a ONDA DE CHOQUE vem pelo chão, um anel de terra crescendo até a câmera)
        w, h = q.get_size()
        u = min(1.0, max(0.0, (tam - 40) / 600))
        rx, ry = 60 + w * 0.7 * u, 14 + 120 * u
        cx, cy = w * 0.5, h - 70 + 40 * u  # (no chão, acima das faixas de cinema)
        pygame.draw.ellipse(q, (110, 86, 60), (cx - rx, cy - ry, rx * 2, ry * 2), max(4, int(10 + 40 * u)))
        rnd = random.Random(3)
        for i in range(16):  # as pedras subindo na frente da onda
            a = math.pi + i * math.pi / 15
            px, py = cx + math.cos(a) * rx, cy + math.sin(a) * ry
            alto = (12 + 50 * u) * rnd.uniform(0.6, 1.2)
            pygame.draw.polygon(q, (130, 104, 76), [(px - alto * 0.4, py), (px, py - alto), (px + alto * 0.4, py)])
            pygame.draw.polygon(q, (60, 46, 34), [(px - alto * 0.4, py), (px, py - alto), (px + alto * 0.4, py)], 2)
    elif tipo == "lobo":  # (o LOBO BRANCO pulando na câmera: a cabeça de frente, o focinho comprido e a bocarra)
        pelo, sombra, borda = (232, 232, 236), (176, 178, 190), (40, 40, 48)
        for lado in (-1, 1):  # as orelhas pontudas
            orelha = [(x + lado * tam * 0.18, y - tam * 0.3), (x + lado * tam * 0.48, y - tam * 0.78), (x + lado * tam * 0.52, y - tam * 0.2)]
            pygame.draw.polygon(q, borda, orelha)
            pygame.draw.polygon(q, pelo, [(px + (x - px) * 0.08, py + (y - tam * 0.4 - py) * 0.08) for px, py in orelha])
        cabeca = [(x - tam * 0.62, y - tam * 0.1), (x - tam * 0.4, y - tam * 0.45), (x, y - tam * 0.52), (x + tam * 0.4, y - tam * 0.45),
                  (x + tam * 0.62, y - tam * 0.1), (x + tam * 0.5, y + tam * 0.2), (x - tam * 0.5, y + tam * 0.2)]
        pygame.draw.polygon(q, borda, [(px, py + 4) for px, py in cabeca])
        pygame.draw.polygon(q, pelo, cabeca)
        for i in range(7):  # o pelo arrepiado nas bochechas
            for lado in (-1, 1):
                bx = x + lado * tam * (0.5 + (i % 2) * 0.08)
                by = y - tam * 0.1 + i * tam * 0.04
                pygame.draw.polygon(q, pelo, [(bx, by), (bx + lado * tam * 0.16, by + tam * 0.03), (bx, by + tam * 0.06)])
        pygame.draw.polygon(q, sombra, [(x - tam * 0.12, y - tam * 0.42), (x + tam * 0.12, y - tam * 0.42), (x, y - tam * 0.05)])
        for lado in (-1, 1):  # os olhos amarelos, bravos
            ox, oy = x + lado * tam * 0.24, y - tam * 0.22
            pygame.draw.polygon(q, (255, 210, 60), [(ox - lado * tam * 0.1, oy - tam * 0.02), (ox + lado * tam * 0.09, oy - tam * 0.07),
                                                    (ox + lado * tam * 0.06, oy + tam * 0.04)])
            pygame.draw.circle(q, borda, (int(ox), int(oy - tam * 0.01)), max(1, int(tam * 0.025)))
        boca = pygame.Rect(0, 0, tam * 0.7, tam * 0.5)  # a BOCARRA aberta (os dentes)
        boca.midtop = (int(x), int(y + tam * 0.05))
        pygame.draw.ellipse(q, borda, boca.inflate(10, 10))
        pygame.draw.ellipse(q, (130, 20, 30), boca)
        pygame.draw.ellipse(q, (210, 70, 80), boca.inflate(-boca.w * 0.5, -boca.h * 0.5).move(0, boca.h * 0.15))
        for i in range(7):
            dx = (i - 3) * tam * 0.09
            pygame.draw.polygon(q, (250, 250, 240), [(x + dx - tam * 0.04, boca.y + 2), (x + dx + tam * 0.04, boca.y + 2), (x + dx, boca.y + tam * 0.12)])
            pygame.draw.polygon(q, (250, 250, 240), [(x + dx - tam * 0.04, boca.bottom - 2), (x + dx + tam * 0.04, boca.bottom - 2),
                                                    (x + dx, boca.bottom - tam * 0.1)])
        pygame.draw.ellipse(q, borda, (x - tam * 0.1, y - tam * 0.08, tam * 0.2, tam * 0.12))  # o nariz
    elif tipo == "tiros":
        pygame.draw.circle(q, (60, 56, 50), (int(x), int(y)), max(2, int(tam * 0.1)))


COR_GOLPE = {"laser": (255, 40, 40), "fogo": (255, 150, 50), "acido": (110, 200, 50), "neve": (248, 252, 255),
             "onda": (150, 120, 90), "ar": (220, 240, 255)}
X_POV = LARGURA * 0.52   # onde ele pousa, na frente da câmera
Y_POV = ALTURA + 150     # (o pé fica embaixo da tela: a gente vê ele de baixo, deitado)
ESC_POV = 3.0
ESC_FRENTE = 3.8   # (o desenho de frente: a cabeça quase no alto da tela, visto de baixo)


def tonto(q, t, escurece=0.55):
    """A visão MEIO APAGADA de quem está caído: escura, sem cor, com a vinheta pulsando."""
    w, h = q.get_size()
    cinza = q.copy()
    cinza.fill((90, 90, 90), special_flags=pygame.BLEND_RGB_MULT)
    cinza.set_alpha(110)
    q.blit(cinza, (0, 0))
    escuro = pygame.Surface((w, h))
    f = int(255 * (1 - escurece) + 20 * math.sin(t * 0.08))
    escuro.fill((max(0, min(255, f)),) * 3)
    q.blit(escuro, (0, 0), special_flags=pygame.BLEND_RGB_MULT)


def piscando(t, base=0.55):
    """O quanto o olho está aberto (meio fechado, piscando devagar de tontura)."""
    pis = (t % 46)
    fecha = max(0.0, 1 - abs(pis - 40) / 5) if pis > 34 else 0.0
    return max(0.0, base + 0.15 * math.sin(t * 0.07) - fecha * 0.6)


def pov_fundo(c, q, t):
    """O que o DERROTADO vê, deitado: o mapa desfocado, de baixo."""
    fundo_desfocado(c, q, t, (XT, CHAO - 160), 1.4, 20)


FRENTE_POSE = {"parado": "parado", "pulo": "pulo", "agachado": "agachado", "especial": "ataque"}
FRENTE_APROVADOS = {"KUN", "MAX-10", "RIB", "KING RIP", "CANNAN", "FINN", "TROMOS", "TAI", "TAMER", "JOHN", "CRÁQUEN", "MAGNUS", "SPHYRUS", "FRIGANTUS"}  # (os desenhos de frente refeitos pixel por pixel e APROVADOS pelo Gomes; os outros ficam de lado)


def frente(c, q, nome_pose, x, y, t, prog=None):
    """O desenho DE FRENTE do lutador (frente.py, feito pelo remodel), se ele já tiver. Devolve os pontos ou None."""
    if c.falso.get("nome_base", c.falso["nome"]) not in FRENTE_APROVADOS:
        return None
    try:
        import frente as fr
    except ImportError:
        return None
    tem = getattr(fr, "tem_frente", None)
    if tem is not None and not tem(c.falso):
        return None
    try:
        return fr.desenhar_frente(q, c.falso, x, y, ESC_FRENTE, FRENTE_POSE.get(nome_pose, "parado"), t, prog=prog) or {}
    except (KeyError, NotImplementedError):
        return None


def falso_pov(c, q, nome_pose, y_extra=0.0, ang=0.0, prog=None):
    """O FALSO (o Trafo transformado) grandão na frente da câmera, DE FRENTE pra ela, visto de baixo.
    (Com o desenho de frente; quem ainda não tem, aparece de lado.)"""
    x, y = X_POV, Y_POV + y_extra
    pts = frente(c, q, nome_pose, x, y, c.t, prog)
    if pts is not None:
        c._pts_frente = pts
        return None
    c._pts_frente = None
    if not ang:
        return por_ficha(c, q, c.falso, nome_pose, ESC_POV, x, y, -1)
    tmp = pygame.Surface(q.get_size(), pygame.SRCALPHA)
    r = por_ficha(c, tmp, c.falso, nome_pose, ESC_POV, x, y, -1)
    tmp = pygame.transform.rotate(tmp, ang)
    q.blit(tmp, (q.get_width() / 2 - tmp.get_width() / 2, q.get_height() / 2 - tmp.get_height() / 2))
    return r


def v1_apagado(c, q, t, k):
    """1) PRIMEIRA PESSOA, deitado no chão, MEIO APAGADO: a visão escura e borrada, piscando devagar...
    uma sombra passa por cima."""
    w, h = q.get_size()
    pov_fundo(c, q, t)
    if 30 <= t < 44:  # a SOMBRA passando (ele pulando lá em cima)
        u = (t - 30) / 14
        sx = -200 + (w + 400) * u
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(sup, (0, 0, 0, 150), (sx - 160, h * 0.1, 320, 160))
        q.blit(sup, (0, 0))
    tonto(q, t)
    palpebras(q, min(piscando(t), t / 14))
    if 8 <= t < 30:
        from efeitos import texto
        texto(q, "...", 40, (200, 200, 210), (int(w * 0.5), int(h * 0.5)))


def v2_pula(c, q, t, k):
    """2) Ele CAI PULANDO bem na frente da câmera, já TRANSFORMADO (de frente pra gente, visto de baixo):
    TUM! a tela treme, a poeira sobe."""
    w, h = q.get_size()
    pov_fundo(c, q, t + 50)
    tonto(q, t + 50, 0.45)
    cai = 10
    if t < cai:
        u = t / cai
        falso_pov(c, q, "pulo", -(1 - u) ** 1.6 * 700)
    else:
        u = t - cai
        falso_pov(c, q, "agachado" if u < 8 else "parado", 20 * max(0, 1 - u / 8))
        if u < 20:  # a POEIRA subindo na frente da câmera
            rnd = random.Random(2)
            sup = pygame.Surface((w, h), pygame.SRCALPHA)
            for i in range(14):
                x = rnd.uniform(0, w)
                r = 60 + u * 6 * rnd.uniform(0.6, 1.2)
                pygame.draw.circle(sup, (200, 190, 170, max(0, 200 - u * 10)), (int(x), int(h - 10 - u * 3 * rnd.uniform(0.5, 1))), int(r))
            q.blit(sup, (0, 0))
    palpebras(q, 0.85)
    if t == cai:
        c.tremor, c.inverte = 20, 2
    if cai <= t < cai + 14:
        texto_pow(q, "TUM!!", (int(w * 0.5), int(h * 0.2)), 80, (255, 240, 220), t - cai)


POV_MIRA, POV_SOLTA, POV_BATE = 8, 22, 36  # (quadros dentro do plano: prepara, solta, bate na câmera)


def v3_ataca(c, q, t, k):
    """3) Ele faz o golpe do E DELE (o do lutador que ele virou)... e o golpe vem DIRETO NA CÂMERA."""
    w, h = q.get_size()
    tipo, efeito = golpe_do(c.falso)
    pov_fundo(c, q, t + 80)
    tonto(q, t + 80, 0.45)
    pose_n = "parado" if t < POV_MIRA else "especial"
    prog = min(1.0, max(0.0, (t - POV_MIRA) / 26))  # (a animação do E do desenho de frente: prepara, gira, taca)
    falso_pov(c, q, pose_n, prog=prog)
    x, y = X_POV, Y_POV
    pf = getattr(c, "_pts_frente", None) or {}
    solta, bate = POV_SOLTA, POV_BATE
    if pf:  # (de frente: o golpe sai na hora que ele solta, e voa 14 quadros até a câmera)
        if pf.get("soltou") and getattr(c, "_soltou_t", None) is None:
            c._soltou_t = t
        if getattr(c, "_soltou_t", None) is None:
            solta = bate = 999
        else:
            solta, bate = c._soltou_t, c._soltou_t + (20 if tipo in ("tiros", "espinhos") else 14)  # (3 tiros: espera a 3ª bala)
    if tipo == "laser":  # (o laser sai dos olhos: a mira acende e o RAIO vem)
        cb = ponto_ficha(c, c.falso, pose_n, "cb", ESC_POV, x, y, -1)
        olho = pf.get("olhos") or (cb[0] - 30, cb[1] + 8)
        if POV_MIRA <= t < POV_SOLTA and not pf:
            brilho(q, (int(olho[0]), int(olho[1])), 30 + (t - POV_MIRA) * 3, (255, 40, 40), 230)
        elif pf and t >= solta:  # (de frente: o raio é do próprio desenho; aqui só o clarão chegando na câmera)
            u = min(1, (t - solta) / (bate - solta))
            brilho(q, (int(w * 0.5), int(h * 0.5)), int(40 + 300 * u), (255, 80, 60), int(120 + 100 * u))
        elif not pf and t >= POV_SOLTA:
            u = min(1, (t - POV_SOLTA) / (POV_BATE - POV_SOLTA))
            ponta = (olho[0] + (w * 0.5 - olho[0]) * min(1, u * 2.5), olho[1] + (h * 0.5 - olho[1]) * min(1, u * 2.5))
            grosso = int(8 + 120 * u ** 2)
            pygame.draw.line(q, (160, 0, 10), olho, ponta, grosso + 16)
            pygame.draw.line(q, (255, 50, 40), olho, ponta, grosso)
            pygame.draw.line(q, (255, 220, 210), olho, ponta, max(2, grosso // 3))
            brilho(q, (int(ponta[0]), int(ponta[1])), int(40 + 260 * u), (255, 80, 60), 200)
    elif t >= solta:
        u = min(1, (t - solta) / (bate - solta))
        mao = pf.get("mao") or ponto_ficha(c, c.falso, "especial", "mf", ESC_POV, x, y, -1)
        ox, oy = mao[0] + (w * 0.5 - mao[0]) * u, mao[1] + (h * 0.5 - mao[1]) * u
        if tipo == "lobo" and pf:  # (de frente: o LOBO de pixel art do Tamer dá o BOTE na câmera, subindo)
            import frente as fr
            oy -= 30 * math.sin(u * math.pi)
            fr.lobo_de_frente(q, ox, oy, fr.UNID * ESC_FRENTE * (1 + 3 * u ** 2), t, fr.cores_lobo(c.falso),
                              boca=u * 3, garras=u * 1.5)
        elif tipo == "ancora" and pf:  # (de frente: a ÂNCORA vem com as unhas pra câmera, puxando a CORRENTE da mão)
            import frente as fr
            esc_a = fr.UNID * ESC_FRENTE * (1 + 4 * u ** 2)
            for i in range(1, 12):  # a corrente (elos em pixel, crescendo perto da âncora)
                v = i / 12
                cx = mao[0] + (ox - mao[0]) * v
                cy = mao[1] + 12 + (oy - mao[1] - 12) * v + math.sin(v * math.pi) * 20 * (1 - u)
                tam_e = fr.UNID * ESC_FRENTE * 0.75 * (1 + 3 * (v * u) ** 2)
                pygame.draw.rect(q, (16, 14, 20), (cx - tam_e / 2 - 2, cy - tam_e / 2 - 2, tam_e + 4, tam_e + 4))
                pygame.draw.rect(q, (150, 170, 176) if i % 2 else (90, 104, 112), (cx - tam_e / 2, cy - tam_e / 2, tam_e, tam_e))
            fr.ancora_voando(q, ox, oy, esc_a, c.falso)
        elif tipo == "cartola" and pf:  # (de frente: a CARTOLA de pixel do John vem DE LADO, girando como disco)
            import frente as fr
            fr.cartola_voando(q, ox, oy, fr.UNID * ESC_FRENTE * (1 + 4 * u ** 2), t * 0.7, c.falso)
        elif tipo == "neve" and pf:  # (de frente: a BOLA DE NEVE de pixel do Frigantus crescendo até a câmera)
            import frente as fr
            fr.bola_de_neve(q, ox, oy, fr.UNID * ESC_FRENTE * 1.05 * (1 + 5 * u ** 2), t)
        elif tipo == "ar" and pf:  # (de frente: a ONDA DE AR em pixel, do giro de pião, subindo pro meio da tela)
            import frente as fr
            fr.onda_de_ar(q, ox, oy, fr.UNID * ESC_FRENTE * (0.8 + 4 * u ** 2), t)
        elif tipo in ("tiros", "espinhos") and pf:
            pass  # (de frente: as balas/espinhos saem um a cada TIRO, logo abaixo)
        else:
            objeto_vindo(c, q, tipo, ox, oy, 40 + 600 * u ** 2.2, t, c.falso)
        if tipo == "tiros":
            for i in range(3):
                if solta + i * 4 <= t < solta + i * 4 + 3:
                    brilho(q, (int(mao[0]), int(mao[1])), 70, (255, 230, 120), 255)
    if tipo == "espinhos" and pf:  # (de frente: cada TIRO tira um ESPINHO de fogo da crista, vindo na câmera)
        import frente as fr
        esp = c.__dict__.setdefault("_balas", [])
        if pf.get("tiro") and (not esp or t - esp[-1][0] > 2):
            esp.append((t, pf.get("mao") or (w * 0.5, h * 0.3)))
        for n_, (t0, (bx, by)) in enumerate(esp):
            voo = (t - t0) / 10
            if 0 <= voo <= 1.1:
                lado = 1 if n_ % 2 else -1
                ex = bx + (w * 0.5 + lado * (90 + n_ * 26) - bx) * voo  # (vindo pro meio da tela, espalhados)
                ey = by + (h * 0.48 + (n_ % 3 - 1) * 70 - by) * voo
                fr.espinho_voando(q, ex, ey, fr.UNID * ESC_FRENTE * (0.5 + 2.5 * voo ** 2), c.falso, lado)
    if tipo == "tiros" and pf:  # (de frente: cada TIRO do desenho solta uma bala vindo na câmera)
        balas = c.__dict__.setdefault("_balas", [])
        if pf.get("tiro") and (not balas or t - balas[-1][0] > 2):
            balas.append((t, pf.get("mao") or (w * 0.5, h * 0.5)))
        for t0, (bx, by) in balas:
            voo = (t - t0) / 8
            if 0 <= voo <= 1.1:
                rr = 2 + 60 * voo ** 1.6
                px, py = bx + (w * 0.5 - bx) * voo, by + (h * 0.5 - by) * voo
                pygame.draw.circle(q, (40, 36, 30), (int(px), int(py)), int(rr) + 2)
                pygame.draw.circle(q, (200, 160, 60), (int(px), int(py)), int(rr))
                pygame.draw.circle(q, (255, 230, 150), (int(px - rr * 0.3), int(py - rr * 0.3)), max(1, int(rr * 0.3)))
    if POV_MIRA <= t < POV_SOLTA and t % 3 == 0:
        c.tremor = max(c.tremor, 2)
    palpebras(q, 0.9)


def cacos(n=26, semente=5):
    """Os CACOS do vidro (triângulos entre as rachaduras que saem do meio), cada um com a sua queda."""
    w, h = LARGURA, ALTURA
    rnd = random.Random(semente)
    cx, cy = w * 0.5, h * 0.5
    angs = sorted(rnd.uniform(0, math.tau) for _ in range(12))
    aneis = (0, 70, 190, 380, 900)
    lista = []
    for i, a0 in enumerate(angs):
        a1 = angs[(i + 1) % len(angs)] + (math.tau if i == len(angs) - 1 else 0)
        for j in range(len(aneis) - 1):
            r0, r1 = aneis[j] * rnd.uniform(0.85, 1.15), aneis[j + 1] * rnd.uniform(0.85, 1.15)
            pts = [(cx + math.cos(a0) * r0, cy + math.sin(a0) * r0), (cx + math.cos(a0) * r1, cy + math.sin(a0) * r1),
                   (cx + math.cos(a1) * r1, cy + math.sin(a1) * r1), (cx + math.cos(a1) * r0, cy + math.sin(a1) * r0)]
            lista.append((pts, rnd.uniform(-6, 6), rnd.uniform(-8, -2), rnd.uniform(-8, 8), j * 3 + rnd.uniform(0, 4)))
    return lista


CACOS = cacos()


def v4_vidro(c, q, t, k):
    """4) O VIDRO QUEBRA: a tela RACHA inteira... os CACOS caem (com o pedaço da imagem em cada um) e mostram o
    preto... TRAFO VENCEU!"""
    w, h = q.get_size()
    tipo, efeito = golpe_do(c.falso)
    if t == 0 or not hasattr(c, "_foto"):  # (a última imagem antes de quebrar: é ela que vira os cacos)
        foto = pygame.Surface((w, h))
        pov_fundo(c, foto, 80 + POV_BATE)
        tonto(foto, 80 + POV_BATE, 0.45)
        falso_pov(c, foto, "especial", prog=1.0)
        cor = COR_GOLPE.get(tipo)
        if cor:  # (o golpe que bateu deixa a cor dele no vidro)
            sup = pygame.Surface((w, h), pygame.SRCALPHA)
            sup.fill((*cor, 120))
            foto.blit(sup, (0, 0))
        c._foto = foto
    q.fill((0, 0, 0))
    solta = 14
    for pts, vx, vy, giro, atraso in CACOS:
        u = max(0.0, t - solta - atraso)
        dx, dy = vx * u, vy * u + 0.9 * u * u
        if dy > h + 200:
            continue
        r = pygame.Rect(min(p[0] for p in pts), min(p[1] for p in pts), 1, 1)
        r.width = int(max(p[0] for p in pts) - r.x) + 2
        r.height = int(max(p[1] for p in pts) - r.y) + 2
        r = r.clip(q.get_rect())
        if r.width < 2 or r.height < 2:
            continue
        mascara = pygame.Surface(r.size, pygame.SRCALPHA)
        local = [(p[0] - r.x, p[1] - r.y) for p in pts]
        pygame.draw.polygon(mascara, (255, 255, 255, 255), local)
        pedaco = mascara.copy()
        pedaco.blit(c._foto, (0, 0), r, special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.polygon(pedaco, (240, 248, 255), local, 2)  # (a borda brilhando do caco)
        if u > 0 and giro:
            pedaco = pygame.transform.rotate(pedaco, giro * u)
        q.blit(pedaco, (r.centerx + dx - pedaco.get_width() / 2, r.centery + dy - pedaco.get_height() / 2))
    if t < solta:  # as RACHADURAS se espalhando (antes de cair)
        for pts, *_ in CACOS:
            pygame.draw.lines(q, (245, 250, 255), True, pts, 2)
        brilho(q, (w // 2, h // 2), 120 + t * 10, (255, 255, 255), 200 - t * 10)
    if t == 0:
        c.tremor, c.inverte = 26, 3
    if t < 12:
        texto_pow(q, "CRASH!!", (int(w * 0.5), int(h * 0.2)), 90, (240, 248, 255), t)
    if t >= 34:  # TRAFO VENCEU!
        from efeitos import texto_grande
        u = min(1, (t - 34) / 10)
        texto_grande(q, "TRAFO VENCEU!", int(70 + 30 * (1 - u)), (255, 220, 120), (w // 2, h // 2), contorno=(80, 30, 10))
        if t >= 44:
            faixa_nome(q, "TRAFO", "QUEM SERÁ O PRÓXIMO?", COR_NOME, (t - 44) / 30)


PLANOS_DESFILE = [
    (50, v1_apagado, {0: ("vento", 0.3), 30: ("vento", 0.6)}),
    (34, v2_pula, {10: ("queda", 1.0), 11: ("terra", 0.6)}),
    (40, v3_ataca, {8: ("carga", 0.5), 22: ("vento", 0.8)}),
    (100, v4_vidro, {0: ("quebra", 1.0), 1: ("ko", 0.8), 34: ("confirma", 0.8)}),
]


def vitoria(ficha, titulo="", oponente=None):
    c = CenaAnime(ficha, PLANOS_DESFILE, titulo, oponente)
    c.falso = sortear_falso(oponente)
    return c
