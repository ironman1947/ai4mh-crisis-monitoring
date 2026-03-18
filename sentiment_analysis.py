"""
sentiment_analysis.py
AI4MH — VADER sentiment scoring pipeline

Scores posts using VADER sentiment analysis and compares
current 72-hour window against the 30-day county baseline
to detect significant drops in regional sentiment.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict


analyzer = SentimentIntensityAnalyzer()


def score_post(text: str) -> float:
    """
    Scores a single post using VADER.
    Returns compound score: -1.0 (most negative) to +1.0 (most positive)
    """
    scores = analyzer.polarity_scores(text)
    return scores["compound"]


def score_county_window(posts: List[str]) -> float:
    """
    Calculates average sentiment score for a list of posts
    from a single county over a time window.

    Args:
        posts: list of post text strings

    Returns:
        average compound sentiment score
    """
    if not posts:
        return 0.0

    scores = [score_post(post) for post in posts]
    return sum(scores) / len(scores)


def calculate_sentiment_intensity(
    current_posts: List[str],
    baseline_score: float
) -> Dict:
    """
    Compares current window sentiment against 30-day baseline.
    Returns sentiment intensity signal and drop magnitude.

    Args:
        current_posts: posts from current 72-hour window
        baseline_score: county's 30-day average sentiment score

    Returns:
        {
            "current_score": float,
            "baseline_score": float,
            "drop": float,
            "significant": bool,
            "si_score": float (normalized 0-1 for CSS engine)
        }
    """
    current_score = score_county_window(current_posts)
    drop = baseline_score - current_score

    # Normalize drop to 0-1 scale for CSS engine
    # A drop of 0.5 or more on VADER scale = maximum SI score
    si_score = min(drop / 0.5, 1.0) if drop > 0 else 0.0

    return {
        "current_score": round(current_score, 4),
        "baseline_score": round(baseline_score, 4),
        "drop": round(drop, 4),
        "significant": drop > 0.2,  # threshold for flagging
        "si_score": round(si_score, 4)
    }


if __name__ == "__main__":
    # Demo with mock county posts
    current_window_posts = [
        "I can't cope with anything anymore, feeling so hopeless",
        "Nobody understands what I'm going through",
        "Everything feels pointless lately",
        "Struggling to get out of bed every day",
        "Don't want to be here anymore"
    ]

    # Simulated 30-day baseline for this county
    county_baseline = -0.15

    print("Sentiment Analysis — County Window Demo\n")
    result = calculate_sentiment_intensity(current_window_posts, county_baseline)

    print(f"Current 72hr average score : {result['current_score']}")
    print(f"30-day baseline score      : {result['baseline_score']}")
    print(f"Sentiment drop             : {result['drop']}")
    print(f"Significant drop detected  : {result['significant']}")
    print(f"SI score for CSS engine    : {result['si_score']}")
