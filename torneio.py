"""TORNEIO: chave de 8 lutadores (você + computadores). Quartas, semi e final; troféu pro campeão.
As lutas entre computadores: ENTER assiste, S pula (simula rapidinho, sem desenhar)."""
import math
import random

import pygame

import roupas
import save
import som
from config import *  # noqa: F401,F403
from controles import Computador
from efeitos import texto, texto_grande, texto_moedas
from selecao import fundo_selecao, retrato

PREMIO_CAMPEAO = 150
FASES = ["QUARTAS DE FINAL", "SEMIFINAL", "FINAL"]


def luta_cpu(f1, f2, nivel, semente=None, regras=()):
    """A luta entre dois computadores do jeito do torneio: 1 round de 40 segundos, já começando.
    Com semente, dá sempre o mesmo resultado (no ONLINE os dois PCs veem a mesma luta)."""
    from partida import Partida
    p = Partida(f1, f2, Computador(nivel), Computador(nivel))
    if semente is not None:
        p.semente = semente
    p.regras.update(regras)  # (ONLINE: os MODOS MALUCOS da sala valem pros computadores também)
    p.rounds = 1
    p.fase, p.tf = "luta", 0
    p.tempo = 40 * FPS
    return p


def vencedor_de(p):
    if p.vencedor in (0, 1):
        return p.vencedor
    return 0 if p.L[0].vida >= p.L[1].vida else 1


def simular(f1, f2, nivel, semente=None, regras=()):
    """Uma luta rapidinha entre dois computadores (1 round, 40 segundos). Devolve 0 ou 1 (quem ganhou)."""
    p = luta_cpu(f1, f2, nivel, semente, regras)
    for _ in range(40 * FPS + 400):
        p.passo(None)
        if p.fase == "fim":
            break
    return vencedor_de(p)


