import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_tempo: Optional[float] = None

# Named weight profiles ("ranking strategies"), each summing to 1.0 so a
# perfect-match song scores exactly 1.0. Every profile scores the same five
# components (genre, mood, energy, tempo, acoustic) - only how much each one
# counts changes, so switching strategies re-ranks the same catalog rather
# than changing what's measured.
WEIGHT_PROFILES: Dict[str, Dict[str, float]] = {
    # Our original, finalized Algorithm Recipe (see README "How The System
    # Works"): genre identity first, mood second, then numeric closeness.
    "genre_first": {
        "genre": 0.35,
        "mood": 0.25,
        "energy": 0.20,
        "tempo": 0.10,
        "acoustic": 0.10,
    },
    # Leads with mood instead of genre, for users who care more about how a
    # song feels than its genre label.
    "mood_first": {
        "genre": 0.25,
        "mood": 0.35,
        "energy": 0.20,
        "tempo": 0.10,
        "acoustic": 0.10,
    },
    # Leads with energy/tempo "vibe" and treats genre/mood as secondary -
    # for users who want a workout-style ranking driven mostly by intensity.
    "energy_focused": {
        "genre": 0.20,
        "mood": 0.20,
        "energy": 0.35,
        "tempo": 0.15,
        "acoustic": 0.10,
    },
}

DEFAULT_STRATEGY = "genre_first"


