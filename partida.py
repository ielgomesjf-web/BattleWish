"""Uma partida: rounds, tempo, quem acertou quem, barras de vida e efeitos."""
import math
import random

import pygame

from config import *  # noqa: F401,F403
import habilidades as hab
import save
import som
from golpes import GOLPES
from efeitos import Cenario, Impactos, fonte, mistura_cor, moeda, texto, texto_grande, texto_moedas
from lutador import Entrada, Lutador

_cenario = None


def cenario():
    """O fundo parado (pros menus)."""
    global _cenario
    if _cenario is None:
        _cenario = Cenario()
    return _cenario.fundo


class Partida:
    def __init__(self, ficha1, ficha2, ctrl1, ctrl2, treino=False, cenario_nome=None, trio=None):
        self.trio = trio      # TRIO: ([3 fichas do lado 1], [3 fichas do lado 2]) — troca no meio da luta
        self.regras = set()   # MODOS MALUCOS ligados (o luta.py preenche)
        if trio:
            ficha1, ficha2 = trio[0][0], trio[1][0]
        self.treino = treino  # MODO TREINO: sem tempo, sem K.O., a vida volta depois de cada combo
        self.arcade = False   # no Arcade o texto do fim muda
        self.ultimo_combo = None  # (golpes, dano) do último combo, pra mostrar no treino
        self.golpes_treino = 0    # golpes que acertaram no boneco desde que a vida voltou
        self.fichas = (ficha1, ficha2)
        self.ctrl = (ctrl1, ctrl2)
        self.vitorias = [0, 0]
        self.round = 1
        self.vencedor = None  # 0, 1 ou "empate" quando a partida acaba
        self.rounds = ROUNDS_PRA_VENCER
        self.vida_inicial = None   # Sobrevivência: começa com a vida que sobrou da luta anterior
        self.sobrevivencia = None  # Sobrevivência: quantos já derrubou antes desta luta
        self.ultima_arcade = False # última luta do Arcade (vale bônus)
        self.combo_max = 0         # maior combo do jogador nesta partida
        self.perfects = 0          # rounds que o jogador venceu sem perder vida
        self.quase = 0             # rounds que venceu com 75% de vida ou mais (sem ser perfect)
        self.premio = None         # moedas ganhas: (itens, nível, multiplicador, total, desafios cumpridos)
        self.stats = dict(parrys=0, quebras=0, ults=0, tomou_ult=False, provocacoes=0, transicoes=0)  # pros desafios
        import cenarios
        self.cena = cenarios.cenario(cenario_nome or ficha2.get("cenario", "TEMPLO"))  # luta na casa do adversário
        self.impactos = Impactos()
        self.t_total = 0
        self.novo_round()

    def novo_round(self):
        self.L = [Lutador(self.fichas[0], 330, 1), Lutador(self.fichas[1], 630, -1)]
        if self.trio:  # TRIO: os 3 de cada lado (só um de cada luta por vez)
            self.equipes = [[Lutador(f, 330 if i == 0 else 630, 1 if i == 0 else -1) for f in self.trio[i]]
                            for i in (0, 1)]
            self.ativo = [0, 0]
            self.troca_espera = [0, 0]
            self.L = [self.equipes[0][0], self.equipes[1][0]]
        for l in self.todos():
            l.regras = self.regras
        if getattr(self, "vida_inicial", None) is not None:
            self.L[0].vida = self.L[0].vida_vista = self.vida_inicial
        self.vida_comeco = self.L[0].vida
        self.transicao_feita = False  # transição de cenário: uma vez por round
        self.projeteis = []
        self.faiscas = []
        self.fase, self.tf = ("luta" if self.treino else "intro"), 0
        if self.round == 1 and not self.treino:  # primeiro round: cada um faz a sua ENTRADA
            self.fase = "entrada"
            for l in self.L:
                l.extra["entrada_x"] = l.x
                l.entrada_t = 0
        self.ultimo_hit = 0
        self.tempo = TEMPO_ROUND * FPS
        self.parada = 0
        self.tremor = 0
        self.combo_txt = None  # (lado, numero, quadros)
        self.msg = ""
        self.escuro = 0        # quadros de tela escura (ultimate)
        self.quem_ultimate = None
        self.clarao = 0        # tela branca (K.O.)
        self.cutscene = None   # cena de anime de algum ultimate (a luta para enquanto passa)
        self.camera = [1.0, LARGURA / 2, ALTURA / 2]  # zoom e centro (cutscene)
        self.camera_alvo = None                        # um golpe pede zoom: (zoom, x, y)
        self.cinema = 0.0                              # faixas pretas de cinema (0 a 1)
        self.quebra_txt = None  # (lado, quadros) "GUARDA QUEBRADA!"
        self.parry_txt = None   # (lado, quadros) "PARRY!"

    # ------------------------------------------------------------ efeitos
    def tremer(self, n):
        self.tremor = max(self.tremor, n)

    def poeira(self, x):
        for _ in range(10):
            self.faiscas.append([x, CHAO - 4, random.uniform(-3, 3), random.uniform(-2.5, -0.5), 24, (150, 130, 110)])

    def faisca(self, x, y, defendeu, forte=False):
        cor = (140, 200, 255) if defendeu else AMARELO
        self.impactos.novo(x, y, "def" if defendeu else "forte" if forte else "hit")
        for _ in range(6 if defendeu else 14 if forte else 9):
            a = random.uniform(0, math.tau)
            v = random.uniform(2, 8)
            self.faiscas.append([x, y, math.cos(a) * v, math.sin(a) * v, random.randint(10, 18), cor, 3])

    # ------------------------------------------------------------ um quadro
    def passo(self, bruto):
        """bruto = (teclado, mouse) do pygame, ou None nos testes."""
        self.tf += 1
        self.t_total += 1
        if getattr(self, "semente", None) is not None:  # ONLINE: o sorteio é igual nos dois PCs
            random.seed(self.semente * 1000003 + self.t_total)
        # câmera: vai deslizando até o que o golpe pediu (ou volta pro normal)
        alvo = self.camera_alvo or (1.0, LARGURA / 2, ALTURA / 2)
        for i in range(3):
            self.camera[i] += (alvo[i] - self.camera[i]) * 0.14
        self.cinema += ((1.0 if self.camera_alvo else 0.0) - self.cinema) * 0.15
        self.camera_alvo = None
        self.impactos.update()
        if self.clarao > 0:
            self.clarao -= 1
        for l in self.L:
            if l.tremor_hit > 0:
                l.tremor_hit -= 1
        for f in self.faiscas:
            f[0] += f[2]
            f[1] += f[3]
            f[3] += 0.3
            f[4] -= 1
        self.faiscas = [f for f in self.faiscas if f[4] > 0]
        if self.tremor > 0:
            self.tremor -= 1
        if self.combo_txt:
            lado, n, q = self.combo_txt
            self.combo_txt = (lado, n, q - 1) if q > 1 else None
        if self.quebra_txt:
            lado, q = self.quebra_txt
            self.quebra_txt = (lado, q - 1) if q > 1 else None
        if self.parry_txt:
            lado, q = self.parry_txt
            self.parry_txt = (lado, q - 1) if q > 1 else None

        if self.fase == "entrada":
            self.passo_entrada()
            return
        for l in self.L:  # (segurança) entrada acabou: nada dela fica na tela
            if l.entrada_t is not None:
                l.entrada_t = None
                l.esconde = l.cortar_chao = False
                l.cortar_acima = None
        if self.cutscene:  # passando a cena: a luta fica parada
            self.cutscene.passo()
            if self.cutscene.acabou:
                self.cutscene = None
            return
        if self.fase == "fim":
            return
        if self.fase == "intro" and self.tf == 1:
            som.tocar("round", 0.8)
        if self.fase == "intro" and self.tf == 70:
            som.tocar("lutem", 0.8)
        if self.fase == "intro" and self.tf >= 110:
            self.fase, self.tf = "luta", 0
        if self.escuro > 0:
            self.escuro -= 1
            return
        if self.parada > 0:
            self.parada -= 1
            return
        if self.fase == "ko" and self.tf < 70 and self.tf % 3:
            return  # câmera lenta no K.O.

        ents = [Entrada(), Entrada()]
        if self.fase == "luta":
            ents = [self.ctrl[i].ler(bruto, self.L[i], self.L[1 - i], self) for i in (0, 1)]
        for i in (0, 1):
            self.L[i].update(ents[i], self.L[1 - i], self)
            if self.L[i].pediu_ultimate:  # momento épico: tudo para e a tela escurece
                self.L[i].pediu_ultimate = False
                self.escuro, self.quem_ultimate = ULTIMATE_PAUSA, self.L[i]
        if self.trio and self.fase == "luta":
            self.passo_trio(ents)
        self.ex_tiros()
        self.empurrar()
        for i in (0, 1):
            self.checar_golpe(self.L[i], self.L[1 - i])
        self.checar_projeteis()
        self.combo_max = max(self.combo_max, self.L[0].combo)
        self.sentir()

        if self.treino:
            self.passo_treino()
            if getattr(self, "combos", None):
                self.combos.passo(self)
        elif self.fase == "luta":
            self.tempo -= 1
            if any(self.perdeu(i) for i in (0, 1)):
                self.fase, self.tf = "ko", 0
                self.msg = "K.O.!"
                som.tocar("ko")
                self.tremer(16)
                self.clarao = 8
            elif self.tempo <= 0:
                self.fase, self.tf = "ko", 0
                self.msg = "TEMPO!"
        elif self.fase == "ko":
            for i, (l, o) in enumerate(((self.L[0], self.L[1]), (self.L[1], self.L[0]))):
                if self.vida_lado(i) > self.vida_lado(1 - i) and l.estado == "parado" and self.tf > 90:
                    l.mudar("vitoria")
            if self.tf > 240:
                self.terminar_round()

    def passo_entrada(self):
        """As entradas dos personagens (Max chega voando, Rib faz Kawarimi, Trafo sai da terra...)."""
        if self.tf >= DURACAO_ENTRADA:
            for l in self.L:
                l.entrada_t = None
                l.esconde = l.cortar_chao = False
                l.cortar_acima = None
                l.sobrepor = {}
                l.angulo, l.vira = 0, False
                l.x, l.y = l.extra.get("entrada_x", l.x), CHAO
                l.mudar("parado")
            self.fase, self.tf = "intro", 0
            return
        for l in self.L:
            l.entrada_t = self.tf
            entrada = l.f.get("entrada")
            if entrada:
                entrada(l, self.tf, self)
            else:
                l.t += 1
            l.animar()

    def passo_treino(self):
        """Treino: ninguém morre; quando o combo acaba, a vida volta e guarda o resultado."""
        for l in self.L:
            if l.vida <= 0:
                l.vida = 1
            if l.dano_combo_vista != l.vida_max - l.vida and l.vida < l.vida_max:
                l.dano_combo_vista = l.vida_max - l.vida
        alvo, atacante = self.L[1], self.L[0]
        livre = alvo.estado in ("parado", "andando", "agachado", "defendendo")
        if livre and alvo.vida < alvo.vida_max and self.tf - self.ultimo_hit > 50:
            self.ultimo_combo = (max(1, self.golpes_treino), alvo.vida_max - alvo.vida)
            self.golpes_treino = 0
            for l in self.L:
                l.vida = l.vida_vista = l.vida_max
                l.dano_combo_vista = 0
        if self.L[0].vida < self.L[0].vida_max and self.L[0].estado in ("parado", "andando", "agachado") \
                and self.tf - self.ultimo_hit > 50:
            self.L[0].vida = self.L[0].vida_max

    def terminar_round(self):
        a, b = self.vida_lado(0), self.vida_lado(1)
        eu = self.L[0]
        self.stats["ults"] += eu.acertou_ult
        self.stats["tomou_ult"] |= eu.tomou_ult
        self.stats["provocacoes"] += eu.provocou
        if a > b and a >= self.vida_comeco:
            self.perfects += 1  # PERFECT: venceu o round sem perder nada de vida
        elif a > b and a >= self.L[0].vida_max * QUASE_VIDA:
            self.quase += 1     # QUASE PERFECT
        if a >= b:
            self.vitorias[0] += 1
        if b >= a:
            self.vitorias[1] += 1  # empate no tempo: os dois ganham o round
        v1, v2 = (v >= self.rounds for v in self.vitorias)
        if v1 or v2:
            self.vencedor = "empate" if v1 and v2 else (0 if v1 else 1)
            self.fase, self.tf = "fim", 0
            self.pagar()
        else:
            self.round += 1
            self.novo_round()

    def controles(self):
        """O controle de videogame de cada lado (ou None), pra vibrar."""
        if hasattr(self, "controles_vibra"):
            return self.controles_vibra
        return [getattr(c, "controle", None) for c in self.ctrl]

    def sentir(self):
        """VIBRAÇÃO: quem perdeu vida sente o controle tremer (mais forte quanto maior o dano)."""
        import controle_video
        cs = self.controles()
        antes = getattr(self, "_vidas", None)
        self._vidas = [l.vida for l in self.L]
        if not antes or not any(cs):
            return
        for i, l in enumerate(self.L):
            perdeu = antes[i] - l.vida
            if perdeu > 0.01:
                forca, ms = ((0.25, 70) if perdeu < 3 else (0.5, 130) if perdeu < 10 else (0.8, 220) if perdeu < 25
                             else (1.0, 450))
                controle_video.vibrar(cs[i], forca, ms)
                if perdeu >= 8:  # quem bateu sente um pouquinho também
                    controle_video.vibrar(cs[1 - i], 0.35, 90)
        for i, l in enumerate(self.L):
            if getattr(l, "_vibrou_ult", False) != (l.estado == "ataque" and bool(l.golpe and l.golpe.get("ultimate"))):
                l._vibrou_ult = not getattr(l, "_vibrou_ult", False)
                if l._vibrou_ult:
                    controle_video.vibrar(cs[i], 0.6, 300)  # soltou a ultimate
        if self.fase == "ko" and not getattr(self, "_vibrou_ko", False):
            self._vibrou_ko = True
            for c in cs:
                controle_video.vibrar(c, 1.0, 600)  # K.O.!

    def ex_tiros(self):
        """EX do E: cada tiro novo vira 3 (em fila) e maiores."""
        import copy
        novos = []
        for p in self.projeteis:
            if getattr(p, "ex_visto", False):
                continue
            p.ex_visto = True
            d = p.dono
            if not (getattr(p, "ex", False) and getattr(d, "ex_botao", None) == "E"):
                continue
            d.ex_dano = False  # (é tiro: não precisa do 1,5x)
            p.raio = int(p.raio * 1.5)
            sinal = 1 if getattr(p, "vx", 0) >= 0 else -1
            for k in (1, 2):
                c = copy.copy(p)
                c.x -= sinal * 46 * k
                c.ex_visto = True
                novos.append(c)
        self.projeteis.extend(novos)

    # ------------------------------------------------------------ TRIO
    def todos(self):
        return [m for eq in self.equipes for m in eq] if self.trio else list(self.L)

    def perdeu(self, i):
        if self.trio:
            return all(m.vida <= 0 for m in self.equipes[i])
        return self.L[i].vida <= 0

    def vida_lado(self, i):
        return sum(max(0, m.vida) for m in self.equipes[i]) if self.trio else self.L[i].vida

    def passo_trio(self, ents):
        for i in (0, 1):
            if self.troca_espera[i] > 0:
                self.troca_espera[i] -= 1
            l = self.L[i]
            vivos = [m for m in self.equipes[i] if m is not l and m.vida > 0]
            for m in self.equipes[i]:  # quem está esperando fora recupera um pouquinho
                if m is not l and 0 < m.vida < m.vida_max:
                    m.vida = m.vida_vista = min(m.vida_max, m.vida + 0.025)
            if not vivos:
                continue
            if l.vida <= 0 and l.estado == "caido" and l.t > 30:
                self.trocar(i, forcado=True)  # caiu: entra o próximo
                continue
            from controles import Computador
            cpu_quer = isinstance(self.ctrl[i], Computador) and l.vida < 25 and random.random() < 0.01 and \
                any(m.vida > l.vida + 20 for m in vivos)
            if (getattr(ents[i], "troca", False) or cpu_quer) and self.troca_espera[i] == 0 and l.no_chao() \
                    and l.estado in ("parado", "andando", "agachado"):
                self.trocar(i)

    def trocar(self, i, forcado=False):
        """TRIO: sai o de agora, entra o próximo pulando com uma voadora."""
        eq, velho = self.equipes[i], self.L[i]
        n = len(eq)
        for k in range(1, n):
            j = (self.ativo[i] + k) % n
            if eq[j].vida > 0:
                break
        else:
            return
        novo = eq[j]
        for _ in range(8):  # puf onde o velho estava
            a = random.uniform(0, math.tau)
            self.faiscas.append([velho.x, velho.y - 60, math.cos(a) * 4, math.sin(a) * 4, 18, (220, 220, 235), 6])
        som.tocar("puf")
        novo.x = max(PAREDE_E, min(PAREDE_D, velho.x - velho.dir * 40))
        novo.y, novo.vx, novo.vy = CHAO - 240, velho.dir * 3, 0
        novo.dir = velho.dir
        novo.barra = velho.barra  # a barra é do time
        novo.mudar("pulando")
        novo.ja_atacou = False
        novo.inv = 30
        novo.regras = self.regras
        if not forcado:
            novo.comecar("ar_chute")  # entra dando uma voadora (o "ataque do parceiro")
        velho.sobrepor = {}
        velho.rastro = []
        self.ativo[i] = j
        self.L[i] = novo
        self.troca_espera[i] = 180

    def desenhar_trio(self, tela):
        """Os 3 retratinhos de cada time, embaixo da vida."""
        from selecao import retrato
        if not hasattr(self, "_retratos"):
            self._retratos = {}
        for i in (0, 1):
            for k, m in enumerate(self.equipes[i]):
                chave = (m.f["nome"], m.f.get("roupa"))
                if chave not in self._retratos:
                    self._retratos[chave] = retrato(m.f, 30)
                x = 34 + k * 38 if i == 0 else LARGURA - 34 - 30 - k * 38
                y = 96
                r = pygame.Rect(x, y, 30, 30)
                tela.blit(self._retratos[chave], r.topleft)
                ativo = m is self.L[i]
                pygame.draw.rect(tela, (255, 220, 70) if ativo else (20, 14, 24), r, 2)
                if m.vida <= 0:
                    escuro = pygame.Surface((30, 30), pygame.SRCALPHA)
                    escuro.fill((0, 0, 0, 160))
                    tela.blit(escuro, r.topleft)
                    pygame.draw.line(tela, (230, 60, 50), r.topleft, r.bottomright, 3)
                    pygame.draw.line(tela, (230, 60, 50), r.topright, r.bottomleft, 3)
                else:
                    pygame.draw.rect(tela, (40, 20, 24), (x, y + 32, 30, 4))
                    pygame.draw.rect(tela, (255, 220, 90), (x, y + 32, int(30 * m.vida / m.vida_max), 4))
            if self.troca_espera[i] == 0 and any(m.vida > 0 and m is not self.L[i] for m in self.equipes[i]):
                import controle_video
                txt = f"{controle_video.nome('troca')} troca"
                texto(tela, txt, 12, (150, 220, 255), (34 + 60 if i == 0 else LARGURA - 34 - 60, 142))

    def registrar_hit(self, atacante, nome, ativacao):
        """Desafios de combo: o jogador acertou o boneco com esse golpe."""
        if getattr(self, "combos", None) and atacante is self.L[0]:
            self.combos.acertou(nome, ativacao, atacante.combo)

    def transicao_parede(self, l, lado):
        """Alguém bateu voando na parede. Se foi forte, atravessa pro cenário vizinho!"""
        import transicao
        if self.fase != "luta" or self.cutscene or self.transicao_feita or l.vida <= 0 or l.malabar:
            return False
        if self.cena.nome not in transicao.DESTINOS or getattr(l, "parede_sobe", False):
            return False
        if not (abs(l.vx) >= transicao.VEL_MINIMA or l.voo_forte):
            return False
        atacante = self.L[1] if l is self.L[0] else self.L[0]
        if getattr(l, "ult_recente", 0) or (atacante.estado == "ataque" and atacante.golpe
                                              and atacante.golpe.get("ultimate")):
            return False  # ultimate já é forte o bastante: não vira transição
        self.transicao_feita = not self.treino  # no treino dá pra fazer de novo
        if atacante is self.L[0]:
            self.stats["transicoes"] += 1
        self.cutscene = transicao.Transicao(self, l, atacante, lado)
        return True

    def resumo(self):
        """O que aconteceu na partida (pros desafios)."""
        venceu = self.vencedor == 0
        n = self.sobrevivencia
        return dict(self.stats, venceu=venceu, personagem=self.fichas[0].get("nome_base", self.fichas[0]["nome"]),
                    nivel=self.ctrl[1].nivel, combo=self.combo_max, bom=venceu and (self.perfects + self.quase) > 0,
                    sobrev=(n + venceu) if n is not None else 0)

    def pagar(self):
        """Moedas! Só quando é você contra o computador (no treino e no CPU x CPU não vale)."""
        from controles import Computador, Jogador
        if self.treino or not isinstance(self.ctrl[0], Jogador) or not isinstance(self.ctrl[1], Computador):
            return
        if self.regras:
            return  # com MODO MALUCO ligado não ganha moeda
        venceu = self.vencedor == 0
        itens = []
        if venceu:
            itens.append(("VITÓRIA", MOEDAS_VITORIA))
        if self.perfects:
            itens.append(("PERFECT" + (f" x{self.perfects}" if self.perfects > 1 else ""), MOEDAS_PERFECT * self.perfects))
        if self.quase:
            itens.append(("QUASE PERFECT" + (f" x{self.quase}" if self.quase > 1 else ""), MOEDAS_QUASE * self.quase))
        sobrou = int(self.L[0].vida // MOEDAS_VIDA)
        if sobrou > 0:
            itens.append((f"VIDA QUE SOBROU ({int(self.L[0].vida)})", sobrou))
        if self.combo_max >= hab.limite_combo(self.L[0], COMBO_MAXIMO):
            itens.append(("COMBO MÁXIMO", MOEDAS_COMBO))
        if self.ultima_arcade and venceu:
            itens.append(("ARCADE COMPLETO", MOEDAS_ARCADE))
        if self.sobrevivencia is not None and not venceu and save.novo_recorde(self.sobrevivencia):
            itens.append(("RECORDE NOVO", MOEDAS_RECORDE))
        nivel = self.ctrl[1].nivel
        mult = MOEDAS_MULT.get(nivel, 1)
        total = round(sum(v for _, v in itens) * mult)
        import desafios
        cumpridos = desafios.atualizar(self.resumo())  # desafios valem sem multiplicador
        self.premio = (itens, nivel, mult, total, cumpridos)
        save.ganhar(total + sum(v for _, v in cumpridos))

    def empurrar(self):
        a, b = self.L
        if "agarrado" in (a.estado, b.estado) or a.y < 0 or b.y < 0:
            return
        if abs(a.y - b.y) > 90:
            return  # um tá pulando por cima do outro
        minimo = CORPO * a.s + CORPO * b.s
        dx = b.x - a.x
        if abs(dx) >= minimo:
            return
        lado = 1 if dx > 0 else (-1 if dx < 0 else a.dir)
        sobra = minimo - abs(dx)
        a.x -= lado * sobra / 2
        b.x += lado * sobra / 2
        for l, o, s in ((a, b, -lado), (b, a, lado)):
            if l.x < PAREDE_E or l.x > PAREDE_D:  # na parede: empurra o outro
                l.x = max(PAREDE_E, min(PAREDE_D, l.x))
                o.x = l.x - s * minimo

    def checar_golpe(self, a, b):
        cb = b.corpo()
        ponto = a.contato(cb) if cb else None
        if not ponto:
            return
        a.acertou = True
        self.ultimo_hit = self.tf
        g = a.memo.get("g_hit", a.golpe)
        if getattr(a, "ex", False) and getattr(a, "ex_dano", False):  # EX de E que não é tiro: bate 1,5x
            g = dict(g, dano=g["dano"] * EX_DANO)
        sinal = 1 if b.x > a.x else -1
        res = b.receber(g, sinal, a, a.f["forca"])
        if res == "hit" and b is self.L[1]:
            self.golpes_treino += 1
            self.registrar_hit(a, a.nome_golpe, getattr(a, "golpe_id", 0))
        if res == "quebrou":
            self.guarda_quebrada(b, ponto)
            return
        if res == "parry":
            self.parry(b, ponto)
            return
        self.som_do_golpe(res, g)
        self.faisca(ponto[0], ponto[1], res == "def", g["dano"] >= 10)
        self.parada = PARADA_GOLPE if res == "hit" else 4
        if g["dano"] <= 3:
            self.parada = 3  # soquinho rápido: congela pouco
        if res == "hit":
            self.tremer(5 if g["dano"] < 8 else 9 if g["dano"] < 20 else 16)
            if a.combo >= 2:
                self.combo_txt = (self.L.index(a), a.combo, 70)

    def som_do_golpe(self, res, g):
        if res == "def":
            som.tocar("defesa", 0.7)
        elif g["dano"] >= 15:
            som.tocar("explosao", 0.8)
            som.tocar("chute")
        elif g["dano"] >= 7:
            som.tocar("chute")
        else:
            som.tocar("soco")

    def parry(self, l, ponto):
        som.tocar("parry")
        if l is self.L[0]:
            self.stats["parrys"] += 1
        """Parry: tudo congela um tiquinho, brilho azul-branco, e quem deu parry fica livre primeiro."""
        self.parada = PARRY_PARADA
        self.impactos.novo(ponto[0], ponto[1], "def")
        for _ in range(16):
            a = random.uniform(0, math.tau)
            v = random.uniform(4, 9)
            self.faiscas.append([ponto[0], ponto[1], math.cos(a) * v, math.sin(a) * v, random.randint(10, 18),
                                 random.choice(((255, 255, 255), (150, 220, 255))), 3])
        self.parry_txt = (self.L.index(l), 60)

    def guarda_quebrada(self, l, ponto):
        """Vidro azul estourando + texto."""
        som.tocar("quebra")
        if l is self.L[1]:
            self.stats["quebras"] += 1
        self.parada = 14
        self.tremer(12)
        self.impactos.novo(ponto[0], ponto[1], "forte")
        for _ in range(26):
            a = random.uniform(0, math.tau)
            v = random.uniform(3, 10)
            self.faiscas.append([ponto[0], ponto[1], math.cos(a) * v, math.sin(a) * v - 2,
                                 random.randint(18, 30), random.choice(((140, 210, 255), (220, 240, 255))), 4])
        self.quebra_txt = (self.L.index(l), 80)

    def checar_projeteis(self):
        for p in self.projeteis:
            p.update()
        ps = self.projeteis
        for i, p in enumerate(ps):  # bola contra bola: as duas somem
            for q in ps[i + 1:]:
                bum = p.golpe.get("bumerangue") or q.golpe.get("bumerangue")  # o nunchaku não some no choque
                if p.vivo and q.vivo and p.dono is not q.dono and not bum and p.rect().colliderect(q.rect()):
                    fica_p, fica_q = p.golpe.get("atravessa"), q.golpe.get("atravessa")  # o Mini Sol passa por cima
                    p.vivo = bool(fica_p) and not fica_q
                    q.vivo = bool(fica_q) and not fica_p
                    self.faisca((p.x + q.x) / 2, p.y, False)
        for p in ps:
            if not p.vivo:
                continue
            alvo = self.L[1] if p.dono is self.L[0] else self.L[0]
            c = alvo.corpo()
            if c and p.rect().colliderect(c) and getattr(p, "pode_acertar", True):
                if p.golpe.get("bumerangue"):
                    p.pode_acertar = False  # bate e continua (acerta de novo na volta)
                else:
                    p.vivo = False
                self.ultimo_hit = self.tf
                res = alvo.receber(p.golpe, 1 if p.vx > 0 else -1, p.dono, p.dono.f["forca"])
                if res == "hit" and alvo is self.L[1]:
                    self.golpes_treino += 1
                    self.registrar_hit(p.dono, getattr(p, "nome_golpe", None), ("proj", getattr(p, "ativacao", 0)))
                if p.golpe.get("ao_acertar"):
                    p.golpe["ao_acertar"](p.dono, alvo, self, res)
                if res == "quebrou":
                    self.guarda_quebrada(alvo, (p.x, p.y))
                    continue
                if res == "parry":
                    self.parry(alvo, (p.x, p.y))
                    continue
                self.som_do_golpe(res, p.golpe)
                self.faisca(p.x, p.y, res == "def", p.golpe["dano"] >= 10)
                self.parada = PARADA_GOLPE if res == "hit" else 4
                if res == "hit":
                    self.tremer(16 if p.golpe is GOLPES["ultimate"] else 8)
        self.projeteis = [p for p in ps if p.vivo]

    # ------------------------------------------------------------ desenho
    def desenhar(self, tela):
        if self.cutscene:
            self.cutscene.desenhar(tela)
            return
        self.desenhar_luta(tela)
        if self.treino and getattr(self, "ver_caixas", False):
            self.desenhar_caixas(tela)
        if getattr(self, "assistindo", False) and self.fase not in ("fim",):
            texto(tela, "TORNEIO: assistindo   (ENTER pula pro resultado)", 14, (220, 220, 235), (LARGURA // 2, ALTURA - 12))

    def pular_pro_fim(self):
        """Assistindo os computadores: roda o resto da luta sem desenhar e arruma a tela do resultado
        (as barras de vida e os brilhos param onde a luta parou, nada fica congelado)."""
        for _ in range(FPS * 60 * 6):
            if self.fase == "fim":
                break
            self.passo(None)
        self.faiscas = []
        for l in self.L:
            l.vida_vista = l.vida
            for nome in ("flash_ex", "flash_escape", "flash_acido", "flash_invisivel", "flash_mutacao"):
                if hasattr(l, nome):
                    setattr(l, nome, 0)

    def desenhar_caixas(self, tela):
        """MODO TREINO (tecla H): azul = onde pode apanhar, vermelho = onde o golpe acerta, laranja = tiros."""
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for l in self.L:
            c = l.corpo()
            if c:
                pygame.draw.rect(camada, (60, 140, 255, 70), c)
                pygame.draw.rect(camada, (120, 190, 255, 230), c, 2)
            g = l.caixa_golpe()
            if g:
                pygame.draw.rect(camada, (255, 40, 40, 90), g)
                pygame.draw.rect(camada, (255, 90, 90, 255), g, 2)
            if l.feixe:
                pygame.draw.line(camada, (255, 60, 60, 255), l.feixe[0], l.feixe[1], 3)
        for p in self.projeteis:
            r = p.rect()
            pygame.draw.rect(camada, (255, 160, 40, 90), r)
            pygame.draw.rect(camada, (255, 190, 80, 255), r, 2)
        tela.blit(camada, (0, 0))
        texto(tela, "CAIXAS LIGADAS (H desliga):  azul = apanha   vermelho = acerta   laranja = tiro", 13,
              (220, 230, 255), (LARGURA // 2, 208))

    def desenhar_luta(self, tela):
        """Tudo é desenhado normal e depois vira PIXEL ART: reduz a imagem (cada bloquinho de
        PIXEL x PIXEL vira 1 ponto) e amplia de volta sem borrar. Lutadores ganham contorno de 1 pixel."""
        lw, lh = LARGURA // PIXEL, ALTURA // PIXEL
        if not hasattr(self, "mundo"):
            self.mundo = pygame.Surface((LARGURA, ALTURA))
            self.camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            self.camada_peq = pygame.Surface((lw, lh), pygame.SRCALPHA)
            self.escurecer = pygame.Surface((lw, lh), pygame.SRCALPHA)
        camada = self.camada
        baixo = self.cena.desenhar_pequeno(self.t_total, PIXEL)
        camada.fill((0, 0, 0, 0))

        tela_toda = pygame.Rect(0, 0, LARGURA, ALTURA)

        def area(lutadores):
            """Pedaço da tela onde esses lutadores (e os golpes deles) estão, pelos pontos do corpo."""
            r = None
            for l in lutadores:
                if l.feixe or l.y < -200 or l.rastro or (l.estado == "ataque" and l.memo.get("tela_toda")) \
                        or l.f.get("tela_toda"):
                    return tela_toda
                p = l.pose_vista or l.pose_atual()
                pts = [l.ponto(p, k) for k in p]
                xs, ys = [q[0] for q in pts], [q[1] for q in pts]
                m = 70 * l.s
                mx = 230 * l.s if l.estado == "ataque" and l.memo.get("pegou") else m
                rl = pygame.Rect(min(xs) - mx, min(ys) - m, max(xs) - min(xs) + 2 * mx, max(ys) - min(ys) + 2 * m)
                rl.union_ip(pygame.Rect(l.x - 40, CHAO - 10, 80, 20))  # sombra
                r = rl if r is None else r.union(rl)
            return r.clip(tela_toda) if r else pygame.Rect(0, 0, 0, 0)

        def passa(contorno, r):
            """Joga o que foi desenhado na camada pra imagem pixelada (só o pedaço r)."""
            if r.w <= 0 or r.h <= 0:
                return
            x0, y0 = r.x // PIXEL * PIXEL, r.y // PIXEL * PIXEL
            x1 = min(LARGURA, -(-r.right // PIXEL) * PIXEL)
            y1 = min(ALTURA, -(-r.bottom // PIXEL) * PIXEL)
            r = pygame.Rect(x0, y0, x1 - x0, y1 - y0)
            peq = pygame.transform.smoothscale(camada.subsurface(r), (r.w // PIXEL, r.h // PIXEL))
            pos = (x0 // PIXEL, y0 // PIXEL)
            if contorno:
                mascara = pygame.mask.from_surface(peq, 90)
                silhueta = mascara.to_surface(setcolor=(16, 10, 20, 255), unsetcolor=(0, 0, 0, 0))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    baixo.blit(silhueta, (pos[0] + dx, pos[1] + dy))
                limpo = pygame.Surface(peq.get_size(), pygame.SRCALPHA)
                mascara.to_surface(limpo, setsurface=peq, unsetcolor=(0, 0, 0, 0))
                peq = limpo
            baixo.blit(peq, pos)
            camada.fill((0, 0, 0, 0), r)

        # quem passa por trás vem primeiro; quem está atacando fica na frente
        ordem = sorted(self.L, key=lambda l: (not getattr(l, "atras", False), l.estado == "ataque"))
        for l in ordem:
            if self.escuro and l is self.quem_ultimate:

                k = 1 - self.escuro / ULTIMATE_PAUSA
                self.escurecer.fill((0, 0, 20, int(190 * min(1, k * 4))))
                baixo.blit(self.escurecer, (0, 0))
                cor = l.f["cor_poder"]
                cx, cy = l.x, l.y - 60 * l.s
                for i in range(3):  # anéis de energia fechando nele
                    r = int(220 * (1 - k) + 40 + i * 30) % 260 + 30
                    pygame.draw.circle(camada, cor, (int(cx), int(cy)), r, 3)
                for i in range(12):  # riscos de velocidade
                    a = i * math.tau / 12 + self.t_total * 0.05
                    r1, r2 = 330 - k * 150, 420
                    pygame.draw.line(camada, (255, 255, 255), (cx + math.cos(a) * r1, cy + math.sin(a) * r1),
                                     (cx + math.cos(a) * r2, cy + math.sin(a) * r2), 3)
                passa(False, tela_toda)
            # cada lutador vira um sprite separado, desenhado direto pequeno, com contorno de 1 pixel
            peq = self.camada_peq
            l.desenhar_px(baixo, peq, camada, PIXEL)
            r = area([l])
            r = pygame.Rect(r.x // PIXEL, r.y // PIXEL, -(-r.w // PIXEL) + 1, -(-r.h // PIXEL) + 1).clip(peq.get_rect())
            if r.w > 0 and r.h > 0:
                pedaco = peq.subsurface(r)
                mascara = pygame.mask.from_surface(pedaco, 90)
                silhueta = mascara.to_surface(setcolor=(16, 10, 20, 255), unsetcolor=(0, 0, 0, 0))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    baixo.blit(silhueta, (r.x + dx, r.y + dy))
                baixo.blit(pedaco, r.topleft)
                peq.fill((0, 0, 0, 0), r)
            if self.fase == "entrada" or l.estado == "vitoria":
                passa(False, tela_toda)
            elif (l.estado == "ataque" and l.golpe and l.golpe.get("efeito")) or l.estado == "tonto"                     or l.efeito_habilidade():
                passa(False, tela_toda if l.feixe or l.y < -200 or l.estado == "ataque" or l.extra.get("pocas")
                      else area([l]))
        # efeitos por cima (sem contorno)
        for p in self.projeteis:
            p.desenhar(camada)
        for f in self.faiscas:
            tam = f[6] * min(1, f[4] / 12) if len(f) > 6 else f[4] // 4
            pygame.draw.circle(camada, f[5], (int(f[0]), int(f[1])), max(2, int(tam)))
        self.impactos.desenhar(camada)
        pts = [(p.x, p.y) for p in self.projeteis] + [(f[0], f[1]) for f in self.faiscas] + \
            [(i[0], i[1]) for i in self.impactos.lista]
        if pts:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            m = 140
            passa(False, pygame.Rect(min(xs) - m, min(ys) - m, max(xs) - min(xs) + 2 * m,
                                     max(ys) - min(ys) + 2 * m).clip(tela_toda))
        self.cena.desenhar_frente(baixo, self.t_total, PIXEL)

        ox = oy = 0
        if self.tremor:
            ox = random.randint(-self.tremor, self.tremor) // 2 // PIXEL * PIXEL
            oy = random.randint(-self.tremor, self.tremor) // 2 // PIXEL * PIXEL
        zoom, cx, cy = self.camera
        if zoom > 1.01:  # cutscene: amplia um pedaço da tela
            w, h = lw / zoom, lh / zoom
            x = max(0, min(lw - w, cx / PIXEL - w / 2))
            y = max(0, min(lh - h, cy / PIXEL - h / 2))
            baixo = baixo.subsurface(pygame.Rect(int(x), int(y), int(w), int(h)))
        if ox or oy:  # tremendo: amplia numa imagem guardada (não cria uma nova todo quadro)
            if not hasattr(self, "_grande"):
                self._grande = pygame.Surface((LARGURA, ALTURA))
            pygame.transform.scale(baixo, (LARGURA, ALTURA), self._grande)
            tela.fill(PRETO)
            tela.blit(self._grande, (ox, oy))
        else:
            pygame.transform.scale(baixo, (LARGURA, ALTURA), tela)  # amplia direto na tela
        if self.cinema > 0.02:  # faixas pretas de cinema
            faixa = int(62 * self.cinema)
            tela.fill(PRETO, (0, 0, LARGURA, faixa))
            tela.fill(PRETO, (0, ALTURA - faixa, LARGURA, faixa))
        if self.clarao:
            if not hasattr(self, "_branco"):
                self._branco = pygame.Surface((LARGURA, ALTURA))
                self._branco.fill(BRANCO)
            self._branco.set_alpha(int(255 * self.clarao / 8))
            tela.blit(self._branco, (0, 0))
        if self.fase == "entrada":
            texto(tela, "ENTER pula", 13, (220, 220, 230), (LARGURA - 60, ALTURA - 14))
        elif self.cinema < 0.5:
            self.hud(tela)

    def barra_vida(self, tela, i, l):
        larg, alt, y = 372, 22, 26
        x = 34 if i == 0 else LARGURA - 34 - larg
        inc = 10  # inclinação das pontas

        def forma(x0, w):  # paralelogramo (cresce pro meio da tela)
            if i == 0:
                return [(x0 + inc, y), (x0 + w + inc, y), (x0 + w, y + alt), (x0, y + alt)]
            return [(x0 - inc, y), (x0 + w - inc, y), (x0 + w, y + alt), (x0, y + alt)]

        pygame.draw.polygon(tela, (20, 14, 24), [(px + (-4 if k in (0, 3) else 4), py + (-4 if k < 2 else 4))
                                                   for k, (px, py) in enumerate(forma(x, larg))])
        pygame.draw.polygon(tela, (60, 20, 30), forma(x, larg))
        for valor, cor1, cor2 in ((l.vida_vista, (230, 60, 50), (160, 20, 30)),
                                  (max(0, l.vida), (255, 236, 90), (255, 150, 30))):
            w = int(larg * valor / l.vida_max)
            if w <= 0:
                continue
            perigo = valor == l.vida and l.vida < 25 and (self.t_total // 8) % 2
            if perigo:
                cor1, cor2 = (255, 120, 80), (230, 40, 30)
            x0 = x + larg - w if i == 0 else x
            pts = forma(x0, w)
            pygame.draw.polygon(tela, cor2, pts)
            topo = [pts[0], pts[1], ((pts[1][0] + pts[2][0]) / 2, y + alt * 0.45), ((pts[0][0] + pts[3][0]) / 2, y + alt * 0.45)]
            pygame.draw.polygon(tela, cor1, topo)
            pygame.draw.line(tela, (255, 255, 230), pts[0], pts[1], 2)
        pygame.draw.polygon(tela, (240, 200, 110), forma(x, larg), 2)
        # barrinha da guarda (azul), embaixo da vida
        gw = int(larg * 0.55 * l.guarda / GUARDA_MAX)
        gx = x + larg - int(larg * 0.55) if i == 0 else x
        pygame.draw.rect(tela, (20, 14, 24), (gx - 2, y + alt + 1, int(larg * 0.55) + 4, 7))
        if gw > 0:
            cor_g = (255, 120, 90) if l.guarda < 35 else (120, 200, 255)
            pygame.draw.rect(tela, cor_g, (gx + (int(larg * 0.55) - gw if i == 0 else 0), y + alt + 2, gw, 5))
        # nome
        nome = fonte(17).render(l.f["nome"], True, BRANCO)
        sombra = fonte(17).render(l.f["nome"], True, PRETO)
        nx = x if i == 0 else x + larg - nome.get_width()
        tela.blit(sombra, (nx + 2, y + alt + 12))
        tela.blit(nome, (nx, y + alt + 10))
        # habilidades (acendem quando estão fazendo efeito)
        hy = y + alt + 30
        for h in hab.ativas(l):
            ligada = hab.ligada(l, h)
            cor = (255, 220, 90) if ligada and (h != "maquinario" or (self.t_total // 10) % 2) else (150, 150, 170)
            img = fonte(12).render(hab.HABILIDADES[h]["nome"], True, cor)
            tela.blit(img, (x if i == 0 else x + larg - img.get_width(), hy))
            hy += 14
        # rounds ganhos (estrelinhas)
        for k in range(ROUNDS_PRA_VENCER):
            cx = x + larg - 14 - k * 24 if i == 0 else x + 14 + k * 24
            cy = y + alt + 22
            ganho = self.vitorias[i] > k
            pts = [(cx + math.cos(a * math.pi / 5 - math.pi / 2) * (9 if a % 2 == 0 else 4),
                    cy + math.sin(a * math.pi / 5 - math.pi / 2) * (9 if a % 2 == 0 else 4)) for a in range(10)]
            pygame.draw.polygon(tela, (255, 214, 60) if ganho else (60, 50, 60), pts)
            pygame.draw.polygon(tela, PRETO, pts, 2)

    def barra_ultimate(self, tela, i, l):
        bw, bh = 230, 14
        x = 34 if i == 0 else LARGURA - 34 - bw
        y = ALTURA - 32
        cheia = l.barra >= BARRA_MAX
        pygame.draw.rect(tela, (10, 10, 20), (x - 3, y - 3, bw + 6, bh + 6), border_radius=4)
        w = int(bw * l.barra / BARRA_MAX)
        x0 = x if i == 0 else x + bw - w
        if w > 0:
            pulso = (math.sin(self.t_total * 0.25) + 1) / 2 if cheia else 0
            cor = mistura_cor((60, 160, 255), (230, 250, 255), pulso)
            pygame.draw.rect(tela, cor, (x0, y, w, bh), border_radius=3)
            pygame.draw.rect(tela, (200, 240, 255), (x0, y, w, 4), border_radius=2)
        for k in range(1, 4):  # divisões
            pygame.draw.line(tela, (10, 10, 20), (x + bw * k // 4, y), (x + bw * k // 4, y + bh), 2)
        if cheia:
            esc = 1 + 0.08 * math.sin(self.t_total * 0.25)
            texto_grande(tela, "ULTIMATE!", 18, (255, 230, 90), (x + bw // 2, y - 16), esc)
        mun = l.extra.get("municao")
        if mun:  # munição do personagem (ex: shurikens do Rib)
            n, total, bloqueado = mun
            for k in range(total):
                mx = x + 8 + k * 18 if i == 0 else x + bw - 8 - k * 18
                my = y - 14
                cheia = k < n and not bloqueado
                cor = (220, 225, 235) if cheia else (70, 70, 80)
                pts = [(mx + math.cos(a * math.pi / 4 + self.t_total * 0.05 * cheia) * (7 if a % 2 == 0 else 2.5),
                        my + math.sin(a * math.pi / 4 + self.t_total * 0.05 * cheia) * (7 if a % 2 == 0 else 2.5))
                       for a in range(8)]
                pygame.draw.polygon(tela, cor, pts)
                pygame.draw.polygon(tela, PRETO, pts, 1)
            if bloqueado:
                texto(tela, bloqueado, 13, (255, 150, 120), (x + bw // 2 if i == 0 else x + bw // 2, y - 30))
        armado = getattr(self.ctrl[i], "armado", 0)
        if armado:  # rodinha armada: um anel que vai fechando em cima do lutador
            cx, cy = int(l.x), int(l.y - 150 * l.s)
            pygame.draw.circle(tela, PRETO, (cx, cy), 6 + armado // 5, 4)
            pygame.draw.circle(tela, AMARELO, (cx, cy), 6 + armado // 5, 2)

    def hud(self, tela):
        if self.trio:
            self.desenhar_trio(tela)
        if self.regras:  # MODOS MALUCOS ligados
            import malucos
            texto(tela, malucos.nomes(self.regras), 12, (255, 200, 120), (LARGURA // 2, 80))
        for i, l in enumerate(self.L):
            if l.vida_vista > l.vida:
                l.vida_vista = max(l.vida, l.vida_vista - 0.6)
            self.barra_vida(tela, i, l)
            self.barra_ultimate(tela, i, l)
        # relógio
        pygame.draw.rect(tela, (20, 14, 24), (LARGURA // 2 - 38, 14, 76, 56), border_radius=10)
        pygame.draw.rect(tela, (240, 200, 110), (LARGURA // 2 - 38, 14, 76, 56), 3, border_radius=10)
        if self.treino and getattr(self, "combos", None):
            texto(tela, "∞", 36, BRANCO, (LARGURA // 2, 40))
            self.combos.desenhar(tela)
        elif self.treino:
            texto(tela, "∞", 36, BRANCO, (LARGURA // 2, 40))
            modo = getattr(self.ctrl[1], "modo", "")
            texto(tela, f"MODO TREINO   boneco: {modo}", 18, AMARELO, (LARGURA // 2, 128))
            texto(tela, "1 parado  2 defende  3 pula  4 agachado  5 luta     P enche a ultimate     H caixas     ESC sai",
                  13, BRANCO, (LARGURA // 2, 150))
            alvo = self.L[1]
            agora = alvo.vida_max - alvo.vida
            if agora > 0:
                texto_grande(tela, f"{self.golpes_treino} GOLPES  {agora:.0f} DE DANO", 20, (255, 230, 120),
                             (LARGURA // 2, 186))
            elif self.ultimo_combo:
                g, d = self.ultimo_combo
                texto(tela, f"último combo: {g} golpes, {d:.0f} de dano", 16, (220, 220, 230), (LARGURA // 2, 186))
        else:
            segundos = max(0, math.ceil(self.tempo / FPS))
            texto(tela, str(segundos), 36, (255, 90, 70) if segundos <= 10 else BRANCO, (LARGURA // 2, 42))

        if self.combo_txt and not getattr(self, "combos", None):  # (nos desafios de combo já tem os passos)
            lado, n, q = self.combo_txt
            esc = 1 + max(0, (q - 60) / 10) * 0.6  # entra grandão e assenta
            texto_grande(tela, f"{n} GOLPES!", 30, (255, 220, 70), (190 if lado == 0 else LARGURA - 190, 150), esc)
        if self.quebra_txt:
            lado, q = self.quebra_txt
            esc = 1 + max(0, (q - 70) / 10) * 0.5
            texto_grande(tela, "GUARDA QUEBRADA!", 30, (140, 210, 255), (LARGURA // 2, 160), esc, contorno=(10, 20, 50))
        if self.parry_txt:
            lado, q = self.parry_txt
            esc = 1 + max(0, (q - 50) / 10) * 0.6
            texto_grande(tela, "PARRY!", 34, (210, 240, 255), (190 if lado == 0 else LARGURA - 190, 150), esc,
                         contorno=(20, 40, 80))
        meio = (LARGURA // 2, 230)
        if self.fase == "intro":
            if self.tf < 70:
                k = min(1, self.tf / 14)
                nome = f"LUTA {self.sobrevivencia + 1}" if self.sobrevivencia is not None else f"ROUND {self.round}"
                texto_grande(tela, nome, 64, BRANCO, meio, 2.6 - 1.6 * k, int(255 * k))
            else:
                k = min(1, (self.tf - 70) / 8)
                texto_grande(tela, "LUTEM!", 84, (255, 220, 60), meio, 0.4 + 0.6 * k + 0.15 * (1 - k))
        elif self.fase == "ko":
            k = min(1, self.tf / 10)
            texto_grande(tela, self.msg, 96, (255, 70, 50), meio, 3 - 2 * k, int(255 * k))
        elif self.fase == "fim":
            k = min(1, self.tf / 15)
            if self.vencedor == "empate":
                texto_grande(tela, "EMPATE!", 70, (255, 220, 60), (LARGURA // 2, 200), 0.5 + 0.5 * k)
            else:
                texto_grande(tela, f"{self.fichas[self.vencedor]['nome']} VENCEU!", 54, (255, 220, 60),
                             (LARGURA // 2, 200), 0.5 + 0.5 * k)
            if getattr(self, "online", False):
                msg = ""  # (o modo online escreve a própria mensagem)
            elif getattr(self, "torneio", False):
                msg = "ENTER: volta pra chave do torneio"
            elif self.sobrevivencia is not None:
                if self.vencedor == 0:
                    msg = f"DERRUBOU {self.sobrevivencia + 1}!   ENTER: próxima luta (a vida volta um pouco)"
                else:
                    msg = f"FIM! Você derrubou {self.sobrevivencia}   RECORDE: {save.recorde()}   ENTER: de novo   ESC: menu"
            elif self.arcade:
                msg = "ENTER: próxima luta" if self.vencedor == 0 else "CONTINUAR?   ENTER: tentar de novo     ESC: menu"
            else:
                msg = "ENTER: revanche     ESC: menu"
            texto(tela, msg, 22 if len(msg) < 60 else 18, BRANCO, (LARGURA // 2, 280))
            if self.premio:
                self.desenhar_premio(tela)

    def desenhar_premio(self, tela):
        """O quadro das moedas que ganhou (e os desafios cumpridos)."""
        itens, nivel, mult, total, cumpridos = self.premio
        linhas = max(1, len(itens)) + len(cumpridos) + 2
        r = pygame.Rect(LARGURA // 2 - 230, 302, 460, 20 + linhas * 21)
        caixa = pygame.Surface(r.size, pygame.SRCALPHA)
        caixa.fill((14, 10, 26, 215))
        tela.blit(caixa, r.topleft)
        pygame.draw.rect(tela, (255, 210, 90), r, 2, border_radius=8)
        y = r.y + 18
        for nome, v in itens:
            texto(tela, nome, 15, BRANCO, (r.centerx - 60, y))
            texto(tela, f"+{v}", 15, (255, 220, 90), (r.right - 60, y))
            y += 21
        if not itens:
            texto(tela, "nada dessa vez... tenta um QUASE PERFECT!", 14, (200, 200, 210), (r.centerx, y))
            y += 21
        cor = (120, 230, 120) if mult > 1 else (255, 140, 110) if mult < 1 else (220, 220, 230)
        texto(tela, f"{nivel}  x{mult:g}", 15, cor, (r.centerx, y))
        y += 21
        for nome, v in cumpridos:
            texto(tela, f"DESAFIO! {nome}", 13, (150, 230, 255), (r.centerx - 40, y))
            texto(tela, f"+{v}", 15, (255, 220, 90), (r.right - 40, y))
            y += 21
        k = min(1.0, self.tf / 40)
        geral = total + sum(v for _, v in cumpridos)
        texto_moedas(tela, f"+{round(geral * k)}", r.centerx + 40, y + 2, self.tf, 21)
