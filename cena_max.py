"""CENA DE ANIME: ENTRADA "CÁPSULA" do MAX-10 (ideia do Gomes).
A cápsula voando no espaço -> lá dentro o Max-10 desligado LIGA -> reentrada em chamas -> cai na terra ->
a porta abre, ele sai -> ALONGAMENTO ROBÔ (uns chutes) -> pose com o nome."""
import math
import random

import pygame

import cutscene
from cenas_anime import FAIXA, CenaAnime, estrelas, faixa_nome, planeta, poeira, texto_pow
from config import *  # noqa: F401,F403
from golpes import misturar, suave
from max10 import brilho

BORDA = (18, 20, 26)
CASCO, CASCO_ESC, CASCO_CLARO = (186, 192, 204), (118, 124, 138), (226, 230, 238)
DESLIGADO = {"r": (60, 18, 16), "R": (80, 30, 26)}  # o olho apagado

# ---- os planos no CHÃO: montados na ESCALA DO JOGO, em cima do MAPA da luta, e a câmera amplia ----
XM, XO, XC = LARGURA * 0.34, LARGURA * 0.7, LARGURA * 0.3  # o Max, o oponente e a cápsula, no mapa
ESC_CAPSULA = 0.62
HORIZ = 0.5  # o horizonte do plano rente ao chão (câmera bem baixinha)


# =====================================================================
# A CÁPSULA (desenhada numa imagem própria e depois girada/ampliada)
# =====================================================================
def _pose(c, pose):
    return pose if isinstance(pose, dict) else (c.l.poses.get(pose) or c.l.poses["parado"])


def max_vetor(c, q, pose, escala, x, y, d=1, olho=1.0, t=0):
    """O MAX-10 com o DESENHO DO JOGO (o design é o do jogo: aqui só cuida da animação)."""
    c.por(q, _pose(c, pose), escala, x, y, d, None if olho > 0 else DESLIGADO, guardar=False)


def max_img(c, pose, escala, olho=1.0, t=0):
    """O MAX-10 (desenho do jogo) numa imagem separada (pra girar, escurecer...). Devolve (imagem, (x, y) do pé)."""
    img, pe = c.corpo(_pose(c, pose), escala, 1, None if olho > 0 else DESLIGADO, guardar=False)
    return img.copy(), pe


