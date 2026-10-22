"""MÚSICAS do Battle Wish compostas pelo Gomes no STRUDEL (strudel.cc), tocadas pelo jogo sem arquivo de áudio.

O código original de cada música fica em musica/*.strudel.js. Aqui as MESMAS notas e batidas são escritas do mesmo
jeitinho (a "mini-notação" do Strudel) e um sintetizador transforma em som. A mini-notação que o jogo entende:
  a3 c4 g#3 eb2   notas (letra + acidente + oitava)          ~       silêncio
  [a b c]         um passo dividido em pedaços                  a,b,c   tocam JUNTOS (acorde / camadas)
  <a b c>         um por VOLTA (compasso): a, depois b, depois c
  x*4             repete 4 vezes no espaço de 1 passo          x!4     vira 4 passos iguais
  x@4             o passo dura 4 (notas longas)
  bd sd hh        bumbo, caixa e chimbal (imitando a bateria Roland TR-909)
E os efeitos: .s("piano"/"sawtooth"/"square"/"triangle"/"sine"), .gain, .lpf, .room, .delay, .attack, .release.
"""
import math

import numpy as np

TAXA = 22050

# =====================================================================
# As MÚSICAS (do mesmo jeito que estão no Strudel)
# =====================================================================
MUSICAS = {
    "warrior_spirit": dict(
        nome="WARRIOR SPIRIT", autor="Gomes", cps=0.35, voltas=16,
        camadas=[
            dict(note="""<
                [a3 c4 a3 ~ a3 c4 a3 ~ a3 c4 b3 a3 c4 b3 b4 ~]
                [a3 c4 a3 ~ a3 c4 a3 ~ a3 c4 b3 a3 g3 e3 a3 ~]
                [c4 e4 c4 ~ c4 e4 c4 ~ c4 e4 d4 c4 e4 d4 d5 ~]
                [e4 d4 c4 b3 c4 b3 a3 g3 a3 b3 c4 d4 e4 ~ d4 ~]
                [e4@4 d4@4 c4@4 b3@4]
                [a3@6 c4@2 e4@8]
                [f4@4 e4@4 d4@4 c4@4]
                [b3@6 c4@2 d4@4 e4@4]
                [c3 c3 c3 c3 c3 c3 c3 c3 d3 ~ c3 c2 ~ e3 e2 ~]
                [c3 c3 c3 c3 c3 c3 c3 c3 d3 ~ c3 c2 ~ e3 g3 a3]
                [d3 d3 d3 d3 d3 d3 d3 d3 e3 ~ d3 d2 ~ f3 f2 ~]
                [e3 e3 e3 e3 e3 e3 e3 e3 f3 ~ e3 e2 ~ g#3 b3 ~]
                [f3 a3 c4 a3 f3 a3 c4 a3 f3 a3 c4 a3 f3 a3 c4 e4]
                [g3 b3 d4 b3 g3 b3 d4 b3 g3 b3 d4 b3 g3 b3 d4 f4]
                [a3 c4 e4 c4 a3 c4 e4 c4 a3 c4 e4 a4 c5 a4 e4 c4]
                [e4@4 g#4@4 b4@4 e5@4]
            >""", s="piano", room=0.5, delay=0.2, gain=0.7),
            dict(note="""<
                [a2,c3,e3] [f2,a2,c3] [c3,e3,g3] [g2,b2,d3]
                [c3,e3,g3] [a2,c3,e3] [f2,a2,c3] [e2,g#2,b2]
                [c3,e3,g3] [c3,e3,g3] [d3,f3,a3] [e2,g#2,b2]
                [f2,a2,c3] [g2,b2,d3] [a2,c3,e3] [e2,g#2,b2]
            >""", s="sawtooth", lpf=700, attack=0.3, release=1.0, gain=0.22),
            dict(note="<a1 f1 c2 g1 c2 a1 f1 e1 c2 c2 d2 e1 f1 g1 a1 e1>*4", s="square", lpf=400, gain=0.4),
            dict(s="<[bd ~ ~ bd, ~ sd, hh*8]!8 [bd bd ~ bd, ~ sd ~ sd, hh*16]!4 ~ ~ [sd*4] [sd*8, bd*4]>",
                 gain=0.7),
        ]),
    "before_the_battle": dict(
        nome="BEFORE THE BATTLE", autor="Gomes", cps=0.22, voltas=8,
        camadas=[
            dict(note="""<
                [a3 c4 a3 c4 a3 c4 b3 ~]
                [a3 c4 a3 c4 g3 e3 a3 ~]
                [c4 e4 c4 e4 c4 e4 d4 ~]
                [e4 d4 c4 b3 a3@3 ~]
                [e4@2 d4@2 c4@2 b3@2]
                [a3@3 c4 e4@4]
                [f4@2 e4@2 d4@2 c4@2]
                [b3@3 c4 d4@2 e4@2]
            >""", s="piano", room=0.8, delay=0.3, gain=0.6),
            dict(note="""<
                [a4 e5 a5 e5 c5 e5 a5 e5]
                [f4 c5 f5 c5 a4 c5 f5 c5]
                [c5 g5 c6 g5 e5 g5 c6 g5]
                [g4 d5 g5 d5 b4 d5 g5 d5]
                [c5 g5 c6 g5 e5 g5 c6 g5]
                [a4 e5 a5 e5 c5 e5 a5 e5]
                [f4 c5 f5 c5 a4 c5 f5 c5]
                [e4 b4 e5 b4 g#4 b4 e5 b4]
            >""", s="piano", room=0.7, delay=0.2, gain=0.5),
            dict(note="""<[a2,e3,a3] [f2,c3,a3] [c3,g3,e4] [g2,d3,b3]
                           [c3,g3,e4] [a2,e3,c4] [f2,c3,a3] [e2,b2,g#3]>""",
                 s="triangle", attack=1.0, release=2.0, lpf=900, room=0.6, gain=0.25),
            dict(note="<~ [~ e5 ~ a5] ~ [~ c6 ~ b5] ~ [~ e5 ~ c6] ~ [~ b5 ~ g#5]>", s="sine", room=0.9, delay=0.4,
                 gain=0.2),
            dict(note="<a1 f1 c2 g1 c2 a1 f1 e1>", s="sine", gain=0.35),
        ]),
    "last_stand": dict(
        nome="LAST STAND", autor="Gomes", cps=0.4, voltas=13,
        camadas=[
            dict(note="""<
                [e4@3 g4@4 d4 e4@3 g4@4 b4]
                [e4@2 g4@2 d4@2 f4@2 c4@2 c3 d3 e3 f3 g3 a3 b3 c4 ~]
                [g4 g4 ~ g4 ~ g4 ~ g4 f4@2 e4@2 d4@2 b3@2]
                [g3@2 g3@2 a3@2 b3 ~]
                [b4@4 a4@2 g4@2 d5@8]
                [c5@4 b4@2 a4@2 e4@8]
                [a4@4 b4@2 c5@2 d5@4 b4@4]
                [g4@3 e4@3 d4@2 c4@8]
                [c4@3 e4 g4 b4]
                [e3 e3 e4 e3 e3 e4 d4 e4 e3 e3 e4 e3 g4 f4 e4 d4]
                [c3 c3 c4 c3 c3 c4 b3 c4 c3 c3 c4 c3 e4 d4 c4 b3]
                [a2 a2 a3 a2 a2 a3 g3 a3 b2 b2 b3 b2 d4 c4 b3 a3]
                [b3@4 d#4@4 f#4@4 b4@4]
            >""", s="square", lpf=1500, room=0.5, gain=0.45),
            dict(note="""<
                [e3,g3,b3] [c3,e3,g3] [g2,b2,d3] [d3,f#3,a3]
                [g2,b2,d3] [a2,c3,e3] [d3,f#3,a3] [c3,e3,g3]
                [c3,e3,g3]
                [e3,g3,b3] [c3,e3,g3] [a2,c3,e3] [b2,d#3,f#3]
            >""", s="sawtooth", attack=0.3, release=1.2, lpf=1200, room=0.6, gain=0.28),
            dict(note="<[e3*8] [c3*8] [g3*8] [d3*8] ~ ~ ~ ~ ~ [e3*8] [c3*8] [a2*8] [b2*8]>", s="sawtooth", lpf=900,
                 gain=0.22),
            dict(note="""<[e1 e1] [c2 c2] [g1 g1] [d2 d2] [g1 g1] [a1 a1] [d2 d2] [c2 c2]
                           [c2@4] [e1*8] [c2*8] [a1*8] [b1*8]>""", s="square", lpf=350, gain=0.45),
            dict(s="""<[bd ~ bd ~ bd bd ~ ~, ~ ~ ~ ~ sd ~ ~ ~]!4
                      [bd ~ ~ ~ ~ ~ ~ ~, ~ ~ ~ ~ sd ~ ~ ~]!4
                      [sd*8]
                      [bd bd bd bd, ~ sd ~ sd, hh*8]!3
                      [bd*4, sd*16]>""", gain=0.8),
        ]),
}


