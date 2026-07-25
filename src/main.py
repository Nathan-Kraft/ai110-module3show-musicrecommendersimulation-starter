"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from tabulate import tabulate

from recommender import load_songs, recommend_songs, Recommender, Song, UserProfile, WEIGHT_PROFILES, DEFAULT_STRATEGY

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
    Prints a ranked list of recommendations as a table: rank, title, artist,
    score out of 100, and the specific reasons behind each score, with a
    divider between each song.

    Accepts either the functional API's (song_dict, score, explanation)
    tuples or (Song, score, explanation) tuples, since both share the
    same shape.
    """
    print(f"\n{title}\n" + "-" * len(title))

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        title_field = song["title"] if isinstance(song, dict) else song.title
        artist_field = song["artist"] if isinstance(song, dict) else song.artist
        reasons = "\n".join(f"- {reason}" for reason in explanation.split("; "))
        rows.append([rank, title_field, artist_field, f"{round(score * 100)}/100", reasons])
    print(tabulate(rows, headers=["Rank", "Title", "Artist", "Score", "Reasons"], tablefmt="grid"))
    print()


def prompt_for_strategy(default: str) -> str:
    """
    Asks the user to pick a ranking strategy by name, showing the available
    options from WEIGHT_PROFILES. Pressing Enter accepts `default`; an
    unrecognized name re-prompts instead of silently falling back.
    """
    options = ", ".join(WEIGHT_PROFILES)
    while True:
        choice = input(f"Choose a ranking strategy [{options}] (default: {default}): ").strip()
        if not choice:
            return default
        if choice in WEIGHT_PROFILES:
            return choice
        print(f"Unknown strategy '{choice}'. Valid options: {options}")


ARTIST_PENALTY_AMOUNT = 0.15


def prompt_for_artist_penalty() -> float:
    """
    Asks the user whether to turn on the artist-diversity penalty (see
    recommender.apply_artist_penalty via recommend()/recommend_songs()).
    Returns ARTIST_PENALTY_AMOUNT if they opt in, 0.0 (off) otherwise -
    pressing Enter keeps the plain highest-score ranking.
    """
    choice = input("Penalize repeat artists to encourage variety? [y/N]: ").strip().lower()
    return ARTIST_PENALTY_AMOUNT if choice in ("y", "yes") else 0.0


def run_demo(recommender: Recommender, song_dicts, artist_penalty: float = 0.0) -> None:
    """Runs the functional + OOP demo using the recommender's current strategy."""
    strategy = recommender.strategy

    # --- Functional API demo (dict-based) ---
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    recommendations = recommend_songs(user_prefs, song_dicts, k=5, strategy=strategy, artist_penalty=artist_penalty)
    print_recommendations(
        f"Functional API [strategy={strategy}, artist_penalty={artist_penalty}]: genre=pop, mood=happy, energy=0.8",
        recommendations,
    )

    # --- OOP API demo (Recommender class, run across several sample profiles) ---
    for label, profile in SAMPLE_PROFILES:
        top_songs = recommender.recommend(profile, k=5, artist_penalty=artist_penalty)
        recs = []
        for song in top_songs:
            score, reasons = recommender._score(profile, song)
            recs.append((song, score, "; ".join(reasons)))
        print_recommendations(f"OOP API [strategy={strategy}, artist_penalty={artist_penalty}]: {label}", recs)


def main() -> None:
    # Load and parse the catalog. load_songs converts numeric CSV columns
    # (energy, tempo_bpm, etc.) to int/float so score_song can do math on them.
    song_dicts = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(song_dicts)}")

    songs = [Song(**song) for song in song_dicts]
    strategy = prompt_for_strategy(DEFAULT_STRATEGY)
    artist_penalty = prompt_for_artist_penalty()
    recommender = Recommender(songs, strategy=strategy)

    while True:
        run_demo(recommender, song_dicts, artist_penalty)

        options = ", ".join(WEIGHT_PROFILES)
        again = input(
            f"\nSwitch strategy? Enter a name [{options}], or press Enter to quit: "
        ).strip()
        if not again:
            break
        if again not in WEIGHT_PROFILES:
            print(f"Unknown strategy '{again}'. Valid options: {options}")
            continue
        recommender.set_strategy(again)


if __name__ == "__main__":
    main()
