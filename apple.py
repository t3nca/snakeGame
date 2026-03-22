# ============================================================
#  apple.py  –  Apple: random spawning and rendering
# ============================================================

import random
import math
import pygame
from settings import (
    TILE_SIZE, GRID_SIZE,
    C_APPLE, C_APPLE_DARK, C_APPLE_SHINE, C_STEM, C_LEAF,
)


class Apple:
    """
    Manages a single apple that spawns on an empty tile and
    is drawn with a small pixel-art icon.
    """

    def __init__(self):
        self.position: tuple[int, int] | None = None
        self._bob_timer: float = 0.0   # animation accumulator

    # ── public ─────────────────────────────────────────────

    def spawn(self, occupied: set[tuple[int, int]]) -> None:
        """Place the apple on a random tile not occupied by the snake."""
        all_tiles = {
            (c, r) for c in range(GRID_SIZE) for r in range(GRID_SIZE)
        }
        available = list(all_tiles - occupied)
        if available:
            self.position = random.choice(available)
        else:
            self.position = None   # board is completely full – shouldn't happen

    def update(self, dt: float) -> None:
        """Advance the idle bobbing animation."""
        self._bob_timer += dt

    def draw(self, surface: pygame.Surface, ox: int, oy: int) -> None:
        if self.position is None:
            return

        col, row = self.position
        # Centre of this tile in screen-space
        cx = ox + col * TILE_SIZE + TILE_SIZE // 2
        cy = oy + row * TILE_SIZE + TILE_SIZE // 2

        # Gentle sine-wave bob (±2 px)
        bob = int(math.sin(self._bob_timer * 3.0) * 2)
        cy += bob

        self._draw_apple(surface, cx, cy)

    # ── private ────────────────────────────────────────────

    @staticmethod
    def _draw_apple(surface: pygame.Surface, cx: int, cy: int) -> None:
        r = TILE_SIZE // 2 - 5          # main body radius

        # Shadow
        shadow_surf = pygame.Surface((r * 2 + 4, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect())
        surface.blit(shadow_surf, (cx - r - 2, cy + r - 2))

        # Main body
        pygame.draw.circle(surface, C_APPLE_DARK, (cx, cy), r)
        pygame.draw.circle(surface, C_APPLE,      (cx, cy), r - 2)

        # Highlight shine
        pygame.draw.circle(surface, C_APPLE_SHINE, (cx - r // 3, cy - r // 3), r // 4)

        # Stem (small brown rectangle)
        stem_rect = pygame.Rect(cx - 1, cy - r - 5, 3, 6)
        pygame.draw.rect(surface, C_STEM, stem_rect, border_radius=1)

        # Leaf (tiny rotated ellipse approximated as a filled polygon)
        lx, ly = cx + 4, cy - r - 3
        leaf_pts = [
            (lx,     ly    ),
            (lx + 6, ly - 3),
            (lx + 8, ly    ),
            (lx + 4, ly + 2),
        ]
        pygame.draw.polygon(surface, C_LEAF, leaf_pts)
