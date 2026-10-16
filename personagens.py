"""Os lutadores.

Os bonecos de treino são provisórios. "golpes" diz qual golpe sai em cada botão (M3 + E/Q/R/SHIFT/Z).
Quem não tem "golpes" usa os golpes dos bonecos de treino.
"""
from corpo import desenhar_manequim
from max10 import GOLPES_MAX10, desenhar_robo
from max10 import entrada as entrada_max
from max10 import entrada_efeito as entrada_efeito_max
from max10 import figura_extra as figura_max
from max10 import vitoria as vitoria_max
from max10 import vitoria_efeito as vitoria_efeito_max
from rib import GOLPES_RIB, POSES_RIB, desenhar_rib, rib_todo_quadro
from rib import entrada as entrada_rib
from rib import entrada_efeito as entrada_efeito_rib
from rib import figura_extra as figura_rib
from rib import vitoria as vitoria_rib
from rib import vitoria_efeito as vitoria_efeito_rib
from trafo import GOLPES_TRAFO, POSES_TRAFO, desenhar_trafo
from king import GOLPES_KING, POSES_KING, desenhar_king
from king import entrada as entrada_king
from king import entrada_efeito as entrada_efeito_king
from king import figura_extra as figura_king
from king import vitoria as vitoria_king
from cannan import GOLPES_CANNAN, POSES_CANNAN, desenhar_cannan, cansado_efeito
from cannan import entrada as entrada_cannan
from finn import GOLPES_FINN, POSES_FINN, desenhar_finn
from kun import GOLPES_KUN, POSES_KUN, desenhar_kun
import xeno
import tai
import tamer
from kun import entrada as entrada_kun
from kun import entrada_efeito as entrada_efeito_kun
from kun import figura_extra as figura_kun
from kun import vitoria as vitoria_kun
from kun import vitoria_efeito as vitoria_efeito_kun
from finn import entrada as entrada_finn
from finn import entrada_efeito as entrada_efeito_finn
from finn import figura_extra as figura_finn
from finn import vitoria as vitoria_finn
from cannan import entrada_efeito as entrada_efeito_cannan
from cannan import figura_extra as figura_cannan
from cannan import vitoria as vitoria_cannan
from trafo import entrada as entrada_trafo
from trafo import entrada_efeito as entrada_efeito_trafo
from trafo import figura_extra as figura_trafo
from trafo import vitoria as vitoria_trafo
from trafo import vitoria_efeito as vitoria_efeito_trafo

NOMES_PALITO = {"E": "bola", "Q": "subida", "R": "giro", "SHIFT": "avanço", "Z": "BOLA GIGANTE"}

# O BONECO DE TREINO: não é lutador da lista; é o parceiro do MODO TREINO (dá pra escolher a cor).
CORES_BONECO = [("AZUL", (70, 130, 220), (120, 200, 255)), ("VERMELHO", (210, 70, 60), (255, 150, 90)),
                ("VERDE", (70, 170, 90), (150, 240, 160)), ("AMARELO", (220, 190, 60), (255, 230, 120)),
                ("ROXO", (140, 90, 200), (210, 160, 255)), ("BRANCO", (225, 225, 230), (255, 255, 255))]
BONECO = dict(nome="BONECO DE TREINO", cor=CORES_BONECO[0][1], vida=100, vel=3.8, pulo=16.5, forca=1.0, tam=1.35,
              desenho=desenhar_manequim, cor_poder=CORES_BONECO[0][2], nomes=NOMES_PALITO, cenario="TEMPLO")


def sombra(ficha):
    """O chefão do Arcade: a SOMBRA do lutador (mesmos golpes, escura, um pouco mais forte)."""
    return dict(ficha, nome="SOMBRA DO " + ficha["nome"], sombra=True, vida=120, forca=1.15, cenario="TEMPLO",
                cor_poder=(170, 120, 255))


def boneco(i):
    """O boneco de treino na cor i."""
    _, cor, poder = CORES_BONECO[i % len(CORES_BONECO)]
    return dict(BONECO, cor=cor, cor_poder=poder)


