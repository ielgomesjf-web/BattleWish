"""A LOJA: compra ROUPAS, ENTRADAS, POSES DE VITÓRIA e PROVOCAÇÕES com as moedas que ganha lutando."""
import math

import pygame

import extras
import roupas
import save
import som
from config import *  # noqa: F401,F403
from efeitos import moeda, texto, texto_grande, texto_moedas
from lutador import Lutador
from selecao import fundo_selecao, retrato

CARTA_LOJA = 48  # (grade de 2 fileiras embaixo das roupas: cabe todo mundo, igual a seleção)
PREVIA_X, PREVIA_CHAO = 230, 374
PREVIA_PAUSA = 40  # quadros parado no fim da prévia antes de repetir


class Palco:
    """Um "jogo" de mentira pra prévia da loja rodar a entrada / vitória / provocação (nada disso é luta de verdade)."""

    def __init__(self, l):
        self.L = [l, l]
        self.faiscas = []
        self.projeteis = []
        self.t_total = 0
        self.cena = None

    def tremer(self, n):
        pass

    def faisca(self, x, y, defendeu=False, forte=False):
        pass

    def passo(self):
        self.t_total += 1
        for f in self.faiscas:
            f[0] += f[2]
            f[1] += f[3]
            f[4] -= 1
        self.faiscas = [f for f in self.faiscas if f[4] > 0]

    def desenhar(self, tela):
        for f in self.faiscas:
            tam = f[6] * min(1, f[4] / 12) if len(f) > 6 else f[4] // 4
            pygame.draw.circle(tela, f[5], (int(f[0]), int(f[1])), max(2, int(tam)))


