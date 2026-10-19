"""MISSÕES DO DIA (v2.0, pedido do Gomes): 3 missões por dia, sorteadas pela data (todo mundo que jogar no mesmo
dia tem as mesmas). No dia seguinte vêm outras. Cada uma dá moedas + XP de MAESTRIA pro lutador que cumpriu.

Fica no save: save.d()["missoes"] = {"dia": "2026-10-16", "lista": [missão, ...], "feitas_total": n}.
Conta nas mesmas lutas das ESTATÍSTICAS (estatisticas.conta): o jogador do lado esquerdo, sem treino.
O sorteio usa um random só dele (random.Random(dia)): não mexe no random da luta (importante pro ONLINE).
"""
import datetime
import random

import save

POR_DIA = 3

# tipo: (texto, alvos possíveis, moedas, xp de maestria, precisa de: "p" lutador / "c" cenário)
TIPOS = {
    "sem_pular": ("Ganhe com o {p} sem pular", (1,), 60, 80, "p"),
    "choques": ("Vença {alvo} CHOQUE{s}", (1, 2), 50, 60, ""),
    "vencer_com": ("Vença {alvo} luta{s} com o {p}", (2, 3), 50, 70, "p"),
    "combo": ("Faça um combo de {alvo} golpes", (8, 10, 12), 40, 50, ""),
    "ults": ("Acerte a ULTIMATE {alvo} vezes", (2, 3), 40, 50, ""),
    "objetos": ("Use objetos do cenário {alvo} vezes", (2, 3), 40, 50, ""),
    "parrys": ("Faça {alvo} PARRYS", (3, 5), 40, 50, ""),
    "cenario": ("Vença uma luta no cenário {c}", (1,), 40, 50, "c"),
    "perfect": ("Vença uma luta com PERFECT", (1,), 60, 80, ""),
    "trio": ("Vença {alvo} luta{s} no TRIO", (1, 2), 50, 60, ""),
    "maluco": ("Vença com um MODO MALUCO ligado", (1,), 40, 50, ""),
    "quebras": ("Quebre a guarda {alvo} vezes", (2, 3), 40, 50, ""),
    "golpes": ("Acerte {alvo} golpes", (60, 100), 30, 40, ""),
    "por_um_fio": ("Vença com 20 de vida ou menos", (1,), 50, 60, ""),
    "sem_ult": ("Vença sem usar a ULTIMATE", (1,), 40, 50, ""),
    "transicao": ("Jogue o adversário pra outro cenário", (1,), 40, 50, ""),
    "rival": ("Vença o RIVAL do seu lutador", (1,), 60, 80, ""),
    "ult2": ("Acerte a 2ª ULTIMATE", (1,), 80, 100, ""),
}
CENARIOS = ("TEMPLO", "PÂNTANO", "FERRO-VELHO", "TOCA", "DOJO", "CAMPO DE BATALHA", "TORRE DO MAGO", "CASSINO",
            "LABORATÓRIO", "ARENA DE SUMÔ", "SELVA", "TEATRO DE MÁGICA")


def _dia(dia=None):
    return (dia or datetime.date.today()).isoformat()


def sortear(dia=None):
    """As 3 missões de um dia (sempre as mesmas pra mesma data)."""
    from personagens import PERSONAGENS
    d = dia or datetime.date.today()
    rng = random.Random(d.toordinal() * 7919 + 2026)
    lista = []
    import estatisticas  # (a missão da 2ª ULTIMATE só entra quando o jogo já conta "ults2": nunca sai impossível)
    tipos = [t for t in sorted(TIPOS) if t != "ult2" or "ults2" in getattr(estatisticas, "GERAL", ())]
    for tipo in rng.sample(tipos, POR_DIA):
        _, alvos, moedas, xp, precisa = TIPOS[tipo]
        i = rng.randrange(len(alvos))
        m = dict(tipo=tipo, alvo=alvos[i], prog=0, moedas=moedas + 10 * i, xp=xp + 15 * i, feita=False)
        if precisa == "p":
            m["p"] = rng.choice(PERSONAGENS)["nome"]
        if precisa == "c":
            import cenarios  # (só os que existem no jogo: nunca sorteia missão impossível)
            m["c"] = rng.choice([c for c in CENARIOS if c in cenarios.CENARIOS])
        lista.append(m)
    return lista


