import unittest

from snake_ai.ai import astar, choose_direction, play
from snake_ai.game import LEFT, RIGHT, UP, SnakeGame


class GameTests(unittest.TestCase):
    def test_moves_forward(self):
        g = SnakeGame(10, 10, seed=1)
        head = g.head
        g.step()
        self.assertEqual(g.head, (head[0] + 1, head[1]))
        self.assertEqual(len(g.snake), 3)

    def test_cannot_reverse(self):
        g = SnakeGame(10, 10, seed=1)
        g.step(LEFT)  # opposite of RIGHT, ignored
        self.assertEqual(g.direction, RIGHT)
        self.assertTrue(g.alive)

    def test_wall_collision(self):
        g = SnakeGame(10, 10, seed=1)
        for _ in range(10):
            g.step(RIGHT)
        self.assertFalse(g.alive)

    def test_eating_grows_and_scores(self):
        g = SnakeGame(10, 10, seed=1)
        g.food = (g.head[0] + 1, g.head[1])
        g.step()
        self.assertEqual(g.score, 1)
        self.assertEqual(len(g.snake), 4)
        self.assertNotIn(g.food, g.snake)

    def test_can_move_into_vacating_tail(self):
        g = SnakeGame(6, 6, seed=1)
        # A 2x2 loop: head chases its own tail cell, which is legal.
        g.snake.clear()
        g.snake.extend([(2, 2), (2, 3), (3, 3), (3, 2)])
        g.direction = UP
        g.food = (0, 0)
        g.step(RIGHT)  # head -> (3,2), the tail cell, which moves away this tick
        self.assertTrue(g.alive)

    def test_self_collision(self):
        g = SnakeGame(10, 10, seed=1)
        g.snake.clear()
        g.snake.extend([(5, 5), (5, 6), (4, 6), (4, 5), (4, 4), (5, 4)])
        g.direction = UP
        g.food = (0, 0)
        g.step(LEFT)  # into (4,5), which is body
        self.assertFalse(g.alive)


class AITests(unittest.TestCase):
    def test_astar_finds_shortest_path(self):
        path = astar((0, 0), (3, 0), set(), 5, 5)
        self.assertEqual(len(path), 4)

    def test_astar_routes_around_walls(self):
        blocked = {(1, 0), (1, 1)}
        path = astar((0, 0), (2, 0), blocked, 5, 5)
        self.assertIsNotNone(path)
        self.assertTrue(blocked.isdisjoint(path))

    def test_astar_unreachable(self):
        blocked = {(1, 0), (0, 1), (1, 1)}
        self.assertIsNone(astar((0, 0), (4, 4), blocked, 5, 5))

    def test_ai_heads_toward_food(self):
        g = SnakeGame(10, 10, seed=1)
        g.food = (g.head[0], g.head[1] - 3)
        self.assertEqual(choose_direction(g), UP)

    def test_ai_scores_near_the_maximum(self):
        # A 10x10 board holds at most 97 food (100 cells minus the 3-cell start).
        # The AI is deterministic per seed. It sometimes clips itself in the crowded
        # endgame, so we assert strong play rather than a perfect game.
        scores = []
        for seed in range(10):
            g = SnakeGame(10, 10, seed=seed)
            scores.append(play(g))
            self.assertGreaterEqual(g.score, 50, f"seed {seed} scored only {g.score}")
        self.assertGreater(sum(scores) / len(scores), 85)


if __name__ == "__main__":
    unittest.main()
