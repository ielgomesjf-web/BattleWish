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
FORCA_REAL = {f["nome"]: f["forca"] for f in PERSONAGENS}  # (o EQUILÍBRIO: a força de cada um multiplica o dano)
for _f in PERSONAGENS:  # os testes de cada golpe conferem o dano BASE (força 1); a força é testada no fim
    _f["forca"] = 1.0
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

# R: KAGE BUNSHIN (corre, encosta, aparece um clone do outro lado: 10 hits de 2)
def sem_objeto(p):
    p.objetos.pronto, p.objetos.recarga = False, 10 ** 9  # (o objeto do cenário também bate)
    return p


p = sem_objeto(contra_rib([Entrada(5, especial="R")], distancia=200))
rodar(p, 260)
checar(dano(p) == 20, f"RIB: KAGE BUNSHIN com o clone tira 10 x 2 = 20 ({dano(p)})")
p = sem_objeto(contra_rib([Entrada(5, especial="R")], distancia=700))
rodar(p, 260)
checar(dano(p) == 0, f"RIB: KAGE BUNSHIN de longe não acha ninguém ({dano(p)})")

# Q: rasteira + chute pra cima
p = contra_rib([Entrada(5, especial="Q")], distancia=90)
altura = 0
for _ in range(80):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) == 10 and altura > 120, f"RIB: rasteira + chute joga pra cima ({dano(p)} de dano, {int(altura)} px)")

# SHIFT: KUNAI COM CORRENTE (fisga, se puxa e chega com a voadora)
p = sem_objeto(contra_rib([Entrada(5, especial="SHIFT")], distancia=330))
perto = 999
for _ in range(260):
    p.passo(None)
    perto = min(perto, abs(p.L[0].x - p.L[1].x))
checar(dano(p) == 16 and perto < 90, f"RIB: kunai fisga (4) + voadora (12) = 16 e ele chega perto ({dano(p)}, {perto:.0f})")
p = sem_objeto(contra_rib([Entrada(5, especial="SHIFT")], distancia=650))
rodar(p, 260)
checar(dano(p) == 0, f"RIB: kunai de muito longe volta sem nada ({dano(p)})")

# PASSIVA SAPO NINJA: pulo alto, pulo duplo, menos dano no ar, substituição
def altura_pulo(ficha, passos):
    p = sem_objeto(Partida(ficha, ALVO, Roteiro(passos), Roteiro([])))
    p.fase, p.tf = "luta", 0
    menor = CHAO
    for _ in range(150):
        p.passo(None)
        menor = min(menor, p.L[0].y)
    return CHAO - menor


_pula = [Entrada(), Entrada(8), Entrada(8)]
_um = altura_pulo(RIB, _pula)
_dois = altura_pulo(RIB, _pula + [Entrada()] * 16 + [Entrada(8), Entrada(8)])
_seg = altura_pulo(RIB, [Entrada()] + [Entrada(8)] * 60)
_kun = altura_pulo(PERSONAGENS[6], _pula)
checar(_um > _kun * 1.15, f"RIB: pulo de sapo mais alto que o normal ({_um:.0f} x {_kun:.0f})")
checar(_dois > _um * 1.3 and abs(_seg - _um) < 3,
       f"RIB: PULO DUPLO só apertando de novo no ar ({_um:.0f} / {_dois:.0f} / segurando {_seg:.0f})")
_l = Lutador(RIB, 300, 1)
_l.y = CHAO - 100
import habilidades as _hab  # noqa: E402
_no_ar = _hab.mult_recebe(_l)
_l.y = CHAO
checar(abs(_no_ar - 0.8) < 1e-6 and _hab.mult_recebe(_l) == 1.0, "RIB: no ar leva 20% menos dano")
p = sem_objeto(Partida(PERSONAGENS[8], RIB, Roteiro([Entrada(), Entrada(especial="E")]), Roteiro([])))
p.fase, p.tf = "luta", 0
p.L[0].x, p.L[1].x = 400, 520
_v0 = p.L[1].vida
rodar(p, 120)
checar(p.L[1].vida == _v0 and p.L[1].extra.get("subst_espera", 0) > 0 and p.L[1].x < p.L[0].x,
       f"RIB: SUBSTITUIÇÃO: o golpe pega no tronco e ele aparece atrás ({p.L[1].vida}, x {p.L[1].x:.0f})")
p.L[0].x, p.L[1].x, p.L[0].dir = 400, 520, 1
p.ctrl = (Roteiro([Entrada(), Entrada(especial="E")]), p.ctrl[1])
rodar(p, 140)
checar(p.L[1].vida < _v0, "RIB: logo depois não substitui de novo (recarga de 10 s)")

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

# R: TRANSFORMAÇÃO (vira o Rib, faz o kage bunshin, volta) e o CLONE que repete cada hit por 5 s
p = contra_trafo([Entrada(5, especial="R")], distancia=200)
p.objetos.pronto, p.objetos.recarga = False, 10 ** 9
virou_rib = False
for _ in range(40):
    p.passo(None)
    virou_rib |= bool(p.L[0].disfarce and p.L[0].disfarce["nome"] == "RIB")
checar(virou_rib and p.L[0].disfarce is None and p.L[0].extra.get("clone_t", 0) > 250,
       "TRAFO: TRANSFORMAÇÃO vira o Rib, volta, e o CLONE aparece (5 s)")
p.L[0].x, p.L[1].x = 380, 560
_v0 = p.L[1].vida
p.ctrl = (Roteiro([Entrada(), Entrada(5, especial="SHIFT")]), p.ctrl[1])
rodar(p, 70)
checar(abs((_v0 - p.L[1].vida) - 20) < 0.01, f"TRAFO: com o clone, o pulão (10) vale 2 hits = 20 ({_v0 - p.L[1].vida:.1f})")
rodar(p, 400)
p.L[0].x, p.L[1].x = 380, 560
_v0 = p.L[1].vida
p.ctrl = (Roteiro([Entrada(), Entrada(5, especial="SHIFT")]), p.ctrl[1])
rodar(p, 70)
checar(p.L[0].extra.get("clone_t", 0) == 0 and abs((_v0 - p.L[1].vida) - 10) < 0.01,
       f"TRAFO: depois de 5 s o clone some (pulão = 10 de novo: {_v0 - p.L[1].vida:.1f})")

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
checar(not teve_cena and dano(p) == 35, f"TRAFO: ultimate sem cutscene, dentro da luta, tira 35 ({dano(p)})")
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
checar(l0.barra == 100, f"TRAFO: a barra do ultimate enche normal ({l0.barra})")

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
p = contra_cannan(segurando_z(200), distancia=250)
p.L[0].barra = BARRA_MAX
cansou = 0
for _ in range(1100):
    p.passo(None)
    if p.L[0].estado == "tonto" and p.L[0].superaquecido:
        cansou += 1
checar(dano(p) == 50, f"CANNAN: ultimate carregada (3s segurando Z) tira 50 ({dano(p)})")
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
    checar("entrada" in fases and p.fase == "falas" and l0.y == CHAO and not l0.esconde and not l0.sobrepor,
           f"ENTRADA: {f['nome']} entra e fica pronto pra luta (e vai falar)")
    while p.fase == "falas":
        p.passo(None)
        if p.tf % 40 == 0:
            p.desenhar(tela)
    checar(p.fase == "intro" and l0.pose_espera is None and l0.f["espera"] in l0.poses,
           f"ENTRADA: {f['nome']} espera na pose '{f['espera']}', fala e vai pra pose de luta")
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
checar("ninja" in hab.ativas(p.L[0]) and hab.mult_recebe(p.L[0]) == 1.0, "HABILIDADE: Rib com a passiva SAPO NINJA")
# Trafo: Conexão Terrestre
TRAFO["habilidade"] = "conexao"
p = contra_trafo([Entrada(2)] * 20, distancia=300)
rodar(p, 20)
checar(p.L[0].corpo().h < 80 * p.L[0].s * 0.9 * 0.55, "HABILIDADE: Trafo agachado fica bem menor (Conexão Terrestre)")
checar(hab.mult_causa(p.L[0], GOLPES["ag_chute"]) == 2.0 and hab.mult_causa(p.L[0], GOLPES["chute"]) == 1.0,
       "HABILIDADE: Trafo agachado bate o dobro")
checar(hab.mult_recebe(p.L[0]) == 0.8, "HABILIDADE: Trafo agachado leva 20% menos dano")
# Trafo: Adaptação (o mesmo golpe, a cada uso que acerta, tira 10% menos; até 40%)
checar(TRAFO["habilidades_opcoes"] == ("conexao", "adaptacao") and "barra_mult" not in TRAFO,
       "HABILIDADE: o Trafo escolhe Conexão Terrestre ou ADAPTAÇÃO (e a barra enche normal)")
TRAFO["habilidade"] = "adaptacao"
_tr, _at = Lutador(TRAFO, 500, -1), Lutador(BONECO, 400, 1)
_at.nome_golpe = "soco"
_mults = []
for _uso in range(6):
    _at.golpe_id = _uso
    _mults.append(round(hab.mult_recebe(_tr, _at, GOLPES["soco"]), 2))
_at.nome_golpe = "chute"
_outro = round(hab.mult_recebe(_tr, _at, GOLPES["chute"]), 2)
_at.nome_golpe, _at.golpe_id = "soco", 5
_mesmo = round(hab.mult_recebe(_tr, _at, GOLPES["soco"]), 2)
checar(_mults == [1.0, 0.9, 0.8, 0.7, 0.6, 0.6] and _outro == 1.0 and _mesmo == 0.6,
       f"HABILIDADE: ADAPTAÇÃO: o mesmo golpe tira 10% menos a cada uso, até 40% ({_mults}, outro {_outro}, mesmo uso {_mesmo})")
# Trafo: Mutação (saiu das opções, mas o código continua)
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
p.L[0].extra["subst_espera"] = 10 ** 6  # (sem a substituição do Rib: a shuriken tem que pegar nele)
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
                assert PAREDE_E <= l.x <= PAREDE_D, ("saiu da tela", l.f["nome"], int(l.x), l.estado, l.nome_golpe,
                                                     [(o.f["nome"], o.estado, o.nome_golpe, o.t) for o in p.L], p.fase)
        if fotos and n == 0 and q % 97 == 0 and q < 97 * 30:
            p.desenhar(tela)
            pygame.image.save(tela, os.path.join(pasta, f"luta_{q // 97:02d}.png"))
        if p.fase == "fim":
            terminadas += 1
            break
checar(terminadas == 20, f"20 partidas do computador terminaram ({terminadas})")
precisa = {"soco", "chute", "ag_chute",  # (os golpes do boneco de treino não contam: ele quase não aparece)
           "max_laser", "max_voo", "max_agarrao", "max_gatling", "max_rasante",
           "rib_shuriken", "rib_bunshin", "rib_rasteira", "rib_kunai", "rib_ultimate",
           "trafo_lingua", "trafo_terra", "trafo_transforma", "trafo_pulo",
           "king_bumerangue", "king_chute", "king_giro", "king_salto"}
