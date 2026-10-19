"""COMO JOGAR: os tutoriais (saíram da tela inicial pra ela ficar limpinha).
Se o jogador está no controle de videogame, mostra os botões do controle."""
import pygame

import controle_video
from config import *  # noqa: F401,F403
from efeitos import texto, texto_grande
from selecao import fundo_selecao

TECLADO = [
    ("ANDAR E DEFENDER", ["A / D  andar      W  pular      S  agachar",
                          "segurar pra TRÁS = defender",
                          "PARRY: toque pra FRENTE na hora",
                          "(golpe baixo: toque pra BAIXO)",
                          "ROLAR: M1 + M2 juntos",
                          "(segurando FRENTE: rola pra frente)"]),
    ("BATER", ["M1 (botão esquerdo)  soco",
               "M2 (botão direito)  chute",
               "agachado ou pulando muda o golpe",
               "COMBO: soco, soco, chute, especial",
               "AÉREO: Q joga pra cima, segura W,",
               "bate no ar e termina com CHUTE"]),
    ("ESPECIAIS", ["segura M3 (rodinha) e aperta",
                   "E, Q, R ou SHIFT",
                   "Z = ULTIMATE (com a barra cheia)",
                   "C = 2ª ULTIMATE (barra AMARELA cheia)",
                   "soltou a rodinha? ainda tem 0,2 s",
                   "T = PROVOCAR (enche a barra)"]),
    ("BARRA AZUL", ["M3 2x (toque e segura) + especial = EX",
                    "  E: mais tiros    R: o dobro de ataques",
                    "  Q: rasteira + soco + Q    SHIFT: vai e volta",
                    "apanhando, M3 2x = ESCAPE",
                    "barra cheia: Z = ULTIMATE"]),
    ("TRIO, TREINO E PASSIVA", ["TRIO: G troca de lutador",
                                "(quem sai recupera um pouco de vida)",
                                "X = PASSIVA (lobo do Tamer, Sphyrus nada)",
                                "SELEÇÃO: H troca a passiva",
                                "TREINO: H mostra as caixas   1 a 5: boneco",
                                "P enche a barra (pra testar)"]),
    ("OUTROS", ["ESC pausa: golpes e MODO FOTO",
                "REI DA ARENA: quem ganha fica no trono",
                "LOJA: roupas, entradas, vitórias...",
                "PERFIL: troféus e MISSÕES DO DIA",
                "CÓDIGOS: as roupas ??? têm charadas...",
                "F11 tela cheia"]),
]

CONTROLE = [
    ("ANDAR E DEFENDER", ["direcional ou analógico: andar e pular",
                          "segurar pra TRÁS = defender",
                          "PARRY: toque pra FRENTE bem na hora",
                          "(golpe baixo: toque pra BAIXO)",
                          "ROLAR: A + B juntos",
                          "(segurando FRENTE: rola pra frente)"]),
    ("BATER", ["A  soco      B  chute",
               "agachado ou pulando muda o golpe",
               "COMBO: soco, soco, chute, especial",
               "AÉREO: Y joga pra cima, segura CIMA,",
               "bate no ar e termina com CHUTE"]),
    ("ESPECIAIS", ["cada especial tem o seu botão:",
                   "X = E     Y = Q     LB = R     RB = SHIFT",
                   "RT = ULTIMATE (com a barra cheia)",
                   "LT + RT = 2ª ULTIMATE (barra AMARELA)",
                   "BACK = PROVOCAR"]),
    ("BARRA AZUL", ["segura LT + especial = EX",
                    "  E: mais tiros    R: o dobro de ataques",
                    "  Q: rasteira + soco + Q    SHIFT: vai e volta",
                    "apanhando, LT = ESCAPE (meia barra)"]),
    ("TRIO, TREINO E PASSIVA", ["TRIO: R3 (aperta o analógico) troca",
                                "(quem sai recupera um pouco de vida)",
                                "L3 = PASSIVA (lobo do Tamer, Sphyrus nada)",
                                "SELEÇÃO: Y troca a passiva",
                                "TREINO: H (teclado) mostra as caixas"]),
    ("OUTROS", ["START pausa: golpes e MODO FOTO",
                "menus: direcional, A confirma, B volta",
                "REI DA ARENA: desafiante no controle",
                "LOJA: roupas, entradas, vitórias...",
                "PERFIL: troféus e MISSÕES DO DIA",
                "CÓDIGOS: as roupas ??? têm charadas..."]),
]


class TelaComoJogar:
    def __init__(self):
        self.t = 0

    def desenhar(self, tela):
        self.t += 1
        tela.blit(fundo_selecao(self.t), (0, 0))
        no_controle = controle_video.no_controle()
        texto_grande(tela, "COMO JOGAR", 40, (255, 220, 70), (LARGURA // 2, 40))
        texto(tela, "(no controle de videogame)" if no_controle else "(teclado e mouse)", 14, (150, 220, 255),
              (LARGURA // 2, 74))
        partes = CONTROLE if no_controle else TECLADO
        for k, (titulo, linhas) in enumerate(partes):
            col, lin = k % 3, k // 3
            r = pygame.Rect(20 + col * 312, 96 + lin * 210, 296, 196)
            pygame.draw.rect(tela, (26, 22, 42), r, border_radius=12)
            pygame.draw.rect(tela, (90, 80, 130), r, 2, border_radius=12)
            texto(tela, titulo, 17, AMARELO, (r.centerx, r.y + 20))
            for i, linha in enumerate(linhas):
                img = pygame.font.SysFont("arial", 14, bold=True).render(linha, True, BRANCO)
                tela.blit(img, (r.x + 14, r.y + 42 + i * 24))
        texto(tela, "ESC (ou B) volta", 14, (200, 200, 220), (LARGURA // 2, ALTURA - 14))
