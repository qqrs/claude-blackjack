# Blackjack CLI Game (Python)

## Context
User wants a simple command-line blackjack game in Python. Core gameplay only: deal, hit, stand, bust/win detection. No betting or advanced moves.

## Approach

Three source files: `blackjack.py` (data model), `game.py` (state machine), `main.py` (CLI), plus a `tests/` package.

### Structure: separate logic from I/O

Game logic lives in classes and one standalone function — no `input()`, no `print()` inside them. The CLI layer (`main()` and the game loop) handles all I/O. This keeps everything directly testable by constructing instances with known cards.

### Data model ✓

- **`Card`**: `@dataclass` with `rank: str`, `suit: str`, and `__str__` → `K♠`
- **`Deck`**: class with `shuffle()` and `deal()` (pops from end of 52-card list)
- **`Hand`**: class with `add(card)`, `value()`, `is_bust()`, `is_blackjack()`, `cards()`, `__len__()`; `value()` caches its result in `_value_cache: int | None`, invalidated on `add()`

### Standalone function

- `determine_winner(player: Hand, dealer: Hand) → str` — returns `"player"`, `"dealer"`, or `"push"`

### Game state machine ✓

- **`Move`**: enum — `HIT`, `STAND`
- **`GameState`**: enum — `PLAYER_TURN`, `DEALER_TURN`, `DONE`
- **`dealer_move(hand) → Move`**: the dealer's policy — `HIT` while value < 17, else `STAND`
- **`Game`**: holds `deck`, `player`, `dealer`; `__init__(deck=None)` deals two cards each (deck injectable for testing) and ends instantly on a player blackjack
  - **`apply_move(move)`**: single entry point for *both* player and dealer — picks the active hand from `state` and `match`es on `(move, state)`. One card per call, so the dealer can be animated by calling `apply_move(dealer_move(game.dealer))` in a loop.
  - `winner` property returns the result once `DONE`; `_finish_game()` centralizes the `determine_winner` + `DONE` transition

### I/O layer ✓ (not unit tested)

- `show_hand(label, hand, hide_second=False)` — prints cards and value
- `play_round()` — drives one game: player input loop, animated dealer draw loop, result
- `main()` — outer play-again loop

### Game flow

```
main()
└── play again loop (until player declines)
    └── play_round()
        ├── Game() → deal 2 cards each (dealer's second hidden)
        ├── while PLAYER_TURN: prompt h/s → apply_move()
        ├── while DEALER_TURN: show hand → apply_move(dealer_move(...))
        ├── assert DONE; print "Blackjack!" on a natural
        └── match game.winner → print result
```

### Ace handling
`Hand.value()` sums Aces as 11, then subtracts 10 per Ace while total > 21.

### Win conditions (in `determine_winner`)
- Player bust → `"dealer"`
- Dealer bust → `"player"`
- Compare totals; equal → `"push"`

## Files ✓

- `/Users/russ/dev/rc/claude/blackjack.py` — data model: `Card`, `Deck`, `Hand`, `determine_winner`
- `/Users/russ/dev/rc/claude/game.py` — state machine: `Move`, `GameState`, `dealer_move`, `Game`
- `/Users/russ/dev/rc/claude/main.py` — CLI: `show_hand`, `play_round`, `main`
- `/Users/russ/dev/rc/claude/tests/test_blackjack.py` — `unittest`, data model + `determine_winner`
- `/Users/russ/dev/rc/claude/tests/test_game.py` — `unittest`, `Game` / `dealer_move` / `apply_move`

### Key test cases
- ~~`Hand.value()`: hard totals, soft Ace (A+6=17), Ace flip (A+6+9=16), multiple Aces~~
- ~~`Hand.is_blackjack()`: A+K → True, A+K+2 → False, 10+J → False~~
- ~~`Hand.is_bust()`: 22 → True, 21 → False~~
- ~~`determine_winner()`: all outcome combinations~~
- ~~`dealer_move()`: hits 16, stands on 17 / soft 17 / bust~~
- ~~`Game` (via injected deck): typical playthrough, player blackjack, both blackjack (push)~~
- ~~`apply_move()`: full game both turns, player bust, dealer bust, rejects when `DONE`~~

## Verification

```
python -m unittest discover -s tests -t .   # run all tests from project root
python main.py                              # manual play-through
```
