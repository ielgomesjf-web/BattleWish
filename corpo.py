"""Desenho de corpo com proporção de gente: membros que afinam e engrossam, luz e sombra, contorno fino.

Tudo parte do esqueleto da pose (os mesmos pontos de sempre) e é desenhado em volta dele.
"""
import math

import pygame

from config import *  # noqa: F401,F403

LUZ = (-0.45, -0.89)  # a luz vem de cima, um pouco da esquerda
BORDA = 1.6           # grossura do contorno (fica mais fino na pixel art)


def clarear(c, k):
    return tuple(min(255, int(v + (255 - v) * k)) for v in c)


def escurecer(c, k):
    return tuple(max(0, int(v * (1 - k))) for v in c)


def _normais(pts):
    """Uma normal pra cada ponto da corrente (média dos pedaços em volta)."""
    ns = []
    for i in range(len(pts)):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        ns.append((-dy / d, dx / d))
    # vira todas pro lado da luz
    soma = sum(nx * LUZ[0] + ny * LUZ[1] for nx, ny in ns)
    if soma < 0:
        ns = [(-nx, -ny) for nx, ny in ns]
    return ns


def _faixa(pts, ns, ws, de, ate):
    """Polígono entre dois deslocamentos (em 'larguras') ao longo da corrente."""
    lado1 = [(p[0] + n[0] * w * de, p[1] + n[1] * w * de) for p, n, w in zip(pts, ns, ws)]
    lado2 = [(p[0] + n[0] * w * ate, p[1] + n[1] * w * ate) for p, n, w in zip(pts, ns, ws)]
    return lado1 + lado2[::-1]


def membro(tela, corrente, cor, cont, borda=None, brilho=0.4, sombra=0.32, pontas=True):
    """corrente = [((x, y), meia_largura), ...]. Desenha um pedaço de corpo arredondado."""
    if borda is None:
        borda = BORDA
    pts = [p for p, _ in corrente]
    ws = [max(0.8, w) for _, w in corrente]
    if len(pts) < 2 or all(math.dist(pts[0], p) < 0.5 for p in pts):
        pygame.draw.circle(tela, cont, (int(pts[0][0]), int(pts[0][1])), int(ws[0] + borda))
        pygame.draw.circle(tela, cor, (int(pts[0][0]), int(pts[0][1])), int(ws[0]))
        return
    ns = _normais(pts)
    contorno = [w + borda for w in ws]
    pygame.draw.polygon(tela, cont, _faixa(pts, ns, contorno, 1, -1))
    if pontas:
        for i in (0, -1):
            pygame.draw.circle(tela, cont, (int(pts[i][0]), int(pts[i][1])), int(contorno[i]))
            pygame.draw.circle(tela, cor, (int(pts[i][0]), int(pts[i][1])), max(1, int(ws[i])))
    pygame.draw.polygon(tela, cor, _faixa(pts, ns, ws, 1, -1))
    if sombra:
        pygame.draw.polygon(tela, escurecer(cor, sombra), _faixa(pts, ns, ws, -0.35, -1))
    if brilho:
        pygame.draw.polygon(tela, clarear(cor, brilho), _faixa(pts, ns, ws, 0.25, 0.7))