def _estado(dia=None):
    """O que está no save; troca pelas missões de hoje se virou o dia (ou se o save estiver estragado)."""
    s = save.d().get("missoes")
    if not isinstance(s, dict):
        s = {}
    hoje_txt = _dia(dia)
    lista = s.get("lista")
    if s.get("dia") != hoje_txt or not isinstance(lista, list) or len(lista) != POR_DIA \
            or not all(isinstance(m, dict) and m.get("tipo") in TIPOS for m in lista):
        s = {"dia": hoje_txt, "lista": sortear(dia), "feitas_total": s.get("feitas_total", 0)}
        save.d()["missoes"] = s
        save.salvar()
    return s


def texto_de(m):
    return TIPOS[m["tipo"]][0].format(alvo=m["alvo"], p=m.get("p", ""), c=m.get("c", ""),
                                      s="s" if m["alvo"] > 1 else "")


def hoje(dia=None):
    """As missões de hoje, pra tela: [{texto, prog, alvo, moedas, xp, feita}]."""
    return [dict(texto=texto_de(m), prog=min(m["prog"], m["alvo"]), alvo=m["alvo"], moedas=m["moedas"],
                 xp=m["xp"], feita=m["feita"]) for m in _estado(dia)["lista"]]


def feitas_total():
    """Quantas missões do dia o jogador já cumpriu (somando todos os dias): pro troféu."""
    s = save.d().get("missoes")
    return s.get("feitas_total", 0) if isinstance(s, dict) else 0


def _andar(m, r):
    """Quanto a missão andou com essa luta (r = partida.resumo()). Combo é o maior da luta; o resto soma."""
    t, venceu = m["tipo"], bool(r["venceu"])
    if t == "sem_pular":
        return int(venceu and r["personagem"] == m["p"] and r.get("pulos", 0) == 0)
    if t == "choques":
        return r.get("choques", 0)
    if t == "vencer_com":
        return int(venceu and r["personagem"] == m["p"])
    if t == "combo":
        return m["alvo"] if r.get("combo", 0) >= m["alvo"] else 0
    if t in ("ults", "objetos", "parrys", "quebras", "golpes"):
        return r.get(t, 0)
    if t == "cenario":
        return int(venceu and r.get("cenario") == m["c"])
    if t == "perfect":
        return int(venceu and r.get("perfects", 0) > 0)
    if t == "trio":
        return int(venceu and r.get("modo") == "trio")
    if t == "maluco":
        return int(venceu and bool(r.get("regras")))
    if t == "por_um_fio":
        return int(venceu and r.get("vida", 999) <= 20)
    if t == "sem_ult":
        return int(venceu and r.get("ults", 0) == 0)
    if t == "transicao":
        return r.get("transicoes", 0)
    if t == "ult2":
        return r.get("ults2", 0)
    if t == "rival":
        import rivais
        return int(venceu and rivais.sao_rivais(r["personagem"], r.get("adversario", "")))
    return 0


def avancar(partida, dia=None):
    """Fim de luta: anda as missões, paga as que acabaram de ser cumpridas (moedas + XP de maestria no lutador
    usado) e salva. Devolve [(texto, moedas, xp)] das cumpridas agora."""
    import estatisticas
    if not estatisticas.conta(partida):
        return []
    return avancar_resumo(partida.resumo(), dia)


def avancar_resumo(r, dia=None):
    """(O mesmo, a partir do resumo: separado pra dar pra testar.)"""
    import maestria
    s = _estado(dia)
    cumpridas = []
    for m in s["lista"]:
        if m["feita"]:
            continue
        m["prog"] = min(m["alvo"], m["prog"] + _andar(m, r))
        if m["prog"] >= m["alvo"]:
            m["feita"] = True
            s["feitas_total"] = s.get("feitas_total", 0) + 1
            cumpridas.append((texto_de(m), m["moedas"], m["xp"]))
            save.ganhar(m["moedas"])
            maestria.ganhar(r["personagem"], m["xp"])  # (já salva)
    save.salvar()
    return cumpridas
