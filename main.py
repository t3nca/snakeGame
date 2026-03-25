# main.py
# Entry point. Creates the window, runs the game loop, and
# coordinates all the other modules.
#
# Game states:
#   "playing"   — normal gameplay
#   "game_over" — snake hit a wall or itself; waiting for R to restart

import sys
import pygame
import sprite_loader as sprites
import settings as S
from gameboard import GameBoard
from player    import Snake
from apple     import Apple
from ui        import UI


class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(S.WINDOW_TITLE)
        self.screen = pygame.display.set_mode((S.WINDOW_WIDTH, S.WINDOW_HEIGHT))
        self.clock  = pygame.time.Clock()

        # Sprites must be loaded after pygame.init() and display mode is set.
        sprites.load()

        # The board sits between the two side panels.
        board_x     = S.PANEL_WIDTH
        self.board  = GameBoard(self.screen, board_x, 0)
        self.snake  = Snake()
        self.apple  = Apple()
        self.ui     = UI(self.screen)

        self._start_new_game()

    # ------------------------------------------------------------------
    # Game loop
    # ------------------------------------------------------------------

    def run(self):
        while True:
            # dt = seconds since last frame (capped to avoid huge jumps)
            dt = min(self.clock.tick(self._speed) / 1000.0, 0.2)
            self._handle_input()
            self._update(dt)
            self._draw()

    # ------------------------------------------------------------------
    # Initialise / reset game state
    # ------------------------------------------------------------------

    def _start_new_game(self):
        self.snake.reset()
        self.apple.spawn(self.snake.occupied_tiles())
        self._state   = "playing"
        self._score   = 0
        self._elapsed = 0.0
        self._speed   = S.SPEED_START
        self._next_dir = S.START_DIR  # buffered direction input

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
            if event.type == pygame.KEYDOWN:
                self._on_key(event.key)

    def _on_key(self, key):
        if key == pygame.K_ESCAPE:
            self._quit()

        if self._state == "game_over":
            if key == pygame.K_r:
                self._start_new_game()
            return

        arrow_to_dir = {
            pygame.K_w:  (0, -1),
            pygame.K_s:  (0,  1),
            pygame.K_a:  (-1, 0),
            pygame.K_d:  ( 1, 0),
        }
        if key in arrow_to_dir:
            dx, dy = self._next_dir
            new    = arrow_to_dir[key]
            # Only accept the turn if it isn't a 180° reversal
            if new != (-dx, -dy):
                self._next_dir = new

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt):
        if self._state == "game_over":
            return

        self._elapsed += dt
        self.apple.update(dt)

        self.snake.change_direction(self._next_dir)
        self.snake.move()

        if self.snake.hit_wall() or self.snake.hit_self():
            self._state = "game_over"
            return

        if self.snake.body[0] == self.apple.position:
            self._score += S.POINTS_PER_APPLE
            self.snake.grow()
            self.apple.spawn(self.snake.occupied_tiles())
            self._maybe_speed_up()

    def _maybe_speed_up(self):
        """Increase speed by 1 every SPEED_BOOST_STEP apples, up to SPEED_MAX."""
        if S.SPEED_BOOST_STEP > 0 and self._score % S.SPEED_BOOST_STEP == 0:
            self._speed = min(self._speed + 1, S.SPEED_MAX)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _draw(self):
        self.screen.fill(S.PANEL_BG)
        self.board.draw()
        self.apple.draw(self.screen, S.PANEL_WIDTH, 0)
        self.snake.draw(self.screen, S.PANEL_WIDTH, 0)
        self.ui.draw(
            score           = self._score,
            elapsed_seconds = self._elapsed,
            length          = self.snake.length,
            game_over       = (self._state == "game_over"),
        )
        pygame.display.flip()

    # ------------------------------------------------------------------

    @staticmethod
    def _quit():
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
