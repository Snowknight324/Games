import pygame
import math
import sys
import time
import random

pygame.init()

WIDTH, HEIGHT = 1000, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down 2-Player Racer")

FPS = 60
CLOCK = pygame.time.Clock()

ROAD = (120, 120, 120)
GRASS = (40, 160, 40)
TRACK_BORDER = (30, 30, 30)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
P1_COLOR = (200, 40, 40)
P2_COLOR = (40, 80, 200)

MARGIN = 60
outer_rect = pygame.Rect(MARGIN, MARGIN, WIDTH - 2 * MARGIN, HEIGHT - 2 * MARGIN)

inner_pad_w = 220
inner_pad_h = 140
inner_rect = pygame.Rect(
    outer_rect.centerx - inner_pad_w // 2,
    outer_rect.centery - inner_pad_h // 2,
    inner_pad_w,
    inner_pad_h,
)

checkpoint_width = 60
checkpoint_rect = pygame.Rect(
    outer_rect.centerx - checkpoint_width // 2,
    outer_rect.top + 6,
    checkpoint_width,
    6
)

FONT = pygame.font.SysFont("Arial", 20)
BIG = pygame.font.SysFont("Arial", 48)
SMALL = pygame.font.SysFont("Arial", 16)

LAPS_TO_WIN = 3

def rotate_surface(surf, angle):
    return pygame.transform.rotozoom(surf, -math.degrees(angle), 1.0)

class Car:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.angle = 0.0
        self.vx = 0.0
        self.vy = 0.0

        # ====== CHANGED: REDUCED SPEED ======
        self.speed = 0.0
        self.max_speed = 60      # was 100
        self.acceleration = 6    # was 10
        # ====================================

        self.brake = 900
        self.friction = 520

        self.turn_speed = 6.8
        self.width = 36
        self.height = 18
        self.controls = controls
        self.color = color

        self.rect = pygame.Rect(0, 0, self.width, self.height)

        self.laps = 0
        self.last_checkpoint = False

        self.drift_factor = 0.15
        self.traction = 0.90
        self.max_lateral_speed = 100

    def update(self, dt, keys):
        forward = keys[self.controls['forward']]
        back = keys[self.controls['back']]
        left = keys[self.controls['left']]
        right = keys[self.controls['right']]

        if forward:
            self.speed += self.acceleration * dt
        elif back:
            self.speed -= self.brake * dt
        else:
            if self.speed > 0:
                self.speed -= min(self.speed, self.friction * dt)
            elif self.speed < 0:
                self.speed += min(-self.speed, self.friction * dt)

        self.speed = max(-self.max_speed * 0.4, min(self.max_speed, self.speed))

        steering_amount = (1 - abs(self.speed) / self.max_speed)
        if left:
            self.angle -= self.turn_speed * dt * max(0.2, steering_amount)
        if right:
            self.angle += self.turn_speed * dt * max(0.2, steering_amount)

        self.vx += math.cos(self.angle) * self.speed * dt
        self.vy += math.sin(self.angle) * self.speed * dt

        forward_x = math.cos(self.angle)
        forward_y = math.sin(self.angle)
        right_x = -forward_y
        right_y = forward_x

        forward_vel = self.vx * forward_x + self.vy * forward_y
        lateral_vel = self.vx * right_x + self.vy * right_y

        lateral_vel *= self.traction

        self.vx = forward_vel * forward_x + lateral_vel * right_x
        self.vy = forward_vel * forward_y + lateral_vel * right_y

        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60

        self.rect = pygame.Rect(self.x - self.width/2, self.y - self.height/2, self.width, self.height)

        if not is_on_road(self.x, self.y):
            self.speed *= 0.91

        self.x = max(20, min(WIDTH - 20, self.x))
        self.y = max(20, min(HEIGHT - 20, self.y))

    # ======= ADDED DRAW METHOD =======
    def draw(self, surf):
        car_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(car_surf, self.color, (0, 0, self.width, self.height), border_radius=4)
        rot = rotate_surface(car_surf, self.angle)
        rect = rot.get_rect(center=(self.x, self.y))
        surf.blit(rot, rect)

def is_on_road(x, y):
    if not outer_rect.collidepoint(x, y):
        return False
    if inner_rect.collidepoint(x, y):
        return False
    return True

def detect_checkpoint_cross(car, prev_pos):
    x1, y1 = prev_pos
    x2, y2 = car.x, car.y
    if not (checkpoint_rect.left <= x1 <= checkpoint_rect.right or 
            checkpoint_rect.left <= x2 <= checkpoint_rect.right):
        return False
    if y1 > checkpoint_rect.bottom and y2 <= checkpoint_rect.bottom:
        return True
    return False

