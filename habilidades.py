"""Habilidades (passivas) de cada personagem — criadas pelo Gomes.

  MAX-10  MAQUINÁRIO PESADO  com 25% de vida ou menos: +25% de dano e leva 25% menos
  RIB     POSTURA NINJA      hitbox naturalmente menor
  TRAFO   (ele ainda está decidindo, dá pra trocar na seleção com H)
          CONEXÃO TERRESTRE  agachado fica bem menor, bate o dobro e leva menos dano
          MUTAÇÃO            levou um ultimate: vira o oponente (aparência, golpes e habilidade dele)
  KING    MAESTRIA DE COMBATE combos mais longos
  CANNAN  COLETE À PROVA DE BALAS  50% menos dano de média e longa distância
  FINN    PODER MÁGICO       fez o combo máximo: fica invisível por 3 segundos
  KUN     ÁS NA MANGA        a cada 15 segundos o ás acende: por 5 segundos, +5 de dano em todo ataque
  XENO    SANGUE ÁCIDO       quem bate nele de perto leva 1 de dano
  TAI     PESO PESADO        120 de vida, soco/chute normal não fazem ele recuar (mas é o mais lento)
  TAMER   ENTENDIMENTO MÚTUO X troca o lobo: BRANCO = +25% de dano, PRETO = ataques 50% mais rápidos
"""

HABILIDADES = {
    "maquinario": dict(nome="MAQUINÁRIO PESADO", desc="25% de vida ou menos: +25% de dano, leva 25% menos"),
    "ninja": dict(nome="POSTURA NINJA", desc="hitbox naturalmente menor"),
    "conexao": dict(nome="CONEXÃO TERRESTRE", desc="agachado: bem menor, bate o dobro e leva 20% menos"),
    "maestria": dict(nome="MAESTRIA DE COMBATE", desc="combos mais longos: 18 golpes em vez de 12"),
    "mutacao": dict(nome="MUTAÇÃO", desc="levou ultimate: vira o oponente e usa os golpes e a habilidade dele"),
    "colete": dict(nome="COLETE À PROVA DE BALAS", desc="leva 50% menos dano de ataques de média e longa distância"),
    "poder_magico": dict(nome="PODER MÁGICO", desc="fez o combo máximo: fica invisível por 3 segundos"),
    "as_na_manga": dict(nome="ÁS NA MANGA", desc="a cada 15 segundos: por 5 segundos, +5 de dano em todo ataque"),
    "sangue_acido": dict(nome="SANGUE ÁCIDO", desc="quem bate nele de perto leva 1 de dano de ácido"),
    "peso_pesado": dict(nome="PESO PESADO", desc="120 de vida e soco/chute normal não fazem ele recuar"),
    "entendimento": dict(nome="ENTENDIMENTO MÚTUO", desc="X troca o lobo: BRANCO = +dano, PRETO = ataques mais rápidos"),
}

MAQUINARIO_VIDA = 0.25
MAQUINARIO_DANO = 1.25
MAQUINARIO_DEFESA = 0.75
NINJA_LARGURA = 0.8
MAESTRIA_MALABAR = 18      # combo no ar: 18 golpes em vez de 12
MAESTRIA_CADEIA = 2        # emenda 2 golpes normais a mais
CONEXAO_AGACHADO = 0.5      # agachado fica com metade da altura
CONEXAO_DANO = 2.0          # soco e chute agachados batem o dobro
CONEXAO_DEFESA = 0.8        # agachado leva 20% menos dano (buff pedido pelo Gomes)
COLETE_DEFESA = 0.5         # ataque de média/longa distância tira metade
COLETE_DISTANCIA = 150      # mais longe que isso (em pixels) já conta como média distância


def ativas(l):
    """As habilidades que o lutador tem agora (a dele + a do oponente, se o Trafo mutou)."""
    hs = []
    for f in (l.f, getattr(l, "mutado", None)):
        if f and f.get("habilidade") and f["habilidade"] not in hs:
            hs.append(f["habilidade"])
    return hs


def ligada(l, h):
    """Se a habilidade está fazendo efeito neste momento (pra acender na tela)."""
    if h == "maquinario":
        return l.vida <= l.vida_max * MAQUINARIO_VIDA
    if h == "mutacao":
        return bool(getattr(l, "mutado", None))
    if h == "as_na_manga":
        return getattr(l, "as_ativo", 0) > 0
    if h == "poder_magico":
        return getattr(l, "invisivel", 0) > 0
    if h == "conexao":
        return l.estado == "agachado" or (l.estado == "ataque" and l.golpe and l.golpe.get("base") == "agachado")
    return True


