"""ÁLBUM DE FIGURINHAS (v2.x, pedido do Gomes).

  Toda luta de gente (as mesmas das ESTATÍSTICAS) tem CHANCE de dar 1 figurinha. Fazer coisas que têm a ver
  com a figurinha aumenta a chance dela: jogar com o lutador, acertar a ULT / 2ª ULT dele, lutar no cenário.
  Repetida vira 10 moedas.

  PÁGINAS
    16 de LUTADOR, 6 figurinhas cada: o LUTADOR, a ULTIMATE, a 2ª ULTIMATE, a CASA, a PASSIVA e a BRILHANTE (rara)
       (o RIBBAT não tem 2ª ult nem passiva: no lugar vêm a LINGUADA e a INVESTIDA)
    CENÁRIOS (de 6 em 6)
    EVENTOS: as figurinhas do PASSE DO EVENTO (passe.py), que só saem lá
  Completar a página de um lutador libera a SKIN HOLOGRÁFICA dele.

No save: save.d()["album"] = {"tem": [ids], "repetidas": n}.

API pros outros arquivos:
  figurinhas.sortear_da_luta(partida)   fim da luta: devolve um "ganho" (dict) ou None. Já salva e paga a repetida.
  figurinhas.desenhar_ganho(tela, ganho, t)  a figurinha virando na tela de resultado (t = quadros desde que apareceu)
  figurinhas.holograficas()             [nomes] dos lutadores com a skin HOLOGRÁFICA liberada
  figurinhas.ganhar_evento(evento, lutador)  (o passe chama)
  figurinhas.TelaAlbum()                .tecla(k) .mouse(pos, clicou) .desenhar(tela) .sair
"""
import math
import random

import pygame

import save
import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande, texto_moedas

CHANCE_VITORIA = 0.45
CHANCE_DERROTA = 0.25
MOEDAS_REPETIDA = 10
# peso de cada figurinha no sorteio (quanto maior, mais fácil sair)
PESO = dict(base=1.0, brilhante=0.25, brilhante_meu=8.0, meu_lutador=6.0, minha_ult=4.0, minha_ult2=4.0, meu_cenario=5.0)

SLOTS = ("lutador", "ult", "ult2", "casa", "passiva", "brilhante")
NOME_SLOT = dict(lutador="LUTADOR", ult="ULTIMATE", ult2="2ª ULTIMATE", casa="CASA", passiva="PASSIVA",
                 brilhante="BRILHANTE", linguada="LINGUADA", investida="INVESTIDA")
SLOTS_RIBBAT = ("lutador", "ult", "linguada", "investida", "casa", "brilhante")
COR_SLOT = dict(lutador=(120, 170, 255), ult=(255, 150, 50), ult2=(255, 215, 60), casa=(110, 210, 120),
                passiva=(190, 130, 255), brilhante=(255, 255, 255), linguada=(240, 110, 150), investida=(240, 110, 150),
                cenario=(110, 210, 120), evento=(240, 130, 30))
POR_PAGINA_CENARIO = 6


# =====================================================================
# o CATÁLOGO (as figurinhas que existem)
# =====================================================================
def _fichas():
    from personagens import PERSONAGENS, SECRETOS
    return [f for f in PERSONAGENS + SECRETOS]


def _ficha(nome):
    return next((f for f in _fichas() if f["nome"] == nome), None)


def slots_de(nome):
    return SLOTS_RIBBAT if nome == "RIBBAT" else SLOTS


def paginas():
    """[(título, tipo, [ids])] na ordem do álbum."""
    import cenarios
    import passe
    pags = []
    for f in _fichas():
        pags.append((f["nome"], "lutador", [f"l:{f['nome']}:{s}" for s in slots_de(f["nome"])]))
    cen = list(cenarios.CENARIOS)
    for i in range(0, len(cen), POR_PAGINA_CENARIO):
        n = i // POR_PAGINA_CENARIO + 1
        pags.append((f"CENÁRIOS {n}", "cenario", [f"c:{c}" for c in cen[i:i + POR_PAGINA_CENARIO]]))
    for ev, p in passe.PASSES.items():
        pags.append((ev, "evento", [f"e:{ev}:{l}" for l in p["paginas"]]))
    return pags


def todas():
    return [i for _, _, ids in paginas() for i in ids]


