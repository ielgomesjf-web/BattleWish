"""As telas do MODO ONLINE: criar sala / entrar com código / escolher o MODO / escolher lutador / lutar / de novo.
Modos: 1 CONTRA 1, TRIO (3 x 3) e TORNEIO (vocês 2 + 6 computadores), todos com os MODOS MALUCOS se quiser.
No TORNEIO cada um luta as lutas dele contra os computadores no próprio PC (ao mesmo tempo) e manda o resultado;
as lutas entre computadores saem iguais nos dois PCs (mesma semente); a FINAL entre vocês dois é pela internet.
(A parte da internet mora em rede.py.)"""
import random
import time

import pygame

import roupas
import save
import som
from config import *  # noqa: F401,F403
from controles import Computador, Jogador
from efeitos import texto, texto_grande
from partida import Partida
from personagens import PERSONAGENS
import threading

import malucos
from rede import Conexao, ControleRede, Lockstep, conferencia, salas_abertas
from selecao import TelaSelecao, TelaVS, fundo_selecao
from torneio import Torneio, luta_cpu, simular, vencedor_de

MENU = ["PROCURAR PARTIDA", "CRIAR SALA", "ENTRAR COM CÓDIGO", "VOLTAR"]
MODOS = [("1x1", "1 CONTRA 1"), ("trio", "TRIO (3 x 3)"), ("torneio", "TORNEIO (vocês 2 + 6 computadores)")]
NIVEL_TORNEIO = "MÉDIO"


