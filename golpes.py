"""Poses e golpes.

POSES: cada ponto do corpo é (pra frente, pra cima), em pixels, contando a partir dos pés.
  pt/jt = pé e joelho de trás     pf/jf = pé e joelho da frente
  qd = quadril   pc = peito   cb = cabeça
  ct/mt = cotovelo e mão de trás  cf/mf = cotovelo e mão da frente

GOLPES: tudo contado em quadros (60 = 1 segundo).
  ini   = quadros "preparando" (ainda não machuca)
  ativo = quadros que o golpe machuca
  rec   = quadros voltando (aqui ele fica aberto pro contra-ataque)
  caixa = onde o golpe acerta (frente1, cima1, frente2, cima2)
  dano  = quanto de vida tira (todo mundo tem 100)
  hit / defe = quanto tempo o outro fica tonto se levou / se defendeu
  nivel: "medio" (defende em pé ou agachado), "baixo" (só agachado), "alto" (só em pé)
"""
import math

POSES = {
    "parado": dict(pt=(-20, 0), jt=(-16, 28), pf=(20, 0), jf=(18, 30), qd=(0, 56), pc=(3, 92), cb=(6, 112),
                   ct=(-6, 74), mt=(10, 88), cf=(20, 76), mf=(30, 92)),
    # caminhada: 4 quadros (pé encosta, perna passa, outro pé encosta, outra perna passa)
    "andar1": dict(pt=(-22, 2), jt=(-14, 28), pf=(26, 0), jf=(22, 30), qd=(0, 53), pc=(4, 89), cb=(7, 109),
                   ct=(-6, 72), mt=(10, 86), cf=(20, 74), mf=(30, 90)),
    "andar2": dict(pt=(4, 12), jt=(12, 34), pf=(2, 0), jf=(8, 30), qd=(0, 57), pc=(3, 93), cb=(6, 113),
                   ct=(-5, 75), mt=(11, 89), cf=(19, 77), mf=(29, 93)),
    "andar3": dict(pt=(24, 0), jt=(20, 30), pf=(-20, 2), jf=(-12, 28), qd=(0, 53), pc=(4, 89), cb=(7, 109),
                   ct=(-6, 72), mt=(10, 86), cf=(20, 74), mf=(30, 90)),
    "andar4": dict(pt=(0, 0), jt=(6, 30), pf=(6, 12), jf=(14, 34), qd=(0, 57), pc=(3, 93), cb=(6, 113),
                   ct=(-5, 75), mt=(11, 89), cf=(19, 77), mf=(29, 93)),
    # pulo em fases
    "prepulo": dict(pt=(-20, 0), jt=(-6, 22), pf=(20, 0), jf=(30, 24), qd=(0, 38), pc=(6, 72), cb=(10, 92),
                    ct=(-4, 56), mt=(10, 70), cf=(18, 58), mf=(28, 72)),
    "pulo_sobe": dict(pt=(-8, 0), jt=(-6, 28), pf=(6, -4), jf=(6, 26), qd=(0, 56), pc=(4, 92), cb=(6, 112),
                      ct=(-8, 80), mt=(4, 98), cf=(16, 84), mf=(26, 102)),
    "pulo_desce": dict(pt=(-16, 2), jt=(-8, 28), pf=(14, 0), jf=(18, 30), qd=(0, 54), pc=(3, 88), cb=(5, 108),
                       ct=(-14, 80), mt=(-4, 94), cf=(22, 82), mf=(34, 96)),
    "pouso": dict(pt=(-22, 0), jt=(-8, 24), pf=(22, 0), jf=(32, 26), qd=(0, 40), pc=(5, 74), cb=(9, 94),
                  ct=(-8, 58), mt=(8, 70), cf=(18, 60), mf=(30, 72)),
    "agachado": dict(pt=(-22, 0), jt=(-8, 22), pf=(22, 0), jf=(32, 24), qd=(0, 30), pc=(6, 62), cb=(10, 82),
                     ct=(-2, 48), mt=(14, 60), cf=(22, 50), mf=(30, 64)),
    "pulo": dict(pt=(-10, 12), jt=(4, 28), pf=(14, 14), jf=(22, 32), qd=(0, 46), pc=(2, 80), cb=(4, 100),
                 ct=(-8, 62), mt=(8, 74), cf=(16, 64), mf=(26, 80)),
    "soco": dict(pt=(-24, 0), jt=(-18, 28), pf=(20, 0), jf=(20, 30), qd=(0, 56), pc=(8, 90), cb=(12, 110),
                 ct=(-8, 74), mt=(2, 82), cf=(38, 88), mf=(66, 90)),
    "chute": dict(pt=(-16, 0), jt=(-14, 28), pf=(70, 66), jf=(38, 56), qd=(-2, 56), pc=(-12, 88), cb=(-14, 108),
                  ct=(-20, 74), mt=(-8, 86), cf=(2, 76), mf=(12, 88)),
    "ag_soco": dict(pt=(-22, 0), jt=(-8, 22), pf=(22, 0), jf=(32, 24), qd=(0, 30), pc=(10, 60), cb=(14, 80),
                    ct=(0, 46), mt=(10, 54), cf=(36, 58), mf=(64, 60)),
    "ag_chute": dict(pt=(-30, 0), jt=(-14, 16), pf=(74, 4), jf=(42, 10), qd=(0, 24), pc=(-6, 52), cb=(-8, 72),
                     ct=(-14, 38), mt=(-24, 6), cf=(4, 40), mf=(14, 30)),
    "ar_soco": dict(pt=(-10, 12), jt=(4, 28), pf=(14, 14), jf=(22, 32), qd=(0, 46), pc=(6, 80), cb=(8, 100),
                    ct=(-8, 62), mt=(4, 70), cf=(26, 62), mf=(48, 50)),
    "ar_chute": dict(pt=(-12, 18), jt=(0, 30), pf=(58, 6), jf=(32, 26), qd=(0, 46), pc=(-6, 80), cb=(-6, 100),
                     ct=(-14, 64), mt=(-4, 76), cf=(10, 66), mf=(20, 80)),
    "especial": dict(pt=(-30, 0), jt=(-22, 28), pf=(26, 0), jf=(24, 30), qd=(-2, 52), pc=(10, 86), cb=(14, 104),
                     ct=(24, 76), mt=(48, 78), cf=(30, 82), mf=(52, 84)),
    "subida": dict(pt=(-12, 6), jt=(-8, 30), pf=(8, 0), jf=(10, 28), qd=(0, 56), pc=(6, 92), cb=(10, 110),
                   ct=(-6, 74), mt=(4, 86), cf=(20, 118), mf=(24, 144)),
    "giro": dict(pt=(-52, 62), jt=(-26, 60), pf=(62, 70), jf=(32, 64), qd=(0, 60), pc=(0, 94), cb=(0, 114),
                 ct=(-16, 92), mt=(-32, 96), cf=(16, 92), mf=(32, 96)),
    "avanco": dict(pt=(-34, 0), jt=(-22, 26), pf=(26, 0), jf=(28, 32), qd=(0, 50), pc=(24, 80), cb=(32, 96),
                   ct=(16, 72), mt=(28, 62), cf=(32, 78), mf=(40, 64)),
    "ultimate": dict(pt=(-34, 0), jt=(-26, 26), pf=(30, 0), jf=(28, 30), qd=(-4, 50), pc=(4, 86), cb=(6, 106),
                     ct=(26, 88), mt=(54, 92), cf=(28, 84), mf=(56, 86)),
    "golpeado": dict(pt=(-22, 0), jt=(-18, 28), pf=(16, 0), jf=(12, 28), qd=(-6, 54), pc=(-16, 86), cb=(-22, 102),
                     ct=(-24, 72), mt=(-30, 86), cf=(-6, 70), mf=(4, 80)),
    "defesa": dict(pt=(-22, 0), jt=(-18, 28), pf=(18, 0), jf=(16, 30), qd=(-2, 56), pc=(0, 90), cb=(2, 110),
                   ct=(14, 78), mt=(26, 98), cf=(18, 82), mf=(22, 102)),
    "ag_defesa": dict(pt=(-22, 0), jt=(-8, 22), pf=(22, 0), jf=(32, 24), qd=(-2, 30), pc=(2, 60), cb=(6, 80),
                      ct=(16, 50), mt=(26, 68), cf=(20, 54), mf=(24, 72)),
    "voando": dict(pt=(26, 36), jt=(12, 38), pf=(30, 48), jf=(16, 46), qd=(0, 40), pc=(-26, 52), cb=(-44, 58),
                   ct=(-28, 62), mt=(-36, 74), cf=(-18, 64), mf=(-10, 76)),
    "caido": dict(pt=(26, 2), jt=(14, 10), pf=(32, 4), jf=(18, 14), qd=(0, 6), pc=(-32, 6), cb=(-52, 8),
                  ct=(-30, 2), mt=(-42, 2), cf=(-20, 4), mf=(-10, 2)),
    "vitoria": dict(pt=(-20, 0), jt=(-16, 28), pf=(20, 0), jf=(18, 30), qd=(0, 56), pc=(3, 92), cb=(6, 112),
                    ct=(-6, 74), mt=(-4, 54), cf=(14, 114), mf=(18, 138)),
}

