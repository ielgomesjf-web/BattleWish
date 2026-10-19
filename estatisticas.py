"""ESTATÍSTICAS (v2.0): tudo que o jogador já fez, somado luta a luta (fica no save, pro PERFIL e os TROFÉUS).
Conta só as lutas em que o jogador é o lado da esquerda (1 jogador, 2 jogadores, trio, torneio, sobrevivência;
no online, só quando ele criou a sala). Treino, combos e lutas de computador assistidas não contam."""
import save

POR_PERSONAGEM = ("lutas", "vitorias", "perfects", "maior_combo", "ults", "parrys", "choques")
GERAL = ("lutas", "vitorias", "derrotas", "perfects", "maior_combo", "ults", "ults2", "parrys", "quebras", "choques", "pulos",
         "objetos", "transicoes", "provocacoes", "golpes", "quadros")


def dados():
    """As estatísticas (sempre com todas as chaves, mesmo num save velho):
    {"geral": {lutas, vitorias, ...}, "personagens": {nome: {lutas, vitorias, ...}}, "golpes": {nome_do_golpe: vezes}}"""
    d = save.d().setdefault("estatisticas", {})
    if not isinstance(d, dict):
        d = save.d()["estatisticas"] = {}
    g = d.setdefault("geral", {})
    for k in GERAL:
        g.setdefault(k, 0)
    d.setdefault("personagens", {})
    d.setdefault("golpes", {})
    return d


def personagem(nome):
    p = dados()["personagens"].setdefault(nome, {})
    for k in POR_PERSONAGEM:
        p.setdefault(k, 0)
    return p


def conta(partida):
    """Essa luta conta pras estatísticas?"""
    if partida.treino or getattr(partida, "assistindo", False) or partida.vencedor is None:
        return False
    return 0 in partida.lados_humanos()


def registrar(partida):
    """Soma a luta que acabou de terminar. Devolve o resumo usado (ou None se não contou)."""
    if not conta(partida):
        return None
    r = partida.resumo()
    d = dados()
    g = d["geral"]
    venceu = bool(r["venceu"])
    g["lutas"] += 1
    g["vitorias"] += venceu
    g["derrotas"] += not venceu and partida.vencedor != "empate"
    g["perfects"] += partida.perfects
    g["maior_combo"] = max(g["maior_combo"], r["combo"])
    for k in ("ults", "ults2", "parrys", "quebras", "choques", "pulos", "objetos", "transicoes", "provocacoes", "golpes"):
        g[k] += r.get(k, 0)
    g["quadros"] += partida.t_total
    nomes = [m.f.get("nome_base", m.f["nome"]) for m in partida.equipes[0]] if partida.trio else [r["personagem"]]
    for nome in nomes:
        p = personagem(nome)
        p["lutas"] += 1
        p["vitorias"] += venceu
        p["perfects"] += partida.perfects
        p["maior_combo"] = max(p["maior_combo"], r["combo"])
        p["ults"] += r.get("ults", 0)
        p["parrys"] += r.get("parrys", 0)
        p["choques"] += r.get("choques", 0)
    for golpe, n in r.get("por_golpe", {}).items():
        d["golpes"][golpe] = d["golpes"].get(golpe, 0) + n
    save.salvar()
    return r


def golpe_favorito():
    """(nome do golpe, vezes) do golpe que mais acertou, ou None."""
    gs = dados()["golpes"]
    return max(gs.items(), key=lambda kv: kv[1]) if gs else None


def personagem_favorito():
    """(nome, lutas) de quem mais lutou, ou None."""
    ps = dados()["personagens"]
    return max(((n, p.get("lutas", 0)) for n, p in ps.items()), key=lambda kv: kv[1]) if ps else None