def mult_causa(l, g):
    """Multiplica o dano que ESSE lutador causa."""
    m = 1.0
    hs = ativas(l)
    if "maquinario" in hs and ligada(l, "maquinario"):
        m *= MAQUINARIO_DANO
    if "conexao" in hs and g and g.get("base") == "agachado" and not g.get("especial"):
        m *= CONEXAO_DANO
    if "entendimento" in hs and l.extra.get("lobo_cor", "branco") == "branco":
        m *= LOBO_DANO  # ENTENDIMENTO MÚTUO: lobo branco = +dano
    return m


LOBO_DANO = 1.25
LOBO_ATAQUE = 1.5   # lobo preto: os ataques andam 1,5x mais rápido (pedido do Gomes: ataque, não movimento)


def mult_vel(l):
    """Quanto mais rápido ele anda (hoje ninguém muda isso)."""
    return 1.0


def mult_ataque(l):
    """Quanto mais rápido os ataques dele rodam (ENTENDIMENTO MÚTUO: lobo preto)."""
    if "entendimento" in ativas(l) and l.extra.get("lobo_cor") == "preto":
        return LOBO_ATAQUE
    return 1.0


def de_longe(l, atacante, g):
    """Golpe de média/longa distância: tiro, laser, bola, ou alguém batendo lá de longe."""
    if not g or g.get("transicao"):
        return False
    if g.get("proj") or g.get("ia") == "longe" or (atacante and atacante.feixe):
        return True
    return bool(atacante) and abs(atacante.x - l.x) > COLETE_DISTANCIA


def mult_recebe(l, atacante=None, g=None):
    """Multiplica o dano que ESSE lutador leva."""
    m = 1.0
    hs = ativas(l)
    if "colete" in hs and atacante is not l and de_longe(l, atacante, g):
        m *= COLETE_DEFESA
    if "maquinario" in hs and ligada(l, "maquinario"):
        m *= MAQUINARIO_DEFESA
    if "conexao" in hs and (l.estado == "agachado" or (l.estado == "defendendo" and l.agachado_def)):
        m *= CONEXAO_DEFESA
    return m


AS_ESPERA = 15 * 60   # quadros até o ás acender
AS_DURA = 5 * 60      # quadros que ele fica aceso
AS_BONUS = 5          # dano a mais em cada ataque


def bonus_causa(l):
    """Dano A MAIS (somado) em cada ataque desse lutador."""
    return AS_BONUS if "as_na_manga" in ativas(l) and ligada(l, "as_na_manga") else 0


def relogio_as(l):
    """Ás na Manga: conta 15 s, acende por 5 s, apaga e conta de novo. Devolve True quando acende."""
    if "as_na_manga" not in ativas(l):
        return False
    if l.as_ativo > 0:
        l.as_ativo -= 1
        return False
    l.as_t += 1
    if l.as_t >= AS_ESPERA:
        l.as_t = 0
        l.as_ativo = AS_DURA
        return True
    return False


ACIDO_DANO = 1
ACIDO_PERTO = 140  # bateu mais perto que isso (golpe de perto, não tiro)


def queima_quem_bate(l, atacante, g):
    """SANGUE ÁCIDO: quem bate nele de perto (sem ser tiro) se queima."""
    if "sangue_acido" not in ativas(l) or not g or g.get("proj"):
        return False
    return abs(atacante.x - l.x) < ACIDO_PERTO


def limite_combo(l, padrao):
    return MAESTRIA_MALABAR if "maestria" in ativas(l) else padrao


def cadeia_extra(l):
    return MAESTRIA_CADEIA if "maestria" in ativas(l) else 0


PESO_LARGURA = 1.3  # o Tai é mais largo (mais fácil de acertar)


def largura(l):
    hs = ativas(l)
    if "ninja" in hs:
        return NINJA_LARGURA
    return PESO_LARGURA if "peso_pesado" in hs else 1.0


def armadura(l, g):
    """PESO PESADO: soco e chute normais (não especiais) tiram vida, mas não fazem ele recuar."""
    return ("peso_pesado" in ativas(l) and g is not None and not g.get("especial") and l.no_chao()
            and l.estado not in ("caido", "voando", "agarrado", "tonto"))


def altura_agachado(l):
    return CONEXAO_AGACHADO if "conexao" in ativas(l) else 1.0
