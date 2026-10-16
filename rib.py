"""RIB: o sapo ninja (criado pelo Gomes). Referência ao Ribbat, outro jogo dele.

Aparência: sapo ninja, shurikens na cintura, cachecol preto, olhos de gato.
  E      shuriken (5 de dano cada, rápida). 5 em 5 segundos = tem que recarregar
  R      corrida: se acertar, vai empurrando e batendo (5 hits de 5)
  Q      rasteira + chute pra cima (joga o oponente pra cima)
  SHIFT  LINGUADA (20 de dano, demora um pouquinho pra sair) e puxa o outro
  Z      ULTIMATE com cutscene: salto, selo de mão, shurikens em bolha. Sempre acerta.
         Mais forte que as outras, mas deixa ele sem shuriken por 15 segundos.
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
# Poses do Rib (sapo ninja: mais agachadinho e com a mão na frente)
# =====================================================================
POSES_RIB = {
    "parado": dict(pt=(-14, 0), jt=(-28, 22), pf=(14, 0), jf=(30, 22), qd=(0, 40), pc=(12, 72), cb=(19, 88),
                   ct=(-4, 58), mt=(-12, 50), cf=(26, 62), mf=(40, 70)),
    "andar1": dict(pt=(-22, 0), jt=(-30, 20), pf=(22, 0), jf=(34, 22), qd=(0, 38), pc=(12, 70), cb=(19, 86),
                   ct=(-4, 56), mt=(-12, 48), cf=(26, 60), mf=(40, 68)),
    "andar2": dict(pt=(4, 10), jt=(-10, 26), pf=(6, 0), jf=(26, 22), qd=(0, 42), pc=(12, 74), cb=(19, 90),
                   ct=(-4, 60), mt=(-12, 52), cf=(26, 64), mf=(40, 72)),
    "andar3": dict(pt=(22, 0), jt=(34, 22), pf=(-22, 0), jf=(-30, 20), qd=(0, 38), pc=(12, 70), cb=(19, 86),
                   ct=(-4, 56), mt=(-12, 48), cf=(26, 60), mf=(40, 68)),
    "andar4": dict(pt=(6, 0), jt=(26, 22), pf=(4, 10), jf=(-10, 26), qd=(0, 42), pc=(12, 74), cb=(19, 90),
                   ct=(-4, 60), mt=(-12, 52), cf=(26, 64), mf=(40, 72)),
    # arremesso de shuriken
    "r_arma": dict(pt=(-26, 0), jt=(-14, 26), pf=(24, 0), jf=(26, 26), qd=(-2, 48), pc=(0, 84), cb=(6, 101),
                   ct=(-16, 82), mt=(-26, 92), cf=(16, 74), mf=(26, 80)),
    "r_arremesso": dict(pt=(-30, 0), jt=(-18, 24), pf=(26, 0), jf=(30, 26), qd=(2, 44), pc=(14, 80), cb=(20, 96),
                        ct=(-6, 68), mt=(-12, 58), cf=(34, 84), mf=(60, 86)),
    # corrida ninja (braços pra trás!)
    "r_corre1": dict(pt=(-30, 10), jt=(-16, 28), pf=(28, 0), jf=(26, 28), qd=(0, 46), pc=(22, 76), cb=(32, 90),
                     ct=(6, 70), mt=(-12, 72), cf=(10, 68), mf=(-8, 68)),
    "r_corre2": dict(pt=(28, 0), jt=(26, 28), pf=(-30, 10), jf=(-16, 28), qd=(0, 46), pc=(22, 76), cb=(32, 90),
                     ct=(6, 70), mt=(-12, 72), cf=(10, 68), mf=(-8, 68)),
    "r_soco_a": dict(pt=(-28, 0), jt=(-16, 26), pf=(26, 0), jf=(28, 28), qd=(0, 46), pc=(14, 80), cb=(22, 96),
                     ct=(-4, 70), mt=(6, 76), cf=(34, 82), mf=(62, 84)),
    "r_soco_b": dict(pt=(-28, 0), jt=(-16, 26), pf=(26, 0), jf=(28, 28), qd=(0, 46), pc=(14, 80), cb=(22, 96),
                     ct=(34, 80), mt=(62, 80), cf=(14, 70), mf=(24, 78)),
    # rasteira e chute pra cima
    "r_rasteira": dict(pt=(-16, 0), jt=(-22, 26), pf=(74, 4), jf=(38, 10), qd=(0, 24), pc=(-8, 52), cb=(-12, 68),
                       ct=(-18, 38), mt=(-28, 6), cf=(4, 40), mf=(12, 28)),
    "r_chute_cima": dict(pt=(-10, 0), jt=(-8, 30), pf=(20, 128), jf=(14, 86), qd=(0, 58), pc=(-12, 94), cb=(-16, 112),
                         ct=(-22, 80), mt=(-30, 68), cf=(-4, 82), mf=(6, 74)),
    # linguada
    "r_puxa_ar": dict(pt=(-26, 0), jt=(-14, 26), pf=(22, 0), jf=(26, 26), qd=(-4, 48), pc=(-8, 84), cb=(-8, 102),
                      ct=(-18, 70), mt=(-22, 60), cf=(4, 70), mf=(10, 62)),
    "r_lingua": dict(pt=(-30, 0), jt=(-18, 24), pf=(26, 0), jf=(30, 26), qd=(2, 44), pc=(16, 80), cb=(26, 94),
                     ct=(-4, 66), mt=(-12, 56), cf=(12, 66), mf=(4, 58)),
    # ultimate
    "r_selo": dict(pt=(-10, 4), jt=(4, 26), pf=(14, 6), jf=(22, 30), qd=(0, 46), pc=(4, 84), cb=(6, 102),
                   ct=(-6, 70), mt=(14, 86), cf=(18, 70), mf=(16, 88)),
    "r_chute_ult": dict(pt=(-16, 0), jt=(-12, 28), pf=(72, 70), jf=(38, 60), qd=(-2, 56), pc=(-14, 88), cb=(-16, 106),
                        ct=(-22, 74), mt=(-12, 86), cf=(0, 78), mf=(12, 88)),
}
proporcionar(POSES_RIB)

# =====================================================================
# E: SHURIKEN (com munição)
# =====================================================================
SHURIKENS = 5          # 5 seguidas...
JANELA_RAJADA = 300    # ...em 5 segundos = tem que recarregar
RECARGA = 180          # 3 segundos recarregando
SEM_SHURIKEN = 900     # depois da ultimate: 15 segundos sem shuriken


def rib_todo_quadro(l, jogo):
    """Conta o relógio do Rib e mostra a munição na tela."""
    x = l.extra
    x["relogio"] = x.get("relogio", 0) + 1
    agora = x["relogio"]
    x["tiros"] = [q for q in x.get("tiros", []) if agora - q < JANELA_RAJADA]
    texto = None
    if agora < x.get("sem_ate", 0):
        texto = f"SEM SHURIKEN {math.ceil((x['sem_ate'] - agora) / FPS)}s"
    elif agora < x.get("recarga_ate", 0):
        texto = "RECARREGANDO"
    x["municao"] = (SHURIKENS - len(x["tiros"]) if not texto else 0, SHURIKENS, texto)


def tem_shuriken(l):
    x = l.extra
    agora = x.get("relogio", 0)
    return agora >= x.get("sem_ate", 0) and agora >= x.get("recarga_ate", 0) and len(x.get("tiros", [])) < SHURIKENS


def lancou_shuriken(l, jogo):
    x = l.extra
    x.setdefault("tiros", []).append(x.get("relogio", 0))
    if len(x["tiros"]) >= SHURIKENS:  # 5 rapidinhas: hora de recarregar
        x["recarga_ate"] = x.get("relogio", 0) + RECARGA
        x["tiros"] = []


def desenha_shuriken(p, tela):
    a = p.t * 0.6 * (1 if p.vx > 0 else -1)
    r = p.raio * 1.6
    for i in range(3):  # rastro
        x = p.x - p.vx * (i + 1) * 0.9
        pygame.draw.circle(tela, (200, 210, 230), (int(x), int(p.y)), max(1, int(r * 0.3 - i)))
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r * 0.35
        pts.append((p.x + math.cos(a + k * math.pi / 4) * rr, p.y + math.sin(a + k * math.pi / 4) * rr))
    pygame.draw.polygon(tela, (40, 44, 52), [(x + (x - p.x) * 0.15, y + (y - p.y) * 0.15) for x, y in pts])
    pygame.draw.polygon(tela, (200, 206, 216), pts)
    pygame.draw.circle(tela, (60, 64, 72), (int(p.x), int(p.y)), max(2, int(r * 0.22)))


# =====================================================================
# R: CORRIDA (empurra e vai batendo)
# =====================================================================
C_SAI, C_INTERVALO, C_HITS, C_CORRE_ATE = 8, 8, 5, 60  # corre até 60 quadros procurando; achou: bate os 5


def corrida_janelas():
    return tuple((C_SAI + k * C_INTERVALO, C_SAI + k * C_INTERVALO + 5)
                 for k in range((C_CORRE_ATE + C_HITS * C_INTERVALO - C_SAI) // C_INTERVALO))


def corrida(l, outro, jogo):
    t = l.t
    m = l.memo
    if t == 1:
        m["hits"], m["antes"] = 0, False
    if l.acertou and not m["antes"]:  # acertou um hit agora
        if outro.estado == "defendendo":
            m["parou"] = t  # defendeu: para a corrida
        else:
            m["hits"] += 1
            if m["hits"] == 1:
                m["quadros"] = [(t, "r_soco_a")] + [(t + 2 + k * 4, "r_soco_b" if k % 2 == 0 else "r_soco_a")
                                                    for k in range(C_HITS * 2 + 2)]
            if m["hits"] >= C_HITS:
                m["parou"] = t
    m["antes"] = l.acertou
    m["g_hit"] = GOLPES["rib_corrida_final"] if m["hits"] == C_HITS - 1 else GOLPES["rib_corrida"]
    if "parou" in m:
        m["caixa"] = None
        l.vx *= 0.75
        if t - m["parou"] > 18:
            return "fim"
    elif t < C_SAI:
        l.vx = 0
    elif t < C_CORRE_ATE or m["hits"]:
        l.vx = (6.5 if m["hits"] else 9.5) * l.dir
        m["caixa"] = (0, 30, 50, 110)
        if t % 3 == 0:
            fumaca(jogo, l.x - 18 * l.dir, CHAO - 4, 1, (170, 150, 130), 1, -0.3)
    else:
        m["parou"] = t
    l.fisica(jogo)


def corrida_quadros():
    q = [(0, "parado"), (C_SAI - 2, "r_corre1")]
    for k in range(1, 16):
        q.append((C_SAI - 2 + k * 4, "r_corre2" if k % 2 else "r_corre1"))
    q.append((C_CORRE_ATE + 18, "parado"))
    return q


# =====================================================================
# Q: RASTEIRA + CHUTE PRA CIMA
# =====================================================================
def rasteira(l, outro, jogo):
    t = l.t
    l.memo["g_hit"] = GOLPES["rib_rasteira"] if t < 13 else GOLPES["rib_chute_cima"]
    l.memo["caixa"] = (16, 0, 96, 26) if t < 13 else (6, 50, 64, 170)
    l.vx = 2.5 * l.dir if t < 12 else 0
    l.fisica(jogo)
    if t >= 42:
        return "fim"


# =====================================================================
# SHIFT: LINGUADA (referência ao Ribbat!)
# =====================================================================
L_SAI, L_ESTICA, L_VOLTA, L_FIM, L_ALCANCE = 22, 27, 36, 52, 160


def boca(l):
    p = l.pose_vista or l.pose_atual()
    return l.ponto({"b": (p["cb"][0] + 8, p["cb"][1] - 4)}, "b")


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
        l.memo["caixa"] = (8, (l.y - by) / l.s - 7, alcance + 8, (l.y - by) / l.s + 7)
    else:
        l.memo["ext"] = 0
    l.vx = 0
    l.fisica(jogo)
    if t >= L_FIM:
        return "fim"


def linguada_efeito(l, tela):
    ext = l.memo.get("ext", 0)
    if ext <= 0:
        if l.t < L_SAI and l.t > 6:  # bochecha inflando
            bx, by = boca(l)
            r = int((3 + 4 * (l.t - 6) / (L_SAI - 6)) * l.s)
            pygame.draw.circle(tela, (230, 120, 150), (int(bx), int(by)), r)
        return
    bx, by = boca(l)
    fx = bx + (L_ALCANCE * ext) * l.s * l.dir
    meio_y = by + math.sin(l.t * 0.8) * 3
    pts = [(bx, by), ((bx + fx) / 2, meio_y), (fx, by)]
    pygame.draw.lines(tela, (120, 30, 50), False, pts, int(9 * l.s))
    pygame.draw.lines(tela, (235, 110, 140), False, pts, int(6 * l.s))
    pygame.draw.circle(tela, (120, 30, 50), (int(fx), int(by)), int(7 * l.s))
    pygame.draw.circle(tela, (245, 140, 170), (int(fx), int(by)), int(5.5 * l.s))


# =====================================================================
# Z: ULTIMATE — KAGE BUNSHIN (do jeito que o Gomes pediu, sem cutscene)
# O Rib faz o selo, aparecem 3 clones (dois no chão atrás dele e um pulando) e eles arremessam um monte de shuriken.
# Dá pra errar: defendendo leva bem menos, pulando escapa de algumas e, se baterem no Rib, os clones somem.
# =====================================================================
U_PUF, U_JOGA, U_INTERVALO, U_TIROS = 16, 26, 4, 14
U_SOME = U_JOGA + U_TIROS * U_INTERVALO + 8
U_FIM = U_SOME + 14
U_DANO = 35                      # total, se todas as shurikens acertarem
CLONES = ((-72, 0), (-144, 0), (-36, None))   # (distância pra trás, altura) — None = o que pula


class ShurikenUlt(Projetil):
    """Shuriken dos clones: vai reto na direção do oponente (inclusive de cima, do clone que pulou)."""

    def __init__(self, dono, x, y, alvo):
        super().__init__(dono, x, y, dono.dir, GOLPES["rib_ult_shuriken"])
        dx, dy = alvo[0] - x, alvo[1] - y
        d = math.hypot(dx, dy) or 1
        self.vx, self.vy = dx / d * self.golpe["vel"], dy / d * self.golpe["vel"]

    def update(self):
        self.t += 1
        self.x += self.vx
        self.y += self.vy
        if self.x < -40 or self.x > LARGURA + 40 or self.y > CHAO:
            self.vivo = False


def _clone_pos(l, i, t):
    """Onde está o clone i (deslocamento em relação ao Rib, no mundo)."""
    dx, dy = CLONES[i]
    if dy is None:  # o que pula: sobe e desce durante os arremessos
        k = max(0.0, min(1.0, (t - U_PUF) / (U_SOME - U_PUF)))
        dy = -math.sin(k * math.pi) * 150
    return dx * l.s / 1.34 * l.dir, dy * l.s / 1.34


def ultimate(l, outro, jogo):
    m = l.memo
    t = l.t
    if t == 1:
        l.extra["sem_ate"] = l.extra.get("relogio", 0) + SEM_SHURIKEN + U_FIM
        m["tela_toda"] = True  # os clones ficam longe dele: desenha a tela toda
    l.vx = 0
    l.fisica(jogo)
    if t == U_PUF:  # KAGE BUNSHIN!
        som.tocar("puf")
        m["clones"] = [dict(pose="r_selo") for _ in CLONES]
        for i in range(len(CLONES)):
            dx, dy = _clone_pos(l, i, t)
            fumaca(jogo, l.x + dx, l.y + dy - 60 * l.s, 8, (220, 226, 236), 4, -1)
    clones = m.get("clones")
    if clones and t < U_SOME:
        for c in clones:
            c["pose"] = "r_arma" if t >= U_PUF + 6 else "r_selo"
        k = t - U_JOGA
        if 0 <= k < U_TIROS * U_INTERVALO:
            quem = (k // U_INTERVALO) % len(CLONES)
            clones[quem]["pose"] = "r_arremesso"
            if k % U_INTERVALO == 0:  # arremessa!
                dx, dy = _clone_pos(l, quem, t)
                mao = POSES_RIB["r_arremesso"]["mt"]
                hx = l.x + dx + mao[0] * l.s * l.dir
                hy = l.y + dy - mao[1] * l.s
                alvo = (outro.x + random.uniform(-10, 10), outro.y - random.uniform(40, 80) * outro.s)
                jogo.projeteis.append(ShurikenUlt(l, hx, hy, alvo))
                som.tocar("shuriken", 0.6)
    if clones and t == U_SOME:  # os clones somem
        som.tocar("puf", 0.6)
        for i in range(len(CLONES)):
            dx, dy = _clone_pos(l, i, t)
            fumaca(jogo, l.x + dx, l.y + dy - 60 * l.s, 8, (220, 226, 236), 4, -1)
        m["clones"] = None
    if t >= U_FIM:
        return "fim"


def ultimate_quadros():
    return [(0, "parado"), (6, "r_selo"), (U_SOME, "r_selo"), (U_FIM, "parado")]


def ultimate_efeito(l, tela):
    if l.t < U_PUF:  # brilho do selo
        p = l.pose_vista or l.pose_atual()
        mx, my = l.ponto(p, "mf")
        brilho(tela, (int(mx), int(my)), int((10 + 3 * l.t) * l.s), (150, 220, 255), 160)


def desenhar_clones(l, tela, branco):
    """Os clones (o mesmo desenho do Rib), atrás dele."""
    clones = l.memo.get("clones") if l.estado == "ataque" and l.nome_golpe == "rib_ultimate" else None
    if not clones or getattr(l, "_clone", False):
        return
    guarda = (l.x, l.y)
    l._clone = True
    try:
        for i, c in enumerate(clones):
            dx, dy = _clone_pos(l, i, l.t)  # (já vem na escala certa: mundo ou desenho pequeno)
            l.x, l.y = guarda[0] + dx, guarda[1] + dy
            desenhar_rib(l, tela, POSES_RIB[c["pose"]], branco)
    finally:
        l.x, l.y = guarda
        l._clone = False


# =====================================================================
# Golpes do Rib
# =====================================================================
def _registra(nome, **g):
    g.setdefault("base", "parado")
    g.setdefault("pose", "parado")
    g.setdefault("caixa", None)
    g.setdefault("especial", True)
    g["total"] = g.get("total", g["ini"] + g["ativo"] + g.get("rec", 0))
    GOLPES[nome] = g


_registra("rib_shuriken", pose="r_arremesso", som="shuriken", ini=5, ativo=1, rec=10, proj=True, varios=True, raio=7, vel=12,
          dano=5, hit=12, defe=8, emp=3, nivel="medio", ia="longe", pode=tem_shuriken, ao_usar=lancou_shuriken,
          desenho_proj=desenha_shuriken,
          quadros=[(0, "parado"), (3, "r_arma"), (5, "r_arremesso"), (11, "r_arremesso"), (16, "parado")])
_registra("rib_corrida", som="vento", ini=C_SAI, ativo=C_CORRE_ATE - C_SAI, rec=18, janelas=corrida_janelas(),
          caixa=(0, 30, 50, 110), dano=5, hit=12, defe=10, emp=6.5, nivel="medio", logica=corrida, ia="medio",
          quadros=corrida_quadros())
GOLPES["rib_corrida_final"] = dict(GOLPES["rib_corrida"], derruba=True, voo=(8, 8), emp=8)
_registra("rib_rasteira", som="vento", ini=7, ativo=12, rec=23, janelas=((7, 11), (15, 21)), caixa=(16, 0, 96, 26),
          dano=4, hit=20, defe=12, emp=1, nivel="baixo", logica=rasteira, ia="perto",
          quadros=[(0, "parado"), (5, "agachado"), (8, "r_rasteira"), (12, "r_rasteira"), (15, "r_chute_cima"),
                   (28, "r_chute_cima"), (42, "parado")])
GOLPES["rib_chute_cima"] = dict(GOLPES["rib_rasteira"], dano=6, nivel="medio", lanca=17)
GOLPES["rib_rasteira"]["lanca"] = None
_registra("rib_lingua", ini=L_SAI + 2, ativo=L_VOLTA - L_SAI, rec=L_FIM - L_VOLTA,
          janelas=((L_SAI + 2, L_VOLTA + 2),), dano=20, hit=24, defe=14, emp=-9, nivel="medio",
          logica=linguada, efeito=linguada_efeito, ia="medio",
          quadros=[(0, "parado"), (L_SAI - 4, "r_puxa_ar"), (L_SAI, "r_lingua"), (L_VOLTA + 4, "r_lingua"),
                   (L_FIM, "parado")])
_registra("rib_ult_shuriken", ini=0, ativo=1, rec=0, dano=U_DANO / U_TIROS, hit=12, defe=6, emp=1, nivel="medio",
          proj=True, raio=8, vel=13, varios=True, ultimate=True, desenho_proj=desenha_shuriken,
          guarda_custo=5)  # segurando a defesa até o fim, a guarda aguenta (dá pra se defender da ultimate)
_registra("rib_ultimate", ini=U_JOGA, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          logica=ultimate, efeito=ultimate_efeito, ia="ultimate", quadros=ultimate_quadros())
GOLPES["rib_ultimate"]["total"] = U_FIM + 1
# o chute pra cima conta como "jogar pra cima" (dá pra pular atrás e fazer combo aéreo)
GOLPES["rib_rasteira"]["lanca_depois"] = True

GOLPES_RIB = {"E": "rib_shuriken", "R": "rib_corrida", "Q": "rib_rasteira", "SHIFT": "rib_lingua", "Z": "rib_ultimate"}

# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  G g d D verde (claro -> escuro)  c C barriga  n N roupa ninja  x X cachecol preto
#   s m shuriken (aço)  y Y p olho de gato (amarelo, brilho, pupila)  b B faixa  t cinto
PALETA = {
    "k": (16, 24, 14), "G": (160, 222, 104), "g": (100, 174, 66), "d": (58, 120, 48), "D": (32, 74, 34),
    "c": (236, 228, 168), "C": (192, 182, 120), "n": (44, 44, 62), "N": (76, 78, 104),
    "x": (22, 22, 28), "X": (64, 64, 78), "s": (204, 210, 220), "m": (110, 116, 128),
    "y": (252, 214, 56), "Y": (255, 246, 180), "p": (8, 8, 8), "b": (220, 212, 188), "B": (160, 150, 126),
    "t": (110, 70, 38),
}
S_REF = 1.34 / 3

TRONCO = Peca([
    "...kkkkkkkk...",
    "..kxXXXxxxxk..",
    ".kxxXxxxxxxxk.",
    ".kGGggxxcccdk.",
    ".kGgggggcccdk.",
    ".kGgggggccCdk.",
    ".kgggggccccdk.",
    ".kgggggccccdk.",
    ".kggggdcccCdk.",
    "..kgggdcccdk..",
    "..kgggdccCdk..",
    "..kggddcccdk..",
    "..kgddDccCdk..",
    "..ktttttttttk.",
    "..ktsmtttsmtk.",
    "..ktttttttttk.",
    "..knnnnnnnnnk.",
    "..kNnnnnnnnnk.",
    "..kNnnnnnnnnk.",
    "..knnnnnnnnnk.",
    "..knnnnnnnnnk.",
    "..knnnnnnnnnk.",
    "...knnnnnnnk..",
    "....kkkkkkk...",
], PALETA, a=(7, 20), b=(7, 1))

TRONCO_COSTAS = Peca([
    "...kkkkkkkk...",
    "..kxXXXxxxxk..",
    ".kxxXxxxxxxxk.",
    ".kGGgggxxgddk.",
    ".kGggggggggdk.",
    ".kGggggdgggdk.",
    ".kgggggggggdk.",
    ".kggdgggggddk.",
    ".kggggggdggdk.",
    "..kgggggggdk..",
    "..kggdgggddk..",
    "..kggggggddk..",
    "..kgddDdddDk..",
    "..ktttttttttk.",
    "..ktttttttttk.",
    "..ktttttttttk.",
    "..knnnnnnnnnk.",
    "..kNnnnnnnnnk.",
    "..kNnnnnnnnnk.",
    "..knnnnnnnnnk.",
    "..knnnnnnnnnk.",
    "..knnnnnnnnnk.",
    "...knnnnnnnk..",
    "....kkkkkkk...",
], PALETA, a=(7, 20), b=(7, 1))

CABECA = Peca([
    "..kkk..kkkkk..",
    ".kyyyk.kyYYyk.",
    ".kypyk.kyYpyk.",
    "kkyykkkkyypyk.",
    "kGkkGGggkkkk..",
    "kGGggggggggGk.",
    "kGgggggggggggk",
    "kgggggggggggdk",
    "kkkkkkkkkkkkkk",
    "kgccccccccccdk",
    ".kdddcccccddk.",
    "..kkxxxxxxkk..",
    "...kxXXxxk....",
], PALETA, a=(6, 6), b=(6, 0), estica=False)

CABECA_COSTAS = Peca([
    "..kkk..kkkkk..",
    ".kgGgk.kgGGgk.",
    ".kgggk.kgggdk.",
    "kkgdkkkkggdk..",
    "kGkkGGggkkkk..",
    "kGGggggggggGk.",
    "kGgggggggggggk",
    "kgggggggggggdk",
    "kgggggggggggdk",
    "kggggggggggddk",
    ".kdddddddddk..",
    "..kkxxxxxxkk..",
    "...kxXXxxk....",
], PALETA, a=(6, 6), b=(6, 0), estica=False)

COXA = Peca([
    ".kkkkkk.",
    "kGGgggdk",
    "kGggggdk",
    "kGggggdk",
    "kGggggdk",
    "kgggggdk",
    "kggggddk",
    "kggggddk",
    "kgggdddk",
    ".kgddDk.",
    ".kgddDk.",
    ".kdddDk.",
    "..kddk..",
    "..kkkk..",
], PALETA, a=(3, 0), b=(3, 13))

CANELA = Peca([
    ".kkkkk.",
    "kGgggdk",
    "kgggddk",
    "kbBbBbk",
    "kBbBbBk",
    "kbBbBbk",
    "kBbBbBk",
    "kbBbBbk",
    "kBbBbBk",
    ".kbBbk.",
    ".kBbBk.",
    ".kgddk.",
    "..kdk..",
    "..kkk..",
], PALETA, a=(3, 0), b=(3, 13))

PE = Peca([
    ".kkkk.......",
    "kgGggkkkk...",
    "kggggggGgkk.",
    "kddddddddgdk",
    ".kkdkkdkkdkk",
    "..k..k..k...",
], PALETA, a=(3, 1), b=(10, 1), estica=False)

BRACO = Peca([
    ".kkk.",
    "kGgdk",
    "kGgdk",
    "kGgdk",
    "kggdk",
    "kggdk",
    "kggdk",
    "kgddk",
    "kgddk",
    "kgddk",
    ".kdk.",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 11))

ANTEBRACO = Peca([
    ".kkk.",
    "kggdk",
    "kggdk",
    "kbBbk",
    "kBbBk",
    "kbBbk",
    "kBbBk",
    "kbBbk",
    "kBbBk",
    "kbBbk",
    ".kkk.",
], PALETA, a=(2, 0), b=(2, 10))

MAO = Peca([
    ".kkkk.",
    "kGgggk",
    "kggGgk",
    "kgdgdk",
    ".kkkk.",
], PALETA, a=(2, 0), b=(2, 4), estica=False)


def _cachecol(l, tela, pescoco, d, esc, branco):
    """A ponta do cachecol balançando atrás (mais forte quando corre)."""
    vel = min(1.5, abs(l.vx) / 6 + 0.3)
    pts = [pescoco]
    for i in range(1, 9):
        onda = math.sin(l.t * 0.25 - i * 0.8) * i * 0.45 * vel * esc
        cai = i * (1.1 - 0.6 * vel) * esc
        pts.append((pescoco[0] - d * i * 3.0 * esc, pescoco[1] + cai + onda))
    import pecas
    troca = pecas.TROCA or {}  # (roupa ou personagem que usa o desenho do Rib, tipo o Ribbat: o cachecol vira lenço)
    cor = (240, 240, 245) if branco else troca.get("x", PALETA["x"])
    pygame.draw.lines(tela, troca.get("k", PALETA["k"]), False, pts, max(3, int(4 * esc)))
    pygame.draw.lines(tela, cor, False, pts, max(1, int(2.4 * esc)))
    pygame.draw.line(tela, (240, 240, 245) if branco else troca.get("X", PALETA["X"]), pts[1], pts[3], 1)


def desenhar_rib(l, tela, p, branco):
    desenhar_clones(l, tela, branco)  # Kage Bunshin: os clones atrás dele
    esc = l.s / S_REF
    d = l.lado()
    espelho = d < 0
    perto_v = "branco" if branco else "normal"
    longe_v = "branco" if branco else "escuro"
    costas = l.vira

    def P(k):
        return l.ponto(p, k)

    def perna(pe, joelho, var):
        q, j, e = P("qd"), P(joelho), P(pe)
        CANELA.desenhar(tela, j, e, esc, espelho, var)
        fr, _ = frente_do_pe(j, e, d)
        PE.desenhar(tela, e, mais(e, fr, 10), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    def braco(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)

    longe, perto = (("cf", "mf", "pf", "jf"), ("ct", "mt", "pt", "jt")) if costas else \
        (("ct", "mt", "pt", "jt"), ("cf", "mf", "pf", "jf"))
    c, cb = P("pc"), P("cb")
    u, _ = cabeca_eixos(c, cb, d)
    _cachecol(l, tela, mais(c, u, 1.5 * esc), d, esc, branco)
    braco(longe[0], longe[1], longe_v)
    perna(longe[2], longe[3], longe_v)
    (TRONCO_COSTAS if costas else TRONCO).desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    perna(perto[2], perto[3], perto_v)
    (CABECA_COSTAS if costas else CABECA).desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    braco(perto[0], perto[1], perto_v)


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Detalhe do Rib grande na cutscene: os olhos de sapo saltados com pupila de gato e o cachecol."""
    cb, pc = P("cb"), P("pc")
    pts = [pc] + [(pc[0] - d * i * 8 * s, pc[1] + math.sin(t * 0.3 - i * 0.7) * i * 1.4 * s + i * s) for i in range(1, 9)]
    pygame.draw.lines(q, (22, 22, 28), False, pts, max(3, int(5 * s)))
    for ox in (-4, 4):
        e = (int(cb[0] + ox * s * d), int(cb[1] - 8 * s))
        pygame.draw.circle(q, cont, e, int(4.6 * s))
        pygame.draw.circle(q, (252, 214, 56), e, int(3.6 * s))
        pygame.draw.ellipse(q, (8, 8, 8), (e[0] - 0.6 * s, e[1] - 2.6 * s, 1.2 * s, 5.2 * s))


