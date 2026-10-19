"""PASSE DO EVENTO (v2.x, pedido do Gomes): um passe GRÁTIS durante o evento, pago com os DOCES 🍬 (do eventos.py).
"Se fosse só as skins, ficaria pouca coisa."

  5 PÁGINAS, uma por lutador. A 1ª começa aberta; pegou 3 prêmios de uma página, a próxima abre.
  Cada página tem 5 prêmios, pegos na ordem que quiser:
      30 MOEDAS                      1 doce
      FIGURINHA do evento            2 doces   (vai pro ÁLBUM, figurinhas.py)
      PROVOCAÇÃO do evento           2 doces
      TÍTULO do evento               2 doces   (o mesmo título em todas as páginas: vale pegar em qualquer uma)
      SKIN do evento                 5 doces
  = 12 por página, 60 no passe inteiro (umas 20 vitórias).

O que foi pego fica PRA SEMPRE (a skin não some quando o evento acaba). No save:
  save.d()["passe"] = {"HALLOWEEN": {"SPHYRUS": ["moedas", "skin"], ...}, "titulo": "TERROR DO HALLOWEEN" ou None}

API pros outros arquivos:
  passe.tem(lutador, tipo, evento="HALLOWEEN")  -> True se já pegou ("skin", "provocacao", "figurinha"...)
  passe.titulos()                                -> títulos de evento que o jogador tem
  passe.titulo_escolhido() / passe.escolher_titulo(t ou None)
  passe.TelaPasse(data=None)                     -> .tecla(k) .mouse(pos, clicou) .desenhar(tela) .sair
"""
import math

import pygame

import eventos
import save
import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande, texto_moedas

ABRE = 3  # prêmios pegos numa página pra abrir a próxima

PASSES = {
    eventos.HALLOWEEN: dict(titulo="TERROR DO HALLOWEEN", paginas=("SPHYRUS", "FINN", "CRÁQUEN", "MAX-10", "RIB"),
                            cor=(240, 130, 30)),
}
# (tipo, preço em doces, nome na tela)
PREMIOS = (("moedas", 1, "30 MOEDAS"), ("figurinha", 2, "FIGURINHA"), ("provocacao", 2, "PROVOCAÇÃO"),
           ("titulo", 2, "TÍTULO"), ("skin", 5, "SKIN"))
TIPOS = tuple(p[0] for p in PREMIOS)
PRECO = {p[0]: p[1] for p in PREMIOS}
MOEDAS = 30


# =====================================================================
# o ESTADO (no save)
# =====================================================================
def _estado():
    s = save.d().get("passe")
    if not isinstance(s, dict):
        s = {}
        save.d()["passe"] = s
    return s


def pegos(evento, lutador):
    """Os tipos já pegos daquela página (lista)."""
    ev = _estado().get(evento)
    lista = ev.get(lutador) if isinstance(ev, dict) else None
    return [t for t in lista if t in TIPOS] if isinstance(lista, list) else []


def tem(lutador, tipo, evento=eventos.HALLOWEEN):
    return tipo in pegos(evento, lutador)


def aberta(evento, i):
    """A página i está aberta? (a 1ª sempre; as outras quando a anterior tem 3 prêmios pegos)"""
    pags = PASSES[evento]["paginas"]
    return i == 0 or len(pegos(evento, pags[i - 1])) >= ABRE


def pode_pegar(evento, lutador, tipo):
    """(True, "") ou (False, motivo)."""
    if evento not in PASSES or lutador not in PASSES[evento]["paginas"] or tipo not in TIPOS:
        return False, "?"
    if eventos.tem_conteudo() != evento and not _forcado(evento):
        return False, "O EVENTO ACABOU"
    if not aberta(evento, PASSES[evento]["paginas"].index(lutador)):
        return False, f"PEGUE {ABRE} PRÊMIOS DA PÁGINA ANTERIOR"
    if tem(lutador, tipo, evento):
        return False, "JÁ É SEU"
    if eventos.doces() < PRECO[tipo]:
        return False, "DOCES INSUFICIENTES"
    return True, ""


