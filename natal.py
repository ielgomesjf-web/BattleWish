"""NATAL (v2.x, pedido do Gomes): de 20/12 a 05/01 (eventos.NATAL).

  MEIA DE NATAL ESCONDIDA: cada um dos cenários tem UMA meia pra achar no Natal. Em cada luta ela aparece num
  LUGAR DIFERENTE do cenário (pequena, pendurada e meio escondida). 1 GOLPE do jogador nela = coletou.
  Coletou a meia de TODOS os cenários = GORRINHO DE NATAL liberado pra sempre: um botão LIGADO/DESLIGADO que põe o
  gorrinho em TODOS os lutadores (e pode usar o ano todo, não só no Natal).
  No Natal seguinte as meias voltam pra achar de novo (o gorrinho continua seu).

No save: save.d()["natal"] = {"temporada": 2026, "meias": ["TEMPLO", ...], "gorro": True/False, "gorro_ligado": bool}

ONLINE: a meia só muda no passo() (a posição sai do random global, igual nos dois PCs); o desenhar() só lê.
Só conta pra quem é GENTE (partida.lados_humanos()); o CPU que bate nela só faz ela balançar.

Como usar (a partida):
  self.meia = natal.criar(self)            (no __init__, depois do cenário)    -> Meia ou None
  no passo (depois dos golpes):   if self.meia: self.meia.passo(self)
  no desenho (na camada, junto do objeto do cenário, atrás dos lutadores):  self.meia.desenhar(camada)
  no HUD (por cima):              self.meia.desenhar_aviso(tela)
O gorrinho (lutador / vitrine / seleção):
  natal.gorro_ligado() -> bool      natal.desenhar_gorro(l, tela)   (DEPOIS de desenhar o lutador)
  natal.tem_gorro() / natal.ligar_gorro(bool)  (o botão: nas CONFIGURAÇÕES ou no PERFIL)
"""
import datetime
import math
import random

import pygame

import save
import som
from config import *  # noqa: F401,F403

AVISO = 150          # quadros do "MEIA DE NATAL! 5/17"
X_MIN, X_MAX = 90, LARGURA - 90
ALTURAS = (60, 95, 130, 165)   # acima do chão: dá pra pegar com soco, chute alto ou pulando


# =====================================================================
# o ESTADO (no save)
# =====================================================================
def temporada(data=None):
    """O Natal de 20/12/2026 a 05/01/2027 é a temporada 2026."""
    import eventos
    d = data or eventos.hoje()
    return d.year - 1 if d.month == 1 else d.year


def _estado(data=None):
    s = save.d().get("natal")
    if not isinstance(s, dict):
        s = {}
        save.d()["natal"] = s
    if not isinstance(s.get("meias"), list):
        s["meias"] = []
    tem = temporada(data)
    if s.get("temporada") != tem:  # Natal novo: as meias voltam (o gorrinho fica)
        s["temporada"] = tem
        s["meias"] = []
    return s


def cenarios_com_meia():
    import cenarios
    return list(cenarios.CENARIOS)


def coletadas(data=None):
    return [c for c in _estado(data)["meias"] if c in cenarios_com_meia()]


def tem_gorro():
    s = save.d().get("natal")
    return isinstance(s, dict) and s.get("gorro") is True


def gorro_ligado():
    s = save.d().get("natal")
    return tem_gorro() and s.get("gorro_ligado", True) is not False


def ligar_gorro(ligado):
    if tem_gorro():
        save.d()["natal"]["gorro_ligado"] = bool(ligado)
        save.salvar()


def coletar(cenario, data=None):
    """Guarda a meia desse cenário. Devolve (quantas, total, liberou_gorro_agora)."""
    s = _estado(data)
    if cenario not in s["meias"]:
        s["meias"].append(cenario)
    n, total = len(coletadas(data)), len(cenarios_com_meia())
    liberou = n >= total and not tem_gorro()
    if liberou:
        s["gorro"] = True
        s["gorro_ligado"] = True
    save.salvar()
    return n, total, liberou


def no_natal(data=None):
    import eventos
    return eventos.evento_atual(data) == eventos.NATAL


def criar(partida, data=None):
    """A meia dessa luta (ou None: fora do Natal, treino, ou a meia desse cenário já foi pega)."""
    if not no_natal(data) or partida.treino or getattr(partida, "assistindo", False):
        return None
    nome = partida.cena.nome
    if nome in coletadas(data):
        return None
    return Meia(nome, data)


