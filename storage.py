import json
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_SCORES_FILE = Path(__file__).resolve().parent / "top10_scores.json"
MAX_LEADERBOARD_ENTRIES = 10


def sort_scores(scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort scores by higher score first, then faster completion time (fewer seconds)."""
    return sorted(
        scores,
        key=lambda item: (-int(item.get("score", 0)), int(item.get("seconds", 999999))),
    )[:MAX_LEADERBOARD_ENTRIES]


def qualifies_for_top10(candidate_score: int, scores: List[Dict[str, Any]]) -> bool:
    ordered = sort_scores(scores)
    if len(ordered) < MAX_LEADERBOARD_ENTRIES:
        return True
    lowest_top10_score = int(ordered[-1].get("score", 0))
    return int(candidate_score) >= lowest_top10_score


def load_scores(filepath: Path = DEFAULT_SCORES_FILE) -> List[Dict[str, Any]]:
    if not filepath.exists():
        return []
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return sort_scores(data)
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_scores(scores: List[Dict[str, Any]], filepath: Path = DEFAULT_SCORES_FILE) -> List[Dict[str, Any]]:
    ordered = sort_scores(scores)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(ordered, indent=2), encoding="utf-8")
    return ordered


def record_score(
    player: str,
    difficulty: str,
    seconds: int,
    mistakes: int = 0,
    filepath: Path = DEFAULT_SCORES_FILE,
) -> Dict[str, Any]:
    clean_player = (player or "Anonymous").strip()[:24] or "Anonymous"
    clean_seconds = max(1, int(seconds))
    clean_mistakes = max(0, int(mistakes))
    difficulty_bonus = {"easy": 500, "medium": 1000, "hard": 1500}.get(difficulty.lower(), 1000)
    raw_score = max(100, difficulty_bonus + max(0, 1800 - clean_seconds * 2) - clean_mistakes * 50)

    current_scores = load_scores(filepath)
    made_top10 = qualifies_for_top10(raw_score, current_scores)

    entry = {
        "player": clean_player,
        "difficulty": difficulty.lower(),
        "score": raw_score,
        "seconds": clean_seconds,
        "mistakes": clean_mistakes,
    }
    updated = save_scores(current_scores + [entry], filepath)
    rank = next((idx + 1 for idx, item in enumerate(updated) if item == entry), None)

    return {
        "entry": entry,
        "qualified": made_top10 and rank is not None,
        "rank": rank,
        "scores": updated,
    }