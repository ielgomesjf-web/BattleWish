"""CHOQUE (v2.0, estilo Budokai Tenkaichi): quando os dois acertam um golpe forte AO MESMO TEMPO,
ou dois tiros especiais se encontram no meio (cabo de guerra de poder), a luta congela e os dois
APERTAM SOCO/CHUTE O MAIS RÁPIDO QUE CONSEGUEM. Quem empurrar a barra até o fim ganha:
o golpe dele entra 1,5x mais forte (e o tiro dele passa por cima do outro). Empate: os dois voam pra trás.
Tudo vem das Entradas (o ONLINE manda as mesmas pros dois PCs), então dá igual nos dois."""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande

DURACAO = 210        # no máximo 3,5 segundos de choque
EMPURRAO = 0.065     # quanto cada apertada empurra a barra (1 = ganhou)
FORCA_VENCEDOR = 1.5
COMECO = 20          # quadros de "CHOQUE!" antes de começar a contar (pra dar tempo de entender)


def forte(l):
    """Golpe que pode entrar em choque: especial (sem ser agarrão de ultimate) ou golpe normal pesado."""
    g = l.golpe if l.estado == "ataque" else None
    if not g or g.get("provocacao"):
        return False
    if g.get("ultimate") and g.get("logica"):
        return False  # (ultimate com cena própria: não congela no meio)
    return bool(g.get("especial")) or g.get("dano", 0) >= 10


def apertou(e):
    """Só soco e chute contam (o especial fica 'guardado' vários quadros e contaria várias vezes)."""
    return bool(e.soco or e.chute)