def capsula(q, x, y, esc, ang=0.0, fogo=0.0, calor=0.0, porta=0.0, olho=0.0, t=0):
    """(x, y) = o meio da cápsula. porta: 0 fechada -> 1 aberta. olho: brilho vermelho na janelinha."""
    W, H = 220, 300
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    if fogo > 0:  # o FOGO dos propulsores embaixo
        for i, (cor, larg, comp) in enumerate((((255, 120, 40), 34, 70), ((255, 200, 80), 22, 54),
                                               ((255, 250, 220), 10, 34))):
            c = comp * fogo * (0.8 + 0.2 * math.sin(t * 1.3 + i))
            pygame.draw.polygon(s, cor, [(cx - larg, 250), (cx + larg, 250), (cx, 250 + c)])
    # o ESCUDO DE CALOR embaixo (fica em brasa na reentrada)
    escudo = [(cx - 78, 236), (cx + 78, 236), (cx + 60, 262), (cx - 60, 262)]
    pygame.draw.polygon(s, BORDA, [(px, py) for px, py in escudo])
    cor_esc = tuple(int(a + (b - a) * calor) for a, b in zip((70, 60, 62), (255, 150, 50)))
    pygame.draw.polygon(s, cor_esc, [(px + (cx - px) * 0.05, py + 2) for px, py in escudo])
    for i in range(6):
        pygame.draw.line(s, BORDA, (cx - 66 + i * 26, 240), (cx - 56 + i * 22, 258), 1)
    # as ALETAS dos lados
    for lado in (-1, 1):
        aleta = [(cx + lado * 58, 150), (cx + lado * 96, 230), (cx + lado * 70, 236)]
        pygame.draw.polygon(s, BORDA, aleta)
        pygame.draw.polygon(s, (190, 60, 50), [(px + (cx - px) * 0.08, py) for px, py in aleta])
    # o CORPO (tronco de cone com a cúpula em cima)
    corpo = [(cx - 50, 70), (cx + 50, 70), (cx + 74, 238), (cx - 74, 238)]
    pygame.draw.polygon(s, BORDA, [(corpo[0][0] - 3, 68), (corpo[1][0] + 3, 68), (corpo[2][0] + 3, 240),
                                   (corpo[3][0] - 3, 240)])
    pygame.draw.polygon(s, CASCO, corpo)
    pygame.draw.polygon(s, CASCO_ESC, [(cx + 20, 70), (cx + 50, 70), (cx + 74, 238), (cx + 34, 238)])  # sombra
    pygame.draw.polygon(s, CASCO_CLARO, [(cx - 44, 74), (cx - 34, 74), (cx - 52, 234), (cx - 62, 234)])  # brilho
    cupula = pygame.Rect(cx - 52, 20, 104, 104)
    pygame.draw.ellipse(s, BORDA, cupula.inflate(6, 6))
    pygame.draw.ellipse(s, CASCO, cupula)
    pygame.draw.arc(s, CASCO_CLARO, cupula.inflate(-16, -16), 1.8, 2.8, 5)
    pygame.draw.rect(s, CASCO, (cx - 49, 70, 98, 10))
    for k in range(1, 4):  # as linhas das placas e os rebites
        y = 70 + k * 42
        larg = 50 + 24 * (y - 70) / 168
        pygame.draw.line(s, CASCO_ESC, (cx - larg + 4, y), (cx + larg - 4, y), 2)
        for i in range(-3, 4):
            pygame.draw.circle(s, CASCO_ESC, (int(cx + i * larg / 4), y + 6), 2)
    for k in range(8):  # a faixa amarela e preta
        larg = 72
        x0 = cx - larg + k * larg * 2 / 8
        pygame.draw.rect(s, (230, 190, 40) if k % 2 else (30, 30, 34), (x0, 214, larg * 2 / 8 + 1, 12))
    # a PORTA (abre girando pro lado)
    porta_r = pygame.Rect(cx - 30, 110, 60, 96)
    pygame.draw.rect(s, (12, 12, 16), porta_r, border_radius=14)
    if porta > 0.4 and olho > 0:  # o olho vermelho lá dentro do escuro
        brilho(s, (porta_r.centerx + 6, porta_r.y + 30), 22, (255, 40, 30), int(220 * olho))
        pygame.draw.circle(s, (255, 90, 70), (porta_r.centerx + 6, porta_r.y + 30), 4)
    larg_p = porta_r.w * (1 - porta)
    if larg_p > 2:
        pr = pygame.Rect(porta_r.right - larg_p, porta_r.y, larg_p, porta_r.h)
        pygame.draw.rect(s, BORDA, pr.inflate(4, 4), border_radius=14)
        pygame.draw.rect(s, (160, 166, 178), pr, border_radius=13)
        if larg_p > 30:  # a JANELINHA redonda
            jan = (int(pr.centerx), pr.y + 30)
            pygame.draw.circle(s, BORDA, jan, 17)
            pygame.draw.circle(s, (40, 80, 120), jan, 14)
            if olho > 0:
                brilho(s, jan, 16, (255, 40, 30), int(220 * olho))
                pygame.draw.circle(s, (255, 80, 60), (jan[0] + 3, jan[1]), 4)
            pygame.draw.circle(s, (210, 240, 255), (jan[0] - 5, jan[1] - 5), 4)
            pygame.draw.line(s, BORDA, (pr.x + 8, pr.bottom - 24), (pr.right - 8, pr.bottom - 24), 2)
    # a ANTENA com a luzinha piscando e o nome pintado
    pygame.draw.line(s, BORDA, (cx, 22), (cx + 10, 2), 3)
    pygame.draw.circle(s, (255, 60, 50) if (t // 8) % 2 else (90, 30, 30), (cx + 10, 4), 4)
    from efeitos import texto
    texto(s, "MAX-10", 13, (60, 64, 76), (cx - 26, 225))
    if calor > 0:  # a cápsula toda em brasa
        brilho(s, (cx, 250), int(120 * calor), (255, 140, 40), int(160 * calor))
    img = pygame.transform.rotozoom(s, math.degrees(-ang), esc)
    q.blit(img, (x - img.get_width() / 2, y - img.get_height() / 2))


# =====================================================================
# Os planos
# =====================================================================
def cabine(c, q, t, escuro=0.0):
    """O interior da cápsula (parede de placas, a janela redonda com a Terra, a poltrona)."""
    w, h = q.get_size()
    cutscene.degrade(q, (0, 0, w, h), (30, 32, 40), (58, 62, 74))
    for i in range(0, w, 120):
        pygame.draw.line(q, (22, 24, 30), (i, 0), (i, h), 3)
        for j in range(60, h, 110):
            pygame.draw.circle(q, (80, 86, 98), (i + 10, j), 4)
            pygame.draw.circle(q, (80, 86, 98), (i + 110, j), 4)
    jan = (int(w * 0.18), int(h * 0.36))
    pygame.draw.circle(q, (12, 12, 16), jan, 92)
    vidro = pygame.Surface((168, 168), pygame.SRCALPHA)
    pygame.draw.circle(vidro, (6, 6, 22), (84, 84), 84)
    estrelas(vidro, t, (0.3, 0), semente=3, n=40)
    planeta(vidro, 120, 220, 140, t)
    mascara = pygame.Surface((168, 168), pygame.SRCALPHA)
    pygame.draw.circle(mascara, (255, 255, 255, 255), (84, 84), 84)
    vidro.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    q.blit(vidro, (jan[0] - 84, jan[1] - 84))
    pygame.draw.circle(q, (110, 116, 130), jan, 92, 10)
    x, y = w * 0.5, h * 0.9
    banco = pygame.Rect(0, 0, 230, 250)
    banco.midbottom = (int(x - 70), int(y - 40))
    pygame.draw.rect(q, (14, 14, 18), banco.inflate(10, 10), border_radius=30)
    pygame.draw.rect(q, (70, 40, 40), banco, border_radius=26)
    assento = pygame.Rect(0, 0, 300, 56)
    assento.midtop = (int(x), int(y - 52))
    pygame.draw.rect(q, (14, 14, 18), assento.inflate(10, 10), border_radius=18)
    pygame.draw.rect(q, (90, 50, 50), assento, border_radius=16)
    return jan


def paleta_max(c):
    """As cores do Max-10 com a SKIN que ele está usando (as letras da paleta do max10.py)."""
    import max10
    return {k: c.cor(k, v) for k, v in max10.PALETA.items()}


def cap_mapa(q, x, esc=ESC_CAPSULA, **kw):
    """A cápsula em pé no chão do mapa (x = o meio)."""
    capsula(q, x, CHAO - 112 * esc, esc, **kw)


def plano_alongamento(c, q, t, pose, centro, zoom, extra=None):
    """Monta um plano do alongamento no MAPA (Max + oponente + cápsula aberta), na escala do jogo, e amplia."""
    base = c._tela_aux()
    c.mapa(base, t + 120)
    cap_mapa(base, XC - 80, porta=1.0, t=t, ang=-0.08)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    max_vetor(c, base, pose, 1.0, XM, CHAO, 1, 1.0, t)
    if extra:
        extra(base)
    c.mapa_frente(base, t + 120)
    c.camera(q, base, centro, zoom, pixel=True)


def para_tela(centro, zoom, p, w=LARGURA, h=ALTURA):
    """Onde um ponto do mapa aparece na tela depois da câmera."""
    rw, rh = w / zoom, h / zoom
    x0 = max(0, min(w - rw, centro[0] - rw / 2))
    y0 = max(0, min(h - rh, centro[1] - rh / 2))
    return (p[0] - x0) * zoom, (p[1] - y0) * zoom


def cores_do_mapa(c):
    """As cores do CHÃO e do CÉU do mapa (pra o close rente ao chão combinar com o cenário)."""
    import cenarios
    if c._mapa is None or c._mapa.nome != c.cenario_nome:
        c._mapa = cenarios.cenario(c.cenario_nome)
    f = c._mapa.fundo
    chao = f.get_at((LARGURA // 2, min(ALTURA - 1, CHAO + 30)))[:3]
    chao2 = f.get_at((LARGURA // 3, min(ALTURA - 1, CHAO + 10)))[:3]
    ceu = f.get_at((LARGURA // 2, 30))[:3]
    ceu2 = f.get_at((LARGURA // 2, CHAO - 60))[:3]
    return chao, chao2, ceu, ceu2


def fundo_desfocado(c, q, t, centro, zoom, escurece=0):
    """O MAPA da luta atrás de um close, ampliado e DESFOCADO (como câmera de anime com o fundo fora de foco)."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    r = pygame.Rect(0, 0, int(w / zoom), int(h / zoom))
    r.center = (int(centro[0]), int(centro[1]))
    r.clamp_ip(base.get_rect())
    pequeno = pygame.transform.smoothscale(base.subsurface(r), (max(1, w // 24), max(1, h // 24)))
    pygame.transform.smoothscale(pequeno, (w, h), q)
    if escurece:
        q.fill((255 - escurece,) * 3, special_flags=pygame.BLEND_RGB_MULT)


def max_rosto(q, cx, cy, e, aceso, t, pal=None):
    """O ROSTO do Max-10 desenhado GRANDE pra close (nas cores da SKIN dele): (cx, cy) = o olho. aceso: 0..1.
    (Com o QR CODE na testa, do remodel do Gomes.)"""
    import max10
    pal = pal or max10.PALETA
    G, g, d, D = pal["G"], pal["g"], pal["d"], pal["D"]
    S, s_, m, k = pal["S"], pal["s"], pal["m"], (30, 22, 14)
    olho_cor = pal["r"]

    def P(x, y):
        return cx + x * e, cy + y * e

    def poli(pts, cor, borda=True):
        tp = [P(*p) for p in pts]
        if borda:
            pygame.draw.polygon(q, k, tp)
            pygame.draw.polygon(q, k, tp, max(3, int(e * 0.9)))
            meio = (sum(x for x, _ in tp) / len(tp), sum(y for _, y in tp) / len(tp))
            pygame.draw.polygon(q, cor, [(x + (meio[0] - x) * 0.04, y + (meio[1] - y) * 0.04) for x, y in tp])
        else:
            pygame.draw.polygon(q, cor, tp)

    for i, x in enumerate((-14, -6, 2)):  # o pescoço com os PISTÕES
        pygame.draw.line(q, k, P(x, 18), P(x - 2, 40), int(e * 3.4))
        pygame.draw.line(q, s_ if i % 2 else S, P(x, 18), P(x - 2, 40), int(e * 2.2))
    casco = [(-26, -18), (-14, -30), (6, -32), (22, -24), (30, -10), (30, 8), (22, 20), (-4, 22), (-22, 14), (-28, 0)]
    poli(casco, g)
    poli([(-24, -16), (-12, -27), (4, -29), (14, -24), (-6, -20), (-20, -8)], G, False)
    poli([(10, 12), (28, 4), (22, 18), (-2, 20)], d, False)
    pygame.draw.line(q, D, P(-6, -31), P(-10, 20), int(e * 0.8))
    for x, y in ((-18, -10), (-16, 8), (16, -24), (24, 12)):
        pygame.draw.circle(q, D, P(x, y), int(e * 1.2))
    for i in range(3):  # o QR CODE na testa (3x3, preto e branco)
        for j in range(3):
            preto = (i + j * 2) % 3 != 1
            r = pygame.Rect(0, 0, int(e * 3.4), int(e * 3.4))
            r.topleft = P(6 + i * 3.6, -26 + j * 3.6)
            pygame.draw.rect(q, (20, 20, 22) if preto else (245, 245, 245), r)
    pygame.draw.rect(q, k, (*P(5.4, -26.6), int(e * 11.8), int(e * 11.8)), max(1, int(e * 0.6)))
    fone = P(-17, 0)
    pygame.draw.circle(q, k, fone, int(e * 9.4))
    pygame.draw.circle(q, S, fone, int(e * 8.2))
    pygame.draw.circle(q, s_, fone, int(e * 5))
    pygame.draw.circle(q, m, fone, int(e * 2.6))
    for a in range(4):
        pygame.draw.circle(q, m, P(-17 + math.cos(a * 1.57 + 0.78) * 6.4, math.sin(a * 1.57 + 0.78) * 6.4), int(e))
    poli([(-7, -8), (31, -11), (31, 6), (-6, 7)], (34, 34, 42))  # o VISOR
    for i in range(4):
        pygame.draw.line(q, D, P(12 + i * 4, 9), P(12 + i * 4, 16), int(e * 1.2))
    pygame.draw.circle(q, k, P(0, 0), int(e * 6.4))
    pygame.draw.circle(q, m, P(0, 0), int(e * 5.4))
    if aceso > 0:
        brilho(q, (int(cx), int(cy)), int(e * 14 * aceso), olho_cor, int(220 * aceso))
    cor = tuple(int(a * 0.2 + (b - a * 0.2) * aceso) for a, b in zip(olho_cor, olho_cor))
    pygame.draw.circle(q, cor, P(0, 0), int(e * 4))
    if aceso > 0:
        pygame.draw.circle(q, tuple(min(255, c + 120) for c in olho_cor), P(-1, -1), int(e * 1.6 * aceso))
    pygame.draw.circle(q, (255, 255, 255), P(-2.4, -2.4), max(1, int(e * 0.9)))




def p3_liga(c, q, t, k):
    """3) LIGA: close ENORME no rosto... o olho falha... e acende VERMELHÃO; a câmera chega, a tela fica vermelha."""
    w, h = q.get_size()
    cutscene.degrade(q, (0, 0, w, h), (6, 8, 16), (20, 22, 32))
    acende = 18
    e = 7.0 + 4.0 * suave(k)  # a câmera não para de chegar perto
    cx, cy = w * 0.58 - 30 * suave(k), h * 0.5
    if t < acende:
        aceso = 0.6 if (10 <= t and t % 3 == 0) else 0.0  # o olho FALHANDO
    else:
        aceso = min(1, (t - acende) / 3)
    max_rosto(q, cx, cy, e, aceso, t, paleta_max(c))
    if t < acende:  # escurinho (só a luz azul da janela de lado)
        escuro = pygame.Surface((w, h), pygame.SRCALPHA)
        escuro.fill((0, 4, 20, 120))
        q.blit(escuro, (0, 0))
        brilho(q, (0, int(h * 0.3)), 300, (120, 170, 255), 40)
        return
    u = t - acende
    brilho(q, (int(cx), int(cy)), int(140 + u * 8), (255, 30, 20), 255)  # o VERMELHÃO
    brilho(q, (int(cx), int(cy)), 70, (255, 210, 190), 230)
    larg = int(w * min(1, u / 5))  # o risco de luz atravessando a tela
    pygame.draw.line(q, (255, 120, 100), (cx - larg, cy), (cx + larg, cy), 8)
    pygame.draw.line(q, (255, 255, 240), (cx - larg * 0.6, cy), (cx + larg * 0.6, cy), 3)
    if u >= 6:  # a TELA FICA VERMELHA (até o corte)
        verm = pygame.Surface((w, h), pygame.SRCALPHA)
        verm.fill((230, 20, 20, int(min(255, (u - 6) * 16))))
        q.blit(verm, (0, 0))
    if u == 0:
        c.tremor = 6


def p1_espaco(c, q, t, k):
    """1) TRAVESSIA: a cápsula cruza a tela em alta velocidade (rastro borrado e linhas de velocidade)."""
    w, h = q.get_size()
    cutscene.degrade(q, (0, 0, w, h), (4, 4, 18), (22, 12, 44))
    brilho(q, (int(w * 0.25), int(h * 0.3)), 260, (110, 60, 160), 50)  # nebulosa
    estrelas(q, t, (2.5, 0.0))
    planeta(q, w * 0.7, h * 1.6, h * 1.05, t)
    cutscene.linhas_horizontais(q, (255, 255, 255), FAIXA + 10, h - FAIXA - 10, 26, t, velocidade=90, alfa=120)
    x = -260 + (w + 520) * (k ** 1.3)  # passa ZUM de um lado pro outro
    y = h * 0.44 - k * 40
    for i in range(5, 0, -1):  # o rastro borrado (cópias apagadas pra trás)
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        capsula(sup, x - i * 60, y + i * 5, 0.9, ang=1.35, fogo=1.0, t=t)
        sup.set_alpha(150 - i * 25)
        q.blit(sup, (0, 0))
    capsula(q, x, y, 0.9, ang=1.35, fogo=1.0, t=t)
    brilho(q, (int(x - 120), int(y + 6)), 60, (255, 170, 90), 170)


def olho_max(c, pose, escala, x, y):
    """Onde fica o olho do Max-10 (desenho do jogo) quando ele está com o pé em (x, y)."""
    cx, cy = c.ponto(_pose(c, pose), "cb", escala, x, y)
    return cx + 5.5 * escala, cy + 1.5 * escala


def max_sentado(c, cabeca_baixa):
    from provocacoes_loja import POSES_EXTRA
    p = dict(POSES_EXTRA["sentado"])
    if cabeca_baixa > 0:  # largado, de cabeça baixa (desligado)
        cb = p["cb"]
        p["cb"] = (cb[0] + 10 * cabeca_baixa, cb[1] - 9 * cabeca_baixa)
        p["mt"] = (p["mt"][0] - 4 * cabeca_baixa, p["mt"][1] - 6 * cabeca_baixa)
        p["mf"] = (p["mf"][0] - 4 * cabeca_baixa, p["mf"][1] - 6 * cabeca_baixa)
    return p


def chao_deserto(q, t, horizonte):
    w, h = q.get_size()
    cutscene.degrade(q, (0, 0, w, horizonte), (90, 150, 220), (230, 220, 210))
    for i, (cor, alt) in enumerate((((160, 140, 150), 90), ((180, 150, 130), 60))):  # montanhas ao fundo
        pts = [(0, horizonte)]
        rnd = random.Random(20 + i)
        for x in range(0, w + 80, 80):
            pts.append((x, horizonte - rnd.uniform(0.3, 1.0) * alt))
        pts.append((w, horizonte))
        pygame.draw.polygon(q, cor, pts)
    pygame.draw.rect(q, (214, 180, 126), (0, horizonte, w, h - horizonte))
    for i in range(12):  # pedrinhas no chão
        rnd = random.Random(40 + i)
        x, y = rnd.uniform(0, w), rnd.uniform(horizonte + 10, h)
        pygame.draw.ellipse(q, (170, 140, 96), (x, y, 14 + i % 4 * 6, 6))


def pose_andar(c, fase):
    """O ANDAR suave: mistura as 4 poses de andar do jogo de forma contínua (fase em quadros de pose)."""
    nomes = ("andar1", "andar2", "andar3", "andar4")
    i = int(fase) % 4
    k = fase - int(fase)
    a = c.l.poses.get(nomes[i]) or c.l.poses["parado"]
    b = c.l.poses.get(nomes[(i + 1) % 4]) or c.l.poses["parado"]
    return misturar(a, b, k)


def p2_cabine(c, q, t, k):
    """2) DESLIGADO: escuro, a luz azul da janela, a cápsula vibrando de leve; a câmera vai chegando."""
    w, h = q.get_size()
    base = c._tela_aux()
    jan = cabine(c, base, t)
    x, y = w * 0.5, h * 0.9 - 40
    max_vetor(c, base, max_sentado(c, 1.0), 2.0, x, y, 1, 0.0, t)
    escuro = pygame.Surface((w, h), pygame.SRCALPHA)
    escuro.fill((0, 4, 20, 175))
    base.blit(escuro, (0, 0))
    luz_jan = pygame.Surface((w, h), pygame.SRCALPHA)  # o feixe azul da janela (com a poeirinha flutuando)
    pygame.draw.polygon(luz_jan, (120, 170, 255, 40), [(jan[0] - 60, jan[1] - 40), (jan[0] + 60, jan[1] + 40),
                                                         (w * 0.75, h), (w * 0.4, h)])
    base.blit(luz_jan, (0, 0))
    rnd = random.Random(8)
    for i in range(30):
        px = rnd.uniform(jan[0], w * 0.7) + math.sin(t * 0.05 + i) * 6
        py = (rnd.uniform(jan[1], h) - t * 0.4) % h
        pygame.draw.circle(base, (200, 220, 255), (int(px), int(py)), 1 + i % 2)
    if (t // 7) % 5 == 0:  # uma luzinha de painel piscando fraquinha no escuro
        brilho(base, (int(w * 0.82), int(h * 0.7)), 12, (90, 255, 120), 120)
    z = 1.0 + 0.6 * suave(k)  # a câmera chegando (e um tremorzinho da viagem)
    centro = (w * 0.52 + math.sin(t * 0.9) * 2, h * 0.5 - 30 * k + math.cos(t * 1.1) * 2)
    c.camera(q, base, centro, z)


def p3a_reentrada(c, q, t, k):
    """3a) A REENTRADA: a câmera ACOMPANHA a cápsula descendo; as nuvens passam na diagonal; o calor só aumenta."""
    w, h = q.get_size()
    cutscene.degrade(q, (0, 0, w, h), (30, 30, 90), (240, 130, 80))
    rnd = random.Random(9)
    vel = 34 + 30 * k
    for i in range(22):  # nuvens passando na diagonal (de baixo/direita pra cima/esquerda)
        x = (rnd.uniform(0, w * 1.6) - t * vel * (0.6 + (i % 3) * 0.3)) % (w * 1.6) - w * 0.3
        y = (rnd.uniform(0, h * 1.6) - t * vel * 0.7 * (0.6 + (i % 3) * 0.3)) % (h * 1.6) - h * 0.3
        larg = 120 + (i % 3) * 80
        pygame.draw.ellipse(q, (250, 228, 226), (x, y, larg, 14 + (i % 3) * 6))
    cx, cy = w * 0.5 + math.sin(t * 0.7) * 5, h * 0.45 + math.cos(t * 0.9) * 4
    ang = -0.6
    calor = 0.4 + 0.6 * k
    for i in range(12):  # o PLASMA (cresce com o calor)
        a = ang + math.pi + (i - 5.5) * 0.08
        comp = (180 + 220 * k) + (i % 3) * 50 + math.sin(t * 0.8 + i) * 30
        cor = ((255, 250, 220), (255, 200, 80), (255, 120, 40))[i % 3]
        pygame.draw.polygon(q, cor, [(cx + math.cos(a + 1.4) * 70, cy + math.sin(a + 1.4) * 70),
                                     (cx + math.cos(a) * comp, cy + math.sin(a) * comp),
                                     (cx + math.cos(a - 1.4) * 70, cy + math.sin(a - 1.4) * 70)])
    brilho(q, (int(cx + 60), int(cy + 70)), int(120 + 80 * k), (255, 150, 60), 210)
    capsula(q, cx, cy, 1.0 + 0.25 * k, ang=ang + math.sin(t * 0.7) * 0.05, calor=calor, t=t)
    for i in range(8):  # faíscas do escudo se soltando
        u = (t * 3 + i * 17) % 50
        pygame.draw.circle(q, (255, 230, 150), (int(cx + 80 - u * 6 + i * 5), int(cy + 60 - u * 5 + i * 3)), 2)
    cutscene.linhas_velocidade(q, (int(cx), int(cy)), (255, 255, 240), n=40, r_dentro=230, grossura=6, semente=5,
                               giro=t * 0.03, alfa=int(60 + 80 * k))
    c.tremor = max(c.tremor, int(3 + 5 * k))


def p3b_risco(c, q, t, k):
    """3b) No MAPA da luta: uma bola de fogo riscando o céu e caindo bem na arena."""
    w, h = q.get_size()
    c.mapa(q, t)
    c.por_oponente(q, "parado", 1.0, XO, CHAO)
    u = suave(k)
    x0, y0 = -60, h * 0.06
    x1, y1 = XC, CHAO - 60
    x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * (u ** 1.4)
    pts = [(x0 + (x1 - x0) * v, y0 + (y1 - y0) * (v ** 1.4)) for v in [i / 24 * u for i in range(25)]]
    for i in range(len(pts) - 1):  # o RASTRO de fumaça
        pygame.draw.line(q, (235, 225, 225), pts[i], pts[i + 1], int(2 + 12 * (i / len(pts))))
    brilho(q, (int(x), int(y)), 60 + int(40 * u), (255, 170, 60), 230)
    pygame.draw.circle(q, (255, 245, 210), (int(x), int(y)), 10)
    c.mapa_frente(q, t)


def p4_impacto(c, q, t, k):
    """4) O IMPACTO no MAPA: desce com rastro, AMASSA, quadro de impacto, rachaduras, anel de poeira, pedras
    quicando... o OPONENTE se protege do vento... e a poeira baixa e mostra a cápsula fumegando."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t)
    cai = 5
    u = t - cai
    opo = "parado" if u < 0 else ("defesa" if u < 34 else "parado")  # (se protegendo da poeira)
    c.por_oponente(base, opo, 1.0, XO + (min(12, max(0, u) * 2) if u >= 0 else 0), CHAO)
    if t < cai:
        y = -200 + (CHAO - 112 * ESC_CAPSULA + 200) * (t / cai)
        for i in range(4, 0, -1):
            sup = pygame.Surface((w, h), pygame.SRCALPHA)
            capsula(sup, XC, y - i * 40, ESC_CAPSULA, ang=-0.1, calor=0.9, t=t)
            sup.set_alpha(110 - i * 22)
            base.blit(sup, (0, 0))
        capsula(base, XC, y, ESC_CAPSULA, ang=-0.1, calor=0.9, t=t)
        c.camera(q, base, (XC + 120, CHAO - 120), 1.5, pixel=True)
        return
    if u == 0:
        c.inverte = 3
        c.tremor = 28
    for i in range(10):  # as RACHADURAS no chão do mapa
        a = math.pi + i * math.pi / 9
        comp = min(1, u / 6) * (90 + (i % 3) * 45)
        pts = [(XC, CHAO)]
        for j in range(1, 5):
            pts.append((XC + math.cos(a) * comp * j / 4 + math.sin(i * 3 + j) * 5,
                        CHAO + abs(math.sin(a)) * comp * j / 4 * 0.15 + 2))
        pygame.draw.lines(base, (60, 44, 34), False, pts, 2)
    pygame.draw.ellipse(base, (40, 30, 24), (XC - 100, CHAO - 8, 200, 22))  # a cratera (sombra)
    amassa = 1 - 0.16 * max(0, 1 - u / 6) * math.cos(u * 1.2)
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    cap_mapa(sup, XC, calor=max(0, 0.8 - u * 0.03), t=t, ang=-0.08)
    sup = pygame.transform.smoothscale(sup, (w, int(h * amassa)))
    base.blit(sup, (0, int(CHAO * (1 - amassa))))
    if u < 8:
        brilho(base, (int(XC), CHAO), int(160 * (1 - u / 8)) + 1, (255, 240, 200), 230)
    anel = min(1, u / 20)  # o ANEL de poeira correndo pelo chão
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(26):
        a = i * math.tau / 26
        d = 50 + 300 * anel
        px, py = XC + math.cos(a) * d, CHAO + 4 + math.sin(a) * d * 0.12
        pygame.draw.circle(sup, (215, 190, 150, int(210 * (1 - anel * 0.6))), (int(px), int(py)), int(18 + 26 * anel))
    base.blit(sup, (0, 0))
    poeira(base, XC, CHAO, min(1, u / 30), larg=150, semente=3)
    rnd = random.Random(3)
    for i in range(12):  # pedras voando e quicando
        vx, vy = rnd.uniform(-7, 7), rnd.uniform(-11, -5)
        px, py = XC + vx * u, CHAO - 14 + vy * u + 0.5 * u * u
        if py > CHAO:
            py = CHAO - abs(math.sin(u * 0.4 + i)) * 10 * max(0, 1 - u / 40)
        tam = 3 + i % 3 * 2
        pygame.draw.polygon(base, (90, 70, 52), [(px, py - tam), (px + tam, py), (px, py + tam * 0.7), (px - tam, py)])
    if u > 24:  # o vapor subindo da cápsula quente
        for i in range(4):
            v = (u * 2 + i * 11) % 50
            sup = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(sup, (240, 240, 245, int(140 * (1 - v / 50))), (30, 30), int(8 + v * 0.3))
            base.blit(sup, (XC - 30 + (i - 1.5) * 16, CHAO - 170 - v))
    c.mapa_frente(base, t)
    c.camera(q, base, (XC + 140 - min(1, u / 30) * 40, CHAO - 110), 1.5 + 0.2 * min(1, u / 30), pixel=True)
    if u < 14:
        texto_pow(q, "BOOM!", (int(w * 0.36), int(h * 0.24)), 80, (255, 200, 60), u, giro=0.12)


def p5_porta(c, q, t, k):
    """5) No MAPA: a porta abre (vapor)... o VULTO com o olho aceso... ele sai andando (suave) pra luz.
    O oponente assiste."""
    w, h = q.get_size()
    base = c._tela_aux()
    c.mapa(base, t + 60)
    c.por_oponente(base, "parado", 1.0, XO, CHAO)
    pygame.draw.ellipse(base, (40, 30, 24), (XC - 100, CHAO - 8, 200, 22))
    abre = suave(min(1, max(0, (t - 4) / 12)))
    olho = 1.0 if 8 <= t < 20 else 0.0
    cap_mapa(base, XC, porta=abre, olho=olho, t=t, ang=-0.08)
    for i in range(5):  # o vapor saindo da porta
        u = (t * 2 + i * 9) % 40
        if t >= 4:
            sup = pygame.Surface((70, 70), pygame.SRCALPHA)
            pygame.draw.circle(sup, (240, 240, 245, int(160 * (1 - u / 40))), (35, 35), int(10 + u * 0.5))
            base.blit(sup, (XC - 30 + (i - 2) * 10 - u * 0.5, CHAO - 160 - u))
    if t >= 20:
        a = suave(min(1, (t - 20) / 22))
        x = XC + 4 + a * (XM - XC + 40)
        pose = pose_andar(c, (t - 20) * 0.22) if a < 1 else c.l.poses["parado"]
        sombra = 1 - a
        img, pe = max_img(c, pose, 1.0, 0.0 if sombra > 0.3 else 1.0, t)
        if sombra > 0:
            img.fill((int(255 - 220 * sombra),) * 3 + (255,), special_flags=pygame.BLEND_RGB_MULT)
        base.blit(img, (int(x - pe[0]), int(CHAO - pe[1])))
        if sombra > 0.3:
            ol = olho_max(c, pose, 1.0, x, CHAO)
            brilho(base, (int(ol[0]), int(ol[1])), 14, paleta_max(c)["r"], 230)
    c.mapa_frente(base, t + 60)
    c.camera(q, base, (XC + 70, CHAO - 90), 2.1, pixel=True)
    if 4 <= t < 20:
        from efeitos import texto
        texto(q, "TSSSSS...", 22, (240, 240, 250), (int(w * 0.62), int(h * 0.22)))


def vapor_junta(q, x, y, u):
    """Vapor saindo de uma junta (o 'tssss' do robô se alongando)."""
    for i in range(4):
        v = u * 2 + i * 6
        if v < 30:
            sup = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(sup, (245, 245, 250, int(170 * (1 - v / 30))), (40, 40), int(8 + v * 0.8))
            q.blit(sup, (x - 40 - v * 1.5 + i * 4, y - 40 - v))


def p6a_chute(c, q, t, k):
    """6a) CHUTE ALTO (antecipação, estica, segura) com CLANK! e vapor saindo do joelho."""
    l = c.l
    par, chute, ag = (l.poses["parado"], l.poses.get("m_chutaco") or l.poses["chute"],
                      l.poses.get("agachado") or l.poses["parado"])
    if t < 8:
        pose = misturar(par, ag, suave(t / 8) * 0.4)
    elif t < 13:
        pose = misturar(misturar(par, ag, 0.4), chute, suave((t - 8) / 5))
    elif t < 26:
        pose = chute
    else:
        pose = misturar(chute, par, suave(min(1, (t - 26) / 6)))
    centro, zoom = (XM + 60, CHAO - 90), 2.2

    def arco(b):
        if 11 <= t < 15:
            pygame.draw.arc(b, (255, 255, 255), (XM - 20, CHAO - 150, 160, 140), 0.2, 1.6, 3)
    plano_alongamento(c, q, t, pose, centro, zoom, arco)
    if 13 <= t < 26:
        jx, jy = para_tela(centro, zoom, c.ponto(chute, "jf", 1.0, XM, CHAO))
        vapor_junta(q, jx, jy, t - 13)
        texto_pow(q, "CLANK!", (int(jx + 160), int(jy - 120)), 48, (255, 220, 90), t - 13)
        if t == 13:
            c.tremor = 5


def p6b_chute2(c, q, t, k):
    """6b) Close de baixo: o SEGUNDO CHUTE, rápido, com o arco e CLIC!"""
    l = c.l
    par, chute = l.poses["parado"], l.poses["chute"]
    if t < 5:
        pose = par
    elif t < 9:
        pose = misturar(par, chute, suave((t - 5) / 4))
    elif t < 20:
        pose = chute
    else:
        pose = misturar(chute, par, suave(min(1, (t - 20) / 6)))
    centro, zoom = (XM + 50, CHAO - 50), 3.2

    def arco(b):
        if 7 <= t < 11:
            pygame.draw.arc(b, (255, 255, 255), (XM - 10, CHAO - 110, 140, 100), 0.0, 1.3, 3)
    plano_alongamento(c, q, t, pose, centro, zoom, arco)
    if 9 <= t < 20:
        jx, jy = para_tela(centro, zoom, c.ponto(chute, "jf", 1.0, XM, CHAO))
        vapor_junta(q, jx, jy, t - 9)
        texto_pow(q, "CLIC!", (int(jx + 180), int(jy - 60)), 44, (150, 230, 255), t - 9, giro=0.1)


def p6c_pose(c, q, t, k):
    """6c) A POSE FINAL: estica os braços... a câmera chega, o olho brilha forte, e entra o nome."""
    w, h = q.get_size()
    l = c.l
    pose = misturar(l.poses["parado"], l.poses.get("vitoria") or l.poses["parado"], suave(min(1, t / 10)))
    z = 2.0 + 0.5 * suave(min(1, t / 40))
    centro = (XM + 30, CHAO - 100)
    plano_alongamento(c, q, t, pose, centro, z)
    ol = para_tela(centro, z, olho_max(c, pose, 1.0, XM, CHAO))
    if t > 12:  # o BRILHO no olho (com o risco de luz)
        f = min(1, (t - 12) / 6)
        cor = paleta_max(c)["r"]
        brilho(q, (int(ol[0]), int(ol[1])), int(50 * f) + 1, cor, 240)
        pygame.draw.line(q, tuple(min(255, x + 90) for x in cor), (ol[0] - 140 * f, ol[1]), (ol[0] + 140 * f, ol[1]), 3)
    if t >= 24:
        faixa_nome(q, "MAX-10", "PRONTO PRA LUTA.", c.cor("g", (210, 60, 50)) if False else (210, 60, 50), (t - 24) / 30)


PLANOS = [
    (20, p1_espaco, {0: ("vento", 0.9)}),
    (36, p2_cabine, {}),
    (40, p3_liga, {10: ("blip", 0.3), 18: ("carga", 0.9)}),
    (30, p3a_reentrada, {0: ("foguete", 0.8), 14: ("vento", 0.6)}),
    (26, p3b_risco, {0: ("vento", 0.5)}),
    (46, p4_impacto, {5: ("explosao", 1.0), 8: ("terra", 0.8)}),
    (44, p5_porta, {4: ("defesa", 0.6), 20: ("queda", 0.3)}),
    (32, p6a_chute, {13: ("soco", 0.7)}),
    (26, p6b_chute2, {9: ("chute", 0.7)}),
    (60, p6c_pose, {12: ("carga", 0.5), 24: ("ultimate", 0.4)}),
]


def entrada(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS, titulo, oponente)


criar = entrada


# =====================================================================
# CENA DE ANIME: VITÓRIA "SAIR VOANDO" do MAX-10
# o derrotado no chão -> close no olho -> os jatos acendem -> DECOLA -> atravessa as nuvens -> pontinho na lua: TING!
# =====================================================================
def por_do_sol(q, horizonte):
    w, h = q.get_size()
    cutscene.degrade(q, (0, 0, w, horizonte), (60, 40, 110), (255, 150, 90))
    brilho(q, (int(w * 0.7), horizonte - 30), 160, (255, 200, 120), 160)
    pygame.draw.circle(q, (255, 210, 140), (int(w * 0.7), horizonte - 30), 56)
    for i, (cor, alt) in enumerate((((120, 70, 100), 90), ((80, 50, 80), 60))):
        pts = [(0, horizonte)]
        rnd = random.Random(30 + i)
        for x in range(0, w + 80, 80):
            pts.append((x, horizonte - rnd.uniform(0.3, 1.0) * alt))
        pts.append((w, horizonte))
        pygame.draw.polygon(q, cor, pts)
    pygame.draw.rect(q, (150, 100, 80), (0, horizonte, w, h - horizonte))
    pygame.draw.line(q, (200, 140, 100), (0, horizonte), (w, horizonte), 3)


def v1_vitoria(c, q, t, k):
    """1) No MAPA: de pé ao lado do derrotado (o oponente de verdade, caído), e a câmera chega."""
    base = c._tela_aux()
    c.mapa(base, t)
    c.por_oponente(base, "caido", 1.0, XO - 40, CHAO)
    max_vetor(c, base, "parado", 1.0, XM + 60, CHAO, 1, 1.0, t)
    c.mapa_frente(base, t)
    c.camera(q, base, (XM + 170, CHAO - 90), 1.8 + 0.3 * suave(k), pixel=True)


def v2_olho(c, q, t, k):
    """2) Close no rosto: o olho PULSA (missão cumprida)."""
    w, h = q.get_size()
    fundo_desfocado(c, q, t, (XM, CHAO - 150), 2.4, 40)
    pulso = 0.6 + 0.4 * abs(math.sin(t * 0.25))
    max_rosto(q, w * 0.55, h * 0.48, 8.0 + 1.5 * k, pulso, t, paleta_max(c))
    from efeitos import texto
    if t > 12:
        texto(q, "MISSÃO CUMPRIDA.", 24, (255, 230, 220), (int(w * 0.5), int(h * 0.86)))


def chao_perto(q, t, horizonte, marca=0.0, brasa=0.0, cores=None, fundo=None):
    """O CHÃO visto de pertinho (câmera no chão), nas cores do MAPA da luta: faixas que alargam pra perto,
    rachaduras saindo do fundo, pedrinhas. marca: a marca queimada dos jatos; brasa: rachaduras brilhando."""
    w, h = q.get_size()
    chao, chao2, ceu, ceu2 = cores or ((180, 140, 100), (160, 120, 90), (70, 40, 110), (255, 160, 100))
    if fundo is not None:  # o próprio mapa, desfocado, lá no fundo
        q.blit(fundo, (0, 0), (0, fundo.get_height() - horizonte, w, horizonte))
    else:
        cutscene.degrade(q, (0, 0, w, horizonte), ceu, ceu2)
    for i in range(10):  # as faixas do chão (mais claras perto da câmera)
        y0 = horizonte + (h - horizonte) * (i / 10) ** 1.7
        y1 = horizonte + (h - horizonte) * ((i + 1) / 10) ** 1.7
        f = 0.75 + i * 0.03
        base_c = chao if i % 2 else chao2
        cor = tuple(min(255, int(x * f)) for x in base_c)
        pygame.draw.rect(q, cor, (0, y0, w, y1 - y0 + 1))
    fuga = (w * 0.5, horizonte - 40)
    rnd = random.Random(12)
    escuro = tuple(int(x * 0.55) for x in chao)
    for i in range(9):  # as RACHADURAS
        x_perto = rnd.uniform(-w * 0.3, w * 1.3)
        pts = []
        for kk in (0.3, 0.55, 0.8, 1.0):
            pts.append((fuga[0] + (x_perto - fuga[0]) * kk + rnd.uniform(-20, 20) * kk, fuga[1] + (h + 20 - fuga[1]) * kk))
        cor = tuple(int(a + (b - a) * brasa) for a, b in zip(escuro, (255, 140, 50)))
        pygame.draw.lines(q, cor, False, pts, 2 + i % 2)
    for i in range(26):  # pedrinhas
        kk = rnd.uniform(0.05, 1) ** 0.6
        x = rnd.uniform(0, w)
        y = horizonte + (h - horizonte) * kk
        r = 2 + 12 * kk
        pygame.draw.ellipse(q, escuro, (x - r, y - r * 0.45, r * 2, r * 0.9))
        pygame.draw.ellipse(q, tuple(min(255, int(x_ * 1.15)) for x_ in chao), (x - r * 0.7, y - r * 0.4, r * 1.2, r * 0.5))
    if marca > 0:
        for lado in (-1, 1):
            mx = w * 0.5 + lado * w * 0.13
            pygame.draw.ellipse(q, (40, 26, 20), (mx - 110 * marca, h * 0.86 - 22, 220 * marca, 50))
            pygame.draw.ellipse(q, (255, 120, 40), (mx - 60 * marca, h * 0.86 - 8, 120 * marca, 22), 2)


def bota(q, x, y, e, d=1, pal=None):
    """A BOTA do Max-10 desenhada GRANDE (de lado), nas cores da SKIN: sola, biqueira, tornozelo articulado e a
    canela. (x, y) = o meio da sola embaixo."""
    import max10
    pal = pal or max10.PALETA
    k, S, s_, m = (24, 20, 16), pal["S"], pal["s"], pal["m"]
    G, g, dd = pal["G"], pal["g"], pal["d"]

    def P(px, py):
        return x + px * e * d, y + py * e

    def poli(pts, cor):
        tp = [P(*p) for p in pts]
        pygame.draw.polygon(q, k, tp)
        pygame.draw.polygon(q, k, tp, max(3, int(e * 1.2)))
        mx, my = sum(a for a, _ in tp) / len(tp), sum(b for _, b in tp) / len(tp)
        pygame.draw.polygon(q, cor, [(a + (mx - a) * 0.06, b + (my - b) * 0.06) for a, b in tp])

    poli([(-12, -40), (-10, -160), (8, -160), (10, -40)], g)  # a CANELA dourada (sai pra cima da tela)
    pygame.draw.polygon(q, G, [P(-9, -44), P(-7, -156), P(-2, -156), P(-4, -44)])  # brilho
    pygame.draw.line(q, dd, P(6, -50), P(7, -152), max(2, int(e)))
    for yy in (-70, -110):  # as placas da armadura da canela
        pygame.draw.line(q, k, P(-11, yy), P(9, yy - 2), max(2, int(e * 0.9)))
        pygame.draw.circle(q, dd, P(-6, yy - 6), max(2, int(e * 1.3)))
        pygame.draw.circle(q, dd, P(4, yy - 7), max(2, int(e * 1.3)))
    poli([(-16, -30), (-14, -46), (14, -46), (16, -30)], s_)  # o TORNOZELO articulado
    pygame.draw.circle(q, k, P(0, -38), int(e * 7))
    pygame.draw.circle(q, S, P(0, -38), int(e * 5.6))
    pygame.draw.circle(q, m, P(0, -38), int(e * 2.4))
    poli([(-20, 0), (-20, -24), (-8, -32), (16, -30), (34, -18), (40, -6), (40, 0)], S)  # a BOTA
    pygame.draw.polygon(q, (226, 228, 234), [P(-17, -6), P(-17, -22), P(-8, -28), P(-2, -27), P(-12, -12)])
    poli([(22, -18), (34, -18), (40, -6), (40, 0), (24, 0)], m)  # a biqueira
    pygame.draw.rect(q, k, (*P(-21, -3), 62 * e, 5 * e))  # a SOLA (de onde sai o jato)
    for i in range(4):
        pygame.draw.circle(q, s_, P(-12 + i * 9, -16), max(1, int(e * 1.3)))  # rebites


def jato(q, x, y, e, forca, t, azul=False, chao=None):
    """O JATO saindo da sola (x, y = a sola). Se o chão estiver perto (chao = y do chão), o fogo BATE e espalha."""
    cores = ((120, 180, 255), (200, 230, 255), (255, 255, 255)) if azul else ((255, 110, 40), (255, 200, 80), (255, 250, 220))
    brilho(q, (int(x), int(y + 20 * e)), int(70 * e * forca) + 1, cores[0], 220)
    fundo = y + 60 * e * forca if chao is None else min(chao, y + 60 * e * forca)
    for i in range(3):
        larg = (24 - i * 7) * e
        pygame.draw.polygon(q, cores[i], [(x - larg, y), (x + larg, y), (x + larg * 0.4, fundo), (x - larg * 0.4, fundo)])
    if chao is not None and fundo >= chao - 2:  # o fogo ESPARRAMANDO no chão pros dois lados
        tremula = 0.85 + 0.15 * math.sin(t * 1.7)
        for i in range(3):
            larg = (90 - i * 26) * e * forca * tremula
            alt = (10 - i * 3) * e
            pygame.draw.ellipse(q, cores[i], (x - larg, chao - alt, larg * 2, alt * 1.4))
        for lado in (-1, 1):  # as línguas de fogo correndo pelo chão
            for j in range(3):
                ponta = x + lado * (90 + j * 26 + math.sin(t * 0.9 + j) * 10) * e * forca * 0.9
                pygame.draw.polygon(q, cores[1], [(x + lado * 30 * e, chao - 6 * e), (ponta, chao - (2 + j * 2) * e),
                                                  (x + lado * 30 * e, chao + 2)])


def v4_chao(c, q, t, k):
    """4) CÂMERA NO CHÃO: o chão de pertinho, as BOTAS dele... os jatos acendem (azul, depois laranja),
    a poeira explode em anel... e as botas sobem e saem da tela. Fica a marca queimada no chão."""
    w, h = q.get_size()
    horizonte = int(h * HORIZ)
    acende, laranja, sobe = 24, 36, 58
    sobe_k = 0 if t < sobe else ((t - sobe) / 22) ** 2
    brasa = 0 if t < laranja else min(1, (t - laranja) / 12) * (1 - min(1, max(0, (t - sobe - 20) / 30)))
    if not hasattr(c, "_fundo_chao"):
        c._fundo_chao = pygame.Surface((w, h))
        fundo_desfocado(c, c._fundo_chao, 0, (LARGURA * 0.5, CHAO - h * 0.22), 1.6, 30)
    chao_perto(q, t, horizonte, marca=1.0 if t >= sobe + 6 else 0.0, brasa=brasa, cores=cores_do_mapa(c),
               fundo=c._fundo_chao)
    e = 4.4
    pes = [(w * 0.36, h * 0.66), (w * 0.62, h * 0.63)]  # (a sola um pouco acima do chão: apoiada no calcanhar)
    chao_y = [h * 0.8, h * 0.77]
    if t >= acende:  # a POEIRA explodindo em anel pelo chão (e o tremor)
        u = min(1, (t - acende) / 40)
        sup = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(22):
            a = i * math.tau / 22
            d = 120 + 520 * u
            px, py = w * 0.5 + math.cos(a) * d, h * 0.9 + math.sin(a) * d * 0.18
            r = 40 + 50 * u
            pygame.draw.circle(sup, (215, 180, 140, int(200 * (1 - u * 0.75))), (int(px), int(py)), int(r))
        q.blit(sup, (0, 0))
        if t < sobe + 10:
            c.tremor = max(c.tremor, 4 if t < laranja else 9)
    if t >= sobe + 18:  # a fumaça subindo da marca queimada (depois que ele já foi)
        for lado in (-1, 1):
            for i in range(4):
                u = ((t - sobe) * 1.5 + i * 12) % 60
                pygame.draw.circle(q, (90, 80, 80), (int(w * 0.5 + lado * w * 0.13 + math.sin(u * 0.1 + i) * 10),
                                                     int(h * 0.84 - u * 3)), int(10 + u * 0.6))
    for (px, py), cy in zip(pes, chao_y):
        y = py - sobe_k * (h * 1.6)
        if y < -300:
            continue
        if t >= acende:
            forca = min(1, (t - acende) / 6) * (1.3 if t >= sobe else 1.0)
            jato(q, px + 10 * e, y + 1, e, forca, t, azul=t < laranja, chao=cy)
        if t < sobe:  # a sombra da bota no chão
            pygame.draw.ellipse(q, (90, 60, 50), (px - 30 * e, cy - 6, 80 * e, 14))
        bota(q, px, y, e, 1, paleta_max(c))
    if acende <= t < acende + 14:
        texto_pow(q, "FSSSHH!", (int(w * 0.24), int(h * 0.3)), 44, (180, 220, 255), t - acende, giro=0.14)
    if sobe <= t < sobe + 14:
        texto_pow(q, "VRUUUM!", (int(w * 0.7), int(h * 0.28)), 60, (255, 230, 120), t - sobe, giro=-0.16)


def v5_ceu(c, q, t, k):
    """5) No MAPA, de longe: as marcas queimadas no chão e ele indo embora voando, riscando o céu (e a faixa)."""
    w, h = q.get_size()
    c.mapa(q, t + 100)
    c.por_oponente(q, "caido", 1.0, XO - 40, CHAO)
    xm = XM + 60
    for lado in (-1, 1):  # as marcas queimadas, ainda fumegando
        mx = xm + lado * 14
        pygame.draw.ellipse(q, (40, 26, 20), (mx - 16, CHAO - 4, 32, 9))
        for i in range(3):
            v = (t * 1.2 + i * 14) % 42
            pygame.draw.circle(q, (110, 100, 100), (int(mx + math.sin(v * 0.15) * 4), int(CHAO - 6 - v * 2)), int(3 + v * 0.3))
    u = min(1, t / 60)
    x0, y0 = xm, CHAO - 40
    x1, y1 = x0 + w * 0.5 * u, y0 - (CHAO - 70) * (u ** 0.7)
    pts = [(x0 + w * 0.5 * v, y0 - (CHAO - 70) * (v ** 0.7)) for v in [i / 20 * u for i in range(21)]]
    if len(pts) > 1:
        pygame.draw.lines(q, (255, 245, 235), False, pts, 4)
        pygame.draw.lines(q, (255, 190, 140), False, [(a, b + 3) for a, b in pts], 2)
    esc = 1.0 * (1 - 0.8 * u)
    img, pe = max_img(c, "m_voo", max(0.15, esc), 1.0, t)
    img = pygame.transform.rotate(img, -35)
    q.blit(img, (int(x1 - img.get_width() / 2), int(y1 - img.get_height() / 2)))
    brilho(q, (int(x1 - 10 * esc), int(y1 + 30 * esc)), int(30 * esc) + 4, (255, 170, 60), 220)
    c.mapa_frente(q, t + 100)
    if t > 50:
        faixa_nome(q, "MAX-10", "MISSÃO CUMPRIDA. PRÓXIMO ALVO...", (210, 60, 50), (t - 50) / 30)


PLANOS_VOA = [
    (50, v1_vitoria, {}),
    (40, v2_olho, {4: ("carga", 0.5)}),
    (100, v4_chao, {24: ("foguete", 0.6), 36: ("foguete", 0.9), 58: ("explosao", 0.8)}),
    (100, v5_ceu, {0: ("vento", 0.6), 50: ("ultimate", 0.4)}),
]


def vitoria(ficha, titulo="", oponente=None):
    return CenaAnime(ficha, PLANOS_VOA, titulo, oponente)