# =====================================================================
# a MEIA
# =====================================================================
class Meia:
    def __init__(self, cenario, data=None):
        self.cenario = cenario
        self.data = data
        self.x = None          # sorteado no 1º passo (random global: igual no online)
        self.alt = 0
        self.t = 0
        self.balanca = 0
        self.pega = False
        self.aviso = 0
        self.resultado = None  # (quantas, total, liberou)
        self.voo = None        # [x, y, vy] da meia voando quando pega
        self.brilhos = []

    def caixa(self):
        return pygame.Rect(self.x - 16, CHAO - self.alt - 20, 32, 46)

    def passo(self, partida):
        self.t += 1
        if self.x is None:
            self.x = random.randint(X_MIN, X_MAX)
            self.alt = random.choice(ALTURAS)
        if self.balanca > 0:
            self.balanca -= 1
        if self.aviso > 0:
            self.aviso -= 1
        if self.voo:
            self.voo[1] += self.voo[2]
            self.voo[2] += 0.4
            if self.voo[1] > ALTURA + 60:
                self.voo = None
        for b in self.brilhos:
            b[0] += b[2]
            b[1] += b[3]
            b[4] -= 1
        self.brilhos = [b for b in self.brilhos if b[4] > 0]
        if self.pega or partida.fase != "luta":
            return
        cx = self.caixa()
        humanos = partida.lados_humanos()
        for i, l in enumerate(partida.L):
            if l.estado != "ataque":
                continue
            cg = l.caixa_golpe()
            bateu = bool(cg and cg.colliderect(cx)) or bool(l.feixe and cx.clipline(*l.feixe))
            if not bateu:
                continue
            if i in humanos:
                self.pegar(partida, i)
                return
            self.balanca = 30  # (o CPU só faz balançar)

    def pegar(self, partida, lado):
        self.pega = True
        self.aviso = AVISO
        cx = self.caixa()
        self.voo = [cx.centerx, cx.centery, -7.0]
        for k in range(14):
            a = k * math.pi * 2 / 14
            self.brilhos.append([cx.centerx, cx.centery, math.cos(a) * 3, math.sin(a) * 3, 30])
        # (no online só o PC dono do lado guarda; os dois desenham igual)
        meu = getattr(partida, "lado_humano", None)
        if meu is None or meu == lado:
            self.resultado = coletar(self.cenario, self.data)
        else:
            self.resultado = (None, None, False)
        som.tocar("confirma")

    # ------------------------------------------------------------ desenho (só lê)
    def desenhar(self, tela):
        if self.x is None:
            return
        if not self.pega:
            cx = self.caixa()
            ang = math.sin(self.t * 0.05) * 0.12 + (math.sin(self.balanca * 0.6) * 0.5 * self.balanca / 30)
            topo = (self.x, cx.y - 30)
            pygame.draw.line(tela, (200, 190, 170), topo, (self.x + math.sin(ang) * 30, cx.y), 1)  # o barbante
            meia(tela, self.x + math.sin(ang) * 30, cx.y, 1.0, ang, alfa=170)  # meio escondida (meio transparente)
        if self.voo:
            meia(tela, self.voo[0], self.voo[1], 1.2, self.t * 0.3)
        for b in self.brilhos:
            pygame.draw.circle(tela, (255, 240, 150), (int(b[0]), int(b[1])), 3)

    def desenhar_aviso(self, tela):
        if self.aviso <= 0 or not self.resultado:
            return
        from efeitos import texto_grande, texto
        n, total, liberou = self.resultado
        alfa = min(255, self.aviso * 8)
        if n is None:
            return
        texto_grande(tela, f"MEIA DE NATAL!  {n}/{total}", 30, (255, 90, 90), (LARGURA // 2, 170), 1.0, alfa=alfa)
        if liberou:
            texto_grande(tela, "GORRINHO DE NATAL LIBERADO!", 26, (255, 255, 255), (LARGURA // 2, 206), 1.0, alfa=alfa)


def meia(tela, x, y, e=1.0, ang=0.0, alfa=255):
    """A meia de Natal (vermelha, punho branco, listras), pendurada pelo punho em (x, y)."""
    w, h = int(34 * e), int(48 * e)
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    v, ve, b = (200, 30, 40), (130, 15, 25), (245, 245, 245)
    corpo = [(w * 0.18, h * 0.22), (w * 0.62, h * 0.22), (w * 0.62, h * 0.68), (w * 0.95, h * 0.78),
             (w * 0.92, h * 0.98), (w * 0.35, h * 0.98), (w * 0.18, h * 0.8)]
    pygame.draw.polygon(sup, v, corpo)
    for k in (0.42, 0.58):  # listras
        pygame.draw.line(sup, b, (w * 0.18, h * k), (w * 0.62, h * k), max(1, int(2 * e)))
    pygame.draw.polygon(sup, ve, corpo, max(1, int(2 * e)))
    pygame.draw.rect(sup, b, (0, 0, int(w * 0.8), int(h * 0.24)), border_radius=int(5 * e))
    pygame.draw.circle(sup, (255, 210, 60), (int(w * 0.7), int(h * 0.88)), max(2, int(3 * e)))  # o remendinho
    if alfa < 255:
        sup.set_alpha(alfa)
    sup = pygame.transform.rotate(sup, -math.degrees(ang))
    tela.blit(sup, sup.get_rect(midtop=(x, y - 2)))


# =====================================================================
# o GORRINHO
# =====================================================================
# ajuste por lutador: (dx, dy, tamanho, inclinação em graus) em unidades da pose, em cima do ponto da cabeça "cb"
AJUSTE = {
    "MAX-10": (0, -12, 1.0, -10), "RIB": (0, -13, 1.0, -10), "TRAFO": (2, -12, 1.0, -12),
    "KING RIP": (0, -12, 1.0, -10), "CANNAN": (0, -12, 1.0, -10), "FINN": (0, -14, 1.0, -10),
    "KUN": (0, -12, 1.0, -10), "TROMOS": (-2, -9, 1.0, -15), "TAI": (0, -12, 1.05, -8),
    "TAMER": (0, -12, 1.0, -10), "JOHN": (0, -16, 1.0, -8), "CRÁQUEN": (0, -13, 1.0, -10),
    "MAGNUS": (27, 7, 0.85, -5), "SPHYRUS": (18, -8, 0.9, -5), "FRIGANTUS": (4, -3, 1.1, -5),
    "RIBBAT": (0, -9, 0.7, -8),
}


def gorro(tela, x, y, e=1.0, ang=0.0, dir_=1, t=0):
    """O gorrinho: (x, y) = o meio da aba branca; dir_ = pra onde o lutador olha (a ponta cai pra trás)."""
    w, h = 40 * e, 34 * e
    ca, sa = math.cos(math.radians(ang * dir_)), math.sin(math.radians(ang * dir_))

    def P(px, py):  # ponto relativo (px pra frente, py pra cima) já girado
        px *= dir_
        return (x + px * ca - (-py) * sa, y + px * sa + (-py) * ca)
    balanco = math.sin(t * 0.08) * 3 * e
    ponta = P(-w * 0.62, h * 0.55 + balanco)
    corpo = [P(-w * 0.5, 0), P(w * 0.5, 0), P(w * 0.18, h * 0.9), P(-w * 0.12, h), ponta]
    pygame.draw.polygon(tela, (205, 30, 40), corpo)
    pygame.draw.polygon(tela, (130, 15, 25), corpo, max(1, int(2 * e)))
    aba = [P(-w * 0.56, -4 * e), P(w * 0.56, -4 * e), P(w * 0.56, 7 * e), P(-w * 0.56, 7 * e)]
    pygame.draw.polygon(tela, (245, 245, 245), aba)
    pygame.draw.circle(tela, (245, 245, 245), (int(ponta[0]), int(ponta[1])), max(3, int(7 * e)))


def desenhar_gorro(l, tela):
    """Põe o gorrinho no lutador l (chame DEPOIS de l.desenhar). Não faz nada se o gorrinho estiver desligado."""
    if not gorro_ligado() or getattr(l, "invisivel", 0) > 0:  # (camuflado/invisível: o gorrinho some junto)
        return
    try:
        p = l.pose_vista or l.pose_atual()
        nome = l.f.get("nome_base", l.f["nome"])
        dx, dy, tam, incl = AJUSTE.get(nome, (0, -12, 1.0, -10))
        cb = p["cb"]
        x, y = l.ponto(dict(p, _g=(cb[0] + dx, cb[1] - dy)), "_g")
        gorro(tela, x, y, l.s * tam * 0.55, incl, l.lado(), getattr(l, "t", 0))
    except Exception:  # (um lutador esquisito nunca pode derrubar a luta)
        pass
