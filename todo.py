
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

# Amtrak to Philly Playtest
# - TODO: render when purusing enemies have gotten stronger from persistence
# - TODO: Implement GameStateV2.player_death()
# - TODO: Implement spell memorization as main player level up progression.
# - TODO: Implement a simple 4x4 zone of nodes and implement simple navigation.
# - ok so I played to the final route and I died. This is to be expected, it was 5-enemy combat which is a lot and I was very low
# - What does progression look like from here? I like the idea of progression only being actually tied to wins.
# - So what if in theory I get nothing from that, but I would be able to try a slightly less challenging route which
#   only requires me to beat a 3 or 4-enemy combat. I beat that and I get to a city, and that city lets me pick one spell 
# - map is a 3x3 grid of zones, and each zone is a 4x4 grid of nodes. Each zone has the 4 enemy factions we talked about.
#   So 4 factions per zone, and 9 zones means 36 total faction instances. But I'll say each faction appears in 2 different
#   zones so so really it's only 18 unique factions required. Even that's a bit much, so maybe I should say each faction
#   appears in 3 zones, that way there's only 12 unique factions for an entire map.
# - Oh shit wait or I just say the entire thing is a 12 by 12 grid of nodes, with each faction getting a column and a row...
#   That is def much simpler.
# - There would be cities scattered across this map, with more clustered around the starting area and getting thinner and
#   thinner as you go.
# - Would they all be pre-existing or would players make cities as well? I do like the idea of new cities popping up as players
#   take their actions? Like what if it's just you discovering cities? Or like finding maps? So then when it's multiplayer
#   there's nice builtin: 'oh Nicole went and discovered a new city we can go to'.
# - And it should be kind of choose-your-own-adventure-y -- I don't want to railroad you to always have to go to the top
#   right corner. If you want you should be able to stay in your little region and do quests trading between cities there
#   and levelling up? You can get to know your area and how to deal with the enemies you mostly encounter.
# - What eventually will incentivize you to explore out to harder locations? I think it should be the quests you get.
#   Quests will be biased towards cities close to you but rarely you'll get ones that are for cities farther away.
# - And you completing quests is how you interact with the story of the world? You are the magical traversers -- some of
#   the only people who can safely make it between cities. And so the messages you choose to ferry, the alliances you
#   help broker, the resources you bring and who you choose to help, has a big impact on how the world evolves.
# - The most basic way is just: cities will come under threat and if nothing is done they may fall to the dark lord
#   Sauron or his equivalent. They will become unavailable to you. But the cities you do choose to help will matter
#   positionally as waypoints for travel, but also for the resources / build-options they provide you.
# - Is my existing combat system sufficient to implement this vision? Yeah? Probably? I just need to make sure that you
#   do get a feeling of progression every time... So I guess that's why I do need experience and levelling up...
#   But do I let you memorize spells from level ups or do I make you wait until cities? Rituals should def wait until cities,
#   but I suppose spell memorization can be on a run by run basis...
# - The other progression can be money to upgrade your spellbook with bigger page capacity and more pages?
#   This can only be done at cities.
# - The only time pressure will be that the story of the world is progressing as more runs pass, so you want to use your time wisely.

# Playtest with Nicole:
# - exploring / discovery aspect is nice
# - lifesteal has a bug
# - healing hard to come by
# - rez downed members
# - item drop rate should be higher
# - drafting focus was more on the spells than the enemies
# - option to try to steal from the shop???
