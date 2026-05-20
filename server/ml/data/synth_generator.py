"""
MoodFlix — Massive synthetic dataset generator.

Generates ~5–8K diverse samples per mood class (≈100K total) covering:
  • formal full sentences
  • casual / Gen Z slang
  • short reactions (1–4 words)
  • long descriptions (2–3 sentences)
  • typos / lowercase-only / no punctuation
  • intensifier / repetition variants ("soooo", "rly rly")
  • common chat abbreviations (rn, ngl, tbh, lmao, fr, idk, omg)

The output is written to `synthetic_mood_data.csv` and is intended to be
*merged* with the cleaned real-world corpus (dair-ai, go_emotions, hand
labels) by `build_dataset.py`. Synthetic data is generated deterministically
(seeded) so the same seed always produces the same corpus.

Run:
    cd server && source venv/bin/activate
    python -m ml.data.synth_generator
"""
from __future__ import annotations

import os
import random
import re
from collections import Counter

import pandas as pd

# --------------------------------------------------------------------------
# 1. CORE TEMPLATES PER MOOD
# --------------------------------------------------------------------------
# For every mood we list:
#   - subjects:    "I", "I'm", "she", "we", "my dog", "my best friend"
#   - feelings:    primary feeling expressions ("so excited", "thrilled")
#   - intensifiers: "really", "absolutely", "kinda", "low key", "high key"
#   - triggers:    optional cause/object ("about the trip", "right now")
#   - reactions:   short pure reactions ("excited!!!", "lol same")
#   - long_seeds:  longer multi-clause sentence seeds
#
# All of the lists below are intentionally large and overlapping (synonyms,
# slang variants, Gen Z forms) so the per-mood Cartesian product produces
# thousands of unique surface forms without manual labour.

INTENSIFIERS = [
    "", "so", "really", "super", "very", "absolutely", "completely",
    "kinda", "kind of", "sort of", "low key", "lowkey", "high key", "highkey",
    "honestly", "literally", "actually", "rly", "rlly", "pretty",
    "kinda just", "just", "totally", "deadass", "no cap",
]

SUBJECTS = [
    "I", "I'm", "i'm", "im", "i", "she", "he", "we", "they", "my friend",
    "my best friend", "my mom", "my brother", "my partner", "everyone",
    "my coworker", "this guy", "this girl",
]

POSSESSIVES_OF_SELF = [
    "my", "this", "today's", "tonight's", "the whole",
]

NEG_TAGS = ["", " not", " never"]  # we'll rarely insert negations; mostly empty

# Casual particles to sprinkle in
CASUAL_TAILS = [
    "", "", "", "", "",  # bias toward no tail
    " lol", " lmao", " fr", " ngl", " tbh", " rn", " omg", " hahaha",
    " ✨", " 😭", " 💀", " 🥹",  # tiny emoji pepper (real users mix these in even when not central)
    " idk", " 🙏", " sigh", " ugh", " yay", " yikes",
]

CASUAL_HEADS = [
    "", "", "", "", "",
    "ok so ", "okay so ", "bro ", "yo ", "lol ", "omg ", "honestly ",
    "ngl ", "tbh ", "i swear ", "deadass ", "fr ",
]


