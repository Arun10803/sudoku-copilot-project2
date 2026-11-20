from sudoku_engine import (
    DIFFICULTY_CLUES,
    count_solutions,
    find_conflicts,
    generate_puzzle,
    has_unique_solution,
    is_board_solved,
)
from storage import load_scores, qualifies_for_top10, record_score, save_scores


def test_puzzle_clue_counts_and_unique_solution():
    for level, (min_clues, max_clues) in DIFFICULTY_CLUES.items():
        puzzle, solution = generate_puzzle(level)
        clues = sum(1 for row in puzzle for val in row if val != 0)
        assert min_clues <= clues <= max_clues
        assert has_unique_solution(puzzle)
        assert count_solutions(puzzle, limit=2) == 1
        assert is_board_solved(solution, solution)


def test_conflict_detection():
    board = [[0 for _ in range(9)] for _ in range(9)]
    board[0][0] = 5
    board[0][4] = 5  # Row duplicate
    board[3][0] = 5  # Column duplicate

    conflicts = find_conflicts(board)
    assert conflicts[0][0] == 1
    assert conflicts[0][4] == 1
    assert conflicts[3][0] == 1
    assert conflicts[1][1] == 0


def test_top10_leaderboard_sorting_and_persistence(tmp_path):
    scores_file = tmp_path / "scores.json"
    save_scores([], scores_file)

    for i in range(12):
        record_score(
            player=f"Player{i}",
            difficulty="medium",
            seconds=120 + i * 10,
            mistakes=0,
            filepath=scores_file,
        )

    persisted = load_scores(scores_file)
    assert len(persisted) == 10
    assert persisted[0]["score"] >= persisted[-1]["score"]
    assert qualifies_for_top10(persisted[-1]["score"] + 100, persisted)