# =====================================================================
# A MINI-NOTAÇÃO (o texto das notas vira uma árvore; a árvore vira eventos no tempo)
# =====================================================================
class _Leitor:
    def __init__(self, texto):
        self.t = texto.replace("\n", " ")
        self.i = 0

    def espia(self):
        while self.i < len(self.t) and self.t[self.i] in " \t\r":
            self.i += 1
        return self.t[self.i] if self.i < len(self.t) else ""

    def pega(self):
        c = self.espia()
        self.i += 1
        return c

    def numero(self):
        ini = self.i
        while self.i < len(self.t) and (self.t[self.i].isdigit() or self.t[self.i] == "."):
            self.i += 1
        return float(self.t[ini:self.i])

    def camadas(self, fecha):
        """Uma lista de sequências separadas por vírgula (tocam juntas), até o caractere de fechar."""
        grupos = [self.sequencia(fecha)]
        while self.espia() == ",":
            self.pega()
            grupos.append(self.sequencia(fecha))
        return grupos[0] if len(grupos) == 1 else ("juntos", grupos)

    def sequencia(self, fecha):
        itens = []  # (nó, peso)
        while True:
            c = self.espia()
            if c == "" or c in fecha or c == ",":
                break
            no = self.elemento()
            peso, repete = 1.0, 1
            while self.espia() in ("*", "!", "@", "/"):
                op = self.pega()
                if op == "!" and not (self.i < len(self.t) and self.t[self.i].isdigit()):
                    repete += 1
                    continue
                v = self.numero()
                if op == "*":
                    no = ("rapido", no, v)
                elif op == "/":
                    no = ("rapido", no, 1 / v)
                elif op == "!":
                    repete = int(v)
                else:
                    peso = v
            itens += [(no, peso)] * repete
        return ("seq", itens)

    def elemento(self):
        c = self.espia()
        if c == "[":
            self.pega()
            no = self.camadas("]")
            self.pega()
            return no
        if c == "<":
            self.pega()
            no = self.camadas(">")
            self.pega()
            if no[0] == "seq":
                return ("volta", [n for n, _ in no[1] for _ in [0]], [p for _, p in no[1]])
            return ("juntos", [("volta", [n for n, _ in s[1]], [p for _, p in s[1]]) for s in no[1]])
        ini = self.i
        while self.i < len(self.t) and self.t[self.i] not in " \t\r[]<>,*!@/":
            self.i += 1
        palavra = self.t[ini:self.i]
        return ("nada",) if palavra in ("~", "-") else ("valor", palavra)


