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
- **`Game`**: holds `deck`, `player`, `dealer`; `__init__(deck=None)` deals two cards each (deck injectable for testing) and ends instantly if either side has a natural
  - **`apply_move(move)`**: single entry point for *both* player and dealer — picks the active hand from `state` and `match`es on `(move, state)`. One card per call, so the dealer can be animated by calling `apply_move(dealer_move(game.dealer))` in a loop.
  - `winner` property returns the result once `DONE`; `_finish_game()` centralizes the `determine_winner` + `DONE` transition

### I/O layer ✓ (not unit tested)

- `show_hand(label, hand, hide_second=False)` — prints cards and value
- `play_round()` — drives one game: player input loop, then reveal the dealer's
  hole card, animated dealer draw loop (shows each drawn card), result
- `main()` — outer play-again loop

### Game flow

```
main()
└── play again loop (until player declines)
    └── play_round()
        ├── Game() → deal 2 cards each (dealer's second hidden)
        ├── while PLAYER_TURN: prompt h/s → apply_move()
        ├── reveal dealer hole card
        ├── while DEALER_TURN: apply_move(dealer_move(...)) → show each draw
        ├── assert DONE; announce player / dealer natural
        └── match game.winner → print result
```

### Ace handling
`Hand.value()` sums Aces as 11, then subtracts 10 per Ace while total > 21.

### Win conditions (in `determine_winner`, in order)
- Player bust → `"dealer"` (an immediate loss, even if the dealer would also bust)
- Dealer bust → `"player"`
- Natural beats a non-natural (incl. a multi-card 21); both naturals → `"push"`
- Otherwise compare totals; equal → `"push"`

### Special cases (per [Wikipedia](https://en.wikipedia.org/wiki/Blackjack))
- A natural is 21 on the *first two cards*, and beats a 3+-card 21 — so blackjack
  status, not just `value() == 21`, decides the winner.
- Both player and dealer have a natural → **push** (handled).
- A natural for either side ends the hand at the deal, before the player acts:
  if either's two cards total 21, the round is immediately `DONE` (handled —
  `Game.__init__` checks both hands).

## Files ✓

- `blackjack.py` — data model: `Card`, `Deck`, `Hand`, `determine_winner`
- `game.py` — state machine: `Move`, `GameState`, `dealer_move`, `Game`
- `main.py` — CLI: `show_hand`, `play_round`, `main`
- `tests/test_blackjack.py` — `unittest`, data model + `determine_winner`
- `tests/test_game.py` — `unittest`, `Game` / `dealer_move` / `apply_move`

### Key test cases
- ~~`Hand.value()`: hard totals, soft Ace (A+6=17), Ace flip (A+6+9=16), multiple Aces~~
- ~~`Hand.is_blackjack()`: A+K → True, A+K+2 → False, 10+J → False~~
- ~~`Hand.is_bust()`: 22 → True, 21 → False~~
- ~~`determine_winner()`: busts, wins/push by total, natural beats multi-card 21~~
- ~~`dealer_move()`: hits 16, stands on 17 / soft 17 / bust~~
- ~~`Game` (via injected deck): player win, player / dealer / both blackjack at deal~~
- ~~`apply_move()`: full game both turns, player bust, dealer bust, rejects when `DONE`~~

## Verification

```
python -m unittest discover -s tests -t .   # run all tests from project root
python main.py                              # manual play-through
```