def eixos(a, b):
    """Direção de a pra b e a perpendicular."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy) or 1
    return (dx / d, dy / d), (-dy / d, dx / d)


def mais(p, v, k):
    return (p[0] + v[0] * k, p[1] + v[1] * k)


def frente_do_pe(joelho, pe, lado):
    """Pra onde o pé aponta (perpendicular à canela, pra frente do lutador)."""
    (ux, uy), _ = eixos(joelho, pe)
    return (uy * lado, -ux * lado), (-ux, -uy)


def cabeca_eixos(pc, cb, lado):
    """u = pra cima da cabeça, f = pra onde o rosto olha."""
    (ux, uy), _ = eixos(pc, cb)
    return (ux, uy), (-uy * lado, ux * lado)


# =====================================================================
# Boneco de treino (manequim articulado)
# =====================================================================
def desenhar_manequim(l, tela, p, branco):
    s = l.s
    d = l.lado()
    base = (240, 240, 240) if branco else (getattr(l, "disfarce", None) or l.f)["cor"]
    cor_f = base
    cor_t = escurecer(base, 0.28)
    junta = escurecer(base, 0.45) if not branco else (200, 200, 200)

    def P(k):
        return l.ponto(p, k)

    def articulacao(pt, r, c):
        pygame.draw.circle(tela, escurecer(c, 0.5), (int(pt[0]), int(pt[1])), int(r + 1.5))
        pygame.draw.circle(tela, c, (int(pt[0]), int(pt[1])), int(r))
        pygame.draw.circle(tela, clarear(c, 0.4), (int(pt[0] - r * 0.3), int(pt[1] - r * 0.35)), max(1, int(r * 0.35)))

    def perna(pe, joelho, cor):
        cont = escurecer(cor, 0.55)
        q, j, e = P("qd"), P(joelho), P(pe)
        membro(tela, [(q, 7.5 * s), (mais(q, eixos(q, j)[0], math.dist(q, j) * 0.45), 6.6 * s), (j, 4.6 * s)], cor, cont)
        dirc, _ = eixos(j, e)
        meio = mais(j, dirc, math.dist(j, e) * 0.3)
        membro(tela, [(j, 4.4 * s), (meio, 5 * s), (e, 2.8 * s)], cor, cont)
        f, cima = frente_do_pe(j, e, d)
        calc = [(mais(mais(e, f, -3 * s), cima, 1 * s), 3 * s), (mais(e, f, 6 * s), 3.2 * s), (mais(e, f, 11 * s), 2.2 * s)]
        membro(tela, calc, escurecer(cor, 0.15), cont)
        articulacao(j, 3.6 * s, junta)
        articulacao(e, 2.4 * s, junta)

    def braco(cot, mao, cor):
        cont = escurecer(cor, 0.55)
        o, c, m = P("pc"), P(cot), P(mao)
        membro(tela, [(o, 5 * s), (mais(o, eixos(o, c)[0], math.dist(o, c) * 0.4), 5.2 * s), (c, 3.6 * s)], cor, cont)
        membro(tela, [(c, 3.5 * s), (mais(c, eixos(c, m)[0], math.dist(c, m) * 0.35), 4 * s), (m, 2.6 * s)], cor, cont)
        dirm, _ = eixos(c, m)
        membro(tela, [(m, 3.4 * s), (mais(m, dirm, 4 * s), 3.2 * s)], cor, cont)  # punho fechado
        articulacao(c, 3 * s, junta)

    longe, perto = (("cf", "mf", "pf", "jf"), ("ct", "mt", "pt", "jt")) if l.vira else \
        (("ct", "mt", "pt", "jt"), ("cf", "mf", "pf", "jf"))
    braco(longe[0], longe[1], cor_t)
    perna(longe[2], longe[3], cor_t)
    # tronco: quadril, cintura fina, peito largo
    q, c = P("qd"), P("pc")
    v, _ = eixos(q, c)
    comp = math.dist(q, c)
    cont = escurecer(cor_f, 0.55)
    membro(tela, [(mais(q, v, -2 * s), 10 * s), (mais(q, v, comp * 0.42), 8.4 * s),
                  (mais(q, v, comp * 0.78), 11.5 * s), (mais(q, v, comp * 1.02), 10 * s)], cor_f, cont)
    perna(perto[2], perto[3], cor_f)
    articulacao(q, 5 * s, junta)
    # pescoço e cabeça (manequim não tem rosto)
    cb = P("cb")
    u, f = cabeca_eixos(c, cb, d)
    membro(tela, [(mais(c, u, 1 * s), 3.4 * s), (mais(cb, u, -6 * s), 3 * s)], escurecer(cor_f, 0.1), cont)
    membro(tela, [(mais(mais(cb, u, -6.5 * s), f, 1.5 * s), 4.8 * s), (mais(cb, u, -2.5 * s), 7.4 * s),
                  (mais(cb, u, 2 * s), 8 * s), (mais(mais(cb, u, 4.5 * s), f, -1 * s), 7.2 * s)], cor_f, cont)
    braco(perto[0], perto[1], cor_f)
    articulacao(c, 4 * s, junta)
