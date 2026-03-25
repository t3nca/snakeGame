# sprite_loader.py
# Loads (or generates) every sprite once at startup and stores them
# in a plain dictionary so the rest of the code can just do:
#
#   img = sprites.get("head_right")   # returns a Surface or None
#
# All source images face RIGHT. The loader rotates each one into
# all four directions and stores every variant in the same dict.

import os
import pygame
import settings as S

# The dict that holds every ready-to-blit Surface.
# Keys are plain strings like "head_right", "body_up", "corner_right_down".
images = {}


def load():
    """Call this once, after pygame.init(), before the game loop starts."""
    if not S.USE_SPRITES:
        return

    os.makedirs(S.ASSET_DIR, exist_ok=True)

    # Load or generate each base image (all facing RIGHT by convention).
    head   = _get_image(S.SPRITE_HEAD,   _draw_head)
    body   = _get_image(S.SPRITE_BODY,   _draw_body)
    corner = _get_image(S.SPRITE_CORNER, _draw_corner)
    tail   = _get_image(S.SPRITE_TAIL,   _draw_tail)
    apple  = _get_image(S.SPRITE_APPLE,  _draw_apple)
    panel  = _get_image(S.SPRITE_PANEL,  _draw_panel, size=(S.PANEL_WIDTH, S.WINDOW_HEIGHT))

    # Rotate directional sprites into all four directions.
    # pygame.transform.rotate() goes counter-clockwise.
    _store_rotations("head",   head)   # → "head_right", "head_up", etc.
    _store_rotations("body",   body)
    _store_rotations("tail",   tail)

    # Corners need all four bend combinations.
    # The source corner goes from the LEFT and exits DOWN (right→down bend).
    # Each entry: (key_suffix, rotation_degrees)
    corner_variants = [
        ("right_down",  0),    # default — no rotation needed
        ("left_down",  90),    # mirror around vertical
        ("left_up",   180),    # full flip
        ("right_up",  270),    # mirror around horizontal
    ]
    for name, angle in corner_variants:
        images[f"corner_{name}"] = pygame.transform.rotate(corner, angle) if corner else None

    images["apple"] = apple
    images["panel"] = panel


# ---------------------------------------------------------------------------
# Helpers used by the rest of the game
# ---------------------------------------------------------------------------

def get_head(direction):
    """Return the head sprite rotated to face `direction` (dx, dy)."""
    name = _dir_name(direction)
    return images.get(f"head_{name}")


def get_body(prev_dir, next_dir):
    """
    Return the correct body-segment sprite.
    prev_dir: direction from the segment behind this one to this one.
    next_dir: direction from this one to the segment in front of it.
    If both directions are the same it's a straight segment; otherwise a corner.
    """
    if prev_dir == next_dir:
        return images.get(f"body_{_dir_name(prev_dir)}")
    return images.get(f"corner_{_corner_name(prev_dir, next_dir)}")


def get_tail(direction):
    """Return the tail sprite pointing in `direction` (dx, dy)."""
    return images.get(f"tail_{_dir_name(direction)}")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Maps a (dx, dy) movement vector to a readable name.
_DIR_NAMES = {
    ( 1,  0): "right",
    (-1,  0): "left",
    ( 0, -1): "up",
    ( 0,  1): "down",
}

def _dir_name(direction):
    return _DIR_NAMES.get(direction, "right")


def _corner_name(from_dir, to_dir):
    """Build a corner key like 'right_down' from two direction vectors."""
    return f"{_dir_name(from_dir)}_{_dir_name(to_dir)}"


def _store_rotations(base, surface):
    """Store four rotations of `surface` under keys like 'base_right'."""
    rotations = [
        ("right",  0),
        ("up",    90),
        ("left", 180),
        ("down", 270),
    ]
    for name, angle in rotations:
        images[f"{base}_{name}"] = pygame.transform.rotate(surface, angle) if surface else None


def _get_image(filename, fallback_fn, size=None):
    """
    Try to load the PNG at assets/filename.
    If the file doesn't exist, call fallback_fn() to draw a placeholder,
    save it, and return that instead.
    Returns None if the filename setting is None.
    """
    if filename is None:
        return None

    path = os.path.join(S.ASSET_DIR, filename)

    if os.path.isfile(path):
        surf = pygame.image.load(path).convert_alpha()
        target_size = size or (S.TILE_SIZE, S.TILE_SIZE)
        return pygame.transform.scale(surf, target_size)

    # File is missing — generate a placeholder and save it for next time.
    surf = fallback_fn()
    try:
        pygame.image.save(surf, path)
        print(f"[sprites] Saved placeholder: {path}")
    except Exception as e:
        print(f"[sprites] Could not save {path}: {e}")
    return surf


# ---------------------------------------------------------------------------
# Placeholder drawing functions
# Each one draws directly onto a new TILE_SIZE x TILE_SIZE surface
# using only the colours defined in settings.py.
# ---------------------------------------------------------------------------

