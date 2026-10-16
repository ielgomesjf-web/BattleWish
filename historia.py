"""A história do MODO ARCADE (quadrinhos sem texto, igual o Ribbat).

A ESTRELA DO DESEJO cai na arena. Quem vencer todas as batalhas ganha um desejo.
  Abertura: a estrela caindo, a estrela na arena, os três lutadores encarando ela.
  Finais:   MAX-10 deseja ter amigos.  RIB deseja o Pergaminho Perdido (o do Ribbat!).  TRAFO deseja um lar.
"""
import math
import random

import pygame

from config import *  # noqa: F401,F403
from cutscene import bezier, degrade, estrela, figura, luz, pixel_fosco

PAINEL_TEMPO = 110  # quadros que cada quadrinho leva pra aparecer o próximo


def _ficha(nome):
    from personagens import PERSONAGENS
    return next(f for f in PERSONAGENS if f["nome"] == nome)


def _estrela_desejo(q, pos, r, t, alfa=255):
    luz(q, (int(pos[0]), int(pos[1])), int(r * 3), (255, 230, 150), min(220, alfa))
    estrela(q, pos, r, r * 0.45, 5, (255, 236, 140), t * 0.02, (120, 80, 20))
    estrela(q, pos, r * 0.55, r * 0.25, 5, (255, 255, 230), t * 0.02)


def _ceu_noite(q, w, h):
    degrade(q, (0, 0, w, h), (16, 14, 40), (60, 40, 80))
    rng = random.Random(2)
    for _ in range(50):
        q.set_at((int(rng.uniform(0, w)), int(rng.uniform(0, h * 0.7))), (220, 220, 240))


def _chao(q, w, h, y, cor=(70, 50, 40)):
    pygame.draw.rect(q, cor, (0, y, w, h - y))
    pygame.draw.line(q, tuple(min(255, c + 40) for c in cor), (0, y), (w, y), 3)


