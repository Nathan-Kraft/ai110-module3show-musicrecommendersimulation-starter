# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

Strategy pattern - swappable ranking algorithms (weight profiles) that share the same scoring interface.

**How did AI help you brainstorm or implement it?**

I asked Claude to add multiple ranking strategies ("Genre-First," "Mood-First," "Energy-Focused") that a user could switch between in `main.py`. Claude first checked whether a "Genre-First" mode already existed and pointed out that the existing code only had one fixed set of weights (`GENRE_WEIGHT`, `MOOD_WEIGHT`, etc.) hardcoded as module-level constants - genre happened to have the largest weight, but there was no way to select a different weighting at runtime.

Claude proposed extracting the weights into named profiles (a dict of dicts: `WEIGHT_PROFILES = {"genre_first": {...}, "mood_first": {...}, "energy_focused": {...}}`) and threading a `strategy` parameter through both the OOP (`Recommender`) and functional (`score_song`/`recommend_songs`) APIs, rather than duplicating the scoring logic once per strategy. This is what a Strategy pattern is: the scoring algorithm (`_score`/`score_song`) stays the same, but the weights it plugs in are selected independently and can be swapped at runtime.

During implementation I asked for more readable code, so we simplified the first draft (which passed a `weights` override into almost every method) down to a single `set_strategy()` method on `Recommender` that swaps `self.weights`, plus an optional `strategy` argument on the functional API. I also asked a clarifying question about how `likes_acoustic` (a boolean) interacts with `acousticness` (a continuous song attribute), which Claude explained before continuing - that flag isn't part of the strategy switch itself, but it confirmed the acoustic term behaves the same way under every weight profile, just scaled by a different weight.

We also caught a real bug during this process: an early version defined `WEIGHT_PROFILES`/`DEFAULT_STRATEGY` after the `Recommender` class but used `DEFAULT_STRATEGY` as a default argument value in `Recommender.__init__`, which would have raised `NameError` at import time since default argument values are evaluated when the class body executes, not when the method is called. Claude caught this from an IDE diagnostic and reordered the module so the weight-profile definitions come before the class that depends on them.

Finally, I asked for `main.py` to prompt the user to choose a strategy and let them switch afterward, rather than just hardcoding a comparison loop over all three strategies. Claude replaced the hardcoded loop with an interactive `prompt_for_strategy()` + a switch/quit loop in `main()`, and confirmed with me first that this wouldn't drop the original demo output - it just re-runs the same functional + OOP demo under whichever strategy is currently selected.

**How does the pattern appear in your final code?**

- `WEIGHT_PROFILES` and `get_weights(strategy)` in [`src/recommender.py`](src/recommender.py) define the interchangeable strategies (`genre_first`, `mood_first`, `energy_focused`), each a dict of weights summing to 1.0.
- `Recommender.__init__(self, songs, strategy=DEFAULT_STRATEGY)` and `Recommender.set_strategy(strategy)` in [`src/recommender.py`](src/recommender.py) select and swap the active strategy; `Recommender._score()` reads from `self.weights` instead of hardcoded constants, so it works identically regardless of which strategy is active.
- `score_song(user_prefs, song, strategy=DEFAULT_STRATEGY)` and `recommend_songs(user_prefs, songs, k=5, strategy=DEFAULT_STRATEGY)` in [`src/recommender.py`](src/recommender.py) expose the same strategy selection through the functional API.
- `main.py`'s `prompt_for_strategy()` and the switch/quit loop in `main()` let a user pick a strategy interactively and re-run the recommendations under a different one without restarting the program.
