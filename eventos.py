"""EVENTOS AUTOMÁTICOS (v2.x, pedido do Gomes): o jogo olha a DATA DO COMPUTADOR e liga o evento sozinho,
todo ano, sem ninguém precisar lembrar.

  HALLOWEEN                 28/10 a 04/11
  ANIVERSÁRIO (do jogo)     15/10 a 18/10   (o Battle Wish nasceu em 15/10/2026)
  NATAL                     20/12 a 05/01   (atravessa a virada do ano)
  CARNAVAL                  sábado a quarta-feira de cinzas (calculado pela Páscoa)
  PÁSCOA                    sexta-feira santa a segunda depois da Páscoa (calculada)
  FESTA JUNINA              o mês de junho inteiro
  DIA DAS CRIANÇAS          10/10 a 14/10

Por enquanto só o HALLOWEEN tem conteúdo (enfeites, doces, tela inicial). Os outros já são reconhecidos.

DOCES 🍬 (moeda do Halloween): vitória +3, derrota +1 (só luta de gente, igual às estatísticas).
As skins do evento custam doces. Quando o evento acaba, o que sobrou vira moeda (1 doce = 5 moedas).
O desenho (enfeites e tela inicial) é SÓ desenho: depende do t, não muda nada da luta (dá igual no online).
"""
import datetime
import math

import pygame

import save
from config import *  # noqa: F401,F403

HALLOWEEN, ANIVERSARIO, NATAL, CARNAVAL, PASCOA, JUNINA, CRIANCAS = (
    "HALLOWEEN", "ANIVERSÁRIO", "NATAL", "CARNAVAL", "PÁSCOA", "FESTA JUNINA", "DIA DAS CRIANÇAS")
COM_CONTEUDO = (HALLOWEEN,)  # (os outros entram nos próximos anos)

DOCES_VITORIA, DOCES_DERROTA = 3, 1
PRECO_SKIN = 12
MOEDAS_POR_DOCE = 5


# =====================================================================
# o CALENDÁRIO
# =====================================================================
import os


def hoje():
    """A data de hoje. (Pra testar um evento antes da hora: a variável BW_DATA=2026-12-24 finge outra data.)"""
    v = os.environ.get("BW_DATA")
    if v:
        try:
            return datetime.date.fromisoformat(v)
        except ValueError:
            pass
    return datetime.date.today()

def pascoa(ano):
    """Domingo de Páscoa (o cálculo de sempre do calendário gregoriano)."""
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return datetime.date(ano, mes, dia)


def periodos(ano):
    """[(evento, começo, fim)] daquele ano (o NATAL que começa no ano anterior também entra)."""
    p = pascoa(ano)
    d = datetime.date
    return [
        (NATAL, d(ano - 1, 12, 20), d(ano, 1, 5)),
        (CARNAVAL, p - datetime.timedelta(days=50), p - datetime.timedelta(days=46)),
        (PASCOA, p - datetime.timedelta(days=2), p + datetime.timedelta(days=1)),
        (JUNINA, d(ano, 6, 1), d(ano, 6, 30)),
        (CRIANCAS, d(ano, 10, 10), d(ano, 10, 14)),
        (ANIVERSARIO, d(ano, 10, 15), d(ano, 10, 18)),
        (HALLOWEEN, d(ano, 10, 28), d(ano, 11, 4)),
        (NATAL, d(ano, 12, 20), d(ano + 1, 1, 5)),
    ]


def evento_atual(data=None):
    """O evento de hoje (ou da data pedida), ou None."""
    data = data or hoje()
    for nome, ini, fim in periodos(data.year):
        if ini <= data <= fim:
            return nome
    return None


def tem_conteudo(data=None):
    """O evento de hoje, se ele já tem coisa no jogo (enfeite, doce, skin). Senão None."""
    e = evento_atual(data)
    return e if e in COM_CONTEUDO else None


def aniversario(data=None):
    """Quantos anos o Battle Wish faz (nesse ano)."""
    data = data or hoje()
    return data.year - 2026


# =====================================================================
# os DOCES (Halloween)
# =====================================================================
def doces():
    v = save.d().get("doces")
    return v if isinstance(v, int) and v > 0 else 0


