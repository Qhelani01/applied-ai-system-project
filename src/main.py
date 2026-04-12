"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


# Define distinct user preference profiles
USER_PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "tempo_bpm": 120
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "tempo_bpm": 80
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.90,
        "tempo_bpm": 145
    },
    "Relaxed Jazz": {
        "genre": "jazz",
        "mood": "relaxed",
        "energy": 0.40,
        "tempo_bpm": 90
    },
    "Electronic Vibes": {
        "genre": "electronic",
        "mood": "energetic",
        "energy": 0.92,
        "tempo_bpm": 128
    },
}

# Adversarial/Edge-case profiles designed to stress-test the algorithm
ADVERSARIAL_PROFILES = {
    "High-Energy Sad": {
        "genre": "indie pop",
        "mood": "melancholic",
        "energy": 0.95,
        "description": "Conflicting preferences: wants sad/melancholic mood but high energy (unusual combo)"
    },
    "Acoustic Metal": {
        "genre": "metal",
        "mood": "dark",
        "energy": 0.88,
        "likes_acoustic": True,
        "description": "Paradoxical: wants metal (usually electronic) but prefers acoustic instruments"
    },
    "Extreme Low Energy": {
        "genre": "rock",
        "mood": "uplifting",
        "energy": 0.05,
        "description": "Conflicting: wants upliftng mood but extremely low energy"
    },
    "Rare Combo: Reggae Classical": {
        "genre": "reggae",
        "mood": "contemplative",
        "energy": 0.32,
        "description": "Unusual mood+genre: contemplative reggae (rare in small catalog)"
    },
    "Genre Mismatch: Happy Metal": {
        "genre": "metal",
        "mood": "playful",
        "energy": 0.85,
        "description": "Contradictory: playful mood + metal genre (typically dark/intense)"
    },
    "Nonexistent Genre": {
        "genre": "dubstep",
        "mood": "focused",
        "energy": 0.75,
        "description": "Stress test: requests genre that doesn't exist in catalog"
    },
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"✓ Loaded {len(songs)} songs\n")
    print("=" * 80)

    # Test recommender across multiple user profiles
    print("\n📊 STANDARD USER PROFILES:\n")
    for profile_name, user_prefs in USER_PROFILES.items():
        print(f"🎵 {profile_name}")
        print(f"   Preferences: Genre={user_prefs['genre']}, Mood={user_prefs['mood']}, Energy={user_prefs['energy']}")
        print("-" * 80)

        recommendations = recommend_songs(user_prefs, songs, k=5)

        for i, rec in enumerate(recommendations, start=1):
            song, score, explanation = rec
            print(f"  {i}. {song['title']} by {song['artist']}")
            print(f"     Score: {score:.2f}/5.8 | {explanation}")
        print()

    # Test adversarial/edge-case profiles
    print("\n" + "=" * 80)
    print("⚠️  ADVERSARIAL/EDGE-CASE PROFILES (Stress Testing):\n")
    for profile_name, user_prefs in ADVERSARIAL_PROFILES.items():
        description = user_prefs.pop("description", "")
        print(f"🎯 {profile_name}")
        print(f"   {description}")
        print(f"   Preferences: Genre={user_prefs['genre']}, Mood={user_prefs['mood']}, Energy={user_prefs['energy']}")
        print("-" * 80)

        recommendations = recommend_songs(user_prefs, songs, k=5)

        for i, rec in enumerate(recommendations, start=1):
            song, score, explanation = rec
            print(f"  {i}. {song['title']} by {song['artist']}")
            print(f"     Score: {score:.2f}/5.8 | {explanation}")
        print()



if __name__ == "__main__":
    main()
