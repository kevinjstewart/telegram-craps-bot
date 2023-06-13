import pytest
from session import *

class TestClassSession: 

    def test_place_bet(self):
        player = Player(1, "Kevin", Decimal(50), bankroll=Decimal(0))
        player_store = PlayerStore(id=1, players={1: player})
        game = CrapsGame(player_store=player_store)

        bet = PassLineBet(player_id=player.id, amount=Decimal(20))

        try:
            game.place_bet(bet)
        except Exception as e:
            print(e)
            pytest.fail()
        
        assert len(game.staged_bets) == 1

        game.roll(player_id=player.id, injected_roll=Roll(3, 3))

        assert len(game.staged_bets) == 0
        assert len(game.bets) == 1

    def test_place_bet_insufficient_funds(self):
        player = Player(1, "Kevin", Decimal(50), bankroll=Decimal(0))
        player_store = PlayerStore(id=1, players={1: player})
        game = CrapsGame(player_store=player_store)

        bet = PassLineBet(player_id=player.id, amount=Decimal(70))

        try:
            game.place_bet(bet)
        except Exception as e:
            print(e)
            return
        pytest.fail("Bet should not have been placed")
    
    def test_payout_bets(self):
        player = Player(1, "Kevin", Decimal(50), bankroll=Decimal(0))
        player_store = PlayerStore(id=1, players={1: player})
        game = CrapsGame(player_store=player_store)

        bet = PassLineBet(player_id=player.id, amount=Decimal(50))
        game.place_bet(bet)
        result = game.roll(1, Roll(3, 4))

        assert len(result.winning_bets) == 1
        assert player.balance == Decimal(100)
        assert len(game.bets) == 0

        game.place_bet(PassLineBet(player_id=1, amount=Decimal(100)))

        assert len(game.staged_bets) == 1

        result2 = game.roll(1, Roll(1, 2))

        assert len(game.bets) == 0
        assert len(result2.losing_bets) == 1
        assert player.balance == 0
    
    def test_pass_line_point(self):
        player = Player(1, "Kevin", Decimal(50), bankroll=Decimal(0))
        player_store = PlayerStore(id=1, players={1: player})
        game = CrapsGame(player_store=player_store)

        bet = PassLineBet(player_id=player.id, amount=Decimal(50))
        game.place_bet(bet)
        result = game.roll(1, Roll(3, 3))

        assert len(result.winning_bets) == 0
        assert len(result.losing_bets) == 0

        assert game.get_point() == 6
        assert len(game.bets) == 1

        game.roll(1, Roll(4, 4))

        assert len(result.winning_bets) == 0
        assert len(result.losing_bets) == 0

        assert game.get_point() == 6
        assert len(game.bets) == 1

        result = game.roll(1, Roll(3, 3))
        assert len(result.winning_bets) == 1
        assert len(result.losing_bets) == 0
        assert len(game.bets) == 0
        assert game.get_point() is None