"""CONFIGURAÇÕES: volume da música, volume dos efeitos, vibração do controle e, pra quem achou as 17 meias,
o GORRINHO DE NATAL (fica salvo no save)."""
import pygame

import save
import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande
from selecao import fundo_selecao

PASSO = 10  # A/D muda o volume de 10 em 10 (%)


LIGA_DESLIGA = ("vibrar", "gorro")


def valor(chave):
    """O que está salvo (volumes de 0 a 100; vibração e gorrinho True/False)."""
    if chave == "gorro":
        import natal
        return natal.gorro_ligado()
    padrao = {"vol_musica": 100, "vol_efeitos": 100, "vibrar": True}[chave]
    return save.d().get(chave, padrao)


class TelaConfiguracoes:
    OPCOES = [("vol_musica", "MÚSICA"), ("vol_efeitos", "EFEITOS"), ("vibrar", "VIBRAÇÃO DO CONTROLE"),
              (None, "VOLTAR")]

    def __init__(self):
        import natal
        self.OPCOES = list(TelaConfiguracoes.OPCOES)
        if natal.tem_gorro():  # (achou as 17 meias de Natal)
            self.OPCOES.insert(-1, ("gorro", "GORRINHO DE NATAL"))
        self.i = 0
        self.t = 0
        self.sair = False

    def rect(self, i):
        passo = 80 if len(self.OPCOES) <= 4 else 70
        return pygame.Rect(LARGURA // 2 - 300, 150 + i * passo, 600, passo - 16)

    def barra(self, i):
        """A barrinha do volume (dá pra clicar nela)."""
        r = self.rect(i)
        return pygame.Rect(r.x + 280, r.centery - 10, 240, 20)

    def mudar(self, chave, novo):
        if chave == "gorro":
            import natal
            natal.ligar_gorro(bool(novo))
            som.tocar("blip")
            return
        if chave == "vibrar":
            save.d()["vibrar"] = bool(novo)
        else:
            save.d()[chave] = max(0, min(100, int(novo)))
        save.salvar()
        som.aplicar_volumes()
        if chave == "vol_efeitos" or chave == "vibrar":
            som.tocar("blip")  # (já toca no volume novo, pra ouvir como ficou)

    def tecla(self, tecla):
        n = len(self.OPCOES)
        chave = self.OPCOES[self.i][0]
        if tecla in (pygame.K_w, pygame.K_UP):
            self.i = (self.i - 1) % n
            som.tocar("blip")
        elif tecla in (pygame.K_s, pygame.K_DOWN):
            self.i = (self.i + 1) % n
            som.tocar("blip")
        elif tecla in (pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT) and chave:
            sinal = -1 if tecla in (pygame.K_a, pygame.K_LEFT) else 1
            if chave in LIGA_DESLIGA:
                self.mudar(chave, not valor(chave))
            else:
                self.mudar(chave, valor(chave) + sinal * PASSO)
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE, "clique"):
            if chave is None:
                self.sair = True
            elif chave in LIGA_DESLIGA:
                self.mudar(chave, not valor(chave))

    def mouse(self, pos, clicou):
        for i in range(len(self.OPCOES)):
            if self.rect(i).collidepoint(pos):
                self.i = i
                chave = self.OPCOES[i][0]
                if clicou:
                    b = self.barra(i)
                    if chave and chave not in LIGA_DESLIGA and b.inflate(0, 20).collidepoint(pos):
                        self.mudar(chave, int((pos[0] - b.x) / b.w * 100 / PASSO + 0.5) * PASSO)  # (25% = 30)
                    else:
                        self.tecla("clique")
                return

    def desenhar(self, tela):
        self.t += 1
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, "CONFIGURAÇÕES", 40, (255, 220, 70), (LARGURA // 2, 70))
        for i, (chave, nome) in enumerate(self.OPCOES):
            r = self.rect(i)
            sel = i == self.i
            pygame.draw.rect(tela, (54, 46, 84) if sel else (26, 22, 42), r, border_radius=12)
            pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), r, 3, border_radius=12)
            if chave is None:
                texto(tela, nome, 22 if sel else 20, AMARELO if sel else BRANCO, r.center)
                continue
            texto(tela, nome, 19 if len(nome) < 12 else 15, AMARELO if sel else BRANCO, (r.x + 140, r.centery))
            if chave in LIGA_DESLIGA:
                liga = valor(chave)
                txt = {True: "< LIGADO >", False: "< DESLIGADO >"}[bool(liga)] if chave == "gorro" else \
                    ("< LIGADA >" if liga else "< DESLIGADA >")
                texto(tela, txt, 20,
                      (120, 255, 150) if liga else (255, 140, 120), (r.x + 400, r.centery))
                continue
            v = valor(chave)
            b = self.barra(i)
            pygame.draw.rect(tela, (14, 12, 24), b, border_radius=6)
            if v > 0:
                pygame.draw.rect(tela, (120, 200, 255) if chave == "vol_musica" else (255, 200, 90),
                                 (b.x, b.y, int(b.w * v / 100), b.h), border_radius=6)
            pygame.draw.rect(tela, (90, 80, 130), b, 2, border_radius=6)
            texto(tela, f"{v}%" if v else "MUDO", 16, BRANCO, (b.right + 36, r.centery))
        import controle_video
        rodape = "direcional escolhe e muda   A confirma   B volta" if controle_video.no_controle() else \
            "W/S escolhe   A/D muda (ou clica na barra)   ESC volta"
        texto(tela, rodape, 14, (200, 200, 220), (LARGURA // 2, ALTURA - 16))