GOLPES = {
    "soco":     dict(pose="soco", base="parado", ini=4, ativo=3, rec=8, caixa=(28, 74, 74, 102),
                     dano=5, hit=15, defe=10, emp=4, nivel="medio"),
    "chute":    dict(pose="chute", base="parado", ini=7, ativo=4, rec=14, caixa=(36, 48, 84, 82),
                     dano=8, hit=18, defe=12, emp=6, nivel="medio"),
    "ag_soco":  dict(pose="ag_soco", base="agachado", ini=4, ativo=3, rec=8, caixa=(26, 46, 72, 72),
                     dano=4, hit=14, defe=9, emp=4, nivel="medio"),
    "ag_chute": dict(pose="ag_chute", base="agachado", ini=7, ativo=4, rec=20, caixa=(30, 0, 84, 22),
                     dano=7, hit=16, defe=10, emp=5, nivel="baixo", derruba=True),
    "ar_soco":  dict(pose="ar_soco", base="pulo", ini=4, ativo=8, rec=6, caixa=(20, 30, 60, 66),
                     dano=6, hit=16, defe=10, emp=3, nivel="alto", aereo=True),
    "ar_chute": dict(pose="ar_chute", base="pulo", ini=6, ativo=10, rec=6, caixa=(26, -4, 70, 32),
                     dano=8, hit=18, defe=11, emp=4, nivel="alto", aereo=True),
    # ---- especiais ----
    "bola":     dict(pose="especial", base="parado", ini=12, ativo=2, rec=22, caixa=None,
                     dano=9, hit=18, defe=12, emp=5, nivel="medio", proj=True, especial=True, raio=15, vel=7, ia="longe"),
    "subida":   dict(pose="subida", base="parado", ini=3, ativo=12, rec=24, caixa=(0, 60, 46, 150), ia="anti",
                     dano=12, hit=20, defe=14, emp=3, nivel="medio", derruba=True,
                     sobe=-15, avanca=2.5, inv=8, especial=True),
    "giro":     dict(pose="giro", base="parado", ini=6, ativo=22, rec=12, caixa=(-50, 46, 70, 86), ia="medio",
                     dano=10, hit=18, defe=12, emp=6, nivel="medio", derruba=True, avanca=5, especial=True),
    "avanco":   dict(pose="avanco", base="parado", ini=8, ativo=16, rec=16, caixa=(10, 40, 52, 100), ia="medio",
                     dano=10, hit=18, defe=12, emp=7, nivel="medio", derruba=True, avanca=8, especial=True),
    # ---- ultimate (M3 + Z, só com a barra cheia) ----
    "ultimate": dict(pose="ultimate", base="parado", ini=10, ativo=2, rec=30, caixa=None,
                     dano=30, hit=24, defe=20, emp=8, nivel="medio", derruba=True, especial=True, ultimate=True,
                     proj=True, raio=42, vel=10, ia="ultimate"),
}
for _g in GOLPES.values():
    _g["total"] = _g["ini"] + _g["ativo"] + _g["rec"]


