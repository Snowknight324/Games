import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 600
CELL = 20

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake With Obstacles")

clock = pygame.time.Clock()

GREEN = (0, 200, 0)
RED = (220, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
TRANSLUCENT_BLACK = (0, 0, 0, 160)

font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 50)

def draw_text(text, x, y, color=BLACK, font_obj=None):
    if font_obj is None:
        font_obj = font
    surface = font_obj.render(text, True, color)
    win.blit(surface, (x, y))

def random_position():
    return (random.randrange(0, WIDTH // CELL) * CELL,
            random.randrange(0, HEIGHT // CELL) * CELL)

def generate_obstacles(n, snake, food):
    obs = []
    while len(obs) < n:
        pos = random_position()
        if pos not in snake and pos != food:
            obs.append(pos)
    return obs

def pause_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(TRANSLUCENT_BLACK)

    win.blit(overlay, (0, 0))
    draw_text("PAUSED", WIDTH//2 - 80, HEIGHT//2 - 40, WHITE, big_font)
    draw_text("Press ESC to Resume", WIDTH//2 - 140, HEIGHT//2 + 10, WHITE)
    draw_text("Click window to Resume", WIDTH//2 - 150, HEIGHT//2 + 50, WHITE)
    pygame.display.update()

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Resume conditions
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                paused = False

def start_screen():
    running = True
    while running:
        win.fill(WHITE)
        draw_text("SNAKE", WIDTH//2 - 80, HEIGHT//2 - 100, BLACK, big_font)
        draw_text("Press SPACE to Start", WIDTH//2 - 140, HEIGHT//2, BLACK)
        draw_text("ESC to Quit", WIDTH//2 - 70, HEIGHT//2 + 50, BLACK)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def game_over_screen(score):
    win.fill(WHITE)
    draw_text("GAME OVER", WIDTH//2 - 100, HEIGHT//2 - 40, BLACK, big_font)
    draw_text(f"Score: {score}", WIDTH//2 - 40, HEIGHT//2)
    draw_text("Press R to Restart or Q to Quit", WIDTH//2 - 160, HEIGHT//2 + 50)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    snake = [(WIDTH//2, HEIGHT//2)]
    direction = "RIGHT"
    change_to = direction

    food = random_position()
    obstacles = generate_obstacles(20, snake, food)

    score = 0
    running = True

    while running:
        mouse_inside = pygame.mouse.get_focused()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: change_to = "UP"
                if event.key == pygame.K_DOWN: change_to = "DOWN"
                if event.key == pygame.K_LEFT: change_to = "LEFT"
                if event.key == pygame.K_RIGHT: change_to = "RIGHT"
                if event.key == pygame.K_ESCAPE:
                    pause_screen()

            # If player clicks outside window → pause
            if event.type == pygame.ACTIVEEVENT:
                if mouse_inside == 0:
                    pause_screen()

        if change_to == "UP" and direction != "DOWN":
            direction = "UP"
        if change_to == "DOWN" and direction != "UP":
            direction = "DOWN"
        if change_to == "LEFT" and direction != "RIGHT":
            direction = "LEFT"
        if change_to == "RIGHT" and direction != "LEFT":
            direction = "RIGHT"

        x, y = snake[0]

        if direction == "UP": y -= CELL
        if direction == "DOWN": y += CELL
        if direction == "LEFT": x -= CELL
        if direction == "RIGHT": x += CELL

        # Wrap around edges
        if x < 0: x = WIDTH - CELL
        if x >= WIDTH: x = 0
        if y < 0: y = HEIGHT - CELL
        if y >= HEIGHT: y = 0

        head = (x, y)

        if head in snake or head in obstacles:
            game_over_screen(score)

        snake.insert(0, head)

        if head == food:
            score += 1
            food = random_position()
        else:
            snake.pop()

        win.fill(WHITE)

        for pos in obstacles:
            pygame.draw.rect(win, GRAY, (pos[0], pos[1], CELL, CELL))

        for segment in snake:
            pygame.draw.rect(win, GREEN, (segment[0], segment[1], CELL, CELL))

        pygame.draw.rect(win, RED, (food[0], food[1], CELL, CELL))

        draw_text(f"Score: {score}", 10, 10)

        pygame.display.update()
        clock.tick(12)

start_screen()
main()
