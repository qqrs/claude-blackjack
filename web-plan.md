# Blackjack Web App (Flask, on disco.cloud)

**Status: shipped** — built in steps 1–5 and deployed to disco.cloud from the
GitHub repo `qqrs/claude-blackjack` (push to `main` triggers a build/deploy).

## Context
Add a minimal web interface to the existing CLI blackjack game, hosted on
[disco.cloud](https://disco.cloud). Constraints from the user:
- Minimal frontend — server-rendered HTML plus one small vanilla-JS script (no
  framework, no build step) purely for a dealer-card reveal animation.
- Small scale — 1–10 concurrent users. No database, no auth.
- Keep it simple.

The core game logic (`blackjack.py`, `game.py`) already separates logic from I/O,
so the web layer is a thin new front-end alongside `main.py` — it reuses `Game`,
`Move`, `GameState`, and `dealer_move` unchanged. **No core changes needed.**

## Stack decision
- **Flask** — tiny synchronous web framework; a few routes + Jinja2 templates.
  (FastAPI is API/async-first and adds concepts we don't need; Streamlit's
  rerun model fights our explicit state machine.)
- **Server-rendered HTML** — Hit/Stand/New are `<form>` buttons that POST and
  reload the page. No build step. The only client-side code is a tiny inline
  script for the dealer reveal animation (progressive enhancement — the page is
  fully playable with JS disabled).
- **In-memory state** — `dict[str, Game]` keyed by a session id in a signed cookie.
  No DB. Games reset on redeploy/restart (acceptable for a casual game).
- **gunicorn**, single worker — see the constraint below.

## Repo layout
disco builds from a Dockerfile at the **repo root** and pulls the whole repo, so
the deploy files stay at root while the app code lives in `web/`:

```
/ (repo root)
├── blackjack.py        # core (unchanged)
├── game.py             # core (unchanged)
├── main.py             # CLI front-end (unchanged)
├── requirements.txt    # flask, gunicorn   [new]
├── Dockerfile          # build + run        [new]
├── disco.json          # disco service def  [new]
└── web/
    ├── __init__.py     # makes `web` a package for `web.app:app`
    ├── app.py          # Flask app — the new I/O layer
    ├── static/
    │   └── style.css   # all styling (served via Flask's static route)
    └── templates/
        └── index.html  # the only page (+ inline reveal script)
```

`web/app.py` imports the core with `from game import Game, ...`; the core modules
resolve because the container runs from `/code` (repo root) with it on `sys.path`.

## Routes (Flask)
All mutating routes use **Post/Redirect/Get** so a browser refresh never
re-submits a move.

- `GET  /`      — render the current game; create one for the session if none.
- `POST /hit`   — `game.apply_move(Move.HIT)` → redirect to `/`.
- `POST /stand` — `game.apply_move(Move.STAND)`, then loop
                  `game.apply_move(dealer_move(game.dealer))` until `DONE`
                  → redirect to `/`.
- `POST /new`   — replace with a fresh `Game()` → redirect to `/`.

Behavioral note: on Stand the server still plays the dealer out to completion in
one request (**no backend change for the animation**). The result page contains
the dealer's full final hand in the HTML; a small client-side script then reveals
those cards one at a time on page load (see Dealer animation below).

## State model
```python
games: dict[str, Game] = {}   # session_id -> Game
```
- Session id is a random token stored in Flask's signed session cookie.
- **Single-worker constraint:** in-memory state requires exactly one server
  process, or users' games would scatter across workers. Run gunicorn with
  `--workers 1 --threads 8` (plenty for 1–10 users).
- `SECRET_KEY` comes from an env var (set in the disco web UI) with a dev fallback,
  used only to sign the session cookie.

## Templates / display
- `index.html` shows: dealer hand (hole card hidden while `state == PLAYER_TURN`),
  player hand + value, Hit/Stand buttons while playing, and the result text +
  "New game" button when `DONE`.
- `hand_view()` formats a hand for display and hides the dealer's hole card — the
  web analogue of `show_hand` (same `hide_hole_card` param name). `card_view()`
  returns `{rank, suit, red}` per card. Reuse the CLI's wording: "Blackjack!",
  "Dealer blackjack!", "You win!", "Dealer wins.", "Push."
- Cards render as card faces (rank over suit) with red suits in red and the
  dealer's hole card as a styled face-down back. Styling lives in
  `web/static/style.css`; no CSS framework.

## Dealer animation (frontend only)
Goal: when the result page loads after a Stand, the dealer's cards appear one at a
time instead of all at once. **No backend change** — the server already renders the
full dealer hand on a completed game.

Approach (progressive enhancement, vanilla JS, ~15 lines inline in `index.html`):
- The template renders every dealer card, tagging the upcard separately from the
  cards revealed at showdown (the hole card + any draws), e.g. a
  `class="dealer-reveal"` on each of the latter.
- On load, **if** any `.dealer-reveal` cards exist, the script hides them — plus
  the dealer total (`#dealer-total`) and the result text — then reveals the cards
  one every ~600ms via `setTimeout`. The dealer total and result appear together
  with the final card, so neither is spoiled early.
- If JS is disabled, nothing is hidden and all cards, the total, and the result
  simply show — fully playable.

Scope note: the script animates whenever a completed dealer hand is shown, which
covers the post-Stand case (and harmlessly re-runs on a manual refresh). Limiting
it to *only* the first load after a Stand would require a one-shot signal from the
server (e.g. a redirect flag), which we're avoiding to keep it backend-free.

## Deployment (disco.cloud)
Confirmed against the official `example-flask-site` repo and `llms.txt`.

**`disco.json`** (at repo root):
```json
{
    "version": "1.0",
    "services": {
        "web": {
            "port": 8080
        }
    }
}
```

**`Dockerfile`** (at repo root) — based on disco's Flask example, with gunicorn:
```dockerfile
FROM python:3.12-slim
WORKDIR /code
ADD ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
ADD . /code
CMD ["gunicorn", "--workers", "1", "--threads", "8", \
     "--bind", "0.0.0.0:8080", "web.app:app"]
```
(The disco example uses the Flask dev server via `python server.py`; we use
gunicorn for a more production-appropriate process. Port must match `disco.json`.)

**`requirements.txt`**: `flask`, `gunicorn`.

**Deploy commands** (from disco docs — run once to set up, then push-to-deploy):
```bash
disco init root@<your-disco-host>          # one-time, connects the CLI
disco github:apps:add                       # authorize GitHub
disco projects:add --name qq21 \
    --github <user>/<repo> --domain <domain>
# set SECRET_KEY in the disco web UI under the project's env vars
```
Done — the project is set up on disco as `qq21`; pushing to `main` deploys. View
logs with `disco logs --project qq21 [--service web]`; check a build with
`disco deploy:output`.

## Out of scope (per "minimal")
No JS framework or build step (just the one inline reveal script), no CSS
framework, no database, no accounts/login, no betting/chips, no multi-table or
multiplayer, no game persistence.

## Verification
```bash
# local
pip install -r requirements.txt
gunicorn --workers 1 --threads 8 --bind 0.0.0.0:8080 web.app:app
# open http://localhost:8080 — play a few rounds: hit-to-bust, stand,
# player blackjack, dealer blackjack, push

python -m unittest discover -s tests -t .   # core tests still pass (unchanged)
```

## Build checklist
- [x] `web/app.py` — routes, in-memory games dict, session cookie, SECRET_KEY env
- [x] `web/templates/index.html` — hands, buttons, result; hole-card hidden mid-hand
- [x] `web/static/style.css` — card-face styling, suit colors, face-down back
- [x] dealer reveal animation — inline vanilla JS in `index.html` (no backend change)
- [x] `web/__init__.py`
- [x] `requirements.txt`, `Dockerfile`, `disco.json` (root)
- [x] Local run-through, then deploy to disco
