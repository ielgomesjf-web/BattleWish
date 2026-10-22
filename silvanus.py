"""SILVANUS: a PLANTA CARNÍVORA guardiã da floresta (criado pelo Gomes) — um espírito antigo que acordou pra proteger
a natureza. Função: ARMADILHAS (enche o mapa de sementes que mordem, prendem e explodem).

Aparência: cabeçona ROXA de planta carnívora (boca grande com dentes) num caule VERDE, folhas grandes na base, raízes
de perna (anda pulando), musgo e florzinhas nas costas e RUNAS que brilham quando usa poder. SEM BRAÇOS: só a cabeça
ataca (mordida e cabeçada) — a cabeça vai pra frente sozinha quando o golpe "estica o braço".
  E      COSPE SEMENTE: acertou direto 4; onde cai vira ARMADILHA MORDEDORA (8, prende 0,5 s). BAIXO+E = CIPÓ (prende 1 s)
  Q      SEMENTE EXPLOSIVA (15)
  R      RAÍZES: nascem 2 PLANTINHAS que mordem (1 a cada 0,5 s, 4 s); murchando, viram semente
  SHIFT  FOLHAS-HÉLICE: voa um pouquinho pra frente e deixa uma semente onde estava
  Z      ULTIMATE: FLORESTA INTEIRA (30, 5 bocas gigantes saindo do chão)
  Z2     2ª ULTIMATE: CHUVA DE SEMENTES (40)
  Passivas (H): JARDIM VIVO / ENGANADOR SELVAGEM / VANTAGEM POR CIMA. Máximo 5 armadilhas.
  Rival: TAMER. Casa: FLORESTA ANTIGA.
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from golpes import GOLPES, misturar, proporcionar, suave  # noqa: F401

POSES_SILVANUS = {
    # (de pé no caule, a cabeçona um pouco pra frente, as raízes abertas)
    "parado": dict(pt=(-16, 0), jt=(-12, 20), pf=(16, 0), jf=(14, 20), qd=(0, 40), pc=(4, 74), cb=(14, 96),
                   ct=(-6, 60), mt=(0, 52), cf=(10, 60), mf=(16, 52)),
    # anda PULANDINHO nas raízes
    "andar1": dict(pt=(-18, 4), jt=(-12, 22), pf=(18, 4), jf=(14, 22), qd=(0, 44), pc=(5, 78), cb=(15, 100),
                   ct=(-6, 64), mt=(0, 56), cf=(10, 64), mf=(16, 56)),
    "andar2": dict(pt=(-14, 10), jt=(-8, 26), pf=(14, 10), jf=(12, 26), qd=(0, 48), pc=(6, 82), cb=(16, 104),
                   ct=(-6, 68), mt=(0, 60), cf=(10, 68), mf=(16, 60)),
    "andar3": dict(pt=(-18, 2), jt=(-12, 20), pf=(18, 2), jf=(14, 20), qd=(0, 40), pc=(4, 72), cb=(14, 94),
                   ct=(-6, 58), mt=(0, 50), cf=(10, 58), mf=(16, 50)),
    "andar4": dict(pt=(-16, 0), jt=(-14, 16), pf=(16, 0), jf=(16, 16), qd=(0, 34), pc=(4, 66), cb=(14, 88),
                   ct=(-6, 52), mt=(0, 44), cf=(10, 52), mf=(16, 44)),
    # E: recolhe o pescoço... e COSPE (a cabeça vai pra frente)
    "s_puxa": dict(pt=(-16, 0), jt=(-12, 20), pf=(16, 0), jf=(14, 20), qd=(0, 38), pc=(0, 72), cb=(4, 100),
                   ct=(-6, 60), mt=(0, 52), cf=(8, 60), mf=(10, 60)),
    "s_cospe": dict(pt=(-16, 0), jt=(-12, 20), pf=(16, 0), jf=(14, 20), qd=(0, 40), pc=(8, 74), cb=(20, 92),
                    ct=(-6, 60), mt=(0, 52), cf=(30, 80), mf=(52, 86)),
    # Q / BAIXO+E: a cabeça desce até o chão e PLANTA a semente na frente
    "s_planta": dict(pt=(-16, 0), jt=(-12, 18), pf=(16, 0), jf=(14, 18), qd=(0, 34), pc=(14, 52), cb=(30, 40),
                     ct=(-6, 50), mt=(0, 44), cf=(24, 44), mf=(32, 40)),
    # R: estica as raízes (a cabeça levanta, as runas acendem)
    "s_raizes": dict(pt=(-26, 0), jt=(-16, 16), pf=(30, 0), jf=(18, 16), qd=(0, 36), pc=(2, 72), cb=(8, 102),
                     ct=(-6, 60), mt=(0, 52), cf=(8, 60), mf=(10, 60)),
    # SHIFT: voando com as folhas girando (as raízes penduradas)
    "s_helice": dict(pt=(-8, 14), jt=(-6, 26), pf=(8, 14), jf=(6, 26), qd=(0, 44), pc=(6, 76), cb=(16, 96),
                     ct=(-6, 60), mt=(0, 52), cf=(8, 60), mf=(10, 60)),
    # Z: BATE a cabeça no chão (chama a floresta)
    "s_bate": dict(pt=(-18, 0), jt=(-12, 18), pf=(18, 0), jf=(14, 18), qd=(0, 32), pc=(12, 50), cb=(26, 30),
                   ct=(-6, 50), mt=(0, 44), cf=(24, 34), mf=(28, 30)),
    "s_ergue": dict(pt=(-18, 0), jt=(-12, 20), pf=(18, 0), jf=(14, 20), qd=(0, 40), pc=(2, 76), cb=(6, 106),
                    ct=(-6, 60), mt=(0, 52), cf=(8, 60), mf=(10, 60)),
}
proporcionar(POSES_SILVANUS)

PALETA = {
    "k": (16, 22, 14), "g": (72, 150, 60), "G": (124, 200, 92), "d": (40, 96, 42),
    "p": (124, 52, 152), "P": (176, 104, 206), "q": (48, 14, 58), "r": (206, 64, 96), "w": (246, 244, 228),
    "t": (104, 82, 52), "T": (146, 116, 74), "m": (62, 112, 52), "f": (240, 150, 200), "F": (255, 240, 200),
    "y": (214, 255, 120), "Y": (96, 136, 64),
}
S_REF = 1.36 / 3


def _cor(letra, branco=False):
    if branco:
        return (245, 245, 250)
    import pecas
    return (pecas.TROCA or {}).get(letra, PALETA[letra])


def onde_cabeca(p):
    """A CABEÇA vai pra frente sozinha quando o golpe 'estica o braço' (ele não tem braço: quem ataca é a boca).
    Devolve (o ponto da cabeça na pose, quanto esticou 0..1)."""
    cb, mf = p["cb"], p["mf"]
    dx, dy = mf[0] - cb[0], mf[1] - cb[1]
    k = max(0.0, min(0.85, (dx - 20) / max(1.0, dx))) if dx > 20 else 0.0
    return (cb[0] + dx * k, cb[1] + dy * k), k


MORDIDAS = {"soco": "parado", "ag_soco": "agachado", "ar_soco": "pulo"}
CHICOTES = {"chute": ((96, 54), "parado"), "ag_chute": ((104, 6), "agachado"), "ar_chute": ((80, -6), "pulo")}


def _lerp(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def animacao(l, p):
    """O jeito de cada ataque dele (sem braço: quem anima é a CABEÇA e as RAÍZES). Devolve
    (a pose do corpo, o deslocamento da cabeça em unidades, a boca 0..1, a ponta da raiz-chicote em unidades ou None).
    Cada golpe tem PREPARO (puxa pra trás), BOTE (vai rápido) e VOLTA (devagar)."""
    if l.estado == "vitoria":  # VITÓRIA: olha pro céu feliz... e ENFIA A CABEÇA NA TERRA
        t = l.t
        if t < V_ENFIA:
            u = suave(min(1.0, t / 12))
            return l.poses["parado"], (-4 * u, 10 * u + math.sin(t * 0.3) * 2 * u), 0.4 * u, None
        u = suave(min(1.0, (t - V_ENFIA) / 8))
        return l.poses["parado"], _lerp((-4, 10), (16, -112), u), 0.0, None
    if l.entrada_t is not None and l.entrada_t >= EN_CRESCEU - 2:  # ENTRADA: o BOTÃO ABRE (a boca)
        u = suave(min(1.0, (l.entrada_t - EN_CRESCEU + 4) / 8)) * (1 - suave(max(0.0, (l.entrada_t - EN_FIM + 6) / 6)))
        return p, (-2 * u, 8 * u), u, None
    if l.estado == "ataque" and l.nome_golpe == "provocar":  # PROVOCAÇÃO: balança feliz embaixo da chuvinha
        t = l.t
        u = min(1.0, t / 8) * (1 if t < 60 else max(0.0, (70 - t) / 10))
        return p, (math.sin(t * 0.25) * 6 * u, 4 * u), 0.3 * u, None
    if l.estado != "ataque" or not l.golpe:
        return p, (0, 0), l.extra.get("boca", 0.0), None
    n, g, t = l.nome_golpe, l.golpe, l.t
    if n == "silv_finta":  # a FINTA: só o preparo do golpe fingido (e fica nele)
        n, t = l.extra.get("finta_de", "soco"), min(l.t, 9)
        g = dict(GOLPES.get(n, {}), ini=10, ativo=99, rec=1)
    ini, at, rec = max(1, g.get("ini", 6)), max(1, g.get("ativo", 3)), max(1, g.get("rec", 8))
    if n in MORDIDAS:
        corpo = l.poses.get(MORDIDAS[n]) or p
        tras, frente = (-12, 6), {"soco": (50, -6), "ag_soco": (52, -4), "ar_soco": (42, -16)}[n]
        if t < ini:  # PREPARO: puxa o pescoço pra trás e vai abrindo a boca
            u = suave(t / ini)
            return corpo, _lerp((0, 0), tras, u), 0.5 * u, None
        if t < ini + at:  # o BOTE: vai rápido (2 quadros) de boca escancarada
            u = min(1.0, (t - ini + 1) / 2)
            return corpo, _lerp(tras, frente, u), 1.0, None
        u = suave(min(1.0, (t - ini - at) / rec))  # NHAC! fecha e volta devagar
        return corpo, _lerp(frente, (0, 0), u), 0.0, None
    if n in CHICOTES:
        alvo, base = CHICOTES[n]
        corpo = l.poses.get(base) or p
        enrola = (-14, 12)
        if t < ini:  # a raiz se ENROLA pra trás
            u = suave(t / ini)
            return corpo, (-3 * u, 0), 0.0, _lerp((6, 2), enrola, u)
        if t < ini + at:  # CHICOTADA pra frente
            u = min(1.0, (t - ini + 1) / 2)
            return corpo, (-3, 0), 0.0, _lerp(enrola, alvo, u)
        u = suave(min(1.0, (t - ini - at) / rec))  # volta pro monte de raízes
        return corpo, (-3 * (1 - u), 0), 0.0, _lerp(alvo, (6, 2), u) if u < 0.95 else None
    if n == "silv_cospe":  # E: enche as bochechas pra trás... e COSPE
        if t < E_COSPE:
            u = suave(t / E_COSPE)
            return p, (-12 * u, 6 * u), 0.0, None
        if t < E_COSPE + 6:
            u = min(1.0, (t - E_COSPE + 1) / 2)
            return p, _lerp((-12, 6), (16, -4), u), 1.0, None
        u = suave(min(1.0, (t - E_COSPE - 6) / (E_FIM - E_COSPE - 6)))
        return p, _lerp((16, -4), (0, 0), u), 0.3 * (1 - u), None
    if n in ("silv_explosiva", "silv_cipo_planta"):  # Q / BAIXO+E: a cabeça desce até o chão e planta
        fundo = (30, -82)
        if t < Q_PLANTA:
            u = suave(t / Q_PLANTA)
            return l.poses["parado"], _lerp((0, 0), fundo, u), 0.7 * u, None
        if t < Q_PLANTA + 6:
            return l.poses["parado"], fundo, 0.0, None
        u = suave(min(1.0, (t - Q_PLANTA - 6) / (Q_FIM - Q_PLANTA - 6)))
        return l.poses["parado"], _lerp(fundo, (0, 0), u), 0.0, None
    if n == "silv_raizes":  # R: levanta a cabeça e RUGE enquanto as raízes correm pelo chão
        u = suave(min(1.0, t / 8)) * (1 - suave(max(0.0, (t - (R_FIM - 8)) / 8)))
        return l.poses["parado"], (-4 * u, 12 * u), u, None
    if n == "silv_ultimate":  # Z: se ergue... e BATE a cabeça no chão
        if t < U_BATE:
            u = suave(t / U_BATE)
            return l.poses["parado"], (-6 * u, 16 * u), 0.6 * u, None
        if t < U_BATE + 3:
            return l.poses["parado"], _lerp((-6, 16), (30, -82), (t - U_BATE + 1) / 3), 0.0, None
        if t < U_BATE + 30:
            return l.poses["parado"], (30, -82), 0.0, None
        u = suave(min(1.0, (t - U_BATE - 30) / 20))
        return l.poses["parado"], _lerp((30, -82), (0, 0), u), 0.0, None
    return p, (0, 0), l.extra.get("boca", 0.0), None


def _oval(cx, cy, rx, ry, ang=0.0, n=16):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + math.cos(a) * rx * c - math.sin(a) * ry * s, cy + math.cos(a) * rx * s + math.sin(a) * ry * c)
            for a in (i / n * math.tau for i in range(n))]


def _poli(sup, cor, pts, borda=True):
    pygame.draw.polygon(sup, cor, pts)
    if borda:
        pygame.draw.polygon(sup, _cor("k"), pts, 1)


def folha(sup, base, comp, larg, ang, cor, veia, branco):
    """Uma FOLHA (gota comprida) saindo da base no ângulo ang, com a veia no meio."""
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux
    pts = []
    for i in range(9):
        k = i / 8
        w = math.sin(k * math.pi) * larg * (1 - 0.3 * k)
        pts.append((base[0] + ux * comp * k + nx * w, base[1] + uy * comp * k + ny * w))
    for i in range(8, -1, -1):
        k = i / 8
        w = math.sin(k * math.pi) * larg * (1 - 0.3 * k)
        pts.append((base[0] + ux * comp * k - nx * w * 0.8, base[1] + uy * comp * k - ny * w * 0.8))
    _poli(sup, _cor(cor, branco), pts)
    pygame.draw.line(sup, _cor(veia, branco), base, (base[0] + ux * comp * 0.85, base[1] + uy * comp * 0.85))


def raiz(sup, q, j, pe, d, cor, branco):
    """A PERNA DE RAIZ (grossa em cima, fininha no pé) com as raizinhas abertas no chão."""
    k = _cor("k")
    pygame.draw.line(sup, k, q, j, 7)
    pygame.draw.line(sup, k, j, pe, 5)
    pygame.draw.line(sup, _cor(cor, branco), q, j, 5)
    pygame.draw.line(sup, _cor(cor, branco), j, pe, 3)
    for kk in (0.35, 0.7):  # as raizinhas soltas (de lado, enroscadas)
        x, y = q[0] + (j[0] - q[0]) * kk, q[1] + (j[1] - q[1]) * kk
        pygame.draw.line(sup, k, (x, y), (x - d * 3, y + 2), 2)
    for dx in (-3, 1, 4):  # as raizinhas do pé
        pygame.draw.line(sup, k, pe, (pe[0] + dx * d, pe[1] + 1), 2)
        pygame.draw.line(sup, _cor("T", branco), pe, (pe[0] + dx * d * 0.8, pe[1] + 1), 1)


def cabeca(sup, H, R, d, boca, branco, runa=0.0, t=0):
    """A CABEÇONA de planta carnívora (de lado, olhando pra d): as duas metades da boca abrem pela dobradiça de
    trás; dentro é escuro com a língua; os DENTES brancos nas bordas; pintinhas claras em cima; folhinhas atrás."""
    hx, hy = H[0] - d * R * 0.75, H[1]  # a dobradiça (atrás)
    ang = math.radians(4 + 38 * boca)
    # as folhinhas de trás da cabeça (a gola)
    for i, a in enumerate((-2.4, -2.9, 2.5)):
        aa = a if d > 0 else math.pi - a
        folha(sup, (hx, hy), R * 0.9, 2.2, aa, "d" if i % 2 else "g", "G", branco)
    # o DENTRO da boca
    frente_c = (H[0] + d * R * math.cos(ang), H[1] - R * math.sin(ang) * 1.2)
    frente_b = (H[0] + d * R * math.cos(ang), H[1] + R * math.sin(ang) * 1.2)
    if boca > 0.05:
        _poli(sup, _cor("q", branco), [(hx, hy), frente_c, frente_b])
        pygame.draw.line(sup, _cor("r", branco), (hx + d * 2, hy + 1), (hx + d * R * 1.2, hy + R * 0.5 * math.sin(ang)), 2)

    def metade(cima):
        s = -1 if cima else 1
        giro = -ang if cima else ang
        pts = []
        for i in range(13):
            a = i / 12 * math.pi
            x, y = math.cos(a) * R * 1.05, s * math.sin(a) * R * 0.95
            x += R * 0.75  # (em volta da dobradiça)
            c, sn = math.cos(giro), math.sin(giro)
            rx, ry = x * c - y * sn, x * sn + y * c
            pts.append((hx + d * rx, hy + ry))
        return pts

    for cima in (False, True):
        pts = metade(cima)
        _poli(sup, _cor("p", branco), pts)
        if cima and not branco:  # as PINTINHAS claras e o brilho de cima
            for i in (3, 5, 8):
                x, y = pts[i]
                sup.set_at((int(x), int(y + 3)), _cor("P"))
                sup.set_at((int(x + 1), int(y + 3)), _cor("P"))
            if runa > 0:  # a RUNA na testa
                x, y = pts[6]
                cor = _cor("y") if runa > 0.5 or (t // 4) % 2 else _cor("Y")
                pygame.draw.line(sup, cor, (x - 1, y + 2), (x + 1, y + 4))
                pygame.draw.line(sup, cor, (x + 1, y + 2), (x - 1, y + 4))
        # os DENTES na borda reta (da dobradiça até a ponta), apontando pra outra metade
        a0, a1 = pts[0], pts[-1]  # (a ponta e a dobradiça: a borda reta)
        for i in range(1, 5):
            k = i / 5
            bx, by = a1[0] + (a0[0] - a1[0]) * k, a1[1] + (a0[1] - a1[1]) * k
            ponta = 3 if cima else -3
            pygame.draw.polygon(sup, _cor("w", branco), [(bx - 1, by), (bx + 1, by), (bx, by + ponta)])


def raizes_chao(sup, base, d, t, mexe, branco, no_ar):
    """O 'corpo de baixo': um MONTE DE RAÍZES saindo da base e se espalhando pelo chão (ele se arrasta com elas).
    mexe 0..1 = andando (as raízes se esticam e puxam); no_ar = penduradas (no pulo)."""
    k = _cor("k")
    for i, (ang, comp) in enumerate(((-0.12, 26), (0.08, 23), (0.3, 18), (-0.3, 20), (0.5, 14), (-0.55, 15), (0.0, 11), (0.2, 9))):
        lado = 1 if i % 2 == 0 else -1  # (umas pra frente, outras pra trás)
        onda = math.sin(t * 0.35 + i * 1.7) * 3 * mexe
        c = comp + onda
        if no_ar:  # penduradas, balançando soltas (curvas, tipo cabelo)
            fim = (base[0] + lado * d * c * 0.25 + math.sin(t * 0.25 + i * 2) * 4, base[1] + c * 0.55)
            meio = (base[0] + lado * d * c * 0.35, base[1] + c * 0.25)
        else:  # deitadas no chão, se enroscando
            fim = (base[0] + lado * d * c * math.cos(ang), base[1] + 1 + abs(ang) * 1.5)
            meio = (base[0] + lado * d * c * 0.45, base[1] - 2 - (i % 3) + onda * 0.4)
        larg = 5 if i < 2 else 4 if i < 5 else 3
        pygame.draw.lines(sup, k, False, [base, meio, fim], larg + 2)
        pygame.draw.lines(sup, _cor("T" if i % 3 == 0 else "t", branco), False, [base, meio, fim], larg)
    pygame.draw.ellipse(sup, k, (base[0] - 10, base[1] - 7, 20, 11))  # o 'pé' onde as raízes se juntam
    pygame.draw.ellipse(sup, _cor("t", branco), (base[0] - 9, base[1] - 6, 18, 9))
    pygame.draw.line(sup, _cor("T", branco), (base[0] - 5, base[1] - 4), (base[0] + 4, base[1] - 5))


def raiz_chicote(sup, ini, fim, d, t, branco):
    """A RAIZ-CHICOTE (o "chute"): sai do monte de raízes rente ao chão, faz uma curva em S e vai AFINANDO até a
    ponta enrolada; casca com nós, um filete claro e raizinhas soltas."""
    dx, dy = fim[0] - ini[0], fim[1] - ini[1]
    n = math.hypot(dx, dy) or 1
    nx, ny = -dy / n, dx / n
    c1 = (ini[0] + dx * 0.35 + nx * 6 * d, ini[1] + dy * 0.35 + ny * 6 * d + 3)
    c2 = (ini[0] + dx * 0.7 - nx * 5 * d, ini[1] + dy * 0.7 - ny * 5 * d)
    pts = []
    for i in range(15):
        u = i / 14
        x = (1 - u) ** 3 * ini[0] + 3 * (1 - u) ** 2 * u * c1[0] + 3 * (1 - u) * u * u * c2[0] + u ** 3 * fim[0]
        y = (1 - u) ** 3 * ini[1] + 3 * (1 - u) ** 2 * u * c1[1] + 3 * (1 - u) * u * u * c2[1] + u ** 3 * fim[1]
        pts.append((x, y))
    k, cor, claro = _cor("k"), _cor("t", branco), _cor("T", branco)
    largs = [max(2, round(9 - 7 * i / 13)) for i in range(14)]
    for (a, b), w in zip(zip(pts, pts[1:]), largs):  # o contorno
        pygame.draw.line(sup, k, a, b, w + 2)
    for (a, b), w in zip(zip(pts, pts[1:]), largs):  # a casca
        pygame.draw.line(sup, cor, a, b, w)
    for (a, b), w in zip(zip(pts[1:-3], pts[2:-2]), largs[1:]):  # o filete claro de cima
        pygame.draw.line(sup, claro, (a[0], a[1] - w // 3), (b[0], b[1] - w // 3), 1)
    for i in (3, 7):  # os NÓS da madeira
        x, y = pts[i]
        sup.set_at((int(x), int(y)), k)
        sup.set_at((int(x + 1), int(y + 1)), k)
    for i, lado in ((4, 1), (8, -1), (11, 1)):  # as raizinhas soltas
        x, y = pts[i]
        ux, uy = pts[i + 1][0] - x, pts[i + 1][1] - y
        m = math.hypot(ux, uy) or 1
        px, py = -uy / m * lado, ux / m * lado
        pygame.draw.line(sup, k, (x, y), (x + px * 4 + ux / m * 2, y + py * 4 + uy / m * 2), 2)
        pygame.draw.line(sup, cor, (x, y), (x + px * 3 + ux / m * 2, y + py * 3 + uy / m * 2), 1)
    fx, fy = fim  # a PONTA enrolada
    ux, uy = (fim[0] - pts[-3][0]), (fim[1] - pts[-3][1])
    m = math.hypot(ux, uy) or 1
    ux, uy = ux / m, uy / m
    gancho = [fim, (fx + ux * 2 - uy * 2, fy + uy * 2 + ux * 2), (fx - uy * 3, fy + ux * 3)]
    pygame.draw.lines(sup, k, False, gancho, 3)
    pygame.draw.lines(sup, claro, False, gancho, 1)


def desenhar_silvanus(l, tela, p, branco):
    from inazumaneko import em_pixel  # (o pincel de PIXEL ART: desenha pequeno e amplia sem borrar)
    esc = l.s / S_REF
    d = l.lado()
    p, desloca, boca, ponta = animacao(l, p)
    H_pose = (p["cb"][0] + desloca[0], p["cb"][1] + desloca[1])
    runa = 1.0 if (l.estado == "ataque" and l.golpe and l.golpe.get("especial")) or l.extra.get("finta_armada", 0) > 0         else 0.0
    t = l.t
    mexe = 1.0 if l.estado == "andando" else 0.0
    s, dd = l.s, l.lado()

    afunda = l.extra.get("afunda", 0) if l.estado == "vitoria" else 0

    def T(u):  # ponto da pose (unidades) -> tela
        return (l.x + u[0] * s * dd, l.y + afunda - u[1] * s)

    base_u = ((p["pt"][0] + p["pf"][0]) / 2 * 0.3, min(p["pt"][1], p["pf"][1]))  # (onde as raízes se juntam)
    ponta_u = (base_u[0] + ponta[0], base_u[1] + ponta[1]) if ponta else None
    no_ar = base_u[1] > 6
    H = T(H_pose)
    pts = [T(base_u), T(p["qd"]), T(p["pc"]), T(p["cb"]), H] + ([T(ponta_u)] if ponta_u else [])

    def desenho(sup, Q, e):
        base, qd, pc, h = Q(T(base_u)), Q(T(p["qd"])), Q(T(p["pc"])), Q(H)
        h = (h[0] + d * 2, h[1] + 6)  # (a cabeça um pouco mais baixa: o pescoço faz a CURVA por cima)
        bal = math.sin(t * 0.1) * 0.12
        raizes_chao(sup, base, d, t, mexe, branco, no_ar)
        if ponta_u:
            raiz_chicote(sup, (base[0] + d * 4, base[1] - 1), Q(T(ponta_u)), d, t, branco)
        gira = l.estado == "ataque" and l.nome_golpe == "silv_helice"
        eixo = (qd[0], qd[1] + 1)  # (o eixo da hélice: no alto do bulbo)
        if gira:  # FOLHAS-HÉLICE: as 3 folhas girando em volta do bulbo (a de trás passa por trás)
            pygame.draw.ellipse(sup, _cor("G", branco), (eixo[0] - 26, eixo[1] - 4, 52, 8), 1)  # (o rastro do giro)
            for i in range(3):
                a = t * 0.9 + i * math.tau / 3
                if math.sin(a) < 0:
                    comp = 24 * abs(math.cos(a)) + 3
                    folha(sup, eixo, comp, 5, 0.0 if math.cos(a) > 0 else math.pi, "d", "g", branco)
        else:  # a folha de TRÁS
            folha(sup, (base[0] - d * 2, base[1] - 4), 20, 5, (math.pi + 0.45 + bal) if d > 0 else (-0.45 - bal), "d", "g", branco)
            folha(sup, (base[0] - d * 1, base[1] - 6), 16, 4, (math.pi + 1.1 + bal) if d > 0 else (-1.1 - bal), "g", "G", branco)
        # o CORPO: curto e GROSSO (um bulbo de caule em cima das raízes)
        topo = (qd[0] + d * 1, qd[1] + 4)
        pygame.draw.ellipse(sup, _cor("k"), (base[0] - 8, topo[1] - 2, 16, base[1] - topo[1] + 2))
        pygame.draw.ellipse(sup, _cor("g", branco), (base[0] - 7, topo[1] - 1, 14, base[1] - topo[1]))
        pygame.draw.ellipse(sup, _cor("d", branco), (base[0] - 7 + (0 if d > 0 else 8), topo[1] + 2, 6,
                                                      base[1] - topo[1] - 4))
        pygame.draw.line(sup, _cor("G", branco), (base[0] + d * 3, topo[1] + 3), (base[0] + d * 4, base[1] - 4))
        # o PESCOÇO: FINO e COMPRIDO, sobe por trás e faz a curva grande (gancho) caindo na cabeça
        a, b, c_, e_ = (base[0], topo[1] + 2), (base[0] - d * 12, topo[1] - 26), (h[0] - d * 8, h[1] - 26), h
        curva = []
        for i in range(17):
            u = i / 16
            x = (1 - u) ** 3 * a[0] + 3 * (1 - u) ** 2 * u * b[0] + 3 * (1 - u) * u * u * c_[0] + u ** 3 * e_[0]
            y = (1 - u) ** 3 * a[1] + 3 * (1 - u) ** 2 * u * b[1] + 3 * (1 - u) * u * u * c_[1] + u ** 3 * e_[1]
            curva.append((x, y))
        pygame.draw.lines(sup, _cor("k"), False, curva, 6)
        pygame.draw.lines(sup, _cor("g", branco), False, curva, 4)
        pygame.draw.lines(sup, _cor("G", branco), False, [(x, y - 1) for x, y in curva[2:-3]], 1)
        if not branco:
            for fx, fy in ((base[0] - d * 4, topo[1] + 4), (base[0] + d * 2, topo[1] + 9)):  # RUNAS no corpo
                cor = _cor("y") if runa else _cor("Y")
                sup.set_at((int(fx), int(fy)), cor)
                sup.set_at((int(fx + 1), int(fy + 1)), cor)
                sup.set_at((int(fx - 1), int(fy + 1)), cor)
            for i in range(7):  # o MUSGO nas costas do corpo e no começo do pescoço
                mx, my = curva[1 + i // 2] if i < 4 else (base[0] - d * 6, topo[1] + 3 + i)
                sup.set_at((int(mx - d * 2), int(my + i % 2)), _cor("m"))
            for fx, fy in (curva[5], (base[0] - d * 6, topo[1] + 6)):  # as FLORZINHAS
                fx -= d * 3
                for ox, oy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                    sup.set_at((int(fx + ox), int(fy + oy)), _cor("f"))
                sup.set_at((int(fx), int(fy)), _cor("F"))
        if gira:
            for i in range(3):
                a = t * 0.9 + i * math.tau / 3
                if math.sin(a) >= 0:
                    comp = 24 * abs(math.cos(a)) + 3
                    folha(sup, (eixo[0], eixo[1] + 1), comp, 5, 0.0 if math.cos(a) > 0 else math.pi, "g", "G", branco)
        else:  # a folha da FRENTE
            folha(sup, (base[0] + d * 2, base[1] - 4), 21, 5, (0.45 - bal) if d > 0 else (math.pi - 0.45 + bal), "g", "G", branco)
        cabeca(sup, h, 9, d, boca, branco, runa, t)

    em_pixel(tela, esc, pts, desenho, folga=40)


# =====================================================================
# AS ARMADILHAS (no l.extra: estado da luta, mexidas no todo_quadro; o desenho só lê)
#   boca  = ARMADILHA MORDEDORA (8, prende 0,5 s)   cipo = CIPÓ (3, prende 1 s)   bomba = SEMENTE EXPLOSIVA (15)
# =====================================================================
MAX_ARMADILHAS = 5
ARMA_EM = 20                       # quadros até a armadilha ficar ARMADA
PISA = 26                          # (distância pra pisar, em unidades)
PRENDE_BOCA, PRENDE_CIPO = 30, 60
BOMBA_PERTO = 46


def outro_de(l, jogo):
    return jogo.L[1] if jogo.L[0] is l else jogo.L[0]


def armadilhas(l):
    return l.extra.setdefault("armadilhas", [])


def plantar(l, tipo, x):
    """Planta uma armadilha no chão em x (a mais velha some se já tiver o máximo)."""
    lista = armadilhas(l)
    lista.append(dict(tipo=tipo, x=max(PAREDE_E, min(PAREDE_D, x)), t=0))
    while len(lista) > MAX_ARMADILHAS:
        lista.pop(0)
    som.tocar("terra", 0.35)


def prende(alvo, tempo):
    if alvo.vida > 0:
        alvo.mudar("tonto")
        alvo.golpe = None
        alvo.tonto_tempo = tempo
        alvo.paralisado = True


def armadilhas_quadro(l, outro, jogo):
    from inazumaneko import acerto
    lista = armadilhas(l)
    pode = outro.vida > 0 and outro.inv <= 0 and outro.estado not in ("caido", "voando", "agarrado")
    for a in lista:
        a["t"] += 1
        if a["t"] < ARMA_EM or not pode or a.get("disparou"):
            continue
        perto = abs(outro.x - a["x"])
        if a["tipo"] == "bomba":
            if perto < BOMBA_PERTO * l.s and outro.y > CHAO - 120 * l.s:
                a["disparou"] = True
                acerto(jogo, l, outro, "silv_bomba", ("silv_explosiva", 0))
                jogo.tremer(10)
                som.tocar("explosao", 0.7)
                for _ in range(14):  # a terra e as folhas voando
                    jogo.faiscas.append([a["x"] + random.uniform(-20, 20), CHAO - random.uniform(0, 30),
                                         random.uniform(-5, 5), random.uniform(-7, -2), random.randint(20, 40),
                                         random.choice(((104, 82, 52), (72, 150, 60), (214, 255, 120))), 3])
        elif perto < PISA * l.s and outro.no_chao():  # PISOU
            a["disparou"] = True
            nome = "silv_boca" if a["tipo"] == "boca" else "silv_cipo"
            res = acerto(jogo, l, outro, nome, (nome, 0))
            if res == "hit":
                prende(outro, PRENDE_BOCA if a["tipo"] == "boca" else PRENDE_CIPO)
            som.tocar("lingua" if a["tipo"] == "boca" else "chute", 0.6)
    for a in list(lista):  # (as que dispararam: a animação de fechar e somem)
        if a.get("disparou"):
            a["some"] = a.get("some", 0) + 1
            if a["some"] > 24:
                lista.remove(a)


def _px(tela, cor, x, y, e):
    pygame.draw.rect(tela, cor, (int(x), int(y), max(1, int(round(e))), max(1, int(round(e)))))


def desenha_armadilha(tela, a, s, t):
    """As armadilhas no chão, em PIXEL ART (desenho pequeno ampliado sem borrar), bem visíveis: uma moitinha com
    folhas verdes claras em volta e o brilho verde piscando quando está armada."""
    e = s / S_REF * 1.0
    armada = a["t"] >= ARMA_EM
    cresce = min(1.0, a["t"] / ARMA_EM) if not armada else 1.0
    sup = pygame.Surface((19, 12), pygame.SRCALPHA)
    k = PALETA["k"]
    # o montinho de terra e as FOLHAS em volta (o que mais aparece de longe)
    pygame.draw.ellipse(sup, (70, 50, 30), (2, 9, 15, 3))
    for x0, lado in ((3, -1), (15, 1)):
        pygame.draw.polygon(sup, k, [(x0, 11), (x0 + lado * 4, 6), (x0 + lado * 1, 11)])
        pygame.draw.line(sup, PALETA["G"], (x0, 10), (x0 + lado * 3, 7))
    if a["tipo"] == "boca":
        fechou = "some" in a
        abre = 0 if (fechou or not armada) else (3 if (t // 18) % 2 else 2)
        pygame.draw.ellipse(sup, k, (4, 6, 11, 6))
        pygame.draw.ellipse(sup, PALETA["p"], (5, 7, 9, 4))  # a metade de baixo
        if abre:
            pygame.draw.rect(sup, PALETA["q"], (6, 7 - abre, 7, abre + 1))
        pygame.draw.ellipse(sup, k, (4, 3 - abre, 11, 6))
        pygame.draw.ellipse(sup, PALETA["p"], (5, 4 - abre, 9, 4))  # a de cima (abrindo e fechando)
        sup.set_at((7, 5 - abre), PALETA["P"])
        for x in (6, 8, 10, 12):  # os DENTES
            sup.set_at((x, 7), PALETA["w"])
            sup.set_at((x + 1, 6 - abre + 1 if abre else 7), PALETA["w"])
    elif a["tipo"] == "cipo":
        for i in range(3):  # o LAÇO de cipó enrolado (mexe quando está armado)
            dy = 1 if armada and (t // 10 + i) % 2 else 0
            pygame.draw.ellipse(sup, k, (3 + i * 4, 6 - dy, 6, 5), 2)
            pygame.draw.ellipse(sup, PALETA["g"], (3 + i * 4, 6 - dy, 6, 5), 1)
        sup.set_at((9, 4), PALETA["G"])
        sup.set_at((10, 3), PALETA["G"])
    else:  # BOMBA: a semente gorda meio enterrada, com a RUNA e um brotinho
        pygame.draw.ellipse(sup, k, (5, 3, 9, 9))
        pygame.draw.ellipse(sup, PALETA["t"], (6, 4, 7, 7))
        pygame.draw.line(sup, PALETA["T"], (7, 5), (8, 5))
        cor = PALETA["y"] if armada and (t // 6) % 2 else PALETA["Y"]
        sup.set_at((9, 7), cor)
        sup.set_at((8, 8), cor)
        sup.set_at((10, 8), cor)
        pygame.draw.line(sup, PALETA["g"], (9, 3), (10, 1))
        sup.set_at((11, 1), PALETA["G"])
    alto = max(1, int(12 * e * (0.4 + 0.6 * cresce)))
    img = pygame.transform.scale(sup, (int(19 * e), alto))
    x, y = a["x"], CHAO + e
    if armada and "some" not in a and (t // 40) % 3 == 0:  # o BRILHO verde fraquinho, de vez em quando (pra quem presta atenção)
        brilho = 40 + int(40 * (0.5 + 0.5 * math.sin(t * 0.15)))
        camada = pygame.Surface((int(26 * e), int(5 * e)), pygame.SRCALPHA)
        pygame.draw.ellipse(camada, (150, 255, 110, brilho // 2), camada.get_rect())
        pygame.draw.ellipse(camada, (190, 255, 140, brilho), camada.get_rect(), max(1, int(e * 0.6)))
        tela.blit(camada, (int(x - 13 * e), int(y - 4 * e)))
    tela.blit(img, (int(x - img.get_width() / 2), int(y - alto)))
    if "some" in a and a["tipo"] != "bomba" and a["some"] < 8:  # o SNAP!
        pygame.draw.circle(tela, (255, 255, 255), (int(x), int(y - 5 * e)), int((4 + a["some"]) * e), max(1, int(e)))


# =====================================================================
# E: COSPE SEMENTE — vai em ARCO; acertou direto = 4; caiu no chão = ARMADILHA (boca; BAIXO+E = cipó plantado)
# =====================================================================
E_COSPE, E_FIM = 12, 28


def cospe(l, outro, jogo):
    t = l.t
    e = getattr(l, "entrada_atual", None)
    if t <= 1 and e is not None and e.dir in (1, 2, 3):  # BAIXO + E: planta o CIPÓ em vez de cuspir
        l.comecar("silv_cipo_planta")
        return
    l.vx = 0
    l.fisica(jogo)
    l.extra["boca"] = 0.0 if t < E_COSPE - 3 else (1.0 if t < E_COSPE + 6 else 0.0)
    if t == E_COSPE:
        l.extra.setdefault("voando", []).append(dict(x=l.x + 46 * l.s * l.dir, y=l.y - 90 * l.s, vx=6.5 * l.dir,
                                                     vy=-5.0, tipo="boca", t=0,
                                                     registro=(l.nome_golpe, getattr(l, "golpe_id", 0))))
        som.tocar("lingua", 0.5)
    if t >= E_FIM:
        l.extra["boca"] = 0.0
        return "fim"


def sementes_quadro(l, outro, jogo):
    from inazumaneko import acerto
    lista = l.extra.get("voando") or []
    for sm in list(lista):
        sm["t"] += 1
        sm["x"] += sm["vx"]
        sm["vy"] += 0.45
        sm["y"] += sm["vy"]
        if (abs(sm["x"] - outro.x) < 22 * outro.s and outro.y - 120 * outro.s < sm["y"] < outro.y
                and outro.inv <= 0 and outro.vida > 0):  # ACERTOU DIRETO
            acerto(jogo, l, outro, "silv_semente", sm.get("registro", ("silv_cospe", 0)))
            lista.remove(sm)
        elif sm["y"] >= CHAO - 2 or sm["x"] < PAREDE_E or sm["x"] > PAREDE_D:  # caiu: vira ARMADILHA
            plantar(l, sm["tipo"], sm["x"])
            lista.remove(sm)


def desenha_sementes(l, tela):
    e = l.s / S_REF
    for sm in l.extra.get("voando") or ():
        x, y = sm["x"], sm["y"]
        for dx, dy, c in ((0, 0, "t"), (1, 0, "T"), (0, 1, "t"), (1, 1, "t"), (-1, 0, "t")):
            _px(tela, PALETA[c], x + dx * e, y + dy * e, e)
        _px(tela, PALETA["G"], x, y - e, e)  # o brotinho


# =====================================================================
# Q: SEMENTE EXPLOSIVA — a cabeça desce e planta na frente; explode quando o oponente chega perto (15)
# BAIXO + E: CIPÓ — planta o cipó na frente (prende 1 s quem pisar)
# =====================================================================
Q_PLANTA, Q_FIM = 14, 30


def _planta(tipo):
    def logica(l, outro, jogo):
        l.vx = 0
        l.fisica(jogo)
        if l.t == Q_PLANTA:
            plantar(l, tipo, l.x + 50 * l.s * l.dir)
        if l.t >= Q_FIM:
            return "fim"
    return logica


semente_explosiva = _planta("bomba")
planta_cipo = _planta("cipo")


# =====================================================================
# R: RAÍZES — estica as raízes pelo chão e nascem 2 PLANTINHAS do lado do adversário que ficam mordendo
#    (1 a cada 0,5 s, por 4 s); quando murcham, viram SEMENTE (armadilha mordedora)
# =====================================================================
R_BROTA, R_FIM = 16, 34
MUDA_VIDA, MUDA_MORDE, MUDA_PERTO, MUDA_NASCE = 240, 30, 34, 12


def raizes(l, outro, jogo):
    t = l.t
    l.vx = 0
    l.fisica(jogo)
    if t == R_BROTA:
        mudas = l.extra.setdefault("mudas", [])
        for lado in (-1, 1):
            mudas.append(dict(x=max(PAREDE_E, min(PAREDE_D, outro.x + lado * 30 * l.s)), t=0, lado=lado,
                              ini=l.x, registro=(l.nome_golpe, getattr(l, "golpe_id", 0))))
        som.tocar("terra", 0.7)
        jogo.tremer(4)
    if t >= R_FIM:
        return "fim"


def mudas_quadro(l, outro, jogo):
    from inazumaneko import acerto
    mudas = l.extra.get("mudas") or []
    for m in list(mudas):
        m["t"] += 1
        if m["t"] > MUDA_NASCE:  # (vai se arrastando atrás dele, devagarinho)
            m["x"] += max(-0.8, min(0.8, (outro.x + m["lado"] * 22 * l.s - m["x"]) * 0.05))
        if (m["t"] > MUDA_NASCE and m["t"] % MUDA_MORDE == 0 and abs(outro.x - m["x"]) < MUDA_PERTO * l.s
                and outro.vida > 0 and outro.inv <= 0 and outro.estado not in ("caido", "voando", "agarrado")
                and outro.y > CHAO - 90 * l.s):
            m["mordeu"] = 6
            acerto(jogo, l, outro, "silv_muda", m["registro"])
        if m.get("mordeu"):
            m["mordeu"] -= 1
        if m["t"] >= MUDA_VIDA:  # MURCHOU: vira semente
            mudas.remove(m)
            plantar(l, "boca", m["x"])


def desenha_mudas(l, tela, alvo_x=None):
    e = l.s / S_REF
    for m in l.extra.get("mudas") or ():
        x, y = m["x"], CHAO
        cresce = min(1.0, m["t"] / MUDA_NASCE)
        if m["t"] < MUDA_NASCE:  # a RAIZ correndo pelo chão até lá
            k = m["t"] / MUDA_NASCE
            pygame.draw.line(tela, PALETA["t"], (m["ini"], CHAO - e), (m["ini"] + (x - m["ini"]) * k, CHAO - e),
                             max(1, int(e * 1.5)))
            continue
        murcha = max(0.0, (m["t"] - (MUDA_VIDA - 40)) / 40)
        alto = max(1, int(6 * cresce * (1 - 0.5 * murcha)))
        for j in range(alto):  # o caulezinho balançando
            _px(tela, PALETA["g"] if murcha < 0.5 else PALETA["T"], x - e / 2 + (e if j > 3 and (l.t // 10) % 2 else 0),
                y - (j + 1) * e, e)
        cy = y - (alto + 2) * e
        abre = 2 if m.get("mordeu") else (1 if (l.t // 10 + m["lado"]) % 2 else 0)
        olha = -m["lado"]  # (olhando pro adversário, que está no meio das duas)
        for i in range(-2, 3):  # a cabecinha roxa (as duas metades + os dentinhos)
            _px(tela, PALETA["p"], x + i * e - e / 2, cy - (abre + 1) * e * 0.5 - e * 0.5, e)
            _px(tela, PALETA["p"], x + i * e - e / 2, cy + abre * e * 0.5, e)
        _px(tela, PALETA["w"], x + olha * e - e / 2, cy, e)
        _px(tela, PALETA["w"], x + olha * 2 * e - e / 2, cy - e * 0.5, e)


# =====================================================================
# SHIFT: FOLHAS-HÉLICE — gira as folhas e voa um pouquinho pra frente; deixa uma SEMENTE onde estava
# =====================================================================
S_VOA, S_FIM = 26, 44


def helice(l, outro, jogo):
    t = l.t
    if t == 1:
        plantar(l, "boca", l.x)
        l.vy = -5.5
        som.tocar("vento", 0.7)
    if t < S_VOA:
        l.vx = 7.5 * l.dir
        l.vy = min(l.vy + 0.35, 1.2)  # (plana com a hélice)
    else:
        l.vx *= 0.85
    l.fisica(jogo)
    if t >= S_FIM or (t > S_VOA and l.no_chao()):
        return "fim"


# =====================================================================
# Z: ULTIMATE — FLORESTA INTEIRA: bate a cabeça no chão, a tela vira floresta e 5 BOCAS GIGANTES saem do chão
#    mordendo (6 cada = 30)
# =====================================================================
U_BATE, U_BOCAS, U_FIM = 16, (30, 40, 50, 60, 72), 100


def ultimate(l, outro, jogo):
    import ult2
    t = l.t
    m = l.memo
    l.vx = 0
    l.inv = 999
    l.fisica(jogo)
    if t == U_BATE:
        som.tocar("terra", 1.0)
        som.tocar("uivo", 0.4)
        ult2.impacto(jogo, 6, 18, 3)
        if hasattr(jogo, "destruicao"):  # (a cabeçada RACHA o chão: CENÁRIO QUE QUEBRA)
            jogo.destruicao().chao(l.x + l.dir * 40 * l.s, 1.0, jogo.t_total)
        m["pegou"] = ult2.pode_pegar(outro, 160)
        m["alvo_x"] = outro.x
        if m["pegou"]:
            ult2.pega(outro)
    if m.get("pegou"):
        for i, tb in enumerate(U_BOCAS):
            if t == tb:  # uma BOCA GIGANTE sai do chão e morde
                ultimo = i == len(U_BOCAS) - 1
                ult2.bate(l, outro, jogo, 6, "silv_ultimate_hit", ultimo=ultimo, forte=ultimo)
                outro.y = CHAO - (10 + i * 12) * outro.s  # (vai sendo levantado de mordida em mordida)
                som.tocar("lingua", 0.8)
        if t == U_BOCAS[-1] + 2:
            ult2.solta(outro, l.dir * 6, -8)
    if t >= U_FIM:
        l.inv = 0
        return "fim"


def ultimate_efeito(l, tela):
    """A FLORESTA tomando a tela (troncos e copas escuras nas bordas) e as BOCAS GIGANTES saindo do chão."""
    t = l.t
    if t < U_BATE:
        return
    w, h = tela.get_size()
    k = min(1.0, (t - U_BATE) / 12) * (1 if t < U_FIM - 12 else max(0.0, (U_FIM - t) / 12))
    camada = pygame.Surface((w, h), pygame.SRCALPHA)
    rnd = random.Random(5)
    for i in range(9):  # os TRONCOS nas bordas
        x = rnd.uniform(0, 170) if i % 2 else rnd.uniform(w - 170, w)
        larg = rnd.uniform(26, 60)
        pygame.draw.rect(camada, (26, 40, 22, int(230 * k)), (x - larg / 2, 0, larg, h))
        pygame.draw.rect(camada, (44, 64, 32, int(230 * k)), (x - larg / 2, 0, larg * 0.3, h))
    for i in range(26):  # as copas (folhas em cima)
        cx, cy, r = rnd.uniform(0, w), rnd.uniform(-20, 70), rnd.uniform(30, 70)
        pygame.draw.circle(camada, (30 + i % 3 * 10, 70 + i % 4 * 12, 30, int(220 * k)), (int(cx), int(cy)), int(r))
    tela.blit(camada, (0, 0))
    e = l.s / S_REF
    bx0 = l.memo.get("alvo_x", l.x + l.dir * 140 * l.s)
    for i, tb in enumerate(U_BOCAS):  # as BOCAS GIGANTES (pixel grande)
        u = t - (tb - 8)
        if 0 <= u < 22:
            alto = min(1.0, u / 8) * (1 if u < 14 else max(0.0, (22 - u) / 8))
            abre = 1.0 if u < 8 else max(0.0, 1 - (u - 8) / 3)
            _boca_gigante(tela, bx0 + (i - 2) * 9 * e, CHAO, e * 1.6, alto, abre)


def _boca_gigante(tela, x, chao, e, alto, abre):
    """Uma boca de planta carnívora ENORME saindo do chão (aberta pra cima), em pixel."""
    h = int(36 * alto)
    if h <= 2:
        return
    sup = pygame.Surface((26, 44), pygame.SRCALPHA)
    pygame.draw.rect(sup, PALETA["k"], (9, 44 - h, 8, h))  # o caule
    pygame.draw.rect(sup, PALETA["g"], (10, 44 - h, 6, h))
    topo = 44 - h
    ang = int(abre * 8)
    pygame.draw.ellipse(sup, PALETA["k"], (1, topo - 11 - ang, 24, 13))  # a metade de cima (abrindo)
    pygame.draw.ellipse(sup, PALETA["p"], (2, topo - 10 - ang, 22, 11))
    pygame.draw.ellipse(sup, PALETA["k"], (1, topo - 3, 24, 11))  # a de baixo
    pygame.draw.ellipse(sup, PALETA["p"], (2, topo - 2, 22, 9))
    if ang > 1:
        pygame.draw.rect(sup, PALETA["q"], (4, topo - 3 - ang, 18, ang + 2))
    for i in range(4, 22, 3):
        sup.set_at((i, topo - 3 - ang), PALETA["w"])
        sup.set_at((i + 1, topo - 1), PALETA["w"])
    img = pygame.transform.scale(sup, (int(26 * e), int(44 * e)))
    tela.blit(img, (int(x - 13 * e), int(chao - 44 * e)))


# =====================================================================
# Z2: 2ª ULTIMATE — CHUVA DE SEMENTES: sementes caem do céu no mapa inteiro e explodem em sequência (8 x 5 = 40)
# =====================================================================
C_CHAMA, C_CHUVA, C_FIM = 20, (40, 50, 58, 66, 74, 82, 90, 100), 130


def chuva(l, outro, jogo):
    import ult2
    t = l.t
    m = l.memo
    ult2.tela_toda(l)
    l.vx = 0
    l.inv = 999
    l.fisica(jogo)
    if t < C_CHAMA:
        ult2.camera(jogo, 1.3, l.x, l.y - 80 * l.s)
        l.sobrepor = dict(POSES_SILVANUS["s_ergue"])
    else:
        l.sobrepor = {}
    if t == C_CHAMA:
        som.tocar("vento", 0.8)
        m["pegou"] = ult2.pode_pegar(outro, 200)
        if m["pegou"]:
            ult2.pega(outro)
    if m.get("pegou"):
        for i, tc in enumerate(C_CHUVA):
            if t == tc:
                ultimo = i == len(C_CHUVA) - 1
                ult2.bate(l, outro, jogo, 5, "silv_chuva", ultimo=ultimo, forte=ultimo)
                som.tocar("explosao", 0.5 + 0.05 * i)
                jogo.tremer(6 + i)
        if t == C_CHUVA[-1] + 2:
            ult2.solta(outro, l.dir * 7, -9)
            ult2.impacto(jogo, 10, 18, 4)
    if t >= C_FIM:
        l.inv = 0
        l.sobrepor = {}
        return "fim"


def chuva_efeito(l, tela):
    """As SEMENTES caindo do céu (o mapa inteiro) e as explosões de terra e folhas (em pixel)."""
    t = l.t
    e = l.s / S_REF * 1.5
    rnd = random.Random(11)
    for i in range(40):
        x0 = rnd.uniform(0, LARGURA)
        t0 = C_CHAMA + rnd.uniform(0, 80)
        u = t - t0
        if 0 <= u < 30:
            y = -20 + u * 18
            if y < CHAO:
                for dx, dy, c in ((0, 0, "t"), (1, 0, "T"), (0, 1, "t"), (1, 1, "t")):
                    _px(tela, PALETA[c], x0 + dx * e, y + dy * e, e)
                _px(tela, PALETA["y"], x0, y - e, e)
            else:
                v = (y - CHAO) / 18
                if v < 6:  # a explosão
                    r = (2 + v * 2) * e
                    for k in range(8):
                        a = k / 8 * math.tau
                        _px(tela, PALETA["y"] if k % 2 else PALETA["T"], x0 + math.cos(a) * r,
                            CHAO - 3 * e + math.sin(a) * r * 0.6, e)


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


_registra("silv_cospe", ini=E_COSPE, ativo=1, rec=E_FIM - E_COSPE, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=cospe, ia="longe", quadros=[(0, "parado"), (6, "s_puxa"), (E_COSPE, "s_cospe"),
                                             (E_COSPE + 8, "s_cospe"), (E_FIM, "parado")])
_registra("silv_cipo_planta", ini=Q_PLANTA, ativo=1, rec=Q_FIM - Q_PLANTA, dano=0, hit=0, defe=0, emp=0,
          nivel="medio", logica=planta_cipo, ia="perto",
          quadros=[(0, "parado"), (Q_PLANTA, "s_planta"), (Q_PLANTA + 6, "s_planta"), (Q_FIM, "parado")])
_registra("silv_explosiva", ini=Q_PLANTA, ativo=1, rec=Q_FIM - Q_PLANTA, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=semente_explosiva, ia="medio",
          quadros=[(0, "parado"), (Q_PLANTA, "s_planta"), (Q_PLANTA + 6, "s_planta"), (Q_FIM, "parado")])
_registra("silv_raizes", ini=R_BROTA, ativo=1, rec=R_FIM - R_BROTA, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=raizes, ia="medio",
          quadros=[(0, "parado"), (8, "s_raizes"), (R_FIM - 6, "s_raizes"), (R_FIM, "parado")])
_registra("silv_helice", ini=1, ativo=1, rec=S_FIM - 2, dano=0, hit=0, defe=0, emp=0, nivel="medio", logica=helice,
          ia="medio", quadros=[(0, "s_helice"), (S_FIM, "s_helice")])
_registra("silv_ultimate", ini=U_BATE, ativo=1, rec=U_FIM - U_BATE, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          ultimate=True, imbloqueavel=True, logica=ultimate, efeito=ultimate_efeito, ia="ultimate", ia_alcance=220,
          quadros=[(0, "parado"), (U_BATE - 6, "s_ergue"), (U_BATE, "s_bate"), (U_BATE + 20, "s_bate"),
                   (U_BATE + 34, "s_ergue"), (U_FIM, "parado")])
GOLPES["silv_ultimate"]["total"] = 9999
GOLPES["silv_semente"] = dict(dano=4, hit=12, defe=6, emp=2, nivel="medio", especial=True)
GOLPES["silv_boca"] = dict(dano=8, hit=16, defe=8, emp=0, nivel="baixo", especial=True, imbloqueavel=True)
GOLPES["silv_cipo"] = dict(dano=3, hit=16, defe=6, emp=0, nivel="baixo", especial=True, imbloqueavel=True)
GOLPES["silv_bomba"] = dict(dano=15, hit=24, defe=12, emp=6, nivel="medio", especial=True, derruba=True, voo=(5, 9))
GOLPES["silv_muda"] = dict(dano=1, hit=8, defe=4, emp=0, nivel="baixo", especial=True)
GOLPES["silv_ultimate_hit"] = dict(dano=6, hit=30, defe=0, emp=0, nivel="medio", especial=True, ultimate=True)
GOLPES["silv_chuva"] = dict(dano=5, hit=30, defe=12, emp=4, nivel="medio", especial=True, ultimate=True,
                            ultimate2=True)

GOLPES_SILVANUS = {"E": "silv_cospe", "Q": "silv_explosiva", "R": "silv_raizes", "SHIFT": "silv_helice",
                   "Z": "silv_ultimate"}
NOMES = {"E": "cospe semente (armadilha)", "Q": "semente explosiva", "R": "raízes (2 plantinhas)",
         "SHIFT": "folhas-hélice", "Z": "FLORESTA INTEIRA", "Z2": "CHUVA DE SEMENTES"}


# =====================================================================
# ENGANADOR SELVAGEM (passiva): X arma a finta; o próximo ataque é só a ANIMAÇÃO (habilidades.finta cuida da entrada)
# =====================================================================
def tecla_x(l):
    import habilidades as hab
    if "enganador" in hab.ativas(l) and l.extra.get("finta_espera", 0) <= 0:
        l.extra["finta_armada"] = 20
        l.extra["finta_flash"] = 12


def finge(l, outro, jogo):
    """A FINTA: faz o começo do golpe escolhido (a pose de preparar), sem acertar nada."""
    import habilidades as hab
    from golpes import POSES
    nome = l.extra.get("finta_de", "soco")
    g = GOLPES.get(nome, {})
    u = min(1.0, l.t / 10)
    if nome in ("soco", "chute"):
        alvo = l.poses.get(nome) or POSES[nome]
        l.sobrepor = misturar(l.poses["parado"], alvo, 0.45 * u)
    else:
        qs = g.get("quadros") or [(0, "parado")]
        pose = qs[1][1] if len(qs) > 1 else qs[0][1]
        alvo = l.poses.get(pose) or POSES.get(pose) or l.poses["parado"]
        l.sobrepor = misturar(l.poses["parado"], alvo, u)
    l.vx = 0
    l.fisica(jogo)
    if l.t >= hab.FINTA_TEMPO:
        l.sobrepor = {}
        return "fim"


_registra("silv_finta", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", logica=finge,
          especial=False, quadros=[(0, "parado")])
GOLPES["silv_finta"]["total"] = 9999


def todo_quadro(l, jogo):
    outro = outro_de(l, jogo)
    for k in ("finta_armada", "finta_espera", "finta_flash"):
        if l.extra.get(k, 0) > 0:
            l.extra[k] -= 1
    sementes_quadro(l, outro, jogo)
    armadilhas_quadro(l, outro, jogo)
    mudas_quadro(l, outro, jogo)
    x = l.extra  # (tem coisa dele no chão longe dele: a camada de efeitos vai pra TELA TODA)
    x["tela_toda"] = bool(x.get("armadilhas") or x.get("mudas") or x.get("voando"))


def desenhar_sempre(l, tela):
    nuvem_chuva(l, tela)
    for a in armadilhas(l):
        desenha_armadilha(tela, a, l.s, l.t)
    desenha_mudas(l, tela)
    desenha_sementes(l, tela)


# =====================================================================
# ENTRADA (escolha do Gomes): NASCE FEITO PLANTA — a sementinha cai, o chão treme, sai um BROTINHO, ela vai
# CRESCENDO (do tamanho de uma mudinha até o tamanho normal) com a boca fechada feito um botão... e o botão ABRE
# =====================================================================
EN_CAI, EN_BROTO, EN_CRESCE, EN_CRESCEU, EN_FIM = 16, 30, 40, 70, 86


def entrada(l, t, jogo):
    x = l.extra
    if "s_base" not in x:
        x["s_base"] = l.s
    if t < EN_CRESCE:  # (ainda é semente / brotinho: desenhado no entrada_efeito)
        l.esconde = True
        if t == EN_CAI:
            som.tocar("terra", 0.5)
        if EN_CAI < t < EN_BROTO and t % 6 == 0:
            jogo.tremer(3)
        if t == EN_BROTO:
            som.tocar("puf", 0.5)
    elif t < EN_CRESCEU:  # CRESCENDO: de mudinha até o tamanho normal
        l.esconde = False
        k = suave((t - EN_CRESCE) / (EN_CRESCEU - EN_CRESCE))
        l.s = x["s_base"] * (0.18 + 0.82 * k)
        if t % 8 == 0:
            som.tocar("terra", 0.25)
    else:
        l.s = x["s_base"]
        if t == EN_CRESCEU:  # o BOTÃO abre!
            som.tocar("lingua", 0.8)
            jogo.tremer(6)
            for _ in range(12):  # as pétalas/folhinhas voando
                jogo.faiscas.append([l.x + random.uniform(-20, 20), l.y - random.uniform(60, 100) * l.s,
                                     random.uniform(-4, 4), random.uniform(-5, -1), random.randint(20, 36),
                                     random.choice(((240, 150, 200), (124, 200, 92), (214, 255, 120))), 3])
    if t >= EN_FIM - 1:
        l.s = x.pop("s_base", l.s)
    l.t += 1


def entrada_efeito(l, tela, t):
    """A SEMENTINHA caindo, a terra mexida e o BROTINHO saindo do chão (em pixel), antes dela crescer."""
    e = l.extra.get("s_base", l.s) / S_REF
    if t < EN_CAI:
        y = -20 + (CHAO + 20) * suave(t / EN_CAI)
        for dx, dy, c in ((0, 0, "t"), (1, 0, "T"), (0, 1, "t"), (1, 1, "t")):
            _px(tela, PALETA[c], l.x + dx * e, y + dy * e, e)
        _px(tela, PALETA["G"], l.x, y - e, e)
        return
    if t < EN_CRESCE + 6:  # a terra mexida
        for i in range(-5, 6):
            _px(tela, (70, 50, 30), l.x + i * e, CHAO - (e if abs(i) < 3 else 0), e)
    if EN_BROTO <= t < EN_CRESCE:  # o BROTINHO: caule subindo e as duas folhinhas abrindo
        k = (t - EN_BROTO) / (EN_CRESCE - EN_BROTO)
        alto = 1 + int(4 * k)
        for j in range(alto):
            _px(tela, PALETA["g"], l.x, CHAO - (j + 1) * e, e)
        topo = CHAO - (alto + 1) * e
        abre = 1 + int(2 * k)
        for lado in (-1, 1):
            for i in range(1, abre + 1):
                _px(tela, PALETA["G"], l.x + lado * i * e, topo + (e if i == abre else 0), e)
        _px(tela, PALETA["p"], l.x, topo - e, e)  # (o botãozinho roxo já aparecendo)


# =====================================================================
# VITÓRIA (ideia do Gomes): FLORES brotam em volta, ela ENFIA A CABEÇA NA TERRA... e AFUNDA INTEIRA no chão
# (fica só o montinho de terra com um brotinho)
# =====================================================================
V_FLORES, V_ENFIA, V_AFUNDA, V_SUMIU = 6, 34, 56, 110


def vitoria(l, t, jogo):
    l.cortar_chao = t >= V_ENFIA + 4  # (o que fica embaixo do chão não aparece)
    if t == V_ENFIA + 8:
        som.tocar("terra", 0.8)
        jogo.tremer(6)
    if V_AFUNDA <= t:  # AFUNDA INTEIRA na terra, aos tranquinhos
        k = suave(min(1.0, (t - V_AFUNDA) / (V_SUMIU - V_AFUNDA)))
        tranco = 0.05 * ((t // 6) % 2) if k < 1 else 0.0
        l.extra["afunda"] = min(1.0, k + tranco) * 170 * l.s  # (só o DESENHO afunda: a física deixa ele no chão)
        if t % 10 == 0 and t < V_SUMIU:
            som.tocar("terra", 0.4)
            jogo.tremer(3)
    if t >= V_SUMIU:
        l.esconde = True
    if t == 0:
        l.extra["afunda"] = 0


def vitoria_atras(l, tela, t=0):
    """O MONTINHO de terra onde ela entrou (e um brotinho roxo saindo dele no final)."""
    if t < V_AFUNDA:
        return
    e = l.s / S_REF * 1.5
    k = min(1.0, (t - V_AFUNDA) / 30)
    larg = int(10 * k)
    for i in range(-larg, larg + 1):
        alto = max(1, int((1 - abs(i) / (larg + 1)) * 3 * k))
        for j in range(alto):
            _px(tela, (124, 92, 58) if j else (96, 70, 44), l.x + i * e, CHAO - (j + 1) * e, e)
    if t > V_SUMIU + 10:
        _px(tela, PALETA["g"], l.x, CHAO - 4 * e, e)
        _px(tela, PALETA["G"], l.x - e, CHAO - 5 * e, e)
        _px(tela, PALETA["G"], l.x + e, CHAO - 5 * e, e)
        _px(tela, PALETA["p"], l.x, CHAO - 6 * e, e)


def vitoria_efeito(l, tela, t):
    """As FLORES brotando em volta dela (rosa e amarela, em pixel)."""
    e = l.s / S_REF
    rnd = random.Random(3)
    for i in range(10):
        x = l.x + rnd.uniform(-110, 110) * l.s
        t0 = V_FLORES + i * 3
        k = min(1.0, max(0.0, (t - t0) / 10))
        if k <= 0:
            continue
        alto = int(1 + 3 * k)
        for j in range(alto):
            _px(tela, PALETA["g"], x, CHAO - (j + 1) * e, e)
        if k >= 1:
            cor = PALETA["f"] if i % 2 else (250, 220, 90)
            cy = CHAO - (alto + 1) * e
            for ox, oy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                _px(tela, cor, x + ox * e, cy + oy * e, e)
            _px(tela, PALETA["F"], x, cy, e)


# =====================================================================
# PROVOCAÇÃO (escolha do Gomes): REGA A SI MESMA — uma nuvenzinha aparece em cima e chove nela; ela balança feliz
# =====================================================================
PROVOCACAO_QUADROS = [(0, "parado"), (70, "parado")]


def nuvem_chuva(l, tela):
    """A NUVENZINHA chovendo em cima da cabeça dela (pixel), enquanto provoca."""
    if not (l.estado == "ataque" and l.nome_golpe == "provocar"):
        return
    t = l.t
    e = l.s / S_REF * 1.8
    k = min(1.0, t / 8) * (1 if t < 60 else max(0.0, (70 - t) / 10))
    if k <= 0:
        return
    p, desloca, _, _ = animacao(l, l.pose_vista or l.pose_atual())
    cx, cy = l.x + (p["cb"][0] + desloca[0]) * l.s * l.lado(), l.y - (p["cb"][1] + desloca[1]) * l.s
    cy -= 22 * e
    cor, sombra = (236, 240, 250), (190, 198, 216)
    for ox, oy, r in ((-4, 0, 3), (0, -2, 4), (4, 0, 3), (0, 1, 3)):  # a nuvem (bolinhas em pixel)
        rr = int(r * e * k)
        if rr > 0:
            pygame.draw.circle(tela, sombra, (int(cx + ox * e), int(cy + oy * e + e)), rr)
            pygame.draw.circle(tela, cor, (int(cx + ox * e), int(cy + oy * e)), rr)
    if t > 10:
        for i in range(6):  # os PINGOS caindo
            u = (t * 2 + i * 7) % 18
            _px(tela, (120, 180, 255), cx + (i - 2.5) * 1.6 * e, cy + 3 * e + u * e, e * 0.6)
