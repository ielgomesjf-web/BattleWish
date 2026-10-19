"""MODO ONLINE: você no seu PC e o seu amigo no dele, sem precisar de VPN.

Como funciona (igual o Mal-mal!, o UNO online do Gomes):
  1. Quem cria a sala ganha um CÓDIGO de 4 letras. Quem entra digita o código.
  2. Um servidor grátis (ntfy.sh) só APRESENTA um PC pro outro: cada um conta o seu endereço na internet
     (descoberto perguntando pro servidor STUN do Google).
  3. Os dois "batem na porta" um do outro ao mesmo tempo (UDP) até a conexão direta abrir.
  4. Na luta, cada PC manda só os BOTÕES que apertou em cada quadro. Os dois rodam a mesma luta ao mesmo tempo
     (com um atrasinho de uns quadros), e o sorteio de tudo é igual nos dois (mesma semente).
Limite: algumas redes (principalmente 4G) bloqueiam a conexão direta.
"""
import json
import os
import random
import socket
import string
import struct
import threading
import time
import urllib.request

from config import VERSAO
from lutador import Entrada

NTFY = "https://ntfy.sh/"
LOBBY = "battlewish-salas"   # a lista de salas abertas (PROCURAR PARTIDA)
STUN = [("stun.l.google.com", 19302), ("stun1.l.google.com", 19302)]
MAGICO = b"BW1"
ATRASO = 4                # quadros de atraso dos botões (deixa o jogo liso mesmo com a internet oscilando)
TEMPO_PROCURA = 25.0      # segundos tentando achar o outro
TEMPO_QUEDA = 6.0         # segundos sem notícia = o outro caiu
ESPECIAIS_COD = [None, "E", "Q", "R", "SHIFT", "Z", "Z2"]


def novo_codigo():
    return "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=4))  # (sem I e O, que confundem com 1 e 0)


# =====================================================================
# Botões <-> número (2 bytes por quadro)
# =====================================================================
def codifica(e):
    n = e.dir & 15
    n |= bool(e.soco) << 4
    n |= bool(e.chute) << 5
    n |= bool(getattr(e, "segura_ult", False)) << 6
    n |= bool(getattr(e, "provoca", False)) << 7
    n |= ESPECIAIS_COD.index(e.especial if e.especial in ESPECIAIS_COD else None) << 8
    n |= bool(getattr(e, "barra", False)) << 11
    n |= bool(getattr(e, "barra_toque", False)) << 12
    n |= bool(getattr(e, "troca", False)) << 13
    n |= bool(getattr(e, "lobo", False)) << 14
    return n


def decodifica(n):
    e = Entrada(n & 15 or 5, bool(n & 16), bool(n & 32), ESPECIAIS_COD[(n >> 8) & 7] if (n >> 8) & 7 < len(ESPECIAIS_COD) else None)
    e.segura_ult = bool(n & 64)
    e.provoca = bool(n & 128)
    e.barra = bool(n & 2048)
    e.barra_toque = bool(n & 4096)
    e.troca = bool(n & 8192)
    e.lobo = bool(n & 16384)
    return e


NEUTRO = codifica(Entrada())


# =====================================================================
# Descobrir endereços (STUN) e conversar pelo ntfy
# =====================================================================
def stun(sock):
    """Pergunta pro servidor STUN qual é o nosso endereço visto da internet."""
    for host in STUN:
        try:
            tid = os.urandom(12)
            sock.sendto(struct.pack("!HHI", 1, 0, 0x2112A442) + tid, host)
            fim = time.time() + 2
            while time.time() < fim:
                sock.settimeout(max(0.05, fim - time.time()))
                data, _ = sock.recvfrom(2048)
                if len(data) < 20 or data[8:20] != tid:
                    continue
                i = 20
                while i + 4 <= len(data):
                    tipo, tam = struct.unpack("!HH", data[i:i + 4])
                    v = data[i + 4:i + 4 + tam]
                    if tipo in (0x0020, 0x8020) and len(v) >= 8:  # XOR-MAPPED-ADDRESS
                        porta = struct.unpack("!H", v[2:4])[0] ^ 0x2112
                        ip = socket.inet_ntoa(bytes(a ^ b for a, b in zip(v[4:8], b"\x21\x12\xa4\x42")))
                        return ip, porta
                    if tipo == 0x0001 and len(v) >= 8:  # MAPPED-ADDRESS (servidor antigo)
                        return socket.inet_ntoa(v[4:8]), struct.unpack("!H", v[2:4])[0]
                    i += 4 + tam + (-tam % 4)
        except OSError:
            continue
    return None