for _g in sorted(precisa - golpes):  # (faltou algum? umas lutas a mais com o dono do golpe: o sorteio às vezes não usa)
    _dono = next((f for f in PERSONAGENS if _g in f["golpes"].values()), None)
    for _k in range(3 if _dono else 0):
        p = Partida(_dono, PERSONAGENS[(_k + 3) % len(PERSONAGENS)], Computador("DIFÍCIL"), Computador("DIFÍCIL"))
        for q in range(60 * 60 * 3):
            p.passo(None)
            golpes.add(p.L[0].nome_golpe)
            if _g in golpes or p.fase == "fim":
                break
        if _g in golpes:
            break
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
checar(vs.acabou and not vs.falas and vs.DURACAO == 150,
       f"FALAS: a tela de VS ficou curtinha (as falas agora são na arena) ({vs.DURACAO} quadros)")

import importlib  # noqa: E402
ok = True
for f in PERSONAGENS:
    modulo = importlib.import_module(f["desenho"].__module__)
    for r in roupas.da(f):
        ok &= all(letra in modulo.PALETA for letra in r.get("troca", {}))
checar(ok and all(len([r for r in roupas.da(f) if not r.get("codigo") and not r.get("evento") and not r.get("album")]) == 3 for f in PERSONAGENS),
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
checar(p.premio and p.premio[3] == (MOEDAS_VITORIA + MOEDAS_PERFECT + 10) * 2 and save.moedas() == antes + p.premio[3] + sum(v for _, v in p.premio[4])
       + sum(m for _, m, _ in p.missoes_feitas),  # (+ as MISSÕES DO DIA que essa luta cumpriu)
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
# ---- MODO FOTO (na pausa) ----
os.environ["BW_FOTOS"] = os.path.join(os.path.dirname(SAVE_TESTE), "luta_maria_fotos")
jogo.pausado, jogo.opcao_pausa = True, luta.PAUSA.index("MODO FOTO")
jogo.pausa(pygame.K_RETURN)
checar(jogo.tela_atual == "foto", "MODO FOTO: a pausa abre o modo foto")
jogo.evento_rei  # (existe)
jogo.tfoto.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f, unicode="", mod=0, scancode=0))
jogo.tfoto.desenhar(tela)
jogo.tfoto.tecla(pygame.K_RETURN)
_foto = jogo.tfoto.ultima_foto
checar(_foto and os.path.exists(_foto), "MODO FOTO: ENTER salva o PNG")
if _foto and os.path.exists(_foto):
    os.remove(_foto)
jogo.tfoto.tecla(pygame.K_ESCAPE)
checar(jogo.tfoto.sair, "MODO FOTO: ESC volta pra pausa")
jogo.tela_atual = "luta"
jogo.pausado, jogo.opcao_pausa = True, luta.PAUSA.index("MENU PRINCIPAL")
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
checar(dano(p) == 12 and altura > 60, f"FINN: levitação de média distância tira 12 e joga pra cima ({dano(p)}, {int(altura)} px)")
p = contra_finn([Entrada(5, especial="Q")], distancia=60)
rodar(p, 90)
checar(dano(p) == 0, "FINN: levitação é de média distância (colado não pega)")
p = contra_finn([Entrada(5, especial="R")], distancia=100)
rodar(p, 120)
checar(dano(p) == 25, f"FINN: cajado amarelo dá 5 hits de 5 ({dano(p)})")
p = contra_finn([Entrada(5, especial="SHIFT")], distancia=260)
x0 = p.L[0].x
rodar(p, 60)
checar(dano(p) == 7 and p.L[0].x - x0 > 60, f"FINN: empurrão mágico vai pra frente e tira 7 ({dano(p)})")
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
# FINN: as 2 passivas novas (H troca): ALQUIMIA e FEITIÇO DE CURA
checar(FINN["habilidade"] == "alquimia" and FINN["habilidades_opcoes"] == ("alquimia", "cura"),
       "FINN: passivas ALQUIMIA (começa) e FEITIÇO DE CURA")
_f = Lutador(FINN, 300, 1)
_f.vida = 50
for _ in range(hab.POCAO_ESPERA - 1):
    hab.finn_quadro(_f, None)
_antes = _f.extra.get("pocao")
hab.finn_quadro(_f, None)
checar(_antes is None and _f.extra.get("pocao") in hab.POCOES, f"FINN: ALQUIMIA bebe uma poção a cada 20 s ({_f.extra.get('pocao')})")
_g = Lutador(FINN, 300, 1)
_g.extra["pocao_forca"] = 10
_forca = hab.mult_causa(_g, GOLPES["soco"])
_g.extra["pocao_forca"], _g.extra["pocao_veloz"] = 0, 10
checar(abs(_forca - 1.25) < 1e-6 and abs(hab.mult_vel(_g) - 1.25) < 1e-6,
       f"FINN: poção de FORÇA = +25% de dano e de VELOCIDADE = +25% ({_forca}, {hab.mult_vel(_g)})")
_h = Lutador(dict(FINN, habilidade="cura"), 300, 1)
_h.vida = 50
for _c in range(1, 12):
    _h.combo = _c
    hab.finn_quadro(_h, None)
checar(_h.vida == 60, f"FINN: FEITIÇO DE CURA, combo de 11 = +10 de vida ({_h.vida})")
# FINN: o PODER MÁGICO antigo (saiu das opções, o código continua)
FINN["habilidade"] = "poder_magico"
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
FINN["habilidade"] = "alquimia"

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
# TROMOS (era o XENOMORPH)
# =====================================================================
XENO = next(f for f in PERSONAGENS if f["nome"] == "TROMOS")


