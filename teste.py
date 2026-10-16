"""Testes: o computador luta contra ele mesmo várias vezes e a gente confere se nada quebra.
Rode: python teste.py   (com --fotos salva umas fotos da luta em ../.tmp)"""
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SEM_SOM", "1")  # os testes rodam mudos
SAVE_TESTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".tmp", "luta_maria_save_teste.json")
os.environ["BW_SAVE"] = SAVE_TESTE  # os testes nunca mexem nas moedas de verdade
if os.path.exists(SAVE_TESTE):
    os.remove(SAVE_TESTE)
import pygame  # noqa: E402

from config import *  # noqa: E402,F401,F403
from controles import Computador, Jogador  # noqa: E402
import roupas as roupas  # noqa: E402
from lutador import Entrada, Lutador  # noqa: E402
from partida import Partida  # noqa: E402
from personagens import BONECO, PERSONAGENS, boneco, sombra  # noqa: E402
from rib import tem_shuriken  # noqa: E402

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
erros = []

import gc  # noqa: E402
_partida_init = Partida.__init__
_criadas = [0]


def _partida_init_limpando(self, *a, **k):
    """Os testes criam centenas de partidas: limpa a memória de vez em quando (senão as imagens acumulam)."""
    _criadas[0] += 1
    if _criadas[0] % 4 == 0:
        gc.collect()
    _partida_init(self, *a, **k)


Partida.__init__ = _partida_init_limpando


def checar(cond, msg):
    print(("ok   " if cond else "ERRO ") + msg)
    if not cond:
        erros.append(msg)


class Roteiro:
    """Controle que aperta uma lista de coisas, um quadro por item."""

    def __init__(self, passos):
        self.passos = list(passos)

    def ler(self, keys, eu, ele, jogo):
        return self.passos.pop(0) if self.passos else Entrada()


def partida_com(r1, r2):
    p = Partida(BONECO, boneco(1), r1, r2)
    p.fase, p.tf = "luta", 0
    return p


def rodar(p, quadros):
    for _ in range(quadros):
        p.passo(None)


# ---- controles novos: mouse + rodinha + teclas ----
class Teclas(dict):
    def __getitem__(self, k):
        return self.get(k, False)


def quadro(teclas=(), m1=False, m2=False, m3=False):
    return Teclas({k: True for k in teclas}), (m1, m3, m2)  # pygame: (esquerdo, rodinha, direito)


def apertos(lista):
    """Passa uma lista de quadros pelo controle do jogador e devolve o que ele leu."""
    j = Jogador()
    p = partida_com(Roteiro([]), Roteiro([]))
    return [j.ler(q, p.L[0], p.L[1], p) for q in lista]


es = apertos([quadro()] * 3 + [quadro(m1=True)] * 5)
checar(sum(e.soco for e in es) == 1, "M1 = soco (segurar não fica socando)")
es = apertos([quadro()] * 3 + [quadro(m2=True)])
checar(es[-1].chute, "M2 = chute")
es = apertos([quadro(m3=True)] * 3 + [quadro([pygame.K_e], m3=True)])
checar(es[-1].especial == "E", "segura M3 + E")
for tecla, nome in ((pygame.K_q, "Q"), (pygame.K_r, "R"), (pygame.K_LSHIFT, "SHIFT")):
    es = apertos([quadro(m3=True)] * 3 + [quadro([tecla], m3=True)])
    checar(es[-1].especial == nome, f"M3 + {pygame.key.name(tecla)} = {nome}")
es = apertos([quadro(m3=True)] * 3 + [quadro()] * 6 + [quadro([pygame.K_q])])
checar(es[-1].especial == "Q", "solta M3, 0,1 segundo depois Q ainda sai")
es = apertos([quadro(m3=True)] * 3 + [quadro()] * 30 + [quadro([pygame.K_q])])
checar(es[-1].especial is None, "solta M3, meio segundo depois Q NÃO sai mais (janela de 0,2 s)")
es = apertos([quadro(m3=True)] * 3 + [quadro([pygame.K_e], m3=True)])
checar(es[-1].especial == "E" and not es[-1].barra, "segura M3 (uma vez) + E = especial normal")
es = apertos([quadro(m3=True)] * 3 + [quadro()] * 5 + [quadro(m3=True)] * 3 + [quadro([pygame.K_e], m3=True)])
checar(es[-1].especial == "E" and es[-1].barra, "TOQUE E SEGURA o M3 + E = EX")
es = apertos([quadro(m3=True)] * 3 + [quadro()] * 5 + [quadro(m3=True)])
checar(es[-1].barra_toque, "M3 2x (clique duplo) = ESCAPE quando está apanhando")
es = apertos([quadro(m3=True)] * 3 + [quadro()] * 40 + [quadro(m3=True)] * 3 + [quadro([pygame.K_e], m3=True)])
checar(es[-1].especial == "E" and not es[-1].barra, "dois toques demorados no M3 não viram EX")
es = apertos([quadro()] * 3 + [quadro([pygame.K_e])])
checar(es[-1].especial is None, "E sem a rodinha não faz nada")
es = apertos([quadro(m3=True)] * 3 + [quadro([pygame.K_z], m3=True)])
checar(es[-1].especial == "Z", "M3 + Z = ultimate")

# ---- ultimate só com a barra cheia ----
p = partida_com(Roteiro([Entrada(5, especial="Z")]), Roteiro([]))
rodar(p, 5)
checar(p.L[0].nome_golpe != "ultimate", "ultimate sem barra cheia não sai")
p = partida_com(Roteiro([Entrada(5, especial="Z")]), Roteiro([]))
p.L[0].barra = BARRA_MAX
rodar(p, 200)
checar(p.L[0].barra < BARRA_MAX / 2, "ultimate gasta a barra")
checar(p.L[1].vida_max - p.L[1].vida >= 25, f"ultimate acerta forte ({p.L[1].vida_max - p.L[1].vida} de dano)")

# ---- especiais pelo nome ----
for botao, nome in (("E", "bola"), ("Q", "subida"), ("R", "giro"), ("SHIFT", "avanco")):  # noqa
    p = partida_com(Roteiro([Entrada(5, especial=botao)]), Roteiro([]))
    rodar(p, 3)
    checar(p.L[0].nome_golpe == nome, f"especial '{nome}' sai")

# ---- bater enche a barra ----
p = partida_com(Roteiro([Entrada(6)] * 60 + [Entrada(5, soco=True)]), Roteiro([]))
rodar(p, 90)
checar(p.L[0].barra > 0 and p.L[1].barra > 0, "bater e apanhar enchem a barra")

# ---- soco de perto acerta e tira vida ----
p = partida_com(Roteiro([Entrada(6)] * 60 + [Entrada(5, soco=True)]), Roteiro([]))
rodar(p, 90)
checar(p.L[1].vida < p.L[1].vida_max, "andar até o outro e socar tira vida")

# ---- segurar trás defende ----
p = partida_com(Roteiro([Entrada(6)] * 75 + [Entrada(5, soco=True)]), Roteiro([Entrada()] * 74 + [Entrada(6)] * 200))
rodar(p, 100)
perdeu = p.L[1].vida_max - p.L[1].vida
checar(p.L[0].acertou and 0 < perdeu <= 5 * DEFESA_DANO + 0.01, f"quem segura TRÁS defende o soco e só perde um pouco ({perdeu:.1f})")

# ---- rasteira passa pela defesa em pé ----
p = partida_com(Roteiro([Entrada(6)] * 75 + [Entrada(3, chute=True)]), Roteiro([Entrada()] * 74 + [Entrada(6)] * 200))
rodar(p, 100)
checar(p.L[1].vida < p.L[1].vida_max, "rasteira (agachado + chute) passa pela defesa em pé")

# ---- bola atravessa a tela e acerta ----
p = partida_com(Roteiro([Entrada(5, especial="E")]), Roteiro([]))
rodar(p, 150)
checar(p.L[1].vida < p.L[1].vida_max, "bola de longe acerta")

# ---- os dois não se atravessam ----
p = partida_com(Roteiro([Entrada(6)] * 300), Roteiro([Entrada(4)] * 300))
rodar(p, 300)
checar(p.L[0].x < p.L[1].x, "andando um contra o outro, ninguém atravessa")

# ---- guarda quebra depois de alguns golpes defendidos ----
socos = []
for _ in range(8):
    socos += [Entrada(5, soco=True)] + [Entrada()] * 15 + [Entrada(6)] * 10  # bate e chega perto de novo
p = partida_com(Roteiro(socos), Roteiro([Entrada(6)] * 400))
p.L[1].x, p.L[0].x = PAREDE_D, PAREDE_D - 70  # encurralado na parede, segurando trás
estados = []
for _ in range(320):
    p.passo(None)
    estados.append(p.L[1].estado)
defesas = sum(1 for a, b in zip(estados, estados[1:]) if b == "defendendo" and a != "defendendo")
checar("tonto" in estados, f"guarda quebra depois de {defesas} socos defendidos")
checar(3 <= defesas <= 6, "a guarda aguenta uns 4-5 socos (nem pouco, nem infinito)")
checar("golpeado" in estados[estados.index("tonto"):], "depois de quebrar, o soco entra")

# ---- combo: soco, soco, chute emendados ----
p = partida_com(Roteiro([Entrada(5, soco=True)] + [Entrada()] * 5 + [Entrada(5, soco=True)] + [Entrada()] * 5
                        + [Entrada(5, chute=True)]), Roteiro([]))
p.L[1].x = p.L[0].x + 70
golpes_vistos = []
t_antes = 99
for _ in range(60):
    p.passo(None)
    l0 = p.L[0]
    if l0.estado == "ataque" and l0.t < t_antes:  # começou um golpe novo
        golpes_vistos.append(l0.nome_golpe)
    t_antes = l0.t if l0.estado == "ataque" else 99
checar(golpes_vistos == ["soco", "soco", "chute"] and p.L[0].combo >= 3,
       f"combo soco, soco, chute ({golpes_vistos}, combo {p.L[0].combo})")

# ---- parry: tocar pra frente bem na hora ----
p = partida_com(Roteiro([Entrada(5, soco=True)]), Roteiro([Entrada()] * 1 + [Entrada(4)] + [Entrada()] * 40))
p.L[1].x = p.L[0].x + 70
v0 = p.L[1].vida
rodar(p, 40)
checar(p.L[1].vida == v0, "PARRY: tocar pra frente na hora não leva nada")
p = partida_com(Roteiro([Entrada(5, soco=True)]), Roteiro([Entrada(4)] + [Entrada()] * 40))
p.L[1].x = p.L[0].x + 70
for _ in range(14):
    p.passo(None)
checar(p.L[1].estado in ("parado", "andando", "agachado"), "PARRY: quem dá parry fica livre na hora (não fica travado)")
mash = []
for k in range(0, 60, 2):
    mash += [Entrada(4), Entrada()]
p = partida_com(Roteiro([Entrada()] * 30 + [Entrada(5, soco=True)]), Roteiro(mash))
p.L[1].x = p.L[0].x + 70
v0 = p.L[1].vida
rodar(p, 60)
checar(p.L[1].vida < v0, "PARRY: ficar apertando pra frente sem parar não funciona")

# ---- computador não defende soco rápido por reflexo ----
from controles import Computador as _C
acertos = 0
for n in range(20):
    random.seed(n)
    p = partida_com(Roteiro([Entrada(5, soco=True)]), _C("DIFÍCIL"))
    p.L[1].x = p.L[0].x + 70  # colados, soco sai na hora
    v0 = p.L[1].vida
    rodar(p, 30)
    acertos += p.L[1].vida < v0
checar(acertos >= 12, f"computador (difícil) não defende todo soco por reflexo ({acertos}/20 acertaram)")

# =====================================================================
# MAX-10
# =====================================================================
MAX = PERSONAGENS[0]
ALVO = BONECO


