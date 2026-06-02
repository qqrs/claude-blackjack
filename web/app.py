import os
import secrets

from flask import Flask, render_template, session

from game import Game, GameState

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# Game state, indexed by session ID. In-memory, cleared on restart.
games: dict[str, Game] = {}


def current_game() -> Game:
    """Return this session's game state. Create if needed."""
    sid = session.get("sid")
    if sid is None or sid not in games:
        sid = secrets.token_hex(16)
        session["sid"] = sid
        games[sid] = Game()
    return games[sid]


def hand_view(hand, hide_hole_card: bool):
    """Return the cards and hand value to be displayed."""
    cards = hand.cards()
    if hide_hole_card:
        return {"cards": [str(cards[0]), "??"], "total": None}
    return {"cards": [str(c) for c in cards], "total": hand.value()}


@app.route("/")
def index():
    game = current_game()
    dealer = hand_view(game.dealer, hide_hole_card=game.state == GameState.PLAYER_TURN)
    player = hand_view(game.player, hide_hole_card=False)
    return render_template("index.html", dealer=dealer, player=player)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