def _por(n):
    save.d()["doces"] = max(0, n)
    save.d()["doces_ano"] = datetime.date.today().year  # (de qual Halloween são esses doces)


def ganhar_doces(partida, data=None):
    """Fim da luta, durante o HALLOWEEN: +3 se o jogador venceu, +1 se perdeu. Devolve quantos ganhou.
    Só conta luta de gente (a mesma regra das estatísticas: lado 0 humano, sem treino nem assistida)."""
    import estatisticas
    if tem_conteudo(data) != HALLOWEEN or not estatisticas.conta(partida):
        return 0
    n = DOCES_VITORIA if partida.vencedor == 0 else DOCES_DERROTA
    _por(doces() + n)
    save.salvar()
    return n


def gastar(n):
    """Paga n doces (a loja chama na compra da skin). Devolve True se tinha."""
    if doces() < n:
        return False
    _por(doces() - n)
    save.salvar()
    return True


def converter_sobras(data=None):
    """Fora do Halloween, os doces que sobraram viram moedas (chame ao abrir o jogo). Devolve as moedas ganhas."""
    if tem_conteudo(data) == HALLOWEEN or doces() <= 0:
        return 0
    moedas = doces() * MOEDAS_POR_DOCE
    save.d()["moedas"] = save.d().get("moedas", 0) + moedas
    save.d()["doces"] = 0
    save.salvar()
    return moedas


# =====================================================================
# os ENFEITES do Halloween (só desenho, coordenadas da tela grande)
# =====================================================================
LARANJA, LARANJA_ESC = (240, 130, 30), (170, 80, 20)


def abobora(tela, x, y, r, t=0, acesa=True):
    """Uma abóbora de Halloween com carinha (x, y = meio da base)."""
    cy = y - r
    for dx, k in ((-0.55, 0.62), (0.55, 0.62), (0, 0.75)):  # os gomos
        pygame.draw.ellipse(tela, LARANJA_ESC if dx else LARANJA,
                            (x + dx * r - r * k, cy - r * 0.85, r * k * 2, r * 1.7))
    pygame.draw.ellipse(tela, (60, 30, 10), (x - r * 1.05, cy - r * 0.88, r * 2.1, r * 1.76), 2)
    pygame.draw.rect(tela, (70, 110, 40), (x - r * 0.12, cy - r * 1.15, r * 0.24, r * 0.35))  # cabinho
    luz = (255, 230, 90) if acesa and (t // 7) % 9 else (255, 190, 60)  # (a vela tremeluz)
    for lado in (-1, 1):  # olhos triangulares
        pygame.draw.polygon(tela, luz, [(x + lado * r * 0.45, cy - r * 0.35), (x + lado * r * 0.2, cy + r * 0.05),
                                        (x + lado * r * 0.7, cy + r * 0.05)])
    boca = [(x - r * 0.6, cy + r * 0.3), (x - r * 0.3, cy + r * 0.45), (x - r * 0.1, cy + r * 0.3),
            (x + r * 0.1, cy + r * 0.45), (x + r * 0.3, cy + r * 0.3), (x + r * 0.6, cy + r * 0.3),
            (x + r * 0.3, cy + r * 0.62), (x - r * 0.3, cy + r * 0.62)]
    pygame.draw.polygon(tela, luz, boca)


def teia(tela, canto, tam, cor=(225, 225, 235)):
    """Teia de aranha num canto da tela ('esq' ou 'dir')."""
    x0 = 0 if canto == "esq" else LARGURA
    sx = 1 if canto == "esq" else -1
    raios = [math.radians(a) for a in (0, 22, 45, 68, 90)]
    for a in raios:
        pygame.draw.line(tela, cor, (x0, 0), (x0 + sx * math.cos(a) * tam, math.sin(a) * tam), 1)
    for k in range(1, 5):
        r = tam * k / 5
        pts = [(x0 + sx * math.cos(a) * r, math.sin(a) * r) for a in raios]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):  # fios caídos entre os raios
            mx, my = (ax + bx) / 2, (ay + by) / 2
            pygame.draw.lines(tela, cor, False, [(ax, ay), (mx - sx * 3, my + 4), (bx, by)], 1)


