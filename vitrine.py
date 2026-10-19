"""TELA INICIAL COM O FAVORITO (v2.x, pedido do Gomes): no menu, o lutador FAVORITO fica lutando contra a
SOMBRA dele, no meio da tela, médio, meio apagado (atrás das opções do menu).

  O favorito é escolhido no PERFIL (aba ESTATÍSTICAS, botão FAVORITO / tecla F). Sem escolher: o mais jogado.
  A luta é uma Partida de TREINO (ninguém morre, a vida volta) com os dois no computador (MÉDIO), SEM SOM.
  Não conta pra nada (estatísticas, missões, maestria...): o treino nunca chega no fim da luta.

No save: save.d()["favorito"] = "MAGNUS" (ou não tem).

Como usar (o menu, luta.py):
  self.vitrine = vitrine.Vitrine()        (uma vez)
  no desenho do título, DEPOIS do fundo e ANTES do logo/opções:
      self.vitrine.passo(); self.vitrine.desenhar(tela)
  vitrine.favorito() / vitrine.definir_favorito(nome)
"""
import random

import pygame

import save
import som
from config import *  # noqa: F401,F403

ESCALA = 0.78        # "médio"
ALFA = 125           # meio apagado
ESCURO = (150, 140, 175)  # multiplica a cor (puxa pro roxo escuro do menu)
CHAO_NA_TELA = 478   # onde fica o chão dos lutadores no menu (o tablado)
CADA = 3             # a imagem nova sai a cada 3 quadros (o trabalho é dividido entre eles)
RENOVA = 90 * FPS    # a cada 1,5 min começa uma luta nova (limpa tudo)


def _fichas():
    from personagens import PERSONAGENS, SECRETOS
    return PERSONAGENS + SECRETOS


def disponiveis():
    """Quem pode ser favorito: os normais + os secretos já liberados."""
    from personagens import disponiveis as d
    return d()


def favorito():
    """O nome do favorito: o escolhido no perfil; senão o mais jogado; senão o MAX-10."""
    nomes = [f["nome"] for f in disponiveis()]
    fav = save.d().get("favorito")
    if fav in nomes:
        return fav
    try:
        import estatisticas
        mj = estatisticas.personagem_favorito()
        if mj and mj[1] > 0 and mj[0] in nomes:
            return mj[0]
    except Exception:
        pass
    return nomes[0] if nomes else "MAX-10"


def escolhido():
    """O favorito escolhido de propósito (ou None, se está usando o mais jogado)."""
    fav = save.d().get("favorito")
    return fav if fav in [f["nome"] for f in disponiveis()] else None


def definir_favorito(nome):
    save.d()["favorito"] = nome
    save.salvar()


class _Mudo:
    """Desliga o som enquanto a luta do menu anda."""
    def __enter__(self):
        self.t, self.m = som.tocar, getattr(som, "musica", None)
        som.tocar = lambda *a, **k: None
        if self.m:
            som.musica = lambda *a, **k: None

    def __exit__(self, *a):
        som.tocar = self.t
        if self.m:
            som.musica = self.m


class Vitrine:
    def __init__(self):
        self.p = None
        self.de = None
        self.t = 0
        self.camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self.sorte = random.Random().getstate()  # (random só da vitrine: não mexe no random do jogo)

    def _nova(self):
        from controles import Computador
        from partida import Partida
        import roupas
        nome = favorito()
        f = next((f for f in _fichas() if f["nome"] == nome), _fichas()[0])
        eu = roupas.vestir(f)                 # com a roupa que ele usa
        sombra = roupas.vestir(f, "sombra")   # a SOMBRA dele
        fora = random.getstate()
        random.setstate(self.sorte)
        with _Mudo():
            self.p = Partida(eu, sombra, Computador("MÉDIO"), Computador("MÉDIO"), treino=True,
                             cenario_nome=f.get("cenario", "TEMPLO"))
        self.sorte = random.getstate()
        random.setstate(fora)
        self.de = nome
        self.t = 0

    def passo(self):
        if self.p is None or self.de != favorito() or self.t >= RENOVA or self.p.fase not in ("luta",):
            self._nova()
        self.t += 1
        fora = random.getstate()
        random.setstate(self.sorte)
        with _Mudo():
            try:
                self.p.passo(None)
            except Exception:  # (a vitrine nunca pode derrubar o menu)
                self.p = None
        self.sorte = random.getstate()
        random.setstate(fora)

    def _area(self):
        """O pedaço da camada onde a luta está (os lutadores e os projéteis), alinhado no PIXEL."""
        xs = [l.x for l in self.p.L] + [pr.x for pr in self.p.projeteis if hasattr(pr, "x")]
        if any(l.f.get("tela_toda") or (l.estado == "ataque" and l.memo.get("tela_toda")) for l in self.p.L):
            return pygame.Rect(0, 0, LARGURA, ALTURA)
        x0 = max(0, int(min(xs)) - 300) // PIXEL * PIXEL
        x1 = min(LARGURA, -(-(int(max(xs)) + 300) // PIXEL) * PIXEL)
        return pygame.Rect(x0, 0, max(PIXEL, x1 - x0), ALTURA)

    def desenhar(self, tela):
        """O trabalho é dividido em 3 quadros (desenhar um lutador custa ~13 ms):
        quadro 1 desenha o de trás, quadro 2 o da frente (e os projéteis), quadro 3 junta e faz a imagem.
        Enquanto isso, a tela mostra a imagem pronta anterior."""
        if self.p is None:
            return
        if not hasattr(self, "camadas"):
            self.camadas = (self.camada, pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA))
            self.fase_d = 0
            self.pronto = None
        a, b = self.camadas
        try:
            if self.fase_d == 0:
                self.ordem = sorted(self.p.L, key=lambda l: l.estado == "ataque")  # (quem ataca fica na frente)
                a.fill((0, 0, 0, 0))
                self.ordem[0].desenhar(a)
            elif self.fase_d == 1:
                b.fill((0, 0, 0, 0))
                self.ordem[1].desenhar(b)
                for pr in self.p.projeteis:
                    pr.desenhar(b)
            else:
                self.pronto = self._juntar(a, b)
        except Exception:
            self.fase_d = 0
            return
        self.fase_d = (self.fase_d + 1) % CADA
        if self.pronto:
            tela.blit(*self.pronto)

    def _juntar(self, a, b):
        r = self._area()
        a.blit(b.subsurface(r), r.topleft)
        # pixel art (igual a luta) + escurece no pequeno (barato) + amplia já no tamanho "médio"
        peq = pygame.transform.smoothscale(a.subsurface(r), (r.w // PIXEL, r.h // PIXEL))
        cor = getattr(self, "_cor_escura", None)
        if cor is None or cor.get_size() != peq.get_size():
            cor = self._cor_escura = pygame.Surface(peq.get_size())
            cor.fill(ESCURO)
        peq.blit(cor, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        img = pygame.transform.scale(peq, (int(r.w * ESCALA), int(r.h * ESCALA)))
        img.set_alpha(ALFA)
        x = (LARGURA - int(LARGURA * ESCALA)) // 2
        y = CHAO_NA_TELA - int(CHAO * ESCALA)
        return img, (x + int(r.x * ESCALA), y + int(r.y * ESCALA))
