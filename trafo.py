"""TRAFO: o cachorro mutante (criado pelo Gomes).

Aparência: cachorro mutante bem estranho, todo amarelo escuro, peludo, com uma COLEIRA QUEBRADA (fugiu do
laboratório). Remodel do Gomes (v2.x): tirou as 2 patas do meio e o Q agora é UM braço só.
  E      LINGUÃO: 10 de dano e PARALISA por 2 segundos
  Q      enfia o braço na terra e UM braço gigante sai embaixo do oponente (tem um sinal pra pular). Joga pra cima, 20
  R      TRANSFORMAÇÃO (v2.x, do Gomes): vira o RIB um instantinho, faz o KAGE BUNSHIN e volta a ser o Trafo;
         o clone (um Trafo) fica 5 s do outro lado do oponente e DUPLICA todo hit (1 hit vira 2)
  SHIFT  PULÃO bem longo, 10 de dano
  Z      ULTIMATE: corrida (lenta). Se acertar: cutscene arrastando o oponente, vira o Max-10 e solta um laserzão,
         vira o oponente e usa uma skill dele. 35 de dano (a barra enche normal desde o remodel).
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from corpo import cabeca_eixos, eixos, frente_do_pe, mais
from golpes import GOLPES, proporcionar, suave
from lutador import Projetil
from max10 import brilho, fumaca
from pecas import Peca

# =====================================================================
# Poses (cachorro em pé, curvado pra frente)
# =====================================================================
POSES_TRAFO = {
    "parado": dict(pt=(-20, 0), jt=(-6, 22), pf=(18, 0), jf=(26, 24), qd=(0, 46), pc=(16, 78), cb=(28, 92),
                   ct=(10, 62), mt=(20, 52), cf=(30, 66), mf=(44, 62)),
    "andar1": dict(pt=(-24, 0), jt=(-8, 22), pf=(24, 0), jf=(28, 24), qd=(0, 44), pc=(16, 76), cb=(28, 90),
                   ct=(8, 60), mt=(16, 50), cf=(32, 64), mf=(46, 60)),
    "andar2": dict(pt=(2, 10), jt=(14, 28), pf=(4, 0), jf=(16, 24), qd=(0, 48), pc=(16, 80), cb=(28, 94),
                   ct=(12, 64), mt=(24, 54), cf=(28, 68), mf=(40, 64)),
    "andar3": dict(pt=(24, 0), jt=(28, 24), pf=(-24, 0), jf=(-8, 22), qd=(0, 44), pc=(16, 76), cb=(28, 90),
                   ct=(32, 64), mt=(46, 60), cf=(8, 60), mf=(16, 50)),
    "andar4": dict(pt=(4, 0), jt=(16, 24), pf=(2, 10), jf=(14, 28), qd=(0, 48), pc=(16, 80), cb=(28, 94),
                   ct=(28, 68), mt=(40, 64), cf=(12, 64), mf=(24, 54)),
    "t_lingua": dict(pt=(-26, 0), jt=(-12, 22), pf=(22, 0), jf=(30, 24), qd=(0, 44), pc=(24, 74), cb=(40, 84),
                     ct=(14, 58), mt=(22, 44), cf=(34, 60), mf=(46, 50)),
    "t_terra": dict(pt=(-24, 0), jt=(-6, 18), pf=(22, 0), jf=(32, 20), qd=(0, 34), pc=(20, 58), cb=(32, 70),
                    ct=(8, 44), mt=(14, 30), cf=(36, 30), mf=(46, 2)),
    "t_olhos": dict(pt=(-26, 0), jt=(-14, 24), pf=(24, 0), jf=(28, 26), qd=(0, 50), pc=(8, 84), cb=(16, 100),
                    ct=(-10, 74), mt=(-22, 84), cf=(26, 76), mf=(38, 88)),
    "t_agacha": dict(pt=(-22, 0), jt=(-4, 18), pf=(20, 0), jf=(32, 18), qd=(0, 30), pc=(18, 54), cb=(30, 64),
                     ct=(10, 40), mt=(20, 26), cf=(30, 42), mf=(42, 30)),
    "t_pulo": dict(pt=(-38, 40), jt=(-20, 46), pf=(-32, 30), jf=(-14, 40), qd=(0, 50), pc=(26, 62), cb=(42, 70),
                   ct=(30, 58), mt=(52, 56), cf=(36, 64), mf=(60, 66)),
    "t_corre1": dict(pt=(-30, 6), jt=(-14, 26), pf=(18, 0), jf=(12, 24), qd=(0, 46), pc=(30, 52), cb=(48, 60),
                     ct=(38, 30), mt=(52, 4), cf=(42, 30), mf=(30, 2)),
    "t_corre2": dict(pt=(16, 0), jt=(10, 24), pf=(-30, 6), jf=(-14, 26), qd=(0, 46), pc=(30, 52), cb=(48, 60),
                     ct=(42, 30), mt=(30, 2), cf=(38, 30), mf=(52, 4)),
}
proporcionar(POSES_TRAFO)


# =====================================================================
# E: LINGUÃO (paralisa)
# =====================================================================
L_SAI, L_ESTICA, L_VOLTA, L_FIM, L_ALCANCE = 14, 19, 28, 46, 175


def boca(l):
    p = l.pose_vista or l.pose_atual()
    return l.ponto({"b": (p["cb"][0] + 12, p["cb"][1] - 5)}, "b")


def linguao(l, outro, jogo):
    t = l.t
    if t == L_SAI:
        som.tocar("lingua")
    if L_SAI <= t < L_FIM:
        if t < L_ESTICA:
            ext = suave((t - L_SAI) / (L_ESTICA - L_SAI))
        elif t < L_VOLTA:
            ext = 1
        else:
            ext = max(0, 1 - suave((t - L_VOLTA) / (L_FIM - 6 - L_VOLTA)))
        l.memo["ext"] = ext
        bx, by = boca(l)
        l.memo["caixa"] = (8, (l.y - by) / l.s - 9, 8 + L_ALCANCE * ext + 10, (l.y - by) / l.s + 9)
    else:
        l.memo["ext"] = 0
    l.vx = 0
    l.fisica(jogo)
    if t >= L_FIM:
        return "fim"


def linguao_efeito(l, tela):
    ext = l.memo.get("ext", 0)
    if ext <= 0:
        return
    bx, by = boca(l)
    fx = bx + L_ALCANCE * ext * l.s * l.dir
    meio = ((bx + fx) / 2, by + 6 * l.s + math.sin(l.t * 0.7) * 4)
    pts = [(bx, by), meio, (fx, by + 2 * l.s)]
    pygame.draw.lines(tela, (110, 30, 50), False, pts, int(14 * l.s))
    pygame.draw.lines(tela, (226, 112, 132), False, pts, int(10 * l.s))
    pygame.draw.lines(tela, (246, 160, 176), False, [(bx, by - 2), (meio[0], meio[1] - 3)], int(3 * l.s))
    pygame.draw.circle(tela, (110, 30, 50), (int(fx), int(by + 2 * l.s)), int(9 * l.s))
    pygame.draw.circle(tela, (226, 112, 132), (int(fx), int(by + 2 * l.s)), int(7 * l.s))
    for i in range(3):  # baba pingando
        x = bx + (fx - bx) * (0.3 + i * 0.25)
        pygame.draw.circle(tela, (220, 230, 150), (int(x), int(by + (8 + (l.t * 2 + i * 7) % 18) * l.s)), int(2 * l.s))


# =====================================================================
# Q: BRAÇOS DA TERRA (sinal pra pular, depois os braços saem embaixo)
# =====================================================================
T_ENFIA, T_SAI, T_SOME, T_FIM = 10, 42, 56, 74
T_TRAVA = T_SAI - 14   # o sinal segue o oponente até aqui; depois trava (hora de PULAR!)
T_ALTURA = 95          # até onde os braços pegam (pulando na hora certa passa por cima)


def terra(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t < T_ENFIA and t % 2 == 0:
        fumaca(jogo, l.x + 46 * l.s * l.dir, CHAO - 4, 2, (120, 96, 60), 2, -1)
    if T_ENFIA <= t < T_TRAVA:  # o sinal aparece e vai seguindo o oponente
        m["alvo"] = outro.x
    if T_SAI + 1 <= t < T_SAI + 9 and "alvo" in m and not m.get("bateu"):
        zona = pygame.Rect(m["alvo"] - 36 * l.s, CHAO - T_ALTURA * l.s, 72 * l.s, T_ALTURA * l.s)  # (um braço só)
        c = outro.corpo()
        if c and zona.colliderect(c):  # os braços pegaram (não dá pra defender, só pular/sair)
            m["bateu"] = True
            l.acertou = True
            res = outro.receber(GOLPES["trafo_terra"], 1 if outro.x >= l.x else -1, l, l.f["forca"])
            jogo.faisca(outro.x, outro.y - 60 * outro.s, res == "def", True)
            jogo.parada = PARADA_GOLPE
            jogo.tremer(10)
    if t == T_ENFIA:
        som.tocar("terra")
    if t == T_SAI and "alvo" in m:
        som.tocar("explosao", 0.7)
        jogo.tremer(8)
        fumaca(jogo, m["alvo"], CHAO - 4, 16, (120, 96, 60), 5, -3)
    if t >= T_FIM:
        return "fim"


def terra_efeito(l, tela):
    t = l.t
    m = l.memo
    if "alvo" not in m:
        return
    x = int(m["alvo"])
    if T_ENFIA <= t < T_SAI:  # o SINAL: rachadura no chão e o "!" piscando
        abre = (t - T_ENFIA) / (T_SAI - T_ENFIA)
        r = int((22 + 30 * abre) * l.s)
        pygame.draw.ellipse(tela, (60, 40, 20), (x - r, CHAO - r // 5, r * 2, r * 2 // 5))
        for i in range(5):
            a = i * 1.26
            pygame.draw.line(tela, (40, 26, 12), (x, CHAO), (x + math.cos(a) * r * 1.3, CHAO + math.sin(a) * r * 0.3), 2)
        if (t // (2 if t >= T_TRAVA else 4)) % 2 == 0:  # pisca mais rápido quando trava
            ty = CHAO - 70 * l.s - 6 * math.sin(t * 0.4)
            pts = [(x, ty - 26 * l.s), (x - 22 * l.s, ty + 12 * l.s), (x + 22 * l.s, ty + 12 * l.s)]
            pygame.draw.polygon(tela, (255, 210, 60), pts)
            pygame.draw.polygon(tela, (60, 30, 0), pts, 3)
            pygame.draw.line(tela, (60, 30, 0), (x, ty - 12 * l.s), (x, ty + 1 * l.s), max(2, int(4 * l.s)))
            pygame.draw.circle(tela, (60, 30, 0), (x, int(ty + 7 * l.s)), max(2, int(2.4 * l.s)))
    elif T_SAI <= t < T_FIM:  # os BRAÇOS saindo da terra
        if t < T_SOME:
            alt = suave((t - T_SAI) / 5) * (T_ALTURA + 15) * l.s
        else:
            alt = max(0.0, 1 - (t - T_SOME) / (T_FIM - T_SOME)) * (T_ALTURA + 15) * l.s
        h = alt  # (UM braço só, pedido do Gomes: mais grosso, com a mão aberta e as garras)
        base = (x, CHAO + 4)
        topo = (x + 4 * l.s * math.sin(t * 0.5), CHAO - h)
        pygame.draw.line(tela, (26, 18, 8), base, topo, int(26 * l.s))
        pygame.draw.line(tela, (184, 148, 48), base, topo, int(20 * l.s))
        pygame.draw.line(tela, (230, 196, 92), (base[0] - 5 * l.s, base[1]), (topo[0] - 5 * l.s, topo[1]), int(5 * l.s))
        for f in range(4):  # pelinho no braço
            fy = CHAO - h * (0.25 + f * 0.18)
            if fy < CHAO:
                pygame.draw.line(tela, (138, 104, 32), (topo[0] - 10 * l.s, fy), (topo[0] - 16 * l.s, fy - 6 * l.s),
                                 max(2, int(3 * l.s)))
        for g in (-2, -1, 0, 1, 2):  # a mão aberta: 5 garras
            ponta = (topo[0] + g * 8 * l.s, topo[1] - (14 - abs(g) * 3) * l.s)
            pygame.draw.line(tela, (26, 18, 8), topo, ponta, max(3, int(6 * l.s)))
            pygame.draw.line(tela, (240, 236, 220), topo, ponta, max(2, int(3.4 * l.s)))
        pygame.draw.ellipse(tela, (60, 40, 20), (x - 60 * l.s, CHAO - 8, 120 * l.s, 16))


# =====================================================================
# R: METRALHADORA DE OLHOS (+4 olhos)
# =====================================================================
O_NASCE, O_ATIRA, O_TIROS, O_INTERVALO, O_SOME, O_FIM = 12, 14, 6, 6, 52, 64


def olhos_extras(l, p):
    """Onde ficam os 4 olhos a mais (unidades da pose)."""
    cb, pc, qd = p["cb"], p["pc"], p["qd"]
    meio = ((qd[0] + pc[0]) / 2, (qd[1] + pc[1]) / 2)
    return [(cb[0] - 6, cb[1] + 9), (cb[0] + 4, cb[1] + 11), (pc[0] + 4, pc[1] - 4), (meio[0] + 8, meio[1] + 2)]


def metralhadora(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t < O_NASCE:
        m["olhos"] = suave(t / O_NASCE)
    elif t < O_SOME:
        m["olhos"] = 1
    else:
        m["olhos"] = max(0.0, 1 - (t - O_SOME) / (O_FIM - O_SOME - 4))
    k = t - O_ATIRA
    if 0 <= k < O_TIROS * O_INTERVALO and k % O_INTERVALO == 0:
        p = l.pose_vista or l.pose_atual()
        u = olhos_extras(l, p)[(k // O_INTERVALO) % 4]
        x, y = l.ponto({"o": u}, "o")
        jogo.projeteis.append(Projetil(l, x + 8 * l.dir, y, l.dir, GOLPES["trafo_tiro_olho"]))
        som.tocar("tiro")
        jogo.tremer(2)
    if t >= O_FIM:
        return "fim"


def desenha_tiro_olho(p, tela):
    for i in range(4):  # rastro
        x = p.x - p.vx * (i + 1) * 1.2
        pygame.draw.circle(tela, (200, 60, 50), (int(x), int(p.y)), max(1, p.raio - i * 2))
    pygame.draw.circle(tela, (255, 90, 70), (int(p.x), int(p.y)), p.raio)
    pygame.draw.circle(tela, (255, 230, 210), (int(p.x), int(p.y)), max(2, p.raio // 2))


# =====================================================================
# SHIFT: PULÃO
# =====================================================================
P_SAI, P_POUSO_REC = 9, 16


def pulao(l, outro, jogo):
    t = l.t
    m = l.memo
    if t < P_SAI:
        l.vx = 0
    elif t == P_SAI:
        som.tocar("pulo")
        l.vy = -12.5
        l.vx = 10.5 * l.dir
        fumaca(jogo, l.x, CHAO - 4, 8, (150, 130, 100), 3, -1)
    if t > P_SAI and l.no_chao() and "pousou" not in m:
        m["pousou"] = t
        m["caixa"] = None
        jogo.tremer(4)
        fumaca(jogo, l.x, CHAO - 4, 8, (150, 130, 100), 3, -1)
    if "pousou" in m:
        l.vx *= 0.7
        m["quadros"] = [(0, "t_agacha"), (P_SAI, "t_pulo"), (m["pousou"], "t_agacha"),
                        (m["pousou"] + P_POUSO_REC, "parado")]
    l.fisica(jogo)
    if "pousou" in m and t >= m["pousou"] + P_POUSO_REC:
        return "fim"
    if t > 120:
        return "fim"


# =====================================================================
# Z: ULTIMATE (sem cutscene, tudo dentro da luta)
#   corrida lenta -> acertou: arrasta o oponente -> vira o MAX-10 e solta o laserzão
#   -> vira o OPONENTE e usa uma skill dele (sorteada) -> volta a ser o Trafo
# =====================================================================
U_SAI, U_CORRE_ATE = 14, 100
U_DANO = 35
# partes da sequência (quadros depois de acertar)
A_ARRASTA, A_VIRA1, A_LASER, A_VIRA2, A_SKILL, A_VOLTA, A_FIM = 0, 46, 62, 108, 124, 168, 196
DANO_ARRASTA, DANO_LASER, DANO_SKILL = 8, 13, 14  # (= 35)


def _pose(ficha, nome):
    from golpes import POSES
    return ficha.get("poses", {}).get(nome) or POSES[nome]


def _tipo_skill(oponente):
    """Que tipo de golpe do oponente o Trafo vai copiar (sorteado)."""
    from lutador import PADRAO
    tipos = []
    for b, n in oponente.get("golpes", PADRAO).items():
        if b == "Z":
            continue
        g = GOLPES[n]
        tipos.append("longe" if g.get("ia") == "longe" else
                     "cima" if g.get("lanca") or g.get("ia") in ("anti", "perto") else "medio")
    return random.choice(tipos or ["medio"])


def _bate(l, outro, jogo, dano, ponto=None):
    outro.levar(dano, l, GOLPES["trafo_ultimate"])
    outro.vida = max(1, outro.vida)  # o K.O. só no finalzinho
    outro.tremor_hit = 8
    px, py = ponto or (outro.x, outro.y - 70 * outro.s)
    jogo.faisca(px, py, False, dano >= 4)


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    if "pegou" in m:
        return sequencia(l, outro, jogo, t - m["pegou"])
    if l.acertou and "parou" not in m:
        if outro.estado == "golpeado":  # acertou de verdade: começa a sequência
            m["pegou"] = t
            m["vida0"] = outro.vida
            m["tipo"] = _tipo_skill(outro.f)
            l.inv = 999
            outro.mudar("agarrado")
            outro.golpe = None
            return
        m["parou"] = t  # defendeu
    if "parou" in m:
        l.vx *= 0.75
        m["caixa"] = None
        l.fisica(jogo)
        if t - m["parou"] > 32:
            return "fim"
        return
    if t < U_SAI:  # rosnando, juntando força
        l.vx = 0
    elif t < U_CORRE_ATE:  # a corrida (meio lenta)
        l.vx = 4.6 * l.dir
        m["caixa"] = (0, 20, 54, 100)
        if t % 4 == 0:
            fumaca(jogo, l.x - 20 * l.dir, CHAO - 4, 1, (160, 140, 110), 1, -0.3)
    else:
        m["parou"] = t
    l.fisica(jogo)


def sequencia(l, outro, jogo, u):
    m = l.memo
    d = l.dir
    if u < A_VIRA1:  # 1) ARRASTA o oponente pelo chão
        alvo = PAREDE_D - 120 if d > 0 else PAREDE_E + 120
        l.vx = 7 * d if (alvo - l.x) * d > 0 else 0
        l.x += l.vx
        l.sobrepor = dict(_pose(l.f, "t_corre1" if (u // 5) % 2 == 0 else "t_corre2"))
        outro.x, outro.y = l.x + 46 * l.s * d, CHAO
        outro.sobrepor = dict(_pose(outro.f, "caido"))
        if u % 3 == 0:
            fumaca(jogo, outro.x, CHAO - 4, 2, (170, 150, 120), 3, -1)
        if u % 11 == 5:
            _bate(l, outro, jogo, DANO_ARRASTA / 4, (outro.x, CHAO - 20))
            jogo.tremer(4)
    elif u < A_LASER:  # 2) brilha e vira o MAX-10; o oponente fica de pé, zonzo, na frente
        from personagens import PERSONAGENS
        l.vx = 0
        if u == A_VIRA1:
            outro.x = max(PAREDE_E, min(PAREDE_D, l.x + 210 * d))
            outro.sobrepor = dict(_pose(outro.f, "golpeado"))
            outro.dir = -d
        if u == A_VIRA1 + 8:
            l.disfarce = next(f for f in PERSONAGENS if f["nome"] == "MAX-10")
            jogo.clarao = 4
            jogo.tremer(6)
        l.sobrepor = dict(_pose(l.disfarce or l.f, "parado"))
    elif u < A_VIRA2:  # 3) LASERZÃO
        k = u - A_LASER
        l.sobrepor = dict(_pose(l.disfarce, "m_laser_tiro" if k >= 12 else "m_laser_carga"))
        l.pisca = min(1, k / 12)
        if k >= 12 and k % 4 == 0:
            _bate(l, outro, jogo, DANO_LASER / 8)
            jogo.tremer(5)
    elif u < A_SKILL:  # 4) brilha e vira o OPONENTE
        l.pisca = 0
        if u == A_VIRA2 + 8:
            l.disfarce = outro.f
            jogo.clarao = 4
            jogo.tremer(6)
        l.sobrepor = dict(_pose(l.disfarce, "parado"))
    elif u < A_VOLTA:  # 5) usa a skill do oponente
        k = u - A_SKILL
        tipo = m["tipo"]
        if tipo == "longe":  # um tiro de longe (na cor do poder dele)
            l.sobrepor = dict(_pose(l.disfarce, "especial"))
            m["bola"] = l.x + (40 + k * 9) * l.s * d
            if (m["bola"] - outro.x) * d >= 0 and "bateu" not in m:
                m["bateu"] = True
                _bate(l, outro, jogo, DANO_SKILL)
                jogo.tremer(12)
        elif tipo == "medio":  # investida
            l.sobrepor = dict(_pose(l.disfarce, "soco" if k > 10 else "avanco"))
            if k > 10 and "bateu" not in m:
                l.x += (outro.x - 60 * l.s * d - l.x) * 0.35
                if abs(outro.x - l.x) < 70 * l.s:
                    m["bateu"] = True
                    _bate(l, outro, jogo, DANO_SKILL)
                    jogo.tremer(12)
        else:  # golpe pra cima: chega perto e joga pra cima
            l.x += (outro.x - 60 * l.s * d - l.x) * 0.3
            l.sobrepor = dict(_pose(l.disfarce, "subida" if k > 12 else "agachado"))
            if k > 12 and "bateu" not in m:
                m["bateu"] = True
                _bate(l, outro, jogo, DANO_SKILL)
                jogo.tremer(12)
            if "bateu" in m:
                outro.y = max(CHAO - 150 * outro.s, outro.y - 9)
    elif u == A_VOLTA:  # 6) volta a ser o Trafo e o oponente cai
        l.disfarce = None
        l.sobrepor = {}
        m["quadros"] = [(0, "parado")]
        jogo.clarao = 4
        outro.sobrepor = {}
        outro.vida = max(0, m["vida0"] - U_DANO)  # no total, sempre U_DANO (35)
        outro.mudar("voando")
        outro.vx, outro.vy = 5 * d, -7
        jogo.tremer(14)
        l.inv = 0
    elif u >= A_FIM:
        return "fim"
    l.x = max(PAREDE_E, min(PAREDE_D, l.x))


def ultimate_efeito(l, tela):
    """Os brilhos da transformação, o laserzão e o tiro copiado."""
    m = l.memo
    if "pegou" not in m:
        return
    u = l.t - m["pegou"]
    p = l.pose_vista or l.pose_atual()
    cx, cy = l.ponto(p, "pc")
    for ini in (A_VIRA1, A_VIRA2, A_VOLTA - 8):  # brilho de transformação
        if ini <= u < ini + 16:
            k = (u - ini) / 16
            brilho(tela, (int(cx), int(cy)), int((40 + 60 * (1 - abs(k - 0.5) * 2)) * l.s), (255, 236, 160), 170)
            for i in range(3):
                r = int((20 + 90 * ((k * 2 + i / 3) % 1)) * l.s)
                pygame.draw.circle(tela, (255, 245, 210), (int(cx), int(cy)), r, 2)
    if A_LASER + 12 <= u < A_VIRA2:  # LASERZÃO
        ox, oy = l.ponto({"o": (p["cb"][0] + 4, p["cb"][1] + 1)}, "o")
        fx = PAREDE_D + 60 if l.dir > 0 else PAREDE_E - 60
        w = int((26 + 6 * math.sin(l.t * 0.9)) * l.s)
        pygame.draw.line(tela, (150, 0, 0), (ox, oy), (fx, oy + 30), w + 12)
        pygame.draw.line(tela, (255, 50, 30), (ox, oy), (fx, oy + 30), w)
        pygame.draw.line(tela, (255, 230, 210), (ox, oy), (fx, oy + 30), max(3, w // 3))
        brilho(tela, (int(ox), int(oy)), int(30 * l.s), (255, 80, 60), 170)
    if m.get("tipo") == "longe" and A_SKILL <= u < A_VOLTA and "bateu" not in m and "bola" in m:
        cor = (l.disfarce or l.f).get("cor_poder", (255, 200, 120))
        by = cy
        brilho(tela, (int(m["bola"]), int(by)), int(26 * l.s), cor, 200)
        pygame.draw.circle(tela, (255, 255, 240), (int(m["bola"]), int(by)), int(9 * l.s))


def ultimate_quadros():
    q = [(0, "parado"), (6, "t_agacha"), (U_SAI - 2, "t_agacha")]
    for k in range(22):
        q.append((U_SAI + k * 4, "t_corre1" if k % 2 == 0 else "t_corre2"))
    q.append((U_CORRE_ATE + 30, "parado"))
    return q


# =====================================================================
# Golpes do Trafo
# =====================================================================
# =====================================================================
# R (v2.x, pedido do Gomes): TRANSFORMAÇÃO — vira o RIB, faz o selo do KAGE BUNSHIN, volta a ser o Trafo e
# aparece um CLONE (um Trafo) do outro lado do oponente. Por 5 s, todo hit do Trafo vale 2 (o clone bate junto).
# =====================================================================
X_VIRA, X_SELO, X_PUF, X_FIM = 6, 10, 26, 36
CLONE_TEMPO = 5 * 60
CLONE_ATRASO = 5      # o clone bate um pouquinho depois do Trafo


def transforma(l, outro, jogo):
    from personagens import PERSONAGENS
    t = l.t
    l.vx = 0
    l.fisica(jogo)
    if t == X_VIRA:  # PUF: vira o Rib
        som.tocar("puf")
        fumaca(jogo, l.x, l.y - 60 * l.s, 10, (220, 226, 236), 4, -1)
        l.disfarce = next(f for f in PERSONAGENS if f["nome"] == "RIB")
    if X_VIRA <= t < X_PUF:
        from rib import POSES_RIB
        l.sobrepor = dict(POSES_RIB["r_selo"])
    if t == X_PUF:  # KAGE BUNSHIN! volta a ser o Trafo e o clone aparece do outro lado
        som.tocar("puf")
        l.disfarce = l.mutado if getattr(l, "mutado", None) else None
        l.sobrepor = None
        fumaca(jogo, l.x, l.y - 60 * l.s, 10, (220, 226, 236), 4, -1)
        l.extra["clone_t"] = CLONE_TEMPO
        l.extra["tela_toda"] = True
        x = _clone_x(l, outro)
        fumaca(jogo, x, l.y - 60 * l.s, 12, (220, 226, 236), 4, -1)
    if t >= X_FIM:
        return "fim"


def _clone_x(l, outro):
    lado = 1 if outro.x >= l.x else -1
    return max(PAREDE_E, min(PAREDE_D, outro.x + lado * 60 * l.s))


def trafo_todo_quadro(l, jogo):
    """O CLONE da Transformação: conta os 5 s e duplica os hits do Trafo. (E o relógio do olho da ADAPTAÇÃO.)"""
    x = l.extra
    if x.get("adapta_flash", 0) > 0:
        x["adapta_flash"] -= 1
    if x.get("clone_t", 0) <= 0:
        x["tela_toda"] = False
        return
    x["clone_t"] -= 1
    outro = next((o for o in getattr(jogo, "L", ()) if o is not l), None)
    if outro is None:
        return
    x["clone_x"] = _clone_x(l, outro)
    x["clone_dir"] = -1 if outro.x < x["clone_x"] else 1
    x["clone_s"] = l.s
    # acertou um golpe agora (não vale ultimate)? o clone repete o hit daqui a pouquinho
    g = l.memo.get("g_hit", l.golpe) if l.estado == "ataque" and l.golpe else None
    if l.acertou and not x.get("acertou_antes") and g and not g.get("ultimate"):
        x.setdefault("repete", []).append((CLONE_ATRASO, g))
    x["acertou_antes"] = l.acertou and l.estado == "ataque"
    fila = []
    for falta, g in x.get("repete", []):
        if falta > 1:
            fila.append((falta - 1, g))
            continue
        x["clone_bate"] = 10  # (pose de golpe no desenho)
        if outro.vida > 0 and outro.estado != "defendendo" and not outro.extra.get("intangivel"):
            outro.levar(g.get("dano", 0), l, g)
            outro.tremor_hit = max(outro.tremor_hit, 6)
            jogo.faisca(outro.x, outro.y - 64 * outro.s, False, g.get("dano", 0) >= 10)
            som.tocar("soco" if g.get("dano", 0) < 7 else "chute", 0.8)
    x["repete"] = fila
    if x.get("clone_bate", 0) > 0:
        x["clone_bate"] -= 1
    if x["clone_t"] == 0:  # o clone some
        som.tocar("puf", 0.6)
        from max10 import fumaca as fum
        fum(jogo, x["clone_x"], l.y - 60 * l.s, 10, (220, 226, 236), 4, -1)


def desenhar_clone(l, tela, branco):
    """O clone (um Trafo) do outro lado do oponente, virado pra ele, copiando a pose do Trafo."""
    x = l.extra
    if x.get("clone_t", 0) <= 0 or "clone_x" not in x or getattr(l, "_clone", False):
        return
    guarda = (l.x, l.dir, l.vira, l.disfarce)
    l._clone = True
    try:
        l.x, l.dir, l.vira = x["clone_x"] * l.s / x["clone_s"], x["clone_dir"], False
        p = l.pose_vista or l.pose_atual()
        if x.get("clone_bate", 0) > 0:  # dando o golpe
            p = POSES_TRAFO.get("t_lingua", p)
        desenhar_trafo(l, tela, p, branco)
    finally:
        l.x, l.dir, l.vira, l.disfarce = guarda
        l._clone = False


def _registra(nome, **g):
    g.setdefault("base", "parado")
    g.setdefault("pose", "parado")
    g.setdefault("caixa", None)
    g.setdefault("especial", True)
    g["total"] = g.get("total", g["ini"] + g["ativo"] + g.get("rec", 0))
    GOLPES[nome] = g


_registra("trafo_lingua", ini=L_SAI + 1, ativo=L_VOLTA - L_SAI, rec=L_FIM - L_VOLTA, janelas=((L_SAI + 1, L_VOLTA + 2),),
          dano=10, hit=20, defe=14, emp=0, nivel="medio", paralisa=120, logica=linguao, efeito=linguao_efeito,
          ia="longe", quadros=[(0, "parado"), (L_SAI - 3, "t_lingua"), (L_VOLTA + 4, "t_lingua"), (L_FIM, "parado")])
_registra("trafo_terra", ini=T_SAI, ativo=T_SOME - T_SAI, rec=T_FIM - T_SOME, janelas=((T_SAI + 1, T_SAI + 9),),
          dano=20, hit=20, defe=12, emp=1, nivel="medio", imbloqueavel=True, lanca=17, logica=terra,
          efeito=terra_efeito, ia="longe",
          quadros=[(0, "parado"), (T_ENFIA, "t_terra"), (T_SOME, "t_terra"), (T_FIM, "parado")])
_registra("trafo_tiro_olho", ini=0, ativo=1, rec=0, dano=4, hit=10, defe=8, emp=2, nivel="medio", proj=True,
          raio=6, vel=11, desenho_proj=desenha_tiro_olho)
_registra("trafo_olhos", ini=O_ATIRA, ativo=O_TIROS * O_INTERVALO, rec=O_FIM - O_ATIRA - O_TIROS * O_INTERVALO,
          dano=4, hit=10, defe=8, emp=2, nivel="medio", logica=metralhadora, ia="longe",
          quadros=[(0, "parado"), (O_NASCE, "t_olhos"), (O_SOME, "t_olhos"), (O_FIM, "parado")])
_registra("trafo_transforma", ini=X_PUF, ativo=1, rec=X_FIM - X_PUF, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=transforma, ia="medio",
          quadros=[(0, "parado"), (X_VIRA - 2, "t_agacha"), (X_VIRA, "parado"), (X_FIM, "parado")])
GOLPES["trafo_transforma"]["total"] = X_FIM + 1
_registra("trafo_pulo", ini=P_SAI, ativo=30, rec=P_POUSO_REC, janelas=((P_SAI + 2, 120),), caixa=(-10, 20, 54, 100),
          dano=10, hit=20, defe=12, emp=6, nivel="alto", derruba=True, voo=(6, 8), logica=pulao, ia="medio",
          quadros=[(0, "t_agacha"), (P_SAI, "t_pulo"), (120, "t_pulo")])
_registra("trafo_ultimate", ini=U_SAI, ativo=U_CORRE_ATE - U_SAI, rec=30, janelas=((U_SAI, U_CORRE_ATE),),
          dano=0, hit=60, defe=20, emp=0, nivel="medio", ultimate=True, logica=ultimate, efeito=ultimate_efeito,
          ia="ultimate", quadros=ultimate_quadros())

GOLPES_TRAFO = {"E": "trafo_lingua", "Q": "trafo_terra", "R": "trafo_transforma", "SHIFT": "trafo_pulo",
                "Z": "trafo_ultimate"}  # ("trafo_olhos", a metralhadora antiga, continua registrada)

# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  G g d D mostarda (claro -> escuro)  h listra do pelo  c C barriga
#   n nariz  t língua  w r p olho (branco, vermelho, pupila)  m dente/garra  L listra (= g, menos no Indoraptor)
PALETA = {
    "k": (26, 18, 8), "G": (230, 196, 92), "g": (190, 152, 52), "d": (138, 104, 32), "D": (92, 68, 20),
    "h": (112, 82, 22), "c": (236, 218, 160), "C": (196, 176, 112), "n": (24, 18, 14), "t": (226, 112, 132),
    "w": (238, 234, 214), "r": (196, 36, 28), "p": (12, 10, 10), "m": (242, 238, 222),
    "L": (190, 152, 52),  # a LISTRA: igual ao pelo (g); só a roupa INDORAPTOR pinta ela de dourado
}
S_REF = 1.32 / 3

TRONCO = Peca([
    "...kkkkkkkk...",
    "..kgGGGgggdk..",
    ".kgLGggggggdk.",
    ".kGLghggghgdk.",
    ".kGLgggggggdk.",
    ".kgLhgcccgddk.",
    ".kgLgccccgddk.",
    ".kgLgccccgddk.",
    ".kgLgccccghdk.",
    "..kLgcccchdk..",
    "..kLgcccgddk..",
    "..kLdcccgddk..",
    "..kLgdccgddk..",
    "..kLhggggddk..",
    "..kLggggdddk..",
    "..kLgggghddk..",
    "..kLggggdddk..",
    "..kLdgggdddk..",
    "..kLgggdddDk..",
    "..kLggdddDDk..",
    "..kLddddDDDk..",
    "...kddddDDk...",
    "....kkkkkk....",
], PALETA, a=(7, 20), b=(7, 1))

TRONCO_COSTAS = Peca([
    "...kkkkkkkk...",
    "..kgGGGgggdk..",
    ".kgLGgghggLdk.",
    ".kGLggggggLdk.",
    ".kGLghggggLdk.",
    ".kgLggggghLdk.",
    ".kgLggggggLdk.",
    ".kgLggghggLdk.",
    ".kgLggggggLdk.",
    "..kLhgggghLk..",
    "..kLgggggdLk..",
    "..kLgghgggLk..",
    "..kLggggghLk..",
    "..kLhggggdLk..",
    "..kLggggddLk..",
    "..kLgghgghLk..",
    "..kLggggddLk..",
    "..kLdgggddLk..",
    "..kLgggdddLk..",
    "..kLggdddDLk..",
    "..kLddddDDDk..",
    "...kddddDDk...",
    "....kkkkkk....",
], PALETA, a=(7, 20), b=(7, 1))

CABECA = Peca([
    "..kk............",
    ".kgdk...........",
    ".kgddkkkkkk.....",
    "kgGgggggggdkk...",
    "kgGgwwrkgggggk..",
    "kLLLwrpkggggggkk",
    "kLLLLkkggggggnnk",
    "kLggggggggggggnk",
    ".kdgggkmkmkmkkkk",
    ".kddgktttttk....",
    "..kdddkkkkk.....",
    "...kkk..........",
], PALETA, a=(5, 6), b=(5, 0), estica=False)

CABECA_COSTAS = Peca([
    "..kk............",
    ".kgdk...........",
    ".kgddkkkkkk.....",
    "kgGgggggggdkk...",
    "kgGgggggggggdk..",
    "kLLLLLLLLgggggkk",
    "kLLLggggggggggdk",
    "kgggghggggggggdk",
    ".kdgggggggggdkkk",
    ".kddggggggdk....",
    "..kdddkkkkk.....",
    "...kkk..........",
], PALETA, a=(5, 6), b=(5, 0), estica=False)

COXA = Peca([
    ".kkkkkk.",
    "kgLgggdk",
    "kGLggddk",
    "kGLghgdk",
    "kgLggddk",
    "kgLgggdk",
    "kgLgggdk",
    "kgLggddk",
    "kgLgdddk",
    ".kLgddk.",
    ".kLdddk.",
    ".kLddDk.",
    "..kddk..",
    "..kddk..",
    "..kkkk..",
], PALETA, a=(3, 0), b=(3, 14))

CANELA = Peca([
    ".kkkk.",
    "kgLgdk",
    "kgLgdk",
    "kgLgdk",
    "kgLgdk",
    ".kLdk.",
    ".kLdk.",
    ".kLdk.",
    ".kLdk.",
    ".kLdk.",
    ".kLdk.",
    ".kLdk.",
    ".kddk.",
    ".kddk.",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 14))

PATA = Peca([
    ".kkkkk...",
    "kggggdkk.",
    "kgggggddk",
    "kddddddmk",
    ".kmkmkkk.",
], PALETA, a=(2, 1), b=(8, 1), estica=False)

BRACO = Peca([
    ".kkk.",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    ".kdk.",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 11))

ANTEBRACO = Peca([
    ".kkk.",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kgLdk",
    "kdddk",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 10))

MAO = Peca([
    ".kkkk.",
    "kggggk",
    "kgggdk",
    "kmkmkk",
    ".k.k..",
], PALETA, a=(2, 0), b=(2, 4), estica=False)

PERNINHA = Peca([
    ".kk.",
    "kgdk",
    "kgdk",
    "kgdk",
    "kgdk",
    "kddk",
    "kddk",
    "kddk",
    "kmmk",
    ".kk.",
], PALETA, a=(1, 0), b=(1, 9))


def _cor(letra, branco):
    import pecas
    if branco:
        return (245, 245, 250) if letra != "k" else (150, 150, 160)
    return (pecas.TROCA or {}).get(letra, PALETA[letra])


def pelos(l, tela, p, d, esc, branco, frente):
    """O Trafo PELUDINHO: tufos de pelo nas costas, no cangote e nas bochechas (frente=True: os da frente)."""
    def U(u):
        return l.ponto({"_": u}, "_")
    k, g, dd = _cor("k", branco), _cor("g", branco), _cor("d", branco)
    qd, pc, cb = p["qd"], p["pc"], p["cb"]
    tufos = []
    if not frente:  # nas costas, do quadril até o cangote (pra trás)
        for i in range(6):
            f = 0.08 + i * 0.17
            x, y = qd[0] + (pc[0] - qd[0]) * f - 9, qd[1] + (pc[1] - qd[1]) * f
            tufos.append(((x + 5, y + 4), (x - 11, y + 2 + i * 0.8), (x + 4, y - 8), dd if i % 2 else g))
    else:  # o cangote (juba) e a bochecha
        for i in range(4):  # a juba no cangote
            x, y = pc[0] - 6 + i * 3, pc[1] + 3 + i * 3
            tufos.append(((x + 4, y + 4), (x - 12, y + 4), (x + 3, y - 8), g if i % 2 else dd))
        for j in range(2):  # topete atrás da cabeça
            bx, by = cb[0] - 4 + j * 4, cb[1] + 6 - j
            tufos.append(((bx, by), (bx - 7, by + 6), (bx + 3, by + 1), g if j else dd))
        cx_, cy_ = cb[0] + 5, cb[1] - 6  # bochecha
        tufos.append(((cx_, cy_), (cx_ - 4, cy_ - 7), (cx_ + 5, cy_ - 3), g))
    for base, ponta, outra, cor in tufos:
        pts = [U(base), U(ponta), U(outra)]
        pygame.draw.polygon(tela, k, pts)
        pygame.draw.polygon(tela, k, pts, max(2, int(1.2 * esc)))
        mx, my = (pts[0][0] + pts[1][0] + pts[2][0]) / 3, (pts[0][1] + pts[1][1] + pts[2][1]) / 3
        miolo = [(x * 0.72 + mx * 0.28, y * 0.72 + my * 0.28) for x, y in pts]
        pygame.draw.polygon(tela, cor, miolo)


def coleira(l, tela, c, cb, d, esc, branco):
    """A COLEIRA QUEBRADA: tira de couro com rebites no pescoço e um pedaço de corrente pendurado, balançando."""
    k = (150, 150, 160) if branco else PALETA["k"]
    couro = (245, 245, 250) if branco else (120, 40, 34)
    metal = (245, 245, 250) if branco else (176, 180, 190)
    m = (c[0] + (cb[0] - c[0]) * 0.45, c[1] + (cb[1] - c[1]) * 0.45)
    ux, uy = cb[0] - c[0], cb[1] - c[1]
    n = math.hypot(ux, uy) or 1
    px, py = -uy / n, ux / n  # atravessado no pescoço
    meia = 6.5 * esc
    a = (m[0] - px * meia, m[1] - py * meia)
    b = (m[0] + px * meia, m[1] + py * meia)
    pygame.draw.line(tela, k, a, b, max(4, int(5 * esc)))
    pygame.draw.line(tela, couro, a, b, max(2, int(3 * esc)))
    for f in (0.25, 0.75):  # rebites
        r = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        pygame.draw.circle(tela, metal, (round(r[0]), round(r[1])), max(1, int(1 * esc)))
    # a argola e a corrente quebrada pendurada (balança com o movimento)
    arg = (m[0] + px * 2 * esc * d, m[1] + 3 * esc)
    pygame.draw.circle(tela, k, (round(arg[0]), round(arg[1])), max(2, int(2.4 * esc)))
    pygame.draw.circle(tela, metal, (round(arg[0]), round(arg[1])), max(2, int(2.4 * esc)), max(1, int(esc)))
    bal = math.sin(l.t * 0.15) * 0.35 - l.vx * 0.04
    pos = arg
    for i in range(4):
        prox = (pos[0] + math.sin(bal + i * 0.15) * 3.2 * esc, pos[1] + math.cos(bal) * 3.2 * esc)
        pygame.draw.line(tela, k, pos, prox, max(3, int(2.6 * esc)))
        pygame.draw.line(tela, metal if i % 2 == 0 else (120, 124, 136), pos, prox, max(1, int(1.4 * esc)))
        pos = prox
    # a ponta quebrada (elo aberto)
    pygame.draw.line(tela, metal, pos, (pos[0] + 1.5 * esc, pos[1] + 1.5 * esc), max(1, int(esc)))


def desenhar_trafo(l, tela, p, branco):
    desenhar_clone(l, tela, branco)  # TRANSFORMAÇÃO (R): o clone do outro lado do oponente
    esc = l.s / S_REF
    d = l.lado()
    espelho = d < 0
    perto_v = "branco" if branco else "normal"
    longe_v = "branco" if branco else "escuro"
    costas = l.vira

    def P(k):
        return l.ponto(p, k)

    def U(u):  # ponto em unidades da pose -> tela
        return l.ponto({"_": u}, "_")

    def perna(pe, joelho, var):
        q, j, e = P("qd"), P(joelho), P(pe)
        CANELA.desenhar(tela, j, e, esc, espelho, var)
        fr, _ = frente_do_pe(j, e, d)
        PATA.desenhar(tela, e, mais(e, fr, 9), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    def braco(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)

    def pata_do_meio(mao, pe, var, lado_fora):
        """O 3º par de patas, saindo do meio do corpo (vai junto com o braço e a perna)."""
        qd, pc, mm, pp = p["qd"], p["pc"], p[mao], p[pe]
        ombro = (qd[0] + (pc[0] - qd[0]) * 0.42, qd[1] + (pc[1] - qd[1]) * 0.42)
        pata = (mm[0] * 0.45 + pp[0] * 0.55, mm[1] * 0.45 + pp[1] * 0.55 + 6)
        joelho = ((ombro[0] + pata[0]) / 2 + 9 * lado_fora, (ombro[1] + pata[1]) / 2 + 4)
        PERNINHA.desenhar(tela, U(joelho), U(pata), esc, espelho, var)
        PERNINHA.desenhar(tela, U(ombro), U(joelho), esc, espelho, var)

    longe, perto = (("cf", "mf", "pf", "jf"), ("ct", "mt", "pt", "jt")) if costas else \
        (("ct", "mt", "pt", "jt"), ("cf", "mf", "pf", "jf"))
    braco(longe[0], longe[1], longe_v)
    perna(longe[2], longe[3], longe_v)
    pelos(l, tela, p, d, esc, branco, frente=False)
    c, cb = P("pc"), P("cb")
    (TRONCO_COSTAS if costas else TRONCO).desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    perna(perto[2], perto[3], perto_v)
    u, _ = cabeca_eixos(c, cb, d)
    pygame.draw.line(tela, PALETA["k"], c, mais(cb, u, -3 * esc), max(3, int(6 * esc)))
    pygame.draw.line(tela, PALETA["g"] if not branco else (240, 240, 240), c, mais(cb, u, -3 * esc), max(1, int(4 * esc)))
    na_cabeca = (CABECA_COSTAS if costas else CABECA).desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    pelos(l, tela, p, d, esc, branco, frente=True)
    fl = l.extra.get("adapta_flash", 0)
    if fl > 0 and not costas and not branco and (fl // 4) % 2 == 0:  # ADAPTAÇÃO: o olho pisca vermelho
        nivel = l.extra.get("adapta_nivel", 1)
        olho = na_cabeca(6.0, 5.0)
        brilho(tela, (int(olho[0]), int(olho[1])), int((3 + nivel * 1.6) * esc), (255, 40, 30), 70 + 45 * nivel)
        pygame.draw.circle(tela, (255, 60 - nivel * 12, 40 - nivel * 8), (int(olho[0]), int(olho[1])), max(1, int(1.2 * esc)))
    coleira(l, tela, c, cb, d, esc, branco)
    braco(perto[0], perto[1], perto_v)
    # os 4 olhos a mais (R)
    olhos = l.memo.get("olhos", 0) if l.estado == "ataque" else 0
    if olhos > 0 and not costas:
        for i, ou in enumerate(olhos_extras(l, p)):
            x, y = U(ou)
            r = max(1, round(2.6 * esc * olhos))
            pygame.draw.circle(tela, PALETA["k"], (round(x), round(y)), r + 1)
            pygame.draw.circle(tela, PALETA["w"], (round(x), round(y)), r)
            pygame.draw.circle(tela, PALETA["r"], (round(x + d * r * 0.3), round(y)), max(1, r - 1))
            if r > 2:
                pygame.draw.circle(tela, PALETA["p"], (round(x + d * r * 0.4), round(y)), 1)


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Detalhes do Trafo quando ele aparece grande na cutscene: orelha, focinho, olho vermelho e as patas do meio."""
    from corpo import membro
    cb, pc, qd = P("cb"), P("pc"), P("qd")
    focinho = (cb[0] + 16 * s * d, cb[1] + 4 * s)
    membro(q, [(cb, 7 * s), (focinho, 4.5 * s)], cor, cont, borda=2.5, brilho=0.35, sombra=0.35)
    pygame.draw.circle(q, (24, 18, 14), (int(focinho[0] + 3 * s * d), int(focinho[1] - 1 * s)), max(2, int(2.6 * s)))
    orelha = [(cb[0] - 4 * s * d, cb[1] - 5 * s), (cb[0] - 10 * s * d, cb[1] - 17 * s), (cb[0] + 1 * s * d, cb[1] - 7 * s)]
    pygame.draw.polygon(q, escura, orelha)
    pygame.draw.polygon(q, cont, orelha, 3)
    pygame.draw.circle(q, (238, 234, 214), (int(cb[0] + 4 * s * d), int(cb[1] - 2 * s)), max(2, int(2.6 * s)))
    pygame.draw.circle(q, (196, 36, 28), (int(cb[0] + 5 * s * d), int(cb[1] - 2 * s)), max(1, int(1.6 * s)))
    # (as patas do meio saíram no remodel do Gomes)


