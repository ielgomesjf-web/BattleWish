"""RIBBAT: o personagem SECRETO (do jogo de plataforma do Gomes, "Ribbat e o Pergaminho Perdido").

Só aparece depois do código ULTRA-MEGA-FROG (na tela de CÓDIGOS). Não é jogável no online.
Visual: o SPRITE DE VERDADE do jogo dele, pequenininho (uns 54 px): soco e chute em pé passam por cima dele. Quebrado!
  E      LINGUADA (35) — a mesma do jogo dele
  SHIFT  INVESTIDA (50) — fica invulnerável enquanto vai
  Z      ULTIMATE: chama TODOS OS CHEFÕES do jogo dele (Viúva Negra, Besouro-rinoceronte, Formiga Rainha,
         Gato Preto e Águia-careca). HIT KILL.
"""
import math
import random

import pygame

import som
from config import *  # noqa: F401,F403
from golpes import GOLPES, misturar, suave
from max10 import brilho, fumaca
from rib import POSES_RIB  # (as poses do Rib, encolhidas, servem pros efeitos e pra caixa de acerto)

CODIGO = "ULTRA-MEGA-FROG"


# =====================================================================
# O SPRITE DE VERDADE do jogo do Ribbat (copiado de Ribbat/desenho.py: o sapinho pequenininho)
# =====================================================================
ESTILO = dict(pele=(112, 186, 80), escura=(62, 124, 54), contorno=(30, 70, 34), barriga=(240, 232, 178),
              manchas=(78, 146, 60), listra=(176, 218, 116), iris=(236, 184, 52))
LENCO = (214, 56, 56)
PRETO_S, BRANCO_S = (20, 20, 24), (255, 255, 255)
ONDAS = (0.0, 1.6, 0.0, -1.6)
TAMANHO = 0.84   # quanto do "tam" vira escala do sprite (o Ribbat fica com uns 54 px de altura: PEQUENININHO)
_cache = {}