def ler(texto):
    return _Leitor(texto).camadas("")


def eventos(no, volta, ini, dur, saida):
    """Coloca em 'saida' os (início, fim, valor) desse nó, que ocupa [ini, ini + dur) na volta 'volta'."""
    tipo = no[0]
    if tipo == "valor":
        saida.append((ini, ini + dur, no[1]))
    elif tipo == "seq":
        total = sum(p for _, p in no[1]) or 1
        t = ini
        for filho, p in no[1]:
            d = dur * p / total
            eventos(filho, volta, t, d, saida)
            t += d
    elif tipo == "juntos":
        for filho in no[1]:
            eventos(filho, volta, ini, dur, saida)
    elif tipo == "volta":  # <a b c>: um por volta (os pesos @ contam como várias voltas)
        filhos, pesos = no[1], no[2]
        ciclo = sum(int(round(p)) for p in pesos)
        k = volta % ciclo
        for filho, p in zip(filhos, pesos):
            if k < p:
                eventos(filho, volta // ciclo * 0 + volta, ini, dur, saida)
                break
            k -= p
    elif tipo == "rapido":  # x*n: n cópias no mesmo espaço (cada cópia é uma "volta" a mais pra dentro)
        n = no[2]
        inteiro = int(math.ceil(n))
        d = dur / n
        for i in range(inteiro):
            eventos(no[1], volta * inteiro + i, ini + i * d, d, saida)


# =====================================================================
# O SINTETIZADOR
# =====================================================================
NOTAS = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}


