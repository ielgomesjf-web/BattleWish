"""Falas antes da luta (na tela de VS), estilo Injustice 2.
Cada dupla tem a sua conversa: [(quem fala, o que fala), ...]."""

CONVERSAS = {
    ("MAX-10", "RIB"): [("MAX-10", "ANALISANDO... ALVO: SAPO. AMEAÇA: BAIXA."),
                        ("RIB", "Ameaça baixa? Seu sensor tá precisando de óleo, lata velha!")],
    ("MAX-10", "TRAFO"): [("TRAFO", "Grrr... você tem cheiro de ferro-velho!"),
                          ("MAX-10", "OBRIGADO. É O MEU PERFUME FAVORITO.")],
    ("KING RIP", "MAX-10"): [("KING RIP", "Na minha época, robô só servia pra lavar louça."),
                             ("MAX-10", "ATUALIZAÇÃO: AGORA EU TAMBÉM LIMPO O CHÃO. COM VOCÊ.")],
    ("CANNAN", "MAX-10"): [("CANNAN", "Já desmontei tanque maior que você, lataria."),
                           ("MAX-10", "MEUS CÁLCULOS DISCORDAM. INICIANDO COMBATE.")],
    ("RIB", "TRAFO"): [("RIB", "Cachorro de seis patas? Agora eu já vi de tudo."),
                       ("TRAFO", "E eu nunca comi sapo... ainda.")],
    ("KING RIP", "RIB"): [("KING RIP", "Um ninja? Mostre o que o seu mestre te ensinou, garoto."),
                          ("RIB", "Meu vô me ensinou a respeitar os mais velhos... mas hoje vai ser difícil!")],
    ("CANNAN", "RIB"): [("CANNAN", "Fica parado, sapo. Assim fica mais fácil mirar."),
                        ("RIB", "Ninja não fica parado. Ninja SOME!")],
    ("KING RIP", "TRAFO"): [("KING RIP", "Senta! Fica! ...Ele não obedece."),
                            ("TRAFO", "AU! Eu só obedeço a minha matilha!")],
    ("CANNAN", "TRAFO"): [("CANNAN", "Na guerra eu tinha um cachorro. Ele tinha quatro patas."),
                          ("TRAFO", "Eu tenho seis. Faz as contas, soldado!")],
    ("FINN", "MAX-10"): [("FINN", "Uma armadura que anda sozinha? Que feitiço é esse?"),
                         ("MAX-10", "NÃO É FEITIÇO. É CIÊNCIA.")],
    ("FINN", "RIB"): [("RIB", "Um velho de chapéu pontudo? Meu vô tinha um igualzinho!"),
                      ("FINN", "Então o seu avô tinha bom gosto, pequeno sapo.")],
    ("FINN", "TRAFO"): [("FINN", "Uma criatura de seis patas... daria um ótimo ingrediente de poção."),
                        ("TRAFO", "Grrr... chega perto que eu te mostro o ingrediente!")],
    ("FINN", "KING RIP"): [("KING RIP", "Barba branca, cajado... você também é dos antigos, hein?"),
                           ("FINN", "Antigo não. CLÁSSICO, meu caro.")],
    ("CANNAN", "FINN"): [("CANNAN", "Magia não segura bala, vovô."),
                         ("FINN", "Você nunca viu uma bala derreter, não é?")],
    ("KUN", "MAX-10"): [("KUN", "Aposto que você não sabe jogar truco, lata velha."),
                        ("MAX-10", "PROBABILIDADE DE VOCÊ VENCER: 2%.")],
    ("KUN", "RIB"): [("RIB", "Cartas? Eu jogo shuriken, que é a mesma coisa só que melhor!"),
                     ("KUN", "Shuriken não sai pela manga, sapinho.")],
    ("KUN", "TRAFO"): [("KUN", "Cachorro bonzinho... quer pegar a carta?"),
                       ("TRAFO", "GRRR! Não me trata que nem cachorro de estimação!")],
    ("KING RIP", "KUN"): [("KING RIP", "Na minha época, carta servia pra jogar com a família."),
                          ("KUN", "E hoje serve pra derrubar velhinho de nunchaku.")],
    ("CANNAN", "KUN"): [("CANNAN", "Carta de baralho contra um canhão? Desiste, garoto."),
                        ("KUN", "Ainda tenho um ás na manga. Literalmente.")],
    ("FINN", "KUN"): [("FINN", "Truques de cartas... isso é magia de criança."),
                      ("KUN", "Pelo menos a minha magia tira um sofá do nada, vovô.")],
    ("MAX-10", "XENOMORPH"): [("MAX-10", "FORMA DE VIDA DESCONHECIDA. NÍVEL DE AMEAÇA: MÁXIMO."),
                              ("XENOMORPH", "Hssssssss...")],
    ("RIB", "XENOMORPH"): [("RIB", "Que bicho é esse?! Por que ele tem DUAS bocas?!"),
                           ("XENOMORPH", "*GRRRK*")],
    ("TRAFO", "XENOMORPH"): [("TRAFO", "Grrr... sai daqui, coisa estranha!"),
                             ("XENOMORPH", "HSSSSSSSS!")],
    ("KING RIP", "XENOMORPH"): [("XENOMORPH", "Hssss..."),
                                ("KING RIP", "Na minha época os monstros ficavam só nos filmes.")],
    ("CANNAN", "XENOMORPH"): [("CANNAN", "Eu já enfrentei um de vocês. Dessa vez eu trouxe o canhão."),
                              ("XENOMORPH", "*KREEEEEE*")],
    ("FINN", "XENOMORPH"): [("FINN", "Criatura das trevas! Volte pro buraco de onde saiu!"),
                            ("XENOMORPH", "Hsssss...")],
    ("KUN", "XENOMORPH"): [("KUN", "Ok... essa carta eu não tinha no baralho."),
                           ("XENOMORPH", "*GRRRK*")],
    ("MAX-10", "TAI"): [("TAI", "Você é pesado, robô. Mas eu sou mais."),
                        ("MAX-10", "CALCULANDO SEU PESO... ERRO: NÚMERO GRANDE DEMAIS.")],
    ("RIB", "TAI"): [("RIB", "Nossa... você é GIGANTE!"),
                     ("TAI", "E você é pequeno o bastante pra caber na minha mão.")],
    ("TAI", "TRAFO"): [("TRAFO", "Seis patas contra duas. Eu ganho no número!"),
                       ("TAI", "No sumô, o que conta é o peso.")],
    ("KING RIP", "TAI"): [("KING RIP", "Na minha época eu também era grandão assim."),
                          ("TAI", "Então hoje o senhor vai lembrar como é ser derrubado.")],
    ("CANNAN", "TAI"): [("CANNAN", "Esse colete aguenta muita coisa... será que aguenta você?"),
                        ("TAI", "Vamos descobrir, soldado.")],
    ("FINN", "TAI"): [("FINN", "Hm... acho que minha levitação não levanta tanto peso."),
                      ("TAI", "Ninguém levanta, velho mago.")],
    ("KUN", "TAI"): [("KUN", "Tenho um armário na carta que pesa menos que você."),
                     ("TAI", "Pode jogar. Eu seguro.")],
    ("TAI", "XENOMORPH"): [("XENOMORPH", "Hssssss..."),
                           ("TAI", "Monstro estranho. Mas no meu ringue, quem empurra sou eu.")],
    ("MAX-10", "TAMER"): [("TAMER", "Já domei bicho mais bravo que um robô."),
                          ("MAX-10", "ANIMAL DETECTADO. ADESTRADOR TAMBÉM.")],
    ("RIB", "TAMER"): [("RIB", "Sai pra lá com esse cachorrão!"),
                       ("TAMER", "É um LOBO. E ele adora sapo.")],
    ("TAMER", "TRAFO"): [("TRAFO", "Grrr... um lobo branco? Ele que é o meu rival!"),
                         ("TAMER", "Calma, garoto. O meu lobo não briga com cachorro de seis patas.")],
    ("KING RIP", "TAMER"): [("KING RIP", "Lutar com ajuda de bicho? Na minha época isso era trapaça."),
                            ("TAMER", "Na selva, isso se chama trabalho em equipe.")],
    ("CANNAN", "TAMER"): [("CANNAN", "Sobreviver na selva? Eu sobrevivi a uma guerra."),
                          ("TAMER", "Então vamos ver quem aguenta mais, soldado.")],
    ("FINN", "TAMER"): [("FINN", "Que lobo magnífico... será que ele aprende uma magia?"),
                        ("TAMER", "Ele já faz mágica: faz gente sumir da arena.")],
    ("KUN", "TAMER"): [("KUN", "Escolhe uma carta, lobinho."),
                       ("TAMER", "Ele só escolhe uma coisa: a sua perna.")],
    ("TAI", "TAMER"): [("TAMER", "Você é grande... mas eu já vi urso maior."),
                       ("TAI", "Urso nenhum sabe sumô.")],
    ("TAMER", "XENOMORPH"): [("TAMER", "Nunca vi esse bicho em nenhum documentário..."),
                             ("XENOMORPH", "Hsssssssss...")],
    ("CANNAN", "KING RIP"): [("KING RIP", "Arma de fogo? Isso é coisa de quem não sabe lutar."),
                             ("CANNAN", "E nunchaku é coisa de quem não sabe mirar, vovô.")],
}

