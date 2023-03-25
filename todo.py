# - implement inventive?
# - implement dig deep
# - implement actual Condition class so that I can do fleeting
# - make empowered not spend all of itself if its overkilling? It stops once hp is 0
# - right now ward doesn't affect escape turn
# - bosses shouldn't have explore option
# - boss combats should be min 7 turns, max 10 turns?
# - refactor enemy actions so that I can compose targets with effects easier

# Design notes:
# - There needs to be doom action every n runs?
# - Every 4 runs? I guess? I need to mark part of the map as corrupted?
#   is that really the mechanism i want to use? Yeah because it means
#   you need to escape from a dangerous spot now and that's fun.
# - regions now have a level of corruption? Yeah not on the layer level yet?
# - 

# Design:
# - need to find a way to store characters outside of map and load them from there?
# - whenever you save() you also save the current character to a file?
# - Sure but how do you load them? I need some way to choose an arbitrary character
#   and let you play them from any node? Special init mode where you autoplay character?