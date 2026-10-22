"""Sons e música, feitos pelo próprio código (nenhum arquivo de áudio).

Cada som é "sintetizado": ondas (seno, quadrada, dente de serra), ruído e envelopes (como o som sobe e some).
Se o computador não tiver som, o jogo continua funcionando (só fica mudo).
"""
import os

import numpy as np
import pygame

TAXA = 22050
_sons = {}
_ok = None
_musica_atual = None
VOLUME_EFEITOS = 0.55
VOLUME_MUSICA = 0.32
MULT_EFEITOS = MULT_MUSICA = 1.0  # o que o jogador escolheu nas CONFIGURAÇÕES (0 a 1)


def aplicar_volumes():
    """Lê os volumes das CONFIGURAÇÕES (no save) e já aplica na música que está tocando."""
    global MULT_EFEITOS, MULT_MUSICA
    import save
    MULT_MUSICA = save.d().get("vol_musica", 100) / 100
    MULT_EFEITOS = save.d().get("vol_efeitos", 100) / 100
    chave = "musica_" + str(_musica_atual)
    if chave in _sons:
        try:
            _sons[chave].set_volume(VOLUME_MUSICA * MULT_MUSICA)
        except Exception:
            pass


def _iniciar():
    global _ok
    if _ok is None:
        if os.environ.get("SEM_SOM"):
            _ok = False
            return _ok
        try:
            pygame.mixer.pre_init(TAXA, -16, 2, 512)
            if not pygame.mixer.get_init():
                pygame.mixer.init(TAXA, -16, 2, 512)
            pygame.mixer.set_num_channels(24)
            pygame.mixer.set_reserved(1)  # o canal 0 é só da música
            _ok = True
        except pygame.error:
            _ok = False
    return _ok


# =====================================================================
# Sintetizador
# =====================================================================
def _t(dur):
    return np.arange(int(TAXA * dur)) / TAXA


def _env(n, ataque=0.005, queda=4.0):
    """Envelope: sobe rapidinho e vai sumindo."""
    t = np.arange(n) / TAXA
    sobe = np.clip(t / max(ataque, 1e-4), 0, 1)
    return sobe * np.exp(-t * queda)


def _ruido(dur, seed=1):
    return np.random.default_rng(seed).uniform(-1, 1, int(TAXA * dur))


def _passa_baixa(x, k=0.15):
    """Deixa o som mais 'abafado' (média simples que corre)."""
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += k * (x[i] - acc)
        y[i] = acc
    return y


def _seno(f, dur):
    t = _t(dur)
    return np.sin(2 * np.pi * np.cumsum(np.broadcast_to(f, t.shape)) / TAXA)


def _quadrada(f, dur):
    return np.sign(_seno(f, dur))


def _serra(f, dur):
    fase = np.cumsum(np.broadcast_to(f, _t(dur).shape)) / TAXA
    return 2 * (fase % 1) - 1


def _varredura(f0, f1, dur):
    return np.linspace(f0, f1, int(TAXA * dur))


def _som(x, vol=1.0):
    x = np.clip(x * vol, -1, 1)
    x = (x * 32767 * 0.9).astype(np.int16)
    estereo = np.ascontiguousarray(np.column_stack([x, x]))
    return pygame.sndarray.make_sound(estereo)