def _blank():
    """Return a transparent TILE_SIZE x TILE_SIZE surface."""
    surf = pygame.Surface((S.TILE_SIZE, S.TILE_SIZE), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    return surf


def _draw_head():
    """Snake head facing right, with two eyes near the right side."""
    T, s = S.TILE_SIZE, _blank()
    p = 3  # padding from the tile edge

    # Rounded body block
    pygame.draw.rect(s, S.SNAKE_OUTLINE, (p, p, T - p*2, T - p*2),     border_radius=8)
    pygame.draw.rect(s, S.SNAKE_HEAD,   (p+2, p+2, T - p*2 - 4, T - p*2 - 4), border_radius=6)

    # Two eyes (white circle + black pupil each), positioned toward the right
    eye_x = T - p - 10
    for eye_y in (T // 2 - 6, T // 2 + 6):
        pygame.draw.circle(s, S.SNAKE_EYE,   (eye_x,     eye_y), 4)
        pygame.draw.circle(s, S.SNAKE_PUPIL, (eye_x + 1, eye_y), 2)
    return s


def _draw_body():
    """Horizontal straight body segment with a subtle highlight stripe."""
    T, s = S.TILE_SIZE, _blank()
    px, py = 2, 5  # horizontal padding is smaller so it reaches tile edges

    pygame.draw.rect(s, S.SNAKE_OUTLINE, (px, py, T - px*2, T - py*2), border_radius=5)
    pygame.draw.rect(s, S.SNAKE_BODY,   (px+2, py+2, T - px*2 - 4, T - py*2 - 4), border_radius=4)

    # A brighter stripe down the middle gives a rounded-tube look
    highlight = tuple(min(c + 30, 255) for c in S.SNAKE_BODY)
    pygame.draw.rect(s, highlight, (px+4, T//2 - 2, T - px*2 - 8, 4), border_radius=2)
    return s


def _draw_corner():
    """
    An L-shaped bend: the snake arrives from the LEFT and exits DOWNWARD.
    Drawn as two overlapping rectangles (one horizontal, one vertical).
    """
    T, s = S.TILE_SIZE, _blank()
    p = 5   # padding; controls how thick the snake tube looks
    w = T - p * 2  # corridor width

    mid = T // 2  # centre of the tile

    # Horizontal arm — from the left edge to the centre
    pygame.draw.rect(s, S.SNAKE_OUTLINE, (0, p, mid + w//2, w), border_radius=3)
    pygame.draw.rect(s, S.SNAKE_BODY,   (0, p+2, mid + w//2 - 2, w - 4), border_radius=2)

    # Vertical arm — from the centre down to the bottom edge
    pygame.draw.rect(s, S.SNAKE_OUTLINE, (p, mid - w//2, w, T - mid + w//2), border_radius=3)
    pygame.draw.rect(s, S.SNAKE_BODY,   (p+2, mid - w//2 + 2, w - 4, T - mid + w//2 - 2), border_radius=2)

    # Fill the inner corner so the two arms connect seamlessly
    pygame.draw.rect(s, S.SNAKE_BODY, (p+2, p+2, mid - p - 1, mid - p - 1))
    return s


def _draw_tail():
    """Tail tip pointing LEFT — a simple tapered triangle shape."""
    T, s = S.TILE_SIZE, _blank()
    py = 6  # vertical padding to narrow the tail end

    # Outer polygon (dark outline), then inner polygon (body colour) inset by 2px
    outline_pts = [(T-4, py), (T-4, T-py), (4, T//2 + 2), (4, T//2 - 2)]
    fill_pts    = [(T-6, py+2), (T-6, T-py-2), (6, T//2 + 1), (6, T//2 - 1)]

    pygame.draw.polygon(s, S.SNAKE_OUTLINE, outline_pts)
    pygame.draw.polygon(s, S.SNAKE_BODY,    fill_pts)
    return s


def _draw_apple():
    """Red circle with a stem and a small green leaf, transparent background."""
    T, s = S.TILE_SIZE, _blank()
    cx, cy = T // 2, T // 2 + 2
    r = T // 2 - 5

    # Drop shadow (semi-transparent ellipse below the apple)
    shadow = pygame.Surface((r*2 + 4, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 50), shadow.get_rect())
    s.blit(shadow, (cx - r - 2, cy + r - 1))

    pygame.draw.circle(s, S.APPLE_DARK,  (cx, cy), r)        # darker ring
    pygame.draw.circle(s, S.APPLE_RED,   (cx, cy), r - 2)    # main body
    pygame.draw.circle(s, S.APPLE_SHINE, (cx - r//3, cy - r//3), r // 4)  # shine spot

    pygame.draw.rect(s, S.APPLE_STEM, (cx - 1, cy - r - 5, 3, 6), border_radius=1)

    lx, ly = cx + 4, cy - r - 3
    pygame.draw.polygon(s, S.APPLE_LEAF, [(lx, ly), (lx+6, ly-3), (lx+8, ly), (lx+4, ly+2)])
    return s


def _draw_panel():
    """Dark panel background with a subtle pixel grid and amber corner dots."""
    W, H = S.PANEL_WIDTH, S.WINDOW_HEIGHT
    s = pygame.Surface((W, H))
    s.fill(S.PANEL_BG)

    grid_colour = (20, 20, 20)
    for x in range(0, W, 10):
        pygame.draw.line(s, grid_colour, (x, 0), (x, H))
    for y in range(0, H, 10):
        pygame.draw.line(s, grid_colour, (0, y), (W, y))

    dot = 5
    for fx, fy in [(4, 4), (W-4-dot, 4), (4, H-4-dot), (W-4-dot, H-4-dot)]:
        pygame.draw.rect(s, S.TEXT_AMBER, (fx, fy, dot, dot))
    return s