PERSONAGENS = [
    dict(nome="MAX-10", cor=(200, 164, 86), vida=100, vel=3.4, pulo=16, forca=1.0, tam=1.42,
         cor_poder=(255, 50, 40), desenho=desenhar_robo, golpes=GOLPES_MAX10, figura_extra=figura_max, provocacao="ERRO 404: DESAFIO NÃO ENCONTRADO.", cenario="FERRO-VELHO", habilidade="maquinario",
         entrada=entrada_max, entrada_efeito=entrada_efeito_max, vitoria=vitoria_max,
         vitoria_efeito=vitoria_efeito_max,
         nomes={"E": "laser dos olhos", "Q": "agarrão (joga pra cima)", "R": "metralhadora de socos", "SHIFT": "voozinho",
                "Z": "RASANTE"}),
    dict(nome="RIB", cor=(100, 174, 66), vida=100, vel=4.3, pulo=18, forca=1.0, tam=1.34, altura=0.84,
         cor_poder=(150, 220, 255), desenho=desenhar_rib, golpes=GOLPES_RIB, poses=POSES_RIB,
         todo_quadro=rib_todo_quadro, provocacao="Tá lento, hein?",
         provocacao_quadros=[(0, "parado"), (8, "r_cruzado"), (58, "r_cruzado"), (70, "parado")], figura_extra=figura_rib, cenario="PÂNTANO", habilidade="ninja", entrada=entrada_rib, entrada_efeito=entrada_efeito_rib,
         vitoria=vitoria_rib, vitoria_efeito=vitoria_efeito_rib,
         nomes={"E": "shuriken", "Q": "rasteira + chute pra cima", "R": "corrida ninja", "SHIFT": "LINGUADA",
                "Z": "KAGE BUNSHIN"}),
    dict(nome="TRAFO", cor=(190, 152, 52), vida=100, vel=3.6, pulo=15.5, forca=1.0, tam=1.32, altura=0.9,
         cor_poder=(196, 36, 28), desenho=desenhar_trafo, golpes=GOLPES_TRAFO, poses=POSES_TRAFO,
         figura_extra=figura_trafo, provocacao="AUUUUUU!",
         provocacao_quadros=[(0, "parado"), (8, "t_agacha"), (16, "t_uivo"), (58, "t_uivo"), (70, "parado")], barra_mult=0.5, cenario="TOCA", habilidade="conexao",
         habilidades_opcoes=("conexao", "mutacao"),  # ele ainda está decidindo: H troca na seleção
         entrada=entrada_trafo, entrada_efeito=entrada_efeito_trafo,
         vitoria=vitoria_trafo, vitoria_efeito=vitoria_efeito_trafo,
         nomes={"E": "linguão (paralisa)", "Q": "braços da terra", "R": "metralhadora de olhos", "SHIFT": "pulão",
                "Z": "TRANSFORMAÇÃO"}),
    dict(nome="KING RIP", cor=(62, 98, 182), vida=100, vel=3.7, pulo=16.5, forca=1.0, tam=1.36,
         cor_poder=(200, 220, 255), desenho=desenhar_king, golpes=GOLPES_KING, poses=POSES_KING,
         figura_extra=figura_king, provocacao="Na minha época, eu já tinha vencido.",
         provocacao_quadros=[(0, "parado"), (10, "k_gira"), (30, "k_bastao"), (58, "k_bastao"), (70, "parado")], cenario="DOJO", habilidade="maestria", entrada=entrada_king,
         entrada_efeito=entrada_efeito_king, vitoria=vitoria_king,
         nomes={"E": "nunchaku bumerangue", "Q": "chute acrobático", "R": "nunchaku giratório",
                "SHIFT": "salto com nunchaku", "Z": "MESTRE DO NUNCHAKU"}),
    dict(nome="CANNAN", cor=(96, 104, 60), vida=100, vel=3.6, pulo=15.5, forca=1.0, tam=1.38,
         cor_poder=(130, 220, 255), desenho=desenhar_cannan, golpes=GOLPES_CANNAN, poses=POSES_CANNAN,
         figura_extra=figura_cannan, provocacao="Isso é tudo, recruta?",
         provocacao_quadros=[(0, "parado"), (8, "c_continencia"), (58, "c_continencia"), (70, "parado")], cenario="CAMPO DE BATALHA", habilidade="colete", entrada=entrada_cannan,
         entrada_efeito=entrada_efeito_cannan, vitoria=vitoria_cannan, cansado_efeito=cansado_efeito,
         nomes={"E": "pistola (3 tiros)", "Q": "coronhada + soco pra cima", "R": "canhão de perto",
                "SHIFT": "corrida maluca", "Z": "FOGO TOTAL (segura o Z pra carregar)"}),
    dict(nome="FINN", cor=(104, 58, 150), vida=100, vel=3.5, pulo=15.5, forca=1.0, tam=1.36,
         cor_poder=(190, 120, 255), desenho=desenhar_finn, golpes=GOLPES_FINN, poses=POSES_FINN,
         figura_extra=figura_finn, provocacao="VOCÊ NÃO PASSARÁ!",
         provocacao_quadros=[(0, "parado"), (8, "f_vitoria"), (58, "f_vitoria"), (70, "parado")],
         cenario="TORRE DO MAGO", habilidade="poder_magico", entrada=entrada_finn, entrada_efeito=entrada_efeito_finn, vitoria=vitoria_finn,
         nomes={"E": "bola de fogo", "Q": "levitação (joga pra cima)", "R": "cajado amarelo (barrage)",
                "SHIFT": "empurrão mágico", "Z": "MINI SOL"}),
    dict(nome="KUN", cor=(176, 44, 42), vida=100, vel=3.9, pulo=16.5, forca=1.0, tam=1.34,
         cor_poder=(255, 220, 140), desenho=desenhar_kun, golpes=GOLPES_KUN, poses=POSES_KUN,
         figura_extra=figura_kun, provocacao="Escolha uma carta... qualquer carta.",
         provocacao_quadros=[(0, "parado"), (8, "k_vitoria"), (58, "k_vitoria"), (70, "parado")],
         cenario="CASSINO", habilidade="as_na_manga", entrada=entrada_kun, entrada_efeito=entrada_efeito_kun, vitoria=vitoria_kun,
         vitoria_efeito=vitoria_efeito_kun,
         nomes={"E": "carta", "Q": "shoryuken de carta (joga pra cima)", "R": "carta-espada",
                "SHIFT": "teleporte da carta", "Z": "CARTA DOS MÓVEIS"}),
    dict(nome="XENOMORPH", cor=(40, 42, 52), vida=100, vel=4.2, pulo=17, forca=1.0, tam=1.4, altura=0.85,
         cor_poder=(255, 210, 40), desenho=xeno.desenhar_xeno, golpes=xeno.GOLPES_XENO, poses=xeno.POSES_XENO,
         figura_extra=xeno.figura_extra, todo_quadro=xeno.todo_quadro, desenhar_sempre=xeno.desenhar_pocas,
         provocacao="Hssssssss...",
         provocacao_quadros=[(0, "parado"), (8, "x_vitoria"), (58, "x_vitoria"), (70, "parado")],
         cenario="LABORATÓRIO", habilidade="sangue_acido", entrada=xeno.entrada, entrada_efeito=xeno.entrada_efeito,
         vitoria=xeno.vitoria,
         nomes={"E": "cuspe de ácido", "Q": "rabada (joga pra cima)", "R": "garras", "SHIFT": "rasteja",
                "Z": "SEGUNDA BOCA"}),
    dict(nome="TAI", cor=(236, 190, 150), vida=120, vel=2.9, pulo=14.5, forca=1.0, tam=1.5,
         cor_poder=(255, 230, 160), desenho=tai.desenhar_tai, golpes=tai.GOLPES_TAI, poses=tai.POSES_TAI,
         figura_extra=tai.figura_extra, provocacao="HAKKEYOI!",
         provocacao_quadros=[(0, "parado"), (10, "t_shiko"), (50, "t_shiko"), (56, "t_pisao"), (70, "parado")],
         cenario="ARENA DE SUMÔ", habilidade="peso_pesado", entrada=tai.entrada, vitoria=tai.vitoria,
         nomes={"E": "pisão (onda no chão)", "Q": "agarra e arremessa", "R": "tapas de sumô",
                "SHIFT": "investida", "Z": "YOKOZUNA"}),
    dict(nome="TAMER", cor=(176, 152, 100), vida=100, vel=3.8, pulo=16.5, forca=1.0, tam=1.36,
         cor_poder=(200, 220, 255), desenho=tamer.desenhar_tamer, golpes=tamer.GOLPES_TAMER, poses=tamer.POSES_TAMER,
         figura_extra=tamer.figura_extra, todo_quadro=tamer.todo_quadro, desenhar_sempre=tamer.lobo_flash,
         tecla_x=tamer.trocar_lobo, tela_toda=True, provocacao="Bom garoto!",
         provocacao_quadros=[(0, "parado"), (8, "t_carinho"), (58, "t_carinho"), (70, "parado")],
         cenario="SELVA", habilidade="entendimento", entrada=tamer.entrada, vitoria=tamer.vitoria,
         nomes={"E": "o lobo avança", "Q": "chute na parede (sobe)", "R": "combo com o lobo",
                "SHIFT": "galope no lobo", "Z": "A ALCATEIA"}),
]


# ---- personagens SECRETOS (aparecem na seleção depois do código; nunca no online) ----
from ribbat_lutador import RIBBAT  # noqa: E402

SECRETOS = [RIBBAT]


def disponiveis():
    """Os lutadores que dá pra escolher agora (os normais + os secretos já desbloqueados)."""
    import codigos
    return PERSONAGENS + [f for f in SECRETOS if codigos.ativo(f["codigo"])]


# (MODO MALUCO "CABEÇÕES": marca as peças de cabeça de cada um)
import cannan as _cannan, finn as _finn, kun as _kun, king as _king, max10 as _max10  # noqa: E401,E402
import rib as _rib, trafo as _trafo  # noqa: E401,E402
for _m in (_max10, _rib, _trafo, _king, _cannan, _finn, _kun, xeno, tai, tamer):
    for _nome in ("CABECA", "CABECA_COSTAS"):
        if hasattr(_m, _nome):
            getattr(_m, _nome).cabeca = True