def morcego(tela, x, y, t, tam=1.0, cor=(25, 15, 30)):
    bate = math.sin(t * 0.5) * 8 * tam
    pygame.draw.ellipse(tela, cor, (x - 5 * tam, y - 4 * tam, 10 * tam, 9 * tam))
    for lado in (-1, 1):
        pygame.draw.polygon(tela, cor, [(x, y), (x + lado * 9 * tam, y - 6 * tam - bate),
                                        (x + lado * 18 * tam, y - 2 * tam - bate), (x + lado * 13 * tam, y + 2 * tam),
                                        (x + lado * 7 * tam, y + 1 * tam)])
    pygame.draw.polygon(tela, cor, [(x - 4 * tam, y - 3 * tam), (x - 3 * tam, y - 8 * tam), (x - 1 * tam, y - 4 * tam)])
    pygame.draw.polygon(tela, cor, [(x + 4 * tam, y - 3 * tam), (x + 3 * tam, y - 8 * tam), (x + 1 * tam, y - 4 * tam)])


def fantasminha(tela, x, y, t, alfa=150):
    s = pygame.Surface((44, 54), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (240, 245, 255, alfa), (2, 0, 40, 40))
    pygame.draw.rect(s, (240, 245, 255, alfa), (2, 20, 40, 22))
    for k in range(4):  # a barra ondulada embaixo
        pygame.draw.circle(s, (240, 245, 255, alfa), (7 + k * 10, 42 + (2 if (k + t // 8) % 2 else -1)), 6)
    pygame.draw.ellipse(s, (30, 20, 40, alfa), (12, 14, 7, 10))
    pygame.draw.ellipse(s, (30, 20, 40, alfa), (25, 14, 7, 10))
    pygame.draw.ellipse(s, (30, 20, 40, alfa), (18, 27, 8, 6))
    tela.blit(s, (x - 22, y - 27))


def lua_laranja(tela, x, y, r, t):
    brilho = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
    for k in range(5, 0, -1):
        pygame.draw.circle(brilho, (255, 150, 50, 12 * k), (r * 3, r * 3), int(r * (1 + k * 0.35)))
    tela.blit(brilho, (x - r * 3, y - r * 3))
    pygame.draw.circle(tela, (255, 170, 70), (x, y), r)
    pygame.draw.circle(tela, (235, 140, 50), (x - r // 3, y - r // 4), r // 4)  # crateras
    pygame.draw.circle(tela, (235, 140, 50), (x + r // 3, y + r // 3), r // 5)


def neblina(tela, t, y0, alfa=70):
    nevoa = pygame.Surface((LARGURA, 90), pygame.SRCALPHA)
    for k in range(7):
        x = (k * 170 + t * (0.4 + 0.15 * (k % 3))) % (LARGURA + 300) - 150
        pygame.draw.ellipse(nevoa, (200, 210, 230, alfa), (x, 20 + (k % 3) * 14, 300, 50))
    tela.blit(nevoa, (0, y0))


class Enfeites:
    """Os enfeites do evento na LUTA. A partida chama: desenhar_fundo(camada, t) logo depois do fundo
    (atrás dos lutadores) e desenhar_frente(tela, t) depois dos lutadores (morcegos, neblina, fantasminhas)."""

    def __init__(self, evento):
        self.evento = evento

    def desenhar_fundo(self, tela, t):
        if self.evento != HALLOWEEN:
            return
        # (sem lua laranja na luta: o cenário já tem o sol/a lua dele; a lua fica só na tela inicial)
        teia(tela, "esq", 120)
        teia(tela, "dir", 95)
        for x, r in ((68, 24), (112, 16), (470, 18), (895, 22)):  # abóboras no chão (longe dos objetos: 180 e 790)
            abobora(tela, x, CHAO + 2, r, t + x)

    def desenhar_frente(self, tela, t):
        if self.evento != HALLOWEEN:
            return
        for k in range(4):  # morcegos atravessando o céu
            u = (t * (1.3 + 0.3 * k) + k * 260) % (LARGURA + 200) - 100
            x = u if k % 2 else LARGURA - u
            morcego(tela, x, 70 + k * 38 + math.sin(t * 0.05 + k) * 18, t + k * 5, 0.9 + 0.2 * (k % 2))
        if (t // 300) % 2 == 0:  # de vez em quando um fantasminha passa flutuando
            u = (t % 300) / 300
            fantasminha(tela, 60 + u * (LARGURA - 120), 200 + math.sin(t * 0.04) * 30, t,
                        int(150 * math.sin(u * math.pi)))
        neblina(tela, t, CHAO - 60)


def criar(data=None):
    """Os enfeites do evento de hoje pra luta (ou None, se não tem evento com conteúdo)."""
    e = tem_conteudo(data)
    return Enfeites(e) if e else None


def desenhar_menu(tela, t, data=None):
    """O FUNDO DA TELA INICIAL no evento (Halloween: abóboras, teias e a aranhinha passando).
    Devolve True se desenhou (aí o menu não precisa do fundo normal)."""
    if tem_conteudo(data) != HALLOWEEN:
        return False
    for y in range(0, ALTURA, 4):  # céu roxo escuro
        k = y / ALTURA
        tela.fill((int(30 + 30 * k), int(14 + 10 * k), int(44 + 20 * k)), (0, y, LARGURA, 4))
    lua_laranja(tela, LARGURA - 150, 110, 52, t)
    pygame.draw.polygon(tela, (20, 10, 26), [(0, ALTURA), (0, ALTURA - 90), (180, ALTURA - 120), (360, ALTURA - 95),
                                             (560, ALTURA - 130), (760, ALTURA - 100), (LARGURA, ALTURA - 125),
                                             (LARGURA, ALTURA)])  # morros
    teia(tela, "esq", 170)
    teia(tela, "dir", 140)
    for x, r in ((80, 26), (150, 18), (LARGURA - 90, 30), (LARGURA - 170, 20), (LARGURA // 2 + 250, 16)):
        abobora(tela, x, ALTURA - 20, r, t + x)
    for k in range(3):
        u = (t * (1.1 + 0.4 * k) + k * 330) % (LARGURA + 200) - 100
        morcego(tela, u if k % 2 else LARGURA - u, 70 + k * 50 + math.sin(t * 0.05 + k) * 14, t + k * 7, 1.1)
    # a ARANHINHA: desce do canto pelo fio, fica balançando, sobe de novo... e às vezes atravessa a tela
    ciclo = t % 720
    if ciclo < 480:
        x = 120 + math.sin(t * 0.03) * 8
        y = 20 + 140 * math.sin(min(1.0, ciclo / 120) * math.pi / 2) - (140 * max(0.0, (ciclo - 360) / 120))
        pygame.draw.line(tela, (220, 220, 230), (120, 0), (x, y), 1)
    else:  # andando pelo topo da tela, da esquerda pra direita
        x = 120 + (ciclo - 480) / 240 * (LARGURA - 240)
        y = 22
    aranha(tela, x, y, t)
    neblina(tela, t, ALTURA - 110, 60)
    return True


def aranha(tela, x, y, t, e=1.8):
    """A aranhinha (e = tamanho)."""
    perna = math.sin(t * 0.4) * 2 * e
    for lado in (-1, 1):
        for k in range(4):
            a = lado * (0.5 + k * 0.35)
            pygame.draw.line(tela, (20, 15, 20), (x, y), (x + lado * (9 + k * 2) * e, y + (-4 + k * 4) * e + perna * (1 if k % 2 else -1)), 2)
    pygame.draw.circle(tela, (25, 18, 28), (int(x), int(y)), int(6 * e))
    pygame.draw.circle(tela, (25, 18, 28), (int(x), int(y + 6 * e)), int(4 * e))
    pygame.draw.circle(tela, (230, 60, 60), (int(x - 2 * e), int(y + 6 * e)), max(1, int(e)))  # olhinhos
    pygame.draw.circle(tela, (230, 60, 60), (int(x + 2 * e), int(y + 6 * e)), max(1, int(e)))