class Torneio:
    def __init__(self, minha_ficha, personagens, nivel):
        rivais = [f for f in personagens if f["nome"] != minha_ficha["nome"]]
        random.shuffle(rivais)
        while len(rivais) < 7:  # (se tiver menos de 8 personagens, repete alguns)
            rivais.append(random.choice(personagens))
        rivais = [roupas.outra(f, "padrao") if f["nome"] == minha_ficha["nome"] else roupas.vestir(f, "padrao")
                  for f in rivais[:7]]
        self.lutadores = [dict(ficha=minha_ficha, humano=True)] + [dict(ficha=f, humano=False) for f in rivais]
        random.shuffle(self.lutadores)
        self.nivel = nivel
        self.chave = [list(range(8))]  # chave[fase] = índices de quem está vivo naquela fase (em pares)
        self.fase = 0
        self.jogo_i = 0               # qual luta da fase é a próxima
        self.resultados = [[None] * 4, [None] * 2, [None]]
        self.campeao = None
        self.t = 0
        self.pago = False
        self.retratos = {}
        self.ultimo = None             # o resultado que acabou de sair (pra piscar na tela)
        self.semente = None            # (ONLINE: as lutas dos computadores saem iguais nos dois PCs)

    @classmethod
    def online(cls, fichas, personagens, nivel, semente, eu):
        """TORNEIO ONLINE: os 2 jogadores (fichas = (quem criou a sala, quem entrou)) + 6 computadores.
        Cada um começa numa metade da chave (só se encontram na FINAL). eu = 0 (criei a sala) ou 1.
        Tudo sorteado com a semente: a chave sai igualzinha nos dois PCs."""
        rng = random.Random(semente)
        t = cls.__new__(cls)
        cls.__init__(t, fichas[0], personagens, nivel)  # (só pra criar as coisas; a chave é montada aqui embaixo)
        nomes = {f["nome"] for f in fichas}
        rivais = [f for f in personagens if f["nome"] not in nomes]
        rng.shuffle(rivais)
        while len(rivais) < 6:
            rivais.append(rng.choice(personagens))
        cpus = [dict(ficha=roupas.vestir(f, "padrao"), humano=False, amigo=False) for f in rivais[:6]]
        for c in cpus:  # (mesmo personagem de um jogador: o computador usa outra roupa)
            for h in fichas:
                if c["ficha"]["nome"] == h["nome"] and c["ficha"].get("roupa") == h.get("roupa"):
                    c["ficha"] = roupas.outra(c["ficha"], h.get("roupa"))
        lugares = [None] * 8
        lugares[rng.randrange(4)] = dict(ficha=fichas[0], humano=eu == 0, amigo=eu == 1)
        lugares[4 + rng.randrange(4)] = dict(ficha=fichas[1], humano=eu == 1, amigo=eu == 0)
        for i in range(8):
            if lugares[i] is None:
                lugares[i] = cpus.pop()
        t.lutadores = lugares
        t.semente = semente
        return t

    # ---- ONLINE: os resultados podem chegar fora de ordem ----
    def par(self, k):
        vivos = self.chave[self.fase]
        return vivos[k * 2], vivos[k * 2 + 1]

    def pendentes(self):
        """As lutas da fase que ainda não têm resultado."""
        if self.campeao is not None:
            return []
        return [k for k, r in enumerate(self.resultados[self.fase]) if r is None]

    def tipo(self, k):
        """'minha' (eu x computador), 'final' (eu x amigo), 'amigo' (amigo x computador) ou 'cpu'."""
        a, b = (self.lutadores[i] for i in self.par(k))
        eu = a["humano"] or b["humano"]
        ele = a.get("amigo") or b.get("amigo")
        return "final" if eu and ele else "minha" if eu else "amigo" if ele else "cpu"

    def semente_luta(self, k):
        return (self.semente or 0) * 31 + self.fase * 8 + k

    def resultado(self, fase, k, lado):
        """Guarda o resultado da luta k da fase (lado 0 ou 1 ganhou). Quando a fase fecha, avança a chave."""
        if fase != self.fase or self.resultados[fase][k] is not None:
            return False
        vivos = self.chave[fase]
        self.resultados[fase][k] = vivos[k * 2 + lado]
        self.ultimo = (fase, k)
        if None in self.resultados[fase]:
            self.jogo_i = self.resultados[fase].index(None)
            return True
        vencedores = self.resultados[fase]
        if fase == 2:
            self.campeao = vencedores[0]
            if self.lutadores[self.campeao]["humano"] and not self.pago:
                self.pago = True
                save.ganhar(PREMIO_CAMPEAO)
            som.tocar("ultimate")
        else:
            self.chave.append(list(vencedores))
            self.fase += 1
            self.jogo_i = 0
        return True

    # ---- quem luta agora ----
    def proxima(self):
        """(a, b) índices da próxima luta, ou None se acabou."""
        if self.campeao is not None:
            return None
        vivos = self.chave[self.fase]
        return vivos[self.jogo_i * 2], vivos[self.jogo_i * 2 + 1]

    def tem_humano(self):
        par = self.proxima()
        return par is not None and any(self.lutadores[i]["humano"] for i in par)

    def humano_vivo(self):
        return any(self.lutadores[i]["humano"] for i in self.chave[self.fase]) and self.campeao is None or \
            (self.campeao is not None and self.lutadores[self.campeao]["humano"])

    def registrar(self, vencedor_lado):
        """Guarda o resultado da luta atual (vencedor_lado 0 ou 1) e avança a chave."""
        self.resultado(self.fase, self.jogo_i, vencedor_lado)

    def simular_proxima(self):
        a, b = self.proxima()
        som.tocar("blip")
        self.registrar(simular(self.lutadores[a]["ficha"], self.lutadores[b]["ficha"], self.nivel))

    def fichas_cpu(self):
        """A luta entre dois computadores (pra assistir): (ficha da esquerda, ficha da direita)."""
        a, b = self.proxima()
        return self.lutadores[a]["ficha"], self.lutadores[b]["ficha"]

    def fichas_da_luta(self):
        """A luta do jogador: (a minha ficha, a do rival, eu estou do lado 0?)"""
        a, b = self.proxima()
        if self.lutadores[a]["humano"]:
            return self.lutadores[a]["ficha"], self.lutadores[b]["ficha"], True
        return self.lutadores[b]["ficha"], self.lutadores[a]["ficha"], False

    # ---- desenho da chave ----
    def ret(self, f):
        nome = f["nome"] + str(f.get("roupa"))
        if nome not in self.retratos:
            self.retratos[nome] = retrato(f, 34)
        return self.retratos[nome]

    def slot(self, tela, i, x, y, perdeu=False, destaque=False):
        lut = self.lutadores[i]
        r = pygame.Rect(x, y, 170, 38)
        pygame.draw.rect(tela, (54, 46, 84) if destaque else (26, 22, 42), r, border_radius=8)
        pygame.draw.rect(tela, (255, 220, 70) if destaque else (70, 62, 100), r, 2, border_radius=8)
        tela.blit(self.ret(lut["ficha"]), (x + 2, y + 2))
        cor = (120, 120, 140) if perdeu else (150, 220, 255) if lut["humano"] else \
            (255, 180, 120) if lut.get("amigo") else BRANCO
        nome = ("VOCÊ: " if lut["humano"] else "AMIGO: " if lut.get("amigo") else "") + lut["ficha"]["nome"]
        img = pygame.font.SysFont("arialblack,arial", 12, bold=True).render(nome, True, cor)
        tela.blit(img, (x + 42, y + 12))
        if perdeu:
            pygame.draw.line(tela, (200, 70, 70), (x + 40, y + 19), (x + 165, y + 19), 2)
        return r

    def desenhar(self, tela, rodape=True):
        self.t += 1
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, "TORNEIO", 40, (255, 220, 70), (LARGURA // 2, 36))
        par_agora = self.proxima()
        colunas = [(20, 4), (290, 2), (560, 1)]  # x de cada fase, quantas lutas
        centros = {}
        for fase, (x, n) in enumerate(colunas):
            if fase >= len(self.chave):
                break
            vivos = self.chave[fase]
            altura = 440 / n
            for k in range(n):
                y0 = 70 + k * altura + altura / 2 - 44
                for lado in (0, 1):
                    i = vivos[k * 2 + lado]
                    venc = self.resultados[fase][k]
                    perdeu = venc is not None and venc != i
                    destaque = par_agora is not None and fase == self.fase and k == self.jogo_i
                    r = self.slot(tela, i, x, y0 + lado * 46, perdeu, destaque)
                    centros[(fase, k, lado)] = r
                # linha até a próxima fase
                if fase < 2:
                    a, b = centros[(fase, k, 0)], centros[(fase, k, 1)]
                    meio_y = (a.centery + b.centery) / 2
                    pygame.draw.lines(tela, (90, 80, 130), False, [(a.right, a.centery), (a.right + 40, a.centery),
                                                                   (a.right + 40, b.centery), (b.right, b.centery)], 2)
                    pygame.draw.line(tela, (90, 80, 130), (a.right + 40, meio_y), (a.right + 80, meio_y), 2)
        # o troféu / campeão
        tx, ty = 860, 270
        if self.campeao is not None:
            k = 1 + 0.05 * math.sin(self.t * 0.15)
            self.trofeu(tela, tx, ty - 30, k)
            camp = self.lutadores[self.campeao]
            texto_grande(tela, "CAMPEÃO!", 24, (255, 220, 70), (tx, ty + 50))
            texto(tela, camp["ficha"]["nome"], 18, (150, 220, 255) if camp["humano"] else BRANCO, (tx, ty + 80))
            if camp["humano"]:
                texto_moedas(tela, f"+{PREMIO_CAMPEAO}", tx + 30, ty + 110, self.t, 20)
            if rodape:
                texto(tela, "ENTER volta pro menu", 15, BRANCO, (LARGURA // 2, ALTURA - 16))
        elif not rodape:
            self.trofeu(tela, tx, ty - 30, 1, apagado=True)
            texto(tela, FASES[self.fase], 16, (255, 220, 120), (tx, ty + 50))
        else:
            self.trofeu(tela, tx, ty - 30, 1, apagado=True)
            texto(tela, FASES[self.fase], 16, (255, 220, 120), (tx, ty + 50))
            if self.tem_humano():
                txt = "ENTER: a SUA luta!"
            elif self.humano_vivo():
                txt = "ENTER: ASSISTIR a luta dos computadores    S: pular"
            else:
                txt = "você caiu...  ENTER: assistir    S: pular"
            texto(tela, txt, 15, BRANCO, (LARGURA // 2, ALTURA - 16))

    def trofeu(self, tela, x, y, k, apagado=False):
        ouro = (120, 110, 90) if apagado else (250, 200, 60)
        escuro = (80, 70, 60) if apagado else (190, 130, 30)
        pygame.draw.polygon(tela, ouro, [(x - 30 * k, y - 30 * k), (x + 30 * k, y - 30 * k), (x + 18 * k, y + 10 * k),
                                         (x - 18 * k, y + 10 * k)])
        pygame.draw.circle(tela, escuro, (int(x - 32 * k), int(y - 16 * k)), int(10 * k), 4)
        pygame.draw.circle(tela, escuro, (int(x + 32 * k), int(y - 16 * k)), int(10 * k), 4)
        pygame.draw.rect(tela, ouro, (x - 5 * k, y + 10 * k, 10 * k, 16 * k))
        pygame.draw.rect(tela, escuro, (x - 22 * k, y + 26 * k, 44 * k, 10 * k))
        if not apagado:
            pygame.draw.circle(tela, (255, 250, 210), (int(x - 10 * k), int(y - 18 * k)), int(5 * k))
