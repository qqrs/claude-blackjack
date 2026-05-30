import time
from game import Game, GameState, Move


def show_hand(label: str, hand, hide_second: bool = False) -> None:
    cards = hand.cards()
    if hide_second and len(cards) >= 2:
        parts = [str(cards[0]), '??']
        print(f'{label}: {" ".join(parts)}')
    else:
        parts = [str(c) for c in cards]
        print(f'{label}: {" ".join(parts)} ({hand.value()})')


def play_round() -> None:
    game = Game()
    show_hand('Dealer', game.dealer, hide_second=True)
    show_hand('You', game.player)

    if game.state == GameState.DONE:
        print('Blackjack!')
    else:
        while game.state == GameState.PLAYER_TURN:
            move = input('Hit or stand? (h/s): ').strip().lower()
            if move == 'h':
                game.apply_move(Move.HIT)
                show_hand('You', game.player)
            elif move == 's':
                game.apply_move(Move.STAND)

        if game.state == GameState.DEALER_TURN:
            print("Dealer's turn:")
            show_hand('Dealer', game.dealer)
            time.sleep(0.8)
            while game.state == GameState.DEALER_TURN:
                game.dealer_step()
                show_hand('Dealer', game.dealer)
                time.sleep(0.8)

    winner = game.winner
    if winner == 'player':
        print('You win!')
    elif winner == 'dealer':
        print('Dealer wins.')
    else:
        print('Push.')


def main() -> None:
    print('Blackjack')
    while True:
        print()
        play_round()
        print()
        if input('Play again? (y/n): ').strip().lower() != 'y':
            break


if __name__ == '__main__':
    main()
