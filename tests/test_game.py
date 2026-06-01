import unittest
from blackjack import Card, Hand
from game import Move, dealer_move


def hand(*ranks):
    h = Hand()
    for r in ranks:
        h.add(Card(r, '♠'))
    return h


class TestDealerMove(unittest.TestCase):
    def test_dealer_move(self):
        self.assertEqual(dealer_move(hand('K', '6')), Move.HIT)    # 16, hit
        self.assertEqual(dealer_move(hand('K', '7')), Move.STAND)  # 17, stand
        self.assertEqual(dealer_move(hand('A', '6')), Move.STAND)  # soft 17, stand
        self.assertEqual(dealer_move(hand('K', 'Q', '5')), Move.STAND)  # 25 bust, stand


if __name__ == '__main__':
    unittest.main()
