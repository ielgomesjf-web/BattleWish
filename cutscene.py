"""Cutscenes: cenas desenhadas grandes, tipo anime, que aparecem no meio da luta (a luta para enquanto isso).

Uma cutscene é uma lista de "planos" (cenas). Cada plano tem uma duração (em quadros) e uma função
que desenha a tela inteira: desenha(tela, t, k), onde t = quadro dentro do plano e k = 0..1 (progresso).
"""
import math
import random

import numpy as np
import pygame

from config import *  # noqa: F401,F403

FAIXA = 46  # faixas pretas de cinema

# ---- jeito pixel art fosco ----
PIXEL_CENA = 5       # tamanho do pixel da cena (médio: ele escolheu o 5)
DESATURA = 0.66      # quanto tira da cor (0 = cor viva, 1 = preto e branco)
NIVEIS = 9           # quantos tons por cor (poucos = faixas de pixel art)
TOM = np.array([10, 6, 0], dtype=np.float32)  # puxadinha pro quente/terroso
_BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) / 16 - 0.5)


def pixel_fosco(q):
    """Transforma a cena desenhada grande em pixel art fosca (com pontilhado nas passagens de cor)."""
    w, h = LARGURA // PIXEL_CENA, ALTURA // PIXEL_CENA
    peq = pygame.transform.smoothscale(q, (w, h))
    a = pygame.surfarray.array3d(peq).astype(np.float32)
    cinza = (a @ np.array([0.30, 0.59, 0.11], dtype=np.float32))[..., None]
    a = cinza + (a - cinza) * (1 - DESATURA)
    a = a * 0.84 + 22 + TOM  # um tiquinho pálido
    passo = 255 / (NIVEIS - 1)
    bayer = np.tile(_BAYER, (w // 4 + 1, h // 4 + 1))[:w, :h, None] * passo * 0.45  # pontilhado só nas passagens
    a = np.round((a + bayer) / passo) * passo
    pygame.surfarray.blit_array(peq, np.clip(a, 0, 255).astype(np.uint8))
    return pygame.transform.scale(peq, (LARGURA, ALTURA))


class Cutscene:
    def __init__(self, planos):
        self.planos = planos
        self.t = 0
        self.total = sum(d for d, _ in planos)
        self.tremor = 0
        self.inverte = 0  # "quadro de impacto": cores invertidas por uns quadros

    @property
    def acabou(self):
        return self.t >= self.total

    def passo(self):
        import som
        if self.inverte > getattr(self, "_inv_antes", 0):
            som.tocar("explosao")
        if self.tremor >= 8 and self.tremor > getattr(self, "_tre_antes", 0):
            som.tocar("chute")
        self._inv_antes, self._tre_antes = self.inverte, self.tremor
        self.t += 1
        if self.tremor > 0:
            self.tremor -= 1
        if self.inverte > 0:
            self.inverte -= 1

    def desenhar(self, tela):
        if not hasattr(self, "_quadro"):
            self._quadro = pygame.Surface((LARGURA, ALTURA))
        q = self._quadro
        t = self.t
        for i, (dur, func) in enumerate(self.planos):
            if t < dur or i == len(self.planos) - 1:
                func(self, q, min(t, dur - 1), min(1.0, t / max(1, dur - 1)))
                inicio_plano = t
                break
            t -= dur
        q = pixel_fosco(q)
        ox = oy = 0
        if self.tremor:
            ox = random.randint(-self.tremor, self.tremor) // PIXEL_CENA * PIXEL_CENA
            oy = random.randint(-self.tremor, self.tremor) // PIXEL_CENA * PIXEL_CENA
        tela.fill(PRETO)
        if self.inverte:  # quadro de impacto (cores invertidas)
            branco = pygame.Surface((LARGURA, ALTURA))
            branco.fill(BRANCO)
            branco.blit(q, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            tela.blit(branco, (ox, oy))
        else:
            tela.blit(q, (ox, oy))
        if inicio_plano < 3:  # corte seco com um flash branco
            flash = pygame.Surface((LARGURA, ALTURA))
            flash.fill(BRANCO)
            flash.set_alpha(200 - inicio_plano * 70)
            tela.blit(flash, (0, 0))
        tela.fill(PRETO, (0, 0, LARGURA, FAIXA))
        tela.fill(PRETO, (0, ALTURA - FAIXA, LARGURA, FAIXA))


# =====================================================================
# Ferramentas de desenho estilo anime
# =====================================================================
def degrade(sup, rect, c1, c2):
    """Degradê de cima (c1) pra baixo (c2)."""
    x, y, w, h = rect
    for i in range(h):
        k = i / max(1, h - 1)
        sup.fill(tuple(int(c1[j] + (c2[j] - c1[j]) * k) for j in range(3)), (x, y + i, w, 1))


def linhas_velocidade(sup, centro, cor, n=60, r_dentro=120, r_fora=1100, grossura=10, semente=1, giro=0.0, alfa=255):
    """Linhas de velocidade que saem do centro (clássico de anime/mangá)."""
    rng = random.Random(semente)
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    cx, cy = centro
    for _ in range(n):
        a = rng.uniform(0, math.tau) + giro
        r1 = r_dentro * rng.uniform(0.8, 1.6)
        w = grossura * rng.uniform(0.3, 1.0) / 1000
        p1 = (cx + math.cos(a) * r1, cy + math.sin(a) * r1)
        p2 = (cx + math.cos(a + w * 50) * r_fora, cy + math.sin(a + w * 50) * r_fora)
        p3 = (cx + math.cos(a - w * 50) * r_fora, cy + math.sin(a - w * 50) * r_fora)
        pygame.draw.polygon(camada, (*cor, alfa), [p1, p2, p3])
    sup.blit(camada, (0, 0))


def linhas_horizontais(sup, cor, y0, y1, n, t, velocidade=40, semente=2, alfa=180):
    """Riscos de movimento horizontais."""
    rng = random.Random(semente)
    camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    for _ in range(n):
        y = rng.uniform(y0, y1)
        comp = rng.uniform(120, 420)
        x = (rng.uniform(0, LARGURA + comp) + t * velocidade * rng.uniform(0.6, 1.4)) % (LARGURA + comp) - comp
        pygame.draw.line(camada, (*cor, alfa), (x, y), (x + comp, y), rng.randint(2, 5))
    sup.blit(camada, (0, 0))


def luz(sup, pos, raio, cor, alfa):
    """Brilho redondo e suave (várias camadas)."""
    camada = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    for i in range(8, 0, -1):
        pygame.draw.circle(camada, (*cor, int(alfa * (1 - i / 9) ** 1.4)), (raio, raio), int(raio * i / 8))
    sup.blit(camada, (pos[0] - raio, pos[1] - raio))


def forma(sup, pts, cor, contorno=(12, 10, 14), grossura=5):
    pygame.draw.polygon(sup, cor, pts)
    if grossura:
        pygame.draw.polygon(sup, contorno, pts, grossura)


def bezier(p0, p1, p2, p3, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def estrela(sup, centro, r_fora, r_dentro, pontas, cor, giro=0.0, contorno=None):
    cx, cy = centro
    pts = []
    for i in range(pontas * 2):
        r = r_fora if i % 2 == 0 else r_dentro
        a = giro + i * math.pi / pontas
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    pygame.draw.polygon(sup, cor, pts)
    if contorno:
        pygame.draw.polygon(sup, contorno, pts, 3)


def shuriken(sup, centro, r, giro, cor=(205, 210, 222)):
    estrela(sup, centro, r, r * 0.32, 4, (30, 30, 36), giro)
    estrela(sup, centro, r * 0.86, r * 0.26, 4, cor, giro)
    pygame.draw.circle(sup, (60, 62, 70), (int(centro[0]), int(centro[1])), max(2, int(r * 0.18)))


def bolha(sup, centro, r, giro, alfa=255):
    """Bolha com shuriken dentro."""
    camada = pygame.Surface((int(r * 2 + 8), int(r * 2 + 8)), pygame.SRCALPHA)
    c = (r + 4, r + 4)
    pygame.draw.circle(camada, (140, 205, 255, int(70 * alfa / 255)), c, int(r))
    shuriken(camada, c, r * 0.62, giro)
    pygame.draw.circle(camada, (225, 245, 255, alfa), c, int(r), max(2, int(r * 0.08)))
    pygame.draw.circle(camada, (255, 255, 255, alfa), (int(c[0] - r * 0.38), int(c[1] - r * 0.4)), max(2, int(r * 0.16)))
    pygame.draw.arc(camada, (255, 255, 255, alfa), (c[0] - r * 0.75, c[1] - r * 0.75, r * 1.5, r * 1.5), 1.9, 2.8, 2)
    sup.blit(camada, (centro[0] - r - 4, centro[1] - r - 4))


def figura(q, ficha, x, y, escala, d, branco, t, pose=None, contorno_cor=None):
    """O oponente redesenhado liso, com sombra de anime, na cor dele."""
    from golpes import POSES
    from corpo import membro
    if pose is None:
        pose = ficha.get("poses", {}).get("golpeado") or POSES["golpeado"]
    elif isinstance(pose, str):
        pose = ficha.get("poses", {}).get(pose) or POSES[pose]
    s = ficha["tam"] * escala
    cor = (250, 250, 255) if branco else ficha["cor"]
    escura = tuple(int(c * 0.55) for c in cor)
    cont = contorno_cor or (14, 10, 16)

    def P(k):
        return (x + pose[k][0] * s * d, y - pose[k][1] * s)

    for a, b, w1, w2, c in (("qd", "jt", 8, 6, escura), ("jt", "pt", 6, 4, escura), ("pc", "ct", 5, 4, escura),
                            ("ct", "mt", 4.5, 3.5, escura)):
        membro(q, [(P(a), w1 * s), (P(b), w2 * s)], c, cont, borda=2.5, brilho=0.3, sombra=0.35)
    qd, pc = P("qd"), P("pc")
    membro(q, [(qd, 10 * s), (((qd[0] + pc[0]) / 2, (qd[1] + pc[1]) / 2), 8.5 * s), (pc, 12 * s)], cor, cont,
           borda=2.5, brilho=0.35, sombra=0.35)
    for a, b, w1, w2 in (("qd", "jf", 8, 6), ("jf", "pf", 6, 4), ("pc", "cf", 5, 4), ("cf", "mf", 4.5, 3.5)):
        membro(q, [(P(a), w1 * s), (P(b), w2 * s)], cor, cont, borda=2.5, brilho=0.35, sombra=0.35)
    cb = P("cb")
    membro(q, [((cb[0], cb[1] + 8 * s), 7 * s), ((cb[0], cb[1] - 4 * s), 8.5 * s)], cor, cont, borda=2.5,
           brilho=0.4, sombra=0.35)
    if ficha.get("figura_extra"):  # detalhes de cada personagem (orelha, focinho, patas a mais...)
        ficha["figura_extra"](q, P, s, d, cor, escura, cont, branco, t)
    elif ficha.get("cor_poder"):  # olho (do lado que olha)
        pygame.draw.circle(q, (255, 255, 255) if branco else ficha["cor_poder"],
                           (int(cb[0] + 4 * s * d), int(cb[1] - 1 * s)), max(2, int(1.8 * s)))