# =====================================================================
# ENTRADA: o chão racha e ele sai da terra
# =====================================================================
def entrada(l, t, jogo):
    from golpes import misturar
    l.cortar_chao = t < 64
    if t < 18:  # o chão tremendo
        if t == 0:
            som.tocar("terra")
        l.esconde = True
        if t % 3 == 0:
            jogo.tremer(4)
            fumaca(jogo, l.x + random.uniform(-30, 30), CHAO - 4, 1, (120, 96, 60), 2, -1.5)
    elif t < 62:  # saindo da terra
        l.esconde = False
        k = suave((t - 18) / 44)
        l.y = CHAO + 175 * l.s * (1 - k)
        l.sobrepor = dict(POSES_TRAFO["t_olhos"])
        if t % 2 == 0:
            fumaca(jogo, l.x + random.uniform(-40, 40), CHAO - 4, 2, (120, 96, 60), 4, -2.5)
    elif t < 80:  # sacode a terra
        l.y = CHAO
        l.sobrepor = dict(POSES_TRAFO["t_agacha"])
        l.tremor_hit = 3 if t % 4 < 2 else 0
        if t % 3 == 0:
            fumaca(jogo, l.x, l.y - 60 * l.s, 2, (130, 100, 60), 5, -1)
    elif t < 96:
        l.sobrepor = misturar(POSES_TRAFO["t_agacha"], POSES_TRAFO["parado"], suave((t - 80) / 16))
    else:
        l.sobrepor = {}
    l.t += 1


