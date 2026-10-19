"""NARRADOR (v2.x, pedido do Gomes): frases grandes e animadas na tela nos momentos marcantes da luta.
Sem voz, só texto. É SÓ DESENHO: lê o estado da partida e não muda nada dela (dá igual no online).

  combo de 10+ golpes                         COMBO INSANO!
  venceu o round com 10% de vida ou menos     POR UM FIO!
  venceu o round sem levar dano               HUMILHAÇÃO!
  perdeu o 1º round e venceu a luta           VIRADA!
  2 parrys seguidos (em até 3 s)              LEITURA PERFEITA!
  acertou a 2ª ULTIMATE                       PODER MÁXIMO!
  K.O. no último segundo do tempo             NO LIMITE!

Como usar (a partida): self.narrador = narrador.Narrador(); no passo: self.narrador.passo(self) (depois de
tudo); no desenho, por cima da luta e antes do HUD: self.narrador.desenhar(tela).
"""
import math

import pygame

from config import *  # noqa: F401,F403
from efeitos import texto_grande

DURACAO = 95          # quadros que a frase fica na tela
COMBO_INSANO = 10
POR_UM_FIO = 0.10     # fração da vida
PARRY_JANELA = 180    # 2 parrys do mesmo lado em até 3 s
NO_LIMITE = FPS       # K.O. com 1 s ou menos no relógio

FRASES = {
    "combo": ("COMBO INSANO!", (255, 140, 40)),
    "fio": ("POR UM FIO!", (255, 80, 80)),
    "humilhacao": ("HUMILHAÇÃO!", (200, 120, 255)),
    "virada": ("VIRADA!", (120, 230, 255)),
    "leitura": ("LEITURA PERFEITA!", (150, 220, 255)),
    "poder": ("PODER MÁXIMO!", (255, 215, 60)),
    "limite": ("NO LIMITE!", (255, 255, 255)),
}


class Narrador:
    def __init__(self):
        self.fila = []            # [(chave, lado)] esperando a vez
        self.atual = None         # (chave, lado, quadros que faltam)
        self.fase = None
        self.round = None
        self.vida_comeco = [None, None]
        self.vencedores = []      # quem venceu cada round (0, 1 ou None)
        self.combo_avisado = [False, False]
        self.ult_parry = [-999, -999]
        self.ult2 = [False, False]
        self.t = 0
        self.historico = []       # (pros testes) todas as frases que saíram: (chave, lado)

    def falar(self, chave, lado):
        self.fila.append((chave, lado))
        self.historico.append((chave, lado))

    def passo(self, p):
        self.t += 1
        L = p.L
        # começo de round: guarda a vida de cada lado
        if p.round != self.round or (self.fase in ("intro", "entrada", "falas") and p.fase == "luta"):
            if p.round != self.round:
                self.round = p.round
                self.combo_avisado = [False, False]
            self.vida_comeco = [p.vida_lado(i) for i in (0, 1)]
        # COMBO INSANO (uma vez por combo)
        for i in (0, 1):
            c = getattr(L[i], "combo", 0)
            if c >= COMBO_INSANO and not self.combo_avisado[i]:
                self.combo_avisado[i] = True
                self.falar("combo", i)
            elif c <= 1:
                self.combo_avisado[i] = False
        # LEITURA PERFEITA: 2 parrys do mesmo lado em pouco tempo
        pt = getattr(p, "parry_txt", None)
        if pt and pt[1] == 60:  # (acabou de acontecer um parry)
            lado = pt[0]
            if p.t_total - self.ult_parry[lado] <= PARRY_JANELA:
                self.falar("leitura", lado)
                self.ult_parry[lado] = -999
            else:
                self.ult_parry[lado] = p.t_total
        # PODER MÁXIMO: a 2ª ultimate acertou
        for i in (0, 1):
            ac = bool(getattr(L[i], "acertou_ult2", False))
            if ac and not self.ult2[i]:
                self.falar("poder", i)
            self.ult2[i] = ac
        # fim do round
        if p.fase == "ko" and self.fase != "ko":
            a, b = p.vida_lado(0), p.vida_lado(1)
            ganhou = 0 if a > b else 1 if b > a else None
            self.vencedores.append(ganhou)
            if ganhou is not None:
                v = (a, b)[ganhou]
                vmax = L[ganhou].vida_max * (3 if getattr(p, "trio", None) else 1)
                if self.vida_comeco[ganhou] is not None and v >= self.vida_comeco[ganhou]:
                    self.falar("humilhacao", ganhou)
                elif v <= vmax * POR_UM_FIO:
                    self.falar("fio", ganhou)
                if getattr(p, "msg", "") == "K.O.!" and getattr(p, "tempo", 999) <= NO_LIMITE:
                    self.falar("limite", ganhou)
        # fim da luta: VIRADA
        if p.fase == "fim" and self.fase != "fim":
            w = p.vencedor
            if w in (0, 1) and len(self.vencedores) >= 2 and self.vencedores[0] == 1 - w:
                self.falar("virada", w)
        self.fase = p.fase
        # a fila: uma frase por vez
        if self.atual:
            c, lado, q = self.atual
            self.atual = (c, lado, q - 1) if q > 1 else None
        if not self.atual and self.fila:
            c, lado = self.fila.pop(0)
            self.atual = (c, lado, DURACAO)

    def desenhar(self, tela):
        if not self.atual:
            return
        chave, lado, q = self.atual
        frase, cor = FRASES[chave]
        k = 1 - q / DURACAO                      # 0 -> 1
        entra = min(1.0, k / 0.12)                # entra crescendo...
        sai = min(1.0, q / 15)                    # ...e some no fim
        esc = (0.4 + 0.8 * entra) * (1 + 0.06 * math.sin(self.t * 0.5)) if entra < 1 else 1.2 + 0.03 * math.sin(self.t * 0.3)
        x = LARGURA // 2 + (-150 if lado == 0 else 150 if lado == 1 else 0)
        texto_grande(tela, frase, 38, cor, (x, 225), esc, alfa=int(255 * sai), contorno=(30, 10, 10))  # (abaixo do PARRY!/combo do jogo)
