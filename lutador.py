"""O lutador: como ele se mexe, ataca, defende e apanha. E o desenho do palito."""
import math

import pygame

from config import *  # noqa: F401,F403
import habilidades as hab
import pecas
import som
from golpes import GOLPES, POSES, misturar, suave
import provocacao  # noqa: F401  (registra o golpe "provocar")

LIVRE = ("parado", "andando", "agachado")
# COMBOS: depois de um golpe normal ACERTAR, dá pra emendar estes (até 3 seguidos)
CADEIA = {"soco": ("soco", "chute"), "ag_soco": ("ag_soco", "ag_chute", "soco"),
          "chute": (), "ag_chute": (), "ar_soco": ("ar_soco", "ar_chute"), "ar_chute": ()}
CADEIA_MAX = 3
CADEIA_AR = 5          # no ar dá pra emendar mais (combo aéreo)
MALABAR_MAX = 12       # depois de tantos golpes no ar, o outro cai (sem combo infinito)
ESPELHO = {1: 3, 3: 1, 4: 6, 6: 4, 7: 9, 9: 7}
PADRAO = {"E": "bola", "Q": "subida", "R": "giro", "SHIFT": "avanco", "Z": "ultimate"}


class Entrada:
    """O que o jogador (ou o computador) está apertando neste quadro.
    dir segue o teclado numérico: 5 = nada, 6 = direita, 4 = esquerda, 8 = cima, 2 = baixo, 3 = baixo+direita...
    especial = qual botão de especial: "E", "Q", "R", "SHIFT" ou "Z"."""

    def __init__(self, dir=5, soco=False, chute=False, especial=None):
        self.dir, self.soco, self.chute, self.especial = dir, soco, chute, especial
        self.segura_ult = False  # ainda segurando o Z (o Cannan carrega a ultimate)
        self.provoca = False     # apertou T (provocação)
        self.barra = False       # segurando o botão de BARRA (F / LT): especial EX
        self.barra_toque = False  # apertou o botão de BARRA agora: ESCAPE de combo
        self.troca = False       # TRIO: apertou o botão de troca (G / R3)
        self.lobo = False        # TAMER: apertou X (troca a cor do lobo)


