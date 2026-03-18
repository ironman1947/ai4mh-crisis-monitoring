"""
crisis_lexicon.py
AI4MH — Crisis keyword and coded language database

Covers explicit terms, coded language, and slang used in online
communities to discuss mental health distress, suicidality, and
substance use. Used by the CSS engine for post-level flagging.
"""

CRISIS_LEXICON = {

    "mental_health_distress": [
        "can't go on", "no reason to live", "feeling hopeless",
        "nothing matters", "empty inside", "mentally exhausted",
        "breaking down", "falling apart", "can't cope",
        "don't want to be here", "tired of everything",
        "no one understands", "completely alone", "giving up"
    ],

    "suicide_related": [
        "end it all", "not worth living", "want to disappear",
        "better off dead", "thinking about suicide", "suicidal",
        "ending my life", "final goodbye", "can't take it anymore",
        "no way out", "want to die", "unalive myself",
        "kms", "kys"  # common coded terms used online
    ],

    "coded_language": [
        # Online community coded terms — updated regularly
        "unalive", "sewerslide", "rope", "exit bag",
        "ctb",   # cease to breathe
        "sui",   # abbreviation used in online spaces
        "sh",    # self harm abbreviation
        "relapse", "triggered", "in crisis"
    ],

    "substance_use": [
        "using again", "back on it", "relapsed",
        "can't stop using", "need a fix", "strung out",
        "overdosed", "od'd", "too much last night",
        "withdrawals", "detox", "struggling with addiction"
    ],

    "help_seeking": [
        # Positive signals — person is reaching out
        "need help", "looking for support", "crisis line",
        "therapy", "counselor", "mental health resources",
        "988",  # US suicide and crisis lifeline
        "reaching out", "getting help"
    ]
}


def flag_post(text: str) -> dict:
    """
    Checks a post against the crisis lexicon.
    Returns a dict with matched categories and match count.

    Args:
        text: raw post text (lowercased before matching)

    Returns:
        {
            "flagged": bool,
            "categories": list of matched categories,
            "match_count": int
        }
    """
    text_lower = text.lower()
    matched_categories = []
    total_matches = 0

    for category, terms in CRISIS_LEXICON.items():
        matches = [term for term in terms if term in text_lower]
        if matches:
            matched_categories.append(category)
            total_matches += len(matches)

    return {
        "flagged": total_matches > 0,
        "categories": matched_categories,
        "match_count": total_matches
    }


if __name__ == "__main__":
    # Simple demo
    test_posts = [
        "I just don't want to be here anymore, feeling hopeless",
        "Had a great day at the park today!",
        "Can't cope with everything, thinking about ctb",
        "Looking for mental health resources in my area"
    ]

    print("Crisis Lexicon — Post Flagging Demo\n")
    for post in test_posts:
        result = flag_post(post)
        print(f"Post: '{post[:60]}...' " if len(post) > 60 else f"Post: '{post}'")
        print(f"  Flagged: {result['flagged']}")
        print(f"  Categories: {result['categories']}")
        print(f"  Match count: {result['match_count']}\n")
