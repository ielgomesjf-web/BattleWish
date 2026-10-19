"""CENAS DE ANIME DA LOJA (pedido do Gomes): cutscene DE VERDADE, desenhada grande quadro a quadro, com cenário
próprio, planos, câmera e cor normal (igual a 1ª ult do Rib, só que sem ficar pálida).

Uma cena = lista de PLANOS: (quadros, desenha(cena, q, t, k), sons {quadro do plano: (som, volume)}).
O lutador aparece com o DESENHO DE VERDADE dele, grande (cena.corpo), em qualquer pose (até poses novas).
Só imagem: não mexe na luta. Não pula (o Gomes pediu) e dura até uns 5-6 segundos (o Gomes liberou).
"""
import math
import random

import pygame

import cutscene
from config import *  # noqa: F401,F403
from max10 import brilho

FAIXA = 40


class CenaAnime:
    def __init__(self, ficha, planos, titulo="", oponente=None):
        from lutador import Lutador
        self.ficha, self.planos, self.titulo = ficha, planos, titulo
        self.oponente = oponente  # (a ficha do oponente: o derrotado nas vitórias, quem assiste nas entradas)
        self.cenario_nome = "TEMPLO"  # (o mapa da luta: quem cria a cena troca pelo de verdade)
        self._mapa = None
        self.total = sum(p[0] for p in planos)
        self.t = 0
        self.tremor = 0
        self.inverte = 0
        self.l = Lutador(ficha, 0, 1)
        self._lut = {}
        self._cache = {}
        self._q = pygame.Surface((LARGURA, ALTURA))

    @property
    def acabou(self):
        return self.t >= self.total

    def plano(self, t=None):
        t = self.t if t is None else t
        for i, p in enumerate(self.planos):
            if t < p[0] or i == len(self.planos) - 1:
                return i, p, t
            t -= p[0]

    def passo(self):
        import som
        _, p, t = self.plano()
        if len(p) > 2 and t in p[2]:
            nome, vol = p[2][t]
            som.tocar(nome, vol)
        self.t += 1
        if self.tremor > 0:
            self.tremor -= 1
        if self.inverte > 0:
            self.inverte -= 1

    # ---- o MAPA da luta e as cores da SKIN ----
    def mapa(self, q, t):
        """Desenha o cenário da luta (o mesmo do jogo, com a animação dele) na tela toda. O chão fica em CHAO."""
        import cenarios
        if self._mapa is None or self._mapa.nome != self.cenario_nome:
            self._mapa = cenarios.cenario(self.cenario_nome)
        q.blit(self._mapa.desenhar_pequeno(t, 1), (0, 0))

    def mapa_frente(self, q, t):
        if self._mapa is not None:
            self._mapa.desenhar_frente(q, t, 1)

    def cor(self, letra, padrao):
        """A cor da SKIN que ele está usando (pelas letras da paleta), ou a original."""
        return (self.ficha.get("troca") or {}).get(letra) or padrao

    def tingir(self, img):
        """SOMBRA / OURO / HOLOGRÁFICA: as skins que pintam o desenho inteiro (vale pros closes também)."""
        if self.l.tem_tinta():
            self.l.aplicar_tinta(img, False)
        return img

    # ---- o lutador grande (o desenho de verdade dele) ----
    def lutador(self, troca=None):
        from lutador import Lutador
        chave = tuple(sorted((troca or {}).items()))
        if chave not in self._lut:
            f = dict(self.ficha)
            if troca:
                f["troca"] = dict(f.get("troca") or {}, **troca)
            self._lut[chave] = Lutador(f, 0, 1)
        return self._lut[chave]

    def corpo(self, pose, escala, d=1, troca=None, guardar=True):
        """(imagem, (x, y) do pé dentro dela) do lutador numa pose (nome ou dict), no tamanho escala."""
        from provocacoes_loja import sprite
        l = self.lutador(troca)
        if isinstance(pose, str):
            pose = l.poses.get(pose) or l.poses["parado"]
        chave = (id(pose), round(escala, 3), d, tuple(sorted((troca or {}).items())))
        if guardar and chave in self._cache:
            return self._cache[chave]
        img, pe = sprite(l, pose, escala)
        self.tingir(img)
        if d < 0:
            img = pygame.transform.flip(img, True, False)
            pe = (img.get_width() - pe[0], pe[1])
        if guardar:
            self._cache[chave] = (img, pe)
        return img, pe

    def ponto(self, pose, k, escala, x, y, d=1):
        """Onde fica o ponto k da pose quando o lutador grande está com o pé em (x, y)."""
        l = self.l
        if isinstance(pose, str):
            pose = l.poses.get(pose) or l.poses["parado"]
        s = l.s * escala
        return x + pose[k][0] * s * d, y - pose[k][1] * s

    def por_oponente(self, q, pose, escala, x, y, d=-1):
        """O OPONENTE (com a skin dele): o derrotado caído nas vitórias, quem assiste nas entradas."""
        from lutador import Lutador
        from provocacoes_loja import sprite
        if not self.oponente:
            return
        chave = ("oponente", pose if isinstance(pose, str) else id(pose), round(escala, 3), d)
        if chave not in self._cache:
            l = Lutador(self.oponente, 0, 1)
            p = pose if isinstance(pose, dict) else (l.poses.get(pose) or l.poses["parado"])
            img, pe = sprite(l, p, escala)
            if l.tem_tinta():
                l.aplicar_tinta(img, False)
            if d < 0:
                img = pygame.transform.flip(img, True, False)
                pe = (img.get_width() - pe[0], pe[1])
            self._cache[chave] = (img, pe)
        img, (px, py) = self._cache[chave]
        q.blit(img, (int(x - px), int(y - py)))

    def por(self, q, pose, escala, x, y, d=1, troca=None, guardar=True):
        img, (px, py) = self.corpo(pose, escala, d, troca, guardar)
        q.blit(img, (int(x - px), int(y - py)))

    # ---- câmera ----
    def _tela_aux(self):
        if not hasattr(self, "_aux"):
            self._aux = pygame.Surface((LARGURA, ALTURA))
        return self._aux

    def camera(self, q, base, centro, zoom, pixel=False):
        """Põe em q o pedaço de base em volta do centro, ampliado (zoom > 1 = câmera chegando perto).
        pixel=True: amplia SEM borrar (fica com a cara do jogo ampliado, pras cenas na escala do jogo)."""
        w, h = q.get_size()
        r = pygame.Rect(0, 0, int(w / zoom), int(h / zoom))
        r.center = (int(centro[0]), int(centro[1]))
        r.clamp_ip(base.get_rect())
        if pixel:
            pygame.transform.scale(base.subsurface(r), (w, h), q)
        else:
            pygame.transform.smoothscale(base.subsurface(r), (w, h), q)

    # ---- desenho final ----
    def desenhar(self, tela):
        i, p, t = self.plano()
        dur = p[0]
        q = self._q
        p[1](self, q, t, t / max(1, dur - 1))
        ox = oy = 0
        if self.tremor:
            ox, oy = random.randint(-self.tremor, self.tremor), random.randint(-self.tremor, self.tremor)
        tela.fill(PRETO)
        if self.inverte:  # quadro de impacto
            branco = pygame.Surface((LARGURA, ALTURA))
            branco.fill(BRANCO)
            branco.blit(q, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            tela.blit(branco, (ox, oy))
        else:
            tela.blit(q, (ox, oy))
        if t < 2 and i > 0:  # corte seco
            flash = pygame.Surface((LARGURA, ALTURA))
            flash.fill(BRANCO)
            flash.set_alpha(150 - t * 70)
            tela.blit(flash, (0, 0))
        tela.fill(PRETO, (0, 0, LARGURA, FAIXA))
        tela.fill(PRETO, (0, ALTURA - FAIXA, LARGURA, FAIXA))


# =====================================================================
# Ferramentas de cenário (reaproveitadas pelas cenas)
# =====================================================================
def estrelas(q, t, vel=(0.0, 0.0), semente=1, n=120):
    w, h = q.get_size()
    rnd = random.Random(semente)
    for i in range(n):
        camada = 1 + i % 3
        x = (rnd.uniform(0, w) - vel[0] * t * camada) % w
        y = (rnd.uniform(0, h) - vel[1] * t * camada) % h
        b = 120 + camada * 40
        if camada == 3:
            pygame.draw.circle(q, (b, b, 255), (int(x), int(y)), 1)
        else:
            q.set_at((int(x), int(y)), (b, b, min(255, b + 30)))


def planeta(q, cx, cy, r, t):
    """A TERRA grandona: oceano, continentes, nuvens girando e o brilho da atmosfera."""
    brilho(q, (int(cx), int(cy)), int(r * 1.12), (110, 180, 255), 120)
    pygame.draw.circle(q, (30, 70, 170), (int(cx), int(cy)), int(r))
    rnd = random.Random(4)
    gira = t * 0.003
    for i in range(9):  # continentes (na parte de cima, que é a que aparece)
        a = -math.pi / 2 + rnd.uniform(-0.7, 0.7) + gira
        dist = rnd.uniform(0.72, 0.95) * r
        x, y = cx + math.cos(a) * dist, cy + math.sin(a) * dist
        tam = rnd.uniform(0.12, 0.28) * r
        pts = [(x + math.cos(b) * tam * rnd.uniform(0.6, 1.2), y + math.sin(b) * tam * 0.7 * rnd.uniform(0.6, 1.2))
               for b in [k * math.tau / 9 for k in range(9)]]
        pygame.draw.polygon(q, (70, 140, 70) if i % 3 else (190, 170, 110), pts)
    nuv = pygame.Surface(q.get_size(), pygame.SRCALPHA)
    for i in range(16):  # nuvens
        a = -math.pi / 2 + rnd.uniform(-0.8, 0.8) + gira * 1.6
        dist = rnd.uniform(0.7, 0.97) * r
        x, y = cx + math.cos(a) * dist, cy + math.sin(a) * dist
        pygame.draw.ellipse(nuv, (255, 255, 255, 150), (x - r * 0.18, y - r * 0.04, r * 0.36, r * 0.08))
    q.blit(nuv, (0, 0))
    sombra = pygame.Surface(q.get_size(), pygame.SRCALPHA)  # o lado da noite
    pygame.draw.circle(sombra, (0, 0, 20, 140), (int(cx + r * 0.35), int(cy + r * 0.25)), int(r))
    q.blit(sombra, (0, 0))
    pygame.draw.circle(q, (150, 210, 255), (int(cx), int(cy)), int(r), 3)


def texto_pow(q, txt, pos, tam, cor, t, giro=-0.15):
    """Onomatopeia de anime (CLANK!, BOOM!): texto grosso com contorno, inclinado, que cresce e treme."""
    from efeitos import texto_grande
    esc = 1 + 0.25 * max(0, 1 - t / 6)
    sup = pygame.Surface((tam * len(txt) + 40, tam * 2 + 20), pygame.SRCALPHA)
    texto_grande(sup, txt, int(tam * esc), cor, (sup.get_width() // 2, sup.get_height() // 2), contorno=(20, 10, 10))
    sup = pygame.transform.rotate(sup, math.degrees(giro))
    q.blit(sup, (pos[0] - sup.get_width() // 2 + random.randint(-2, 2), pos[1] - sup.get_height() // 2))


def faixa_nome(q, nome, sub, cor, k):
    """A faixa final com o nome do lutador (entra deslizando da esquerda)."""
    from efeitos import texto, texto_grande
    w, h = q.get_size()
    x = -420 + 420 * min(1, k * 3)
    pts = [(x, h - 150), (x + 470, h - 150), (x + 430, h - 70), (x - 40, h - 70)]
    pygame.draw.polygon(q, (12, 10, 16), [(px, py + 6) for px, py in pts])
    pygame.draw.polygon(q, cor, pts)
    pygame.draw.line(q, (255, 255, 255), pts[0], pts[1], 3)
    texto_grande(q, nome, 44, (255, 255, 255), (int(x + 210), h - 116), contorno=(20, 10, 10))
    texto(q, sub, 16, (20, 16, 24), (int(x + 210), h - 84))


def poeira(q, cx, cy, k, cor=(200, 180, 140), n=14, larg=320, semente=7):
    """A nuvem de poeira do impacto (bolotas que crescem e vão ficando transparentes)."""
    rnd = random.Random(semente)
    sup = pygame.Surface(q.get_size(), pygame.SRCALPHA)
    for i in range(n):
        a = rnd.uniform(math.pi, math.tau)
        d = rnd.uniform(0.3, 1.0) * larg * (0.3 + k)
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d * 0.45
        r = rnd.uniform(30, 70) * (0.5 + k)
        alfa = int(230 * (1 - k * 0.8))
        pygame.draw.circle(sup, (*cor, alfa), (int(x), int(y)), int(r))
        pygame.draw.circle(sup, (*tuple(min(255, c + 30) for c in cor), alfa), (int(x - r * 0.3), int(y - r * 0.3)),
                           int(r * 0.5))
    q.blit(sup, (0, 0))
