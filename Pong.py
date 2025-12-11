import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Paddle:
    WIDTH, HEIGHT = 10, 80
    SPEED = 6
    def __init__(self, x):
        self.rect = pygame.Rect(x, HEIGHT//2 - self.HEIGHT//2, self.WIDTH, self.HEIGHT)
    def move(self, up=True):
        self.rect.y += -self.SPEED if up else self.SPEED
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.HEIGHT))
    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

class Ball:
    SIZE = 12
    SPIN_FRICTION = 0.993
    MAX_SPIN = 0.45
    BASE_SPEED_INC = 1.0003
    def __init__(self):
        self.reset()
    def reset(self):
        self.x = WIDTH / 2.0
        self.y = HEIGHT / 2.0
        angle = random.uniform(-0.35, 0.35)
        horiz = random.choice([-1, 1])
        speed = 5.5
        self.dx = horiz * speed * math.cos(angle)
        self.dy = speed * math.sin(angle)
        self.spin = 0.0
        self.update_rect()
    def update_rect(self):
        self.rect = pygame.Rect(int(self.x - self.SIZE/2), int(self.y - self.SIZE/2), self.SIZE, self.SIZE)
    def update(self, paddle_left, paddle_right):
        self.dy += self.spin
        self.dx *= self.BASE_SPEED_INC
        self.dx = max(min(self.dx, 14), -14)
        self.dy = max(min(self.dy, 12), -12)
        self.x += self.dx
        self.y += self.dy
        self.update_rect()
        if self.rect.top <= 0:
            self.rect.top = 0
            self.y = self.rect.centery
            self.dy *= -1
            self.spin *= -0.6
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.y = self.rect.centery
            self.dy *= -1
            self.spin *= -0.6
        if self.rect.colliderect(paddle_left.rect) and self.dx < 0:
            self.x = paddle_left.rect.right + self.SIZE / 2 + 0.1
            self.paddle_bounce(paddle_left)
        if self.rect.colliderect(paddle_right.rect) and self.dx > 0:
            self.x = paddle_right.rect.left - self.SIZE / 2 - 0.1
            self.paddle_bounce(paddle_right)
        self.spin *= self.SPIN_FRICTION
        self.update_rect()
    def paddle_bounce(self, paddle):
        self.dx *= -1
        offset = (self.y - (paddle.rect.centery)) / (paddle.HEIGHT / 2)
        offset = max(min(offset, 1.0), -1.0)
        self.dy = offset * 6.5
        self.spin += max(min(offset * 0.28, self.MAX_SPIN), -self.MAX_SPIN)
        self.dx += random.uniform(-0.35, 0.35)
        self.dx = max(min(self.dx, 14), -14)
        self.dy = max(min(self.dy, 12), -12)
    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

def predict_ball_destination(ball, target_x):
    x, y, dx, dy, spin = ball.x, ball.y, ball.dx, ball.dy, ball.spin
    for _ in range(2000):
        y += dy + spin
        x += dx
        if y <= 0:
            y = -y
            dy *= -1
            spin *= -0.6
        if y >= HEIGHT:
            y = 2*HEIGHT - y
            dy *= -1
            spin *= -0.6
        if (dx > 0 and x >= target_x) or (dx < 0 and x <= target_x):
            return y
    return HEIGHT / 2.0

