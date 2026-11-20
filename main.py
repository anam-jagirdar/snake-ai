"""Play Snake yourself, or press A and watch the AI play.

Controls
--------
Arrow keys / W S D  steer
A                  toggle AI autopilot
R                  restart
+ / -              change speed
Esc                quit
"""
import pathlib

import pygame

from snake_ai.ai import choose_direction
from snake_ai.game import DOWN, LEFT, RIGHT, UP, SnakeGame

CELL = 28
COLS, ROWS = 20, 20
HUD = 56
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + HUD

BG = (18, 24, 38)
GRID = (26, 34, 52)
SNAKE_HEAD = (120, 255, 190)
SNAKE_BODY = (52, 200, 140)
FOOD = (255, 110, 90)
TEXT = (225, 232, 245)
MUTED = (130, 145, 170)

KEYS = {
    pygame.K_UP: UP, pygame.K_w: UP,
    pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
}  # A is the autopilot toggle, so left is the arrow key only
HIGHSCORE_FILE = pathlib.Path(__file__).with_name("highscore.txt")


def load_highscore() -> int:
    try:
        return int(HIGHSCORE_FILE.read_text())
    except (OSError, ValueError):
        return 0


def save_highscore(value: int) -> None:
    try:
        HIGHSCORE_FILE.write_text(str(value))
    except OSError:
        pass  # a read-only folder should not crash the game


def draw(screen, fonts, game, ai_on, best, speed):
    screen.fill(BG)
    for x in range(COLS):
        for y in range(ROWS):
            if (x + y) % 2 == 0:
                pygame.draw.rect(screen, GRID, (x * CELL, HUD + y * CELL, CELL, CELL))

    if game.food:
        fx, fy = game.food
        pygame.draw.circle(screen, FOOD, (fx * CELL + CELL // 2, HUD + fy * CELL + CELL // 2), CELL // 2 - 4)

    for i, (x, y) in enumerate(game.snake):
        colour = SNAKE_HEAD if i == 0 else SNAKE_BODY
        pygame.draw.rect(screen, colour, (x * CELL + 2, HUD + y * CELL + 2, CELL - 4, CELL - 4), border_radius=6)

    screen.blit(fonts[0].render(f"Score {game.score}", True, TEXT), (16, 10))
    screen.blit(fonts[1].render(f"Best {best}", True, MUTED), (16, 34))
    mode = "AI autopilot (A to take over)" if ai_on else "You are driving (A for autopilot)"
    label = fonts[1].render(f"{mode}   speed {speed}", True, MUTED)
    screen.blit(label, (WIDTH - label.get_width() - 16, 20))

    if not game.alive:
        msg = "Board filled. You win! R to restart" if game.won else "Game over. R to restart"
        text = fonts[0].render(msg, True, TEXT)
        pad = 14
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2)).inflate(pad * 2, pad * 2)
        pygame.draw.rect(screen, BG, rect, border_radius=10)
        screen.blit(text, text.get_rect(center=rect.center))


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Snake AI")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fonts = (pygame.font.SysFont("arial", 22, bold=True), pygame.font.SysFont("arial", 16))

    game = SnakeGame(COLS, ROWS)
    best = load_highscore()
    ai_on = False
    speed = 10
    pending = None  # buffer the latest key press so quick turns are not lost

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                    pending = None
                elif event.key == pygame.K_a:
                    ai_on = not ai_on
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    speed = min(60, speed + 2)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    speed = max(4, speed - 2)
                elif event.key in KEYS:
                    pending = KEYS[event.key]

        if game.alive:
            game.step(choose_direction(game) if ai_on else pending)
            pending = None
            if game.score > best:
                best = game.score
                save_highscore(best)

        draw(screen, fonts, game, ai_on, best, speed)
        pygame.display.flip()
        clock.tick(speed)

    pygame.quit()


if __name__ == "__main__":
    main()
