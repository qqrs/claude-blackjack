from dataclasses import dataclass, field
import random


@dataclass
class Card:
    rank: str
    suit: str

    def __str__(self):
        return f'{self.rank}{self.suit}'


RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']


class Deck:
    def __init__(self):
        self._cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle(self):
        random.shuffle(self._cards)

    def deal(self):
        return self._cards.pop()


class Hand:
    def __init__(self, cards=None):
        self._cards: list[Card] = list(cards) if cards else []
        self._value_cache: int | None = None

    def add(self, card: Card):
        self._cards.append(card)
        self._value_cache = None

    def value(self) -> int:
        if self._value_cache is not None:
            return self._value_cache
        total = 0
        aces = 0
        for card in self._cards:
            if card.rank in ('J', 'Q', 'K'):
                total += 10
            elif card.rank == 'A':
                total += 11
                aces += 1
            else:
                total += int(card.rank)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        self._value_cache = total
        return total

    def is_bust(self) -> bool:
        return self.value() > 21

    def is_blackjack(self) -> bool:
        return len(self._cards) == 2 and self.value() == 21

    def cards(self) -> list[Card]:
        return list(self._cards)

    def __len__(self):
        return len(self._cards)


def determine_winner(player: Hand, dealer: Hand) -> str:
    if player.is_bust():
        return 'dealer'
    if dealer.is_bust():
        return 'player'
    match player.is_blackjack(), dealer.is_blackjack():
        case True, True:
            return 'push'
        case True, False:
            return 'player'
        case False, True:
            return 'dealer'
    pv, dv = player.value(), dealer.value()
    if pv > dv:
        return 'player'
    if dv > pv:
        return 'dealer'
    return 'push'
