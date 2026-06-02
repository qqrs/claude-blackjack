import unittest
from blackjack import Card, Deck, Hand
from game import Game, GameState, Move, dealer_move


def hand(*ranks):
    h = Hand()
    for r in ranks:
        h.add(Card(r, '♠'))
    return h


def deck_dealing(*ranks):
    """A Deck whose next deals, in order, are the given ranks."""
    d = Deck()
    d._cards = [Card(r, '♠') for r in reversed(ranks)]  # pop() draws first
    return d


def rigged_game(player, dealer, upcoming):
    """A Game with known hands and a deck that deals `upcoming` in order."""
    game = Game()
    game.player = player
    game.dealer = dealer
    game.deck._cards = [Card(r, '♠') for r in reversed(upcoming)]  # pop() draws first
    game.state = GameState.PLAYER_TURN
    return game


class TestGame(unittest.TestCase):
    # deal order is player, dealer, player, dealer
    def test_player_wins(self):
        # player 16 -> hit 3 -> 19 -> stand; dealer stands on 17; player wins
        game = Game(deck=deck_dealing('10', '10', '6', '7', '3'))
        self.assertEqual(game.state, GameState.PLAYER_TURN)
        self.assertEqual(game.player.value(), 16)

        game.apply_move(Move.HIT)
        self.assertEqual(game.player.value(), 19)
        game.apply_move(Move.STAND)
        self.assertEqual(game.state, GameState.DEALER_TURN)

        game.apply_move(dealer_move(game.dealer))   # dealer 17 -> stand -> resolve
        self.assertEqual(game.state, GameState.DONE)
        self.assertEqual(game.winner, 'player')     # 19 > 17

    def test_player_blackjack(self):
        game = Game(deck=deck_dealing('A', '9', 'K', '7'))  # player A,K=21; dealer 9,7=16
        self.assertTrue(game.player.is_blackjack())
        self.assertEqual(game.state, GameState.DONE)
        self.assertEqual(game.winner, 'player')

    def test_dealer_blackjack(self):
        game = Game(deck=deck_dealing('10', 'A', '9', 'K'))  # player 10,9=19; dealer A,K=21
        self.assertTrue(game.dealer.is_blackjack())
        self.assertEqual(game.state, GameState.DONE)
        self.assertEqual(game.winner, 'dealer')

    def test_both_blackjack(self):
        game = Game(deck=deck_dealing('A', 'A', 'K', 'K'))  # both A,K=21
        self.assertTrue(game.player.is_blackjack())
        self.assertTrue(game.dealer.is_blackjack())
        self.assertEqual(game.state, GameState.DONE)
        self.assertEqual(game.winner, 'push')


class TestDealerMove(unittest.TestCase):
    def test_dealer_move(self):
        self.assertEqual(dealer_move(hand('K', '6')), Move.HIT)    # 16, hit
        self.assertEqual(dealer_move(hand('K', '7')), Move.STAND)  # 17, stand
        self.assertEqual(dealer_move(hand('A', '6')), Move.STAND)  # soft 17, stand
        self.assertEqual(dealer_move(hand('K', 'Q', '5')), Move.STAND)  # 25 bust, stand


class TestApplyMove(unittest.TestCase):
    def test_full_game(self):
        # player 15 -> hit 4 -> 19 -> stand; dealer 16 -> hit 5 -> 21 -> stand
        game = rigged_game(hand('10', '5'), hand('10', '6'), upcoming=['4', '5'])

        game.apply_move(Move.HIT)
        self.assertEqual(game.player.value(), 19)
        self.assertEqual(game.state, GameState.PLAYER_TURN)

        game.apply_move(Move.STAND)
        self.assertEqual(game.state, GameState.DEALER_TURN)

        game.apply_move(dealer_move(game.dealer))   # 16 -> hit -> 21
        self.assertEqual(game.dealer.value(), 21)
        self.assertEqual(game.state, GameState.DEALER_TURN)  # one card per step

        game.apply_move(dealer_move(game.dealer))   # 21 -> stand -> resolve
        self.assertEqual(game.state, GameState.DONE)
        self.assertEqual(game.winner, 'dealer')     # 19 < 21

    def test_player_bust_ends_immediately(self):
        game = rigged_game(hand('K', '6'), hand('K', '7'), upcoming=['Q'])
        game.apply_move(Move.HIT)                    # 16 -> 26, bust
        self.assertTrue(game.player.is_bust())
        self.assertEqual(game.state, GameState.DONE)
        self.assertEqual(game.winner, 'dealer')

    def test_dealer_bust(self):
        # player stands on 18; dealer 16 -> hit Q -> 26 bust, resolves in same step
        game = rigged_game(hand('10', '8'), hand('10', '6'), upcoming=['Q'])
        game.apply_move(Move.STAND)
        self.assertEqual(game.state, GameState.DEALER_TURN)
        game.apply_move(dealer_move(game.dealer))   # 16 -> hit -> 26 bust
        self.assertTrue(game.dealer.is_bust())
        self.assertEqual(game.state, GameState.DONE)
        self.assertEqual(game.winner, 'player')

    def test_apply_move_rejects_when_done(self):
        game = rigged_game(hand('K', '6'), hand('K', '7'), upcoming=['Q'])
        game.apply_move(Move.HIT)                    # busts -> DONE
        with self.assertRaises(ValueError):
            game.apply_move(Move.HIT)


if __name__ == '__main__':
    unittest.main()
