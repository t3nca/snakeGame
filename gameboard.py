# gameboard.py
# Draws the 12x12 checkerboard. The board never changes between frames,
# so we render it once into a Surface at startup and just blit that
# cached surface every frame — no per-frame tile drawing needed.

import pygame
import settings as S


class GameBoard:

    def __init__(self, surface, offset_x, offset_y):
        self.surface  = surface
        self.offset_x = offset_x
        self.offset_y = offset_y
        self._cached  = self._build_board_surface()

    def draw(self):
        self.surface.blit(self._cached, (self.offset_x, self.offset_y))
        # Draw a thin border around the entire play area
        board_rect = pygame.Rect(self.offset_x, self.offset_y, S.BOARD_PX, S.BOARD_PX)
        pygame.draw.rect(self.surface, S.BOARD_EDGE, board_rect, 2)

    def _build_board_surface(self):
        """Render all 144 tiles once and return the finished surface."""
        board = pygame.Surface((S.BOARD_PX, S.BOARD_PX))
        for row in range(S.GRID_SIZE):
            for col in range(S.GRID_SIZE):
                colour = S.TILE_LIGHT if (row + col) % 2 == 0 else S.TILE_DARK
                rect   = pygame.Rect(col * S.TILE_SIZE, row * S.TILE_SIZE, S.TILE_SIZE, S.TILE_SIZE)
                pygame.draw.rect(board, colour, rect)
        return board
