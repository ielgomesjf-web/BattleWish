"""CUTSCENES DA LOJA (ideia do Gomes): as VITÓRIAS caprichadas e a ENTRADA mais cara de cada lutador viram uma CENA
DE ANIME: a animação de verdade (a mesma da arena) roda num palco separado, com FUNDO PRÓPRIO, e é FILMADA em
PLANOS (geral, close, câmera lenta no clímax, linhas de velocidade), com faixas de cinema e o pixel fosco das cenas.

Regras do Gomes: NÃO dá pra pular (a pessoa pagou pra ver) e dura no máximo uns 4 segundos (240 quadros).
Só o jogador vê (o computador e o online usam as poses originais). É só imagem: não mexe em nada da luta.

Um PLANO = (quadros, zoom, foco, fundo, velocidade):
  foco: "geral" (o palco todo), "corpo" (o lutador), "cabeca" (close no rosto), "alvo" (o derrotado), "acima" (o céu)
  fundo: "luz" (holofote), "veloc" (linhas de velocidade), "ceu" (degradê), "noite" (escuro com estrelas)
  velocidade: 1 = normal, 0.5 = câmera lenta (a animação anda metade)
"""
import math
import random

import pygame

import cutscene
from config import *  # noqa: F401,F403

DURACAO_MAX = 360  # (6 segundos: o Gomes liberou cenas maiores)
X0 = LARGURA * 0.38  # onde o lutador fica no palco da cena


class Palco:
    """O "jogo" de mentira onde a animação roda (o mesmo jeito da prévia da loja)."""

    def __init__(self, l, o=None):
        self.L = [l, o or l]
        self.faiscas = []
        self.projeteis = []
        self.t_total = 0
        self.cena = None
        self.tremor = 0

    def tremer(self, n):
        self.tremor = max(self.tremor, n)

    def faisca(self, x, y, defendeu=False, forte=False):
        pass

    def passo(self):
        self.t_total += 1
        if self.tremor > 0:
            self.tremor -= 1
        for f in self.faiscas:
            f[0] += f[2]
            f[1] += f[3]
            f[3] += 0.3
            f[4] -= 1
        self.faiscas = [f for f in self.faiscas if f[4] > 0]

    def desenhar(self, tela):
        for f in self.faiscas:
            tam = f[6] * min(1, f[4] / 12) if len(f) > 6 else f[4] // 4
            pygame.draw.circle(tela, f[5], (int(f[0]), int(f[1])), max(2, int(tam)))


