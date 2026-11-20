import random
from typing import List, Optional, Set, Tuple

Board = List[List[int]]

DIFFICULTY_CLUES = {
    "easy": (38, 44),
    "medium": (30, 36),
    "hard": (24, 29),
}


def empty_board() -> Board:
    return [[0 for _ in range(9)] for _ in range(9)]


def clone_board(board: Board) -> Board:
    return [row[:] for row in board]


def get_candidates(board: Board, row: int, col: int) -> Set[int]:
    if board[row][col] != 0:
        return set()

    used = set(board[row])
    for r in range(9):
        if board[r][col] != 0:
            used.add(board[r][col])

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if board[r][c] != 0:
                used.add(board[r][c])

    return {num for num in range(1, 10) if num not in used}


def find_mrv_cell(board: Board) -> Optional[Tuple[int, int, Set[int]]]:
    """Return (row, col, candidates) for an empty cell with fewest candidates."""
    best: Optional[Tuple[int, int, Set[int]]] = None
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                candidates = get_candidates(board, r, c)
                if not candidates:
                    return (r, c, set())
                if best is None or len(candidates) < len(best[2]):
                    best = (r, c, candidates)
                    if len(candidates) == 1:
                        return best
    return best


def solve_board(board: Board, randomize: bool = False) -> Optional[Board]:
    work = clone_board(board)

    def backtrack() -> bool:
        cell = find_mrv_cell(work)
        if cell is None:
            return True
        r, c, candidates = cell
        if not candidates:
            return False

        nums = list(candidates)
        if randomize:
            random.shuffle(nums)
        else:
            nums.sort()

        for num in nums:
            work[r][c] = num
            if backtrack():
                return True
            work[r][c] = 0
        return False

    return work if backtrack() else None


def count_solutions(board: Board, limit: int = 2) -> int:
    """Count valid solutions up to `limit` using MRV backtracking."""
    work = clone_board(board)
    solutions = 0

    def backtrack() -> None:
        nonlocal solutions
        if solutions >= limit:
            return

        cell = find_mrv_cell(work)
        if cell is None:
            solutions += 1
            return

        r, c, candidates = cell
        if not candidates:
            return

        for num in sorted(candidates):
            work[r][c] = num
            backtrack()
            work[r][c] = 0
            if solutions >= limit:
                return

    backtrack()
    return solutions


def has_unique_solution(board: Board) -> bool:
    return count_solutions(board, limit=2) == 1


def generate_puzzle(difficulty: str = "medium") -> Tuple[Board, Board]:
    """Generate a (puzzle, solution) pair with a unique solution."""
    level = difficulty.lower() if difficulty.lower() in DIFFICULTY_CLUES else "medium"
    min_clues, max_clues = DIFFICULTY_CLUES[level]
    target_clues = random.randint(min_clues, max_clues)

    solved = solve_board(empty_board(), randomize=True)
    if solved is None:
        raise RuntimeError("Failed to generate a solved Sudoku board.")

    puzzle = clone_board(solved)
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    clues_remaining = 81
    for r, c in positions:
        if clues_remaining <= target_clues:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        if has_unique_solution(puzzle):
            clues_remaining -= 1
        else:
            puzzle[r][c] = backup

    return puzzle, solved


def find_conflicts(board: Board) -> List[List[int]]:
    """Return a 9x9 boolean-like int grid where 1 indicates a rule conflict."""
    conflicts = [[0 for _ in range(9)] for _ in range(9)]

    # Row duplicates
    for r in range(9):
        seen = {}
        for c in range(9):
            val = board[r][c]
            if val != 0:
                seen.setdefault(val, []).append((r, c))
        for cells in seen.values():
            if len(cells) > 1:
                for cr, cc in cells:
                    conflicts[cr][cc] = 1

    # Column duplicates
    for c in range(9):
        seen = {}
        for r in range(9):
            val = board[r][c]
            if val != 0:
                seen.setdefault(val, []).append((r, c))
        for cells in seen.values():
            if len(cells) > 1:
                for cr, cc in cells:
                    conflicts[cr][cc] = 1

    # 3x3 subgrid duplicates
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            seen = {}
            for r in range(br, br + 3):
                for c in range(bc, bc + 3):
                    val = board[r][c]
                    if val != 0:
                        seen.setdefault(val, []).append((r, c))
            for cells in seen.values():
                if len(cells) > 1:
                    for cr, cc in cells:
                        conflicts[cr][cc] = 1

    return conflicts


def is_board_solved(board: Board, solution: Optional[Board] = None) -> bool:
    for r in range(9):
        for c in range(9):
            if board[r][c] not in range(1, 10):
                return False
    if any(cell == 1 for row in find_conflicts(board) for cell in row):
        return False
    if solution is not None:
        return board == solution
    return True