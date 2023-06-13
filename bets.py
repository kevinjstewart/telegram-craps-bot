from abc import abstractmethod
from enum import Enum, auto
from typing import Optional
from uuid import uuid4
from decimal import *
from player import *

# constants
POINT_NUMBERS = [4, 5, 6, 8, 9, 10]
DIE_SIDES = [1, 2, 3, 4, 5, 6]

class Roll:
    def __init__(self, first_side: int, second_side: int):
        if first_side not in DIE_SIDES or second_side not in DIE_SIDES:
            raise ValueError
        self.first_side = first_side
        self.second_side = second_side
        self.sum = first_side + second_side

class BetOutcomeState(Enum):
    KEEP = auto()
    REMOVE = auto()
    PAY = auto()

class BetOutcome:
    def __init__(self, state: BetOutcomeState, payout: Optional[Decimal] = None):
        self.state = state
        self.payout = payout

class Bet:
    def __init__(self, player_id: int, amount: Decimal, is_contract_bet: bool):
        self.id = uuid4()
        self.player_id = player_id
        self.amount = amount
        self.is_contract_bet = is_contract_bet

    @abstractmethod
    def get_outcome(self, roll: Roll, point: Optional[int]) -> BetOutcome:
        """Indicates how the bet should be treated after a given roll."""
        pass

    def display_name(self) -> str:
        return "generic"

    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

class PlaceBet(Bet):
    def __init__(self, player_id: int, roll_number: int, amount: Decimal):
        super().__init__(player_id=player_id, amount=amount, is_contract_bet=False)
        if roll_number not in POINT_NUMBERS:
            raise ValueError
        self.roll_number = roll_number
    
    @staticmethod
    def odds_multiplier(roll_number: int) -> Decimal:
        if roll_number in [4, 10]:
            return Decimal(9) / Decimal(5)
        elif roll_number in [5, 9]:
            return Decimal(7) / Decimal(5)
        elif roll_number in [6, 8]:
            return Decimal(7) / Decimal(6)
    
    def get_outcome(self, roll: Roll, point: Optional[int]) -> BetOutcome:
        if point is None:
            return BetOutcome(BetOutcomeState.KEEP)
        if roll.sum == 7:
            return BetOutcome(BetOutcomeState.REMOVE)
        elif roll.sum == self.roll_number:
            winnings = self.amount + (self.amount * self.odds_multiplier(self.roll_number))
            return BetOutcome(BetOutcomeState.PAY, winnings)
        else:
            return BetOutcome(BetOutcomeState.KEEP)
    
    def display_name(self) -> str:
        return f'{self.roll_number} place'

class PassLineBet(Bet):
    def __init__(self, player_id: int, amount: Decimal):
        super().__init__(player_id=player_id, amount=amount, is_contract_bet=True)
    
    def get_outcome(self, roll: Roll, point: Optional[int]) -> BetOutcome:
        if point == None:
            if roll.sum in [2, 3, 12]:
                return BetOutcome(BetOutcomeState.REMOVE)
            elif roll.sum in [7, 11]:
                return BetOutcome(BetOutcomeState.PAY, self.amount * Decimal(2))
            else:
                return BetOutcome(BetOutcomeState.KEEP)

        else:
            if roll.sum == point:
                return BetOutcome(BetOutcomeState.PAY, self.amount * Decimal(2))
            elif roll.sum == 7:
                return BetOutcome(BetOutcomeState.REMOVE)
            else:
                return BetOutcome(BetOutcomeState.KEEP)
    
    def display_name(self) -> str:
        return "pass line"

class ComeBet(Bet):
    def __init__(self, player_id: int, amount: Decimal, point_number: Optional[int] = None):
        super().__init__(player_id=player_id, amount=amount, is_contract_bet=True)
        if point_number not in POINT_NUMBERS:
            raise ValueError
        self.point_number = point_number
    
    def get_outcome(self, roll: Roll, point: Optional[int]) -> BetOutcome:
        if self.point_number == None:
            if roll.sum in [2, 3, 12]:
                return BetOutcome(BetOutcomeState.REMOVE)
            elif roll.sum in [7, 11]:
                return BetOutcome(BetOutcomeState.PAY, self.amount * Decimal(2))
            else:
                self.point_number = roll.sum
                return BetOutcome(BetOutcomeState.KEEP)
        else:
            if roll.sum == self.point_number:
                return BetOutcome(BetOutcomeState.PAY, self.amount * Decimal(2))
            elif roll.sum == 7:
                return BetOutcome(BetOutcomeState.REMOVE)
            else:
                return BetOutcome(BetOutcomeState.KEEP)
    
    def display_name(self) -> str:
        return f'come' if self.point_number is None else f'{self.point_number} come'

class FieldBet(Bet):
    def __init__(self, player_id: int, amount: Decimal):
        super().__init__(player_id=player_id, amount=amount, is_contract_bet=True)
    
    def get_outcome(self, roll: Roll, point: Optional[int]) -> BetOutcome:
        if point is None:
            return BetOutcome(BetOutcomeState.KEEP)
        if roll.sum in [2, 12]:
            return BetOutcome(BetOutcomeState.PAY, self.amount * Decimal(3))
        elif roll.sum in [3, 4, 9, 10, 11]:
            return BetOutcome(BetOutcomeState.PAY, self.amount * Decimal(2))
        else:
            return BetOutcome(BetOutcomeState.REMOVE)
    
    def display_name(self) -> str:
        return "field"

class HornBet(Bet):
    def __init__(self, player_id: int, amount: Decimal):
        super().__init__(player_id=player_id, amount=amount, is_contract_bet=False)
    
    def get_outcome(self, roll: Roll, point: Optional[int]) -> BetOutcome:
        if roll.sum == 2 or roll.sum == 12:
            winnings = self.amount * Decimal(30)
            return BetOutcome(BetOutcomeState.PAY, winnings)
        elif roll.sum == 3 or roll.sum == 11:
            winnings = self.amount * Decimal(15)
            return BetOutcome(BetOutcomeState.PAY, winnings)
        else:
            return BetOutcome(BetOutcomeState.REMOVE)
    
    def display_name(self) -> str:
        return "horn"

class HardwaysBet(Bet):
    def __init__(self, player_id: int, roll_number: int, amount: Decimal):
        super().__init__(player_id=player_id, amount=amount, is_contract_bet=False)
        if roll_number not in [4, 6, 8, 10]:
            raise ValueError("Invalid roll number for Hardways bet")
        self.roll_number = roll_number
    
    def get_outcome(self, roll: Roll, point: Optional[int]) -> BetOutcome:
        if point is None:
            return BetOutcome(BetOutcomeState.KEEP)

        if roll.sum == self.roll_number and roll.first_side == roll.second_side:
            if self.roll_number in [4, 10]:
                winnings = self.amount * Decimal(7)
            else:  # Roll number is 6 or 8
                winnings = self.amount * Decimal(9)
            return BetOutcome(BetOutcomeState.PAY, winnings)
        elif roll.sum == self.roll_number or roll.sum == 7:
            return BetOutcome(BetOutcomeState.REMOVE)
        else:
            return BetOutcome(BetOutcomeState.KEEP)
    
    def display_name(self) -> str:
        return f'hardway on {self.roll_number}'