// LAST STAND — música de LUTA do Battle Wish (pro radinho). Composta pelo Gomes no Strudel (strudel.cc):
// a melodia é dele (A, B, a passagem c-e-g-b e a C); as camadas (cordas, cordas martelando, baixo, tambores
// de guerra) foram montadas em volta. O jogo toca pelo musica.py (MUSICAS["last_stand"]): se mudar aqui, mude lá.
setcps(0.4)
stack(
  note(`<
    [e4@3 g4@4 d4 e4@3 g4@4 b4]
    [e4@2 g4@2 d4@2 f4@2 c4@2 c3 d3 e3 f3 g3 a3 b3 c4 ~]
    [g4 g4 ~ g4 ~ g4 ~ g4 f4@2 e4@2 d4@2 b3@2]
    [g3@2 g3@2 a3@2 b3 ~]
    [b4@4 a4@2 g4@2 d5@8]
    [c5@4 b4@2 a4@2 e4@8]
    [a4@4 b4@2 c5@2 d5@4 b4@4]
    [g4@3 e4@3 d4@2 c4@8]
    [c4@3 e4 g4 b4]
    [e3 e3 e4 e3 e3 e4 d4 e4 e3 e3 e4 e3 g4 f4 e4 d4]
    [c3 c3 c4 c3 c3 c4 b3 c4 c3 c3 c4 c3 e4 d4 c4 b3]
    [a2 a2 a3 a2 a2 a3 g3 a3 b2 b2 b3 b2 d4 c4 b3 a3]
    [b3@4 d#4@4 f#4@4 b4@4]
  >`).s("square").lpf(1500).room(0.5).gain(0.45),
  note(`<
    [e3,g3,b3] [c3,e3,g3] [g2,b2,d3] [d3,f#3,a3]
    [g2,b2,d3] [a2,c3,e3] [d3,f#3,a3] [c3,e3,g3]
    [c3,e3,g3]
    [e3,g3,b3] [c3,e3,g3] [a2,c3,e3] [b2,d#3,f#3]
  >`).s("sawtooth").attack(0.3).release(1.2).lpf(1200).room(0.6).gain(0.28),
  note("<[e3*8] [c3*8] [g3*8] [d3*8] ~ ~ ~ ~ ~ [e3*8] [c3*8] [a2*8] [b2*8]>")
    .s("sawtooth").lpf(900).gain(0.22),
  note(`<[e1 e1] [c2 c2] [g1 g1] [d2 d2] [g1 g1] [a1 a1] [d2 d2] [c2 c2]
         [c2@4] [e1*8] [c2*8] [a1*8] [b1*8]>`).s("square").lpf(350).gain(0.45),
  s(`<[bd ~ bd ~ bd bd ~ ~, ~ ~ ~ ~ sd ~ ~ ~]!4
      [bd ~ ~ ~ ~ ~ ~ ~, ~ ~ ~ ~ sd ~ ~ ~]!4
      [sd*8]
      [bd bd bd bd, ~ sd ~ sd, hh*8]!3
      [bd*4, sd*16]>`).bank("RolandTR909").gain(0.8)
)
