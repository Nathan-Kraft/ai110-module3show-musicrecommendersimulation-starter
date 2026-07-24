"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs, Recommender, Song, UserProfile

# Sample user profiles used to demonstrate the Recommender (OOP) class
# against a range of tastes, including a couple of deliberate edge cases
# where a user's stated preferences pull the score in different directions.
taste_profile = UserProfile(
    favorite_genre="rock",
    favorite_mood="intense",   # randomly chosen
    target_energy=0.65,
    likes_acoustic=False,      # randomly chosen
    target_tempo=140,          # randomly chosen (bpm)
)

high_energy_pop_profile = UserProfile(
    favorite_genre="High-Energy Pop",
    favorite_mood="euphoric",
    target_energy=0.9,
    likes_acoustic=False,
    target_tempo=128,
)

chill_lofi_profile = UserProfile(
    favorite_genre="Chill Lofi",
    favorite_mood="relaxed",
    target_energy=0.25,
    likes_acoustic=True,
    target_tempo=75,
)

deep_intense_rock_profile = UserProfile(
    favorite_genre="Deep Intense Rock",
    favorite_mood="intense",
    target_energy=0.8,
    likes_acoustic=False,
    target_tempo=140,
)

# Edge case: wants a high-energy, fast rock song but says the mood should be
# "sad" and that they like acoustic textures - traits that pull toward
# opposite ends of the dataset (rock/intense songs here are loud and
# non-acoustic), so genre/energy/tempo scoring and mood/acoustic scoring
# should pull the ranking in different directions.
conflicted_energy_mood_profile = UserProfile(
    favorite_genre="rock",
    favorite_mood="sad",
    target_energy=0.95,
    likes_acoustic=True,
    target_tempo=170,
)

# Edge case: picks "classical" as favorite genre (typically slow and
# acoustic in this dataset) but asks for a euphoric mood, near-max energy,
# a non-acoustic sound, and a very slow target tempo - so even a perfect
# genre match still clashes with every other stated preference.
mismatched_genre_expectations_profile = UserProfile(
    favorite_genre="classical",
    favorite_mood="euphoric",
    target_energy=0.9,
    likes_acoustic=False,
    target_tempo=60,
)

SAMPLE_PROFILES = [
    ("Taste Profile", taste_profile),
    ("High-Energy Pop Fan", high_energy_pop_profile),
    ("Chill Lofi Fan", chill_lofi_profile),
    ("Deep Intense Rock Fan", deep_intense_rock_profile),
    ("Conflicted Energy/Mood Edge Case", conflicted_energy_mood_profile),
    ("Mismatched Genre Expectations Edge Case", mismatched_genre_expectations_profile),
]


def print_recommendations(title: str, recommendations) -> None:
    """
    Prints a ranked list of recommendations: rank + title/artist + score
    out of 100, followed by the specific reasons behind each score, one
    per line.

    Accepts either the functional API's (song_dict, score, explanation)
    tuples or (Song, score, explanation) tuples, since both share the
    same shape.
    """
    print(f"\n{title}\n" + "-" * len(title))
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        display_score = round(score * 100)
        title_field = song["title"] if isinstance(song, dict) else song.title
        artist_field = song["artist"] if isinstance(song, dict) else song.artist
        print(f"{rank}. {title_field} ({artist_field}) - Score: {display_score}/100")
        for reason in explanation.split("; "):
            print(f"   - {reason}")
        print()


def main() -> None:
    # Load and parse the catalog. load_songs converts numeric CSV columns
    # (energy, tempo_bpm, etc.) to int/float so score_song can do math on them.
    song_dicts = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(song_dicts)}")

    # --- Functional API demo (dict-based) ---
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    recommendations = recommend_songs(user_prefs, song_dicts, k=5)
    print_recommendations("Functional API: genre=pop, mood=happy, energy=0.8", recommendations)

    # --- OOP API demo (Recommender class, run across several sample profiles) ---
    songs = [Song(**song) for song in song_dicts]
    recommender = Recommender(songs)

    for label, profile in SAMPLE_PROFILES:
        top_songs = recommender.recommend(profile, k=5)
        recs = []
        for song in top_songs:
            score, reasons = recommender._score(profile, song)
            recs.append((song, score, "; ".join(reasons)))
        print_recommendations(f"OOP API: {label}", recs)


if __name__ == "__main__":
    main()