class Choque:
    def __init__(self, partida, ponto, tiros=None):
        self.p = partida
        self.ponto = ponto              # onde a energia se encontra
        self.tiros = tiros              # (tiro do lado 0, tiro do lado 1) no choque de tiros; None no corpo a corpo
        self.pos = 0.0                  # > 0: o lado 0 está ganhando
        self.t = 0
        self.apertos = [0, 0]
        self.pulso = [0, 0]             # (desenho: brilho de quem acabou de apertar)
        self.acabou = False
        som.tocar("explosao", 0.8)
        partida.tremer(10)

    def passo(self, ents):
        self.t += 1
        for i in (0, 1):
            self.pulso[i] = max(0, self.pulso[i] - 1)
            if self.t > COMECO and apertou(ents[i]):
                self.apertos[i] += 1
                self.pulso[i] = 6
                self.pos += EMPURRAO * (1 if i == 0 else -1)
        if self.t > COMECO and self.t % 8 == 0:
            som.tocar("carga", 0.35)
        if abs(self.pos) >= 1 or self.t >= DURACAO:
            self.resolver()

    def resolver(self):
        p = self.p
        self.acabou = True
        vence = 0 if self.pos > 0.05 else 1 if self.pos < -0.05 else None
        if vence is not None:
            p.L[vence].bonus_amarelo(BONUS_CHOQUE)  # 2ª ULTIMATE: vencer o choque enche a amarela
        if vence == 0:
            p.stats["choques"] += 1  # (ESTATÍSTICAS / MISSÕES: choques que o jogador ganhou)
        p.choque_txt = ("EMPATE!" if vence is None else "VENCEU O CHOQUE!", vence, 80)
        p.tremer(18)
        p.clarao = 6
        som.tocar("ko", 0.7)
        if self.tiros:  # cabo de guerra de tiros: o de quem ganhou passa (mais forte), o outro some
            for i, t in enumerate(self.tiros):
                if vence is None or i != vence:
                    t.vivo = False
                else:
                    t.golpe = dict(t.golpe, dano=t.golpe["dano"] * FORCA_VENCEDOR)
            return
        a, b = p.L
        if vence is None:  # empate: os dois voam pra trás
            for l, sinal in ((a, -1 if a.x < b.x else 1), (b, -1 if b.x < a.x else 1)):
                l.mudar("parado")
                l.vx = 9 * sinal
            return
        ganhou, perdeu = p.L[vence], p.L[1 - vence]
        g = ganhou.memo.get("g_hit", ganhou.golpe) if ganhou.estado == "ataque" else None
        if not g or "dano" not in g:  # (o golpe dele já tinha acabado: entra um chutão)
            from golpes import GOLPES
            g = GOLPES["chute"]
        g = dict(g, dano=g["dano"] * FORCA_VENCEDOR)
        perdeu.mudar("parado")  # (o golpe dele foi cancelado: não defende, leva tudo)
        perdeu.estado = "golpeado"
        ganhou.acertou = True
        res = perdeu.receber(g, 1 if perdeu.x > ganhou.x else -1, ganhou, ganhou.f["forca"])
        p.faisca(self.ponto[0], self.ponto[1], res == "def", True)
        if res == "hit":
            p.registrar_hit(ganhou, ganhou.nome_golpe, getattr(ganhou, "golpe_id", 0))

    # ---- desenho ----
    def desenhar(self, tela):
        t = self.t
        cx, cy = self.ponto
        escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escuro.fill((10, 6, 20, 70))
        tela.blit(escuro, (0, 0))
        # a bola de energia no meio, empurrada pro lado de quem está perdendo
        x = cx + self.pos * 60
        cores = [(120, 190, 255), (255, 110, 90)]
        for k in range(5, 0, -1):
            r = 14 + k * 9 + math.sin(t * 0.6 + k) * 4
            mix = 0.5 + 0.5 * max(-1, min(1, -self.pos))
            cor = tuple(int(cores[0][j] * (1 - mix) + cores[1][j] * mix) for j in range(3))
            sup = pygame.Surface((int(r * 2), int(r * 2)), pygame.SRCALPHA)
            pygame.draw.circle(sup, (*cor, 40 + k * 10), (int(r), int(r)), int(r))
            tela.blit(sup, (x - r, cy - r))
        pygame.draw.circle(tela, (255, 255, 240), (int(x), int(cy)), 12)
        rng = random.Random(t)  # (só desenho: raios saindo)
        for _ in range(6):
            a = rng.uniform(0, math.tau)
            d = rng.uniform(30, 70)
            pygame.draw.line(tela, (255, 255, 220), (x, cy), (x + math.cos(a) * d, cy + math.sin(a) * d), 2)
        # a barra de cabo de guerra
        larg = 420
        bx, by = LARGURA // 2 - larg // 2, 96
        meio = bx + larg // 2 + int(self.pos * larg / 2)
        pygame.draw.rect(tela, (12, 10, 20), (bx - 4, by - 4, larg + 8, 30), border_radius=8)
        pygame.draw.rect(tela, (60, 120, 230), (bx, by, meio - bx, 22), border_radius=6)
        pygame.draw.rect(tela, (230, 70, 60), (meio, by, bx + larg - meio, 22), border_radius=6)
        pygame.draw.rect(tela, (255, 255, 240), (meio - 3, by - 6, 6, 34))
        for i in (0, 1):
            if self.pulso[i]:
                lado_x = bx - 20 if i == 0 else bx + larg + 20
                pygame.draw.circle(tela, cores[i], (lado_x, by + 11), 8 + self.pulso[i] * 2, 3)
        if t <= COMECO:
            texto_grande(tela, "CHOQUE!", 52, (255, 230, 90), (LARGURA // 2, 170), 1 + (COMECO - t) / COMECO,
                         contorno=(60, 20, 0))
        else:
            pisca = (t // 6) % 2
            texto_grande(tela, "CHOQUE!", 40, (255, 230, 90), (LARGURA // 2, 160), contorno=(60, 20, 0))
            texto(tela, "APERTA SOCO OU CHUTE O MAIS RÁPIDO QUE DER!", 18,
                  (255, 255, 255) if pisca else (255, 220, 120), (LARGURA // 2, 140 + 54))
