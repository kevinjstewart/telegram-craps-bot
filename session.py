import random
from copy import deepcopy
from bets import *
from playerstore import *
from error import CrapsError

class RollResult:
    def __init__(self, roll: Roll, winning_bets: list[Bet], losing_bets: list[Bet], point: Optional[int], updated_come_bets: list[ComeBet] = []):
        self.roll = roll
        self.winning_bets = winning_bets
        self.losing_bets = losing_bets
        self.updated_come_bets = updated_come_bets

class CrapsGame:
    def __init__(self, player_store: PlayerStore) -> None:
        self.player_store = player_store
        self.bets = set()
        self.staged_bets = set()
        self.point = None
    
    def roll(self, player_id: int, injected_roll: Optional[Roll] = None) -> RollResult:
        # roll staged bets into real bets
        self.bets = self.bets.union(self.staged_bets)
        self.staged_bets.clear()
        # roll the dice
        dice_roll = Roll(
            first_side=random.randint(1, 6),
            second_side=random.randint(1, 6)
        )
        if injected_roll is not None:
            dice_roll = injected_roll

        bet_result = self._payout_bets(dice_roll, self.point)

        if self.point == dice_roll.sum or dice_roll.sum == 7:
            self.point = None
        elif self.point is None and dice_roll.sum in POINT_NUMBERS:
            self.point = dice_roll.sum

        # mutate with updated point
        bet_result.point = dice_roll.sum
        return bet_result
    
    def get_point(self) -> Optional[int]:
        return self.point
    
    def place_bet(self, bet: Bet):
        player = self.player_store.players[bet.player_id]
        if player.balance < bet.amount:
            raise CrapsError(f'Insufficient funds, you only have ${player.balance:.2f}.')

        self.player_store.players[bet.player_id].balance -= bet.amount
        self.staged_bets.add(bet)

    # Returns a tuple containing [paid_out_bets, removed_bets]
    def _payout_bets(self, roll: Roll, point: Optional[int]) -> RollResult:
        paid_out_bets = list[Bet]()
        removed_bets = list[Bet]()
        remaining_bets = set[Bet]()
        updated_come_bets = list[ComeBet]()
        for bet in self.bets:
            old_bet = deepcopy(bet)
            outcome = bet.get_outcome(roll=roll, point=point)
            if outcome.state == BetOutcomeState.PAY and outcome.payout is not None:
                self.player_store.players[bet.player_id].balance += outcome.payout
                paid_out_bets.append(bet)
            elif outcome.state == BetOutcomeState.REMOVE:
                removed_bets.append(bet)
            else:
                remaining_bets.add(bet)
                # check for updated come bets
                if isinstance(bet, ComeBet) and old_bet.point_number != bet.point_number:
                    updated_come_bets.append(deepcopy(bet))
        self.bets = remaining_bets
        return RollResult(roll=roll, winning_bets=paid_out_bets, losing_bets=removed_bets, point=point, updated_come_bets=updated_come_bets)
