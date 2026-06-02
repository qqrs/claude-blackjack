import os
import secrets

from flask import Flask, redirect, render_template, session, url_for

from game import Game, GameState, Move, dealer_move

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# Game state, indexed by session ID. In-memory, cleared on restart.
games: dict[str, Game] = {}

OUTCOMES = {"player": "You win!", "dealer": "Dealer wins.", "push": "Push."}


def session_id() -> str:
    """Return this session's ID, creating one if needed."""
    sid = session.get("sid")
    if sid is None:
        sid = secrets.token_hex(16)
        session["sid"] = sid
    return sid


def current_game() -> Game:
    """Return this session's game state. Create if needed."""
    sid = session_id()
    if sid not in games:
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
    result = None
    if game.state == GameState.DONE:
        result = {
            "outcome": OUTCOMES[game.winner],
            "player_blackjack": game.player.is_blackjack(),
            "dealer_blackjack": game.dealer.is_blackjack(),
        }
    return render_template("index.html", dealer=dealer, player=player, result=result)


@app.route("/hit", methods=["POST"])
def hit():
    game = current_game()
    if game.state == GameState.PLAYER_TURN:
        game.apply_move(Move.HIT)
    return redirect(url_for("index"))


@app.route("/stand", methods=["POST"])
def stand():
    game = current_game()
    if game.state == GameState.PLAYER_TURN:
        game.apply_move(Move.STAND)
        while game.state == GameState.DEALER_TURN:
            game.apply_move(dealer_move(game.dealer))
    return redirect(url_for("index"))


@app.route("/new", methods=["POST"])
def new():
    games[session_id()] = Game()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
