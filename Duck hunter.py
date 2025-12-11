import pygame
import random
import sys
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Duck Hunter - Pixel-Perfect Hits")

CLOCK = pygame.time.Clock()
FPS = 60


FRAME_PATHS = [
    "D:/Projects/Games/Duck hunter/Frame-1.png",
    "D:/Projects/Games/Duck hunter/Frame-2.png",
    "D:/Projects/Games/Duck hunter/Frame-3.png",
]

DUCK_FRAMES = []
for p in FRAME_PATHS:
    img = pygame.image.load(p).convert_alpha()
    img = pygame.transform.scale(img, (64, 64))
    DUCK_FRAMES.append(img)

# precompute masks for each frame and its horizontal flip
DUCK_MASKS = [pygame.mask.from_surface(f) for f in DUCK_FRAMES]
DUCK_FRAMES_FLIP = [pygame.transform.flip(f, True, False) for f in DUCK_FRAMES]
DUCK_MASKS_FLIP = [pygame.mask.from_surface(f) for f in DUCK_FRAMES_FLIP]

# crosshair
CROSSHAIR = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.circle(CROSSHAIR, (255, 0, 0), (15, 15), 12, 2)
pygame.draw.line(CROSSHAIR, (255, 0, 0), (15, 0), (15, 30), 2)
pygame.draw.line(CROSSHAIR, (255, 0, 0), (0, 15), (30, 15), 2)

class Duck:
    def __init__(self):
        self.spawn()

    def spawn(self):
        self.y = random.randint(50, HEIGHT // 2)
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(2.0, 5.0) * self.direction
        self.frame_index = 0.0
        self.animation_speed = 0.18
        if self.direction > 0:
            self.x = -32
        else:
            self.x = WIDTH
        self.update_image_and_mask()

    def update_image_and_mask(self):
        idx = int(self.frame_index) % len(DUCK_FRAMES)
        if self.direction > 0:
            self.image = DUCK_FRAMES[idx]
            self.mask = DUCK_MASKS[idx]
        else:
            self.image = DUCK_FRAMES_FLIP[idx]
            self.mask = DUCK_MASKS_FLIP[idx]
        self.rect = self.image.get_rect(topleft=(int(self.x), int(self.y)))

    def move(self):
        self.x += self.speed
        if self.direction > 0 and self.x > WIDTH:
            self.spawn()
            return
        if self.direction < 0 and self.x < -32:
            self.spawn()
            return
        self.frame_index = (self.frame_index + self.animation_speed) % len(DUCK_FRAMES)
        self.update_image_and_mask()

    def draw(self, surf):
        surf.blit(self.image, (int(self.x), int(self.y)))

    def is_hit(self, mx, my):
        # quick bounding check first
        if not self.rect.collidepoint(mx, my):
            return False
        local_x = mx - self.rect.x
        local_y = my - self.rect.y
        if local_x < 0 or local_y < 0 or local_x >= self.rect.width or local_y >= self.rect.height:
            return False
        try:
            return self.mask.get_at((int(local_x), int(local_y))) == 1
        except IndexError:
            return False

def draw_window(ducks, crosshair_pos, score):
    WIN.fill((135, 206, 250))
    for d in ducks:
        d.draw(WIN)
    WIN.blit(CROSSHAIR, (crosshair_pos[0] - 15, crosshair_pos[1] - 15))
    font = pygame.font.SysFont("Arial", 24)
    WIN.blit(font.render(f"Score: {score}", True, (0,0,0)), (10,10))
    pygame.display.update()

def game_loop():
    NUM_DUCKS = 6
    ducks = [Duck() for _ in range(NUM_DUCKS)]
    score = 0
    font = pygame.font.SysFont("Arial", 28)

    while True:
        CLOCK.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # iterate in reverse so topmost/last-drawn ducks are hit first
                for i in range(len(ducks)-1, -1, -1):
                    d = ducks[i]
                    if d.is_hit(mx, my):
                        score += 1
                        ducks[i] = Duck()
                        break

        for d in ducks:
            d.move()

        draw_window(ducks, (mx,my), score)

if __name__ == "__main__":
    game_loop()
