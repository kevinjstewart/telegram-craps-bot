import pytest
from bets import *

class TestClassBets:
    # Test PlaceBet
    def test_place_bet_get_outcome(self):
        roll = Roll(2, 2)
        bet = PlaceBet(1, 6, Decimal(10))
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.KEEP

        roll = Roll(3, 5)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.KEEP

        roll = Roll(3, 3)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(10) + Decimal(10) * Decimal(9) / Decimal(5)

        roll = Roll(4, 3)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.REMOVE

    # Test PassLineBet
    def test_pass_line_bet_get_outcome(self):
        roll = Roll(2, 3)
        bet = PassLineBet(1, Decimal(20))
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.REMOVE

        roll = Roll(7, 4)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(20) * Decimal(2)

        roll = Roll(5, 5)
        outcome = bet.get_outcome(roll, 10)
        assert outcome.state == BetOutcomeState.KEEP

        roll = Roll(10, 5)
        outcome = bet.get_outcome(roll, 10)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(20) * Decimal(2)

        roll = Roll(7, 7)
        outcome = bet.get_outcome(roll, 10)
        assert outcome.state == BetOutcomeState.REMOVE

    # Test ComeBet
    def test_come_bet_get_outcome(self):
        roll = Roll(2, 3)
        bet = ComeBet(1, Decimal(30))
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.REMOVE

        roll = Roll(7, 4)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(30) * Decimal(2)

        roll = Roll(5, 5)
        outcome = bet.get_outcome(roll, 10)
        assert outcome.state == BetOutcomeState.KEEP

        roll = Roll(10, 5)
        outcome = bet.get_outcome(roll, 10)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(30) * Decimal(2)

        roll = Roll(7, 7)
        outcome = bet.get_outcome(roll, 10)
        assert outcome.state == BetOutcomeState.REMOVE

    # Test FieldBet
    def test_field_bet_get_outcome(self):
        roll = Roll(2, 2)
        bet = FieldBet(1, Decimal(25))
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(25) * Decimal(3)

        roll = Roll(3, 4)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(25) * Decimal(2)

        roll = Roll(5, 5)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.REMOVE

        roll = Roll(6, 6)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(25) * Decimal(2)

        roll = Roll(10, 11)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(25) * Decimal(2)

        roll = Roll(7, 7)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.REMOVE

    # Test HornBet
    def test_horn_bet_get_outcome(self):
        roll = Roll(1, 2)
        bet = HornBet(1, Decimal(50))
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(50) * Decimal(30)

        roll = Roll(3, 4)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.KEEP

        roll = Roll(5, 6)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.KEEP

        roll = Roll(6, 6)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(50) * Decimal(30)

        roll = Roll(7, 7)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.KEEP

        roll = Roll(2, 3)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.REMOVE

    # Test HardwaysBet
    def test_hardways_bet_get_outcome(self):
        roll = Roll(2, 2)
        bet = HardwaysBet(1, 4, Decimal(40))
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.PAY
        assert outcome.payout == Decimal(40) * Decimal(7)

        roll = Roll(3, 5)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.KEEP

        roll = Roll(4, 4)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.KEEP

        roll = Roll(7, 7)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.REMOVE

        roll = Roll(4, 3)
        outcome = bet.get_outcome(roll, None)
        assert outcome.state == BetOutcomeState.REMOVE
