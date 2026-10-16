"""Os cenários. Cada personagem tem a sua casa:
  TEMPLO      (o de sempre)
  PÂNTANO     do Rib: noite, lua, água com vitória-régia, vaga-lumes
  FERRO-VELHO do Max-10: fumaça laranja, carros velhos, guindaste, faíscas de solda
  TOCA        do Trafo: caverna, raízes, cogumelos que brilham, gotas pingando

Todo cenário tem: fundo (desenhado uma vez), desenhar_pequeno (fundo + coisas que mexem, já na pixel art)
e desenhar_frente (coisas que ficam na frente dos lutadores).
"""
import math
import random

import pygame

from config import *  # noqa: F401,F403
from efeitos import Cenario as Templo
from efeitos import mistura_cor


def _degrade(sup, rect, c1, c2):
    x, y, w, h = rect
    for i in range(h):
        sup.fill(mistura_cor(c1, c2, i / max(1, h - 1)), (x, y + i, w, 1))


def _brilho(sup, pos, raio, cor, alfa):
    camada = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    for i in range(6, 0, -1):
        pygame.draw.circle(camada, (*cor, int(alfa * (1 - i / 7))), (raio, raio), int(raio * i / 6))
    sup.blit(camada, (pos[0] - raio, pos[1] - raio))


