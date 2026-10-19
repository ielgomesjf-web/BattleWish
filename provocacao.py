"""PROVOCAÇÃO (tecla T): o lutador provoca o adversário.
Se terminar sem apanhar, enche um pouco a barra da ultimate. Mas fica parado, aberto pra apanhar!"""
import pygame

import som
from config import *  # noqa: F401,F403
from efeitos import fonte
from golpes import GOLPES

PADRAO = [(0, "parado"), (8, "vitoria"), (PROVOCA_TEMPO - 12, "vitoria"), (PROVOCA_TEMPO, "parado")]


def provocar(l, outro, jogo):
    f = l.mutado or l.f
    if l.t == 1:
        l.memo["quadros"] = f.get("provocacao_quadros", PADRAO)
        som.tocar("blip")
    l.vx = 0
    l.fisica(jogo)
    if f.get("provocacao_passo"):  # (provocação da loja com gesto próprio)
        f["provocacao_passo"](l, jogo)
    if l.t == PROVOCA_TEMPO - 12:  # terminou a provocação sem apanhar: enche a barra
        l.encher(PROVOCA_BARRA)
        l.provocou += 1
        l.memo["encheu"] = l.t
        som.tocar("carga", 0.5)
    if l.t >= PROVOCA_TEMPO:
        return "fim"


def linhas(frase, maximo=28):
    """Frase comprida (até uns 50 letras) vira 2 linhas, quebrando no espaço mais perto do meio."""
    if len(frase) <= maximo:
        return [frase]
    meio = len(frase) // 2
    espacos = [i for i, c in enumerate(frase) if c == " "]
    if not espacos:
        return [frase]
    i = min(espacos, key=lambda k: abs(k - meio))
    return [frase[:i], frase[i + 1:]]


def provocar_efeito(l, tela):
    """O balãozinho com a frase da provocação (e um brilho azul quando a barra enche)."""
    f = l.mutado or l.f
    p = l.pose_vista or l.pose_atual()
    cx, cy = l.ponto(p, "cb")
    if l.t >= 6:
        imgs = [fonte(15).render(lin, True, (20, 16, 30)) for lin in linhas(f.get("provocacao", "Vem!"))]
        w = max(i.get_width() for i in imgs)
        h = sum(i.get_height() for i in imgs)
        r = pygame.Rect(0, 0, w, h)
        r.midbottom = (cx, cy - 34 * l.s)
        r.clamp_ip(pygame.Rect(4, 4, LARGURA - 8, ALTURA - 8))
        caixa = r.inflate(18, 12)
        pygame.draw.rect(tela, (12, 10, 20), caixa.inflate(4, 4), border_radius=10)
        pygame.draw.rect(tela, (250, 248, 236), caixa, border_radius=9)
        pygame.draw.polygon(tela, (250, 248, 236), [(cx - 6, caixa.bottom - 1), (cx + 6, caixa.bottom - 1),
                                                    (cx, caixa.bottom + 9)])
        y = r.y
        for img in imgs:  # (frase comprida: 2 linhas, cada uma no meio)
            tela.blit(img, (r.centerx - img.get_width() // 2, y))
            y += img.get_height()
    if f.get("provocacao_desenho"):  # (provocação da loja: o desenho do gesto)
        f["provocacao_desenho"](l, tela)
    if "encheu" in l.memo:
        k = l.t - l.memo["encheu"]
        pygame.draw.circle(tela, (120, 200, 255), (int(l.x), int(l.y - 60 * l.s)), int((20 + k * 6) * l.s / 1.4), 3)


GOLPES["provocar"] = dict(base="parado", pose="parado", caixa=None, especial=True, provocacao=True, ini=0, ativo=0,
                          rec=0, total=PROVOCA_TEMPO + 4, dano=0, hit=0, defe=0, emp=0, nivel="medio",
                          logica=provocar, efeito=provocar_efeito, quadros=PADRAO)
