"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    # Load and parse the catalog. load_songs converts numeric CSV columns
    # (energy, tempo_bpm, etc.) to int/float so score_song can do math on them.
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    # Score every song against user_prefs, rank by our Ranking Rule (score
    # descending, tie-break by id), and keep the top k with explanations.
    recommendations = recommend_songs(user_prefs, songs, k=5)

    # Display each recommendation: rank + title/artist + score out of 100,
    # followed by the specific reasons score_song generated, one per line.
    print("\nTop recommendations:\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        display_score = round(score * 100)
        print(f"{rank}. {song['title']} ({song['artist']}) - Score: {display_score}/100")
        for reason in explanation.split("; "):
            print(f"   - {reason}")
        print()


if __name__ == "__main__":
    main()