# =====================================================================
# ENTRADA: Kawarimi — um tronco no lugar dele, PUF, e ele aparece
# =====================================================================
def entrada(l, t, jogo):
    from golpes import misturar
    l.esconde = t < 34
    if t == 34:  # PUF!
        som.tocar("puf")
        jogo.tremer(6)
        for _ in range(22):
            a = random.uniform(0, math.tau)
            v = random.uniform(1, 4)
            jogo.faiscas.append([l.x + math.cos(a) * 20, l.y - 60 * l.s + math.sin(a) * 30, math.cos(a) * v,
                                 math.sin(a) * v - 1, random.randint(26, 40), (230, 230, 225), random.randint(8, 14)])
    if 34 <= t < 74:
        l.sobrepor = dict(POSES_RIB["r_selo"])
    elif t < 92:
        l.sobrepor = misturar(POSES_RIB["r_selo"], POSES_RIB["parado"], suave((t - 74) / 18))
    else:
        l.sobrepor = {}
    l.t += 1


def entrada_efeito(l, tela, t):
    """O tronco de madeira (parado, depois voando pra longe depois do puf)."""
    if t >= 70:
        return
    s = l.s
    if t < 34:
        cx, cy, ang = l.x, l.y - 45 * s, 0
    else:
        u = t - 34
        cx = l.x - l.dir * u * 6 * s
        cy = l.y - 45 * s - u * 7 * s + u * u * 0.35 * s
        ang = -l.dir * u * 0.25
    w, h = 26 * s, 80 * s
    pts = []
    for px, py in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append((cx + px * math.cos(ang) - py * math.sin(ang), cy + px * math.sin(ang) + py * math.cos(ang)))
    pygame.draw.polygon(tela, (120, 80, 44), pts)
    pygame.draw.polygon(tela, (60, 36, 18), pts, 4)
    for f in (0.3, 0.6):  # cascas
        a = (pts[0][0] + (pts[3][0] - pts[0][0]) * f, pts[0][1] + (pts[3][1] - pts[0][1]) * f)
        b = (pts[1][0] + (pts[2][0] - pts[1][0]) * f, pts[1][1] + (pts[2][1] - pts[1][1]) * f)
        pygame.draw.line(tela, (80, 52, 26), a, b, 3)
    topo = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
    pygame.draw.ellipse(tela, (200, 160, 100), (topo[0] - w / 2, topo[1] - 5 * s, w, 10 * s))
    pygame.draw.ellipse(tela, (140, 100, 60), (topo[0] - w / 4, topo[1] - 2.5 * s, w / 2, 5 * s), 2)



