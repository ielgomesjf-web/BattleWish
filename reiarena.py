"""REI DA ARENA (v2.x, pedido do Gomes): modo de festa, pra jogar com os amigos no mesmo PC.
Quem ganha FICA (é o REI), quem perde vai pro fim da fila e passa o controle pro próximo.
O placar mostra a coroa, a sequência de vitórias do rei, a fila e o ranking da noite.
O recorde de sequência fica no save: save.d()["rei_arena"] = {"recorde": n, "quem": nome, "data": "AAAA-MM-DD"}.

O REI luta sempre do lado ESQUERDO (lado 0) e o desafiante do DIREITO (lado 1).
Este arquivo cuida das regras e das telas (nomes e placar); quem roda a seleção e a luta é o luta.py.
"""
import datetime
import math

import pygame

import save
import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande

MIN_JOGADORES, MAX_JOGADORES = 2, 8
MAX_NOME = 10


# =====================================================================
# as REGRAS
# =====================================================================
class ReiArena:
    def __init__(self, nomes):
        nomes = [n.strip()[:MAX_NOME] or f"JOGADOR {i + 1}" for i, n in enumerate(nomes)]
        vistos = set()
        for i, n in enumerate(nomes):  # (nomes repetidos ganham um número)
            base, k = n, 2
            while n in vistos:
                n = f"{base[:MAX_NOME - 2]} {k}"
                k += 1
            vistos.add(n)
            nomes[i] = n
        self.nomes = nomes
        self.rei = nomes[0]
        self.fila = nomes[1:]                 # o primeiro da fila é o próximo desafiante
        self.sequencia = 0                    # vitórias seguidas do rei atual
        self.lutas = 0
        self.placar = {n: dict(vitorias=0, derrotas=0, maior=0) for n in nomes}
        self.lutador = {}                     # nome -> índice do último lutador escolhido (a seleção pode usar)
        self.ultima = None                    # o que aconteceu na última luta (pro placar mostrar)

    def proxima_luta(self):
        """(rei, desafiante): o rei no lado 0, o desafiante no lado 1."""
        return self.rei, self.fila[0]

    def registrar(self, vencedor_lado):
        """Fim da luta. vencedor_lado: 0 = o rei ganhou, 1 = o desafiante ganhou, "empate" = os dois ficam.
        Devolve um dict com o que aconteceu (rei_mudou, novo_recorde, sequencia, ...)."""
        rei, desafiante = self.proxima_luta()
        self.lutas += 1
        info = dict(rei_antes=rei, desafiante=desafiante, rei_mudou=False, novo_recorde=False, empate=False)
        if vencedor_lado == "empate":
            info["empate"] = True  # empate: o rei continua, o desafiante vai pro fim da fila
            self.fila.append(self.fila.pop(0))
        elif vencedor_lado == 0:  # o REI ganhou: fica
            self.sequencia += 1
            self.placar[rei]["vitorias"] += 1
            self.placar[desafiante]["derrotas"] += 1
            self.fila.append(self.fila.pop(0))
        else:  # o desafiante ganhou: vira o novo rei; o rei antigo vai pro fim da fila
            self.placar[desafiante]["vitorias"] += 1
            self.placar[rei]["derrotas"] += 1
            self.fila.pop(0)
            self.fila.append(rei)
            self.rei = desafiante
            self.sequencia = 1
            info["rei_mudou"] = True
        p = self.placar[self.rei]
        p["maior"] = max(p["maior"], self.sequencia)
        info["sequencia"] = self.sequencia
        info["rei"] = self.rei
        info["novo_recorde"] = self.guardar_recorde()
        self.ultima = info
        return info

    def guardar_recorde(self):
        """Se a sequência do rei passou o recorde do save, guarda. Devolve True se é recorde novo."""
        r = recorde()
        if self.sequencia > r["recorde"]:
            save.d()["rei_arena"] = dict(recorde=self.sequencia, quem=self.rei,
                                         data=datetime.date.today().isoformat())
            save.salvar()
            return True
        return False

    def ranking(self):
        """[(nome, vitórias, derrotas, maior sequência)], do melhor pro pior."""
        return sorted(((n, p["vitorias"], p["derrotas"], p["maior"]) for n, p in self.placar.items()),
                      key=lambda x: (-x[3], -x[1], x[2]))


def recorde():
    r = save.d().get("rei_arena")
    if not isinstance(r, dict) or not isinstance(r.get("recorde"), int):
        return dict(recorde=0, quem="", data="")
    return r


