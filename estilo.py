"""RANKING DE ESTILO (v3.0, escolha do Gomes): uma letra no canto que mostra o quanto você está lutando BONITO.

  D DEVAGAR → C CAPRICHADO → B BRABO → A ARRASADOR → S SINISTRO → SS SUPER SINISTRO → SSS SENSACIONAL!!!

Sobe quando você ACERTA golpes VARIADOS (golpe que você não usou faz tempo vale muito; repetir o mesmo vale quase
nada), cai quando você APANHA e vai descendo sozinha se você ficar sem acertar nada. No SSS a letra pega FOGO.
No fim da luta, a MAIOR letra que você alcançou dá MOEDAS BÔNUS.

Faz parte da luta (o partida chama nos dois PCs do online): sem random e sem nada que dependa do computador; os
números são só contas com o que aconteceu. O desenho só lê.
"""
import pygame

LETRAS = (  # (pontos pra chegar, letra, palavra, cor, moedas bônus se for a maior do fim da luta)
    (0, "D", "DEVAGAR", (150, 150, 160), 0),
    (100, "C", "CAPRICHADO", (110, 200, 255), 2),
    (220, "B", "BRABO", (120, 230, 120), 4),
    (360, "A", "ARRASADOR", (255, 220, 80), 6),
    (520, "S", "SINISTRO", (255, 150, 60), 10),
    (700, "SS", "SUPER SINISTRO", (255, 90, 70), 15),
    (880, "SSS", "SENSACIONAL!!!", (255, 60, 200), 20),
)
MAXIMO = 1000
GOLPE_NOVO, GOLPE_VARIADO, GOLPE_REPETIDO = 60, 28, 6  # quanto vale o acerto (novo / diferente do último / igual)
LEMBRA = 5                                            # quantos golpes ele lembra pra saber se é "novo"
APANHOU = 120                                         # quanto cai quando apanha
ESPERA, DESCE = 120, 1.6                              # 2 s sem acertar nada: começa a descer (por quadro)


class Estilo:
    def __init__(self):
        self.pontos = 0.0
        self.ultimos = []        # os últimos golpes que ACERTARAM (nomes)
        self.ultimo_t = -9999    # quando acertou da última vez
        self.maior = 0           # o maior índice de letra alcançado na luta
        self.subiu_t = -9999     # (pro desenho: a letra "pula" quando sobe)
        self.t = 0

    # ---- o que aconteceu na luta ----
    def acertou(self, nome, t):
        """Um golpe ACERTOU (o mesmo golpe acertando várias vezes seguidas — multi-hit — conta 1 vez cheia)."""
        if not nome:
            nome = "?"
        if nome not in self.ultimos:
            ganho = GOLPE_NOVO
        elif self.ultimos and self.ultimos[-1] != nome:
            ganho = GOLPE_VARIADO
        else:
            ganho = GOLPE_REPETIDO
        antes = self.indice()
        self.pontos = min(MAXIMO, self.pontos + ganho)
        self.ultimos = (self.ultimos + [nome])[-LEMBRA:]
        self.ultimo_t = t
        if self.indice() > antes:
            self.subiu_t = t
        self.maior = max(self.maior, self.indice())

    def apanhou(self):
        self.pontos = max(0.0, self.pontos - APANHOU)

    def passo(self, t):
        """Todo quadro: se faz tempo que não acerta nada, a letra vai descendo."""
        self.t = t
        if t - self.ultimo_t > ESPERA:
            self.pontos = max(0.0, self.pontos - DESCE)

    # ---- pra ler ----
    def indice(self):
        i = 0
        for k, (minimo, *_) in enumerate(LETRAS):
            if self.pontos >= minimo:
                i = k
        return i

    def letra(self):
        return LETRAS[self.indice()][1]

    def moedas_bonus(self):
        """As moedas bônus da MAIOR letra que ele alcançou na luta (e o nome dela, pro quadro das moedas)."""
        _, letra, palavra, _, moedas = LETRAS[self.maior]
        return moedas, f"ESTILO {letra}"

    # ---- o desenho (só lê) ----
    def desenhar(self, tela, x, y, t, lado=1):
        """A letra (com a palavra embaixo) em (x, y) = o meio da letra. lado = -1 alinha pra esquerda (jogador 2)."""
        from efeitos import fonte, texto_grande
        i = self.indice()
        minimo, letra, palavra, cor, _ = LETRAS[i]
        prox = LETRAS[i + 1][0] if i + 1 < len(LETRAS) else MAXIMO
        enchendo = (self.pontos - minimo) / max(1, prox - minimo)
        pulo = max(0.0, 1 - (t - self.subiu_t) / 12)  # acabou de subir: a letra cresce e volta
        treme = (t // 2) % 2 if i >= 5 else 0
        if i == len(LETRAS) - 1:
            _fogo(tela, x, y, t)
        texto_grande(tela, letra, 34 if len(letra) < 3 else 30, cor, (x + treme * lado, y), escala=1 + 0.5 * pulo,
                     contorno=(20, 10, 20))
        img = fonte(11).render(palavra, True, cor)
        sombra = fonte(11).render(palavra, True, (20, 10, 20))
        px = x - img.get_width() // 2
        tela.blit(sombra, (px + 1, y + 21))
        tela.blit(img, (px, y + 20))
        # a barrinha até a próxima letra (em degraus, pixel)
        larg = 44
        pygame.draw.rect(tela, (20, 10, 20), (x - larg // 2 - 1, y + 35, larg + 2, 5))
        pygame.draw.rect(tela, cor, (x - larg // 2, y + 36, int(larg * min(1.0, enchendo)) // 4 * 4, 3))


def _fogo(tela, x, y, t):
    """O FOGO do SSS: labaredas em pixel subindo atrás da letra."""
    cores = ((255, 230, 120), (255, 150, 40), (230, 60, 30))
    for k in range(11):
        fase = (t * 2 + k * 7) % 24
        alto = 9 + (k * 5) % 7
        bx = x - 40 + k * 8
        for j in range(max(0, alto - fase // 5)):
            cor = cores[2 - min(2, j * 3 // max(1, alto))]  # (embaixo vermelho, em cima amarelo)
            pygame.draw.rect(tela, cor, (bx + ((j + k + t // 6) % 2) * 2, y + 16 - j * 4 - fase // 3, 4, 4))
