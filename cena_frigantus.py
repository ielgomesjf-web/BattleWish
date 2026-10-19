"""CENAS DE ANIME do FRIGANTUS (loja): a entrada O BARRIL e a vitória GUERRA DE NEVE.

Tudo no MAPA da luta, com a SKIN dele e o OPONENTE de verdade (com a skin dele). O Frigantus aparece com o
desenho do jogo (montado na escala do jogo e a câmera amplia); só os closes de detalhe (olho, caçador, barril,
bola de neve) são ilustrados.
"""
import math
import random

import pygame

import cutscene
from cena_max import cores_do_mapa, chao_perto, fundo_desfocado, para_tela
from cenas_anime import CenaAnime, faixa_nome, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho
import frigantus

BORDA = (16, 18, 26)
XF, XO, XH = LARGURA * 0.3, LARGURA * 0.74, LARGURA * 0.52  # o Frigantus, o oponente e o caçador, no mapa
NEVE, NEVE_SOMBRA = (246, 250, 255), (196, 214, 238)
AZUL_NOME = (90, 170, 230)


def pal(c):
    """As cores do Frigantus na SKIN que ele está usando."""
    return {k: c.cor(k, v) for k, v in frigantus.PALETA.items()}


def pose(c, nome):
    return c.l.poses.get(nome) or c.l.poses["parado"]


def flocos(q, t, n=60, vel=1.0, semente=5, alfa=230, tam=2):
    """Neve caindo (ou o frio que ele traz com ele) na tela toda."""
    w, h = q.get_size()
    rnd = random.Random(semente)
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(n):
        x = (rnd.uniform(0, w) + math.sin(t * 0.05 + i) * 20) % w
        y = (rnd.uniform(0, h) + t * vel * rnd.uniform(1.0, 2.2)) % h
        pygame.draw.circle(sup, (255, 255, 255, alfa), (int(x), int(y)), tam + i % 2)
    q.blit(sup, (0, 0))


