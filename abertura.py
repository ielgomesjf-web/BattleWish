"""Abertura do BATTLE WISH e o logo."""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande


def logo(tela, centro, escala=1.0, t=0):
    """O logo: BATTLE WISH com sombra laranja."""
    x, y = centro
    for txt, dy, tam in (("BATTLE", -34, 78), ("WISH", 40, 92)):
        texto_grande(tela, txt, int(tam * escala), (120, 40, 10), (x + 5, y + dy * escala + 6), contorno=(20, 6, 0))
        texto_grande(tela, txt, int(tam * escala), (255, 214, 70), (x, y + dy * escala), contorno=(40, 12, 0))


# o símbolo do jogo (o mesmo do ícone): estrela cadente com rastro de 3 garras
SIMBOLO_VERMELHO = (255, 70, 85)
SIMBOLO_BRANCO = (245, 240, 230)
_simbolos = {}


def _estrela4(r_longo, r_curto, cx, cy):
    pts = []
    for i in range(8):
        a = i * math.pi / 4 - math.pi / 2
        r = r_longo if i % 2 == 0 else r_curto
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def simbolo_sup(tam):
    """O símbolo desenhado num quadrado tam x tam (transparente), com borda lisa."""
    if tam not in _simbolos:
        g = tam * 2  # desenha no dobro e reduz (fica liso)
        k = g / 1000
        sup = pygame.Surface((g, g), pygame.SRCALPHA)
        for i, (comp, larg) in enumerate(((560, 64), (470, 52), (380, 40))):  # as garras (rastro)
            off = (i - 1) * 78
            ax, ay = 590 + off - 5, 410 + off + 5
            ang = math.radians(135)
            bx, by = ax + math.cos(ang) * comp, ay + math.sin(ang) * comp
            dx, dy = bx - ax, by - ay
            n = math.hypot(dx, dy)
            nx, ny = -dy / n * larg / 2, dx / n * larg / 2
            mx, my = ax + dx * 0.45, ay + dy * 0.45
            pygame.draw.polygon(sup, SIMBOLO_VERMELHO,
                                [(x * k, y * k) for x, y in ((ax, ay), (mx + nx, my + ny), (bx, by), (mx - nx, my - ny))])
        pygame.draw.polygon(sup, SIMBOLO_BRANCO, [(x * k, y * k) for x, y in _estrela4(250, 52, 605, 395)])
        _simbolos[tam] = pygame.transform.smoothscale(sup, (tam, tam))
    return _simbolos[tam]


def cor_fogo(v):
    """0 = brasa vermelha escura ... 1 = quase branco."""
    v = max(0.0, min(1.0, v))
    if v < 0.4:
        k = v / 0.4
        return (int(120 + 110 * k), int(20 + 40 * k), 10)
    if v < 0.75:
        k = (v - 0.4) / 0.35
        return (230 + int(25 * k), int(60 + 110 * k), int(10 + 20 * k))
    k = (v - 0.75) / 0.25
    return (255, int(170 + 70 * k), int(30 + 170 * k))


