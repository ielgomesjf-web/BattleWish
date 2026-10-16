"""CONTROLE DE VIDEOGAME (Xbox, PlayStation ou genérico pelo USB).

Botões na luta:
  direcional ou analógico   andar / pular / agachar
  A soco    B chute
  X = E     Y = Q     LB = R     RB = SHIFT      (no controle não precisa segurar nada: cada especial tem o seu botão)
  RT = ULTIMATE (segurar carrega, igual o Z)     LT = PROVOCAR
  START = pausa
Nos menus: direcional anda, A confirma, B volta.
"""
import pygame

try:
    from pygame._sdl2 import controller as _ctl
except ImportError:  # pygame sem suporte: o jogo funciona só com teclado e mouse
    _ctl = None

CONTROLES = []          # os controles ligados agora
usando = "teclado"      # o último que o jogador mexeu: "teclado" ou "controle" (a tela mostra os botões dele)
ZONA_MORTA = 0.45       # analógico: menos que isso conta como "solto"
GATILHO = 0.5


def iniciar():
    if _ctl:
        try:
            _ctl.init()
        except pygame.error:
            return
    atualizar()


def atualizar():
    """Liga os controles conectados (chamar quando alguém pluga ou tira um)."""
    if not _ctl:
        return
    novos = []
    for i in range(_ctl.get_count()):
        try:
            if _ctl.is_controller(i):
                novos.append(_ctl.Controller(i))
        except pygame.error:
            continue
    CONTROLES[:] = novos


def _botao(c, nome):
    try:
        return bool(c.get_button(getattr(pygame, "CONTROLLER_BUTTON_" + nome)))
    except (pygame.error, AttributeError):
        return False


def _eixo(c, nome):
    try:
        return c.get_axis(getattr(pygame, "CONTROLLER_AXIS_" + nome)) / 32767
    except (pygame.error, AttributeError):
        return 0.0


def estado(c):
    """O que está apertado nesse controle agora."""
    h = (_botao(c, "DPAD_RIGHT") - _botao(c, "DPAD_LEFT"))
    v = (_botao(c, "DPAD_UP") - _botao(c, "DPAD_DOWN"))
    lx, ly = _eixo(c, "LEFTX"), _eixo(c, "LEFTY")
    if not h and abs(lx) > ZONA_MORTA:
        h = 1 if lx > 0 else -1
    if not v and abs(ly) > ZONA_MORTA:
        v = -1 if ly > 0 else 1  # (no analógico, pra baixo é positivo)
    return {
        "h": h, "v": v,
        "soco": _botao(c, "A"), "chute": _botao(c, "B"),
        "E": _botao(c, "X"), "Q": _botao(c, "Y"), "R": _botao(c, "LEFTSHOULDER"), "SHIFT": _botao(c, "RIGHTSHOULDER"),
        "Z": _eixo(c, "TRIGGERRIGHT") > GATILHO,
        "barra": _eixo(c, "TRIGGERLEFT") > GATILHO,          # LT: EX (segurando) e ESCAPE (apertando apanhando)
        "troca": _botao(c, "RIGHTSTICK"),                    # R3: troca de lutador no TRIO
        "lobo": _botao(c, "LEFTSTICK"),                      # L3: TAMER troca a cor do lobo
        "provoca": _botao(c, "BACK"),
    }


# eventos do controle nos menus -> teclas (assim todas as telas já funcionam com o controle)
MENU = {"DPAD_UP": pygame.K_w, "DPAD_DOWN": pygame.K_s, "DPAD_LEFT": pygame.K_a, "DPAD_RIGHT": pygame.K_d,
        "A": pygame.K_RETURN, "B": pygame.K_ESCAPE, "START": pygame.K_ESCAPE,
        "LEFTSHOULDER": pygame.K_q, "RIGHTSHOULDER": pygame.K_e, "Y": pygame.K_h}  # (LB/RB troca a roupa, Y a habilidade)

# o nome de cada coisa no controle (pra mostrar na tela)
NO_CONTROLE = {"E": "X", "Q": "Y", "R": "LB", "SHIFT": "RB", "Z": "RT", "soco": "A", "chute": "B", "provoca": "BACK",
               "barra": "LT", "troca": "R3", "lobo": "L3"}
NO_TECLADO = {"soco": "M1", "chute": "M2", "provoca": "T", "barra": "F", "troca": "G", "lobo": "X"}


def no_controle():
    """O jogador está usando o controle agora? (aí a tela mostra os botões do controle)"""
    return usando == "controle" and bool(CONTROLES)


def nome(botao):
    """'E' -> 'X' no controle, 'M3+E' no teclado...  'soco' -> 'A' ou 'M1'."""
    if no_controle():
        return NO_CONTROLE.get(botao, botao)
    return NO_TECLADO.get(botao, "M3+" + botao if botao in ("E", "Q", "R", "SHIFT", "Z") else botao)


def perceber(ev):
    """Olha o evento e guarda se o jogador está no teclado ou no controle."""
    global usando
    if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
        usando = "teclado"
    elif ev.type == getattr(pygame, "CONTROLLERBUTTONDOWN", -1):
        usando = "controle"
    elif ev.type == getattr(pygame, "CONTROLLERAXISMOTION", -1) and abs(getattr(ev, "value", 0)) > 16000:
        usando = "controle"


def vibrar(c, forca, ms):
    """Treme o controle (forca de 0 a 1)."""
    if c is None:
        return
    try:
        f = max(0.0, min(1.0, forca))
        c.rumble(f * 0.7, f, int(ms))
    except (pygame.error, AttributeError, TypeError):
        pass


def tecla_do_evento(ev, na_luta):
    """Um botão do controle virou qual tecla? (na luta, só o START, que pausa)"""
    if ev.type != getattr(pygame, "CONTROLLERBUTTONDOWN", -1):
        return None
    for nome, tecla in MENU.items():
        if ev.button == getattr(pygame, "CONTROLLER_BUTTON_" + nome, -99):
            if na_luta and nome != "START":
                return None
            return tecla
    return None