def check_collisions(a: Car, b: Car):
    rect_a = a.rect
    rect_b = b.rect
    if rect_a.colliderect(rect_b):
        nx = a.x - b.x
        ny = a.y - b.y
        dist = math.hypot(nx, ny) or 1.0
        nx /= dist
        ny /= dist

        # project velocities onto collision axis
        va = a.vx * nx + a.vy * ny
        vb = b.vx * nx + b.vy * ny

        exchange = 0.6
        a_proj = va * (1-exchange) + vb * exchange
        b_proj = vb * (1-exchange) + va * exchange

        # tangential velocities
        a_tang = (-ny, nx)
        at = a.vx * a_tang[0] + a.vy * a_tang[1]
        bt = b.vx * a_tang[0] + b.vy * a_tang[1]

        # set new velocities
        a.vx = a_proj * nx + at * a_tang[0]
        a.vy = a_proj * ny + at * a_tang[1]
        b.vx = b_proj * nx + bt * a_tang[0]
        b.vy = b_proj * ny + bt * a_tang[1]

        # update speed magnitude
        a.speed = math.hypot(a.vx, a.vy)
        b.speed = math.hypot(b.vx, b.vy)

def draw_track(surface):
    surface.fill(GRASS)
    pygame.draw.rect(surface, TRACK_BORDER, outer_rect)
    pygame.draw.rect(surface, ROAD, outer_rect.inflate(-8, -8))
    pygame.draw.rect(surface, TRACK_BORDER, inner_rect)
    pygame.draw.rect(surface, GRASS, inner_rect.inflate(-6, -6))
    pygame.draw.rect(surface, (255, 255, 0), checkpoint_rect)

def draw_hud(surface, p1, p2, elapsed):
    t1 = FONT.render(f"P1 Laps: {p1.laps}/{LAPS_TO_WIN}", True, WHITE)
    t2 = FONT.render(f"P2 Laps: {p2.laps}/{LAPS_TO_WIN}", True, WHITE)
    surface.blit(t1, (10, 10))
    surface.blit(t2, (220, 10))
    t3 = FONT.render(f"Time: {elapsed:.1f}s", True, WHITE)
    surface.blit(t3, (WIDTH - 140, 10))

def run_game():
    p1 = Car(outer_rect.centerx - 80, outer_rect.top + 100, P1_COLOR,
             {'forward': pygame.K_w, 'back': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d})

    p2 = Car(outer_rect.centerx + 80, outer_rect.top + 100, P2_COLOR,
             {'forward': pygame.K_UP, 'back': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT})

    p1.angle = math.pi / 2
    p2.angle = math.pi / 2

    winner = None
    race_start = time.time()

    while True:
        dt = CLOCK.tick(FPS) / 1000
        keys = pygame.key.get_pressed()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    return

        p1_prev = (p1.x, p1.y)
        p2_prev = (p2.x, p2.y)

        p1.update(dt, keys)
        p2.update(dt, keys)

        # ===== COLLISIONS =====
        check_collisions(p1, p2)

        # ===== LAP COUNTER =====
        if detect_checkpoint_cross(p1, p1_prev):
            if not p1.last_checkpoint:
                p1.laps += 1
                p1.last_checkpoint = True
                if p1.laps >= LAPS_TO_WIN:
                    winner = "Player 1"
        else:
            p1.last_checkpoint = False

        if detect_checkpoint_cross(p2, p2_prev):
            if not p2.last_checkpoint:
                p2.laps += 1
                p2.last_checkpoint = True
                if p2.laps >= LAPS_TO_WIN:
                    winner = "Player 2"
        else:
            p2.last_checkpoint = False

        draw_track(WIN)
        p1.draw(WIN)
        p2.draw(WIN)
        draw_hud(WIN, p1, p2, time.time() - race_start)

        if winner:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,150))
            WIN.blit(overlay, (0,0))
            txt = BIG.render(winner + " Wins!", True, WHITE)
            WIN.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 30))
            sub = FONT.render("Press R to restart or ESC to quit", True, WHITE)
            WIN.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 30))
            pygame.display.update()
            while True:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_r:
                            return
                        if ev.key == pygame.K_ESCAPE:
                            pygame.quit(); sys.exit()

        pygame.display.update()

def main_menu():
    title_font = pygame.font.SysFont("Arial", 56, True)
    btn_font = pygame.font.SysFont("Arial", 24, True)

    play_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 - 30, 180, 60)
    quit_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 60, 180, 50)

    while True:
        CLOCK.tick(FPS)
        WIN.fill((18,140,60))

        title = title_font.render("Top-Down Racer", True, WHITE)
        WIN.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        pygame.draw.rect(WIN, (200,50,50), play_rect, border_radius=10)
        pygame.draw.rect(WIN, (60,60,60), quit_rect, border_radius=10)

        WIN.blit(btn_font.render("Play (2 Player)", True, WHITE),
                 (play_rect.centerx - 75, play_rect.centery - 12))
        WIN.blit(btn_font.render("Quit", True, WHITE),
                 (quit_rect.centerx - 25, quit_rect.centery - 12))

        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(ev.pos):
                    return
                if quit_rect.collidepoint(ev.pos):
                    pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    return
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

if __name__ == "__main__":
    while True:
        main_menu()
        run_game()
