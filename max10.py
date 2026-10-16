"""MAX-10: o robô (criado pelo Gomes).

Aparência: fusão do C-3PO com a Mark 1 do Homem de Ferro. Olhos vermelhos.
  E      laser pelos olhos (dá uma subidinha e carrega antes)    20 de dano
  SHIFT  voozinho: os foguetes dos pés jogam ele pra frente       6 de dano se trombar
  Q      agarra o braço, gira e joga PRA CIMA (bem de perto)      15 de dano
  R      metralhadora de socos esticados (5 socos)                2 de dano cada
  Z      ULTIMATE: voa pra fora da tela e dá um rasante           30 de dano
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from corpo import cabeca_eixos, eixos, frente_do_pe, mais
from golpes import GOLPES, POSES, proporcionar, suave
from pecas import Peca

# =====================================================================
# Poses (mesmo esqueleto do palito: pra frente, pra cima)
# =====================================================================
POSES.update({
    "m_agacha": dict(pt=(-22, 0), jt=(-8, 22), pf=(22, 0), jf=(30, 24), qd=(0, 32), pc=(6, 64), cb=(10, 84),
                     ct=(-10, 50), mt=(-16, 36), cf=(12, 50), mf=(14, 36)),
    "m_laser_carga": dict(pt=(-14, 6), jt=(-6, 30), pf=(10, 4), jf=(16, 30), qd=(0, 56), pc=(6, 90), cb=(12, 108),
                          ct=(-14, 76), mt=(-22, 62), cf=(-6, 74), mf=(-16, 60)),
    "m_laser_tiro": dict(pt=(-20, 2), jt=(-14, 30), pf=(12, 2), jf=(16, 30), qd=(-2, 56), pc=(0, 90), cb=(10, 108),
                         ct=(-16, 80), mt=(-30, 72), cf=(-8, 78), mf=(-22, 68)),
    "m_giro": dict(pt=(-14, 0), jt=(-10, 28), pf=(14, 0), jf=(12, 30), qd=(0, 56), pc=(0, 92), cb=(0, 112),
                   ct=(-18, 92), mt=(-38, 94), cf=(18, 92), mf=(38, 94)),
    "m_chute_arma": dict(pt=(-16, 0), jt=(-12, 28), pf=(10, 44), jf=(30, 62), qd=(-2, 56), pc=(-10, 90),
                         cb=(-12, 110), ct=(-22, 78), mt=(-14, 92), cf=(0, 80), mf=(10, 92)),
    "m_chutaco": dict(pt=(-18, 0), jt=(-14, 28), pf=(92, 74), jf=(50, 66), qd=(-4, 58), pc=(-24, 86),
                      cb=(-30, 104), ct=(-32, 72), mt=(-22, 86), cf=(-14, 74), mf=(-4, 84)),
    "m_alcanca": dict(pt=(-26, 0), jt=(-18, 28), pf=(22, 0), jf=(24, 30), qd=(0, 54), pc=(12, 86), cb=(18, 104),
                      ct=(0, 74), mt=(12, 84), cf=(34, 84), mf=(58, 84)),
    "m_gira": dict(pt=(-26, 0), jt=(-22, 28), pf=(26, 0), jf=(22, 30), qd=(0, 54), pc=(0, 88), cb=(0, 108),
                   ct=(-8, 104), mt=(4, 126), cf=(10, 106), mf=(10, 128)),
    "m_joga": dict(pt=(-30, 0), jt=(-22, 26), pf=(28, 0), jf=(30, 30), qd=(4, 52), pc=(18, 82), cb=(26, 98),
                   ct=(26, 88), mt=(50, 96), cf=(30, 92), mf=(56, 102)),
    "m_dash": dict(pt=(-34, 30), jt=(-14, 40), pf=(-26, 22), jf=(-6, 36), qd=(0, 56), pc=(26, 86), cb=(36, 100),
                   ct=(14, 80), mt=(30, 74), cf=(40, 90), mf=(62, 92)),
    "m_vitima": dict(pt=(-6, 0), jt=(-4, 28), pf=(6, 0), jf=(4, 28), qd=(0, 56), pc=(0, 92), cb=(0, 112),
                     ct=(-4, 124), mt=(-2, 140), cf=(4, 124), mf=(2, 140)),
    "m_gatling": dict(pt=(-30, 0), jt=(-22, 26), pf=(26, 0), jf=(28, 30), qd=(0, 50), pc=(8, 84), cb=(12, 102),
                      ct=(-6, 74), mt=(6, 84), cf=(14, 76), mf=(24, 86)),
    "m_gatling_arma": dict(pt=(-30, 0), jt=(-22, 26), pf=(26, 0), jf=(28, 30), qd=(-4, 50), pc=(-2, 84),
                           cb=(2, 102), ct=(-20, 72), mt=(-30, 84), cf=(-12, 74), mf=(-22, 86)),
    "m_voo": dict(pt=(-4, 0), jt=(-3, 28), pf=(4, 0), jf=(3, 28), qd=(0, 56), pc=(0, 92), cb=(0, 112),
                  ct=(-12, 76), mt=(-14, 58), cf=(6, 118), mf=(8, 146)),
    "m_pouso": dict(pt=(-26, 0), jt=(-14, 20), pf=(20, 0), jf=(30, 26), qd=(0, 30), pc=(10, 58), cb=(16, 74),
                    ct=(-8, 46), mt=(-22, 40), cf=(20, 30), mf=(26, 2)),
})
proporcionar(POSES)


# =====================================================================
# Ajudas
# =====================================================================
def local(l, x, y):
    """Ponto da tela -> unidades da pose do lutador (pra frente, pra cima)."""
    return ((x - l.x) / l.s * l.lado(), (l.y - y) / l.s)


def olho(l):
    """Onde fica o olho na tela agora."""
    p = l.pose_atual()
    q = {"o": (p["cb"][0] + 4, p["cb"][1] + 1)}
    return l.ponto(q, "o")


def fumaca(jogo, x, y, n=3, cor=(150, 150, 150), espalha=2.0, sobe=-1.0):
    for _ in range(n):
        jogo.faiscas.append([x + random.uniform(-6, 6), y, random.uniform(-espalha, espalha),
                             random.uniform(sobe - 1, sobe), random.randint(22, 36), cor, random.randint(5, 10)])


def fogo(jogo, x, y, forte=1.0):
    for _ in range(int(3 * forte)):
        cor = random.choice(((255, 220, 120), (255, 150, 40), (255, 90, 30)))
        jogo.faiscas.append([x + random.uniform(-5, 5), y, random.uniform(-1.2, 1.2),
                             random.uniform(3, 7) * forte, random.randint(8, 14), cor, random.randint(3, 7)])


_brilhos = {}


def brilho(tela, pos, raio, cor, alfa):
    """Bolinha de luz transparente (guardada pronta, pra não criar de novo todo quadro)."""
    if raio < 1:
        return
    chave = (raio, cor, alfa // 8)
    sup = _brilhos.get(chave)
    if sup is None:
        sup = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(sup, (*cor, alfa // 8 * 8), (raio, raio), raio)
        if len(_brilhos) < 600:
            _brilhos[chave] = sup
    tela.blit(sup, (pos[0] - raio, pos[1] - raio))


# =====================================================================
# E: LASER PELOS OLHOS
# =====================================================================
LASER_SOBE, LASER_CARGA, LASER_TIRO, LASER_DESCE, LASER_FIM = 10, 24, 62, 78, 96
LASER_TRAVA = LASER_TIRO - 16  # a mira trava aqui (o olho pisca branco): dá tempo de pular!
ALTURA_LASER = 46
ALTURA_MIRA = 98  # altura (em unidades do corpo) em que o laser passa: acima de quem agacha, no peito de quem está em pé


def laser(l, outro, jogo):
    t = l.t
    if t < LASER_SOBE:
        pass
    elif t < LASER_CARGA:  # subidinha
        if t == LASER_SOBE:
            som.tocar("carga")
        l.y = CHAO - ALTURA_LASER * suave((t - LASER_SOBE) / (LASER_CARGA - LASER_SOBE))
        if t % 2 == 0:
            fogo(jogo, l.x - 6 * l.dir, l.y + 2, 0.6)
    elif t < LASER_TIRO:  # carregando: o olho vai ficando cada vez mais forte
        l.y = CHAO - ALTURA_LASER + math.sin(t * 0.3) * 2
        l.pisca = (t - LASER_CARGA) / (LASER_TIRO - LASER_CARGA)
        if t % 2 == 0:
            fogo(jogo, l.x - 6 * l.dir, l.y + 2, 0.4)
        ox, oy = olho(l)
        a = random.uniform(0, math.tau)
        d = random.uniform(40, 70)
        jogo.faiscas.append([ox + math.cos(a) * d, oy + math.sin(a) * d, -math.cos(a) * d / 10,
                             -math.sin(a) * d / 10, 10, (255, 90, 70), 3])  # energia sendo sugada pro olho
        if t == LASER_TRAVA:
            # mira numa altura fixa onde o outro está: pega quem está EM PÉ, passa por cima de quem AGACHA
            l.memo["travou"] = True
            dx = max(1, (outro.x - ox) * l.dir)
            dy = (CHAO - ALTURA_MIRA * outro.s) - oy
            l.memo["mira"] = max(0.0, min(0.38, math.atan2(dy, dx)))
    elif t < LASER_DESCE:  # FOGO!
        if t == LASER_TIRO:
            som.tocar("laser")
        l.pisca = 1
        ox, oy = olho(l)
        a = l.memo.get("mira", 0.1)
        dx, dy = math.cos(a) * l.dir, math.sin(a)
        comp = 1400 if dy <= 0 else min(1400, (CHAO - oy) / dy)
        l.feixe = ((ox, oy), (ox + dx * comp, oy + dy * comp))
        l.vx = -0.6 * l.dir  # coice
        l.x = max(PAREDE_E, min(PAREDE_D, l.x + l.vx))
        jogo.tremer(3)
        ex, ey = l.feixe[1]
        if ey >= CHAO - 2 and t % 2 == 0:
            fumaca(jogo, ex, CHAO - 4, 2, (120, 90, 80))
    elif t < LASER_FIM:  # desce
        l.feixe = None
        l.pisca = max(0, l.pisca - 0.1)
        l.y = CHAO - ALTURA_LASER * (1 - suave((t - LASER_DESCE) / (LASER_FIM - LASER_DESCE - 4)))
        l.y = min(CHAO, l.y)
    else:
        l.y = CHAO
        return "fim"


def laser_efeito(l, tela):
    if l.memo.get("travou") and not l.feixe and l.t < LASER_TIRO and (l.t // 3) % 2:
        # linha de mira pontilhada: mostra por onde o laser vai passar
        ox, oy = olho(l)
        a = l.memo["mira"]
        dx, dy = math.cos(a) * l.dir, math.sin(a)
        for i in range(4, 60, 2):
            x1, y1 = ox + dx * i * 16, oy + dy * i * 16
            if y1 > CHAO:
                break
            pygame.draw.line(tela, (255, 60, 50), (x1, y1), (x1 + dx * 14, y1 + dy * 14), 3)
    if l.pisca > 0:  # olho brilhando enquanto carrega
        o = tuple(int(v) for v in olho(l))
        brilho(tela, o, int((6 + 16 * l.pisca) * l.s), (255, 40, 30), int(80 + 100 * l.pisca))
        if l.memo.get("travou") and not l.feixe and (l.t // 2) % 2:
            brilho(tela, o, int(12 * l.s), (255, 255, 255), 200)  # aviso: mira travada!
    if l.feixe:
        (x1, y1), (x2, y2) = l.feixe
        w = 10 + int(math.sin(l.t * 1.3) * 3)
        pygame.draw.line(tela, (150, 0, 0), (x1, y1), (x2, y2), w + 8)
        pygame.draw.line(tela, (255, 40, 30), (x1, y1), (x2, y2), w)
        pygame.draw.line(tela, (255, 230, 220), (x1, y1), (x2, y2), max(2, w // 3))
        brilho(tela, (int(x1), int(y1)), 18, (255, 60, 40), 120)
        brilho(tela, (int(x2), int(y2)), 26, (255, 120, 60), 110)


# =====================================================================
# SHIFT: CHUTAÇO (com girinho antes)
# =====================================================================
def chutaco(l, outro, jogo):
    t = l.t
    if t < 18:  # o girinho: dá uma volta inteira no lugar
        l.vira = 6 <= t < 12
        l.vx = 1.4 * l.dir
    else:
        l.vira = False
        l.vx = 3 * l.dir if t < 28 else l.vx * 0.7
    l.fisica(jogo)
    if t >= 50:
        return "fim"


def chutaco_efeito(l, tela):
    if l.t < 18:  # vento do giro
        for i in range(3):
            a = l.t * 0.7 + i * 2.1
            r = 46 * l.s
            cx, cy = l.x, l.y - 70 * l.s
            pygame.draw.arc(tela, (230, 230, 240), (cx - r, cy - r * 0.45, r * 2, r * 0.9), a, a + 1.2, 2)
    elif 24 <= l.t < 32:  # risco do chute
        x0 = l.x + 20 * l.dir
        for i in range(4):
            y = l.y - (62 + i * 8) * l.s
            pygame.draw.line(tela, (255, 255, 255), (x0, y), (x0 + 70 * l.dir * l.s, y - 4), 2)


# =====================================================================
# SHIFT: VOOZINHO (dash com os foguetes dos pés)
# =====================================================================
VOO_SAI, VOO_FIM, VOO_POUSO = 8, 28, 44


def voo(l, outro, jogo):
    t = l.t
    if t < VOO_SAI:  # agacha e acende os foguetes
        l.vx = 0
        if t == 1:
            som.tocar("foguete", 0.8)
        fogo(jogo, l.x - 8 * l.dir, l.y, 0.5)
    elif t < VOO_FIM:  # VOA pra frente, baixinho
        k = (t - VOO_SAI) / (VOO_FIM - VOO_SAI)
        l.y = CHAO - 34 * l.s * math.sin(k * math.pi)
        l.vx = 11 * l.dir
        l.x = max(PAREDE_E, min(PAREDE_D, l.x + l.vx))
        pe = l.ponto(l.pose_atual(), "pt")
        fogo(jogo, pe[0] - 6 * l.dir, pe[1], 1.4)
        if t % 2 == 0:
            fumaca(jogo, pe[0] - 14 * l.dir, pe[1], 1, (190, 190, 190), 1, 0)
        return
    elif t == VOO_FIM:
        l.y = CHAO
        l.vx = 2 * l.dir
        fumaca(jogo, l.x, CHAO - 4, 6, (170, 150, 130), 3, -0.5)
    l.vx *= 0.8
    l.fisica(jogo)
    if t >= VOO_POUSO:
        return "fim"


# =====================================================================
# Q: AGARRÃO (agarra o braço, gira e joga)
# =====================================================================
PEGA, PUXA, GIRA, SOLTA = 6, 12, 50, 22  # quadros de cada parte
ALCANCE_AGARRAR = 78


def agarrao(l, outro, jogo):
    t = l.t
    m = l.memo
    if not m.get("pegou"):
        if t == PEGA:
            perto = abs(outro.x - l.x) <= ALCANCE_AGARRAR * l.s
            pode = outro.no_chao() and outro.estado not in ("caido", "voando", "agarrado", "levantando") \
                and outro.inv == 0
            if perto and pode:  # PEGOU! (agarrão não dá pra defender)
                m["pegou"] = True
                m["ini"] = (outro.x, outro.y)
                outro.mudar("agarrado")
                outro.golpe = None
                l.inv = 999
                jogo.parada = 5
                jogo.faisca(outro.x, outro.y - 80 * outro.s, True)
            else:  # errou: fica com a mão esticada um tiquinho e volta
                m["quadros"] = [(0, "parado"), (PEGA, "m_alcanca"), (16, "m_alcanca"), (36, "parado")]
        l.fisica(jogo)
        return "fim" if t >= 36 else None

    u = t - PEGA
    a0 = 0.0 if l.dir == 1 else math.pi  # começa com o outro do lado da frente
    voltas = 2  # duas voltas inteiras, cada vez mais rápido; solta de novo na frente

    def coloca(a, mistura=1.0):
        """Giro LATERAL (em volta do Max, como martelo olímpico).
        cos(a) = de que lado ele está (direita/esquerda); sin(a) = se está na frente ou atrás do Max."""
        lado = math.cos(a)
        aberto = abs(lado) ** 0.6  # de lado: deitado no ar; passando na frente/atrás: mais pendurado
        alto = (105 + 40 * (1 - abs(lado))) * l.s
        mao = (l.x + lado * 24 * l.s, l.y - alto)  # onde as mãos do Max seguram
        fi = -math.copysign(math.pi / 2, lado) * aberto  # inclina o corpo dele pra fora
        cima = (math.sin(fi), -math.cos(fi))  # direção da mão dele (na tela)
        braco = 88 * outro.s
        quadril = (mao[0] - cima[0] * braco, mao[1] - cima[1] * braco)
        x0, y0 = m["ini"]
        alvo_x, alvo_y = quadril[0], quadril[1] + 50 * outro.s
        outro.x = x0 + (alvo_x - x0) * mistura
        outro.y = min(CHAO, y0 + (alvo_y - y0) * mistura)
        outro.x = max(PAREDE_E - 30, min(PAREDE_D + 30, outro.x))
        outro.angulo = fi * outro.lado() * mistura
        outro.sobrepor = POSES["m_vitima"]
        outro.atras = math.sin(a) * l.dir < 0  # passando por trás do Max: fica escondido atrás dele
        l.vira = lado * l.dir < 0  # o Max vira acompanhando (mostra as costas)
        mx, my = local(l, *mao)
        l.sobrepor = {"mf": (mx, my), "mt": (mx - 3, my - 2)}

    if u < PUXA:  # puxa ele pro alto, do lado da frente
        coloca(a0, suave(u / PUXA))
    elif u < PUXA + GIRA:  # gira, cada vez mais rápido
        k = ((u - PUXA) / GIRA) ** 1.6
        a = a0 + math.tau * voltas * k
        coloca(a)
        m["a"] = a
        if u % 6 == 0:
            jogo.tremer(2)
    elif u == PUXA + GIRA:  # SOLTA!
        outro.sobrepor = {}
        outro.angulo = 0
        outro.atras = False
        outro.mudar("voando")
        outro.vx = 1.5 * l.dir
        outro.vy = -16  # PRA CIMA! (aperta CIMA pra pular atrás e fazer combo aéreo)
        outro.malabar, outro.malabar_n = True, 0
        outro.levar(15, l, GOLPES["max_agarrao"])
        l.acertou = True
        l.combo = 1
        l.inv = 0
        l.vira = False
        l.sobrepor = {}
        jogo.tremer(10)
        jogo.parada = 6
        jogo.faisca(outro.x, outro.y - 50, False)
    elif u >= PUXA + GIRA + SOLTA:
        return "fim"
    if u > PUXA + GIRA:
        l.sobrepor = {}


def agarrao_quadros():
    giro = PEGA + PUXA
    return [(0, "parado"), (PEGA, "m_alcanca"), (giro, "m_gira"), (giro + GIRA, "m_gira"),
            (giro + GIRA + 6, "m_joga"), (giro + GIRA + SOLTA, "parado")]


def agarrao_efeito(l, tela):
    u = l.t - PEGA
    if l.memo.get("pegou") and PUXA + GIRA * 0.3 <= u < PUXA + GIRA:
        # vento do giro: elipse deitada em volta do Max
        cx, cy = l.x, l.y - 110 * l.s
        rx, ry = 150 * l.s, 26 * l.s
        for i in range(2):
            a = l.memo.get("a", 0) + i * math.pi
            pygame.draw.arc(tela, (235, 235, 245), (cx - rx, cy - ry, rx * 2, ry * 2), -a - 0.9, -a, 3)


# =====================================================================
# R: METRALHADORA DE SOCOS (5 socos esticados, tipo Gomu Gomu no Gatling)
# =====================================================================
G_INI, G_INTERVALO, G_SOCOS, G_ALCANCE = 12, 20, 5, 150


def gatling_janelas():
    return tuple((G_INI + k * G_INTERVALO + 3, G_INI + k * G_INTERVALO + 9) for k in range(G_SOCOS))


def gatling(l, outro, jogo):
    t = l.t
    fim_socos = G_INI + G_SOCOS * G_INTERVALO
    l.memo.pop("mola", None)
    if G_INI <= t < fim_socos:
        k, u = divmod(t - G_INI, G_INTERVALO)
        if u < 5:
            ext = suave(u / 5)
        elif u < 9:
            ext = 1
        elif u < 15:
            ext = 1 - suave((u - 9) / 6)
        else:
            ext = 0
        frente = k % 2 == 0  # alterna os braços
        mao = (26 + G_ALCANCE * ext, 88 if frente else 82)
        cot = (18 + 16 * ext, 84 if frente else 80)
        l.sobrepor = {"mf": mao, "cf": cot} if frente else {"mt": mao, "ct": cot}
        if ext > 0.15:
            l.memo["mola"] = "f" if frente else "t"
        l.memo["ext"] = ext
        l.memo["caixa"] = (20, 70, 26 + G_ALCANCE * ext + 16, 102)
        l.memo["g_hit"] = GOLPES["max_gatling_final"] if k == G_SOCOS - 1 else GOLPES["max_gatling"]
    else:
        l.sobrepor = {}
    l.vx = 0
    l.fisica(jogo)
    if t >= fim_socos + 16:
        return "fim"


def gatling_efeito(l, tela):
    ext = l.memo.get("ext", 0)
    if l.memo.get("mola") and ext > 0.3:  # punhos fantasmas (efeito de muitos socos)
        y = l.y - 86 * l.s
        for i in range(1, 4):
            x = l.x + (26 + G_ALCANCE * ext * (1 - i * 0.22)) * l.s * l.dir
            yy = y + random.randint(-14, 14)
            brilho(tela, (int(x), int(yy)), int(9 * l.s), (200, 170, 100), 90 - i * 20)
        xm = l.x + (26 + G_ALCANCE * ext) * l.s * l.dir
        for i in range(3):
            yy = y + (i - 1) * 12
            pygame.draw.line(tela, (255, 255, 255), (xm - 40 * l.dir, yy), (xm - 70 * l.dir, yy), 2)


# =====================================================================
# Z: ULTIMATE, O RASANTE
# =====================================================================
R_AGACHA, R_SOBE, R_FORA, R_TRAVA, R_DESCE, R_POUSO, R_FIM = 18, 40, 84, 74, 104, 132, 148


def rasante(l, outro, jogo):
    t = l.t
    m = l.memo
    if t == 1:
        m["base_y"] = l.y
        m["dir0"] = l.dir
    if t < R_AGACHA:  # agacha, os foguetes dos pés acendem
        jogo.tremer(2)
        fogo(jogo, l.x, l.y, 0.5 + t / R_AGACHA)
        if t % 3 == 0:
            fumaca(jogo, l.x, CHAO - 4, 2, (170, 160, 150), 4, -0.5)
    elif t < R_SOBE:  # DECOLA!
        if t == R_AGACHA:
            som.tocar("foguete")
        l.inv = 3
        k = t - R_AGACHA
        l.y = CHAO - 1.7 * k * k - 4 * k
        fogo(jogo, l.x, l.y + 4, 2.2)
        fumaca(jogo, l.x, l.y + 20, 2, (190, 190, 190), 1.0, 0.5)
        if t == R_AGACHA:
            jogo.tremer(10)
            fumaca(jogo, l.x, CHAO - 4, 14, (180, 170, 160), 6, -1)
    elif t < R_FORA:  # lá em cima, fora da tela: a mira persegue o outro
        l.inv = 3
        l.y = -400
        if t < R_TRAVA:
            m["alvo"] = outro.x
    elif t < R_DESCE:  # o rasante!
        l.inv = 3
        if t == R_FORA:
            m["de"] = (m["alvo"] - m["dir0"] * 420, -160)
            jogo.tremer(4)
        k = (t - R_FORA) / (R_DESCE - R_FORA)
        k = k * k  # vai acelerando
        (x0, y0), (x1, y1) = m["de"], (m["alvo"], CHAO - 40 * l.s)
        px, py = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        l.dir = m["dir0"]
        l.x, l.y = px, py + 50 * l.s  # o quadril segue a linha
        fx, fy = (x1 - x0) * l.dir, (y1 - y0)
        l.angulo = math.atan2(fx, -fy) * 1  # a cabeça aponta pra onde ele vai
        fogo(jogo, *l.ponto(l.pose_atual(), "pt"), 1.5)
        m["caixa"] = (-50, -10, 70, 110)
        if t % 2 == 0:
            fumaca(jogo, px, py, 2, (200, 200, 200), 1, 0)
    elif t == R_DESCE:  # BUM, chega no chão
        som.tocar("explosao")
        l.angulo = 0
        l.x = max(PAREDE_E, min(PAREDE_D, m["alvo"]))
        l.y = CHAO
        l.inv = 0
        jogo.tremer(18)
        jogo.parada = max(jogo.parada, 5)
        fumaca(jogo, l.x, CHAO - 4, 24, (170, 150, 130), 7, -1.5)
    elif t >= R_FIM:
        return "fim"


def rasante_quadros():
    return [(0, "parado"), (12, "m_agacha"), (R_AGACHA, "m_agacha"), (R_AGACHA + 6, "m_voo"),
            (R_DESCE - 1, "m_voo"), (R_DESCE, "m_pouso"), (R_POUSO, "m_pouso"), (R_FIM, "parado")]


def rasante_efeito(l, tela):
    t = l.t
    m = l.memo
    if R_SOBE <= t < R_DESCE and "alvo" in m:  # a mira vermelha no chão
        x = int(m["alvo"])
        travou = t >= R_TRAVA
        if not travou or (t // 3) % 2:
            r = int(46 - (t - R_SOBE) * 0.35)
            cor = (255, 40, 30)
            pygame.draw.ellipse(tela, cor, (x - r, CHAO - r // 3, r * 2, r * 2 // 3), 3)
            pygame.draw.ellipse(tela, cor, (x - r // 2, CHAO - r // 6, r, r // 3), 2)
            for s in (-1, 1):
                pygame.draw.line(tela, cor, (x + s * (r + 8), CHAO), (x + s * (r - 8), CHAO), 3)
    if R_FORA <= t < R_DESCE:  # rastro de velocidade
        x0, y0 = m["de"]
        pygame.draw.line(tela, (255, 200, 120), (int(x0), int(y0)),
                         l.ponto(l.pose_atual(), "qd"), 3)


# =====================================================================
# Golpes do Max-10
# =====================================================================
def _registra(nome, **g):
    g.setdefault("base", "parado")
    g.setdefault("pose", "parado")
    g.setdefault("caixa", None)
    g.setdefault("especial", True)
    g["total"] = g.get("total", g["ini"] + g["ativo"] + g.get("rec", 0))
    GOLPES[nome] = g


_registra("max_laser", ini=LASER_TIRO, ativo=LASER_DESCE - LASER_TIRO, rec=LASER_FIM - LASER_DESCE,
          janelas=((LASER_TIRO, LASER_DESCE),), dano=20, hit=22, defe=16, emp=8, nivel="medio",
          logica=laser, efeito=laser_efeito, ia="longe",
          quadros=[(0, "parado"), (LASER_SOBE, "m_agacha"), (LASER_CARGA, "m_laser_carga"),
                   (LASER_TIRO - 4, "m_laser_carga"), (LASER_TIRO, "m_laser_tiro"),
                   (LASER_DESCE, "m_laser_tiro"), (LASER_FIM, "parado")])
_registra("max_chutaco", ini=24, ativo=6, rec=20, janelas=((24, 30),), caixa=(30, 48, 98, 88),
          dano=10, hit=20, defe=14, emp=8, nivel="medio", derruba=True, voo=(13, 11), giro_voo=0.25,
          logica=chutaco, efeito=chutaco_efeito, ia="medio",
          quadros=[(0, "parado"), (4, "m_giro"), (16, "m_giro"), (21, "m_chute_arma"), (25, "m_chutaco"),
                   (32, "m_chutaco"), (50, "parado")])
_registra("max_agarrao", ini=PEGA, ativo=1, rec=30, dano=15, hit=0, defe=0, emp=0, nivel="medio", lanca=18,
          logica=agarrao, efeito=agarrao_efeito, ia="perto", quadros=agarrao_quadros())
_registra("max_voo", ini=VOO_SAI, ativo=VOO_FIM - VOO_SAI, rec=VOO_POUSO - VOO_FIM, janelas=((VOO_SAI, VOO_FIM),),
          caixa=(-10, 30, 44, 120), dano=6, hit=16, defe=12, emp=8, nivel="medio", logica=voo, ia="medio",
          quadros=[(0, "parado"), (VOO_SAI - 2, "m_agacha"), (VOO_SAI + 3, "m_dash"), (VOO_FIM - 1, "m_dash"),
                   (VOO_FIM + 3, "pouso"), (VOO_POUSO, "parado")])
_registra("max_gatling", ini=G_INI, ativo=G_SOCOS * G_INTERVALO, rec=16, janelas=gatling_janelas(),
          caixa=(20, 70, 60, 102), dano=2, hit=8, defe=8, emp=1, nivel="medio",
          logica=gatling, efeito=gatling_efeito, ia="medio",
          quadros=[(0, "parado"), (G_INI - 2, "m_gatling_arma"), (G_INI + 3, "m_gatling"),
                   (G_INI + G_SOCOS * G_INTERVALO, "m_gatling"), (G_INI + G_SOCOS * G_INTERVALO + 16, "parado")])
GOLPES["max_gatling_final"] = dict(GOLPES["max_gatling"], emp=6, hit=14)
_registra("max_rasante", ini=R_FORA, ativo=R_DESCE - R_FORA, rec=R_FIM - R_DESCE,
          janelas=((R_FORA, R_DESCE),), dano=30, hit=30, defe=24, emp=8, nivel="medio", derruba=True,
          voo=(10, 13), giro_voo=0.2, ultimate=True, logica=rasante, efeito=rasante_efeito, ia="ultimate",
          quadros=rasante_quadros())

GOLPES_MAX10 = {"E": "max_laser", "SHIFT": "max_voo", "Q": "max_agarrao", "R": "max_gatling", "Z": "max_rasante"}
# (o chutaço continua aqui embaixo guardado, caso a gente queira usar ele de novo)


# =====================================================================
# Desenho: robô (C-3PO + Mark 1) em PIXEL ART, peça por peça
# =====================================================================
# Cada letra é uma cor. Dá pra editar pixel por pixel aqui mesmo!
#   k contorno   G g d D dourado (claro -> escuro)   S s m aço (claro -> escuro)
#   r R olho     w b y fios da cintura (vermelho, azul, amarelo)
PALETA = {
    "k": (30, 22, 14), "G": (246, 214, 132), "g": (212, 172, 90), "d": (160, 120, 56), "D": (110, 78, 34),
    "S": (196, 198, 204), "s": (134, 136, 144), "m": (84, 86, 96),
    "r": (255, 46, 36), "R": (255, 200, 180), "w": (220, 64, 52), "b": (72, 132, 226), "y": (232, 204, 76),
}
S_REF = 1.42 / 3  # tamanho em que as peças foram desenhadas (1 letra = 1 pixel do jogo)

TRONCO = Peca([
    "...kkkkkkkk...",
    "..kGGGGgggggk.",
    ".kGGGgggggggdk",
    ".kGGggggggggdk",
    ".kGggggggggddk",
    ".kGggggggggddk",
    ".kGggkkkkkgddk",
    ".kgggggggggddk",
    ".kgggggggggddk",
    "..kggggggggdk.",
    "..kgggggggddk.",
    "..kdddddddDDk.",
    "...kmmmmmmmk..",
    "...kmwmbmymk..",
    "...kwmbmymmk..",
    "...kmwmbmymk..",
    "...kwmbmymmk..",
    "..kmmmmmmmmmk.",
    "..kSSSssssmmk.",
    "..kSsssssssmk.",
    "..kSssssssmmk.",
    "..kssssssmmmk.",
    "...kmmmmmmmk..",
    "....kkkkkkk...",
], PALETA, a=(7, 21), b=(7, 1))

TRONCO_COSTAS = Peca([
    "...kkkkkkkk...",
    "..kGGGGgggggk.",
    ".kGGGggdgggddk",
    ".kGGgggdggggdk",
    ".kGggggdgggddk",
    ".kGggggdgggddk",
    ".kgggggdgggddk",
    ".kgggggdgggddk",
    ".kgggggdgggddk",
    "..kggggdgggdk.",
    "..kggggdggddk.",
    "..kddddDddDDk.",
    "...kmmmmmmmk..",
    "...kmmmsmmmk..",
    "...kmmmsmmmk..",
    "...kmmmsmmmk..",
    "...kmmmsmmmk..",
    "..kmmmmmmmmmk.",
    "..kSSSssssmmk.",
    "..kSsssssssmk.",
    "..kSssssssmmk.",
    "..kssssssmmmk.",
    "...kmmmmmmmk..",
    "....kkkkkkk...",
], PALETA, a=(7, 21), b=(7, 1))

CABECA = Peca([
    "...kkkk...",
    "..kGGggk..",
    ".kGGgggdk.",
    ".kGgggggdk",
    "kSkgggkkkk",
    "kSmkgkrRmk",
    "kmmkgkmmmk",
    ".kkgggkmmk",
    "..kgddkkmk",
    "..kddDDkk.",
    "...kmmk...",
], PALETA, a=(5, 5), b=(5, 0), estica=False)

CABECA_COSTAS = Peca([
    "...kkkk...",
    "..kGGggk..",
    ".kGGgggdk.",
    ".kGggggddk",
    ".kgggggddk",
    "kSkggggddk",
    "kSmkgggddk",
    "kmmkggdddk",
    ".kkgddddk.",
    "..kdddDk..",
    "...kmmk...",
], PALETA, a=(5, 5), b=(5, 0), estica=False)

COXA = Peca([
    ".kkkkk.",
    "kGGgggk",
    "kGgggdk",
    "kGgggdk",
    "kGgggdk",
    "kGgggdk",
    "kGggddk",
    "kgggddk",
    "kgggddk",
    "kggdddk",
    "kggdddk",
    "kgddDDk",
    ".kddDk.",
    ".kddDk.",
    ".kmmmk.",
    "kmSSsmk",
    ".kmmmk.",
], PALETA, a=(3, 0), b=(3, 15))

CANELA = Peca([
    ".kkkkk.",
    "kmgGggk",
    "kmgGggk",
    "kmgGggk",
    "kmgggdk",
    "ksgggdk",
    "ksgggdk",
    "ksggddk",
    "ksggddk",
    "ksgdddk",
    "kmgdddk",
    ".kdddk.",
    ".kdDdk.",
    "..kmk..",
    "..kmk..",
], PALETA, a=(3, 0), b=(3, 14))

BOTA = Peca([
    "..kkkk.....",
    ".kmSSmk....",
    ".kmSssmkkk.",
    "kmsssssssmk",
    "kmmmmmmmmmk",
    ".kkkkkkkkk.",
], PALETA, a=(3, 1), b=(9, 1), estica=False)

BRACO = Peca([
    ".kkk.",
    "kSSsk",
    "kSssk",
    "kmsmk",
    "kgGgk",
    "kgGgk",
    "kgggk",
    "kgggk",
    "kggdk",
    "kggdk",
    "kgddk",
    ".kmk.",
    "kmsmk",
    ".kkk.",
], PALETA, a=(2, 1), b=(2, 12))

ANTEBRACO = Peca([
    ".kkk.",
    "kgGgk",
    "kgGgk",
    "kgggk",
    "kgggk",
    "kggdk",
    "kggdk",
    "kgddk",
    "kgddk",
    "kmmmk",
    "kSsmk",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 10))

MAO = Peca([
    ".kkkk.",
    "kSSsmk",
    "kSssmk",
    "kssmmk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 4), estica=False)


def _mola(tela, a, b, w, cor):
    """Braço esticado: uma mola de metal."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = max(1, int(math.hypot(dx, dy) / 3))
    comp = math.hypot(dx, dy) or 1
    px, py = -dy / comp * w, dx / comp * w
    pts = [(a[0] + dx * i / n + (px if i % 2 else -px), a[1] + dy * i / n + (py if i % 2 else -py))
           for i in range(n + 1)]
    pts[0], pts[-1] = a, b
    pygame.draw.lines(tela, PALETA["k"], False, pts, 3)
    pygame.draw.lines(tela, cor, False, pts, 1)


