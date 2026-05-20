"""
MoodFlix — Quick smoke test for the mood classifier.

Runs a fixed set of representative inputs (formal, slang, Gen Z, emoji-only,
typo-laden, edge cases) and prints the predicted mood + confidence + source
for each, plus a summary count of how many landed on the "expected" mood.

Run:
    cd server && source venv/bin/activate
    python -m ml.smoke_test
"""
from __future__ import annotations

from ml.mood_classifier import get_classifier


CASES: list[tuple[str, str]] = [
    # text, expected_mood
    ("I love this", "romantic"),
    ("I hate everything", "dark"),
    ("lol so excited", "excited"),
    ("feeling so down rn", "sad"),
    ("just got back from hiking", "adventurous"),
    ("going to climb a mountain tomorrow", "adventurous"),
    ("idk what to feel anymore", "sad"),

    ("lfg let's gooo!!!", "excited"),
    ("im so hyped for the concert tomorrow", "excited"),
    ("locked in, no days off", "motivated"),
    ("workout done and im ready to crush it", "motivated"),

    ("alone again tonight, the silence is too much", "lonely"),
    ("no one ever texts me anymore", "lonely"),

    ("listening to old songs from high school", "nostalgic"),
    ("found my old yearbook today, took me right back", "nostalgic"),

    ("just want to curl up with a book and tea", "relaxed"),
    ("cozy sunday afternoon, no plans", "relaxed"),

    ("watched a movie that scrambled my brain, what is reality", "mind-bending"),
    ("i cant stop thinking about consciousness", "mind-bending"),

    ("i swear i heard footsteps downstairs at 3am", "scared"),
    ("this house feels haunted tonight", "scared"),

    ("how does the brain actually store memories", "curious"),
    ("ive been going down a wikipedia rabbit hole all day", "curious"),

    ("anniversary dinner with my partner was magical", "romantic"),
    ("got butterflies just thinking about him", "romantic"),

    ("deadline tomorrow and i havent even started", "stressed"),
    ("my anxiety is through the roof", "stressed"),

    ("watched my niece blow out her birthday candles, my heart", "wholesome"),
    ("a stranger paid for my coffee today, made my whole day", "wholesome"),

    ("crying watching old home videos tonight", "emotional"),
    ("this song hit me right in the feels", "emotional"),

    # Pure emoji
    ("🥳🥳🥳", "happy"),
    ("😭", "sad"),
    ("🏔️ ✈️", "adventurous"),
    ("🥺", "lonely"),
]


def main() -> None:
    classifier = get_classifier()
    print(f"{'text':<60s} {'expected':<14s} → {'predicted':<14s} {'conf':>6s}  {'source':<12s} {'hit'}")
    print("-" * 130)
    hits = 0
    for text, expected in CASES:
        r = classifier.predict(text)
        ok = "✓" if r["detected_mood"] == expected else "✗"
        if r["detected_mood"] == expected:
            hits += 1
        print(f"{text[:58]:<60s} {expected:<14s} → {r['detected_mood']:<14s} {r['confidence']:>6.2f}  {r['source']:<12s} {ok}")
    print("-" * 130)
    print(f"  hits: {hits}/{len(CASES)} = {hits/len(CASES)*100:.1f}%")


if __name__ == "__main__":
    main()