MOOD_TEMPLATES: dict[str, dict[str, list[str]]] = {
    # ------------------------------------------------------------- happy
    "happy": {
        "feelings": [
            "happy", "so happy", "really happy", "joyful", "cheerful", "elated",
            "delighted", "thrilled", "in such a good mood", "buzzing", "glowing",
            "smiling so much", "feeling great", "feeling amazing", "feeling fantastic",
            "having the best day", "loving life", "on cloud nine", "feeling blessed",
            "in a great mood", "having such a good time", "vibing", "feeling lucky",
        ],
        "triggers": [
            "", "right now", "today", "this morning", "this evening", "lately",
            "after that news", "because of you", "for no reason",
            "since I woke up", "ever since this morning", "after that win",
        ],
        "reactions": [
            "yay!", "yes!!!", "best day ever", "this slaps", "this is amazing",
            "lfg", "let's go!!", "happiest girl alive", "happiest guy alive",
            "im smiling fr", "this just made my day", "couldn't be happier",
            "10/10", "10 out of 10", "we won", "biggest grin rn", "what a day",
            "im so happy rn", "feeling it today", "no notes, perfect day",
            "best news ever", "love this for me", "this is the moment",
        ],
        "long_seeds": [
            "Just got the best news and I cannot stop smiling, feels like everything is finally going right.",
            "Spent the whole day with people I love and my cheeks honestly hurt from laughing so much.",
            "Woke up in the best mood and somehow the day just kept getting better, I needed this.",
            "Everything just clicked today — work was good, friends were good, I feel light.",
            "I don't even know why but I just feel really really good today, like nothing can ruin this.",
            "This is one of those days where you remember why life is actually pretty great.",
        ],
    },
    # ------------------------------------------------------------- sad
    "sad": {
        "feelings": [
            "sad", "so sad", "really sad", "down", "heartbroken", "miserable",
            "devastated", "low", "blue", "gutted", "deflated", "broken",
            "feeling low", "feeling empty", "feeling hopeless", "down bad",
            "feeling like crying", "near tears", "tearful", "sobbing",
            "in a slump", "in the dumps", "depressed", "drained",
        ],
        "triggers": [
            "", "right now", "today", "lately", "for some reason", "again",
            "since this morning", "all day", "this whole week",
            "after that conversation", "after the news",
        ],
        "reactions": [
            "i wanna cry", "crying rn", "im sobbing", "this hurts", "im not okay",
            "this sucks so bad", "feeling like crap", "feeling like nothing",
            "everything sucks rn", "wish today never happened", "worst day",
            "another bad day", "nothing feels right", "im so down",
            "i feel awful", "i feel terrible", "today broke me",
            "rough day", "not having a good day", "really down rn",
        ],
        "long_seeds": [
            "I don't really know what to say, today has been one of the worst days I've had in a long time.",
            "Everything just feels heavy and I keep wanting to cry but the tears won't even come anymore.",
            "I've been trying to hold it together but honestly I feel like I'm falling apart and no one can tell.",
            "This whole week has been awful, like one bad thing after another, and I'm completely drained.",
            "It hurts more than I want to admit and I don't have the energy to pretend I'm fine.",
        ],
    },
    # ------------------------------------------------------------- lonely
    "lonely": {
        "feelings": [
            "lonely", "so lonely", "really lonely", "alone", "all alone",
            "isolated", "by myself", "on my own", "left out", "abandoned",
            "disconnected", "lonesome", "empty inside", "alone in my head",
            "the only one", "forgotten", "invisible", "left behind",
        ],
        "triggers": [
            "", "tonight", "in this house", "in this city", "lately",
            "this weekend", "again", "since they left", "without my friends",
            "even in a crowd", "even surrounded by people",
        ],
        "reactions": [
            "no one to talk to", "no one texts me anymore", "wish someone called",
            "miss being around people", "miss having friends close by",
            "everyone is busy", "nobody checks in on me", "feeling forgotten",
            "phone hasn't buzzed all day", "house is too quiet",
            "i hate eating alone", "weekends alone hit different",
            "i miss them so much", "wish i had someone to hang with",
        ],
        "long_seeds": [
            "It's another quiet Friday night and I'm sitting alone in my apartment again, just me and the silence.",
            "Everyone seems to have their own life and I keep refreshing my phone hoping someone reaches out, but nothing.",
            "Moved to a new city and I haven't really made any real friends yet, the loneliness is starting to get to me.",
            "I miss my old friend group so much, we used to hang out every weekend and now I just sit at home alone.",
            "Even in a room full of people I feel completely alone, like nobody actually sees me at all.",
        ],
    },
    # ------------------------------------------------------------- romantic
    "romantic": {
        "feelings": [
            "in love", "so in love", "head over heels", "smitten", "obsessed with them",
            "feeling lovey", "feeling romantic", "feeling soft", "feeling all mushy",
            "giddy about him", "giddy about her", "crushing hard", "got butterflies",
            "swooning", "falling for them", "thinking about them nonstop",
            "missing them already", "stuck on them", "weak for them",
        ],
        "triggers": [
            "", "tonight", "again", "still", "right now", "all day",
            "ever since we met", "since our first date", "after last night",
        ],
        "reactions": [
            "i love you", "i love them so much", "they're perfect", "she's perfect",
            "he's perfect", "best person ever", "my favorite person",
            "butterflies all over", "kissing my partner rn",
            "date night was amazing", "couldn't ask for better",
            "they make me so happy", "i found my person", "perfect first date",
        ],
        "long_seeds": [
            "Spent the whole evening with them and I genuinely don't think I've ever been this happy, they're everything.",
            "He just sent the cutest text and I'm literally smiling at my phone like an idiot, I love him so much.",
            "She held my hand on the walk home and I felt like a teenager again, this is what love is supposed to feel like.",
            "I keep thinking about them all day and I can't focus on anything, I am hopelessly in love.",
            "Anniversary dinner tonight, candles, wine, the whole thing — pure magic with my favorite human.",
        ],
    },
    # ------------------------------------------------------------- excited
    "excited": {
        "feelings": [
            "excited", "so excited", "really excited", "thrilled", "pumped",
            "hyped", "hyped up", "hyped af", "stoked", "amped", "fired up",
            "buzzing", "geeking out", "losing my mind", "freaking out (good way)",
            "shaking with excitement", "vibrating", "literally can't wait",
            "counting down the days", "ready to scream", "screaming internally",
        ],
        "triggers": [
            "", "for tomorrow", "for the trip", "for the concert", "for the launch",
            "about the news", "about tonight", "for the weekend", "for friday",
            "about the show", "for the game", "for the season finale",
        ],
        "reactions": [
            "lfg", "let's gooo", "lets goooo", "lets go!!!", "i can't wait",
            "icantwait", "cant wait fr", "this is gonna be insane", "yesssss",
            "scream", "im screaming", "shaking", "shaking rn", "best news",
            "biggest hype ever", "all caps energy", "WE ARE SO BACK",
            "im so hyped", "im so pumped", "tomorrow can't come fast enough",
            "this is the best news ever", "WOOO", "woohoo",
        ],
        "long_seeds": [
            "Just bought tickets to the concert and I am literally vibrating with excitement, this is going to be the best night.",
            "Tomorrow is the day I've been waiting months for and I genuinely cannot sit still, I'm so pumped.",
            "I just got accepted and I'm running around the room screaming, this changes everything for me.",
            "Three more days until vacation and I am hyped beyond belief, already packed and ready.",
            "Cannot believe this is actually happening, I've been waiting forever and now it's finally here.",
        ],
    },
    # ------------------------------------------------------------- relaxed
    "relaxed": {
        "feelings": [
            "relaxed", "chill", "so chill", "totally chill", "calm", "peaceful",
            "at peace", "zen", "mellow", "easy going right now", "unwinding",
            "decompressing", "in chill mode", "vibing quietly", "soft and cozy",
            "comfortable", "settled", "feeling serene", "tranquil",
            "in a cozy mood", "no stress vibes",
        ],
        "triggers": [
            "", "tonight", "this evening", "this morning", "right now",
            "after a long week", "on this lazy sunday", "with a book and tea",
            "on the couch", "in bed",
        ],
        "reactions": [
            "ahhh this feels good", "this is the life", "no stress",
            "just vibing", "vibing quietly", "no thoughts head empty",
            "tea and a book kinda night", "candle on, music low",
            "cozy season", "lazy sunday", "self care day",
            "blanket fort time", "rainy day no plans",
            "low key perfect evening", "i love quiet nights",
        ],
        "long_seeds": [
            "Lit a candle, put on slow music, made some tea — this is exactly the kind of evening I needed.",
            "No plans, no obligations, just me and a book on the couch with the rain outside. Perfect.",
            "Slept in, made a slow breakfast, took my time with everything. I forgot how good this feels.",
            "Long bath, soft pajamas, lavender everywhere — completely at peace right now.",
            "Sunday mornings like this are the reason I love staying in. Just calm and quiet.",
        ],
    },
    # ------------------------------------------------------------- stressed
    "stressed": {
        "feelings": [
            "stressed", "so stressed", "stressed out", "stressed af", "overwhelmed",
            "anxious", "frazzled", "burnt out", "burned out", "wired",
            "running on fumes", "drowning", "behind on everything",
            "tense", "on edge", "nervous", "panicking", "freaking out",
            "spiraling", "losing it", "at my limit", "maxed out",
        ],
        "triggers": [
            "", "right now", "this week", "about the deadline", "with work",
            "with school", "with exams", "with this project", "about money",
            "again", "for no reason", "for too many reasons",
        ],
        "reactions": [
            "i can't even", "i can't do this", "too much going on",
            "overloaded", "deadline tomorrow", "haven't slept",
            "my brain is fried", "running on coffee", "no time to breathe",
            "everything is on fire", "this is too much", "im drowning rn",
            "spiraling fr", "panic mode", "my heart is racing",
            "can't sit still", "feel like im falling apart",
        ],
        "long_seeds": [
            "I have three deadlines this week, two meetings tomorrow, and I haven't slept properly in days — I'm losing it.",
            "Work has been absolutely insane and my inbox is at 400 unread emails, I don't even know where to start.",
            "Finals week is brutal, I've been living on coffee and energy drinks and my anxiety is through the roof.",
            "Bills are piling up, I'm behind on everything, and I just feel like I'm constantly running and getting nowhere.",
            "I keep waking up at 3am with my mind racing about all the things I haven't done, this is unsustainable.",
        ],
    },
    # ------------------------------------------------------------- dark
    "dark": {
        "feelings": [
            "angry", "furious", "pissed", "pissed off", "raging", "fuming",
            "livid", "seething", "boiling", "bitter", "resentful",
            "in a dark mood", "feeling vicious", "feeling violent (not literally)",
            "ready to fight someone", "out for blood", "feeling cynical",
            "full of hate", "disgusted", "morbid", "twisted right now",
            "in a sinister mood",
        ],
        "triggers": [
            "", "right now", "about that", "after what they did",
            "today", "again", "about this whole situation",
        ],
        "reactions": [
            "i could scream", "i hate everyone", "i hate everything",
            "everything is awful", "people suck", "this world is messed up",
            "want to break something", "ready to throw hands",
            "im so angry rn", "fuming", "pissed beyond words",
            "this is bullshit", "absolute betrayal", "i'm done",
            "burn it down", "no mercy", "i could ruin them",
        ],
        "long_seeds": [
            "I cannot believe what they did, I am genuinely furious and I don't think I'll forgive this for a long time.",
            "Everything about today made me angrier and angrier until I just snapped, I'm seething right now.",
            "I'm so tired of the same lies and the same broken promises, my patience is completely gone.",
            "There's a darkness to my mood today that I can't shake, feel like I just want to be alone with my anger.",
            "Watching the world burn around me and honestly I'm too tired to even care anymore, just bitter.",
        ],
    },
    # ------------------------------------------------------------- emotional
    "emotional": {
        "feelings": [
            "emotional", "really emotional", "all in my feelings", "in my feelings",
            "soft right now", "tender", "vulnerable", "raw", "all teared up",
            "tearing up", "choked up", "welled up", "moved", "touched",
            "deeply moved", "overwhelmed by feelings", "hit me hard",
            "hit me in the feels", "in my feels", "sentimental",
            "feeling everything at once",
        ],
        "triggers": [
            "", "tonight", "about everything", "thinking about my parents",
            "watching that scene", "after that letter", "after that hug",
            "for no real reason", "after that song came on",
        ],
        "reactions": [
            "i'm tearing up", "this got me", "this hit different",
            "right in the feels", "im so touched", "im so moved",
            "this is making me cry", "the way this got me", "ugh my heart",
            "my heart is full", "my heart hurts", "this means a lot",
            "im a mess rn", "in my feels tonight", "no words",
        ],
        "long_seeds": [
            "Watching old home videos tonight and I just keep crying, the people, the laughs, time goes by way too fast.",
            "Got a letter from my grandma after years and reading it I just broke down, in the best and worst way.",
            "My friend reminded me of something I did for them years ago and now I'm sitting here crying at my desk.",
            "Sometimes a single song will hit me out of nowhere and I'll just sit there with tears streaming down.",
            "I don't even know how to describe what I'm feeling, it's heavy and warm and sad and beautiful all at once.",
        ],
    },
    # ------------------------------------------------------------- mind-bending
    "mind-bending": {
        "feelings": [
            "confused", "so confused", "lost", "mind blown", "mindblown",
            "head spinning", "brain melting", "tripping out", "questioning reality",
            "in an existential crisis", "having an existential moment",
            "deep in thought", "philosophical", "lost in thought",
            "stuck on this idea", "spiraling intellectually", "bending my brain",
            "trippy thoughts", "surreal feeling", "disoriented",
        ],
        "triggers": [
            "", "lately", "tonight", "about what they said",
            "about the meaning of it all", "about that movie",
            "after reading that", "all day",
        ],
        "reactions": [
            "wait what", "wait wait wait", "what does this even mean",
            "this is so trippy", "my brain hurts", "mind = blown",
            "is this real", "are we living in a simulation",
            "this movie broke me", "i don't understand anything anymore",
            "philosophy hits hard at 3am", "thinking too hard rn",
            "what is reality", "everything is so weird", "i need to lie down",
        ],
        "long_seeds": [
            "Just finished a movie that completely scrambled my brain, I have so many questions and no answers, this is wild.",
            "Was reading about quantum mechanics and now I'm staring at the ceiling wondering if anything is even real.",
            "The more I think about consciousness the less it makes sense, like what even is a self, what is anything.",
            "That book has me questioning every assumption I've ever had, my whole worldview is shifting.",
            "Sat up till 3am with my friend talking about time and free will and now I cannot fall asleep at all.",
        ],
    },
    # ------------------------------------------------------------- curious
    "curious": {
        "feelings": [
            "curious", "so curious", "really curious", "intrigued", "fascinated",
            "interested", "really interested", "wondering", "asking questions",
            "in research mode", "in a learning mood", "deep diving",
            "going down a rabbit hole", "obsessed with finding out",
            "dying to know", "trying to figure it out", "investigating",
        ],
        "triggers": [
            "", "about this", "about how things work", "about that topic",
            "lately", "ever since I read that", "after listening to that podcast",
        ],
        "reactions": [
            "wait how does that even work", "tell me everything",
            "i need to know more", "wikipedia rabbit hole",
            "googling this for hours", "this is fascinating",
            "i love learning about this", "i could talk about this all day",
            "asking too many questions", "deep dive time", "wait but why",
        ],
        "long_seeds": [
            "Started reading about ancient civilizations and now I cannot stop, every link leads to another rabbit hole.",
            "How does a piano even produce sound mechanically, I need to know everything about how instruments work.",
            "I love when a documentary makes me realize how little I actually know about something this common.",
            "Spent the whole afternoon learning about how the brain encodes memories and I'm completely fascinated.",
            "Was talking with my friend about black holes and now I have like fifty more questions about physics.",
        ],
    },
    # ------------------------------------------------------------- nostalgic
    "nostalgic": {
        "feelings": [
            "nostalgic", "so nostalgic", "feeling nostalgic", "reminiscing",
            "missing the old days", "longing for the past", "stuck in memories",
            "thinking about the good old days", "in a nostalgic mood",
            "transported back in time", "remembering everything",
            "remembering when", "lost in memories", "throwback mood",
        ],
        "triggers": [
            "", "tonight", "lately", "today", "this evening",
            "about high school", "about college", "about my childhood",
            "about that summer", "every time I hear this song",
        ],
        "reactions": [
            "remember when", "those days were the best", "miss being a kid",
            "high school hits different now", "i miss the 2000s",
            "that song takes me back", "best summer ever", "where did the time go",
            "we were so young", "i miss that version of me",
            "the smell of summer rain", "childhood backyard vibes",
            "old school never dies", "throwback thursday",
        ],
        "long_seeds": [
            "Found an old box of photos from middle school today and spent two hours just looking through every single one.",
            "Heard a song from like 2007 on the radio and was instantly back in my mom's car on the way to school.",
            "Drove through my old neighborhood today and so many memories came flooding back, time really flies.",
            "Going through high school yearbooks and missing everyone, even the people I haven't talked to in years.",
            "There's something about summer evenings that always sends me right back to being eleven years old.",
        ],
    },
    # ------------------------------------------------------------- motivated
    "motivated": {
        "feelings": [
            "motivated", "so motivated", "fired up", "driven", "determined",
            "locked in", "in beast mode", "in grind mode", "on a mission",
            "ready to work", "feeling unstoppable", "feeling capable",
            "feeling powerful", "ambitious", "all about my goals",
            "in the zone", "focused", "dialed in", "ready to crush it",
            "ready to win", "ready to outwork everyone",
        ],
        "triggers": [
            "", "right now", "today", "this morning", "this week",
            "for the new year", "for this season", "for this goal",
            "after that talk", "after that workout",
        ],
        "reactions": [
            "let's go", "lfg", "locked in", "no days off", "rise and grind",
            "5am club", "in the gym", "studying for hours",
            "writing the paper", "shipping the project", "no excuses",
            "discipline > motivation", "outwork everyone", "build the empire",
            "the comeback starts today", "we keep going", "i won't stop",
        ],
        "long_seeds": [
            "Up at 5am, workout done, three hours of deep work, and I'm just getting started, I love this version of me.",
            "Finally got my act together and built a plan for the next six months, I'm not letting anything stop me.",
            "I'm going to read more, train harder, save more — this is the year everything changes for me.",
            "The goals are big, the plan is real, and I'm done waiting for the perfect time, starting today.",
            "Watched a documentary on athletes and now I want to channel that level of discipline into my own life.",
        ],
    },
    # ------------------------------------------------------------- adventurous
    "adventurous": {
        "feelings": [
            "adventurous", "feeling adventurous", "in adventure mode",
            "wanderlust hitting hard", "craving an adventure",
            "ready for the wild", "down to explore", "ready to roam",
            "got the travel bug", "itching to travel", "ready for a trip",
            "in the mood to explore", "in the mood for the outdoors",
            "feeling bold", "ready for something new",
        ],
        "triggers": [
            "", "this summer", "next month", "this weekend", "right now",
            "out here in the mountains", "out in the woods", "out on the road",
        ],
        "reactions": [
            "let's hit the road", "road trip time", "passport ready",
            "booking the flight", "let's go hiking", "summit time",
            "tent packed", "trail calling", "campfire vibes",
            "no plans just vibes", "off grid for a week",
            "one way ticket", "let's get lost", "mountain calling",
        ],
        "long_seeds": [
            "Got back from a four day backpacking trip in the mountains and honestly I want to go right back out there.",
            "Booked a one way ticket to a country I've never been to and I've never felt more alive in my life.",
            "Spent the weekend climbing and camping and waking up to sunrises like nothing I've ever seen.",
            "Road trip with the windows down, no destination, just exploring tiny towns — this is freedom.",
            "Trekking through jungle for three days, sleeping under stars, drinking from rivers — pure adventure.",
        ],
    },
    # ------------------------------------------------------------- wholesome
    "wholesome": {
        "feelings": [
            "grateful", "so grateful", "thankful", "warm inside", "blessed",
            "loved", "cared for", "lifted up", "feeling soft", "feeling sweet",
            "in a wholesome mood", "appreciated", "valued", "warm hearted",
            "full of love", "full of warmth", "really touched in a good way",
        ],
        "triggers": [
            "", "today", "tonight", "lately", "by my family", "by my friends",
            "by my partner", "by a stranger today",
        ],
        "reactions": [
            "the small things", "my heart is full", "love my family",
            "love my friends", "good people are out there",
            "my dog is the best", "kids are the best", "people are kind",
            "this made my whole week", "such a sweet moment",
            "feeling so loved", "warm fuzzies", "this is what life is about",
            "humanity restored", "faith in people restored",
        ],
        "long_seeds": [
            "A stranger paid for my coffee today and said have a good one, and honestly it made my whole week.",
            "My little nephew drew me a picture and told me I'm his favorite person and now I'm a puddle.",
            "Family dinner tonight, everyone laughing around the table, the dog under my feet — this is everything.",
            "My partner left me a sticky note on the mirror just to say they're proud of me, I love them so much.",
            "Helped an old lady carry her groceries and she squeezed my hand and called me dear, my heart melted.",
        ],
    },
    # ------------------------------------------------------------- scared
    "scared": {
        "feelings": [
            "scared", "so scared", "terrified", "petrified", "freaked out",
            "spooked", "creeped out", "shaking", "trembling", "afraid",
            "really afraid", "frightened", "horrified", "on edge",
            "jumpy", "nervous", "paranoid", "got the creeps", "got chills",
            "hair standing on end",
        ],
        "triggers": [
            "", "right now", "tonight", "in this house", "alone at night",
            "after that noise", "after that movie", "watching this",
            "every time I hear it",
        ],
        "reactions": [
            "what was that noise", "im not okay", "i hate this",
            "this is scary", "im hiding under the covers",
            "checking every door", "leaving the light on",
            "i heard footsteps", "this house is haunted",
            "every shadow is moving", "im paranoid rn",
            "couldn't sleep at all", "movie ruined me",
        ],
        "long_seeds": [
            "Heard a noise downstairs at like 3am and I'm under the covers afraid to move, this is genuinely terrifying.",
            "Watched a horror movie I shouldn't have and now I'm convinced something is in my closet, sleeping with the light on.",
            "Walking home alone tonight and every shadow looked like a person, my heart was pounding the whole way.",
            "Something keeps creaking in this house and I am too scared to go check what it is.",
            "I was alone in the office at night and I swear I heard footsteps in the empty hallway, I sprinted out.",
        ],
    },
}

