"""Quick test for the mood classifier fixes."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ml.mood_classifier import get_classifier

c = get_classifier()

tests = [
    "i got rejected by my girlfriend",
    "i feel so alone nobody cares about me",
    "i want a scary horror movie tonight",
    "feeling great today love life",
    "i want something dark and twisted",
    "i am so stressed with work deadlines",
    "take me on an epic adventure",
    "adventurous",
    "wholesome",
    "scared",
    "i miss my childhood so much",
    "give me a psychological thriller",
    "i need motivation to keep going",
]

print("\n{:<45} {:<15} {:>6}  {}".format("Input", "Mood", "Conf", "Source"))
print("-" * 80)
for t in tests:
    r = c.predict(t)
    mood = r["detected_mood"]
    conf = int(r["confidence"] * 100)
    src  = r["source"]
    print("{:<45} {:<15} {:>5}%  {}".format(t[:44], mood, conf, src))
