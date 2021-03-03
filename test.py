from pokepediaRepository import PokepediaRepository, PokepediaGeneration

pr = PokepediaRepository()
move = pr.searchMoves('fire spin')
moveDict = move.getGenDictionary()
moveGen1 = moveDict[PokepediaGeneration.GENERATION_1]

# pokemon = pr.searchPokemon('moltres')

print(move.getName(), move.getRawName())
# print(type(move.getName()))
# print(type(move.getGenDictionary()))
# print(moveDict[PokepediaGeneration.GENERATION_1])
print(moveGen1.getPower())
print(moveGen1.getAccuracy())
print(moveGen1.getPp())
print(moveGen1.getType())
print(moveGen1.getMoveType())