class Base:
    nome = ""

    def __init__(self):
        self.fundo = self._fundo()
        self._px = None

    def desenhar_pequeno(self, t, px):
        if self._px != px:
            self._px = px
            self._fundo_peq = pygame.transform.smoothscale(self.fundo, (LARGURA // px, ALTURA // px))
            self._tela_peq = pygame.Surface((LARGURA // px, ALTURA // px))
        tela = self._tela_peq
        tela.blit(self._fundo_peq, (0, 0))
        self.animar(tela, t, px)
        return tela

    def animar(self, tela, t, px):
        pass

    def desenhar_frente(self, tela, t, px=1):
        pass


# =====================================================================
# PÂNTANO (Rib)
# =====================================================================
class Pantano(Base):
    nome = "PÂNTANO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, 400), (14, 26, 34), (60, 92, 80))
        _brilho(sup, (720, 150), 150, (220, 240, 200), 70)
        pygame.draw.circle(sup, (226, 236, 200), (720, 150), 56)
        pygame.draw.circle(sup, (206, 218, 182), (700, 136), 10)
        pygame.draw.circle(sup, (206, 218, 182), (738, 168), 7)
        rng = random.Random(21)
        for camada, (cor, base, alt) in enumerate((((30, 52, 50), 410, 220), ((18, 36, 34), 420, 260))):
            for _ in range(7):  # árvores com musgo pendurado
                x = rng.uniform(-40, LARGURA + 40)
                h = alt * rng.uniform(0.7, 1.1)
                pygame.draw.polygon(sup, cor, [(x - 14, base), (x - 6, base - h), (x + 6, base - h), (x + 14, base)])
                for _ in range(5):
                    cx, cy = x + rng.uniform(-60, 60), base - h + rng.uniform(-10, 40)
                    pygame.draw.circle(sup, cor, (int(cx), int(cy)), int(rng.uniform(24, 44)))
                    for _ in range(3):  # musgo
                        mx = cx + rng.uniform(-30, 30)
                        pygame.draw.line(sup, mistura_cor(cor, (70, 100, 60), 0.4), (mx, cy), (mx, cy + rng.uniform(30, 70)), 3)
        # água atrás do píer
        _degrade(sup, (0, 400, LARGURA, CHAO - 400), (40, 66, 56), (22, 40, 36))
        for _ in range(9):  # vitórias-régias
            x, y = rng.uniform(0, LARGURA), rng.uniform(412, CHAO - 14)
            r = rng.uniform(14, 26)
            pygame.draw.ellipse(sup, (52, 110, 54), (x - r, y - r * 0.32, r * 2, r * 0.64))
            pygame.draw.polygon(sup, (40, 66, 56), [(x, y), (x + r, y - 2), (x + r, y + 3)])
            if rng.random() < 0.4:
                pygame.draw.circle(sup, (236, 170, 200), (int(x - r * 0.3), int(y - 4)), 5)
        # píer de madeira
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (112, 84, 56), (64, 46, 32))
        for k in range(1, 6):
            y = CHAO + (ALTURA - CHAO) * (k / 6) ** 1.4
            pygame.draw.line(sup, (54, 38, 26), (0, y), (LARGURA, y), 2)
        for x in range(30, LARGURA, 160):  # postes
            pygame.draw.rect(sup, (70, 50, 32), (x, CHAO - 26, 14, 30))
            pygame.draw.rect(sup, (40, 28, 18), (x, CHAO - 26, 14, 30), 2)
        pygame.draw.line(sup, (150, 116, 80), (0, CHAO), (LARGURA, CHAO), 3)
        névoa = pygame.Surface((LARGURA, 80), pygame.SRCALPHA)
        for y in range(80):
            névoa.fill((180, 210, 190, int(40 * math.sin(y / 80 * math.pi))), (0, y, LARGURA, 1))
        sup.blit(névoa, (0, 360))
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(5)
        self.vaga = [[rng.uniform(0, LARGURA), rng.uniform(180, 460), rng.uniform(0, math.tau)] for _ in range(22)]
        self.taboas = [(rng.uniform(0, 140) if i % 2 else rng.uniform(LARGURA - 140, LARGURA), rng.uniform(0.8, 1.3))
                       for i in range(12)]

    def animar(self, tela, t, px):
        for i in range(5):  # ondinhas na água
            y = (412 + i * 14) / px
            x = ((t * 0.6 + i * 170) % (LARGURA + 200) - 100) / px
            pygame.draw.line(tela, (90, 130, 110), (x, y), (x + 40 / px, y), 1)
        for v in self.vaga:  # vaga-lumes
            v[2] += 0.04
            x = v[0] + math.sin(v[2] * 1.3) * 20
            y = v[1] + math.cos(v[2]) * 12
            if math.sin(v[2] * 3) > -0.2:
                pygame.draw.circle(tela, (230, 255, 140), (int(x / px), int(y / px)), max(1, 3 // px))

    def desenhar_frente(self, tela, t, px=1):
        for x, e in self.taboas:  # taboas balançando nos cantos
            vento = math.sin(t * 0.04 + x * 0.03) * 6 * e
            topo = (x + vento, ALTURA - 120 * e)
            pygame.draw.line(tela, (40, 70, 36), (x / px, ALTURA / px), (topo[0] / px, topo[1] / px), max(1, 3 // px))
            pygame.draw.ellipse(tela, (96, 64, 36), (topo[0] / px - 3 / px, topo[1] / px - 4, max(2, 7 // px), 9))


# =====================================================================
# FERRO-VELHO (Max-10)
# =====================================================================
class FerroVelho(Base):
    nome = "FERRO-VELHO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (70, 44, 40), (220, 130, 70))
        _brilho(sup, (240, 300), 170, (255, 180, 100), 90)
        rng = random.Random(8)
        for x in (90, 160, 820):  # chaminés
            pygame.draw.rect(sup, (60, 40, 38), (x, 170, 26, 260))
            pygame.draw.rect(sup, (150, 60, 40), (x, 190, 26, 10))
        pygame.draw.rect(sup, (54, 38, 36), (40, 300, 220, 140))  # fábrica
        for i in range(6):
            pygame.draw.rect(sup, (230, 170, 80), (56 + i * 34, 330, 14, 18))
        # guindaste
        pygame.draw.line(sup, (40, 30, 30), (620, CHAO), (620, 120), 10)
        for y in range(130, CHAO, 30):
            pygame.draw.line(sup, (40, 30, 30), (614, y), (626, y + 30), 3)
        pygame.draw.line(sup, (40, 30, 30), (560, 130), (900, 130), 10)
        # pilhas de carros velhos
        for base, n in ((CHAO - 4, 4), (CHAO - 48, 3)):
            for i in range(n):
                x = 300 + i * 90 + (20 if base < CHAO - 10 else 0) + rng.uniform(-10, 10)
                cor = rng.choice(((110, 60, 50), (70, 80, 90), (120, 100, 50), (60, 70, 60)))
                pygame.draw.rect(sup, cor, (x, base - 44, 84, 40), border_radius=6)
                pygame.draw.rect(sup, mistura_cor(cor, (0, 0, 0), 0.5), (x + 14, base - 58, 50, 18), border_radius=4)
                pygame.draw.rect(sup, (30, 24, 24), (x, base - 44, 84, 40), 2, border_radius=6)
                for rx in (x + 16, x + 66):
                    pygame.draw.circle(sup, (24, 20, 20), (int(rx), int(base - 4)), 9)
        for i in range(4):  # tambores de óleo
            x = 760 + i * 34
            pygame.draw.rect(sup, (60, 90, 120) if i % 2 else (140, 60, 40), (x, CHAO - 40, 28, 40))
            pygame.draw.line(sup, (20, 20, 20), (x, CHAO - 26), (x + 28, CHAO - 26), 2)
        # cerca de arame
        for x in range(0, LARGURA, 18):
            pygame.draw.line(sup, (90, 70, 60), (x, 380), (x + 30, CHAO - 50), 1)
            pygame.draw.line(sup, (90, 70, 60), (x + 30, 380), (x, CHAO - 50), 1)
        # chão de concreto
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (120, 112, 104), (70, 66, 62))
        for _ in range(8):  # manchas de óleo
            x, y = rng.uniform(0, LARGURA), rng.uniform(CHAO + 10, ALTURA - 10)
            pygame.draw.ellipse(sup, (54, 50, 50), (x, y, rng.uniform(30, 80), rng.uniform(6, 14)))
        for x in range(0, LARGURA, 40):  # faixa amarela e preta
            pygame.draw.polygon(sup, (220, 180, 40), [(x, CHAO), (x + 20, CHAO), (x + 30, CHAO + 8), (x + 10, CHAO + 8)])
        pygame.draw.line(sup, (40, 36, 34), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def animar(self, tela, t, px):
        for i, x in enumerate((90, 160, 820)):  # fumaça das chaminés
            for k in range(4):
                u = (t * 0.6 + k * 30 + i * 13) % 120
                pygame.draw.circle(tela, (110, 90, 86), (int((x + 13 + u * 0.6) / px), int((170 - u) / px)),
                                   max(2, int((8 + u * 0.18) / px)))
        a = math.sin(t * 0.03) * 0.25  # gancho balançando
        topo = (840, 130)
        ponta = (topo[0] + math.sin(a) * 150, topo[1] + math.cos(a) * 150)
        pygame.draw.line(tela, (30, 24, 24), (topo[0] / px, topo[1] / px), (ponta[0] / px, ponta[1] / px), 1)
        pygame.draw.rect(tela, (60, 60, 64), (ponta[0] / px - 14 / px, ponta[1] / px, 28 / px, 12 / px))
        if (t // 20) % 2:  # luz de alerta piscando
            pygame.draw.circle(tela, (255, 60, 40), (int(620 / px), int(116 / px)), max(2, 6 // px))
        if (t // 3) % 7 < 3:  # faíscas de solda
            rng = random.Random(t // 3)
            for _ in range(6):
                pygame.draw.line(tela, (255, 230, 150), (int(470 / px), int(400 / px)),
                                 (int((470 + rng.uniform(-30, 30)) / px), int((400 + rng.uniform(-30, 10)) / px)), 1)


# =====================================================================
# TOCA (Trafo)
# =====================================================================
class Toca(Base):
    nome = "TOCA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (26, 18, 14), (70, 48, 30))
        rng = random.Random(3)
        for x in (160, 520, 800):  # luz entrando por buracos no teto
            luz = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            pygame.draw.polygon(luz, (255, 230, 170, 30), [(x - 20, 0), (x + 20, 0), (x + 120, CHAO), (x - 40, CHAO)])
            sup.blit(luz, (0, 0))
            pygame.draw.ellipse(sup, (200, 190, 150), (x - 24, -8, 48, 16))
        for cor, base in (((44, 30, 22), 360), ((34, 24, 18), 420)):  # pedras do fundo
            pts = [(0, CHAO)] + [(x, base - 50 * abs(math.sin(x * 0.011 + base))) for x in range(0, LARGURA + 30, 30)] + \
                [(LARGURA, CHAO)]
            pygame.draw.polygon(sup, cor, pts)
        pygame.draw.rect(sup, (20, 14, 10), (0, 0, LARGURA, 40))  # teto
        for _ in range(26):  # raízes penduradas
            x = rng.uniform(0, LARGURA)
            pts = [(x, 30)]
            for k in range(1, 6):
                pts.append((pts[-1][0] + rng.uniform(-8, 8), 30 + k * rng.uniform(12, 26)))
            pygame.draw.lines(sup, (70, 50, 30), False, pts, 3)
        for _ in range(10):  # ossinhos e pedras
            x = rng.uniform(0, LARGURA)
            pygame.draw.ellipse(sup, (90, 80, 70), (x, CHAO - 8, rng.uniform(14, 30), 10))
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (96, 70, 44), (52, 36, 24))
        for _ in range(60):  # pedrinhas no chão
            pygame.draw.circle(sup, (70, 52, 36), (int(rng.uniform(0, LARGURA)), int(rng.uniform(CHAO + 6, ALTURA))),
                               int(rng.uniform(1, 4)))
        pygame.draw.line(sup, (120, 90, 60), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(9)
        self.cogumelos = [(rng.uniform(20, LARGURA - 20), rng.choice(((80, 220, 200), (140, 240, 120))), rng.uniform(0.7, 1.3))
                          for _ in range(9)]
        self.gotas = [(rng.uniform(0, LARGURA), rng.uniform(0, 200)) for _ in range(7)]

    def animar(self, tela, t, px):
        for x, cor, e in self.cogumelos:  # cogumelos que brilham
            pulso = 0.6 + 0.4 * math.sin(t * 0.05 + x)
            y = CHAO - 2
            r = 10 * e
            pygame.draw.circle(tela, mistura_cor((40, 30, 20), cor, pulso * 0.5),
                               (int(x / px), int((y - 14 * e) / px)), max(2, int(r * 1.8 / px)))
            pygame.draw.line(tela, (200, 190, 160), (x / px, y / px), (x / px, (y - 14 * e) / px), max(1, int(3 * e / px)))
            pygame.draw.ellipse(tela, mistura_cor((60, 60, 50), cor, pulso),
                                (int((x - r) / px), int((y - 14 * e - r * 0.6) / px), max(2, int(2 * r / px)),
                                 max(2, int(r / px))))
        for x, fase in self.gotas:  # gotas pingando do teto
            u = (t * 4 + fase * 3) % 600
            if u < CHAO - 40:
                pygame.draw.line(tela, (150, 190, 220), (x / px, (40 + u) / px), (x / px, (46 + u) / px), 1)


# =====================================================================
# DOJO (King Rip)
# =====================================================================
class Dojo(Base):
    nome = "DOJO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (70, 44, 30), (120, 80, 52))
        pygame.draw.rect(sup, (50, 30, 20), (0, 0, LARGURA, 60))  # viga do teto
        for x in range(0, LARGURA, 120):
            pygame.draw.rect(sup, (40, 24, 16), (x, 0, 18, CHAO))  # pilares
        for i, x in enumerate((140, 380, 620)):  # portas de papel (shoji) com luz atrás
            pygame.draw.rect(sup, (236, 222, 180), (x, 120, 180, 280))
            for k in range(1, 4):
                pygame.draw.line(sup, (90, 60, 40), (x + k * 45, 120), (x + k * 45, 400), 4)
            for k in range(1, 6):
                pygame.draw.line(sup, (90, 60, 40), (x, 120 + k * 47), (x + 180, 120 + k * 47), 4)
            pygame.draw.rect(sup, (60, 36, 24), (x, 120, 180, 280), 8)
        for x, cor in ((70, (150, 30, 30)), (880, (30, 50, 120))):  # estandartes com símbolo
            pygame.draw.rect(sup, cor, (x - 30, 70, 60, 200))
            pygame.draw.circle(sup, (230, 210, 150), (x, 150), 20, 4)
            pygame.draw.line(sup, (230, 210, 150), (x - 12, 150), (x + 12, 150), 4)
        # suporte de armas (bastões e nunchakus)
        pygame.draw.rect(sup, (60, 36, 24), (820, 300, 110, 10))
        pygame.draw.rect(sup, (60, 36, 24), (820, 380, 110, 10))
        for k in range(4):
            pygame.draw.line(sup, (160, 110, 60), (830 + k * 26, 290), (836 + k * 26, CHAO - 4), 5)
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (176, 150, 96), (120, 96, 60))  # tatame
        for x in range(0, LARGURA, 120):
            pygame.draw.line(sup, (100, 80, 50), (x, CHAO), (x - 60, ALTURA), 3)
        pygame.draw.line(sup, (60, 40, 26), (0, CHAO), (LARGURA, CHAO), 4)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(6)
        self.po = [[rng.uniform(140, 800), rng.uniform(120, 420), rng.uniform(0, math.tau)] for _ in range(30)]

    def animar(self, tela, t, px):
        for x in (110, 850):  # lanternas tremeluzindo
            a = 0.7 + 0.3 * math.sin(t * 0.2 + x)
            pygame.draw.circle(tela, mistura_cor((120, 60, 20), (255, 190, 90), a), (int(x / px), int(300 / px)),
                               max(2, 10 // px))
        for p in self.po:  # pozinho flutuando na luz
            p[2] += 0.02
            x = p[0] + math.sin(p[2]) * 16
            y = (p[1] - t * 0.15) % 300 + 120
            tela.set_at((int(x / px), int(y / px)), (250, 236, 200))


# =====================================================================
# CAMPO DE BATALHA (Cannan)
# =====================================================================
class CampoBatalha(Base):
    nome = "CAMPO DE BATALHA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (40, 40, 46), (150, 110, 80))  # céu de fumaça no fim da tarde
        _brilho(sup, (700, 330), 200, (255, 150, 80), 70)  # incêndio lá longe
        rng = random.Random(12)
        for cor, base, amp in (((70, 62, 58), 380, 40), ((56, 50, 46), 420, 26)):  # morros e ruínas
            pts = [(0, CHAO)] + [(x, base - amp * abs(math.sin(x * 0.009 + base))) for x in range(0, LARGURA + 30, 30)] + \
                [(LARGURA, CHAO)]
            pygame.draw.polygon(sup, cor, pts)
        for x, h in ((120, 90), (300, 60), (760, 110)):  # prédios destruídos
            pts = [(x, 420), (x, 420 - h), (x + 20, 420 - h + 14), (x + 34, 420 - h - 6), (x + 60, 420 - h + 20), (x + 60, 420)]
            pygame.draw.polygon(sup, (44, 40, 40), pts)
            for k in range(3):
                pygame.draw.rect(sup, (26, 24, 26), (x + 8 + k * 18, 420 - h + 30, 8, 10))
        for x in (230, 620):  # holofotes
            pygame.draw.rect(sup, (40, 40, 44), (x - 4, CHAO - 90, 8, 90))
            pygame.draw.rect(sup, (60, 60, 66), (x - 14, CHAO - 104, 28, 16))
        # sacos de areia e arame farpado
        for i in range(LARGURA // 34 + 1):
            for fila, y in ((0, CHAO - 14), (1, CHAO - 28)):
                x = i * 34 + fila * 17 - 10
                if fila and i % 3 == 0:
                    continue
                pygame.draw.ellipse(sup, (140, 120, 80), (x, y, 36, 16))
                pygame.draw.ellipse(sup, (90, 76, 50), (x, y, 36, 16), 2)
        for x in range(0, LARGURA, 22):
            pygame.draw.line(sup, (90, 86, 80), (x, CHAO - 44), (x + 22, CHAO - 40), 1)
            pygame.draw.line(sup, (90, 86, 80), (x + 10, CHAO - 46), (x + 12, CHAO - 38), 1)
        for x in range(40, LARGURA, 180):
            pygame.draw.line(sup, (60, 50, 40), (x, CHAO - 50), (x, CHAO - 28), 3)
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (96, 84, 64), (54, 46, 36))  # terra
        for _ in range(9):  # crateras
            x, y = rng.uniform(0, LARGURA), rng.uniform(CHAO + 10, ALTURA - 12)
            w = rng.uniform(40, 90)
            pygame.draw.ellipse(sup, (44, 38, 30), (x, y, w, w * 0.22))
            pygame.draw.ellipse(sup, (110, 98, 76), (x, y, w, w * 0.22), 2)
        for _ in range(30):  # cápsulas de bala no chão
            pygame.draw.rect(sup, (190, 160, 70), (rng.uniform(0, LARGURA), rng.uniform(CHAO + 6, ALTURA - 4), 3, 2))
        pygame.draw.line(sup, (40, 34, 28), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(4)
        self.cinzas = [[rng.uniform(0, LARGURA), rng.uniform(0, CHAO), rng.uniform(0, math.tau)] for _ in range(26)]

    def animar(self, tela, t, px):
        for x, fase in ((230, 0.0), (620, 2.0)):  # luz dos holofotes varrendo o céu
            a = -math.pi / 2 + math.sin(t * 0.012 + fase) * 0.6
            topo = (x, CHAO - 100)
            luz = [(topo[0] / px, topo[1] / px)]
            for d in (-0.08, 0.08):
                luz.append(((topo[0] + math.cos(a + d) * 600) / px, (topo[1] + math.sin(a + d) * 600) / px))
            camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(camada, (255, 240, 200, 26), luz)
            tela.blit(camada, (0, 0))
        ciclo = t % 170  # explosão lá longe
        if ciclo < 26:
            rng = random.Random(t // 170)
            x, y = rng.uniform(80, LARGURA - 80), rng.uniform(330, 400)
            r = (6 + ciclo * 1.6) / px
            cor = mistura_cor((255, 230, 140), (120, 80, 60), ciclo / 26)
            pygame.draw.circle(tela, cor, (int(x / px), int(y / px)), max(2, int(r)))
        for c in self.cinzas:  # cinzas caindo
            c[2] += 0.03
            x = (c[0] + math.sin(c[2]) * 20 + t * 0.2) % LARGURA
            y = (c[1] + t * 0.4) % CHAO
            tela.set_at((int(x / px), int(y / px)), (200, 190, 180) if int(c[0]) % 3 else (255, 150, 80))


# =====================================================================
# TORRE DO MAGO (Finn)
# =====================================================================
class TorreMago(Base):
    nome = "TORRE DO MAGO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (30, 22, 46), (62, 48, 80))  # parede de pedra
        rng = random.Random(21)
        for y in range(0, CHAO, 26):  # tijolos de pedra
            off = 0 if (y // 26) % 2 else 30
            for x in range(-30 + off, LARGURA, 60):
                c = rng.randint(-6, 6)
                pygame.draw.rect(sup, (48 + c, 38 + c, 66 + c), (x + 2, y + 2, 56, 22))
        # janelão redondo com o céu de noite e a lua
        cx, cy, r = LARGURA // 2, 190, 120
        pygame.draw.circle(sup, (20, 26, 60), (cx, cy), r)
        for _ in range(40):
            a, d = rng.uniform(0, math.tau), rng.uniform(0, r - 10)
            sup.set_at((int(cx + math.cos(a) * d), int(cy + math.sin(a) * d)), (230, 230, 255))
        _brilho(sup, (cx + 40, cy - 30), 70, (220, 220, 255), 70)
        pygame.draw.circle(sup, (236, 236, 220), (cx + 40, cy - 30), 30)
        pygame.draw.circle(sup, (210, 210, 196), (cx + 32, cy - 36), 6)
        pygame.draw.circle(sup, (60, 46, 30), (cx, cy), r, 14)
        pygame.draw.line(sup, (60, 46, 30), (cx - r, cy), (cx + r, cy), 8)
        pygame.draw.line(sup, (60, 46, 30), (cx, cy - r), (cx, cy + r), 8)
        # estantes de livros nos lados
        for x0 in (30, LARGURA - 230):
            pygame.draw.rect(sup, (70, 44, 26), (x0, 120, 200, 300))
            for k in range(4):
                y = 140 + k * 70
                x = x0 + 10
                while x < x0 + 186:
                    w = rng.randint(8, 16)
                    h = rng.randint(40, 56)
                    cor = rng.choice(((140, 40, 40), (40, 80, 140), (60, 120, 60), (150, 120, 40), (90, 50, 120)))
                    pygame.draw.rect(sup, cor, (x, y + 56 - h, w, h))
                    x += w + 2
                pygame.draw.rect(sup, (50, 30, 18), (x0, y + 56, 200, 8))
        # mesa com a bola de cristal
        pygame.draw.rect(sup, (80, 50, 30), (640, CHAO - 70, 120, 12))
        pygame.draw.rect(sup, (60, 36, 20), (650, CHAO - 58, 10, 58))
        pygame.draw.rect(sup, (60, 36, 20), (740, CHAO - 58, 10, 58))
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (70, 58, 84), (40, 32, 50))  # chão de pedra
        for x in range(0, LARGURA, 80):
            pygame.draw.line(sup, (34, 28, 44), (x, CHAO), (x - 40, ALTURA), 2)
        # tapete com círculo mágico
        pygame.draw.ellipse(sup, (90, 30, 50), (LARGURA // 2 - 260, CHAO + 8, 520, 40))
        pygame.draw.ellipse(sup, (200, 160, 80), (LARGURA // 2 - 240, CHAO + 12, 480, 32), 2)
        pygame.draw.line(sup, (30, 24, 40), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(5)
        self.velas = [(rng.uniform(260, 700), rng.uniform(250, 380), rng.uniform(0, math.tau)) for _ in range(7)]

    def animar(self, tela, t, px):
        for x, y, f in self.velas:  # velas flutuando
            yy = y + math.sin(t * 0.03 + f) * 8
            pygame.draw.rect(tela, (236, 228, 200), (int(x / px), int(yy / px), max(1, 6 // px), max(2, 18 // px)))
            chama = (255, 200, 90) if (t // 6 + int(f * 10)) % 3 else (255, 240, 160)
            pygame.draw.circle(tela, chama, (int((x + 3) / px), int((yy - 4) / px)), max(1, 4 // px))
        pulso = 0.5 + 0.5 * math.sin(t * 0.05)  # bola de cristal brilhando
        cor = mistura_cor((90, 60, 160), (200, 160, 255), pulso)
        pygame.draw.circle(tela, cor, (int(700 / px), int((CHAO - 88) / px)), max(3, int(20 / px)))
        pygame.draw.circle(tela, (240, 230, 255), (int(694 / px), int((CHAO - 94) / px)), max(1, int(4 / px)))


# =====================================================================
# CASSINO (Kun)
# =====================================================================
class Cassino(Base):
    nome = "CASSINO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (36, 10, 22), (80, 24, 36))
        for x in range(0, LARGURA, 48):  # cortinas vermelhas
            pygame.draw.rect(sup, (110, 20, 34), (x, 0, 30, 300))
            pygame.draw.rect(sup, (80, 12, 24), (x + 30, 0, 18, 300))
        pygame.draw.rect(sup, (200, 160, 70), (0, 296, LARGURA, 8))  # faixa dourada
        # letreiro com os naipes
        pygame.draw.rect(sup, (20, 8, 16), (LARGURA // 2 - 170, 160, 340, 80), border_radius=14)
        pygame.draw.rect(sup, (255, 210, 90), (LARGURA // 2 - 170, 160, 340, 80), 4, border_radius=14)
        f = pygame.font.SysFont("arialblack,arial", 48, bold=True)
        for i, (naipe, cor) in enumerate((("♠", (240, 240, 250)), ("♥", (255, 70, 90)), ("♦", (255, 70, 90)),
                                          ("♣", (240, 240, 250)))):
            img = f.render(naipe, True, cor)
            sup.blit(img, img.get_rect(center=(LARGURA // 2 - 120 + i * 80, 200)))
        # máquinas caça-níquel no fundo
        for x in (40, 120, 760, 840):
            pygame.draw.rect(sup, (60, 50, 70), (x, 320, 70, 140), border_radius=8)
            pygame.draw.rect(sup, (20, 16, 24), (x + 10, 344, 50, 30))
            for k in range(3):
                pygame.draw.rect(sup, (240, 230, 200), (x + 13 + k * 16, 348, 13, 22))
            pygame.draw.line(sup, (200, 200, 210), (x + 70, 360), (x + 82, 330), 3)
            pygame.draw.circle(sup, (220, 40, 40), (x + 82, 328), 6)
        # mesas de carta (verde)
        for x in (300, 560):
            pygame.draw.ellipse(sup, (20, 14, 16), (x - 4, 386, 108, 34))
            pygame.draw.ellipse(sup, (30, 110, 60), (x, 388, 100, 28))
            pygame.draw.rect(sup, (60, 30, 20), (x + 44, 414, 12, CHAO - 414))
            for k in range(3):
                pygame.draw.rect(sup, (240, 240, 236), (x + 22 + k * 20, 394, 12, 16))
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (120, 24, 36), (60, 10, 20))  # carpete vermelho
        for x in range(0, LARGURA, 40):
            pygame.draw.circle(sup, (160, 120, 50), (x + 20, CHAO + 24), 4)
        pygame.draw.line(sup, (200, 160, 70), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def animar(self, tela, t, px):
        for i, x in enumerate((160, 800)):  # lustres balançando
            a = math.sin(t * 0.02 + i) * 0.05
            topo = (x, 0)
            base = (x + math.sin(a) * 100, math.cos(a) * 100)
            pygame.draw.line(tela, (60, 50, 40), (topo[0] / px, 0), (base[0] / px, base[1] / px), 1)
            for k in range(5):
                bx = base[0] + (k - 2) * 14
                brilha = (t // 8 + k + i) % 4 != 0
                pygame.draw.circle(tela, (255, 230, 160) if brilha else (200, 160, 90),
                                   (int(bx / px), int((base[1] + 6) / px)), max(1, int(4 / px) + 1))
        for i, x in enumerate((40, 120, 760, 840)):  # luzinhas das máquinas
            for k in range(5):
                acesa = (t // 6 + k + i * 2) % 5 == 0
                cor = (255, 220, 80) if acesa else (90, 70, 40)
                pygame.draw.rect(tela, cor, (int((x + 6 + k * 13) / px), int(326 / px), max(1, int(6 / px)),
                                             max(1, int(6 / px))))


# =====================================================================
# LABORATÓRIO (Xenomorph) — o salão de contenção do jogo de terror do Gomes
# =====================================================================
class Laboratorio(Base):
    nome = "LABORATÓRIO"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (10, 18, 22), (24, 40, 44))
        rng = random.Random(31)
        for x in range(0, LARGURA, 64):  # placas de metal da parede
            pygame.draw.rect(sup, (20, 32, 36), (x + 2, 60, 60, CHAO - 60))
            pygame.draw.line(sup, (40, 58, 62), (x + 2, 60), (x + 2, CHAO), 2)
        pygame.draw.rect(sup, (14, 22, 26), (0, 0, LARGURA, 60))  # teto com canos
        for y in (18, 40):
            pygame.draw.line(sup, (50, 62, 66), (0, y), (LARGURA, y), 8)
        # tanques de contenção (um quebrado)
        for i, x in enumerate((140, 380, 620, 840)):
            quebrado = i == 2
            pygame.draw.rect(sup, (40, 50, 54), (x - 50, 140, 100, 18))
            pygame.draw.rect(sup, (40, 50, 54), (x - 50, CHAO - 40, 100, 40))
            vidro = pygame.Surface((90, CHAO - 198), pygame.SRCALPHA)
            vidro.fill((60, 160, 120, 40 if quebrado else 90))
            sup.blit(vidro, (x - 45, 158))
            if not quebrado:
                pygame.draw.rect(sup, (90, 200, 150), (x - 45, 220, 90, CHAO - 260))
                pygame.draw.ellipse(sup, (20, 40, 34), (x - 20, 260, 40, 90))  # um vulto lá dentro
            else:
                for _ in range(6):  # vidro estourado
                    a = rng.uniform(0, math.tau)
                    pygame.draw.line(sup, (170, 220, 210), (x, 300), (x + math.cos(a) * 46, 300 + math.sin(a) * 60), 2)
            pygame.draw.rect(sup, (110, 140, 140), (x - 45, 158, 90, CHAO - 198), 3)
        for _ in range(9):  # gosma preta (resina) nas paredes
            x = rng.uniform(0, LARGURA)
            pts = [(x, 60)]
            for k in range(1, 6):
                pts.append((x + rng.uniform(-24, 24), 60 + k * rng.uniform(20, 50)))
            pygame.draw.lines(sup, (6, 8, 10), False, pts, rng.randint(6, 14))
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (40, 50, 52), (18, 24, 26))  # chão de grade
        for x in range(0, LARGURA, 24):
            pygame.draw.line(sup, (26, 34, 36), (x, CHAO), (x - 30, ALTURA), 2)
        pygame.draw.ellipse(sup, (60, 110, 30), (600, CHAO + 14, 120, 16))  # poça de ácido velha
        pygame.draw.line(sup, (70, 90, 92), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def animar(self, tela, t, px):
        a = t * 0.05  # luz de alarme girando
        cx, cy = 480, 52
        camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        for lado in (0, math.pi):
            ang = a + lado
            pts = [(cx / px, cy / px), ((cx + math.cos(ang - 0.18) * 700) / px, (cy + abs(math.sin(ang - 0.18)) * 500) / px),
                   ((cx + math.cos(ang + 0.18) * 700) / px, (cy + abs(math.sin(ang + 0.18)) * 500) / px)]
            pygame.draw.polygon(camada, (255, 40, 30, 22), pts)
        tela.blit(camada, (0, 0))
        pygame.draw.circle(tela, (255, 60, 40) if (t // 10) % 2 else (140, 20, 20), (int(cx / px), int(cy / px)),
                           max(2, int(8 / px)))
        for i, x in enumerate((140, 380, 840)):  # bolhas subindo nos tanques
            for k in range(3):
                u = ((t * 1.5 + k * 40 + i * 17) % 120) / 120
                pygame.draw.circle(tela, (170, 240, 200), (int((x - 20 + k * 20) / px), int((CHAO - 50 - u * 180) / px)),
                                   1)
        if (t // 7) % 23 == 0:  # luz piscando (falhando)
            escuro = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
            escuro.fill((0, 0, 0, 90))
            tela.blit(escuro, (0, 0))


# =====================================================================
# ARENA DE SUMÔ (Tai)
# =====================================================================
class ArenaSumo(Base):
    nome = "ARENA DE SUMÔ"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (40, 24, 20), (90, 56, 40))
        rng = random.Random(17)
        for fila, (y, cor) in enumerate(((250, (50, 34, 30)), (300, (64, 42, 36)), (350, (78, 52, 42)))):  # plateia
            for x in range(-10, LARGURA + 20, 26):
                xx = x + (13 if fila % 2 else 0) + rng.uniform(-3, 3)
                pygame.draw.circle(sup, cor, (int(xx), y), 11)
                pygame.draw.rect(sup, cor, (xx - 12, y + 6, 24, 30), border_radius=6)
        # o teto pendurado (tsuriyane) com as borlas coloridas nos cantos
        pygame.draw.polygon(sup, (60, 40, 30), [(160, 60), (800, 60), (860, 110), (100, 110)])
        pygame.draw.rect(sup, (120, 30, 40), (110, 110, 740, 14))
        for x, cor in ((130, (40, 120, 60)), (330, (220, 220, 220)), (630, (200, 40, 40)), (830, (30, 30, 30))):
            pygame.draw.line(sup, (90, 70, 50), (x, 124), (x, 190), 2)
            pygame.draw.polygon(sup, cor, [(x - 10, 190), (x + 10, 190), (x + 6, 230), (x - 6, 230)])
        for x in (60, 900):  # estandartes
            pygame.draw.rect(sup, (230, 210, 170), (x - 18, 130, 36, 160))
            for k in range(4):
                pygame.draw.rect(sup, (30, 24, 20), (x - 8, 150 + k * 34, 16, 18))
        # o ringue de barro (dohyo) com a corda em círculo
        pygame.draw.polygon(sup, (180, 150, 110), [(40, CHAO), (920, CHAO), (LARGURA, ALTURA), (0, ALTURA)])
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (200, 170, 126), (150, 120, 86))
        pygame.draw.ellipse(sup, (230, 220, 190), (110, CHAO + 4, 740, 48), 6)  # a corda (tawara)
        for x in (420, 540):  # as linhas brancas do começo
            pygame.draw.line(sup, (250, 250, 250), (x, CHAO + 20), (x, CHAO + 34), 4)
        pygame.draw.line(sup, (120, 90, 60), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def animar(self, tela, t, px):
        rng = random.Random(t // 8)
        for _ in range(4):  # flashes de câmera na plateia
            if rng.random() < 0.5:
                x, y = rng.uniform(0, LARGURA), rng.choice((250, 300, 350))
                pygame.draw.circle(tela, (255, 255, 240), (int(x / px), int(y / px)), max(1, int(3 / px)))
        for x in (130, 330, 630, 830):  # borlas balançando
            a = math.sin(t * 0.04 + x) * 3
            pygame.draw.line(tela, (200, 180, 120), (int((x + a) / px), int(230 / px)), (int((x + a * 2) / px),
                                                                                         int(244 / px)), 1)


# =====================================================================
# SELVA (Tamer)
# =====================================================================
class Selva(Base):
    nome = "SELVA"

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (40, 80, 60), (120, 170, 110))
        rng = random.Random(41)
        # cachoeira lá no fundo
        pygame.draw.polygon(sup, (60, 90, 70), [(560, 40), (760, 40), (790, CHAO - 60), (530, CHAO - 60)])
        for k in range(8):
            x = 580 + k * 24
            pygame.draw.line(sup, (200, 230, 240), (x, 50), (x + rng.uniform(-6, 6), CHAO - 70), 6)
        pygame.draw.ellipse(sup, (220, 240, 250), (500, CHAO - 90, 320, 50))
        for cor, base, amp in (((46, 92, 54), 300, 60), ((34, 74, 42), 380, 40)):  # morros de mato
            pts = [(0, CHAO)] + [(x, base - amp * abs(math.sin(x * 0.012 + base))) for x in range(0, LARGURA + 30, 30)] + \
                [(LARGURA, CHAO)]
            pygame.draw.polygon(sup, cor, pts)
        for x in (40, 200, 860):  # troncos grandes
            pygame.draw.rect(sup, (70, 50, 34), (x, 0, 46, CHAO))
            pygame.draw.rect(sup, (90, 66, 44), (x + 6, 0, 12, CHAO))
            for _ in range(6):  # copa
                cx, cy = x + 23 + rng.uniform(-90, 90), rng.uniform(-20, 90)
                pygame.draw.circle(sup, rng.choice(((30, 80, 40), (40, 100, 50), (26, 66, 34))), (int(cx), int(cy)),
                                   int(rng.uniform(50, 80)))
        for _ in range(14):  # cipós
            x = rng.uniform(0, LARGURA)
            pts = [(x, 0)]
            for k in range(1, 8):
                pts.append((x + math.sin(k * 0.9) * 10, k * rng.uniform(30, 45)))
            pygame.draw.lines(sup, (50, 110, 50), False, pts, 3)
        for _ in range(20):  # folhagem perto do chão
            x = rng.uniform(0, LARGURA)
            for k in range(5):
                a = -math.pi / 2 + (k - 2) * 0.5
                pygame.draw.line(sup, (40, 120, 50), (x, CHAO), (x + math.cos(a) * 40, CHAO + math.sin(a) * 40), 6)
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (94, 72, 46), (54, 40, 26))  # chão de terra
        pygame.draw.rect(sup, (70, 130, 160), (0, CHAO + 30, LARGURA, 18))  # riozinho
        pygame.draw.line(sup, (120, 180, 200), (0, CHAO + 32), (LARGURA, CHAO + 32), 2)
        pygame.draw.line(sup, (40, 90, 40), (0, CHAO), (LARGURA, CHAO), 3)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(8)
        self.passaros = [[rng.uniform(0, LARGURA), rng.uniform(40, 160), rng.uniform(0.6, 1.4)] for _ in range(4)]
        self.vagalumes = [(rng.uniform(0, LARGURA), rng.uniform(200, CHAO - 20), rng.uniform(0, math.tau)) for _ in range(14)]

    def animar(self, tela, t, px):
        for k in range(10):  # a água da cachoeira descendo
            y = (t * 4 + k * 40) % (CHAO - 120) + 50
            pygame.draw.line(tela, (240, 250, 255), (int((585 + k * 18) / px), int(y / px)),
                             (int((585 + k * 18) / px), int((y + 14) / px)), 1)
        for p in self.passaros:  # passarinhos voando
            p[0] = (p[0] + p[2]) % (LARGURA + 40)
            asa = 4 if (t // 6) % 2 else -2
            x, y = p[0] / px, p[1] / px
            pygame.draw.lines(tela, (30, 40, 30), False, [(x - 4, y + asa / px), (x, y), (x + 4, y + asa / px)], 1)
        for x, y, f in self.vagalumes:  # bichinhos brilhando
            if math.sin(t * 0.08 + f) > 0.3:
                tela.set_at((int((x + math.sin(t * 0.02 + f) * 20) / px), int(y / px)), (230, 255, 150))


# =====================================================================
# VILA DOS SAPOS (secreta: código ULTRA-MEGA-VILLAGE) — a vila do jogo do Ribbat
# =====================================================================
def _casinha(s, x, base, k=1.0):
    """Casinha de folha da Vila dos Sapos (igual à do jogo do Ribbat, quadrinhos.py)."""
    pygame.draw.ellipse(s, (60, 130, 66), (x - 34 * k, base - 50 * k, 68 * k, 70 * k))
    pygame.draw.ellipse(s, (90, 170, 80), (x - 28 * k, base - 46 * k, 50 * k, 40 * k))
    pygame.draw.rect(s, (60, 130, 66), (x - 34 * k, base - 16 * k, 68 * k, 16 * k))
    pygame.draw.ellipse(s, (50, 34, 22), (x - 10 * k, base - 26 * k, 20 * k, 30 * k))
    pygame.draw.line(s, (40, 100, 50), (x, base - 50 * k), (x + 6 * k, base - 60 * k), max(1, int(3 * k)))


def _bandeirinha(s, x, y, k, t):
    """A bandeira verde da Vila dos Sapos, com a vitória-régia (igual à do jogo do Ribbat)."""
    onda = math.sin(t * 0.1) * 3 * k
    pts = [(x, y), (x + 34 * k, y + 2 * k + onda), (x + 32 * k, y + 22 * k + onda), (x, y + 20 * k)]
    pygame.draw.polygon(s, (96, 196, 84), pts)
    pygame.draw.polygon(s, (40, 112, 50), pts, max(1, int(2 * k)))
    cx, cy = x + 16 * k, y + 11 * k + onda / 2
    pygame.draw.circle(s, (230, 245, 160), (int(cx), int(cy)), max(1, int(6 * k)))
    pygame.draw.line(s, (96, 196, 84), (cx, cy), (cx + 6 * k, cy - 4 * k), max(1, int(2 * k)))


class VilaSapos(Base):
    nome = "VILA DOS SAPOS"
    BANDEIRAS = ((150, 300), (470, 270), (790, 300))  # (x, topo do mastro)

    def _fundo(self):
        sup = pygame.Surface((LARGURA, ALTURA))
        _degrade(sup, (0, 0, LARGURA, CHAO), (150, 200, 240), (255, 220, 170))  # manhã
        _brilho(sup, (820, 90), 90, (255, 240, 170), 120)
        pygame.draw.circle(sup, (255, 236, 150), (820, 90), 40)
        rng = random.Random(23)
        for _ in range(5):  # nuvenzinhas
            x, y = rng.uniform(0, LARGURA), rng.uniform(40, 170)
            for i in range(4):
                pygame.draw.circle(sup, (250, 246, 240), (int(x + i * 22), int(y + (i % 2) * 6)), 18)
        for x in range(-20, LARGURA + 40, 34):  # a floresta lá longe
            alt = 150 + (x * 53 % 60)
            pygame.draw.polygon(sup, (70, 120, 90), [(x - 30, CHAO - 90), (x, CHAO - 90 - alt * 0.6), (x + 30, CHAO - 90)])
        pts = [(0, CHAO)] + [(x, CHAO - 110 - 26 * math.sin(x * 0.01)) for x in range(0, LARGURA + 40, 40)] + [(LARGURA, CHAO)]
        pygame.draw.polygon(sup, (110, 180, 96), pts)  # morrinho de grama
        for x, k in ((70, 1.6), (300, 1.2), (620, 1.4), (900, 1.8)):  # as casinhas de folha
            _casinha(sup, x, CHAO - 34, k)
        for x, topo in self.BANDEIRAS:  # mastros (as bandeiras balançam no animar)
            pygame.draw.line(sup, (230, 220, 190), (x, CHAO - 30), (x, topo), 4)
        _degrade(sup, (0, CHAO, LARGURA, ALTURA - CHAO), (96, 170, 84), (70, 130, 66))  # o chão de grama
        pygame.draw.line(sup, (60, 120, 56), (0, CHAO), (LARGURA, CHAO), 3)
        pygame.draw.rect(sup, (60, 120, 160), (0, CHAO + 26, LARGURA, ALTURA - CHAO - 26))  # o lago na frente
        pygame.draw.line(sup, (140, 200, 230), (0, CHAO + 28), (LARGURA, CHAO + 28), 2)
        return sup

    def __init__(self):
        super().__init__()
        rng = random.Random(5)
        self.regias = [(rng.uniform(0, LARGURA), CHAO + rng.uniform(36, 52), rng.uniform(60, 110), rng.uniform(0, 6))
                       for _ in range(7)]
        self.libelulas = [[rng.uniform(0, LARGURA), rng.uniform(220, 400), rng.uniform(0, 6)] for _ in range(3)]

    def animar(self, tela, t, px):
        for x, topo in self.BANDEIRAS:
            _bandeirinha(tela, (x + 2) / px, topo / px, 1.3 / px, t + x)
        for x, y, w, f in self.regias:  # vitórias-régias boiando
            y += math.sin(t * 0.05 + f) * 2
            pygame.draw.ellipse(tela, (70, 140, 76), ((x - w / 2) / px, (y - w * 0.12) / px, w / px, w * 0.24 / px))
            pygame.draw.polygon(tela, (60, 120, 160), [(x / px, y / px), ((x + w / 2) / px, (y - w * 0.06) / px),
                                                       ((x + w / 2) / px, (y + w * 0.06) / px)])
        for b in self.libelulas:  # libélulas
            b[2] += 0.03
            x = (b[0] + t * 0.8) % (LARGURA + 60) - 30
            y = b[1] + math.sin(b[2] * 2) * 20
            pygame.draw.line(tela, (60, 140, 200), ((x - 6) / px, y / px), ((x + 6) / px, y / px), max(1, 2 // px))
            if (t // 2) % 2:
                pygame.draw.line(tela, (220, 240, 255), (x / px, (y - 4) / px), (x / px, (y + 4) / px), 1)


SECRETOS = {"VILA DOS SAPOS": "ULTRA-MEGA-VILLAGE"}  # cenário: código que libera


def disponiveis():
    """Os cenários que dá pra escolher (os secretos só depois do código)."""
    import codigos
    return [n for n in CENARIOS if n not in SECRETOS or codigos.ativo(SECRETOS[n])]


Templo.nome = "TEMPLO"
CENARIOS = {"TEMPLO": Templo, "PÂNTANO": Pantano, "FERRO-VELHO": FerroVelho, "TOCA": Toca, "DOJO": Dojo,
            "CAMPO DE BATALHA": CampoBatalha, "TORRE DO MAGO": TorreMago, "CASSINO": Cassino, "LABORATÓRIO": Laboratorio, "ARENA DE SUMÔ": ArenaSumo, "SELVA": Selva,
            "VILA DOS SAPOS": VilaSapos}
_prontos = {}


def cenario(nome):
    """Pega o cenário pelo nome (desenha o fundo uma vez só e guarda)."""
    if nome not in _prontos:
        _prontos[nome] = CENARIOS[nome]()
    return _prontos[nome]
