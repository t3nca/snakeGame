# apple.py
# Handles apple spawning and drawing.
# The apple bobs up and down slightly using a sine wave animation.

import random
import math
import pygame
import sprite_loader as sprites
import settings as S


class Apple:

    def __init__(self):
        self.position  = None  # (col, row) grid tile, or None if not yet spawned
        self._bob_time = 0.0   # accumulates real time to drive the bobbing

    def spawn(self, occupied_tiles):
        """Place the apple on a random tile that the snake isn't on."""
        all_tiles = {(c, r) for c in range(S.GRID_SIZE) for r in range(S.GRID_SIZE)}
        free_tiles = list(all_tiles - occupied_tiles)
        self.position = random.choice(free_tiles) if free_tiles else None

    def update(self, dt):
        self._bob_time += dt

    def draw(self, surface, ox, oy):
        if self.position is None:
            return

        col, row = self.position
        x = ox + col * S.TILE_SIZE
        y = oy + row * S.TILE_SIZE

        # ±2 pixel vertical bob
        bob = int(math.sin(self._bob_time * 3.0) * 2)

        spr = sprites.images.get("apple")
        if spr:
            surface.blit(spr, (x, y + bob))
        else:
            self._draw_plain(surface, x + S.TILE_SIZE // 2, y + S.TILE_SIZE // 2 + bob)

    @staticmethod
    def _draw_plain(surface, cx, cy):
        """Fallback: draw the apple procedurally when no sprite is loaded."""
        r = S.TILE_SIZE // 2 - 5

        # Drop shadow
        shadow = pygame.Surface((r*2 + 4, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
        surface.blit(shadow, (cx - r - 2, cy + r - 2))

        pygame.draw.circle(surface, S.APPLE_DARK,  (cx, cy), r)
        pygame.draw.circle(surface, S.APPLE_RED,   (cx, cy), r - 2)
        pygame.draw.circle(surface, S.APPLE_SHINE, (cx - r//3, cy - r//3), r // 4)

        pygame.draw.rect(surface, S.APPLE_STEM, (cx - 1, cy - r - 5, 3, 6), border_radius=1)

        lx, ly = cx + 4, cy - r - 3
        pygame.draw.polygon(surface, S.APPLE_LEAF,
                            [(lx, ly), (lx+6, ly-3), (lx+8, ly), (lx+4, ly+2)])
