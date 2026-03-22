# ============================================================
#  main.py  –  Entry point: game loop, event handling, state
# ============================================================

import sys
import pygame

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    PANEL_WIDTH, FPS_INITIAL, FPS_MAX,
    SPEED_BOOST_EVERY, APPLE_POINTS,
    SNAKE_START_DIR,
    C_PANEL_BG,
)
from gameboard import GameBoard
from player    import Snake
from apple     import Apple
from ui        import UI


# ── Game states ────────────────────────────────────────────
PLAYING   = "playing"
GAME_OVER = "game_over"


class Game:
    """
    Top-level coordinator.
    Owns the pygame window, the fixed-timestep tick loop,
    and all sub-systems (board, snake, apple, UI).
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock  = pygame.time.Clock()

        # Board is drawn starting at x = PANEL_WIDTH, y = 0
        self.board_ox = PANEL_WIDTH
        self.board_oy = 0

        self.board = GameBoard(self.screen, self.board_ox, self.board_oy)
        self.snake = Snake()
        self.apple = Apple()
        self.ui    = UI(self.screen)

        self._reset_game()

    # ── public ─────────────────────────────────────────────

    def run(self) -> None:
        """Main loop – runs until the window is closed."""
        while True:
            # clock.tick returns milliseconds since last call
            raw_dt = self.clock.tick(self._current_fps)
            dt     = min(raw_dt / 1000.0, 0.2)   # cap to avoid spiral

            self._handle_events()
            self._update(dt)
            self._draw()

    # ── private: reset ─────────────────────────────────────

    def _reset_game(self) -> None:
        self.snake.reset()
        self.apple.spawn(self.snake.get_positions())

        self._state        : str   = PLAYING
        self._score        : int   = 0
        self._elapsed      : float = 0.0
        self._current_fps  : int   = FPS_INITIAL
        self._next_dir     : tuple = SNAKE_START_DIR
        self._queued_dir   : tuple | None = None   # double-tap buffer

    # ── private: events ────────────────────────────────────

    def _handle_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self._quit()

            if event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self._quit()

        if self._state == GAME_OVER:
            if key == pygame.K_r:
                self._reset_game()
            return

        dir_map = {
            pygame.K_UP:    (0, -1),
            pygame.K_DOWN:  (0,  1),
            pygame.K_LEFT:  (-1, 0),
            pygame.K_RIGHT: ( 1, 0),
        }
        if key in dir_map:
            nd  = dir_map[key]
            dx, dy = self._next_dir
            # Reject 180° reversal
            if nd != (-dx, -dy):
                self._next_dir = nd

    # ── private: update ────────────────────────────────────

    def _update(self, dt: float) -> None:
        if self._state == GAME_OVER:
            return

        # Accumulate real time only while alive
        self._elapsed += dt

        # Let the apple animation tick at real time too
        self.apple.update(dt)

        # Apply buffered direction, then move
        self.snake.change_direction(self._next_dir)
        self.snake.move()

        # Collision with walls or self → game over
        if self.snake.check_wall_collision() or self.snake.check_self_collision():
            self._state = GAME_OVER
            return

        # Collision with apple?
        if self.snake.body[0] == self.apple.position:
            self._score += APPLE_POINTS
            self.snake.grow()
            self.apple.spawn(self.snake.get_positions())
            self._maybe_increase_speed()

    def _maybe_increase_speed(self) -> None:
        if SPEED_BOOST_EVERY > 0 and self._score % SPEED_BOOST_EVERY == 0:
            self._current_fps = min(self._current_fps + 1, FPS_MAX)

    # ── private: draw ──────────────────────────────────────

    def _draw(self) -> None:
        self.screen.fill(C_PANEL_BG)

        self.board.draw()
        self.apple.draw(self.screen, self.board_ox, self.board_oy)
        self.snake.draw(self.screen, self.board_ox, self.board_oy)

        self.ui.draw(
            score     = self._score,
            elapsed   = self._elapsed,
            length    = self.snake.length,
            game_over = (self._state == GAME_OVER),
        )

        pygame.display.flip()

    # ── private: quit ──────────────────────────────────────

    @staticmethod
    def _quit() -> None:
        pygame.quit()
        sys.exit()


# ── entry point ────────────────────────────────────────────

if __name__ == "__main__":
    game = Game()
    game.run()