# --------------------------------------------------------------------------
# 2. STYLE TRANSFORMERS
# --------------------------------------------------------------------------
# Each transformer takes a generated sentence and (probabilistically) modifies
# it. Multiple transformers can stack to produce gen-z lowercase, typo-laden,
# emoji-stripped variants.

def _maybe(p: float, rng: random.Random) -> bool:
    return rng.random() < p


def _typo(word: str, rng: random.Random) -> str:
    """Introduce a small realistic typo: swap, drop, double or wrong-key."""
    if len(word) < 4:
        return word
    op = rng.choice(["swap", "drop", "double", "neighbor"])
    i = rng.randint(1, len(word) - 2)
    if op == "swap":
        return word[:i] + word[i + 1] + word[i] + word[i + 2:]
    if op == "drop":
        return word[:i] + word[i + 1:]
    if op == "double":
        return word[:i] + word[i] + word[i:]
    if op == "neighbor":
        # rough qwerty neighbor map
        neighbors = {"a": "s", "s": "d", "d": "f", "f": "g", "e": "r",
                     "r": "t", "t": "y", "o": "i", "i": "u", "n": "m"}
        ch = word[i].lower()
        return word[:i] + neighbors.get(ch, ch) + word[i + 1:]
    return word


def style_lowercase(text: str, rng: random.Random) -> str:
    return text.lower()