def info(fid):
    """O que a figurinha mostra: dict(tipo, slot, nome, titulo, sub)."""
    partes = fid.split(":")
    if partes[0] == "l":
        nome, slot = partes[1], partes[2]
        f = _ficha(nome) or {}
        nomes = f.get("nomes", {})
        sub = {"lutador": "", "ult": nomes.get("Z", ""), "ult2": nomes.get("Z2", ""),
               "casa": f.get("cenario", ""), "passiva": _nome_passiva(f), "brilhante": "RARA!",
               "linguada": nomes.get("E", ""), "investida": nomes.get("SHIFT", "")}.get(slot, "")
        return dict(tipo="lutador", slot=slot, nome=nome, titulo=NOME_SLOT[slot], sub=_limpa(sub))
    if partes[0] == "c":
        return dict(tipo="cenario", slot="cenario", nome=partes[1], titulo="CENÁRIO", sub=partes[1])
    return dict(tipo="evento", slot="evento", nome=partes[2], titulo=partes[1], sub=partes[2])


def _limpa(txt):
    txt = txt.split(" (")[0]
    return txt


def _nome_passiva(f):
    import habilidades
    ops = f.get("habilidades_opcoes") or ((f.get("habilidade"),) if f.get("habilidade") else ())
    return " / ".join(habilidades.HABILIDADES[h]["nome"] for h in ops if h in habilidades.HABILIDADES)


# =====================================================================
# o ESTADO (no save)
# =====================================================================
def _estado():
    s = save.d().get("album")
    if not isinstance(s, dict):
        s = {}
        save.d()["album"] = s
    if not isinstance(s.get("tem"), list):
        s["tem"] = []
    if not isinstance(s.get("repetidas"), int):
        s["repetidas"] = 0
    return s


def tem(fid):
    return fid in _estado()["tem"]


def quantas():
    validas = set(todas())
    return len([i for i in _estado()["tem"] if i in validas]), len(validas)


def pagina_completa(ids):
    return all(tem(i) for i in ids)


def holograficas():
    """Os lutadores com a página completa (= skin HOLOGRÁFICA liberada)."""
    return [t for t, tipo, ids in paginas() if tipo == "lutador" and pagina_completa(ids)]


def _dar(fid):
    """Entrega uma figurinha. Devolve o 'ganho'."""
    s = _estado()
    g = dict(id=fid, nova=not tem(fid), moedas=0, completou=None)
    if g["nova"]:
        s["tem"].append(fid)
        for t, tipo, ids in paginas():
            if fid in ids and pagina_completa(ids):
                g["completou"] = (t, tipo)
    else:
        s["repetidas"] += 1
        g["moedas"] = MOEDAS_REPETIDA
        save.ganhar(MOEDAS_REPETIDA)
    save.salvar()
    return g


def ganhar_evento(evento, lutador):
    return _dar(f"e:{evento}:{lutador}")


def pesos_da_luta(r):
    """O peso de cada figurinha que pode sair dessa luta (r = partida.resumo()). As de evento não saem aqui."""
    eu = r.get("personagem")
    cen = r.get("cenario")
    out = {}
    for t, tipo, ids in paginas():
        if tipo == "evento":
            continue
        for fid in ids:
            i = info(fid)
            w = PESO["brilhante"] if i["slot"] == "brilhante" else PESO["base"]
            if tipo == "lutador" and i["nome"] == eu:
                w *= PESO["meu_lutador"] * (PESO["brilhante_meu"] if i["slot"] == "brilhante" else 1)
                if i["slot"] == "ult" and r.get("ults", 0) > 0:
                    w *= PESO["minha_ult"]
                if i["slot"] == "ult2" and r.get("ults2", 0) > 0:
                    w *= PESO["minha_ult2"]
                if i["slot"] == "casa" and cen == _ficha(eu).get("cenario"):
                    w *= PESO["meu_cenario"]
            if tipo == "cenario" and i["nome"] == cen:
                w *= PESO["meu_cenario"]
            out[fid] = w
    return out


def sortear_resumo(r, rng=None):
    """(O sorteio a partir do resumo: separado pra dar pra testar.)"""
    rng = rng or random.Random()  # (random só dele: não mexe no random da luta)
    if rng.random() >= (CHANCE_VITORIA if r.get("venceu") else CHANCE_DERROTA):
        return None
    pesos = pesos_da_luta(r)
    ids = list(pesos)
    fid = rng.choices(ids, weights=[pesos[i] for i in ids])[0]
    return _dar(fid)