def enderecos_locais(porta):
    ips = {"127.0.0.1"}
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            ips.add(ip)
    except OSError:
        pass
    try:  # o IP da rede de casa (o "caminho" pra internet)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return [[ip, porta] for ip in sorted(ips)]


def publica(topico, dados):
    req = urllib.request.Request(NTFY + topico, data=json.dumps(dados).encode(), method="POST")
    urllib.request.urlopen(req, timeout=8).read()


def le(topico, desde):
    """Mensagens do tópico desde 'desde' (segundos). Devolve [(tempo, dados), ...]."""
    url = f"{NTFY}{topico}/json?poll=1&since={int(desde)}"
    texto = urllib.request.urlopen(url, timeout=8).read().decode()
    msgs = []
    for linha in texto.splitlines():
        try:
            m = json.loads(linha)
            if m.get("event") == "message":
                msgs.append((m.get("time", 0), json.loads(m.get("message", "{}"))))
        except ValueError:
            continue
    return msgs


# =====================================================================
# A conexão
# =====================================================================
class Conexao:
    """Liga com o outro jogador. estado: 'procurando' -> 'conectado' (ou 'erro')."""

    def __init__(self, hospedar, codigo=None, pares_diretos=None):
        self.hospedar = hospedar
        self.codigo = codigo or novo_codigo()
        self.estado = "procurando"
        self.status = "abrindo a conexão..."
        self.erro = None
        self.par = None
        self.nonce = os.urandom(6).hex()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 0))
        self.ultimo_receb = time.time()
        self.fila = []                  # pacotes que chegaram (depois de conectado)
        # mensagens confiáveis (chegam sempre e em ordem)
        self.seq_env = 0
        self.pendentes = {}             # seq -> (dados, quando mandou)
        self.seq_rec = 0
        self.guardadas = {}
        self.mensagens = []
        self.ping = 0.0
        self._ping_t = 0
        self.pares_diretos = pares_diretos  # (testes: endereços já conhecidos, sem ntfy)
        threading.Thread(target=self._procurar, daemon=True).start()

    @property
    def topico(self):
        return "battlewish-sala-" + self.codigo

    # ---- achando o outro ----
    def _procurar(self):
        try:
            porta = self.sock.getsockname()[1]
            meus = enderecos_locais(porta)
            if self.pares_diretos is None:
                self.status = "descobrindo o seu endereço na internet..."
                publico = stun(self.sock)
                if publico:
                    meus.insert(0, list(publico))
                inicio = time.time() - 5
                if self.hospedar:
                    self.status = "esperando o amigo entrar..."
                    pares = self._esperar_convidado(meus, inicio)
                else:
                    self.status = "procurando a sala..."
                    pares = self._entrar(meus, inicio)
            else:  # (testes) os endereços do outro vêm direto, sem ntfy
                pares = self.pares_diretos
                fim = time.time() + 5
                while callable(pares):
                    pares = self.pares_diretos() or (None if time.time() > fim else pares)
                    time.sleep(0.02)
            if pares is None:
                return
            self.status = "conectando direto com o amigo..."
            self._bater_na_porta(pares)
        except Exception as e:  # sem internet, servidor fora do ar...
            self.estado, self.erro = "erro", f"deu erro na conexão ({type(e).__name__})"

    def _esperar_convidado(self, meus, inicio):
        fim = time.time() + 600  # a sala fica aberta 10 minutos
        avisou = 0
        recusados = set()
        while time.time() < fim and self.estado == "procurando":
            if time.time() - avisou > 8:  # aparece no PROCURAR PARTIDA
                avisou = time.time()
                try:
                    publica(LOBBY, {"tipo": "sala", "codigo": self.codigo, "versao": VERSAO})
                except OSError:
                    pass
            for _, m in le(self.topico, inicio):
                if m.get("tipo") != "oi" or m.get("nonce") == self.nonce or m.get("nonce") in recusados:
                    continue
                if m.get("versao") != VERSAO:  # jogo de versão diferente: não dá pra lutar junto
                    recusados.add(m.get("nonce"))
                    publica(self.topico, {"tipo": "ola", "para": m["nonce"], "erro": "versao", "versao": VERSAO})
                    continue
                publica(self.topico, {"tipo": "ola", "para": m["nonce"], "nonce": self.nonce, "addrs": meus})
                try:
                    publica(LOBBY, {"tipo": "fechou", "codigo": self.codigo})
                except OSError:
                    pass
                return [tuple(a) for a in m.get("addrs", [])]
            time.sleep(1.0)
        self.estado, self.erro = "erro", "ninguém entrou na sala"
        return None

    def _entrar(self, meus, inicio):
        publica(self.topico, {"tipo": "oi", "nonce": self.nonce, "addrs": meus, "versao": VERSAO})
        fim = time.time() + TEMPO_PROCURA
        while time.time() < fim and self.estado == "procurando":
            time.sleep(1.0)
            for _, m in le(self.topico, inicio):
                if m.get("tipo") == "ola" and m.get("para") == self.nonce:
                    if m.get("erro") == "versao":
                        self.estado = "erro"
                        self.erro = f"o jogo do seu amigo é de outra versão ({m.get('versao')}, o seu é {VERSAO})"
                        return None
                    return [tuple(a) for a in m.get("addrs", [])]
        self.estado, self.erro = "erro", "não achei essa sala (confere o código)"
        return None

    def _bater_na_porta(self, pares):
        """UDP hole punching: os dois mandam 'oi' pros endereços um do outro até alguém responder."""
        pacote = MAGICO + b"P" + self.nonce.encode()
        fim = time.time() + 12
        achou = None
        self.sock.settimeout(0.1)
        while time.time() < fim and not achou:
            for a in pares:
                try:
                    self.sock.sendto(pacote, a)
                except OSError:
                    pass
            t = time.time() + 0.2
            while time.time() < t:
                try:
                    data, addr = self.sock.recvfrom(2048)
                except (socket.timeout, OSError):
                    continue
                if data.startswith(MAGICO + b"P") and data[4:].decode(errors="ignore") != self.nonce:
                    achou = addr
                    break
        if not achou:
            self.estado, self.erro = "erro", "a rede bloqueou a conexão direta :("
            return
        for _ in range(5):  # avisa o outro que deu certo
            self.sock.sendto(pacote, achou)
        self.par = achou
        self.sock.setblocking(False)
        self.ultimo_receb = time.time()
        self.estado = "conectado"
        self.status = "conectado!"

    # ---- depois de conectado ----
    def enviar(self, dados):
        if self.par:
            try:
                self.sock.sendto(dados, self.par)
            except OSError:
                pass

    def mandar(self, msg):
        """Mensagem que chega com certeza (e em ordem)."""
        self.seq_env += 1
        dados = MAGICO + b"M" + struct.pack("!I", self.seq_env) + json.dumps(msg).encode()
        self.pendentes[self.seq_env] = [dados, 0.0]

    def bombear(self):
        """Lê tudo que chegou, confirma as mensagens e reenvia as que não foram confirmadas."""
        if self.estado != "conectado":
            return
        agora = time.time()
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
            except (BlockingIOError, OSError):
                break
            if addr != self.par or not data.startswith(MAGICO) or len(data) < 4:
                continue
            self.ultimo_receb = agora
            tipo = data[3:4]
            if tipo == b"M":
                seq = struct.unpack("!I", data[4:8])[0]
                self.enviar(MAGICO + b"A" + data[4:8])
                if seq >= self.seq_rec + 1 and seq not in self.guardadas:
                    self.guardadas[seq] = json.loads(data[8:].decode())
                while self.seq_rec + 1 in self.guardadas:
                    self.seq_rec += 1
                    self.mensagens.append(self.guardadas.pop(self.seq_rec))
            elif tipo == b"A":
                self.pendentes.pop(struct.unpack("!I", data[4:8])[0], None)
            elif tipo == b"K":
                self.enviar(MAGICO + b"k" + data[4:])
            elif tipo == b"k":
                self.ping = (agora - struct.unpack("!d", data[4:12])[0]) * 1000
            else:
                self.fila.append(data)
        for seq, p in self.pendentes.items():
            if agora - p[1] > 0.15:
                self.enviar(p[0])
                p[1] = agora
        if agora - self._ping_t > 1.0:
            self._ping_t = agora
            self.enviar(MAGICO + b"K" + struct.pack("!d", agora))
        if agora - self.ultimo_receb > TEMPO_QUEDA:
            self.estado, self.erro = "erro", "a conexão com o amigo caiu"

    def pegar_mensagens(self):
        m, self.mensagens = self.mensagens, []
        return m

    def pegar_pacotes(self):
        f, self.fila = self.fila, []
        return f

    def fechar(self):
        try:
            if self.estado == "conectado":
                for _ in range(3):
                    self.enviar(MAGICO + b"M" + struct.pack("!I", self.seq_env + 1) + b'{"t": "tchau"}')
            self.estado = "fechado"
            self.sock.close()
        except OSError:
            pass


