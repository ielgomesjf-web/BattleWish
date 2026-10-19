"""PERFIL E TROFÉUS (v2.0, pedido do Gomes): a tela com tudo que o jogador já fez.
Abas: ESTATÍSTICAS / TROFÉUS / MISSÕES DO DIA (A/D, setas ou clique trocam).
Os troféus são conferidos no fim de cada luta (trofeus_novos) e ficam em save.d()["trofeus"] (lista de ids).
"""
import datetime
import math

import pygame

import save
import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande, texto_moedas


# =====================================================================
# TROFÉUS: (id, nome, dica, condição(g = estatísticas gerais, d = estatísticas inteiras))
# =====================================================================
def _ps(d):
    return d["personagens"].values()


def _maior_maestria():
    import maestria
    from personagens import PERSONAGENS, SECRETOS
    return max([maestria.nivel(f["nome"]) for f in PERSONAGENS + SECRETOS] or [1])


def _todos_jogados(d):
    from personagens import PERSONAGENS
    return all(d["personagens"].get(f["nome"], {}).get("lutas", 0) > 0 for f in PERSONAGENS)


def _roupas():
    return sum(len(v) for v in save.d().get("roupas", {}).values() if isinstance(v, list))


def _recorde_rei():
    import reiarena
    return reiarena.recorde()["recorde"]


def _extras():
    """Quantas entradas/vitórias/provocações compradas (a loja nova guarda em save["extras"])."""
    ex = save.d().get("extras")
    if not isinstance(ex, dict):
        return 0
    return sum(len(lst) for cat in ex.values() if isinstance(cat, dict) for lst in cat.values() if isinstance(lst, list))


def _fotos():
    import os
    import foto
    try:
        return len([n for n in os.listdir(foto.pasta_fotos()) if n.startswith("battlewish_") and n.endswith(".png")])
    except OSError:
        return 0


def _todos_maestria(n):
    import maestria
    from personagens import PERSONAGENS
    return all(maestria.nivel(f["nome"]) >= n for f in PERSONAGENS)


def _vitorias_rival():
    import rivais
    return rivais.vitorias()


def _missoes_feitas():
    import missoes
    return missoes.feitas_total()


