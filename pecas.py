"""Peças de pixel art presas no esqueleto.

Cada peça é um desenho feito de letras (cada letra é uma cor da paleta, "." é vazio).
A peça tem dois pontos marcados, A e B (em pixels do desenho). Na hora de desenhar,
A vai pro começo do osso e a peça gira (e estica, se for braço/perna) pra B ficar no fim do osso.
"""
import math

import pygame

TROCA = None        # roupa alternativa: {letra: cor nova} enquanto desenha um lutador
CABECAO = 1.0       # MODO MALUCO "CABEÇÕES": as peças de cabeça ficam desse tamanho
TROCA_CHAVE = None


def usar_troca(troca):
    """Liga (ou desliga, com None) as cores trocadas da roupa alternativa."""
    global TROCA, TROCA_CHAVE
    TROCA = troca or None
    TROCA_CHAVE = tuple(sorted(troca.items())) if troca else None


class Peca:
    def __init__(self, mapa, paleta, a, b, estica=True):
        self.mapa = [linha.rstrip("\n") for linha in mapa]
        self.paleta = paleta
        self.a = (a[0] + 0.5, a[1] + 0.5)  # centro do pixel
        self.b = (b[0] + 0.5, b[1] + 0.5)
        self.estica = estica
        self.w = max(len(linha) for linha in self.mapa)
        self.h = len(self.mapa)
        self._sups = {}

    def sup(self, variante):
        """A imagem da peça: 'normal', 'escuro' (membro de trás) ou 'branco' (piscando quando apanha)."""
        chave = (variante, TROCA_CHAVE)
        if chave not in self._sups:
            s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            for y, linha in enumerate(self.mapa):
                for x, ch in enumerate(linha):
                    if ch == "." or ch == " ":
                        continue
                    cor = TROCA[ch] if TROCA and ch in TROCA else self.paleta[ch]
                    if cor is None:  # (cor escondida: esse pixel não aparece nessa roupa)
                        continue
                    if variante == "escuro":
                        cor = tuple(int(c * 0.7) for c in cor)
                    elif variante == "branco":
                        cor = (150, 150, 160) if ch == "k" else (245, 245, 250)
                    s.set_at((x, y), (*cor, 255))
            self._sups[chave] = s
        return self._sups[chave]

    def desenhar(self, tela, ini, fim, escala, espelho, variante="normal"):
        """Desenha a peça com A em 'ini', apontando pra 'fim'. Devolve uma função que leva
        um ponto do desenho (x, y) pra tela (útil pra achar o olho, por exemplo)."""
        if getattr(self, "cabeca", False):
            escala *= CABECAO
        sup = self.sup(variante)
        ax, ay = self.a
        bx, by = self.b
        if espelho:
            sup = pygame.transform.flip(sup, True, False)
            ax, bx = self.w - ax, self.w - bx
        d1x, d1y = fim[0] - ini[0], fim[1] - ini[1]
        comp1 = math.hypot(d1x, d1y)
        comp0 = math.hypot(bx - ax, by - ay) or 1
        sx = escala
        sy = (comp1 / comp0) if self.estica and comp1 > 0.5 else escala
        nw, nh = max(1, round(self.w * sx)), max(1, round(self.h * sy))
        sx, sy = nw / self.w, nh / self.h
        sup = pygame.transform.scale(sup, (nw, nh))
        ax, ay, bx, by = ax * sx, ay * sy, bx * sx, by * sy
        if comp1 < 0.5:
            teta = 0.0
        else:
            teta = math.atan2(d1y, d1x) - math.atan2(by - ay, bx - ax)
        rot = pygame.transform.rotate(sup, -math.degrees(teta))
        c, s = math.cos(teta), math.sin(teta)
        cx, cy = nw / 2, nh / 2

        def para_tela(px, py):
            if espelho:
                px = self.w - px
            vx, vy = px * sx - cx, py * sy - cy
            return (ini[0] - (ax - cx) * c + (ay - cy) * s + vx * c - vy * s,
                    ini[1] - (ax - cx) * s - (ay - cy) * c + vx * s + vy * c)

        vx, vy = ax - cx, ay - cy
        rx, ry = vx * c - vy * s, vx * s + vy * c
        tela.blit(rot, (round(ini[0] - (rot.get_width() / 2 + rx)), round(ini[1] - (rot.get_height() / 2 + ry))))
        return para_tela
