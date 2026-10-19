"""LOJA NOVA: além das roupas, ENTRADAS, POSES DE VITÓRIA e PROVOCAÇÕES pra comprar (ideia do Gomes).

Cada lutador tem a lista dele em cada categoria (a "ORIGINAL" é sempre a primeira e é de graça).
Um item troca, na ficha do SEU lutador, só os campos que ele tiver:
  ENTRADAS     entrada(l, t, jogo), entrada_efeito(l, tela, t)
  VITÓRIAS     vitoria(l, t, jogo), vitoria_efeito(l, tela, t)
  PROVOCAÇÕES  provocacao (a frase), provocacao_quadros (as poses), provocacao_passo(l, jogo), provocacao_desenho(l, tela)
O computador usa sempre a original. Os itens de cada lutador ficam nos arquivos dele (ou aqui) e entram com registrar().
"""
import save

CATEGORIAS = [("roupas", "ROUPAS"), ("entradas", "ENTRADAS"), ("vitorias", "VITÓRIAS"), ("provocacoes", "PROVOCAÇÕES")]
CAMPOS = {"entradas": ("entrada", "entrada_efeito", "entrada_atras", "entrada_cutscene"),
          "vitorias": ("vitoria", "vitoria_efeito", "vitoria_atras", "vitoria_cutscene"),
          "provocacoes": ("provocacao", "provocacao_quadros", "provocacao_passo", "provocacao_desenho")}
ORIGINAL = dict(id="padrao", nome="ORIGINAL", preco=0)
CATALOGO = {cat: {} for cat in CAMPOS}   # {categoria: {lutador: [itens]}}


def registrar(categoria, lutador, **item):
    """Põe um item na loja: registrar("entradas", "MAX-10", id="paraquedas", nome="...", preco=150, entrada=...)."""
    item.setdefault("preco", 100)
    lista = CATALOGO[categoria].setdefault(lutador, [])
    assert all(i["id"] != item["id"] for i in lista), f"id repetido na loja: {categoria} {lutador} {item['id']}"
    lista.append(item)


def da(categoria, nome):
    return [ORIGINAL] + CATALOGO[categoria].get(nome, [])


def item(categoria, nome, ident):
    return next((i for i in da(categoria, nome) if i["id"] == ident), ORIGINAL)


# ---- save ----
def _comprados(categoria, nome):
    return save.d().setdefault("extras", {}).setdefault(categoria, {}).setdefault(nome, [])


def tem(categoria, nome, ident):
    if ident == "padrao" or ident in _comprados(categoria, nome):
        return True
    it = next((i for i in CATALOGO[categoria].get(nome, []) if i["id"] == ident), None)
    if it and it.get("evento"):  # prêmio do PASSE DO EVENTO (fica pra sempre)
        import passe
        return passe.tem(nome, {"provocacoes": "provocacao"}.get(categoria, categoria), it["evento"].upper())
    return False


def comprar(categoria, nome, ident, preco):
    if tem(categoria, nome, ident):
        return True
    if save.moedas() < preco:
        return False
    save.d()["moedas"] -= preco
    _comprados(categoria, nome).append(ident)
    save.salvar()
    return True


def usando(categoria, nome):
    i = save.d().setdefault("extras_usando", {}).setdefault(categoria, {}).get(nome, "padrao")
    return i if tem(categoria, nome, i) and any(x["id"] == i for x in da(categoria, nome)) else "padrao"


def usar(categoria, nome, ident):
    if tem(categoria, nome, ident):
        save.d().setdefault("extras_usando", {}).setdefault(categoria, {})[nome] = ident
        save.salvar()


def aplicar(ficha, nome, escolhas=None):
    """A ficha com as entradas/vitórias/provocações equipadas (escolhas = {categoria: id}, senão as do save)."""
    novo = dict(ficha)
    for cat, campos in CAMPOS.items():
        ident = (escolhas or {}).get(cat) or usando(cat, nome)
        if ident == "padrao":
            continue
        it = item(cat, nome, ident)
        for c in campos:
            if c in it:
                novo[c] = it[c]
        if cat == "entradas" and "entrada" in it and "entrada_efeito" not in it:
            novo.pop("entrada_efeito", None)  # (a entrada nova não usa o efeito da original)
        if cat == "entradas" and "entrada" in it and "entrada_atras" not in it:
            novo.pop("entrada_atras", None)
        if cat == "vitorias" and "vitoria" in it and "vitoria_atras" not in it:
            novo.pop("vitoria_atras", None)
        for tipo in ("entrada", "vitoria"):  # a CUTSCENE (só as caras têm) e o nome da cena
            if cat == tipo + "s" and tipo in it:
                if f"{tipo}_cutscene" not in it:
                    novo.pop(f"{tipo}_cutscene", None)
                novo[f"{tipo}_nome"] = it["nome"]
        if cat == "vitorias" and "vitoria" in it and "vitoria_efeito" not in it:
            novo.pop("vitoria_efeito", None)
        if cat == "provocacoes":
            for c in ("provocacao_passo", "provocacao_desenho"):
                if c not in it:
                    novo.pop(c, None)
    return novo