def desenhar_robo(l, tela, p, branco):
    esc = l.s / S_REF            # 1 = tamanho em que as peças foram desenhadas
    d = l.lado()
    espelho = d < 0
    perto_v = "branco" if branco else "normal"
    longe_v = "branco" if branco else "escuro"
    costas = l.vira  # de costas (no meio de um giro): mostra as costas, sem rosto

    def P(k):
        return l.ponto(p, k)

    def perna(pe, joelho, var):
        q, j, e = P("qd"), P(joelho), P(pe)
        CANELA.desenhar(tela, j, e, esc, espelho, var)
        fr, _ = frente_do_pe(j, e, d)
        BOTA.desenhar(tela, e, mais(e, fr, 10), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    def braco(cot, mao, var, esticado):
        o, c, m = P("pc"), P(cot), P(mao)
        if esticado:
            _mola(tela, c, m, 2.2 * esc, PALETA["S"] if not branco else (245, 245, 250))
        else:
            ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)

    mola = l.memo.get("mola") if l.estado == "ataque" else None
    longe, perto = (("cf", "mf", "pf", "jf", "f"), ("ct", "mt", "pt", "jt", "t")) if costas else \
        (("ct", "mt", "pt", "jt", "t"), ("cf", "mf", "pf", "jf", "f"))
    braco(longe[0], longe[1], longe_v, mola == longe[4])
    perna(longe[2], longe[3], longe_v)
    c, cb = P("pc"), P("cb")
    u, _ = cabeca_eixos(c, cb, d)
    # pescoço
    pygame.draw.line(tela, PALETA["k"], c, mais(cb, u, -3 * esc), max(3, int(4 * esc)))
    pygame.draw.line(tela, PALETA["m"] if not branco else (200, 200, 205), c, mais(cb, u, -3 * esc), max(1, int(2 * esc)))
    (TRONCO_COSTAS if costas else TRONCO).desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    perna(perto[2], perto[3], perto_v)
    (CABECA_COSTAS if costas else CABECA).desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    braco(perto[0], perto[1], perto_v, mola == perto[4])


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Detalhe do Max-10 grande na cutscene: o visor escuro e o olho vermelho brilhando."""
    cb = P("cb")
    pygame.draw.rect(q, (60, 60, 68), (cb[0] + (2 if d > 0 else -12) * s, cb[1] - 4 * s, 10 * s, 5 * s))
    o = (int(cb[0] + 6 * s * d), int(cb[1] - 1.5 * s))
    brilho(q, o, int(9 * s), (255, 40, 30), 140)
    pygame.draw.circle(q, (255, 60, 40), o, max(2, int(2.2 * s)))


# =====================================================================
# ENTRADA: chega voando com os foguetes e pousa em pose de herói
# =====================================================================
def entrada(l, t, jogo):
    from golpes import misturar
    xf = l.extra["entrada_x"]
    if t < 46:  # voando
        if t == 1:
            som.tocar("foguete")
        k = suave(t / 46)
        x0, y0 = xf - l.dir * 340, -160
        l.x = x0 + (xf - x0) * k
        l.y = y0 + (CHAO - y0) * k
        l.sobrepor = dict(POSES["m_voo"])
        fx, fy = (xf - x0) * l.dir, (CHAO - y0)
        l.angulo = math.atan2(fx, -fy) * (1 - k * k)
        pe = l.ponto(l.sobrepor, "pt")
        fogo(jogo, pe[0], pe[1], 1.4)
        if t % 2 == 0:
            fumaca(jogo, pe[0], pe[1], 1, (200, 200, 200), 1, 0)
    elif t == 46:  # POUSO
        som.tocar("queda")
        l.x, l.y, l.angulo = xf, CHAO, 0
        l.sobrepor = dict(POSES["m_pouso"])
        jogo.tremer(10)
        fumaca(jogo, l.x, CHAO - 4, 18, (170, 150, 130), 6, -1.5)
    elif t < 90:
        k = suave((t - 62) / 28)
        l.sobrepor = misturar(POSES["m_pouso"], l.poses["parado"], k) if t >= 62 else dict(POSES["m_pouso"])
        l.pisca = max(0, 1 - abs(t - 70) / 10)  # o olho acende
    else:
        l.sobrepor, l.pisca = {}, 0
    l.t += 1


def entrada_efeito(l, tela, t):
    if 60 <= t < 82:
        brilho(tela, tuple(int(v) for v in olho(l)), int(14 * l.s), (255, 40, 30), 160)



# =====================================================================
# VITÓRIA: punho pra cima, olho pulsando, faísca de foguete nos pés
# =====================================================================
def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES["vitoria"])
    l.pisca = (math.sin(t * 0.15) + 1) / 2
    if t % 6 == 0 and t < 60:
        pe = l.ponto(l.sobrepor, "pt")
        fogo(jogo, pe[0], pe[1], 0.6)
    if t == 2:
        som.tocar("foguete", 0.5)


def vitoria_efeito(l, tela, t):
    brilho(tela, tuple(int(v) for v in olho(l)), int((8 + 10 * l.pisca) * l.s), (255, 40, 30), int(80 + 120 * l.pisca))
