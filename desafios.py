"""DESAFIOS: sempre tem 3 valendo. Cumpriu um, ganha as moedas e aparece outro no lugar.
Valem em qualquer luta contra o computador (Arcade, 1 Jogador e Sobrevivência)."""
import random

import pygame

import save
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande, texto_moedas

ATIVOS = 3

# tipo: (texto, alvos possíveis, moedas do menor alvo, moedas a mais por alvo maior)
TIPOS = {
    "vencer_com": ("Vença {alvo} lutas com o {p}", (2, 3), 40, 15),
    "parrys": ("Faça {alvo} PARRYS", (3, 5), 40, 20),
    "sem_ult": ("Vença uma luta sem tomar ULTIMATE", (1,), 30, 0),
    "quebras": ("Quebre a guarda do adversário {alvo} vezes", (2, 3), 40, 15),
    "combo": ("Faça um combo de {alvo} golpes", (6, 8, 10), 40, 15),
    "dificil": ("Vença {alvo} luta{s} no DIFÍCIL", (1, 2), 60, 40),
    "ults": ("Acerte a ULTIMATE em {alvo} rounds", (2, 3), 40, 15),
    "transicao": ("Jogue o adversário pra outro cenário", (1,), 40, 0),
    "provocar": ("Provoque o adversário {alvo} vezes (tecla T)", (3, 5), 30, 15),
    "sobrev": ("Derrube {alvo} lutadores na SOBREVIVÊNCIA", (3, 5), 50, 30),
    "bom": ("Vença {alvo} luta{s} com PERFECT ou QUASE PERFECT", (1, 2), 50, 30),
}


def texto_de(d):
    return TIPOS[d["tipo"]][0].format(alvo=d["alvo"], p=d.get("p", ""), s="s" if d["alvo"] > 1 else "")


def novo(menos=()):
    """Sorteia um desafio novo (de um tipo que ainda não está valendo)."""
    from personagens import PERSONAGENS
    tipo = random.choice([t for t in TIPOS if t not in menos] or list(TIPOS))
    _, alvos, base, extra = TIPOS[tipo]
    i = random.randrange(len(alvos))
    d = dict(tipo=tipo, alvo=alvos[i], prog=0, premio=base + extra * i)
    if tipo == "vencer_com":
        d["p"] = random.choice(PERSONAGENS)["nome"]
    return d


def ativos():
    lista = save.d().setdefault("desafios", [])
    lista[:] = [d for d in lista if isinstance(d, dict) and d.get("tipo") in TIPOS]
    while len(lista) < ATIVOS:
        lista.append(novo({d["tipo"] for d in lista}))
    return lista


def avancar(d, r):
    """Quanto o desafio andou com essa partida (r = resumo da partida)."""
    t = d["tipo"]
    if t == "vencer_com":
        d["prog"] += r["venceu"] and r["personagem"] == d["p"]
    elif t == "parrys":
        d["prog"] += r["parrys"]
    elif t == "sem_ult":
        d["prog"] += r["venceu"] and not r["tomou_ult"]
    elif t == "quebras":
        d["prog"] += r["quebras"]
    elif t == "combo":
        d["prog"] = max(d["prog"], r["combo"])
    elif t == "dificil":
        d["prog"] += r["venceu"] and r["nivel"] == "DIFÍCIL"
    elif t == "ults":
        d["prog"] += r["ults"]
    elif t == "transicao":
        d["prog"] += r["transicoes"]
    elif t == "provocar":
        d["prog"] += r["provocacoes"]
    elif t == "sobrev":
        d["prog"] = max(d["prog"], r["sobrev"])
    elif t == "bom":
        d["prog"] += r["bom"]
    d["prog"] = int(min(d["prog"], d["alvo"]))


def atualizar(r):
    """Conta o que a partida fez. Devolve os desafios cumpridos: [(texto, moedas), ...]."""
    lista = ativos()
    cumpridos = []
    for i, d in enumerate(lista):
        avancar(d, r)
        if d["prog"] >= d["alvo"]:
            cumpridos.append((texto_de(d), d["premio"]))
            lista[i] = novo({x["tipo"] for x in lista})
            save.d()["desafios_feitos"] = save.d().get("desafios_feitos", 0) + 1
    save.salvar()
    return cumpridos


class TelaDesafios:
    def __init__(self):
        self.t = 0

    def desenhar(self, tela):
        from selecao import fundo_selecao
        self.t += 1
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, "DESAFIOS", 44, (255, 220, 70), (LARGURA // 2, 44))
        texto_moedas(tela, save.moedas(), LARGURA - 24, 36, self.t, 26)
        for i, d in enumerate(ativos()):
            r = pygame.Rect(130, 104 + i * 112, 700, 96)
            pygame.draw.rect(tela, (30, 26, 48), r, border_radius=12)
            pygame.draw.rect(tela, (90, 80, 130), r, 3, border_radius=12)
            img = pygame.font.SysFont("arialblack,arial", 20, bold=True).render(texto_de(d), True, BRANCO)
            tela.blit(img, (r.x + 22, r.y + 14))
            barra = pygame.Rect(r.x + 22, r.y + 56, 460, 22)
            pygame.draw.rect(tela, (16, 12, 26), barra, border_radius=8)
            k = d["prog"] / d["alvo"]
            if k > 0:
                pygame.draw.rect(tela, (120, 210, 255), (barra.x, barra.y, max(12, int(barra.w * k)), barra.h),
                                 border_radius=8)
            pygame.draw.rect(tela, (70, 62, 100), barra, 2, border_radius=8)
            texto(tela, f"{d['prog']} / {d['alvo']}", 14, BRANCO, barra.center)
            texto_moedas(tela, f"+{d['premio']}", r.right - 30, r.y + 66, self.t, 22)
        feitos = save.d().get("desafios_feitos", 0)
        texto(tela, f"desafios cumpridos: {feitos}", 16, (220, 220, 235), (LARGURA // 2, 452))
        texto(tela, "valem no ARCADE, 1 JOGADOR e SOBREVIVÊNCIA (contra o computador)", 14, (255, 220, 120),
              (LARGURA // 2, 480))
        texto(tela, "ESC volta", 14, (200, 200, 220), (LARGURA // 2, ALTURA - 16))
