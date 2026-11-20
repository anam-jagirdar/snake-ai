"""A* based Snake AI with a safety check.

Strategy
--------
1. Find the shortest path (A*) to the food.
2. Before committing, *simulate* eating the food and check the snake could still
   reach its own tail afterwards. If it can, it will never trap itself.
3. If the food path is unsafe or missing, stall: take the safe move that keeps the
   tail reachable and stays farthest from it, until the board opens up.
4. As a last resort pick the move with the most open space (flood fill).
"""
import heapq
from collections.abc import Iterable

from .game import DIRECTIONS, Point, SnakeGame


def manhattan(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(p: Point, width: int, height: int) -> Iterable[Point]:
    for dx, dy in DIRECTIONS:
        q = (p[0] + dx, p[1] + dy)
        if 0 <= q[0] < width and 0 <= q[1] < height:
            yield q


def astar(start: Point, goal: Point, blocked: set[Point], width: int, height: int) -> list[Point] | None:
    """Shortest path from start to goal, inclusive of both. None if unreachable."""
    frontier: list[tuple[int, int, Point]] = [(manhattan(start, goal), 0, start)]
    came_from: dict[Point, Point | None] = {start: None}
    cost = {start: 0}
    while frontier:
        _, g, current = heapq.heappop(frontier)
        if current == goal:
            path = [current]
            while came_from[path[-1]] is not None:
                path.append(came_from[path[-1]])
            return path[::-1]
        if g > cost[current]:
            continue  # stale heap entry
        for nxt in neighbors(current, width, height):
            if nxt in blocked:
                continue
            new_cost = g + 1
            if new_cost < cost.get(nxt, 1 << 30):
                cost[nxt] = new_cost
                came_from[nxt] = current
                heapq.heappush(frontier, (new_cost + manhattan(nxt, goal), new_cost, nxt))
    return None


def flood_fill_size(start: Point, blocked: set[Point], width: int, height: int) -> int:
    seen = {start}
    stack = [start]
    while stack:
        for nxt in neighbors(stack.pop(), width, height):
            if nxt not in blocked and nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return len(seen)


def _after_following(snake: list[Point], path: list[Point]) -> list[Point]:
    """The snake's body (head first) after walking `path` and eating at its end."""
    body = list(snake)
    for p in path[1:]:
        body.insert(0, p)
    for _ in range(len(path) - 2):  # it grows only on the final step
        body.pop()
    return body


def _can_reach_tail(body: list[Point], width: int, height: int) -> bool:
    if len(body) >= width * height:
        return True
    return astar(body[0], body[-1], set(body[:-1]), width, height) is not None


def _delta(a: Point, b: Point) -> Point:
    return (b[0] - a[0], b[1] - a[1])


def choose_direction(game: SnakeGame) -> Point:
    w, h = game.width, game.height
    snake = list(game.snake)
    head, tail = snake[0], snake[-1]
    blocked = set(snake[:-1])  # the tail will have moved by the time we get there

    # 1. Safe path to the food.
    if game.food is not None:
        path = astar(head, game.food, blocked, w, h)
        if path and _can_reach_tail(_after_following(snake, path), w, h):
            return _delta(head, path[1])

    # 2. Otherwise stall: pick the safe move that keeps the tail reachable, farthest from it.
    best, best_score = None, -1
    for nxt in neighbors(head, w, h):
        if nxt in blocked:
            continue
        moved = [nxt] + snake[:-1]
        if _can_reach_tail(moved, w, h) and manhattan(nxt, tail) > best_score:
            best, best_score = nxt, manhattan(nxt, tail)
    if best is not None:
        return _delta(head, best)

    # 3. Desperation: most open space.
    best, best_area = None, -1
    for nxt in neighbors(head, w, h):
        if nxt in blocked:
            continue
        area = flood_fill_size(nxt, blocked | {head}, w, h)
        if area > best_area:
            best, best_area = nxt, area
    return _delta(head, best) if best is not None else game.direction


def play(game: SnakeGame, max_steps: int | None = None) -> int:
    """Let the AI play a whole game headless. Returns the final score."""
    limit = max_steps or game.width * game.height * 200
    while game.alive and game.steps < limit:
        game.step(choose_direction(game))
    return game.score