def _sapo_bruto(pose, e, onda):
    """Desenha o sapo virado pra DIREITA. Caixa de 80x52 unidades, chão em y=46. (igual ao jogo dele)"""
    c = ESTILO
    s = pygame.Surface((max(1, int(80 * e)), max(1, int(52 * e))), pygame.SRCALPHA)
    oy = -2 if pose == "anda" else 0

    def P(x, y):
        return ((x + 16) * e, (y + 4 + oy) * e)

    def circ(x, y, r, cor):
        pygame.draw.circle(s, cor, P(x, y), max(1, r * e))

    def eli(x, y, w, h, cor):
        px, py = P(x, y)
        pygame.draw.ellipse(s, cor, pygame.Rect(px, py, w * e, h * e))

    def pol(pts, cor):
        pygame.draw.polygon(s, cor, [P(*q) for q in pts])

    def linha(pts, cor, larg):
        pygame.draw.lines(s, cor, False, [P(*q) for q in pts], max(1, int(larg * e)))

    def osso(a, b, r1, r2, cor):
        (x1, y1), (x2, y2) = a, b
        ang = math.atan2(y2 - y1, x2 - x1)
        nx, ny = -math.sin(ang), math.cos(ang)
        pol([(x1 + nx * r1, y1 + ny * r1), (x2 + nx * r2, y2 + ny * r2),
             (x2 - nx * r2, y2 - ny * r2), (x1 - nx * r1, y1 - ny * r1)], cor)
        circ(x1, y1, r1, cor)
        circ(x2, y2, r2, cor)

    pele, esc = c["pele"], c["escura"]
    if pose == "parado":
        osso((10, 40), (24, 43.5), 3.6, 3.0, esc)
        osso((22, 44), (36, 45), 2.6, 2.0, esc)
        circ(37, 45, 2.0, esc)
        circ(34.5, 46.2, 1.7, esc)
    elif pose == "anda":
        osso((8, 37), (22, 40.5), 3.6, 3.0, esc)
        osso((20, 41), (33, 42.5), 2.6, 2.0, esc)
        circ(34, 42.5, 2.0, esc)
    elif pose == "pulo":
        osso((14, 34), (2, 39), 6.5, 4.0, pele)
        osso((2, 39), (-8, 43), 3.4, 2.6, esc)
        osso((-8, 43), (-18, 45), 2.4, 1.8, esc)
        circ(-19, 45, 1.9, esc)
    elif pose == "queda":
        osso((16, 36), (12, 43), 6.5, 4.0, pele)
        osso((12, 43), (20, 46.5), 3.2, 2.6, esc)
        osso((20, 46.5), (30, 47), 2.4, 1.8, esc)
    elif pose == "investida":
        osso((12, 32), (-2, 33), 6.0, 4.0, pele)
        osso((-2, 33), (-14, 34), 3.2, 2.6, esc)
        osso((-14, 34), (-24, 34), 2.4, 1.8, esc)
    eli(6, 20, 32, 24, pele)
    eli(26, 12, 30, 23, pele)
    pol([(16, 20), (34, 12), (46, 15), (42, 36), (16, 43)], pele)
    circ(42, 14, 8.5, pele)
    eli(21, 30, 27, 13.5, c["barriga"])
    linha([(9, 25), (19, 18.5), (31, 13.5), (37, 10.5)], c["listra"], 1.7)
    for mx, my, mr in ((16, 27, 2.6), (24, 22, 2.0), (11, 33, 2.0), (30, 18.5, 1.5), (20, 33, 1.7)):
        circ(mx, my, mr, c["manchas"])
    if pose in ("parado", "anda"):
        dy = -3 if pose == "anda" else 0
        eli(3, 27 + dy, 25, 15, pele)
        linha([(9, 30 + dy), (12, 40 + dy)], esc, 1.6)
        linha([(16, 29 + dy), (19, 40 + dy)], esc, 1.6)
    if pose == "parado":
        osso((42, 32), (44, 43), 3.0, 2.4, pele)
        circ(46.5, 44.6, 1.9, esc)
        circ(43.5, 45.2, 1.9, esc)
    elif pose == "anda":
        osso((42, 31), (48, 40), 3.0, 2.4, pele)
        circ(50, 41, 1.9, esc)
    elif pose == "pulo":
        osso((41, 32), (35, 39), 2.8, 2.2, pele)
    elif pose == "queda":
        osso((43, 32), (50, 41), 3.0, 2.4, pele)
        circ(51.5, 42.5, 2.0, esc)
    elif pose == "investida":
        osso((40, 33), (30, 38), 2.6, 2.1, pele)
    pol([(31, 19), (22, 15.5 + onda), (21.5, 20 + onda), (30, 22)], LENCO)  # o lenço da Vila dos Sapos
    pol([(31, 21), (24, 24 + onda * 0.6), (25, 27.5 + onda * 0.6), (32, 23.5)], LENCO)
    osso((31.5, 19), (36, 32), 2.2, 2.2, LENCO)
    pol([(35, 27), (44, 33), (37, 37)], LENCO)
    linha([(35, 27.5), (43, 32.8)], (170, 36, 40), 0.9)
    circ(31, 20.5, 2.6, (190, 44, 46))
    circ(52.5, 18.5, 0.9, c["contorno"])
    linha([(55.5, 24), (51, 26.4), (44, 27.2), (38.5, 25.6)], c["contorno"], 1.3)
    circ(48, 27.8, 2.4, (238, 156, 136))
    if pose == "tonto":
        linha([(39, 10), (47, 18)], c["contorno"], 1.6)
        linha([(47, 10), (39, 18)], c["contorno"], 1.6)
    else:
        circ(43, 13.5, 6.2, c["iris"])
        circ(44, 13.6, 4.3, PRETO_S)
        circ(45.6, 11.6, 1.6, BRANCO_S)
        circ(42.3, 15.6, 0.8, BRANCO_S)
        linha([(35.5, 10), (39, 6.6), (45, 6), (50, 9)], c["escura"], 1.3)
    return s