class Projetil:
    def __init__(self, dono, x, y, dir, golpe):
        self.dono, self.x, self.y = dono, x, y
        self.golpe = golpe
        self.vx = golpe["vel"] * dir
        self.raio = golpe["raio"]
        self.vivo = True
        self.t = 0
        self.ex = getattr(dono, "ex", False)          # saiu de um especial EX (bate mais forte)
        self.nome_golpe = dono.nome_golpe              # (pros desafios de combo: de qual golpe saiu)
        self.ativacao = getattr(dono, "golpe_id", 0)

    def rect(self):
        return pygame.Rect(self.x - self.raio, self.y - self.raio, self.raio * 2, self.raio * 2)

    def update(self):
        self.t += 1
        self.x += self.vx
        if self.x < -40 or self.x > LARGURA + 40:
            self.vivo = False

    def desenhar(self, tela):
        if self.golpe.get("desenho_proj"):
            return self.golpe["desenho_proj"](self, tela)
        cor = self.dono.f["cor_poder"]
        for i in range(4):  # rastro
            r = self.raio - i * self.raio // 5
            x = self.x - self.vx * i * 1.6
            pygame.draw.circle(tela, tuple(c // (i + 1) for c in cor), (int(x), int(self.y)), max(3, r))
        r = self.raio + math.sin(self.t * 0.6) * 2
        pygame.draw.circle(tela, cor, (int(self.x), int(self.y)), int(r))
        pygame.draw.circle(tela, BRANCO, (int(self.x), int(self.y)), int(r * 0.5))


class Lutador:
    def __init__(self, ficha, x, dir):
        self.f = ficha
        self.s = ficha["tam"]
        self.poses = dict(POSES)
        self.poses.update(ficha.get("poses", {}))  # cada personagem pode ter o próprio jeito de ficar parado, andar...
        self.extra = {}                             # coisas do personagem que duram a luta toda (ex: munição)
        self.disfarce = None                        # ficha de outro lutador (o Trafo se transformando)
        self.dano_combo_vista = 0
        self.mutado = None                          # Trafo com MUTAÇÃO: a ficha do oponente que ele virou
        self.entrada_t = None                       # quadro da entrada (começo da luta), ou None
        self.esconde = False                        # entrada: ainda não apareceu
        self.cortar_chao = False                    # entrada: parte embaixo do chão não aparece (Trafo saindo da terra)
        self.cortar_acima = None                    # entrada: acima dessa altura não aparece (Finn se materializando)
        self.x, self.y = float(x), float(CHAO)
        self.vx = self.vy = 0.0
        self.dir = dir
        self.vida = self.vida_max = ficha["vida"]
        self.vida_vista = self.vida  # a barra vermelha que desce devagar
        self.estado, self.t = "parado", 0
        self.golpe = self.nome_golpe = None
        self.acertou = False
        self.ja_atacou = False
        self.stun = 0
        self.inv = 0
        self.r = 5
        self.combo = 0
        self.projetil = None
        self.agachado_def = False
        self.barra = 0
        self.pediu_ultimate = False  # a partida escurece a tela quando isso liga
        # coisas que os golpes especiais usam
        self.angulo = 0.0          # corpo girado (radianos), em volta do quadril
        self.giro_voo = 0.0        # rodopiando enquanto voa
        self.vira = False          # desenha virado pro outro lado (rodopio)
        self.sobrepor = {}         # pontos da pose trocados pelo golpe (ex: braço esticado)
        self.feixe = None          # laser: ((x1, y1), (x2, y2)) quando está machucando
        self.bonus_parede = 0      # dano extra se bater na parede voando
        self.memo = {}             # anotações do golpe especial em andamento
        self.ex = False            # o golpe de agora é um especial EX
        self.regras = set()        # MODOS MALUCOS ligados nesta luta (a partida preenche)
        self.pisca = 0             # brilho extra (olho carregando, etc.)
        # só pra animação (não muda o jogo)
        self.pose_vista = None     # a pose que aparece na tela: vai "deslizando" até a pose certa
        self.passo = 0.0           # em que parte da caminhada ele está
        self.pouso = 0             # amortecida quando cai do pulo
        self.tremor_hit = 0        # treme quando apanha
        self.rastro = []           # fotos dos últimos quadros (rastro nos golpes rápidos)
        self.pulo_r = 8
        self.guarda = GUARDA_MAX   # gasta defendendo; zerou = guarda quebrada (fica tonto)
        self.guarda_espera = 0     # quadros desde a última defesa (depois de um tempo a guarda volta)
        self.r_antes = 5           # direção do quadro anterior (pra saber quando TOCOU pra frente)
        self.parry_frente = 0      # quadros que o parry de cima/meio está "ligado"
        self.parry_baixo = 0       # quadros que o parry de baixo está ligado
        self.parry_trava = 0       # tocou e errou: espera um pouco (não dá pra ficar apertando sem parar)
        self.buffer = None         # soco/chute apertado um tiquinho antes da hora
        self.buffer_t = 0
        self.cadeia = 0            # quantos golpes normais já emendou
        self.malabar = False       # jogado pra cima: dá pra continuar batendo nele no ar
        self.malabar_n = 0         # quantos golpes já levou no ar
        self.quica = False         # chute pra baixo: quica no chão e continua no combo
        self.combo_ar = False      # está fazendo combo aéreo (pode atacar de novo no mesmo pulo)
        self.perseguindo = 0       # quadros do pulo de perseguição teleguiado
        self.provocou = 0          # provocações completas neste round
        self.tomou_ult = False     # levou ultimate neste round
        self.acertou_ult = False   # acertou a ultimate neste round
        self.voo_forte = False     # saiu voando de um golpe forte (pode atravessar pra outro cenário)
        self.invisivel = 0         # PODER MÁGICO (Finn): quadros que ainda fica invisível
        self.as_t = 0              # ÁS NA MANGA (Kun): quadros contando até o ás acender
        self.as_ativo = 0          # ÁS NA MANGA: quadros que o ás ainda fica aceso

    # ------------------------------------------------------------ ajudas
    def no_chao(self):
        return self.y >= CHAO

    def rel(self, d):
        """Transforma a direção da tela em direção 'pra frente/pra trás' do lutador."""
        return d if self.dir == 1 else ESPELHO.get(d, d)

    def mudar(self, estado):
        self.estado, self.t = estado, 0
        self.angulo = self.giro_voo = 0.0
        self.vira = False
        self.sobrepor = {}
        self.feixe = None
        self.pisca = 0
        self.superaquecido = False  # Cannan cansado depois da ultimate (fumaça no lugar das estrelas)
        self.ex = False             # o golpe de agora é EX (o comecar liga depois de chamar o mudar)
        self.voo_forte = False

    def encher(self, quanto):
        if quanto > 0:
            quanto *= self.f.get("barra_mult", 1.0)  # alguns personagens enchem a ultimate mais devagar
            if "so_ultimate" in self.regras:
                quanto *= 5  # MODO MALUCO: SÓ ULTIMATE
        self.barra = max(0, min(BARRA_MAX, self.barra + quanto))

    def golpe_do_botao(self, botao):
        return (self.mutado or self.f).get("golpes", PADRAO).get(botao)

    def mutar(self, ficha):
        """MUTAÇÃO: vira o oponente (aparência, golpes e habilidade dele) até o fim do round."""
        self.mutado = ficha
        self.disfarce = ficha
        self.poses = dict(POSES)
        self.poses.update(ficha.get("poses", {}))
        self.flash_mutacao = 30
        som.tocar("puf")

    def comecar(self, nome):
        g = GOLPES[nome]
        if g.get("pode") and not g["pode"](self):
            return False
        if g.get("ultimate"):
            if self.barra < BARRA_MAX:
                return False  # barra ainda não encheu
        elif g.get("proj") and not g.get("varios") and self.projetil and self.projetil.vivo:
            return False  # só uma bola por vez
        if g.get("ultimate"):
            self.barra = 0
            self.pediu_ultimate = True
            som.tocar("ultimate")
        elif g.get("som"):
            som.tocar(g["som"])
        elif not g.get("especial"):
            som.tocar("vento", 0.7)
        self.mudar("ataque")
        self.golpe, self.nome_golpe = g, nome
        self.golpe_id = getattr(self, "golpe_id", 0) + 1  # cada vez que começa um golpe, um número novo
        if (g.get("especial") and not g.get("ultimate") and getattr(self, "ex_pedido", False)
                and self.barra >= EX_CUSTO and nome != "provocar"):  # ESPECIAL EX: gasta 1/4 da barra
            self.barra -= EX_CUSTO
            self.ex = True
            self.flash_ex = 26
            som.tocar("carga", 0.7)
            self.preparar_ex(nome)
        self.acertou = False
        self.memo = {}
        self.inv = g.get("inv", 0)
        if g.get("aereo"):
            self.ja_atacou = True
        elif self.no_chao():
            self.vx = 0
        return True

    def tentar_especial(self, botao):
        nome = self.golpe_do_botao(botao) if botao else None
        self.botao_pedido = botao
        return bool(nome) and self.comecar(nome)

    def janelas(self):
        g = self.golpe
        return g.get("janelas") or ((g["ini"], g["ini"] + g["ativo"]),)

    # ------------------------------------------------------------ a cada quadro
    def update(self, e, outro, jogo):
        self.entrada_atual = e
        self._update(e, outro, jogo)
        rapido = hab.mult_ataque(self)
        if rapido > 1 and self.estado == "ataque":  # LOBO PRETO: o ataque roda mais rápido (um passo a mais às vezes)
            self._acelera = getattr(self, "_acelera", 0.0) + (rapido - 1)
            if self._acelera >= 1:
                self._acelera -= 1
                calmo = Entrada(e.dir)  # (sem apertar nada de novo no passo extra)
                calmo.segura_ult = getattr(e, "segura_ult", False)
                self._update(calmo, outro, jogo)
        self.animar()

    def animar(self):
        """Só visual: a pose da tela desliza até a pose certa (fica com quadros entre os quadros)."""
        alvo = self.pose_atual()
        if self.pose_vista is None or self.estado == "agarrado" or self.sobrepor:
            self.pose_vista = alvo
        else:
            if self.estado == "ataque" and self.t <= 2:
                k = 0.85  # golpe começa seco (não fica "socando de dentro da defesa")
            elif self.estado == "ataque":
                k = 0.6
            elif self.estado in ("golpeado", "voando", "defendendo", "tonto"):
                k = 0.5
            else:
                k = 0.3
            self.pose_vista = misturar(self.pose_vista, alvo, k)
        if self.pouso > 0:
            self.pouso -= 1
        g = self.golpe if self.estado == "ataque" else None
        ativo = g and any(a <= self.t < b for a, b in self.janelas())
        rapido = abs(self.vx) > 6.5 or (g and abs(self.vy) > 9) or (g and g.get("ultimate") and self.angulo)
        if rapido:
            self.rastro.append((self.x, self.y, self.pose_vista, self.angulo, self.vira))
            del self.rastro[:-7]
        elif self.rastro:
            self.rastro.pop(0)

    def _update(self, e, outro, jogo):
        self.t += 1
        self.ex_pedido = bool(getattr(e, "barra", False))  # segurando a BARRA: o próximo especial sai EX
        if getattr(e, "barra_toque", False) and self.pode_escapar():
            self.escapar(outro, jogo)
            return
        f = self.mutado or self.f
        if getattr(e, "lobo", False) and f.get("tecla_x"):  # TAMER: X troca o lobo
            f["tecla_x"](self)
        if getattr(self, "ex_cadeia", False) and self.estado == "ataque" and outro.estado == "golpeado":
            outro.stun = max(outro.stun, 12)  # EX de Q/R: os pedaços emendam (o outro não escapa no meio)
        for ficha in (self.f, self.mutado):
            if ficha and ficha.get("todo_quadro"):
                ficha["todo_quadro"](self, jogo)
        self.guarda_espera += 1
        if getattr(self, "ult_recente", 0) > 0:
            self.ult_recente -= 1
        if self.invisivel > 0:
            self.invisivel -= 1
        if hab.relogio_as(self):  # ÁS NA MANGA acendeu!
            som.tocar("confirma", 0.6)
        if self.guarda_espera > GUARDA_VOLTA_DEPOIS and self.estado != "tonto":
            self.guarda = min(GUARDA_MAX, self.guarda + GUARDA_VOLTA)
        if self.inv > 0:
            self.inv -= 1
        self.r = self.rel(e.dir)
        est = self.estado
        # ---- parry: TOCAR pra frente (ou pra baixo) bem na hora ----
        for nome in ("parry_frente", "parry_baixo"):
            v = getattr(self, nome)
            if v > 0:
                setattr(self, nome, v - 1)
                if v == 1:
                    self.parry_trava = PARRY_TRAVA  # passou a janela sem nada: trava um pouquinho
        if self.parry_trava > 0:
            self.parry_trava -= 1
        elif est in LIVRE and self.no_chao():
            tocou_frente = self.r == 6 and self.r_antes not in (6, 3, 9)
            tocou_baixo = self.r == 2 and self.r_antes not in (1, 2, 3)
            if (tocou_frente or tocou_baixo) and (self.parry_frente or self.parry_baixo):
                # tocou de novo com o parry ligado = tá só apertando sem parar: perde e trava
                self.parry_frente = self.parry_baixo = 0
                self.parry_trava = PARRY_TRAVA
            elif tocou_frente:
                self.parry_frente = PARRY_JANELA
            elif tocou_baixo:
                self.parry_baixo = PARRY_JANELA
        self.r_antes = self.r
        # ---- guarda o botão apertado um pouquinho antes da hora ----
        if e.soco or e.chute:
            self.buffer, self.buffer_t = ("soco" if e.soco else "chute"), BUFFER_BOTAO
        elif self.buffer_t > 0:
            self.buffer_t -= 1
            if self.buffer_t == 0:
                self.buffer = None

        if est == "agarrado":
            return  # quem agarrou controla tudo (agarrão, ultimate que sempre acerta)

        if est in LIVRE:
            if self.no_chao() and abs(outro.x - self.x) > 2:
                self.dir = 1 if outro.x > self.x else -1  # sempre de frente pro outro
                self.r = self.rel(e.dir)
            r = self.r
            self.cadeia = 0
            if self.tentar_especial(e.especial):
                pass
            elif getattr(e, "provoca", False) and self.no_chao():
                self.comecar("provocar")
            elif self.buffer:
                botao, self.buffer, self.buffer_t = self.buffer, None, 0
                self.comecar(("ag_" if r in (1, 2, 3) else "") + botao)
            elif r in (7, 8, 9):
                self.pulo_r = r
                self.vx = 0
                self.mudar("prepulo")  # agachadinha antes de pular
            elif r in (1, 2, 3):
                if est != "agachado":
                    self.mudar("agachado")
                self.vx = 0
            elif r in (4, 6):
                if est != "andando":
                    self.mudar("andando")
                self.vx = self.f["vel"] * hab.mult_vel(self) * self.dir * (1 if r == 6 else -0.75)
                self.passo += abs(self.vx) * 0.014 * (1 if r == 6 else -1)
            else:
                if est != "parado":
                    self.mudar("parado")
                self.vx = 0

        elif est == "ataque":
            g = self.golpe
            # golpe normal que acertou pode ser "cancelado" num especial (combo!)
            if not g.get("especial") and not g.get("aereo") and self.acertou and e.especial:
                if self.tentar_especial(e.especial):
                    return self.fisica(jogo)
            # ...ou num outro golpe normal (soco -> soco -> chute)
            limite = (CADEIA_AR if g.get("aereo") else CADEIA_MAX) + hab.cadeia_extra(self)
            if (not g.get("especial") and self.acertou and self.buffer and self.t >= g["ini"] + 1
                    and self.cadeia < limite - 1):
                prefixo = "ar_" if g.get("aereo") else "ag_" if self.r in (1, 2, 3) and self.no_chao() else ""
                prox = prefixo + self.buffer
                if prox in CADEIA.get(self.nome_golpe, ()):
                    self.buffer, self.buffer_t = None, 0
                    self.cadeia += 1
                    if self.comecar(prox):
                        return self.fisica(jogo)
            # jogou o outro pra cima e acertou: aperta pra CIMA e pula atrás dele (pulo de perseguição)
            if (g.get("lanca") or g.get("lanca_depois")) and self.acertou and self.r in (7, 8, 9) and self.no_chao() \
                    and outro.estado == "voando" and outro.malabar:
                self.vy = -PULO_PERSEGUE
                self.ja_atacou = False
                self.cadeia = 0
                self.mudar("pulando")
                self.perseguindo = 22  # vai "teleguiado" até ficar do ladinho dele no ar
                self.pose_vista = misturar(self.pose_vista or self.poses["pulo"], self.poses["pulo_sobe"], 0.6)
                return self.fisica(jogo)
            for a, _ in self.janelas():
                if self.t == a:
                    self.acertou = False  # golpe de vários socos: cada um pode acertar
            if g.get("logica"):
                # golpe especial com regras próprias (fica no arquivo do personagem)
                if g["logica"](self, outro, jogo) == "fim":
                    self.terminar_golpe()
                return
            if self.t == g["ini"]:
                if g.get("ao_usar"):
                    g["ao_usar"](self, jogo)
                if g.get("proj"):
                    self.projetil = Projetil(self, self.x + 58 * self.s * self.dir, self.y - 84 * self.s, self.dir, g)
                    jogo.projeteis.append(self.projetil)
                if g.get("sobe"):
                    self.vy = g["sobe"]
            if g.get("avanca") and self.t < g["ini"] + g["ativo"]:
                self.vx = g["avanca"] * self.dir
            elif self.no_chao():
                self.vx *= 0.6
            if self.t >= g["total"]:
                self.terminar_golpe()

        elif est == "prepulo":
            if self.t >= 4:
                self.vy = -self.f["pulo"]
                self.vx = {7: -1, 8: 0, 9: 1}[self.pulo_r] * 3.8 * self.dir
                som.tocar("pulo")
                self.ja_atacou = False
                self.mudar("pulando")

        elif est == "pulando":
            if self.perseguindo > 0:
                self.perseguindo -= 1
                lado = 1 if outro.x >= self.x else -1
                alvo_x = outro.x - lado * 46 * self.s
                alvo_y = outro.y - 22 * self.s  # um pouquinho acima dele
                self.vx = (alvo_x - self.x) / 5
                self.vy = (alvo_y - self.y) / 5 - GRAVIDADE
                self.dir = lado
                if math.hypot(alvo_x - self.x, alvo_y - self.y) < 14 or outro.estado != "voando":
                    self.perseguindo = 0
                    self.vx, self.vy = outro.vx, min(outro.vy, 0) - 2
            if not self.ja_atacou and self.buffer:
                botao, self.buffer, self.buffer_t = self.buffer, None, 0
                self.comecar("ar_" + botao)

        elif est == "tonto":  # guarda quebrada ou paralisado: não faz nada por um tempinho
            self.vx *= 0.8
            if self.t >= getattr(self, "tonto_tempo", TONTO_TEMPO):
                self.tonto_tempo = TONTO_TEMPO
                self.paralisado = False
                self.guarda = GUARDA_MAX
                self.mudar("parado")

        elif est in ("golpeado", "defendendo"):
            self.stun -= 1
            self.vx *= 0.82
            if self.stun <= 0:
                self.combo = 0
                self.mudar("agachado" if self.r in (1, 2, 3) else "parado")

        elif est == "voando":
            self.angulo += self.giro_voo

        elif est == "caido":
            self.vx = 0
            if self.t > 45 and self.vida > 0:
                self.mudar("levantando")
                self.inv = 30

        elif est == "levantando":
            if self.t >= 16:
                self.mudar("parado")

        elif est == "vitoria" and self.f.get("vitoria"):  # pose de vitória de cada personagem
            self.f["vitoria"](self, self.t, jogo)

        self.fisica(jogo)

    def tem_tinta(self):
        return bool(self.f.get("sombra") or self.f.get("tinta"))

    def aplicar_tinta(self, sup, branco):
        """SOMBRA (tudo escuro e roxo) ou OURO (estátua dourada): pinta o desenho inteiro do lutador."""
        if self.f.get("sombra") or self.f.get("tinta") == "sombra":
            sup.fill((70, 50, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)
        elif self.f.get("tinta") == "ouro" and not branco:
            self.pintar_ouro(sup)

    def pintar_ouro(self, peq):
        """Roupa LENDÁRIA: tira as cores (fica cinza), pinta de dourado e passa um brilho de vez em quando."""
        cinza = pygame.transform.grayscale(peq)
        cinza.fill((255, 206, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
        cinza.fill((60, 40, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
        fase = (self.t * 3) % 240  # o brilho passando na diagonal
        if fase < 90:
            w, h = peq.get_size()
            faixa = pygame.Surface((w, h), pygame.SRCALPHA)
            x = (fase / 90) * (w + h) - h
            pygame.draw.polygon(faixa, (255, 255, 230, 150), [(x, h), (x + 8, h), (x + 8 + h, 0), (x + h, 0)])
            faixa.blit(peq, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)  # (só onde tem lutador)
            cinza.blit(faixa, (0, 0))
        peq.fill((0, 0, 0, 0))
        peq.blit(cinza, (0, 0))

    def pode_escapar(self):
        """ESCAPE de combo: apanhando (não preso em ultimate), com meia barra."""
        return (self.estado in ("golpeado", "voando", "tonto") and self.vida > 0 and self.barra >= ESCAPE_CUSTO
                and not getattr(self, "paralisado", False))

    def escapar(self, outro, jogo):
        """Gasta meia barra, se solta do combo e empurra quem estava batendo."""
        self.barra -= ESCAPE_CUSTO
        self.mudar("parado" if self.no_chao() else "pulando")
        self.ja_atacou = True
        self.vx = 0
        self.malabar, self.malabar_n, self.quica = False, 0, False
        self.inv = ESCAPE_INV
        self.stun = 0
        self.flash_escape = 24
        if outro.estado not in ("agarrado", "caido"):
            sinal = 1 if outro.x > self.x else -1
            outro.golpe = None
            outro.mudar("golpeado")
            outro.stun = 16
            outro.vx = sinal * 9
            outro.combo = 0
        jogo.tremer(10)
        som.tocar("parry")
        som.tocar("explosao", 0.4)

    def preparar_ex(self, nome):
        """O EX muda conforme o botão (a regra do Gomes):
        E = mais projéteis (ou 1,5x se não for tiro)   R = o dobro de ataques
        Q = rasteira + soco + o Q (joga pra cima)      SHIFT = dash pra frente e outro pra trás"""
        b = getattr(self, "botao_pedido", None)
        self.ex_botao = b
        self.ex_dano = b == "E"            # (se o E for de perto, bate 1,5x; se for tiro, os tiros viram 3)
        self.ex_fila = []
        self.ex_cadeia = b in ("Q", "R")
        if b == "R":
            self.ex_fila = [nome]          # faz de novo
        elif b == "SHIFT":
            self.ex_fila = ["ex_volta"]    # e volta
        elif b == "Q":                     # começa pela rasteira, depois soco, depois o Q
            self.ex_fila = ["soco", nome]
            self.golpe, self.nome_golpe = GOLPES["ex_rasteira"], "ex_rasteira"

    def terminar_golpe(self):
        fila = getattr(self, "ex_fila", None)
        if fila and self.estado == "ataque":  # EX: emenda o próximo pedaço
            prox = fila.pop(0)
            b, cadeia = self.ex_botao, self.ex_cadeia
            self.ex_pedido = False
            if self.comecar(prox):
                self.ex, self.ex_botao, self.ex_cadeia, self.ex_fila = True, b, cadeia, fila
                self.ex_dano = False
                return
        self.ex_fila = []
        self.ex_cadeia = False
        self.golpe = None
        if self.no_chao():
            self.mudar("parado")
        else:
            self.mudar("pulando")
            self.ja_atacou = not self.combo_ar  # no combo aéreo pode continuar batendo

    def fisica(self, jogo):
        if self.y < CHAO or self.vy < 0:
            leve = self.estado == "voando" and self.malabar and self.malabar_n > 0 and not self.quica
            lua = 0.42 if "lua" in self.regras else 1  # MODO MALUCO: GRAVIDADE DA LUA
            if self.estado == "voando" and getattr(self, "parede_sobe", False) and self.t < 50:
                lua = 0  # (chute do Tamer: voa reto até bater na parede)
            self.vy += GRAVIDADE * (0.62 if leve else 1) * lua
        self.x += self.vx
        self.y += self.vy
        if self.y >= CHAO:
            caiu = self.vy > 0
            self.y, self.vy = CHAO, 0
            self.combo_ar = False
            self.perseguindo = 0
            if caiu:
                if self.estado == "pulando":
                    self.mudar("parado")
                    self.vx = 0
                    self.pouso = 8
                    if self.pose_vista:
                        self.pose_vista = misturar(self.pose_vista, self.poses["pouso"], 0.6)
                elif self.estado == "voando" and self.quica:  # bateu no chão e QUICA (dá pra continuar o combo)
                    self.quica = False
                    self.vy = -8.5
                    self.y = CHAO - 1
                    self.vx *= 0.4
                    jogo.tremer(12)
                    jogo.poeira(self.x)
                    jogo.parada = max(jogo.parada, 4)
                elif self.estado == "voando":
                    som.tocar("queda")
                    self.mudar("caido")
                    self.malabar, self.malabar_n, self.quica = False, 0, False
                    self.vx = 0
                    jogo.tremer(6)
                    jogo.poeira(self.x)
                elif self.estado == "ataque":
                    if self.golpe and self.golpe.get("aereo"):
                        self.golpe = None
                        self.mudar("parado")
                    self.vx = 0
        if self.x < PAREDE_E or self.x > PAREDE_D:
            lado = 1 if self.x > PAREDE_D else -1
            self.x = max(PAREDE_E, min(PAREDE_D, self.x))
            if self.estado == "voando" and hasattr(jogo, "transicao_parede") and jogo.transicao_parede(self, lado):
                return  # atravessou a parede: TRANSIÇÃO DE CENÁRIO!
            if self.estado == "voando" and self.bonus_parede:  # jogado na parede: dói mais!
                self.vida = max(0, self.vida - self.bonus_parede)
                self.bonus_parede = 0
                self.vx = -self.vx * 0.35
                if getattr(self, "parede_sobe", False):  # bateu na parede e SOBE (dá pra continuar batendo)
                    self.parede_sobe = False
                    self.vy = -13
                    self.malabar, self.malabar_n = True, 0
                jogo.tremer(12)
                jogo.faisca(self.x, self.y - 60 * self.s, False)
                jogo.parada = max(jogo.parada, 6)

    # ------------------------------------------------------------ caixas
    def caixa_golpe(self):
        """Onde o golpe machuca agora (ou None)."""
        if self.estado != "ataque" or self.acertou:
            return None
        g = self.golpe
        caixa = self.memo.get("caixa", g["caixa"])
        if not caixa or not any(a <= self.t < b for a, b in self.janelas()):
            return None
        x1, y1, x2, y2 = (v * self.s for v in caixa)
        esq, dir_ = (self.x + x1, self.x + x2) if self.dir == 1 else (self.x - x2, self.x - x1)
        return pygame.Rect(esq, self.y - y2, dir_ - esq, y2 - y1)

    def contato(self, corpo):
        """Se o golpe encostou nesse corpo, devolve o ponto do encontro."""
        if self.estado != "ataque" or self.acertou:
            return None
        if self.feixe:
            linha = corpo.clipline(*self.feixe)
            return linha[0] if linha else None
        cg = self.caixa_golpe()
        if cg and cg.colliderect(corpo):
            return cg.clip(corpo).center
        return None

    def corpo(self):
        """Onde ele pode ser acertado (ou None se não pode)."""
        if self.estado == "voando" and self.malabar and self.malabar_n < getattr(self, "malabar_lim", MALABAR_MAX) \
                and self.inv == 0:
            return pygame.Rect(self.x - 26 * self.s, self.y - 104 * self.s, 52 * self.s, 104 * self.s)
        if self.estado in ("caido", "voando", "agarrado") or self.inv > 0:
            return None
        s = self.s
        baixo = self.estado == "agachado" or (self.estado == "defendendo" and self.agachado_def) \
            or (self.estado == "ataque" and self.golpe["base"] == "agachado")
        if not self.no_chao():
            topo, fundo = 108, 10
        elif baixo:
            topo, fundo = 80, 0
        else:
            topo, fundo = 122, 0
        topo *= self.f.get("altura", 1.0)  # personagem mais baixinho (ex: o Rib, agachadinho)
        if baixo and self.no_chao():
            topo *= hab.altura_agachado(self)  # CONEXÃO TERRESTRE: agachado fica bem menor
        meia = 22 * s * hab.largura(self)      # POSTURA NINJA: mais fininho
        return pygame.Rect(self.x - meia, self.y - topo * s, meia * 2, (topo - fundo) * s)

    # ------------------------------------------------------------ apanhar
    def pode_defender(self, g):
        if g.get("imbloqueavel"):
            return False  # vem de baixo da terra: não dá pra defender, só pular
        r = self.r
        pode = (self.no_chao() and self.estado in ("parado", "andando", "agachado", "defendendo")
                and r in (4, 1))
        if pode and g["nivel"] == "baixo" and r != 1:
            return False
        if pode and g["nivel"] == "alto" and r == 1:
            return False
        return pode

    def levar(self, dano, atacante, g):
        """Tira vida e enche as barras (já com as habilidades de quem bate e de quem apanha)."""
        if atacante:
            dano *= hab.mult_causa(atacante, g)
        dano *= hab.mult_recebe(self, atacante, g)
        if "um_golpe" in self.regras and dano > 0:
            dano = max(dano, self.vida)  # MODO MALUCO: UM GOLPE MATA
        if atacante and atacante is not self and dano > 0:
            dano += hab.bonus_causa(atacante)  # ÁS NA MANGA: +5 em cada ataque
        if atacante and atacante is not self and hab.queima_quem_bate(self, atacante, g):
            atacante.vida = max(0, atacante.vida - hab.ACIDO_DANO)  # SANGUE ÁCIDO: bateu de perto, queimou
            atacante.flash_acido = 16
        self.vida = max(0, self.vida - dano)
        if g and g.get("ultimate") and atacante and atacante is not self:
            self.tomou_ult = atacante.acertou_ult = True
            self.ult_recente = 120  # voando de ultimate não vira transição de cenário
        if g and g.get("ultimate") and "mutacao" in hab.ativas(self) and not self.mutado and atacante \
                and atacante is not self:
            self.mutar(atacante.mutado or atacante.f)
        self.encher(dano * BARRA_APANHAR)
        if atacante and not g.get("ultimate"):
            atacante.encher(dano * BARRA_BATER)

    def voar(self, sinal, vx, vy):
        """Sai voando (vy positivo = pra cima)."""
        malabar, n = self.malabar, self.malabar_n
        self.mudar("voando")
        self.malabar, self.malabar_n = malabar, n
        self.vy = -vy
        self.vx = sinal * vx

    def pode_parry(self, g):
        if g.get("imbloqueavel") or not self.no_chao() or self.estado not in LIVRE:
            return False
        if g["nivel"] == "baixo":
            return self.parry_baixo > 0
        return self.parry_frente > 0

    def receber(self, g, sinal, atacante, forca):
        """Levou um golpe. sinal = pra que lado ele é empurrado. Devolve 'parry', 'def', 'quebrou' ou 'hit'."""
        if self.pode_parry(g):  # PARRY! não leva nada e fica livre na hora
            self.parry_frente = self.parry_baixo = 0
            self.parry_trava = 0
            self.vx = 0
            self.guarda = min(GUARDA_MAX, self.guarda + 15)
            if self.estado == "andando":
                self.mudar("parado")
            self.parry_brilho = 12
            return "parry"
        if self.pode_defender(g):
            self.guarda -= g.get("guarda_custo", GUARDA_POR_GOLPE + g["dano"] * GUARDA_POR_DANO)
            self.guarda_espera = 0
            if self.guarda <= 0:  # QUEBROU A GUARDA!
                self.guarda = 0
                self.mudar("tonto")
                self.golpe = None
                self.vx = sinal * 3
                self.tremor_hit = 10
                self.quebrou = True  # a partida mostra o efeito
                return "quebrou"
            self.agachado_def = self.r == 1
            self.mudar("defendendo")
            self.tremor_hit = 4
            self.stun = g["defe"]
            self.vx = sinal * g["emp"] * 1.2
            # defendendo ainda tira um pouco (especial pode até nocautear; golpe normal não)
            dano = g["dano"] * forca * (DEFESA_DANO_ESPECIAL if g.get("especial") else DEFESA_DANO)
            self.vida = max(0 if g.get("especial") else 1, self.vida - dano)
            self.encher(10)
            return "def"

        if self.estado == "tonto":
            self.guarda = GUARDA_MAX  # apanhou tonto: acorda com a guarda cheia
        if self.estado in ("golpeado", "voando", "tonto"):
            if atacante:
                atacante.combo += 1
        elif atacante:
            atacante.combo = 1
        if atacante and "poder_magico" in hab.ativas(atacante) and atacante.invisivel <= 0                 and atacante.combo >= hab.limite_combo(atacante, COMBO_MAXIMO):
            atacante.invisivel = INVISIVEL_TEMPO  # PODER MÁGICO: combo máximo = some!
            atacante.flash_invisivel = 24
            som.tocar("puf")
        escala = 1
        if atacante and not g.get("especial"):
            escala = max(0.4, 1 - 0.1 * (atacante.combo - 1))  # combo longo de soco/chute tira menos por golpe
        self.levar(g["dano"] * forca * escala, atacante, g)
        self.ex_fila = []  # (apanhou: perde o resto do EX)
        if hab.armadura(self, g) and self.vida > 0:  # PESO PESADO: nem se mexe
            self.tremor_hit = 6
            return "hit"
        self.golpe = None
        self.tremor_hit = 9
        if self.pose_vista:  # reage na hora, mesmo com a tela congelada
            self.pose_vista = misturar(self.pose_vista, self.poses["golpeado"], 0.75)
        no_ar = not self.no_chao()
        if atacante:  # MAESTRIA DE COMBATE de quem bate deixa o combo no ar mais longo
            self.malabar_lim = hab.limite_combo(atacante, MALABAR_MAX)
        atacante_no_ar = atacante is not None and not atacante.no_chao() and atacante.estado != "agarrado"
        if self.vida <= 0:
            self.voar(sinal, 4, 9)
        elif g.get("lanca"):  # JOGA PRA CIMA
            self.voar(sinal, 1.2, g["lanca"])
            self.malabar, self.malabar_n = True, 0
        elif no_ar and atacante_no_ar and g.get("aereo"):
            self.malabar = True
            self.malabar_n += 1
            if g is GOLPES["ar_chute"] and self.malabar_n >= 2:  # CHUTE PRA BAIXO: quica no chão
                self.voar(sinal, 2, -17)
                self.quica = True
            else:  # combo aéreo: os dois ficam flutuando juntos (o atacante acompanha a distância)
                self.voar(sinal, 0.5, 4.5)
                atacante.vy = min(atacante.vy, -6.2)  # quem bate fica um pouco ACIMA (pra dar o chute pra baixo)
                atacante.vx = self.vx + (self.x - sinal * 46 * atacante.s - atacante.x) / 10
                atacante.ja_atacou = False
                atacante.combo_ar = True
        elif no_ar and self.malabar:  # já estava no ar (quicando): o golpe do chão levanta um tiquinho
            self.malabar_n += 1
            self.voar(sinal, 2, 7)
        elif g.get("derruba") or no_ar:
            vx, vy = g.get("voo", (4, 9))
            self.voar(sinal, vx, vy)
            self.parede_sobe = bool(g.get("parede_sobe"))  # (chute do Tamer: bate na parede e sobe)
            self.voo_forte = g["dano"] >= 10 or bool(g.get("ultimate"))
            self.bonus_parede = g.get("parede", 0)
            self.giro_voo = g.get("giro_voo", 0) * sinal
            self.malabar = False
        elif g.get("paralisa"):  # PARALISADO: fica travado um tempão
            self.mudar("tonto")
            self.tonto_tempo = g["paralisa"]
            self.paralisado = True
            self.vx = sinal * g["emp"]
        else:
            self.mudar("golpeado")
            self.stun = g["hit"]
            self.vx = sinal * g["emp"]
        return "hit"

    # ------------------------------------------------------------ desenho
    def pose_atual(self):
        est, t = self.estado, self.t
        if est == "ataque":
            g = self.golpe
            quadros = self.memo.get("quadros") or g.get("quadros")
            if quadros:
                p = pose_quadros(quadros, t, self.poses)
            else:
                base, alvo = self.poses[g["base"]], self.poses[g["pose"]]
                if t < g["ini"]:
                    p = misturar(base, alvo, suave(t / g["ini"]))
                elif t < g["ini"] + g["ativo"]:
                    p = alvo
                else:
                    p = misturar(alvo, base, suave(min(1, (t - g["ini"] - g["ativo"]) / g["rec"])))
        elif est == "defendendo":
            p = self.poses["ag_defesa" if self.agachado_def else "defesa"]
        elif est == "tonto":
            balanco = (math.sin(self.t * 0.15) + 1) / 2
            p = misturar(self.poses["golpeado"], self.poses["pouso"], 0.3 + 0.4 * balanco)
        elif est in ("golpeado", "agarrado"):
            p = self.poses["golpeado" if est == "golpeado" else "voando"]
        elif est == "pulando":
            if self.vy < 0:
                p = misturar(self.poses["pulo"], self.poses["pulo_sobe"], min(1, -self.vy / 10))
            else:
                p = misturar(self.poses["pulo"], self.poses["pulo_desce"], min(1, self.vy / 10))
        elif est == "prepulo":
            p = self.poses["prepulo"]
        elif est in ("voando", "caido", "agachado", "vitoria"):
            p = self.poses[est]
        elif est == "levantando":
            p = misturar(self.poses["agachado"], self.poses["parado"], suave(t / 16))
        else:
            if est == "andando":
                p = pose_quadros(CAMINHADA, self.passo % 1, self.poses)
            else:  # respirando: o corpo sobe e desce, os joelhos dobram um tiquinho
                p = dict(self.poses["parado"])
                b = math.sin(self.t * 0.07)
                for k in ("qd", "pc", "cb", "ct", "mt", "cf", "mf"):
                    p[k] = (p[k][0], p[k][1] + b * (1.2 if k == "qd" else 2.0))
                for k in ("jt", "jf"):
                    p[k] = (p[k][0] + b * 0.8, p[k][1] + b * 0.5)
            if self.pouso > 0:
                p = misturar(p, self.poses["pouso"], self.pouso / 8 * 0.7)
        if self.sobrepor:
            p = dict(p)
            p.update(self.sobrepor)
        return p

    def lado(self):
        return -self.dir if self.vira else self.dir

    def ponto(self, p, k):
        """Onde fica na tela o ponto k da pose p (com o giro do corpo)."""
        s, d = self.s, self.lado()
        x, y = self.x + p[k][0] * s * d, self.y - p[k][1] * s
        if self.angulo:
            cx, cy = self.x, self.y - 50 * s
            c, sn = math.cos(self.angulo * d), math.sin(self.angulo * d)
            x, y = cx + (x - cx) * c - (y - cy) * sn, cy + (x - cx) * sn + (y - cy) * c
        return (int(x), int(y))

    def desenhar(self, tela):
        g = self.golpe if self.estado == "ataque" else None
        if g and g.get("efeito_atras"):
            g["efeito_atras"](self, tela)
        p = self.pose_vista or self.pose_atual()
        desenho = (self.disfarce or self.f).get("desenho", desenhar_palito)  # disfarce: o Trafo vira outro lutador
        if self.rastro:
            self.desenhar_rastro(tela, desenho)
        x_real = self.x
        if self.tremor_hit > 0:
            self.x += (2 if self.tremor_hit % 2 else -2) * min(3, self.tremor_hit)
        if self.estado == "ataque" and self.nome_golpe == "giro" and self.t >= self.golpe["ini"]:
            self.vira = (self.t // 5) % 2 == 1  # rodopio
        branco = self.estado in ("golpeado", "voando") and self.t < 6  # pisca branco quando apanha
        if self.inv > 0 and self.estado == "parado" and (self.t // 3) % 2:
            branco = True
        # sombra no chão
        chao = getattr(self, "chao_sombra", CHAO)
        sombra = max(10, int(34 - (chao - self.y) * 0.08))
        if self.y > -50:
            pygame.draw.ellipse(tela, (25, 25, 35), (self.x - sombra, chao - 5, sombra * 2, 10))
        pecas.usar_troca((self.disfarce or self.f).get("troca"))  # roupa alternativa
        pecas.CABECAO = 2.0 if "cabecoes" in self.regras else 1.0
        try:
            if self.tem_tinta():  # SOMBRA / OURO: desenha numa camada separada e pinta ela
                camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
                desenho(self, camada, p, branco)
                self.aplicar_tinta(camada, branco)
                tela.blit(camada, (0, 0))
            else:
                desenho(self, tela, p, branco)
        finally:
            pecas.usar_troca(None)
            pecas.CABECAO = 1.0
        self.x = x_real
        if g and g.get("efeito"):
            g["efeito"](self, tela)

    def desenhar_px(self, baixo, peq, grande, px):
        """Desenho pra PIXEL ART: o corpo vai direto na imagem pequena (peq, 1/px do tamanho);
        sombra e rastro vão direto no fundo pequeno; os efeitos dos golpes vão na imagem grande."""
        import corpo
        g = self.golpe if self.estado == "ataque" else None
        if g and g.get("efeito_atras"):
            g["efeito_atras"](self, grande)
        p = self.pose_vista or self.pose_atual()
        desenho = (self.disfarce or self.f).get("desenho", desenhar_palito)  # disfarce: o Trafo vira outro lutador
        guarda = (self.x, self.y, self.s)
        self.x, self.y, self.s = self.x / px, self.y / px, self.s / px
        corpo.BORDA = 1.0
        pecas.usar_troca((self.disfarce or self.f).get("troca"))  # roupa alternativa
        pecas.CABECAO = 2.0 if "cabecoes" in self.regras else 1.0
        try:
            chao = CHAO / px
            sombra = max(5, int((34 - (CHAO - guarda[1]) * 0.08) / px))
            if guarda[1] > -50 and not self.invisivel:
                pygame.draw.ellipse(baixo, (25, 25, 35), (self.x - sombra, chao - 5 / px, sombra * 2, 10 / px))
            if self.rastro and not self.invisivel:
                self.rastro = [(x / px, y / px, pose, ang, vira) for x, y, pose, ang, vira in self.rastro]
                self.desenhar_rastro(baixo, desenho)
                self.rastro = [(x * px, y * px, pose, ang, vira) for x, y, pose, ang, vira in self.rastro]
            if self.estado == "ataque" and self.nome_golpe == "giro" and self.t >= self.golpe["ini"]:
                self.vira = (self.t // 5) % 2 == 1  # rodopio
            branco = self.estado in ("golpeado", "voando") and self.t < 6
            if self.inv > 0 and self.estado == "parado" and (self.t // 3) % 2:
                branco = True
            if self.tremor_hit > 0:
                self.x += (2 if self.tremor_hit % 2 else -2) * min(3, self.tremor_hit) / px
            if not self.esconde:
                desenho(self, peq, p, branco)
                self.aplicar_tinta(peq, branco)
            if self.cortar_chao:  # o que está embaixo da terra não aparece
                chao_px = int(CHAO / px) + 1
                peq.fill((0, 0, 0, 0), (0, chao_px, peq.get_width(), peq.get_height() - chao_px))
            if self.invisivel:  # PODER MÁGICO: quase não dá pra ver (só um vulto tremendo)
                k = min(1.0, self.invisivel / 15, (INVISIVEL_TEMPO - self.invisivel) / 15)
                a = int(255 - (255 - (18 + 14 * ((self.t // 3) % 2))) * k)
                peq.fill((255, 255, 255, a), special_flags=pygame.BLEND_RGBA_MULT)
            if self.cortar_acima is not None:  # ainda se materializando: de cima não aparece
                peq.fill((0, 0, 0, 0), (0, 0, peq.get_width(), max(0, int(self.cortar_acima / px))))
        finally:
            self.x, self.y, self.s = guarda
            corpo.BORDA = 1.6
            pecas.usar_troca(None)
            pecas.CABECAO = 1.0
        if g and g.get("efeito"):
            g["efeito"](self, grande)
        if self.entrada_t is not None and self.f.get("entrada_efeito"):
            self.f["entrada_efeito"](self, grande, self.entrada_t)
        if self.estado == "vitoria" and self.f.get("vitoria_efeito"):
            self.f["vitoria_efeito"](self, grande, self.t)
        self.desenhar_habilidade(grande)
        if self.f.get("desenhar_sempre"):  # coisas do personagem que ficam no cenário (ex: poças de ácido)
            self.f["desenhar_sempre"](self, grande)
        if self.estado == "tonto" and getattr(self, "paralisado", False):
            self.desenhar_gosma(grande)
        elif self.estado == "tonto" and getattr(self, "superaquecido", False) and self.f.get("cansado_efeito"):
            self.f["cansado_efeito"](self, grande)
        elif self.estado == "tonto":
            self.desenhar_estrelas(grande)

    def efeito_habilidade(self):
        """Tem algum desenho de habilidade aparecendo agora? (ás, fumaça do Maquinário, brilhos)"""
        return (hab.bonus_causa(self) or getattr(self, "flash_invisivel", 0) > 0 or bool(self.extra.get("pocas"))
                or getattr(self, "flash_ex", 0) > 0 or getattr(self, "flash_escape", 0) > 0
                or self.extra.get("lobo_flash", 0) > 0
                or (self.ex and self.estado == "ataque")
                or getattr(self, "flash_acido", 0) > 0
                or getattr(self, "flash_mutacao", 0) > 0
                or ("maquinario" in hab.ativas(self) and hab.ligada(self, "maquinario")))

    def desenhar_habilidade(self, tela):
        if "maquinario" in hab.ativas(self) and hab.ligada(self, "maquinario"):  # fumaça e faísca
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "pc")
            k = (self.t * 3) % 40
            pygame.draw.circle(tela, (170, 170, 170), (int(x - 10 * self.dir), int(y - k)), int((6 + k * 0.3) * self.s / 1.4))
            if (self.t // 3) % 5 == 0:
                pygame.draw.line(tela, (255, 220, 120), (x, y), (x + 12 * self.dir, y - 10), 2)
        if hab.bonus_causa(self):  # ÁS NA MANGA aceso: um ás dourado girando em cima da cabeça
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "cb")
            y -= 50 * self.s
            w = 9 * self.s * max(0.2, abs(math.cos(self.t * 0.12)))
            h = 13 * self.s
            from max10 import brilho
            brilho(tela, (int(x), int(y)), int(22 * self.s), (255, 210, 80), 110)
            pygame.draw.rect(tela, (255, 220, 90), (x - w - 2, y - h - 2, 2 * w + 4, 2 * h + 4), border_radius=3)
            pygame.draw.rect(tela, (250, 248, 236), (x - w, y - h, 2 * w, 2 * h), border_radius=2)
            if w > 3 * self.s:
                pygame.draw.circle(tela, (210, 40, 40), (int(x), int(y)), max(2, int(3 * self.s)))
            if self.as_ativo < 60 and (self.t // 4) % 2:  # piscando quando está pra acabar
                pygame.draw.rect(tela, (255, 255, 255), (x - w, y - h, 2 * w, 2 * h), 2, border_radius=2)
        if self.ex and self.estado == "ataque":  # ESPECIAL EX: brilho dourado em volta
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "pc")
            from max10 import brilho
            brilho(tela, (int(x), int(y)), int((38 + 4 * math.sin(self.t * 0.6)) * self.s), (255, 200, 60), 70)
        if getattr(self, "flash_ex", 0) > 0:
            self.flash_ex -= 1
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "cb")
            from efeitos import texto_grande
            texto_grande(tela, "EX!", 26, (255, 210, 70), (x, y - 40 * self.s - (26 - self.flash_ex)), contorno=(60, 30, 0))
        if getattr(self, "flash_escape", 0) > 0:  # ESCAPE: onda azul saindo do corpo
            self.flash_escape -= 1
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "pc")
            r = int((24 - self.flash_escape) * 7 * self.s)
            pygame.draw.circle(tela, (130, 210, 255), (int(x), int(y)), max(4, r), 4)
            pygame.draw.circle(tela, (230, 245, 255), (int(x), int(y)), max(2, r // 2), 2)
        if getattr(self, "flash_acido", 0) > 0:  # SANGUE ÁCIDO: queimou a mão de quem bateu
            self.flash_acido -= 1
            p = self.pose_vista or self.pose_atual()
            for k in ("mf", "mt"):
                x, y = self.ponto(p, k)
                u = 16 - self.flash_acido
                pygame.draw.circle(tela, (150, 230, 60), (int(x), int(y + u * 1.5)), max(2, int(4 - u * 0.2)))
                pygame.draw.circle(tela, (210, 210, 200), (int(x + 4), int(y - u * 2)), max(1, int(5 - u * 0.3)), 1)
        if getattr(self, "flash_invisivel", 0) > 0:  # PODER MÁGICO: estouro roxo quando some
            self.flash_invisivel -= 1
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "pc")
            k = 24 - self.flash_invisivel
            for i in range(10):
                a = i * math.tau / 10 + k * 0.1
                d = (20 + k * 5) * self.s
                pygame.draw.circle(tela, (200, 140, 255), (int(x + math.cos(a) * d), int(y + math.sin(a) * d)), 3)
        if getattr(self, "flash_mutacao", 0) > 0:  # brilho da mutação
            self.flash_mutacao -= 1
            p = self.pose_vista or self.pose_atual()
            x, y = self.ponto(p, "pc")
            r = int((40 + (30 - self.flash_mutacao) * 4) * self.s / 1.4)
            pygame.draw.circle(tela, (230, 200, 90), (int(x), int(y)), r, 3)
            pygame.draw.circle(tela, (255, 245, 200), (int(x), int(y)), r // 2, 2)

    def desenhar_gosma(self, tela):
        """Paralisado: coberto de baba amarela e com uns raiozinhos."""
        p = self.pose_vista or self.pose_atual()
        for k, ox in (("cb", -6), ("pc", 8), ("qd", -4), ("mf", 0)):
            x, y = self.ponto(p, k)
            pingo = (self.t * 2 + ox * 3) % 30
            pygame.draw.circle(tela, (210, 220, 120), (int(x + ox * self.s), int(y)), int(7 * self.s))
            pygame.draw.circle(tela, (210, 220, 120), (int(x + ox * self.s), int(y + pingo * self.s)), int(3 * self.s))
        if (self.t // 4) % 2:
            cx, cy = self.ponto(p, "cb")
            for i in range(3):
                a = self.t * 0.3 + i * 2.1
                pygame.draw.line(tela, (255, 255, 160), (cx, cy - 20 * self.s),
                                 (cx + math.cos(a) * 30 * self.s, cy - 20 * self.s + math.sin(a) * 18 * self.s), 2)

    def desenhar_estrelas(self, tela):
        p = self.pose_vista or self.pose_atual()
        cx, cy = self.ponto(p, "cb")
        cy -= 26 * self.s
        for i in range(3):
            a = self.t * 0.12 + i * math.tau / 3
            x, y = cx + math.cos(a) * 26 * self.s, cy + math.sin(a) * 7 * self.s
            pts = [(x + math.cos(k * math.pi / 5 - math.pi / 2) * (8 if k % 2 == 0 else 3.5),
                    y + math.sin(k * math.pi / 5 - math.pi / 2) * (8 if k % 2 == 0 else 3.5)) for k in range(10)]
            pygame.draw.polygon(tela, (255, 230, 80), pts)
            pygame.draw.polygon(tela, (120, 80, 0), pts, 2)

    def desenhar_rastro(self, tela, desenho):
        """Fantasmas dos últimos quadros, ficando transparentes."""
        if getattr(self, "_sup_rastro", None) is None or self._sup_rastro.get_size() != tela.get_size():
            self._sup_rastro = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        guarda = (self.x, self.y, self.angulo, self.vira)
        sup = self._sup_rastro
        for i in (0, len(self.rastro) // 2):
            if i >= len(self.rastro) - 1:
                continue
            x, y, pose, ang, vira = self.rastro[i]
            self.x, self.y, self.angulo, self.vira = x, y, ang, vira
            desenho(self, sup, pose, False)
        # vira uma mancha lisa de uma cor (não aparece braço nem perna do fantasma)
        m = 280 * self.s
        r = pygame.Rect(self.x - m - 200 * self.s, self.y - m - 200 * self.s, m * 2 + 400 * self.s,
                        m + 400 * self.s).clip(sup.get_rect())
        if r.w:
            mancha = pygame.mask.from_surface(sup.subsurface(r)).to_surface(
                setcolor=(*self.f["cor_poder"], 70), unsetcolor=(0, 0, 0, 0))
            tela.blit(mancha, r.topleft)
            sup.fill((0, 0, 0, 0), r)
        self.x, self.y, self.angulo, self.vira = guarda


CAMINHADA = [(0, "andar1"), (0.25, "andar2"), (0.5, "andar3"), (0.75, "andar4"), (1.0, "andar1")]


def pose_quadros(quadros, t, poses=POSES):
    """quadros = [(quadro, pose), ...]. Mistura suave entre o quadro-chave de antes e o de depois."""
    def pega(pz):
        return poses[pz] if isinstance(pz, str) else pz
    if t <= quadros[0][0]:
        return pega(quadros[0][1])
    for (t1, p1), (t2, p2) in zip(quadros, quadros[1:]):
        if t1 <= t < t2:
            return misturar(pega(p1), pega(p2), suave((t - t1) / (t2 - t1)))
    return pega(quadros[-1][1])


def desenhar_palito(l, tela, p, branco):
    s = l.s
    cor = BRANCO if branco else l.f["cor"]
    escura = BRANCO if branco else tuple(int(c * 0.55) for c in l.f["cor"])

    def P(k):
        return l.ponto(p, k)

    larg = max(3, int(6 * s))
    for c, pts in ((escura, ("pt", "jt", "qd")), (escura, ("pc", "ct", "mt")),
                   (cor, ("qd", "pc")),
                   (cor, ("pf", "jf", "qd")), (cor, ("pc", "cf", "mf"))):
        pygame.draw.lines(tela, c, False, [P(k) for k in pts], larg)
        for k in pts:
            pygame.draw.circle(tela, c, P(k), larg // 2)
    pygame.draw.circle(tela, escura, P("mt"), int(6 * s))
    pygame.draw.circle(tela, cor, P("mf"), int(7 * s))
    cx, cy = P("cb")
    pygame.draw.circle(tela, cor, (cx, cy), int(14 * s))
    # olhinho, pra saber pra onde ele olha
    pygame.draw.circle(tela, PRETO, (cx + int(6 * s * l.lado()), cy - int(2 * s)), max(2, int(3 * s)))
