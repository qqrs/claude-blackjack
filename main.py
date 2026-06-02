import time
from game import Game, GameState, Move, dealer_move


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

    while game.state == GameState.PLAYER_TURN:
        choice = input('Hit or stand? (h/s): ').strip().lower()
        match choice:
            case 'h':
                game.apply_move(Move.HIT)
                show_hand('You', game.player)
            case 's':
                game.apply_move(Move.STAND)
            case _:
                print("Please type 'h' or 's'.")
                continue

    print()
    show_hand('Dealer', game.dealer)
    while game.state == GameState.DEALER_TURN:
        time.sleep(0.8)
        move = dealer_move(game.dealer)
        game.apply_move(move)
        if move == Move.HIT:
            show_hand('Dealer', game.dealer)

    assert game.state == GameState.DONE

    if game.player.is_blackjack():
        print('Blackjack!')
    if game.dealer.is_blackjack():
        print('Dealer blackjack!')

    match game.winner:
        case 'player':
            print('You win!')
        case 'dealer':
            print('Dealer wins.')
        case 'push':
            print('Push.')
        case _:
            raise ValueError(f'unexpected winner: {game.winner!r}')


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
