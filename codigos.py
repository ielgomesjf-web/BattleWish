"""A tela de CÓDIGOS: digita um código secreto e desbloqueia coisas (tipo os jogos antigos)."""
import math

import pygame

import save
import som
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande
from selecao import fundo_selecao

# código -> o que ele desbloqueia (as roupas secretas vêm do roupas.py)
CODIGOS = {"ULTRA-MEGA-FROG": ("ribbat", "RIBBAT DESBLOQUEADO!"),
           "ULTRA-MEGA-VILLAGE": ("cenario", "VILA DOS SAPOS DESBLOQUEADA!")}


# CHARADAS (pedido do Gomes): a pista da roupa secreta na loja, sem entregar o código. Nível MÉDIO.
CHARADAS = {
    "IRONMAN": "Um herói inteiro feito de ferro voa por aí. Chame ele na língua dos filmes, tudo junto.",
    "FIGHTMON": "Monstrinhos de bolso que vivem lutando. Junte 'luta' com o começo de 'monstro', na língua dos filmes.",
    "DINOWOLF": "Metade réptil gigante de antigamente, metade bicho que uiva pra lua. Na língua dos filmes, tudo junto.",
    "DESTEMIBLEWARRIOR": "Um guerreiro que não tem medo de nada. 'Destemido' quase do jeito daqui, e 'guerreiro' na "
                         "língua dos filmes.",
    "MEGACANNON": "A arma do braço dele, só que muito, muito maior. Na língua dos filmes, tudo junto.",
    "THEBESTMAGICIAN": "Não é um mago qualquer: é o melhor de todos. Diga 'o melhor mágico' na língua dos filmes.",
    "CARDFIGHT": "Duas coisas que ele faz: jogar carta e brigar. Na língua dos filmes, com um & no meio.",
    "UNTAMABLE": "Ninguém consegue domar essa fera. Diga 'indomável' na língua dos filmes.",
    "FENRIR": "O lobo gigante das lendas nórdicas, de quem até os deuses tinham medo. Diga o nome dele.",
    "THEMOONISMINE": "Um vilão olha pro céu e grita que a lua é dele. Diga a frase na língua dos filmes, tudo junto.",
    "TIGERHAT": "Um gatão listrado usando a cartola. Diga o bicho e o chapéu na língua dos filmes.",
    "MAGICCREATURES": "Seres mágicos e assombrados. Diga 'criaturas mágicas' na língua dos filmes.",
    "MASTEROFTACTICS": "O raptor mais esperto do bando, mestre em planos de caça. Diga 'mestre das táticas' na língua "
                       "dos filmes.",
    "ANCIENTJAW": "O avô de todos os tubarões tinha a mandíbula mais antiga do mar. Diga isso na língua dos filmes.",
    "BIGFOOTPRINT": "Na floresta ficou a marca de um pé enorme. Diga isso na língua dos filmes, tudo junto.",
    "THEDARKESTDUMMY": "O boneco de treino mais sombrio que existe. Diga isso na língua dos filmes, tudo junto.",
    "BRUTEFORTUNE": "Força bruta e uma fortuna em ouro. Junte as duas na língua dos filmes.",
    "ULTRAMEGASKINS": "Ultra, mega e roupas, na língua dos filmes, com tracinhos. O sapo mais roubado agradece.",
    "ULTRAMEGAFROG": "Ultra, mega e o bicho que diz ribbit, na língua dos filmes, com tracinhos.",
    "ULTRAMEGAVILLAGE": "Ultra, mega e o lugar onde os sapos moram, na língua dos filmes, com tracinhos.",
}


def charada(codigo):
    return CHARADAS.get(_limpo(codigo or ""))


def _limpo(c):
    """Tanto faz maiúscula, espaço ou tracinho: Iron Man = IRON-MAN = IRONMAN."""
    return "".join(ch for ch in c.upper() if ch.isalnum())


def ativo(codigo):
    return codigo in save.d().setdefault("codigos", [])


