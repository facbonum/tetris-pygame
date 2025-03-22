import pygame, random, sys

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 320, 640
BLOCK_SIZE = 32
BOARD_WIDTH, BOARD_HEIGHT = SCREEN_WIDTH // BLOCK_SIZE, SCREEN_HEIGHT // BLOCK_SIZE
FALL_SPEED, MOVE_SPEED = 500, 50

# Colors
COLORS = [(255, 85, 85), (255, 165, 0), (255, 255, 85), (0, 255, 85), (85, 255, 255), (85, 85, 255), (255, 85, 255)]
WHITE, BLACK, GRID_COLOR, SHADOW = (255, 255, 255), (0, 0, 0), (30, 30, 30), (0, 0, 0)

# Shapes
SHAPES = [
    [[1, 1, 1, 1]], [[1, 1], [1, 1]], [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]], [[0, 1, 1], [1, 1, 0]],
    [[1, 0, 0], [1, 1, 1]], [[0, 0, 1], [1, 1, 1]]
]

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()


def new_tetromino():
    """Generates a new random tetromino"""
    shape = random.choice(SHAPES)
    color = random.choice(COLORS)
    spawn_x = BOARD_WIDTH // 2 - len(shape[0]) // 2
    return shape, color, [spawn_x, 0]


def rotate(shape):
    """Rotates tetromino clockwise"""
    return [list(row) for row in zip(*shape[::-1])]


def valid_position(board, shape, offset):
    """Check if shape fits on the board at the offset"""
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            if cell:
                if off_x + cx < 0 or off_x + cx >= BOARD_WIDTH or off_y + cy >= BOARD_HEIGHT:
                    return False
                if off_y + cy >= 0 and board[off_y + cy][off_x + cx]:
                    return False
    return True


def hard_drop(board, shape, offset):
    """Instantly drop the tetromino to the floor"""
    while valid_position(board, shape, [offset[0], offset[1] + 1]):
        offset[1] += 1
    return offset


def clear_lines(board):
    """Clear completed lines and return count"""
    lines = [i for i, row in enumerate(board) if all(row)]
    for i in lines:
        del board[i]
        board.insert(0, [0] * BOARD_WIDTH)
    return len(lines)


def draw_board(board):
    """Draw the board grid and placed pieces"""
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, cell, rect)
                pygame.draw.line(screen, WHITE, rect.topleft, rect.topright, 2)
                pygame.draw.line(screen, WHITE, rect.topleft, rect.bottomleft, 2)
                pygame.draw.line(screen, BLACK, rect.bottomleft, rect.bottomright, 2)
                pygame.draw.line(screen, BLACK, rect.topright, rect.bottomright, 2)

    # Draw grid lines
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


def draw_tetromino(x, y, shape, color):
    """Draws the falling tetromino with shading and shadow"""
    shadow_offset = 4
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            if cell:
                # Shadow
                pygame.draw.rect(screen, SHADOW, (
                    x + cx * BLOCK_SIZE + shadow_offset, y + cy * BLOCK_SIZE + shadow_offset, BLOCK_SIZE, BLOCK_SIZE))
                # Main block
                rect = pygame.Rect(x + cx * BLOCK_SIZE, y + cy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.line(screen, WHITE, rect.topleft, rect.topright, 2)
                pygame.draw.line(screen, WHITE, rect.topleft, rect.bottomleft, 2)
                pygame.draw.line(screen, BLACK, rect.bottomleft, rect.bottomright, 2)
                pygame.draw.line(screen, BLACK, rect.topright, rect.bottomright, 2)


def main():
    """Main game loop"""
    board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
    current_shape, current_color, offset = new_tetromino()

    fall_timer, move_timer = pygame.time.get_ticks(), 0
    paused = False

    while True:
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Pause
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_DOWN:  # Hard drop
                        offset = hard_drop(board, current_shape, offset)
                    if event.key == pygame.K_UP:  # Rotate
                        rotated = rotate(current_shape)
                        if valid_position(board, rotated, offset):
                            current_shape = rotated

        keys = pygame.key.get_pressed()
        if not paused:
            if keys[pygame.K_LEFT] and current_time - move_timer > MOVE_SPEED:
                new_offset = [offset[0] - 1, offset[1]]
                if valid_position(board, current_shape, new_offset):
                    offset = new_offset
                move_timer = current_time

            if keys[pygame.K_RIGHT] and current_time - move_timer > MOVE_SPEED:
                new_offset = [offset[0] + 1, offset[1]]
                if valid_position(board, current_shape, new_offset):
                    offset = new_offset
                move_timer = current_time

        # Gravity
        if not paused and current_time - fall_timer >= FALL_SPEED:
            if valid_position(board, current_shape, [offset[0], offset[1] + 1]):
                offset[1] += 1
            else:
                for cy, row in enumerate(current_shape):
                    for cx, cell in enumerate(row):
                        if cell:
                            board[offset[1] + cy][offset[0] + cx] = current_color
                clear_lines(board)
                current_shape, current_color, offset = new_tetromino()
            fall_timer = current_time

        # Draw
        draw_board(board)
        draw_tetromino(offset[0] * BLOCK_SIZE, offset[1] * BLOCK_SIZE, current_shape, current_color)

        # Pause screen
        if paused:
            font = pygame.font.SysFont('Segoe UI', 50)
            pause_text = font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 25))

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()
