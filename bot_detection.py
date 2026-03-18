"""
bot_detection.py
AI4MH — Bot amplification detection

Detects unnatural posting patterns that suggest coordinated
bot activity rather than genuine community distress signals.
"""

from typing import List, Dict
from datetime import datetime
from collections import Counter


BOT_THRESHOLD = 0.30  # if 30%+ posts flagged as bots, discount the spike


def check_posting_burst(timestamps: List[str], burst_window_seconds: int = 60) -> float:
    """
    Checks what proportion of posts arrived in unnatural bursts.
    Real humans post at varied times. Bots post in rapid bursts.

    Args:
        timestamps: list of ISO format timestamp strings
        burst_window_seconds: time window to detect bursts

    Returns:
        burst_ratio: proportion of posts in burst windows (0-1)
    """
    if len(timestamps) < 2:
        return 0.0

    times = sorted([datetime.fromisoformat(t) for t in timestamps])
    burst_count = 0

    for i in range(1, len(times)):
        diff = (times[i] - times[i-1]).total_seconds()
        if diff < burst_window_seconds:
            burst_count += 1

    return round(burst_count / len(times), 4)


def check_language_similarity(posts: List[str], similarity_threshold: float = 0.8) -> float:
    """
    Checks what proportion of posts are near-identical.
    Bot campaigns tend to repeat the same phrases across accounts.

    Returns:
        duplicate_ratio: proportion of near-duplicate posts (0-1)
    """
    if not posts:
        return 0.0

    # Simple word-level fingerprint
    def fingerprint(text):
        words = set(text.lower().split())
        return frozenset(words)

    fingerprints = [fingerprint(post) for post in posts]
    duplicate_count = 0

    for i in range(len(fingerprints)):
        for j in range(i+1, len(fingerprints)):
            fp_i, fp_j = fingerprints[i], fingerprints[j]
            if len(fp_i) == 0 or len(fp_j) == 0:
                continue
            overlap = len(fp_i & fp_j) / len(fp_i | fp_j)
            if overlap >= similarity_threshold:
                duplicate_count += 1

    total_pairs = len(posts) * (len(posts) - 1) / 2
    return round(duplicate_count / total_pairs, 4) if total_pairs > 0 else 0.0


def check_account_age(account_ages_days: List[int], new_account_threshold: int = 30) -> float:
    """
    Checks proportion of posts from newly created accounts.
    A spike driven by new accounts is suspicious.

    Args:
        account_ages_days: age of each posting account in days
        new_account_threshold: accounts younger than this are flagged

    Returns:
        new_account_ratio: proportion of posts from new accounts (0-1)
    """
    if not account_ages_days:
        return 0.0

    new_accounts = sum(1 for age in account_ages_days if age < new_account_threshold)
    return round(new_accounts / len(account_ages_days), 4)


def run_bot_detection(
    posts: List[str],
    timestamps: List[str],
    account_ages_days: List[int]
) -> Dict:
    """
    Runs full bot detection pipeline.
    Returns detection result and whether spike should be discounted.
    """
    burst_ratio = check_posting_burst(timestamps)
    similarity_ratio = check_language_similarity(posts)
    new_account_ratio = check_account_age(account_ages_days)

    # Combined bot score — weighted average
    bot_score = (
        (0.4 * burst_ratio) +
        (0.4 * similarity_ratio) +
        (0.2 * new_account_ratio)
    )

    is_bot_amplified = bot_score >= BOT_THRESHOLD

    return {
        "burst_ratio": burst_ratio,
        "similarity_ratio": similarity_ratio,
        "new_account_ratio": new_account_ratio,
        "bot_score": round(bot_score, 4),
        "bot_flag": is_bot_amplified,
        "action": "Discount spike — possible bot amplification" if is_bot_amplified else "No bot activity detected"
    }


if __name__ == "__main__":
    # Demo with mock data
    mock_posts = [
        "I feel so hopeless and alone right now",
        "I feel so hopeless and alone right now",  # duplicate
        "everything is pointless nothing matters",
        "everything is pointless nothing matters",  # duplicate
        "I genuinely cannot cope with life anymore"
    ]

    mock_timestamps = [
        "2026-03-18T14:00:01",
        "2026-03-18T14:00:03",  # 2 seconds later — burst
        "2026-03-18T14:00:05",  # burst
        "2026-03-18T14:32:00",
        "2026-03-18T15:14:00"
    ]

    mock_account_ages = [2, 5, 3, 180, 365]  # first 3 are new accounts

    print("Bot Detection — Demo\n")
    result = run_bot_detection(mock_posts, mock_timestamps, mock_account_ages)
    for key, value in result.items():
        print(f"{key}: {value}")
