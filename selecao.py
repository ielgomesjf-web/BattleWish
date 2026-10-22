"""Tela de seleção (estilo Injustice 2) e tela de VS."""
import math
import random

import pygame

from config import *  # noqa: F401,F403
from efeitos import fonte, texto, texto_grande
from lutador import Lutador
import maestria

CARTA = 112          # tamanho de referência do retrato (a loja usa outro tamanho)
CARTA_GRADE = 60     # retratos da grade de seleção (tipo Injustice 2: vários pequenininhos)
COLUNAS = 6
GRADE_X0 = LARGURA // 2 - (COLUNAS * (CARTA_GRADE + 6) - 6) // 2
GRADE_Y0 = 74
AZUL = (80, 160, 255)
VERMELHO = (255, 80, 70)


def fundo_selecao(t):
    """Fundo escuro com faixas diagonais andando devagar."""
    sup = pygame.Surface((LARGURA, ALTURA))
    for y in range(0, ALTURA, 4):
        k = y / ALTURA
        sup.fill((int(14 + 20 * k), int(12 + 14 * k), int(30 + 30 * k)), (0, y, LARGURA, 4))
    for i in range(-6, 16):
        x = i * 90 + (t * 0.4) % 90
        pygame.draw.polygon(sup, (24, 22, 46), [(x, 0), (x + 40, 0), (x - 160, ALTURA), (x - 200, ALTURA)])
    return sup


def retrato(ficha, tam=CARTA):
    """Close no rosto e no peito do lutador (pro quadradinho da grade)."""
    sup = pygame.Surface((tam, tam))
    for y in range(tam):
        k = y / tam
        sup.fill((int(40 + 30 * k), int(36 + 20 * k), int(60 + 20 * k)), (0, y, tam, 1))
    l = Lutador(ficha, 0, 1)
    l.s = ficha["tam"] * 2.3 * tam / CARTA * ficha.get("retrato_zoom", 1.0)  # (cabeção grande: afasta)
    p = l.pose_atual()
    l.x = tam * 0.5 - p["cb"][0] * l.s  # a cabeça no meio do quadradinho
    topo_cabeca = (p["cb"][1] + 12 + ficha.get("retrato_dy", 0)) * l.s
    l.y = topo_cabeca + tam * 0.12
    l.chao_sombra = 10_000
    l.desenhar(sup)
    return sup