# quando não tem conversa pronta (ou é um personagem novo), cada um fala a sua frase
FRASES = {
    "MAX-10": "COMBATE INICIADO.",
    "RIB": "Pode vir! Eu sou mais rápido que a sua sombra!",
    "TRAFO": "AUUUUUU!",
    "KING RIP": "Vamos ver do que você é feito.",
    "CANNAN": "Missão: vencer. Começando agora.",
    "FINN": "Prepare-se para a minha magia!",
    "KUN": "A sorte já está lançada.",
    "XENOMORPH": "Hssssssss...",
    "TAI": "Hakkeyoi! Vamos lutar!",
    "TAMER": "Fica perto de mim, garoto. Vai ser divertido.",
}


def _base(nome):
    return nome[len("SOMBRA DO "):] if nome.startswith("SOMBRA DO ") else nome


def dialogo(f1, f2):
    """A conversa entre o lutador da esquerda (lado 0) e o da direita (lado 1): [(lado, texto), ...]."""
    n1, n2 = f1["nome"], f2["nome"]
    if f2.get("sombra") or f1.get("sombra"):
        sombra = 1 if f2.get("sombra") else 0
        return [(sombra, "Eu sou tudo aquilo que você tem medo de ser..."),
                (1 - sombra, "Então hoje eu vou vencer o meu medo!")]
    if n1 == n2:
        return [(0, "Ei! Quem deixou você usar a minha cara?"), (1, "Eu ia te perguntar a mesma coisa!")]
    conversa = CONVERSAS.get(tuple(sorted((n1, n2))))
    if conversa:
        return [(0 if quem == n1 else 1, txt) for quem, txt in conversa]
    return [(lado, FRASES.get(_base(n), "Prepare-se!")) for lado, n in ((0, n1), (1, n2))]
