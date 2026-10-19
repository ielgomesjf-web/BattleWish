"""MAESTRIA: cada lutador sobe do nível 1 ao 10 quanto mais você joga com ele (v2.0, pedido do Gomes).
Cada nível dá um prêmio visual: título embaixo do nome, moldura do retrato (bronze, prata, ouro, brilhante)
e, no nível 10, o título de MESTRE e o brilho dourado na pose de vitória.

Fica no save: save.d()["maestria"] = {nome do lutador: xp total}.
Só conta luta de gente (1 jogador, 2 jogadores, trio, torneio, sobrevivência, online). Treino e combos não contam.
"""
import math

import pygame

import save

NIVEL_MAX = 10
# xp TOTAL pra chegar em cada nível (nível 1 = começo). Uma luta boa dá uns 80-120 pontos:
# nível 5 em umas 7 lutas, nível 10 em umas 25.
XP_NIVEL = [0, 80, 200, 360, 560, 800, 1100, 1450, 1850, 2300]

# pontos da luta
PONTOS_LUTOU = 20         # só de lutar até o fim
PONTOS_VITORIA = 40
PONTOS_ROUND = 10         # por round vencido
PONTOS_PERFECT = 15       # por round sem perder vida
PONTOS_VIDA = 10          # +1 a cada 10 de vida que sobrou (só quem venceu)
PONTOS_COMBO_MAX = 20     # o maior combo vale 1 ponto por golpe, até 20
PONTOS_ULT = 10           # acertou a ultimate

BRONZE = (205, 127, 50)
PRATA = (205, 212, 225)
OURO = (255, 200, 40)
BRILHANTE = (140, 245, 255)

# o prêmio de cada nível (o que aparece no fim da luta: "NÍVEL 4! ganhou: ...")
PREMIOS = {
    1: "",
    2: "título APRENDIZ",
    3: "moldura de BRONZE",
    4: "título LUTADOR",
    5: "moldura de PRATA",
    6: "título VETERANO",
    7: "moldura de OURO",
    8: "título CAMPEÃO",
    9: "moldura BRILHANTE",
    10: "título de MESTRE + brilho na vitória",
}
TITULOS = {2: "APRENDIZ", 4: "LUTADOR", 6: "VETERANO", 8: "CAMPEÃO"}
MOLDURAS = {3: BRONZE, 5: PRATA, 7: OURO, 9: BRILHANTE}

# o título de nível 10, de cada um
MESTRES = {
    "MAX-10": "MESTRE DO LASER",
    "RIB": "MESTRE NINJA",
    "TRAFO": "MESTRE DA MUTAÇÃO",
    "KING RIP": "MESTRE DO NUNCHAKU",
    "CANNAN": "MESTRE DO CANHÃO",
    "FINN": "MESTRE DA MAGIA",
    "KUN": "MESTRE DAS CARTAS",
    "TROMOS": "MESTRE DO ÁCIDO",
    "TAI": "MESTRE DO SUMÔ",
    "TAMER": "MESTRE DA MATILHA",
    "RIBBAT": "MESTRE SAPO",
    "JOHN": "GRANDE ILUSIONISTA",
    "MAGNUS": "PREDADOR DE FOGO",
    "SPHYRUS": "REI DAS PROFUNDEZAS",
    "FRIGANTUS": "FERA DAS NEVES",
    "CRÁQUEN": "TERROR DOS SETE MARES",
}


def _nome(nome):
    """Aceita o nome ou a ficha inteira (roupa e Sombra contam pro lutador de verdade)."""
    if isinstance(nome, dict):
        nome = nome.get("nome_base", nome.get("nome", ""))
    if nome.startswith("SOMBRA DO "):
        nome = nome[len("SOMBRA DO "):]
    return nome


def _tabela():
    t = save.d().setdefault("maestria", {})
    if not isinstance(t, dict):
        t = save.d()["maestria"] = {}
    return t


def xp(nome):
    v = _tabela().get(_nome(nome), 0)
    return v if isinstance(v, (int, float)) and v > 0 else 0


def nivel_do_xp(total):
    n = 1
    for i, precisa in enumerate(XP_NIVEL):
        if total >= precisa:
            n = i + 1
    return min(n, NIVEL_MAX)


def nivel(nome):
    return nivel_do_xp(xp(nome))


def progresso(nome):
    """(nível, xp dentro do nível, xp que falta juntar pro próximo). No nível 10: (10, 0, 0)."""
    total = xp(nome)
    n = nivel_do_xp(total)
    if n >= NIVEL_MAX:
        return n, 0, 0
    return n, int(total - XP_NIVEL[n - 1]), XP_NIVEL[n] - XP_NIVEL[n - 1]


def ganhar(nome, pontos):
    """Soma os pontos e salva. Devolve (nível antes, nível depois)."""
    nome = _nome(nome)
    antes = nivel(nome)
    pontos = max(0, int(pontos))
    if pontos:
        _tabela()[nome] = xp(nome) + pontos
        save.salvar()
    return antes, nivel(nome)


