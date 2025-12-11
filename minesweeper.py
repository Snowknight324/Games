import pygame, random, sys, os

pygame.init()

# Game constants
WIDTH, HEIGHT = 600, 700
ROWS, COLS = 10, 10
TILE_SIZE = 50
TOP_OFFSET = 120  # Space for score/info
NUM_MINES = 15
FPS = 60

# Colors
BG_COLOR = (200, 200, 200)
GRID_COLOR = (150, 150, 150)
HIDDEN_COLOR = (100, 100, 100)
REVEALED_COLOR = (220, 220, 220)
FLAG_COLOR = (255, 0, 0)
TEXT_COLOR = (0, 0, 0)

# Fonts
FONT = pygame.font.SysFont("arial", 24, bold=True)
FONT_BIG = pygame.font.SysFont("arial", 48, bold=True)

# Screen
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")
CLOCK = pygame.time.Clock()

# Load mine sprite
MINE_IMAGE = pygame.image.load(os.path.join("mine.png"))
MINE_IMAGE = pygame.transform.scale(MINE_IMAGE, (TILE_SIZE-10, TILE_SIZE-10))

# Calculate offsets to center grid
GRID_WIDTH = COLS * TILE_SIZE
GRID_HEIGHT = ROWS * TILE_SIZE
X_OFFSET = (WIDTH - GRID_WIDTH) // 2
Y_OFFSET = TOP_OFFSET + (HEIGHT - TOP_OFFSET - GRID_HEIGHT) // 2


class Tile:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.rect = pygame.Rect(X_OFFSET + col*TILE_SIZE, Y_OFFSET + row*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.is_mine = False
        self.revealed = False
        self.flagged = False
        self.neighbors = 0

    def draw(self):
        color = REVEALED_COLOR if self.revealed else HIDDEN_COLOR
        pygame.draw.rect(WIN, color, self.rect)
        pygame.draw.rect(WIN, GRID_COLOR, self.rect, 2)
        if self.revealed:
            if self.is_mine:
                WIN.blit(MINE_IMAGE, (self.rect.x+5, self.rect.y+5))
            elif self.neighbors > 0:
                text = FONT.render(str(self.neighbors), True, TEXT_COLOR)
                WIN.blit(text, (self.rect.x + (TILE_SIZE - text.get_width())//2,
                                self.rect.y + (TILE_SIZE - text.get_height())//2))
        elif self.flagged:
            pygame.draw.circle(WIN, FLAG_COLOR, self.rect.center, TILE_SIZE//4)


class Game:
    def __init__(self):
        self.grid = [[Tile(r, c) for c in range(COLS)] for r in range(ROWS)]
        self.mines = NUM_MINES
        self.game_over = False
        self.win = False
        self.place_mines()
        self.calculate_neighbors()

    def place_mines(self):
        positions = random.sample([(r,c) for r in range(ROWS) for c in range(COLS)], NUM_MINES)
        for r,c in positions:
            self.grid[r][c].is_mine = True

    def calculate_neighbors(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c].is_mine:
                    continue
                count = 0
                for dr in [-1,0,1]:
                    for dc in [-1,0,1]:
                        nr,nc = r+dr,c+dc
                        if 0<=nr<ROWS and 0<=nc<COLS and self.grid[nr][nc].is_mine:
                            count +=1
                self.grid[r][c].neighbors = count

    def reveal(self, row, col):
        tile = self.grid[row][col]
        if tile.revealed or tile.flagged:
            return
        tile.revealed = True
        if tile.is_mine:
            self.game_over = True
            return
        if tile.neighbors == 0:
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    nr,nc = row+dr,col+dc
                    if 0<=nr<ROWS and 0<=nc<COLS:
                        if not self.grid[nr][nc].revealed:
                            self.reveal(nr,nc)

    def toggle_flag(self, row, col):
        tile = self.grid[row][col]
        if tile.revealed:
            return
        tile.flagged = not tile.flagged

    def check_win(self):
        for r in range(ROWS):
            for c in range(COLS):
                tile = self.grid[r][c]
                if not tile.is_mine and not tile.revealed:
                    return False
        self.win = True
        return True

    def draw(self):
        WIN.fill(BG_COLOR)
        # Top info
        status = f"Mines: {self.mines}"
        text = FONT.render(status, True, TEXT_COLOR)
        WIN.blit(text, (10,30))
        # Draw grid
        for row in self.grid:
            for tile in row:
                tile.draw()
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,150))
            WIN.blit(overlay,(0,0))
            text = FONT_BIG.render("Game Over", True, (255,255,255))
            WIN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
        if self.win:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,150))
            WIN.blit(overlay,(0,0))
            text = FONT_BIG.render("You Win!", True, (0,255,0))
            WIN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
        pygame.display.update()


def main():
    game = Game()
    running = True
    while running:
        CLOCK.tick(FPS)
        game.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if game.game_over or game.win:
                if event.type == pygame.KEYDOWN:
                    game = Game()
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                row = (my - Y_OFFSET)//TILE_SIZE
                col = (mx - X_OFFSET)//TILE_SIZE
                if 0<=row<ROWS and 0<=col<COLS:
                    if event.button == 1:
                        game.reveal(row,col)
                        game.check_win()
                    elif event.button == 3:
                        game.toggle_flag(row,col)
    pygame.quit()
    sys.exit()

main()
