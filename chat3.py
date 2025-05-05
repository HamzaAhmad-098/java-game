import pygame
import sys
import random

# --- Constants ---
WIDTH, HEIGHT = 700, 700

# For smooth cell-by-cell animation, use grid dimensions as odd numbers.
ROWS, COLS = 21, 21
CELL_SIZE = WIDTH // COLS
FPS = 30

# Colors (RGB) – mainly for UI and maze walls.
NAVY   = (18, 32, 47)
YELLOW = (245, 200, 70)
WHITE  = (255, 255, 255)
RED    = (255, 0, 0)
BLACK  = (0, 0, 0)

# Game State Variables
maze = []
dots = []
tissues = []
allergens = []
sneeze_bar = 0     # Range: 0 to 100
sneeze_timer = 0   # Counts game ticks for level time
score = 0
level = 1
lost = False
game_completed = False
show_instructions = True
level_selected = False
restart_button = False
level_won = False
level_time = 30 * FPS  # Each level is 30 seconds

# Movement speed in pixels per frame (adjust as desired)
MOVE_SPEED = CELL_SIZE / 5  # Moves one cell in about 5 frames

# Sneeze mechanism variables:
# When sneeze_bar reaches 100, the sneezing state is triggered.
sneezing = False
SNEEZE_DURATION = 30  # Reduced sneeze duration (30 frames ~ 1 second at 30 FPS)
sneeze_countdown = 0

# Global image variables
player_img = None
player_sneeze_img = None
tissue_img = None
germ_img = None

# Global sound variables
sneeze_sound = None
tissue_sound = None
allergen_sound = None

# --- Sound Loading Function ---
def load_sounds():
    global sneeze_sound, tissue_sound, allergen_sound
    # Load sound effects from the "shahenazalshams-attachments" folder.
    sneeze_sound = pygame.mixer.Sound("shahenazalshams-attachments/sneeze.wav")
    tissue_sound = pygame.mixer.Sound("shahenazalshams-attachments/tissue.wav")
    allergen_sound = pygame.mixer.Sound("shahenazalshams-attachments/allergen.wav")
    # Start background music (loop indefinitely)
    pygame.mixer.music.load("shahenazalshams-attachments/background.mp3")
    pygame.mixer.music.play(-1)

