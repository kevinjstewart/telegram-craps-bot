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
        player = self.players[player_id]
        if player.bankroll < amount:
            if player.balance > Decimal(15.0):
                raise CrapsError(f'{player.name} is not eligible to withdraw money, you need to have less than $15 in your hand to take out a loan.\n{player.name}\'s current balance is ${player.balance} and bankroll is ${player.bankroll:.2f}.')
            elif amount > Decimal(50.0):
                raise CrapsError(f'{player.name} is not eligible to withdraw money, the bank will only give you a loan up to $50.\n{player.name}\'s current bankroll is ${player.bankroll:.2f}.')
        player.bankroll -= amount
        player.balance += amount
    
    def deposit(self, player_id: int, amount: Decimal):
        if player_id not in self.players:
            raise CrapsError('Player does not exist.')
        if self.players[player_id].balance < amount:
            raise CrapsError(f'You don\'t have enough to make this deposit. You have ${self.players[player_id].balance}.')
        else:
            self.players[player_id].balance -= amount
            self.players[player_id].bankroll += amount