def contra_max(passos_max, passos_alvo=(), distancia=None):
    p = Partida(MAX, ALVO, Roteiro(passos_max), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


def dano(p):
    return p.L[1].vida_max - p.L[1].vida


# E: laser de longe
p = contra_max([Entrada(5, especial="E")], distancia=450)
rodar(p, 130)
checar(dano(p) == 20, f"MAX-10: laser acerta de longe e tira 20 ({dano(p)})")
p = contra_max([Entrada(5, especial="E")], [Entrada()] * 47 + [Entrada(8)] + [Entrada()] * 100, distancia=450)
rodar(p, 130)
checar(dano(p) == 0, "MAX-10: pulando quando a mira trava, escapa do laser")

# SHIFT: voozinho (dash)
p = contra_max([Entrada(5, especial="SHIFT")], distancia=600)
x0 = p.L[0].x
subiu = False
for _ in range(50):
    p.passo(None)
    subiu |= p.L[0].y < CHAO - 10
checar(p.L[0].x - x0 > 150 and subiu, f"MAX-10: voozinho voa pra frente ({int(p.L[0].x - x0)} px)")
p = contra_max([Entrada(5, especial="SHIFT")], distancia=200)
rodar(p, 60)
checar(dano(p) == 6, f"MAX-10: voozinho trombando tira 6 ({dano(p)})")

# Q: agarrão
p = contra_max([Entrada(5, especial="Q")], distancia=60)
p.L[0].x, p.L[1].x = 120, 180
estados = set()
for _ in range(160):
    p.passo(None)
    estados.add(p.L[1].estado)
checar("agarrado" in estados and "caido" in estados, "MAX-10: agarrão pega, gira e derruba")
checar(dano(p) == 15, f"MAX-10: agarrão tira 15 ({dano(p)})")
p = contra_max([Entrada(5, especial="Q")], distancia=60)
altura = 0
for _ in range(160):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(altura > 150, f"MAX-10: agarrão joga PRA CIMA ({int(altura)} px de altura)")
p = contra_max([Entrada(5, especial="Q")], [Entrada(6)] * 60, distancia=200)
rodar(p, 80)
checar(dano(p) == 0, "MAX-10: agarrão de longe erra")

# R: metralhadora
p = contra_max([Entrada(5, especial="R")], distancia=150)
livre_entre, seguidos, maior = 0, 0, 0
for _ in range(160):
    p.passo(None)
    if p.L[0].estado == "ataque" and p.L[1].estado in ("parado", "andando"):
        seguidos += 1
        maior = max(maior, seguidos)
    else:
        seguidos = 0
checar(dano(p) == 10, f"MAX-10: metralhadora dá 5 socos de 2 ({dano(p)})")
checar(maior >= 10, f"MAX-10: entre os socos o outro fica livre uns 0,2s ({maior} quadros)")
p = contra_max([Entrada(5, especial="R")], [Entrada()] * 24 + [Entrada(6)] * 200, distancia=150)
rodar(p, 160)
checar(dano(p) < 10, f"MAX-10: dá pra escapar/defender no meio da metralhadora ({dano(p)})")

# E: agachar faz o laser passar por cima
p = contra_max([Entrada(5, especial="E")], [Entrada(1)] * 200, distancia=450)
rodar(p, 130)
checar(dano(p) == 0, "MAX-10: agachado, o laser passa por cima")
p = contra_max([Entrada(5, especial="E")], [Entrada()] * 200, distancia=450)
rodar(p, 130)
checar(dano(p) == 20, "MAX-10: em pé, o laser acerta")

# computador não fica spammando laser
random.seed(5)
from controles import Computador as _C2
lasers = 0
p = Partida(MAX, ALVO, _C2("DIFÍCIL"), Roteiro([]))
p.fase, p.tf = "luta", 0
p.L[1].x = PAREDE_D
for _ in range(60 * 20):
    p.passo(None)
    if p.L[0].estado == "ataque" and p.L[0].nome_golpe == "max_laser" and p.L[0].t == 1:
        lasers += 1
    p.L[1].vida = p.L[1].vida_max
checar(lasers <= 7, f"MAX-10 (computador difícil): no máximo ~1 laser a cada 3-4s ({lasers} em 20s)")

# Z: rasante
p = contra_max([Entrada(5, especial="Z")], distancia=300)
rodar(p, 10)
checar(p.L[0].nome_golpe != "max_rasante", "MAX-10: rasante sem barra cheia não sai")
p = contra_max([Entrada(5, especial="Z")], distancia=300)
p.L[0].barra = BARRA_MAX
saiu_da_tela = False
for _ in range(260):
    p.passo(None)
    saiu_da_tela |= p.L[0].y < -100
checar(saiu_da_tela, "MAX-10: rasante sai voando da tela")
checar(dano(p) == 30, f"MAX-10: rasante tira 30 ({dano(p)})")
checar(p.L[0].y == CHAO and PAREDE_E <= p.L[0].x <= PAREDE_D, "MAX-10: volta pro chão dentro da tela")

# =====================================================================
# COMBO AÉREO
# =====================================================================
# Max joga pra cima com o Q, pula atrás (CIMA), dá socos no ar e termina com chute pra baixo
passos = [Entrada(5, especial="Q")] + [Entrada()] * 60 + [Entrada(8)] * 22 + [Entrada()] * 8
for _ in range(3):
    passos += [Entrada(5, soco=True)] + [Entrada()] * 9
passos += [Entrada(5, chute=True)] + [Entrada()] * 120
p = contra_max(passos, distancia=60)
estados_ar, viu_quica, hits_ar = set(), False, 0
for _ in range(260):
    antes = p.L[1].malabar_n
    p.passo(None)
    if p.L[1].malabar_n > antes:
        hits_ar += 1
    viu_quica |= p.L[1].quica
checar(hits_ar >= 3, f"COMBO AÉREO: socos no ar acertam quem foi jogado pra cima ({hits_ar} golpes no ar)")
checar(viu_quica, "COMBO AÉREO: o chute no ar joga pra baixo e ele quica")
checar(p.L[0].combo >= 4, f"COMBO AÉREO: conta tudo como um combo só ({p.L[0].combo} golpes)")

# =====================================================================
# RIB
# =====================================================================
RIB = PERSONAGENS[1]


def contra_rib(passos_rib, passos_alvo=(), distancia=None):
    p = Partida(RIB, ALVO, Roteiro(passos_rib), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


# E: shuriken
p = contra_rib([Entrada(5, especial="E")], distancia=400)
rodar(p, 80)
checar(dano(p) == 5, f"RIB: shuriken tira 5 ({dano(p)})")
seis = []
for _ in range(6):
    seis += [Entrada(5, especial="E")] + [Entrada()] * 17
p = contra_rib(seis, distancia=500)
saiu = 0
for _ in range(6 * 18 + 10):
    antes = len(p.projeteis)
    p.passo(None)
    saiu += len(p.projeteis) > antes
checar(saiu == 5, f"RIB: depois de 5 shurikens rapidinhas tem que recarregar ({saiu} saíram de 6)")

# R: corrida
p = contra_rib([Entrada(5, especial="R")], distancia=300)
rodar(p, 120)
checar(dano(p) == 25, f"RIB: corrida acerta 5 vezes de 5 ({dano(p)})")

# Q: rasteira + chute pra cima
p = contra_rib([Entrada(5, especial="Q")], distancia=90)
altura = 0
for _ in range(80):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) == 10 and altura > 120, f"RIB: rasteira + chute joga pra cima ({dano(p)} de dano, {int(altura)} px)")

# SHIFT: linguada
p = contra_rib([Entrada(5, especial="SHIFT")], distancia=200)
x0 = p.L[1].x
rodar(p, 70)
checar(dano(p) == 20, f"RIB: linguada tira 20 ({dano(p)})")
checar(p.L[1].x < x0, "RIB: a língua puxa o outro pra perto")
p = contra_rib([Entrada(5, especial="SHIFT")], [Entrada()] * 10 + [Entrada(6)] * 60, distancia=140)
rodar(p, 70)
checar(dano(p) == 0 or p.L[1].estado == "defendendo" or dano(p) < 20, "RIB: linguada demora pra sair (dá tempo de reagir)")

# Z: ultimate (KAGE BUNSHIN)
p = contra_rib([Entrada(5, especial="Z")], [], distancia=300)
p.L[0].barra = BARRA_MAX
viu_clones = False
for _ in range(500):
    p.passo(None)
    if p.L[0].memo.get("clones"):
        viu_clones = True
        p.desenhar(tela)
checar(viu_clones and abs(dano(p) - 35) < 0.01 and p.cutscene is None,
       f"RIB: ultimate Kage Bunshin (sem cutscene): os clones arremessam e tiram 35 ({dano(p):.1f})")
p = contra_rib([Entrada(5, especial="Z")], [Entrada(6)] * 400, distancia=300)
p.L[0].barra = BARRA_MAX
rodar(p, 300)
checar(dano(p) < 10, f"RIB: ultimate DEFENDIDA tira bem menos ({dano(p):.1f})")
p = contra_rib([Entrada(5, especial="Z")], [Entrada()] * 40 + [Entrada(5, especial="E")], distancia=250)
p.L[0].barra = BARRA_MAX
p.L[1].f = MAX
rodar(p, 300)
x = p.L[0].extra
checar(not tem_shuriken(p.L[0]), "RIB: depois da ultimate fica sem shuriken")
x["relogio"] += 60 * 16
checar(tem_shuriken(p.L[0]), "RIB: depois de 15 segundos a shuriken volta")

# =====================================================================
# TRAFO
# =====================================================================
TRAFO = PERSONAGENS[2]


def contra_trafo(passos_trafo, passos_alvo=(), distancia=None):
    p = Partida(TRAFO, ALVO, Roteiro(passos_trafo), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


# E: linguão paralisa
p = contra_trafo([Entrada(5, especial="E")], distancia=200)
tonto = 0
for _ in range(220):
    p.passo(None)
    tonto += p.L[1].estado == "tonto"
checar(dano(p) == 10, f"TRAFO: linguão tira 10 ({dano(p)})")
checar(110 <= tonto <= 130, f"TRAFO: linguão paralisa uns 2 segundos ({tonto} quadros)")

# Q: braços da terra (não dá pra defender, dá pra pular)
p = contra_trafo([Entrada(5, especial="Q")], [Entrada(6)] * 200, distancia=300)
altura = 0
for _ in range(120):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) == 20 and altura > 100, f"TRAFO: braços da terra jogam pra cima, mesmo defendendo ({dano(p)}, {int(altura)} px)")
p = contra_trafo([Entrada(5, especial="Q")], [Entrada()] * 28 + [Entrada(8)] * 3, distancia=300)
rodar(p, 120)
checar(dano(p) == 0, "TRAFO: pulando no sinal, os braços erram")

# R: metralhadora de olhos
p = contra_trafo([Entrada(5, especial="R")], distancia=400)
rodar(p, 140)
checar(dano(p) == 24, f"TRAFO: metralhadora de olhos dá 6 tiros de 4 ({dano(p)})")

# SHIFT: pulão
p = contra_trafo([Entrada(5, especial="SHIFT")], distancia=500)
x0 = p.L[0].x
rodar(p, 90)
checar(p.L[0].x - x0 > 220, f"TRAFO: pulão bem longo ({int(p.L[0].x - x0)} px)")
p = contra_trafo([Entrada(5, especial="SHIFT")], distancia=260)
rodar(p, 90)
checar(dano(p) == 10, f"TRAFO: pulão tira 10 ({dano(p)})")

# Z: ultimate
p = contra_trafo([Entrada(5, especial="Z")], distancia=250)
p.L[0].barra = BARRA_MAX
teve_cena, virou = False, set()
for q in range(700):
    p.passo(None)
    teve_cena |= p.cutscene is not None
    if p.L[0].disfarce:
        virou.add(p.L[0].disfarce["nome"])
    if q % 20 == 0:
        p.desenhar(tela)  # desenhar disfarçado não pode dar erro
checar(not teve_cena and dano(p) == 40, f"TRAFO: ultimate sem cutscene, dentro da luta, tira 40 ({dano(p)})")
checar(virou == {"MAX-10", ALVO["nome"]}, f"TRAFO: na ultimate vira o Max-10 e depois o oponente ({sorted(virou)})")
checar(p.L[0].disfarce is None, "TRAFO: no final volta a ser o Trafo")
p = contra_trafo([Entrada(5, especial="Z")], [Entrada(6)] * 400, distancia=250)
p.L[0].barra = BARRA_MAX
teve_cena = False
for _ in range(400):
    p.passo(None)
    teve_cena |= p.cutscene is not None
checar(not teve_cena, "TRAFO: ultimate defendida erra")
p = contra_trafo([], distancia=200)
l0 = p.L[0]
l0.encher(100)
checar(l0.barra == 50, f"TRAFO: a barra do ultimate enche na metade da velocidade ({l0.barra})")

# =====================================================================
# KING RIP
# =====================================================================
KING = next(f for f in PERSONAGENS if f["nome"] == "KING RIP")