def _criar(nome):
    if nome == "soco":  # pancada curta
        n = _ruido(0.12, 2) * _env(int(TAXA * 0.12), 0.001, 40)
        g = _seno(_varredura(160, 60, 0.12), 0.12) * _env(int(TAXA * 0.12), 0.001, 25)
        return _som(_passa_baixa(n, 0.35) * 0.7 + g)
    if nome == "chute":  # pancada pesada
        n = _ruido(0.2, 3) * _env(int(TAXA * 0.2), 0.001, 22)
        g = _seno(_varredura(120, 40, 0.2), 0.2) * _env(int(TAXA * 0.2), 0.001, 14)
        return _som(_passa_baixa(n, 0.25) * 0.6 + g * 1.1)
    if nome == "defesa":  # metal batendo
        t = _t(0.18)
        x = (np.sin(2 * np.pi * 1250 * t) + 0.6 * np.sin(2 * np.pi * 1870 * t)) * _env(len(t), 0.001, 26)
        return _som(x * 0.6 + _ruido(0.18, 4) * _env(len(t), 0.001, 60) * 0.3)
    if nome == "parry":  # plim brilhante
        t = _t(0.45)
        x = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((1760, 0.6), (2637, 0.4), (3520, 0.25)))
        return _som(x * _env(len(t), 0.002, 7))
    if nome == "quebra":  # vidro quebrando
        n = _ruido(0.5, 5) * _env(int(TAXA * 0.5), 0.001, 9)
        t = _t(0.5)
        brilho = np.sin(2 * np.pi * 2900 * t) * _env(len(t), 0.001, 14) * 0.4
        return _som(n * 0.7 + brilho + _seno(_varredura(300, 80, 0.5), 0.5) * _env(len(t), 0.001, 8) * 0.5)
    if nome == "vento":  # golpe passando no ar
        n = _passa_baixa(_ruido(0.16, 6), 0.08)
        env = np.sin(np.linspace(0, np.pi, len(n))) ** 2
        return _som(n * env * 2.2, 0.5)
    if nome == "pulo":
        x = _quadrada(_varredura(220, 520, 0.12), 0.12) * _env(int(TAXA * 0.12), 0.002, 18)
        return _som(x, 0.25)
    if nome == "queda":  # caindo no chão
        n = _passa_baixa(_ruido(0.3, 7), 0.1) * _env(int(TAXA * 0.3), 0.002, 12)
        g = _seno(_varredura(90, 35, 0.3), 0.3) * _env(int(TAXA * 0.3), 0.002, 9)
        return _som(n * 1.4 + g)
    if nome == "ko":  # BUM grandão
        n = _passa_baixa(_ruido(1.4, 8), 0.06) * _env(int(TAXA * 1.4), 0.002, 2.5)
        g = _seno(_varredura(70, 28, 1.4), 1.4) * _env(int(TAXA * 1.4), 0.002, 2)
        return _som(n * 1.6 + g * 1.2)
    if nome == "laser":
        t = _t(0.35)
        x = _serra(_varredura(880, 300, 0.35), 0.35) * 0.5 + _quadrada(440 + 30 * np.sin(t * 90), 0.35) * 0.3
        return _som(x * _env(len(t), 0.004, 4), 0.5)
    if nome == "carga":  # energia juntando
        t = _t(0.7)
        x = _seno(_varredura(120, 900, 0.7), 0.7) * np.clip(t / 0.7, 0, 1)
        return _som(x * (1 + 0.5 * np.sin(t * 60)), 0.35)
    if nome == "tiro":  # pew
        x = _quadrada(_varredura(1300, 300, 0.1), 0.1) * _env(int(TAXA * 0.1), 0.001, 25)
        return _som(x, 0.3)
    if nome == "shuriken":  # shiiing
        t = _t(0.25)
        x = np.sin(2 * np.pi * _varredura(3000, 4200, 0.25).cumsum() / TAXA) * _env(len(t), 0.002, 10)
        return _som(x * 0.4 + _ruido(0.25, 9) * _env(len(t), 0.001, 30) * 0.2)
    if nome == "lingua":  # fluuup
        t = _t(0.3)
        x = _seno(_varredura(600, 140, 0.3), 0.3) * _env(len(t), 0.003, 6)
        return _som(x * 0.8 + _passa_baixa(_ruido(0.3, 10), 0.2) * _env(len(t), 0.002, 10) * 0.4)
    if nome == "explosao":
        n = _passa_baixa(_ruido(0.8, 11), 0.12) * _env(int(TAXA * 0.8), 0.002, 4)
        return _som(n * 1.8)
    if nome == "foguete":  # rugido de foguete
        n = _passa_baixa(_ruido(0.7, 12), 0.05)
        env = np.clip(np.linspace(0, 3, len(n)), 0, 1) * np.clip(np.linspace(3, 0, len(n)), 0, 1)
        return _som(n * env * 3.0, 0.6)
    if nome == "terra":  # tremor
        n = _passa_baixa(_ruido(0.8, 13), 0.03)
        t = _t(0.8)
        return _som((n * 4 + np.sin(2 * np.pi * 45 * t) * 0.5) * _env(len(t), 0.05, 3), 0.7)
    if nome == "puf":  # fumaça ninja
        n = _passa_baixa(_ruido(0.35, 14), 0.18) * _env(int(TAXA * 0.35), 0.003, 9)
        return _som(n * 1.6)
    if nome == "ultimate":  # acorde subindo
        t = _t(1.0)
        x = sum(np.sin(2 * np.pi * f * (1 + t * 0.3) * t) for f in (220, 277, 330, 440)) / 4
        return _som(x * np.clip(t / 0.6, 0, 1) * _env(len(t), 0.2, 1.5), 0.7)
    if nome == "uivo":  # AUUUUU
        t = _t(1.4)
        f = 320 + 260 * np.sin(np.clip(t / 1.4, 0, 1) * np.pi) + 8 * np.sin(t * 38)
        x = _seno(f, 1.4) * 0.7 + _serra(f, 1.4) * 0.15
        return _som(x * np.clip(t / 0.15, 0, 1) * np.clip((1.4 - t) / 0.5, 0, 1), 0.6)
    if nome == "blip":
        x = _quadrada(880, 0.05) * _env(int(TAXA * 0.05), 0.001, 40)
        return _som(x, 0.2)
    if nome == "confirma":
        x = np.concatenate([_quadrada(660, 0.06), _quadrada(990, 0.1)])
        return _som(x * _env(len(x), 0.001, 12), 0.25)
    if nome == "round":  # gongo
        t = _t(1.2)
        x = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((110, 1), (165, 0.6), (233, 0.4), (311, 0.3)))
        return _som(x * _env(len(t), 0.004, 2.2) * 0.5)
    if nome == "lutem":  # fanfarra curtinha
        notas = (392, 523, 659, 784)
        x = np.concatenate([_quadrada(f, 0.09) * _env(int(TAXA * 0.09), 0.002, 8) for f in notas[:3]] +
                           [_quadrada(notas[3], 0.35) * _env(int(TAXA * 0.35), 0.002, 4)])
        return _som(x, 0.3)
    raise KeyError(nome)