def midi(nome):
    """'g#3' -> 56 (o Strudel usa c4 = 60)."""
    n = NOTAS[nome[0].lower()]
    resto = nome[1:]
    while resto and resto[0] in "#sb":
        n += 1 if resto[0] in "#s" else -1
        resto = resto[1:]
    return 12 * (int(resto or "3") + 1) + n


def freq(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _onda(tipo, f, n):
    fase = np.arange(n) * f / TAXA
    if tipo == "square":
        return np.where(fase % 1 < 0.5, 1.0, -1.0) * 0.6
    if tipo == "sawtooth":
        return (2 * (fase % 1) - 1) * 0.6
    if tipo == "triangle":
        return (2 * np.abs(2 * (fase % 1) - 1) - 1)
    return np.sin(2 * np.pi * fase)


def _piano(f, n):
    """Um 'piano' sintetizado: harmônicos que somem mais rápido no agudo e uma batidinha no começo."""
    t = np.arange(n) / TAXA
    x = np.zeros(n)
    for h, a in ((1, 1.0), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06)):
        x += a * np.sin(2 * np.pi * f * h * t * (1 + 0.0004 * h * h)) * np.exp(-t * (1.6 + 0.9 * h + f / 500))
    x *= np.clip(t / 0.004, 0, 1)
    return x * 0.5


def _envelope(n, n_soando, ataque, soltura):
    t = np.arange(n) / TAXA
    dur = n_soando / TAXA
    sobe = np.clip(t / max(ataque, 0.003), 0, 1)
    desce = np.where(t < dur, 1.0, np.clip(1 - (t - dur) / max(soltura, 0.01), 0, 1))
    return sobe * desce


def _bumbo(rnd):
    n = int(TAXA * 0.35)
    t = np.arange(n) / TAXA
    f = 50 + 110 * np.exp(-t * 28)
    x = np.sin(2 * np.pi * np.cumsum(f) / TAXA) * np.exp(-t * 9)
    x[:60] += rnd.uniform(-0.4, 0.4, 60) * np.linspace(1, 0, 60)
    return x * 1.1


def _caixa(rnd):
    n = int(TAXA * 0.22)
    t = np.arange(n) / TAXA
    ruido = rnd.uniform(-1, 1, n)
    ruido = ruido - np.concatenate([[0], ruido[:-1]]) * 0.6
    tom = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return (ruido * np.exp(-t * 16) * 0.55 + tom * 0.5) * 0.9


