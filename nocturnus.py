"""NOCTURNUS: o mutante morcego + escorpião (criado pelo Gomes) — experimento que fugiu do mesmo laboratório do
MAGNUS e do SPHYRUS. Função: ATRAPALHA (bate pouco, mas é insuportável de enfrentar).

Aparência: curvado pra frente, preto e roxo, uns vermelhinhos na cabeça e detalhes azuis. Os BRAÇOS SÃO AS ASAS
(a membrana vai do braço até o corpo, com os dedos compridos de morcego e garras). Orelhas ENORMES com aparelhinhos
azuis nos ouvidos (os cientistas CORTARAM um pedaço de uma delas). CÓDIGO DE BARRAS no peito. Cauda de ESCORPIÃO atrás,
balançando, com o ferrão.
  E      BOLA DE ECO: um redemoinho de ar quase invisível; acertou = CONTROLES TROCADOS 1,5 s (6)
  Q      ABRAÇO DAS ASAS: pega, aperta 3 vezes e solta: PARALISADO 0,5 s (12)
  R      NUVEM DE MORCEGOS: vai até o adversário, morde 8 vezes de 1 e deixa CEGO 2 s
  SHIFT  PENDURADO NO TETO: voa, pendura de cabeça pra baixo seguindo o adversário; SHIFT de novo = CAI em cima (18)
  Z      ULTIMATE: RAJADONA SONORA — tapa os ouvidos com as orelhas e grita: 20, PARALISA 5 s + 1 efeito sorteado
  Z2     2ª ULTIMATE: CANÇÃO DE NINAR — o adversário DORME ~3 s e leva a MORDIDONA VAMPÍRICA (35, rouba vida)
  Passivas (H): ECOLOCALIZAÇÃO / PLANAR / SENSO AUDITIVO (X troca agudo/grave)
  Rival: SPHYRUS. Casa: CAVERNA DOS MORCEGOS.
"""
import math
import random

import pygame

import habilidades as hab
import som
from config import *  # noqa: F401,F403
from corpo import cabeca_eixos, eixos, frente_do_pe, mais
from golpes import GOLPES, misturar, proporcionar, suave
from lutador import Projetil
from max10 import brilho
from pecas import Peca

POSES_NOCTURNUS = {
    # (curvado pra frente, a cabeça na frente do corpo, as garras prontas)
    "parado": dict(pt=(-20, 0), jt=(-10, 22), pf=(18, 0), jf=(24, 22), qd=(0, 44), pc=(14, 74), cb=(19, 90),
                   ct=(8, 60), mt=(16, 46), cf=(24, 62), mf=(32, 48)),
    "andar1": dict(pt=(-24, 2), jt=(-12, 22), pf=(22, 0), jf=(26, 22), qd=(0, 42), pc=(14, 72), cb=(19, 88),
                   ct=(6, 58), mt=(12, 44), cf=(26, 60), mf=(34, 46)),
    "andar2": dict(pt=(-4, 8), jt=(4, 26), pf=(8, 0), jf=(14, 22), qd=(0, 46), pc=(14, 76), cb=(19, 92),
                   ct=(8, 62), mt=(16, 48), cf=(24, 64), mf=(32, 50)),
    "andar3": dict(pt=(22, 0), jt=(26, 22), pf=(-24, 2), jf=(-12, 22), qd=(0, 42), pc=(14, 72), cb=(19, 88),
                   ct=(10, 60), mt=(20, 46), cf=(22, 60), mf=(28, 46)),
    "andar4": dict(pt=(8, 0), jt=(14, 22), pf=(-4, 8), jf=(4, 26), qd=(0, 46), pc=(14, 76), cb=(19, 92),
                   ct=(8, 62), mt=(16, 48), cf=(24, 64), mf=(32, 50)),
    # E: abre a boca e manda o eco (o peito pra frente, as asas pra trás)
    "n_eco": dict(pt=(-22, 0), jt=(-12, 22), pf=(20, 0), jf=(26, 22), qd=(0, 44), pc=(16, 76), cb=(24, 90),
                  ct=(-4, 70), mt=(-16, 62), cf=(4, 72), mf=(-8, 66)),
    # Q: abre as asas... e ABRAÇA apertando
    "n_abraco_abre": dict(pt=(-22, 0), jt=(-12, 22), pf=(20, 0), jf=(26, 22), qd=(0, 44), pc=(12, 78), cb=(18, 94),
                          ct=(4, 84), mt=(-8, 100), cf=(30, 86), mf=(44, 100)),
    "n_abraco": dict(pt=(-22, 0), jt=(-12, 22), pf=(22, 0), jf=(28, 22), qd=(0, 44), pc=(18, 74), cb=(24, 88),
                     ct=(28, 74), mt=(44, 66), cf=(30, 64), mf=(46, 58)),
    # R: chama os morcegos (os braços pra cima)
    "n_chama": dict(pt=(-20, 0), jt=(-10, 22), pf=(18, 0), jf=(24, 22), qd=(0, 46), pc=(12, 78), cb=(16, 94),
                    ct=(2, 86), mt=(-6, 104), cf=(24, 88), mf=(34, 106)),
    # SHIFT: voando, pendurado e o mergulho
    "n_voa": dict(pt=(-12, 14), jt=(-4, 30), pf=(10, 14), jf=(14, 30), qd=(0, 44), pc=(10, 74), cb=(14, 90),
                  ct=(-6, 84), mt=(-24, 92), cf=(22, 84), mf=(40, 92)),
    "n_pendura": dict(pt=(-4, 0), jt=(-2, 22), pf=(4, 0), jf=(4, 22), qd=(0, 44), pc=(10, 74), cb=(14, 90),
                      ct=(20, 72), mt=(12, 60), cf=(22, 70), mf=(10, 58)),
    "n_mergulho": dict(pt=(4, 8), jt=(10, 26), pf=(16, 4), jf=(22, 24), qd=(0, 44), pc=(12, 72), cb=(20, 84),
                       ct=(16, 56), mt=(26, 40), cf=(24, 58), mf=(34, 40)),
    # Z: tapa os ouvidos com as orelhas e GRITA
    "n_tapa": dict(pt=(-20, 0), jt=(-10, 22), pf=(18, 0), jf=(24, 22), qd=(0, 44), pc=(14, 74), cb=(19, 90),
                   ct=(10, 80), mt=(16, 92), cf=(26, 80), mf=(26, 94)),
    "n_grito": dict(pt=(-24, 0), jt=(-12, 22), pf=(22, 0), jf=(28, 22), qd=(0, 44), pc=(16, 76), cb=(26, 92),
                    ct=(-2, 74), mt=(-18, 80), cf=(6, 76), mf=(-10, 84)),
    # Z2, vitória e provocação
    "n_canta": dict(pt=(-20, 0), jt=(-10, 22), pf=(18, 0), jf=(24, 22), qd=(0, 46), pc=(12, 76), cb=(16, 92),
                    ct=(4, 72), mt=(-2, 84), cf=(26, 72), mf=(34, 84)),
    "n_capa": dict(pt=(-18, 0), jt=(-10, 22), pf=(16, 0), jf=(22, 22), qd=(0, 46), pc=(14, 76), cb=(18, 92),
                   ct=(24, 74), mt=(14, 62), cf=(26, 70), mf=(12, 58)),
    "n_ri": dict(pt=(-20, 0), jt=(-10, 22), pf=(18, 0), jf=(24, 22), qd=(0, 44), pc=(14, 76), cb=(18, 92),
                 ct=(10, 82), mt=(18, 92), cf=(24, 82), mf=(28, 94)),
}
proporcionar(POSES_NOCTURNUS)

