# ============================================================
#  ui.py  –  8-bit HUD panels (time left, score right)
# ============================================================

import pygame
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PANEL_WIDTH, BOARD_PX,
    FONT_TINY, FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_HUGE,
    C_PANEL_BG, C_PANEL_BORDER,
    C_LABEL, C_VALUE_AMBER, C_VALUE_DIM,
    C_WHITE, C_BLACK, C_RED, C_GREEN_BRIGHT,
    SEG_W, SEG_H, SEG_T, SEG_GAP,
)

# ── 7-segment encoding ─────────────────────────────────────
#  Segments: a(top) b(top-right) c(bot-right) d(bot)
#            e(bot-left) f(top-left) g(middle)
#  Index:      a  b  c  d  e  f  g
_SEGMENTS: dict[str, tuple[bool, ...]] = {
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
    ":": (0, 0, 0, 0, 0, 0, 0),   # colon handled separately
    "-": (0, 0, 0, 0, 0, 0, 1),
}


class UI:
    """
    Renders two side panels in a chunky 8-bit style:
     - Left  panel : elapsed time (MM:SS) with 7-segment digits
     - Right panel : score + snake length with 7-segment digits
    Also handles the Game-Over overlay.
    """

    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self._init_fonts()

        # Pre-build scanline overlay for panels
        self._scanlines = self._make_scanlines(PANEL_WIDTH, WINDOW_HEIGHT)

    # ── public ─────────────────────────────────────────────

    def draw(
        self,
        score:    int,
        elapsed:  float,
        length:   int,
        game_over: bool,
    ) -> None:
        self._draw_left_panel(elapsed)
        self._draw_right_panel(score, length)
        if game_over:
            self._draw_game_over_overlay(score)

    # ── panels ─────────────────────────────────────────────

    def _draw_left_panel(self, elapsed: float) -> None:
        rect = pygame.Rect(0, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.surface, C_PANEL_BG, rect)
        self._draw_pixel_frame(rect)
        self.surface.blit(self._scanlines, rect.topleft)

        cx = PANEL_WIDTH // 2

        # ── label ──
        self._blit_label("T I M E", cx, 30)

        # ── 7-seg time ──
        total_s = int(elapsed)
        mm      = total_s // 60
        ss      = total_s % 60
        time_str = f"{mm:02d}:{ss:02d}"
        self._draw_7seg_string(time_str, cx, 75)

        # ── decorative snake icon ──
        self._draw_mini_snake(cx, 220)

        # ── hint ──
        self._blit_tiny("ARROWS TO MOVE", cx, WINDOW_HEIGHT - 30)

    def _draw_right_panel(self, score: int, length: int) -> None:
        board_right = PANEL_WIDTH + BOARD_PX
        rect = pygame.Rect(board_right, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.surface, C_PANEL_BG, rect)
        self._draw_pixel_frame(rect)
        self.surface.blit(self._scanlines, rect.topleft, area=pygame.Rect(0, 0, PANEL_WIDTH, WINDOW_HEIGHT))

        cx = board_right + PANEL_WIDTH // 2

        # ── Score ──
        self._blit_label("S C O R E", cx, 30)
        self._draw_7seg_string(str(score).zfill(3), cx, 75)

        # ── Length ──
        self._blit_label("L E N G T H", cx, 195)
        self._draw_7seg_string(str(length).zfill(3), cx, 235)

        # ── hint ──
        self._blit_tiny("EAT APPLES!", cx, WINDOW_HEIGHT - 30)

    # ── game over overlay ──────────────────────────────────

    def _draw_game_over_overlay(self, score: int) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.surface.blit(overlay, (0, 0))

        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2

        # Outer box
        box = pygame.Rect(cx - 180, cy - 110, 360, 220)
        pygame.draw.rect(self.surface, (20, 20, 20), box, border_radius=8)
        pygame.draw.rect(self.surface, C_VALUE_AMBER, box, 3, border_radius=8)

        # "GAME OVER" header
        go_surf = self._font_large.render("GAME  OVER", True, C_RED)
        self.surface.blit(go_surf, go_surf.get_rect(centerx=cx, top=cy - 95))

        # Score line
        s_surf = self._font_med.render(f"SCORE : {score}", True, C_VALUE_AMBER)
        self.surface.blit(s_surf, s_surf.get_rect(centerx=cx, top=cy - 30))

        # Restart hint (blinking is handled by alpha oscillation)
        r_surf = self._font_small.render("PRESS  R  TO  RESTART", True, C_WHITE)
        self.surface.blit(r_surf, r_surf.get_rect(centerx=cx, top=cy + 40))

        # Quit hint
        q_surf = self._font_tiny.render("ESC  TO  QUIT", True, C_LABEL)
        self.surface.blit(q_surf, q_surf.get_rect(centerx=cx, top=cy + 80))

    # ── 7-segment display ──────────────────────────────────

    def _draw_7seg_string(self, text: str, cx: int, top: int) -> None:
        """Render a string of digits (and colons) as a 7-segment display."""
        # Calculate total width
        total_w = 0
        for ch in text:
            if ch == ":":
                total_w += 10 + SEG_GAP
            else:
                total_w += SEG_W + SEG_GAP
        total_w -= SEG_GAP
        x = cx - total_w // 2

        for ch in text:
            if ch == ":":
                self._draw_colon(x, top)
                x += 10 + SEG_GAP
            else:
                self._draw_digit(ch, x, top)
                x += SEG_W + SEG_GAP

    def _draw_digit(self, ch: str, x: int, y: int) -> None:
        segs = _SEGMENTS.get(ch, (0,)*7)
        w, h, t = SEG_W, SEG_H, SEG_T
        hw = w // 2
        hh = h // 2

        # All 7 segment positions as (rect, on_flag)
        seg_rects = [
            # a – top horizontal
            (pygame.Rect(x + t,      y,          w - 2*t, t),    segs[0]),
            # b – top-right vertical
            (pygame.Rect(x + w - t,  y + t,      t,  hh - t),   segs[1]),
            # c – bot-right vertical
            (pygame.Rect(x + w - t,  y + hh,     t,  hh - t),   segs[2]),
            # d – bottom horizontal
            (pygame.Rect(x + t,      y + h - t,  w - 2*t, t),   segs[3]),
            # e – bot-left vertical
            (pygame.Rect(x,          y + hh,     t,  hh - t),   segs[4]),
            # f – top-left vertical
            (pygame.Rect(x,          y + t,      t,  hh - t),   segs[5]),
            # g – middle horizontal
            (pygame.Rect(x + t,      y + hh - t//2, w - 2*t, t), segs[6]),
        ]
        for rect, on in seg_rects:
            colour = C_VALUE_AMBER if on else C_VALUE_DIM
            pygame.draw.rect(self.surface, colour, rect, border_radius=2)

    def _draw_colon(self, x: int, y: int) -> None:
        t = SEG_T
        h = SEG_H
        dot1 = pygame.Rect(x + 1, y + h // 3 - t, t + 2, t + 2)
        dot2 = pygame.Rect(x + 1, y + 2 * h // 3, t + 2, t + 2)
        pygame.draw.rect(self.surface, C_VALUE_AMBER, dot1, border_radius=1)
        pygame.draw.rect(self.surface, C_VALUE_AMBER, dot2, border_radius=1)

    # ── decorative mini snake ──────────────────────────────

    def _draw_mini_snake(self, cx: int, cy: int) -> None:
        """Draw a tiny pixel-art snake icon in the left panel."""
        tile = 10
        segs = [(0,0),(1,0),(2,0),(2,1),(2,2),(1,2),(0,2)]
        ox = cx - (3 * tile) // 2
        for i, (sc, sr) in enumerate(segs):
            t = i / max(len(segs) - 1, 1)
            r = int(34  + (74  - 34)  * t)
            g = int(197 + (222 - 197) * t)
            b = int(94  + (128 - 94)  * t)
            rect = pygame.Rect(ox + sc * tile + 1, cy + sr * tile + 1, tile - 2, tile - 2)
            pygame.draw.rect(self.surface, (r, g, b), rect, border_radius=2)

    # ── frame / scanlines ──────────────────────────────────

    def _draw_pixel_frame(self, rect: pygame.Rect) -> None:
        """Draw a chunky pixel-art border around a panel rect."""
        pygame.draw.rect(self.surface, C_PANEL_BORDER, rect, 2)
        # Corner pixel accents
        s = 5
        for fx, fy in [
            (rect.left + 4,       rect.top + 4),
            (rect.right - 4 - s,  rect.top + 4),
            (rect.left + 4,       rect.bottom - 4 - s),
            (rect.right - 4 - s,  rect.bottom - 4 - s),
        ]:
            pygame.draw.rect(self.surface, C_VALUE_AMBER, (fx, fy, s, s))

    @staticmethod
    def _make_scanlines(w: int, h: int) -> pygame.Surface:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 4):
            pygame.draw.line(surf, (0, 0, 0, 35), (0, y), (w, y))
        return surf

    # ── text helpers ───────────────────────────────────────

    def _blit_label(self, text: str, cx: int, top: int) -> None:
        surf = self._font_small.render(text, True, C_LABEL)
        self.surface.blit(surf, surf.get_rect(centerx=cx, top=top))

    def _blit_tiny(self, text: str, cx: int, bottom: int) -> None:
        surf = self._font_tiny.render(text, True, C_LABEL)
        self.surface.blit(surf, surf.get_rect(centerx=cx, bottom=bottom))

    # ── font init ──────────────────────────────────────────

    def _init_fonts(self) -> None:
        candidates = ["courier new", "courier", "monospace", "consolas", "lucidaconsole"]
        def load(size: int) -> pygame.font.Font:
            for name in candidates:
                f = pygame.font.SysFont(name, size, bold=True)
                if f:
                    return f
            return pygame.font.Font(None, size)

        self._font_tiny  = load(FONT_TINY)
        self._font_small = load(FONT_SMALL)
        self._font_med   = load(FONT_MEDIUM)
        self._font_large = load(FONT_LARGE)