def pontos_da_luta(partida, lado):
    """Quantos pontos de maestria o lutador do lado (0 = esquerda, 1 = direita) ganhou nessa partida.
    (A partida só guarda perfect, combo e ultimate do lado 0; o lado 1 ganha pela vitória, rounds e vida.)"""
    if partida.treino or partida.vencedor is None:
        return 0
    pts = PONTOS_LUTOU
    if partida.vencedor == lado:
        pts += PONTOS_VITORIA
        vida = partida.vida_lado(lado) if hasattr(partida, "vida_lado") else partida.L[lado].vida
        pts += int(max(0, vida) // PONTOS_VIDA)
    pts += PONTOS_ROUND * partida.vitorias[lado]
    if lado == 0:
        pts += PONTOS_PERFECT * partida.perfects
        pts += min(PONTOS_COMBO_MAX, partida.combo_max)
        if partida.stats.get("ults"):
            pts += PONTOS_ULT
    return pts


def premio_do_nivel(n):
    return PREMIOS.get(n, "")


def titulo(nome):
    """O título que aparece embaixo do nome (ou "" no nível 1)."""
    n = nivel(nome)
    if n >= NIVEL_MAX:
        return MESTRES.get(_nome(nome), "MESTRE")
    melhor = ""
    for k, t in TITULOS.items():
        if n >= k:
            melhor = t
    return melhor


def moldura(nome):
    """A cor da moldura do retrato (ou None antes do nível 3)."""
    n = nivel(nome)
    cor = None
    for k, c in MOLDURAS.items():
        if n >= k:
            cor = c
    return cor


def brilho_na_vitoria(nome):
    """Nível 10: brilho dourado em volta na pose de vitória."""
    return nivel(nome) >= NIVEL_MAX


def _arco_iris(t, k=0.0):
    a = t * 0.06 + k
    return (int(150 + 100 * math.sin(a)), int(150 + 100 * math.sin(a + 2.1)), int(150 + 100 * math.sin(a + 4.2)))


def desenhar_moldura(tela, rect, nome, t):
    """Desenha a moldura em volta do retrato (rect). Nível 9+: brilhante, com as cores andando e um brilho correndo."""
    cor = moldura(nome)
    if cor is None:
        return
    r = pygame.Rect(rect).inflate(6, 6)
    if cor != BRILHANTE:
        pygame.draw.rect(tela, tuple(c // 2 for c in cor), r.inflate(2, 2), 2, border_radius=5)
        pygame.draw.rect(tela, cor, r, 3, border_radius=4)
        if cor == OURO:  # o ouro tem um brilhinho piscando no canto
            if (t // 20) % 3 == 0:
                pygame.draw.circle(tela, (255, 255, 230), (r.right - 4, r.y + 4), 3)
        return
    # BRILHANTE: cada lado com uma cor do arco-íris e uma luz branca dando a volta
    lados = [((r.x, r.y), (r.right, r.y)), ((r.right, r.y), (r.right, r.bottom)),
             ((r.right, r.bottom), (r.x, r.bottom)), ((r.x, r.bottom), (r.x, r.y))]
    for i, (a, b) in enumerate(lados):
        pygame.draw.line(tela, _arco_iris(t, i * 1.5), a, b, 4)
    perim = 2 * (r.w + r.h)
    d = (t * 6) % perim
    if d < r.w:
        p = (r.x + d, r.y)
    elif d < r.w + r.h:
        p = (r.right, r.y + d - r.w)
    elif d < 2 * r.w + r.h:
        p = (r.right - (d - r.w - r.h), r.bottom)
    else:
        p = (r.x, r.bottom - (d - 2 * r.w - r.h))
    pygame.draw.circle(tela, (255, 255, 255), (int(p[0]), int(p[1])), 4)


def desenhar_brilho_vitoria(tela, x, chao_y, t, escala=1.0):
    """Nível 10: brilho dourado subindo em volta de quem venceu (x = pés, chao_y = chão)."""
    camada = pygame.Surface((int(200 * escala), int(260 * escala)), pygame.SRCALPHA)
    w, h = camada.get_size()
    pulsa = 0.75 + 0.25 * math.sin(t * 0.12)
    for i in range(3, 0, -1):  # luz dourada no chão, nos pés
        pygame.draw.ellipse(camada, (255, 210, 80, int(45 * (4 - i) * pulsa)),  # (o miolo mais forte)
                            (w / 2 - w * 0.16 * i, h - 14 - 5 * i, w * 0.32 * i, 10 * i + 8))
    # (tudo vem do tempo: o desenho não muda nada da luta)
    for k in range(7):  # riscos de luz subindo
        u = (t * 1.2 + k * 41) % 100 / 100
        px = w / 2 + (k - 3) * w * 0.11
        y1 = h - 10 - u * h * 0.9
        alfa = int(150 * math.sin(u * math.pi))
        pygame.draw.line(camada, (255, 225, 120, alfa), (px, y1), (px, y1 + 26 * escala), max(1, int(2 * escala)))
    for k in range(9):  # estrelinhas de 4 pontas
        u = (t * 1.6 + k * 37) % 100 / 100
        px = w / 2 + math.sin(k * 2.3 + t * 0.05) * w * 0.36
        py = h - 10 - u * (h - 20)
        r = max(2, int(6 * escala * math.sin(u * math.pi)))
        cor = (255, 245, 170, int(255 * math.sin(u * math.pi)))
        pygame.draw.line(camada, cor, (px - r, py), (px + r, py), 2)
        pygame.draw.line(camada, cor, (px, py - r), (px, py + r), 2)
    tela.blit(camada, (x - w / 2, chao_y - h))