AZUL_SOM = (150, 210, 255)


def outro_de(l, jogo):
    return jogo.L[1] if jogo.L[0] is l else jogo.L[0]


# =====================================================================
# E: BOLA DE ECO — distorções no ar; acertou = CONTROLES TROCADOS 1,5 s
# =====================================================================
E_SOLTA, E_FIM = 12, 30
TROCADO_TEMPO = 90


def eco(l, outro, jogo):
    t = l.t
    l.vx = 0
    l.fisica(jogo)
    if t == E_SOLTA:
        jogo.projeteis.append(Projetil(l, l.x + 40 * l.s * l.dir, l.y - 80 * l.s, l.dir, GOLPES["noct_bola_eco"]))
        som.tocar("vento", 0.6)
    if t >= E_FIM:
        return "fim"


def eco_acertou(dono, alvo, jogo, res):
    if res == "hit" and alvo.vida > 0:
        alvo.extra["trocado_t"] = TROCADO_TEMPO


def desenha_bola_eco(p, tela):
    """A bola de eco: um REDEMOINHO de ar quase transparente (distorções, não uma bola escancarada)."""
    s = p.dono.s
    camada = pygame.Surface((int(90 * s), int(90 * s)), pygame.SRCALPHA)
    c = camada.get_width() // 2
    for i in range(4):
        r = (10 + i * 8) * s
        a0 = p.t * 0.25 * (1 if i % 2 else -1) + i
        pygame.draw.arc(camada, (*AZUL_SOM, 110 - i * 22), (c - r, c - r, 2 * r, 2 * r), a0, a0 + 4.2,
                        max(2, int(3 * s)))
    tela.blit(camada, (int(p.x - c), int(p.y - c)))


# =====================================================================
# Q: ABRAÇO DAS ASAS — pega, aperta forte 3 vezes e solta: PARALISADO 0,5 s ("travou a coluna")
# =====================================================================
Q_PEGA, Q_APERTA, Q_SOLTA = 8, (8, 16, 24), 32
Q_PARALISA = 30