def contra_xeno(passos_xeno, passos_alvo=(), distancia=None):
    p = Partida(XENO, ALVO, Roteiro(passos_xeno), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


p = contra_xeno([Entrada(5, especial="E")], distancia=250)
rodar(p, 40)
d_cuspe = dano(p)
checar(d_cuspe == 9 and p.L[0].extra.get("pocas"), f"XENO: cuspe de ácido tira 9 e deixa poça ({d_cuspe})")
rodar(p, 200)
checar(dano(p) == 12 and not p.L[0].extra.get("pocas"), f"XENO: a poça queima 1 por segundo e some em 3 s ({dano(p)})")
p = contra_xeno([Entrada(5, especial="Q")], distancia=90)
altura = 0
for _ in range(80):
    p.passo(None)
    altura = max(altura, CHAO - p.L[1].y)
checar(dano(p) == 15 and altura > 80, f"XENO: rabada tira 15 e joga pra cima ({dano(p)}, {int(altura)} px)")
p = contra_xeno([Entrada(5, especial="R")], distancia=95)
rodar(p, 100)
checar(dano(p) == 24, f"XENO: garras dão 6 hits de 4 ({dano(p)})")
p = contra_xeno([Entrada(5, especial="SHIFT")], distancia=300)
rodar(p, 50)
checar(dano(p) == 8, f"XENO: rasteja tira 8 ({dano(p)})")
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
p.L[0].vida = 50
pegou = False
for _ in range(260):
    p.passo(None)
    pegou |= "pegou" in p.L[0].memo
    if pegou:
        p.desenhar(tela)
checar(pegou and dano(p) == 25 and p.L[0].estado != "ataque", f"XENO: SEGUNDA BOCA pega e tira 25 ({dano(p)})")
checar(p.L[0].vida == 65, f"XENO: cada mordida da SEGUNDA BOCA cura 3 (5 x 3 = +15: {p.L[0].vida})")
p = contra_xeno([Entrada(5, especial="Z")], [Entrada()] * 10 + [Entrada(8)] * 3, distancia=280)
p.L[0].barra = BARRA_MAX
rodar(p, 200)
checar(dano(p) == 0, f"XENO: pulando, a ultimate erra ({dano(p)})")
# TROMOS: as 2 passivas novas (H troca): EMBOSCADA e REGENERAÇÃO
checar(XENO["habilidade"] == "emboscada" and XENO["habilidades_opcoes"] == ("emboscada", "regeneracao"),
       "TROMOS: passivas EMBOSCADA (começa) e REGENERAÇÃO")


class _Jogo:
    def __init__(self, *lut):
        self.L = list(lut)


_t = Lutador(XENO, 300, 1)
for _ in range(int(_hab.EMBOSCADA_ESPERA) + 2):
    _hab.tromos_quadro(_t, _Jogo(_t))
checar(_t.extra.get("camuflado") and _t.invisivel > 0, "TROMOS: EMBOSCADA, parado 1,5 s fica CAMUFLADO")
_r = Lutador(dict(XENO, habilidade="regeneracao"), 300, 1)
_o = Lutador(BONECO, 500, -1)
_r.vida = 50
_j = _Jogo(_r, _o)
for _estado in ("parado", "caido", "caido", "parado", "caido"):
    _o.estado = _estado
    _hab.tromos_quadro(_r, _j)
checar(_r.vida == 50 + 2 * _hab.REGENERA_VIDA == 62, f"TROMOS: REGENERAÇÃO, cada vez que o outro CAI = +6 ({_r.vida})")
# TROMOS: o SANGUE ÁCIDO antigo (saiu das opções, o código continua)
XENO["habilidade"] = "sangue_acido"
p = Partida(MAX, XENO, Roteiro([Entrada(5, soco=True)]), Roteiro([]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 80
rodar(p, 30)
checar(p.L[0].vida == 100 - 1 and p.L[1].vida < 100, f"XENO: SANGUE ÁCIDO, quem soca leva 1 ({p.L[0].vida})")
XENO["habilidade"] = "emboscada"
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
checar(pegou and dano(p) == 30 and p.L[0].estado != "ataque", f"TAI: YOKOZUNA levanta, pula e senta: 30 ({dano(p)})")
p = contra_tai([Entrada(5, especial="Z")], distancia=300)
p.L[0].barra = BARRA_MAX
rodar(p, 200)
checar(dano(p) == 0, "TAI: de longe a Yokozuna erra (tem que estar colado)")
checar(TAI["habilidade"] == "furia_sumo", "TAI: a passiva agora é a FÚRIA DO SUMÔ")
TAI["habilidade"] = "peso_pesado"  # (o PESO PESADO antigo: saiu, mas o código continua)
p = Partida(MAX, TAI, Roteiro([Entrada()] * 3 + [Entrada(5, soco=True)]), Roteiro([Entrada(5, especial="R")]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 85
rodar(p, 12)
checar(p.L[1].estado == "ataque" and p.L[1].vida < 120, "TAI: PESO PESADO, o soco tira vida mas ele continua o golpe")
TAI["habilidade"] = "furia_sumo"

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
checar(abs(dano(b) - 36) < 0.01, f"TAMER: LOBO BRANCO = +50% de dano (24 -> {dano(b)})")
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
checar(p.fase in ("falas", "intro", "luta"), "TAMER: entra correndo com o lobo (na SELVA)")

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
oa, ob = dois_robos("trio", ["cabecoes"], limite=300)  # (o trio é longo: com o PC ocupado, 120 s não davam)
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
checar(codigos.usar("Tiger Hat") and save.tem_roupa("JOHN", "gatola") and save.usando("JOHN") == "gatola"
       and roupas.vestir(next(f for f in PERSONAGENS if f["nome"] == "JOHN"))["estilo"] == "gatola",
       "CÓDIGOS: TIGERHAT dá o GATOLA DA CARTOLA pro John (cartola listrada e bigodes)")
tcd = codigos.TelaCodigos()
for ch in "Card&Fight":
    tcd.tecla(pygame.event.Event(pygame.KEYDOWN, key=0, unicode=ch))
checar(tcd.digitado == "CARD&FIGHT", f"CÓDIGOS: dá pra digitar o & (Card&Fight) ({tcd.digitado})")
for codigo, nome, roupa in (("The Best Magician", "FINN", "gandalf"), ("The Moon Is Mine", "TAI", "gru"),
                            ("Untamable", "TROMOS", "indominus"), ("Card&Fight", "KUN", "ash"),
                            ("Destemible Warrior", "KING RIP", "aragorn"), ("Magic Creatures", "CRÁQUEN", "mumia"),
                            ("Master of Tactics", "MAGNUS", "blue"), ("Ancient Jaw", "SPHYRUS", "megalodonte")):
    ok = bool(codigos.usar(codigo)) and save.tem_roupa(nome, roupa) and save.usando(nome) == roupa
    f = roupas.vestir(next(x for x in PERSONAGENS if x["nome"] == nome))
    p = Partida(f, ALVO, Roteiro([Entrada(5, especial="E")]), Roteiro([]))
    p.fase = "luta"
    for _ in range(60):
        p.passo(None)
        p.desenhar(tela)
    Lutador(f, 300, 1).desenhar(tela)
    checar(ok and f["estilo"] == roupa, f"CÓDIGOS: {codigo.upper()} dá a roupa {f['roupa'].upper()} pro {nome}")
    save.usar(nome, "padrao")
p = Partida(roupas.vestir(next(f for f in PERSONAGENS if f["nome"] == "JOHN")), ALVO,
            Roteiro([Entrada(5, especial="E")]), Roteiro([]))
p.fase = "luta"
for _ in range(40):
    p.passo(None)
    p.desenhar(tela)
save.usar("JOHN", "padrao")
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
checar(p.fase in ("falas", "intro", "luta") and p.L[0].x == p.L[0].extra["entrada_x"], "RIBBAT: entra pulando")
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

# ---- v2.0: FALAS NA ENTRADA, CHOQUE, REPLAY E MAESTRIA ----
import random as _r20  # noqa: E402
_r20.seed(5)
p = Partida(next(f for f in PERSONAGENS if f["nome"] == "RIB"), next(f for f in PERSONAGENS if f["nome"] == "TAI"),
            Roteiro([]), Roteiro([]))
fases, espera_rib, balao_ok = [], False, False
for _ in range(900):
    p.passo(None)
    if not fases or fases[-1] != p.fase:
        fases.append(p.fase)
    if p.fase == "falas":
        espera_rib |= p.L[0].pose_espera == "r_selo"
        if p.tf % 25 == 0:
            p.desenhar(tela)
    if p.fase == "luta":
        break
checar(fases[:4] == ["entrada", "falas", "intro", "luta"] and espera_rib,
       f"ENTRADA: chega, faz a pose de espera (Rib: selo de mão), fala e só depois luta ({fases})")
checar(all(l.pose_espera is None for l in p.L), "ENTRADA: depois de falar, os dois vão pra pose de luta")
p = Partida(MAX, ALVO, Roteiro([]), Roteiro([]))
for _ in range(DURACAO_ENTRADA + 5):
    p.passo(None)
p.pular_entrada()
checar(p.fase == "intro", "ENTRADA: ENTER pula as falas também")
p = Partida(MAX, ALVO, Roteiro([]), Roteiro([]))
p.pular_entrada()
checar(p.fase == "intro", "ENTRADA: ENTER no meio da entrada pula tudo (entrada e falas)")
# o sorteio da conversa é igual nos dois PCs do ONLINE (usa a semente da luta)
vistas = []
for _ in range(2):
    p = Partida(MAX, next(f for f in PERSONAGENS if f["nome"] == "TRAFO"), Roteiro([]), Roteiro([]))
    p.semente = 777
    _r20.seed(len(vistas) * 99)  # (o random de fora diferente nos dois "PCs")
    while p.fase != "luta":
        p.passo(None)
    vistas.append((p.falas_luta, p.t_total))
checar(vistas[0] == vistas[1], "ENTRADA: no ONLINE os dois PCs sorteiam a mesma conversa (e a luta começa junto)")

import choque  # noqa: E402
FINN = next(f for f in PERSONAGENS if f["nome"] == "FINN")
KUN = next(f for f in PERSONAGENS if f["nome"] == "KUN")


def choque_de_tiros(aperta0, aperta1):
    a = [Entrada(5, especial="E")] + [Entrada(5, soco=(k % aperta0 == 0)) if aperta0 else Entrada() for k in range(300)]
    b = [Entrada(5, especial="E")] + [Entrada(5, soco=(k % aperta1 == 0)) if aperta1 else Entrada() for k in range(300)]
    p = Partida(FINN, KUN, Roteiro(a), Roteiro(b))
    p.fase, p.tf = "luta", 0
    p.L[1].x = p.L[0].x + 420
    viu = False
    for _ in range(320):
        p.passo(None)
        if p.choque:
            viu = True
            if p.choque.t == 40:
                p.desenhar(tela)
    return p, viu


p, viu = choque_de_tiros(3, 0)
checar(viu and p.L[1].vida < p.L[1].vida_max and p.L[0].vida == p.L[0].vida_max,
       f"CHOQUE: os tiros se encontram, quem aperta mais ganha e o tiro dele passa ({p.L[1].vida:.0f})")
p, viu = choque_de_tiros(0, 3)
checar(viu and p.L[0].vida < p.L[0].vida_max and p.L[1].vida == p.L[1].vida_max, "CHOQUE: o outro lado também ganha")
p = Partida(KING, KING, Roteiro([Entrada(5, especial="R")]), Roteiro([Entrada(5, especial="R")]))
p.fase, p.tf = "luta", 0
p.L[1].x = p.L[0].x + 80
viu = False
for _ in range(60):
    p.passo(None)
    viu |= p.choque is not None
    if viu:
        break
checar(viu, "CHOQUE: dois golpes fortes acertando juntos (corpo a corpo) também dá choque")
p = Partida(KING, next(f for f in PERSONAGENS if f["nome"] == "TAI"), Computador("DIFÍCIL"), Computador("FÁCIL"))
p.fase = "luta"
p.choque = choque.Choque(p, (p.L[0].x + 50, CHAO - 60))
q = 0
while p.choque and q < 400:
    p.passo(None)
    q += 1
checar(p.choque is None and p.choque_txt and q <= choque.DURACAO + 2,
       f"CHOQUE: o computador aperta sozinho e o choque termina ({p.choque_txt[0] if p.choque_txt else None})")
checar(choque.forte(p.L[0]) is False, "CHOQUE: parado não entra em choque")

p = Partida(MAX, ALVO, Computador("DIFÍCIL"), Roteiro([]))
p.rounds = 1
for q in range(60 * 120):
    p.passo(None)
    if q % 2 == 0:
        p.desenhar(tela)
    if p.fase == "fim":
        break
checar(p.fase == "fim" and p.msg == "K.O.!" and len(p.replay) > 20 and p.replay_tocando(),
       "REPLAY: no K.O. final passa o replay dos últimos segundos")
for _ in range(20):
    p.desenhar(tela)
p.pular_replay()
p.desenhar(tela)
checar(not p.replay_tocando(), "REPLAY: ENTER pula o replay")

import maestria  # noqa: E402
save.d()["maestria"] = {}
checar(maestria.ganhar("RIB", 200) == (1, 3) and maestria.moldura("RIB") == maestria.BRONZE
       and maestria.titulo("RIB") == "APRENDIZ", "MAESTRIA: 200 pontos = nível 3, moldura de bronze")
from controles import BonecoTreino as _BT  # noqa: E402
pt = Partida(MAX, ALVO, Jogador(), _BT(), treino=True)
checar(maestria.pontos_da_luta(pt, 0) == 0, "MAESTRIA: treino não conta")
class _JogadorParado(Jogador):  # (um "jogador de verdade" que não aperta nada: o teste não tem teclado)
    def ler(self, bruto, eu, ele, jogo):
        return Entrada()


p = Partida(MAX, ALVO, _JogadorParado(), Computador("FÁCIL"))
p.rounds = 1
p.fase = "luta"
p.L[1].vida = 0
for _ in range(400):
    p.passo(None)
    if p.fase == "fim":
        break
checar(p.fase == "fim" and maestria.xp("MAX-10") > 0 and p.maestria_info and p.maestria_info[0][0] == 0,
       f"MAESTRIA: ganhar uma luta dá pontos pro lutador de quem jogou ({maestria.xp('MAX-10')})")
p.tf = 80
p.pular_replay()
p.desenhar(tela)
sel = TelaSelecao(PERSONAGENS)
sel.desenhar(tela)
save.d()["maestria"] = {}
save.salvar()

# ---- CENÁRIO INTERATIVO (v2.0) ----
import objetos  # noqa: E402
import cenarios as _cen  # noqa: E402
checar(all(objetos.criar(n).nome for n in _cen.CENARIOS), "OBJETOS: todo cenário tem um objeto")
p = Partida(MAX, ALVO, Roteiro([]), Roteiro([]), cenario_nome="DOJO")
p.fase = "luta"
o = p.objetos
p.L[1].x = 480
v0 = p.L[1].vida
o.disparar(p, p.L[0], p.L[1])
for _ in range(120):
    o.passo(p)
    if _ % 30 == 0:
        p.desenhar(tela)
checar(p.L[1].vida < v0 and not o.pronto, "OBJETOS: o gongo do DOJO deixa tonto e fica gasto")
p.novo_round()
checar(p.objetos.pronto, "OBJETOS: no round seguinte o objeto volta")
for n in _cen.CENARIOS:
    p = Partida(MAX, ALVO, Roteiro([]), Roteiro([]), cenario_nome=n)
    p.fase = "luta"
    p.L[1].x = 480
    p.objetos.disparar(p, p.L[0], p.L[1])
    for q in range(90):
        p.passo(None)
        if q % 30 == 0:
            p.desenhar(tela)
checar(True, "OBJETOS: os 12 disparam e desenham sem erro")

# ---- PERFIL, TROFÉUS E MISSÕES DO DIA (v2.0) ----
import datetime  # noqa: E402
import estatisticas  # noqa: E402
import missoes  # noqa: E402
import perfil  # noqa: E402
d = datetime.date(2026, 10, 16)
checar(missoes.sortear(d) == missoes.sortear(d) and missoes.sortear(d) != missoes.sortear(d + datetime.timedelta(1)),
       "MISSÕES: 3 por dia, iguais no mesmo dia (e outras amanhã)")
save.d()["trofeus"] = []
save.d()["estatisticas"] = {}
estatisticas.dados()["geral"]["vitorias"] = 1
checar("PRIMEIRA VITÓRIA" in perfil.trofeus_novos() and "PRIMEIRA VITÓRIA" not in perfil.trofeus_novos(),
       "TROFÉUS: sai uma vez só")
save.d()["trofeus"] = []
save.d()["estatisticas"] = {}
save.d()["missoes"] = {}
m0 = save.moedas()
p = Partida(MAX, ALVO, _JogadorParado(), Computador("FÁCIL"))
p.rounds = 1
p.fase = "luta"
p.L[1].vida = 0
for _ in range(400):
    p.passo(None)
    if p.fase == "fim":
        break
g = estatisticas.dados()["geral"]
checar(g["lutas"] == 1 and g["vitorias"] == 1 and estatisticas.personagem("MAX-10")["vitorias"] == 1,
       "ESTATÍSTICAS: a luta entra no perfil (1 luta, 1 vitória do MAX-10)")
checar("PRIMEIRA VITÓRIA" in p.trofeus_ganhos, f"TROFÉUS: a primeira vitória sai no fim da luta ({p.trofeus_ganhos})")
p.tf = 60
p.pular_replay()
p.desenhar(tela)
pt = Partida(MAX, ALVO, _JogadorParado(), _BT(), treino=True)
checar(not estatisticas.conta(pt), "ESTATÍSTICAS: treino não conta")
jogo.tela_atual = "titulo"
jogo.opcao = luta.PERFIL
jogo.titulo(pygame.K_RETURN)
checar(jogo.tela_atual == "perfil", "MENU: PERFIL abre o perfil (estatísticas, troféus e missões)")
for _ in range(3):
    jogo.tperfil.desenhar(tela)
    jogo.tperfil.tecla(pygame.K_d)
jogo.tperfil.tecla(pygame.K_s)
jogo.tperfil.tecla(pygame.K_RETURN)
checar(jogo.tperfil.sair, "PERFIL: VOLTAR volta pro menu")
jogo.tela_atual = "titulo"
for k in ("trofeus", "estatisticas", "missoes", "maestria"):
    save.d()[k] = [] if k == "trofeus" else {}
save.salvar()

# ---- CRÁQUEN: a ultimate agarra logo (só escapa quem já está no ar) ----
CRAQ = next(f for f in PERSONAGENS if f["nome"] == "CRÁQUEN")
acertou = 0
for dist in (140, 260, 420):
    p = Partida(CRAQ, ALVO, Roteiro([Entrada(5, especial="Z")]), Roteiro([Entrada(6)] * 300))  # (defendendo)
    p.fase = "luta"
    p.L[1].x = p.L[0].x + dist
    p.L[0].barra = BARRA_MAX
    for _ in range(260):
        p.passo(None)
    acertou += p.L[1].vida <= p.L[1].vida_max - 31
checar(acertou == 3, f"CRÁQUEN: o NAVIO FANTASMA acerta 32 até em quem defende, de perto e de longe ({acertou} de 3)")
p = Partida(CRAQ, ALVO, Roteiro([Entrada(5, especial="Z")]), Roteiro([Entrada(8)] + [Entrada(5)] * 100))
p.fase = "luta"
p.L[1].x = p.L[0].x + 220
p.L[0].barra = BARRA_MAX
for _ in range(260):
    p.passo(None)
checar(p.L[1].vida == p.L[1].vida_max, "CRÁQUEN: quem pula na hora escapa do navio")
p = Partida(CRAQ, ALVO, Roteiro([Entrada(5)] * 130 + [Entrada(5, chute=True)]), Roteiro([]))
p.fase = "luta"
p.L[1].x = p.L[0].x + 300
for _ in range(70):
    p.passo(None)
_cedo = bool(p.L[0].extra.get("intangivel"))
for _ in range(60):
    p.passo(None)
checar(not _cedo and p.L[0].extra.get("intangivel"), "CRÁQUEN: parado 2 segundos fica INTANGÍVEL (1 s ainda não)")
p.L[0].receber(GOLPES["soco"], 1, p.L[1], 1.0)
checar(p.L[0].vida == p.L[0].vida_max and not p.L[0].extra.get("intangivel"),
       "CRÁQUEN: o golpe ATRAVESSA (sem dano) e a passiva recarrega")

# ---- RIVAIS e CLIMA (v2.0) ----
import clima  # noqa: E402
import rivais  # noqa: E402
import random as _rnd  # noqa: E402
JOHN_F = next(f for f in PERSONAGENS if f["nome"] == "JOHN")
KUN_F = next(f for f in PERSONAGENS if f["nome"] == "KUN")
checar(rivais.sao_rivais("JOHN", "KUN") and len({tuple(falas.dialogo(JOHN_F, KUN_F, _rnd.Random(s))) for s in range(40)}) == 3,
       "RIVAIS: John x Kun são rivais e têm 3 conversas de rival")
vs = TelaVS(JOHN_F, KUN_F)
for _ in range(40):
    vs.desenhar(tela)
save.d()["moedas"] = 0
p = Partida(JOHN_F, KUN_F, _JogadorParado(), Computador("FÁCIL"))
p.rounds = 1
p.fase = "luta"
p.L[1].vida = 0
for _ in range(600):
    p.passo(None)
    if p.fase == "fim":
        break
checar(p.premio and p.premio[2] == 2 * MOEDAS_MULT.get("FÁCIL", 1) and rivais.vitorias("JOHN") == 1,
       f"RIVAIS: vencer o rival dá moedas em dobro e conta a vitória ({p.premio and p.premio[1]})")
for nome in cenarios.CENARIOS:
    p = Partida(MAX, ALVO, Roteiro([Entrada(6)] * 300), Roteiro([]), cenario_nome=nome)
    p.round, p.fase = 2, "luta"
    for q in range(240):
        p.passo(None)
        if q % 60 == 0:
            p.desenhar(tela)
p = Partida(MAX, ALVO, Roteiro([]), Roteiro([]), cenario_nome="SELVA")
p.round, p.fase = 2, "luta"
x0 = p.L[0].x
for _ in range(240):
    p.passo(None)
checar(p.clima.ativo and p.L[0].x != x0, "CLIMA: na SELVA, do round 2 a ventania começa e empurra")
p = Partida(MAX, ALVO, Roteiro([]), Roteiro([]), cenario_nome="SELVA")
p.fase = "luta"
for _ in range(240):
    p.passo(None)
checar(not p.clima.ativo, "CLIMA: no começo do round 1 o tempo está bom")
save.d()["rivais"] = {}
save.salvar()

# ---- FINISH (v2.0): acabou com ULTIMATE -> cena de finalização de cada um ----
import finish  # noqa: E402
sem = []
for f in PERSONAGENS + SECRETOS:
    p = Partida(f, ALVO, Roteiro([]), Roteiro([]))
    p.rounds = 1
    p.fase = "luta"
    p.L[1].vida, p.L[1].ult_recente = 0, 60
    fases = set()
    for q in range(900):
        p.passo(None)
        fases.add(p.fase)
        if p.fase == "finish" and p.tf % 40 == 0:
            p.desenhar(tela)
        if p.fase == "fim":
            break
    if not ("finish" in fases and p.fase == "fim" and p.L[0].estado == "vitoria"):
        sem.append(f["nome"])
checar(not sem, f"FINISH: todo mundo tem a sua cena quando a luta acaba com ULTIMATE (sem: {sem})")
p = Partida(MAX, ALVO, Roteiro([]), Roteiro([]))
p.rounds = 1
p.fase = "luta"
p.L[1].vida = 0
fases = set()
for _ in range(600):
    p.passo(None)
    fases.add(p.fase)
    if p.fase == "fim":
        break
checar("finish" not in fases and p.fase == "fim", "FINISH: sem ULTIMATE no final, não tem FINISH")

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
for _ in range(60 * 60 * 8):  # (até 3 rounds de 99 segundos, mais as entradas/falas/KO de cada round)
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
checar(jogo.opcao == luta.POR_COLUNA + luta.ONLINE, "MENU: D vai pra outra coluna")
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

# ---- CONFIGURAÇÕES (v2.0): volume da música, dos efeitos e vibração ----
jogo.opcao = luta.CONFIG
jogo.titulo(pygame.K_RETURN)
checar(jogo.tela_atual == "config", "MENU: CONFIGURAÇÕES abre a tela de configurações")
tcf = jogo.tconfig
tcf.desenhar(tela)
tcf.i = 0
for _ in range(3):
    tcf.tecla(pygame.K_a)  # música: 100 -> 70
tcf.i = 1
for _ in range(15):
    tcf.tecla(pygame.K_a)  # efeitos: até o 0 (mudo), não passa
import som as _som2  # noqa: E402
checar(save.d()["vol_musica"] == 70 and save.d()["vol_efeitos"] == 0 and abs(_som2.MULT_MUSICA - 0.7) < 1e-9
       and _som2.MULT_EFEITOS == 0, "CONFIGURAÇÕES: A/D muda o volume (e o 0 é mudo)")
tcf.mouse(tcf.barra(1).center, True)
checar(save.d()["vol_efeitos"] == 50, f"CONFIGURAÇÕES: clicar no meio da barra = 50% ({save.d()['vol_efeitos']})")
tcf.i = 2
tcf.tecla(pygame.K_RETURN)
checar(save.d()["vibrar"] is False, "CONFIGURAÇÕES: ENTER desliga a vibração do controle")
save.carregar()
checar(save.d()["vol_musica"] == 70 and save.d()["vibrar"] is False, "CONFIGURAÇÕES: fica salvo")
save.d().update(vol_musica=100, vol_efeitos=100, vibrar=True)
save.salvar()
save.d()["combos"] = {"KUN": [0]}
save.d()["regras"] = ["lua"]
save.salvar()
save.carregar()
checar(save.d()["combos"] == {"KUN": [0]} and save.d()["regras"] == ["lua"],
       "SAVE: desafios de combo e MODOS MALUCOS também ficam salvos depois de fechar o jogo")
save.d()["combos"], save.d()["regras"] = {}, []
save.salvar()
import json as _json  # noqa: E402
with open(save.arquivo(), encoding="utf-8") as _a:
    _d = _json.load(_a)
_d.update(vol_musica=None, vibrar="sim", moedas=_d.get("moedas", 0))
with open(save.arquivo(), "w", encoding="utf-8") as _a:
    _json.dump(_d, _a)
save.carregar()
_som2.aplicar_volumes()
checar(save.d()["vol_musica"] == 100 and save.d()["vibrar"] is True,
       "SAVE: valor estragado no arquivo (null, texto) volta pro padrão sem quebrar o jogo")
_som2.aplicar_volumes()
tcf.i = 3
tcf.tecla(pygame.K_RETURN)
tcf.desenhar(tela)
checar(tcf.sair, "CONFIGURAÇÕES: VOLTAR volta pro menu")
jogo.tela_atual = "titulo"

# ---- DIÁLOGOS SORTEADOS (v2.0) ----
import itertools  # noqa: E402
import random as _rnd  # noqa: E402
nomes = [f["nome"] for f in PERSONAGENS]
checar(all(len(falas.conversas(a, b)) >= 2 for a, b in itertools.combinations(nomes, 2)),
       "FALAS: toda dupla tem pelo menos 2 conversas")
r = _rnd.Random(1)
vistas = {tuple(falas.dialogo(MAX, next(f for f in PERSONAGENS if f["nome"] == "TRAFO"), r)) for _ in range(60)}
checar(len(vistas) == 3, f"FALAS: sorteia uma conversa diferente a cada luta ({len(vistas)} de 3)")
ok = all(len(falas.dialogo(a, b, r)) == 2 for a in PERSONAGENS for b in PERSONAGENS + SECRETOS)
checar(ok, "FALAS: toda dupla (até espelho e Ribbat) tem uma conversa de 2 falas")
checar(all(t == t.upper() for a in PERSONAGENS for b in PERSONAGENS + SECRETOS for l, t in falas.dialogo(a, b, r)
           if (a, b)[l]["nome"] == "MAX-10"), "FALAS: o MAX-10 sempre fala em MAIÚSCULA (até no espelho e contra o Ribbat)")
controle_video.CONTROLES[:] = [cf]
controle_video.usando = "controle"
jogo.tcomo.desenhar(tela)
controle_video.usando = "teclado"
controle_video.CONTROLES[:] = []
jogo.tela_atual = "titulo"
for _ in range(3):
    jogo.desenhar_titulo()

# =====================================================================
# MAGNUS (o raptor-robô de fogo)
# =====================================================================
MAGNUS = next(f for f in PERSONAGENS if f["nome"] == "MAGNUS")


def contra_magnus(passos, passos_alvo=(), distancia=None):
    p = Partida(MAGNUS, ALVO, Roteiro(passos), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


p = contra_magnus([Entrada(5, especial="E")], distancia=250)
preso = 0
for _ in range(120):
    p.passo(None)
    preso = max(preso, p.L[1].t if p.L[1].estado == "golpeado" else 0)
checar(dano(p) == 12 and p.L[1].estado != "caido", f"MAGNUS: espinhos da nuca = 6 hits de 2, sem derrubar ({dano(p)})")
checar(p.L[0].extra["penas"] < 1, "MAGNUS: atirou os espinhos, as penas do pescoço saem (e crescem de novo)")
p = contra_magnus([Entrada(5, especial="Q")], distancia=90)
caiu = False
for _ in range(90):
    p.passo(None)
    caiu |= p.L[1].estado == "voando" and p.L[1].malabar
checar(dano(p) == 10 and caiu, f"MAGNUS: duas rabadas = 2 de 5 e a segunda joga pra cima ({dano(p)})")
p = contra_magnus([Entrada(5, especial="Q")] + [Entrada()] * 22 + [Entrada(8)] * 10, distancia=90)
pulou = False
for _ in range(60):
    p.passo(None)
    pulou |= p.L[0].perseguindo > 0
checar(pulou, "MAGNUS: depois da rabada pro alto dá pra pular atrás (combo aéreo)")
p = contra_magnus([Entrada(5, especial="R")], distancia=150)
caiu = False
for _ in range(150):
    p.passo(None)
    caiu |= p.L[1].estado == "caido"
checar(dano(p) == 20 and caiu, f"MAGNUS: o bote = 10 garradas de 2 e fica caído ({dano(p)})")
p = contra_magnus([Entrada(5, especial="SHIFT")], distancia=250)
tonto = False
for _ in range(90):
    p.passo(None)
    tonto |= p.L[1].estado == "tonto"
checar(dano(p) == 15 and tonto, f"MAGNUS: corrida (5) + rabada de fogo (10) que paralisa ({dano(p)})")
p = contra_magnus([Entrada(5, especial="Z")], distancia=300)
p.L[0].barra = BARRA_MAX
pegou = False
for _ in range(200):
    p.passo(None)
    pegou |= "pegou" in p.L[0].memo
    if pegou:
        p.desenhar(tela)
checar(pegou and dano(p) == 35 and p.L[0].estado != "ataque", f"MAGNUS: bola de fogo (15) + RABADA DE FOGO (20) ({dano(p)})")
p = contra_magnus([Entrada(5, especial="Z")], [Entrada(6)] * 300, distancia=300)
p.L[0].barra = BARRA_MAX
rodar(p, 200)
checar(dano(p) < 15 and "pegou" not in p.L[0].memo and p.L[0].estado != "ataque",
       f"MAGNUS: defendendo as bolas de fogo, não tem rabada ({dano(p)})")
p = Partida(MAGNUS, MAX, Roteiro([]), Roteiro([]))
for _ in range(200):
    p.passo(None)
    p.desenhar(tela)
checar(p.fase != "entrada", f"MAGNUS: entrada (fogo no canto e farejando) termina ({p.fase})")
p = Partida(MAGNUS, MAX, Roteiro([]), Roteiro([]))
p.fase = "luta"
cm, cx = p.L[0].corpo(), p.L[1].corpo()
area = (cm.w * cm.h) / (cx.w * cx.h)
checar(p.L[0].vida_max == 70 and 0.62 <= area <= 0.78 and cm.w >= cx.w and cm.h <= cx.h * 0.66,
       f"MAGNUS: CORPO ÁGIL = 70 de vida e uns 70% da hitbox (baixinho, não fininho) ({area:.2f})")
_rb = next(f for f in SECRETOS if f["nome"] == "RIBBAT")
_pr = Partida(_rb, MAX, Roteiro([]), Roteiro([]))
_cr = _pr.L[0].corpo()
checar(_cr.w * _cr.h < cm.w * cm.h, "MAGNUS: só o Ribbat tem a hitbox menor que a dele")
p = Partida(MAGNUS, MAX, Roteiro([Entrada(6)] * 40), Roteiro([]))
p.fase = "luta"
x0 = p.L[0].x
rodar(p, 20)
p2 = Partida(XENO, MAX, Roteiro([Entrada(6)] * 40), Roteiro([]))
p2.fase = "luta"
x2 = p2.L[0].x
rodar(p2, 20)
checar(abs((p.L[0].x - x0) / (p2.L[0].x - x2) - 4.3 * _hab.AGIL_VEL / 4.2) < 0.05, f"MAGNUS: CORPO ÁGIL anda {round((_hab.AGIL_VEL - 1) * 100)}% mais rápido")
# ---- ROLAMENTO (M1 + M2 juntos) ----
p = partida_com(Roteiro([Entrada(6, soco=True, chute=True)]), Roteiro([]))
p.L[1].x = p.L[0].x + 90
x0 = p.L[0].x
rolou = invencivel = False
for _ in range(30):
    p.passo(None)
    rolou |= p.L[0].estado == "rolando"
    invencivel |= p.L[0].estado == "rolando" and p.L[0].corpo() is None
checar(rolou and invencivel and p.L[0].x > p.L[1].x, f"ROLAMENTO: M1+M2 segurando FRENTE rola pra frente, invencível, passando pelo outro ({int(p.L[0].x - x0)} px)")
p = partida_com(Roteiro([Entrada(5, soco=True), Entrada(5), Entrada(5, chute=True)]), Roteiro([]))
x0 = p.L[0].x
rodar(p, 30)
checar(p.L[0].x < x0 - 60 and p.L[0].estado == "parado", f"ROLAMENTO: M1 e logo M2 (sem direção) rola pra trás ({int(p.L[0].x - x0)} px)")
p = partida_com(Roteiro([Entrada(5, soco=True)] + [Entrada()] * 9 + [Entrada(5, chute=True)]), Roteiro([]))
viu = False
for _ in range(30):
    p.passo(None)
    viu |= p.L[0].estado == "rolando"
checar(not viu, "ROLAMENTO: soco e chute separados (combo normal) NÃO rolam")
p = partida_com(Roteiro([Entrada(5, soco=True, chute=True)] + [Entrada()] * 26 + [Entrada(5, soco=True, chute=True)]), Roteiro([]))
duas = 0
for _ in range(40):
    antes = p.L[0].estado
    p.passo(None)
    duas += antes != "rolando" and p.L[0].estado == "rolando"
checar(duas == 1, "ROLAMENTO: tem um tempinho de espera antes de rolar de novo")

import finish as _fin  # noqa: E402
# =====================================================================
# SPHYRUS (tubarão-martelo + mosassauro)
# =====================================================================
SPHYRUS = next(f for f in PERSONAGENS if f["nome"] == "SPHYRUS")


def contra_sphyrus(passos, passos_alvo=(), distancia=None, hab_=None, alvo=None):
    f = dict(SPHYRUS, habilidade=hab_ or "eletro")
    p = Partida(f, alvo or ALVO, Roteiro(passos), Roteiro(passos_alvo))
    p.fase, p.tf = "luta", 0
    if distancia:
        p.L[1].x = p.L[0].x + distancia
    return p


checar(SPHYRUS["vida"] == 80, "SPHYRUS: 80 de vida (vidro que bate forte)")
p = contra_sphyrus([Entrada(5, especial="E")], distancia=300)
rodar(p, 80)
checar(dano(p) == 14, f"SPHYRUS: onda de ar = 14 ({dano(p)})")
p = contra_sphyrus([Entrada(5, especial="Q")], distancia=90)
alto = 0
for _ in range(80):
    p.passo(None)
    alto = max(alto, CHAO - p.L[1].y)
checar(dano(p) == 15 and alto > 60, f"SPHYRUS: martelada = 15 e joga pra cima ({dano(p)}, {int(alto)} px)")
p = contra_sphyrus([Entrada(5, especial="R")], distancia=90)
rodar(p, 70)
checar(dano(p) == 24, f"SPHYRUS: corte em X = 2 hits de 12 ({dano(p)})")
p = contra_sphyrus([Entrada(5, especial="SHIFT")], distancia=260)
intangivel = False
for _ in range(110):
    p.passo(None)
    intangivel |= p.L[0].corpo() is None and p.L[0].estado == "ataque"
checar(dano(p) == 10 and intangivel, f"SPHYRUS: mergulho passa por baixo da terra e morde = 10 ({dano(p)})")
p = contra_sphyrus([Entrada(5, especial="Z")], distancia=250)
p.L[0].barra = BARRA_MAX
for _ in range(260):
    p.passo(None)
    if "pegou" in p.L[0].memo:
        p.desenhar(tela)
checar(dano(p) == 45 and p.L[0].s == SPHYRUS["tam"] and p.L[0].estado != "ataque",
       f"SPHYRUS: O MAR = 45 e ele volta pro tamanho normal ({dano(p)})")
# passivas
import habilidades as _hb  # noqa: E402
CRAQ = next(f for f in PERSONAGENS if f["nome"] == "CRÁQUEN")
p = contra_sphyrus([Entrada()] * 5 + [Entrada(5, soco=True)], alvo=CRAQ, distancia=90)
p.L[1].extra["intangivel"] = True
rodar(p, 30)
checar(p.L[1].vida < p.L[1].vida_max, "SPHYRUS: ELETRORRECEPÇÃO acerta o Cráquen intangível")
p = contra_sphyrus([], [Entrada(5, especial="E")], distancia=300)
achou = 0
for _ in range(20):
    p.passo(None)
    achou = max(achou, p.L[0].extra.get("sente", 0))
p.L[0].r_antes, p.L[0].r = 5, 5
p.L[0].parry_trava = 0
checar(achou > 0 and _hb.mult_parry(p.L[0]) == 2, "SPHYRUS: ELETRORRECEPÇÃO sente o especial e o parry fica 2x")


class _Nadador:
    def __init__(self, n_anda):
        self.n = 0
        self.n_anda = n_anda

    def ler(self, keys, eu, ele, jogo):
        self.n += 1
        e = Entrada(6 if 3 < self.n < self.n_anda else 5, soco=self.n == 20)
        e.lobo = self.n == 2
        return e


p = Partida(dict(SPHYRUS, habilidade="natacao"), ALVO, _Nadador(70), Roteiro([]))
p.fase, p.tf = "luta", 0
p.L[1].x = p.L[0].x + 120
nadou = derrubou = False
for _ in range(90):
    p.passo(None)
    nadou |= bool(p.L[0].extra.get("nadando")) and p.L[0].corpo() is None
    derrubou |= p.L[1].estado in ("voando", "caido")
checar(nadou and derrubou and dano(p) == 8, f"SPHYRUS: NATAÇÃO = intangível, não soca, passar por baixo dá 8 e derruba ({dano(p)})")
p = Partida(dict(SPHYRUS, habilidade="natacao"), ALVO, _Nadador(3), Roteiro([]))
p.fase, p.tf = "luta", 0
rodar(p, 8 * FPS + 30)
checar(not p.L[0].extra.get("nadando") and p.L[0].extra.get("nada_recarga", 0) > 0,
       "SPHYRUS: NATAÇÃO dura no máximo 8 s e depois recarrega")
p = contra_sphyrus([Entrada()] * 3 + [Entrada(5, especial="R")], distancia=90, hab_="frenesi")
p.L[1].vida_max = 200
p.L[1].vida = p.L[1].vida_max * 0.35
v0 = p.L[1].vida
rodar(p, 80)
checar(p.L[0].extra.get("frenesi") and abs((v0 - p.L[1].vida) - 48) < 0.01 and _hb.mult_vel(p.L[0]) >= 1.3,
       f"SPHYRUS: FRENESI = dano x2 e +30% de velocidade ({v0 - p.L[1].vida:.0f})")
p = contra_sphyrus([], distancia=200)
import cenarios as _cn  # noqa: E402
p.cena = _cn.cenario("PRAIA DA ILHA")
rodar(p, 2)
checar(abs(_hb.mult_vel(p.L[0]) - 1.1) < 0.001, "SPHYRUS: BÔNUS NA ÁGUA (na praia anda 10% mais rápido)")
p = Partida(SPHYRUS, MAX, Roteiro([]), Roteiro([]))
for _ in range(220):
    p.passo(None)
    p.desenhar(tela)
checar(p.fase != "entrada", f"SPHYRUS: entrada (barbatana + rugidão) termina ({p.fase})")
checar(_fin.FINISHES.get("SPHYRUS", {}).get("nome") == "VIROU ISCA!", "SPHYRUS: FINISH = VIROU ISCA!")
# =====================================================================
# 2ª ULTIMATE (barra AMARELA)
# =====================================================================
import ult2 as _u2  # noqa: E402
P2 = {f["nome"]: f for f in PERSONAGENS}
checar(all("Z2" in f["golpes"] for f in PERSONAGENS) and "Z2" not in next(f for f in SECRETOS if f["nome"] == "RIBBAT")["golpes"],
       "2ª ULTIMATE: todo mundo tem (menos o Ribbat: NÃO PRECISA)")
p = Partida(P2["MAX-10"], P2["TAI"], Roteiro([]), Roteiro([]))
p.fase = "luta"
l0 = p.L[0]
l0.encher(5000)
checar(l0.barra == BARRA_TOTAL, f"2ª ULTIMATE: a barra continua enchendo em AMARELO (metade do tamanho) ({l0.barra})")
l0.barra = BARRA_MAX + 300
l0.comecar(l0.golpe_do_botao("Z"))
checar(l0.barra == 300, f"2ª ULTIMATE: usar a 1ª gasta só a azul (o amarelo desce) ({l0.barra})")
l0.mudar("parado")
l0.barra = BARRA_MAX + 300
checar(not l0.comecar("max_ult2"), "2ª ULTIMATE: com a amarela pela metade não sai")
l0.barra = BARRA_MAX
l0.bonus_amarelo(BONUS_COMBO)
checar(l0.barra == BARRA_MAX + BONUS_COMBO, "2ª ULTIMATE: jogada boa (combo 5+, choque, objeto) enche a amarela")
l0.barra = 200
l0.bonus_amarelo(BONUS_COMBO)
checar(l0.barra == 200, "2ª ULTIMATE: o bônus só vale com a azul cheia")
_rb2 = Partida(next(f for f in SECRETOS if f["nome"] == "RIBBAT"), MAX, Roteiro([]), Roteiro([]))
_rb2.L[0].encher(5000)
checar(_rb2.L[0].barra == BARRA_MAX, "2ª ULTIMATE: a barra do Ribbat para na azul (NÃO PRECISA)")
p = Partida(P2["MAX-10"], P2["TAI"], Roteiro([Entrada()] * 3 + [Entrada(5, especial="Z", )]), Roteiro([]))
p.fase = "luta"
p.L[0].barra = BARRA_TOTAL
p.L[0].ex_pedido = False
import rede as _rede  # noqa: E402
_e = Entrada(5, especial="Z2")
checar(_rede.decodifica(_rede.codifica(_e)).especial == "Z2", "2ª ULTIMATE: o botão vai pelo online")


def contra_ult2(nome, alvo="TAI", hab_=None, cena=None, quadros=900):
    f = dict(P2[nome], habilidade=hab_ or P2[nome].get("habilidade"))
    p = Partida(f, P2[alvo], Roteiro([Entrada()] * 3 + [Entrada(5, especial="Z2")]), Roteiro([]))
    p.fase, p.tf = "luta", 0
    if cena:
        import cenarios as _c
        p.cena = _c.cenario(cena)
    p.L[1].x = p.L[0].x + 200
    p.L[0].barra = BARRA_TOTAL
    v0 = p.L[1].vida
    saiu = False
    for i in range(quadros):
        p.passo(None)
        saiu |= p.L[0].nome_golpe == f["golpes"]["Z2"]
        if i % 9 == 0:
            p.desenhar(tela)
    return p, saiu, v0 - p.L[1].vida


for nome, esperado, extra in (("MAX-10", 45, {}), ("RIB", 50, {}), ("KING RIP", 55, {}), ("CANNAN", 55, {}),
                              ("KUN", 55, {}), ("TAI", 45, dict(alvo="RIB")), ("JOHN", 55, {}),
                              ("CRÁQUEN", 60, dict(cena="PRAIA DA ILHA")),
                              ("SPHYRUS", 65, dict(hab_="natacao")), ("SPHYRUS", 60, dict(hab_="eletro")),
                              ("SPHYRUS", 60, dict(hab_="frenesi"))):
    p, saiu, d = contra_ult2(nome, **extra)
    checar(saiu and abs(d - esperado) < 0.6 and p.L[0].estado != "ataque",
           f"2ª ULTIMATE: {nome} {extra.get('hab_', '')} tira {esperado} ({d:.1f})")
p, saiu, d = contra_ult2("CANNAN")
checar(abs(p.L[0].vida - (p.L[0].vida_max - 10)) < 0.01, f"2ª ULTIMATE: o coice da MINIGUN tira 10 do Cannan ({p.L[0].vida:.1f})")
p, saiu, d = contra_ult2("TRAFO")
checar(saiu and abs(d - 60) < 0.6, f"2ª ULTIMATE: TRAFO braços de terra, parado leva todos = 60 ({d:.1f})")
p, saiu, d = contra_ult2("CRÁQUEN", cena="TEMPLO", quadros=5 * 5 * FPS + 200)
checar(saiu and abs(d - 50) < 0.6, f"2ª ULTIMATE: CRÁQUEN sem água = 5 marujos, 1 hit a cada 5 s ({d:.1f})")
p, saiu, d = contra_ult2("FINN", quadros=220)
checar(saiu and d == 15 and p.L[0].extra.get("golem", 0) > 0, f"2ª ULTIMATE: FINN chama o golem (soco de 15, e ele fica) ({d})")
for nome, chave in (("TROMOS", "cacada"), ("TAMER", "lobisomem"), ("MAGNUS", "fornalha")):
    p, saiu, d = contra_ult2(nome, quadros=260)
    checar(saiu and p.L[0].extra.get(chave, 0) > 0, f"2ª ULTIMATE: {nome} liga o {chave.upper()} por 10 s")
_stuns = []
for _forn in (0, 100):
    p = Partida(P2["MAGNUS"], P2["RIB"], Roteiro([]), Roteiro([]))
    p.fase = "luta"
    p.L[0].extra["fornalha"] = _forn
    p.L[1].receber(GOLPES["soco"], 1, p.L[0], 1.0)
    _stuns.append((p.L[1].stun, p.L[1].vida))
checar(_stuns[1][0] > _stuns[0][0] and _stuns[1][1] < _stuns[0][1],
       f"2ª ULTIMATE: MODO FORNALHA queima (mais dano) e PRENDE (mais tempo) ({_stuns})")

# ---- DIA E NOITE (periodo.py) ----
import periodo as _per  # noqa: E402
import random as _rnd2  # noqa: E402
checar(_per.criar("SELVA", _rnd2.Random(5)).nome == _per.criar("SELVA", _rnd2.Random(5)).nome
       and isinstance(_per.criar("DOJO"), _per.Nada), "DIA/NOITE: igual com a mesma semente; lugar fechado não muda")
_pa, _pb = (Partida(MAX, P2["TAI"], Roteiro([]), Roteiro([])) for _ in range(2))
_pa.semente = _pb.semente = 1234
_estado = _rnd2.getstate()
checar(_pa.periodo_atual().nome == _pb.periodo_atual().nome and _rnd2.getstate() == _estado,
       "DIA/NOITE: no online os dois PCs sorteiam igual (e não mexe no random da luta)")
_pa.desenhar(tela)

# ---- REI DA ARENA ----
import reiarena as _rei  # noqa: E402
_a = _rei.ReiArena(["A", "B", "C"])
_a.registrar(0)
_a.registrar(1)
checar(_a.rei == "C" and _a.fila == ["B", "A"] and _a.sequencia == 1,
       "REI DA ARENA: quem ganha fica, quem perde vai pro fim da fila")
jogo.modo = luta.REI
jogo.arena = _rei.ReiArena(["ANA", "BIA"])
jogo.tplacar = _rei.TelaPlacar(jogo.arena)
jogo.tela_atual = "rei_placar"
jogo.tplacar.desenhar(tela)
jogo.evento_rei(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="", mod=0, scancode=0))
checar(jogo.tela_atual == "escolha" and "ANA" in (jogo.sel.titulo or ""),
       "REI DA ARENA: do placar vai pra escolha (REI x DESAFIANTE)")
jogo.sel.desenhar(tela)
jogo.tela_atual = "titulo"
jogo.modo = luta.UM

# ---- LOJA NOVA (entradas, vitórias e provocações) ----
import extras as _ex  # noqa: E402
import tai as _tai  # noqa: E402
from loja import TelaLoja as _TL  # noqa: E402
_ex.registrar("entradas", "MAX-10", id="teste", nome="TESTE", preco=30, entrada=_tai.entrada)
_ex.registrar("provocacoes", "MAX-10", id="teste", nome="TESTE", preco=30, provocacao="TESTE!")
save.d()["moedas"] = 100
_lj = _TL(PERSONAGENS)
for _c in range(len(_ex.CATEGORIAS)):
    _lj.cat, _lj.j = _c, len(_lj.itens()) - 1
    for _ in range(3):
        _lj.desenhar(tela)
_lj.cat = 1
_lj.j = [i["id"] for i in _lj.itens()].index("teste")
_lj.confirmar()
_f = roupas.vestir(MAX)
checar(_ex.usando("entradas", "MAX-10") == "teste" and _f["entrada"] is _tai.entrada and save.moedas() == 70,
       "LOJA NOVA: compra uma ENTRADA e o seu lutador entra com ela")
checar(roupas.vestir(MAX, "padrao").get("entrada") is MAX.get("entrada"), "LOJA NOVA: o computador entra com a original")
_lj.cat = 3
_lj.j = [i["id"] for i in _lj.itens()].index("teste")
_lj.confirmar()
_p = Partida(roupas.vestir(MAX), P2["TAI"], Roteiro([Entrada()] * 2 + [Entrada(5)]), Roteiro([]))
_p.fase = "luta"
_p.L[0].comecar("provocar")
for _ in range(10):
    _p.passo(None)
    _p.desenhar(tela)
checar(_p.L[0].f["provocacao"] == "TESTE!", "LOJA NOVA: a provocação comprada aparece na luta")
for _cat in ("entradas", "provocacoes"):  # (tira os itens de teste)
    _ex.CATALOGO[_cat]["MAX-10"] = [i for i in _ex.CATALOGO[_cat]["MAX-10"] if i["id"] != "teste"]
    save.d()["extras_usando"][_cat]["MAX-10"] = "padrao"

# ---- PROVOCAÇÕES DA LOJA (2 por lutador) ----
_n_prov = 0
_tudo_ok = True
_P3 = {f["nome"]: f for f in PERSONAGENS + list(SECRETOS)}
for _nome, _itens in _ex.CATALOGO["provocacoes"].items():
    for _it in _itens:
        _f = _ex.aplicar(dict(_P3[_nome]), _nome, {"provocacoes": _it["id"]})
        _pp = Partida(_f, P2["TAI"] if _nome != "TAI" else P2["RIB"], Roteiro([]), Roteiro([]))
        _pp.fase = "luta"
        _pp.L[1].x = _pp.L[0].x + 220
        _pp.passo(None)
        _pp.L[0].comecar("provocar")
        for _i in range(PROVOCA_TEMPO + 30):
            _pp.passo(None)
            if _i % 10 == 0:
                _pp.desenhar(tela)
        _tudo_ok &= not _pp.L[0].extra.get("prov_vis") and not _pp.L[0].esconde and _pp.L[0].barra > 0
        _n_prov += 1
checar(_tudo_ok and _n_prov == 32 + 5, f"LOJA: as {_n_prov} provocações novas (32 + 5 de Halloween) rodam e o lutador volta ao normal")
_f = _ex.aplicar(dict(_P3["TROMOS"]), "TROMOS", {"provocacoes": "teto"})
_pp = Partida(_f, P2["TAI"], Roteiro([]), Roteiro([Entrada()] * 20 + [Entrada(5, soco=True)]))
_pp.fase = "luta"
_pp.L[1].x = _pp.L[0].x + 70
_pp.passo(None)
_pp.L[0].comecar("provocar")
for _ in range(60):
    _pp.passo(None)
checar(not _pp.L[0].esconde and not _pp.L[0].extra.get("prov_vis"),
       "LOJA: apanhou no meio da provocação (sumiu pro teto): volta a aparecer normal")

# ---- POSES DE VITÓRIA DA LOJA (2 por lutador) ----
_n_vit = 0
for _nome, _itens in _ex.CATALOGO["vitorias"].items():
    for _it in _itens:
        _f = _ex.aplicar(dict(_P3[_nome]), _nome, {"vitorias": _it["id"]})
        _pp = Partida(_f, P2["TAI"] if _nome != "TAI" else P2["RIB"], Roteiro([]), Roteiro([]))
        _pp.fase = "luta"
        _pp.passo(None)
        _pp.L[0].mudar("vitoria")
        _pp.L[1].mudar("caido")
        for _i in range(160):
            _pp.L[0].update(Entrada(), _pp.L[1], _pp)
            _pp.L[0].animar()
            if _i % 20 == 0:
                _pp.desenhar(tela)
        _n_vit += 1
checar(_n_vit == 31, f"LOJA: as {_n_vit} poses de vitória novas rodam (repetindo) sem quebrar")

# ---- ENTRADAS DA LOJA (2 por lutador) ----
_n_ent = 0
_ent_ok = True
for _nome, _itens in _ex.CATALOGO["entradas"].items():
    for _it in _itens:
        _f = _ex.aplicar(dict(_P3[_nome]), _nome, {"entradas": _it["id"]})
        _pp = Partida(_f, P2["TAI"] if _nome != "TAI" else P2["RIB"], Roteiro([]), Roteiro([]))
        for _i in range(DURACAO_ENTRADA + 5):
            _pp.passo(None)
            if _i % 15 == 0:
                _pp.desenhar(tela)
        _l = _pp.L[0]
        _ent_ok &= (_l.x, _l.y, _l.esconde, _l.angulo, _l.s) == (_l.extra["entrada_x"], CHAO, False, 0, _l.f["tam"])
        _n_ent += 1
checar(_ent_ok and _n_ent == 31, f"LOJA: as {_n_ent} entradas novas rodam e terminam com ele no lugar")

# =====================================================================
# FRIGANTUS (o yeti gigantopiteco, 15º)
# =====================================================================
FRIG = P2["FRIGANTUS"]


def contra_frig(passos, alvo="TAI", distancia=200, quadros=200, barra=0):
    p = Partida(FRIG, P2[alvo], Roteiro([Entrada()] * 3 + passos), Roteiro([]))
    p.fase, p.tf = "luta", 0
    p.L[1].x = p.L[0].x + distancia
    p.L[0].barra = barra
    p.L[1].extra["subst_espera"] = 10 ** 6  # (sem a substituição do Rib)
    v0 = p.L[1].vida
    congelou = False
    for i in range(quadros):
        p.passo(None)
        congelou |= bool(getattr(p.L[1], "congelado", False))
        if i % 9 == 0:
            p.desenhar(tela)
    return p, v0 - p.L[1].vida, congelou


checar(FRIG["vida"] == 120 and FRIG["habilidade"] == "nevasca", "FRIGANTUS: 120 de vida e a passiva NEVASCA")
p, d, cong = contra_frig([Entrada(5, especial="E")], distancia=300)
checar(abs(d - 10) < 0.01 and cong, f"FRIGANTUS: bola de neve = 10 e CONGELA ({d:.1f})")
p, d, cong = contra_frig([Entrada(5, especial="Q")], distancia=110, quadros=90)
checar(abs(d - 12) < 0.01, f"FRIGANTUS: pisão com estacas de gelo = 12 ({d:.1f})")
p, d, cong = contra_frig([Entrada(5, especial="R")], alvo="RIB", distancia=220, quadros=160)
checar(d >= 14 and p.L[1].x in (PAREDE_E, PAREDE_D) or d >= 14, f"FRIGANTUS: as 8 estacas na cabeça ({d:.1f})")
p, d, cong = contra_frig([Entrada(5, especial="SHIFT")], distancia=240, quadros=90)
checar(abs(d - 10) < 0.01, f"FRIGANTUS: escorregão = 10 ({d:.1f})")
p, d, cong = contra_frig([Entrada(5, especial="Z")], quadros=220, barra=BARRA_MAX)
checar(abs(d - 40) < 0.01, f"FRIGANTUS: AVALANCHE = 40 ({d:.1f})")
p, d, cong = contra_frig([Entrada(5, especial="Z2")], quadros=420, barra=BARRA_TOTAL)
checar(abs(d - 60) < 0.01 and p.cena.nome != "MONTANHA NEVADA" and p.cutscene is None,
       f"FRIGANTUS: ERA DO GELO = 60 e a luta continua 3 cenários depois ({d:.1f}, {p.cena.nome})")
checar(p.stats["ults2"] == 0 and p.L[0].acertou_ult2, "2ª ULTIMATE: conta quem acertou (pro troféu PODER MÁXIMO)")
_pp = Partida(FRIG, P2["RIB"], Roteiro([]), Roteiro([]))
_pp.fase = "luta"
_alvo = _pp.L[1]
for _ in range(3):
    _alvo.mudar("parado")
    _alvo.receber(GOLPES["soco"], 1, _pp.L[0], 1.0)
checar(getattr(_alvo, "congelado", False), "FRIGANTUS: NEVASCA = 3 golpes seguidos CONGELA")
_pp2 = Partida(FRIG, P2["RIB"], Roteiro([]), Roteiro([]))
_pp2.L[1].receber(GOLPES["soco"], 1, _pp2.L[0], 1.0)
import habilidades as _hb2  # noqa: E402
checar(_hb2.mult_vel(_pp2.L[1]) < 1.0, "FRIGANTUS: NEVASCA = cada golpe deixa mais lento")

import save as _sv  # noqa: E402
checar(_sv._renomear({"usando": {"XENOMORPH": "fogo"}, "trofeus": ["SOMBRA DO XENOMORPH"]})
       == {"usando": {"TROMOS": "fogo"}, "trofeus": ["SOMBRA DO TROMOS"]},
       "SAVE: o save antigo do XENOMORPH passa pro TROMOS (ninguém perde roupa nem maestria)")
import finish as _fin  # noqa: E402
checar(_fin.FINISHES.get("MAGNUS", {}).get("nome") == "TOSTADO!", "MAGNUS: FINISH = TOSTADO!")

# ---- EVENTOS (Halloween) ----
import datetime  # noqa: E402
import eventos as _ev  # noqa: E402
checar(_ev.evento_atual(datetime.date(2026, 10, 30)) == "HALLOWEEN" and _ev.evento_atual(datetime.date(2026, 11, 5)) is None
       and _ev.pascoa(2027) == datetime.date(2027, 3, 28), "EVENTOS: calendário")
_hw = [(n, r["id"]) for n, lista in roupas.ROUPAS.items() for r in lista if r.get("evento") == "halloween"]
checar(len(_hw) == 5, f"HALLOWEEN: as 5 skins do passe ({_hw})")
for _n, _rid in _hw:  # cada skin desenha sem quebrar (parada e atacando)
    _f = roupas.vestir(next(f for f in PERSONAGENS if f["nome"] == _n), _rid)
    _p = Partida(_f, PERSONAGENS[1], Roteiro([Entrada(5, especial="Q")]), Roteiro([]))
    _p.fase = "luta"
    for _ in range(20):
        _p.passo(None)
    _p.desenhar(pygame.display.get_surface())
checar(True, "HALLOWEEN: as 5 skins desenham")
import loja as _lj  # noqa: E402
_tl = _lj.TelaLoja(PERSONAGENS)
_tl.i = next(i for i, f in enumerate(PERSONAGENS) if f["nome"] == "RIB")
checar(not any(r.get("evento") for r in _tl.itens()), "HALLOWEEN: a loja não mostra a skin do passe pra quem não ganhou")
_sv.d()["doces"] = 1
import extras as _ex  # noqa: E402
_hwp = [(n, i["id"]) for n, lista in _ex.CATALOGO["provocacoes"].items() for i in lista if i.get("evento")]
checar(len(_hwp) == 5 and not any(_ex.tem("provocacoes", n, i) for n, i in _hwp),
       f"HALLOWEEN: 5 provocações do passe (só com o passe) ({_hwp})")
for _n, _i in _hwp:  # cada uma roda inteira e desenha (e não deixa o lutador sumido no fim)
    _f = _ex.aplicar(next(f for f in PERSONAGENS if f["nome"] == _n), _n, {"provocacoes": _i})
    _p = Partida(_f, PERSONAGENS[1], Roteiro([]), Roteiro([]))
    _p.fase = "luta"
    _p.passo(None)
    _p.L[0].comecar("provocar")
    for _ in range(PROVOCA_TEMPO + 4):
        _p.passo(None)
        _p.desenhar(pygame.display.get_surface())
    checar(not _p.L[0].esconde and not _p.L[0].extra.get("prov_vis"), f"HALLOWEEN: provocação {_n} {_i} termina limpa")
import narrador as _nar  # noqa: E402
_n0 = _nar.Narrador()
_pn = Partida(PERSONAGENS[0], PERSONAGENS[1], Roteiro([]), Roteiro([]))
_pn.fase = "luta"
_n0.passo(_pn)
_pn.L[0].combo = 10
_n0.passo(_pn)
checar(("combo", 0) in _n0.historico, "NARRADOR: combo de 10 = COMBO INSANO")
# ---- NATAL (meias e gorrinho) ----
import natal as _nt  # noqa: E402
_pz = Partida(PERSONAGENS[0], PERSONAGENS[1], Roteiro([]), Roteiro([]))
checar(_nt.criar(_pz, datetime.date(2026, 10, 18)) is None and _nt.criar(_pz, datetime.date(2026, 12, 22)) is not None,
       "NATAL: a meia só existe no Natal")
_dn = datetime.date(2026, 12, 22)
for _lado, _quer in ((0, True), (1, False)):  # golpe do JOGADOR pega; golpe do CPU só balança
    _pz = Partida(PERSONAGENS[0], PERSONAGENS[1], Roteiro([]), Roteiro([]))
    _pz.fase = "luta"
    _pz.lado_humano = 0
    _pz.meia = _nt.Meia(_pz.cena.nome, _dn)
    _pz.passo(None)
    _l = _pz.L[_lado]
    _l.estado = "ataque"
    _l.caixa_golpe = lambda c=_pz.meia.caixa(): c
    _pz.meia.passo(_pz)
    checar(_pz.meia.pega == _quer and (_quer or _pz.meia.balanca > 0),
           f"NATAL: golpe do {'jogador pega' if _quer else 'CPU só balança'} a meia")
_sv.d()["natal"] = {}
# ---- CUTSCENES DA LOJA ----
import cenas_loja as _cl  # noqa: E402
_ok_c, _n_c = True, 0
for _cat, _tipo in (("vitorias", "vitoria"), ("entradas", "entrada")):
    for _n, _lista in _ex.CATALOGO[_cat].items():
        for _it in _lista:
            if not _it.get(_tipo + "_cutscene"):
                continue
            _f = _ex.aplicar(dict(_P3[_n]), _n, {_cat: _it["id"]})
            _c = _cl.criar(_f, _tipo, PERSONAGENS[1])
            _ok_c &= _c.total <= _cl.DURACAO_MAX
            for _q in range(_c.total):
                if _q % 40 == 0:
                    _c.desenhar(tela)
                _c.passo()
            _ok_c &= _c.acabou
            _n_c += 1
checar(_ok_c and _n_c == 32, f"CUTSCENES: as {_n_c} cenas (16 vitórias + 16 entradas) rodam até o fim em até 6 s")
import dis as _dis  # noqa: E402
import entradas_loja as _el  # noqa: E402
import vitorias_loja as _vl  # noqa: E402
_anime = {v.split(":")[0] for v in list(_el.ANIME.values()) + list(_vl.ANIME.values())}
_no_exe = {i.argval for i in _dis.get_instructions(_cl._pro_exe) if i.opname == "IMPORT_NAME"}
checar(_anime <= _no_exe and _anime <= set(_cl.CENAS_ANIME),
       f"CUTSCENES: toda cena de anime está no _pro_exe (senão fica FORA do BattleWish.exe) ({sorted(_anime - _no_exe) or 'ok'})")
_fc = _ex.aplicar(dict(_P3["MAX-10"]), "MAX-10", {"entradas": "capsula"})
_pc = Partida(_fc, PERSONAGENS[1], Roteiro([]), Roteiro([]))
_pc.lados_humanos = lambda: [0]
_pc.passo(None)
_tem = _pc.cena_loja is not None
_pc.pular_entrada()  # (não pode pular)
_nao_pulou = _pc.cena_loja is not None and _pc.fase == "entrada"
for _ in range(_cl.DURACAO_MAX + DURACAO_ENTRADA + 10):
    _pc.passo(None)
checar(_tem and _nao_pulou and _pc.cena_loja is None and _pc.fase != "entrada"
       and abs(_pc.L[0].x - _pc.L[0].extra.get("entrada_x", _pc.L[0].x)) < 1 and not _pc.L[0].esconde,
       "CUTSCENES: a entrada da loja passa antes da luta, não pula com ENTER e ele fica no lugar")
_pc2 = Partida(_fc, PERSONAGENS[1], Roteiro([]), Roteiro([]))
_pc2.passo(None)
checar(_pc2.cena_loja is None, "CUTSCENES: o computador (e o online) não têm cena")
_m0 = _sv.moedas()
checar(_ev.converter_sobras(datetime.date(2026, 11, 20)) == 5 and _sv.moedas() == _m0 + 5 and _ev.doces() == 0,
       "HALLOWEEN: depois do evento, os doces que sobraram viram moedas")

# ---- ESQUIVA PERFEITA (v3.0): rolar no último instante deixa o OPONENTE em câmera lenta ----
_king = next(f for f in PERSONAGENS if f["nome"] == "KING RIP")
_tai = next(f for f in PERSONAGENS if f["nome"] == "TAI")


def _esquiva(atraso):
    """O TAI dá um chute; o KING rola (M1+M2 juntos) depois de 'atraso' quadros."""
    pe = Partida(_king, _tai, Roteiro([Entrada()] * atraso + [Entrada(5, True, True)]), Roteiro([Entrada(5, False, True)]))
    pe.fase, pe.tf = "luta", 0
    pe.objetos.pronto, pe.objetos.recarga = False, 10 ** 9
    pe.L[1].x = pe.L[0].x + 90
    v = pe.L[0].vida
    lentos, quadros_tai = 0, 0
    for _ in range(40):
        t0 = pe.L[1].t
        pe.passo(None)
        if pe.L[1].extra.get("lento", 0) > 0:
            lentos += 1
            quadros_tai += pe.L[1].t != t0
    return pe, pe.L[0].vida < v, lentos, quadros_tai


pe, apanhou, lentos, andou = _esquiva(4)
checar(not apanhou and pe.esquiva_txt and lentos > 20 and andou <= lentos // 2 + 1,
       f"ESQUIVA PERFEITA: rolou na hora, não leva nada e o oponente fica em câmera lenta ({lentos} quadros, andou {andou})")
pe, apanhou, lentos, _ = _esquiva(12)
checar(apanhou and lentos == 0, "ESQUIVA PERFEITA: rolou tarde demais, apanha (e ninguém fica lento)")

# ---- EQUILÍBRIO: a FORÇA de cada lutador multiplica o dano dos golpes dele ----
for _f in PERSONAGENS:
    _f["forca"] = FORCA_REAL[_f["nome"]]
_rib = next(f for f in PERSONAGENS if f["nome"] == "RIB")
p = Partida(_rib, BONECO, Roteiro([Entrada(5, especial="E")]), Roteiro([]))
p.fase, p.tf = "luta", 0
p.objetos.pronto, p.objetos.recarga = False, 10 ** 9
p.L[1].x = p.L[0].x + 400
rodar(p, 80)
checar(abs(dano(p) - 5 * FORCA_REAL["RIB"]) < 0.01 and FORCA_REAL["RIB"] < 1 < FORCA_REAL["TAI"],
       f"EQUILÍBRIO: a força multiplica o dano (shuriken do Rib 5 x {FORCA_REAL['RIB']} = {dano(p):.2f})")

if os.path.exists(SAVE_TESTE):
    os.remove(SAVE_TESTE)

print()
print("TUDO CERTO!" if not erros else f"{len(erros)} ERRO(S)")
