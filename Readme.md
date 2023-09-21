# durakAI
Based on the russian card game: Durak

https://en.wikipedia.org/wiki/Durak

# Digitizing Game
First step was to make a digital version of the game.
Challenging because of the uncommon gameplay flow of Durak.
Classes for players, cards, and deck. Deck deals to the players.
Handles turns by having players go in order taking turns attacking, defending, allows adding to attack of all players.
Handles win conditions and deck running out of cards.
# AI
Initially making an AI for playing only with two players.
Dividing AI into two parts:
Once the deck is out of cards the game has no hidden information; by following which cards have been discarded and which cards are in hand, the agent knows exactly which cards are in the opponents hand.
For this stage, made a Minimax algorithm with Alpha Beta Pruning, it plays 100% optimally.
AI is complete up to this point.
# Midgame
Work in Progress*
In the midgame the information is not known.
Will use probabilities of cards being useful to determine which cards to play.
