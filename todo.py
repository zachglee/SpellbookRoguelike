
# - implement actual Condition class so that I can do fleeting
# - refactor enemy actions so that I can compose targets with effects easier
# - enemy that steals or strips your conditions?
# - spells that windup?
# - enemies like the hunter that spawn just meat shields?
# - spells w uses for more energy?

# - enemy that turns you around
# - enemies that swap places in they queue
# - enemies that jump to a different side?
# - confusion condition effect? (take damage per action?)
# - enemies that give you energy when they die
# - enemies that just give you stuff when they die in general?
# - Give information about what's in the queue


# This is a good soundtrack! https://www.youtube.com/watch?v=dJ_RDaIQ61Y&t=259s

# -------------------------------------------------

# New map design:
# - So I need to refactor regiondraft and regionshop into one thing -- a region?
# - And then a map is a grid of regions, generated from 4 factions
# - There's a new interactive phase after a combat where you choose which region you're going to
# ^ This is a stable milestone to reach
# - Here I should probably test what it's like to bring old characters to new maps...
# 
# - Once I have that I might be ready to move to building the remote state database?
# - First we get single player working with a data store. Probably nosql?

# --------

# Multiplayer notes:
# - play_setup() has some components which need to be shared by players, and some which don't...
#   So there are 3 bits of state: the haven, the map, the player, and temporarily their encounter.
# - The haven and map are shared by players in a run, but player stuff ofc is not shared.
# - Ah ok so there is one GameState per run id. The game state has the map, and a reference to the haven.
# - Need to move the wait_for_teammate() to the GameState. 
