// BEFORE THE BATTLE — a música do MENU do Battle Wish.
// Composta pelo Gomes no Strudel (strudel.cc): o tema da Warrior Spirit DEVAGAR e calmo, com um SEGUNDO PIANO
// (ideia dele) fazendo um arpejo constante por baixo, acordes suaves, a caixinha de música e o baixo.
// O jogo toca esta MESMA música pelo musica.py (MUSICAS["before_the_battle"]): se mudar aqui, mude lá também.
setcps(0.22)
stack(
  // PIANO PRINCIPAL: o riff da Warrior Spirit devagar + a parte calma
  note(`<
    [a3 c4 a3 c4 a3 c4 b3 ~]
    [a3 c4 a3 c4 g3 e3 a3 ~]
    [c4 e4 c4 e4 c4 e4 d4 ~]
    [e4 d4 c4 b3 a3@3 ~]
    [e4@2 d4@2 c4@2 b3@2]
    [a3@3 c4 e4@4]
    [f4@2 e4@2 d4@2 c4@2]
    [b3@3 c4 d4@2 e4@2]
  >`).s("piano").room(0.8).delay(0.3).gain(0.6),
  // SEGUNDO PIANO: arpejo constante (o acorde de cada compasso desmanchado)
  note(`<
    [a4 e5 a5 e5 c5 e5 a5 e5]
    [f4 c5 f5 c5 a4 c5 f5 c5]
    [c5 g5 c6 g5 e5 g5 c6 g5]
    [g4 d5 g5 d5 b4 d5 g5 d5]
    [c5 g5 c6 g5 e5 g5 c6 g5]
    [a4 e5 a5 e5 c5 e5 a5 e5]
    [f4 c5 f5 c5 a4 c5 f5 c5]
    [e4 b4 e5 b4 g#4 b4 e5 b4]
  >`).s("piano").room(0.7).delay(0.2).gain(0.5).pan(0.7),
  // FUNDO: acordes longos e suaves
  note(`<[a2,e3,a3] [f2,c3,a3] [c3,g3,e4] [g2,d3,b3]
         [c3,g3,e4] [a2,e3,c4] [f2,c3,a3] [e2,b2,g#3]>`)
    .s("triangle").attack(1).release(2).lpf(900).room(0.6).gain(0.25),
  // CAIXINHA DE MÚSICA
  note("<~ [~ e5 ~ a5] ~ [~ c6 ~ b5] ~ [~ e5 ~ c6] ~ [~ b5 ~ g#5]>")
    .s("sine").room(0.9).delay(0.4).gain(0.2),
  // BAIXO
  note("<a1 f1 c2 g1 c2 a1 f1 e1>").s("sine").gain(0.35)
)