TROFEUS = [
    ("vitoria1", "PRIMEIRA VITÓRIA", "Vença uma luta", lambda g, d: g["vitorias"] >= 1),
    ("vitoria10", "DEZ VITÓRIAS", "Vença 10 lutas", lambda g, d: g["vitorias"] >= 10),
    ("vitoria50", "LENDA DA ARENA", "Vença 50 lutas", lambda g, d: g["vitorias"] >= 50),
    ("lutas100", "MARATONISTA", "Jogue 100 lutas", lambda g, d: g["lutas"] >= 100),
    ("fiel", "PARCEIRO FIEL", "Vença 10 lutas com o mesmo lutador",
     lambda g, d: any(p.get("vitorias", 0) >= 10 for p in _ps(d))),
    ("todos", "TODO MUNDO JOGA", "Lute com todos os lutadores", lambda g, d: _todos_jogados(d)),
    ("perfect", "PERFEITO!", "Vença um round sem perder vida", lambda g, d: g["perfects"] >= 1),
    ("perfect10", "INTOCÁVEL", "Faça 10 PERFECTS", lambda g, d: g["perfects"] >= 10),
    ("combo15", "COMBO DE 15", "Faça um combo de 15 golpes", lambda g, d: g["maior_combo"] >= 15),
    ("ult", "ULTIMATE!", "Acerte uma ULTIMATE", lambda g, d: g["ults"] >= 1),
    ("ult25", "SUPER PODER", "Acerte 25 ULTIMATES", lambda g, d: g["ults"] >= 25),
    ("parry", "PAREDÃO", "Faça 10 PARRYS", lambda g, d: g["parrys"] >= 10),
    ("quebra", "QUEBRA-GUARDA", "Quebre a guarda 10 vezes", lambda g, d: g["quebras"] >= 10),
    ("choque", "CHOCANTE", "Vença 5 CHOQUES", lambda g, d: g["choques"] >= 5),
    ("objetos", "O CENÁRIO É MEU", "Use 10 objetos do cenário", lambda g, d: g["objetos"] >= 10),
    ("transicao", "VIAJANTE", "Jogue o adversário pra outro cenário 3 vezes", lambda g, d: g["transicoes"] >= 3),
    ("provoca", "PROVOCADOR", "Provoque 20 vezes (tecla T)", lambda g, d: g["provocacoes"] >= 20),
    ("pulos", "PERNA DE MOLA", "Pule 500 vezes", lambda g, d: g["pulos"] >= 500),
    ("maestria5", "APRENDIZ DE MESTRE", "Chegue no nível 5 de MAESTRIA", lambda g, d: _maior_maestria() >= 5),
    ("maestria10", "MESTRE", "Chegue no nível 10 de MAESTRIA", lambda g, d: _maior_maestria() >= 10),
    ("codigo", "CAÇADOR DE SEGREDOS", "Ache um código secreto",
     lambda g, d: len(save.d().get("codigos", [])) >= 1),
    ("roupas", "FASHION", "Tenha 5 roupas", lambda g, d: _roupas() >= 5),
    ("sobrev", "SOBREVIVENTE", "Derrube 5 lutadores na SOBREVIVÊNCIA",
     lambda g, d: save.d().get("recorde_sobrevivencia", 0) >= 5),
    ("missoes", "MISSÃO CUMPRIDA", "Cumpra 10 MISSÕES DO DIA", lambda g, d: _missoes_feitas() >= 10),
    ("rival", "RIVAL DERROTADO", "Vença o RIVAL do seu lutador", lambda g, d: _vitorias_rival() >= 1),
    ("rival10", "ARQUI-INIMIGO", "Vença RIVAIS 10 vezes", lambda g, d: _vitorias_rival() >= 10),
    # ---- v2.x: as coisas novas ----
    ("ult2", "PODER MÁXIMO", "Acerte uma 2ª ULTIMATE", lambda g, d: g.get("ults2", 0) >= 1),
    ("rei3", "REI DA ARENA", "Fique 3 lutas seguidas no trono do REI DA ARENA", lambda g, d: _recorde_rei() >= 3),
    ("estilo", "ESTILO PRÓPRIO", "Compre uma entrada, vitória ou provocação", lambda g, d: _extras() >= 1),
    ("estilo10", "COLECIONADOR", "Tenha 10 entradas, vitórias ou provocações", lambda g, d: _extras() >= 10),
    ("foto", "FOTÓGRAFO", "Tire 10 fotos no MODO FOTO", lambda g, d: _fotos() >= 10),
    ("todos3", "TIME COMPLETO", "Leve todos os lutadores pro nível 3 de MAESTRIA", lambda g, d: _todos_maestria(3)),
]
NOMES = {t[0]: t[1] for t in TROFEUS}


def ganhos():
    """Os ids dos troféus já conquistados."""
    lista = save.d().get("trofeus")
    if not isinstance(lista, list):
        lista = save.d()["trofeus"] = []
    return lista


def trofeus_novos():
    """Confere todos os troféus. Os que acabaram de ser conquistados entram no save (e salva).
    Devolve a lista dos NOMES novos (pra tela mostrar "TROFÉU: X!")."""
    import estatisticas
    d = estatisticas.dados()
    g = d["geral"]
    tem = ganhos()
    novos = []
    for tid, nome, _, cond in TROFEUS:
        if tid in tem:
            continue
        try:
            ok = cond(g, d)
        except Exception:  # (save estranho: o troféu só não sai agora)
            ok = False
        if ok:
            tem.append(tid)
            novos.append(nome)
    if novos:
        save.salvar()
    return novos


