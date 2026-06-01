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
    def __init__(self, deck=None):
        if deck is None:
            deck = Deck()
            deck.shuffle()
        self.deck = deck
        self.player = Hand()
        self.dealer = Hand()
        for _ in range(2):
            self.player.add(self.deck.deal())
            self.dealer.add(self.deck.deal())
        self._winner: str | None = None
        self.state = GameState.PLAYER_TURN
        if self.player.is_blackjack():
            self._finish_game()

    def apply_move(self, move: Move) -> None:
        if self.state == GameState.PLAYER_TURN:
            hand = self.player
        elif self.state == GameState.DEALER_TURN:
            hand = self.dealer
        else:
            raise ValueError(f'apply_move called in state {self.state}')

        match move, self.state:
            case Move.HIT, _:
                hand.add(self.deck.deal())
                if hand.is_bust():
                    self._finish_game()
            case Move.STAND, GameState.PLAYER_TURN:
                self.state = GameState.DEALER_TURN   # player stands -> dealer's turn
            case Move.STAND, GameState.DEALER_TURN:
                self._finish_game()                  # dealer stands -> resolve
            case _:
                raise ValueError(f'unhandled move/state: {move!r} in {self.state!r}')

    def _finish_game(self) -> None:
        self._winner = determine_winner(self.player, self.dealer)
        self.state = GameState.DONE

    @property
    def winner(self) -> str | None:
        return self._winner