def entrada_efeito(l, tela, t):
    if t >= 70:
        return
    r = int((30 + min(t, 30) * 1.6) * l.s)
    pygame.draw.ellipse(tela, (60, 40, 20), (l.x - r, CHAO - r // 6, r * 2, r // 3))
    for i in range(6):
        a = i * 1.05 + 0.3
        pygame.draw.line(tela, (40, 26, 12), (l.x, CHAO), (l.x + math.cos(a) * r * 1.4, CHAO + math.sin(a) * r * 0.25), 2)



# =====================================================================
# VITÓRIA: levanta a cabeça e UIVA
# =====================================================================
POSES_TRAFO["t_uivo"] = dict(pt=(-20, 0), jt=(-6, 22), pf=(18, 0), jf=(26, 24), qd=(0, 48), pc=(6, 82), cb=(-2, 102),
                             ct=(18, 88), mt=(26, 102), cf=(24, 90), mf=(34, 106))
proporcionar(POSES_TRAFO)


def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES_TRAFO["t_uivo"] if t > 8 else POSES_TRAFO["t_agacha"])
    if t == 10:
        som.tocar("uivo")


def vitoria_efeito(l, tela, t):
    if not 10 <= t < 90:
        return
    p = l.pose_vista or l.pose_atual()
    x, y = l.ponto({"b": (p["cb"][0] + 4, p["cb"][1] + 14)}, "b")
    for i in range(3):  # ondinhas do uivo
        r = int(((t - 10) * 3 + i * 26) % 90 + 10)
        pygame.draw.arc(tela, (240, 230, 200), (x - r, y - r, r * 2, r * 2), 0.9, 2.3, 2)