# =====================================================================
# desenhos
# =====================================================================
def desenhar_coroa(tela, x, y, t=0, escala=1.0):
    """A coroa do rei (x, y = o meio da base). Dá pra a luta desenhar em cima da cabeça do rei também."""
    s = escala
    sobe = math.sin(t * 0.08) * 2 * s
    base = [(x - 18 * s, y + sobe), (x + 18 * s, y + sobe)]
    pts = [base[0], (x - 20 * s, y - 16 * s + sobe), (x - 9 * s, y - 7 * s + sobe), (x, y - 22 * s + sobe),
           (x + 9 * s, y - 7 * s + sobe), (x + 20 * s, y - 16 * s + sobe), base[1]]
    pygame.draw.polygon(tela, (255, 205, 40), pts)
    pygame.draw.polygon(tela, (150, 100, 10), pts, max(1, int(2 * s)))
    for px, py, cor in ((x, y - 6 * s, (230, 40, 60)), (x - 11 * s, y - 4 * s, (60, 140, 255)),
                        (x + 11 * s, y - 4 * s, (60, 200, 90))):
        pygame.draw.circle(tela, cor, (int(px), int(py + sobe)), max(2, int(3 * s)))
    if (t // 15) % 4 == 0:  # brilhinho
        pygame.draw.circle(tela, (255, 255, 230), (int(x + 14 * s), int(y - 14 * s + sobe)), max(1, int(2 * s)))


def _fundo(tela, t):
    from selecao import fundo_selecao
    tela.blit(fundo_selecao(t), (0, 0))


# =====================================================================
# TELA 1: quem vai jogar
# =====================================================================
class TelaNomes:
    """Cadastra os jogadores (2 a 8). W/S escolhe a linha, digita o nome, + / - (ou A/D na última linha)
    muda quantos são, ENTER no COMEÇAR começa. .pronto + .nomes quando acabar; .sair pra voltar."""

    def __init__(self, nomes=None):
        self.nomes = list(nomes or ["JOGADOR 1", "JOGADOR 2"])
        self.i = 0
        self.t = 0
        self.pronto = False
        self.sair = False
        self.aviso_t = 0

    @property
    def linhas(self):
        return len(self.nomes) + 2  # (+ "QUANTOS JOGADORES" e "COMEÇAR")

    def rect(self, i):
        return pygame.Rect(LARGURA // 2 - 220, 112 + i * 40, 440, 34)

    def mudar_qtd(self, d):
        na_linha = self.i == len(self.nomes)  # (a linha "N JOGADORES" anda junto quando muda)
        n = max(MIN_JOGADORES, min(MAX_JOGADORES, len(self.nomes) + d))
        while len(self.nomes) < n:
            self.nomes.append(f"JOGADOR {len(self.nomes) + 1}")
        del self.nomes[n:]
        self.i = len(self.nomes) if na_linha else min(self.i, self.linhas - 1)
        som.tocar("blip")

    def tecla(self, ev):
        k = ev.key if hasattr(ev, "key") else ev
        uni = getattr(ev, "unicode", "")
        qtd, comecar = len(self.nomes), len(self.nomes) + 1
        if k in (pygame.K_UP,) or (k == pygame.K_w and self.i >= qtd):
            self.i = (self.i - 1) % self.linhas
        elif k in (pygame.K_DOWN, pygame.K_TAB) or (k == pygame.K_s and self.i >= qtd):
            self.i = (self.i + 1) % self.linhas
        elif self.i == qtd and k in (pygame.K_a, pygame.K_LEFT, pygame.K_MINUS, pygame.K_KP_MINUS):
            self.mudar_qtd(-1)
        elif self.i == qtd and k in (pygame.K_d, pygame.K_RIGHT, pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self.mudar_qtd(1)
        elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.i == comecar or self.i < qtd:
                if self.i < qtd:  # ENTER no nome: vai pro próximo
                    self.i += 1
                else:
                    self.pronto = True
                    som.tocar("confirma")
        elif k == pygame.K_ESCAPE:
            self.sair = True
        elif self.i < qtd:  # digitando o nome
            if k == pygame.K_BACKSPACE:
                self.nomes[self.i] = self.nomes[self.i][:-1]
            elif uni and (uni.isalnum() or uni in " -_") and len(self.nomes[self.i]) < MAX_NOME:
                if self.nomes[self.i].startswith("JOGADOR ") and self.nomes[self.i][8:].isdigit():
                    self.nomes[self.i] = ""  # (o nome padrão some quando começa a digitar)
                self.nomes[self.i] += uni.upper()

    def mouse(self, pos, clicou):
        for i in range(self.linhas):
            if self.rect(i).collidepoint(pos):
                self.i = i
                if clicou and i == len(self.nomes) + 1:
                    self.pronto = True
                    som.tocar("confirma")
                elif clicou and i == len(self.nomes):
                    self.mudar_qtd(1 if pos[0] > self.rect(i).centerx else -1)

    def desenhar(self, tela):
        self.t += 1
        _fundo(tela, self.t)
        desenhar_coroa(tela, LARGURA // 2, 52, self.t, 1.4)
        texto_grande(tela, "REI DA ARENA", 38, (255, 220, 70), (LARGURA // 2, 80))
        r = recorde()
        if r["recorde"]:
            texto(tela, f"recorde: {r['quem']} com {r['recorde']} vitórias seguidas", 13, (255, 230, 150),
                  (LARGURA // 2, 104))
        for i in range(self.linhas):
            rr = self.rect(i)
            sel = i == self.i
            pygame.draw.rect(tela, (54, 46, 84) if sel else (26, 22, 42), rr, border_radius=8)
            pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), rr, 2, border_radius=8)
            if i < len(self.nomes):
                cursor = "_" if sel and (self.t // 20) % 2 else ""
                texto(tela, f"{i + 1}.", 16, (190, 190, 210), (rr.x + 26, rr.centery))
                texto(tela, self.nomes[i] + cursor, 18, BRANCO, rr.center)
            elif i == len(self.nomes):
                texto(tela, f"< {len(self.nomes)} JOGADORES >", 17, (255, 220, 70) if sel else BRANCO, rr.center)
            else:
                texto(tela, "COMEÇAR!", 20, (140, 255, 160) if sel else BRANCO, rr.center)
        texto(tela, "↑/↓ escolhe   digita o nome   A/D na linha de jogadores muda quantos   ENTER começa", 12,
              (190, 190, 210), (LARGURA // 2, ALTURA - 24))
        texto(tela, "o REI joga do lado esquerdo (teclado e mouse); o desafiante do direito (controle)", 12,
              (190, 190, 210), (LARGURA // 2, ALTURA - 8))


# =====================================================================
# TELA 2: o placar entre as lutas
# =====================================================================
class TelaPlacar:
    """Entre uma luta e outra: o rei com a coroa, a sequência, quem é o próximo, a fila e o ranking.
    ENTER = próxima luta (.continuar); ESC = acabar a noite (.sair)."""

    def __init__(self, arena):
        self.a = arena
        self.t = 0
        self.continuar = False
        self.sair = False

    def tecla(self, k):
        k = getattr(k, "key", k)
        if k in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
            self.continuar = True
            som.tocar("confirma")
        elif k == pygame.K_ESCAPE:
            self.sair = True

    def mouse(self, pos, clicou):
        if clicou:
            self.continuar = True

    def desenhar(self, tela):
        self.t += 1
        a = self.a
        _fundo(tela, self.t)
        texto_grande(tela, "REI DA ARENA", 32, (255, 220, 70), (LARGURA // 2, 34))
        u = a.ultima
        if u:  # o que aconteceu agora
            if u["empate"]:
                msg, cor = "EMPATE! O rei continua no trono.", (220, 220, 235)
            elif u["rei_mudou"]:
                msg, cor = f"{u['rei']} DERRUBOU {u['rei_antes']}! TEMOS UM NOVO REI!", (255, 140, 110)
            else:
                msg, cor = f"{u['rei']} SEGUE NO TRONO!", (140, 255, 160)
            texto(tela, msg, 18, cor, (LARGURA // 2, 70))
            if u["novo_recorde"] and (self.t // 12) % 2:
                texto_grande(tela, "RECORDE NOVO!", 22, (255, 230, 90), (LARGURA // 2, 96), contorno=(60, 30, 0))
        # o REI
        caixa = pygame.Rect(60, 120, 380, 190)
        pygame.draw.rect(tela, (40, 30, 10), caixa, border_radius=14)
        pygame.draw.rect(tela, (255, 205, 40), caixa, 3, border_radius=14)
        desenhar_coroa(tela, caixa.centerx, caixa.y + 46, self.t, 1.6)
        texto_grande(tela, a.rei, 30, BRANCO, (caixa.centerx, caixa.y + 84))
        texto(tela, f"{a.sequencia} vitória{'s' if a.sequencia != 1 else ''} seguida{'s' if a.sequencia != 1 else ''}",
              18, (255, 230, 120), (caixa.centerx, caixa.y + 122))
        r = recorde()
        if r["recorde"]:
            texto(tela, f"recorde: {r['quem']} ({r['recorde']})", 13, (220, 200, 150), (caixa.centerx, caixa.y + 150))
        # o próximo e a fila
        rei, prox = a.proxima_luta()
        texto(tela, "PRÓXIMO DESAFIANTE", 15, (200, 200, 222), (690, 136))
        texto_grande(tela, prox, 28, (255, 120, 100), (690, 172))
        texto(tela, "lado direito (controle)", 12, (190, 190, 210), (690, 200))
        if len(a.fila) > 1:
            texto(tela, "na fila: " + ", ".join(a.fila[1:6]) + (" ..." if len(a.fila) > 6 else ""), 13,
                  (200, 200, 222), (690, 232))
        # o ranking da noite
        texto(tela, "RANKING DA NOITE", 15, (200, 200, 222), (LARGURA // 2, 336))
        for i, (n, v, d, m) in enumerate(a.ranking()[:6]):
            y = 362 + i * 22
            cor = (255, 220, 70) if n == a.rei else (225, 225, 240)
            texto(tela, f"{i + 1}. {n}", 15, cor, (LARGURA // 2 - 150, y), sombra=False)
            texto(tela, f"{v} V   {d} D   maior sequência {m}", 14, cor, (LARGURA // 2 + 90, y), sombra=False)
        texto(tela, "ENTER: próxima luta (passa o controle!)    ESC: acabar", 13, (220, 220, 235),
              (LARGURA // 2, ALTURA - 14))
