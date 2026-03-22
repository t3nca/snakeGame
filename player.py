# ============================================================
#  player.py  –  Snake logic: movement, growth, collision
# ============================================================

import pygame
from settings import (
    TILE_SIZE, GRID_SIZE,
    SNAKE_START_COL, SNAKE_START_ROW, SNAKE_START_DIR, SNAKE_START_LENGTH,
    C_SNAKE_HEAD, C_SNAKE_BODY, C_SNAKE_OUTLINE,
    C_SNAKE_EYE, C_SNAKE_PUPIL, C_BLACK,
)


class Snake:
    """
    Stores the snake as a list of (col, row) tuples,
    head first.  All mutation goes through move() and grow().
    """

    def __init__(self):
        self.reset()

    # ── setup ──────────────────────────────────────────────

    def reset(self) -> None:
        start = (SNAKE_START_COL, SNAKE_START_ROW)
        # Build initial body extending to the left of the start tile
        self.body: list[tuple[int, int]] = [
            (start[0] - i, start[1]) for i in range(SNAKE_START_LENGTH)
        ]
        self.direction: tuple[int, int] = SNAKE_START_DIR
        self._pending_growth: int = 0

    # ── direction ──────────────────────────────────────────

    def change_direction(self, new_dir: tuple[int, int]) -> None:
        """Ignore reversal; accept any other 90-degree turn."""
        dx, dy = self.direction
        if new_dir != (-dx, -dy):
            self.direction = new_dir

    # ── movement ───────────────────────────────────────────

    def move(self) -> None:
        """Advance the snake one tile in the current direction."""
        hx, hy   = self.body[0]
        dx, dy   = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)
        if self._pending_growth > 0:
            self._pending_growth -= 1
        else:
            self.body.pop()

    def grow(self) -> None:
        """Queue one extra segment to be added on the next move."""
        self._pending_growth += 1

    # ── collision ──────────────────────────────────────────

    def check_wall_collision(self) -> bool:
        hx, hy = self.body[0]
        return not (0 <= hx < GRID_SIZE and 0 <= hy < GRID_SIZE)

    def check_self_collision(self) -> bool:
        return self.body[0] in self.body[1:]

    # ── queries ────────────────────────────────────────────

    def get_positions(self) -> set[tuple[int, int]]:
        return set(self.body)

    @property
    def length(self) -> int:
        return len(self.body)

    # ── rendering ──────────────────────────────────────────

    def draw(self, surface: pygame.Surface, ox: int, oy: int) -> None:
        n = len(self.body)
        for i, (col, row) in enumerate(self.body):
            self._draw_segment(surface, ox, oy, col, row, i, n)
        # Draw eyes on top so they're never occluded
        self._draw_eyes(surface, ox, oy)

    # ── private helpers ────────────────────────────────────

    def _draw_segment(
        self,
        surface: pygame.Surface,
        ox: int, oy: int,
        col: int, row: int,
        index: int, total: int,
    ) -> None:
        pad    = 4
        radius = 6 if index == 0 else 4

        x = ox + col * TILE_SIZE
        y = oy + row * TILE_SIZE

        # Gradient from head (bright) to tail (dim)
        t      = index / max(total - 1, 1)
        colour = _lerp_colour(C_SNAKE_HEAD, C_SNAKE_BODY, t)

        rect = pygame.Rect(x + pad, y + pad, TILE_SIZE - pad * 2, TILE_SIZE - pad * 2)
        pygame.draw.rect(surface, C_SNAKE_OUTLINE, rect, border_radius=radius + 1)
        inner = rect.inflate(-2, -2)
        pygame.draw.rect(surface, colour, inner, border_radius=radius)

    def _draw_eyes(self, surface: pygame.Surface, ox: int, oy: int) -> None:
        if not self.body:
            return
        col, row = self.body[0]
        cx = ox + col * TILE_SIZE + TILE_SIZE // 2
        cy = oy + row * TILE_SIZE + TILE_SIZE // 2
        dx, dy = self.direction

        # Perpendicular offset for two eyes
        px, py = -dy, dx  # rotate direction 90°

        EYE_DIST   = 7
        EYE_RADIUS = 4
        EYE_FWD    = 5   # push eyes forward toward the nose

        for sign in (-1, 1):
            ex = cx + dx * EYE_FWD + px * EYE_DIST * sign
            ey = cy + dy * EYE_FWD + py * EYE_DIST * sign
            pygame.draw.circle(surface, C_SNAKE_EYE, (ex, ey), EYE_RADIUS)
            pygame.draw.circle(surface, C_SNAKE_PUPIL, (ex + dx, ey + dy), 2)


# ── utility ────────────────────────────────────────────────

def _lerp_colour(
    c1: tuple[int, int, int],
    c2: tuple[int, int, int],
    t: float,
) -> tuple[int, int, int]:
    """Linear interpolation between two RGB colours."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