class Abertura:
    """Raio no meio da tela -> sai fogo dele -> o fogo cobre tudo -> abre um buraco queimando
    e aparece o símbolo e BATTLE WISH."""
    DURACAO = 240
    RAIO = 12        # o raio cai
    FOGO = 20        # o fogo começa a sair do raio
    COBRE = 62       # o fogo cobriu a tela toda
    ABRE = 76        # o fogo começa a queimar no meio e mostra o logo
    ABRIU = 104      # (já mostrou tudo)

    def __init__(self, personagens=None):
        self.t = 0
        self.rng = random.Random(7)
        cx = LARGURA // 2
        pts = [(cx, -10)]  # o raio: sempre no meio, em ziguezague
        while pts[-1][1] < ALTURA:
            x = pts[-1][0] + self.rng.randint(-34, 34)
            x = cx + max(-50, min(50, x - cx))
            pts.append((x, pts[-1][1] + self.rng.randint(34, 58)))
        self.raio = pts
        self.galhos = []  # galhinhos do raio
        for i in range(2, len(pts) - 2, 3):
            q = [pts[i]]
            lado = self.rng.choice((-1, 1))
            for _ in range(3):
                q.append((q[-1][0] + lado * self.rng.randint(20, 46), q[-1][1] + self.rng.randint(16, 34)))
            self.galhos.append(q)
        self.chamas = []
        self.brasas = [[self.rng.uniform(0, LARGURA), self.rng.uniform(0, ALTURA), self.rng.uniform(0.5, 1.6),
                        self.rng.uniform(0, 6.28)] for _ in range(50)]
        self.faiscas = []

    @property
    def acabou(self):
        return self.t >= self.DURACAO

    # ---- partes ----
    def x_raio(self, y):
        """Onde o raio passa nessa altura."""
        pts = self.raio
        for a, b in zip(pts, pts[1:]):
            if a[1] <= y <= b[1]:
                k = (y - a[1]) / max(1, b[1] - a[1])
                return a[0] + (b[0] - a[0]) * k
        return LARGURA // 2

    def largura_fogo(self):
        """Até onde o fogo já espalhou, pra cada lado do raio."""
        t = self.t
        if t < self.FOGO:
            return 0
        k = min(1.0, (t - self.FOGO) / (self.COBRE - self.FOGO))
        return 10 + (LARGURA * 0.62) * k ** 1.7

    def desenhar_raio(self, tela, forca):
        t = self.t
        jit = random.Random(t // 2)
        pts = [(x + jit.randint(-3, 3), y) for x, y in self.raio]
        brilho = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        pygame.draw.lines(brilho, (140, 160, 255, int(90 * forca)), False, pts, 26)
        pygame.draw.lines(brilho, (190, 200, 255, int(140 * forca)), False, pts, 12)
        tela.blit(brilho, (0, 0))
        for g in self.galhos:
            pygame.draw.lines(tela, (200, 210, 255), False, g, 2)
        pygame.draw.lines(tela, (255, 255, 255), False, pts, 5)

    def desenhar_fogo(self, tela):
        """A parede de fogo saindo do raio pros dois lados (borda tremendo) + as labaredas."""
        t = self.t
        w = self.largura_fogo()
        if w <= 0:
            return
        esq, dir_ = [], []
        for y in range(-10, ALTURA + 30, 18):
            onda = math.sin(y * 0.05 + t * 0.4) * 14 + math.sin(y * 0.13 - t * 0.7) * 8
            xr = self.x_raio(y)
            esq.append((xr - w - onda, y))
            dir_.append((xr + w + onda, y))
        forma = esq + dir_[::-1]
        pygame.draw.polygon(tela, cor_fogo(0.35), forma)
        # faixas mais claras por dentro (o fogo é mais quente perto do raio)
        for camada, v in ((0.72, 0.6), (0.45, 0.82), (0.2, 0.97)):
            ww = w * camada
            if ww < 4:
                continue
            e2 = [(self.x_raio(y) - ww - math.sin(y * 0.07 + t * 0.6 + v * 5) * 10 * camada, y) for _, y in esq]
            d2 = [(self.x_raio(y) + ww + math.sin(y * 0.07 - t * 0.6 + v * 5) * 10 * camada, y) for _, y in esq]
            pygame.draw.polygon(tela, cor_fogo(v), e2 + d2[::-1])
        # labaredas soltando da borda e subindo
        for lado, borda in ((-1, esq), (1, dir_)):
            for _ in range(5):
                bx, by = borda[random.randrange(len(borda))]
                self.chamas.append([bx, by, lado * random.uniform(1, 4), random.uniform(-5, -2),
                                    random.uniform(14, 30), random.randint(16, 30)])

    def desenhar_chamas(self, tela):
        for c in self.chamas:
            c[0] += c[2]
            c[1] += c[3]
            c[4] *= 0.95
            c[5] -= 1
            pygame.draw.circle(tela, cor_fogo(0.4 + 0.6 * c[5] / 30), (int(c[0]), int(c[1])), max(1, int(c[4])))
        self.chamas = [c for c in self.chamas if c[5] > 0 and c[4] > 1.5]

    def tela_cheia_de_fogo(self, tela):
        """Quando já cobriu tudo: a tela inteira pegando fogo. Camadas: vermelho escuro em cima,
        amarelo quase branco embaixo, e a borda de cada camada são labaredas tremendo."""
        t = self.t
        tela.fill(cor_fogo(0.22))
        sorteio = random.Random(3)
        for camada in range(6):
            topo = ALTURA * (0.05 + camada * 0.16)
            v = 0.32 + camada * 0.13
            pts = [(LARGURA + 40, ALTURA + 10), (-40, ALTURA + 10)]
            x = -40
            while x < LARGURA + 40:
                larg = sorteio.randint(36, 70)
                fase = sorteio.uniform(0, 6.28)
                alt = sorteio.randint(40, 110) * (0.75 + 0.35 * math.sin(t * 0.32 + fase))
                balanca = math.sin(t * 0.2 + fase) * larg * 0.3
                pts += [(x, topo + 14 + math.sin(t * 0.15 + fase) * 6), (x + larg / 2 + balanca, topo - alt)]
                x += larg
            pts.append((LARGURA + 40, topo + 14))
            pygame.draw.polygon(tela, cor_fogo(v), pts)

    def cena_final(self):
        """O que aparece por trás do fogo: o símbolo e BATTLE WISH."""
        t = self.t
        sup = pygame.Surface((LARGURA, ALTURA))
        sup.fill((10, 12, 22))
        if not hasattr(self, "_brilhos"):  # (os brilhos são sempre iguais: desenha uma vez só)
            self._brilhos = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            for k in range(8):  # brilho de fogo embaixo (o resto do incêndio)
                pygame.draw.ellipse(self._brilhos, (230, 90, 20, 20), (-100 + k * 30, ALTURA - 120 + k * 12,
                                                                       LARGURA + 200 - k * 60, 260))
        sup.blit(self._brilhos, (0, 0))
        for b in self.brasas:  # brasinhas subindo
            b[1] -= b[2]
            b[0] += math.sin(t * 0.05 + b[3]) * 0.6
            if b[1] < -10:
                b[1] = ALTURA + 10
            pisca = 0.6 + 0.4 * math.sin(t * 0.2 + b[3] * 3)
            pygame.draw.circle(sup, cor_fogo(0.4 + 0.5 * pisca), (int(b[0]), int(b[1])), 2)
        # o símbolo (entra grande e assenta) com um brilho atrás
        k = min(1.0, max(0.0, (t - self.ABRE) / 22))
        tam = int(220 * (1.5 - 0.5 * (1 - (1 - k) ** 3)))
        cy = 170 + math.sin(t * 0.05) * 4 * k
        img = simbolo_sup(tam)
        sup.blit(img, img.get_rect(center=(LARGURA // 2, int(cy))))
        logo(sup, (LARGURA // 2, 350), 0.92, t)
        return sup

    def buraco(self, raio):
        """Contorno queimado (irregular) do buraco que abre no fogo."""
        t = self.t
        pts = []
        for i in range(48):
            a = i * math.tau / 48
            r = raio * (1 + 0.08 * math.sin(a * 5 + t * 0.3) + 0.05 * math.sin(a * 11 - t * 0.5))
            pts.append((LARGURA // 2 + math.cos(a) * r, 250 + math.sin(a) * r * 0.82))
        return pts

    # ---- quadro a quadro ----
    def desenhar(self, tela):
        self.t += 1
        t = self.t
        if t == self.RAIO:
            som.tocar("explosao")
            som.tocar("ko", 0.5)
        if t == self.FOGO:
            som.tocar("foguete", 0.9)
        if t == self.ABRE:
            som.tocar("ultimate")
        if t == self.ABRE + 20:
            som.tocar("chute")
        tela.fill((6, 6, 12))
        if t < self.ABRE:
            if t < self.COBRE:
                if self.RAIO <= t:
                    if t < self.RAIO + 4:  # clarão do raio
                        tela.fill((70, 70, 110))
                    self.desenhar_fogo(tela)
                    self.desenhar_chamas(tela)
                    self.desenhar_raio(tela, max(0.0, 1 - max(0, t - self.FOGO) / 30))
                    if t > self.COBRE - 12:  # o fogo da tela cheia já vai aparecendo por cima (sem pulo)
                        cheio = pygame.Surface((LARGURA, ALTURA))
                        self.tela_cheia_de_fogo(cheio)
                        cheio.set_alpha(int(255 * (t - (self.COBRE - 12)) / 12))
                        tela.blit(cheio, (0, 0))
                elif (t // 3) % 2 and t > 4:  # nuvem piscando antes de cair
                    pygame.draw.ellipse(tela, (30, 30, 50), (LARGURA // 2 - 300, -80, 600, 140))
            else:
                self.tela_cheia_de_fogo(tela)
                self.desenhar_chamas(tela)
        else:
            # o fogo continua por fora e o buraco no meio vai crescendo
            self.tela_cheia_de_fogo(tela)
            k = min(1.0, (t - self.ABRE) / (self.ABRIU - self.ABRE))
            raio = 20 + (LARGURA * 0.75) * (k ** 1.6)
            fin = self.cena_final()
            if k < 1:
                forma = self.buraco(raio)
                fin.set_colorkey((255, 0, 255))  # (o que fica fora do buraco some e deixa o fogo aparecer)
                fora = pygame.Surface((LARGURA, ALTURA))
                fora.fill((255, 0, 255))
                pygame.draw.polygon(fora, (0, 0, 0), forma)
                fora.set_colorkey((0, 0, 0))
                fin.blit(fora, (0, 0))
                tela.blit(fin, (0, 0))
                pygame.draw.polygon(tela, (255, 220, 120), forma, 10)  # a borda queimando
                pygame.draw.polygon(tela, (255, 255, 230), forma, 3)
                if t % 2 == 0:  # faíscas soltando da borda
                    for _ in range(6):
                        x, y = forma[random.randrange(len(forma))]
                        a = random.uniform(0, math.tau)
                        self.faiscas.append([x, y, math.cos(a) * 3, math.sin(a) * 3 - 2, random.randint(14, 26)])
            else:
                tela.blit(fin, (0, 0))
            if self.ABRE <= t < self.ABRE + 6:  # clarão
                branco = pygame.Surface((LARGURA, ALTURA))
                branco.fill(BRANCO)
                branco.set_alpha(200 - (t - self.ABRE) * 34)
                tela.blit(branco, (0, 0))
        for f in self.faiscas:
            f[0] += f[2]
            f[1] += f[3]
            f[3] += 0.15
            f[4] -= 1
            pygame.draw.circle(tela, (255, 230, 150), (int(f[0]), int(f[1])), max(1, f[4] // 7))
        self.faiscas = [f for f in self.faiscas if f[4] > 0]
        if t >= self.ABRIU + 20 and (t // 25) % 2 == 0:
            texto(tela, "aperte ENTER", 22, BRANCO, (LARGURA // 2, 470))


def criar_icone(caminho_png, caminho_ico):
    """Desenha o ícone do jogo (BW num escudo) e salva como .png e .ico."""
    sup = pygame.Surface((256, 256), pygame.SRCALPHA)
    pygame.draw.polygon(sup, (40, 12, 0), [(128, 8), (240, 48), (220, 180), (128, 250), (36, 180), (16, 48)])
    pygame.draw.polygon(sup, (200, 60, 30), [(128, 22), (226, 56), (208, 172), (128, 234), (48, 172), (30, 56)])
    pygame.draw.polygon(sup, (255, 214, 70), [(128, 22), (226, 56), (208, 172), (128, 234), (48, 172), (30, 56)], 8)
    texto_grande(sup, "BW", 110, (255, 214, 70), (128, 124), contorno=(40, 12, 0))
    pygame.image.save(sup, caminho_png)
    from PIL import Image
    Image.open(caminho_png).save(caminho_ico, sizes=[(256, 256), (64, 64), (48, 48), (32, 32), (16, 16)])