def interrogacao(tam=CARTA):
    sup = pygame.Surface((tam, tam))
    sup.fill((40, 34, 60))
    texto(sup, "?", int(tam * 0.7), (255, 220, 70), (tam // 2, tam // 2 + 4))
    return sup


class TelaSelecao:
    """Escolhe o lutador do jogador 1 e (se precisar) o adversário."""

    def __init__(self, personagens, so_um=False, rotulo2="CPU", titulo=None):
        self.titulo = titulo        # (ex: "TRIO: ESCOLHA O 2º LUTADOR")
        self.rotulo2 = rotulo2      # "CPU" ou "2P" (dois jogadores no mesmo PC)
        self.lista = personagens
        import save
        for f in personagens:  # a última passiva que ele escolheu (Trafo, Sphyrus)
            salva = save.d().get("passivas", {}).get(f["nome"])
            if f.get("habilidades_opcoes") and salva in f["habilidades_opcoes"]:
                f["habilidade"] = salva
        self.so_um = so_um          # treino: só escolhe o seu
        self.cartas = [retrato(f, CARTA_GRADE) for f in personagens] + [interrogacao(CARTA_GRADE)]
        self.cursor = [0, min(1, len(personagens) - 1)]
        self.quem = 0               # 0 = escolhendo o seu, 1 = escolhendo o adversário
        self.escolhido = [None, None]
        self.t = 0
        self.grandes = {}
        self.pronto = False
        self.roupa_bot = {}         # a roupa que o adversário (CPU ou 2P) vai usar: {nome: id da roupa}

    # ---- posições ----
    def rect_carta(self, i):
        lin, col = divmod(i, COLUNAS)
        return pygame.Rect(GRADE_X0 + col * (CARTA_GRADE + 6), GRADE_Y0 + lin * (CARTA_GRADE + 6), CARTA_GRADE,
                           CARTA_GRADE)

    def fim_grade(self):
        """Onde a grade termina (embaixo)."""
        return self.rect_carta(len(self.cartas) - 1).bottom

    def ficha_do_cursor(self, lado):
        i = self.escolhido[lado] if self.escolhido[lado] is not None else self.cursor[lado]
        return None if i >= len(self.lista) else self.lista[i]

    # ---- controle ----
    def tecla(self, tecla):
        q = self.quem
        n = len(self.cartas)
        if tecla in (pygame.K_a, pygame.K_LEFT):
            self.cursor[q] = (self.cursor[q] - 1) % n
        elif tecla in (pygame.K_d, pygame.K_RIGHT):
            self.cursor[q] = (self.cursor[q] + 1) % n
        elif tecla in (pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN):  # anda entre as fileiras
            passo = -COLUNAS if tecla in (pygame.K_w, pygame.K_UP) else COLUNAS
            novo = self.cursor[q] + passo
            if novo >= n:
                novo = self.cursor[q] % COLUNAS  # passou do fim: volta pra primeira fileira
            elif novo < 0:
                novo = self.cursor[q] + COLUNAS * ((n - 1 - self.cursor[q]) // COLUNAS)  # vai pra última
            self.cursor[q] = novo
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE, "clique"):
            self.confirmar()
        elif tecla == pygame.K_h:  # troca a habilidade (Trafo: ele ainda está decidindo)
            f = self.ficha_do_cursor(q)
            if f and f.get("habilidades_opcoes"):
                ops = f["habilidades_opcoes"]
                f["habilidade"] = ops[(ops.index(f["habilidade"]) + 1) % len(ops)]
                import save
                save.d().setdefault("passivas", {})[f["nome"]] = f["habilidade"]  # (lembra na próxima luta)
                save.salvar()
        elif tecla in (pygame.K_q, pygame.K_e) and q == 0:  # troca a roupa
            f = self.ficha_do_cursor(0)
            if f:
                import roupas
                import save
                minhas = [r["id"] for r in roupas.da(f) if save.tem_roupa(f["nome"], r["id"])]
                i = minhas.index(save.usando(f["nome"])) if save.usando(f["nome"]) in minhas else 0
                passo = -1 if tecla == pygame.K_q else 1
                save.usar(f["nome"], minhas[(i + passo) % len(minhas)])
        elif tecla in (pygame.K_q, pygame.K_e) and q == 1:  # a roupa do ADVERSÁRIO (das que você tem)
            f = self.ficha_do_cursor(1)
            if f:
                todas = self.roupas_bot_de(f)
                atual = self.roupa_bot.get(f["nome"], "padrao")
                i = todas.index(atual) if atual in todas else 0
                self.roupa_bot[f["nome"]] = todas[(i + (-1 if tecla == pygame.K_q else 1)) % len(todas)]
        elif tecla == pygame.K_BACKSPACE and q == 1:
            self.quem, self.escolhido[0] = 0, None

    def mouse(self, pos, clicou):
        for i in range(len(self.cartas)):
            if self.rect_carta(i).collidepoint(pos):
                self.cursor[self.quem] = i
                if clicou:
                    self.confirmar()
                return

    def confirmar(self):
        q = self.quem
        i = self.cursor[q]
        if i >= len(self.lista):  # "?" = sorteia
            i = random.randrange(len(self.lista))
            self.cursor[q] = i
        self.escolhido[q] = i
        if q == 0 and not self.so_um:
            self.quem = 1
        else:
            self.pronto = True

    # ---- desenho ----
    def roupas_bot_de(self, f):
        import roupas
        import save
        return [r["id"] for r in roupas.da(f) if save.tem_roupa(f["nome"], r["id"])]

    def lutador_grande(self, ficha, lado):
        chave = (ficha["nome"], lado, ficha.get("roupa"))
        if chave not in self.grandes:
            l = Lutador(ficha, 0, 1 if lado == 0 else -1)
            l.s = ficha["tam"] * 1.55
            self.grandes[chave] = l
        return self.grandes[chave]

    def desenhar(self, tela):
        self.t += 1
        tela.blit(fundo_selecao(self.t), (0, 0))
        texto_grande(tela, self.titulo or ("ESCOLHA SEU LUTADOR" if self.quem == 0 else "ESCOLHA O ADVERSÁRIO"), 34,
                     (255, 220, 70), (LARGURA // 2, 42))
        for lado in (0, 1):
            if lado == 1 and self.so_um:
                continue
            x = 128 if lado == 0 else LARGURA - 128
            cor = AZUL if lado == 0 else VERMELHO
            ficha = self.ficha_do_cursor(lado) if (lado == 0 or self.quem == 1) else None
            # palco com luz
            luz = pygame.Surface((300, 420), pygame.SRCALPHA)
            for i in range(10, 0, -1):
                pygame.draw.ellipse(luz, (*cor, 8), (150 - i * 14, 40, i * 28, 380))
            tela.blit(luz, (x - 150, 0))
            pygame.draw.ellipse(tela, (20, 18, 30), (x - 100, 346, 200, 30))
            pygame.draw.ellipse(tela, cor, (x - 100, 346, 200, 30), 3)
            if ficha is None:
                texto_grande(tela, "?", 130, (90, 80, 120), (x, 230))
                continue
            import roupas
            if lado == 0:
                ficha = roupas.vestir(ficha)
            else:  # o adversário com a roupa que você escolheu pra ele
                ficha = roupas.vestir(ficha, self.roupa_bot.get(ficha["nome"], "padrao"))
                if self.quem == 1 and len(self.roupas_bot_de(ficha)) > 1:
                    atual = next(r["nome"] for r in roupas.da(ficha) if r["id"] == ficha.get("roupa", "padrao"))
                    texto(tela, f"Q/E roupa do {self.rotulo2}: {atual}", 13, (255, 160, 150), (x, 80))
            l = self.lutador_grande(ficha, lado)
            l.x, l.y = x, 360
            l.chao_sombra = 360
            l.t = self.t
            l.desenhar(tela)
            confirmado = self.escolhido[lado] is not None
            texto_grande(tela, ficha["nome"], 26, BRANCO if confirmado else (210, 210, 230), (x, 396))
            if not confirmado:
                texto(tela, "1P" if lado == 0 else self.rotulo2, 16, cor, (x, 424))
            if lado == 0:  # MAESTRIA: o nível e o título
                n = maestria.nivel(ficha)
                tit = maestria.titulo(ficha)
                import passe
                evento = passe.titulo_escolhido()  # TÍTULO DO EVENTO (do passe): fica no lugar do de maestria
                if evento:
                    texto(tela, f"NÍVEL {n}  {evento}", 13, (255, 150, 50), (x, 444))
                else:
                    texto(tela, f"NÍVEL {n}" + (f"  {tit}" if tit else ""), 13,
                          maestria.moldura(ficha) or (190, 190, 210), (x, 444))
            if lado == 0 and self.quem == 0:
                import roupas
                import save
                todas = roupas.da(ficha)
                minhas = [r for r in todas if save.tem_roupa(ficha["nome"], r["id"])]
                atual = next(r["nome"] for r in todas if r["id"] == ficha.get("roupa", "padrao"))
                if len(minhas) > 1:
                    texto(tela, f"Q/E roupa: {atual}", 13, (150, 220, 255), (x, 80))
                elif len(todas) > 1:
                    texto(tela, "mais roupas na LOJA", 13, (190, 190, 210), (x, 80))
        # grade de retratos (tipo Injustice 2): os escolhidos ficam por cima
        cursores = {}
        for lado in (0, 1):
            if not (lado == 1 and (self.so_um or self.quem == 0)):
                cursores.setdefault(self.cursor[lado], []).append(lado)
        ordem = sorted(range(len(self.cartas)), key=lambda i: i in cursores)
        for i in ordem:
            r = self.rect_carta(i)
            if i in cursores:
                r = r.inflate(8, 8)
                tela.blit(pygame.transform.scale(self.cartas[i], r.size), r.topleft)
            else:
                tela.blit(self.cartas[i], r.topleft)
            if i < len(self.lista):  # faixinha com a cor do lutador
                pygame.draw.rect(tela, self.lista[i]["cor"], (r.x, r.bottom - 5, r.w, 5))
            pygame.draw.rect(tela, (12, 10, 20), r, 2)
            if i < len(self.lista) and maestria.moldura(self.lista[i]):  # MAESTRIA: moldura bronze/prata/ouro...
                maestria.desenhar_moldura(tela, r, self.lista[i], self.t)
            for k, lado in enumerate(cursores.get(i, [])):
                cor = AZUL if lado == 0 else VERMELHO
                pisca = 3 if (self.t // 10) % 2 else 4
                pygame.draw.rect(tela, cor, r.inflate(4 + k * 8, 4 + k * 8), pisca, border_radius=3)
                dx = (k * 22 - 11) * (len(cursores[i]) - 1)
                texto(tela, "1P" if lado == 0 else self.rotulo2, 12, cor, (r.centerx + dx, r.top - 9))
        # golpes do lutador do cursor (embaixo da grade)
        f = self.ficha_do_cursor(self.quem)
        y = self.fim_grade() + 16
        if f and f.get("nomes"):
            n = f["nomes"]
            from efeitos import texto_botao
            for k, b in enumerate(("E", "Q", "R", "SHIFT", "Z")):
                texto_botao(tela, b, n[b], 14, (230, 230, 240), (LARGURA // 2, y + k * 20))
            y += 5 * 20 + 6
            if f.get("habilidade"):
                import habilidades as hab
                h = hab.HABILIDADES[f["habilidade"]]
                texto(tela, "HABILIDADE: " + h["nome"], 15, (255, 220, 90), (LARGURA // 2, y))
                texto(tela, h["desc"], 12, (220, 220, 235), (LARGURA // 2, y + 18))
                if f.get("habilidades_opcoes"):
                    texto(tela, "H troca a habilidade", 12, (150, 220, 255), (LARGURA // 2, y + 35))
        import controle_video
        rodape = "direcional escolhe   A confirma   B volta   LB/RB roupa" if controle_video.no_controle() else \
            "WASD escolhe   ENTER ou clique confirma   ESC volta"
        texto(tela, rodape, 14, (200, 200, 220), (LARGURA // 2, ALTURA - 14))


def quebrar(txt, tam, largura):
    """Quebra o texto em linhas que cabem na largura."""
    linhas, atual = [], ""
    for palavra in txt.split():
        teste = (atual + " " + palavra).strip()
        if fonte(tam).size(teste)[0] > largura and atual:
            linhas.append(atual)
            atual = palavra
        else:
            atual = teste
    return linhas + [atual] if atual else linhas


def balao(tela, txt, lado, letras, alvo=None):
    """Balão de fala em cima do lutador (as letras vão aparecendo uma por uma).
    alvo = (x, y) pra onde a pontinha aponta (na luta: a cabeça de quem fala)."""
    tam = 17
    linhas = quebrar(txt, tam, 300)
    alt = len(linhas) * 24 + 22
    if alvo is None:
        cx = 250 if lado == 0 else LARGURA - 250
        r = pygame.Rect(cx - 170, 30, 340, alt)
        ponta = (cx - 60 if lado == 0 else cx + 60, r.bottom + 22)
        base = (cx - 90, r.bottom - 2) if lado == 0 else (cx + 90, r.bottom - 2)
    else:
        cx = max(176, min(LARGURA - 176, alvo[0] + (60 if lado == 0 else -60)))
        topo = max(64, alvo[1] - 26 - alt)
        r = pygame.Rect(cx - 170, topo, 340, alt)
        ponta = (alvo[0], r.bottom + 22)
        base = (max(r.x + 30, min(r.right - 30, alvo[0] + (14 if lado == 0 else -14))), r.bottom - 2)
    pygame.draw.polygon(tela, (12, 10, 20), [(base[0] - 16, base[1]), (base[0] + 16, base[1]), ponta])
    pygame.draw.rect(tela, (12, 10, 20), r.inflate(8, 8), border_radius=16)
    pygame.draw.rect(tela, (250, 248, 236), r, border_radius=14)
    pygame.draw.polygon(tela, (250, 248, 236), [(base[0] - 11, base[1] - 4), (base[0] + 11, base[1] - 4),
                                                (ponta[0] + (4 if lado == 0 else -4), ponta[1] - 7)])
    resta = letras
    for i, linha in enumerate(linhas):
        parte = linha[:max(0, resta)]
        resta -= len(linha) + 1
        if parte:
            img = fonte(tam).render(parte, True, (20, 16, 30))
            tela.blit(img, (r.x + 20, r.y + 12 + i * 24))


class TelaVS:
    """Os dois grandões frente a frente antes da luta (e trocando umas provocações)."""
    FALA1, FALA2, DEPOIS = 34, 130, 110  # quando cada um fala (e quanto tempo fica depois da última)

    def __init__(self, f1, f2, com_falas=False):
        import falas
        self.f = (f1, f2)
        self.t = 0
        # (v2.0: as falas passaram pra ENTRADA da luta, cada um fala na arena; aqui só com com_falas=True)
        self.falas = falas.dialogo(f1, f2) if com_falas else []
        self.DURACAO = self.FALA2 + max(60, len(self.falas[-1][1]) * 2) + self.DEPOIS if self.falas else 150
        self.l = [Lutador(f1, 0, 1), Lutador(f2, 0, -1)]
        for l, f in zip(self.l, self.f):
            l.s = f["tam"] * 2.2

    @property
    def acabou(self):
        return self.t >= self.DURACAO

    def desenhar(self, tela):
        self.t += 1
        t = self.t
        k = min(1, t / 18)
        entra = 1 - (1 - k) ** 3
        # metade azul e metade vermelha, cortadas na diagonal
        tela.fill((10, 8, 18))
        meio = LARGURA // 2
        pygame.draw.polygon(tela, (30, 50, 110), [(0, 0), (meio + 80, 0), (meio - 80, ALTURA), (0, ALTURA)])
        pygame.draw.polygon(tela, (110, 30, 36), [(meio + 80, 0), (LARGURA, 0), (LARGURA, ALTURA), (meio - 80, ALTURA)])
        for i in range(14):  # riscos de velocidade
            y = (i * 47 + t * 9) % ALTURA
            pygame.draw.line(tela, (60, 80, 150), (0, y), (meio - 140, y), 2)
            pygame.draw.line(tela, (150, 60, 60), (meio + 140, ALTURA - y), (LARGURA, ALTURA - y), 2)
        for lado, l in enumerate(self.l):
            alvo = 230 if lado == 0 else LARGURA - 230
            fora = -260 if lado == 0 else LARGURA + 260
            l.x = fora + (alvo - fora) * entra
            l.y = l.chao_sombra = 470
            l.t = t
            l.desenhar(tela)
            nome_x = 230 if lado == 0 else LARGURA - 230
            texto_grande(tela, self.f[lado]["nome"], 34, BRANCO, (nome_x, 506))
            if self.f[lado].get("nome_completo"):  # o nome inteiro, pequenininho embaixo
                texto(tela, self.f[lado]["nome_completo"], 14, (200, 200, 220), (nome_x, 530))
        if t > 14:  # o VS estourando
            e = 1 + max(0, (26 - t) / 12) * 1.5
            pygame.draw.line(tela, (255, 240, 200), (meio + 80, 0), (meio - 80, ALTURA), 6)
            texto_grande(tela, "VS", 110, (255, 220, 70), (meio, ALTURA // 2 - 20), e, contorno=(60, 20, 0))
        if t < 6:
            branco = pygame.Surface((LARGURA, ALTURA))
            branco.fill(BRANCO)
            branco.set_alpha(255 - t * 40)
            tela.blit(branco, (0, 0))
        for i, (lado, txt) in enumerate(self.falas[:2]):
            comeca = self.FALA1 if i == 0 else self.FALA2
            if t >= comeca:
                balao(tela, txt, lado, (t - comeca) * 2)
        import rivais  # RIVAIS: a faixa "RIVAIS!" com o lema (só se forem rivais)
        rivais.desenhar_faixa(tela, self.f[0], self.f[1], self.t)
        texto(tela, "ENTER pula", 13, (220, 220, 230), (LARGURA - 60, ALTURA - 14))


class TelaCenario:
    """Escolhe o cenário da luta (começa na casa do adversário). Igual à seleção de lutador:
    grade de cartinhas no meio, o escolhido aparece grandão no fundo da tela."""
    COLUNAS = 6
    CW, CH = 104, 58   # tamanho da cartinha (16:9, igual à tela)

    def __init__(self, padrao):
        import cenarios
        self.nomes = cenarios.disponiveis()  # (a VILA DOS SAPOS só com o código)
        self.cursor = self.nomes.index(padrao) if padrao in self.nomes else 0
        self.miniaturas = [pygame.transform.smoothscale(cenarios.cenario(n).fundo, (self.CW, self.CH))
                           for n in self.nomes]
        self.fundos = {}
        self.pronto = False
        self.escolhido = None
        self.t = 0

    def rect(self, i):
        lin, col = divmod(i, self.COLUNAS)
        x0 = LARGURA // 2 - (self.COLUNAS * (self.CW + 8) - 8) // 2
        return pygame.Rect(x0 + col * (self.CW + 8), 92 + lin * (self.CH + 10), self.CW, self.CH)

    def tecla(self, tecla):
        n = len(self.nomes) + 1  # (+ o "?" = sorteia)
        if tecla in (pygame.K_a, pygame.K_LEFT):
            self.cursor = (self.cursor - 1) % n
        elif tecla in (pygame.K_d, pygame.K_RIGHT):
            self.cursor = (self.cursor + 1) % n
        elif tecla in (pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN):  # (mesma conta da seleção de lutador)
            c = self.COLUNAS
            novo = self.cursor + (-c if tecla in (pygame.K_w, pygame.K_UP) else c)
            if novo >= n:
                novo = self.cursor % c  # passou do fim: volta pra primeira fileira
            elif novo < 0:
                novo = self.cursor + c * ((n - 1 - self.cursor) // c)  # vai pra última
            self.cursor = novo
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE, "clique"):
            i = self.cursor if self.cursor < len(self.nomes) else random.randrange(len(self.nomes))
            self.escolhido = self.nomes[i]
            self.pronto = True

    def mouse(self, pos, clicou):
        for i in range(len(self.nomes) + 1):
            if self.rect(i).collidepoint(pos):
                self.cursor = i
                if clicou:
                    self.tecla("clique")

    def fundo(self, i):
        """O cenário escolhido na tela inteira, um pouco mais escuro (pra grade aparecer por cima)."""
        if i not in self.fundos:
            import cenarios
            f = pygame.transform.smoothscale(cenarios.cenario(self.nomes[i]).fundo, (LARGURA, ALTURA))
            escuro = pygame.Surface((LARGURA, ALTURA))
            escuro.fill((10, 8, 20))
            escuro.set_alpha(110)
            f.blit(escuro, (0, 0))
            self.fundos[i] = f
        return self.fundos[i]

    def desenhar(self, tela):
        self.t += 1
        i = self.cursor
        if i < len(self.nomes):
            tela.blit(self.fundo(i), (0, 0))
        else:
            tela.blit(fundo_selecao(self.t), (0, 0))
        faixa = pygame.Surface((LARGURA, 74), pygame.SRCALPHA)
        faixa.fill((8, 6, 18, 150))
        tela.blit(faixa, (0, 0))
        texto_grande(tela, "ESCOLHA O CENÁRIO", 34, (255, 220, 70), (LARGURA // 2, 40))
        # a grade (o do cursor fica por cima, maior)
        n = len(self.nomes) + 1
        for k in sorted(range(n), key=lambda k: k == self.cursor):
            r = self.rect(k)
            sel = k == self.cursor
            if sel:
                r = r.inflate(14, 8)
            pygame.draw.rect(tela, (8, 6, 18), r.inflate(6, 6), border_radius=4)
            if k < len(self.nomes):
                img = self.miniaturas[k] if not sel else pygame.transform.smoothscale(self.miniaturas[k], r.size)
                tela.blit(img, r.topleft)
            else:
                pygame.draw.rect(tela, (40, 34, 60), r)
                texto(tela, "?", 44, (255, 220, 70), (r.centerx, r.centery + 2))
            pygame.draw.rect(tela, (12, 10, 20), r, 2)
            if sel:
                pygame.draw.rect(tela, (255, 220, 70), r.inflate(6, 6), 4 if (self.t // 10) % 2 else 2,
                                 border_radius=3)
        # o nome grandão embaixo
        nome = self.nomes[i] if i < len(self.nomes) else "SORTEAR"
        y = self.rect(n - 1).bottom + 70
        texto_grande(tela, nome, 44, BRANCO, (LARGURA // 2, y))
        if i >= len(self.nomes):
            texto(tela, "um cenário qualquer, surpresa!", 16, (220, 220, 235), (LARGURA // 2, y + 40))
        import controle_video
        rodape = "direcional escolhe   A confirma" if controle_video.no_controle() else             "WASD escolhe   ENTER ou clique confirma"
        texto(tela, rodape, 14, (220, 220, 235), (LARGURA // 2, ALTURA - 14))
