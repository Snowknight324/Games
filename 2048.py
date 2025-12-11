import pygame, random, time, math

pygame.init()
WIDTH, HEIGHT = 500, 620
GRID_SIZE = 4
TILE_SIZE = 100
GAP = 15
TOP_OFFSET = 120
FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

FONT = pygame.font.SysFont("arial", 32, bold=True)
FONT_BIG = pygame.font.SysFont("arial", 56, bold=True)
CLOCK = pygame.time.Clock()

COLORS = {
    0: (205,193,180), 2: (238,228,218), 4: (237,224,200), 8: (242,177,121),
    16: (245,149,99), 32: (246,124,95), 64: (246,94,59), 128: (237,207,114),
    256: (237,204,97), 512: (237,200,80), 1024: (237,197,63), 2048: (237,194,46)
}

def ease_out(t):
    return 1 - pow(1 - t, 3)

class Tile:
    def __init__(self, value, r, c):
        self.value = value
        self.row = r
        self.col = c
        self.x = c*(TILE_SIZE+GAP)+GAP
        self.y = r*(TILE_SIZE+GAP)+GAP+TOP_OFFSET
        self.anim_x = self.x
        self.anim_y = self.y
        self.scale = 1
    def draw(self):
        s = self.scale
        size = TILE_SIZE*s
        offset = (TILE_SIZE-size)/2
        rect = pygame.Rect(self.anim_x+offset, self.anim_y+offset, size, size)
        pygame.draw.rect(WIN, COLORS.get(self.value,(60,58,50)), rect, border_radius=8)
        text = FONT_BIG.render(str(self.value), True, (0,0,0) if self.value<=4 else (255,255,255))
        WIN.blit(text, (rect.x+(rect.width-text.get_width())/2, rect.y+(rect.height-text.get_height())/2))

