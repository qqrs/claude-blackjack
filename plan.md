# Blackjack CLI Game (Python)

## Context
User wants a simple command-line blackjack game in Python. Core gameplay only: deal, hit, stand, bust/win detection. No betting or advanced moves.

## Approach

Three files: `blackjack.py` (data model), `game.py` (state machine), `main.py` (CLI), plus `test_blackjack.py` (tests).

### Structure: separate logic from I/O

Game logic lives in classes and one standalone function — no `input()`, no `print()` inside them. The CLI layer (`main()` and the game loop) handles all I/O. This keeps everything directly testable by constructing instances with known cards.

### Data model ✓

- **`Card`**: `@dataclass` with `rank: str`, `suit: str`, and `__str__` → `K♠`
- **`Deck`**: class with `shuffle()` and `deal()` (pops from end of 52-card list)
- **`Hand`**: class with `add(card)`, `value()`, `is_bust()`, `is_blackjack()`, `cards()`, `__len__()`; `value()` caches result in `_value_cache: int | None`, invalidated on `add()`; `value()` caches its result in `_value_cache: int | None`, invalidated on `add()`

### Standalone function

- `determine_winner(player: Hand, dealer: Hand) → str` — returns `"player"`, `"dealer"`, or `"push"`

### Game state machine ✓

- **`Move`**: enum — `HIT`, `STAND`
- **`GameState`**: enum — `PLAYER_TURN`, `DEALER_TURN`, `DONE`
- **`Game`**: holds `deck`, `player`, `dealer`; exposes `apply_move(move)` and `dealer_step()` (one card at a time for animation); `winner` property returns result when `DONE`

### I/O layer ✓ (not unit tested)

- `show_hand(label, hand, hide_second=False)` — prints cards and value
- `play_round()` — drives one game: player input loop, animated dealer draw loop, result
- `main()` — outer play-again loop

### Game flow

```
main()
└── game loop (runs until player types 'n')
    ├── Deck() → shuffle
    ├── deal 2 cards to player Hand, 2 to dealer Hand (one face-down)
    ├── check hand.is_blackjack() for instant win
    ├── player_turn() → calls hand.value() / hand.is_bust() each hit
    ├── dealer_turn() → hits while hand.value() < 17
    ├── determine_winner() → print result
    └── "Play again? (y/n)"
```

### Ace handling
`Hand.value()` sums Aces as 11, then subtracts 10 per Ace while total > 21.

### Win conditions (in `determine_winner`)
- Player bust → `"dealer"`
- Dealer bust → `"player"`
- Compare totals; equal → `"push"`

## Files ✓

- `/Users/russ/dev/rc/claude/blackjack.py` — data model: `Card`, `Deck`, `Hand`, `determine_winner`
- `/Users/russ/dev/rc/claude/game.py` — state machine: `Move`, `GameState`, `Game`, `dealer_move`
- `/Users/russ/dev/rc/claude/main.py` — CLI: `show_hand`, `play_round`, `main`
- `/Users/russ/dev/rc/claude/tests/test_blackjack.py` — `unittest`, data model + `determine_winner`
- `/Users/russ/dev/rc/claude/tests/test_game.py` — `unittest`, `dealer_move`

### Key test cases
- ~~`Hand.value()`: hard totals, soft Ace (A+6=17), Ace flip (A+6+9=16), multiple Aces~~
- ~~`Hand.is_blackjack()`: A+K → True, A+K+2 → False, 10+J → False~~
- ~~`Hand.is_bust()`: 22 → True, 21 → False~~
- ~~`determine_winner()`: all outcome combinations~~
- ~~`dealer_move()`: hits 16, stands on 17 / soft 17 / bust~~

## Verification

```
python -m unittest discover -s tests -t .   # run all tests from project root
python main.py                              # manual play-through
```