def contra_king(passos_king, passos_alvo=(), distancia=None):
    p = Partida(KING, ALVO, Roteiro(passos_king), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


p = contra_king([Entrada(5, especial="E")], distancia=250)
voltou = False
for _ in range(140):
    p.passo(None)
    voltou |= p.L[0].extra.get("nunchaku_fora") is False
checar(dano(p) == 10 and voltou, f"KING RIP: bumerangue bate na ida e na volta e volta pra mão ({dano(p)})")
p = contra_king([Entrada(5, especial="Q")], distancia=110)
altura = 0
for _ in range(80):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) == 15 and altura > 100, f"KING RIP: chute acrobático tira 15 e joga pra cima ({dano(p)}, {int(altura)} px)")
p = contra_king([Entrada(5, especial="R")], distancia=110)
rodar(p, 120)
checar(dano(p) == 20, f"KING RIP: nunchaku giratório dá 10 hits de 2 ({dano(p)})")
p = contra_king([Entrada(5, especial="SHIFT")], distancia=600)
x0 = p.L[0].x
rodar(p, 60)
checar(p.L[0].x - x0 > 180 and p.L[0].angulo == 0, f"KING RIP: salto com nunchaku vai longe girando ({int(p.L[0].x - x0)} px)")
p = contra_king([Entrada(5, especial="Z")], distancia=200)
p.L[0].barra = BARRA_MAX
for _ in range(400):
    p.passo(None)
checar(dano(p) == 30, f"KING RIP: ultimate de acrobacias tira 30 ({dano(p)})")
p = contra_king([Entrada(5, especial="Z")], [Entrada(6)] * 400, distancia=200)
p.L[0].barra = BARRA_MAX
rodar(p, 300)
checar(dano(p) < 3, "KING RIP: ultimate defendida erra")
import habilidades as _hab  # noqa: E402
p = contra_king([], distancia=100)
checar(_hab.limite_combo(p.L[0], 12) == 18 and _hab.cadeia_extra(p.L[0]) == 2,
       "KING RIP: Maestria de Combate deixa o combo mais longo (18)")

# =====================================================================
# CANNAN
# =====================================================================
CANNAN = next(f for f in PERSONAGENS if f["nome"] == "CANNAN")


def contra_cannan(passos_cannan, passos_alvo=(), distancia=None):
    p = Partida(CANNAN, ALVO, Roteiro(passos_cannan), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


def segurando_z(n):
    e = []
    for i in range(n):
        x = Entrada(5, especial="Z" if i == 0 else None)
        x.segura_ult = True
        e.append(x)
    return e


p = contra_cannan([Entrada(5, especial="E")], distancia=300)
rodar(p, 120)
checar(dano(p) == 15, f"CANNAN: pistola dá 3 tiros de 5 ({dano(p)})")
p = contra_cannan([Entrada(5, especial="Q")], distancia=90)
altura = 0
for _ in range(80):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) == 20 and altura > 60, f"CANNAN: coronhada + soco pra cima tira 20 e joga pra cima ({dano(p)}, {int(altura)} px)")
p = contra_cannan([Entrada(5, especial="R")], distancia=90)
rodar(p, 140)
checar(dano(p) == 18, f"CANNAN: canhão de perto dá 6 de 2 e o último 6 ({dano(p)})")
p = contra_cannan([Entrada(5, especial="SHIFT")], distancia=500)
rodar(p, 90)
checar(dano(p) == 10, f"CANNAN: corrida maluca tira 10 ({dano(p)})")
p = contra_cannan([Entrada(5, especial="Z")], distancia=250)
p.L[0].barra = BARRA_MAX
cansou = 0
for _ in range(700):
    p.passo(None)
    if p.L[0].estado == "tonto" and p.L[0].superaquecido:
        cansou += 1
checar(dano(p) == 40, f"CANNAN: ultimate dá 20 tiros de 2 ({dano(p)})")
checar(280 <= cansou <= 320, f"CANNAN: depois da ultimate fica 5s sem agir ({cansou} quadros)")
p = contra_cannan(segurando_z(320), distancia=250)
p.L[0].barra = BARRA_MAX
cansou = 0
for _ in range(1100):
    p.passo(None)
    if p.L[0].estado == "tonto" and p.L[0].superaquecido:
        cansou += 1
checar(dano(p) == 50, f"CANNAN: ultimate carregada (5s segurando Z) tira 50 ({dano(p)})")
checar(400 <= cansou <= 440, f"CANNAN: ultimate carregada deixa 7s sem agir ({cansou} quadros)")
p = contra_cannan([], distancia=300)
c, o = p.L[0], p.L[1]
from golpes import GOLPES as _G  # noqa: E402
checar(_hab.mult_recebe(c, o, _G["cannan_bala"]) == 0.5, "CANNAN: Colete à Prova de Balas tira metade de tiro")
o.x = c.x + 60
checar(_hab.mult_recebe(c, o, _G["soco"]) == 1.0, "CANNAN: Colete não protege de soco de perto")
j = Jogador()
e = j.ler(quadro((ULTIMATE,)), c, o, p)
checar(e.segura_ult, "CANNAN: o jogo sabe quando o Z está segurado (pra carregar)")

# =====================================================================
# MODO TREINO
# =====================================================================
from controles import BonecoTreino  # noqa: E402
treinador = BonecoTreino()
socos = []
for _ in range(12):
    socos += [Entrada(6)] * 6 + [Entrada(5, soco=True)] + [Entrada()] * 12
p = Partida(MAX, boneco(2), Roteiro([Entrada(6)] * 40 + socos), treinador, treino=True)
morreu = False
for _ in range(900):
    p.passo(None)
    morreu |= p.L[1].vida <= 0 or p.fase != "luta"
checar(not morreu, "TREINO: ninguém morre e a luta não acaba")
checar(p.ultimo_combo is not None and p.L[1].vida == p.L[1].vida_max,
       f"TREINO: depois do combo a vida volta e mostra o resultado ({p.ultimo_combo})")
treinador.modo = "DEFENDE"
p = Partida(MAX, boneco(0), Roteiro([Entrada(6)] * 60 + [Entrada(5, soco=True)]), treinador, treino=True)
estados = []
for _ in range(100):
    p.passo(None)
    estados.append(p.L[1].estado)
checar("defendendo" in estados, "TREINO: no modo DEFENDE o boneco defende")

# =====================================================================
# TELAS: seleção e VS
# =====================================================================
from selecao import TelaSelecao, TelaVS  # noqa: E402
sel = TelaSelecao(PERSONAGENS)
for tecla in (pygame.K_d, pygame.K_RETURN, pygame.K_d, pygame.K_d, pygame.K_RETURN):
    sel.desenhar(tela)
    sel.tecla(tecla)
checar(sel.pronto and sel.escolhido[0] == 1 and sel.escolhido[1] is not None,
       f"SELEÇÃO: escolhe o seu e o adversário ({sel.escolhido})")
vs = TelaVS(PERSONAGENS[0], PERSONAGENS[1])
while not vs.acabou:
    vs.desenhar(tela)
checar(True, "VS: a tela de VS passa sem erro")

# ---- entradas dos personagens (começo da luta) ----
for f in PERSONAGENS:
    p = Partida(f, BONECO, Roteiro([]), Roteiro([]))
    fases = set()
    for q in range(DURACAO_ENTRADA + 5):
        p.passo(None)
        fases.add(p.fase)
        if q % 15 == 0:
            p.desenhar(tela)
    l0 = p.L[0]
    checar("entrada" in fases and p.fase == "intro" and l0.y == CHAO and not l0.esconde and not l0.sobrepor,
           f"ENTRADA: {f['nome']} entra e fica pronto pra luta")
    checar(callable(f.get("entrada")) and callable(f.get("vitoria")),
           f"ENTRADA: {f['nome']} tem entrada e pose de vitória próprias")

# ---- poses de vitória ----
for f in PERSONAGENS:
    p = Partida(f, BONECO, Roteiro([]), Roteiro([]))
    p.fase, p.tf = "luta", 0
    p.L[1].vida = 0
    viu = False
    for q in range(260):
        p.passo(None)
        viu |= p.L[0].estado == "vitoria"
        if q % 20 == 0:
            p.desenhar(tela)
    checar(viu, f"VITÓRIA: {f['nome']} faz a pose de vitória")

# =====================================================================
# HABILIDADES
# =====================================================================
import habilidades as hab  # noqa: E402
from golpes import GOLPES  # noqa: E402
# Max-10: Maquinário Pesado
p = contra_max([], distancia=200)
mx, alvo = p.L
dano_normal = 10 * hab.mult_causa(mx, GOLPES["soco"])
mx.vida = 20
checar(hab.mult_causa(mx, GOLPES["soco"]) == 1.25 and hab.mult_recebe(mx) == 0.75 and dano_normal == 10,
       "HABILIDADE: Max-10 com 25% de vida bate 25% mais forte e leva 25% menos")
v = mx.vida
mx.levar(8, alvo, GOLPES["chute"])
checar(abs((v - mx.vida) - 6) < 0.01, f"HABILIDADE: Max-10 no Maquinário leva 6 em vez de 8 ({v - mx.vida})")
# Rib: Postura Ninja
p = contra_rib([], distancia=200)
checar(p.L[0].corpo().w < 44 * p.L[0].s * 0.85, "HABILIDADE: Rib com hitbox mais fininha (Postura Ninja)")
# Trafo: Conexão Terrestre
TRAFO["habilidade"] = "conexao"
p = contra_trafo([Entrada(2)] * 20, distancia=300)
rodar(p, 20)
checar(p.L[0].corpo().h < 80 * p.L[0].s * 0.9 * 0.55, "HABILIDADE: Trafo agachado fica bem menor (Conexão Terrestre)")
checar(hab.mult_causa(p.L[0], GOLPES["ag_chute"]) == 2.0 and hab.mult_causa(p.L[0], GOLPES["chute"]) == 1.0,
       "HABILIDADE: Trafo agachado bate o dobro")
checar(hab.mult_recebe(p.L[0]) == 0.8, "HABILIDADE: Trafo agachado leva 20% menos dano")
# Trafo: Mutação
TRAFO["habilidade"] = "mutacao"
p = Partida(RIB, TRAFO, Roteiro([Entrada(5, especial="Z")]), Roteiro([]))
p.fase, p.tf = "luta", 0
p.L[1].x = p.L[0].x + 300
p.L[0].barra = BARRA_MAX
for _ in range(500):
    p.passo(None)
tr = p.L[1]
checar(tr.mutado is RIB and tr.disfarce is RIB, "HABILIDADE: Trafo levou ultimate do Rib e virou o Rib (Mutação)")
checar(tr.golpe_do_botao("E") == "rib_shuriken" and "ninja" in hab.ativas(tr) and "mutacao" in hab.ativas(tr),
       "HABILIDADE: mutado, usa os golpes e a habilidade do Rib e continua com a Mutação")
p.L[0].vida = p.L[0].vida_max
tr.estado, tr.t = "parado", 0
p.ctrl = (p.ctrl[0], Roteiro([Entrada(5, especial="E")] + [Entrada()] * 40))
for q in range(60):
    p.passo(None)
    if q % 10 == 0:
        p.desenhar(tela)
checar(any(pr.dono is tr for pr in p.projeteis) or p.L[0].vida < p.L[0].vida_max,
       "HABILIDADE: o Trafo mutado consegue jogar a shuriken do Rib")
TRAFO["habilidade"] = "conexao"

# ---- arcade: história e chefão ----
from historia import ABERTURA, FINAIS, Creditos, Quadrinho  # noqa: E402
from personagens import sombra  # noqa: E402
for paineis in [ABERTURA] + list(FINAIS.values()):
    q = Quadrinho(paineis)
    while not q.acabou:
        q.desenhar(tela)
c = Creditos()
while not c.acabou:
    c.desenhar(tela)
from historia import final_generico  # noqa: E402
for f in PERSONAGENS:  # quem ainda não tem final próprio usa o genérico (a história completa vem depois)
    q = Quadrinho(FINAIS.get(f["nome"]) or final_generico(f["nome"]))
    while not q.acabou:
        q.desenhar(tela)
checar(True, "ARCADE: todo personagem tem um final (próprio ou o genérico)")
s = sombra(RIB)
p = Partida(RIB, s, Computador("DIFÍCIL"), Computador("DIFÍCIL"))
for q in range(3000):
    p.passo(None)
    if q % 300 == 0:
        p.desenhar(tela)
    if p.fase == "fim":
        break
checar(p.L[1].vida_max == 120 and s["sombra"], "ARCADE: a Sombra (chefão) luta e é mais forte")

