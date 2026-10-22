// WARRIOR SPIRIT — a música de LUTA do Battle Wish.
// Composta pelo Gomes: nasceu "sem querer" no violão (corda 3 casa 2 / corda 2 casa 1 = a3 c4),
// arrumada no Strudel (strudel.cc). Partes: A (o riff) → B (refrão calmo) → C (agitada, notas repetidas)
// → D (ponte: a bateria para e rufa no fim) → volta pro A.
// O jogo toca esta MESMA música pelo musica.py (MUSICAS["warrior_spirit"]): se mudar aqui, mude lá também.
setcps(0.35)
stack(
  // PIANO: A → B → C → D → volta
  note(`<
    [a3 c4 a3 ~ a3 c4 a3 ~ a3 c4 b3 a3 c4 b3 b4 ~]
    [a3 c4 a3 ~ a3 c4 a3 ~ a3 c4 b3 a3 g3 e3 a3 ~]
    [c4 e4 c4 ~ c4 e4 c4 ~ c4 e4 d4 c4 e4 d4 d5 ~]
    [e4 d4 c4 b3 c4 b3 a3 g3 a3 b3 c4 d4 e4 ~ d4 ~]
    [e4@4 d4@4 c4@4 b3@4]
    [a3@6 c4@2 e4@8]
    [f4@4 e4@4 d4@4 c4@4]
    [b3@6 c4@2 d4@4 e4@4]
    [c3 c3 c3 c3 c3 c3 c3 c3 d3 ~ c3 c2 ~ e3 e2 ~]
    [c3 c3 c3 c3 c3 c3 c3 c3 d3 ~ c3 c2 ~ e3 g3 a3]
    [d3 d3 d3 d3 d3 d3 d3 d3 e3 ~ d3 d2 ~ f3 f2 ~]
    [e3 e3 e3 e3 e3 e3 e3 e3 f3 ~ e3 e2 ~ g#3 b3 ~]
    [f3 a3 c4 a3 f3 a3 c4 a3 f3 a3 c4 a3 f3 a3 c4 e4]
    [g3 b3 d4 b3 g3 b3 d4 b3 g3 b3 d4 b3 g3 b3 d4 f4]
    [a3 c4 e4 c4 a3 c4 e4 c4 a3 c4 e4 a4 c5 a4 e4 c4]
    [e4@4 g#4@4 b4@4 e5@4]
  >`).s("piano").room(0.5).delay(0.2).gain(0.7),
  // ACORDES
  note(`<
    [a2,c3,e3] [f2,a2,c3] [c3,e3,g3] [g2,b2,d3]
    [c3,e3,g3] [a2,c3,e3] [f2,a2,c3] [e2,g#2,b2]
    [c3,e3,g3] [c3,e3,g3] [d3,f3,a3] [e2,g#2,b2]
    [f2,a2,c3] [g2,b2,d3] [a2,c3,e3] [e2,g#2,b2]
  >`).s("sawtooth").lpf(700).attack(0.3).release(1).gain(0.22),
  // BAIXO
  note("<a1 f1 c2 g1 c2 a1 f1 e1 c2 c2 d2 e1 f1 g1 a1 e1>*4").s("square").lpf(400).gain(0.4),
  // BATERIA (mais forte na parte C, para na ponte e rufa no fim)
  s("<[bd ~ ~ bd, ~ sd, hh*8]!8 [bd bd ~ bd, ~ sd ~ sd, hh*16]!4 ~ ~ [sd*4] [sd*8, bd*4]>")
    .bank("RolandTR909").gain(0.7)
)
