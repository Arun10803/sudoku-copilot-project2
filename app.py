from flask import Flask, jsonify, render_template, request
from sudoku_engine import find_conflicts, generate_puzzle, is_board_solved, solve_board
from storage import load_scores, record_score

app = Flask(__name__)

# In-memory active game state for single-session play
ACTIVE_GAME = {
    "difficulty": "medium",
    "puzzle": [],
    "solution": [],
}


def _init_game(difficulty: str = "medium") -> dict:
    puzzle, solution = generate_puzzle(difficulty)
    ACTIVE_GAME["difficulty"] = difficulty
    ACTIVE_GAME["puzzle"] = puzzle
    ACTIVE_GAME["solution"] = solution
    return {
        "difficulty": difficulty,
        "puzzle": puzzle,
        "clues": sum(1 for row in puzzle for val in row if val != 0),
    }


_init_game("medium")


@app.route("/")
def index():
    return render_template("index.html", scores=load_scores())


@app.route("/api/new-game", methods=["POST"])
def api_new_game():
    payload = request.get_json(silent=True) or {}
    difficulty = str(payload.get("difficulty", "medium")).lower()
    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "medium"
    return jsonify(_init_game(difficulty))


@app.route("/api/check", methods=["POST"])
def api_check():
    payload = request.get_json(silent=True) or {}
    board = payload.get("board")
    if not isinstance(board, list) or len(board) != 9 or any(not isinstance(r, list) or len(r) != 9 for r in board):
        return jsonify({"error": "Invalid 9x9 board payload."}), 400

    normalized = [[int(v) if isinstance(v, (int, str)) and str(v).isdigit() and 1 <= int(v) <= 9 else 0 for v in row] for row in board]
    conflicts = find_conflicts(normalized)
    solved = is_board_solved(normalized, ACTIVE_GAME.get("solution"))
    return jsonify({
        "conflicts": conflicts,
        "has_conflicts": any(cell == 1 for row in conflicts for cell in row),
        "solved": solved,
    })


@app.route("/api/solve", methods=["GET"])
def api_solve():
    solution = ACTIVE_GAME.get("solution") or solve_board(ACTIVE_GAME.get("puzzle", []))
    return jsonify({"solution": solution})


@app.route("/api/scores", methods=["GET", "POST"])
def api_scores():
    if request.method == "GET":
        return jsonify({"scores": load_scores()})

    payload = request.get_json(silent=True) or {}
    result = record_score(
        player=str(payload.get("player", "Anonymous")),
        difficulty=str(payload.get("difficulty", ACTIVE_GAME.get("difficulty", "medium"))),
        seconds=int(payload.get("seconds", 120)),
        mistakes=int(payload.get("mistakes", 0)),
    )
    return jsonify(result), 201


if __name__ == "__main__":
    app.run(debug=True)