def abraco(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    if "pegou" in m:
        u = t - m["pegou"]
        l.inv = 999
        outro.x = l.x + 36 * l.s * l.dir
        outro.y = l.y
        l.sobrepor = dict(POSES_NOCTURNUS["n_abraco"])
        if u in Q_APERTA:  # APERTA
            outro.levar(4, l, GOLPES["noct_abraco"])
            outro.vida = max(1, outro.vida) if u != Q_APERTA[-1] else outro.vida
            outro.tremor_hit = 8
            som.tocar("soco", 0.6)
            jogo.tremer(4)
        if u >= Q_SOLTA:  # solta: a coluna TRAVOU
            l.inv = 0
            l.sobrepor = {}
            outro.sobrepor = {}
            if outro.vida > 0:
                outro.mudar("tonto")
                outro.tonto_tempo = Q_PARALISA
                outro.paralisado = True
            return "fim"
        return
    if l.acertou and "errou" not in m:
        if outro.estado == "golpeado" and outro.no_chao():  # PEGOU
            m["pegou"] = t
            outro.mudar("agarrado")
            outro.golpe = None
            outro.sobrepor = dict(outro.poses["golpeado"])
            som.tocar("puf", 0.5)
            return
        m["errou"] = t
    l.fisica(jogo)
    if t >= Q_PEGA + 26:
        return "fim"


# =====================================================================
# R: NUVEM DE MORCEGOS — vai até o adversário, morde 8 vezes de 1 e deixa CEGO 2 s
#    (a nuvem vive no l.extra e o todo_quadro cuida dela: o Nocturnus fica livre depois de chamar)
# =====================================================================
R_CHAMA, R_FIM = 10, 26
NUVEM_TEMPO, NUVEM_CADA, NUVEM_MORDIDAS = 70, 8, 8
CEGO_TEMPO = 120


def chama(l, outro, jogo):
    t = l.t
    l.vx = 0
    l.fisica(jogo)
    if t == R_CHAMA:
        n = l.extra["nuvem"] = dict(x=l.x + 40 * l.s * l.dir, y=l.y - 90 * l.s, t=0, mordidas=0,
                                    registro=(l.nome_golpe, getattr(l, "golpe_id", 0)))
        if abs(outro.x - l.x) < 140 * l.s:  # PERTO (no meio do combo): a nuvem já sai em cima dele e morde na hora
            n["x"], n["y"], n["t"] = outro.x, outro.y - 70 * outro.s, NUVEM_CADA - 1
        som.tocar("puf", 0.6)
    if t >= R_FIM:
        return "fim"


def nuvem_quadro(l, outro, jogo):
    n = l.extra.get("nuvem")
    if not n:
        return
    n["t"] += 1
    alvo_y = outro.y - 70 * outro.s
    n["x"] += (outro.x - n["x"]) * 0.12  # (vai voando até ele)
    n["y"] += (alvo_y - n["y"]) * 0.12
    perto = abs(outro.x - n["x"]) < 50 * l.s
    if (perto and n["t"] % NUVEM_CADA == 0 and n["mordidas"] < NUVEM_MORDIDAS and outro.vida > 0
            and outro.inv <= 0 and outro.estado not in ("caido", "voando", "agarrado")):
        n["mordidas"] += 1
        from inazumaneko import acerto
        res = acerto(jogo, l, outro, "noct_mordisco", n["registro"])  # (conta no combo / treino como o R)
        if res == "hit":
            outro.extra["cego_t"] = max(outro.extra.get("cego_t", 0), CEGO_TEMPO)
            cobrir(outro, MORCEGOS_R if n["mordidas"] == 1 else 1)  # (a 1ª lota; as outras repõem 1)
    if n["t"] >= NUVEM_TEMPO:
        l.extra["nuvem"] = None


def desenha_nuvem(l, tela):
    """Os morcegos voando em volta do ponto da nuvem (só desenho)."""
    n = l.extra.get("nuvem")
    if not n:
        return
    rnd = random.Random(7)
    for i in range(14):
        a = l.t * 0.2 * (1 + rnd.random()) + i * 0.9
        r = (18 + rnd.random() * 26) * l.s
        x, y = n["x"] + math.cos(a) * r, n["y"] + math.sin(a * 1.3) * r * 0.6
        batida = (l.t + i * 3) % 8 < 4
        morcego(tela, x, y, l.s * 0.6, batida)


# =====================================================================
# CEGO = a TELA LOTADA DE MORCEGOS tapando a visão; o adversário tem que BATER (soco/chute) pra espantar eles
# (morcegos_tela: estado da luta, mexe no quadro; o desenho só lê)
# =====================================================================
MORCEGOS_R, MORCEGOS_ULT = 110, 110  # quantos o R (1ª mordida) e a ultimate colocam: a tela TODA tapada
MORCEGOS_MAX = 110
ESPANTA = 5                       # quantos saem a cada soco/chute apertado
SOBRA = 0.10                      # sobrou só 10%: os outros vão embora sozinhos
MORCEGO_SAI = 24                  # quadros voando pra fora da tela


def cobrir(alvo, n):
    """Enche a tela do alvo de morcegos (até n a mais, no máximo MORCEGOS_MAX). Eles ficam numa GRADE bagunçada
    (12 colunas x 7 linhas, cada um meio torto) pra tapar tudo; os que sobram vão em lugares aleatórios.
    Só saem quando o alvo BATE (não somem sozinhos)."""
    lista = alvo.extra.setdefault("morcegos_tela", [])
    ficando = sum(1 for m in lista if not m["sai"])
    novos = min(n, MORCEGOS_MAX - ficando)
    alvo.extra["morc_total"] = (alvo.extra.get("morc_total", 0) if ficando else 0) + novos
    for k in range(novos):
        c = (ficando + k) % MORCEGOS_MAX
        if c < 84:
            x = (c % 12 + 0.5 + random.uniform(-0.35, 0.35)) / 12 * LARGURA
            y = (0.06 + (c // 12 + 0.5 + random.uniform(-0.3, 0.3)) / 7 * 0.94) * ALTURA
        else:
            x, y = random.uniform(0.0, 1.0) * LARGURA, random.uniform(0.05, 1.0) * ALTURA
        lista.append(dict(x=x, y=y, fase=random.randint(0, 7), tam=random.uniform(10.0, 13.0), sai=0,
                          vx=random.choice((-1, 1)) * random.uniform(10, 16), vy=random.uniform(-8, -3)))


def morcegos_tela_quadro(outro):
    """Todo quadro: o adversário espanta morcegos BATENDO (soco/chute): saem os ESPANTA mais perto de ONDE o golpe
    pegou (bateu na borda = limpa a borda) e voam pra longe dali. Os outros FICAM; quando sobrar só 10%
    (SOBRA), esses vão embora sozinhos."""
    x = outro.extra
    lista = x.get("morcegos_tela")
    if not lista:
        x["morc_bateu"] = False
        return
    e = getattr(outro, "entrada_atual", None)
    bate = bool(e and (e.soco or e.chute))
    if x.get("cego_cpu"):  # o COMPUTADOR não 'vê' a tela: em vez de bater, os morcegos vão saindo sozinhos
        bate = x.get("cego_cpu_t", 0) % hab.CEGO_CPU_BATE == 1
        x["morc_bateu"] = False
    if bate and not x.get("morc_bateu"):
        # o PONTO do golpe: na frente dele, na altura do soco (chute/agachado mais baixo)
        baixo = bool(e and (e.chute or e.dir in (1, 2, 3)))
        px = outro.x + outro.dir * 70 * outro.s
        py = outro.y - (55 if baixo else 95) * outro.s
        ficando = sorted((m for m in lista if not m["sai"]), key=lambda m: (m["x"] - px) ** 2 + (m["y"] - py) ** 2)
        for m in ficando[:ESPANTA]:
            m["sai"] = 1
            dx, dy = m["x"] - px, m["y"] - py
            n = math.hypot(dx, dy) or 1
            m["vx"], m["vy"] = dx / n * 15 + outro.dir * 4, dy / n * 15 - 4  # (foge do soco)
        resto = len(ficando) - ESPANTA
        if 0 < resto <= x.get("morc_total", 0) * SOBRA:  # tirou 90%: o resto vai embora
            for m in ficando[ESPANTA:]:
                m["sai"] = 1
    x["morc_bateu"] = bate
    for m in lista:
        if m["sai"]:
            m["sai"] += 1
            m["x"] += m["vx"]
            m["y"] += m["vy"]
    x["morcegos_tela"] = [m for m in lista if m["sai"] < MORCEGO_SAI]


MORCEGO_PIXEL = (
    ["k...........k",
     "kk...k.k...kk",
     "kpk..kpk..kpk",
     "kppkkpppkkppk",
     "kpPppvpvppPpk",
     ".kpPpppppPpk.",
     "..kk.kwk.kk..",
     "......k......"],
    [".............",
     ".....k.k.....",
     ".....kpk.....",
     "..kkkpppkkk..",
     "kkpPpvpvpPpkk",
     "kpPpppppppPpk",
     "kpk.k.w.k.kpk",
     "k...........k"],
)
MORCEGO_CORES = {"k": (14, 10, 20), "p": (52, 36, 72), "P": (84, 60, 112), "v": (120, 210, 255), "w": (240, 240, 245)}
_morcego_cache = {}


def morcego_pixel(tela, x, y, tam, batida):
    """Um morcegão em PIXEL ART (tam = tamanho do pixel), centrado em (x, y)."""
    chave = (int(tam * 2), batida)
    img = _morcego_cache.get(chave)
    if img is None:
        mapa = MORCEGO_PIXEL[0 if batida else 1]
        peq = pygame.Surface((len(mapa[0]), len(mapa)), pygame.SRCALPHA)
        for j, linha in enumerate(mapa):
            for i, c in enumerate(linha):
                if c != ".":
                    peq.set_at((i, j), MORCEGO_CORES[c])
        img = pygame.transform.scale(peq, (int(peq.get_width() * chave[0] / 2), int(peq.get_height() * chave[0] / 2)))
        _morcego_cache[chave] = img
    tela.blit(img, (int(x - img.get_width() / 2), int(y - img.get_height() / 2)))


def desenha_morcegos_tela(outro, tela, t):
    for i, m in enumerate(outro.extra.get("morcegos_tela") or ()):
        balanco = 0 if m["sai"] else math.sin(t * 0.12 + i) * 6
        batida = (t + m["fase"]) % (4 if m["sai"] else 8) < (2 if m["sai"] else 4)
        morcego_pixel(tela, m["x"] + balanco, m["y"] + math.cos(t * 0.15 + i * 2) * 4, m["tam"], batida)


def morcego(tela, x, y, s, batida):
    """Um morceguinho (asas pra cima ou pra baixo)."""
    borda, cor = (16, 12, 22), (50, 36, 66)
    dy = -4 if batida else 3
    asa_e = [(x, y), (x - 9 * s, y + dy * s), (x - 5 * s, y + 2 * s)]
    asa_d = [(x, y), (x + 9 * s, y + dy * s), (x + 5 * s, y + 2 * s)]
    for a in (asa_e, asa_d):
        pygame.draw.polygon(tela, cor, a)
        pygame.draw.polygon(tela, borda, a, 1)
    pygame.draw.circle(tela, borda, (int(x), int(y)), max(2, int(2.6 * s)))
    pygame.draw.circle(tela, (120, 200, 255), (int(x + 1), int(y)), 1)


# =====================================================================
# SHIFT: PENDURADO NO TETO — voa, pendura de cabeça pra baixo seguindo o adversário; SHIFT de novo (ou o tempo
#        acabar) = CAI em cima dele (18)
# =====================================================================
S_SOBE, S_PENDURA_MAX = 12, 70
TETO = 40


def teto(l, outro, jogo):
    t = l.t
    m = l.memo
    if "caiu" in m:  # já caiu: levanta
        l.angulo = 0
        l.fisica(jogo)
        if t - m["caiu"] >= 14:
            return "fim"
        return
    if "cai" in m:  # CAINDO de garra
        l.angulo = 0
        l.inv = 0
        l.vy = max(l.vy, 14)
        l.sobrepor = dict(POSES_NOCTURNUS["n_mergulho"])
        l.fisica(jogo)
        if l.no_chao():
            m["caiu"] = t
            l.sobrepor = {}
            jogo.tremer(10)
            som.tocar("queda")
            if abs(outro.x - l.x) < 80 * l.s and outro.estado not in ("caido",) and outro.inv <= 0:
                from inazumaneko import acerto
                acerto(jogo, l, outro, "noct_queda")
        return
    alto = TETO + 100 * l.s  # (os pés no teto, de cabeça pra baixo)
    l.inv = 999
    l.vx = l.vy = 0
    if t < S_SOBE:  # SOBE voando
        k = suave(t / S_SOBE)
        l.y = l.y + (alto - l.y) * k * 0.5
        l.sobrepor = dict(POSES_NOCTURNUS["n_voa"])
        if t == 1:
            som.tocar("vento", 0.6)
        return
    l.y = alto  # PENDURADO, seguindo o adversário devagar
    l.angulo = math.pi
    l.sobrepor = dict(POSES_NOCTURNUS["n_pendura"])
    l.x += max(-3.0, min(3.0, outro.x - l.x)) * 0.8
    e = getattr(l, "entrada_atual", None)
    apertou = e is not None and e.especial == "SHIFT" and t > S_SOBE + 6
    if apertou or t >= S_SOBE + S_PENDURA_MAX:
        m["cai"] = t
        som.tocar("vento", 0.8)


# =====================================================================
# Z: ULTIMATE — tapa os ouvidos com as orelhas e solta a RAJADONA SONORA: 20, PARALISA 5 s + um efeito sorteado
# =====================================================================
U_GRITA, U_FIM = 24, 60
U_DANO, U_PARALISA = 20, 300
EFEITOS_ULT = ("trocado", "cego", "lento", "tonto", "enjoo")


def ultimate(l, outro, jogo):
    t = l.t
    l.vx = 0
    l.inv = 999
    l.fisica(jogo)
    if t == U_GRITA:
        som.tocar("explosao", 0.8)
        som.tocar("uivo", 0.6)
        jogo.tremer(24)
        if hasattr(jogo, "clarao"):
            jogo.clarao = max(jogo.clarao, 4)
        if outro.vida > 0 and outro.inv <= 0:
            outro.levar(U_DANO, l, GOLPES["noct_ultimate"])
            outro.tremor_hit = 14
            if outro.vida > 0:
                outro.mudar("tonto")
                outro.golpe = None
                outro.tonto_tempo = U_PARALISA
                outro.paralisado = True
                efeito = random.choice(EFEITOS_ULT)  # (random da luta: igual nos dois PCs)
                aplicar_efeito(outro, efeito, U_PARALISA + 150)
    if t >= U_FIM:
        l.inv = 0
        return "fim"


def aplicar_efeito(alvo, efeito, tempo):
    x = alvo.extra
    if efeito == "trocado":
        x["trocado_t"] = tempo
    elif efeito == "cego":
        x["cego_t"] = tempo
        cobrir(alvo, MORCEGOS_ULT)
    elif efeito == "enjoo":
        x["enjoo_t"] = tempo
    elif efeito == "lento":
        x["neve"], x["neve_t"] = 3, tempo
    elif efeito == "tonto":
        x["tonto_extra"] = tempo


def ultimate_efeito(l, tela):
    """As ONDAS DE SOM saindo dele (a tela toda)."""
    u = l.t - U_GRITA
    if 0 <= u < 30:
        cx, cy = l.x + 20 * l.s * l.dir, l.y - 90 * l.s
        camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        for i in range(5):
            r = (u * 30 + i * 70) * l.s
            if r > 0:
                pygame.draw.circle(camada, (*AZUL_SOM, max(0, 200 - u * 6 - i * 25)), (int(cx), int(cy)), int(r),
                                   max(3, int(8 * l.s)))
        tela.blit(camada, (0, 0))


# =====================================================================
# Z2: 2ª ULTIMATE — CANÇÃO DE NINAR: o adversário DORME ~3 s e leva a MORDIDONA VAMPÍRICA (35, rouba vida)
#     (o ult2.py pluga: logica=cancao, efeito=cancao_efeito)
# =====================================================================
C_DORME, C_VOA, C_MORDE, C_FIM = 40, 70, 90, 120
C_SONO, C_DANO, C_CURA = 180, 35, 15


def cancao(l, outro, jogo):
    import ult2
    t = l.t
    m = l.memo
    ult2.tela_toda(l)
    l.vx = 0
    l.inv = 999
    if t < C_DORME:  # CANTA (zoom nele)
        ult2.camera(jogo, 1.3, l.x, l.y - 90 * l.s)
        l.sobrepor = dict(POSES_NOCTURNUS["n_canta"])
        if t % 10 == 0:
            som.tocar("blip", 0.4)
    elif t == C_DORME:  # o adversário DORME
        if ult2.pode_pegar(outro, 200):
            m["dormiu"] = True
            outro.mudar("tonto")
            outro.golpe = None
            outro.tonto_tempo = C_SONO
            outro.extra["dormindo_t"] = C_SONO
    elif C_DORME < t < C_MORDE and m.get("dormiu"):  # voa até ele
        k = suave((t - C_VOA) / (C_MORDE - C_VOA)) if t >= C_VOA else 0
        if t >= C_VOA:
            l.x += (outro.x - l.dir * 40 * l.s - l.x) * k * 0.3
            l.sobrepor = dict(POSES_NOCTURNUS["n_voa"])
    elif t == C_MORDE:
        if m.get("dormiu"):  # a MORDIDONA VAMPÍRICA (rouba vida)
            l.sobrepor = dict(POSES_NOCTURNUS["n_abraco"])
            outro.extra["dormindo_t"] = 0
            ult2.bate(l, outro, jogo, C_DANO, "noct_mordidona", ultimo=True)
            l.vida = min(l.vida_max, l.vida + C_CURA)
            ult2.impacto(jogo, 12, 20, 4)
    elif t > C_MORDE + 14:
        l.sobrepor = {}
    l.fisica(jogo)
    if t >= C_FIM:
        l.inv = 0
        l.sobrepor = {}
        return "fim"


def cancao_efeito(l, tela):
    """As NOTINHAS saindo da boca (só desenho)."""
    t = l.t
    if t < C_DORME + 10:
        for i in range(6):
            u = (t * 2 + i * 22) % 120
            x = l.x + l.dir * (20 + u * 2.2) * l.s
            y = l.y - (100 + math.sin(u * 0.15 + i) * 16) * l.s
            cor = (200, 160, 255) if i % 2 else AZUL_SOM
            pygame.draw.circle(tela, cor, (int(x), int(y)), max(2, int(3 * l.s)))
            pygame.draw.line(tela, cor, (x + 3 * l.s, y), (x + 3 * l.s, y - 10 * l.s), max(1, int(1.5 * l.s)))


# =====================================================================
# os EFEITOS NA TELA (cego / enjoo / sono): o partida chama isso por cima de tudo (efeito_tela da ficha)
# =====================================================================
def eh_computador(alvo, jogo):
    """O alvo é o COMPUTADOR? (pelo tipo do controle: igual nos dois PCs do online, não mexe no lockstep)"""
    from controles import BonecoTreino, Computador
    ctrl = getattr(jogo, "ctrl", None)
    if not ctrl or alvo not in getattr(jogo, "L", ()):
        return False
    return isinstance(ctrl[jogo.L.index(alvo)], (Computador, BonecoTreino))


def tela_de_gente(alvo, jogo):
    """A tela é de quem SOFRE o efeito? Só tapa/entorta a tela se o alvo é um jogador de verdade NESTE PC (contra o
    computador, quem usou o golpe não fica cego; no ONLINE, só o PC de quem levou)."""
    if jogo is None or not hasattr(jogo, "lados_humanos") or alvo not in getattr(jogo, "L", ()):
        return True
    return jogo.L.index(alvo) in jogo.lados_humanos()


def efeito_tela(l, outro, tela, jogo=None):
    """Desenha, POR CIMA DA LUTA, o que o adversário sofre: CEGO (a tela LOTADA de morcegos — bate pra espantar), ENJOO (a tela toda ondulando com uma cor estranha) e SONO (os Zzz)."""
    x = outro.extra
    w, h = tela.get_size()
    if not tela_de_gente(outro, jogo):  # (quem sofre é o COMPUTADOR / o outro PC: não tapa a tela de quem joga)
        x = dict(x, enjoo_t=0)
    elif x.get("morcegos_tela"):
        desenha_morcegos_tela(outro, tela, l.t)  # (CEGO: a tela LOTADA de morcegos — por cima de tudo, no fim)
    if x.get("enjoo_t", 0) > 0:
        camada = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(0, h, 12):
            dx = math.sin(i * 0.05 + l.t * 0.15) * 16
            pygame.draw.line(camada, (120, 200, 90, 40), (dx, i), (w + dx, i + 6), 6)
        tela.blit(camada, (0, 0))
    if x.get("dormindo_t", 0) > 0:
        for i in range(3):
            u = (l.t + i * 20) % 60
            zx = outro.x + (10 + u * 0.5) * outro.s
            zy = outro.y - (130 + u) * outro.s
            from efeitos import texto
            texto(tela, "Z", int(14 + i * 5), (200, 200, 255), (int(zx), int(zy)))


# =====================================================================
# Golpes
# =====================================================================
def _registra(nome, **g):
    g.setdefault("base", "parado")
    g.setdefault("pose", "parado")
    g.setdefault("caixa", None)
    g.setdefault("especial", True)
    g["total"] = g.get("total", g["ini"] + g["ativo"] + g.get("rec", 0))
    GOLPES[nome] = g


_registra("noct_eco", ini=E_SOLTA, ativo=1, rec=E_FIM - E_SOLTA, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=eco, ia="longe", quadros=[(0, "parado"), (5, "n_eco"), (E_SOLTA + 4, "n_eco"), (E_FIM, "parado")])
_registra("noct_bola_eco", ini=0, ativo=1, rec=0, proj=True, raio=20, vel=7, dano=6, hit=14, defe=8, emp=2,
          nivel="medio", desenho_proj=desenha_bola_eco, ao_acertar=eco_acertou)
_registra("noct_abraco", ini=Q_PEGA, ativo=6, rec=0, janelas=((Q_PEGA, Q_PEGA + 6),), caixa=(10, 30, 62, 110), dano=0,
          hit=60, defe=0, emp=0, nivel="medio", imbloqueavel=True, logica=abraco, ia="perto",
          quadros=[(0, "parado"), (4, "n_abraco_abre"), (Q_PEGA, "n_abraco"), (Q_PEGA + 26, "n_abraco")])
GOLPES["noct_abraco"]["total"] = 9999
_registra("noct_chama", ini=R_CHAMA, ativo=1, rec=R_FIM - R_CHAMA, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=chama, ia="medio", quadros=[(0, "parado"), (5, "n_chama"), (R_CHAMA + 6, "n_chama"), (R_FIM, "parado")])
GOLPES["noct_mordisco"] = dict(dano=2, hit=10, defe=4, emp=0, nivel="medio", especial=True)
_registra("noct_teto", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", logica=teto, ia="medio",
          quadros=[(0, "n_voa")])
GOLPES["noct_teto"]["total"] = 9999
GOLPES["noct_queda"] = dict(dano=18, hit=24, defe=12, emp=4, nivel="medio", especial=True, derruba=True, voo=(6, 8))
_registra("noct_ultimate", ini=U_GRITA, ativo=1, rec=U_FIM - U_GRITA, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          ultimate=True, imbloqueavel=True, logica=ultimate, efeito=ultimate_efeito, ia="ultimate",
          quadros=[(0, "parado"), (8, "n_tapa"), (U_GRITA - 2, "n_tapa"), (U_GRITA + 2, "n_grito"),
                   (U_FIM - 10, "n_grito"), (U_FIM, "parado")])
GOLPES["noct_ultimate"]["total"] = 9999
GOLPES["noct_mordidona"] = dict(dano=C_DANO, hit=30, defe=12, emp=6, nivel="medio", especial=True, ultimate=True,
                                ultimate2=True)

GOLPES_NOCTURNUS = {"E": "noct_eco", "Q": "noct_abraco", "R": "noct_chama", "SHIFT": "noct_teto",
                    "Z": "noct_ultimate"}
NOMES = {"E": "bola de eco (controles trocados)", "Q": "abraço das asas (paralisa)", "R": "nuvem de morcegos (cego)",
         "SHIFT": "pendurado no teto (cai em cima)", "Z": "RAJADONA SONORA", "Z2": "CANÇÃO DE NINAR"}


def todo_quadro(l, jogo):
    outro = outro_de(l, jogo)
    nuvem_quadro(l, outro, jogo)
    morcegos_tela_quadro(outro)
    l.extra["tela_toda"] = bool(l.extra.get("nuvem"))  # (a nuvem fica longe dele: efeitos na TELA TODA)
    o = outro.extra  # o COMPUTADOR com a tela lotada luta às cegas (o habilidades.trocar_controles aplica)
    o["cego_cpu"] = any(not m["sai"] for m in o.get("morcegos_tela") or ()) and eh_computador(outro, jogo)
    o["cego_cpu_t"] = o.get("cego_cpu_t", 0) + 1 if o["cego_cpu"] else 0
    hab.nocturnus_quadro(l, jogo)


def tecla_x(l):
    """SENSO AUDITIVO: o X troca entre AGUDO e GRAVE."""
    if "senso" in hab.ativas(l):
        l.extra["senso"] = "grave" if l.extra.get("senso", "agudo") == "agudo" else "agudo"
        l.extra["senso_flash"] = 30
        som.tocar("blip", 0.5)


def desenhar_sempre(l, tela):
    desenha_nuvem(l, tela)


# =====================================================================
# ENTRADA: a NUVEM DE MORCEGOS chega voando e se junta formando ele
# =====================================================================
EN_JUNTA, EN_FIM = 40, 70


def entrada(l, t, jogo):
    l.esconde = t < EN_JUNTA
    if t == EN_JUNTA:
        som.tocar("puf", 0.8)
    l.sobrepor = dict(POSES_NOCTURNUS["n_capa"]) if EN_JUNTA <= t < EN_JUNTA + 12 else \
        (misturar(POSES_NOCTURNUS["n_capa"], POSES_NOCTURNUS["n_chama"], suave((t - EN_JUNTA - 12) / 8))
         if t < EN_JUNTA + 24 else {})
    l.t += 1


def entrada_efeito(l, tela, t):
    if t < EN_JUNTA + 6:
        rnd = random.Random(3)
        for i in range(30):
            k = suave(min(1.0, t / EN_JUNTA))
            ox = rnd.uniform(-1, 1) * 520 * (1 - k)
            oy = rnd.uniform(-1, 0.2) * 320 * (1 - k)
            gira = 30 * (1 - k * 0.6) * l.s
            x = l.x + ox + math.cos(t * 0.3 + i) * gira
            y = l.y - 70 * l.s + oy + math.sin(t * 0.4 + i) * gira * 1.4
            morcego_pixel(tela, x, y, 2.4 * l.s, (t + i) % 8 < 4)


# =====================================================================
# VITÓRIA: ASAS-CAPA — se fecha nas asas e só os olhos ficam brilhando
# =====================================================================
def vitoria(l, t, jogo):
    l.sobrepor = misturar(POSES_NOCTURNUS["parado"], POSES_NOCTURNUS["n_capa"], suave(min(1, t / 20)))
    if t == 20:
        som.tocar("vento", 0.4)


def vitoria_efeito(l, tela, t):
    if t > 24:
        p = l.pose_vista or l.pose_atual()
        cx, cy = l.ponto(p, "cb")
        for dx in (4, 9):
            brilho(tela, (int(cx + dx * l.s * l.dir), int(cy - 2 * l.s)), int(6 * l.s), (150, 230, 255), 160)


# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  p P pelo preto/roxo (e o brilho)  r vermelhinhos da cabeça  b B azul (aparelhos do ouvido)
#   e olho  w presas e garras  c código de barras  m M membrana da asa (roxa)  v veneno do ferrão
PALETA = {
    "k": (14, 10, 20), "p": (38, 28, 50), "P": (70, 52, 92), "r": (200, 44, 64), "b": (70, 160, 255),
    "B": (170, 220, 255), "e": (150, 230, 255), "w": (240, 236, 240), "c": (220, 220, 232), "m": (96, 60, 132),
    "M": (64, 40, 92), "v": (90, 200, 255), "f": (104, 86, 128), "F": (138, 118, 162),
}
S_REF = 1.38 / 3


def _m(linhas, w):
    return [linha.ljust(w, ".")[:w] for linha in linhas]


# a cabeça de lado (olhando pra direita): orelha de TRÁS cortada (o pedaço que os cientistas tiraram),
# orelha da frente inteira, os dois com o aparelhinho azul dentro
CABECA = Peca(_m([
    "...........kk.........",
    "..........kpk.........",
    "..kkkkk...kpmk........",
    "..kpmpk..kpmmpk.......",
    "..kpmmpk.kpmmpk.......",
    ".kpmmmpk.kpmmmpk......",
    ".kpmmmpk.kpmmmpk......",
    ".kpmbmpk.kpmmbmpk.....",
    ".kpmBbmpkkpmmBbmpk....",
    ".kpmbbmpkkpmmbbmpk....",
    "..kpmmpk.kpmmmmpk.....",
    "..kppmppkkppmmppk.....",
    "..kpppppppppppppk.....",
    "..kprppppprrppppPk....",
    ".kpppppppppkkppppPk...",
    ".kppppppppkBekppPPPk..",
    ".kpppppppppkkpppPPPssk",
    "..kppppppppppppPPPPsk.",
    "..kpppppppppkkkkkkkk..",
    "...kppppppkwkwkwkk....",
    "...kpppppppPPPPk......",
    "....kkpppppppkk.......",
    ".......kkkkkk.........",
], 22), dict(PALETA, s=(20, 14, 26)), a=(9, 20), b=(9, 0), estica=False)
# (a orelha de TRÁS tem o topo RETO: é o pedaço que os cientistas cortaram)

TRONCO = Peca(_m([
    "..kkFkFkFkk....",
    ".kfFfFfFfFfk...",
    "kpfFfFfFfFfFk..",
    "kppfffffffffk..",
    "kpppPPffPckckk.",
    "kpppPffffckckFk",
    "kppppPfffckckFk",
    "kppppPffffffFk.",
    "kspppPPfffffk..",
    ".kspppPfffPk...",
    ".kssppppPPPk...",
    "..ksppbppPk....",
    "..ksspppppk....",
    "...kkkkkkk.....",
], 15), dict(PALETA, s=(24, 16, 32)), a=(7, 12), b=(7, 1))

BRACO = Peca(_m([".kk.", "kppk", "kpPk", "kpPk", "kppk", ".kk."], 4), PALETA, a=(2, 0), b=(2, 5))
ANTEBRACO = Peca(_m([".kk.", "kpPk", "kpPk", "kpPk", "kpPk", ".kk."], 4), PALETA, a=(2, 0), b=(2, 5))
MAO = Peca(_m([".kk..", "kppk.", "kwkwk"], 5), PALETA, a=(1, 0), b=(1, 2), estica=False)
COXA = Peca(_m([".kkkkk.", "kpPPppk", "kpPPppk", "kpPpppk", "kpPpppk", ".kPppk.", ".kpppk.", "..kpk..",
                "..kkk.."], 7), PALETA, a=(3, 0), b=(3, 8))
CANELA = Peca(_m([".kkk.", "kpPpk", "kpPpk", "kpPpk", ".kPk.", ".kpk.", ".kpk.", ".kkk."], 5), PALETA, a=(2, 0), b=(2, 7))
PE = Peca(_m([".kkkkk..", "kpppppkk", "kpppppppk", "kwkwkwkwk", ".w.w.w.w."], 9), PALETA, a=(2, 1), b=(6, 1),
          estica=False)


def _cor(letra):
    import pecas
    return (pecas.TROCA or {}).get(letra, PALETA[letra])


def asa(tela, ombro, cot, mao, quadril, esc, d, branco=False, atras=False, abre=0.0):
    """A ASA: a membrana vai do ombro, passa pelo cotovelo e pela mão, desce pelos 3 dedos compridos de morcego
    e volta no quadril. abre 0..1 = os dedos abrindo pra trás (asa aberta)."""
    borda = (16, 12, 22)
    memb = (245, 245, 250) if branco else (_cor("M") if atras else _cor("m"))
    osso = (245, 245, 250) if branco else _cor("p")
    pontas = []
    for i, (ang, comp) in enumerate(((0.12, 16), (0.32, 14), (0.55, 11))):
        a = math.pi / 2 + d * (ang + abre * (1.2 + i * 0.35))  # (pra baixo e pra trás; abrindo, vai pra cima)
        comp *= 1 + 0.6 * abre
        pontas.append((mao[0] + math.cos(a) * comp * esc, mao[1] + math.sin(a) * comp * esc))
    tras_quadril = (quadril[0] - d * 2 * esc, quadril[1] - 4 * esc)
    contorno = [ombro, cot, mao] + pontas + [tras_quadril]
    pygame.draw.polygon(tela, memb, contorno)
    if not branco:
        sombra = tuple(int(c * 0.72) for c in memb)
        claro = tuple(min(255, int(c * 1.25)) for c in memb)
        # a SOMBRA perto da borda de baixo (faixa entre os dedos e a borda)
        miolo = [(cot[0] * 0.5 + p_[0] * 0.5, cot[1] * 0.5 + p_[1] * 0.5) for p_ in pontas]
        pygame.draw.polygon(tela, sombra, [mao] + pontas + [tras_quadril] + miolo[::-1])
        # o BRILHO junto do braço
        pygame.draw.polygon(tela, claro, [ombro, cot, (cot[0] * 0.7 + quadril[0] * 0.3, cot[1] * 0.7 + quadril[1] * 0.3)])
        for p_ in pontas:  # as DOBRAS saindo do cotovelo
            pygame.draw.line(tela, sombra, cot, (cot[0] * 0.25 + p_[0] * 0.75, cot[1] * 0.25 + p_[1] * 0.75),
                             max(1, int(esc * 0.7)))
    # a borda de baixo "recortada" (entre os dedos a membrana faz uma curvinha pra dentro)
    for p1, p2 in zip([mao] + pontas, pontas + [tras_quadril]):
        meio = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 - 3 * esc)
        pygame.draw.polygon(tela, memb, [p1, meio, p2])
        pygame.draw.lines(tela, borda, False, [p1, meio, p2], max(1, int(esc * 0.9)))
    for pt in pontas:  # os DEDOS compridos (ossos da asa)
        pygame.draw.line(tela, borda, mao, pt, max(2, int(esc * 1.6)))
        pygame.draw.line(tela, osso, mao, pt, max(1, int(esc * 0.8)))


def cauda(tela, quadril, esc, d, t, branco=False, levanta=0.0):
    """A CAUDA DE ESCORPIÃO: GOMOS (plaquinhas) afinando até a ponta, atrás e balançando; no fim a BOLSA DE VENENO e o
    FERRÃO curvado (levanta 0..1 = sobe pra atacar)."""
    borda = (16, 12, 22)
    pts = []
    for i in range(9):
        k = i / 8
        x = quadril[0] - d * (4 + 22 * k - 12 * levanta * k * k) * esc
        y = quadril[1] + (2 + 6 * k - 18 * k * k - 34 * levanta * k ** 1.5 + 2 * math.sin(t * 0.09 + k * 3) * k) * esc
        pts.append((x, y))
    cor, claro = ((245, 245, 250), (245, 245, 250)) if branco else (_cor("p"), _cor("P"))
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        w1, w2 = (3.4 - i * 0.28) * esc, (3.0 - i * 0.28) * esc
        placa = [(a[0] + nx * w1, a[1] + ny * w1), (b[0] + nx * w2, b[1] + ny * w2),
                 (b[0] - nx * w2, b[1] - ny * w2), (a[0] - nx * w1, a[1] - ny * w1)]
        pygame.draw.polygon(tela, borda, [(x + nx * esc * 0.6, y + ny * esc * 0.6) for x, y in placa[:2]] +
                            [(x - nx * esc * 0.6, y - ny * esc * 0.6) for x, y in placa[2:]])
        pygame.draw.polygon(tela, cor, placa)
        cima = placa[:2] if ny < 0 else placa[2:]
        pygame.draw.line(tela, claro, cima[0], cima[1], max(1, int(esc)))  # a borda clara de cima do gomo
        pygame.draw.line(tela, borda, placa[0], placa[3], max(1, int(esc * 0.6)))  # a emenda entre os gomos
    # a BOLSA DE VENENO
    (fx, fy), (gx, gy) = pts[-1], pts[-2]
    dx, dy = fx - gx, fy - gy
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    bolsa = (fx + ux * 2.5 * esc, fy + uy * 2.5 * esc)
    pygame.draw.circle(tela, borda, (int(bolsa[0]), int(bolsa[1])), int(3.6 * esc))
    pygame.draw.circle(tela, claro, (int(bolsa[0]), int(bolsa[1])), int(2.8 * esc))
    if not branco:
        pygame.draw.circle(tela, _cor("v"), (int(bolsa[0] - ux * esc), int(bolsa[1] - uy * esc)), max(1, int(esc)))
    # o FERRÃO curvado
    base = (bolsa[0] + ux * 2.5 * esc, bolsa[1] + uy * 2.5 * esc)
    meio = (base[0] + ux * 4 * esc - uy * 2 * esc * d, base[1] + uy * 4 * esc + ux * 2 * esc * d)
    ponta = (meio[0] - uy * 4 * esc * d + ux * 1.5 * esc, meio[1] + ux * 4 * esc * d + uy * 1.5 * esc)
    pygame.draw.lines(tela, borda, False, [base, meio, ponta], max(3, int(esc * 2.6)))
    pygame.draw.lines(tela, (245, 245, 250) if branco else _cor("r"), False, [base, meio, ponta], max(2, int(esc * 1.4)))
    if not branco:
        pygame.draw.circle(tela, _cor("v"), (int(ponta[0]), int(ponta[1])), max(1, int(esc * 0.9)))


def quanto_capa(l):
    """0..1: as ASAS FECHADAS feito capa (vitória, e na entrada quando os morcegos se juntam)."""
    if l.estado == "vitoria":
        return suave(min(1.0, max(0.0, (l.t - 4) / 16)))
    t = l.entrada_t
    if t is not None and t >= EN_JUNTA:
        return 1.0 if t < EN_JUNTA + 14 else max(0.0, 1 - (t - EN_JUNTA - 14) / 8)
    return 0.0


def capa(sup, cb, y_joelho, y_joelho2, d, k, branco):
    """A CAPA DE ASAS em pixel: as duas asas fechadas em volta do corpo, do queixo até os joelhos, com as
    dobras (os dedos) e as garrinhas segurando na frente. Só as orelhas e os OLHOS ficam pra fora."""
    borda = (16, 12, 22)
    cor, sombra, dobra = ((245, 245, 250),) * 3 if branco else (_cor("M"), tuple(int(c * 0.7) for c in _cor("M")),
                                                                 _cor("m"))
    cx = cb[0] - d * 1
    topo = cb[1] + 2
    baixo = max(y_joelho, y_joelho2) + 2
    alto = baixo - topo
    w0, w1 = 7 * k + 3, 15 * k + 4  # (abre/fecha dos lados)
    lado_e = [(cx - w0, topo), (cx - w1, topo + alto * 0.25), (cx - w1 - 2, baixo - 3)]
    lado_d = [(cx + w1 + 2, baixo - 3), (cx + w1, topo + alto * 0.25), (cx + w0, topo)]
    pontas, n = [], 5  # a borda de baixo em BICOS (as pontas dos dedos)
    for i in range(n + 1):
        x = cx - w1 - 2 + (2 * w1 + 4) * i / n
        pontas.append((x, baixo + (0 if i % 2 else -3)))
    contorno = lado_e + pontas + lado_d
    pygame.draw.polygon(sup, borda, [(x + (1 if x > cx else -1), y + 1) for x, y in contorno])
    pygame.draw.polygon(sup, cor, contorno)
    pygame.draw.polygon(sup, sombra, [(cx - d * 2, topo + 4), (cx + d * (w1 + 1), topo + alto * 0.3),
                                      (cx + d * (w1 + 2), baixo - 3), (cx - d * 2, baixo)])
    for i in range(1, n, 2):  # as DOBRAS descendo até os bicos
        pygame.draw.line(sup, dobra if not branco else borda, (cx + (pontas[i][0] - cx) * 0.3, topo + 5), pontas[i])
    pygame.draw.line(sup, borda, (cx, topo + 2), (cx, baixo - 1))  # onde as duas asas se encontram
    pygame.draw.polygon(sup, borda, contorno, 1)
    if not branco:  # as GARRINHAS segurando a capa fechada
        for dx in (-2, 1):
            pygame.draw.line(sup, _cor("w"), (cx + dx, topo + 1), (cx + dx + 1, topo + 3))


def desenhar_nocturnus(l, tela, p, branco):
    from inazumaneko import em_pixel  # (o pincel de PIXEL ART: desenha pequeno e amplia sem borrar)
    esc = l.s / S_REF
    d = l.lado()
    espelho = d < 0
    perto_v = "branco" if branco else "normal"
    longe_v = "branco" if branco else "escuro"

    def P(k):
        return l.ponto(p, k)

    def perna(pe, joelho, var):
        q, j, e = P("qd"), P(joelho), P(pe)
        CANELA.desenhar(tela, j, e, esc, espelho, var)
        fr, _ = frente_do_pe(j, e, d)
        PE.desenhar(tela, e, mais(e, fr, 6), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    def abre_de(mao):
        """A asa ABRE sozinha quando a mão sobe ou vai pra trás (sem precisar dizer em cada golpe)."""
        cima = (p[mao][1] - p["pc"][1] + 10) / 30
        tras = (p["pc"][0] - p[mao][0] - 4) / 20
        return max(0.0, min(1.0, max(cima, tras)))

    def braco(cot, mao, var, atras, com_asa=True):
        o, c, m = P("pc"), P(cot), P(mao)
        if com_asa:
            q = P("qd")
            ab = abre_de(mao)
            em_pixel(tela, esc, [o, c, m, q],
                     lambda sup, Q, e: asa(sup, Q(o), Q(c), Q(m), Q(q), e, d, branco, atras, ab))
        ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 3), esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)

    braco("ct", "mt", longe_v, True)
    perna("pt", "jt", longe_v)
    em_pixel(tela, esc, [P("qd")], lambda sup, Q, e: cauda(sup, Q(P("qd")), e, d, l.t, branco))
    perna("pf", "jf", perto_v)
    pts_ = [P("pc"), P("cf"), P("mf"), P("qd")]
    ab_f = abre_de("mf")
    em_pixel(tela, esc, pts_, lambda sup, Q, e: asa(sup, *[Q(q) for q in pts_], e, d, branco, False, ab_f))  # (a asa da frente ATRÁS do peito:
    c, cb = P("pc"), P("cb")                                       #  assim o código de barras aparece)
    TRONCO.desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    u, _ = cabeca_eixos(c, cb, d)
    pescoco = mais(cb, u, -3 * esc)
    pygame.draw.line(tela, (16, 12, 22), c, pescoco, max(3, int(6 * esc)))
    pygame.draw.line(tela, (245, 245, 250) if branco else _cor("p"), c, pescoco, max(1, int(4 * esc)))
    CABECA.desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    braco("cf", "mf", perto_v, False, com_asa=False)
    if l.estado == "ataque" and l.nome_golpe == "provocar" and 8 <= l.t < 30 and not branco:  # o GRITINHO
        bx, by = mais(cb, u, 2 * esc)
        for i in range(3):
            r = ((l.t * 3 + i * 10) % 30) * esc * 0.8
            pygame.draw.arc(tela, AZUL_SOM, (bx + d * 4 * esc - r, by - r, 2 * r, 2 * r),
                            -0.7 if d > 0 else math.pi - 0.7, 0.7 if d > 0 else math.pi + 0.7, max(1, int(esc)))
    k_capa = quanto_capa(l)
    if k_capa > 0:
        em_pixel(tela, esc, [cb, P("jf"), P("jt")],
                 lambda sup, Q, e: capa(sup, Q(cb), Q(P("jf"))[1], Q(P("jt"))[1], d, k_capa, branco))
    if not branco and l.extra.get("senso_flash", 0) > 0:  # trocou o SENSO AUDITIVO: as orelhas piscam
        cor = (255, 120, 120) if l.extra.get("senso") == "grave" else AZUL_SOM
        brilho(tela, (int(cb[0]), int(cb[1] - 10 * esc)), int(16 * esc), cor, 6 * l.extra["senso_flash"])