def _chimbal(rnd):
    n = int(TAXA * 0.06)
    t = np.arange(n) / TAXA
    ruido = rnd.uniform(-1, 1, n)
    agudo = ruido - np.concatenate([[0], ruido[:-1]])
    return agudo * np.exp(-t * 70) * 0.35


BATERIA = {"bd": _bumbo, "sd": _caixa, "hh": _chimbal}


def _passa_baixa(x, corte):
    """Abafa o som acima da frequência de corte (como o .lpf do Strudel), rápido pela FFT."""
    if not corte or len(x) < 2:
        return x
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / TAXA)
    X /= np.sqrt(1 + (f / corte) ** 4)
    return np.fft.irfft(X, len(x))


def _sala(x, quanto):
    """O .room: o eco de sala (reverberação), juntando o som com uma 'cauda' de ruído que vai sumindo."""
    if quanto <= 0:
        return x
    rnd = np.random.default_rng(7)
    n_ir = int(TAXA * (0.6 + 1.6 * quanto))
    t = np.arange(n_ir) / TAXA
    ir = rnd.uniform(-1, 1, n_ir) * np.exp(-t * (5.0 / (0.6 + 1.6 * quanto)))
    ir = _passa_baixa(ir, 3500)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    n = len(x) + n_ir
    tam = 1 << (n - 1).bit_length()
    molhado = np.fft.irfft(np.fft.rfft(x, tam) * np.fft.rfft(ir, tam), tam)[:len(x)]
    return x * (1 - 0.35 * quanto) + molhado * quanto * 0.9


def _eco(x, quanto, tempo=0.25, volta=0.45):
    """O .delay: repete o som atrasado, cada vez mais baixo."""
    if quanto <= 0:
        return x
    y = x.copy()
    passo = int(TAXA * tempo)
    ganho = quanto
    k = passo
    while ganho > 0.02 and k < len(x):
        y[k:] += x[:-k] * ganho
        ganho *= volta
        k += passo
    return y


def renderizar(nome):
    """A música inteira (todas as voltas) como um vetor de amostras de -1 a 1 (TAXA por segundo)."""
    m = MUSICAS[nome]
    seg_volta = 1 / m["cps"]
    total = int(TAXA * seg_volta * m["voltas"]) + 1
    mix = np.zeros(total)
    for ci, c in enumerate(m["camadas"]):
        texto = c.get("note") or c["s"]
        arvore = ler(texto)
        evs = []
        for v in range(m["voltas"]):
            eventos(arvore, v, v, 1.0, evs)
        camada = np.zeros(total + int(TAXA * 3))
        rnd = np.random.default_rng(11 + ci)
        for ini, fim, valor in evs:
            i = int(ini * seg_volta * TAXA)
            if valor in BATERIA:
                som = BATERIA[valor](rnd)
            else:
                dur = (fim - ini) * seg_volta
                soltura = c.get("release", 0.08 if c.get("s") != "piano" else 0.6)
                n_soa = int(TAXA * dur)
                n = n_soa + int(TAXA * soltura)
                f = freq(midi(valor))
                if c.get("s") == "piano":
                    som = _piano(f, n + int(TAXA * 0.6))
                    som *= _envelope(len(som), n_soa + int(TAXA * 0.25), 0.003, 0.6)
                else:
                    som = _onda(c.get("s", "triangle"), f, n) * _envelope(n, n_soa, c.get("attack", 0.005), soltura)
            fim_i = min(len(camada), i + len(som))
            camada[i:fim_i] += som[:fim_i - i]
        camada = _passa_baixa(camada, c.get("lpf"))
        camada = _eco(camada, c.get("delay", 0))
        camada = _sala(camada, c.get("room", 0))
        mix += camada[:total] * c.get("gain", 1.0)
    pico = np.abs(mix).max() or 1
    return mix / pico * 0.95