def style_dropdots(text: str, rng: random.Random) -> str:
    return re.sub(r"[.,!?]", "", text)


def style_lengthen(text: str, rng: random.Random) -> str:
    """Stretch a random vowel (e.g. 'so' -> 'soooo')."""
    words = text.split()
    if not words:
        return text
    i = rng.randrange(len(words))
    w = words[i]
    for vowel in "aeiou":
        if vowel in w:
            words[i] = w.replace(vowel, vowel * rng.randint(3, 5), 1)
            break
    return " ".join(words)


def style_typoize(text: str, rng: random.Random) -> str:
    words = text.split()
    if not words:
        return text
    # 1-2 typos in long-ish sentences
    n = max(1, len(words) // 12)
    for _ in range(n):
        i = rng.randrange(len(words))
        words[i] = _typo(words[i], rng)
    return " ".join(words)


def style_strip_punct(text: str, rng: random.Random) -> str:
    return re.sub(r"[!?.,;:]+", "", text)


def style_genz_swap(text: str, rng: random.Random) -> str:
    """Replace common phrases with chat shortcuts."""
    swaps = {
        r"\bI am\b": "im", r"\bIm\b": "im", r"\bI'm\b": "im",
        r"\byou are\b": "ur", r"\byou're\b": "ur",
        r"\bbecause\b": "bc", r"\bright now\b": "rn",
        r"\bnot gonna lie\b": "ngl", r"\bto be honest\b": "tbh",
        r"\bI don't know\b": "idk", r"\bfor real\b": "fr",
        r"\bI swear\b": "iswear", r"\boh my god\b": "omg",
        r"\bI guess\b": "iguess", r"\bkind of\b": "kinda",
    }
    out = text
    for pat, repl in swaps.items():
        if _maybe(0.45, rng):
            out = re.sub(pat, repl, out, flags=re.I)
    return out


def style_add_emoji(text: str, rng: random.Random, mood: str) -> str:
    pool = {
        "happy": ["😊", "😄", "🥳", "🎉"],
        "sad": ["😢", "😭", "💔", "😞"],
        "lonely": ["😔", "🥺"],
        "romantic": ["❤️", "💕", "🥰", "😍"],
        "excited": ["🤩", "🔥", "⚡", "🎉"],
        "relaxed": ["😌", "🧘", "🌿", "🕯️"],
        "stressed": ["😰", "😩", "🤯"],
        "dark": ["🖤", "💀", "😈"],
        "emotional": ["🥲", "🥹", "😥"],
        "mind-bending": ["🌀", "🧠", "🔮"],
        "curious": ["🤔", "🧐"],
        "nostalgic": ["📸", "🌅"],
        "motivated": ["💪", "🏆", "🚀"],
        "adventurous": ["🏔️", "✈️", "🗺️"],
        "wholesome": ["🤗", "☀️", "🌸"],
        "scared": ["😱", "👻", "😨"],
    }
    emojis = pool.get(mood, [])
    if not emojis:
        return text
    n = rng.randint(1, 2)
    addition = "".join(rng.choice(emojis) for _ in range(n))
    return f"{text} {addition}"


def style_cap_yell(text: str, rng: random.Random) -> str:
    return text.upper()


# --------------------------------------------------------------------------
# 3. SENTENCE COMPOSERS
# --------------------------------------------------------------------------

def _short_reaction(mood: str, rng: random.Random) -> str:
    return rng.choice(MOOD_TEMPLATES[mood]["reactions"])


def _medium_sentence(mood: str, rng: random.Random) -> str:
    """Compose ${subject} (am/is) ${intensifier} ${feeling} ${trigger}."""
    t = MOOD_TEMPLATES[mood]
    subj = rng.choice(SUBJECTS)
    inten = rng.choice(INTENSIFIERS)
    feel = rng.choice(t["feelings"])
    trig = rng.choice(t["triggers"])

    if subj in ("I", "i", "im", "i'm", "I'm"):
        verb = ""
        if subj.lower() in ("i",):
            verb = "am"
        sub_disp = subj
        if subj.lower() == "i" and rng.random() < 0.5:
            verb = "am"
        if verb:
            core = f"{sub_disp} {verb} {inten} {feel}".strip()
        else:
            # "i'm so excited"
            core = f"{sub_disp} {inten} {feel}".strip()
    else:
        verb = "is"
        if subj in ("we", "they", "everyone"):
            verb = "are" if subj != "everyone" else "is"
        core = f"{subj} {verb} {inten} {feel}".strip()

    core = re.sub(r"\s+", " ", core).strip()
    if trig:
        core = f"{core} {trig}"
    return core


def _long_sentence(mood: str, rng: random.Random) -> str:
    return rng.choice(MOOD_TEMPLATES[mood]["long_seeds"])


# --------------------------------------------------------------------------
# 4. SAMPLE GENERATION
# --------------------------------------------------------------------------

def _generate_one(mood: str, rng: random.Random) -> str:
    """Produce a single labelled sentence for `mood`."""
    # Pick a base form
    roll = rng.random()
    if roll < 0.32:
        text = _short_reaction(mood, rng)
    elif roll < 0.85:
        text = _medium_sentence(mood, rng)
    else:
        text = _long_sentence(mood, rng)

    # Optional casual head / tail
    if _maybe(0.20, rng):
        text = rng.choice(CASUAL_HEADS) + text
    if _maybe(0.25, rng):
        text = text + rng.choice(CASUAL_TAILS)

    # Stack styles probabilistically
    if _maybe(0.45, rng):
        text = style_lowercase(text, rng)
    if _maybe(0.20, rng):
        text = style_strip_punct(text, rng)
    if _maybe(0.18, rng):
        text = style_genz_swap(text, rng)
    if _maybe(0.10, rng):
        text = style_lengthen(text, rng)
    if _maybe(0.08, rng):
        text = style_typoize(text, rng)
    if _maybe(0.18, rng):
        text = style_add_emoji(text, rng, mood)
    if _maybe(0.015, rng):
        text = style_cap_yell(text, rng)

    return re.sub(r"\s+", " ", text).strip()


def generate(per_class: int = 6000, seed: int = 1337) -> pd.DataFrame:
    rng = random.Random(seed)
    rows: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for mood in MOOD_TEMPLATES:
        produced = 0
        attempts = 0
        while produced < per_class and attempts < per_class * 8:
            attempts += 1
            text = _generate_one(mood, rng)
            if len(text) < 3:
                continue
            key = (mood, text)
            if key in seen:
                continue
            seen.add(key)
            rows.append((text, mood))
            produced += 1
        print(f"[synth] {mood:13s} produced {produced} (attempts: {attempts})")

    df = pd.DataFrame(rows, columns=["text", "mood"])
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    out_csv = os.path.join(here, "synthetic_mood_data.csv")
    df = generate(per_class=6000, seed=1337)
    print(f"\n[synth] total rows: {len(df)}")
    print(f"[synth] class counts:\n{df['mood'].value_counts()}")
    df.to_csv(out_csv, index=False)
    print(f"[synth] wrote {out_csv}")


if __name__ == "__main__":
    main()