def planos_auto(climax, fim, foco_climax="corpo", fundo="luz", foco_fim="geral"):
    """Os planos de sempre: abre GERAL, aproxima, CÂMERA LENTA no clímax (com linhas de velocidade) e fecha geral.
    climax / fim = quadros da animação (da arena) em que acontece o principal / em que ela termina."""
    a = max(16, int(climax * 0.45))           # 1) geral
    b = max(10, climax - a - 8)               # 2) aproximando
    c = 40                                     # 3) clímax em câmera lenta (anda 20 quadros da animação)
    resto = max(20, fim - (a + b + c // 2))  # 4) final geral
    planos = [(a, 1.1, "geral", fundo, 1.0), (b, 1.7, "corpo", fundo, 1.0), (c, 2.2, foco_climax, "veloc", 0.5),
              (resto, 1.25, foco_fim, fundo, 1.0)]
    total = sum(p[0] for p in planos)
    if total > DURACAO_MAX:  # (corta o final pra caber nos 4 s)
        d, z, f, fu, v = planos[-1]
        planos[-1] = (max(16, d - (total - DURACAO_MAX)), z, f, fu, v)
    return planos


class CenaLoja:
    """A cutscene de uma VITÓRIA ou ENTRADA da loja (mesmo jeito do cutscene.Cutscene: passo/desenhar/acabou)."""

    def __init__(self, ficha, tipo, planos, oponente=None, titulo=""):
        from lutador import Lutador
        self.ficha, self.tipo, self.planos, self.titulo = ficha, tipo, planos, titulo
        self.total = min(DURACAO_MAX, sum(p[0] for p in planos))
        self.t = 0
        self.k = 0  # o quadro da animação
        self.acc = 0.0
        self.l = Lutador(ficha, X0, 1)
        self.l.extra["entrada_x"] = X0
        self.o = None
        if tipo == "vitoria" and oponente is not None:  # o derrotado, caído do lado
            self.o = Lutador(oponente, X0 + 230, -1)
            self.o.vida = 0
            self.o.mudar("caido")
            for _ in range(30):
                self.o.animar()
            self.l._alvo_marujos = self.o
        self.palco = Palco(self.l, self.o)
        self.passo_animacao()  # (o 1º quadro já com a cena começada: nada aparece antes da hora)
        self._q = pygame.Surface((LARGURA, ALTURA))
        self._fundo = {}

    @property
    def acabou(self):
        return self.t >= self.total

    # ------------------------------------------------------------ a animação (igual à da arena)
    def plano(self):
        t = self.t
        for i, p in enumerate(self.planos):
            if t < p[0] or i == len(self.planos) - 1:
                return i, p, t
            t -= p[0]

    def passo(self):
        _, p, _ = self.plano()
        self.t += 1
        self.acc += p[4]
        while self.acc >= 1:
            self.acc -= 1
            self.passo_animacao()

    def passo_animacao(self):
        l, f, k = self.l, self.ficha, self.k
        if self.tipo == "vitoria":
            if l.estado != "vitoria":
                l.mudar("vitoria")
            l.t = k
            if f.get("vitoria"):
                f["vitoria"](l, k, self.palco)
        else:
            l.entrada_t = k
            if f.get("entrada") and k < DURACAO_ENTRADA:
                f["entrada"](l, k, self.palco)
            else:
                l.t += 1
        l.animar()
        if self.o:
            self.o.animar()
        self.palco.passo()
        self.k += 1

    # ------------------------------------------------------------ o desenho (só lê)
    def foco(self, nome):
        l = self.l
        p = l.pose_vista or l.pose_atual()
        if nome == "cabeca":
            return l.ponto(p, "cb")
        if nome == "alvo" and self.o:
            return self.o.x, CHAO - 40 * self.o.s
        if nome == "acima":
            return l.x, CHAO - 260
        if nome == "corpo":
            return l.x, l.y - 70 * l.s
        if nome == "alto":  # (o lutador com o que está em cima dele: troféu, bambu...)
            return l.x, l.y - 130 * l.s
        return (l.x + (self.o.x if self.o else l.x + 120)) / 2, CHAO - 130

    def fundo(self, q, nome, t):
        cor = self.ficha.get("cor_poder") or self.ficha.get("cor", (200, 200, 255))
        escura = tuple(int(c * 0.25) for c in cor)
        if nome == "noite":
            q.fill((10, 8, 22))
            rnd = random.Random(5)
            for _ in range(70):
                pygame.draw.circle(q, (230, 230, 255), (rnd.randrange(LARGURA), rnd.randrange(ALTURA - 120)), 1)
        elif nome == "ceu":
            cutscene.degrade(q, q.get_rect(), (40, 60, 120), (250, 170, 110))
        else:
            cutscene.degrade(q, q.get_rect(), escura, tuple(int(c * 0.6) for c in cor))
        if nome == "luz":  # o HOLOFOTE no lutador
            cutscene.luz(q, (int(self.l.x), CHAO - 80), 260, (255, 240, 200), 70)
        if nome == "veloc":  # as LINHAS DE VELOCIDADE (o momento épico)
            cutscene.linhas_velocidade(q, self.foco("corpo"), (255, 255, 255), n=50, r_dentro=140, grossura=8,
                                       semente=3, giro=t * 0.02, alfa=150)
        pygame.draw.rect(q, tuple(int(c * 0.35) for c in cor), (0, CHAO, LARGURA, ALTURA - CHAO))  # o chão
        pygame.draw.line(q, tuple(min(255, int(c * 0.8)) for c in cor), (0, CHAO), (LARGURA, CHAO), 3)

    def desenhar(self, tela):
        i, (dur, zoom, foco, fundo, _), t = self.plano()
        q = self._q
        self.fundo(q, fundo, t)
        l, f, k = self.l, self.ficha, max(0, self.k - 1)
        chave_atras = "vitoria_atras" if self.tipo == "vitoria" else "entrada_atras"
        if f.get(chave_atras):
            f[chave_atras](l, q, k)
        if self.o:
            self.o.desenhar(q)
        if not l.esconde:
            l.desenhar(q)
        chave_ef = "vitoria_efeito" if self.tipo == "vitoria" else "entrada_efeito"
        if f.get(chave_ef):
            try:
                f[chave_ef](l, q, k)
            except Exception:  # (efeito esquisito nunca derruba a luta)
                pass
        self.palco.desenhar(q)
        # a CÂMERA: o plano corta e amplia em volta do foco (e aproxima devagarinho durante o plano)
        z = zoom * (1 + 0.06 * (t / max(1, dur)))
        cx, cy = self.foco(foco)
        w, h = LARGURA / z, ALTURA / z
        r = pygame.Rect(0, 0, int(w), int(h))
        r.center = (int(cx), int(cy))
        r.clamp_ip(q.get_rect())
        img = pygame.transform.smoothscale(q.subsurface(r), (LARGURA, ALTURA))
        img = cutscene.pixel_fosco(img)
        ox = oy = 0
        if self.palco.tremor:
            ox = random.randint(-self.palco.tremor, self.palco.tremor)
            oy = random.randint(-self.palco.tremor, self.palco.tremor)
        tela.fill(PRETO)
        tela.blit(img, (ox, oy))
        if t < 3:  # corte seco com flash branco
            flash = pygame.Surface((LARGURA, ALTURA))
            flash.fill(BRANCO)
            flash.set_alpha(200 - t * 70)
            tela.blit(flash, (0, 0))
        tela.fill(PRETO, (0, 0, LARGURA, cutscene.FAIXA))
        tela.fill(PRETO, (0, ALTURA - cutscene.FAIXA, LARGURA, cutscene.FAIXA))
        if self.titulo and self.t < 70:  # o nome da cena na faixa de baixo
            from efeitos import texto
            texto(tela, self.titulo, 18, (255, 220, 120), (LARGURA // 2, ALTURA - cutscene.FAIXA // 2))


CENAS_ANIME = ("cena_max", "cena_frigantus", "cena_sphyrus", "cena_magnus", "cena_kun", "cena_rib", "cena_trafo",
               "cena_king", "cena_cannan", "cena_finn",
               "cena_tromos", "cena_tai", "cena_tamer", "cena_john", "cena_craquen", "cena_nocturnus")


def _pro_exe():
    """NUNCA é chamada: só existe pro PyInstaller ENXERGAR as cenas de anime (elas são carregadas pelo NOME, em texto,
    e sem isso ficam de fora do BattleWish.exe). Cena nova = pôr aqui E no CENAS_ANIME (o teste.py confere)."""
    import cena_cannan  # noqa: F401
    import cena_craquen  # noqa: F401
    import cena_finn  # noqa: F401
    import cena_frigantus  # noqa: F401
    import cena_john  # noqa: F401
    import cena_king  # noqa: F401
    import cena_kun  # noqa: F401
    import cena_magnus  # noqa: F401
    import cena_nocturnus  # noqa: F401
    import cena_max  # noqa: F401
    import cena_rib  # noqa: F401
    import cena_tai  # noqa: F401
    import cena_tamer  # noqa: F401
    import cena_sphyrus  # noqa: F401
    import cena_trafo  # noqa: F401
    import cena_tromos  # noqa: F401


def criar(ficha, tipo, oponente=None, cenario=None):
    """A cutscene dessa ficha (a vitória ou a entrada equipada), ou None se o item não tem cena."""
    planos = ficha.get(f"{tipo}_cutscene")
    if not planos:
        return None
    titulo = ficha.get(f"{tipo}_nome", "")
    if isinstance(planos, str):  # CENA DE ANIME desenhada: "arquivo:função" (ex. "cena_max:entrada")
        import importlib
        mod, _, func = planos.partition(":")
        cena = getattr(importlib.import_module(mod), func or "criar")(ficha, titulo, oponente)
        cena.cenario_nome = cenario or "TEMPLO"  # (o MAPA da luta: as cenas acontecem nele)
        return cena
    return CenaLoja(ficha, tipo, planos, oponente, titulo)