# --- Image Loading Function ---
def load_images():
    global player_img, player_sneeze_img, tissue_img, germ_img
    player_img = pygame.image.load("shahenazalshams-attachments/Professor_Munir.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (CELL_SIZE, CELL_SIZE))
    
    player_sneeze_img = pygame.image.load("shahenazalshams-attachments/Professor_Munir_Sneeze.png").convert_alpha()
    player_sneeze_img = pygame.transform.scale(player_sneeze_img, (CELL_SIZE, CELL_SIZE))
    
    tissue_img = pygame.image.load("shahenazalshams-attachments/Tissues.png").convert_alpha()
    tissue_img = pygame.transform.scale(tissue_img, (CELL_SIZE, CELL_SIZE))
    
    germ_img = pygame.image.load("shahenazalshams-attachments/Germs.png").convert_alpha()
    germ_img = pygame.transform.scale(germ_img, (CELL_SIZE, CELL_SIZE))

# --- Maze Generation using DFS (Recursive Backtracker) ---
def generate_maze():
    maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    start_x, start_y = 1, 1
    maze[start_y][start_x] = 0
    stack = [(start_x, start_y)]
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < COLS - 1 and 0 < ny < ROWS - 1 and maze[ny][nx] == 1:
                neighbors.append((nx, ny, dx, dy))
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            maze[y + dy//2][x + dx//2] = 0
            maze[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    maze[1][1] = 0
    return maze

# --- Player Class with Smooth Movement ---
class Player:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pos_x = grid_x * CELL_SIZE + CELL_SIZE / 2
        self.pos_y = grid_y * CELL_SIZE + CELL_SIZE / 2
        self.moving = False
        self.target_x = grid_x
        self.target_y = grid_y

    def start_move(self, dx, dy, maze):
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        if 0 <= new_x < COLS and 0 <= new_y < ROWS and maze[new_y][new_x] == 0:
            self.moving = True
            self.target_x = new_x
            self.target_y = new_y

    def update(self):
        if self.moving:
            target_px = self.target_x * CELL_SIZE + CELL_SIZE / 2
            target_py = self.target_y * CELL_SIZE + CELL_SIZE / 2
            dx = target_px - self.pos_x
            dy = target_py - self.pos_y
            dist = (dx**2 + dy**2) ** 0.5
            if dist < MOVE_SPEED:
                self.pos_x = target_px
                self.pos_y = target_py
                self.grid_x = self.target_x
                self.grid_y = self.target_y
                self.moving = False
            else:
                self.pos_x += MOVE_SPEED * dx / dist
                self.pos_y += MOVE_SPEED * dy / dist

# Global player variable
player = None

# --- Game Reset ---
def reset_game():
    global player, maze, dots, tissues, allergens, sneeze_bar, sneeze_timer, score, lost, game_completed, level_won, sneezing, sneeze_countdown
    maze.clear()
    maze.extend(generate_maze())
    player = Player(1, 1)
    dots = []
    tissues = []
    allergens = []
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 0 and (x, y) != (1, 1):
                dots.append((x, y))
                rnd = random.random()
                if rnd < 0.08:
                    tissues.append((x, y))
                elif rnd < 0.13:
                    allergens.append((x, y))
    sneeze_bar = 0
    sneeze_timer = 0
    score = 0
    lost = False
    game_completed = False
    level_won = False
    sneezing = False
    sneeze_countdown = 0

# --- Drawing Functions ---
def draw_maze(screen):
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == 1:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, YELLOW, rect)

def draw_dots(screen):
    for (x, y) in dots:
        center = (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.circle(screen, WHITE, center, CELL_SIZE // 8)

def draw_tissues(screen):
    for (x, y) in tissues:
        pos = (x * CELL_SIZE, y * CELL_SIZE)
        screen.blit(tissue_img, pos)

def draw_allergens(screen):
    for (x, y) in allergens:
        pos = (x * CELL_SIZE, y * CELL_SIZE)
        screen.blit(germ_img, pos)

def draw_player(screen):
    img = player_sneeze_img if sneezing else player_img
    pos = (int(player.pos_x - CELL_SIZE / 2), int(player.pos_y - CELL_SIZE / 2))
    screen.blit(img, pos)

def draw_ui(screen, font):
    bar_width = 200
    bar_height = 20
    bar_x = 10
    bar_y = 10
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height))
    fill_width = int(bar_width * min(sneeze_bar, 100) / 100)
    pygame.draw.rect(screen, RED, (bar_x, bar_y, fill_width, bar_height))
    time_left = max(0, int((level_time - sneeze_timer) / FPS))
    score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
    time_text = font.render(f"Time Left: {time_left}s", True, WHITE)
    screen.blit(score_text, (10, 40))
    screen.blit(time_text, (10, 70))

def draw_instructions(screen, font):
    rect = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 180, 440, 360)
    pygame.draw.rect(screen, YELLOW, rect, border_radius=30)
    title = font.render("SNEEZE ATTACK!", True, NAVY)
    authors = font.render("By Maitha Ali & Shahenaz Al Shamsi", True, NAVY)
    instr1 = font.render("Use Arrow Keys to move.", True, NAVY)
    instr2 = font.render("Collect tissues (blue) to reduce sneeze bar.", True, NAVY)
    instr3 = font.render("Avoid allergens (red) which increase it.", True, NAVY)
    instr4 = font.render("Clear all dots (white) before time runs out!", True, NAVY)
    prompt = font.render("Press any key to continue...", True, NAVY)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 150))
    screen.blit(authors, (WIDTH // 2 - authors.get_width() // 2, HEIGHT // 2 - 110))
    screen.blit(instr1, (WIDTH // 2 - instr1.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(instr2, (WIDTH // 2 - instr2.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(instr3, (WIDTH // 2 - instr3.get_width() // 2, HEIGHT // 2))
    screen.blit(instr4, (WIDTH // 2 - instr4.get_width() // 2, HEIGHT // 2 + 30))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 80))

def draw_level_selection(screen, font):
    screen.fill(NAVY)
    title = font.render("Select a Level:", True, YELLOW)
    option1 = font.render("Press 1 for Easy", True, YELLOW)
    option2 = font.render("Press 2 for Medium", True, YELLOW)
    option3 = font.render("Press 3 for Hard", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(option1, (WIDTH // 2 - option1.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(option2, (WIDTH // 2 - option2.get_width() // 2, HEIGHT // 2))
    screen.blit(option3, (WIDTH // 2 - option3.get_width() // 2, HEIGHT // 2 + 30))

def draw_level_win(screen, font):
    screen.fill(YELLOW)
    msg1 = font.render("You completed this level!", True, NAVY)
    msg2 = font.render("Press any key to continue to next level", True, NAVY)
    msg3 = font.render("Press 1 to quit", True, NAVY)
    screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2))
    screen.blit(msg3, (WIDTH // 2 - msg3.get_width() // 2, HEIGHT // 2 + 40))

def draw_win_screen(screen, font):
    screen.fill(YELLOW)
    msg = font.render("YOU'VE WON!", True, NAVY)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 20))

def draw_game_over(screen, font):
    screen.fill(NAVY)
    msg1 = font.render("Game Over!", True, WHITE)
    msg2 = font.render("Click anywhere to Restart", True, RED)
    screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 + 10))

# --- Collision Checks ---
def check_collisions():
    global score, sneeze_bar
    current_cell = (player.grid_x, player.grid_y)
    # Tissue collection
    if current_cell in dots:
        dots.remove(current_cell)
        score += 10
    if current_cell in tissues:
        tissues.remove(current_cell)
        sneeze_bar = max(sneeze_bar - 20, 0)
        score += 20
        tissue_sound.play()  # Play tissue collection sound
    # Allergen encounter
    if current_cell in allergens:
        allergens.remove(current_cell)
        sneeze_bar += 30
        allergen_sound.play()  # Play allergen encounter sound

# --- Main Game Loop ---
def main():
    global show_instructions, level_selected, lost, sneeze_timer, sneeze_bar
    global level, level_won, game_completed, restart_button, player, maze, sneezing, sneeze_countdown

    pygame.init()
    pygame.mixer.init()  # initialize the mixer for sounds
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sneeze Attack!")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)
    large_font = pygame.font.SysFont("Arial", 36)
    
    load_images()
    load_sounds()
    maze.extend(generate_maze())
    reset_game()

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if show_instructions:
                    show_instructions = False
                    continue
                if not level_selected:
                    if event.key == pygame.K_1:
                        level = 1
                    elif event.key == pygame.K_2:
                        level = 2
                    elif event.key == pygame.K_3:
                        level = 3
                    level_selected = True
                    reset_game()
                    continue
                if level_won:
                    if event.key == pygame.K_1:
                        game_completed = True
                    else:
                        level += 1
                        level_won = False
                        reset_game()
                    continue
                if lost:
                    reset_game()
                    lost = False
                    continue
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if lost or restart_button:
                    reset_game()
                    lost = False
                    restart_button = False

        # If not sneezing, allow movement via continuous key input.
        if not sneezing and not player.moving:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.start_move(-1, 0, maze)
            elif keys[pygame.K_RIGHT]:
                player.start_move(1, 0, maze)
            elif keys[pygame.K_UP]:
                player.start_move(0, -1, maze)
            elif keys[pygame.K_DOWN]:
                player.start_move(0, 1, maze)

        player.update()

        if show_instructions:
            screen.fill(YELLOW)
            draw_instructions(screen, large_font)
            pygame.display.flip()
            continue

        if not level_selected:
            draw_level_selection(screen, large_font)
            pygame.display.flip()
            continue

        if level_won:
            draw_level_win(screen, large_font)
            pygame.display.flip()
            continue

        if game_completed:
            draw_win_screen(screen, large_font)
            pygame.display.flip()
            continue

        sneeze_timer += 1
        if not sneezing:
            sneeze_bar += 0.1 + (0.1 * (level - 1))
        
        # Trigger sneeze state if sneeze_bar is full
        if sneeze_bar >= 100 and not sneezing:
            sneezing = True
            sneeze_countdown = SNEEZE_DURATION
            sneeze_sound.play()  # Play the sneeze sound when the character sneezes

        if sneezing:
            sneeze_countdown -= 1
            if sneeze_countdown <= 0:
                sneezing = False
                sneeze_bar = 0

        time_left = max(0, int((level_time - sneeze_timer) / FPS))
        if time_left <= 5 and (pygame.time.get_ticks() // 300) % 2 == 0:
            screen.fill(RED)
        else:
            screen.fill(NAVY)

        draw_maze(screen)
        draw_dots(screen)
        draw_tissues(screen)
        draw_allergens(screen)
        draw_player(screen)
        draw_ui(screen, font)

        if not player.moving and not sneezing:
            check_collisions()

        if len(dots) == 0:
            score += 100 * level
            if level < 3:
                level_won = True
            else:
                game_completed = True

        if sneeze_timer > level_time:
            lost = True

        if lost:
            draw_game_over(screen, large_font)
            restart_button = True

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