# =====================================================================
# Abertura
# =====================================================================
def ab_cai(q, t):
    w, h = q.get_size()
    _ceu_noite(q, w, h)
    k = min(1, t / 80)
    x, y = w * 0.15 + w * 0.6 * k, h * 0.1 + h * 0.55 * k
    for i in range(12):  # rastro
        pygame.draw.circle(q, (255, 220, 140), (int(x - i * 14), int(y - i * 9)), max(1, 9 - i // 2))
    _estrela_desejo(q, (x, y), 18, t)
    pygame.draw.polygon(q, (30, 20, 40), [(0, h), (0, h * 0.8), (w * 0.3, h * 0.72), (w * 0.6, h * 0.85), (w, h * 0.75), (w, h)])


def ab_arena(q, t):
    w, h = q.get_size()
    degrade(q, (0, 0, w, h), (40, 24, 60), (150, 80, 70))
    _chao(q, w, h, int(h * 0.75))
    _estrela_desejo(q, (w / 2, h * 0.6), 22 + 3 * math.sin(t * 0.1), t)
    for nome, x, d in (("MAX-10", w * 0.15, 1), ("TRAFO", w * 0.85, -1)):
        figura(q, _ficha(nome), x, h * 0.75, 0.55, d, False, t, "parado")
    figura(q, _ficha("RIB"), w * 0.32, h * 0.75, 0.5, 1, False, t, "parado")


def ab_encara(q, t):
    w, h = q.get_size()
    degrade(q, (0, 0, w, h), (90, 20, 30), (30, 10, 20))
    for i in range(30):  # linhas de tensão
        a = i * math.tau / 30
        pygame.draw.line(q, (140, 40, 50), (w / 2, h / 2), (w / 2 + math.cos(a) * w, h / 2 + math.sin(a) * w), 2)
    for nome, x, d, pose in (("MAX-10", w * 0.2, 1, "parado"), ("RIB", w * 0.5, 1, "parado"), ("TRAFO", w * 0.8, -1, "parado")):
        figura(q, _ficha(nome), x, h * 0.95, 0.75, d, False, t, pose)


# =====================================================================
# Finais
# =====================================================================
def fim_pega(nome):
    def painel(q, t):
        w, h = q.get_size()
        degrade(q, (0, 0, w, h), (30, 20, 50), (90, 60, 90))
        luz(q, (int(w / 2), int(h * 0.4)), 140, (255, 230, 150), 160)
        figura(q, _ficha(nome), w / 2, h * 0.98, 0.8, 1, False, t, "vitoria")
        _estrela_desejo(q, (w / 2 + 30, h * 0.18), 20 + 3 * math.sin(t * 0.15), t)
    return painel


def fim_max_coracao(q, t):
    w, h = q.get_size()
    degrade(q, (0, 0, w, h), (10, 10, 20), (40, 30, 50))
    figura(q, _ficha("MAX-10"), w / 2, h * 1.15, 1.2, 1, False, t, "parado")
    k = min(1, t / 50)
    luz(q, (int(w / 2 + 6), int(h * 0.5)), int(30 + 60 * k), (255, 210, 120), int(220 * k))  # a estrela vira um brilho no peito


def fim_max_amigos(q, t):
    w, h = q.get_size()
    degrade(q, (0, 0, w, h), (90, 50, 100), (255, 170, 100))
    pygame.draw.circle(q, (255, 230, 160), (int(w * 0.5), int(h * 0.62)), 60)
    _chao(q, w, h, int(h * 0.8), (60, 40, 50))
    for nome, x, d in (("MAX-10", w * 0.3, 1), ("RIB", w * 0.5, 1), ("TRAFO", w * 0.7, -1)):
        figura(q, _ficha(nome), x, h * 0.8, 0.5, d, False, t, "parado")


def fim_rib_pergaminho(q, t):
    w, h = q.get_size()
    degrade(q, (0, 0, w, h), (20, 40, 40), (60, 100, 80))
    k = min(1, t / 40)
    luz(q, (int(w / 2), int(h * 0.5)), 120, (255, 230, 150), int(200 * (1 - k * 0.5)))
    # a estrela vira o PERGAMINHO
    rx, ry = w / 2, h * 0.5
    pygame.draw.rect(q, (236, 220, 170), (rx - 50 * k, ry - 30, 100 * k, 60))
    for dx in (-1, 1):
        pygame.draw.circle(q, (190, 150, 90), (int(rx + dx * 50 * k), int(ry)), 18)
        pygame.draw.circle(q, (120, 80, 40), (int(rx + dx * 50 * k), int(ry)), 18, 3)
    pygame.draw.rect(q, (200, 60, 50), (rx - 6, ry - 30, 12, 60))
    if k < 1:
        _estrela_desejo(q, (rx, ry), 20 * (1 - k) + 1, t, int(255 * (1 - k)))


def fim_rib_vila(q, t):
    w, h = q.get_size()
    degrade(q, (0, 0, w, h), (110, 170, 200), (200, 220, 180))
    _chao(q, w, h, int(h * 0.78), (70, 110, 60))
    for x in (w * 0.12, w * 0.88):  # casinhas da vila dos sapos
        pygame.draw.ellipse(q, (120, 90, 60), (x - 40, h * 0.5, 80, 70))
        pygame.draw.ellipse(q, (40, 30, 20), (x - 12, h * 0.62, 24, 30))
    figura(q, _ficha("RIB"), w * 0.38, h * 0.78, 0.55, 1, False, t, "vitoria")
    # o vô (sapão velho com bigode branco)
    vx, vy = w * 0.64, h * 0.78
    pygame.draw.ellipse(q, (90, 140, 70), (vx - 34, vy - 70, 68, 70))
    pygame.draw.ellipse(q, (14, 20, 12), (vx - 34, vy - 70, 68, 70), 3)
    for ox in (-14, 6):
        pygame.draw.circle(q, (240, 240, 240), (int(vx + ox), int(vy - 72)), 10)
        pygame.draw.circle(q, (20, 20, 20), (int(vx + ox), int(vy - 72)), 4)
    pygame.draw.lines(q, (245, 245, 245), False, [(vx - 20, vy - 50), (vx - 6, vy - 44), (vx + 8, vy - 50)], 5)
    for i in range(6):  # sapinhos pulando de alegria
        x = w * 0.15 + i * w * 0.14
        y = h * 0.78 - 10 - abs(math.sin(t * 0.15 + i)) * 26
        pygame.draw.ellipse(q, (100, 170, 70), (x - 9, y - 10, 18, 12))


def fim_trafo_luz(q, t):
    w, h = q.get_size()
    degrade(q, (0, 0, w, h), (40, 30, 20), (90, 70, 40))
    figura(q, _ficha("TRAFO"), w / 2, h * 0.98, 0.8, 1, False, t, "parado")
    k = min(1, t / 50)
    for i in range(10):  # a estrela vira uma casinha de luz
        a = i * math.tau / 10 + t * 0.03
        pygame.draw.circle(q, (255, 230, 150), (int(w / 2 + math.cos(a) * 90 * k), int(h * 0.5 + math.sin(a) * 50 * k)), 4)


def fim_trafo_lar(q, t):
    w, h = q.get_size()
    degrade(q, (0, 0, w, h), (130, 190, 230), (220, 230, 200))
    _chao(q, w, h, int(h * 0.78), (90, 150, 70))
    # casinha de cachorro
    cx, cy = w * 0.25, h * 0.78
    pygame.draw.rect(q, (170, 70, 50), (cx - 50, cy - 70, 100, 70))
    pygame.draw.polygon(q, (110, 40, 30), [(cx - 62, cy - 68), (cx, cy - 115), (cx + 62, cy - 68)])
    pygame.draw.ellipse(q, (40, 20, 14), (cx - 20, cy - 46, 40, 50))
    figura(q, _ficha("TRAFO"), w * 0.55, h * 0.78, 0.5, -1, False, t, "parado")
    # a criança abraçando ele
    kx, ky = w * 0.72, h * 0.78
    pygame.draw.circle(q, (240, 200, 160), (int(kx), int(ky - 74)), 13)
    pygame.draw.rect(q, (60, 120, 200), (kx - 12, ky - 62, 24, 34))
    pygame.draw.line(q, (50, 50, 80), (kx - 6, ky - 28), (kx - 8, ky), 6)
    pygame.draw.line(q, (50, 50, 80), (kx + 6, ky - 28), (kx + 8, ky), 6)
    pygame.draw.line(q, (240, 200, 160), (kx - 10, ky - 56), (kx - 40, ky - 60), 6)  # braço no Trafo
    if (t // 20) % 2:  # coraçãozinho
        hx, hy = w * 0.63, h * 0.35
        pygame.draw.circle(q, (230, 70, 90), (int(hx - 6), int(hy)), 7)
        pygame.draw.circle(q, (230, 70, 90), (int(hx + 6), int(hy)), 7)
        pygame.draw.polygon(q, (230, 70, 90), [(hx - 13, hy + 2), (hx + 13, hy + 2), (hx, hy + 18)])


def final_generico(nome):
    """Personagem que ainda não tem final próprio: ele pega a estrela (e a gente faz o final dele depois)."""
    return [fim_pega(nome), fim_pega(nome), fim_max_amigos]


ABERTURA = [ab_cai, ab_arena, ab_encara]
FINAIS = {
    "MAX-10": [fim_pega("MAX-10"), fim_max_coracao, fim_max_amigos],
    "RIB": [fim_pega("RIB"), fim_rib_pergaminho, fim_rib_vila],
    "TRAFO": [fim_pega("TRAFO"), fim_trafo_luz, fim_trafo_lar],
}


class Quadrinho:
    """Uma página de quadrinho: os painéis vão aparecendo um por um. ENTER adianta."""

    def __init__(self, paineis):
        self.paineis = paineis
        self.t = 0
        w, h = LARGURA - 60, (ALTURA - 80) // 2 - 10
        self.rects = [pygame.Rect(30, 30, w // 2 - 6, h), pygame.Rect(30 + w // 2 + 6, 30, w // 2 - 6, h),
                      pygame.Rect(30, 30 + h + 14, w, h)]
        self.sups = [pygame.Surface(r.size) for r in self.rects]
        self.pagina = pygame.Surface((LARGURA, ALTURA))

    @property
    def acabou(self):
        return self.t >= PAINEL_TEMPO * len(self.paineis) + 80

    def adiantar(self):
        prox = (self.t // PAINEL_TEMPO + 1) * PAINEL_TEMPO
        self.t = min(prox, PAINEL_TEMPO * len(self.paineis) + 80)

    def desenhar(self, tela):
        self.t += 1
        q = self.pagina
        q.fill((236, 226, 200))  # papel
        for i, (painel, r, sup) in enumerate(zip(self.paineis, self.rects, self.sups)):
            u = self.t - i * PAINEL_TEMPO
            if u < 0:
                continue
            painel(sup, u)
            k = min(1, u / 12)
            q.blit(sup, (r.x, r.y + int((1 - k) * 30)))
            pygame.draw.rect(q, (20, 16, 14), r.move(0, int((1 - k) * 30)), 5)
        tela.blit(pixel_fosco(q), (0, 0))
        if self.t > PAINEL_TEMPO * len(self.paineis):
            if (self.t // 25) % 2:
                f = pygame.font.SysFont("arialblack,arial", 16, bold=True)
                img = f.render("ENTER", True, (40, 30, 20))
                tela.blit(img, (LARGURA - 90, ALTURA - 30))


class Creditos:
    DURACAO = 420

    def __init__(self):
        self.t = 0

    @property
    def acabou(self):
        return self.t >= self.DURACAO

    def desenhar(self, tela):
        from abertura import logo
        from efeitos import texto
        self.t += 1
        tela.fill((8, 6, 14))
        logo(tela, (LARGURA // 2, 140), 0.8, self.t)
        linhas = [("criado por", 18, (200, 200, 220)), ("GOMES", 40, (255, 220, 70)), ("", 10, BRANCO),
                  ("personagens", 16, (200, 200, 220)), ("MAX-10   •   RIB   •   TRAFO", 22, BRANCO), ("", 10, BRANCO),
                  ("ajudante", 14, (170, 170, 200)), ("MARIA", 18, (200, 200, 230)), ("", 10, BRANCO),
                  ("obrigado por jogar!", 20, (255, 220, 70))]
        y = 260
        for txt, tam, cor in linhas:
            if txt:
                texto(tela, txt, tam, cor, (LARGURA // 2, y))
            y += tam + 10