def nome_de(nome):
    """'WARRIOR SPIRIT' (pro RADINHO mostrar)."""
    m = MUSICAS.get(nome)
    return m["nome"] if m else ""


# =====================================================================
# GUARDAR a música pronta (fabricar leva uns segundos: na 2ª vez o jogo só lê o arquivo)
# =====================================================================
VERSAO_SINTETIZADOR = 1


def carregar(nome, pasta=None):
    """A música pronta (vetor de -1 a 1). Guarda numa pastinha 'musica_pronta' (do lado do save) e só fabrica de
    novo se a música (ou o sintetizador) mudar."""
    import hashlib
    import os
    m = MUSICAS[nome]
    chave = hashlib.md5(repr((VERSAO_SINTETIZADOR, TAXA, m)).encode()).hexdigest()[:12]
    arquivo = None
    if pasta:
        try:
            os.makedirs(pasta, exist_ok=True)
            arquivo = os.path.join(pasta, f"{nome}_{chave}.npy")
            if os.path.exists(arquivo):
                return np.load(arquivo).astype(np.float64) / 32767
        except OSError:
            arquivo = None
    x = renderizar(nome)
    if arquivo:
        try:
            np.save(arquivo, (x * 32767).astype(np.int16))
        except OSError:
            pass
    return x


# =====================================================================
# O RADINHO (ideia do Gomes): um radinho em pixel art tocando, bem pequenininho, com o nome da música no cantinho
# =====================================================================
RADIO = [
    "......k.....",
    ".......k....",
    "kkkkkkkkkkkk",
    "krrrrrrrrrrk",
    "krkkkrwwwwrk",
    "krkskrrrrrrk",
    "krkkkrwyywrk",
    "krrrrrrrrrrk",
    "kkkkkkkkkkkk",
]
RADIO_CORES = {"k": (24, 18, 30), "r": (200, 70, 60), "w": (230, 226, 210), "s": (90, 80, 100), "y": (255, 210, 70)}
_radio_cache = {}


def desenhar_radio(tela, x, y, nome, t, escala=3):
    """O radinho em (x, y) = canto de cima à esquerda, com o alto-falante pulsando no ritmo, notinhas subindo e o
    NOME da música do lado. t = quadros (60 por segundo). Só desenho."""
    from efeitos import fonte
    batida = (t // 10) % 2
    chave = (escala, batida)
    img = _radio_cache.get(chave)
    if img is None:
        import pygame
        peq = pygame.Surface((len(RADIO[0]), len(RADIO)), pygame.SRCALPHA)
        for j, linha in enumerate(RADIO):
            for i, c in enumerate(linha):
                if c != ".":
                    cor = RADIO_CORES[c]
                    if c == "s" and batida:  # o alto-falante "batendo"
                        cor = (150, 140, 160)
                    peq.set_at((i, j), cor)
        img = pygame.transform.scale(peq, (peq.get_width() * escala, peq.get_height() * escala))
        _radio_cache[chave] = img
    import pygame
    tela.blit(img, (x, y + (escala if batida else 0) // 2))
    for k in range(2):  # as NOTINHAS subindo
        u = (t + k * 30) % 60
        nx, ny = x + img.get_width() + 2 + k * escala * 2, y + img.get_height() // 2 - u * escala * 0.25
        if u < 50:
            pygame.draw.rect(tela, (255, 230, 120), (nx, ny, escala, escala))
            pygame.draw.rect(tela, (255, 230, 120), (nx + escala, ny - escala * 2, escala // 2 + 1, escala * 2))
    rot = fonte(max(10, escala * 4)).render(nome, True, (240, 236, 220))
    sombra = fonte(max(10, escala * 4)).render(nome, True, (20, 16, 24))
    tx, ty = x + img.get_width() + escala * 7, y + img.get_height() // 2 - rot.get_height() // 2
    tela.blit(sombra, (tx + 1, ty + 1))
    tela.blit(rot, (tx, ty))
