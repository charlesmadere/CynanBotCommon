from pokepediaRepository import PokepediaRepository, PokepediaGeneration

pr = PokepediaRepository()
move = pr.searchMoves('fire spin')

# pokemon = pr.searchPokemon('moltres')

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


move = pr.searchMoves('recover')

for s in move.toStrList():
  print(s)


move = pr.searchMoves('bide')

for s in move.toStrList():
  print(s)


move = pr.searchMoves('rage')

for s in move.toStrList():
  print(s)


move = pr.searchMoves('barrier')

for s in move.toStrList():
  print(s)


move = pr.searchMoves('hidden power')

for s in move.toStrList():
  print(s)

move = pr.searchMoves('horn drill')

for s in move.toStrList():
  print(s)

mon = pr.searchPokemon('azumarill')
print(mon.toStrList())
print(mon.getGenerationElementTypes())

mon = pr.searchPokemon('clefairy')
print(mon.toStrList())
print(mon.getGenerationElementTypes())