class Online:
    def __init__(self, robo=False, arquivo_codigo=None, robo_modo="1x1"):
        self.robo = robo                  # o "robô da MARIA": a outra ponta controlada pelo computador
        self.robo_modo = robo_modo        # (o modo que o robô escolhe quando é ele quem criou a sala)
        self.modo = "1x1"
        self.regras = set()               # MODOS MALUCOS da sala (quem criou escolhe)
        self.op_modo = 0
        self.op_regra = 0
        self.torneio = None
        self.tres_fila = []               # resultados do torneio que chegaram do amigo (aplicados na hora certa)
        self.eu_pronto = self.ele_pronto = False
        self.espera = 0                   # (robô: quadros até a próxima ação)
        self.arquivo_codigo = arquivo_codigo
        self.estado = "menu"
        self.op = 0
        self.digitado = ""
        self.con = None
        self.sair = False
        self.t = 0
        self.msg = ""
        self.salas = None        # PROCURAR PARTIDA: os códigos das salas abertas (None = procurando)
        self.op_sala = 0
        self.limpar_luta()
        if robo:
            self.criar()

    def limpar_luta(self):
        self.sel = None
        self.minha = None
        self.dele = None
        self.partida = None
        self.lock = None
        self.vs = None
        self.quero_denovo = self.ele_quer_denovo = False
        self.conf = {}
        self.dessinc = False
        self.fim_t = 0
        self.escolhas = []      # TRIO: os lutadores escolhidos até agora
        self.confirma_sair = False  # (a pausa do torneio some quando a tela muda)
        self.luta_tipo = None   # "rede" (pela internet), "local" (eu x computador no torneio) ou "assistir"

    @property
    def host(self):
        return self.con is not None and self.con.hospedar

    # ------------------------------------------------------------ conexão
    def criar(self):
        self.con = Conexao(True)
        self.estado = "conectando"
        if self.arquivo_codigo:
            with open(self.arquivo_codigo, "w", encoding="utf-8") as arq:
                arq.write(self.con.codigo)

    def entrar(self):
        self.con = Conexao(False, self.digitado)
        self.estado = "conectando"

    def voltar_menu(self, msg=""):
        if self.con:
            self.con.fechar()
        self.con = None
        self.limpar_luta()
        self.estado = "erro" if msg else "menu"
        self.msg = msg

    def tratar_mensagens(self):
        for m in self.con.pegar_mensagens():
            t = m.get("t")
            if t == "escolha":
                if self.estado in ("fim", "modo", "regras", "torneio"):
                    self.dele_prox = m  # ele já escolheu pra próxima luta (guarda pra depois)
                else:
                    self.dele = m
            elif t == "modo":  # quem criou a sala escolheu o modo
                self.modo, self.regras = m["modo"], set(m.get("regras", []))
                self.ir_escolher()
            elif t == "tres":  # TORNEIO: o resultado da luta do amigo
                self.tres_fila.append((m["f"], m["k"], m["lado"]))
                self.aplicar_fila()
            elif t == "pronto":  # TORNEIO: o amigo quer começar a FINAL
                self.ele_pronto = True
            elif t == "comecar":
                self.comecar(m)
            elif t == "denovo":
                self.ele_quer_denovo = True
            elif t == "chk":
                meu = self.conf.get(m["f"])
                if meu is not None and meu != m["v"]:
                    self.dessinc = True
            elif t == "tchau":
                self.voltar_menu("o seu amigo saiu da sala")
                return

    # ------------------------------------------------------------ escolha e começo
    def ir_modo(self):
        """Depois de conectar (e a cada 'jogar de novo'): quem criou a sala escolhe o modo."""
        self.limpar_luta()
        self.torneio = None
        self.tres_fila = []
        self.eu_pronto = self.ele_pronto = False
        self.estado = "modo"
        if self.robo and self.host:
            self.escolher_modo(self.robo_modo)

    def escolher_modo(self, modo):
        som.tocar("confirma")
        self.modo = modo
        self.con.mandar({"t": "modo", "modo": modo, "regras": sorted(self.regras)})
        self.ir_escolher()

    def ir_escolher(self):
        prox = getattr(self, "dele_prox", None)
        self.limpar_luta()
        self.dele, self.dele_prox = prox, None
        self.estado = "escolha"
        self.nova_selecao()

    def nova_selecao(self):
        n = len(self.escolhas) + 1
        titulo = {"trio": f"TRIO ONLINE: ESCOLHA O {n}º LUTADOR",
                  "torneio": "TORNEIO ONLINE: ESCOLHA O SEU LUTADOR"}.get(self.modo)
        self.sel = TelaSelecao(PERSONAGENS, so_um=True, titulo=titulo)
        if self.robo:
            self.sel.cursor[0] = random.randrange(len(PERSONAGENS))
            self.sel.confirmar()
            self.escolheu()

    def escolheu(self):
        i = self.sel.escolhido[0]
        f = PERSONAGENS[i]
        self.escolhas.append({"i": i, "roupa": save.usando(f["nome"]), "hab": f.get("habilidade")})
        if self.modo == "trio" and len(self.escolhas) < 3:  # TRIO: mais um
            self.nova_selecao()
            return
        self.minha = {"t": "escolha", "lista": self.escolhas}
        self.con.mandar(self.minha)
        self.estado = "aguardando"

    def ficha(self, e):
        f = roupas.vestir(PERSONAGENS[e["i"]], e.get("roupa"))
        if e.get("hab"):
            f = dict(f, habilidade=e["hab"])
        return f

    def fichas_de(self, m):
        return [self.ficha(e) for e in m.get("lista", [m] if "i" in m else [])]

    def comecar(self, m):
        if not self.minha or not self.dele:
            return
        meus, deles = self.fichas_de(self.minha), self.fichas_de(self.dele)
        f1, f2 = (meus, deles) if self.host else (deles, meus)  # quem criou a sala fica na esquerda
        self.cenario, self.semente = m["cenario"], m["semente"]
        if self.modo == "torneio":  # monta a chave (igualzinha nos dois PCs)
            self.torneio = Torneio.online((f1[0], f2[0]), PERSONAGENS, NIVEL_TORNEIO, self.semente,
                                          0 if self.host else 1)
            self.estado = "torneio"
            self.aplicar_fila()
            return
        for k in range(min(len(f1), len(f2))):  # espelho: o da direita usa outra roupa
            if f1[k]["nome"] == f2[k]["nome"] and f1[k].get("roupa") == f2[k].get("roupa"):
                f2[k] = roupas.outra(f2[k], f1[k].get("roupa"))
        self.fichas = (f1, f2)
        self.luta_tipo = "rede"
        self.eu = 0 if self.host else 1
        self.vs = TelaVS(f1[0], f2[0])
        self.estado = "vs"

    def comecar_luta(self):
        if self.luta_tipo == "local":  # TORNEIO: eu contra um computador, aqui no meu PC
            f1, f2 = self.fichas
            eu = Computador("MÉDIO") if self.robo else Jogador()
            p = self.partida = Partida(f1, f2, eu, Computador(NIVEL_TORNEIO))
            p.regras.update(self.regras)
            p.torneio = True
            if self.robo:
                p.rounds = 1
            self.estado = "local"
            som.musica("luta")
            return
        f1, f2 = self.fichas
        if self.modo == "trio":
            p = self.partida = Partida(None, None, ControleRede(), ControleRede(), cenario_nome=self.cenario,
                                       trio=(f1, f2))
        else:
            p = self.partida = Partida(f1[0], f2[0], ControleRede(), ControleRede(), cenario_nome=self.cenario)
        p.semente = self.semente
        p.online = True
        p.lado_humano = self.eu  # (MAESTRIA: só o meu lado conta aqui)
        p.regras.update(self.regras)
        self.lock = Lockstep(self.con, self.semente % 65536)
        self.controle = Computador("MÉDIO") if self.robo else Jogador()
        p.controles_vibra = [getattr(self.controle, "controle", None) if i == self.eu else None for i in (0, 1)]
        self.estado = "luta"
        som.musica("luta")

    def velocidade(self):
        """MODO MALUCO TURBO: a luta roda 1,5x (nos dois PCs igual)."""
        if self.partida is not None and self.estado in ("luta", "local") and "turbo" in self.partida.regras:
            return malucos.TURBO
        return 1.0

    # ------------------------------------------------------------ TORNEIO ONLINE
    def aplicar_fila(self):
        """Aplica os resultados do amigo que já podem entrar (os de fases futuras esperam)."""
        t = self.torneio
        if t is None:
            return
        mudou = True
        while mudou:
            mudou = False
            for item in list(self.tres_fila):
                f, k, lado = item
                if f < t.fase or (f == t.fase and t.resultados[f][k] is not None):
                    self.tres_fila.remove(item)
                elif f == t.fase:
                    t.resultado(f, k, lado)
                    self.tres_fila.remove(item)
                    mudou = True

    def acao_torneio(self, pular=False):
        """ENTER (ou S = pular a luta dos computadores) na chave do torneio online."""
        t = self.torneio
        if t.campeao is not None:
            if not pular:
                self.pedir_denovo()
            return
        tipos = {k: t.tipo(k) for k in t.pendentes()}
        cpu = [k for k, v in tipos.items() if v == "cpu"]
        minha = [k for k, v in tipos.items() if v == "minha"]
        final = [k for k, v in tipos.items() if v == "final"]
        if pular:
            if cpu:
                k = cpu[0]
                a, b = (t.lutadores[i]["ficha"] for i in t.par(k))
                som.tocar("blip")
                t.resultado(t.fase, k, simular(a, b, t.nivel, t.semente_luta(k), self.regras))
                self.aplicar_fila()
            return
        if minha:  # a minha luta contra um computador: no meu PC
            k = minha[0]
            a, b = t.par(k)
            eu_esq = t.lutadores[a]["humano"]
            meu, dele = (t.lutadores[a], t.lutadores[b]) if eu_esq else (t.lutadores[b], t.lutadores[a])
            self.limpar_luta()
            self.luta_tipo, self.luta_k, self.luta_fase, self.eu_esq = "local", k, t.fase, eu_esq
            self.fichas = (meu["ficha"], dele["ficha"])
            self.vs = TelaVS(*self.fichas)
            self.estado = "vs"
            som.tocar("confirma")
        elif final:  # a FINAL contra o amigo: os dois apertam ENTER
            if not self.eu_pronto:
                self.eu_pronto = True
                self.con.mandar({"t": "pronto"})
                som.tocar("confirma")
        elif cpu:  # assistir os computadores (sai igual à luta pulada, nos dois PCs)
            k = cpu[0]
            a, b = (t.lutadores[i]["ficha"] for i in t.par(k))
            self.limpar_luta()
            self.luta_tipo, self.luta_k, self.luta_fase = "assistir", k, t.fase
            p = self.partida = luta_cpu(a, b, t.nivel, t.semente_luta(k), self.regras)
            p.assistindo = p.torneio = True
            self.estado = "local"
            som.musica("luta")

    def comecar_final(self):
        t = self.torneio
        k = next(k for k in t.pendentes() if t.tipo(k) == "final")
        a, b = t.par(k)
        self.eu_pronto = self.ele_pronto = False
        self.limpar_luta()
        self.luta_tipo, self.luta_k, self.luta_fase = "rede", k, t.fase
        self.fichas = ([t.lutadores[a]["ficha"]], [t.lutadores[b]["ficha"]])
        f1, f2 = self.fichas[0][0], self.fichas[1][0]
        if f1["nome"] == f2["nome"] and f1.get("roupa") == f2.get("roupa"):  # (os dois com o mesmo)
            self.fichas[1][0] = roupas.outra(f2, f1.get("roupa"))
        self.eu = 0 if t.lutadores[a]["humano"] else 1
        self.semente = t.semente_luta(k) + 7
        self.cenario = random.Random(self.semente).choice([f[0].get("cenario", "TEMPLO") for f in self.fichas])
        self.vs = TelaVS(self.fichas[0][0], self.fichas[1][0])
        self.estado = "vs"

    def terminar_luta_torneio(self):
        """Fim de uma luta do torneio: guarda o resultado (e manda pro amigo, se a luta era minha)."""
        t, p = self.torneio, self.partida
        lado = vencedor_de(p)  # (na tela: 0 = esquerda)
        if self.luta_tipo == "local":
            eu_ganhei = lado == 0
            lado = (0 if eu_ganhei else 1) if self.eu_esq else (1 if eu_ganhei else 0)
            self.con.mandar({"t": "tres", "f": self.luta_fase, "k": self.luta_k, "lado": lado})
        t.resultado(self.luta_fase, self.luta_k, lado)
        self.partida = None
        self.estado = "torneio"
        self.aplicar_fila()
        som.musica("menu")

    def pular_assistida(self):
        self.partida.pular_pro_fim()

    # ------------------------------------------------------------ a cada quadro (60 por segundo)
    def tick(self, bruto):
        self.t += 1
        if self.con is None:
            return
        if self.con.estado == "erro":
            self.voltar_menu(self.con.erro)
            return
        if self.estado == "conectando":
            if self.con.estado == "conectado":
                som.tocar("confirma")
                self.ir_modo()
            return
        self.con.bombear()
        if self.con.estado != "conectado":
            return
        self.tratar_mensagens()
        if self.con is None:
            return
        if self.estado == "aguardando" and self.dele and self.host and not self.vs:
            cen = random.choice([self.fichas_de(self.minha)[0].get("cenario", "TEMPLO"),
                                 self.fichas_de(self.dele)[0].get("cenario", "TEMPLO")])
            m = {"t": "comecar", "cenario": cen, "semente": random.randrange(1, 10 ** 6)}
            self.con.mandar(m)
            self.comecar(m)
        elif self.estado == "luta":
            self.passo_luta(bruto)
        elif self.estado == "local":  # TORNEIO: luta no meu PC (minha contra um computador, ou assistindo)
            p = self.partida
            if getattr(self, "confirma_sair", False):
                return  # (pausada)
            if p.fase != "fim":
                p.passo(bruto)
            else:
                self.fim_t += 1
                if self.robo and self.fim_t >= 60:
                    self.terminar_luta_torneio()
        elif self.estado == "torneio":
            self.aplicar_fila()
            t = self.torneio
            if t.campeao is not None:
                if self.quero_denovo and self.ele_quer_denovo:
                    self.ir_modo()
                    return
            elif self.eu_pronto and self.ele_pronto:
                self.comecar_final()
                return
            self.espera += 1
            if self.robo and self.espera >= 30:  # o robô: pula as lutas dos computadores e luta as dele
                self.espera = 0
                tipos = {t.tipo(k) for k in t.pendentes()}
                self.acao_torneio(pular="cpu" in tipos and t.campeao is None)
        elif self.estado == "fim":
            self.fim_t += 1
            if self.modo == "torneio":
                if self.robo and self.fim_t >= 120:
                    self.terminar_luta_torneio()
                return
            if self.robo and self.fim_t == 300:
                self.pedir_denovo()
            if self.quero_denovo and self.ele_quer_denovo:
                self.ir_modo()

    def passo_luta(self, bruto):
        p, lock = self.partida, self.lock
        lock.receber()
        if lock.pode_coletar():
            eu, ele = p.L[self.eu], p.L[1 - self.eu]
            if self.robo:
                e = self.controle.ler(None, eu, ele, p) if p.fase == "luta" else ControleRede().atual
            else:
                e = self.controle.ler(bruto, eu, ele, p)
            lock.coletar(e)
        else:
            lock.enviar()
        rodou = 0
        while lock.pode_avancar() and rodou < 2:
            local, remoto = lock.avancar()
            p.ctrl[self.eu].atual = local
            p.ctrl[1 - self.eu].atual = remoto
            p.passo(None)
            rodou += 1
            if lock.quadro % 120 == 0:  # confere se os dois estão vendo a mesma luta
                v = conferencia(p)
                self.conf[lock.quadro] = v
                self.con.mandar({"t": "chk", "f": lock.quadro, "v": v})
        if not rodou:
            lock.esperando += 1
        if p.fase == "fim":
            self.estado = "fim"
            self.fim_t = 0

    def pedir_denovo(self):
        if not self.quero_denovo:
            self.quero_denovo = True
            self.con.mandar({"t": "denovo"})

    # ------------------------------------------------------------ teclas e mouse
    def evento(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.estado == "menu":
            for i in range(len(MENU)):
                if self.rect_menu(i).collidepoint(ev.pos):
                    self.op = i
                    self.escolher_menu()
            return
        if ev.type == pygame.MOUSEMOTION and self.estado == "escolha":
            self.sel.mouse(ev.pos, False)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.estado == "escolha":
            self.sel.mouse(ev.pos, True)
            if self.sel.pronto:
                self.escolheu()
        if ev.type != pygame.KEYDOWN:
            return
        k = ev.key
        if k == pygame.K_ESCAPE and self.estado == "regras":
            self.estado = "modo"
            som.tocar("blip")
            return
        if self.estado in ("local", "torneio") and getattr(self, "confirma_sair", False):
            if k == pygame.K_ESCAPE:
                self.confirma_sair = False
                self.voltar_menu()  # (agora sim: sai da sala)
            elif k in (pygame.K_RETURN, pygame.K_SPACE):
                self.confirma_sair = False  # continua
            som.tocar("blip")
            return
        acabou = self.estado == "torneio" and self.torneio.campeao is not None  # (torneio acabou: ESC sai direto)
        if k == pygame.K_ESCAPE and self.estado in ("local", "torneio") and not acabou:
            self.confirma_sair = True  # PAUSA (a luta local para) e pergunta: ESC de novo sai da sala
            som.tocar("blip")
            return
        if k == pygame.K_ESCAPE:
            if self.estado in ("menu",):
                self.sair = True
            elif self.estado in ("digitando", "lista"):
                self.estado = "menu"
            else:
                self.voltar_menu()  # sai da sala (avisa o amigo) e volta pro menu do online
            som.tocar("blip")
            return
        if self.estado == "menu":
            if k in (pygame.K_w, pygame.K_UP):
                self.op = (self.op - 1) % len(MENU)
                som.tocar("blip")
            elif k in (pygame.K_s, pygame.K_DOWN):
                self.op = (self.op + 1) % len(MENU)
                som.tocar("blip")
            elif k in (pygame.K_RETURN, pygame.K_SPACE):
                self.escolher_menu()
        elif self.estado == "lista":
            if self.salas:
                if k in (pygame.K_w, pygame.K_UP):
                    self.op_sala = (self.op_sala - 1) % len(self.salas)
                elif k in (pygame.K_s, pygame.K_DOWN):
                    self.op_sala = (self.op_sala + 1) % len(self.salas)
                elif k in (pygame.K_RETURN, pygame.K_SPACE):
                    som.tocar("confirma")
                    self.digitado = self.salas[self.op_sala]
                    self.entrar()
            if k == pygame.K_r:  # procura de novo
                self.procurar()
        elif self.estado == "digitando":
            if k == pygame.K_BACKSPACE:
                self.digitado = self.digitado[:-1]
            elif k == pygame.K_RETURN and len(self.digitado) == 4:
                som.tocar("confirma")
                self.entrar()
            elif pygame.K_a <= k <= pygame.K_z and len(self.digitado) < 4:
                self.digitado += chr(k).upper()
                som.tocar("blip")
        elif self.estado == "erro":
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                self.estado = "menu"
        elif self.estado == "escolha":
            self.sel.tecla(k)
            if self.sel.pronto:
                som.tocar("confirma")
                self.escolheu()
        elif self.estado == "vs":
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                self.comecar_luta()
        elif self.estado == "modo" and self.host:
            n = len(MODOS) + 1
            if k in (pygame.K_w, pygame.K_UP):
                self.op_modo = (self.op_modo - 1) % n
                som.tocar("blip")
            elif k in (pygame.K_s, pygame.K_DOWN):
                self.op_modo = (self.op_modo + 1) % n
                som.tocar("blip")
            elif k in (pygame.K_RETURN, pygame.K_SPACE):
                if self.op_modo == len(MODOS):
                    self.estado = "regras"
                    som.tocar("confirma")
                else:
                    self.escolher_modo(MODOS[self.op_modo][0])
        elif self.estado == "regras":
            n = len(malucos.REGRAS)
            if k in (pygame.K_w, pygame.K_UP):
                self.op_regra = (self.op_regra - 1) % n
                som.tocar("blip")
            elif k in (pygame.K_s, pygame.K_DOWN):
                self.op_regra = (self.op_regra + 1) % n
                som.tocar("blip")
            elif k in (pygame.K_RETURN, pygame.K_SPACE):
                chave = malucos.REGRAS[self.op_regra][0]
                self.regras ^= {chave}
                som.tocar("confirma")
        elif self.estado == "torneio":
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                self.acao_torneio()
            elif k == pygame.K_s:
                self.acao_torneio(pular=True)
        elif self.estado == "local":
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                if self.partida.replay_tocando():
                    self.partida.pular_replay()
                elif self.partida.fase == "fim":
                    som.tocar("confirma")
                    self.terminar_luta_torneio()
                elif self.luta_tipo == "assistir" and k == pygame.K_RETURN:
                    self.pular_assistida()
        elif self.estado == "fim" and self.partida.replay_tocando():
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                self.partida.pular_replay()
        elif self.estado == "fim":
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                som.tocar("confirma")
                if self.modo == "torneio":
                    self.terminar_luta_torneio()
                else:
                    self.pedir_denovo()

    def procurar(self):
        """Busca a lista de salas abertas (em segundo plano, pra tela não travar)."""
        self.estado = "lista"
        self.salas = None
        self.op_sala = 0

        def busca():
            try:
                self.salas = salas_abertas()
            except OSError:
                self.salas = []
        threading.Thread(target=busca, daemon=True).start()

    def escolher_menu(self):
        som.tocar("confirma")
        if MENU[self.op] == "PROCURAR PARTIDA":
            self.procurar()
        elif MENU[self.op] == "CRIAR SALA":
            self.criar()
        elif MENU[self.op] == "ENTRAR COM CÓDIGO":
            self.digitado = ""
            self.estado = "digitando"
        else:
            self.sair = True

    def rect_menu(self, i):
        return pygame.Rect(LARGURA // 2 - 170, 200 + i * 64, 340, 50)

    # ------------------------------------------------------------ desenho
    def desenhar(self, tela):
        if self.estado in ("luta", "fim"):
            self.partida.desenhar(tela)
            ping = self.con.ping if self.con else 0
            texto(tela, f"ONLINE  ping {ping:.0f} ms", 13, (150, 220, 255), (LARGURA // 2, ALTURA - 12))
            if self.estado == "luta" and self.lock.esperando > 15:
                texto_grande(tela, "esperando o amigo...", 26, (220, 220, 240), (LARGURA // 2, 300))
            if self.dessinc:
                texto(tela, "atenção: os dois jogos ficaram diferentes", 14, (255, 140, 120), (LARGURA // 2, 300))
            if self.estado == "fim" and self.modo == "torneio":
                texto(tela, "ENTER: volta pra chave do torneio", 20, BRANCO, (LARGURA // 2, 316))
            elif self.estado == "fim":
                txt = "esperando o amigo querer jogar de novo..." if self.quero_denovo else \
                    "ENTER: jogar de novo     ESC: sair"
                if self.ele_quer_denovo and not self.quero_denovo:
                    txt = "o amigo quer jogar de novo!  ENTER: bora     ESC: sair"
                texto(tela, txt, 20, BRANCO, (LARGURA // 2, 316))
            return
        if self.estado == "local":
            self.partida.desenhar(tela)
            if self.luta_tipo == "local":
                texto(tela, "TORNEIO ONLINE: a sua luta (no seu PC)", 13, (150, 220, 255), (LARGURA // 2, ALTURA - 12))
            if getattr(self, "confirma_sair", False):
                self.desenhar_sair(tela)
            return
        if self.estado == "torneio":
            self.desenhar_torneio(tela)
            if getattr(self, "confirma_sair", False):
                self.desenhar_sair(tela)
            return
        if self.estado == "escolha":
            self.sel.desenhar(tela)
            texto(tela, "ONLINE: escolha o seu lutador", 16, (150, 220, 255), (LARGURA // 2, 80))
            return
        if self.estado == "vs":
            self.vs.desenhar(tela)
            if self.vs.acabou:
                self.comecar_luta()
            return
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, "ONLINE", 50, (255, 220, 70), (LARGURA // 2, 70))
        texto(tela, "você no seu PC, o seu amigo no dele", 16, (220, 220, 235), (LARGURA // 2, 120))
        if self.estado == "menu":
            for i, op in enumerate(MENU):
                r = self.rect_menu(i)
                sel = i == self.op
                pygame.draw.rect(tela, (54, 46, 84) if sel else (26, 22, 42), r, border_radius=10)
                pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), r, 3, border_radius=10)
                texto(tela, op, 22 if sel else 19, AMARELO if sel else BRANCO, r.center)
            texto(tela, "os dois precisam ter a MESMA versão do BattleWish.exe", 14, (200, 200, 220),
                  (LARGURA // 2, 478))
        elif self.estado == "digitando":
            texto(tela, "digite o código da sala do seu amigo:", 20, BRANCO, (LARGURA // 2, 210))
            for i in range(4):
                r = pygame.Rect(LARGURA // 2 - 150 + i * 78, 250, 66, 80)
                pygame.draw.rect(tela, (30, 26, 48), r, border_radius=10)
                pygame.draw.rect(tela, (255, 220, 70) if i == len(self.digitado) else (90, 80, 130), r, 3,
                                 border_radius=10)
                if i < len(self.digitado):
                    texto_grande(tela, self.digitado[i], 46, BRANCO, r.center)
            texto(tela, "ENTER entra     BACKSPACE apaga     ESC volta", 14, (200, 200, 220), (LARGURA // 2, 380))
        elif self.estado == "conectando":
            if self.host:
                texto(tela, "o código da sua sala é:", 20, BRANCO, (LARGURA // 2, 200))
                texto_grande(tela, self.con.codigo, 90, (255, 220, 70), (LARGURA // 2, 280))
                texto(tela, "fala esse código pro seu amigo", 16, (220, 220, 235), (LARGURA // 2, 350))
            pontos = "." * (1 + (self.t // 20) % 3)
            texto(tela, self.con.status.rstrip(".") + pontos, 18, (150, 220, 255), (LARGURA // 2, 410))
            texto(tela, "ESC cancela", 14, (200, 200, 220), (LARGURA // 2, ALTURA - 20))
        elif self.estado == "lista":
            if self.salas is None:
                texto(tela, "procurando salas abertas" + "." * (1 + (self.t // 20) % 3), 20, (150, 220, 255),
                      (LARGURA // 2, 260))
            elif not self.salas:
                texto(tela, "nenhuma sala aberta agora :(", 22, BRANCO, (LARGURA // 2, 240))
                texto(tela, "cria uma sala e espera alguém entrar, ou aperta R pra procurar de novo", 15,
                      (220, 220, 235), (LARGURA // 2, 280))
            else:
                texto(tela, "salas abertas agora:", 18, (220, 220, 235), (LARGURA // 2, 170))
                for i, c in enumerate(self.salas[:6]):
                    r = pygame.Rect(LARGURA // 2 - 140, 196 + i * 50, 280, 42)
                    sel = i == self.op_sala
                    pygame.draw.rect(tela, (54, 46, 84) if sel else (26, 22, 42), r, border_radius=10)
                    pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), r, 3, border_radius=10)
                    texto(tela, f"SALA {c}", 20 if sel else 18, AMARELO if sel else BRANCO, r.center)
            texto(tela, "W/S escolhe   ENTER entra   R procura de novo   ESC volta", 14, (200, 200, 220),
                  (LARGURA // 2, ALTURA - 20))
        elif self.estado == "aguardando":
            texto(tela, "esperando o seu amigo escolher o lutador...", 20, BRANCO, (LARGURA // 2, 280))
        elif self.estado == "modo":
            if not self.host:
                texto(tela, "o seu amigo está escolhendo o modo" + "." * (1 + (self.t // 20) % 3), 20, BRANCO,
                      (LARGURA // 2, 280))
            else:
                texto(tela, "escolha o modo da sala:", 18, (220, 220, 235), (LARGURA // 2, 170))
                ops = [nome for _, nome in MODOS] + ["MODOS MALUCOS: " + (malucos.nomes(self.regras) or "desligados")]
                for i, op in enumerate(ops):
                    r = pygame.Rect(LARGURA // 2 - 280, 196 + i * 60, 560, 48)
                    sel = i == self.op_modo
                    pygame.draw.rect(tela, (54, 46, 84) if sel else (26, 22, 42), r, border_radius=10)
                    pygame.draw.rect(tela, (255, 220, 70) if sel else (70, 62, 100), r, 3, border_radius=10)
                    tam = 19 if i < len(MODOS) else 15
                    texto(tela, op, tam + (2 if sel else 0), AMARELO if sel else BRANCO, r.center)
                texto(tela, "W/S escolhe   ENTER confirma   (MODOS MALUCOS: liga as regras doidas antes)", 14,
                      (200, 200, 220), (LARGURA // 2, ALTURA - 20))
        elif self.estado == "regras":
            texto(tela, "MODOS MALUCOS da sala (valem pros dois):", 18, (220, 220, 235), (LARGURA // 2, 160))
            for i, (chave, nome, desc) in enumerate(malucos.REGRAS):
                r = pygame.Rect(LARGURA // 2 - 300, 186 + i * 54, 600, 46)
                sel = i == self.op_regra
                liga = chave in self.regras
                pygame.draw.rect(tela, (54, 46, 84) if sel else (26, 22, 42), r, border_radius=10)
                pygame.draw.rect(tela, (120, 255, 150) if liga else (255, 220, 70) if sel else (70, 62, 100), r, 3,
                                 border_radius=10)
                texto(tela, ("[X] " if liga else "[  ] ") + nome, 18, AMARELO if sel else BRANCO,
                      (r.centerx, r.y + 15))
                texto(tela, desc, 12, (200, 200, 220), (r.centerx, r.y + 34))
            texto(tela, "ENTER liga/desliga   ESC volta", 14, (200, 200, 220), (LARGURA // 2, ALTURA - 20))
        elif self.estado == "erro":
            texto(tela, "não deu :(", 30, (255, 140, 120), (LARGURA // 2, 240))
            texto(tela, self.msg or "", 18, BRANCO, (LARGURA // 2, 290))
            texto(tela, "ENTER volta", 14, (200, 200, 220), (LARGURA // 2, 360))

    def desenhar_sair(self, tela):
        """ESC no torneio: a pausa perguntando se quer mesmo sair da sala."""
        escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escuro.fill((0, 0, 0, 160))
        tela.blit(escuro, (0, 0))
        texto_grande(tela, "PAUSA", 50, (255, 220, 70), (LARGURA // 2, 210))
        texto(tela, "ESC de novo: SAIR da sala (o torneio acaba pros dois)", 18, (255, 150, 130), (LARGURA // 2, 280))
        texto(tela, "ENTER: continuar", 18, BRANCO, (LARGURA // 2, 316))

    def desenhar_torneio(self, tela):
        t = self.torneio
        t.desenhar(tela, rodape=False)
        if self.regras:
            texto(tela, "MODOS MALUCOS: " + malucos.nomes(self.regras), 13, (255, 180, 120), (LARGURA // 2, 62))
        if t.campeao is not None:
            if self.quero_denovo:
                txt = "esperando o amigo querer jogar de novo..."
            elif self.ele_quer_denovo:
                txt = "o amigo quer jogar de novo!  ENTER: bora     ESC: sair"
            else:
                txt = "ENTER: jogar de novo     ESC: sair"
        else:
            tipos = {t.tipo(k) for k in t.pendentes()}
            pular = "   S: pular a luta dos computadores" if "cpu" in tipos else ""
            if "minha" in tipos:
                txt = "ENTER: a SUA luta!" + pular
            elif "final" in tipos:
                if self.eu_pronto:
                    txt = "esperando o amigo apertar ENTER pra FINAL..."
                elif self.ele_pronto:
                    txt = "o amigo está pronto pra FINAL!  ENTER: bora"
                else:
                    txt = "ENTER: a FINAL contra o seu amigo!"
            elif "cpu" in tipos:
                txt = "ENTER: assistir a luta dos computadores" + pular
            elif "amigo" in tipos:
                txt = "esperando o amigo terminar a luta dele" + "." * (1 + (self.t // 20) % 3)
            else:
                txt = ""
        texto(tela, txt, 16, BRANCO, (LARGURA // 2, ALTURA - 16))
