import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 320, 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tengen Tetris")

# Colors (retro palette)
COLORS = [
    (255, 85, 85), (255, 165, 0), (255, 255, 85), (0, 255, 85),
    (85, 255, 255), (85, 85, 255), (255, 85, 255)
]
WHITE, BLACK, GRID_COLOR = (255, 255, 255), (0, 0, 0), (30, 30, 30)

# Game constants
BLOCK_SIZE = 32
BOARD_WIDTH, BOARD_HEIGHT = SCREEN_WIDTH // BLOCK_SIZE, SCREEN_HEIGHT // BLOCK_SIZE
FALL_SPEED, MOVE_DELAY, ROTATE_DELAY, HARD_DROP_DELAY = 30, 150, 200, 500

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
def rotate(shape): return [list(row) for row in zip(*shape[::-1])]

# Valid position check
def valid_position(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            if cell:
                if off_x + cx < 0 or off_x + cx >= BOARD_WIDTH or off_y + cy >= BOARD_HEIGHT or board[off_y + cy][off_x + cx]:
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
        return shape, color, [BOARD_WIDTH // 2 - len(shape[0]) // 2, 0]

    current_shape, current_color, offset = new_tetromino()
    fall_timer, hard_drop_timer, last_rotate_time, last_move_time = 0, 0, 0, 0

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(), sys.exit()

        keys, current_time = pygame.key.get_pressed(), pygame.time.get_ticks()

        # Horizontal movement with delay
        if current_time - last_move_time > MOVE_DELAY:
            move_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 1  # Left or Right movement
            if move_x != 0:
                new_offset_x = offset[0] + move_x
                if valid_position(board, current_shape, [new_offset_x, offset[1]]): offset[0] = new_offset_x
                last_move_time = current_time

        # Hard drop
        if keys[pygame.K_DOWN] and current_time - hard_drop_timer > HARD_DROP_DELAY:
            offset = hard_drop(board, current_shape, offset)
            hard_drop_timer = current_time

        # Rotation with delay
        if keys[pygame.K_UP] and current_time - last_rotate_time > ROTATE_DELAY:
            rotated_shape = rotate(current_shape)
            if valid_position(board, rotated_shape, offset):
                current_shape = rotated_shape
                last_rotate_time = current_time

        # Gravity
        fall_timer += 1
        if fall_timer >= FALL_SPEED:
            if valid_position(board, current_shape, [offset[0], offset[1] + 1]):
                offset[1] += 1
            else:
                for cy, row in enumerate(current_shape):
                    for cx, cell in enumerate(row):
                        if cell:
                            board[offset[1] + cy][offset[0] + cx] = current_color
                current_shape, current_color, offset = new_tetromino()
            fall_timer = 0

        draw_board(board)
        draw_tetromino(offset[0] * BLOCK_SIZE, offset[1] * BLOCK_SIZE, current_shape, current_color)
        pygame.display.update()
        clock.tick(60)

# Run the game
if __name__ == "__main__":
    main()