_FORCA = set()  # (pros testes / pra TelaPasse com data: considera o evento ligado)


def _forcado(evento):
    return evento in _FORCA


def pegar(evento, lutador, tipo):
    """Paga os doces e entrega o prêmio. Devolve True se pegou."""
    ok, _ = pode_pegar(evento, lutador, tipo)
    if not ok or not eventos.gastar(PRECO[tipo]):
        return False
    s = _estado()
    ev = s.get(evento) if isinstance(s.get(evento), dict) else {}
    s[evento] = ev
    ev[lutador] = pegos(evento, lutador) + [tipo]
    if tipo == "moedas":
        save.ganhar(MOEDAS)
    elif tipo == "figurinha":
        try:
            import figurinhas  # (o álbum; se ainda não existir, o prêmio fica guardado aqui e o álbum lê depois)
            figurinhas.ganhar_evento(evento, lutador)
        except (ImportError, AttributeError):
            pass
    elif tipo == "titulo" and not titulo_escolhido():
        s["titulo"] = PASSES[evento]["titulo"]  # (o 1º título já vem escolhido)
    save.salvar()
    return True


def titulos():
    """Os títulos de evento que o jogador já tem."""
    return [PASSES[ev]["titulo"] for ev in PASSES
            if any(tem(l, "titulo", ev) for l in PASSES[ev]["paginas"])]


def titulo_escolhido():
    t = _estado().get("titulo")
    return t if t in titulos() else None


def escolher_titulo(t):
    """t = um dos titulos() ou None (volta pro título de maestria)."""
    _estado()["titulo"] = t if t in titulos() else None
    save.salvar()


def skins():
    """[(evento, lutador)] das skins de evento que o jogador tem (pra loja/seleção liberar a roupa)."""
    return [(ev, l) for ev in PASSES for l in PASSES[ev]["paginas"] if tem(l, "skin", ev)]


