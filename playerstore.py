from player import *
from error import CrapsError

class PlayerStore:
    def __init__(self, id: int, players: dict[int: Player] = dict()):
        self.id = id
        self.players = {}
        if players:
            self.players = players

    # return type True indicates new player added
    def register_player(self, id: int, name: str) -> bool:
        if id in self.players:
            return False
        self.players[id] = Player(id=id, name=name, balance=Decimal(50.0))
        return True

    def register_player_from_message(self, message) -> bool:
        return self.register_player(id=message.from_user.id, name=message.from_user.first_name)
    
    def withdraw(self, player_id: int, amount: Decimal):
        if player_id not in self.players:
            raise CrapsError('Player does not exist.')
        if self.players[player_id].balance >= Decimal(5.0):
            raise CrapsError('Player is not eligible to withdraw money. Minimum balance to withdraw is $5.')
        else:
            self.players[player_id].bankroll -= amount
            self.players[player_id].balance += amount
    
    def deposit(self, player_id: int, amount: Decimal):
        if player_id not in self.players:
            raise CrapsError('Player does not exist.')
        if self.players[player_id].balance < amount:
            raise CrapsError(f'You don\'t have enough to make this deposit. You have ${self.players[player_id].balance}.')
        else:
            self.players[player_id].balance -= amount
            self.players[player_id].bankroll += amount