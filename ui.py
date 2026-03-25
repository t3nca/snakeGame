# ui.py
# Draws both side panels (time on the left, score on the right)
# and the game-over overlay.
#
# The digits are drawn as 7-segment LCD displays, the same style
# as a calculator or digital clock.

import pygame
import sprite_loader as sprites
import settings as S


# Which segments are lit for each digit 0-9.
# Segment order: top, top-right, bot-right, bottom, bot-left, top-left, middle
DIGIT_SEGMENTS = {
    "0": (1, 1, 1, 1, 1, 1, 0),
    "1": (0, 1, 1, 0, 0, 0, 0),
    "2": (1, 1, 0, 1, 1, 0, 1),
    "3": (1, 1, 1, 1, 0, 0, 1),
    "4": (0, 1, 1, 0, 0, 1, 1),
    "5": (1, 0, 1, 1, 0, 1, 1),
    "6": (1, 0, 1, 1, 1, 1, 1),
    "7": (1, 1, 1, 0, 0, 0, 0),
    "8": (1, 1, 1, 1, 1, 1, 1),
    "9": (1, 1, 1, 1, 0, 1, 1),
}


class UI:

    def __init__(self, surface):
        self.surface   = surface
        self._fonts    = _load_fonts()
        self._scanlines = _make_scanlines(S.PANEL_WIDTH, S.WINDOW_HEIGHT)

    # ------------------------------------------------------------------
    # Main draw call — called every frame from main.py
    # ------------------------------------------------------------------

    def draw(self, score, elapsed_seconds, length, game_over):
        self._draw_panel(side="left")
        self._draw_panel(side="right")
        self._draw_time(elapsed_seconds)
        self._draw_score(score, length)
        if game_over:
            self._draw_game_over(score)

    # ------------------------------------------------------------------
    # Panels
    # ------------------------------------------------------------------

    def _draw_panel(self, side):
        x = 0 if side == "left" else S.PANEL_WIDTH + S.BOARD_PX
        rect = pygame.Rect(x, 0, S.PANEL_WIDTH, S.WINDOW_HEIGHT)

        spr = sprites.images.get("panel")
        if spr:
            self.surface.blit(spr, rect.topleft)
        else:
            pygame.draw.rect(self.surface, S.PANEL_BG, rect)
            self.surface.blit(self._scanlines, rect.topleft)

        # Border + four amber corner squares
        pygame.draw.rect(self.surface, S.PANEL_BORDER, rect, 2)
        dot = 5
        for fx, fy in [(x+4, 4), (x+S.PANEL_WIDTH-4-dot, 4),
                       (x+4, S.WINDOW_HEIGHT-4-dot), (x+S.PANEL_WIDTH-4-dot, S.WINDOW_HEIGHT-4-dot)]:
            pygame.draw.rect(self.surface, S.TEXT_AMBER, (fx, fy, dot, dot))

    def _draw_time(self, elapsed_seconds):
        cx = S.PANEL_WIDTH // 2
        self._label("T I M E", cx, 30)
        total = int(elapsed_seconds)
        self._seven_seg(f"{total // 60:02d}:{total % 60:02d}", cx, 75)
        self._draw_snake_doodle(cx, 220)
        self._small_label("WASD TO MOVE", cx, S.WINDOW_HEIGHT - 30, bottom=True)

    def _draw_score(self, score, length):
        cx = S.PANEL_WIDTH + S.BOARD_PX + S.PANEL_WIDTH // 2
        self._label("S C O R E", cx, 30)
        self._seven_seg(f"{score:03d}", cx, 75)
        self._label("L E N G T H", cx, 195)
        self._seven_seg(f"{length:03d}", cx, 235)
        self._small_label("EAT APPLES!", cx, S.WINDOW_HEIGHT - 30, bottom=True)

    # ------------------------------------------------------------------
    # Game-over overlay
    # ------------------------------------------------------------------

    def _draw_game_over(self, score):
        # Dim the whole screen
        overlay = pygame.Surface((S.WINDOW_WIDTH, S.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.surface.blit(overlay, (0, 0))

        cx = S.WINDOW_WIDTH  // 2
        cy = S.WINDOW_HEIGHT // 2

        # Dark box with amber border
        box = pygame.Rect(cx - 180, cy - 110, 360, 220)
        pygame.draw.rect(self.surface, (20, 20, 20),   box, border_radius=8)
        pygame.draw.rect(self.surface, S.TEXT_AMBER,   box, 3, border_radius=8)

        self._render("GAME  OVER",          self._fonts["large"], S.TEXT_RED,   cx, cy - 95)
        self._render(f"SCORE : {score}",    self._fonts["mid"],   S.TEXT_AMBER, cx, cy - 30)
        self._render("PRESS  R  TO  RESTART", self._fonts["med"], S.TEXT_WHITE, cx, cy + 40)
        self._render("ESC  TO  QUIT",        self._fonts["small"], S.TEXT_DIM,  cx, cy + 80)

    # ------------------------------------------------------------------
    # 7-segment display
    # ------------------------------------------------------------------

    def _seven_seg(self, text, cx, top):
        """
        Render a string of digits and colons as a 7-segment LCD display.
        Each digit is S.SEG_DIGIT_W wide; colons take up 10px.
        """
        # Work out total width so we can centre it
        total_w = 0
        for ch in text:
            total_w += 10 if ch == ":" else S.SEG_DIGIT_W
            total_w += S.SEG_GAP
        total_w -= S.SEG_GAP

        x = cx - total_w // 2
        for ch in text:
            if ch == ":":
                self._draw_colon(x, top)
                x += 10 + S.SEG_GAP
            else:
                self._draw_digit(ch, x, top)
                x += S.SEG_DIGIT_W + S.SEG_GAP

    def _draw_digit(self, ch, x, y):
        W = S.SEG_DIGIT_W
        H = S.SEG_DIGIT_H
        T = S.SEG_BAR_T
        half = H // 2
        lit  = DIGIT_SEGMENTS.get(ch, (0,)*7)

        # Each entry is (pygame.Rect, segment_index)
        bars = [
            (pygame.Rect(x+T,   y,        W-T*2, T),    0),  # top
            (pygame.Rect(x+W-T, y+T,      T,  half-T),  1),  # top-right
            (pygame.Rect(x+W-T, y+half,   T,  half-T),  2),  # bot-right
            (pygame.Rect(x+T,   y+H-T,    W-T*2, T),    3),  # bottom
            (pygame.Rect(x,     y+half,   T,  half-T),  4),  # bot-left
            (pygame.Rect(x,     y+T,      T,  half-T),  5),  # top-left
            (pygame.Rect(x+T,   y+half-T//2, W-T*2, T), 6),  # middle
        ]
        for rect, seg_index in bars:
            colour = S.TEXT_AMBER if lit[seg_index] else S.TEXT_UNLIT
            pygame.draw.rect(self.surface, colour, rect, border_radius=2)

    def _draw_colon(self, x, y):
        dot_size = S.SEG_BAR_T + 2
        pygame.draw.rect(self.surface, S.TEXT_AMBER,
                         (x+1, y + S.SEG_DIGIT_H//3 - S.SEG_BAR_T, dot_size, dot_size), border_radius=1)
        pygame.draw.rect(self.surface, S.TEXT_AMBER,
                         (x+1, y + 2*S.SEG_DIGIT_H//3,              dot_size, dot_size), border_radius=1)

    # ------------------------------------------------------------------
    # Decorative snake doodle (left panel)
    # ------------------------------------------------------------------

    def _draw_snake_doodle(self, cx, cy):
        """A tiny pixel snake drawn in the left panel as decoration."""
        tile = 10
        # Each tuple is a (col, row) in a 3x3 micro-grid
        path = [(0,0), (1,0), (2,0), (2,1), (2,2), (1,2), (0,2)]
        ox   = cx - (3 * tile) // 2
        for i, (sc, sr) in enumerate(path):
            t = i / max(len(path) - 1, 1)
            colour = _lerp(S.SNAKE_HEAD, S.SNAKE_BODY, t)
            rect   = pygame.Rect(ox + sc*tile + 1, cy + sr*tile + 1, tile-2, tile-2)
            pygame.draw.rect(self.surface, colour, rect, border_radius=2)

    # ------------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------------

    def _label(self, text, cx, top):
        surf = self._fonts["med"].render(text, True, S.TEXT_DIM)
        self.surface.blit(surf, surf.get_rect(centerx=cx, top=top))

    def _small_label(self, text, cx, y, bottom=False):
        surf = self._fonts["small"].render(text, True, S.TEXT_DIM)
        rect = surf.get_rect(centerx=cx)
        if bottom:
            rect.bottom = y
        else:
            rect.top = y
        self.surface.blit(surf, rect)

    def _render(self, text, font, colour, cx, top):
        surf = font.render(text, True, colour)
        self.surface.blit(surf, surf.get_rect(centerx=cx, top=top))


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _load_fonts():
    """Try to load a monospace font; fall back to pygame's built-in."""
    candidates = ["courier new", "courier", "consolas", "monospace"]
    def get(size):
        for name in candidates:
            f = pygame.font.SysFont(name, size, bold=True)
            if f:
                return f
        return pygame.font.Font(None, size)

    return {
        "small": get(S.FONT_SMALL),
        "med":   get(S.FONT_MEDIUM),
        "mid":   get(S.FONT_LARGE),
        "large": get(S.FONT_XLARGE),
    }


def _make_scanlines(width, height):
    """A transparent surface with faint horizontal lines every 4 pixels."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, 4):
        pygame.draw.line(surf, (0, 0, 0, 35), (0, y), (width, y))
    return surf


def _lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
