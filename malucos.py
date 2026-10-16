"""MODOS MALUCOS: regras doidas pra ligar antes da luta (dá pra misturar).
Valem no 1 JOGADOR, 2 JOGADORES, TRIO, TORNEIO, TREINO e CPU x CPU (no Arcade, Sobrevivência, Combos e Online não).
Com algum modo ligado não ganha moeda (senão ficava fácil demais)."""
import math

import pygame

import save
import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande
from selecao import fundo_selecao

REGRAS = [
    ("lua", "GRAVIDADE DA LUA", "todo mundo pula altíssimo e cai devagarinho"),
    ("cabecoes", "CABEÇÕES", "cabeça gigante (só o desenho: a caixa de acerto é a mesma)"),
    ("turbo", "TURBO", "a luta toda roda 1,5x mais rápido"),
    ("so_ultimate", "SÓ ULTIMATE", "a barra da ultimate enche 5x mais rápido"),
    ("um_golpe", "UM GOLPE MATA", "qualquer golpe que acerta derruba de vez (defender salva!)"),
]
LUA = 0.42
TURBO = 1.5
SO_ULTIMATE = 5


def ligadas():
    return set(save.d().setdefault("regras", []))


def nomes(regras):
    return " + ".join(nome for chave, nome, _ in REGRAS if chave in regras)


class TelaMalucos:
    def __init__(self):
        self.i = 0
        self.t = 0

    def rect(self, i):
        return pygame.Rect(LARGURA // 2 - 300, 130 + i * 62, 600, 54)

    def tecla(self, tecla):
        if tecla in (pygame.K_w, pygame.K_UP):
            self.i = (self.i - 1) % len(REGRAS)
            som.tocar("blip")
        elif tecla in (pygame.K_s, pygame.K_DOWN):
            self.i = (self.i + 1) % len(REGRAS)
            som.tocar("blip")
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE, "clique"):
            lista = save.d().setdefault("regras", [])
            chave = REGRAS[self.i][0]
            if chave in lista:
                lista.remove(chave)
                som.tocar("defesa", 0.6)
            else:
                lista.append(chave)
                som.tocar("confirma")
            save.salvar()

    def mouse(self, pos, clicou):
        for i in range(len(REGRAS)):
            if self.rect(i).collidepoint(pos):
                self.i = i
                if clicou:
                    self.tecla("clique")

    def desenhar(self, tela):
        self.t += 1
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, "MODOS MALUCOS", 44, (255, 220, 70), (LARGURA // 2, 60),
                     1 + 0.03 * math.sin(self.t * 0.15))
        on = ligadas()
        for i, (chave, nome, desc) in enumerate(REGRAS):
            r = self.rect(i)
            sel = i == self.i
            ligado = chave in on
            pygame.draw.rect(tela, (54, 46, 84) if sel else (26, 22, 42), r, border_radius=12)
            pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), r, 3, border_radius=12)
            chave_r = pygame.Rect(r.x + 16, r.y + 14, 52, 26)  # o interruptor
            pygame.draw.rect(tela, (60, 190, 90) if ligado else (70, 60, 80), chave_r, border_radius=13)
            bx = chave_r.right - 13 if ligado else chave_r.x + 13
            pygame.draw.circle(tela, BRANCO, (bx, chave_r.centery), 10)
            img = pygame.font.SysFont("arialblack,arial", 19, bold=True).render(nome, True,
                                                                                 AMARELO if ligado else BRANCO)
            tela.blit(img, (r.x + 84, r.y + 6))
            img = pygame.font.SysFont("arial", 14, bold=True).render(desc, True, (210, 210, 225))
            tela.blit(img, (r.x + 84, r.y + 31))
        if on:
            texto(tela, "ligados: " + nomes(on) + "   (com modo maluco não ganha moeda)", 14, (255, 220, 120),
                  (LARGURA // 2, 456))
        else:
            texto(tela, "nada ligado = luta normal", 14, (200, 200, 220), (LARGURA // 2, 456))
        texto(tela, "W/S escolhe   ENTER liga/desliga   ESC volta", 14, (200, 200, 220), (LARGURA // 2, ALTURA - 16))
