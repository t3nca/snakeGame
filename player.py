# player.py
# Everything to do with the snake: its position, movement,
# growth, collision detection, and drawing.
#
# The snake is stored as a list of (col, row) grid positions,
# head first. So body[0] is the head, body[-1] is the tail tip.
from settings import Apple_eaten as apple_eaten
import pygame
import sprite_loader as sprites
import settings as S


class Snake:

    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    # Setup / reset
    # ------------------------------------------------------------------

    def reset(self):
        # Build the starting body. Each extra segment sits one tile to
        # the left of the previous one (snake starts moving right).
        self.body      = [(S.START_COL - i, S.START_ROW) for i in range(S.START_LENGTH)]
        self.direction = S.START_DIR
        self._queued_growth = 0  # segments to add on upcoming moves

    # ------------------------------------------------------------------
    # Every-frame update
    # ------------------------------------------------------------------

    def change_direction(self, new_dir):
        # Ignore a request to reverse (that would make the snake eat itself)
        dx, dy = self.direction
        if new_dir != (-dx, -dy):
            self.direction = new_dir

    def move(self):
        hx, hy = self.body[0]
        dx, dy = self.direction
        self.body.insert(0, (hx + dx, hy + dy))  # add new head

        if self._queued_growth > 0:
            self._queued_growth -= 1  # keep the tail: snake gets longer
        else:
            self.body.pop()  # remove the tail: length stays the same

    def grow(self):
        """Call this when the snake eats an apple."""
        apple_eaten = pygame.mixer.Sound(S.Apple_eaten)
        apple_eaten.play()
        self._queued_growth += 1


    # ------------------------------------------------------------------
    # Collision checks  (called by main.py after every move)
    # ------------------------------------------------------------------

    def hit_wall(self):
        hx, hy = self.body[0]
        return not (0 <= hx < S.GRID_SIZE and 0 <= hy < S.GRID_SIZE)

    def hit_self(self):
        return self.body[0] in self.body[1:]

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def occupied_tiles(self):
        """Return the set of grid tiles the snake currently fills."""
        return set(self.body)

    @property
    def length(self):
        return len(self.body)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface, ox, oy):
        """
        Draw every segment. Each segment can be a head, a straight body,
        a corner bend, or a tail tip — chosen by looking at the neighbouring
        segments to work out the entry and exit directions.
        """
        n = len(self.body)
        for i in range(n):
            col, row   = self.body[i]
            entry, exit = self._segment_directions(i)

            if i == 0:
                self._draw_head(surface, ox, oy, col, row)
            elif i == n - 1:
                self._draw_tail(surface, ox, oy, col, row, entry)
            else:
                self._draw_body(surface, ox, oy, col, row, entry, exit)

        # When using procedural (non-sprite) drawing the eyes are drawn
        # last so they always appear on top of the body.
        if not sprites.get_head(self.direction):
            self._draw_eyes(surface, ox, oy)

    # ------------------------------------------------------------------
    # Per-segment drawing helpers
    # ------------------------------------------------------------------

    def _draw_head(self, surface, ox, oy, col, row):
        spr = sprites.get_head(self.direction)
        if spr:
            surface.blit(spr, (ox + col * S.TILE_SIZE, oy + row * S.TILE_SIZE))
        else:
            self._draw_segment_plain(surface, ox, oy, col, row, index=0)

    def _draw_body(self, surface, ox, oy, col, row, entry, exit):
        spr = sprites.get_body(entry, exit)
        if spr:
            surface.blit(spr, (ox + col * S.TILE_SIZE, oy + row * S.TILE_SIZE))
        else:
            idx = self.body.index((col, row))
            self._draw_segment_plain(surface, ox, oy, col, row, index=idx)

    def _draw_tail(self, surface, ox, oy, col, row, entry):
        spr = sprites.get_tail(entry)
        if spr:
            surface.blit(spr, (ox + col * S.TILE_SIZE, oy + row * S.TILE_SIZE))
        else:
            self._draw_segment_plain(surface, ox, oy, col, row, index=self.length - 1)

    # ------------------------------------------------------------------
    # Direction helper
    # ------------------------------------------------------------------

    def _segment_directions(self, i):
        """
        For body[i], return (entry_dir, exit_dir).
        entry_dir = the direction the snake is travelling INTO this segment.
        exit_dir  = the direction it travels OUT of this segment.
        Both are (dx, dy) unit vectors.
        """
        def vec(a, b):
            # Direction vector pointing from grid position a to b
            return (b[0] - a[0], b[1] - a[1])

        n = len(self.body)

        if n == 1:
            return self.direction, self.direction

        if i == 0:       # head
            return self.direction, vec(self.body[0], self.body[1])

        if i == n - 1:   # tail tip
            entry = vec(self.body[i - 1], self.body[i])
            return entry, entry

        # Middle segment
        entry = vec(self.body[i - 1], self.body[i])
        exit  = vec(self.body[i],     self.body[i + 1])
        return entry, exit

    # ------------------------------------------------------------------
    # Procedural (no-sprite) fallback drawing
    # ------------------------------------------------------------------

    def _draw_segment_plain(self, surface, ox, oy, col, row, index):
        """
        Draw a simple rounded rectangle. Colour fades from head (bright)
        to tail (dim) using linear interpolation.
        """
        pad    = 4
        radius = 6 if index == 0 else 4
        x = ox + col * S.TILE_SIZE
        y = oy + row * S.TILE_SIZE

        t      = index / max(self.length - 1, 1)   # 0.0 at head, 1.0 at tail
        colour = _lerp(S.SNAKE_HEAD, S.SNAKE_BODY, t)

        outer = pygame.Rect(x + pad, y + pad, S.TILE_SIZE - pad*2, S.TILE_SIZE - pad*2)
        inner = outer.inflate(-2, -2)
        pygame.draw.rect(surface, S.SNAKE_OUTLINE, outer, border_radius=radius + 1)
        pygame.draw.rect(surface, colour,          inner, border_radius=radius)

    def _draw_eyes(self, surface, ox, oy):
        """Draw two eyes on the head, oriented toward the current direction."""
        col, row = self.body[0]
        cx = ox + col * S.TILE_SIZE + S.TILE_SIZE // 2
        cy = oy + row * S.TILE_SIZE + S.TILE_SIZE // 2
        dx, dy = self.direction

        # The perpendicular axis separates the two eyes side by side
        perp_x, perp_y = -dy, dx

        for side in (-1, +1):
            ex = cx + dx * 5 + perp_x * 7 * side
            ey = cy + dy * 5 + perp_y * 7 * side
            pygame.draw.circle(surface, S.SNAKE_EYE,   (ex,      ey),      4)
            pygame.draw.circle(surface, S.SNAKE_PUPIL, (ex + dx, ey + dy), 2)


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _lerp(c1, c2, t):
    """Linearly interpolate between two RGB colours. t=0 → c1, t=1 → c2."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