class Game:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.move_animations = []
        self.merge_animations = []
        self.spawn_animations = []
        self.game_over = False
        self.spawn_tile(True)
        self.spawn_tile(True)

    def spawn_tile(self, initial=False):
        empty = [(r,c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.grid[r][c] is None]
        if not empty: return
        r,c = random.choice(empty)
        t = Tile(2 if random.random()<0.9 else 4, r, c)
        t.scale = 0.1
        self.grid[r][c] = t
        self.spawn_animations.append(("spawn", t, time.time(), 0.12))

    def valid_moves_exist(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                tile = self.grid[r][c]
                if tile is None: return True
                if c+1<GRID_SIZE:
                    right = self.grid[r][c+1]
                    if right is not None and right.value==tile.value: return True
                if r+1<GRID_SIZE:
                    down = self.grid[r+1][c]
                    if down is not None and down.value==tile.value: return True
        return False

    def check_game_over(self):
        if not self.valid_moves_exist(): self.game_over = True

    def all_tiles(self):
        return [self.grid[r][c] for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.grid[r][c]]

    def animate(self):
        now = time.time()
        remove = []
        for anim in list(self.spawn_animations):
            _, tile, start, dur = anim
            t = (now-start)/dur
            if t>=1: tile.scale=1; remove.append(anim); continue
            tile.scale = 0.1+0.9*ease_out(t)
        for anim in list(self.move_animations):
            tile, sx,sy,ex,ey,start,dur = anim
            t = (now-start)/dur
            if t>=1: tile.anim_x=ex; tile.anim_y=ey; tile.x=ex; tile.y=ey; remove.append(anim); continue
            e = ease_out(t)
            tile.anim_x = sx + (ex-sx)*e
            tile.anim_y = sy + (ey-sy)*e
        for anim in list(self.merge_animations):
            tile, start, dur = anim
            t = (now-start)/dur
            if t>=1: tile.scale=1; remove.append(anim); continue
            tile.scale = 1+0.3*math.sin(t*math.pi)
        for r in remove:
            if r in self.spawn_animations: self.spawn_animations.remove(r)
            if r in self.move_animations: self.move_animations.remove(r)
            if r in self.merge_animations: self.merge_animations.remove(r)

    def draw(self):
        WIN.fill((250,248,239))
        pygame.draw.rect(WIN,(187,173,160),(GAP,TOP_OFFSET,WIDTH-GAP*2,WIDTH-GAP*2),border_radius=10)
        WIN.blit(FONT.render(f"Score: {self.score}", True, (0,0,0)), (GAP,40))
        for r in range(GRID_SIZE+1):
            pygame.draw.line(WIN,(187,173,160),(GAP,TOP_OFFSET+r*(TILE_SIZE+GAP)-GAP//2),(WIDTH-GAP,TOP_OFFSET+r*(TILE_SIZE+GAP)-GAP//2),3)
        for c in range(GRID_SIZE+1):
            pygame.draw.line(WIN,(187,173,160),(GAP+c*(TILE_SIZE+GAP)-GAP//2,TOP_OFFSET),(GAP+c*(TILE_SIZE+GAP)-GAP//2,TOP_OFFSET+GRID_SIZE*(TILE_SIZE+GAP)),3)
        for tile in self.all_tiles(): tile.draw()
        if self.game_over:
            surf = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            surf.fill((0,0,0,150))
            WIN.blit(surf,(0,0))
            t = FONT_BIG.render("Game Over",True,(255,255,255))
            WIN.blit(t,(WIDTH//2 - t.get_width()//2, HEIGHT//2-40))
        pygame.display.update()

    def move_line(self, line):
        new_line = [t for t in line if t is not None]
        merged_line = []
        skip=False
        i=0
        while i<len(new_line):
            if skip: skip=False; i+=1; continue
            if i+1<len(new_line) and new_line[i].value==new_line[i+1].value:
                new_line[i].value*=2
                self.score += new_line[i].value
                new_line[i+1]=None
                merged_line.append(new_line[i])
                skip=True
            else:
                merged_line.append(new_line[i])
            i+=1
        while len(merged_line)<GRID_SIZE:
            merged_line.append(None)
        return merged_line

    def move(self, direction):
        if self.game_over: return
        moved=False
        if direction in ["left","right"]:
            for r in range(GRID_SIZE):
                line = self.grid[r][:]
                if direction=="right": line=line[::-1]
                new_line = self.move_line(line)
                if direction=="right": new_line=new_line[::-1]
                for c in range(GRID_SIZE):
                    tile = new_line[c]
                    old_tile = self.grid[r][c]
                    if tile!=old_tile: moved=True
                    self.grid[r][c]=tile
                    if tile:
                        ex = c*(TILE_SIZE+GAP)+GAP
                        ey = r*(TILE_SIZE+GAP)+GAP+TOP_OFFSET
                        self.move_animations.append((tile, tile.x, tile.y, ex, ey, time.time(),0.13))
                        tile.x=ex; tile.y=ey
                        tile.anim_x=ex; tile.anim_y=ey
        else:
            for c in range(GRID_SIZE):
                line = [self.grid[r][c] for r in range(GRID_SIZE)]
                if direction=="down": line=line[::-1]
                new_line = self.move_line(line)
                if direction=="down": new_line=new_line[::-1]
                for r in range(GRID_SIZE):
                    tile = new_line[r]
                    old_tile = self.grid[r][c]
                    if tile!=old_tile: moved=True
                    self.grid[r][c]=tile
                    if tile:
                        ex = c*(TILE_SIZE+GAP)+GAP
                        ey = r*(TILE_SIZE+GAP)+GAP+TOP_OFFSET
                        self.move_animations.append((tile, tile.x, tile.y, ex, ey, time.time(),0.13))
                        tile.x=ex; tile.y=ey
                        tile.anim_x=ex; tile.anim_y=ey
        if moved:
            self.spawn_tile()
            self.check_game_over()
            # Animate until done
            while self.move_animations or self.spawn_animations or self.merge_animations:
                CLOCK.tick(FPS)
                self.animate()
                self.draw()

def main():
    g = Game()
    running = True
    while running:
        CLOCK.tick(FPS)
        g.animate()
        g.draw()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            if g.game_over:
                if event.type==pygame.KEYDOWN: g.__init__()
                continue
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_LEFT: g.move("left")
                elif event.key==pygame.K_RIGHT: g.move("right")
                elif event.key==pygame.K_UP: g.move("up")
                elif event.key==pygame.K_DOWN: g.move("down")
    pygame.quit()

main()