# ---- sons: todos são criados sem erro ----
import som as _som  # noqa: E402
erros_som = []
for nome in ("soco", "chute", "defesa", "parry", "quebra", "vento", "pulo", "queda", "ko", "laser", "carga", "tiro", "uivo",
             "shuriken", "lingua", "explosao", "foguete", "terra", "puf", "ultimate", "blip", "confirma", "round",
             "lutem"):
    try:
        _som._criar(nome)
    except Exception as erro:
        erros_som.append(f"{nome}: {erro}")
checar(not erros_som, f"SOM: todos os efeitos são criados ({erros_som or 'ok'})")
try:
    _som._musica_luta()
    _som._musica_menu()
    checar(True, "SOM: as músicas são criadas")
except Exception as erro:
    checar(False, f"SOM: as músicas são criadas ({erro})")

# ---- computador contra computador, várias partidas ----
random.seed(1)
fotos = "--fotos" in sys.argv
pasta = os.path.join(os.path.dirname(__file__), "..", ".tmp")
terminadas, golpes = 0, set()
for n in range(20):
    nivel = list(Computador.NIVEIS)[n % 3]
    todos = PERSONAGENS + [BONECO]
    f1, f2 = todos[n % len(todos)], todos[(n + 1) % len(todos)]
    p = Partida(f1, f2, Computador(nivel), Computador(nivel))
    for q in range(60 * 60 * 6):
        p.passo(None)
        for l in p.L:
            golpes.add(l.nome_golpe)
            if l.no_chao() and l.estado != "agarrado" and p.fase != "entrada":  # (entrada pode vir de fora)
                assert PAREDE_E <= l.x <= PAREDE_D, "saiu da tela"
        if fotos and n == 0 and q % 97 == 0 and q < 97 * 30:
            p.desenhar(tela)
            pygame.image.save(tela, os.path.join(pasta, f"luta_{q // 97:02d}.png"))
        if p.fase == "fim":
            terminadas += 1
            break
checar(terminadas == 20, f"20 partidas do computador terminaram ({terminadas})")
precisa = {"soco", "chute", "ag_chute",  # (os golpes do boneco de treino não contam: ele quase não aparece)
           "max_laser", "max_voo", "max_agarrao", "max_gatling", "max_rasante",
           "rib_shuriken", "rib_corrida", "rib_rasteira", "rib_lingua", "rib_ultimate",
           "trafo_lingua", "trafo_terra", "trafo_olhos", "trafo_pulo",
           "king_bumerangue", "king_chute", "king_giro", "king_salto"}
checar(precisa <= golpes, f"o computador usa os golpes todos (faltou: {sorted(precisa - golpes)})")

# =====================================================================
# FALAS, ROUPAS, MOEDAS, LOJA, SOBREVIVÊNCIA E PAUSA
# =====================================================================
import falas  # noqa: E402
import pecas  # noqa: E402
import roupas  # noqa: E402
import save  # noqa: E402
nomes = [f["nome"] for f in PERSONAGENS]
checar(all(k == tuple(sorted(k)) and all(n in nomes for n in k) for k in falas.CONVERSAS),
       "FALAS: as conversas usam nomes de personagens que existem")
ok = True
for f1 in PERSONAGENS:
    for f2 in PERSONAGENS:
        conv = falas.dialogo(f1, f2)
        ok &= len(conv) == 2 and {lado for lado, _ in conv} == {0, 1}
checar(ok, "FALAS: toda dupla (e o espelho) tem uma conversa de 2 falas, uma de cada lado")
checar(len(falas.dialogo(PERSONAGENS[0], sombra(PERSONAGENS[0]))) == 2, "FALAS: a Sombra fala também")
vs = TelaVS(PERSONAGENS[3], PERSONAGENS[4])
for _ in range(vs.DURACAO):
    vs.desenhar(tela)
checar(vs.acabou and vs.DURACAO > 150, f"FALAS: a tela de VS espera as falas ({vs.DURACAO} quadros)")

import importlib  # noqa: E402
ok = True
for f in PERSONAGENS:
    modulo = importlib.import_module(f["desenho"].__module__)
    for r in roupas.da(f):
        ok &= all(letra in modulo.PALETA for letra in r.get("troca", {}))
checar(ok and all(len([r for r in roupas.da(f) if not r.get("codigo")]) == 3 for f in PERSONAGENS),
       "ROUPAS: cada personagem tem 2 roupas novas que trocam cores que existem")
from cannan import TRONCO as _tronco  # noqa: E402
pecas.usar_troca(None)
normal = pygame.image.tostring(_tronco.sup("normal"), "RGBA")
pecas.usar_troca(roupas.ROUPAS["CANNAN"][2]["troca"])
artico = pygame.image.tostring(_tronco.sup("normal"), "RGBA")
pecas.usar_troca(None)
checar(normal != artico and pygame.image.tostring(_tronco.sup("normal"), "RGBA") == normal,
       "ROUPAS: a roupa muda as cores do desenho (e desliga depois)")

save.carregar()
checar(save.moedas() == 0 and not save.comprar("CANNAN", "artico", 300), "MOEDAS: começa com 0 e não compra sem moeda")
save.ganhar(320)
checar(save.comprar("CANNAN", "artico", 300) and save.moedas() == 20 and save.tem_roupa("CANNAN", "artico"),
       "MOEDAS: compra a roupa e desconta as moedas")
save.usar("CANNAN", "artico")
save.carregar()  # lê de novo do arquivo
checar(save.usando("CANNAN") == "artico" and save.moedas() == 20, "MOEDAS: o save guarda as moedas e a roupa")
f = roupas.vestir(CANNAN)
checar(f["roupa"] == "artico" and f["troca"] and roupas.outra(f, "artico")["roupa"] != "artico",
       "ROUPAS: veste a roupa do save (e no espelho o computador usa outra)")


def ganha_luta(nivel, perfect=True, vida=60):
    p = Partida(CANNAN, ALVO, Jogador(), Computador(nivel))
    p.rounds = 1
    p.fase, p.tf = "ko", 0  # já no K.O. (o computador não tem chance de atirar antes)
    if not perfect:
        p.L[0].vida = vida
    p.L[1].vida = 0
    for _ in range(400):
        p.passo(quadro())
        if p.fase == "fim":
            break
    return p


antes = save.moedas()
p = ganha_luta("DIFÍCIL")
checar(p.premio and p.premio[3] == (MOEDAS_VITORIA + MOEDAS_PERFECT + 10) * 2 and save.moedas() == antes + p.premio[3] + sum(v for _, v in p.premio[4]),
       f"MOEDAS: vitória + perfect + vida no DIFÍCIL vale o dobro ({p.premio and p.premio[3]})")
p = ganha_luta("FÁCIL", perfect=False)
checar(p.premio[3] == round((MOEDAS_VITORIA + 6) * 0.5), f"MOEDAS: no FÁCIL vale a metade ({p.premio[3]})")
checar(not any(n.startswith("QUASE") for n, _ in p.premio[0]), "MOEDAS: com 60 de vida não é quase perfect")
p = ganha_luta("MÉDIO", perfect=False, vida=80)
checar(p.premio[3] == MOEDAS_VITORIA + MOEDAS_QUASE + 8, f"MOEDAS: com 80 de vida é QUASE PERFECT ({p.premio[3]})")
p = Partida(CANNAN, ALVO, Roteiro([]), Roteiro([]))
p.rounds, p.fase = 1, "luta"
p.L[1].vida = 0
rodar(p, 400)
checar(p.fase == "fim" and p.premio is None, "MOEDAS: computador contra computador não ganha moeda")
p = ganha_luta("MÉDIO")
p.combo_max = 12
p.premio = None
p.pagar()
checar(any(n == "COMBO MÁXIMO" for n, _ in p.premio[0]), "MOEDAS: combo máximo dá bônus")
for _ in range(50):
    p.desenhar(tela)

from loja import TelaLoja  # noqa: E402
lj = TelaLoja(PERSONAGENS)
lj.i = 0
lj.j = 2
save.d()["moedas"] = 0
m0 = save.moedas()
lj.confirmar()
checar(not save.tem_roupa("MAX-10", "carmesim") and save.moedas() == m0, "LOJA: sem moeda suficiente não compra")
save.ganhar(500)
lj.confirmar()
checar(save.tem_roupa("MAX-10", "carmesim") and save.usando("MAX-10") == "carmesim", "LOJA: compra e já veste")
for _ in range(60):
    lj.desenhar(tela)
for k in (pygame.K_d, pygame.K_s, pygame.K_w, pygame.K_a):
    lj.tecla(k)
lj.mouse((10, 10), True)
checar(True, "LOJA: a tela desenha e responde às teclas")

import luta  # noqa: E402
jogo = luta.Jogo()
jogo.modo = luta.SOBREV
jogo.escolha = [4, 0]
jogo.sobrev = {"n": 0, "vida": None, "ultimo": None}
jogo.sobrev_proxima()
jogo.comecar()
checar(jogo.partida.rounds == 1 and jogo.partida.sobrevivencia == 0 and jogo.partida.L[0].vida == 100,
       "SOBREVIVÊNCIA: a primeira luta é de 1 round com a vida cheia")
rival1 = jogo.sobrev["ultimo"]
jogo.sobrev.update(n=3, vida=45)
jogo.sobrev_proxima()
jogo.comecar()
checar(jogo.partida.L[0].vida == 45 and jogo.sobrev["ultimo"] != rival1 and jogo.sobrev_nivel() == "MÉDIO",
       "SOBREVIVÊNCIA: continua com a vida que sobrou, outro adversário e mais difícil")
jogo.partida.sobrevivencia = 7
jogo.partida.L[0].vida = 0
jogo.partida.fase = "luta"
for _ in range(400):
    jogo.partida.passo(quadro())
    if jogo.partida.fase == "fim":
        break
checar(save.recorde() == 7 and any(n == "RECORDE NOVO" for n, _ in jogo.partida.premio[0]),
       "SOBREVIVÊNCIA: guarda o recorde (e dá moedas por ele)")
jogo.pausado, jogo.opcao_pausa, jogo.tela_atual = True, 0, "luta"
jogo.partida.desenhar(tela)
jogo.desenhar_pausa()
jogo.pausa(pygame.K_RETURN)
checar(not jogo.pausado, "PAUSA: o menu desenha e CONTINUAR volta pra luta")
jogo.pausado, jogo.opcao_pausa = True, 2
jogo.pausa(pygame.K_RETURN)
checar(jogo.tela_atual == "titulo", "PAUSA: MENU PRINCIPAL volta pro título")
jogo.desenhar_titulo()

# =====================================================================
# FINN
# =====================================================================
FINN = next(f for f in PERSONAGENS if f["nome"] == "FINN")


