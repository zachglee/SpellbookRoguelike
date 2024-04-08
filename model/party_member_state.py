
from model.player import Player

class PartyMemberState:
    def __init__(self, player: Player):
        self.player = player
        self.completed_choices = []