def nome_do_golpe(id_golpe):
    """'king_bumerangue' -> 'nunchaku bumerangue (KING RIP)'; 'soco' -> 'SOCO'."""
    from personagens import PERSONAGENS, SECRETOS
    for f in PERSONAGENS + SECRETOS:
        for botao, g in f.get("golpes", {}).items():
            if g == id_golpe and f.get("nomes", {}).get(botao):
                return f"{f['nomes'][botao]} ({f['nome']})"
    return id_golpe.replace("_", " ").upper()


def _n(n, palavra):
    """3 lutas / 1 luta."""
    return f"{n} {palavra}" + ("" if n == 1 else "s")


# =====================================================================
# desenhos pequenos
# =====================================================================
def _taca(tela, cx, cy, cor, t=0, brilha=False):
    """Uma taça de troféu."""
    escura = tuple(c * 2 // 3 for c in cor)
    pygame.draw.rect(tela, escura, (cx - 11, cy + 12, 22, 6))                  # base
    pygame.draw.rect(tela, cor, (cx - 3, cy + 4, 6, 9))                        # pé
    pygame.draw.polygon(tela, cor, [(cx - 13, cy - 14), (cx + 13, cy - 14), (cx + 8, cy + 4), (cx - 8, cy + 4)])
    pygame.draw.arc(tela, cor, (cx - 20, cy - 13, 12, 12), math.pi / 2, math.pi * 1.5, 3)  # alças
    pygame.draw.arc(tela, cor, (cx + 8, cy - 13, 12, 12), -math.pi / 2, math.pi / 2, 3)
    pygame.draw.line(tela, (255, 255, 230), (cx - 7, cy - 11), (cx - 4, cy), 2)  # reflexo
    if brilha and (t // 12) % 4 == 0:
        pygame.draw.circle(tela, (255, 255, 255), (cx + 9, cy - 13), 2)


def _estrela(tela, cx, cy, r, cor=(255, 215, 60)):
    pts = [(cx + math.cos(-math.pi / 2 + i * math.pi / 5) * (r if i % 2 == 0 else r * 0.45),
            cy + math.sin(-math.pi / 2 + i * math.pi / 5) * (r if i % 2 == 0 else r * 0.45)) for i in range(10)]
    pygame.draw.polygon(tela, cor, pts)
    pygame.draw.polygon(tela, (120, 80, 10), pts, 1)


def _cadeado(tela, cx, cy):
    pygame.draw.arc(tela, (120, 115, 140), (cx - 9, cy - 16, 18, 20), 0, math.pi, 3)
    pygame.draw.rect(tela, (120, 115, 140), (cx - 12, cy - 6, 24, 18), border_radius=3)
    pygame.draw.circle(tela, (40, 36, 56), (cx, cy + 2), 3)


# =====================================================================
# a TELA
# =====================================================================
ABAS = ["ESTATÍSTICAS", "TROFÉUS", "MISSÕES DO DIA", "ÁLBUM"]


class TelaPerfil:
    def __init__(self, aba=0):
        self.aba = aba
        self.t = 0
        self.sair = False
        self.foco = "abas"        # "abas" ou "voltar" (W/S troca; ENTER no VOLTAR sai)
        self._retratos = {}
        self.sobre = None         # troféu com o mouse em cima (mostra a dica maior)
        self.album = None         # o ÁLBUM aberto (figurinhas.TelaAlbum) por cima do perfil
        self.escolhendo = None    # escolhendo o FAVORITO (o que luta com a sombra no menu): índice na grade

    # ---- áreas ----
    def rect_aba(self, i):
        w = 200
        x0 = LARGURA // 2 - (len(ABAS) * (w + 10) - 10) // 2
        return pygame.Rect(x0 + i * (w + 10), 78, w, 36)

    def rect_voltar(self):
        return pygame.Rect(LARGURA // 2 - 90, ALTURA - 54, 180, 32)

    def rect_trofeu(self, i):
        col, lin = i % 4, i // 4
        passo = min(59, 350 // -(-len(TROFEUS) // 4))  # (mais troféus = linhas mais baixinhas, pra caber)
        return pygame.Rect(36 + col * 226, 128 + lin * passo, 216, passo - 6)

    # ---- teclas e mouse ----
    def rect_abrir_album(self):
        return pygame.Rect(LARGURA // 2 - 130, 384, 260, 46)

    def abrir_album(self):
        import figurinhas
        self.album = figurinhas.TelaAlbum()
        som.tocar("confirma")

    # ---- o FAVORITO (vitrine do menu) ----
    def rect_favorito(self):
        return pygame.Rect(484 + 440 - 132, 128 + 8, 122, 26)

    def lista_fav(self):
        import vitrine
        return [f["nome"] for f in vitrine.disponiveis()]

    def rect_escolha(self, i):
        n = len(self.lista_fav())
        por = 8
        col, lin = i % por, i // por
        w = 100
        x0 = LARGURA // 2 - (por * (w + 10) - 10) // 2
        return pygame.Rect(x0 + col * (w + 10), 170 + lin * 128, w, 118)

    def abrir_favorito(self):
        import vitrine
        nomes = self.lista_fav()
        fav = vitrine.favorito()
        self.escolhendo = nomes.index(fav) if fav in nomes else 0
        som.tocar("confirma")

    def tecla_favorito(self, tecla):
        import vitrine
        n = len(self.lista_fav())
        mov = {pygame.K_a: -1, pygame.K_LEFT: -1, pygame.K_d: 1, pygame.K_RIGHT: 1,
               pygame.K_w: -8, pygame.K_UP: -8, pygame.K_s: 8, pygame.K_DOWN: 8}
        if tecla in mov:
            self.escolhendo = max(0, min(n - 1, self.escolhendo + mov[tecla]))
            som.tocar("blip")
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE):
            vitrine.definir_favorito(self.lista_fav()[self.escolhendo])
            som.tocar("confirma")
            self.escolhendo = None
        elif tecla in (pygame.K_f, pygame.K_BACKSPACE):
            self.escolhendo = None

    def desenhar_escolha_favorito(self, tela):
        import vitrine
        from selecao import fundo_selecao
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, "ESCOLHA O FAVORITO", 34, (255, 220, 70), (LARGURA // 2, 50))
        texto(tela, "ele fica lutando contra a SOMBRA dele na tela inicial", 16, (210, 210, 230), (LARGURA // 2, 92))
        atual = vitrine.escolhido()
        for i, nome in enumerate(self.lista_fav()):
            r = self.rect_escolha(i)
            sel = i == self.escolhendo
            pygame.draw.rect(tela, (60, 50, 96) if sel else (24, 20, 40), r, border_radius=10)
            pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), r, 3 if sel else 2, border_radius=10)
            img = self.retrato(nome)
            if img:
                tela.blit(pygame.transform.smoothscale(img, (84, 84)), (r.x + 8, r.y + 6))
            texto(tela, nome, 12 if len(nome) < 9 else 10, (255, 220, 70) if sel else BRANCO, (r.centerx, r.bottom - 14),
                  sombra=False)
            if nome == atual:
                _estrela(tela, r.right - 14, r.y + 14, 11)
        texto(tela, "WASD escolhe   ENTER confirma   F volta", 14, (180, 180, 200), (LARGURA // 2, ALTURA - 20))

    def tecla(self, tecla):
        if self.album:
            self.album.tecla(tecla)
            return
        if self.escolhendo is not None:
            self.tecla_favorito(tecla)
            return
        if tecla == pygame.K_f and self.aba == 0:
            self.abrir_favorito()
            return
        if tecla in (pygame.K_a, pygame.K_LEFT):
            self.aba = (self.aba - 1) % len(ABAS)
            self.foco = "abas"
            som.tocar("blip")
        elif tecla in (pygame.K_d, pygame.K_RIGHT):
            self.aba = (self.aba + 1) % len(ABAS)
            self.foco = "abas"
            som.tocar("blip")
        elif tecla in (pygame.K_s, pygame.K_DOWN):
            self.foco = "voltar"
            som.tocar("blip")
        elif tecla in (pygame.K_w, pygame.K_UP):
            self.foco = "abas"
            som.tocar("blip")
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE):
            if self.foco == "voltar":
                self.sair = True
            elif self.aba == 3:  # ENTER na aba ÁLBUM: abre o álbum
                self.abrir_album()
            else:  # ENTER nas abas: vai pra próxima
                self.aba = (self.aba + 1) % len(ABAS)
                som.tocar("blip")

    def mouse(self, pos, clicou):
        if self.album:
            self.album.mouse(pos, clicou)
            return
        if self.escolhendo is not None:
            for i in range(len(self.lista_fav())):
                if self.rect_escolha(i).collidepoint(pos):
                    self.escolhendo = i
                    if clicou:
                        self.tecla_favorito(pygame.K_RETURN)
                    return
            return
        self.sobre = None
        if self.aba == 0 and clicou and self.rect_favorito().collidepoint(pos):
            self.abrir_favorito()
            return
        if self.aba == 3 and clicou and self.rect_abrir_album().collidepoint(pos):
            self.abrir_album()
            return
        for i in range(len(ABAS)):
            if self.rect_aba(i).collidepoint(pos):
                self.foco = "abas"
                if clicou and self.aba != i:
                    self.aba = i
                    som.tocar("blip")
                return
        if self.rect_voltar().collidepoint(pos):
            self.foco = "voltar"
            if clicou:
                self.sair = True
            return
        if self.aba == 1:
            for i in range(len(TROFEUS)):
                if self.rect_trofeu(i).collidepoint(pos):
                    self.sobre = i
                    return

    # ---- desenho ----
    def retrato(self, nome):
        if nome not in self._retratos:
            from personagens import PERSONAGENS, SECRETOS
            from selecao import retrato
            f = next((f for f in PERSONAGENS + SECRETOS if f["nome"] == nome), None)
            self._retratos[nome] = pygame.transform.smoothscale(retrato(f), (96, 96)) if f else None
        return self._retratos[nome]

    def desenhar(self, tela):
        from selecao import fundo_selecao
        self.t += 1
        if self.album:
            self.album.desenhar(tela)
            if self.album.sair:  # (o VOLTAR do álbum volta pro perfil)
                self.album = None
            return
        if self.escolhendo is not None:
            self.desenhar_escolha_favorito(tela)
            return
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, "PERFIL", 40, (255, 220, 70), (LARGURA // 2, 38))
        texto_moedas(tela, save.d().get("moedas", 0), LARGURA - 20, 24, self.t)
        for i, nome in enumerate(ABAS):
            r = self.rect_aba(i)
            sel = i == self.aba
            pygame.draw.rect(tela, (70, 58, 110) if sel else (26, 22, 42), r, border_radius=10)
            borda = (255, 220, 70) if sel and self.foco == "abas" else (150, 130, 200) if sel else (70, 62, 100)
            pygame.draw.rect(tela, borda, r, 3, border_radius=10)
            texto(tela, nome, 17, (255, 220, 70) if sel else (200, 200, 220), r.center)
        [self.desenhar_estatisticas, self.desenhar_trofeus, self.desenhar_missoes, self.desenhar_album][self.aba](tela)
        r = self.rect_voltar()
        sel = self.foco == "voltar"
        pygame.draw.rect(tela, (54, 46, 84) if sel else (26, 22, 42), r, border_radius=10)
        pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), r, 3, border_radius=10)
        texto(tela, "VOLTAR", 18, (255, 220, 70) if sel else BRANCO, r.center)
        import controle_video
        rodape = "direcional: aba / VOLTAR   A confirma   B volta" if controle_video.no_controle() else \
            "A/D troca a aba   S + ENTER ou clique: VOLTAR   ESC volta"
        texto(tela, rodape, 12, (170, 170, 195), (LARGURA // 2, ALTURA - 11))

    def caixa(self, tela, r):
        pygame.draw.rect(tela, (18, 15, 32), r, border_radius=12)
        pygame.draw.rect(tela, (70, 62, 100), r, 2, border_radius=12)

    def desenhar_estatisticas(self, tela):
        import estatisticas
        import maestria
        d = estatisticas.dados()
        g = d["geral"]
        esq = pygame.Rect(36, 128, 430, 352)
        self.caixa(tela, esq)
        pct = f"{round(100 * g['vitorias'] / g['lutas'])}%" if g["lutas"] else "-"
        minutos = g["quadros"] // (FPS * 60)
        linhas = [("LUTAS", g["lutas"]), ("VITÓRIAS", f"{g['vitorias']}  ({pct})"), ("DERROTAS", g["derrotas"]),
                  ("PERFECTS", g["perfects"]), ("MAIOR COMBO", g["maior_combo"]), ("ULTIMATES", g["ults"]),
                  ("PARRYS", g["parrys"]), ("GUARDAS QUEBRADAS", g["quebras"]), ("CHOQUES VENCIDOS", g["choques"]),
                  ("OBJETOS USADOS", g["objetos"]), ("PULOS", g["pulos"]),
                  ("TEMPO LUTANDO", f"{minutos // 60}h {minutos % 60:02d}min" if minutos >= 60 else f"{minutos} min")]
        for i, (nome, v) in enumerate(linhas):
            y = esq.y + 22 + i * 27
            if i % 2 == 0:
                pygame.draw.rect(tela, (26, 22, 44), (esq.x + 8, y - 12, esq.w - 16, 25), border_radius=6)
            texto(tela, nome, 15, (200, 200, 222), (esq.x + 120, y), sombra=False)
            texto(tela, str(v), 16, (255, 230, 120), (esq.x + 330, y), sombra=False)
        dir_ = pygame.Rect(484, 128, 440, 352)
        self.caixa(tela, dir_)
        import vitrine
        mj = estatisticas.personagem_favorito()
        tem_fav = vitrine.escolhido() or (mj and mj[1] > 0)
        texto(tela, "LUTADOR FAVORITO", 15, (200, 200, 222), (dir_.centerx - 50, dir_.y + 20))
        b = self.rect_favorito()  # o botão de escolher (o favorito luta com a sombra no menu)
        pygame.draw.rect(tela, (60, 50, 96), b, border_radius=8)
        pygame.draw.rect(tela, (255, 220, 70), b, 2, border_radius=8)
        _estrela(tela, b.x + 14, b.centery, 8)
        texto(tela, "TROCAR (F)", 13, (255, 220, 70), (b.centerx + 8, b.centery), sombra=False)
        if tem_fav:
            nome = vitrine.favorito()
            img = self.retrato(nome)
            rr = pygame.Rect(dir_.x + 24, dir_.y + 42, 96, 96)
            if img:
                tela.blit(img, rr)
            pygame.draw.rect(tela, (70, 62, 100), rr, 2)
            maestria.desenhar_moldura(tela, rr, nome, self.t)
            p = estatisticas.personagem(nome)
            texto(tela, nome, 22, BRANCO, (dir_.x + 270, dir_.y + 56))
            tit = maestria.titulo(nome)
            if tit:
                texto(tela, tit, 13, maestria.moldura(nome) or (200, 200, 222), (dir_.x + 270, dir_.y + 78))
            texto(tela, f"{_n(p['lutas'], 'luta')}   {_n(p['vitorias'], 'vitória')}", 14, (220, 220, 235),
                  (dir_.x + 270, dir_.y + 100))
            n, xp, prox = maestria.progresso(nome)
            barra = pygame.Rect(dir_.x + 160, dir_.y + 118, 220, 10)
            pygame.draw.rect(tela, (14, 10, 26), barra.inflate(4, 4), border_radius=4)
            pygame.draw.rect(tela, maestria.moldura(nome) or (120, 200, 255),
                             (barra.x, barra.y, int(barra.w * (xp / prox if prox else 1)), barra.h), border_radius=4)
            texto(tela, f"MAESTRIA NÍVEL {n}", 12, (200, 200, 222), (barra.centerx, barra.bottom + 12))
        else:
            texto(tela, "jogue uma luta pra aparecer aqui!", 15, (170, 170, 195), (dir_.centerx, dir_.y + 90))
        gf = estatisticas.golpe_favorito()
        texto(tela, "GOLPE FAVORITO", 15, (200, 200, 222), (dir_.centerx, dir_.y + 178))
        if gf:
            texto(tela, nome_do_golpe(gf[0]), 17, BRANCO, (dir_.centerx, dir_.y + 202))
            texto(tela, f"acertou {gf[1]} vezes", 13, (190, 190, 210), (dir_.centerx, dir_.y + 224))
        else:
            texto(tela, "-", 17, BRANCO, (dir_.centerx, dir_.y + 202))
        # os mais jogados (até 3, com as vitórias)
        ps = sorted(((n, p) for n, p in d["personagens"].items() if p.get("lutas", 0) > 0),
                    key=lambda kv: -kv[1].get("lutas", 0))[:3]
        texto(tela, "MAIS JOGADOS", 15, (200, 200, 222), (dir_.centerx, dir_.y + 258))
        for i, (n, p) in enumerate(ps):
            texto(tela, f"{n}: {_n(p['lutas'], 'luta')}, {_n(p['vitorias'], 'vitória')}, maior combo {p['maior_combo']}",
                  13, (220, 220, 235), (dir_.centerx, dir_.y + 282 + i * 20))

    def desenhar_trofeus(self, tela):
        from selecao import quebrar
        tem = set(ganhos())
        for i, (tid, nome, dica, _) in enumerate(TROFEUS):
            r = self.rect_trofeu(i)
            ok = tid in tem
            destaque = self.sobre == i
            pygame.draw.rect(tela, (40, 34, 20) if ok else (20, 18, 32), r, border_radius=8)
            pygame.draw.rect(tela, (255, 210, 70) if ok and destaque else (200, 160, 60) if ok else
                             (150, 140, 180) if destaque else (56, 50, 80), r, 2, border_radius=8)
            if ok:
                _taca(tela, r.x + 26, r.centery, (240, 190, 50), self.t + i * 7, brilha=True)
            else:
                _cadeado(tela, r.x + 26, r.centery + 2)
            from efeitos import fonte
            titulo = nome if ok else "???"
            tam = next((t for t in (14, 13, 12, 11) if fonte(t).size(titulo)[0] <= 158), 11)  # (nome comprido: menor)
            baixo = r.h < 50  # (cartão baixinho: letra da dica menor)
            td = 10 if baixo else 11
            texto(tela, titulo, tam, (255, 225, 120) if ok else (150, 145, 170), (r.x + 132, r.y + (11 if baixo else 13)),
                  sombra=False)
            linhas = quebrar(dica, td, 158)[:2]
            for k, linha in enumerate(linhas):
                if baixo:
                    y = r.y + (29 if len(linhas) == 1 else 24 + k * 11)
                else:
                    y = r.y + (33 if len(linhas) == 1 else 28 + k * 12)
                texto(tela, linha, td, (215, 215, 230) if ok else (130, 126, 150), (r.x + 132, y), sombra=False)
        texto(tela, f"{len(tem & set(NOMES))} de {len(TROFEUS)} troféus", 15, (255, 220, 120), (LARGURA - 110, 60))

    def desenhar_missoes(self, tela):
        import missoes
        lista = missoes.hoje()
        for i, m in enumerate(lista):
            r = pygame.Rect(90, 140 + i * 102, LARGURA - 180, 88)
            pygame.draw.rect(tela, (22, 34, 24) if m["feita"] else (20, 18, 36), r, border_radius=12)
            pygame.draw.rect(tela, (90, 200, 110) if m["feita"] else (90, 80, 130), r, 3, border_radius=12)
            texto(tela, m["texto"], 20, (150, 255, 170) if m["feita"] else BRANCO, (r.x + 330, r.y + 24))
            barra = pygame.Rect(r.x + 120, r.y + 50, 420, 14)
            pygame.draw.rect(tela, (10, 8, 20), barra.inflate(4, 4), border_radius=6)
            k = m["prog"] / m["alvo"] if m["alvo"] else 1
            pygame.draw.rect(tela, (90, 210, 110) if m["feita"] else (120, 180, 255),
                             (barra.x, barra.y, int(barra.w * k), barra.h), border_radius=6)
            texto(tela, f"{m['prog']}/{m['alvo']}", 13, BRANCO, barra.center, sombra=False)
            texto_moedas(tela, f"+{m['moedas']}", r.right - 34, r.y + 30, self.t, tam=18)
            texto(tela, f"+{m['xp']} MAESTRIA", 13, (150, 220, 255), (r.right - 80, r.y + 58))
            if m["feita"]:  # o "check" verde
                c = (r.x + 50, r.centery)
                pygame.draw.circle(tela, (60, 170, 80), c, 22)
                pygame.draw.lines(tela, BRANCO, False, [(c[0] - 10, c[1]), (c[0] - 3, c[1] + 8), (c[0] + 11, c[1] - 8)], 4)
            else:
                pygame.draw.circle(tela, (60, 54, 90), (r.x + 50, r.centery), 22, 3)
                texto(tela, str(i + 1), 20, (200, 200, 222), (r.x + 50, r.centery))
        agora = datetime.datetime.now()  # (só desenho: quanto falta pra virar o dia)
        falta = datetime.datetime.combine(agora.date() + datetime.timedelta(days=1), datetime.time()) - agora
        h, mnt = falta.seconds // 3600, falta.seconds % 3600 // 60
        texto(tela, f"missões novas em {h}h {mnt:02d}min   (a missão dá moedas + MAESTRIA pro lutador que cumprir)",
              14, (190, 190, 210), (LARGURA // 2, 456))

    def desenhar_album(self, tela):
        import figurinhas
        tem, total = figurinhas.quantas()
        r = pygame.Rect(150, 140, LARGURA - 300, 300)
        self.caixa(tela, r)
        texto_grande(tela, "ÁLBUM DE FIGURINHAS", 28, (255, 220, 70), (LARGURA // 2, r.y + 34))
        barra = pygame.Rect(r.x + 80, r.y + 74, r.w - 160, 20)
        pygame.draw.rect(tela, (10, 8, 20), barra.inflate(4, 4), border_radius=8)
        pygame.draw.rect(tela, (120, 180, 255), (barra.x, barra.y, int(barra.w * tem / max(1, total)), barra.h),
                         border_radius=8)
        texto(tela, f"{tem} de {total} figurinhas", 15, BRANCO, barra.center, sombra=False)
        # 3 figurinhas de enfeite (as últimas que ele tem, ou espaços vazios)
        lista = [i for i in figurinhas.todas() if figurinhas.tem(i)][-3:]
        for k in range(3):
            fr = pygame.Rect(0, 0, 80, 104)
            fr.center = (LARGURA // 2 + (k - 1) * 100, r.y + 160)
            if k < len(lista):
                figurinhas.desenhar_figurinha(tela, lista[k], fr, self.t + k * 11)
            else:
                pygame.draw.rect(tela, (24, 22, 36), fr, border_radius=8)
                pygame.draw.rect(tela, (70, 64, 92), fr, 2, border_radius=8)
                texto(tela, "?", 30, (80, 74, 104), fr.center, sombra=False)
        holo = figurinhas.holograficas()
        texto(tela, f"SKINS HOLOGRÁFICAS: {len(holo)}", 14, (200, 190, 230), (LARGURA // 2, r.y + 228))
        b = self.rect_abrir_album()
        sel = self.foco == "abas"
        pygame.draw.rect(tela, (70, 58, 110) if sel else (26, 22, 42), b, border_radius=12)
        pygame.draw.rect(tela, (255, 220, 70) if sel else (150, 130, 200), b, 3, border_radius=12)
        texto(tela, "ABRIR O ÁLBUM (ENTER)", 18, (255, 220, 70) if sel else BRANCO, b.center)
