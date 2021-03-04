from pokepediaRepository import PokepediaRepository, PokepediaGeneration

pr = PokepediaRepository()
move = pr.searchMoves('fire spin')

# pokemon = pr.searchPokemon('moltres')

print(move.toStr())

for s in move.toStrList():
  print(s)

move = pr.searchMoves('vine whip')

for s in move.toStrList():
  print(s)

move = pr.searchMoves('bite')

for s in move.toStrList():
  print(s)

move = pr.searchMoves('acid')

for s in move.toStrList():
  print(s)