def sortear_da_luta(partida, rng=None):
    """Fim da luta: talvez ganha uma figurinha. Devolve o ganho (dict: id, nova, moedas, completou) ou None."""
    import estatisticas
    if not estatisticas.conta(partida):
        return None
    return sortear_resumo(partida.resumo(), rng)


# =====================================================================
# o DESENHO das figurinhas (só desenho)
# =====================================================================
_cache = {}


def _retrato(nome, tam):
    k = ("r", nome, tam)
    if k not in _cache:
        from selecao import retrato
        f = _ficha(nome)
        _cache[k] = pygame.transform.smoothscale(retrato(f), (tam, tam)) if f else None
    return _cache[k]


def _cenario(nome, w, h):
    k = ("c", nome, w, h)
    if k not in _cache:
        import cenarios
        try:
            fundo = cenarios.cenario(nome).fundo
            fw, fh = fundo.get_size()
            corte = pygame.Rect(0, 0, int(fh * w / h), fh)
            corte.centerx = fw // 2
            _cache[k] = pygame.transform.smoothscale(fundo.subsurface(corte.clip(fundo.get_rect())), (w, h))
        except Exception:
            _cache[k] = None
    return _cache[k]


def _arco_iris(t, k=0.0):
    a = t * 0.05 + k
    return (int(160 + 95 * math.sin(a)), int(160 + 95 * math.sin(a + 2.1)), int(160 + 95 * math.sin(a + 4.2)))


def _raios(tela, cx, cy, r, cor, t, n=10):
    for i in range(n):
        a = i * 2 * math.pi / n + t * 0.02
        p1 = (cx + math.cos(a - 0.12) * r, cy + math.sin(a - 0.12) * r)
        p2 = (cx + math.cos(a + 0.12) * r, cy + math.sin(a + 0.12) * r)
        pygame.draw.polygon(tela, cor, [(cx, cy), p1, p2])


def _icone_passiva(tela, cx, cy, r, cor):
    """Um escudo com uma estrela (a passiva)."""
    pts = [(cx - r, cy - r * 0.8), (cx + r, cy - r * 0.8), (cx + r * 0.85, cy + r * 0.2), (cx, cy + r * 1.05),
           (cx - r * 0.85, cy + r * 0.2)]
    pygame.draw.polygon(tela, (40, 30, 60), pts)
    pygame.draw.polygon(tela, cor, pts, 3)
    est = [(cx + math.cos(-math.pi / 2 + i * math.pi / 5) * (r * 0.55 if i % 2 == 0 else r * 0.24),
            cy - r * 0.05 + math.sin(-math.pi / 2 + i * math.pi / 5) * (r * 0.55 if i % 2 == 0 else r * 0.24))
           for i in range(10)]
    pygame.draw.polygon(tela, cor, est)