class TelaLoja:
    def __init__(self, personagens):
        self.lista = personagens
        self.i = 0
        self.j = 0
        self.cat = 0  # 0 = ROUPAS, 1 = ENTRADAS, 2 = VITÓRIAS, 3 = PROVOCAÇÕES
        self.t = 0
        self.msg, self.msg_t, self.msg_cor = "", 0, BRANCO
        self.cartas = [retrato(f, CARTA_LOJA) for f in personagens]
        self.vitrine = {}
        self.brilho = 0
        self.previa = None  # (chave, lutador, palco, t)

    # ---- o que está na prateleira ----
    def categoria(self):
        return extras.CATEGORIAS[self.cat][0]

    def nome(self):
        return self.lista[self.i]["nome"]

    def itens(self):
        if self.categoria() == "roupas":  # (skin de EVENTO só aparece pra quem já ganhou no passe)
            return [r for r in roupas.da(self.lista[self.i])
                    if not (r.get("evento") or r.get("album")) or save.tem_roupa(self.nome(), r["id"])]
        return [i for i in extras.da(self.categoria(), self.nome())  # (prêmio de evento: só pra quem ganhou)
                if not i.get("evento") or extras.tem(self.categoria(), self.nome(), i["id"])]

    roupas = itens  # (nome antigo)

    def tem(self, it):
        if self.categoria() == "roupas":
            return save.tem_roupa(self.nome(), it["id"])
        return extras.tem(self.categoria(), self.nome(), it["id"])

    def usando(self):
        if self.categoria() == "roupas":
            return save.usando(self.nome())
        return extras.usando(self.categoria(), self.nome())

    def usar(self, it):
        if self.categoria() == "roupas":
            save.usar(self.nome(), it["id"])
        else:
            extras.usar(self.categoria(), self.nome(), it["id"])

    def comprar(self, it):
        if self.categoria() == "roupas":
            return save.comprar(self.nome(), it["id"], it["preco"])
        return extras.comprar(self.categoria(), self.nome(), it["id"], it["preco"])

    # ---- controle ----
    def tecla(self, tecla):
        if tecla in (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP,
                     pygame.K_DOWN, pygame.K_q, pygame.K_e, pygame.K_TAB):
            som.tocar("blip")
        if tecla in (pygame.K_a, pygame.K_LEFT):
            self.i = (self.i - 1) % len(self.lista)
            self.j = 0
        elif tecla in (pygame.K_d, pygame.K_RIGHT):
            self.i = (self.i + 1) % len(self.lista)
            self.j = 0
        elif tecla in (pygame.K_w, pygame.K_UP):
            self.j = (self.j - 1) % len(self.itens())
        elif tecla in (pygame.K_s, pygame.K_DOWN):
            self.j = (self.j + 1) % len(self.itens())
        elif tecla in (pygame.K_e, pygame.K_TAB):
            self.cat, self.j = (self.cat + 1) % len(extras.CATEGORIAS), 0
        elif tecla == pygame.K_q:
            self.cat, self.j = (self.cat - 1) % len(extras.CATEGORIAS), 0
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE, "clique"):
            self.confirmar()

    def rect_aba(self, k):
        w = 440 // len(extras.CATEGORIAS)
        return pygame.Rect(470 + k * w, 64, w - 4, 26)

    def rect_carta(self, i):
        colunas = -(-len(self.lista) // 2)  # 2 fileiras
        lin, col = divmod(i, colunas)
        x0 = 690 - (colunas * (CARTA_LOJA + 6) - 6) // 2
        return pygame.Rect(x0 + col * (CARTA_LOJA + 6), 404 + lin * (CARTA_LOJA + 6), CARTA_LOJA, CARTA_LOJA)

    def rect_roupa(self, j):
        passo = min(74, 262 // max(1, len(self.itens())))
        return pygame.Rect(470, 100 + j * passo, 440, passo - 6)

    def mouse(self, pos, clicou):
        for k in range(len(extras.CATEGORIAS)):
            if self.rect_aba(k).collidepoint(pos):
                if clicou and self.cat != k:
                    self.cat, self.j = k, 0
                    som.tocar("blip")
                return
        for i in range(len(self.lista)):
            if self.rect_carta(i).collidepoint(pos):
                if clicou and self.i != i:
                    self.i, self.j = i, 0
                    som.tocar("blip")
                return
        for j in range(len(self.itens())):
            if self.rect_roupa(j).collidepoint(pos):
                self.j = j
                if clicou:
                    self.confirmar()
                return

    def avisar(self, msg, cor):
        self.msg, self.msg_t, self.msg_cor = msg, 120, cor

    def confirmar(self):
        it = self.itens()[self.j]
        nome = self.nome()
        if self.tem(it):
            self.usar(it)
            som.tocar("confirma")
            self.avisar(f"{nome} está usando: {it['nome']}", (150, 220, 255))
        elif it.get("codigo"):
            som.tocar("defesa")
            self.avisar("essa só com CÓDIGO SECRETO!", (255, 200, 90))
        elif self.comprar(it):
            self.usar(it)
            som.tocar("ultimate", 0.6)
            self.brilho = 40
            self.avisar(f"COMPROU! {it['nome']}", (255, 220, 90))
        else:
            som.tocar("defesa")
            self.avisar(f"faltam {it['preco'] - save.moedas()} moedas", (255, 110, 90))

    # ---- desenho ----
    def lutador(self, ficha):
        chave = (ficha["nome"], ficha.get("roupa"))
        if chave not in self.vitrine:
            l = Lutador(ficha, 0, 1)
            l.s = ficha["tam"] * 1.7
            self.vitrine[chave] = l
        return self.vitrine[chave]

    def desenhar_previa(self, tela, f, it):
        """ENTRADAS / VITÓRIAS / PROVOCAÇÕES: o lutador fazendo, de verdade, num palco de mentira (repete sozinho)."""
        cat = self.categoria()
        ficha = extras.aplicar(roupas.vestir(f, save.usando(f["nome"])), f["nome"], {cat: it["id"]})
        chave = (f["nome"], cat, it["id"])
        tipo = {"entradas": "entrada", "vitorias": "vitoria"}.get(cat)
        if tipo and ficha.get(f"{tipo}_cutscene"):  # CUTSCENE: a prévia é a própria cena (pequena, repetindo)
            return self.desenhar_previa_cena(tela, ficha, tipo, chave)
        if not self.previa or self.previa[0] != chave:
            l = Lutador(ficha, PREVIA_X, 1)
            l.s = ficha["tam"] * 1.3
            l.chao_sombra = CHAO  # (roda no chão da arena e a camada desce pro chão da loja)
            self.previa = [chave, l, Palco(l), 0]
        _, l, palco, t = self.previa
        self.previa[3] += 1
        duracao = {"entradas": DURACAO_ENTRADA, "vitorias": 170, "provocacoes": PROVOCA_TEMPO}[cat]
        if t >= duracao + PREVIA_PAUSA:  # recomeça
            self.previa = None
            return self.desenhar_previa(tela, f, it)
        destino, tela = tela, pygame.Surface((460, ALTURA), pygame.SRCALPHA)
        try:
            k = min(t, duracao)
            if cat == "entradas":
                l.extra["entrada_x"] = PREVIA_X
                if t < duracao and ficha.get("entrada"):
                    l.entrada_t = k
                    ficha["entrada"](l, k, palco)
                else:
                    l.x, l.y = PREVIA_X, CHAO
                    l.sobrepor = {}
                    l.esconde = False
            elif cat == "vitorias":
                if l.estado != "vitoria":
                    l.mudar("vitoria")
                l.t = k
                l.x, l.y = PREVIA_X, CHAO
                if ficha.get("vitoria"):
                    ficha["vitoria"](l, k, palco)
            else:
                from golpes import GOLPES
                if l.estado != "ataque":
                    l.estado, l.golpe, l.nome_golpe = "ataque", GOLPES["provocar"], "provocar"
                    l.memo = {"quadros": ficha.get("provocacao_quadros", GOLPES["provocar"]["quadros"])}
                l.t = k
                l.x, l.y = PREVIA_X, CHAO
                if ficha.get("provocacao_passo"):
                    ficha["provocacao_passo"](l, palco)
            l.animar()
            palco.passo()
            if not l.esconde:
                l.desenhar(tela)
            if cat == "entradas" and ficha.get("entrada_efeito") and t < duracao:
                ficha["entrada_efeito"](l, tela, k)
            if cat == "vitorias" and ficha.get("vitoria_efeito"):
                ficha["vitoria_efeito"](l, tela, k)
            if cat == "provocacoes" and t < duracao:
                import provocacao
                provocacao.provocar_efeito(l, tela)
            palco.desenhar(tela)
            destino.blit(tela, (0, PREVIA_CHAO - CHAO))
        except Exception:  # (prévia nunca pode quebrar a loja: mostra parado)
            self.previa = None
            l = self.lutador(roupas.vestir(f, save.usando(f["nome"])))
            l.x, l.y = PREVIA_X, PREVIA_CHAO
            l.chao_sombra = PREVIA_CHAO
            l.desenhar(destino)

    def desenhar_previa_cena(self, tela, ficha, tipo, chave):
        import cenas_loja
        if not self.previa or self.previa[0] != chave:
            from personagens import PERSONAGENS
            outro = next(f for f in PERSONAGENS if f["nome"] != ficha.get("nome_base", ficha["nome"]))
            self.previa = [chave, cenas_loja.criar(ficha, tipo, outro, "TEMPLO"), None, 0]
        cena = self.previa[1]
        self.previa[3] += 1
        if cena.acabou:
            if self.previa[3] > cena.total + PREVIA_PAUSA:
                self.previa = None
            return
        if not hasattr(self, "_tela_cena"):
            self._tela_cena = pygame.Surface((LARGURA, ALTURA))
        cena.desenhar(self._tela_cena)
        cena.passo()
        w = tela.get_width() - 20
        h = int(w * ALTURA / LARGURA)
        img = pygame.transform.smoothscale(self._tela_cena, (w, h))
        y = 120
        tela.blit(img, (10, y))
        pygame.draw.rect(tela, (255, 220, 70), (10, y, w, h), 2)
        selo = pygame.Rect(16, y - 24, 104, 20)
        pygame.draw.rect(tela, (200, 60, 60), selo, border_radius=6)
        texto(tela, "CUTSCENE", 13, BRANCO, selo.center)

    def desenhar(self, tela):
        self.t += 1
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, "LOJA", 44, (255, 220, 70), (LARGURA // 2, 30))
        texto_moedas(tela, save.moedas(), LARGURA - 24, 36, self.t, 26)
        f = self.lista[self.i]
        itens = self.itens()
        self.j = min(self.j, len(itens) - 1)
        r = itens[self.j]
        cat = self.categoria()
        # o lutador (com a roupa escolhida ou fazendo a entrada/vitória/provocação escolhida)
        x = PREVIA_X
        luz = pygame.Surface((300, 420), pygame.SRCALPHA)
        for k in range(10, 0, -1):
            pygame.draw.ellipse(luz, (255, 210, 90, 7), (150 - k * 14, 40, k * 28, 380))
        tela.blit(luz, (x - 150, 0))
        pygame.draw.ellipse(tela, (20, 18, 30), (x - 100, 360, 200, 30))
        pygame.draw.ellipse(tela, (255, 210, 90), (x - 100, 360, 200, 30), 3)
        if cat == "roupas":
            self.previa = None
            l = self.lutador(roupas.vestir(f, r["id"]))
            l.x, l.y = x, PREVIA_CHAO
            l.chao_sombra = PREVIA_CHAO
            l.t = self.t
            l.desenhar(tela)
        else:
            area = tela.subsurface(pygame.Rect(0, 0, 460, 400))
            self.desenhar_previa(area, f, r)
        if self.brilho > 0:  # brilho de compra
            self.brilho -= 1
            for k in range(8):
                a = self.t * 0.2 + k * 0.785
                d = 60 + (40 - self.brilho) * 3
                moeda(tela, (x + math.cos(a) * d, 230 + math.sin(a) * d * 0.6), 8, self.t + k * 7)
        texto_grande(tela, f["nome"], 26, BRANCO, (x, 410))
        # as abas
        for k, (_, titulo) in enumerate(extras.CATEGORIAS):
            ra = self.rect_aba(k)
            sel = k == self.cat
            pygame.draw.rect(tela, (80, 66, 120) if sel else (30, 26, 48), ra, border_radius=8)
            pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), ra, 2, border_radius=8)
            texto(tela, titulo, 13 if sel else 12, AMARELO if sel else (200, 200, 220), ra.center)
        # a lista
        usando_id = self.usando()
        for j, it in enumerate(itens):
            rr = self.rect_roupa(j)
            sel = j == self.j
            tem = self.tem(it)
            usando = usando_id == it["id"]
            pygame.draw.rect(tela, (54, 46, 84) if sel else (30, 26, 48), rr, border_radius=10)
            pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), rr, 3, border_radius=10)
            cor = it.get("cor", f["cor"])
            if it.get("codigo") and not tem:
                cor = (60, 54, 80)  # (secreta: não mostra a cor)
            q = min(36, rr.h - 10)
            quad = (rr.x + 14, rr.centery - q // 2, q, q)
            pygame.draw.rect(tela, cor, quad, border_radius=6)
            pygame.draw.rect(tela, (12, 10, 20), quad, 2, border_radius=6)
            baixa = rr.h < 50  # (linha baixinha: letra menor)
            mini = rr.h < 34   # (baixinha demais: tudo numa linha só, o estado na direita)
            nome_r = "???" if it.get("codigo") and not tem else it["nome"]
            img = pygame.font.SysFont("arialblack,arial", 13 if mini else 15 if baixa else 20, bold=True).render(
                nome_r, True, BRANCO)
            tela.blit(img, (rr.x + 64, rr.centery - img.get_height() // 2 if mini else rr.y + (2 if baixa else 10)))
            veste = "veste" if cat == "roupas" else "usa"
            if usando:
                estado, cor_e = "USANDO", (150, 220, 255)
            elif tem:
                estado, cor_e = f"COMPRADA (ENTER {veste})", (170, 230, 170)
            elif it.get("codigo"):
                estado, cor_e = "SECRETA: só com código", (255, 200, 90)
            else:
                estado, cor_e = None, None
            if estado and mini:
                estado = "COMPRADA" if estado.startswith("COMPRADA") else "SECRETA" if estado.startswith("SECRETA") \
                    else estado
                img = pygame.font.SysFont("arial", 12, bold=True).render(estado, True, cor_e)
                tela.blit(img, (rr.right - img.get_width() - 12, rr.centery - img.get_height() // 2))
            elif estado:
                img = pygame.font.SysFont("arial", 13 if baixa else 15, bold=True).render(estado, True, cor_e)
                tela.blit(img, (rr.x + 64, rr.y + (21 if baixa else 38)))
            else:
                pode = save.moedas() >= it["preco"]
                texto_moedas(tela, it["preco"], rr.x + 160, rr.y + (28 if baixa else 46), self.t, 16)
                if not pode:
                    img = pygame.font.SysFont("arial", 14, bold=True).render("moedas insuficientes", True,
                                                                             (230, 120, 110))
                    tela.blit(img, (rr.x + 176, rr.y + (21 if baixa else 38)))
                    pygame.draw.rect(tela, (230, 120, 110), (rr.right - 34, rr.y + 20, 18, 14), border_radius=3)
                    pygame.draw.arc(tela, (230, 120, 110), (rr.right - 31, rr.y + 10, 12, 16), 0, 3.14, 3)
        if len(itens) == 1 and cat != "roupas":
            texto(tela, "EM BREVE: novidades pra esse lutador!", 15, (200, 200, 230), (690, 200))
        if r.get("codigo") and not self.tem(r):  # a CHARADA da roupa secreta (pista, sem entregar o código)
            import codigos
            pista = codigos.charada(r["codigo"])
            if pista:
                caixa = pygame.Rect(16, 428, 430, 82)
                pygame.draw.rect(tela, (24, 20, 40), caixa, border_radius=10)
                pygame.draw.rect(tela, (255, 200, 90), caixa, 2, border_radius=10)
                texto(tela, "CHARADA", 13, (255, 200, 90), (caixa.centerx, caixa.y + 12))
                fnt = pygame.font.SysFont("arial", 14, bold=True)
                linhas, linha = [], ""
                for palavra in pista.split():
                    if fnt.size(linha + " " + palavra)[0] > caixa.w - 24 and linha:
                        linhas.append(linha)
                        linha = palavra
                    else:
                        linha = (linha + " " + palavra).strip()
                linhas.append(linha)
                for i, lin in enumerate(linhas[:3]):
                    img = fnt.render(lin, True, (235, 230, 250))
                    tela.blit(img, (caixa.centerx - img.get_width() // 2, caixa.y + 24 + i * 17))
        if self.msg_t > 0:
            self.msg_t -= 1
            texto(tela, self.msg, 18, self.msg_cor, (690, 386))
        # personagens embaixo
        for i, carta in enumerate(self.cartas):
            rc = self.rect_carta(i)
            tela.blit(carta, rc.topleft)
            pygame.draw.rect(tela, (12, 10, 20), rc, 3)
            if i == self.i:
                pygame.draw.rect(tela, (255, 220, 70), rc.inflate(6, 6), 3 if (self.t // 10) % 2 else 2)
        texto(tela, "A/D personagem   W/S item   Q/E aba   ENTER ou clique compra/usa   ESC volta", 14, (200, 200, 220),
              (LARGURA // 2, ALTURA - 14))