def usar(texto_digitado):
    """Tenta o código. Devolve a mensagem de sucesso, ou None se o código não existe."""
    import roupas
    c = _limpo(texto_digitado)
    certo = next((k for k in CODIGOS if _limpo(k) == c), None)
    lista = save.d().setdefault("codigos", [])
    if certo:
        if certo not in lista:
            lista.append(certo)
            save.salvar()
        return CODIGOS[certo][1]
    secretas = {_limpo(k): v for k, v in roupas.de_codigo().items()}
    if c not in secretas:
        return None
    for nome, r in secretas[c]:
        if not save.tem_roupa(nome, r["id"]):
            save.d()["roupas"].setdefault(nome, []).append(r["id"])
    nome, r = secretas[c][0]
    if len({n for n, _ in secretas[c]}) > 1:  # pra todo mundo (SOMBRA, OURO): não veste ninguém sozinho
        if c not in lista:
            lista.append(c)
        save.salvar()
        return f"{r['nome']} PRA TODO MUNDO!"
    save.usar(nome, r["id"])  # (já veste a primeira)
    if c not in lista:
        lista.append(c)
    save.salvar()
    from personagens import SECRETOS, disponiveis
    if any(f["nome"] == nome for f in SECRETOS) and not any(f["nome"] == nome for f in disponiveis()):
        return f"ROUPAS DO {nome} GUARDADAS!"  # (ele ainda é secreto: falta o código dele)
    if len(secretas[c]) > 1:
        return f"{nome}: {len(secretas[c])} ROUPAS NOVAS!"
    return f"{nome}: {r['nome']}!"


class TelaCodigos:
    def __init__(self):
        self.digitado = ""
        self.msg, self.msg_t, self.acertou = "", 0, False
        self.t = 0

    def tecla(self, ev):
        if ev.key == pygame.K_BACKSPACE:
            self.digitado = self.digitado[:-1]
        elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            msg = usar(self.digitado)
            if msg:
                self.msg, self.acertou = msg, True
                som.tocar("ultimate")
            else:
                self.msg, self.acertou = "código errado...", False
                som.tocar("defesa")
            self.msg_t = 180
            self.digitado = ""
        elif ev.unicode and (ev.unicode.isalnum() or ev.unicode in "-_&") and len(self.digitado) < 24:
            self.digitado += ev.unicode.upper()
            som.tocar("blip", 0.5)

    def desenhar(self, tela):
        self.t += 1
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, "CÓDIGOS", 46, (255, 220, 70), (LARGURA // 2, 70))
        texto(tela, "digite um código secreto:", 18, (220, 220, 235), (LARGURA // 2, 170))
        r = pygame.Rect(LARGURA // 2 - 260, 200, 520, 70)
        pygame.draw.rect(tela, (20, 16, 34), r, border_radius=12)
        pygame.draw.rect(tela, (255, 220, 70), r, 3, border_radius=12)
        cursor = "_" if (self.t // 20) % 2 else " "
        texto_grande(tela, self.digitado + cursor, 34, BRANCO, r.center)
        if self.msg_t > 0:
            self.msg_t -= 1
            if self.acertou:
                esc = 1 + 0.08 * math.sin(self.t * 0.3)
                texto_grande(tela, self.msg, 40, (120, 255, 150), (LARGURA // 2, 340), esc, contorno=(10, 40, 20))
                dica = "a roupa já está vestida!" if ":" in self.msg else "olha a tela de seleção..."
                if "TODO MUNDO" in self.msg:
                    dica = "veste na seleção (Q/E) ou na LOJA"
                elif "VILA" in self.msg:
                    dica = "olha a escolha de cenário..."
                if "GUARDADAS" in self.msg:
                    dica = "mas ele ainda é secreto... falta descobrir o código dele!"
                texto(tela, dica, 16, (220, 220, 235), (LARGURA // 2, 386))
            else:
                texto(tela, self.msg, 22, (255, 130, 110), (LARGURA // 2, 330))
        faltam = [c for c in CODIGOS if not ativo(c) and charada(c)]
        if faltam:  # as PISTAS dos segredos que ainda faltam (Ribbat e a Vila), sem entregar o código
            texto(tela, "PISTAS DOS SEGREDOS", 13, (255, 200, 90), (LARGURA // 2, 412))
            fnt = pygame.font.SysFont("arial", 14, bold=True)
            for i, c in enumerate(faltam):
                quem = "LUTADOR SECRETO" if CODIGOS[c][0] == "ribbat" else "CENÁRIO SECRETO"
                img = fnt.render(f"{quem}: {charada(c)}", True, (235, 230, 250))
                tela.blit(img, (LARGURA // 2 - img.get_width() // 2, 424 + i * 20))
        n = len(save.d().get("codigos", []))
        if n:
            texto(tela, f"códigos descobertos: {n}", 14, (190, 190, 210), (LARGURA // 2, 484))
        texto(tela, "ENTER confirma   BACKSPACE apaga   ESC volta", 14, (200, 200, 220), (LARGURA // 2, ALTURA - 16))