def desenhar_figurinha(tela, fid, rect, t=0, tem_=True, destaque=False):
    """Desenha a figurinha (ou o espaço vazio dela, com o número) dentro do rect."""
    r = pygame.Rect(rect)
    i = info(fid)
    cor = COR_SLOT.get(i["slot"], (200, 200, 200))
    if not tem_:
        pygame.draw.rect(tela, (24, 22, 36), r, border_radius=8)
        pygame.draw.rect(tela, (255, 220, 70) if destaque else (70, 64, 92), r, 2, border_radius=8)
        n = todas().index(fid) + 1
        texto(tela, str(n), max(14, r.w // 5), (80, 74, 104), (r.centerx, r.centery - 8), sombra=False)
        texto(tela, i["titulo"], max(9, r.w // 11), (110, 104, 132), (r.centerx, r.bottom - 14), sombra=False)
        return
    brilha = i["slot"] == "brilhante"
    if brilha:
        cor = _arco_iris(t)
    pygame.draw.rect(tela, (245, 240, 228), r, border_radius=8)
    pygame.draw.rect(tela, cor, r, 4 if not destaque else 5, border_radius=8)
    # a janela da imagem
    jan = pygame.Rect(r.x + 6, r.y + 6, r.w - 12, r.h - 40)
    img = None
    pygame.draw.rect(tela, (40, 34, 60), jan)
    if i["tipo"] == "lutador":
        if i["slot"] == "casa":
            img = _cenario(_ficha(i["nome"]).get("cenario", "TEMPLO"), jan.w, jan.h)
            if img:
                tela.blit(img, jan)
            mini = _retrato(i["nome"], jan.w // 2)
            if mini:
                tela.blit(mini, (jan.right - mini.get_width() - 2, jan.bottom - mini.get_height() - 2))
        elif i["slot"] == "passiva":
            f = _ficha(i["nome"])
            pygame.draw.rect(tela, tuple(max(0, c // 3) for c in f.get("cor_poder", cor)) if f else (40, 30, 60), jan)
            _icone_passiva(tela, jan.centerx, jan.centery, min(jan.w, jan.h) * 0.32, cor)
        else:
            f = _ficha(i["nome"]) or {}
            if i["slot"] in ("ult", "ult2", "linguada", "investida"):
                pc = f.get("cor_poder", cor)
                pygame.draw.rect(tela, tuple(c // 3 for c in pc), jan)
                tela.set_clip(jan)
                _raios(tela, jan.centerx, jan.centery, jan.w, pc if i["slot"] != "ult2" else (255, 215, 60), t)
                tela.set_clip(None)
            elif brilha:
                pygame.draw.rect(tela, _arco_iris(t, 2.0), jan)
            img = _retrato(i["nome"], min(jan.w, jan.h))
            if img:
                tela.blit(img, img.get_rect(center=jan.center), special_flags=0) if i["slot"] in ("lutador", "brilhante") \
                    else _blit_recortado(tela, img, jan)
    elif i["tipo"] == "cenario":
        img = _cenario(i["nome"], jan.w, jan.h)
        if img:
            tela.blit(img, jan)
    else:  # evento
        pygame.draw.rect(tela, (60, 24, 40), jan)
        img = _retrato(i["nome"], min(jan.w, jan.h))
        if img:
            tela.blit(img, img.get_rect(center=jan.center))
        import eventos
        eventos.abobora(tela, jan.right - 12, jan.bottom - 12, max(6, jan.w // 9), t)
    if brilha:  # o brilho passando
        tela.set_clip(jan)
        x = jan.x + (t * 3) % (jan.w * 3) - jan.w
        brilho = pygame.Surface((jan.w // 3, jan.h * 2), pygame.SRCALPHA)
        brilho.fill((255, 255, 255, 55))
        brilho = pygame.transform.rotate(brilho, -25)
        tela.blit(brilho, (x, jan.y - jan.h // 2))
        tela.set_clip(None)
        for k in range(4):
            a = t * 0.08 + k * 1.6
            sx = jan.x + (k * 37 + 11) % jan.w
            sy = jan.y + (k * 23 + 7) % jan.h
            s = 2 + 2 * abs(math.sin(a))
            pygame.draw.line(tela, BRANCO, (sx - s * 2, sy), (sx + s * 2, sy), 2)
            pygame.draw.line(tela, BRANCO, (sx, sy - s * 2), (sx, sy + s * 2), 2)
    pygame.draw.rect(tela, cor, jan, 2)
    # a faixa com o nome
    faixa = pygame.Rect(r.x + 4, r.bottom - 32, r.w - 8, 28)
    pygame.draw.rect(tela, cor, faixa, border_radius=5)
    nome = i["nome"] if i["tipo"] != "cenario" else i["nome"]
    from efeitos import fonte
    tam = next((s for s in (13, 12, 11, 10, 9) if fonte(s).size(nome)[0] <= faixa.w - 6), 9)
    texto(tela, nome, tam, (25, 20, 30), (faixa.centerx, faixa.y + 9), sombra=False)
    sub = i["titulo"] if i["tipo"] != "cenario" else "CENÁRIO"
    if i["tipo"] == "evento":
        sub = i["titulo"].lower()
    texto(tela, sub, 9, (60, 50, 60), (faixa.centerx, faixa.y + 21), sombra=False)


def _blit_recortado(tela, img, jan):
    """Retrato menor no canto de baixo (pras figurinhas de golpe: o golpe é o fundo)."""
    peq = pygame.transform.smoothscale(img, (int(jan.w * 0.7), int(jan.w * 0.7)))
    tela.blit(peq, peq.get_rect(midbottom=jan.midbottom))


def desenhar_ganho(tela, ganho, t):
    """A figurinha que saiu na luta, girando e aparecendo (t = quadros desde que apareceu)."""
    if not ganho:
        return
    cx, cy = LARGURA // 2, ALTURA // 2 - 10
    w, h = 150, 200
    k = min(1.0, t / 24)
    larg = max(2, int(w * abs(math.cos((1 - k) * math.pi * 1.5))))  # (vira de lado e aparece)
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    if k < 1 and (1 - k) * 1.5 % 1 > 0.5:
        pygame.draw.rect(sup, (120, 60, 200), (0, 0, w, h), border_radius=8)
        pygame.draw.rect(sup, (255, 220, 70), (0, 0, w, h), 4, border_radius=8)
        texto(sup, "?", 60, (255, 220, 70), (w // 2, h // 2))
    else:
        desenhar_figurinha(sup, ganho["id"], (0, 0, w, h), t)
    if k >= 1:
        _raios(tela, cx, cy, 170, (60, 50, 90), t, 14)
    sup = pygame.transform.smoothscale(sup, (larg, h))
    tela.blit(sup, sup.get_rect(center=(cx, cy)))
    if k >= 1:
        if ganho["nova"]:
            texto_grande(tela, "FIGURINHA NOVA!", 28, (140, 255, 160), (cx, cy - h // 2 - 26))
        else:
            texto_grande(tela, "REPETIDA", 26, (220, 220, 230), (cx, cy - h // 2 - 26))
            texto_moedas(tela, f"+{ganho['moedas']}", cx + 40, cy + h // 2 + 22, t, tam=20)
        if ganho.get("completou"):
            t_, tipo = ganho["completou"]
            txt = f"PÁGINA DO {t_} COMPLETA!" if tipo == "lutador" else f"PÁGINA {t_} COMPLETA!"
            texto_grande(tela, txt, 24, (255, 215, 60), (cx, cy + h // 2 + 26))
            if tipo == "lutador":
                texto(tela, "SKIN HOLOGRÁFICA LIBERADA!", 18, _arco_iris(t), (cx, cy + h // 2 + 54))


# =====================================================================
# a TELA do álbum
# =====================================================================
class TelaAlbum:
    def __init__(self):
        self.pags = paginas()
        self.pag = 0
        self.sel = 0
        self.foco = "figurinhas"   # "figurinhas" ou "voltar"
        self.t = 0
        self.sair = False

    def ids(self):
        return self.pags[self.pag][2]

    def rect_fig(self, i):
        n = len(self.ids())
        col, lin = i % 3, i // 3
        w, h = 124, 162
        x0 = LARGURA // 2 - (3 * (w + 24) - 24) // 2
        linhas = -(-n // 3)
        y0 = 104 if linhas == 2 else 180
        return pygame.Rect(x0 + col * (w + 24), y0 + lin * (h + 10), w, h)

    def rect_seta(self, lado):
        return pygame.Rect((40 if lado < 0 else LARGURA - 90), ALTURA // 2 - 40, 50, 80)

    def rect_voltar(self):
        return pygame.Rect(LARGURA // 2 - 90, ALTURA - 54, 180, 32)

    def virar(self, d):
        self.pag = (self.pag + d) % len(self.pags)
        self.sel = min(self.sel, len(self.ids()) - 1)
        som.tocar("blip")

    def tecla(self, tecla):
        n = len(self.ids())
        if tecla in (pygame.K_q, pygame.K_PAGEUP):
            self.virar(-1)
        elif tecla in (pygame.K_e, pygame.K_PAGEDOWN):
            self.virar(1)
        elif tecla in (pygame.K_a, pygame.K_LEFT):
            if self.foco == "figurinhas" and self.sel % 3 > 0:
                self.sel -= 1
                som.tocar("blip")
            else:
                self.virar(-1)
                self.sel = min(n, len(self.ids())) - 1 if self.foco == "figurinhas" else self.sel
        elif tecla in (pygame.K_d, pygame.K_RIGHT):
            if self.foco == "figurinhas" and self.sel % 3 < 2 and self.sel + 1 < n:
                self.sel += 1
                som.tocar("blip")
            else:
                self.virar(1)
                self.sel = 0
        elif tecla in (pygame.K_w, pygame.K_UP):
            if self.foco == "voltar":
                self.foco = "figurinhas"
            elif self.sel >= 3:
                self.sel -= 3
            som.tocar("blip")
        elif tecla in (pygame.K_s, pygame.K_DOWN):
            if self.foco == "figurinhas" and self.sel + 3 < n:
                self.sel += 3
            else:
                self.foco = "voltar"
            som.tocar("blip")
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE):
            if self.foco == "voltar":
                self.sair = True
            else:
                self.virar(1)

    def mouse(self, pos, clicou):
        for i in range(len(self.ids())):
            if self.rect_fig(i).collidepoint(pos):
                self.foco, self.sel = "figurinhas", i
                return
        for d in (-1, 1):
            if self.rect_seta(d).collidepoint(pos):
                if clicou:
                    self.virar(d)
                return
        if self.rect_voltar().collidepoint(pos):
            self.foco = "voltar"
            if clicou:
                self.sair = True

    def desenhar(self, tela):
        from selecao import fundo_selecao
        self.t += 1
        tela.blit(fundo_selecao(self.t), (0, 0))
        titulo, tipo, ids = self.pags[self.pag]
        tem_n, total = quantas()
        texto_grande(tela, "ÁLBUM", 36, (255, 220, 70), (LARGURA // 2, 30))
        texto(tela, f"{tem_n} de {total} figurinhas", 15, (210, 210, 230), (110, 24))
        texto_moedas(tela, save.d().get("moedas", 0), LARGURA - 20, 24, self.t)
        completa = pagina_completa(ids)
        nome_pag = titulo if tipo != "evento" else f"EVENTO: {titulo}"
        cor_t = _arco_iris(self.t) if completa and tipo == "lutador" else (255, 225, 150) if completa else BRANCO
        texto(tela, nome_pag, 22, cor_t, (LARGURA // 2, 70))
        texto(tela, f"página {self.pag + 1}/{len(self.pags)}", 12, (170, 170, 195), (LARGURA // 2, 90))
        for i, fid in enumerate(ids):
            r = self.rect_fig(i)
            sel = self.foco == "figurinhas" and i == self.sel
            if sel:
                r = r.move(0, -4)
            desenhar_figurinha(tela, fid, r, self.t + i * 11, tem(fid), sel)
        for d in (-1, 1):  # as setas de virar a página
            r = self.rect_seta(d)
            pts = [(r.right, r.y), (r.x, r.centery), (r.right, r.bottom)] if d < 0 else \
                  [(r.x, r.y), (r.right, r.centery), (r.x, r.bottom)]
            pygame.draw.polygon(tela, (70, 60, 110), pts)
            pygame.draw.polygon(tela, (200, 180, 255), pts, 3)
        # rodapé da página: a dica / o prêmio
        if self.foco == "figurinhas" and self.sel < len(ids):
            fid = ids[self.sel]
            i = info(fid)
            if tem(fid):
                linha = f"{i['titulo']}: {i['sub']}" if i["sub"] and i["sub"] != i["nome"] else i["titulo"]
            elif i["tipo"] == "evento":
                linha = f"só sai no PASSE DO {i['titulo']}"
            elif i["tipo"] == "cenario":
                linha = f"lutar no {i['nome']} aumenta a chance"
            elif i["slot"] == "brilhante":
                linha = f"RARA! jogar com o {i['nome']} aumenta a chance"
            elif i["slot"] == "ult":
                linha = f"acertar a ULTIMATE com o {i['nome']} aumenta a chance"
            elif i["slot"] == "ult2":
                linha = f"acertar a 2ª ULTIMATE com o {i['nome']} aumenta a chance"
            elif i["slot"] == "casa":
                linha = f"lutar no {_ficha(i['nome']).get('cenario', '')} com o {i['nome']} aumenta a chance"
            else:
                linha = f"jogar com o {i['nome']} aumenta a chance"
            texto(tela, linha, 15, (220, 215, 235), (LARGURA // 2, 452 if len(ids) > 3 else 400))
        if tipo == "lutador":
            if completa:
                texto(tela, "COMPLETA!  SKIN HOLOGRÁFICA LIBERADA", 16, _arco_iris(self.t), (LARGURA // 2, 474))
            else:
                texto(tela, "complete a página: SKIN HOLOGRÁFICA", 13, (180, 170, 210), (LARGURA // 2, 474))
        r = self.rect_voltar()
        sel = self.foco == "voltar"
        pygame.draw.rect(tela, (54, 46, 84) if sel else (26, 22, 42), r, border_radius=10)
        pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), r, 3, border_radius=10)
        texto(tela, "VOLTAR", 18, (255, 220, 70) if sel else BRANCO, r.center)
        texto(tela, "Q/E ou setas: vira a página   WASD escolhe   ESC volta", 12, (170, 170, 195),
              (LARGURA // 2, ALTURA - 11))
