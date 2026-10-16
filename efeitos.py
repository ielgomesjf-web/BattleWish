"""Efeitos visuais: o cenário (com coisas se mexendo), as explosões de impacto e os textos animados."""
import math
import random

import pygame

from config import *  # noqa: F401,F403

_fontes = {}


def fonte(tam):
    if tam not in _fontes:
        _fontes[tam] = pygame.font.SysFont("arialblack,arial", tam, bold=True)
    return _fontes[tam]


def texto(tela, txt, tam, cor, centro, sombra=True):
    img = fonte(tam).render(txt, True, cor)
    r = img.get_rect(center=centro)
    if sombra:
        tela.blit(fonte(tam).render(txt, True, PRETO), r.move(3, 3))
    tela.blit(img, r)


def texto_grande(tela, txt, tam, cor, centro, escala=1.0, alfa=255, contorno=(30, 10, 10)):
    """Texto com contorno grosso, que pode crescer/encolher (pras animações de ROUND e K.O.)."""
    base = fonte(tam).render(txt, True, cor)
    borda = fonte(tam).render(txt, True, contorno)
    w, h = base.get_size()
    sup = pygame.Surface((w + 12, h + 12), pygame.SRCALPHA)
    for dx in (-4, 0, 4):
        for dy in (-4, 0, 4):
            sup.blit(borda, (6 + dx, 6 + dy))
    sup.blit(borda, (10, 11))
    sup.blit(base, (6, 6))
    if escala != 1:
        sup = pygame.transform.smoothscale(sup, (max(1, int(sup.get_width() * escala)),
                                                 max(1, int(sup.get_height() * escala))))
    if alfa < 255:
        sup.set_alpha(alfa)
    tela.blit(sup, sup.get_rect(center=centro))


