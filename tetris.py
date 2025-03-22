import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 320, 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Colors (retro palette)
COLORS = [
    (255, 85, 85), (255, 165, 0), (255, 255, 85), (0, 255, 85),
    (85, 255, 255), (85, 85, 255), (255, 85, 255)
]
WHITE, BLACK, GRID_COLOR = (255, 255, 255), (0, 0, 0), (30, 30, 30)

# Game constants
BLOCK_SIZE = 32
BOARD_WIDTH, BOARD_HEIGHT = SCREEN_WIDTH // BLOCK_SIZE, SCREEN_HEIGHT // BLOCK_SIZE
FALL_SPEED = 500  # Slower falling speed (milliseconds)
MOVE_DELAY = 150  # Delay for horizontal movement
ROTATE_DELAY = 200  # Delay for rotation

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]], [[1, 1], [1, 1]], [[0, 1, 0], [1, 1, 1]], 
    [[1, 1, 0], [0, 1, 1]], [[0, 1, 1], [1, 1, 0]], 
    [[1, 0, 0], [1, 1, 1]], [[0, 0, 1], [1, 1, 1]]
]

# Draw tetromino with shading and shadow
def draw_tetromino(x, y, shape, color):
    shadow_offset, shadow_color = 4, (0, 0, 0)
    # Shadow
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, shadow_color, (x + cx * BLOCK_SIZE + shadow_offset, y + cy * BLOCK_SIZE + shadow_offset, BLOCK_SIZE, BLOCK_SIZE))
    # Main blocks with shading
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(x + cx * BLOCK_SIZE, y + cy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.line(screen, WHITE, rect.topleft, rect.topright, 2)
                pygame.draw.line(screen, WHITE, rect.topleft, rect.bottomleft, 2)
                pygame.draw.line(screen, BLACK, rect.bottomleft, rect.bottomright, 2)
                pygame.draw.line(screen, BLACK, rect.topright, rect.bottomright, 2)

# Rotate shape
def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

# Valid position check
def valid_position(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            if cell:
                # Check if the position is within bounds
                if off_x + cx < 0 or off_x + cx >= BOARD_WIDTH or off_y + cy >= BOARD_HEIGHT:
                    return False
                # Check if there's already a block in the position
                if off_y + cy >= 0 and board[off_y + cy][off_x + cx]:
                    return False
    return True

# Hard drop (instant drop to the bottom)
def hard_drop(board, shape, offset):
    while valid_position(board, shape, [offset[0], offset[1] + 1]):
        offset[1] += 1
    return offset

# Clear full lines
def clear_lines(board):
    full_lines = [i for i, row in enumerate(board) if all(cell for cell in row)]
    for i in full_lines:
        del board[i]
        board.insert(0, [0] * BOARD_WIDTH)
    return len(full_lines)

# Draw the game board with grid and blocks
def draw_board(board):
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, cell, rect)
                pygame.draw.line(screen, WHITE, rect.topleft, rect.topright, 2)
                pygame.draw.line(screen, WHITE, rect.topleft, rect.bottomleft, 2)
                pygame.draw.line(screen, BLACK, rect.bottomleft, rect.bottomright, 2)
                pygame.draw.line(screen, BLACK, rect.topright, rect.bottomright, 2)

# Main game loop
def main():
    clock = pygame.time.Clock()
    board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]

    def new_tetromino():
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        # Start spawn in the middle of the board, ensuring valid position
        spawn_x = BOARD_WIDTH // 2 - len(shape[0]) // 2
        spawn_y = 0  # Start from the top row
        return shape, color, [spawn_x, spawn_y]

    current_shape, current_color, offset = new_tetromino()
    fall_timer = pygame.time.get_ticks()  # Start fall timer
    last_rotate_time, last_move_time = 0, 0
    paused = False

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Toggle pause
                    paused = not paused
                if event.key == pygame.K_DOWN:  # Hard drop on down arrow
                    offset = hard_drop(board, current_shape, offset)
                if event.key == pygame.K_UP and not paused:  # Rotate
                    rotated_shape = rotate(current_shape)
                    if valid_position(board, rotated_shape, offset):
                        current_shape = rotated_shape
                if event.key == pygame.K_LEFT and not paused:  # Left movement
                    new_offset = [offset[0] - 1, offset[1]]
                    if valid_position(board, current_shape, new_offset):
                        offset = new_offset
                if event.key == pygame.K_RIGHT and not paused:  # Right movement
                    new_offset = [offset[0] + 1, offset[1]]
                    if valid_position(board, current_shape, new_offset):
                        offset = new_offset

        # Gravity - control speed consistently
        if not paused:
            current_time = pygame.time.get_ticks()
            if current_time - fall_timer >= FALL_SPEED:  # Ensure the timer is consistent
                if valid_position(board, current_shape, [offset[0], offset[1] + 1]):
                    offset[1] += 1
                else:
                    # Place the tetromino on the board at the final position
                    for cy, row in enumerate(current_shape):
                        for cx, cell in enumerate(row):
                            if cell:
                                board[offset[1] + cy][offset[0] + cx] = current_color
                    # Clear lines and spawn a new tetromino
                    lines_cleared = clear_lines(board)
                    current_shape, current_color, offset = new_tetromino()  # Get a new tetromino
                    fall_timer = pygame.time.get_ticks()  # Reset fall timer after tetromino placement

        # Draw the game
        draw_board(board)
        draw_tetromino(offset[0] * BLOCK_SIZE, offset[1] * BLOCK_SIZE, current_shape, current_color)

        # If paused, display the pause screen
        if paused:
            font = pygame.font.SysFont('Segoe UI', 50)
            pause_text = font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 25))

        pygame.display.update()
        clock.tick(8)

# Run the game
if __name__ == "__main__":
    main()