def sprite_sapo(pose, d, escala, onda, branco=False):
    chave = (pose, d, round(escala, 3), onda, branco)
    img = _cache.get(chave)
    if img is None:
        ss = 3
        bruto = _sapo_bruto(pose, escala * ss, ONDAS[onda % 4])
        cont = pygame.mask.from_surface(bruto).to_surface(setcolor=ESTILO["contorno"], unsetcolor=(0, 0, 0, 0))
        final = pygame.Surface(bruto.get_size(), pygame.SRCALPHA)
        k = max(1, int(1.3 * escala * ss))
        for dx, dy in ((-k, 0), (k, 0), (0, -k), (0, k), (-k, -k), (k, k), (-k, k), (k, -k)):
            final.blit(cont, (dx, dy))
        final.blit(bruto, (0, 0))
        w, h = bruto.get_size()
        img = pygame.transform.smoothscale(final, (max(1, w // ss), max(1, h // ss)))
        if branco:  # piscando quando apanha
            img.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
        if d < 0:
            img = pygame.transform.flip(img, True, False)
        if len(_cache) < 400:
            _cache[chave] = img
    return img


def no_mundo(l, ux, uy):
    """Um ponto do sprite (unidades do jogo do Ribbat) levado pra tela."""
    e = l.s * TAMANHO
    return l.x + l.lado() * (ux - 30) * e, l.y - (46 - uy) * e


def pose_do_sapo(l):
    est = l.estado
    if est == "ataque" and l.nome_golpe == "ribbat_investida" and I_INI - 2 <= l.t < I_FIM:
        return "investida"
    if est in ("pulando", "voando") or not l.no_chao():
        return "pulo" if l.vy < 0 else "queda"
    if est == "tonto":
        return "tonto"
    if est == "andando":
        return "anda" if int(l.passo * 6) % 2 else "parado"
    return "parado"


def desenhar_ribbat(l, tela, p, branco):
    e = l.s * TAMANHO
    d = l.lado()
    img = sprite_sapo(pose_do_sapo(l), d, e, (l.t // 6) % 4, branco)
    if l.angulo:
        img = pygame.transform.rotate(img, -math.degrees(l.angulo * d))
    w, h = img.get_size()
    if l.angulo:
        tela.blit(img, img.get_rect(center=(int(l.x), int(l.y - 24 * e))))
    else:
        fx = (46 / 80 if d > 0 else 34 / 80) * w
        tela.blit(img, (l.x - fx, l.y - 50 / 52 * h))
        if l.f.get("chapeu") and not branco:  # roupa secreta: o chapéu do jogo dele (girando, o chapéu some)
            import chapeus_ribbat
            chapeus_ribbat.desenhar(tela, l.f["chapeu"], l.x, l.y, d, e)


def figura_ribbat(q, P, s, d, cor, escura, cont, branco, t):
    pass


def _encolhe(pose):
    """As poses (que só servem pros efeitos e pra caixa) do tamanho do sapinho."""
    return {k: (x * 0.55, y * 0.36) for k, (x, y) in pose.items()}


from golpes import POSES as _POSES_BASE  # noqa: E402
POSES_RIBBAT = {nome: _encolhe(p) for nome, p in {**_POSES_BASE, **POSES_RIB}.items()}


# =====================================================================
# E: LINGUADA (35) — sai da boca dele, lá embaixo
# =====================================================================
from rib import L_ALCANCE, L_ESTICA, L_FIM, L_SAI, L_VOLTA  # noqa: E402


def boca(l):
    return no_mundo(l, 55.5, 24)


def linguada(l, outro, jogo):
    t = l.t
    if t == L_SAI:
        som.tocar("lingua")
    if L_SAI <= t < L_FIM:
        if t < L_ESTICA:
            ext = suave((t - L_SAI) / (L_ESTICA - L_SAI))
        elif t < L_VOLTA:
            ext = 1
        else:
            ext = 1 - suave((t - L_VOLTA) / (L_FIM - 8 - L_VOLTA))
        ext = max(0, ext)
        l.memo["ext"] = ext
        bx, by = boca(l)
        alcance = 8 + L_ALCANCE * ext
        l.memo["caixa"] = (8, (l.y - by) / l.s - 9, alcance + 8, (l.y - by) / l.s + 9)
    else:
        l.memo["ext"] = 0
    l.vx = 0
    l.fisica(jogo)
    if t >= L_FIM:
        return "fim"


def linguada_efeito(l, tela):
    ext = l.memo.get("ext", 0)
    bx, by = boca(l)
    if ext <= 0:
        if 6 < l.t < L_SAI:  # bochecha inflando
            r = int((2 + 3 * (l.t - 6) / (L_SAI - 6)) * l.s)
            pygame.draw.circle(tela, (238, 156, 136), (int(bx - 6 * l.dir), int(by + 4)), r)
        return
    fx = bx + (L_ALCANCE * ext) * l.s * l.dir
    meio_y = by + math.sin(l.t * 0.8) * 3
    pts = [(bx, by), ((bx + fx) / 2, meio_y), (fx, by)]
    pygame.draw.lines(tela, (120, 30, 50), False, pts, int(8 * l.s))
    pygame.draw.lines(tela, (235, 110, 140), False, pts, int(5 * l.s))
    pygame.draw.circle(tela, (235, 110, 140), (int(fx), int(by)), int(6 * l.s))


# =====================================================================
# SHIFT: INVESTIDA (50)
# =====================================================================
I_INI, I_FIM = 6, 24


def investida(l, outro, jogo):
    t = l.t
    m = l.memo
    if l.acertou:
        m["bateu"] = True
    if I_INI <= t < I_FIM and "bateu" not in m:
        l.vx = 14 * l.dir
        l.inv = 2  # invulnerável enquanto vai (igual no jogo dele)
        if t % 2 == 0:
            fumaca(jogo, l.x - 16 * l.dir, CHAO - 4, 1, (150, 130, 100), 1, -0.4)
    else:
        l.vx *= 0.7
    l.fisica(jogo)
    if t >= I_FIM + 14:
        return "fim"


# =====================================================================
# Z: ULTIMATE — OS CHEFÕES DO RIBBAT. HIT KILL.
# =====================================================================
U_CHAMA, U_CHEFE = 20, 46
CHEFES = ("viuva", "besouro", "rainha", "gato", "aguia")
U_FIM = U_CHAMA + len(CHEFES) * U_CHEFE + 40


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.fisica(jogo)
    if t == 1:  # prende o outro: ninguém escapa dos chefões
        outro.mudar("agarrado")
        outro.golpe = None
        outro.y, outro.vx, outro.vy = CHAO, 0, 0
        outro.sobrepor = dict(outro.poses["golpeado"])
        m["alvo"] = (outro.x, outro.y)
        l.inv = 999
        som.tocar("lingua")
    for i in range(len(CHEFES)):
        bate = U_CHAMA + i * U_CHEFE + U_CHEFE // 2
        if t == U_CHAMA + i * U_CHEFE:
            som.tocar("puf", 0.6)
        if t == bate:  # o chefe acertou
            outro.tremor_hit = 10
            jogo.tremer(10)
            jogo.faisca(outro.x, outro.y - 60 * outro.s, False, True)
            som.tocar("explosao", 0.7)
    if t == U_CHAMA + len(CHEFES) * U_CHEFE:  # HIT KILL
        outro.sobrepor = {}
        outro.levar(999, l, GOLPES["ribbat_ultimate"])
        outro.vida = 0
        outro.mudar("voando")
        outro.vx, outro.vy = 5 * l.dir, -9
        l.inv = 0
        jogo.tremer(24)
        jogo.clarao = 8
        som.tocar("ko")
    if t >= U_FIM:
        return "fim"


def ultimate_efeito(l, tela):
    t = l.t
    m = l.memo
    if "alvo" not in m:
        return
    ax, ay = m["alvo"]
    s = l.s / 1.2 * 1.6  # (chefão é GRANDE)
    for i, nome in enumerate(CHEFES):
        u = t - (U_CHAMA + i * U_CHEFE)
        if 0 <= u < U_CHEFE:
            k = u / U_CHEFE
            DESENHOS[nome](tela, ax, ay, k, s, l.dir, t)
    final = U_CHAMA + len(CHEFES) * U_CHEFE
    if final <= t < final + 40:
        k = (t - final) / 40
        from efeitos import texto_grande
        texto_grande(tela, "HIT KILL!", 80, (255, 60, 40), (LARGURA // 2, 200), 1.6 - 0.6 * min(1, k * 3),
                     contorno=(40, 0, 0))


# ---------------------------------------------------------------- os chefões (desenhados em formas)
def _ida_volta(k):
    """0 -> 1 (chega, bate no meio) -> 0 (vai embora)."""
    return math.sin(k * math.pi)


def viuva(tela, ax, ay, k, s, d, t):
    """Viúva Negra: desce do teto pelo fio e morde."""
    y = (ay - 260 * s) + 190 * s * _ida_volta(k)
    pygame.draw.line(tela, (236, 238, 246), (ax, 0), (ax, y), 2)
    for lado in (-1, 1):
        for p in range(4):
            a = 0.5 + p * 0.35
            jx = ax + lado * math.cos(a) * 30 * s
            jy = y - math.sin(a) * 18 * s
            pygame.draw.lines(tela, (20, 16, 20), False, [(ax, y), (jx, jy), (jx + lado * 14 * s, jy + 26 * s)],
                              max(2, int(3 * s)))
    pygame.draw.ellipse(tela, (20, 16, 20), (ax - 18 * s, y - 14 * s, 36 * s, 30 * s))
    pygame.draw.polygon(tela, (210, 30, 30), [(ax - 5 * s, y - 4 * s), (ax + 5 * s, y - 4 * s), (ax, y + 3 * s),
                                              (ax + 5 * s, y + 10 * s), (ax - 5 * s, y + 10 * s), (ax, y + 3 * s)])
    pygame.draw.circle(tela, (20, 16, 20), (int(ax), int(y + 18 * s)), int(10 * s))
    for ox in (-4, 4):
        pygame.draw.circle(tela, (230, 40, 40), (int(ax + ox * s), int(y + 20 * s)), max(1, int(2 * s)))


def besouro(tela, ax, ay, k, s, d, t):
    """Besouro-rinoceronte: atravessa a tela em disparada com o chifre."""
    x = ax - d * 520 * s + d * 1040 * s * k
    y = ay - 24 * s
    pygame.draw.ellipse(tela, (34, 15, 7), (x - 44 * s, y - 30 * s, 88 * s, 52 * s))
    pygame.draw.ellipse(tela, (92, 44, 22), (x - 40 * s, y - 27 * s, 80 * s, 46 * s))
    pygame.draw.arc(tela, (196, 116, 66), (x - 32 * s, y - 24 * s, 50 * s, 30 * s), 1.6, 3.0, max(2, int(3 * s)))
    cx = x + d * 40 * s
    pygame.draw.polygon(tela, (58, 26, 12), [(cx, y - 6 * s), (cx + d * 34 * s, y - 34 * s), (cx + d * 14 * s, y + 2 * s)])
    for p in range(3):
        px = x - 22 * s + p * 22 * s
        pernas = math.sin(t * 0.9 + p) * 6 * s
        pygame.draw.line(tela, (40, 20, 10), (px, y + 14 * s), (px + pernas, y + 26 * s), max(2, int(3 * s)))


def rainha(tela, ax, ay, k, s, d, t):
    """Formiga Rainha: sai de um buraco no chão, com a coroa, e morde."""
    sobe = _ida_volta(k)
    x = ax + d * 60 * s
    y = ay - 70 * s * sobe
    pygame.draw.ellipse(tela, (40, 26, 18), (x - 40 * s, ay - 8 * s, 80 * s, 16 * s))  # o buraco
    if sobe < 0.05:
        return
    corte = pygame.Rect(0, 0, LARGURA, int(ay))
    sup = pygame.Surface((int(130 * s), int(140 * s)), pygame.SRCALPHA)
    cx, cy = sup.get_width() / 2, sup.get_height() * 0.55
    pygame.draw.ellipse(sup, (124, 36, 22), (cx - 34 * s, cy - 6 * s, 54 * s, 40 * s))  # abdômen
    pygame.draw.ellipse(sup, (206, 96, 64), (cx - 6 * s, cy - 22 * s, 26 * s, 26 * s))  # tórax
    pygame.draw.circle(sup, (124, 36, 22), (int(cx + 24 * s), int(cy - 30 * s)), int(15 * s))  # cabeça
    pygame.draw.polygon(sup, (250, 214, 70), [(cx + 12 * s, cy - 44 * s), (cx + 16 * s, cy - 58 * s),
                                              (cx + 22 * s, cy - 48 * s), (cx + 28 * s, cy - 60 * s),
                                              (cx + 32 * s, cy - 46 * s), (cx + 36 * s, cy - 44 * s)])  # coroa
    pygame.draw.circle(sup, (20, 10, 10), (int(cx + 30 * s), int(cy - 32 * s)), max(2, int(3 * s)))
    if d < 0:
        sup = pygame.transform.flip(sup, True, False)
    r = sup.get_rect(midbottom=(int(x), int(y + 60 * s)))
    tela.set_clip(corte)
    tela.blit(sup, r)
    tela.set_clip(None)


def gato(tela, ax, ay, k, s, d, t):
    """Gato Preto: pula de cima na diagonal com as garras."""
    x = ax + d * (300 - 300 * k) * s
    y = ay - 60 * s - 180 * s * (1 - k) * (1 - k) + 40 * s * k * k
    pygame.draw.ellipse(tela, (26, 24, 30), (x - 40 * s, y - 20 * s, 80 * s, 36 * s))
    pygame.draw.circle(tela, (26, 24, 30), (int(x - d * 40 * s), int(y - 10 * s)), int(18 * s))
    for ox in (-8, 8):  # orelhas
        bx = x - d * 40 * s + ox * s
        pygame.draw.polygon(tela, (26, 24, 30), [(bx - 6 * s, y - 22 * s), (bx + 6 * s, y - 22 * s), (bx, y - 38 * s)])
    for ox in (-6, 6):
        pygame.draw.ellipse(tela, (250, 208, 60), (x - d * 40 * s + ox * s - 3 * s, y - 14 * s, 6 * s, 8 * s))
    pygame.draw.lines(tela, (26, 24, 30), False, [(x + d * 38 * s, y), (x + d * 60 * s, y - 20 * s),
                                                  (x + d * 66 * s, y - 40 * s)], max(3, int(5 * s)))
    for p in (-1, 1):
        pygame.draw.line(tela, (70, 66, 92), (x - d * 30 * s + p * 6 * s, y + 10 * s),
                         (x - d * 52 * s + p * 6 * s, y + 26 * s), max(2, int(4 * s)))


def aguia(tela, ax, ay, k, s, d, t):
    """Águia-careca: mergulha do céu com as garras."""
    x = ax - d * 220 * s * (1 - k) + d * 160 * s * max(0, k - 0.5)
    y = ay - 70 * s - 300 * s * (1 - _ida_volta(k))
    asa = math.sin(t * 0.6) * 30 * s
    for lado in (-1, 1):
        pygame.draw.polygon(tela, (74, 50, 34), [(x, y), (x + lado * 90 * s, y - 20 * s + asa), (x + lado * 60 * s, y + 10 * s)])
    pygame.draw.ellipse(tela, (116, 84, 56), (x - 22 * s, y - 14 * s, 44 * s, 30 * s))
    pygame.draw.circle(tela, (248, 246, 240), (int(x + d * 24 * s), int(y - 12 * s)), int(13 * s))
    pygame.draw.polygon(tela, (250, 196, 44), [(x + d * 34 * s, y - 14 * s), (x + d * 48 * s, y - 8 * s),
                                               (x + d * 34 * s, y - 4 * s)])
    pygame.draw.circle(tela, (20, 20, 24), (int(x + d * 28 * s), int(y - 15 * s)), max(1, int(2 * s)))
    for p in (-1, 1):
        pygame.draw.line(tela, (250, 196, 44), (x + p * 8 * s, y + 14 * s), (x + p * 10 * s, y + 30 * s), max(2, int(3 * s)))


DESENHOS = {"viuva": viuva, "besouro": besouro, "rainha": rainha, "gato": gato, "aguia": aguia}


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


GOLPES["ribbat_lingua"] = dict(GOLPES["rib_lingua"], dano=35, logica=linguada, efeito=linguada_efeito)
_registra("ribbat_investida", ini=I_INI, ativo=I_FIM - I_INI, rec=14, janelas=((I_INI, I_FIM),), caixa=(0, 10, 58, 90),
          dano=50, hit=30, defe=16, emp=6, nivel="medio", derruba=True, voo=(9, 10), logica=investida, ia="medio",
          som="vento", quadros=[(0, "parado"), (I_INI - 2, "r_corre1"), (I_INI + 6, "r_corre2"),
                                (I_FIM, "r_corre1"), (I_FIM + 14, "parado")])
_registra("ribbat_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=ultimate, efeito=ultimate_efeito, ia="ultimate",
          quadros=[(0, "parado"), (8, "r_selo"), (U_FIM - 10, "r_selo"), (U_FIM, "parado")])
GOLPES["ribbat_ultimate"]["total"] = 9999

GOLPES_RIBBAT = {"E": "ribbat_lingua", "SHIFT": "ribbat_investida", "Z": "ribbat_ultimate"}


# =====================================================================
# ENTRADA (ideia do Gomes): chega pulando EM CIMA DE UMA FORMIGA e depois PEGA UMA MOSCA com a língua
# (a formiga e a mosca são os desenhos do jogo dele, de Ribbat/desenho.py)
# =====================================================================
E_CAI, E_MOSCA, E_LINGUA, E_ENGOLE = 36, 40, 74, 90


def _formiga_bruta(amassada, d, anim):
    """A formiga do jogo dele (desenhar_formiga), numa imagem de 40x30 com os pés em y=24."""
    sup = pygame.Surface((40, 30), pygame.SRCALPHA)
    cor, escura = (128, 48, 32), (70, 24, 14)
    if amassada:  # PLOFT: virou panqueca
        pygame.draw.ellipse(sup, cor, (4, 19, 32, 6))
        for px in (8, 16, 24, 32):
            pygame.draw.line(sup, escura, (px, 22), (px + 3, 25), 2)
        return sup
    x, y, w, h = 7, 8, 26, 16
    meio = x + w / 2
    by = y + h - 8
    for i, px in enumerate((-6, 0, 6)):
        o = math.sin(anim + i * 2) * 3
        pygame.draw.line(sup, escura, (meio + px, by), (meio + px - 4 + o, y + h), 2)
        pygame.draw.line(sup, escura, (meio + px, by), (meio + px + 4 - o, y + h), 2)
    pygame.draw.ellipse(sup, cor, (meio - d * 9 - 8, by - 7, 16, 12))
    pygame.draw.circle(sup, cor, (int(meio), int(by - 1)), 4)
    hx, hy = meio + d * 9, by - 3
    pygame.draw.circle(sup, cor, (int(hx), int(hy)), 6)
    pygame.draw.circle(sup, (255, 255, 255), (int(hx + d * 2), int(hy - 1)), 2)
    mexe = math.sin(anim * 0.7) * 2
    pygame.draw.line(sup, escura, (hx, hy - 4), (hx + d * 7, hy - 11 + mexe), 2)
    pygame.draw.line(sup, escura, (hx - d * 2, hy - 5), (hx + d * 2, hy - 13 - mexe), 2)
    return sup


def _mosca_bruta(t):
    """A mosca do jogo dele (desenhar_mosca), centrada em (15, 14) numa imagem de 30x24."""
    sup = pygame.Surface((30, 24), pygame.SRCALPHA)
    x, y = 15, 14
    asa = 3 + abs(math.sin(t * 0.42)) * 5
    pygame.draw.ellipse(sup, (215, 235, 250), (x - 9, y - 4 - asa, 9, asa + 2))
    pygame.draw.ellipse(sup, (215, 235, 250), (x, y - 4 - asa, 9, asa + 2))
    pygame.draw.ellipse(sup, (50, 50, 60), (x - 6, y - 4, 12, 8))
    pygame.draw.circle(sup, (210, 40, 40), (int(x + 5), int(y - 1)), 2)
    return sup


def _formiga_x(l, t):
    xf = l.extra["entrada_x"]
    return xf + l.dir * 70 * (1 - min(1, t / E_CAI))  # vem andando até onde ele vai cair


def _mosca_pos(l, t):
    xf = l.extra["entrada_x"]
    alvo = (xf + l.dir * 86 * l.s, CHAO - 34 * l.s)
    if t < E_LINGUA:  # chega zumbindo de cima
        k = suave(min(1, (t - E_MOSCA) / (E_LINGUA - E_MOSCA - 6)))
        x = alvo[0] + l.dir * 160 * (1 - k) + math.sin(t * 0.5) * 10
        y = alvo[1] - 180 * (1 - k) + math.cos(t * 0.7) * 8
        return x, y
    if t < E_LINGUA + 6:
        return alvo
    k = (t - E_LINGUA - 6) / (E_ENGOLE - E_LINGUA - 6)  # vem grudada na língua
    bx, by = boca(l)
    return alvo[0] + (bx - alvo[0]) * k, alvo[1] + (by - alvo[1]) * k


def entrada(l, t, jogo):
    xf = l.extra["entrada_x"]
    if t < E_CAI:  # o pulão de longe...
        k = t / E_CAI
        l.x = xf - l.dir * 420 * (1 - k)
        l.y = CHAO - math.sin(k * math.pi) * 200
        l.sobrepor = dict(POSES_RIB["r_corre2"])
    elif t < E_CAI + 14:  # ...EM CIMA DA FORMIGA (e quica)
        if t == E_CAI:
            som.tocar("queda", 0.6)
            som.tocar("puf", 0.5)
            fumaca(jogo, xf, CHAO - 4, 8, (150, 130, 100), 3, -1)
        k = (t - E_CAI) / 14
        l.x, l.y = xf, CHAO - math.sin(k * math.pi) * 40
    else:
        l.x, l.y = xf, CHAO
        if t == E_LINGUA:
            som.tocar("lingua")
        if t == E_ENGOLE:
            som.tocar("confirma", 0.4)  # GLUP
        l.sobrepor = dict(POSES_RIB["r_cruzado"]) if t > E_ENGOLE else {}
    l.t += 1


def entrada_efeito(l, tela, t):
    e = l.s * TAMANHO * 1.25
    # a FORMIGA
    if t < E_CAI + 40:
        d = -l.dir
        img = _formiga_bruta(t >= E_CAI, d, t * 0.4)
        w, h = int(40 * e), int(30 * e)
        img = pygame.transform.smoothscale(img, (w, h))
        if t >= E_CAI + 20:
            img.set_alpha(int(255 * (1 - (t - E_CAI - 20) / 20)))
        x = _formiga_x(l, t)
        tela.blit(img, (x - w / 2, CHAO - 24 * e))
    # a MOSCA e a LÍNGUA
    if E_MOSCA <= t < E_ENGOLE:
        mx, my = _mosca_pos(l, t)
        if t >= E_LINGUA:
            bx, by = boca(l)
            pygame.draw.line(tela, (120, 30, 50), (bx, by), (mx, my), int(7 * l.s))
            pygame.draw.line(tela, (235, 110, 140), (bx, by), (mx, my), int(4 * l.s))
            pygame.draw.circle(tela, (235, 110, 140), (int(mx), int(my)), int(5 * l.s))
        img = pygame.transform.smoothscale(_mosca_bruta(t), (int(30 * e), int(24 * e)))
        if l.dir < 0:
            img = pygame.transform.flip(img, True, False)
        tela.blit(img, (mx - 15 * e, my - 14 * e))


def vitoria(l, t, jogo):
    l.sobrepor = dict(POSES_RIB["r_cruzado"] if (t // 30) % 2 else POSES_RIB["r_selo"])
    if t % 60 == 10:
        som.tocar("lingua", 0.4)


RIBBAT = dict(nome="RIBBAT", cor=(112, 186, 80), vida=100, vel=4.6, pulo=18.5, forca=1.0, tam=1.24, altura=0.36,
              cor_poder=(236, 184, 52), desenho=desenhar_ribbat, golpes=GOLPES_RIBBAT, poses=POSES_RIBBAT,
              figura_extra=figura_ribbat, secreto=True, codigo=CODIGO,
              provocacao="RIBBIT!", cenario="PÂNTANO", entrada=entrada, entrada_efeito=entrada_efeito,
              vitoria=vitoria,
              provocacao_quadros=[(0, "parado"), (8, "r_cruzado"), (58, "r_cruzado"), (70, "parado")],
              nomes={"E": "LINGUADA (35)", "Q": "-", "R": "-", "SHIFT": "INVESTIDA (50)",
                     "Z": "OS CHEFÕES (HIT KILL)"})
