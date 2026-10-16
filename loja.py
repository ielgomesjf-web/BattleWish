"""A LOJA: compra roupas alternativas com as moedas que ganha lutando."""
import math

import pygame

import roupas
import save
import som
from config import *  # noqa: F401,F403
from efeitos import moeda, texto, texto_grande, texto_moedas
from lutador import Lutador
from selecao import fundo_selecao, retrato

CARTA_LOJA = 84


class TelaLoja:
    def __init__(self, personagens):
        self.lista = personagens
        self.i = 0
        self.j = 0
        self.t = 0
        self.msg, self.msg_t, self.msg_cor = "", 0, BRANCO
        self.cartas = [retrato(f, CARTA_LOJA) for f in personagens]
        self.vitrine = {}
        self.brilho = 0

    def roupas(self):
        return roupas.da(self.lista[self.i])

    # ---- controle ----
    def tecla(self, tecla):
        if tecla in (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP,
                     pygame.K_DOWN):
            som.tocar("blip")
        if tecla in (pygame.K_a, pygame.K_LEFT):
            self.i = (self.i - 1) % len(self.lista)
            self.j = 0
        elif tecla in (pygame.K_d, pygame.K_RIGHT):
            self.i = (self.i + 1) % len(self.lista)
            self.j = 0
        elif tecla in (pygame.K_w, pygame.K_UP):
            self.j = (self.j - 1) % len(self.roupas())
        elif tecla in (pygame.K_s, pygame.K_DOWN):
            self.j = (self.j + 1) % len(self.roupas())
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE, "clique"):
            self.confirmar()

    def rect_carta(self, i):
        n = len(self.lista)
        x0 = LARGURA // 2 - (n * (CARTA_LOJA + 10) - 10) // 2
        return pygame.Rect(x0 + i * (CARTA_LOJA + 10), ALTURA - CARTA_LOJA - 34, CARTA_LOJA, CARTA_LOJA)

    def rect_roupa(self, j):
        passo = min(74, 300 // max(1, len(self.roupas())))
        return pygame.Rect(470, 100 + j * passo, 440, passo - 6)

    def mouse(self, pos, clicou):
        for i in range(len(self.lista)):
            if self.rect_carta(i).collidepoint(pos):
                if clicou and self.i != i:
                    self.i, self.j = i, 0
                    som.tocar("blip")
                return
        for j in range(len(self.roupas())):
            if self.rect_roupa(j).collidepoint(pos):
                self.j = j
                if clicou:
                    self.confirmar()
                return

    def avisar(self, msg, cor):
        self.msg, self.msg_t, self.msg_cor = msg, 120, cor

    def confirmar(self):
        f = self.lista[self.i]
        r = self.roupas()[self.j]
        nome = f["nome"]
        if save.tem_roupa(nome, r["id"]):
            save.usar(nome, r["id"])
            som.tocar("confirma")
            self.avisar(f"{nome} está usando: {r['nome']}", (150, 220, 255))
        elif r.get("codigo"):
            som.tocar("defesa")
            self.avisar("essa só com CÓDIGO SECRETO!", (255, 200, 90))
        elif save.comprar(nome, r["id"], r["preco"]):
            save.usar(nome, r["id"])
            som.tocar("ultimate", 0.6)
            self.brilho = 40
            self.avisar(f"COMPROU! {r['nome']}", (255, 220, 90))
        else:
            som.tocar("defesa")
            self.avisar(f"faltam {r['preco'] - save.moedas()} moedas", (255, 110, 90))

    # ---- desenho ----
    def lutador(self, ficha):
        chave = (ficha["nome"], ficha.get("roupa"))
        if chave not in self.vitrine:
            l = Lutador(ficha, 0, 1)
            l.s = ficha["tam"] * 1.7
            self.vitrine[chave] = l
        return self.vitrine[chave]

    def desenhar(self, tela):
        self.t += 1
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, "LOJA", 44, (255, 220, 70), (LARGURA // 2, 40))
        texto_moedas(tela, save.moedas(), LARGURA - 24, 36, self.t, 26)
        f = self.lista[self.i]
        r = self.roupas()[self.j]
        # o lutador vestindo a roupa escolhida
        x = 230
        luz = pygame.Surface((300, 420), pygame.SRCALPHA)
        for k in range(10, 0, -1):
            pygame.draw.ellipse(luz, (255, 210, 90, 7), (150 - k * 14, 40, k * 28, 380))
        tela.blit(luz, (x - 150, 0))
        pygame.draw.ellipse(tela, (20, 18, 30), (x - 100, 360, 200, 30))
        pygame.draw.ellipse(tela, (255, 210, 90), (x - 100, 360, 200, 30), 3)
        l = self.lutador(roupas.vestir(f, r["id"]))
        l.x, l.y = x, 374
        l.chao_sombra = 374
        l.t = self.t
        l.desenhar(tela)
        if self.brilho > 0:  # brilho de compra
            self.brilho -= 1
            for k in range(8):
                a = self.t * 0.2 + k * 0.785
                d = 60 + (40 - self.brilho) * 3
                moeda(tela, (x + math.cos(a) * d, 230 + math.sin(a) * d * 0.6), 8, self.t + k * 7)
        texto_grande(tela, f["nome"], 26, BRANCO, (x, 410))
        # lista de roupas
        for j, roupa in enumerate(self.roupas()):
            rr = self.rect_roupa(j)
            sel = j == self.j
            tem = save.tem_roupa(f["nome"], roupa["id"])
            usando = save.usando(f["nome"]) == roupa["id"]
            pygame.draw.rect(tela, (54, 46, 84) if sel else (30, 26, 48), rr, border_radius=10)
            pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), rr, 3, border_radius=10)
            cor = roupa.get("cor", f["cor"])
            if roupa.get("codigo") and not tem:
                cor = (60, 54, 80)  # (secreta: não mostra a cor)
            q = min(36, rr.h - 10)
            quad = (rr.x + 14, rr.centery - q // 2, q, q)
            pygame.draw.rect(tela, cor, quad, border_radius=6)
            pygame.draw.rect(tela, (12, 10, 20), quad, 2, border_radius=6)
            baixa = rr.h < 50  # (linha baixinha: letra menor)
            mini = rr.h < 34   # (baixinha demais: tudo numa linha só, o estado na direita)
            nome_r = "???" if roupa.get("codigo") and not tem else roupa["nome"]
            img = pygame.font.SysFont("arialblack,arial", 13 if mini else 15 if baixa else 20, bold=True).render(
                nome_r, True, BRANCO)
            tela.blit(img, (rr.x + 64, rr.centery - img.get_height() // 2 if mini else rr.y + (2 if baixa else 10)))
            if usando:
                estado, cor_e = "USANDO", (150, 220, 255)
            elif tem:
                estado, cor_e = "COMPRADA (ENTER veste)", (170, 230, 170)
            elif roupa.get("codigo"):
                estado, cor_e = "SECRETA: só com código", (255, 200, 90)
            else:
                estado, cor_e = None, None
            if estado and mini:
                estado = {"COMPRADA (ENTER veste)": "COMPRADA", "SECRETA: só com código": "SECRETA"}.get(estado, estado)
                img = pygame.font.SysFont("arial", 12, bold=True).render(estado, True, cor_e)
                tela.blit(img, (rr.right - img.get_width() - 12, rr.centery - img.get_height() // 2))
            elif estado:
                img = pygame.font.SysFont("arial", 13 if baixa else 15, bold=True).render(estado, True, cor_e)
                tela.blit(img, (rr.x + 64, rr.y + (21 if baixa else 38)))
            else:
                pode = save.moedas() >= roupa["preco"]
                texto_moedas(tela, roupa["preco"], rr.x + 160, rr.y + (28 if baixa else 46), self.t, 16)
                if not pode:
                    img = pygame.font.SysFont("arial", 14, bold=True).render("moedas insuficientes", True,
                                                                             (230, 120, 110))
                    tela.blit(img, (rr.x + 176, rr.y + (21 if baixa else 38)))
                    pygame.draw.rect(tela, (230, 120, 110), (rr.right - 34, rr.y + 20, 18, 14), border_radius=3)
                    pygame.draw.arc(tela, (230, 120, 110), (rr.right - 31, rr.y + 10, 12, 16), 0, 3.14, 3)
        if self.msg_t > 0:
            self.msg_t -= 1
            texto(tela, self.msg, 20, self.msg_cor, (690, 404))
        # personagens embaixo
        for i, carta in enumerate(self.cartas):
            rc = self.rect_carta(i)
            tela.blit(carta, rc.topleft)
            pygame.draw.rect(tela, (12, 10, 20), rc, 3)
            if i == self.i:
                pygame.draw.rect(tela, (255, 220, 70), rc.inflate(8, 8), 4 if (self.t // 10) % 2 else 2)
        texto(tela, "A/D personagem   W/S roupa   ENTER ou clique compra/veste   ESC volta", 14, (200, 200, 220),
              (LARGURA // 2, ALTURA - 14))
        texto(tela, "PERFECT, COMBO MÁXIMO e DIFÍCIL dão mais moedas!", 13, (255, 220, 120),
              (690, 76))