def get_weights(strategy: str) -> Dict[str, float]:
    """Looks up a named weight profile, e.g. get_weights("mood_first")."""
    if strategy not in WEIGHT_PROFILES:
        valid = ", ".join(sorted(WEIGHT_PROFILES))
        raise ValueError(f"Unknown ranking strategy '{strategy}'. Valid options: {valid}")
    return WEIGHT_PROFILES[strategy]

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py

    This class implements the same Algorithm Recipe as score_song() /
    recommend_songs() below, but works directly with Song/UserProfile
    dataclasses instead of dicts. The scoring math is intentionally
    duplicated here rather than shared with the functional API: the two
    APIs take different inputs (dataclasses vs. dicts), and converting
    between them on every call would add coupling and overhead for a
    scoring formula this small. Keeping them independent makes each API
    simple to read and explain on its own, at the cost of ~20 lines of
    repeated logic.
    """
    def __init__(self, songs: List[Song], strategy: str = DEFAULT_STRATEGY):
        self.songs = songs
        self.set_strategy(strategy)

    def set_strategy(self, strategy: str) -> None:
        """
        Switches which named weight profile (see WEIGHT_PROFILES) this
        recommender uses. Affects every _score()/recommend() call that
        follows, until set_strategy() is called again.
        """
        self.strategy = strategy
        self.weights = get_weights(strategy)

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """
        Scores a single Song against a UserProfile using the current
        strategy's weights (weighted genre match, mood match, and
        energy/tempo/acousticness closeness). Mirrors score_song()'s logic.

        Returns (score, reasons) where score is 0-1 and reasons is a
        list of human-readable strings explaining what drove the score.
        """
        weights = self.weights
        reasons: List[str] = []
        score = 0.0

        genre_match = song.genre.lower() == user.favorite_genre.lower()
        if genre_match:
            score += weights["genre"]
            reasons.append(f"matches your favorite genre ({song.genre})")

        mood_match = song.mood.lower() == user.favorite_mood.lower()
        if mood_match:
            score += weights["mood"]
            reasons.append(f"matches your favorite mood ({song.mood})")

        energy_closeness = 1 - min(abs(song.energy - user.target_energy), 1.0)
        score += weights["energy"] * energy_closeness
        if energy_closeness >= 0.85:
            reasons.append(f"energy ({song.energy}) is close to what you want ({user.target_energy})")

        # Tempo preference is optional - only score it if the user stated one.
        if user.target_tempo is not None:
            tempo_distance = abs(song.tempo_bpm - user.target_tempo)
            tempo_closeness = 1 - min(tempo_distance / TEMPO_RANGE, 1.0)
            score += weights["tempo"] * tempo_closeness
            if tempo_closeness >= 0.85:
                reasons.append(f"tempo ({song.tempo_bpm} bpm) is close to what you want ({user.target_tempo} bpm)")

        if user.likes_acoustic:
            score += weights["acoustic"] * song.acousticness
            if song.acousticness >= 0.6:
                reasons.append("has an acoustic feel you tend to like")
        else:
            score += weights["acoustic"] * (1 - song.acousticness)
            if song.acousticness <= 0.3:
                reasons.append("has the non-acoustic energy you tend to like")

        if not reasons:
            reasons.append("a decent overall match on your preferences")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5, artist_penalty: float = 0.0) -> List[Song]:
        """
        Returns the top k Song records for this user.

        Applies our Ranking Rule: score every song with _score(), sort
        by score descending (tie-break by song id ascending for a
        deterministic order), then take the top k.

        artist_penalty is an opt-in anti-repetition/diversity control
        (default 0, i.e. off): each time a song is picked, that much is
        subtracted from the remaining scores of every other song by the
        same artist, so one artist's several close matches can't crowd
        out the rest of the top k (a "filter bubble"). The picked
        songs' original, un-penalized scores are unaffected.
        """
        remaining = [(song, self._score(user, song)[0]) for song in self.songs]
        if artist_penalty == 0.0:
            remaining.sort(key=lambda pair: (-pair[1], pair[0].id))
            return [song for song, _ in remaining[:k]]

        picks: List[Song] = []
        artist_pick_counts: Dict[str, int] = {}
        for _ in range(min(k, len(remaining))):
            remaining.sort(
                key=lambda pair: (
                    -(pair[1] - artist_penalty * artist_pick_counts.get(pair[0].artist, 0)),
                    pair[0].id,
                )
            )
            song, _ = remaining.pop(0)
            picks.append(song)
            artist_pick_counts[song.artist] = artist_pick_counts.get(song.artist, 0) + 1
        return picks

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """
        Returns a human-readable, semicolon-separated explanation of
        why `song` was recommended to `user`, built from the reasons
        generated by _score().
        """
        _, reasons = self._score(user, song)
        return "; ".join(reasons)

INTEGER_FIELDS = {"id"}
FLOAT_FIELDS = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py

    Reads the file with csv.DictReader, which turns every row into a
    dict of column_name -> string value. Since every value from a CSV
    starts out as a string, the fields listed in INTEGER_FIELDS and
    FLOAT_FIELDS are converted to their numeric types so later scoring
    math (e.g. energy_closeness) can operate on real numbers instead
    of text.
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            song = dict(row)
            for field in INTEGER_FIELDS:
                song[field] = int(song[field])
            for field in FLOAT_FIELDS:
                song[field] = float(song[field])
            songs.append(song)
    return songs

# tempo_bpm isn't naturally on a 0-1 scale like the other features, so we
# normalize its distance against an assumed realistic range (ballad to
# drum & bass) before it can be combined with the other components.
TEMPO_MIN = 40
TEMPO_MAX = 200
TEMPO_RANGE = TEMPO_MAX - TEMPO_MIN

def score_song(user_prefs: Dict, song: Dict, strategy: str = DEFAULT_STRATEGY) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Implements the Algorithm Recipe: a weighted sum of a genre match,
    a mood match, and how close the song's energy/tempo/acousticness
    are to what the user wants. Each numeric feature uses a "closeness"
    formula (1 - normalized distance) so being near the target scores
    well, not just being high or low.

    user_prefs keys used: genre, mood, energy, tempo (optional),
    likes_acoustic (optional, default False).

    `strategy` selects which named weight profile from WEIGHT_PROFILES
    to score with (e.g. "genre_first", "mood_first", "energy_focused").

    Returns (score, reasons) where score is 0-1 and reasons is a list
    of human-readable strings explaining what drove the score, so the
    caller can build an explanation for the user.
    """
    weights = get_weights(strategy)
    reasons: List[str] = []
    score = 0.0

    genre_match = song.get("genre", "").lower() == user_prefs.get("genre", "").lower()
    if genre_match:
        score += weights["genre"]
        reasons.append(f"matches your favorite genre ({song.get('genre')})")

    mood_match = song.get("mood", "").lower() == user_prefs.get("mood", "").lower()
    if mood_match:
        score += weights["mood"]
        reasons.append(f"matches your favorite mood ({song.get('mood')})")

    energy = float(song.get("energy", 0.0))
    target_energy = float(user_prefs.get("energy", 0.0))
    energy_closeness = 1 - min(abs(energy - target_energy), 1.0)
    score += weights["energy"] * energy_closeness
    if energy_closeness >= 0.85:
        reasons.append(f"energy ({energy}) is close to what you want ({target_energy})")

    # Tempo preference is optional - only score it if the user stated one.
    target_tempo = user_prefs.get("tempo")
    if target_tempo is not None:
        tempo_bpm = float(song.get("tempo_bpm", 0.0))
        tempo_distance = abs(tempo_bpm - float(target_tempo))
        tempo_closeness = 1 - min(tempo_distance / TEMPO_RANGE, 1.0)
        score += weights["tempo"] * tempo_closeness
        if tempo_closeness >= 0.85:
            reasons.append(f"tempo ({tempo_bpm} bpm) is close to what you want ({target_tempo} bpm)")

    acousticness = float(song.get("acousticness", 0.0))
    likes_acoustic = user_prefs.get("likes_acoustic", False)
    if likes_acoustic:
        score += weights["acoustic"] * acousticness
        if acousticness >= 0.6:
            reasons.append("has an acoustic feel you tend to like")
    else:
        score += weights["acoustic"] * (1 - acousticness)
        if acousticness <= 0.3:
            reasons.append("has the non-acoustic energy you tend to like")

    if not reasons:
        reasons.append("a decent overall match on your preferences")

    return score, reasons

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    strategy: str = DEFAULT_STRATEGY,
    artist_penalty: float = 0.0,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Applies our Ranking Rule: score every song, sort by score descending
    (tie-break by song id ascending for a deterministic order), then take
    the top k. Each result includes a human-readable explanation built
    from score_song's reasons, joined with "; " so callers can split the
    string back into individual reasons for display (e.g. as bullets).

    `strategy` selects which named weight profile to score with (see
    WEIGHT_PROFILES).

    artist_penalty is an opt-in anti-repetition/diversity control
    (default 0, i.e. off): each time a song is picked, that much is
    subtracted from the remaining scores of every other song by the
    same artist, so one artist's several close matches can't crowd out
    the rest of the top k (a "filter bubble"). The reported score for
    each pick is still its original, un-penalized score.
    """
    scored = [(song, *score_song(user_prefs, song, strategy)) for song in songs]

    if artist_penalty == 0.0:
        scored.sort(key=lambda entry: (-entry[1], entry[0].get("id", 0)))
        return [
            (song, score, "; ".join(reasons))
            for song, score, reasons in scored[:k]
        ]

    remaining = scored
    picks: List[Tuple[Dict, float, List[str]]] = []
    artist_pick_counts: Dict[str, int] = {}
    for _ in range(min(k, len(remaining))):
        remaining.sort(
            key=lambda entry: (
                -(entry[1] - artist_penalty * artist_pick_counts.get(entry[0].get("artist"), 0)),
                entry[0].get("id", 0),
            )
        )
        song, score, reasons = remaining.pop(0)
        picks.append((song, score, reasons))
        artist = song.get("artist")
        artist_pick_counts[artist] = artist_pick_counts.get(artist, 0) + 1

    return [(song, score, "; ".join(reasons)) for song, score, reasons in picks]