def mistura_cor(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# =====================================================================
# Impactos (o "PÁ!" quando um golpe acerta)
# =====================================================================
class Impactos:
    def __init__(self):
        self.lista = []

    def novo(self, x, y, tipo):
        """tipo: 'hit', 'forte' ou 'def'."""
        self.lista.append([x, y, 0, tipo, random.uniform(0, math.tau)])

    def update(self):
        for i in self.lista:
            i[2] += 1
        self.lista = [i for i in self.lista if i[2] < 16]

    def desenhar(self, tela):
        if not self.lista:
            return
        sup = tela
        for x, y, t, tipo, ang in self.lista:
            k = t / 16
            if tipo == "def":  # escudo azul
                for i in range(2):
                    r = int(18 + t * 3 + i * 8)
                    pts = [(x + math.cos(ang + a * math.pi / 3) * r, y + math.sin(ang + a * math.pi / 3) * r)
                           for a in range(6)]
                    pygame.draw.polygon(sup, (120, 200, 255, int(220 * (1 - k))), pts, 3)
                if t < 5:
                    pygame.draw.circle(sup, (220, 240, 255, 200), (int(x), int(y)), 14 - t * 2)
                continue
            g = 1.7 if tipo == "forte" else 1.0
            if t < 6:  # clarão branco
                pygame.draw.circle(sup, (255, 255, 255, 230 - t * 30), (int(x), int(y)), int((30 - t * 3) * g))
            # estrela de pontas
            r_fora = (22 + t * 3.5) * g
            r_dentro = r_fora * 0.38
            pontas = 9
            pts = []
            for i in range(pontas * 2):
                r = r_fora * (1 if i % 2 == 0 else 0.0) + r_dentro * (0 if i % 2 == 0 else 1)
                if i % 2 == 0:
                    r *= 0.8 + 0.4 * ((i * 37) % 7) / 7  # pontas de tamanhos diferentes
                a = ang + i * math.pi / pontas
                pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
            alfa = int(255 * (1 - k) ** 1.5)
            pygame.draw.polygon(sup, (255, 190, 40, alfa), pts)
            pts2 = [(x + (px - x) * 0.55, y + (py - y) * 0.55) for px, py in pts]
            pygame.draw.polygon(sup, (255, 250, 210, alfa), pts2)
            # anel de choque
            pygame.draw.circle(sup, (255, 255, 255, int(200 * (1 - k))), (int(x), int(y)), int((12 + t * 6) * g), 3)
            if tipo == "forte":
                pygame.draw.circle(sup, (255, 160, 60, int(160 * (1 - k))), (int(x), int(y)), int((8 + t * 9) * g), 4)


# =====================================================================
# Cenário: templo no fim de tarde, com nuvens, pétalas e grama se mexendo
# =====================================================================
def _pagode(sup, x, base, e, cor):
    """Templo de 3 andares (silhueta)."""
    larg = 46 * e
    y = base
    for andar in range(3):
        alt = 26 * e
        corpo = larg * (0.7 - andar * 0.12)
        pygame.draw.rect(sup, cor, (x - corpo / 2, y - alt, corpo, alt))
        teto = larg * (1.2 - andar * 0.18)
        ty = y - alt
        pygame.draw.polygon(sup, cor, [(x - teto / 2 - 8 * e, ty - 6 * e), (x - teto / 2, ty + 2 * e),
                                       (x + teto / 2, ty + 2 * e), (x + teto / 2 + 8 * e, ty - 6 * e),
                                       (x + teto * 0.3, ty - 12 * e), (x - teto * 0.3, ty - 12 * e)])
        y = ty - 12 * e
    pygame.draw.line(sup, cor, (x, y), (x, y - 22 * e), max(2, int(3 * e)))
    return [(x, base - 14 * e), (x, base - 52 * e)]  # onde ficam as janelas acesas


def _torii(sup, x, base, e, cor):
    for s in (-1, 1):
        pygame.draw.rect(sup, cor, (x + s * 34 * e - 4 * e, base - 120 * e, 8 * e, 120 * e))
    pygame.draw.rect(sup, cor, (x - 46 * e, base - 98 * e, 92 * e, 7 * e))
    pygame.draw.polygon(sup, cor, [(x - 60 * e, base - 126 * e), (x + 60 * e, base - 126 * e),
                                   (x + 52 * e, base - 116 * e), (x - 52 * e, base - 116 * e)])
    pygame.draw.rect(sup, cor, (x - 3 * e, base - 116 * e, 6 * e, 18 * e))


def _arvore(sup, x, base, e, cor_tronco, cor_copa, rng):
    pygame.draw.line(sup, cor_tronco, (x, base), (x + 6 * e, base - 60 * e), max(2, int(7 * e)))
    pygame.draw.line(sup, cor_tronco, (x + 4 * e, base - 40 * e), (x + 24 * e, base - 66 * e), max(2, int(4 * e)))
    for _ in range(9):
        cx = x + rng.uniform(-30, 38) * e
        cy = base - rng.uniform(58, 92) * e
        pygame.draw.circle(sup, cor_copa, (int(cx), int(cy)), int(rng.uniform(13, 22) * e))


class Cenario:
    def __init__(self):
        self.fundo = self._fundo()
        rng = random.Random(7)
        self.nuvens = [[rng.uniform(0, LARGURA), rng.uniform(40, 200), rng.uniform(0.08, 0.25), rng.uniform(0.7, 1.4)]
                       for _ in range(6)]
        self.petalas = [[rng.uniform(0, LARGURA), rng.uniform(-ALTURA, CHAO), rng.uniform(0, math.tau),
                         rng.uniform(0.4, 1.0)] for _ in range(34)]
        self.tufos = [(rng.uniform(0, LARGURA), rng.uniform(0.6, 1.2)) for _ in range(26)]
        self.lanternas = self._lanternas

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        topo, meio, baixo = (34, 26, 72), (150, 70, 110), (255, 160, 90)
        for y in range(CHAO):
            t = y / CHAO
            cor = mistura_cor(topo, meio, t / 0.55) if t < 0.55 else mistura_cor(meio, baixo, (t - 0.55) / 0.45)
            sup.fill(cor, (0, y, LARGURA, 1))
        # estrelinhas lá em cima
        rng = random.Random(3)
        for _ in range(40):
            x, y = rng.uniform(0, LARGURA), rng.uniform(0, 130)
            c = rng.randint(150, 230)
            sup.set_at((int(x), int(y)), (c, c, c))
        # sol com brilho
        brilho = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for r, a in ((190, 25), (140, 35), (105, 50)):
            pygame.draw.circle(brilho, (255, 200, 120, a), (690, 330), r)
        sup.blit(brilho, (0, 0))
        pygame.draw.circle(sup, (255, 226, 150), (690, 330), 74)
        pygame.draw.circle(sup, (255, 240, 190), (690, 330), 60)
        # morros (do mais longe pro mais perto), com névoa
        camadas = (((122, 74, 118), 175, 0.0, 0.005), ((92, 54, 98), 130, 1.7, 0.007), ((64, 38, 74), 82, 3.1, 0.009))
        self._lanternas = []
        rng = random.Random(11)
        for n, (cor, alt, fase, fr) in enumerate(camadas):
            def altura(x):
                return CHAO - alt - 34 * math.sin(x * fr + fase) - 16 * math.sin(x * fr * 3.1 + fase)
            pts = [(0, CHAO)] + [(x, altura(x)) for x in range(0, LARGURA + 10, 10)] + [(LARGURA, CHAO)]
            pygame.draw.polygon(sup, cor, pts)
            if n == 0:
                self._lanternas += _pagode(sup, 190, altura(190) + 6, 1.15, cor)
                _arvore(sup, 300, altura(300) + 4, 0.7, cor, cor, rng)
            if n == 1:
                _torii(sup, 820, altura(820) + 10, 0.75, cor)
                for x in (60, 120, 560, 620):
                    _arvore(sup, x, altura(x) + 6, 0.9, cor, mistura_cor(cor, (160, 70, 110), 0.35), rng)
            nevoa = pygame.Surface((LARGURA, 60), pygame.SRCALPHA)
            for y in range(60):
                nevoa.fill((255, 170, 140, int(40 * (1 - y / 60))), (0, y, LARGURA, 1))
            sup.blit(nevoa, (0, CHAO - alt - 40))
        # chão de madeira com perspectiva
        for y in range(CHAO, ALTURA):
            t = (y - CHAO) / (ALTURA - CHAO)
            sup.fill(mistura_cor((120, 76, 52), (70, 42, 32), t), (0, y, LARGURA, 1))
        for i in range(-20, 21):  # tábuas
            x0, x1 = LARGURA // 2 + i * 38, LARGURA // 2 + i * 110
            pygame.draw.line(sup, (82, 50, 36), (x0, CHAO), (x1, ALTURA), 2)
        for k in range(1, 6):  # emendas
            y = CHAO + (ALTURA - CHAO) * (k / 6) ** 1.6
            pygame.draw.line(sup, (96, 60, 42), (0, y), (LARGURA, y), 1)
        reflexo = pygame.Surface((LARGURA, ALTURA - CHAO), pygame.SRCALPHA)
        pygame.draw.ellipse(reflexo, (255, 190, 120, 50), (690 - 220, -10, 440, 40))
        sup.blit(reflexo, (0, CHAO))
        pygame.draw.line(sup, (170, 110, 72), (0, CHAO), (LARGURA, CHAO), 3)
        pygame.draw.line(sup, (60, 34, 26), (0, CHAO + 2), (LARGURA, CHAO + 2), 1)
        # cantinhos escuros (deixa o meio em destaque)
        vinheta = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for i in range(40):
            a = int(80 * (1 - i / 40) ** 2)
            pygame.draw.rect(vinheta, (10, 0, 20, a), (i * 2, i * 2, LARGURA - i * 4, ALTURA - i * 4), 2)
        sup.blit(vinheta, (0, 0))
        return sup

    def desenhar_pequeno(self, t, px):
        """O cenário já do tamanho da pixel art (o fundo parado é reduzido uma vez só)."""
        if getattr(self, "_px", None) != px:
            self._px = px
            self._fundo_peq = pygame.transform.smoothscale(self.fundo, (LARGURA // px, ALTURA // px))
            self._tela_peq = pygame.Surface((LARGURA // px, ALTURA // px))
            self._nuvem = {}
        tela = self._tela_peq
        tela.blit(self._fundo_peq, (0, 0))
        for x, y in self._lanternas:
            a = 150 + int(60 * math.sin(t * 0.07 + x))
            pygame.draw.circle(tela, (255, 200 + a // 30, 110), (int(x / px), int(y / px)), max(1, 3 // px))
        for n in self.nuvens:
            n[0] += n[2]
            if n[0] > LARGURA + 120:
                n[0] = -120
            x, y, _, e = n
            chave = round(e, 2)
            if chave not in self._nuvem:
                s = pygame.Surface((int(200 * e / px), int(70 * e / px)), pygame.SRCALPHA)
                for dx, dy, r in ((50, 40, 26), (80, 30, 32), (115, 36, 28), (140, 44, 20), (30, 48, 18)):
                    pygame.draw.circle(s, (255, 200, 200, 60), (int(dx * e / px), int(dy * e / px)), int(r * e / px))
                self._nuvem[chave] = s
            tela.blit(self._nuvem[chave], ((x - 100 * e) / px, y / px))
        return tela

    def desenhar(self, tela, t):
        tela.blit(self.fundo, (0, 0))
        # janelinhas do templo piscando
        for x, y in self._lanternas:
            a = 150 + int(60 * math.sin(t * 0.07 + x))
            pygame.draw.circle(tela, (255, 200, 110), (int(x), int(y)), 3)
            s = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 190, 100, a // 3), (12, 12), 11)
            tela.blit(s, (x - 12, y - 12))
        # nuvens
        for n in self.nuvens:
            n[0] += n[2]
            if n[0] > LARGURA + 120:
                n[0] = -120
            x, y, _, e = n
            s = pygame.Surface((int(200 * e), int(70 * e)), pygame.SRCALPHA)
            for dx, dy, r in ((50, 40, 26), (80, 30, 32), (115, 36, 28), (140, 44, 20), (30, 48, 18)):
                pygame.draw.circle(s, (255, 200, 200, 60), (int(dx * e), int(dy * e)), int(r * e))
            tela.blit(s, (x - 100 * e, y))

    def desenhar_frente(self, tela, t, px=1):
        """Coisas na frente dos lutadores: pétalas caindo e grama no canto."""
        for p in self.petalas:
            p[1] += p[3]
            p[0] += math.sin(t * 0.03 + p[2]) * 0.6 - 0.25
            if p[1] > ALTURA:
                p[1] = -10
                p[0] = random.uniform(0, LARGURA + 100)
            a = t * 0.08 + p[2]
            w = 3 + 2 * abs(math.sin(a))
            pygame.draw.ellipse(tela, (255, 170, 200), (p[0] / px, p[1] / px, max(2, w / px), max(1, 3 / px)))
        for x, e in self.tufos:
            if 120 < x < LARGURA - 120:
                continue  # grama só nos cantos, pra não tampar a luta
            vento = math.sin(t * 0.05 + x * 0.05) * 4 * e
            for i in range(5):
                bx = x + (i - 2) * 4 * e
                pygame.draw.line(tela, (40, 70, 40), (bx / px, ALTURA / px),
                                 ((bx + vento + (i - 2) * 3) / px, (ALTURA - 26 * e - i % 2 * 8) / px), 1)


def moeda(tela, centro, r=9, t=0):
    """Moedinha dourada do jogo (gira um pouquinho)."""
    x, y = int(centro[0]), int(centro[1])
    w = max(2, int(r * (0.75 + 0.25 * abs(math.cos(t * 0.05)))))
    pygame.draw.ellipse(tela, (110, 70, 10), (x - w - 1, y - r - 1, 2 * w + 2, 2 * r + 2))
    pygame.draw.ellipse(tela, (250, 200, 60), (x - w, y - r, 2 * w, 2 * r))
    pygame.draw.ellipse(tela, (200, 140, 30), (x - w + 3, y - r + 3, max(1, 2 * w - 6), max(1, 2 * r - 6)), 2)
    pygame.draw.line(tela, (255, 245, 190), (x - w // 3, y - r // 2), (x - w // 3, y + r // 3), 2)


def texto_moedas(tela, n, direita, y, t=0, tam=20):
    """'(moeda) 123' encostado na direita."""
    img = fonte(tam).render(str(n), True, (255, 220, 90))
    r = img.get_rect(midright=(direita, y))
    tela.blit(fonte(tam).render(str(n), True, PRETO), r.move(2, 2))
    tela.blit(img, r)
    moeda(tela, (r.left - tam * 0.7, y), int(tam * 0.45), t)


CORES_BOTAO = {"A": (70, 180, 70), "B": (214, 60, 50), "X": (60, 120, 224), "Y": (232, 190, 40)}


def desenhar_botao(tela, nome, centro, tam=16):
    """Um botão do controle: A/B/X/Y redondinhos e coloridos, LB/RB/LT/RT retangulares."""
    x, y = int(centro[0]), int(centro[1])
    if nome in CORES_BOTAO:
        pygame.draw.circle(tela, (12, 10, 16), (x, y), tam // 2 + 2)
        pygame.draw.circle(tela, CORES_BOTAO[nome], (x, y), tam // 2)
        img = fonte(max(8, int(tam * 0.62))).render(nome, True, BRANCO)
        tela.blit(img, img.get_rect(center=(x, y + 1)))
        return tam + 4
    img = fonte(max(8, int(tam * 0.55))).render(nome, True, BRANCO)
    w = img.get_width() + 10
    r = pygame.Rect(0, 0, w, tam)
    r.center = (x, y)
    pygame.draw.rect(tela, (12, 10, 16), r.inflate(4, 4), border_radius=6)
    pygame.draw.rect(tela, (90, 92, 104), r, border_radius=5)
    tela.blit(img, img.get_rect(center=r.center))
    return w + 4


def texto_botao(tela, botao, resto, tam, cor, centro):
    """Uma linha 'botão + texto' centralizada. No controle o botão é desenhado colorido; no teclado vira texto."""
    import controle_video
    nome = controle_video.nome(botao)
    if not controle_video.no_controle():
        texto(tela, f"{nome}  {resto}", tam, cor, centro)
        return
    img = fonte(tam).render(resto, True, cor)
    wb = desenhar_botao(pygame.Surface((1, 1), pygame.SRCALPHA), nome, (0, 0), tam + 4)
    total = wb + 6 + img.get_width()
    x0 = centro[0] - total / 2
    desenhar_botao(tela, nome, (x0 + wb / 2, centro[1]), tam + 4)
    r = img.get_rect(midleft=(x0 + wb + 6, centro[1]))
    tela.blit(fonte(tam).render(resto, True, PRETO), r.move(2, 2))
    tela.blit(img, r)