# =====================================================================
# os DESENHOS dos prêmios (só desenho)
# =====================================================================
def doce(tela, cx, cy, r=9, cor=(240, 130, 30)):
    """Uma balinha embrulhada."""
    esc = tuple(max(0, c - 70) for c in cor)
    for s in (-1, 1):
        pygame.draw.polygon(tela, esc, [(cx + s * r, cy), (cx + s * (r + r * 0.8), cy - r * 0.6),
                                        (cx + s * (r + r * 0.8), cy + r * 0.6)])
    pygame.draw.circle(tela, cor, (cx, cy), r)
    pygame.draw.arc(tela, (255, 240, 220), (cx - r + 2, cy - r + 2, 2 * r - 4, 2 * r - 4), 0.6, 2.2, 2)
    pygame.draw.line(tela, esc, (cx - r // 2, cy + r // 2), (cx + r // 2, cy - r // 2), 2)


def _icone(tela, tipo, cx, cy, t, retrato, cor):
    if tipo == "moedas":
        for k, (dx, dy) in enumerate(((-12, 8), (10, 6), (0, -6))):
            pygame.draw.circle(tela, (190, 140, 30), (cx + dx, cy + dy), 15)
            pygame.draw.circle(tela, (250, 205, 60), (cx + dx, cy + dy), 12)
            texto(tela, "$", 14, (190, 140, 30), (cx + dx, cy + dy), sombra=False)
    elif tipo == "figurinha":
        r = pygame.Rect(0, 0, 44, 58)
        r.center = (cx, cy + int(2 * math.sin(t * 0.06)))
        pygame.draw.rect(tela, (245, 240, 225), r, border_radius=5)
        pygame.draw.rect(tela, cor, r, 3, border_radius=5)
        if retrato:
            tela.blit(pygame.transform.smoothscale(retrato, (36, 36)), (r.x + 4, r.y + 5))
        pygame.draw.rect(tela, cor, (r.x + 4, r.bottom - 14, r.w - 8, 9), border_radius=3)
    elif tipo == "provocacao":
        pygame.draw.ellipse(tela, BRANCO, (cx - 30, cy - 24, 60, 40))
        pygame.draw.polygon(tela, BRANCO, [(cx - 10, cy + 10), (cx - 20, cy + 26), (cx + 4, cy + 12)])
        texto(tela, "HA HA!", 14, (40, 20, 50), (cx, cy - 4), sombra=False)
    elif tipo == "titulo":
        pygame.draw.polygon(tela, (150, 60, 20), [(cx - 44, cy - 8), (cx - 54, cy + 4), (cx - 44, cy + 16), (cx - 34, cy + 4)])
        pygame.draw.polygon(tela, (150, 60, 20), [(cx + 44, cy - 8), (cx + 54, cy + 4), (cx + 44, cy + 16), (cx + 34, cy + 4)])
        pygame.draw.rect(tela, cor, (cx - 40, cy - 12, 80, 24), border_radius=4)
        texto(tela, "TERROR", 13, (40, 15, 10), (cx, cy), sombra=False)
    elif tipo == "skin":
        if retrato:
            pygame.draw.circle(tela, (60, 30, 20), (cx, cy - 2), 36)
            pygame.draw.circle(tela, cor, (cx, cy - 2), 36, 2)
            tela.blit(pygame.transform.smoothscale(retrato, (64, 64)), (cx - 32, cy - 34))
        eventos.abobora(tela, cx + 30, cy + 12, 10, t)


# =====================================================================
# a TELA
# =====================================================================
class TelaPasse:
    def __init__(self, data=None):
        self.evento = eventos.tem_conteudo(data) or eventos.HALLOWEEN
        if data is not None and eventos.tem_conteudo(data) == self.evento:
            _FORCA.add(self.evento)  # (a tela foi aberta "naquele dia": pros testes)
        self.p = PASSES[self.evento]
        self.pag = 0
        self.premio = len(PREMIOS) - 1  # (começa olhando a SKIN, o prêmio que ele quer)
        self.foco = "premios"           # "paginas", "premios" ou "voltar"
        self.t = 0
        self.sair = False
        self.aviso = None               # (texto, cor, quadros)
        self._retratos = {}
        self.pegou_t = -99              # (animação de "pegou!")

    # ---- áreas ----
    def rect_pagina(self, i):
        n = len(self.p["paginas"])
        w = 150
        x0 = LARGURA // 2 - (n * (w + 10) - 10) // 2
        return pygame.Rect(x0 + i * (w + 10), 74, w, 54)

    def rect_premio(self, i):
        w = 162
        x0 = LARGURA // 2 - (len(PREMIOS) * (w + 12) - 12) // 2
        return pygame.Rect(x0 + i * (w + 12), 196, w, 220)

    def rect_voltar(self):
        return pygame.Rect(LARGURA // 2 - 90, ALTURA - 54, 180, 32)

    # ---- ações ----
    def _avisar(self, txt, cor=(255, 120, 120)):
        self.aviso = (txt, cor, 110)

    def tentar_pegar(self, i):
        lut = self.p["paginas"][self.pag]
        tipo = PREMIOS[i][0]
        ok, motivo = pode_pegar(self.evento, lut, tipo)
        if ok and pegar(self.evento, lut, tipo):
            som.tocar("confirma")
            self.pegou_t = self.t
            self._avisar(f"PEGOU: {PREMIOS[i][2]}" + (f" DO {lut}" if tipo in ("skin", "provocacao", "figurinha") else "")
                         + ("!" if tipo != "titulo" else f" \"{self.p['titulo']}\"!"), (140, 255, 160))
            if self.pag + 1 < len(self.p["paginas"]) and len(pegos(self.evento, lut)) == ABRE:
                self._avisar(f"PÁGINA DO {self.p['paginas'][self.pag + 1]} ABERTA!", (255, 210, 80))
        else:
            som.tocar("defesa")
            self._avisar(motivo)

    def tecla(self, tecla):
        esq = tecla in (pygame.K_a, pygame.K_LEFT)
        dir_ = tecla in (pygame.K_d, pygame.K_RIGHT)
        if esq or dir_:
            d = -1 if esq else 1
            if self.foco == "paginas":
                self.pag = (self.pag + d) % len(self.p["paginas"])
            elif self.foco == "premios":
                self.premio = (self.premio + d) % len(PREMIOS)
            som.tocar("blip")
        elif tecla in (pygame.K_w, pygame.K_UP):
            self.foco = {"voltar": "premios", "premios": "paginas"}.get(self.foco, "paginas")
            som.tocar("blip")
        elif tecla in (pygame.K_s, pygame.K_DOWN):
            self.foco = {"paginas": "premios", "premios": "voltar"}.get(self.foco, "voltar")
            som.tocar("blip")
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE):
            if self.foco == "voltar":
                self.sair = True
            elif self.foco == "paginas":
                self.foco = "premios"
                som.tocar("blip")
            else:
                self.tentar_pegar(self.premio)

    def mouse(self, pos, clicou):
        for i in range(len(self.p["paginas"])):
            if self.rect_pagina(i).collidepoint(pos):
                self.foco = "paginas"
                if clicou and self.pag != i:
                    self.pag = i
                    som.tocar("blip")
                return
        for i in range(len(PREMIOS)):
            if self.rect_premio(i).collidepoint(pos):
                self.foco, self.premio = "premios", i
                if clicou:
                    self.tentar_pegar(i)
                return
        if self.rect_voltar().collidepoint(pos):
            self.foco = "voltar"
            if clicou:
                self.sair = True

    # ---- desenho ----
    def retrato(self, nome):
        if nome not in self._retratos:
            from personagens import PERSONAGENS, SECRETOS
            from selecao import retrato
            f = next((f for f in PERSONAGENS + SECRETOS if f["nome"] == nome), None)
            self._retratos[nome] = retrato(f) if f else None
        return self._retratos[nome]

    def desenhar(self, tela):
        from selecao import fundo_selecao
        self.t += 1
        cor = self.p["cor"]
        tela.blit(fundo_selecao(self.t), (0, 0))
        escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escuro.fill((25, 8, 30, 120))
        tela.blit(escuro, (0, 0))
        if self.evento == eventos.HALLOWEEN:
            eventos.teia(tela, "esq", 60)
        texto_grande(tela, f"PASSE DO {self.evento}", 36, cor, (LARGURA // 2, 34))
        texto(tela, "GRÁTIS", 14, (140, 255, 160), (LARGURA // 2, 60))
        doce(tela, 96, 30, 11, cor)
        texto(tela, f"{eventos.doces()}", 22, (255, 230, 200), (134, 30))
        texto_moedas(tela, save.d().get("moedas", 0), LARGURA - 20, 24, self.t)
        # as páginas
        for i, nome in enumerate(self.p["paginas"]):
            r = self.rect_pagina(i)
            sel, abre = i == self.pag, aberta(self.evento, i)
            pygame.draw.rect(tela, (70, 40, 30) if sel else (26, 20, 32), r, border_radius=10)
            borda = (255, 220, 70) if sel and self.foco == "paginas" else cor if sel else (70, 58, 80)
            pygame.draw.rect(tela, borda, r, 3, border_radius=10)
            img = self.retrato(nome)
            if img:
                mini = pygame.transform.smoothscale(img, (44, 44))
                if not abre:
                    mini.fill((60, 60, 70), special_flags=pygame.BLEND_RGB_MULT)
                tela.blit(mini, (r.x + 6, r.y + 5))
            texto(tela, nome, 14 if len(nome) < 8 else 12, (255, 220, 70) if sel else (210, 205, 220) if abre else (110, 105, 120),
                  (r.x + 98, r.y + 19), sombra=False)
            n = len(pegos(self.evento, nome))
            texto(tela, f"{n}/{len(PREMIOS)}" if abre else "TRANCADA", 12,
                  (140, 255, 160) if n == len(PREMIOS) else (190, 185, 200), (r.x + 98, r.y + 38), sombra=False)
        # a página escolhida
        lut = self.p["paginas"][self.pag]
        abre = aberta(self.evento, self.pag)
        texto(tela, f"PÁGINA {self.pag + 1}: {lut}", 20, BRANCO, (LARGURA // 2, 160))
        img = self.retrato(lut)
        for i, (tipo, preco, nome) in enumerate(PREMIOS):
            r = self.rect_premio(i)
            ja = tem(lut, tipo, self.evento)
            sel = self.foco == "premios" and i == self.premio
            sobe = -6 if sel else 0
            r = r.move(0, sobe)
            fundo = (30, 50, 32) if ja else (40, 24, 20) if abre else (22, 20, 28)
            pygame.draw.rect(tela, fundo, r, border_radius=12)
            borda = (255, 220, 70) if sel else (90, 200, 110) if ja else cor if abre else (60, 55, 70)
            pygame.draw.rect(tela, borda, r, 3 if not sel else 4, border_radius=12)
            texto(tela, nome, 16, (255, 225, 150) if abre else (120, 115, 130), (r.centerx, r.y + 22))
            _icone(tela, tipo, r.centerx, r.y + 96, self.t + i * 9, img, cor)
            if tipo == "titulo":
                texto(tela, f"\"{self.p['titulo']}\"", 10, (230, 200, 170), (r.centerx, r.y + 140), sombra=False)
            elif tipo in ("skin", "provocacao", "figurinha"):
                texto(tela, f"de {self.evento.lower()}", 11, (230, 200, 170), (r.centerx, r.y + 140), sombra=False)
            if ja:
                c = (r.centerx, r.bottom - 38)
                pygame.draw.circle(tela, (60, 170, 80), c, 18)
                pygame.draw.lines(tela, BRANCO, False, [(c[0] - 8, c[1]), (c[0] - 2, c[1] + 7), (c[0] + 9, c[1] - 7)], 4)
                if self.t - self.pegou_t < 30 and sel:  # (estrelinhas de "pegou!")
                    k = (self.t - self.pegou_t) / 30
                    for a in range(8):
                        ang = a * math.pi / 4
                        pygame.draw.circle(tela, (255, 230, 120), (int(c[0] + math.cos(ang) * 50 * k),
                                                                  int(c[1] - 40 + math.sin(ang) * 50 * k)), 3)
            elif abre:
                pode = eventos.doces() >= preco
                doce(tela, r.centerx - 14, r.bottom - 38, 10, cor)
                texto(tela, str(preco), 22, (255, 240, 210) if pode else (255, 110, 110), (r.centerx + 14, r.bottom - 38))
            else:
                from perfil import _cadeado
                _cadeado(tela, r.centerx, r.bottom - 36)
        if not abre:
            texto(tela, f"Pegue {ABRE} prêmios da página do {self.p['paginas'][self.pag - 1]} pra abrir esta",
                  15, (255, 200, 140), (LARGURA // 2, 438))
        else:
            texto(tela, f"pegue {ABRE} prêmios pra abrir a próxima página   vitória +{eventos.DOCES_VITORIA}"
                        f"   derrota +{eventos.DOCES_DERROTA}", 13, (200, 190, 210), (LARGURA // 2, 438))
        if self.aviso:
            txt, c, q = self.aviso
            texto_grande(tela, txt, 22, c, (LARGURA // 2, 462), 1.0, alfa=min(255, q * 8))
            self.aviso = (txt, c, q - 1) if q > 1 else None
        r = self.rect_voltar()
        sel = self.foco == "voltar"
        pygame.draw.rect(tela, (54, 46, 84) if sel else (26, 22, 42), r, border_radius=10)
        pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), r, 3, border_radius=10)
        texto(tela, "VOLTAR", 18, (255, 220, 70) if sel else BRANCO, r.center)
        texto(tela, "W/S: páginas / prêmios / VOLTAR   A/D escolhe   ENTER pega   ESC volta", 12, (170, 170, 195),
              (LARGURA // 2, ALTURA - 11))