def contra_finn(passos_finn, passos_alvo=(), distancia=None):
    p = Partida(FINN, ALVO, Roteiro(passos_finn), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


p = contra_finn([Entrada(5, especial="E")], distancia=350)
rodar(p, 120)
checar(dano(p) == 20, f"FINN: bola de fogo tira 20 ({dano(p)})")
p = contra_finn([Entrada(5, especial="Q")], distancia=230)
altura = 0
for _ in range(90):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) == 10 and altura > 60, f"FINN: levitação de média distância tira 10 e joga pra cima ({dano(p)}, {int(altura)} px)")
p = contra_finn([Entrada(5, especial="Q")], distancia=60)
rodar(p, 90)
checar(dano(p) == 0, "FINN: levitação é de média distância (colado não pega)")
p = contra_finn([Entrada(5, especial="R")], distancia=100)
rodar(p, 120)
checar(dano(p) == 20, f"FINN: cajado amarelo dá 5 hits de 4 ({dano(p)})")
p = contra_finn([Entrada(5, especial="SHIFT")], distancia=260)
x0 = p.L[0].x
rodar(p, 60)
checar(dano(p) == 5 and p.L[0].x - x0 > 60, f"FINN: empurrão mágico vai pra frente e tira 5 ({dano(p)})")
p = contra_finn([Entrada(5, especial="Z")], distancia=300)
p.L[0].barra = BARRA_MAX
rodar(p, 260)
checar(dano(p) == 40, f"FINN: ultimate MINI SOL tira 40 ({dano(p)})")
p = Partida(FINN, RIB, Roteiro([Entrada(5, especial="Z")]), Roteiro([Entrada(5)] * 75 + [Entrada(5, especial="E")]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 300
p.L[0].barra = BARRA_MAX
rodar(p, 260)
checar(dano(p) >= 40, "FINN: o Mini Sol passa por cima da shuriken (não some)")
p = Partida(FINN, ALVO, Roteiro([]), Roteiro([]))
viu_meio = False
while p.fase == "entrada":
    p.passo(None)
    l = p.L[0]
    if l.cortar_acima is not None and CHAO - 100 < l.cortar_acima < CHAO - 30:
        viu_meio = True
        p.desenhar(tela)
checar(viu_meio and p.L[0].cortar_acima is None, "FINN: se materializa dos pés à cabeça")
p = contra_finn([], distancia=80)
f, o = p.L[0], p.L[1]
for _ in range(COMBO_MAXIMO):
    o.mudar("golpeado")
    o.receber(GOLPES["soco"], 1, f, 1.0)
checar(f.invisivel == INVISIVEL_TEMPO, f"FINN: PODER MÁGICO, combo de {COMBO_MAXIMO} deixa ele invisível")
for _ in range(30):
    p.passo(None)
    p.desenhar(tela)
checar(0 < f.invisivel < INVISIVEL_TEMPO, "FINN: a invisibilidade vai acabando (e desenha sem quebrar)")
rodar(p, INVISIVEL_TEMPO)
checar(f.invisivel == 0, "FINN: depois de 3 segundos aparece de novo")

# =====================================================================
# KUN
# =====================================================================
KUN = next(f for f in PERSONAGENS if f["nome"] == "KUN")


def contra_kun(passos_kun, passos_alvo=(), distancia=None):
    p = Partida(KUN, ALVO, Roteiro(passos_kun), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


p = contra_kun([Entrada(5, especial="E")], distancia=350)
rodar(p, 90)
checar(dano(p) == 5, f"KUN: carta tira 5 ({dano(p)})")
p = contra_kun([Entrada(5, especial="Q")], distancia=70)
altura = 0
for _ in range(120):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) == 25 and altura > 80 and p.L[0].no_chao(),
       f"KUN: shoryuken de carta tira 25 e joga pra cima ({dano(p)}, {int(altura)} px)")
p = contra_kun([Entrada(5, especial="R")], distancia=95)
rodar(p, 120)
checar(dano(p) == 18, f"KUN: carta-espada dá 6 hits de 3 ({dano(p)})")
p = contra_kun([Entrada(5, especial="SHIFT")], distancia=500)
x0 = p.L[0].x
rodar(p, 60)
checar(dano(p) == 0 and abs(p.L[0].x - x0 - 300) < 2, f"KUN: teleporte da carta (andou {int(p.L[0].x - x0)} px, 0 de dano)")
p = contra_kun([Entrada(5, especial="SHIFT")], distancia=150)
rodar(p, 60)
checar(p.L[0].x > p.L[1].x and p.L[0].dir == -1, "KUN: dá pra se teleportar pra trás do oponente (e já vira)")
p = contra_kun([Entrada(5, especial="Z")], distancia=330)
p.L[0].barra = BARRA_MAX
rodar(p, 400)
checar(abs(dano(p) - 35) < 0.01, f"KUN: ultimate da carta dos móveis tira 35 ({dano(p):.1f})")
p = contra_kun([Entrada(5, especial="Z")], [Entrada(6)] * 500, distancia=330)
p.L[0].barra = BARRA_MAX
rodar(p, 400)
checar(dano(p) < 12 and p.L[1].estado != "tonto", f"KUN: defendendo os móveis leva bem menos ({dano(p):.1f})")
p = contra_kun([], distancia=350)
k = p.L[0]
rodar(p, 15 * 60 + 2)
checar(k.as_ativo > 0, "KUN: ÁS NA MANGA acende depois de 15 segundos")
k.ctrl_teste = None
p.ctrl[0].passos = [Entrada(5, especial="E")]
rodar(p, 60)
checar(dano(p) == 10, f"KUN: com o ás aceso a carta tira 5 + 5 ({dano(p)})")
rodar(p, 5 * 60)
checar(k.as_ativo == 0 and 0 < k.as_t < 15 * 60, "KUN: o ás apaga depois de 5 segundos e começa a contar de novo")
for _ in range(10):
    p.desenhar(tela)

# =====================================================================
# XENOMORPH
# =====================================================================
XENO = next(f for f in PERSONAGENS if f["nome"] == "XENOMORPH")


def contra_xeno(passos_xeno, passos_alvo=(), distancia=None):
    p = Partida(XENO, ALVO, Roteiro(passos_xeno), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


p = contra_xeno([Entrada(5, especial="E")], distancia=250)
rodar(p, 40)
d_cuspe = dano(p)
checar(d_cuspe == 8 and p.L[0].extra.get("pocas"), f"XENO: cuspe de ácido tira 8 e deixa poça ({d_cuspe})")
rodar(p, 200)
checar(dano(p) == 11 and not p.L[0].extra.get("pocas"), f"XENO: a poça queima 1 por segundo e some em 3 s ({dano(p)})")
p = contra_xeno([Entrada(5, especial="Q")], distancia=90)
altura = 0
for _ in range(80):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) == 15 and altura > 80, f"XENO: rabada tira 15 e joga pra cima ({dano(p)}, {int(altura)} px)")
p = contra_xeno([Entrada(5, especial="R")], distancia=95)
rodar(p, 100)
checar(dano(p) == 18, f"XENO: garras dão 6 hits de 3 ({dano(p)})")
p = contra_xeno([Entrada(5, especial="SHIFT")], distancia=300)
rodar(p, 50)
checar(dano(p) == 6, f"XENO: rasteja tira 6 ({dano(p)})")
p = contra_xeno([Entrada()] * 8 + [Entrada(5, especial="SHIFT")], distancia=500)
p.L[1].f = dict(p.L[1].f, golpes={"E": "max_laser"})
p2 = Partida(XENO, CANNAN, Roteiro([Entrada()] * 14 + [Entrada(5, especial="SHIFT")]),
             Roteiro([Entrada(5, especial="E")]))
p2.fase = "luta"
p2.L[1].x = p2.L[0].x + 330
rodar(p2, 60)
checar(p2.L[0].vida == 100, "XENO: rastejando passa por baixo dos tiros (a pistola do Cannan)")
p = contra_xeno([Entrada(5, especial="Z")], distancia=250)
p.L[0].barra = BARRA_MAX
pegou = False
for _ in range(260):
    p.passo(None)
    pegou |= "pegou" in p.L[0].memo
    if pegou:
        p.desenhar(tela)
