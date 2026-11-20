"""Pure game logic. No pygame imports so it can be tested and simulated headless."""
import random
from collections import deque

Point = tuple[int, int]

UP: Point = (0, -1)
DOWN: Point = (0, 1)
LEFT: Point = (-1, 0)
RIGHT: Point = (1, 0)
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)


def opposite(d: Point) -> Point:
    return (-d[0], -d[1])


class SnakeGame:
    def __init__(self, width: int = 20, height: int = 20, seed: int | None = None):
        if width < 4 or height < 4:
            raise ValueError("Board must be at least 4x4.")
        self.width = width
        self.height = height
        self.rng = random.Random(seed)
        self.reset()

    def reset(self) -> None:
        cx, cy = self.width // 2, self.height // 2
        self.snake: deque[Point] = deque([(cx, cy), (cx - 1, cy), (cx - 2, cy)])  # head first
        self.direction: Point = RIGHT
        self.score = 0
        self.steps = 0
        self.alive = True
        self.food: Point | None = self._place_food()

    @property
    def head(self) -> Point:
        return self.snake[0]

    @property
    def won(self) -> bool:
        return self.food is None

    def in_bounds(self, p: Point) -> bool:
        return 0 <= p[0] < self.width and 0 <= p[1] < self.height

    def _place_food(self) -> Point | None:
        occupied = set(self.snake)
        free = [(x, y) for x in range(self.width) for y in range(self.height) if (x, y) not in occupied]
        return self.rng.choice(free) if free else None

    def step(self, direction: Point | None = None) -> None:
        """Advance one tick. Reversing into yourself is ignored, like in the classic game."""
        if not self.alive:
            return
        if direction is not None and direction != opposite(self.direction):
            self.direction = direction

        new_head = (self.head[0] + self.direction[0], self.head[1] + self.direction[1])
        eating = new_head == self.food
        # The tail cell is vacated this tick unless the snake is growing.
        body = list(self.snake) if eating else list(self.snake)[:-1]

        self.steps += 1
        if not self.in_bounds(new_head) or new_head in body:
            self.alive = False
            return

        self.snake.appendleft(new_head)
        if eating:
            self.score += 1
            self.food = self._place_food()
            if self.food is None:  # board is full: the player has won
                self.alive = False
        else:
            self.snake.pop()
