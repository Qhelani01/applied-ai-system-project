"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"✓ Loaded {len(songs)} songs\n")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    print(f"User Profile: Genre={user_prefs['genre']}, Mood={user_prefs['mood']}, Energy={user_prefs['energy']}")
    print("=" * 70)

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\n🎵 Top 5 Recommendations:\n")
    for i, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        print(f"{i}. {song['title']}")
        print(f"   Artist: {song['artist']}")
        print(f"   Score:  {score:.2f}/5.8")
        print(f"   Why:    {explanation}")
        print()


if __name__ == "__main__":
    main()
