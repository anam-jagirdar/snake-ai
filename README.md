# Snake AI

Classic Snake in Python with pygame, plus an autopilot that plays using A* pathfinding.

Play it yourself, or press **A** and watch the AI take over.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

| Key | Action |
| --- | --- |
| Arrow keys, W, S, D | Steer |
| A | Toggle AI autopilot |
| R | Restart |
| + / - | Change speed |
| Esc | Quit |

Your best score is saved to `highscore.txt`.

## How the AI works

Each turn the AI picks a move in this order:

1. **A\* to the food.** Finds the shortest path, treating the body as walls (the tail cell counts as free, since it moves away).
2. **Safety check.** It simulates walking that path and eating the food, then checks that the snake could still reach its own tail. If it can, it cannot have trapped itself. If not, it rejects the path.
3. **Stall safely.** With no safe food path, it takes the move that keeps the tail reachable and stays farthest from it, buying time for the board to open up.
4. **Last resort.** It moves toward the largest open region (flood fill).

## Results

Headless simulation on a 10x10 board (97 is the maximum score), 30 different food seeds:

| Metric | Result |
| --- | --- |
| Mean score | 94.5 of 97 |
| Games that filled the whole board | 15 of 30 |
| Lowest score | 58 |

The AI is strong but not perfect. In the other half of games it clips itself in the cramped endgame, when the board is nearly full. A Hamiltonian-cycle strategy would fix that and is the natural next step (see below).

## Project layout

```
snake_ai/game.py   Pure game rules. No pygame, so it runs headless.
snake_ai/ai.py     A*, flood fill and the move chooser.
main.py            The pygame window and controls.
tests/             Game rules and AI behaviour.
```

Keeping the rules separate from rendering is what makes it possible to simulate thousands of games without opening a window.

## Tests

```bash
python -m unittest discover -v
```

These need no pygame, since they only touch `snake_ai/`.

## Ideas for extending it

- Add a Hamiltonian-cycle fallback so the AI never dies in the endgame
- Draw the AI's planned path on screen
- Train a reinforcement-learning agent and compare it with A*
- Add walls or obstacles and different board sizes
