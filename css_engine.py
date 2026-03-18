"""
css_engine.py
AI4MH — Crisis Signal Score (CSS) calculation engine

Combines sentiment intensity, volume spike, and geographic
clustering into a single actionable crisis score per county.
Applies safeguards and determines escalation level.
"""

from typing import Dict, List


MINIMUM_SAMPLE_SIZE = 30
MINIMUM_SAMPLE_SIZE_RURAL = 15
RURAL_POPULATION_THRESHOLD = 50000


def calculate_volume_spike(
    current_count: int,
    baseline_average: float
) -> float:
    """
    Calculates how unusual the current post volume is
    compared to the 30-day baseline average.

    VS = (current - baseline) / baseline

    Returns normalized VS score (0-1 for CSS engine)
    """
    if baseline_average == 0:
        return 0.0

    vs_raw = (current_count - baseline_average) / baseline_average
    # Normalize: a 300% spike = max score
    vs_score = min(vs_raw / 3.0, 1.0) if vs_raw > 0 else 0.0
    return round(vs_score, 4)


def calculate_geographic_clustering(
    flagged_counties: List[str],
    county_adjacency_map: Dict[str, List[str]]
) -> float:
    """
    Checks whether flagged counties are geographically
    close to each other (neighbouring counties).

    A real regional crisis tends to cluster geographically.
    A media spike hits random unconnected counties.

    Returns GC score (0-1):
    - 1.0 = all flagged counties are neighbours
    - 0.0 = no geographic clustering detected
    """
    if len(flagged_counties) < 2:
        return 0.0

    neighbour_pairs = 0
    total_pairs = 0

    for i, county in enumerate(flagged_counties):
        for other in flagged_counties[i+1:]:
            total_pairs += 1
            neighbours = county_adjacency_map.get(county, [])
            if other in neighbours:
                neighbour_pairs += 1

    return round(neighbour_pairs / total_pairs, 4) if total_pairs > 0 else 0.0


def calculate_confidence(
    post_count: int,
    days_sustained: int,
    has_bot_flag: bool,
    has_media_flag: bool,
    is_sparse: bool
) -> float:
    """
    Estimates confidence in the crisis signal.

    Higher post count + more days sustained = higher confidence.
    Bot flag, media flag, or sparse data = reduced confidence.
    """
    # Base confidence from volume (max at 500+ posts)
    volume_conf = min(post_count / 500, 1.0)

    # Sustained signal confidence (max at 5+ days)
    sustained_conf = min(days_sustained / 5, 1.0)

    confidence = (0.6 * volume_conf) + (0.4 * sustained_conf)

    # Apply penalties
    if has_bot_flag:
        confidence *= 0.4
    if has_media_flag:
        confidence *= 0.5
    if is_sparse:
        confidence *= 0.6

    return round(confidence, 4)


def calculate_css(
    si_score: float,
    vs_score: float,
    gc_score: float
) -> float:
    """
    Final CSS formula:
    CSS = (0.4 × SI) + (0.4 × VS) + (0.2 × GC)
    """
    css = (0.4 * si_score) + (0.4 * vs_score) + (0.2 * gc_score)
    return round(css, 4)


def determine_escalation(css: float, confidence: float) -> Dict:
    """
    Determines escalation level based on CSS and confidence.

    Level 1 — Monitor   : CSS 0.5-0.7
    Level 2 — Review    : CSS 0.7-0.85, confidence > 0.5
    Level 3 — Escalate  : CSS > 0.85, confidence > 0.7
    """
    if css >= 0.85 and confidence >= 0.7:
        return {
            "level": 3,
            "label": "IMMEDIATE ESCALATION",
            "action": "Alert State Behavioral Health Office — human response within 4 hours"
        }
    elif css >= 0.7 and confidence >= 0.5:
        return {
            "level": 2,
            "label": "HUMAN REVIEW",
            "action": "Alert analyst — review within 24 hours"
        }
    elif css >= 0.5:
        return {
            "level": 1,
            "label": "MONITOR",
            "action": "Log for weekly report — no immediate action"
        }
    else:
        return {
            "level": 0,
            "label": "NO SIGNAL",
            "action": "Log only"
        }


def run_css_pipeline(
    county: str,
    post_count: int,
    population: int,
    si_score: float,
    baseline_volume: float,
    days_sustained: int,
    flagged_counties: List[str],
    county_adjacency_map: Dict,
    has_bot_flag: bool = False,
    has_media_flag: bool = False
) -> Dict:
    """
    Full CSS pipeline for a single county.
    Returns complete scoring result with escalation decision.
    """
    # Determine if rural/sparse
    is_sparse = population < RURAL_POPULATION_THRESHOLD
    min_sample = MINIMUM_SAMPLE_SIZE_RURAL if is_sparse else MINIMUM_SAMPLE_SIZE

    # Check minimum sample size
    if post_count < min_sample:
        return {
            "county": county,
            "status": "INSUFFICIENT DATA",
            "post_count": post_count,
            "minimum_required": min_sample,
            "css": None,
            "escalation": None
        }

    # Calculate component scores
    vs_score = calculate_volume_spike(post_count, baseline_volume)
    gc_score = calculate_geographic_clustering(flagged_counties, county_adjacency_map)
    css = calculate_css(si_score, vs_score, gc_score)
    confidence = calculate_confidence(
        post_count, days_sustained,
        has_bot_flag, has_media_flag, is_sparse
    )
    escalation = determine_escalation(css, confidence)

    return {
        "county": county,
        "status": "SPARSE WARNING" if is_sparse else "OK",
        "post_count": post_count,
        "si_score": si_score,
        "vs_score": vs_score,
        "gc_score": gc_score,
        "css": css,
        "confidence": confidence,
        "bot_flag": has_bot_flag,
        "media_flag": has_media_flag,
        "escalation": escalation
    }


if __name__ == "__main__":
    # Mock adjacency map for demo
    adjacency = {
        "County_A": ["County_B", "County_C"],
        "County_B": ["County_A", "County_C"],
        "County_C": ["County_A", "County_B"]
    }

    result = run_css_pipeline(
        county="County_A",
        post_count=320,
        population=120000,
        si_score=0.78,
        baseline_volume=80,
        days_sustained=3,
        flagged_counties=["County_A", "County_B", "County_C"],
        county_adjacency_map=adjacency,
        has_bot_flag=False,
        has_media_flag=False
    )

    print("CSS Engine — Pipeline Demo\n")
    for key, value in result.items():
        print(f"{key}: {value}")