checar(pegou and dano(p) == 35 and p.L[0].estado != "ataque", f"XENO: SEGUNDA BOCA pega e tira 35 ({dano(p)})")
p = contra_xeno([Entrada(5, especial="Z")], [Entrada()] * 10 + [Entrada(8)] * 3, distancia=280)
p.L[0].barra = BARRA_MAX
rodar(p, 200)
checar(dano(p) == 0, f"XENO: pulando, a ultimate erra ({dano(p)})")
p = Partida(MAX, XENO, Roteiro([Entrada(5, soco=True)]), Roteiro([]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 80
rodar(p, 30)
checar(p.L[0].vida == 100 - 1 and p.L[1].vida < 100, f"XENO: SANGUE ÁCIDO, quem soca leva 1 ({p.L[0].vida})")
p = Partida(CANNAN, XENO, Roteiro([Entrada(5, especial="E")]), Roteiro([]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 300
rodar(p, 80)
checar(p.L[0].vida == 100, "XENO: tiro de longe não queima com o sangue ácido")

# =====================================================================
# TAI (sumô)
# =====================================================================
TAI = next(f for f in PERSONAGENS if f["nome"] == "TAI")


def contra_tai(passos_tai, passos_alvo=(), distancia=None):
    p = Partida(TAI, ALVO, Roteiro(passos_tai), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


checar(TAI["vida"] == 120, "TAI: tem 120 de vida")
p = contra_tai([Entrada(5, especial="E")], distancia=300)
rodar(p, 90)
checar(dano(p) == 10, f"TAI: pisão manda onda rasteira que tira 10 ({dano(p)})")
p = contra_tai([Entrada(5, especial="E")], [Entrada()] * 16 + [Entrada(8)] * 3, distancia=300)
rodar(p, 90)
checar(dano(p) == 0, "TAI: pulando, a onda passa por baixo")
p = contra_tai([Entrada(5, especial="Q")], [Entrada(6)] * 80, distancia=80)
altura = 0
for _ in range(80):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) == 20 and altura > 80, f"TAI: agarrão pega mesmo defendendo e arremessa (20, {int(altura)} px)")
p = contra_tai([Entrada(5, especial="R")], distancia=90)
rodar(p, 100)
checar(dano(p) == 16, f"TAI: tapas, 8 de 2 ({dano(p)})")
p = contra_tai([Entrada(5, especial="SHIFT")], distancia=150)
rodar(p, 120)
checar(dano(p) == 12 and p.L[1].x >= PAREDE_D - 3, f"TAI: investida tira 12 e empurra até a parede ({dano(p)}, x={int(p.L[1].x)})")
p = contra_tai([Entrada(5, especial="Z")], distancia=80)
p.L[0].barra = BARRA_MAX
pegou = False
for _ in range(300):
    p.passo(None)
    pegou |= "pegou" in p.L[0].memo
    if pegou and p.tf % 7 == 0:
        p.desenhar(tela)
checar(pegou and dano(p) == 40 and p.L[0].estado != "ataque", f"TAI: YOKOZUNA levanta, pula e senta: 40 ({dano(p)})")
p = contra_tai([Entrada(5, especial="Z")], distancia=300)
p.L[0].barra = BARRA_MAX
rodar(p, 200)
checar(dano(p) == 0, "TAI: de longe a Yokozuna erra (tem que estar colado)")
p = Partida(MAX, TAI, Roteiro([Entrada()] * 3 + [Entrada(5, soco=True)]), Roteiro([Entrada(5, especial="R")]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 85
rodar(p, 12)
checar(p.L[1].estado == "ataque" and p.L[1].vida < 120, "TAI: PESO PESADO, o soco tira vida mas ele continua o golpe")

# =====================================================================
# TAMER (e o lobo)
# =====================================================================
TAMER = next(f for f in PERSONAGENS if f["nome"] == "TAMER")


def contra_tamer(passos, passos_alvo=(), distancia=None, preto=False):
    p = Partida(TAMER, ALVO, Roteiro(passos), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    p.L[0].extra["lobo_cor"] = "preto" if preto else "branco"
    return p


p = contra_tamer([Entrada(5, especial="E")], distancia=260, preto=True)
lobo_longe = 0
for _ in range(80):
    p.passo(None)
    lobo_longe = max(lobo_longe, p.L[0].extra["lobo_x"] - p.L[0].x)
checar(dano(p) == 15 and lobo_longe > 150, f"TAMER: o lobo avança e morde: 15 ({dano(p)}, foi {int(lobo_longe)} px)")
p = contra_tamer([Entrada(5, especial="Q")], distancia=90, preto=True)
p.L[0].x = 600
p.L[1].x = 700
subiu, bateu_parede = 0, False
for _ in range(120):
    p.passo(None)
    bateu_parede |= p.L[1].x >= PAREDE_D - 2
    if bateu_parede:
        subiu = max(subiu, CHAO - p.L[1].y)
checar(dano(p) == 20 and bateu_parede and subiu > 60,
       f"TAMER: chute joga na parede (15 + 5) e ele sobe ({dano(p)}, {int(subiu)} px)")
p = contra_tamer([Entrada(5, especial="R")], distancia=95, preto=True)
rodar(p, 120)
checar(dano(p) == 24, f"TAMER: combo com o lobo, 8 de 3 ({dano(p)})")
p = contra_tamer([Entrada(5, especial="SHIFT")], distancia=400, preto=True)
x0 = p.L[0].x
rodar(p, 80)
checar(dano(p) == 10 and p.L[0].x - x0 > 150, f"TAMER: galope no lobo tira 10 ({dano(p)})")
p = contra_tamer([Entrada(5, especial="Z")], distancia=250, preto=True)
p.L[0].barra = BARRA_MAX
pegou = False
for _ in range(300):
    p.passo(None)
    pegou |= "pegou" in p.L[0].memo
    if pegou and p.tf % 9 == 0:
        p.desenhar(tela)
checar(pegou and dano(p) == 35, f"TAMER: A ALCATEIA (3 lobos) tira 35 ({dano(p)})")
p = contra_tamer([Entrada(5, especial="Z")], [Entrada(6)] * 300, distancia=250)
p.L[0].barra = BARRA_MAX
rodar(p, 200)
checar(dano(p) == 0, "TAMER: defendendo, a alcateia passa direto")
lobo = Entrada(5)
lobo.lobo = True
p = contra_tamer([lobo], distancia=300)
rodar(p, 3)
checar(p.L[0].extra["lobo_cor"] == "preto", "TAMER: X troca o lobo branco pelo preto")
b = contra_tamer([Entrada(5, especial="R")], distancia=95)
rodar(b, 120)
checar(abs(dano(b) - 30) < 0.01, f"TAMER: LOBO BRANCO = +25% de dano (24 -> {dano(b)})")
duracao = []
for preto in (False, True):
    p = contra_tamer([Entrada(5, especial="R")], distancia=95, preto=preto)
    q = 0
    p.passo(None)
    while p.L[0].estado == "ataque" and q < 300:
        rodando = not p.parada  # (não conta o congelamento de cada hit)
        p.passo(None)
        q += rodando
    duracao.append(q)
    if preto:
        checar(dano(p) == 24, f"TAMER: com o LOBO PRETO o combo acerta tudo igual ({dano(p)})")
checar(duracao[1] < duracao[0] * 0.75, f"TAMER: LOBO PRETO = ataques 50% mais rápidos ({duracao[0]} -> {duracao[1]} quadros)")
andou = []
for preto in (False, True):
    p = contra_tamer([Entrada(6)] * 30, distancia=500, preto=preto)
    x0 = p.L[0].x
    rodar(p, 30)
    andou.append(p.L[0].x - x0)
checar(andou[0] == andou[1], "TAMER: o lobo preto não muda a velocidade de andar")
p = Partida(TAMER, CANNAN, Roteiro([]), Roteiro([]), cenario_nome="SELVA")
for _ in range(DURACAO_ENTRADA + 30):
    p.passo(None)
    if p.tf % 11 == 0:
        p.desenhar(tela)
checar(p.fase in ("intro", "luta"), "TAMER: entra correndo com o lobo (na SELVA)")

# ---- PROVOCAÇÃO ----

p = contra_cannan([Entrada(5)] * 2, distancia=400)
e = Entrada(5)
e.provoca = True
p.ctrl[0].passos = [e]
b0 = p.L[0].barra
rodar(p, 90)
checar(p.L[0].barra == b0 + PROVOCA_BARRA and p.L[0].provocou == 1 and p.L[0].estado == "parado",
       f"PROVOCAÇÃO: T provoca e enche a barra ({p.L[0].barra - b0})")
p = contra_cannan([e], [Entrada(5)] * 20 + [Entrada(5, especial="E")], distancia=300)
p.L[1].f = dict(p.L[1].f)
p2 = Partida(CANNAN, CANNAN, Roteiro([e]), Roteiro([Entrada(5)] * 10 + [Entrada(5, especial="E")]))
p2.fase, p2.tf = "luta", 0
p2.L[1].x = p2.L[0].x + 300
b0 = p2.L[0].barra
rodar(p2, 90)
checar(p2.L[0].provocou == 0, "PROVOCAÇÃO: se apanhar no meio, não enche a barra")
for f in PERSONAGENS:
    pz = Partida(f, ALVO, Roteiro([e]), Roteiro([]))
    pz.fase = "luta"
    for _ in range(40):
        pz.passo(None)
        pz.desenhar(tela)
checar(True, "PROVOCAÇÃO: todo mundo provoca (com a frase) sem quebrar")
j = Jogador()
pj = partida_com(Roteiro([]), Roteiro([]))
checar(j.ler(quadro((PROVOCA,)), pj.L[0], pj.L[1], pj).provoca, "PROVOCAÇÃO: a tecla T funciona")

# ---- TRANSIÇÃO DE CENÁRIO ----
import transicao  # noqa: E402
p = Partida(CANNAN, ALVO, Roteiro([]), Roteiro([]), cenario_nome="FERRO-VELHO")
p.fase, p.tf = "luta", 0
v = p.L[1]
v.x = PAREDE_D - 30
v.voar(1, 9, 6)
v.voo_forte = True
vida0 = v.vida
viu = False
for _ in range(200):
    p.passo(None)
    viu |= p.cutscene is not None
    if viu:
        p.desenhar(tela)
    if viu and p.cutscene is None:
        break
checar(viu and p.cena.nome == "CAMPO DE BATALHA" and vida0 - v.vida == transicao.DANO and p.stats["transicoes"] == 1,
       f"TRANSIÇÃO: voou forte na parede e caiu no CAMPO DE BATALHA (-{vida0 - v.vida})")
v.mudar("parado")
v.x = PAREDE_D - 30
v.voar(1, 9, 6)
v.voo_forte = True
rodar(p, 60)
checar(p.cena.nome == "CAMPO DE BATALHA" and p.cutscene is None, "TRANSIÇÃO: só uma vez por round")
p = Partida(CANNAN, ALVO, Roteiro([]), Roteiro([]), cenario_nome="DOJO")
p.fase = "luta"
v = p.L[1]
v.x = PAREDE_D - 20
v.voar(1, 3, 6)
rodar(p, 60)
checar(p.cena.nome == "DOJO", "TRANSIÇÃO: golpe fraco não atravessa a parede")
checar(all(d in cenarios.CENARIOS for d in transicao.DESTINOS.values()) if (cenarios := __import__("cenarios")) else False,
       "TRANSIÇÃO: todo cenário vizinho existe")

# ---- DESAFIOS ----
import desafios  # noqa: E402
save.carregar()
lista = desafios.ativos()
checar(len(lista) == 3 and len({d["tipo"] for d in lista}) == 3, "DESAFIOS: sempre tem 3 diferentes valendo")
lista[0] = dict(tipo="parrys", alvo=3, prog=2, premio=40)
lista[1] = dict(tipo="combo", alvo=8, prog=0, premio=55)
lista[2] = dict(tipo="vencer_com", alvo=2, prog=0, premio=40, p="RIB")
resumo = dict(parrys=1, quebras=0, ults=0, tomou_ult=False, provocacoes=0, transicoes=0, venceu=True,
              personagem="RIB", nivel="MÉDIO", combo=5, bom=False, sobrev=0)
feitos = desafios.atualizar(resumo)
lista = desafios.ativos()
checar(feitos == [("Faça 3 PARRYS", 40)] and lista[0]["tipo"] != "parrys" and lista[1]["prog"] == 5 and lista[2]["prog"] == 1,
       "DESAFIOS: conta o progresso, paga e troca o cumprido por um novo")
for t in desafios.TIPOS:
    d = desafios.novo()
    d["tipo"] = t
    d.setdefault("p", "RIB")
    desafios.avancar(d, resumo)
    desafios.texto_de(d)
checar(True, "DESAFIOS: todos os tipos funcionam")
td = desafios.TelaDesafios()
for _ in range(10):
    td.desenhar(tela)
checar(True, "DESAFIOS: a tela desenha")

# ---- DESAFIOS DE COMBO ----
from combos import BotCombo, TreinoCombos  # noqa: E402
from controles import BonecoTreino  # noqa: E402
from personagens import SECRETOS as _SECRETOS  # noqa: E402
falhou = []
for f in PERSONAGENS + _SECRETOS:
    for i in range(5):
        p = Partida(f, boneco(0), Roteiro([]), BonecoTreino(), treino=True)
        tc = TreinoCombos(f)
        tc.i = i
        p.combos = tc
        p.ctrl = (BotCombo(tc), p.ctrl[1])
        tc.arrumar(p)
        for _ in range(700):
            p.passo(None)
            if tc.completo_t:
                break
        if not tc.completo_t:
            falhou.append(f"{f['nome']} {i + 1}")
checar(not falhou, f"COMBOS: todos os {5 * len(PERSONAGENS + _SECRETOS)} combos dá pra fazer de verdade (o robô fez; falhou: {falhou})")
save.carregar()
save.d()["combos"] = {}
m0 = save.moedas()
p = Partida(KUN, boneco(0), Jogador(), BonecoTreino(), treino=True)
tc = p.combos = TreinoCombos(KUN)
tc.arrumar(p)
tc.feito = 2
tc.completou()
checar(save.moedas() == m0 + tc.atual["moedas"] and 0 in save.d()["combos"]["KUN"], "COMBOS: completou a primeira vez, ganha moedas")
tc.limpar()
tc.completou()
checar(save.moedas() == m0 + tc.atual["moedas"], "COMBOS: fazer de novo não ganha de novo")
tc.limpar()
tc.i = 1
tc.comecar_demo(p)
m1 = save.moedas()
for _ in range(400):
    p.passo(quadro())
    p.desenhar(tela)
checar(save.moedas() == m1 and not tc.demo and isinstance(p.ctrl[0], Jogador),
       "COMBOS: a demonstração mostra o combo, não dá moeda e devolve o controle")
tc.limpar()
tc.feito = 2
p.combos.passo(p)
checar(tc.feito == 0 and tc.caiu_t > 0, "COMBOS: se o boneco se soltar, o combo cai")

# ---- ONLINE (sem internet: os dois jogos se ligam direto, no mesmo PC) ----
import time  # noqa: E402
from online import Online  # noqa: E402
from rede import Conexao, codifica, conferencia, decodifica  # noqa: E402
ok = True
for d in range(1, 10):
    for esp in (None, "E", "Q", "R", "SHIFT", "Z"):
        e = Entrada(d, d % 2 == 0, d % 3 == 0, esp)
        e.segura_ult, e.provoca = d > 5, d == 7
        x = decodifica(codifica(e))
        ok &= (x.dir, x.soco, x.chute, x.especial, x.segura_ult, x.provoca) == (d, e.soco, e.chute, esp, d > 5, d == 7)
checar(ok, "ONLINE: os botões viram número e voltam iguais")


def dois_robos(modo="1x1", regras=(), acabou=lambda a, b: a.estado == b.estado == "fim", limite=120):
    """Dois jogos ligados direto (no mesmo PC), cada um com o robô jogando. Roda até acabou(a, b)."""
    porta_b = []
    ca = Conexao(True, pares_diretos=lambda: [("127.0.0.1", porta_b[0])] if porta_b else None)
    cb = Conexao(False, pares_diretos=[("127.0.0.1", ca.sock.getsockname()[1])])
    porta_b.append(cb.sock.getsockname()[1])
    a, b = Online(robo_modo=modo), Online()
    a.robo = b.robo = True
    a.regras = set(regras)
    a.con, b.con = ca, cb
    a.estado = b.estado = "conectando"
    t0 = time.time()
    n = 0
    while time.time() - t0 < limite and not acabou(a, b):
        for o in (a, b):
            o.tick(None)
            if o.estado == "vs":
                o.vs.t = o.vs.DURACAO
                o.desenhar(tela)
            elif n % 97 == 0:
                o.desenhar(tela)
        n += 1
        if "erro" in (a.estado, b.estado):
            break
        time.sleep(0.0005)
    return a, b


oa, ob = dois_robos()
checar(oa.estado == ob.estado == "fim" and conferencia(oa.partida) == conferencia(ob.partida)
       and oa.partida.vencedor == ob.partida.vencedor and not (oa.dessinc or ob.dessinc),
       f"ONLINE: os dois jogos lutam a mesma luta até o fim ({oa.estado}, {ob.estado})")
oa.voltar_menu()
ob.voltar_menu()
oa, ob = dois_robos("trio", ["cabecoes"])
checar(oa.estado == ob.estado == "fim" and oa.partida.trio and ob.partida.regras == {"cabecoes"}
       and conferencia(oa.partida) == conferencia(ob.partida) and not (oa.dessinc or ob.dessinc),
       f"ONLINE TRIO: 3 x 3 com MODO MALUCO, igual nos dois PCs até o fim ({oa.estado}, {ob.estado})")
oa.voltar_menu()
ob.voltar_menu()


def torneio_acabou(a, b):
    return all(o.torneio is not None and o.torneio.campeao is not None and o.estado == "torneio" for o in (a, b))


oa, ob = dois_robos("torneio", acabou=torneio_acabou, limite=400)
ok = torneio_acabou(oa, ob)
if ok:
    ta, tb = oa.torneio, ob.torneio
    ok = ta.resultados == tb.resultados and ta.campeao == tb.campeao
    ok &= sum(x["humano"] for x in ta.lutadores) == 1 and sum(x.get("amigo", False) for x in ta.lutadores) == 1
    eu_a = next(i for i, x in enumerate(ta.lutadores) if x["humano"])
    eu_b = next(i for i, x in enumerate(tb.lutadores) if x["humano"])
    ok &= (eu_a < 4) != (eu_b < 4)  # um em cada metade da chave
    for o in (oa, ob):
        o.desenhar(tela)
checar(ok, f"ONLINE TORNEIO: vocês 2 + 6 computadores, a chave sai igual nos dois PCs ({oa.estado}, {ob.estado})")
oa.confirma_sair = True
oa.limpar_luta()
checar(not oa.confirma_sair, "ONLINE TORNEIO: a pausa some quando a tela muda (não volta depois da final)")
from selecao import TelaCenario  # noqa: E402
tc = TelaCenario("SELVA")
tc.nomes = tc.nomes + ["X"] * (13 - len(tc.nomes))  # (finge 13 cenários: 14 casas, a última fileira incompleta)
ok = True
for i in range(len(tc.nomes) + 1):
    for tecla in (pygame.K_w, pygame.K_s):
        tc.cursor = i
        tc.tecla(tecla)
        ok &= tc.cursor % tc.COLUNAS == i % tc.COLUNAS and 0 <= tc.cursor <= len(tc.nomes)
checar(ok, "CENÁRIO: W/S fica na mesma coluna (mesmo com a última fileira incompleta)")
oa.voltar_menu()
ob.voltar_menu()

# ---- RIBBAT (secreto) e CÓDIGOS ----
import codigos  # noqa: E402
from personagens import SECRETOS, disponiveis  # noqa: E402
RIBBAT = SECRETOS[0]
save.carregar()
save.d()["codigos"] = []
checar(RIBBAT not in disponiveis(), "RIBBAT: escondido antes do código")
ok = codigos.usar("Ultra-Mega-Skins") and all(save.tem_roupa("RIBBAT", c) for c in
                                                ("bone", "folha", "gato", "besouro", "coroa", "pena", "cartola"))
checar(ok, "CÓDIGOS: ULTRA-MEGA-SKINS dá os 7 chapéus do Ribbat")
for c in ("coroa", "folha", "cartola"):
    p = Partida(roupas.vestir(RIBBAT, c), ALVO, Roteiro([]), Roteiro([]))
    for _ in range(30):
        p.passo(None)
    p.desenhar(tela)
save.usar("RIBBAT", "padrao")
from abertura import Abertura  # noqa: E402
ab = Abertura()
while not ab.acabou:
    ab.desenhar(tela)
checar(ab.t == Abertura.DURACAO, "ABERTURA: raio no meio -> fogo cobre a tela -> aparece o símbolo e BATTLE WISH")
checar(codigos.usar("ultra-mega-sapo") is None and RIBBAT not in disponiveis(), "CÓDIGOS: código errado não faz nada")
checar(codigos.usar("ultra-mega-frog") and RIBBAT in disponiveis(), "CÓDIGOS: ULTRA-MEGA-FROG desbloqueia o RIBBAT")
secretas = {"Iron Man": ("MAX-10", "wartank"), "Fenrir": ("TAMER", "zeus"), "Mega-Cannon": ("CANNAN", "megacannon"),
            "Fightmon": ("RIB", "greninja"), "Dinowolf": ("TRAFO", "indoraptor")}
checar(all(not save.tem_roupa(n, r) for n, r in secretas.values()), "CÓDIGOS: as roupas secretas começam trancadas")
ok = all(codigos.usar(c) and save.tem_roupa(n, r) and save.usando(n) == r for c, (n, r) in secretas.items())
checar(ok, "CÓDIGOS: Iron Man, Fenrir, Mega-Cannon, Fightmon e Dinowolf dão as roupas secretas (e já vestem)")
zeus = roupas.vestir(TAMER, "zeus")
checar(zeus["lobo"] and zeus["lobo"]["tam"] > 1 and roupas.vestir(TAMER, "padrao")["lobo"] is None,
       "CÓDIGOS: na roupa ZEUS o lobo vira o FENRIR (maior, olho vermelho)")
p = Partida(zeus, ALVO, Roteiro([]), Roteiro([]))
for _ in range(40):
    p.passo(None)
p.desenhar(tela)
for n, r in secretas.values():
    save.usar(n, "padrao")
import cenarios  # noqa: E402
checar("VILA DOS SAPOS" not in cenarios.disponiveis(), "CÓDIGOS: a VILA DOS SAPOS começa escondida")
checar(codigos.usar("Ultra-Mega-Village") and "VILA DOS SAPOS" in cenarios.disponiveis()
       and "VILA DOS SAPOS" in TelaCenario("SELVA").nomes, "CÓDIGOS: ULTRA-MEGA-VILLAGE libera o cenário secreto")
p = Partida(TAMER, ALVO, Roteiro([]), Roteiro([]), cenario_nome="VILA DOS SAPOS")
for _ in range(30):
    p.passo(None)
p.desenhar(tela)
todos = PERSONAGENS + [RIBBAT]
checar(not any(save.tem_roupa(f["nome"], "sombra") or save.tem_roupa(f["nome"], "ouro") for f in todos),
       "CÓDIGOS: SOMBRA e OURO começam trancadas")
ok = bool(codigos.usar("TheDarkestDummy") and codigos.usar("BruteFortune"))
ok &= all(save.tem_roupa(f["nome"], "sombra") and save.tem_roupa(f["nome"], "ouro") for f in todos)
checar(ok, "CÓDIGOS: THEDARKESTDUMMY e BRUTEFORTUNE dão SOMBRA e OURO pra todo mundo (até o Ribbat)")
for f in todos:
    for r in ("sombra", "ouro"):
        p = Partida(roupas.vestir(f, r), ALVO, Roteiro([]), Roteiro([]))
        for _ in range(3):
            p.passo(None)
        p.desenhar(tela)
        Lutador(roupas.vestir(f, r), 300, 1).desenhar(tela)  # (o desenho da seleção/loja também)
from loja import TelaLoja  # noqa: E402
lj = TelaLoja(PERSONAGENS + [RIBBAT])
cabe = True
for i in range(len(lj.lista)):
    lj.i = i
    lj.desenhar(tela)
    cabe &= lj.rect_roupa(len(lj.roupas()) - 1).bottom < 400
checar(cabe, "LOJA: muitas roupas ainda cabem na tela (até as 10 do Ribbat)")
sel = TelaSelecao(PERSONAGENS)
sel.cursor[0] = 0
sel.confirmar()
i_tai = next(i for i, f in enumerate(PERSONAGENS) if f["nome"] == "TAI")
sel.cursor[1] = i_tai
save.d()["roupas"].setdefault("TAI", []).append("luchador")
sel.tecla(pygame.K_e)
sel.desenhar(tela)
roupa_tai = sel.roupa_bot.get("TAI")
sel.confirmar()
jogo.sel, jogo.modo, jogo.lista = sel, luta.UM, PERSONAGENS
jogo.escolha = [i if i is not None else 0 for i in sel.escolhido]
_, f2 = jogo.fichas_da_luta()
checar(roupa_tai == "luchador" and f2["roupa"] == "luchador" and f2.get("orelhas"),
       f"SELEÇÃO: Q/E escolhe a roupa do BOT (o Tai vem de SHREK: {f2['roupa']})")
p = Partida(f2, roupas.vestir(next(f for f in PERSONAGENS if f["nome"] == "KUN"), "coringa"), Roteiro([]), Roteiro([]))
for _ in range(20):
    p.passo(None)
p.desenhar(tela)
save.carregar()
checar(RIBBAT in disponiveis(), "CÓDIGOS: o desbloqueio fica salvo")
from online import Online as _On  # noqa: E402
checar(all(f.get("secreto") is not True for f in PERSONAGENS), "RIBBAT: não aparece no online (fica fora da lista normal)")


def contra_ribbat(passos, passos_alvo=(), distancia=None):
    p = Partida(RIBBAT, ALVO, Roteiro(passos), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


p = contra_ribbat([Entrada(5, especial="E")], distancia=150)
rodar(p, 80)
checar(dano(p) == 35, f"RIBBAT: linguada tira 35 ({dano(p)})")
p = contra_ribbat([Entrada(5, especial="SHIFT")], distancia=300)
inv = False
for _ in range(60):
    p.passo(None)
    inv |= p.L[0].inv > 0 and p.L[0].estado == "ataque"
checar(dano(p) == 50 and inv, f"RIBBAT: investida tira 50 e fica invulnerável ({dano(p)})")
p = contra_ribbat([Entrada(5, especial="Z")], distancia=300)
p.L[0].barra = BARRA_MAX
for q in range(420):
    p.passo(None)
    if q % 9 == 0:
        p.desenhar(tela)
checar(p.L[1].vida == 0 and p.fase in ("ko", "fim"), f"RIBBAT: os chefões dão HIT KILL ({p.L[1].vida})")
p = Partida(RIBBAT, CANNAN, Roteiro([]), Roteiro([]))
for _ in range(DURACAO_ENTRADA + 5):
    p.passo(None)
    p.desenhar(tela)
checar(p.fase in ("intro", "luta") and p.L[0].x == p.L[0].extra["entrada_x"], "RIBBAT: entra pulando")
import ribbat_lutador  # noqa: E402
checar(RIBBAT["desenho"] is ribbat_lutador.desenhar_ribbat, "RIBBAT: usa o sprite de verdade do jogo dele")
p = Partida(MAX, RIBBAT, Roteiro([Entrada(5, soco=True)]), Roteiro([]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 75
rodar(p, 20)
pq = p.L[1].vida == 100
p = Partida(MAX, RIBBAT, Roteiro([Entrada(2, chute=True)]), Roteiro([]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 75
rodar(p, 30)
checar(pq and p.L[1].vida < 100, "RIBBAT: pequenininho, o soco em pé passa por cima (só golpe baixo pega)")

# ---- CONTROLE DE VIDEOGAME ----
import controle_video  # noqa: E402


class ControleFalso:
    def __init__(self):
        self.botoes, self.eixos = set(), {}

    def get_button(self, b):
        return b in self.botoes

    def get_axis(self, a):
        return self.eixos.get(a, 0)


cf = ControleFalso()
j = Jogador(controle=cf, teclado=False)
cf.botoes = {pygame.CONTROLLER_BUTTON_A}
e1 = j.ler(None, None, None, None)
e2 = j.ler(None, None, None, None)
cf.botoes = {pygame.CONTROLLER_BUTTON_X, pygame.CONTROLLER_BUTTON_DPAD_RIGHT}
e3 = j.ler(None, None, None, None)
cf.botoes = set()
cf.eixos = {pygame.CONTROLLER_AXIS_LEFTY: 32000, pygame.CONTROLLER_AXIS_TRIGGERRIGHT: 32000}
e4 = j.ler(None, None, None, None)
checar(e1.soco and not e2.soco and e3.especial == "E" and e3.dir == 6 and e4.dir == 2 and e4.segura_ult,
       "CONTROLE: A soca (uma vez), X = E, direcional e analógico andam, RT segura a ultimate")
j2 = Jogador(controle=cf)
cf.eixos = {}
cf.botoes = {pygame.CONTROLLER_BUTTON_B}
e5 = j2.ler(quadro(), None, None, None)
checar(e5.chute, "CONTROLE: o jogador 1 pode usar teclado e controle juntos")
ev = pygame.event.Event(pygame.CONTROLLERBUTTONDOWN, button=pygame.CONTROLLER_BUTTON_A, instance_id=0)
checar(controle_video.tecla_do_evento(ev, False) == pygame.K_RETURN and controle_video.tecla_do_evento(ev, True) is None,
       "CONTROLE: nos menus o A confirma (na luta não)")

# ---- A IA NÃO ESCAPA NO MEIO DE ESPECIAL (pedido do Gomes: "é meio paia") ----


def ia_escapa(golpe):
    """Quantas vezes (em 400 tentativas) a IA no DIFÍCIL, com a barra cheia, escapa de um combo de 5 hits."""
    p = Partida(KING, ALVO, Roteiro([]), Roteiro([]))
    ele, eu = p.L
    ele.comecar(golpe)
    ele.combo = 5
    eu.mudar("golpeado")
    eu.barra = BARRA_MAX
    ia = Computador("DIFÍCIL")
    return sum(bool(getattr(ia.ler(None, eu, ele, p), "barra_toque", False)) for _ in range(400))


KING = next(f for f in PERSONAGENS if f["nome"] == "KING RIP")
esp, normal = ia_escapa(KING["golpes"]["R"]), ia_escapa("soco")
checar(esp == 0 and normal > 0, f"IA: não dá ESCAPE no meio de especial ({esp}), só em combo de soco/chute ({normal})")

# ---- EX E ESCAPE DE COMBO ----
def com_barra(e):
    e.barra = True
    return e


p = contra_kun([com_barra(Entrada(5, especial="E"))], distancia=350)
p.L[0].barra = 300
rodar(p, 3)
rodar(p, 120)
checar(dano(p) == 15 and p.L[0].barra < 300, f"EX do E: gasta 1/4 da barra e a carta vira 3 ({dano(p)})")
p = contra_kun([com_barra(Entrada(5, especial="R"))], distancia=100)
p.L[0].barra = 300
rodar(p, 220)
checar(dano(p) == 36, f"EX do R: o dobro de ataques (12 de 3 = {dano(p)})")
p = contra_kun([com_barra(Entrada(5, especial="Q"))], distancia=80)
p.L[0].barra = 300
altura = 0
for _ in range(160):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) > 25 and altura > 60, f"EX do Q: rasteira + soco + shoryuken ({dano(p)}, {int(altura)} px)")
p = contra_kun([com_barra(Entrada(5, especial="SHIFT"))], distancia=500)
p.L[0].barra = 300
x0 = p.L[0].x
mais_longe = x0
for _ in range(90):
    p.passo(None)
    mais_longe = max(mais_longe, p.L[0].x)
checar(mais_longe - p.L[0].x > 100, f"EX do SHIFT: vai e depois dá um dash pra trás ({int(mais_longe - x0)}, voltou "
       f"{int(mais_longe - p.L[0].x)})")
p = Partida(MAX, ALVO, Roteiro([com_barra(Entrada(5, especial="E"))]), Roteiro([]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 300
p.L[0].barra = 300
rodar(p, 120)
checar(dano(p) > 8, f"EX do E que não é tiro (laser do Max): bate 1,5x ({dano(p)})")
p = contra_kun([com_barra(Entrada(5, especial="R"))], distancia=100)
p.L[0].barra = 100
rodar(p, 120)
checar(dano(p) == 18, f"EX: sem barra suficiente sai o normal ({dano(p)})")
fuga = Entrada(5)
fuga.barra_toque = True
p = Partida(KING, ALVO, Roteiro([Entrada(5, especial="R")]), Roteiro([Entrada()] * 30 + [fuga]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 100
p.L[1].barra = 600
rodar(p, 120)
checar(dano(p) < 20 and p.L[1].barra < 600, f"ESCAPE: tocar F apanhando se solta do combo ({dano(p)} de 20)")
p = Partida(KING, ALVO, Roteiro([Entrada(5, especial="R")]), Roteiro([Entrada()] * 30 + [fuga]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 100
p.L[1].barra = 200
rodar(p, 120)
checar(dano(p) == 20, "ESCAPE: sem meia barra não escapa")

# ---- VIBRAÇÃO, BOTÕES NA TELA E CAIXAS ----
class ControleQueTreme(ControleFalso):
    def __init__(self):
        super().__init__()
        self.tremidas = []

    def rumble(self, baixo, alto, ms):
        self.tremidas.append((round(alto, 2), ms))


ct = ControleQueTreme()
p = Partida(MAX, ALVO, Roteiro([Entrada()] * 3 + [Entrada(5, especial="E")]), Roteiro([]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 300
p.controles_vibra = [None, ct]
rodar(p, 120)
checar(ct.tremidas and max(t[0] for t in ct.tremidas) >= 0.5, f"VIBRAÇÃO: quem apanha sente o controle tremer ({ct.tremidas[:3]})")
ct2 = ControleQueTreme()
p = contra_tai([Entrada(5, especial="Z")], distancia=80)
p.L[0].barra = BARRA_MAX
p.controles_vibra = [None, ct2]
rodar(p, 300)
checar(any(t == (1.0, 450) for t in ct2.tremidas), "VIBRAÇÃO: a Yokozuna do Tai treme no máximo")
controle_video.CONTROLES[:] = [cf]
controle_video.usando = "controle"
checar(controle_video.nome("E") == "X" and controle_video.nome("soco") == "A" and controle_video.nome("Z") == "RT",
       "BOTÕES: no controle a tela mostra X, A, RT...")
from efeitos import texto_botao  # noqa: E402
texto_botao(tela, "SHIFT", "investida", 16, BRANCO, (480, 300))
jogo.partida = Partida(KUN, ALVO, Jogador(controle=cf), Roteiro([]))
jogo.desenhar_pausa()
controle_video.usando = "teclado"
checar(controle_video.nome("E") == "M3+E" and controle_video.nome("soco") == "M1", "BOTÕES: no teclado continua M1, M3+E...")
controle_video.CONTROLES[:] = []
p = contra_kun([Entrada(5, especial="R")], distancia=100)
p.treino = True
p.ver_caixas = True
for _ in range(20):
    p.passo(None)
p.desenhar(tela)
checar(True, "CAIXAS: o treino desenha as caixas de acerto (tecla H)")

# ---- MODOS MALUCOS ----
def pulo_mais_alto(regras):
    e = Entrada(8)
    p = contra_kun([e], distancia=400)
    p.regras.update(regras)
    for l in p.L:
        l.regras = p.regras
    alto = 0
    for _ in range(120):
        p.passo(None)
        alto = max(alto, CHAO - p.L[0].y)
    return alto


normal, lua = pulo_mais_alto(set()), pulo_mais_alto({"lua"})
checar(lua > normal * 1.8, f"MALUCOS: na LUA pula bem mais alto ({int(normal)} -> {int(lua)} px)")
p = contra_kun([Entrada(5, especial="E")], distancia=350)
p.regras.add("um_golpe")
rodar(p, 90)
checar(p.L[1].vida == 0, "MALUCOS: UM GOLPE MATA (a cartinha de 5 derruba)")
p = contra_kun([Entrada(5, especial="E")], [Entrada(6)] * 90, distancia=350)
p.regras.add("um_golpe")
rodar(p, 90)
checar(p.L[1].vida > 0, "MALUCOS: defendendo, o UM GOLPE MATA não mata")
k = Lutador(KUN, 300, 1)
k.encher(100)
k2 = Lutador(KUN, 300, 1)
k2.regras = {"so_ultimate"}
k2.encher(100)
checar(k2.barra == 5 * k.barra, "MALUCOS: SÓ ULTIMATE enche a barra 5x mais rápido")
p = contra_kun([], distancia=200)
p.regras.add("cabecoes")
p.desenhar(tela)
import pecas  # noqa: E402
checar(pecas.CABECAO == 1.0, "MALUCOS: CABEÇÕES desenha e depois volta ao normal")
import malucos  # noqa: E402
save.d()["regras"] = ["turbo"]
p = Partida(KUN, ALVO, Jogador(), Computador("MÉDIO"))
p.rounds, p.fase = 1, "ko"
p.L[1].vida = 0
p.regras.update(malucos.ligadas())
for _ in range(300):
    p.passo(quadro())
    if p.fase == "fim":
        break
checar(p.premio is None, "MALUCOS: com modo maluco ligado não ganha moeda")
save.d()["regras"] = []
tm = malucos.TelaMalucos()
tm.tecla(pygame.K_RETURN)
checar(malucos.ligadas() == {"lua"}, "MALUCOS: ENTER liga a regra (e fica salva)")
tm.tecla(pygame.K_RETURN)
tm.desenhar(tela)
checar(malucos.ligadas() == set(), "MALUCOS: ENTER de novo desliga")

# ---- TRIO ----
troca = Entrada(5)
troca.troca = True
eq1, eq2 = [KUN, RIB, TAI], [MAX, CANNAN, FINN]
p = Partida(None, None, Roteiro([Entrada()] * 5 + [troca]), Roteiro([]), trio=(eq1, eq2))
p.fase = "luta"
rodar(p, 30)
checar(p.L[0].f is RIB and p.troca_espera[0] > 0, f"TRIO: G troca de lutador (entrou o {p.L[0].f['nome']})")
p.L[1].vida = 0
p.L[1].mudar("caido")
rodar(p, 40)
checar(p.L[1].f is CANNAN and p.fase == "luta", "TRIO: caiu um, entra o próximo (a luta continua)")
for m in p.equipes[1]:
    m.vida = 0
p.L[1].mudar("caido")
rodar(p, 5)
checar(p.fase == "ko", "TRIO: só perde quando os 3 caem")
for _ in range(5):
    p.desenhar(tela)
p = Partida(None, None, Computador("DIFÍCIL"), Computador("DIFÍCIL"), trio=(eq1, eq2))
for _ in range(60 * 60 * 6):  # (até 3 rounds de 99 segundos)
    p.passo(None)
    if p.fase == "fim":
        break
checar(p.fase == "fim", "TRIO: o computador luta um trio inteiro até o fim")

# ---- TORNEIO ----
from torneio import Torneio, simular  # noqa: E402
checar(simular(KUN, TAI, "MÉDIO") in (0, 1), "TORNEIO: dá pra simular uma luta entre computadores")
t = Torneio(KUN, PERSONAGENS, "MÉDIO")
checar(len(t.lutadores) == 8 and sum(x["humano"] for x in t.lutadores) == 1, "TORNEIO: chave de 8 com você dentro")
lutas = 0
while t.campeao is None and lutas < 10:
    if t.tem_humano():
        _, _, eu_esq = t.fichas_da_luta()
        t.registrar(0 if eu_esq else 1)  # (você ganha todas)
    else:
        t.simular_proxima()
    lutas += 1
    t.desenhar(tela)
m0 = save.moedas()
checar(lutas == 7 and t.lutadores[t.campeao]["humano"], f"TORNEIO: 7 lutas (4+2+1) e você campeão ({lutas})")
jogo.torneio = t
jogo.tela_atual = "torneio"
jogo.torneio_enter()
checar(jogo.tela_atual == "titulo", "TORNEIO: no fim, ENTER volta pro menu")
t = Torneio(KUN, PERSONAGENS, "FÁCIL")
while t.tem_humano():
    t.registrar(0 if t.fichas_da_luta()[2] else 1)
jogo.torneio, jogo.modo, jogo.tela_atual = t, luta.TORNEIO, "torneio"
antes = t.proxima()
jogo.torneio_enter(pular=True)
checar(t.proxima() != antes and jogo.tela_atual == "torneio", "TORNEIO: S pula a luta dos computadores (simula)")
while t.tem_humano():
    t.registrar(0 if t.fichas_da_luta()[2] else 1)
jogo.torneio_enter()
checar(jogo.tela_atual == "vs", "TORNEIO: ENTER na luta dos computadores vai pro VS (assistir)")
jogo.comecar()
p = jogo.partida
checar(all(isinstance(c, Computador) for c in p.ctrl) and p.assistindo and
       p.L[0].f["nome"] == t.lutadores[t.proxima()[0]]["ficha"]["nome"], "TORNEIO: assistindo os dois computadores")
for _ in range(200):
    p.passo(None)
    if p.tf % 20 == 0:
        p.desenhar(tela)
jogo.pular_luta_assistida()
checar(p.fase == "fim", "TORNEIO: ENTER na luta assistida pula pro resultado")
jogo.assistindo = False

# ---- MENU EM 2 COLUNAS ----
jogo.tela_atual = "titulo"
checar("ARCADE" not in luta.MODOS and "CPU x CPU" not in luta.MODOS, "MENU: sem ARCADE e sem CPU x CPU")
jogo.opcao = luta.ONLINE
jogo.titulo(pygame.K_d)
checar(luta.MODOS[jogo.opcao] == "CÓDIGOS", "MENU: D vai pra outra coluna")
jogo.opcao = luta.POR_COLUNA
jogo.titulo(pygame.K_w)
checar(luta.MODOS[jogo.opcao] == "SAIR", "MENU: W no topo dá a volta na coluna")
jogo.opcao = luta.CODIGOS
jogo.titulo(pygame.K_RETURN)
checar(jogo.tela_atual == "codigos", "MENU: CÓDIGOS abre a tela de códigos")
jogo.tcodigos.desenhar(tela)
jogo.opcao = luta.COMOJOGAR
jogo.titulo(pygame.K_RETURN)
checar(jogo.tela_atual == "como", "MENU: COMO JOGAR abre os tutoriais")
jogo.tcomo.desenhar(tela)
controle_video.CONTROLES[:] = [cf]
controle_video.usando = "controle"
jogo.tcomo.desenhar(tela)
controle_video.usando = "teclado"
controle_video.CONTROLES[:] = []
jogo.tela_atual = "titulo"
for _ in range(3):
    jogo.desenhar_titulo()

if os.path.exists(SAVE_TESTE):
    os.remove(SAVE_TESTE)

print()
print("TUDO CERTO!" if not erros else f"{len(erros)} ERRO(S)")
