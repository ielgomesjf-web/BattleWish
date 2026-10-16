<p align="center"><img src="battlewish_icone.png" width="128" alt="Battle Wish"></p>

<h1 align="center">BATTLE WISH</h1>

<p align="center">Um jogo de luta 2D estilo Street Fighter, com personagens próprios, pixel art, combos, ultimates e online com os amigos.</p>

<p align="center"><b><a href="https://github.com/ielgomesjf-web/BattleWish/releases/latest">⬇️ Baixar o jogo (Windows)</a></b></p>

![Tamer contra o Xenomorph na Selva](imagens/luta1.png)

## Como baixar e jogar

1. Entre em **[Releases](https://github.com/ielgomesjf-web/BattleWish/releases/latest)** e baixe o **`BattleWish.exe`**.
   É o jogo direto, sem instalar: é só abrir e jogar.
2. Na primeira vez, o Windows pode mostrar **"O Windows protegeu o computador"**. Isso acontece com qualquer jogo
   feito em casa (o arquivo não tem assinatura digital paga). Clique em **"Mais informações"** e depois em
   **"Executar assim mesmo"**.

Funciona no Windows 10 e 11. O save (moedas, roupas, recordes) fica num arquivo `battlewish_save.json` do lado do jogo.

## Os lutadores

| | |
|---|---|
| **MAX-10** | o robô: laser dos olhos, agarrão e metralhadora de socos |
| **RIB** | o sapo ninja: shurikens, corrida ninja, linguada e o KAGE BUNSHIN (clones jogando shuriken) |
| **TRAFO** | o cachorro mutante de seis patas: linguão que paralisa, braços que saem da terra e metralhadora de olhos |
| **KING RIP** | o mestre do nunchaku: nunchaku bumerangue, giratório e salto com nunchaku |
| **CANNAN** | o soldado: pistola, canhão de perto, corrida maluca e o FOGO TOTAL |
| **FINN** | o mago: bola de fogo, levitação, cajado e o MINI SOL (e fica invisível no combo) |
| **KUN** | o jogador de cartas: cartas, carta-espada, teleporte, e o Ás na Manga deixa os golpes mais fortes |
| **XENOMORPH** | o alien: cuspe de ácido, rabada, garras, rasteja e tem sangue ácido |
| **TAI** | o lutador de sumô: pisão que faz onda no chão, tapas, investida e muita armadura |
| **TAMER** | o explorador com o lobo: o lobo branco bate mais forte e o preto deixa os ataques mais rápidos |

Cada um tem 4 especiais, uma ULTIMATE, uma habilidade própria, entrada, pose de vitória e roupas pra comprar na loja.
E tem segredo escondido na tela de **CÓDIGOS**...

![A tela de seleção](imagens/selecao.png)

## Os modos

- **1 JOGADOR**: você contra o computador (fácil, médio ou difícil).
- **2 JOGADORES**: dois no mesmo PC (o segundo precisa de um controle).
- **TRIO**: 3 contra 3, trocando de lutador no meio da luta.
- **TORNEIO**: chave de 8 lutadores até a final. As lutas dos computadores dá pra assistir ou pular.
- **ONLINE**: contra um amigo em outra casa, sem precisar de VPN. Quem cria a sala escolhe o modo:
  1 contra 1, trio ou torneio (vocês 2 + 6 computadores), e pode ligar os modos malucos.
  Os dois precisam estar com a **mesma versão** do jogo.
- **SOBREVIVÊNCIA**: um adversário atrás do outro até cair.
- **MODOS MALUCOS**: gravidade da lua, cabeções, turbo, só ultimate e um golpe mata.
- **MODO TREINO** e **COMBOS**: pra aprender os golpes e os desafios de combo de cada lutador.
- **LOJA** e **DESAFIOS**: roupas novas com as moedas que você ganha lutando.

![Torneio](imagens/torneio.png)

## Controles

Dá pra jogar no **teclado e mouse** ou no **controle de Xbox** (com fio ou bluetooth). A tela **COMO JOGAR** dentro
do jogo mostra tudo.

| Teclado e mouse | Controle | O que faz |
|---|---|---|
| A / D | direcional | andar (segurar pra trás defende) |
| W / S | cima / baixo | pular / agachar |
| botão esquerdo | A | soco |
| botão direito | B | chute |
| segura a rodinha + E, Q, R ou SHIFT | X, Y, LB, RB | os 4 especiais |
| segura a rodinha + Z | RT | ULTIMATE (com a barra cheia) |
| rodinha 2x + especial | LT + especial | especial EX (gasta barra) |
| rodinha 2x apanhando | LT apanhando | ESCAPE de combo |
| T | BACK | provocar |
| G | R3 | trocar de lutador (TRIO) |
| ESC | START | pausa |
| F11 | | tela cheia |

![Rib contra o MAX-10 no Pântano](imagens/luta2.png)

## Rodar pelo código

Precisa do Python 3.12 com `pygame` e `numpy`:

```
pip install pygame numpy
python luta.py
```

Os testes: `python teste.py`. Pra gerar o `.exe`: `pip install pyinstaller` e rodar o `gerar_exe.bat`
(o jogo fica na pasta `dist`).

---

Feito pelo Gomes, em Python + Pygame.
