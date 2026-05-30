# Blackjack CLI Game (Python)

## Context
User wants a simple command-line blackjack game in Python. Core gameplay only: deal, hit, stand, bust/win detection. No betting or advanced moves.

## Approach

Two files: `blackjack.py` (game logic + CLI) and `test_blackjack.py` (tests).

### Structure: separate logic from I/O

Game logic lives in classes and one standalone function — no `input()`, no `print()` inside them. The CLI layer (`main()` and the game loop) handles all I/O. This keeps everything directly testable by constructing instances with known cards.

### Data model ✓

- **`Card`**: `@dataclass` with `rank: str`, `suit: str`, and `__str__` → `K♠`
- **`Deck`**: class with `shuffle()` and `deal()` (pops from end of 52-card list)
- **`Hand`**: class with `add(card)`, `value()`, `is_bust()`, `is_blackjack()`, `cards()`, `__len__()`; `value()` caches result in `_value_cache: int | None`, invalidated on `add()`; `value()` caches its result in `_value_cache: int | None`, invalidated on `add()`

### Standalone function

- `determine_winner(player: Hand, dealer: Hand) → str` — returns `"player"`, `"dealer"`, or `"push"`

### I/O layer (not unit tested)

- `show_hand(hand, hide_second=False)` — prints cards
- `player_turn(deck, hand)` — loop prompting h/s
- `dealer_turn(deck, hand)` — hits until hand.value() >= 17
- `main()` — game loop, play-again prompt

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

## Files

- `/Users/russ/dev/rc/claude/blackjack.py` — data model only: `Card`, `Deck`, `Hand`, `determine_winner`
- `/Users/russ/dev/rc/claude/game.py` — game loop logic: `player_turn`, `dealer_turn`
- `/Users/russ/dev/rc/claude/main.py` — CLI entry point: `show_hand`, `main`
- `/Users/russ/dev/rc/claude/test_blackjack.py` — uses `unittest`, covers all code paths and edge cases

### Key test cases
- ~~`Hand.value()`: hard totals, soft Ace (A+6=17), Ace flip (A+6+9=16), multiple Aces~~
- ~~`Hand.is_blackjack()`: A+K → True, A+K+2 → False, 10+J → False~~
- ~~`Hand.is_bust()`: 22 → True, 21 → False~~
- ~~`determine_winner()`: all outcome combinations~~

## Verification

```
python -m pytest test_blackjack.py   # or: python -m unittest test_blackjack
python main.py                       # manual play-through
```