# =====================================================================
# VITÓRIA: selo, PUF, some, e volta de braços cruzados com folhas caindo
# =====================================================================
POSES_RIB["r_cruzado"] = dict(pt=(-14, 0), jt=(-22, 22), pf=(14, 0), jf=(24, 22), qd=(0, 42), pc=(6, 76), cb=(10, 94),
                              ct=(16, 70), mt=(-6, 74), cf=(18, 68), mf=(-4, 72))
proporcionar(POSES_RIB)


def vitoria(l, t, jogo):
    if t < 16:
        l.sobrepor = dict(POSES_RIB["r_selo"])
    l.esconde = 16 <= t < 40
    if t in (16, 40):
        som.tocar("puf")
        for _ in range(16):
            a = random.uniform(0, math.tau)
            jogo.faiscas.append([l.x + math.cos(a) * 16, l.y - 60 * l.s + math.sin(a) * 26, math.cos(a) * 2.5,
                                 math.sin(a) * 2.5 - 1, random.randint(24, 36), (230, 230, 225), random.randint(8, 13)])
    if t >= 40:
        l.sobrepor = dict(POSES_RIB["r_cruzado"])


def vitoria_efeito(l, tela, t):
    if t < 40:
        return
    rng = random.Random(4)
    for i in range(10):  # folhas caindo
        x = l.x + rng.uniform(-160, 160) + math.sin(t * 0.05 + i) * 20
        y = (rng.uniform(0, 300) + (t - 40) * rng.uniform(1.2, 2.2)) % (CHAO - 40) + 40
        pygame.draw.ellipse(tela, (90, 170, 70), (x, y, 9, 5))
