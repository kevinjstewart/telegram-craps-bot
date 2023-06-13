from decimal import *

class Player:

    # constructor
    def __init__(self, id: int, name: str, balance: Decimal = 50, bankroll: Decimal = 0) -> None:
        self.id = id
        self.name = name
        self.balance = balance
        self.bankroll = bankroll

    