import unittest
from blackjack import Card, Deck, Hand, determine_winner


def hand(*ranks):
    h = Hand()
    for r in ranks:
        h.add(Card(r, '♠'))
    return h


class TestCard(unittest.TestCase):
    def test_str(self):
        self.assertEqual(str(Card('K', '♠')), 'K♠')


class TestDeck(unittest.TestCase):
    def test_deal(self):
        d = Deck()
        c = d.deal()
        self.assertIsInstance(c, Card)
        self.assertEqual(len(d._cards), 51)


class TestHand(unittest.TestCase):
    def test_value(self):
        self.assertEqual(hand('5', '7').value(), 12)
        self.assertEqual(hand('J', 'Q', 'K').value(), 30)
        self.assertEqual(hand('A', '6').value(), 17)       # A=11
        self.assertEqual(hand('A', '6', '9').value(), 16)  # A flips to 1
        self.assertEqual(hand('A', 'A').value(), 12)       # 11+1, not 22

    def test_add(self):
        h = hand('5')
        self.assertEqual(h.value(), 5)
        h.add(Card('6', '♠'))
        self.assertEqual(h.value(), 11)  # catches stale cache bug

    def test_len(self):
        self.assertEqual(len(hand('2', '3')), 2)

    def test_is_bust(self):
        self.assertTrue(hand('K', 'Q', '5').is_bust())
        self.assertFalse(hand('K', 'A').is_bust())

    def test_is_blackjack(self):
        self.assertTrue(hand('A', 'K').is_blackjack())
        self.assertFalse(hand('7', '7', '7').is_blackjack())  # 21 but 3 cards
        self.assertFalse(hand('10', 'J').is_blackjack())      # 20, not 21

    def test_init(self):
        h = Hand([Card('A', '♠'), Card('K', '♥')])
        self.assertTrue(h.is_blackjack())


class TestDetermineWinner(unittest.TestCase):
    def test_busts(self):
        self.assertEqual(determine_winner(hand('K', 'Q', '5'), hand('K', '7')), 'dealer')
        self.assertEqual(determine_winner(hand('K', '7'), hand('K', 'Q', '5')), 'player')
        # player bust takes precedence when both bust
        self.assertEqual(determine_winner(hand('K', 'Q', '5'), hand('K', 'Q', '5')), 'dealer')

    def test_wins(self):
        self.assertEqual(determine_winner(hand('K', '9'), hand('K', '8')), 'player')
        self.assertEqual(determine_winner(hand('K', '8'), hand('K', '9')), 'dealer')
        self.assertEqual(determine_winner(hand('K', '9'), hand('K', '9')), 'push')

    def test_blackjack_beats_multicard_21(self):
        self.assertEqual(determine_winner(hand('A', 'K'), hand('7', '7', '7')), 'player')


if __name__ == '__main__':
    unittest.main()
