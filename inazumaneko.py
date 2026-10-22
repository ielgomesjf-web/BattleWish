"""INAZUMANEKO: o tigre samurai ("gato-relâmpago") — criado pelo Gomes pra v3.0.

Aparência: tigre-gato de pé (corpo de guerreiro), pelo CINZA com listras pretas (pedido do Gomes), quimono azul-escuro com ombreiras e placa
vermelha e dourada, faixa branca, hakama preta, DUAS KATANAS na cintura e uma cicatriz no olho. Função: DUELISTA de contra-golpe
(forte de perto e no meio; fraco contra quem atira de longe — o contra-ataque não segura tiro).
  E      CORTE DE VENTO: saca, corte VERTICAL e sai a MEIA-LUA (10); guarda a espada
  Q      CONTRA-ATAQUE: postura de meio segundo; se apanhar (de perto), desvia e revida (15). Errou = fica aberto
  R      DANÇA TROVEJANTE: espada pra frente, 8 golpes de 2
  SHIFT  PASSO RELÂMPAGO: atravessa o adversário num piscar de olhos, cortando (6)
  Z      ULTIMATE: CORTE SAMURAI — respira 1 s (não dá pra defender nem interromper: só FUGIR), corta ao meio;
         se pegou, saca a 2ª katana e dá a espadada em X (45). Não pega quem está no chão.
  Z2     2ª ULTIMATE: MIL CORTES — a tela escurece, ele aparece atrás, guarda a espada... *clic* (50 + tontura)
  Passivas (H na seleção): FÚRIA SAMURAI / PODER SAMURAI (em habilidades.py)
  Rival: RIB (ninja x samurai). Casa: MONTE KARASUMA.
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

POSES_INAZUMANEKO = {
    # (de lado, virado pra direita; a mão da FRENTE fica no cabo da katana da cintura)
    "parado": dict(pt=(-20, 0), jt=(-14, 28), pf=(20, 0), jf=(24, 28), qd=(0, 52), pc=(4, 90), cb=(8, 108),
                   ct=(-4, 72), mt=(4, 60), cf=(16, 76), mf=(12, 62)),
    "andar1": dict(pt=(-26, 2), jt=(-16, 28), pf=(24, 0), jf=(26, 28), qd=(0, 50), pc=(4, 88), cb=(8, 106),
                   ct=(-6, 72), mt=(2, 58), cf=(16, 74), mf=(12, 60)),
    "andar2": dict(pt=(-8, 6), jt=(-2, 30), pf=(10, 0), jf=(16, 28), qd=(0, 54), pc=(4, 92), cb=(8, 110),
                   ct=(-4, 74), mt=(4, 62), cf=(16, 78), mf=(12, 64)),
    "andar3": dict(pt=(24, 0), jt=(26, 28), pf=(-26, 2), jf=(-16, 28), qd=(0, 50), pc=(4, 88), cb=(8, 106),
                   ct=(-6, 72), mt=(2, 58), cf=(16, 74), mf=(12, 60)),
    "andar4": dict(pt=(10, 0), jt=(16, 28), pf=(-8, 6), jf=(-2, 30), qd=(0, 54), pc=(4, 92), cb=(8, 110),
                   ct=(-4, 74), mt=(4, 62), cf=(16, 78), mf=(12, 64)),
    # E: saca lá em cima -> corte vertical -> guarda
    "i_saca": dict(pt=(-20, 0), jt=(-14, 28), pf=(22, 0), jf=(24, 28), qd=(0, 54), pc=(2, 92), cb=(6, 110),
                   ct=(4, 100), mt=(14, 120), cf=(12, 102), mf=(20, 122)),
    "i_corta": dict(pt=(-26, 0), jt=(-16, 26), pf=(26, 0), jf=(30, 28), qd=(0, 48), pc=(12, 84), cb=(18, 100),
                    ct=(22, 78), mt=(42, 62), cf=(28, 82), mf=(46, 64)),
    "i_guarda": dict(pt=(-20, 0), jt=(-14, 28), pf=(20, 0), jf=(24, 28), qd=(0, 52), pc=(4, 90), cb=(8, 108),
                     ct=(-6, 72), mt=(2, 60), cf=(18, 78), mf=(10, 64)),
    # Q: a postura do contra-ataque (baixa, mão no cabo) e o revide
    "i_contra": dict(pt=(-26, 0), jt=(-18, 22), pf=(24, 0), jf=(26, 24), qd=(0, 42), pc=(-2, 78), cb=(2, 96),
                     ct=(-10, 62), mt=(2, 52), cf=(12, 66), mf=(14, 54)),
    "i_revida": dict(pt=(-30, 0), jt=(-16, 24), pf=(30, 0), jf=(34, 26), qd=(0, 44), pc=(14, 80), cb=(22, 94),
                     ct=(2, 70), mt=(-6, 56), cf=(36, 86), mf=(62, 84)),
    # R: a espada pra frente, balançando (alto / baixo)
    "i_danca_a": dict(pt=(-24, 0), jt=(-14, 26), pf=(24, 0), jf=(28, 28), qd=(0, 50), pc=(8, 88), cb=(14, 106),
                      ct=(20, 84), mt=(38, 90), cf=(30, 88), mf=(54, 96)),
    "i_danca_b": dict(pt=(-24, 0), jt=(-14, 26), pf=(24, 0), jf=(28, 28), qd=(0, 50), pc=(8, 88), cb=(14, 106),
                      ct=(20, 78), mt=(38, 68), cf=(30, 80), mf=(54, 70)),
    # SHIFT: o passo relâmpago (agachado, a espada pra trás depois do corte)
    "i_passo": dict(pt=(-36, 4), jt=(-18, 22), pf=(26, 0), jf=(24, 26), qd=(0, 40), pc=(20, 72), cb=(32, 84),
                    ct=(8, 64), mt=(-10, 58), cf=(16, 66), mf=(-14, 72)),
    # Z: respira com a espada pra frente -> corta ao meio -> balança as duas pra trás -> X
    "i_respira": dict(pt=(-22, 0), jt=(-14, 28), pf=(22, 0), jf=(24, 28), qd=(0, 52), pc=(2, 90), cb=(6, 108),
                      ct=(14, 80), mt=(30, 86), cf=(22, 82), mf=(42, 88)),
    "i_x_tras": dict(pt=(-24, 0), jt=(-14, 26), pf=(24, 0), jf=(26, 28), qd=(0, 50), pc=(0, 88), cb=(4, 106),
                     ct=(-18, 94), mt=(-38, 110), cf=(-14, 96), mf=(-32, 116)),
    "i_x": dict(pt=(-28, 0), jt=(-16, 26), pf=(28, 0), jf=(32, 28), qd=(0, 48), pc=(14, 84), cb=(20, 100),
                ct=(28, 80), mt=(52, 60), cf=(28, 92), mf=(52, 114)),
    "i_embainha": dict(pt=(-20, 0), jt=(-14, 28), pf=(20, 0), jf=(24, 28), qd=(0, 52), pc=(2, 90), cb=(6, 108),
                       ct=(-4, 66), mt=(6, 60), cf=(16, 80), mf=(18, 66)),
    "i_curva": dict(pt=(-18, 0), jt=(-12, 28), pf=(18, 0), jf=(22, 28), qd=(0, 50), pc=(12, 84), cb=(22, 96),
                    ct=(2, 68), mt=(8, 56), cf=(14, 70), mf=(10, 58)),
    # (as poses do MEIO dos movimentos: deixam o espadachim FLUIDO — pedido do Gomes)
    "i_mao_cabo": dict(pt=(-22, 0), jt=(-16, 24), pf=(22, 0), jf=(26, 26), qd=(0, 46), pc=(6, 84), cb=(12, 100),
                       ct=(-2, 68), mt=(8, 56), cf=(18, 72), mf=(14, 58)),
    "i_saca_meio": dict(pt=(-22, 0), jt=(-16, 26), pf=(22, 0), jf=(26, 28), qd=(0, 50), pc=(4, 88), cb=(8, 106),
                        ct=(8, 84), mt=(22, 96), cf=(20, 88), mf=(32, 100)),
    "i_corta_fim": dict(pt=(-28, 0), jt=(-16, 24), pf=(28, 0), jf=(32, 26), qd=(0, 44), pc=(16, 78), cb=(22, 94),
                        ct=(20, 68), mt=(32, 48), cf=(26, 70), mf=(38, 46)),
    "i_chiburi": dict(pt=(-24, 0), jt=(-16, 26), pf=(24, 0), jf=(28, 28), qd=(0, 48), pc=(6, 86), cb=(10, 104),
                      ct=(-6, 70), mt=(2, 58), cf=(30, 80), mf=(50, 72)),
    "i_revida_fim": dict(pt=(-30, 0), jt=(-16, 24), pf=(32, 0), jf=(36, 26), qd=(0, 44), pc=(16, 80), cb=(24, 92),
                         ct=(0, 70), mt=(-10, 58), cf=(30, 90), mf=(16, 110)),
    "i_passo_fim": dict(pt=(-30, 2), jt=(-16, 22), pf=(28, 0), jf=(26, 24), qd=(0, 42), pc=(12, 76), cb=(20, 92),
                        ct=(4, 66), mt=(-8, 60), cf=(8, 70), mf=(-16, 80)),
    "i_pouso": dict(pt=(-24, 0), jt=(-20, 14), pf=(22, 0), jf=(26, 22), qd=(0, 30), pc=(10, 62), cb=(18, 76),
                    ct=(-4, 50), mt=(4, 40), cf=(26, 30), mf=(30, 4)),
    "i_equilibra": dict(pt=(-20, 0), jt=(-14, 28), pf=(20, 0), jf=(24, 28), qd=(0, 52), pc=(4, 90), cb=(10, 108),
                        ct=(-6, 72), mt=(2, 60), cf=(20, 96), mf=(22, 116)),
    "i_x_fim": dict(pt=(-28, 0), jt=(-16, 24), pf=(28, 0), jf=(32, 26), qd=(0, 44), pc=(16, 80), cb=(22, 96),
                    ct=(30, 66), mt=(46, 46), cf=(30, 76), mf=(50, 60)),
}
proporcionar(POSES_INAZUMANEKO)

AZUL_RAIO = (170, 220, 255)
AMARELO_RAIO = (255, 236, 120)
LAMINA = (226, 232, 242)


def outro_de(l, jogo):
    return jogo.L[1] if jogo.L[0] is l else jogo.L[0]


def acerto(jogo, l, outro, nome, registro=None):
    """Um acerto feito pela LÓGICA do golpe (passo / revide), mas tratado IGUAL a um acerto normal da partida:
    conta o combo e o treino (registrar_hit), mostra o COMBO, faz parry/guarda quebrada, som, faísca e parada.
    registro = (nome do golpe, ativação) pra contar no treino quando o golpe já acabou (a nuvem do Nocturnus)."""
    g = GOLPES[nome]
    sinal = 1 if outro.x > l.x else -1
    res = outro.receber(g, sinal, l, l.f["forca"])
    if res == "esquiva" or not hasattr(jogo, "L"):
        return res
    l.acertou = True
    ponto = (outro.x, outro.y - 60 * outro.s)
    if res == "hit" and outro is jogo.L[1] and hasattr(jogo, "registrar_hit"):
        jogo.golpes_treino += 1
        jogo.registrar_hit(l, *(registro or (l.nome_golpe, getattr(l, "golpe_id", 0))))
    if res == "quebrou" and hasattr(jogo, "guarda_quebrada"):
        jogo.guarda_quebrada(outro, ponto)
        return res
    if res == "parry" and hasattr(jogo, "parry"):
        jogo.parry(outro, ponto)
        return res
    if hasattr(jogo, "som_do_golpe"):
        jogo.som_do_golpe(res, g)
    jogo.faisca(ponto[0], ponto[1], res == "def", g["dano"] >= 10)
    if hasattr(jogo, "parada"):
        jogo.parada = max(jogo.parada, PARADA_GOLPE if res == "hit" else 4)
    if res == "hit":
        jogo.tremer(5 if g["dano"] < 8 else 9)
        if l.combo >= 2 and hasattr(jogo, "combo_txt"):
            jogo.combo_txt = (jogo.L.index(l), l.combo, 70)
    return res


def faisca_raio(jogo, x, y, n=6, cor=AMARELO_RAIO):
    """Faisquinhas de raio (amarelas/azuladas) saindo de um ponto."""
    for _ in range(n):
        a = random.uniform(0, math.tau)
        v = random.uniform(2, 6)
        jogo.faiscas.append([x, y, math.cos(a) * v, math.sin(a) * v, random.randint(8, 14),
                             random.choice((cor, AZUL_RAIO, (255, 255, 255))), 3])


# =====================================================================
# E: CORTE DE VENTO — a meia-lua (vertical) voando
# =====================================================================
E_SACA, E_SOLTA, E_GUARDA, E_FIM = 8, 13, 26, 36


def corte_vento(l, outro, jogo):
    t = l.t
    l.vx = 0
    l.fisica(jogo)
    if t == E_SACA:
        som.tocar("vento", 0.5)
    if t == E_SOLTA:  # o corte VERTICAL solta a meia-lua
        jogo.projeteis.append(Projetil(l, l.x + 44 * l.s * l.dir, l.y - 68 * l.s, l.dir, GOLPES["inaz_meia_lua"]))
        som.tocar("shuriken", 0.6)
    if t == E_GUARDA + 6:  # *clic* (guardou)
        som.tocar("defesa", 0.3)
    if t >= E_FIM:
        return "fim"


def desenha_meia_lua(p, tela):
    """A meia-lua de vento: um arco EM PÉ (o corte foi vertical), com rastros."""
    s = p.dono.s
    d = 1 if p.vx > 0 else -1
    alto = 40 * s
    for i in range(3):
        r = pygame.Rect(0, 0, (16 - i * 3) * s, alto * 2 - i * 6 * s)
        r.center = (int(p.x - d * i * 12 * s), int(p.y))
        ini = -1.25 if d > 0 else math.pi - 1.25
        cor = (255, 255, 255) if i == 0 else (AZUL_RAIO if i == 1 else (120, 170, 230))
        pygame.draw.arc(tela, cor, r, ini, ini + 2.5, max(2, int((4 - i) * s)))
    for k in range(3):  # os risquinhos de vento
        y = p.y + (k - 1) * 16 * s
        pygame.draw.line(tela, (210, 236, 255), (p.x - d * (26 + k * 5) * s, y), (p.x - d * (50 + k * 5) * s, y), 1)


# =====================================================================
# Q: CONTRA-ATAQUE — postura de meio segundo; a pegada é feita no habilidades.contra_samurai
# =====================================================================
C_INI, C_JANELA, C_ABERTO = 4, 30, 24  # (errou: fica parado e ABERTO um tempinho)
C_REVIDA = 4


def contra(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    if "pegou" in m:  # PEGOU! desvia pro lado dele e revida
        u = t - m["pegou"]
        if u == 1:
            som.tocar("parry")
            jogo.faisca(l.x + 20 * l.s * l.dir, l.y - 80 * l.s, False, True)
            frente = outro.x - l.dir * 52 * l.s  # (aparece colado nele, de frente)
            if abs(outro.x - l.x) > 60 * l.s:
                l.x = max(PAREDE_E, min(PAREDE_D, frente))
        if u == C_REVIDA:
            res = acerto(jogo, l, outro, "inaz_revide")
            som.tocar("shuriken", 0.8)
            if res == "hit":
                hab.furia_samurai(l, hab.FURIA_CONTRA)
        P_ = POSES_INAZUMANEKO
        if u < 2:
            l.sobrepor = dict(P_["i_contra"])
        elif u < C_REVIDA + 1:  # o corte saindo (rapidinho, mas misturando)
            l.sobrepor = misturar(P_["i_contra"], P_["i_revida"], suave((u - 2) / (C_REVIDA - 1)))
        elif u < C_REVIDA + 8:  # a lâmina continua o movimento
            l.sobrepor = misturar(P_["i_revida"], P_["i_revida_fim"], suave((u - C_REVIDA - 1) / 7))
        else:  # volta pra base
            l.sobrepor = misturar(P_["i_revida_fim"], P_["parado"], suave(min(1, (u - C_REVIDA - 8) / 12)))
        l.fisica(jogo)
        if u >= C_REVIDA + 20:
            l.sobrepor = {}
            return "fim"
        return
    l.fisica(jogo)
    if t >= C_INI + C_JANELA + C_ABERTO:  # ninguém bateu: ficou aberto e agora volta
        return "fim"


# =====================================================================
# R: DANÇA TROVEJANTE — 8 golpes de 2
# =====================================================================
D_INI, D_INTERVALO, D_HITS = 8, 5, 8


def danca(l, outro, jogo):
    t = l.t
    dentro = D_INI <= t < D_INI + D_HITS * D_INTERVALO
    l.vx = 0.7 * l.dir if dentro else 0
    if dentro and (t - D_INI) % D_INTERVALO == 0:
        som.tocar("vento", 0.35)
        p = l.pose_vista or l.pose_atual()
        x, y = l.ponto(p, "mf")
        faisca_raio(jogo, x + 30 * l.s * l.dir, y, 3)
    l.fisica(jogo)
    if t >= D_INI + D_HITS * D_INTERVALO + 12:
        return "fim"


def danca_quadros():
    q = [(0, "parado"), (D_INI - 2, "i_danca_a")]
    for k in range(D_HITS):
        q.append((D_INI + k * D_INTERVALO + 2, "i_danca_b" if k % 2 == 0 else "i_danca_a"))
    q.append((D_INI + D_HITS * D_INTERVALO + 12, "parado"))
    return q


# =====================================================================
# SHIFT: PASSO RELÂMPAGO — some e aparece do outro lado, cortando no caminho
# =====================================================================
P_INI, P_FIM = 7, 26
P_DISTANCIA = 230


def passo(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    if t == P_INI:
        ini = l.x
        fim = l.x + l.dir * P_DISTANCIA * l.s
        no_caminho = min(ini, fim) - 20 * l.s <= outro.x <= max(ini, fim) + 40 * l.s and abs(outro.y - l.y) < 90
        if no_caminho:  # passa ATRAVÉS dele e para do outro lado
            fim = outro.x + l.dir * 70 * l.s
        fim = max(PAREDE_E, min(PAREDE_D, fim))
        m["rastro"] = (ini, fim, l.y)
        l.x = fim
        l.inv = max(l.inv, 10)
        som.tocar("vento", 0.8)
        faisca_raio(jogo, ini, l.y - 60 * l.s, 8)
        faisca_raio(jogo, fim, l.y - 60 * l.s, 8)
        if no_caminho and outro.inv <= 0 and outro.estado not in ("caido", "agarrado"):
            acerto(jogo, l, outro, "inaz_passo_corte")
    l.fisica(jogo)
    if t >= P_FIM:
        if (outro.x - l.x) * l.dir < 0:  # (passou: vira pra ele)
            l.dir = -l.dir
        return "fim"


def passo_efeito(l, tela):
    """O TROVÃOZINHO entre onde ele estava e onde apareceu (pedido do Gomes): raio em zigue-zague com galhos,
    brilho azul em volta, miolo branco, clarão nas duas pontas e piscando antes de sumir. (Só desenho.)"""
    r = l.memo.get("rastro")
    u = l.t - P_INI
    if not r or u < 0 or u > 14:
        return
    if 4 <= u < 10 and u % 2 == 1:  # (pisca)
        return
    ini, fim, y = r
    s = l.s
    rnd = random.Random(int(ini * 7 + fim))
    meio_y = y - 62 * s

    def zigue(a, b, n, abre):
        pts = [a]
        for i in range(1, n):
            k = i / n
            pts.append((a[0] + (b[0] - a[0]) * k + rnd.uniform(-4, 4) * s,
                        a[1] + (b[1] - a[1]) * k + rnd.uniform(-abre, abre) * s))
        pts.append(b)
        return pts

    tronco = zigue((ini, meio_y), (fim, meio_y), 12, 22)
    galhos = []
    for _ in range(3):  # os galhinhos saindo do raio
        base = tronco[rnd.randint(2, 9)]
        ponta = (base[0] + rnd.uniform(-30, 30) * s, base[1] + rnd.choice((-1, 1)) * rnd.uniform(18, 34) * s)
        galhos.append(zigue(base, ponta, 4, 6))
    some = max(0.0, 1 - u / 14)
    camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
    for pts, w in [(tronco, 1.0)] + [(g, 0.5) for g in galhos]:
        pygame.draw.lines(camada, (90, 150, 255, int(90 * some)), False, pts, max(3, int(12 * w * s)))  # o brilho
        pygame.draw.lines(camada, (*AZUL_RAIO, int(220 * some)), False, pts, max(2, int(5 * w * s)))
        pygame.draw.lines(camada, (255, 255, 255, int(255 * some)), False, pts, max(1, int(2 * w * s)))  # o miolo
    tela.blit(camada, (0, 0))
    if u < 6:  # o CLARÃO onde sumiu e onde apareceu
        for x in (ini, fim):
            brilho(tela, (int(x), int(meio_y)), int((30 + u * 6) * s), (200, 230, 255), int(200 * some))


# =====================================================================
# Z: CORTE SAMURAI — respira (1 s), corte ao meio; pegou = saca a 2ª e espadada em X
# =====================================================================
U_RESPIRA = 60
U_MEIO, U_TRAS, U_X, U_FIM = 10, 22, 30, 60
U_DANO = 45
U_ALCANCE = 120


def ultimate(l, outro, jogo):
    t = l.t
    m = l.memo
    l.vx = 0
    l.inv = 999  # (não dá pra interromper: só fugir)
    if "pegou" in m:
        import ult2
        u = t - m["pegou"]
        if u < U_X + 20:  # a câmera fica nos dois (e chega mais perto no X)
            ult2.camera(jogo, 1.25 if u < U_X else 1.4, (l.x + outro.x) / 2, l.y - 80 * l.s)
        return corte_x(l, outro, jogo, u)
    import ult2
    if t < U_RESPIRA:  # RESPIRA (a câmera vai chegando nele, a lâmina vai brilhando)
        k = t / U_RESPIRA
        ult2.camera(jogo, 1.0 + 0.4 * suave(k), l.x + 30 * l.s * l.dir, l.y - 90 * l.s)
        if t % 20 == 0:
            som.tocar("vento", 0.3)
        if t == U_RESPIRA - 10:  # o OLHO brilha
            som.tocar("parry", 0.5)
        l.fisica(jogo)
        return
    if t == U_RESPIRA:  # O CORTE AO MEIO (um risco branco cruzando a tela toda)
        som.tocar("shuriken", 1.0)
        if hasattr(jogo, "clarao"):
            jogo.clarao = max(jogo.clarao, 4)
        perto = 0 < (outro.x - l.x) * l.dir < U_ALCANCE * l.s + 30
        pega = (perto and outro.inv <= 0 and outro.estado not in ("caido", "voando", "agarrado")
                and outro.y > CHAO - 90 and outro.vida > 0)
        if pega:
            m["pegou"] = t
            outro.mudar("agarrado")
            outro.golpe = None
            outro.sobrepor = dict(outro.poses["golpeado"])
            outro.vx = outro.vy = 0
            jogo.faisca(outro.x, outro.y - 70 * outro.s, False, True)
            if hasattr(jogo, "parada"):
                jogo.parada = max(jogo.parada, 8)
            jogo.tremer(10)
            return
        m["errou"] = t
    l.fisica(jogo)
    if t >= U_RESPIRA + 30:  # errou: fica parado um pouquinho
        l.inv = 0
        return "fim"


def corte_x(l, outro, jogo, u):
    P_ = POSES_INAZUMANEKO
    if u < U_MEIO:  # o corte ao meio seguindo até embaixo
        l.sobrepor = misturar(P_["i_corta"], P_["i_corta_fim"], suave(u / U_MEIO))
    elif u < U_TRAS:  # saca a 2ª katana e balança as duas pra trás
        if u == U_MEIO:
            som.tocar("vento", 0.7)
        l.sobrepor = misturar(P_["i_corta_fim"], P_["i_x_tras"], suave((u - U_MEIO) / (U_TRAS - U_MEIO)))
    elif u < U_X:  # as duas lá atrás... e vem vindo
        l.sobrepor = misturar(P_["i_x_tras"], P_["i_x"], suave((u - U_TRAS) / (U_X - U_TRAS)) * 0.35)
    elif u == U_X:  # ESPADADA EM X
        l.sobrepor = dict(P_["i_x"])
        outro.levar(U_DANO, l, GOLPES["inaz_ultimate"])
        outro.tremor_hit = 14
        outro.sobrepor = {}
        outro.mudar("voando")
        outro.vx, outro.vy = 9 * l.dir, -9
        if hasattr(jogo, "parada"):
            jogo.parada = max(jogo.parada, 12)
        jogo.tremer(22)
        som.tocar("explosao", 0.6)
        som.tocar("ko", 0.5)
        faisca_raio(jogo, outro.x, outro.y - 70 * outro.s, 20)
    elif u < U_FIM:
        l.sobrepor = misturar(P_["i_x"], P_["i_x_fim"], suave((u - U_X) / 8)) if u < U_X + 16 else \
            misturar(P_["i_x_fim"], P_["parado"], suave((u - U_X - 16) / 14))
    else:
        l.sobrepor = {}
        l.inv = 0
        return "fim"
    l.fisica(jogo)


def ultimate_efeito(l, tela):
    t = l.t
    m = l.memo
    p = l.pose_vista or l.pose_atual()
    if U_RESPIRA - 10 <= t < U_RESPIRA - 2:  # o BRILHO NO OLHO (estrelinha)
        cx, cy = l.ponto(p, "cb")
        x, y = cx + 8 * l.s * l.dir, cy - 2 * l.s
        r = (8 - abs(t - (U_RESPIRA - 6)) * 1.6) * l.s
        for a in (0, math.pi / 2):
            pygame.draw.line(tela, (255, 240, 180), (x - math.cos(a) * r * 2, y - math.sin(a) * r * 2),
                             (x + math.cos(a) * r * 2, y + math.sin(a) * r * 2), max(1, int(2 * l.s)))
    if U_RESPIRA <= t < U_RESPIRA + 6:  # o CORTE cruzando a TELA TODA
        k = (t - U_RESPIRA) / 6
        y = l.y - 70 * l.s
        camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        pygame.draw.line(camada, (255, 255, 255, int(255 * (1 - k))), (0, y), (tela.get_width(), y + 30 * l.s * l.dir),
                         max(3, int((7 - 4 * k) * l.s)))
        tela.blit(camada, (0, 0))
    if "pegou" not in m and t < U_RESPIRA:  # a lâmina brilhando cada vez mais (o aviso pra FUGIR)
        x, y = l.ponto(p, "mf")
        k = t / U_RESPIRA
        brilho(tela, (int(x + 24 * l.s * l.dir), int(y)), int((10 + 30 * k) * l.s), (255, 255, 255), int(60 + 140 * k))
        for i in range(3):  # o ar entrando (respiração)
            a = t * 0.15 + i * 2.1
            r = (60 - 40 * ((t * 2 + i * 20) % 60) / 60) * l.s
            cx, cy = l.ponto(p, "cb")
            pygame.draw.circle(tela, (230, 240, 255), (int(cx + math.cos(a) * r), int(cy + math.sin(a) * r)), 2)
    if "pegou" in m:
        u = t - m["pegou"]
        alvo_x = l.x + 70 * l.s * l.dir
        if u < 12:  # o risco do corte ao meio
            y0 = l.y - 140 * l.s
            pygame.draw.line(tela, (255, 255, 255), (alvo_x, y0), (alvo_x + 6 * l.dir, l.y), max(2, int(4 * l.s)))
        if U_X <= u < U_X + 14:  # o X
            for sgn in (-1, 1):
                pygame.draw.line(tela, (255, 255, 255), (alvo_x - 40 * l.s, l.y - (70 + sgn * 50) * l.s),
                                 (alvo_x + 40 * l.s, l.y - (70 - sgn * 50) * l.s), max(3, int(6 * l.s)))
                pygame.draw.line(tela, AZUL_RAIO, (alvo_x - 44 * l.s, l.y - (70 + sgn * 54) * l.s),
                                 (alvo_x + 44 * l.s, l.y - (70 - sgn * 54) * l.s), max(1, int(2 * l.s)))


# =====================================================================
# Z2: MIL CORTES (a 2ª ultimate — o ult2.py pluga: logica=mil_cortes, efeito=mil_cortes_efeito)
# =====================================================================
M_ESCURO, M_APARECE, M_CORTES, M_CLIC, M_FIM = 20, 26, 70, 100, 130
M_DANO = 50
M_TONTO = 30  # tontura de meio segundo


def mil_cortes(l, outro, jogo):
    import ult2
    t = l.t
    m = l.memo
    ult2.tela_toda(l)
    l.vx = 0
    l.inv = 999
    if t < M_ESCURO:  # respira (zoom nele)
        ult2.camera(jogo, 1.35, l.x, l.y - 90 * l.s)
        l.sobrepor = dict(POSES_INAZUMANEKO["i_respira"])
    elif t == M_APARECE:  # SOME e APARECE ATRÁS dele
        if ult2.pode_pegar(outro, 200):
            m["pegou"] = True
            ult2.pega(outro)
        atras = outro.x + (1 if outro.x >= l.x else -1) * 80 * l.s
        l.x = max(PAREDE_E, min(PAREDE_D, atras))
        l.dir = 1 if outro.x > l.x else -1
        som.tocar("vento", 1.0)
    elif M_APARECE < t < M_CORTES:  # de costas pra ele, a espada já passou... os cortes piscando
        ult2.camera(jogo, 1.15, (l.x + outro.x) / 2, CHAO - 110)
        l.sobrepor = dict(POSES_INAZUMANEKO["i_passo"])
        if m.get("pegou") and t % 4 == 0:
            som.tocar("shuriken", 0.3)
            outro.tremor_hit = 3
    elif t < M_CLIC:  # guarda a espada DEVAGAR... (a câmera bem pertinho da mão no cabo)
        k = (t - M_CORTES) / (M_CLIC - M_CORTES)
        l.sobrepor = misturar(POSES_INAZUMANEKO["i_passo"], POSES_INAZUMANEKO["i_embainha"], suave(k))
        ult2.camera(jogo, 1.4 + 0.4 * k, l.x + 10 * l.s * l.dir, l.y - 60 * l.s)
    elif t == M_CLIC:  # ... *clic*
        som.tocar("defesa", 0.8)
        if m.get("pegou"):
            ult2.bate(l, outro, jogo, M_DANO, "inaz_mil_cortes", ultimo=True)
            ult2.impacto(jogo, 14, 26, 8)
            if outro.vida > 0:
                ult2.solta(outro, 4 * -l.dir, -6)
                m["tonto"] = True
        else:
            m["errou"] = True
    elif t > M_CLIC:
        l.sobrepor = dict(POSES_INAZUMANEKO["i_embainha"]) if t < M_CLIC + 16 else {}
        if m.get("tonto") and outro.no_chao() and outro.estado in ("parado", "caido", "voando") and outro.vida > 0:
            outro.mudar("tonto")  # (tontinho de meio segundo, pedido do Gomes)
            outro.tonto_tempo = M_TONTO
            m["tonto"] = False
    l.fisica(jogo)
    if t >= M_FIM:
        l.sobrepor = {}
        l.inv = 0
        return "fim"


def mil_cortes_efeito(l, tela):
    t = l.t
    m = l.memo
    if t < M_CLIC + 8:  # a tela ESCURECE (só desenho)
        k = min(1.0, t / M_ESCURO) if t < M_CLIC else 1 - (t - M_CLIC) / 8
        escuro = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        escuro.fill((0, 0, 14, int(185 * k)))
        tela.blit(escuro, (0, 0))
    alvo_x = l.x - l.dir * 80 * l.s
    cy = l.y - 70 * l.s
    if M_APARECE < t < M_CLIC and m.get("pegou"):  # os MIL CORTES: cada quadro risca mais um... e eles FICAM no ar
        camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        for st in range(M_APARECE + 1, min(t, M_CORTES) + 1):
            rnd = random.Random(st * 97)
            for _ in range(2):
                a = rnd.uniform(0, math.pi)
                r = rnd.uniform(36, 96) * l.s
                ox, oy = rnd.uniform(-20, 20) * l.s, rnd.uniform(-30, 30) * l.s
                p1 = (alvo_x + ox + math.cos(a) * r, cy + oy + math.sin(a) * r)
                p2 = (alvo_x + ox - math.cos(a) * r, cy + oy - math.sin(a) * r)
                novo = t - st < 3
                cor = (255, 255, 255, 255) if novo else (170, 220, 255, 120)
                pygame.draw.line(camada, cor, p1, p2, max(3, int((4 if novo else 3) * l.s)))
        tela.blit(camada, (0, 0))
    if M_CLIC <= t < M_CLIC + 14 and m.get("pegou"):  # *clic*: os cortes ESTOURAM em caquinhos de luz
        u = t - M_CLIC
        rnd = random.Random(7)
        for _ in range(40):
            a = rnd.uniform(0, math.tau)
            v = rnd.uniform(4, 14) * l.s
            x, y = alvo_x + math.cos(a) * v * u, cy + math.sin(a) * v * u
            tam = max(1, int((4 - u * 0.25) * l.s))
            pygame.draw.line(tela, (230, 245, 255), (x, y), (x + math.cos(a) * tam * 3, y + math.sin(a) * tam * 3), tam)
    if M_CLIC <= t < M_CLIC + 10:  # o clarão do *clic*
        brilho(tela, (int(alvo_x), int(cy)), int(120 + (t - M_CLIC) * 34), (255, 255, 255),
               max(0, 230 - (t - M_CLIC) * 23))


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


def danca_efeito(l, tela):
    """Os raios na lâmina enquanto ele dança."""
    if D_INI <= l.t < D_INI + D_HITS * D_INTERVALO:
        p = l.pose_vista or l.pose_atual()
        x, y = l.ponto(p, "mf")
        brilho(tela, (int(x + 22 * l.s * l.dir), int(y)), int(14 * l.s), AMARELO_RAIO, 90)


_registra("inaz_corte", ini=E_SOLTA, ativo=1, rec=E_FIM - E_SOLTA, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=corte_vento, ia="longe",
          quadros=[(0, "parado"), (3, "i_mao_cabo"), (6, "i_saca_meio"), (E_SACA + 2, "i_saca"),
                   (E_SOLTA - 1, "i_saca"), (E_SOLTA + 1, "i_corta"), (E_SOLTA + 5, "i_corta_fim"),
                   (E_GUARDA - 2, "i_corta_fim"), (E_GUARDA + 2, "i_chiburi"), (E_GUARDA + 6, "i_guarda"),
                   (E_FIM, "parado")])
_registra("inaz_meia_lua", ini=0, ativo=1, rec=0, proj=True, raio=20, vel=10, dano=10, hit=16, defe=10, emp=4,
          nivel="medio", desenho_proj=desenha_meia_lua)
_registra("inaz_contra", ini=C_INI, ativo=C_JANELA, rec=C_ABERTO, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=contra, ia="contra", quadros=[(0, "parado"), (C_INI, "i_contra"), (C_INI + C_JANELA, "i_contra"),
                                               (C_INI + C_JANELA + C_ABERTO, "parado")])
GOLPES["inaz_contra"]["total"] = 9999
GOLPES["inaz_revide"] = dict(dano=15, hit=24, defe=12, emp=4, nivel="medio", especial=True, derruba=True, voo=(6, 8))
_registra("inaz_danca", ini=D_INI, ativo=D_HITS * D_INTERVALO, rec=12,
          janelas=tuple((D_INI + k * D_INTERVALO, D_INI + k * D_INTERVALO + 3) for k in range(D_HITS)),
          caixa=(10, 50, 104, 124), dano=2, hit=9, defe=6, emp=1, nivel="medio", logica=danca, efeito=danca_efeito,
          ia="perto", quadros=danca_quadros())
_registra("inaz_passo", ini=P_INI, ativo=1, rec=P_FIM - P_INI, dano=0, hit=0, defe=0, emp=0, nivel="medio",
          logica=passo, efeito=passo_efeito, ia="medio",
          quadros=[(0, "parado"), (P_INI - 3, "i_contra"), (P_INI, "i_passo"), (P_INI + 6, "i_passo_fim"),
                   (P_FIM - 4, "i_passo_fim"), (P_FIM, "parado")])
GOLPES["inaz_passo_corte"] = dict(dano=6, hit=16, defe=8, emp=3, nivel="medio", especial=True)
_registra("inaz_ultimate", ini=1, ativo=1, rec=0, dano=0, hit=0, defe=0, emp=0, nivel="medio", ultimate=True,
          imbloqueavel=True, logica=ultimate, efeito=ultimate_efeito, ia="ultimate", ia_alcance=U_ALCANCE + 30,
          quadros=[(0, "parado"), (6, "i_mao_cabo"), (14, "i_respira"), (U_RESPIRA - 2, "i_respira"),
                   (U_RESPIRA + 2, "i_corta"), (U_RESPIRA + 8, "i_corta_fim"), (U_RESPIRA + 30, "parado")])
GOLPES["inaz_ultimate"]["total"] = 9999
# (a 2ª ultimate: o dano final; o ult2.py registra o golpe "inaz_ult2" com logica=mil_cortes / efeito=mil_cortes_efeito)
GOLPES["inaz_mil_cortes"] = dict(dano=M_DANO, hit=30, defe=12, emp=6, nivel="medio", especial=True, ultimate=True,
                                 ultimate2=True)

GOLPES_INAZUMANEKO = {"E": "inaz_corte", "Q": "inaz_contra", "R": "inaz_danca", "SHIFT": "inaz_passo",
                      "Z": "inaz_ultimate"}
NOMES = {"E": "corte de vento (meia-lua)", "Q": "contra-ataque", "R": "dança trovejante",
         "SHIFT": "passo relâmpago", "Z": "CORTE SAMURAI", "Z2": "MIL CORTES"}


def ponta_lamina(l, p):
    """Onde está a ponta da katana da frente na pose p (na tela) e a mão."""
    esc = l.s / S_REF
    c, m = l.ponto(p, "cf"), l.ponto(p, "mf")
    (fx, fy), _ = eixos(c, m)
    d = 1 if fx >= 0 else -1
    giro = -0.75 * d
    dx, dy = fx * math.cos(giro) - fy * math.sin(giro), fx * math.sin(giro) + fy * math.cos(giro)
    return (m[0] + dx * 34 * esc, m[1] + dy * 34 * esc), m


def rastro_lamina(l, tela):
    """O RASTRO da lâmina: um leque branco-azulado seguindo a ponta da espada nos últimos quadros.
    (Só desenho: refaz a pose dos quadros anteriores pelos quadros-chave; não guarda nada na luta.)"""
    from lutador import pose_quadros
    g = l.golpe
    if not g or l.sobrepor or not espadas(l)[0]:
        return
    quadros = l.memo.get("quadros") or g.get("quadros")
    if not quadros:
        return
    pontas = []
    for k in range(5):
        if l.t - k < 0:
            break
        pontas.append(ponta_lamina(l, pose_quadros(quadros, l.t - k, l.poses)))
    if len(pontas) < 3:
        return
    anda = sum(math.hypot(a[0][0] - b[0][0], a[0][1] - b[0][1]) for a, b in zip(pontas, pontas[1:]))
    if anda < 14 * l.s:  # (a espada quase parada: sem rastro)
        return
    camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
    for i, ((p1, m1), (p2, m2)) in enumerate(zip(pontas, pontas[1:])):
        alfa = 150 - i * 34
        meio1 = ((p1[0] * 2 + m1[0]) / 3, (p1[1] * 2 + m1[1]) / 3)
        meio2 = ((p2[0] * 2 + m2[0]) / 3, (p2[1] * 2 + m2[1]) / 3)
        pygame.draw.polygon(camada, (200, 230, 255, max(30, alfa)), [p1, p2, meio2, meio1])
        pygame.draw.line(camada, (255, 255, 255, max(40, alfa + 60)), p1, p2, max(1, int(2 * l.s)))
    tela.blit(camada, (0, 0))


def com_rastro(efeito=None):
    """O efeito do golpe + o rastro da lâmina."""
    def f(l, tela):
        rastro_lamina(l, tela)
        if efeito:
            efeito(l, tela)
    return f


for _n in ("inaz_corte", "inaz_danca", "inaz_passo", "inaz_ultimate", "inaz_contra"):
    GOLPES[_n]["efeito"] = com_rastro(GOLPES[_n].get("efeito"))


def todo_quadro(l, jogo):
    hab.samurai_quadro(l, jogo)


# =====================================================================
# Desenho em pixel art
# =====================================================================
#   k contorno  w W pelo branco (e a sombra)  s listra preta  n nariz/orelha rosa  o olho azul-gelo  c cicatriz
#   r R armadura vermelha  d dourado  h H hakama azul-escura  b cabo da katana
PALETA = {
    "k": (16, 14, 20), "w": (168, 170, 178), "W": (126, 128, 138), "l": (222, 222, 226), "s": (24, 22, 28),
    "n": (120, 80, 86), "o": (240, 190, 60), "e": (16, 14, 20), "c": (170, 70, 80),
    "r": (170, 34, 40), "R": (214, 70, 58), "d": (226, 186, 74),
    "g": (40, 46, 82), "G": (66, 76, 118), "h": (34, 34, 44), "H": (64, 64, 80), "b": (232, 228, 216),
}
S_REF = 1.38 / 3


def _m(linhas, w):
    return [linha.ljust(w, ".")[:w] for linha in linhas]


#   k contorno  w W pelo cinza (e a sombra)  l focinho/bochecha clara  s listra preta  n nariz  o e olho âmbar
#   c cicatriz  r R d armadura vermelha e dourada  g G quimono azul-escuro  h H hakama preta  b faixas brancas (obi)
CABECA = Peca(_m([
    "......kk....kk.....",
    ".....kssk..kssk....",
    ".....kswkkkkwsk....",
    "....kwwwwwwwwwwk...",
    "...kwssswwswwsswk..",
    "..kwwwwswwwswwwwwk.",
    "..kswwwwwwwwkkkwwwk",
    ".kssswwwwwwkooekwwk",
    ".kwwwwwwwwwwkckwllk",
    "kwssswwwwwwwwwllllk",
    "kwwwwwwwwwwwlllllnk",
    "kWwwwwwwwwwllllnnk.",
    "klWwwwwwwwlkkkkkk..",
    ".kllWwwwwlllllk....",
    "..kllkllllkllk.....",
    "...kk.kkkk.kk......",
], 19), PALETA, a=(7, 13), b=(7, 0), estica=False)

TRONCO = Peca(_m([
    "....kkkkkkk.....",
    "...kGgggwwwk....",
    "..kGgggwwlwgk...",
    "..kGggggwwlgk...",
    "..kGrrrrrrwgk...",
    "..kGdddddddgk...",
    "..kGrRrrrrrgk...",
    "..kGdddddddgk...",
    "..kGrRrrrrrgk...",
    "...kGggggggk....",
    "...kGgggggggk...",
    "..kdbbbbbbbbdk..",
    "..kbbdbbbbbbbk..",
    "..khhhhhhhhhhk..",
    ".kHhhhhhhhhhhhk.",
    ".kHhhhhhhhhhhhk.",
    "..kkkkkkkkkkkk..",
], 16), PALETA, a=(7, 15), b=(7, 1))

BRACO = Peca(_m([
    "kkkkkkk",
    "kRrrrRk",
    "kdddddk",
    "kRrrrRk",
    ".kgggk.",
    ".kgGgk.",
    ".kgggk.",
    ".kkkk..",
], 7), PALETA, a=(3, 0), b=(3, 7))

ANTEBRACO = Peca(_m([
    ".kkkk.",
    "kggGgk",
    "kggGgk",
    "kwswwk",
    "kwwswk",
    ".kkkk.",
], 6), PALETA, a=(2, 0), b=(2, 5))

MAO = Peca(_m([
    ".kkkk.",
    "kwwwWk",
    "kwwwWk",
    "kWWWWk",
    ".kkkk.",
], 6), PALETA, a=(2, 0), b=(2, 4), estica=False)

COXA = Peca(_m([
    ".kkkkkkk.",
    "kHhhhhhhk",
    "kHhhhhhhk",
    "kHhhkhhhk",
    "kHhhkhhhk",
    "kHhhkhhhk",
    ".kHhkhhk.",
    ".kHhkhhk.",
    ".kHhhhhk.",
    ".kHhhhhk.",
    ".kkkkkkk.",
], 9), PALETA, a=(4, 0), b=(4, 10))

CANELA = Peca(_m([
    "kkkkkkk",
    "kHhhhhk",
    "kHhhhhk",
    "kHhhhhk",
    ".kbbbk.",
    ".kbbbk.",
    ".kwWk..",
    ".kwWk..",
    ".kkkk..",
], 7), PALETA, a=(3, 0), b=(3, 8))

PE = Peca(_m([
    ".kkkk.....",
    "kwwwwkkk..",
    "kwwwwwwwk.",
    "kwwwwwwwWk",
    "klklklklk.",
    ".kkkkkkk..",
], 10), PALETA, a=(2, 1), b=(8, 1), estica=False)


def _cor(letra):
    import pecas
    return (pecas.TROCA or {}).get(letra, PALETA[letra])


def em_pixel(tela, esc, pontos, desenho, folga=46):
    """Desenha um acessório em PIXEL ART de verdade: faz o desenho PEQUENO (1 pixel = 1 pixel do sprite) e amplia
    sem borrar, pra ficar com os mesmos quadradinhos do corpo em qualquer tamanho (pedido do Gomes).
    desenho(sup, Q) recebe a superfície pequena e Q(ponto da tela) -> ponto na pequena; e desenha com esc = 1."""
    if esc <= 1.2:  # (já pequeno: desenha direto)
        desenho(tela, lambda q: q, esc)
        return
    xs, ys = [q[0] for q in pontos], [q[1] for q in pontos]
    x0, y0 = min(xs) - folga * esc, min(ys) - folga * esc
    w, h = (max(xs) - min(xs)) / esc + folga * 2, (max(ys) - min(ys)) / esc + folga * 2
    peq = pygame.Surface((max(1, int(w)), max(1, int(h))), pygame.SRCALPHA)
    desenho(peq, lambda q: ((q[0] - x0) / esc, (q[1] - y0) / esc), 1.0)
    grande = pygame.transform.scale(peq, (round(peq.get_width() * esc), round(peq.get_height() * esc)))
    tela.blit(grande, (round(x0), round(y0)))


def espadas(l):
    """Quantas katanas estão NA MÃO agora: (frente, trás)."""
    if l.estado == "vitoria":
        return l.t < V_CLIC, False
    if l.estado != "ataque" or not l.nome_golpe:
        return False, False
    n, t = l.nome_golpe, l.t
    if n == "inaz_corte":
        return 4 <= t < E_GUARDA + 8, False
    if n == "inaz_contra":
        return "pegou" in l.memo, False
    if n in ("inaz_danca", "inaz_passo"):
        return True, False
    if n == "inaz_ultimate":
        m = l.memo
        dupla = "pegou" in m and t - m["pegou"] >= U_MEIO
        return t >= 8, dupla
    if n == "inaz_ult2":
        return l.t < M_CLIC, False
    return False, False


def katana(tela, mao, cot, esc, cor_lamina=LAMINA, brilho_cor=None):
    """Uma katana NA MÃO: segue a direção do antebraço; cabo escuro, guarda dourada, lâmina curvinha."""
    (fx, fy), _ = eixos(cot, mao)
    # a lâmina sai da mão INCLINADA pra cima em relação ao antebraço (pegada de katana, não "braço esticado")
    d = 1 if fx >= 0 else -1
    giro = -0.75 * d
    dx, dy = fx * math.cos(giro) - fy * math.sin(giro), fx * math.sin(giro) + fy * math.cos(giro)
    nx, ny = -dy, dx
    base = (mao[0] + dx * 4 * esc, mao[1] + dy * 4 * esc)          # (a guarda logo depois do punho)
    cabo_fim = (mao[0] - dx * 4.5 * esc, mao[1] - dy * 4.5 * esc)  # (o pomo aparecendo atrás do punho)
    ponta = (base[0] + dx * 30 * esc + nx * 2.2 * esc, base[1] + dy * 30 * esc + ny * 2.2 * esc)
    meio = (base[0] + dx * 15 * esc + nx * 1.4 * esc, base[1] + dy * 15 * esc + ny * 1.4 * esc)
    borda = (16, 14, 20)
    if brilho_cor:
        brilho(tela, (int(meio[0]), int(meio[1])), int(14 * esc), brilho_cor, 110)
    pygame.draw.line(tela, borda, cabo_fim, base, max(3, int(2.6 * esc)))
    pygame.draw.line(tela, (60, 44, 50), cabo_fim, base, max(1, int(1.4 * esc)))
    pygame.draw.lines(tela, borda, False, [base, meio, ponta], max(4, int(3.4 * esc)))
    pygame.draw.lines(tela, cor_lamina, False, [base, meio, ponta], max(2, int(2 * esc)))
    pygame.draw.line(tela, (255, 255, 255), meio, ponta, max(1, int(0.6 * esc)))  # o fio brilhando
    g1 = (base[0] + nx * 2.2 * esc, base[1] + ny * 2.2 * esc)
    g2 = (base[0] - nx * 2.2 * esc, base[1] - ny * 2.2 * esc)
    pygame.draw.line(tela, borda, g1, g2, max(4, int(3 * esc)))
    pygame.draw.line(tela, _cor("d"), g1, g2, max(2, int(1.8 * esc)))  # a guarda (tsuba)


def bainhas(tela, qd, esc, d, cheias):
    """As DUAS bainhas pretas na cintura (pra trás, inclinadas). cheias = (frente, trás): o cabo aparece."""
    borda = (16, 14, 20)
    for i, (cheia, cor) in enumerate(((cheias[0], (30, 28, 36)), (cheias[1], (50, 40, 46)))):
        y = qd[1] - (6 + i * 1.5) * esc  # (na cintura, presas no obi)
        frente = (qd[0] + d * (4 - i * 2) * esc, y)
        tras = (qd[0] - d * (11 - i * 2) * esc, y + (3 + i) * esc)
        pygame.draw.line(tela, borda, frente, tras, max(3, int(2.6 * esc)))
        pygame.draw.line(tela, cor, frente, tras, max(1, int(1.2 * esc)))
        if cheia:  # o cabo da katana saindo da bainha, pra frente
            cabo = (frente[0] + d * 6 * esc, frente[1] - 2 * esc)
            pygame.draw.line(tela, borda, frente, cabo, max(3, int(2.6 * esc)))
            pygame.draw.line(tela, (60, 44, 50), frente, cabo, max(1, int(1.2 * esc)))
            pygame.draw.circle(tela, _cor("d"), (int(frente[0]), int(frente[1])), max(1, int(1.4 * esc)))


def rabo(tela, qd, esc, d, t, branco=False):
    """O RABO de tigre: cinza, afinando até a ponta (que vira pra cima e é preta), com anéis pretos."""
    pts = []
    for i in range(8):
        k = i / 7
        pts.append((qd[0] - d * (3 + 17 * k) * esc,
                    qd[1] + (5 + 3 * k - 16 * k ** 2.4 + 2.5 * math.sin(t * 0.08 + k * 3) * k) * esc))
    borda = (16, 14, 20)
    cinza = (245, 245, 250) if branco else _cor("w")
    preto = (245, 245, 250) if branco else _cor("s")
    for i, (a, b) in enumerate(zip(pts, pts[1:])):  # (cada pedaço um pouco mais fino)
        w = (4.2 - i * 0.4) * esc
        pygame.draw.line(tela, borda, a, b, max(3, int(w + 2 * esc)))
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        w = (4.2 - i * 0.4) * esc
        cor = preto if (i >= 5 or i in (1, 3)) else cinza  # anéis pretos e a ponta preta
        pygame.draw.line(tela, cor, a, b, max(2, int(w)))


def desenhar_inazumaneko(l, tela, p, branco):
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
        PE.desenhar(tela, e, mais(e, fr, 9), esc, espelho, var)
        COXA.desenhar(tela, q, j, esc, espelho, var)

    def braco(cot, mao, var):
        o, c, m = P("pc"), P(cot), P(mao)
        ANTEBRACO.desenhar(tela, c, m, esc, espelho, var)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)
        BRACO.desenhar(tela, o, c, esc, espelho, var)

    def mao_por_cima(cot, mao, var):
        c, m = P(cot), P(mao)
        dm, _ = eixos(c, m)
        MAO.desenhar(tela, m, mais(m, dm, 4), esc, espelho, var)

    frente_mao, tras_mao = espadas(l)
    poder = l.extra.get("poder_t", 0) > 0 and not branco
    cor_poder = hab.COR_STATUS.get(l.extra.get("poder_tipo")) if poder else None
    braco("ct", "mt", longe_v)
    if tras_mao and not branco:
        em_pixel(tela, esc, [P("mt")], lambda sup, Q, e: katana(sup, Q(P("mt")), Q(P("ct")), e * 0.9, brilho_cor=cor_poder))
        mao_por_cima("ct", "mt", longe_v)  # (a mão FECHADA em volta do cabo)
    perna("pt", "jt", longe_v)
    em_pixel(tela, esc, [P("qd")], lambda sup, Q, e: rabo(sup, Q(P("qd")), e, d, l.t, branco))
    perna("pf", "jf", perto_v)
    c, cb = P("pc"), P("cb")
    TRONCO.desenhar(tela, P("qd"), c, esc, espelho, perto_v)
    if not branco:
        sem_frente = frente_mao or (l.estado == "ataque" and l.nome_golpe == "provocar" and 8 <= l.t < PROVOCA_TEMPO - 10)
        em_pixel(tela, esc, [P("qd")], lambda sup, Q, e: bainhas(sup, Q(P("qd")), e, d, (not sem_frente, not tras_mao)))
    u, _ = cabeca_eixos(c, cb, d)
    pescoco = mais(cb, u, -4 * esc)  # o PESCOÇO de pelo branco (liga a cabeça no corpo)
    pygame.draw.line(tela, (16, 14, 20), c, pescoco, max(3, int(7 * esc)))
    pygame.draw.line(tela, (245, 245, 250) if branco else _cor("W"), c, pescoco, max(1, int(5 * esc)))
    na_cabeca = CABECA.desenhar(tela, cb, mais(cb, u, 10), esc, espelho, perto_v)
    if l.f.get("estilo") == "oni" and not branco:
        mascara_oni(tela, na_cabeca, esc, l.t)
    braco("cf", "mf", perto_v)
    if frente_mao and not branco:
        em_pixel(tela, esc, [P("mf")], lambda sup, Q, e: katana(sup, Q(P("mf")), Q(P("cf")), e, brilho_cor=cor_poder))
        mao_por_cima("cf", "mf", perto_v)  # (a mão FECHADA em volta do cabo)
    provocando = l.estado == "ataque" and l.nome_golpe == "provocar" and 8 <= l.t < PROVOCA_TEMPO - 10
    if provocando and not branco:
        dedo = mais(P("mf"), eixos(P("cf"), P("mf"))[0], 3 * esc)
        em_pixel(tela, esc, [dedo], lambda sup, Q, e: espada_equilibrada(sup, Q(dedo), e, l.t))
    if not branco and l.extra.get("furia_flash", 0) > 0:  # FÚRIA SAMURAI: a barra encheu (aura vermelha)
        brilho(tela, (int(c[0]), int(c[1])), int(26 * esc), (255, 60, 40), 4 * l.extra["furia_flash"])
    if poder and (l.t // 6) % 2:  # PODER SAMURAI aceso: faísca da cor do status em volta
        a = l.t * 0.2
        pygame.draw.circle(tela, cor_poder, (int(c[0] + math.cos(a) * 20 * esc), int(c[1] + math.sin(a) * 10 * esc)),
                           max(1, int(1.2 * esc)))


MASCARA_ONI = {  # (pixels da máscara, na MESMA grade da cabeça de lado: x de 0 a 18, y de 0 a 15; y negativo = em cima)
    # os CHIFRES: grossos na testa e CURVANDO PRA TRÁS (o da frente maior)
    "Z": [(12, 3), (13, 3), (12, 2), (13, 2), (12, 1), (13, 1), (12, 0), (11, -1), (12, -1), (10, -2), (11, -2), (9, -3),
          (10, -3), (8, -4),
          (8, 3), (9, 3), (8, 2), (9, 2), (8, 1), (7, 0), (8, 0), (6, -1), (7, -1), (5, -2)],
    "z": [(13, 0), (12, -2), (11, -3), (9, -4), (9, 1), (8, -1), (6, -2)],
    "X": [(x, 5) for x in range(10, 16)] + [(x, 6) for x in (9, 10, 17)] + [(x, 7) for x in (9, 10, 14, 15, 16, 17, 18)]
         + [(x, 8) for x in range(9, 19)] + [(x, 9) for x in range(9, 19)] + [(x, 10) for x in range(10, 19)]
         + [(11, 11), (13, 11), (15, 11), (17, 11)],
    "Y": [(x, 6) for x in range(11, 17)] + [(x, 12) for x in range(11, 17)] + [(18, 10)],
    "d": [(x, 5) for x in range(11, 15)] + [(16, 6), (15, 6)],
    "e": [(11, 7), (12, 7), (13, 7)],
    "o": [(12, 7)],
    "w": [(12, 11), (14, 11), (16, 11), (12, 12), (16, 12)],
}
COR_MASCARA = {"Z": (232, 222, 192), "z": (176, 164, 136), "X": (200, 36, 40), "Y": (128, 18, 26), "d": (226, 186, 74),
               "e": (20, 8, 12), "o": (255, 70, 56), "w": (246, 242, 232)}


def mascara_oni(tela, P, esc, t):
    """ONI (a skin secreta, escolha do Gomes): a MÁSCARA DE DEMÔNIO com chifres, feita PIXEL POR PIXEL na mesma grade
    da cabeça (fica pixel art igual o resto). P leva um ponto da cabeça (em pixels do desenho) pra tela."""
    px = {}
    for letra in ("X", "Y", "Z", "z", "d", "e", "o", "w"):  # (a ordem: o que vem depois fica por cima)
        for xy in MASCARA_ONI[letra]:
            px[xy] = COR_MASCARA[letra]
    if (t // 10) % 3 == 0:  # o olho pisca mais forte de vez em quando
        px[(12, 7)] = (255, 160, 120)
    contorno = set()
    for (x, y) in px:  # o CONTORNO preto de 1 pixel em volta de tudo
        for vx, vy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + vx, y + vy) not in px:
                contorno.add((x + vx, y + vy))
    for (x, y) in contorno:
        pygame.draw.polygon(tela, (16, 10, 14), [P(x, y), P(x + 1, y), P(x + 1, y + 1), P(x, y + 1)])
    for (x, y), cor in px.items():
        pygame.draw.polygon(tela, cor, [P(x, y), P(x + 1, y), P(x + 1, y + 1), P(x, y + 1)])
    olho = P(12.5, 7.5)
    brilho(tela, (int(olho[0]), int(olho[1])), int(4 * esc), (255, 40, 40), 110 + int(50 * math.sin(t * 0.2)))


def espada_equilibrada(tela, dedo, esc, t):
    """PROVOCAÇÃO (escolha do Gomes): a katana EM PÉ equilibrada na ponta do dedo, balançando."""
    ang = math.sin(t * 0.22) * 0.18
    ux, uy = math.sin(ang), -math.cos(ang)
    ponta = dedo
    guarda = (dedo[0] + ux * 30 * esc, dedo[1] + uy * 30 * esc)
    pomo = (dedo[0] + ux * 40 * esc, dedo[1] + uy * 40 * esc)
    borda = (16, 14, 20)
    pygame.draw.line(tela, borda, ponta, guarda, max(4, int(3.4 * esc)))
    pygame.draw.line(tela, LAMINA, ponta, guarda, max(2, int(2 * esc)))
    pygame.draw.line(tela, borda, guarda, pomo, max(4, int(3 * esc)))
    pygame.draw.line(tela, (60, 44, 50), guarda, pomo, max(1, int(1.4 * esc)))
    g1 = (guarda[0] - uy * 3 * esc, guarda[1] + ux * 3 * esc)
    g2 = (guarda[0] + uy * 3 * esc, guarda[1] - ux * 3 * esc)
    pygame.draw.line(tela, borda, g1, g2, max(4, int(3 * esc)))
    pygame.draw.line(tela, _cor("d"), g1, g2, max(2, int(1.8 * esc)))


def figura_extra(q, P, s, d, cor, escura, cont, branco, t):
    """Inazumaneko grande: as orelhas e a katana na cintura."""
    cb, qd = P("cb"), P("qd")
    for dx in (-4, 3):
        pygame.draw.polygon(q, (240, 240, 240) if branco else (242, 242, 238),
                            [(cb[0] + (dx - 2) * s, cb[1] - 8 * s), (cb[0] + dx * s, cb[1] - 14 * s),
                             (cb[0] + (dx + 2) * s, cb[1] - 8 * s)])
    pygame.draw.line(q, (30, 28, 36), (qd[0] + d * 8 * s, qd[1] - 10 * s), (qd[0] - d * 24 * s, qd[1] + 2 * s),
                     max(2, int(2 * s)))


# =====================================================================
# ENTRADA (escolha do Gomes): um TROVÃO cai do céu e ele aparece agachado com a mão no chão, levanta com faíscas
# =====================================================================
EN_RAIO, EN_LEVANTA, EN_FIM = 26, 56, 80


def entrada(l, t, jogo):
    if t < EN_RAIO:  # ainda não apareceu (o céu piscando)
        l.esconde = True
        if t in (10, 18):
            som.tocar("terra", 0.3)
    elif t == EN_RAIO:  # CABRUUUM
        l.esconde = False
        som.tocar("explosao", 0.9)
        som.tocar("terra", 0.8)
        jogo.tremer(16)
        if hasattr(jogo, "clarao"):
            jogo.clarao = max(jogo.clarao, 6)
        faisca_raio(jogo, l.x, CHAO - 10, 24)
    l.sobrepor = dict(POSES_INAZUMANEKO["i_pouso"]) if t < EN_LEVANTA else \
        misturar(POSES_INAZUMANEKO["i_pouso"], POSES_INAZUMANEKO["i_mao_cabo"], suave(min(1, (t - EN_LEVANTA) / 14)))
    if EN_RAIO < t < EN_LEVANTA and t % 5 == 0:  # faíscas soltando do corpo
        faisca_raio(jogo, l.x + random.uniform(-20, 20) * l.s, l.y - random.uniform(10, 70) * l.s, 3)
    if t >= EN_FIM:
        l.sobrepor = {}
    l.t += 1


def entrada_efeito(l, tela, t):
    """O TROVÃO caindo do céu bem em cima dele (e os raiozinhos antes, avisando)."""
    if t in (8, 9, 16, 17, EN_RAIO - 3) or EN_RAIO <= t < EN_RAIO + 8:
        forte = t >= EN_RAIO
        rnd = random.Random(t // 2 * 31)
        x0 = l.x + (0 if forte else rnd.uniform(-160, 160))
        pts = [(x0 + rnd.uniform(-30, 30), 0)]
        n = 12
        for k in range(1, n):
            pts.append((l.x + (x0 - l.x) * (1 - k / n) + rnd.uniform(-26, 26) * l.s, l.y * k / n))
        pts.append((l.x, l.y - (0 if forte else 200)))
        some = 1.0 if not forte else max(0.0, 1 - (t - EN_RAIO) / 8)
        camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        largura = 16 if forte else 4
        pygame.draw.lines(camada, (90, 150, 255, int(90 * some)), False, pts, max(3, int(largura * 2 * l.s)))
        pygame.draw.lines(camada, (*AZUL_RAIO, int(230 * some)), False, pts, max(2, int(largura * 0.8 * l.s)))
        pygame.draw.lines(camada, (255, 255, 255, int(255 * some)), False, pts, max(1, int(largura * 0.35 * l.s)))
        tela.blit(camada, (0, 0))
        if forte:  # o clarão no chão
            brilho(tela, (int(l.x), int(l.y)), int((70 + (t - EN_RAIO) * 18) * l.s), (200, 230, 255),
                   int(220 * some))


# =====================================================================
# VITÓRIA (escolha do Gomes): vira de costas, guarda a espada BEM devagar... *clic* e o vento levanta as folhas
# =====================================================================
V_VIRA, V_GUARDA, V_CLIC = 6, 20, 84


def vitoria(l, t, jogo):
    if t == V_VIRA:  # vira de COSTAS pro derrotado
        l.dir = -l.dir
    P_ = POSES_INAZUMANEKO
    if t < V_GUARDA:
        l.sobrepor = misturar(P_["parado"], P_["i_chiburi"], suave(min(1, t / 12)))
    elif t < V_CLIC:  # guardando devagar...
        l.sobrepor = misturar(P_["i_chiburi"], P_["i_embainha"], suave((t - V_GUARDA) / (V_CLIC - V_GUARDA)))
    else:
        l.sobrepor = dict(P_["i_embainha"]) if t < V_CLIC + 30 else \
            misturar(P_["i_embainha"], P_["parado"], suave(min(1, (t - V_CLIC - 30) / 20)))
    if t == V_CLIC:  # *clic*
        som.tocar("defesa", 0.9)
        som.tocar("vento", 0.8)
        for _ in range(26):  # o VENTO levantando as folhas vermelhas
            jogo.faiscas.append([l.x - l.dir * random.uniform(-200, 60), CHAO - random.uniform(0, 30),
                                 -l.dir * random.uniform(4, 9), random.uniform(-4, -1), random.randint(30, 60),
                                 random.choice(((200, 50, 40), (230, 110, 40), (170, 30, 40))), 4])


def vitoria_efeito(l, tela, t):
    """O risco do vento passando no *clic*."""
    if V_CLIC <= t < V_CLIC + 16:
        u = t - V_CLIC
        for k in range(4):
            y = l.y - (20 + k * 30) * l.s
            x = l.x - l.dir * (u * 40 - 200 + k * 30) * l.s
            pygame.draw.line(tela, (235, 240, 255), (x, y), (x - l.dir * 90 * l.s, y), max(3, int(3 * l.s)))