def bafo(q, x, y, t, d=1, e=1.0, n=4):
    """O BAFO GELADO saindo da boca (nuvenzinhas que crescem e somem)."""
    for i in range(n):
        u = (t * 1.4 + i * 9) % 36
        sup = pygame.Surface((int(60 * e) + 2, int(60 * e) + 2), pygame.SRCALPHA)
        pygame.draw.circle(sup, (230, 244, 255, int(170 * (1 - u / 36))), (sup.get_width() // 2, sup.get_height() // 2),
                           int((5 + u * 0.5) * e))
        q.blit(sup, (int(x + d * u * 1.6 * e - sup.get_width() / 2), int(y - u * 0.5 * e - sup.get_height() / 2)))


# =====================================================================
# O CAÇADOR (personagem novo da cena, inventado) — no tamanho do jogo ou GRANDE pro close
# =====================================================================
CASACO, CASACO_ESC, CALCA, BOTA, PELE_H, CHAPEU, PELUCIA, BIGODE = (
    (78, 108, 64), (52, 74, 44), (96, 74, 52), (40, 30, 24), (236, 190, 150), (120, 80, 42), (214, 196, 166), (92, 60, 38))

POSES_CACADOR = {  # (unidades: o pé no (0, 0), pra cima é negativo; d=1 olhando pra direita)
    "anda1": dict(qd=(0, -46), ombro=(8, -78), cb=(14, -92), j1=(12, -24), p1=(18, -2), j2=(-8, -24), p2=(-16, 0),
                  m1=(30, -86), m2=(20, -74), cabo=((-16, -58), (44, -118)), rede="alto"),
    "anda2": dict(qd=(0, -44), ombro=(8, -76), cb=(14, -90), j1=(6, -24), p1=(4, -2), j2=(-2, -26), p2=(-4, -4),
                  m1=(30, -84), m2=(20, -72), cabo=((-16, -56), (44, -116)), rede="alto"),
    "susto": dict(qd=(0, -12), ombro=(-10, -42), cb=(-14, -56), j1=(16, -24), p1=(30, -4), j2=(10, -28), p2=(24, -2),
                  m1=(-28, -72), m2=(6, -74), cabo=((-50, -2), (14, -4)), rede="chao"),
}


def cacador(q, x, y, e, d=1, pose="anda1", medo=0.0, giro=0.0):
    """O caçador (gorro de pelúcia, bigode, casaco verde e a REDE no cabo). e = tamanho (1 = escala do jogo)."""
    P = POSES_CACADOR[pose]
    lado = int(170 * e)
    sup = pygame.Surface((lado * 2, lado * 2), pygame.SRCALPHA)
    ox, oy = lado, lado + 40 * e

    def T(p):
        return ox + p[0] * e * d, oy + p[1] * e

    def membro(a, b, c_, cor, g):
        for cor_, gg in ((BORDA, g + 4), (cor, g)):
            pygame.draw.lines(sup, cor_, False, [T(a), T(b), T(c_)], max(2, int(gg * e)))
            for p in (a, b, c_):
                pygame.draw.circle(sup, cor_, T(p), max(1, int(gg * e / 2)))

    if P["rede"] == "chao":  # a rede caída
        a, b = P["cabo"]
        pygame.draw.line(sup, BORDA, T(a), T(b), max(2, int(5 * e)))
        pygame.draw.line(sup, (150, 110, 60), T(a), T(b), max(1, int(3 * e)))
        r = pygame.Rect(0, 0, 40 * e, 12 * e)
        r.center = T((b[0] + 14, b[1]))
        pygame.draw.ellipse(sup, (220, 210, 180), r, max(1, int(2 * e)))
    membro(P["qd"], P["j2"], P["p2"], CALCA, 9)  # (a perna de trás)
    pygame.draw.ellipse(sup, BOTA, (*T((P["p2"][0] - (5 if d > 0 else 9), P["p2"][1] - 6)), 14 * e, 8 * e))
    tronco = [T((P["qd"][0] - 11, P["qd"][1] + 4)), T((P["qd"][0] + 11, P["qd"][1] + 4)),
              T((P["ombro"][0] + 12, P["ombro"][1])), T((P["ombro"][0] - 12, P["ombro"][1] - 2))]
    pygame.draw.polygon(sup, BORDA, tronco)
    pygame.draw.polygon(sup, CASACO, tronco, 0)
    pygame.draw.polygon(sup, BORDA, tronco, max(1, int(2 * e)))
    pygame.draw.line(sup, CASACO_ESC, T(P["qd"]), T(P["ombro"]), max(1, int(2 * e)))  # (o zíper)
    membro(P["qd"], P["j1"], P["p1"], CALCA, 9)
    pygame.draw.ellipse(sup, BOTA, (*T((P["p1"][0] - (5 if d > 0 else 9), P["p1"][1] - 6)), 14 * e, 8 * e))
    membro(P["ombro"], ((P["ombro"][0] + P["m2"][0]) / 2 - 4, (P["ombro"][1] + P["m2"][1]) / 2 + 6), P["m2"], CASACO, 7)
    cb = P["cb"]  # a CABEÇA: gorro de pelúcia com abas, bigodão
    pygame.draw.circle(sup, BORDA, T(cb), int(12 * e))
    pygame.draw.circle(sup, PELE_H, T(cb), int(10.5 * e))
    olho = T((cb[0] + 4, cb[1] - 1))
    if medo > 0.5:
        pygame.draw.circle(sup, (255, 255, 255), olho, max(2, int(3.4 * e)))
        pygame.draw.circle(sup, BORDA, olho, max(1, int(1.2 * e)))
        pygame.draw.ellipse(sup, BORDA, (*T((cb[0] + 2, cb[1] + 5)), 5 * e, 6 * e))  # (boca de O)
    else:
        pygame.draw.line(sup, BORDA, (olho[0] - 2 * e, olho[1]), (olho[0] + 2 * e, olho[1] - e), max(1, int(1.6 * e)))
    pygame.draw.ellipse(sup, BIGODE, (*T((cb[0] + (1 if d > 0 else -11), cb[1] + 2)), 10 * e, 4 * e))
    gorro = pygame.Rect(0, 0, 26 * e, 14 * e)
    gorro.midbottom = T((cb[0], cb[1] - 3))
    pygame.draw.ellipse(sup, BORDA, gorro.inflate(4, 4))
    pygame.draw.ellipse(sup, CHAPEU, gorro)
    pygame.draw.rect(sup, PELUCIA, (gorro.x - e, gorro.bottom - 5 * e, gorro.w + 2 * e, 6 * e), border_radius=int(3 * e))
    aba = T((cb[0] - 9, cb[1] + 4))
    pygame.draw.ellipse(sup, PELUCIA, (aba[0] - 3 * e, aba[1] - 6 * e, 7 * e, 12 * e))
    if P["rede"] == "alto":  # o CABO com a REDE erguida
        a, b = P["cabo"]
        pygame.draw.line(sup, BORDA, T(a), T(b), max(2, int(5 * e)))
        pygame.draw.line(sup, (150, 110, 60), T(a), T(b), max(1, int(3 * e)))
        aro = T((b[0] + 6, b[1] - 8))
        r = int(15 * e)
        for i in range(5):  # a malha da rede (pendurada)
            ang = math.pi * 0.15 + i * math.pi * 0.17
            pygame.draw.line(sup, (220, 210, 180), (aro[0] + math.cos(ang) * r, aro[1] - math.sin(ang) * r * 0.4),
                             (aro[0] + math.cos(ang) * r * 0.5, aro[1] + r * 1.3), max(1, int(e)))
        pygame.draw.ellipse(sup, BORDA, (aro[0] - r, aro[1] - r * 0.4, r * 2, r * 0.8), max(2, int(3 * e)))
    membro(P["ombro"], ((P["ombro"][0] + P["m1"][0]) / 2 + 2, (P["ombro"][1] + P["m1"][1]) / 2 + 8), P["m1"], CASACO, 7)
    for m in (P["m1"], P["m2"]):
        pygame.draw.circle(sup, BORDA, T(m), int(4.5 * e))
        pygame.draw.circle(sup, (90, 70, 50), T(m), int(3.5 * e))  # (luvas)
    if giro:
        sup = pygame.transform.rotate(sup, giro)
    q.blit(sup, (int(x - sup.get_width() / 2), int(y - sup.get_height() / 2 - (40 * e if not giro else 50 * e))))


def cacador_rosto(q, cx, cy, e, medo, t):
    """O CLOSE no rosto do caçador: sorrisinho malandro (medo 0) ... olhão arregalado e suando (medo 1)."""
    def P(x, y):
        return int(cx + x * e), int(cy + y * e)

    pygame.draw.ellipse(q, BORDA, (*P(-26, 14), int(52 * e), int(60 * e)))  # (gola do casaco)
    pygame.draw.ellipse(q, CASACO, (*P(-24, 16), int(48 * e), int(56 * e)))
    pygame.draw.circle(q, BORDA, P(0, 0), int(23 * e))
    pygame.draw.circle(q, PELE_H, P(0, 0), int(21 * e))
    pygame.draw.circle(q, (246, 160, 140), P(-11, 6), int(4 * e))  # bochechas vermelhas de frio
    pygame.draw.circle(q, (246, 160, 140), P(13, 6), int(4 * e))
    for lado in (-1, 1):  # OLHOS
        ox = 8 * lado
        if medo < 0.5:  # (apertadinhos, malandros)
            pygame.draw.arc(q, BORDA, (*P(ox - 5, -6), int(10 * e), int(8 * e)), 0.2, math.pi - 0.2, max(2, int(1.6 * e)))
            pygame.draw.line(q, BORDA, P(ox - 6, -11 + lado * 1), P(ox + 5, -10 - lado * 2), max(2, int(1.8 * e)))
        else:
            pygame.draw.circle(q, BORDA, P(ox, -4), int(7 * e))
            pygame.draw.circle(q, (255, 255, 255), P(ox, -4), int(6 * e))
            pygame.draw.circle(q, BORDA, P(ox + math.sin(t * 2) * 0.6, -4), max(2, int(1.6 * e)))
            pygame.draw.line(q, BORDA, P(ox - 6, -14 - lado * 2), P(ox + 5, -13 + lado * 2), max(2, int(1.8 * e)))
    pygame.draw.circle(q, BORDA, P(0, 4), int(4.4 * e))  # nariz
    pygame.draw.circle(q, (240, 170, 140), P(0, 4), int(3.6 * e))
    if medo < 0.5:  # boca: o sorrisinho...
        pygame.draw.arc(q, BORDA, (*P(-9, 4), int(18 * e), int(10 * e)), math.pi + 0.3, math.tau - 0.3, max(2, int(1.8 * e)))
    else:  # ...ou o grito
        pygame.draw.ellipse(q, BORDA, (*P(-5, 10), int(10 * e), int(12 * e)))
        pygame.draw.ellipse(q, (150, 40, 40), (*P(-3, 13), int(6 * e), int(7 * e)))
    for lado in (-1, 1):  # o BIGODÃO
        pygame.draw.ellipse(q, BORDA, (*P(-1 if lado > 0 else -15, 6), int(16 * e), int(7 * e)))
        pygame.draw.ellipse(q, BIGODE, (*P(0 if lado > 0 else -14, 6.6), int(14 * e), int(5.6 * e)))
    gorro = pygame.Rect(0, 0, int(52 * e), int(30 * e))  # GORRO de pelúcia com as abas
    gorro.midbottom = P(0, -12)
    pygame.draw.ellipse(q, BORDA, gorro.inflate(6, 6))
    pygame.draw.ellipse(q, CHAPEU, gorro)
    pygame.draw.rect(q, BORDA, (gorro.x - 3 * e, gorro.bottom - 10 * e, gorro.w + 6 * e, 12 * e), border_radius=int(6 * e))
    pygame.draw.rect(q, PELUCIA, (gorro.x - 2 * e, gorro.bottom - 9 * e, gorro.w + 4 * e, 10 * e), border_radius=int(5 * e))
    for lado in (-1, 1):
        pygame.draw.ellipse(q, BORDA, (*P(lado * 22 - 7, -8), int(14 * e), int(26 * e)))
        pygame.draw.ellipse(q, PELUCIA, (*P(lado * 22 - 6, -7), int(12 * e), int(24 * e)))
    if medo > 0.5:  # gotas de suor
        for i, (sx, sy) in enumerate(((24, -16), (28, -4), (-26, -12))):
            yy = sy + ((t * 0.8 + i * 7) % 14)
            pygame.draw.polygon(q, (150, 210, 255), [P(sx, yy - 4), P(sx + 2.2, yy + 1), P(sx - 2.2, yy + 1)])
            pygame.draw.circle(q, (150, 210, 255), P(sx, yy + 1), int(2.3 * e))


# =====================================================================
# Objetos: o BARRIL e a BOLA DE NEVE
# =====================================================================
def barril(q, x, y, e, ang=0.0):
    """O barril de madeira com os aros de ferro (e = tamanho; 1 = do jogo). ang em graus."""
    w, h = int(34 * e), int(42 * e)
    sup = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
    r = pygame.Rect(4, 4, w, h)
    pygame.draw.rect(sup, BORDA, r, border_radius=int(10 * e))
    pygame.draw.rect(sup, (150, 96, 44), r.inflate(-4, -4), border_radius=int(9 * e))
    for i in range(1, 4):  # as tábuas
        xx = r.x + r.w * i / 4
        pygame.draw.line(sup, (110, 68, 30), (xx, r.y + 4), (xx, r.bottom - 4), max(1, int(1.4 * e)))
    pygame.draw.rect(sup, (190, 130, 70), (r.x + 4 * e, r.y + 4, 4 * e, r.h - 8), border_radius=int(2 * e))  # (luz)
    for f in (0.22, 0.78):
        yy = r.y + r.h * f
        pygame.draw.line(sup, BORDA, (r.x, yy), (r.right, yy), max(2, int(4 * e)))
        pygame.draw.line(sup, (120, 124, 134), (r.x + 2, yy - e * 0.5), (r.right - 2, yy - e * 0.5), max(1, int(2.4 * e)))
    if ang:
        sup = pygame.transform.rotate(sup, ang)
    q.blit(sup, (int(x - sup.get_width() / 2), int(y - sup.get_height() / 2)))


def bola_neve(q, x, y, r, giro=0.0):
    """A BOLA DE NEVE (com sombra, brilho e uns pedaços rolando)."""
    r = max(2, int(r))
    pygame.draw.circle(q, (110, 130, 160), (int(x), int(y)), r + max(2, r // 18))
    pygame.draw.circle(q, NEVE, (int(x), int(y)), r)
    pygame.draw.circle(q, NEVE_SOMBRA, (int(x + r * 0.25), int(y + r * 0.3)), int(r * 0.62))
    pygame.draw.circle(q, NEVE, (int(x - r * 0.08), int(y - r * 0.08)), int(r * 0.6))
    for i in range(6):  # os pedaços de neve grudados (giram com a bola)
        a = giro + i * math.tau / 6
        px, py = x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62
        pygame.draw.circle(q, NEVE_SOMBRA, (int(px), int(py)), max(1, int(r * 0.1)))
    pygame.draw.circle(q, (255, 255, 255), (int(x - r * 0.38), int(y - r * 0.4)), max(1, int(r * 0.16)))


def monte_neve(q, x, y, larg, alt, t=0):
    """Um MONTE DE NEVE (com bolotas em cima)."""
    r = pygame.Rect(0, 0, larg, max(2, alt * 2))
    r.midbottom = (int(x), int(y + alt))
    pygame.draw.ellipse(q, (120, 140, 170), r.inflate(6, 6))
    pygame.draw.ellipse(q, NEVE, r)
    pygame.draw.ellipse(q, NEVE_SOMBRA, (r.x + larg * 0.1, r.centery, larg * 0.8, alt * 0.8))
    for i in range(4):
        pygame.draw.circle(q, NEVE, (int(r.x + larg * (0.25 + i * 0.17)), int(r.y + alt * 0.2 + (i % 2) * 4)),
                           max(2, int(alt * 0.3)))


# =====================================================================
# ENTRADA: O BARRIL
# =====================================================================
MONTE = (XF, CHAO)


def base_mapa(c, t, opo="parado"):
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, opo, 1.0, XO, CHAO)
    return base


def e1_espreita(c, q, t, k):
    """1) No MAPA: um monte de neve... e um CAÇADOR chegando na ponta do pé, com a rede erguida. O oponente olha."""
    base = base_mapa(c, t)
    barril(base, XF + 70, CHAO - 21, 1.0)
    monte_neve(base, XF, CHAO, 150, 54, t)
    hx = XF + 270 - 140 * suave(k)
    cacador(base, hx, CHAO, 1.0, -1, "anda1" if (t // 10) % 2 else "anda2")
    for i in range(int(k * 5)):  # as pegadas dele
        pygame.draw.ellipse(base, (60, 50, 50), (XF + 280 - i * 28, CHAO + 4 + (i % 2) * 5, 12, 5))
    flocos(base, t, 40, 0.8)
    c.mapa_frente(base, t)
    c.camera(q, base, (XF + 215 - 15 * k, CHAO - 110), 1.6, pixel=True)
    if 10 < t:
        texto_pow(q, "pé ante pé...", (int(q.get_width() * 0.7), int(q.get_height() * 0.22)), 30, (240, 240, 250),
                  t - 10, giro=0.05)


def e2_rosto_cacador(c, q, t, k):
    """2) CLOSE no caçador: sorrisinho malandro (achou um yeti dormindo!)."""
    w, h = q.get_size()
    fundo_desfocado(c, q, t, (XH, CHAO - 100), 2.0, 30)
    cacador_rosto(q, w * 0.52 - 30 * k, h * 0.52, 7.0 + 0.8 * k, 0.0, t)
    if t > 10:
        texto_pow(q, "HEHEHE...", (int(w * 0.24), int(h * 0.24)), 40, (255, 230, 150), t - 10, giro=0.08)


def frig_olho(c, q, w, h, abre, t):
    """O close no OLHO do Frigantus DENTRO do monte de neve: tudo escuro (só a fresta de neve em volta)...
    o olho pequeno e fundo ABRE e ACENDE, e a luz gelada mostra a sobrancelha grossa e o pelo."""
    p = pal(c)
    luz = suave(min(1, max(0, abre - 0.2) / 0.8))  # (quanto o brilho do olho ilumina em volta)

    def esc(cor, f):
        return tuple(int(v * f) for v in cor)

    q.fill((14, 18, 32))
    cx, cy = w * 0.5, h * 0.53
    f_pelo = 0.16 + 0.5 * luz
    rnd = random.Random(2)
    for i in range(120):  # o PELO em volta (aparece com a luz do olho)
        a = rnd.uniform(0, math.tau)
        d = rnd.uniform(140, 520)
        x, y = cx + math.cos(a) * d * 1.3, cy + math.sin(a) * d * 0.7
        comp = rnd.uniform(50, 110)
        perto = max(0.3, 1 - d / 600)
        cor = esc(p["m"] if i % 3 else p["M"], f_pelo * perto)
        pygame.draw.line(q, cor, (x, y), (x + comp * 0.25, y + comp), 12)
    face = pygame.Rect(0, 0, 520, 300)  # a PELE cinza do rosto
    face.center = (int(cx), int(cy + 30))
    pygame.draw.ellipse(q, esc(p["p"], 0.18 + 0.45 * luz), face)
    pygame.draw.ellipse(q, esc(p["p"], 0.08 + 0.2 * luz), (cx - 130, cy - 56, 260, 120))  # (o olho FUNDO)
    franze = 24 * luz
    bro = [(cx - 260, cy - 96), (cx - 20, cy - 132 + franze), (cx + 250, cy - 112 + franze * 0.4),
           (cx + 240, cy - 64 + franze * 0.6), (cx + 30, cy - 60 + franze), (cx - 250, cy - 50)]
    pygame.draw.polygon(q, esc(p["m"], 0.2 + 0.55 * luz), bro)  # a SOBRANCELHA grossa
    pygame.draw.lines(q, esc(p["c"], 0.3 + 0.7 * luz), False, bro[3:], 4)  # (a borda de baixo, iluminada pelo olho)
    for i in range(8):
        x = cx - 220 + i * 58
        pygame.draw.line(q, esc(p["M"], 0.2 + 0.5 * luz), (x, cy - 112 + franze * 0.5), (x + 28, cy - 70 + franze * 0.7), 5)
    aberto = 56 * suave(abre)
    if aberto > 2:
        brilho(q, (int(cx + 6), int(cy)), int(60 + 160 * luz), p["c"], int(60 + 110 * luz))
        pygame.draw.ellipse(q, (6, 6, 12), (cx - 68, cy - aberto / 2, 136, aberto))
        rr = max(3, int(min(aberto, 50) * 0.5))
        pygame.draw.circle(q, p["c"], (int(cx + 6), int(cy)), rr)
        pygame.draw.circle(q, (255, 255, 255), (int(cx + 6), int(cy)), max(2, int(rr * 0.45)))
        pygame.draw.line(q, (255, 255, 255), (cx + 6 - 160 * luz, cy), (cx + 6 + 160 * luz, cy), 2)  # (o risco de luz)
    pygame.draw.ellipse(q, (6, 6, 12), (cx - 74, cy - max(aberto / 2, 2) - 4, 148, max(aberto, 4) + 8), 5)
    for borda_y, lado in ((0, 1), (h, -1)):  # a FRESTA do monte de neve (em cima e embaixo)
        for i in range(12):
            x = i * w / 11
            r_ = 60 + (i * 37) % 40
            pygame.draw.circle(q, esc(NEVE_SOMBRA, 0.35 + 0.4 * luz), (int(x), int(borda_y + lado * (r_ * 0.2))), r_)
    for i in range(10):  # a neve escorregando quando ele abre o olho
        if abre > 0.3:
            u = (abre - 0.3) / 0.7
            pygame.draw.circle(q, esc(NEVE, 0.4 + 0.5 * luz), (int(cx - 260 + i * 56), int(cy - 160 + u * (90 + i * 20))), 6 + i % 3 * 3)


def e3_olho(c, q, t, k):
    """3) Debaixo da neve... um OLHO se abre. (silêncio)"""
    w, h = q.get_size()
    frig_olho(c, q, w, h, 0 if t < 12 else min(1, (t - 12) / 8), t)
    if t > 22:
        c.tremor = max(c.tremor, 2)


def e4_ruge(c, q, t, k):
    """4) Ele EXPLODE do monte rugindo: neve voando pra todo lado, linhas de impacto, o caçador cai sentado."""
    w, h = q.get_size()
    base = base_mapa(c, t + 40, "defesa" if t > 4 else "parado")
    barril(base, XF + 70, CHAO - 21, 1.0)
    p = misturar(pose(c, "agachado"), pose(c, "fr_ruge"), suave(min(1, t / 6)))
    c.por(base, p, 1.0, XF, CHAO, 1, guardar=False)
    cacador(base, XF + 150, CHAO, 1.0, -1, "susto", medo=1.0)
    rnd = random.Random(9)
    for i in range(22):  # os pedaços do monte voando
        vx, vy = rnd.uniform(-9, 9), rnd.uniform(-14, -5)
        px, py = XF + vx * t, CHAO - 40 + vy * t + 0.45 * t * t
        if py < CHAO:
            pygame.draw.circle(base, NEVE, (int(px), int(py)), 3 + i % 4)
    poeira(base, XF, CHAO, min(1, t / 26), cor=(236, 244, 255), larg=140, semente=4)
    cb = c.ponto(p, "cb", 1.0, XF, CHAO)
    bafo(base, cb[0] + 20, cb[1] + 14, t, 1, 1.2)
    c.mapa_frente(base, t + 40)
    centro, z = (XF + 40, CHAO - 120), 2.3 - 0.3 * suave(k)
    c.camera(q, base, centro, z, pixel=True)
    if t == 2:
        c.inverte, c.tremor = 3, 22
    if t > 2:
        cutscene.linhas_velocidade(q, para_tela(centro, z, cb), (255, 255, 255), n=40, r_dentro=200, grossura=6,
                                   semente=t // 3, alfa=150)
        texto_pow(q, "GRRRAAAH!!", (int(w * 0.66), int(h * 0.24)), 62, (170, 220, 255), t - 2, giro=0.1)


def e5_arranca(c, q, t, k):
    """5) Câmera de BAIXO: ele arranca o BARRIL do chão e ergue em cima da cabeça."""
    base = base_mapa(c, t + 80, "parado")
    p = misturar(pose(c, "fr_soco_chao"), pose(c, "fr_arremessa"), suave(min(1, max(0, t - 6) / 10)))
    c.por(base, p, 1.0, XF, CHAO, 1, guardar=False)
    m1, m2 = c.ponto(p, "mt", 1.0, XF, CHAO), c.ponto(p, "mf", 1.0, XF, CHAO)
    bx, by = (m1[0] + m2[0]) / 2, (m1[1] + m2[1]) / 2 - 18
    if t < 6:
        bx, by = XF + 70, CHAO - 21
    barril(base, bx, by, 1.0, ang=0 if t < 6 else -10 * suave(min(1, (t - 6) / 10)))
    if 6 <= t < 14:  # os torrões saindo de onde ele arrancou
        for i in range(8):
            pygame.draw.circle(base, (90, 74, 56), (int(XF + 70 + (i - 4) * 6 * (t - 5)), int(CHAO - 4 - (t - 5) * (3 + i % 3))), 3)
    cb = c.ponto(p, "cb", 1.0, XF, CHAO)
    bafo(base, cb[0] + 18, cb[1] + 14, t, 1, 1.0)
    c.mapa_frente(base, t + 80)
    c.camera(q, base, (XF + 30, CHAO - 150 + 20 * k), 2.6, pixel=True)
    if t == 7:
        c.tremor = 8


def e6_barril_voa(c, q, t, k):
    """6) O BARRIL vem GIRANDO pra cima da câmera... e BONK! (quadro de impacto)."""
    w, h = q.get_size()
    fundo_desfocado(c, q, t, (XH, CHAO - 120), 1.6, 20)
    cutscene.linhas_velocidade(q, (w * 0.5, h * 0.5), (255, 255, 255), n=50, r_dentro=160, grossura=8,
                               semente=t // 2, alfa=170)
    bate = 20
    if t < bate:
        u = t / bate
        barril(q, w * (0.2 + 0.3 * u), h * (0.4 + 0.1 * u), 1.0 + 11 * u ** 2, ang=t * 34)
        cacador_rosto(q, w * 0.5, h * 0.62, 3.5 + 2 * u, 1.0, t)
    else:
        if t == bate:
            c.inverte, c.tremor = 4, 24
        barril(q, w * 0.5, h * 0.5, 13, ang=bate * 34)
        texto_pow(q, "BONK!!", (int(w * 0.5), int(h * 0.3)), 96, (255, 210, 60), t - bate)
        for i in range(10):
            a = i * math.tau / 10
            pygame.draw.line(q, (255, 240, 180), (w / 2 + math.cos(a) * 260, h / 2 + math.sin(a) * 200),
                             (w / 2 + math.cos(a) * 420, h / 2 + math.sin(a) * 320), 8)


def e7_longe(c, q, t, k):
    """7) No MAPA, de longe: o caçador sai VOANDO até virar uma estrelinha no céu (PLIM!). O oponente acompanha."""
    w, h = q.get_size()
    c.mapa(q, t + 120)
    c.por_oponente(q, "parado", 1.0, XO, CHAO)
    c.por(q, "fr_joga", 1.0, XF, CHAO)
    u = min(1, t / 26)
    x0, y0 = XF + 150, CHAO - 40
    x1, y1 = x0 + (w * 0.92 - x0) * u, y0 - (y0 - 70) * math.sin(u * math.pi / 2)
    if u < 1:
        cacador(q, x1, y1, 1.0 - 0.8 * u, -1, "susto", medo=1.0, giro=t * 25)
        barril(q, x1 - 30 * (1 - u), y1 + 20, 1.0 - 0.8 * u, ang=t * 30)
    else:
        f = max(0, 1 - (t - 26) / 14)
        cutscene.estrela(q, (int(x1), int(y1)), 18 * f + 2, 6 * f + 1, 4, (255, 250, 200), giro=t * 0.2)
        if t < 40:
            texto_pow(q, "PLIM!", (int(x1 - 40), int(y1 + 50)), 30, (255, 250, 200), t - 26)
    flocos(q, t, 50, 0.8)
    c.mapa_frente(q, t + 120)


def e8_peito(c, q, t, k):
    """8) A POSE: bate no peito (UH-UH-UH!), o bafo gelado, a neve caindo... e entra o nome."""
    w, h = q.get_size()
    base = base_mapa(c, t + 160)
    nome = "fr_peito_a" if (t // 6) % 2 else "fr_peito_b"
    if t < 8:
        p = misturar(pose(c, "fr_joga"), pose(c, "fr_peito_a"), suave(t / 8))
    elif t > 40:
        p = misturar(pose(c, nome), pose(c, "fr_ruge"), suave(min(1, (t - 40) / 8)))
    else:
        p = pose(c, nome)
    c.por(base, p, 1.0, XF, CHAO, 1, guardar=False)
    cb = c.ponto(p, "cb", 1.0, XF, CHAO)
    bafo(base, cb[0] + 18, cb[1] + 14, t, 1, 1.0)
    flocos(base, t, 50, 0.9, alfa=210)
    c.mapa_frente(base, t + 160)
    z = 1.8 + 0.3 * suave(min(1, t / 50))
    c.camera(q, base, (XF + 20, CHAO - 125), z, pixel=True)
    if 8 <= t < 40 and t % 6 == 0:
        c.tremor = max(c.tremor, 4)
    if 8 <= t < 40:
        texto_pow(q, "UH-UH-UH!", (int(w * 0.68), int(h * 0.26)), 46, (230, 240, 255), (t - 8) % 6, giro=0.12)
    if t >= 30:
        faixa_nome(q, "FRIGANTUS", "O GIGANTE DA NEVASCA.", AZUL_NOME, (t - 30) / 30)


PLANOS = [
    (44, e1_espreita, {0: ("vento", 0.5)}),
    (36, e2_rosto_cacador, {10: ("blip", 0.4)}),
    (32, e3_olho, {12: ("carga", 0.6)}),
    (40, e4_ruge, {2: ("uivo", 1.0), 4: ("explosao", 0.6)}),
    (30, e5_arranca, {7: ("terra", 0.7)}),
    (34, e6_barril_voa, {0: ("vento", 0.8), 20: ("ko", 0.9)}),
    (44, e7_longe, {0: ("queda", 0.3), 26: ("blip", 0.6)}),
    (62, e8_peito, {8: ("soco", 0.5), 14: ("soco", 0.5), 20: ("soco", 0.5), 26: ("soco", 0.5), 42: ("uivo", 0.7)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


# =====================================================================
# VITÓRIA: GUERRA DE NEVE
# =====================================================================
def raio_bola(t):
    return 10 + min(1, t / 40) * 34  # (a bola cresce rolando; 44 = do tamanho de um lutador deitado)


def v1_rola(c, q, t, k):
    """1) No MAPA: ele vai empurrando uma bola de neve, que cresce rolando (o derrotado caído lá na frente)."""
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    x = XF - 60 + 80 * k
    p = pose(c, ("andar1", "andar2", "andar3", "andar4")[(t // 7) % 4])
    r = raio_bola(t)
    bx = x + 70 + r
    for i in range(int(k * 8)):  # o rastro da bola no chão
        pygame.draw.line(base, NEVE, (bx - 20 - i * 12, CHAO), (bx - 28 - i * 12, CHAO), 6)
    c.por(base, p, 1.0, x, CHAO)
    bola_neve(base, bx, CHAO - r, r, giro=t * 0.15)
    flocos(base, t, 30, 0.6)
    c.mapa_frente(base, t)
    c.camera(q, base, (x + 110, CHAO - 80), 1.8, pixel=True)


def v2_chao(c, q, t, k):
    """2) CÂMERA NO CHÃO: a bola vem rolando pra cima da câmera, crescendo, levantando neve... e TAPA a tela."""
    w, h = q.get_size()
    hz = int(h * 0.5)
    if not hasattr(c, "_fundo_chao"):
        c._fundo_chao = pygame.Surface((w, h))
        fundo_desfocado(c, c._fundo_chao, 0, (LARGURA * 0.5, CHAO - h * 0.22), 1.6, 30)
    chao_perto(q, t, hz, cores=cores_do_mapa(c), fundo=c._fundo_chao)
    u = suave(k) ** 1.6
    r = 50 + u * w * 0.75
    by = hz + 20 + r * 0.92
    rnd = random.Random(t // 2)
    for i in range(14):  # a neve espirrando dos lados
        lado = -1 if i % 2 else 1
        px = w * 0.5 + lado * (r * 0.9 + rnd.uniform(0, 80) * (0.3 + u))
        py = by + r * 0.6 - rnd.uniform(0, 120) * (0.3 + u)
        pygame.draw.circle(q, NEVE, (int(px), int(py)), int(4 + 10 * u))
    bola_neve(q, w * 0.5, by - r * 0.15, r, giro=-t * 0.3)
    if t > 6:
        texto_pow(q, "RRRRUMBLE", (int(w * 0.3), int(h * 0.22)), 40, (230, 240, 255), (t - 6) % 8, giro=0.06)
    c.tremor = max(c.tremor, 3)


def v3_ergue(c, q, t, k):
    """3) Câmera de BAIXO: ele ergue a bola GIGANTE em cima da cabeça (contra o céu)."""
    base = c._tela_aux()
    c.mapa(base, t + 50)
    p = misturar(pose(c, "parado"), pose(c, "fr_arremessa"), suave(min(1, t / 16)))
    c.por(base, p, 1.0, XF, CHAO, 1, guardar=False)
    m1, m2 = c.ponto(p, "mt", 1.0, XF, CHAO), c.ponto(p, "mf", 1.0, XF, CHAO)
    r = raio_bola(40)
    bx = (m1[0] + m2[0]) / 2
    by = min(CHAO - r, (m1[1] + m2[1]) / 2 - r + 6)
    bola_neve(base, bx, by, r, giro=0.3)
    cb = c.ponto(p, "cb", 1.0, XF, CHAO)
    bafo(base, cb[0] + 18, cb[1] + 14, t, 1, 1.0)
    c.mapa_frente(base, t + 50)
    c.camera(q, base, (XF + 10, CHAO - 175 + 30 * (1 - suave(k))), 1.8 + 0.25 * suave(k), pixel=True)
    if t == 16:
        c.tremor = 6


def v4_sombra(c, q, t, k):
    """4) CLOSE no derrotado: a SOMBRA da bola cresce em cima dele... ele olha pra cima: !?"""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 90)
    c.por_oponente(base, "caido", 1.0, XO, CHAO)
    sombra = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)  # a SOMBRA da bola (no chão e em cima dele)
    r = 20 + 80 * suave(k)
    pygame.draw.ellipse(sombra, (0, 0, 20, int(60 + 110 * k)), (XO - r * 1.4, CHAO - 26 - r * 0.25, r * 2.8, r * 0.5 + 34))
    base.blit(sombra, (0, 0))
    c.mapa_frente(base, t + 90)
    centro, z = (XO, CHAO - 50), 2.6
    c.camera(q, base, centro, z, pixel=True)
    if k > 0.4:  # a bola chegando por cima (só a beirada)
        rb = 520
        bola_neve(q, w * 0.5, -rb + (k - 0.4) / 0.6 * 170, rb, giro=t * 0.1)
    if t > 12:
        texto_pow(q, "!?", (int(w * 0.55), int(h * 0.28)), 80, (255, 230, 120), t - 12)


def v5_joga(c, q, t, k):
    """5) ARREMESSA: a bola voa em arco... SPLAT! (quadro de impacto, neve pra todo lado)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 120)
    splat = 14
    c.por(base, "fr_joga" if t >= 3 else "fr_arremessa", 1.0, XF, CHAO)
    r = raio_bola(40)
    if t < splat:
        c.por_oponente(base, "caido", 1.0, XO, CHAO)
        u = t / splat
        x0, y0 = XF + 20, CHAO - 200
        bola_neve(base, x0 + (XO - x0) * u, y0 + (CHAO - r - y0) * u - math.sin(u * math.pi) * 90, r, giro=t * 0.4)
    else:
        if t == splat:
            c.inverte, c.tremor = 3, 20
        monte_neve(base, XO, CHAO, 170, int(60 * min(1, (t - splat) / 4)), t)
        rnd = random.Random(1)
        for i in range(30):
            vx, vy = rnd.uniform(-12, 12), rnd.uniform(-14, -3)
            u = t - splat
            px, py = XO + vx * u, CHAO - 40 + vy * u + 0.5 * u * u
            if py < CHAO:
                pygame.draw.circle(base, NEVE, (int(px), int(py)), 3 + i % 4)
        poeira(base, XO, CHAO, min(1, (t - splat) / 20), cor=(240, 246, 255), larg=200, semente=6)
    c.mapa_frente(base, t + 120)
    c.camera(q, base, ((XF + XO) / 2 + 40, CHAO - 120), 1.5, pixel=True)
    if t >= splat:
        texto_pow(q, "SPLAT!!", (int(w * 0.66), int(h * 0.3)), 84, (230, 244, 255), t - splat)


def v6_final(c, q, t, k):
    """6) O MONTE de neve com só os pés pra fora, mexendo... e ele bate no peito (e o nome)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 150)
    monte_neve(base, XO, CHAO, 170, 60, t)
    for i, dx in enumerate((48, 66)):  # os pés pra fora, mexendo
        yy = CHAO - 14 + math.sin(t * 0.5 + i * 2) * 4
        pygame.draw.ellipse(base, BORDA, (XO + dx - 1, yy - 7, 22, 14))
        pygame.draw.ellipse(base, (90, 60, 40), (XO + dx, yy - 6, 20, 12))
    nome = "fr_peito_a" if (t // 6) % 2 else "fr_peito_b"
    p = misturar(pose(c, "fr_joga"), pose(c, nome), suave(min(1, t / 8)))
    c.por(base, p, 1.0, XF + 40, CHAO, 1, guardar=False)
    cb = c.ponto(p, "cb", 1.0, XF + 40, CHAO)
    bafo(base, cb[0] + 18, cb[1] + 14, t, 1, 1.0)
    flocos(base, t, 50, 0.9, alfa=210)
    c.mapa_frente(base, t + 150)
    c.camera(q, base, ((XF + XO) / 2 + 40, CHAO - 110), 1.5, pixel=True)
    if 8 <= t < 50 and t % 6 == 0:
        c.tremor = max(c.tremor, 3)
    if 8 <= t < 50:
        texto_pow(q, "UH-UH-UH!", (int(w * 0.3), int(h * 0.22)), 44, (230, 240, 255), (t - 8) % 6, giro=-0.1)
    if t >= 40:
        faixa_nome(q, "FRIGANTUS", "GUERRA DE NEVE: VENCIDA.", AZUL_NOME, (t - 40) / 30)


PLANOS_GUERRA = [
    (48, v1_rola, {0: ("terra", 0.4)}),
    (36, v2_chao, {0: ("terra", 0.8)}),
    (40, v3_ergue, {4: ("carga", 0.6), 16: ("uivo", 0.6)}),
    (34, v4_sombra, {12: ("blip", 0.5)}),
    (34, v5_joga, {3: ("vento", 0.8), 14: ("puf", 1.0)}),
    (96, v6_final, {8: ("soco", 0.4), 20: ("soco", 0.4), 32: ("soco", 0.4), 44: ("soco", 0.4)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_GUERRA, titulo, oponente)
