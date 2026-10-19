"""MODO FOTO (v2.x, pedido do Gomes): pausa a luta, mexe a câmera, dá zoom, põe um filtro e salva a imagem.

  WASD / setas      mexe a câmera            Q / E ou rodinha   zoom (1x até 3x)
  F                 próximo filtro           H                  esconde/mostra a barra de vida (HUD)
  ENTER             salva a foto (PNG)       arrastar o mouse   mexe a câmera
  ESC               volta pra pausa (quem cuida é o luta.py: TelaFoto.sair)

As fotos vão pra pasta "fotos" do lado do jogo (ou BW_FOTOS, nos testes). É só tela: não mexe na luta.
"""
import datetime
import os

import numpy as np
import pygame

import save
import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande

FILTROS = ["NORMAL", "PRETO E BRANCO", "SÉPIA", "QUADRINHO", "CINEMA"]
ZOOM_MAX = 3.0
PASSO_CAMERA = 10  # pixels (da tela) por quadro segurando WASD


def pasta_fotos():
    return os.environ.get("BW_FOTOS") or os.path.join(save.pasta_do_jogo(), "fotos")


# =====================================================================
# os filtros (numpy: recebem e devolvem uma Surface do mesmo tamanho)
# =====================================================================
def _array(s):
    return pygame.surfarray.array3d(s).astype(np.float32)


def _surface(a):
    return pygame.surfarray.make_surface(np.clip(a, 0, 255).astype(np.uint8))