# =====================================================================
# Lockstep: os dois só avançam a luta quando têm os botões dos dois
# =====================================================================
def salas_abertas():
    """PROCURAR PARTIDA: as salas abertas agora (da mesma versão). Devolve a lista de códigos."""
    agora = time.time()
    estado = {}
    for t, m in le(LOBBY, agora - 40):
        c = m.get("codigo")
        if not c:
            continue
        if m.get("tipo") == "fechou":
            estado[c] = None
        elif m.get("tipo") == "sala" and m.get("versao") == VERSAO and estado.get(c, 0) is not None:
            estado[c] = max(t, estado.get(c) or 0)
    return [c for c, t in sorted(estado.items(), key=lambda x: -(x[1] or 0)) if t and agora - t < 25]


class Lockstep:
    def __init__(self, con, id_luta=0, atraso=ATRASO):
        self.con = con
        self.id_luta = id_luta     # (pacote de outra luta é ignorado)
        self.atraso = atraso
        self.local = {f: NEUTRO for f in range(atraso)}
        self.remoto = {f: NEUTRO for f in range(atraso)}
        self.prox_local = atraso   # próximo quadro que vai receber o botão local
        self.quadro = 0            # próximo quadro da luta a rodar
        self.remoto_ate = atraso - 1  # até onde chegou tudo do outro (sem buraco)
        self.par_tem = -1          # até onde o outro já confirmou que recebeu
        self.esperando = 0         # quadros parado esperando o outro

    def pode_coletar(self):
        return self.prox_local - self.quadro < self.atraso + 2

    def coletar(self, entrada):
        self.local[self.prox_local] = codifica(entrada)
        self.prox_local += 1
        self.enviar()

    def enviar(self):
        ini = max(self.par_tem + 1, self.prox_local - 60, 0)
        n = self.prox_local - ini
        if n <= 0:
            return
        valores = [self.local[f] for f in range(ini, self.prox_local)]
        self.con.enviar(MAGICO + b"I" + struct.pack(f"!HiIB{n}H", self.id_luta, self.remoto_ate, ini, n, *valores))

    def receber(self):
        for data in self.con.pegar_pacotes():
            if data[3:4] != b"I" or len(data) < 15:
                continue
            id_luta, ack, ini, n = struct.unpack("!HiIB", data[4:15])
            if id_luta != self.id_luta or len(data) < 15 + 2 * n:
                continue
            valores = struct.unpack(f"!{n}H", data[15:15 + 2 * n])
            self.par_tem = max(self.par_tem, ack)
            for k, v in enumerate(valores):
                self.remoto.setdefault(ini + k, v)
            while self.remoto_ate + 1 in self.remoto:
                self.remoto_ate += 1
        for f in [f for f in self.local if f < self.quadro - 120]:  # limpa o velho
            del self.local[f]
        for f in [f for f in self.remoto if f < self.quadro - 120]:
            del self.remoto[f]

    def pode_avancar(self):
        return self.quadro in self.local and self.quadro <= self.remoto_ate

    def avancar(self):
        """Os botões (local, remoto) do próximo quadro da luta."""
        f = self.quadro
        self.quadro += 1
        self.esperando = 0
        return decodifica(self.local[f]), decodifica(self.remoto[f])


class ControleRede:
    """O controle de um lutador na luta online: devolve os botões que o lockstep mandou pra esse quadro."""

    def __init__(self):
        self.atual = Entrada()

    def ler(self, bruto, eu, ele, jogo):
        return self.atual


def conferencia(partida):
    """Um número que resume a luta (pra ver se os dois PCs estão vendo a mesma coisa)."""
    v = 0
    for l in partida.L:
        v += int(l.x * 10) * 7 + int(l.y * 10) * 13 + int(l.vida * 100) * 17 + int(l.barra) * 3 + len(l.estado)
    return v + len(partida.projeteis) * 101 + partida.round * 1009
