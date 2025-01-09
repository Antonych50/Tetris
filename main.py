import random
import sys
import time
import keyboard
import pygame
from pygame.locals import *

# Константы
SCREEN_WIDTH = 321
SCREEN_HEIGHT = 641
BLOCK_SIZE = 32
COLUMNS = SCREEN_WIDTH // BLOCK_SIZE
ROWS = SCREEN_HEIGHT // BLOCK_SIZE
FPS = 3

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
# Определение фигурок тетриса
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[0, 1, 0], [1, 1, 1]]  # T
]

class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.fps_prev = FPS
        self.fps_curr = FPS
        self.reset()

    def reset(self):
        self.board = [[0] * COLUMNS for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.falling_piece = None
        self.next_piece = self.get_random_shape()
        self.falling_piece = self.next_piece
        self.game_over = False
        self.fps_curr = self.fps_prev

    def get_random_shape(self):
        shape = random.choice(SHAPES)
        return {
            'shape': shape,
            'x': COLUMNS  // 2 - len(shape[0]) // 2,
            'y': 0
        }

    def draw_grid(self):
        for i in range(COLUMNS + 1):
            pygame.draw.line(
                self.screen, GRAY,
                (i * BLOCK_SIZE, 0),
                (i * BLOCK_SIZE, SCREEN_HEIGHT)
            )
        for j in range(ROWS + 1):
            pygame.draw.line(
                self.screen, GRAY,
                (0, j * BLOCK_SIZE),
                (SCREEN_WIDTH, j * BLOCK_SIZE)
            )

    def draw_board(self):
        #pass
        for i in range(ROWS):
            for j in range(COLUMNS):
                if self.board[i][j]:
                    pygame.draw.rect(
                        self.screen, BLUE,
                        (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )

    def draw_falling_piece(self):
        if not self.falling_piece:
            return
        #if self.fps_curr == 150: self.fps_curr = self.fps_prev
        shape = self.falling_piece['shape']
        x = self.falling_piece['x']
        y = self.falling_piece['y']
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j]:
                    pygame.draw.rect(
                        self.screen, GREEN,
                        ((x + j) * BLOCK_SIZE, (y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )


    def draw_next_piece(self):
        #if self.fps_curr == 150: self.fps_curr = self.fps_prev
        next_piece = self.next_piece
        shape = next_piece['shape']
        x = next_piece['x'] * BLOCK_SIZE# + 160
        y = next_piece['y'] * BLOCK_SIZE# + 80
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j]:
                    pygame.draw.rect(
                        self.screen, GREEN,
                        (x + j * BLOCK_SIZE, y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )

    def piece_speed(self, ds:int):
        self.fps_curr += ds
        if self.fps_curr < 0: self.speed = FPS

    def move_down(self):
        if not self.falling_piece:
            return
        self.falling_piece['y'] += 1
        if self.check_collision():
            if self.falling_piece['y']==1:
                self.reset()
                self.fps_curr = self.fps_prev
            else:
                self.falling_piece['y'] -= 1
                self.freeze_piece()


    def freeze_piece(self):
        if not self.falling_piece:
            return
        piece = self.falling_piece
        shape = piece['shape']
        x = piece['x']
        y = piece['y']
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j]:
                    self.board[y + i][x + j] = 1
        self.clear_rows()
        self.new_piece()

    def new_piece(self):
        self.falling_piece = self.next_piece
        self.next_piece = self.get_random_shape()
        if self.check_collision():
            self.game_over = True

    def check_collision(self):
        if not self.falling_piece:
            return False
        if self.fps_curr == 150: self.fps_curr = self.fps_prev
        piece = self.falling_piece
        shape = piece['shape']
        x = piece['x']
        y = piece['y']
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j] and (y + i >= ROWS or x + j < 0 or x + j >= COLUMNS or self.board[y + i][x + j]):
                    return True
        return False

    def clear_rows(self):
        rows_to_clear = []
        for i in range(ROWS):
            if all(self.board[i]):
                rows_to_clear.append(i)
        for row in reversed(rows_to_clear):
            del self.board[row]
            self.board.insert(0, [0] * COLUMNS)
        self.score += len(rows_to_clear) ** 2

    def rotate_piece(self):
        if not self.falling_piece:
            return
        piece = self.falling_piece
        shape = piece['shape']
        new_shape = list(zip(*shape[::-1]))
        piece['shape'] = new_shape
        if self.check_collision():
            piece['shape'] = shape

    def reflect_piece(self):
        if not self.falling_piece:
            return
        piece = self.falling_piece
        shape = piece['shape']
        new_shape = shape[::-1]
        piece['shape'] = new_shape
        if self.check_collision():
            piece['shape'] = shape

    def move_sideways(self, dx):
        if not self.falling_piece:
            return
        self.falling_piece['x'] += dx
        if self.check_collision():
            self.falling_piece['x'] -= dx

    def run(self):
        while True:
            self.clock.tick(self.fps_curr)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        self.move_sideways(-1)
                    elif event.key == K_RIGHT:
                        self.move_sideways(1)
                    elif event.key == K_UP:
                        self.rotate_piece()
                    elif event.key == K_PAGEUP:
                        self.reflect_piece()
                        self.move_down()
                    elif (event.key == K_DOWN) or (event.key == K_RETURN):#роняем фигурку
                        self.fps_prev = self.fps_curr
                        self.fps_curr = 150
                        self.game_over = True
                        #print(f"{self.game_over}")

                    elif event.key == K_f:#увеличиваем скорость
                        self.piece_speed(1)
                    elif event.key == K_s:#уменьшаем скорость
                        self.piece_speed(-1)
                    elif event.key == K_w:
                        keyboard.wait("SPACE")
                        
            if not self.game_over:
                self.move_down()
                #pass
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_board()
            self.draw_falling_piece()
            #self.draw_next_piece
            self.game_over = False
            pygame.display.update()

if __name__ == "__main__":
    game = Tetris()
    game.run()