def suave(t):
    """Começa devagar, acelera e chega devagar (fica mais bonito que andar reto)."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def misturar(a, b, t):
    """Mistura duas poses (t=0 é a primeira, t=1 é a segunda)."""
    return {k: (a[k][0] + (b[k][0] - a[k][0]) * t, a[k][1] + (b[k][1] - a[k][1]) * t) for k in a}


# =====================================================================
# Proporção de gente de verdade
# =====================================================================
# Cada pose foi desenhada à mão, mas o tamanho dos ossos é ajustado aqui:
# mantém o ÂNGULO de cada osso e troca só o COMPRIMENTO (uns 7,5 "cabeças" de altura).
OSSOS = [("qd", "jt", 32), ("jt", "pt", 31), ("qd", "jf", 32), ("jf", "pf", 31),
         ("qd", "pc", 42), ("pc", "cb", 16),
         ("pc", "ct", 24), ("ct", "mt", 22), ("pc", "cf", 24), ("cf", "mf", 22)]
_ajustadas = set()


def proporcionar(poses):
    for nome, p in poses.items():
        if id(p) in _ajustadas:
            continue
        _ajustadas.add(id(p))
        novo = {"qd": p["qd"]}
        for a, b, comp in OSSOS:
            dx, dy = p[b][0] - p[a][0], p[b][1] - p[a][1]
            d = math.hypot(dx, dy) or 1
            novo[b] = (novo[a][0] + dx / d * comp, novo[a][1] + dy / d * comp)
        # os pés continuam encostando no chão
        desce = min(novo["pt"][1], novo["pf"][1]) - min(p["pt"][1], p["pf"][1])
        p.update({k: (x, y - desce) for k, (x, y) in novo.items()})


proporcionar(POSES)



# ---- pedaços do EX (valem pra todo mundo) ----
def _ex_volta(l, outro, jogo):
    """EX do SHIFT: depois do dash pra frente, um dash pra trás."""
    if l.t < 14:
        l.vx = -12 * l.dir
        l.inv = 2
    else:
        l.vx *= 0.6
    l.fisica(jogo)
    if l.t >= 20:
        return "fim"


GOLPES["ex_rasteira"] = dict(base="agachado", pose="ag_chute", ini=4, ativo=5, rec=4, caixa=(16, 0, 92, 30), dano=4,
                             hit=22, defe=10, emp=1, nivel="baixo", especial=True, total=13)
GOLPES["ex_volta"] = dict(base="parado", pose="parado", ini=0, ativo=0, rec=0, caixa=None, dano=0, hit=0, defe=0, emp=0,
                          nivel="medio", especial=True, logica=_ex_volta, total=20,
                          quadros=[(0, "pulo_desce"), (12, "pulo_desce"), (20, "parado")])