def _cinza(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def filtro_pb(s):
    g = _cinza(_array(s))
    g = (g - 128) * 1.15 + 128  # (um pouco mais de contraste)
    return _surface(np.stack([g, g, g], axis=-1))


def filtro_sepia(s):
    g = _cinza(_array(s))
    return _surface(np.stack([g * 1.07 + 20, g * 0.87 + 10, g * 0.62], axis=-1))


def filtro_quadrinho(s):
    a = _array(s)
    a = np.round(a / 64) * 64 + 16  # poucas cores (cara de gibi)
    g = _cinza(a)
    borda = (np.abs(np.diff(g, axis=0, append=g[-1:, :])) + np.abs(np.diff(g, axis=1, append=g[:, -1:]))) > 60
    a[borda] = (20, 16, 24)  # contorno preto onde a cor muda muito
    w, h = g.shape
    xs, ys = np.meshgrid(np.arange(h), np.arange(w))
    pontos = ((xs % 6 < 2) & (ys % 6 < 2)) & (g < 90)  # pontinhos de retícula nas sombras
    a[pontos] = a[pontos] * 0.55
    return _surface(a)


def por_cima_quadrinho(out):
    """Um "balão" de título no canto, tipo capa de gibi (vai depois do zoom, pra não crescer junto)."""
    caixa = pygame.Rect(18, 16, 250, 46)
    pygame.draw.rect(out, (255, 230, 60), caixa)
    pygame.draw.rect(out, (20, 16, 24), caixa, 4)
    texto_grande(out, "BATTLE WISH", 24, (230, 40, 40), caixa.center, contorno=(20, 16, 24))


def filtro_cinema(s):
    a = _array(s)
    g = _cinza(a)[..., None]
    sombra, luz = np.array([20, 70, 90], np.float32), np.array([255, 190, 120], np.float32)
    k = (g / 255.0)
    tom = sombra * (1 - k) + luz * k  # sombras azuladas, luzes alaranjadas
    a = a * 0.55 + tom * 0.45
    return _surface(a)


_VINHETAS = {}


def _vinheta(w, h):
    """As bordas escurecidas do filtro cinema (feitas uma vez só por tamanho)."""
    if (w, h) not in _VINHETAS:
        xs, ys = np.meshgrid(np.linspace(-1, 1, h), np.linspace(-1, 1, w))
        escuro = 1 - np.clip(1.15 - (xs ** 2 + ys ** 2) * 0.45, 0.35, 1.0)
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        sup.fill((0, 0, 0, 255))
        alfa = pygame.surfarray.pixels_alpha(sup)
        alfa[...] = (escuro * 255).astype(np.uint8)
        del alfa
        try:
            sup = sup.convert_alpha()  # (fica bem mais rápido de colar, se já tiver janela)
        except pygame.error:
            pass
        _VINHETAS[(w, h)] = sup
    return _VINHETAS[(w, h)]


def por_cima_cinema(out):
    """Vinheta e faixas pretas de cinema (depois do zoom: ficam sempre do tamanho da tela)."""
    w, h = out.get_size()
    out.blit(_vinheta(w, h), (0, 0))
    faixa = h // 8
    pygame.draw.rect(out, (0, 0, 0), (0, 0, w, faixa))
    pygame.draw.rect(out, (0, 0, 0), (0, h - faixa, w, faixa))


APLICAR = {"NORMAL": lambda s: s.copy(), "PRETO E BRANCO": filtro_pb, "SÉPIA": filtro_sepia,
           "QUADRINHO": filtro_quadrinho, "CINEMA": filtro_cinema}
POR_CIMA = {"QUADRINHO": por_cima_quadrinho, "CINEMA": por_cima_cinema}


# =====================================================================
# a TELA
# =====================================================================
class TelaFoto:
    def __init__(self, sem_hud, com_hud=None):
        """sem_hud: a tela da luta SEM barras/textos; com_hud: a tela inteira (se não tiver, usa a sem_hud)."""
        self.fonte = {False: sem_hud.copy(), True: (com_hud or sem_hud).copy()}
        self.hud = False
        self.zoom = 1.0
        self.cx, self.cy = LARGURA / 2, ALTURA / 2
        self.filtro = 0
        self.sair = False
        self.t = 0
        self.msg, self.msg_t = "", 0
        self.flash = 0
        self.arrastando = None
        self._cache = None  # (chave, imagem pronta)
        self._filtrada = {}  # (hud, filtro) -> a tela INTEIRA já com o filtro (o filtro pesado roda 1 vez só)
        self.ultima_foto = None

    # ---- câmera ----
    def limitar(self):
        self.zoom = max(1.0, min(ZOOM_MAX, self.zoom))
        meia_w, meia_h = LARGURA / 2 / self.zoom, ALTURA / 2 / self.zoom
        self.cx = max(meia_w, min(LARGURA - meia_w, self.cx))
        self.cy = max(meia_h, min(ALTURA - meia_h, self.cy))

    def recorte(self):
        w, h = LARGURA / self.zoom, ALTURA / self.zoom
        return pygame.Rect(int(self.cx - w / 2), int(self.cy - h / 2), int(w), int(h))

    def imagem(self):
        """A foto do jeito que vai ser salva (sem as instruções da tela)."""
        chave = (self.hud, round(self.zoom, 3), round(self.cx), round(self.cy), self.filtro)
        if self._cache and self._cache[0] == chave:
            return self._cache[1]
        nome = FILTROS[self.filtro]
        if (self.hud, nome) not in self._filtrada:
            self._filtrada[(self.hud, nome)] = APLICAR[nome](self.fonte[self.hud])
        r = self.recorte().clip(pygame.Rect(0, 0, LARGURA, ALTURA))
        img = pygame.transform.scale(self._filtrada[(self.hud, nome)].subsurface(r), (LARGURA, ALTURA))
        if nome in POR_CIMA:
            POR_CIMA[nome](img)
        self._cache = (chave, img)
        return img

    def salvar(self):
        pasta = pasta_fotos()
        try:
            os.makedirs(pasta, exist_ok=True)
            nome = datetime.datetime.now().strftime("battlewish_%Y%m%d_%H%M%S_%f")[:-3] + ".png"
            caminho = os.path.join(pasta, nome)
            pygame.image.save(self.imagem(), caminho)
            self.ultima_foto = caminho
            self.msg = "FOTO SALVA! (pasta fotos)"
            self.flash = 10
            som.tocar("confirma")
        except (OSError, pygame.error):
            self.msg = "não deu pra salvar a foto :("
            som.tocar("defesa")
        self.msg_t = 120

    # ---- teclas e mouse ----
    def tecla(self, tecla):
        if tecla in (pygame.K_q, pygame.K_MINUS, pygame.K_KP_MINUS):
            self.zoom /= 1.15
        elif tecla in (pygame.K_e, pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
            self.zoom *= 1.15
        elif tecla == pygame.K_f:
            self.filtro = (self.filtro + 1) % len(FILTROS)
            som.tocar("blip")
        elif tecla == pygame.K_h:
            self.hud = not self.hud
            som.tocar("blip")
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
            self.salvar()
        elif tecla == pygame.K_ESCAPE:
            self.sair = True
        self.limitar()

    def segurando(self, teclas):
        """Chame todo quadro com pygame.key.get_pressed(): WASD/setas mexem a câmera."""
        passo = PASSO_CAMERA / self.zoom
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.cx -= passo
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.cx += passo
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            self.cy -= passo
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            self.cy += passo
        self.limitar()

    def evento(self, ev):
        """Mouse: rodinha = zoom, arrastar com o botão esquerdo = mexer a câmera."""
        if ev.type == pygame.MOUSEWHEEL:
            self.zoom *= 1.15 if ev.y > 0 else 1 / 1.15
            self.limitar()
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.arrastando = ev.pos
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            self.arrastando = None
        elif ev.type == pygame.MOUSEMOTION and self.arrastando:
            dx, dy = ev.pos[0] - self.arrastando[0], ev.pos[1] - self.arrastando[1]
            self.cx -= dx / self.zoom
            self.cy -= dy / self.zoom
            self.arrastando = ev.pos
            self.limitar()
        elif ev.type == pygame.KEYDOWN:
            self.tecla(ev.key)

    # ---- desenho ----
    def desenhar(self, tela):
        self.t += 1
        tela.blit(self.imagem(), (0, 0))
        if self.flash > 0:  # o "clique" da câmera
            branco = pygame.Surface((LARGURA, ALTURA))
            branco.fill(BRANCO)
            branco.set_alpha(int(255 * self.flash / 10))
            tela.blit(branco, (0, 0))
            self.flash -= 1
        topo = pygame.Surface((LARGURA, 30), pygame.SRCALPHA)
        topo.fill((0, 0, 0, 130))
        tela.blit(topo, (0, 0))
        texto(tela, f"MODO FOTO   filtro: {FILTROS[self.filtro]}   zoom: {self.zoom:.1f}x", 15, (255, 230, 120),
              (LARGURA // 2, 15))
        texto(tela, "WASD câmera   Q/E zoom   F filtro   H barras   ENTER salva   ESC volta", 13, (230, 230, 240),
              (LARGURA // 2, ALTURA - 12))
        if self.msg_t > 0:
            self.msg_t -= 1
            texto_grande(tela, self.msg, 28, (140, 255, 160), (LARGURA // 2, ALTURA // 2), contorno=(10, 40, 20))
