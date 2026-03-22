# ============================================================
#  gameboard.py  –  Draws the 12×12 checkerboard play field
# ============================================================

import pygame
from settings import (
    TILE_SIZE, GRID_SIZE,
    C_TILE_LIGHT, C_TILE_DARK, C_BOARD_BORDER,
)


class GameBoard:
    """Responsible solely for rendering the tiled game world."""

    def __init__(self, surface: pygame.Surface, offset_x: int, offset_y: int):
        self.surface  = surface
        self.offset_x = offset_x
        self.offset_y = offset_y

        # Pre-bake the board into its own surface so we only redraw it once.
        board_px = GRID_SIZE * TILE_SIZE
        self._board_surf = pygame.Surface((board_px, board_px))
        self._bake()

    # ── public ─────────────────────────────────────────────

    def draw(self) -> None:
        """Blit the cached board surface, then draw its border."""
        self.surface.blit(self._board_surf, (self.offset_x, self.offset_y))
        board_px = GRID_SIZE * TILE_SIZE
        border = pygame.Rect(self.offset_x, self.offset_y, board_px, board_px)
        pygame.draw.rect(self.surface, C_BOARD_BORDER, border, 2)

    def tile_rect(self, col: int, row: int) -> pygame.Rect:
        """Return the screen-space Rect for a given tile (col, row)."""
        return pygame.Rect(
            self.offset_x + col * TILE_SIZE,
            self.offset_y + row * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE,
        )

    # ── private ────────────────────────────────────────────

    def _bake(self) -> None:
        """Render tiles into the cached surface once at startup."""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                colour = C_TILE_LIGHT if (row + col) % 2 == 0 else C_TILE_DARK
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self._board_surf, colour, rect)