def tocar(nome, vol=1.0):
    """Toca um efeito de som (se der)."""
    if not _iniciar():
        return
    try:
        if nome not in _sons:
            _sons[nome] = _criar(nome)
        s = _sons[nome]
        s.set_volume(VOLUME_EFEITOS * vol * MULT_EFEITOS)
        s.play()
    except Exception:  # som nunca pode derrubar o jogo
        pass


# =====================================================================
# Música (provisória: o Gomes pode compor a dele no Strudel, igual no Ribbat)
# =====================================================================
def _nota(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def _musica_luta():
    bpm = 132
    passo = 60 / bpm / 4                  # semicolcheia
    n_passos = 16 * 8                     # 8 compassos
    total = int(TAXA * passo * n_passos)
    mix = np.zeros(total)
    escala = (0, 2, 3, 5, 7, 8, 10)       # menor
    raiz = 45                              # Lá
    baixo = [0, 0, 7, 0, 5, 5, 3, 3]       # graus por compasso
    melodia = "0 ~ 2 3 ~ 4 ~ 3 2 ~ 0 ~ 4 ~ 6 4"

    def soma(ini, x):
        fim = min(total, ini + len(x))
        mix[ini:fim] += x[:fim - ini]

    for c in range(8):
        for p in range(16):
            i = int((c * 16 + p) * passo * TAXA)
            if p in (0, 6, 8, 11):  # bumbo
                soma(i, _seno(_varredura(140, 45, 0.18), 0.18) * _env(int(TAXA * 0.18), 0.001, 14) * 0.9)
            if p in (4, 12):  # caixa
                soma(i, _passa_baixa(_ruido(0.15, c * 16 + p), 0.5) * _env(int(TAXA * 0.15), 0.001, 22) * 0.5)
            if p % 2 == 0:  # chimbal
                soma(i, _ruido(0.04, 99 + p) * _env(int(TAXA * 0.04), 0.001, 80) * 0.18)
            if p % 4 in (0, 3):  # baixo
                grau = baixo[c]
                f = _nota(raiz - 12 + escala[grau % 7] + 12 * (grau // 7))
                soma(i, _quadrada(f, passo * 1.8) * _env(int(TAXA * passo * 1.8), 0.003, 6) * 0.22)
        if c % 2 == 1:  # melodia nos compassos ímpares
            for p, tok in enumerate(melodia.split()):
                if tok == "~":
                    continue
                g = int(tok)
                f = _nota(raiz + 12 + escala[g % 7] + 12 * (g // 7) + (3 if c >= 4 else 0))
                i = int((c * 16 + p) * passo * TAXA)
                soma(i, _serra(f, passo * 1.6) * _env(int(TAXA * passo * 1.6), 0.004, 5) * 0.16)
    return _som(mix / max(1.0, np.abs(mix).max()) * 0.9)


def _musica_menu():
    bpm = 90
    passo = 60 / bpm / 2
    total = int(TAXA * passo * 32)
    mix = np.zeros(total)
    acordes = [(57, 60, 64), (53, 57, 60), (55, 59, 62), (52, 55, 59)]
    for k, ac in enumerate(acordes):
        for r in range(8):
            i = int((k * 8 + r) * passo * TAXA)
            f = _nota(ac[r % 3] + 12)
            x = _seno(f, passo * 2) * _env(int(TAXA * passo * 2), 0.01, 2.5) * 0.25
            mix[i:i + len(x)] += x[:max(0, total - i)]
    return _som(mix / max(1.0, np.abs(mix).max()) * 0.8)


# =====================================================================
# MÚSICAS do Gomes (do Strudel: musica.py): LUTA = WARRIOR SPIRIT, MENU = BEFORE THE BATTLE. Fabricar leva uns
# segundos na 1ª vez (depois fica guardada em "musica_pronta"), então começa numa THREAD quando o jogo abre; até
# ficar pronta, toca a música antiga (e o atualizar() troca assim que fica pronta).
# =====================================================================
MUSICA_MENU = "before_the_battle"
MUSICAS_LUTA = ["warrior_spirit", "last_stand"]  # (o RADINHO: sorteia uma por luta, sem repetir; M passa pra próxima)
MUSICA_LUTA = MUSICAS_LUTA[0]  # (a que está tocando na luta: o nome que o radinho mostra)
_prontas = {}  # nome da música -> o vetor, quando a thread termina
_sorteio = __import__("random").Random()  # (sorteio SÓ da música: não mexe no random da luta, o online fica igual)


def preparar_musicas():
    """Chamado quando o jogo abre (no menu): fabrica (ou lê do arquivo) as músicas do Gomes em segundo plano."""
    if not _iniciar() or _prontas:
        return
    import threading

    def fabrica():
        try:
            import musica as _m
            import save
            for nome in [MUSICA_MENU] + MUSICAS_LUTA:  # (o menu primeiro: é a que já está tocando)
                _prontas[nome] = _m.carregar(nome, os.path.join(save.pasta_do_jogo(), "musica_pronta"))
        except Exception:
            pass
    threading.Thread(target=fabrica, daemon=True).start()


def _trilha(nome):
    """O som pronto da música do Gomes (na taxa do mixer), ou None se ainda não ficou pronta."""
    if "trilha_" + nome not in _sons:
        if nome not in _prontas:
            return None
        try:
            x = _prontas[nome]
            freq = (pygame.mixer.get_init() or (TAXA,))[0]
            if freq != TAXA:  # (o mixer abriu em outra taxa: estica pra música tocar na velocidade e no tom certos)
                x = np.interp(np.arange(int(len(x) * freq / TAXA)) * TAXA / freq, np.arange(len(x)), x)
            _sons["trilha_" + nome] = _som(x * 0.9)
        except Exception:
            return None
    return _sons["trilha_" + nome]


def _escolher(qual, proxima=False):
    """Põe a música do Gomes no lugar de 'musica_<qual>'. Luta: sorteia (sem repetir a última) ou a PRÓXIMA."""
    global MUSICA_LUTA
    if qual == "menu":
        t = _trilha(MUSICA_MENU)
        if t:
            _sons["musica_menu"], _sons["_nova_menu"] = t, MUSICA_MENU
        return
    prontas = [n for n in MUSICAS_LUTA if _trilha(n)]
    if not prontas:
        return
    if proxima:
        i = MUSICAS_LUTA.index(MUSICA_LUTA)
        nome = next(MUSICAS_LUTA[(i + k) % len(MUSICAS_LUTA)] for k in range(1, len(MUSICAS_LUTA) + 1)
                    if MUSICAS_LUTA[(i + k) % len(MUSICAS_LUTA)] in prontas)
    else:
        outras = [n for n in prontas if n != _sons.get("_nova_luta")] or prontas
        nome = _sorteio.choice(outras)
    MUSICA_LUTA = nome
    _sons["musica_luta"], _sons["_nova_luta"] = _trilha(nome), nome


def proxima_musica():
    """(Tecla M na luta.) Passa pra próxima música de luta."""
    global _musica_atual
    if _musica_atual != "luta" or not _iniciar():
        return
    _escolher("luta", proxima=True)
    _musica_atual = None
    _ja_escolheu[0] = True
    musica("luta")


_ja_escolheu = [False]


def atualizar():
    """(Todo quadro, no laço do jogo.) A música do Gomes que está tocando ficou pronta agora? Já troca."""
    global _musica_atual
    if _musica_atual in ("menu", "luta") and not _sons.get("_nova_" + _musica_atual)             and (MUSICA_MENU if _musica_atual == "menu" else MUSICAS_LUTA[0]) in _prontas:
        agora, _musica_atual = _musica_atual, None
        musica(agora)


def musica(nome):
    """Troca a música ('luta', 'menu' ou None pra parar)."""
    global _musica_atual
    if not _iniciar() or nome == _musica_atual:
        return
    if nome in ("menu", "luta") and not _ja_escolheu[0]:
        _escolher(nome)  # (luta nova: sorteia a música)
    _ja_escolheu[0] = False
    try:
        canal = pygame.mixer.Channel(0)
        canal.stop()
        _musica_atual = nome
        if nome is None:
            return
        chave = "musica_" + nome
        if chave not in _sons:
            _sons[chave] = _musica_luta() if nome == "luta" else _musica_menu()
        _sons[chave].set_volume(VOLUME_MUSICA * MULT_MUSICA)
        canal.play(_sons[chave], loops=-1)
    except Exception:
        pass