def main():
    clock = pygame.time.Clock()
    left = Paddle(20)
    right = Paddle(WIDTH - 30)
    ball = Ball()
    score_left = 0
    score_right = 0
    font = pygame.font.SysFont("Arial", 32)
    WIN_SCORE = 7

    ai_enabled = True
    ai_target_y = HEIGHT // 2
    ai_timer = 0
    ai_reaction_delay = 12
    ai_deadzone = 14
    ai_mistake_probability = 0.22
    ai_mistake_max = 130

    state = "menu"  # states: menu, playing, paused, win
    winner_text = ""

    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if state == "playing":
                    if event.key == pygame.K_p:
                        state = "paused"
                elif state == "paused":
                    if event.key == pygame.K_r:
                        state = "playing"
                elif state == "win":
                    if event.key == pygame.K_SPACE:
                        state = "menu"
                    if event.key == pygame.K_m:
                        state = "playing"
                        score_left = 0
                        score_right = 0
                        ball.reset()
                        left.rect.y = HEIGHT//2 - Paddle.HEIGHT//2
                        right.rect.y = HEIGHT//2 - Paddle.HEIGHT//2
                elif state == "menu":
                    if event.key == pygame.K_1:
                        ai_enabled = True
                        state = "playing"
                        score_left = 0
                        score_right = 0
                        ball.reset()
                    if event.key == pygame.K_2:
                        ai_enabled = False
                        state = "playing"
                        score_left = 0
                        score_right = 0
                        ball.reset()
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

        keys = pygame.key.get_pressed()
        if state == "playing":
            if keys[pygame.K_w]: left.move(up=True)
            if keys[pygame.K_s]: left.move(up=False)
            if not ai_enabled:
                if keys[pygame.K_UP]: right.move(up=True)
                if keys[pygame.K_DOWN]: right.move(up=False)
            else:
                ai_timer += 1
                if ai_timer >= ai_reaction_delay:
                    if ball.dx > 0:
                        predicted = predict_ball_destination(ball, right.rect.centerx)
                        mistake = random.randint(-ai_mistake_max, ai_mistake_max) if random.random() < ai_mistake_probability else 0
                        ai_target_y = predicted + mistake
                    else:
                        ai_target_y = HEIGHT/2
                    ai_timer = 0
                if right.rect.centery < ai_target_y - ai_deadzone: right.move(up=False)
                elif right.rect.centery > ai_target_y + ai_deadzone: right.move(up=True)

            ball.update(left, right)

            if ball.rect.right < 0:
                score_right += 1
                ball.reset()
            if ball.rect.left > WIDTH:
                score_left += 1
                ball.reset()

            if score_left >= WIN_SCORE or score_right >= WIN_SCORE:
                winner_text = "Player 1" if score_left >= WIN_SCORE else ("AI" if ai_enabled else "Player 2")
                state = "win"

        WIN.fill(BLACK)

        if state == "menu":
            title_font = pygame.font.SysFont("Arial", 48)
            font = pygame.font.SysFont("Arial", 28)
            title = title_font.render("PONG", True, WHITE)
            one = font.render("Press 1 - Single Player (vs AI)", True, WHITE)
            two = font.render("Press 2 - Two Players (local)", True, WHITE)
            quit_txt = font.render("Press Q - Quit", True, WHITE)
            WIN.blit(title, (WIDTH//2 - title.get_width()//2, 110))
            WIN.blit(one, (WIDTH//2 - one.get_width()//2, 210))
            WIN.blit(two, (WIDTH//2 - two.get_width()//2, 260))
            WIN.blit(quit_txt, (WIDTH//2 - quit_txt.get_width()//2, 320))

        elif state == "playing" or state == "paused" or state == "win":
            dash_h = 18
            gap = 12
            for y in range(0, HEIGHT, dash_h + gap):
                pygame.draw.rect(WIN, WHITE, (WIDTH//2 - 2, y, 4, dash_h))
            score_text = font.render(f"{score_left}   {score_right}", True, WHITE)
            WIN.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 18))
            left.draw(WIN)
            right.draw(WIN)
            ball.draw(WIN)
            if state == "paused":
                pause_font = pygame.font.SysFont("Arial", 50)
                sub_font = pygame.font.SysFont("Arial", 26)
                pause_txt = pause_font.render("PAUSED", True, WHITE)
                sub_txt = sub_font.render("Press R to Resume", True, WHITE)
                WIN.blit(pause_txt, (WIDTH//2 - pause_txt.get_width()//2, HEIGHT//2 - 50))
                WIN.blit(sub_txt, (WIDTH//2 - sub_txt.get_width()//2, HEIGHT//2 + 20))
            if state == "win":
                big = pygame.font.SysFont("Arial", 54)
                small = pygame.font.SysFont("Arial", 28)
                win_txt = big.render(f"{winner_text} Wins!", True, WHITE)
                sub_txt = small.render("Press SPACE for Menu or M for Rematch", True, WHITE)
                WIN.blit(win_txt, (WIDTH//2 - win_txt.get_width()//2, HEIGHT//2 - 70))
                WIN.blit(sub_txt, (WIDTH//2 - sub_txt.get_width()//2, HEIGHT//2 + 10))

        pygame.display.update()

if __name__ == "__main__":
    main()
