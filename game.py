from enum import Enum
from blackjack import Deck, Hand, determine_winner


class Move(Enum):
    HIT = 'hit'
    STAND = 'stand'


class GameState(Enum):
    PLAYER_TURN = 'player_turn'
    DEALER_TURN = 'dealer_turn'
    DONE = 'done'


def dealer_move(hand: Hand) -> Move:
    return Move.HIT if hand.value() < 17 else Move.STAND


class Game:
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.player = Hand()
        self.dealer = Hand()
        for _ in range(2):
            self.player.add(self.deck.deal())
            self.dealer.add(self.deck.deal())
        self._winner: str | None = None
        if self.player.is_blackjack():
            self._winner = determine_winner(self.player, self.dealer)
            self.state = GameState.DONE
        else:
            self.state = GameState.PLAYER_TURN

    def apply_move(self, move: Move) -> None:
        if self.state != GameState.PLAYER_TURN:
            raise ValueError(f'apply_move called in state {self.state}')
        if move == Move.HIT:
            self.player.add(self.deck.deal())
            if self.player.is_bust():
                self._winner = 'dealer'
                self.state = GameState.DONE
        else:
            self.state = GameState.DEALER_TURN

    def dealer_step(self) -> None:
        if self.state != GameState.DEALER_TURN:
            raise ValueError(f'dealer_step called in state {self.state}')
        if dealer_move(self.dealer) == Move.HIT:
            self.dealer.add(self.deck.deal())
        else:
            self._winner = determine_winner(self.player, self.dealer)
            self.state = GameState.DONE

    @property
    def winner(self) -> str | None:
        return self._winner
