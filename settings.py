# settings.py
# All tunable values live here. Change anything in this file
# to adjust how the game looks and behaves.

# --- Window & grid ---
TILE_SIZE   = 40    # pixels per tile (grid square)
GRID_SIZE   = 12    # number of tiles per side (12x12 = 144 tiles)
PANEL_WIDTH = 170   # width of each side panel (left = timer, right = score)

BOARD_PX      = GRID_SIZE * TILE_SIZE           # 480 px — the play area
WINDOW_WIDTH  = BOARD_PX + PANEL_WIDTH * 2      # 820 px — total window width
WINDOW_HEIGHT = BOARD_PX                        # 480 px — window height

WINDOW_TITLE = "S N A K E"

# --- Speed ---
SPEED_START      = 5   # moves per second at the start
SPEED_MAX        = 20  # fastest the snake can ever go
SPEED_BOOST_STEP = 5   # eat this many apples to gain +1 speed (0 = no scaling)

# --- Snake starting state ---
START_COL    = GRID_SIZE // 2  # column the head begins on
START_ROW    = GRID_SIZE // 2  # row    the head begins on
START_DIR    = (1, 0)          # initial direction: (1,0) = right
START_LENGTH = 1               # how many segments the snake starts with

# --- Scoring ---
POINTS_PER_APPLE = 1

# --- Board colours ---
TILE_LIGHT  = (106, 168,  79)
TILE_DARK   = ( 78, 140,  52)
BOARD_EDGE  = ( 40,  40,  40)

# --- Snake colours ---
SNAKE_HEAD    = ( 34, 197,  94)
SNAKE_BODY    = ( 74, 222, 128)
SNAKE_OUTLINE = ( 21, 128,  61)
SNAKE_EYE     = (255, 255, 255)
SNAKE_PUPIL   = (  0,   0,   0)

# --- Apple colours ---
APPLE_RED    = (220,  38,  38)
APPLE_DARK   = (153,  27,  27)
APPLE_SHINE  = (252, 165, 165)
APPLE_STEM   = ( 92,  51,  23)
APPLE_LEAF   = ( 34, 197,  94)

# --- Panel colours ---
PANEL_BG     = ( 10,  10,  10)
PANEL_BORDER = ( 50,  50,  50)

# --- Text colours ---
TEXT_DIM    = (100, 100, 100)   # labels like "SCORE", "TIME"
TEXT_AMBER  = (251, 191,  36)   # lit segments on the 7-segment display
TEXT_UNLIT  = (120,  90,  10)   # unlit segments (dark amber)
TEXT_WHITE  = (255, 255, 255)
TEXT_RED    = (239,  68,  68)

# --- 7-segment display sizing ---
SEG_DIGIT_W = 28  # width of one digit
SEG_DIGIT_H = 50  # height of one digit
SEG_BAR_T   =  5  # thickness of each bar
SEG_GAP     =  2  # gap between digits

# --- Font sizes (pt) ---
FONT_SMALL  = 13
FONT_MEDIUM = 17
FONT_LARGE  = 24
FONT_XLARGE = 36

# =============================================================================
# Sprite settings
# All sprite images live in the "assets/" folder.
# On first run the game draws placeholder images and saves them there,
# so you get a working game straight away.
# To use your own art: drop a same-named PNG into assets/ and restart.
# To turn off a single sprite: set its value to None (falls back to drawing).
# To turn off all sprites at once: set USE_SPRITES = False.
# =============================================================================

USE_SPRITES = True
ASSET_DIR   = "assets"

# Snake sprites — all must be TILE_SIZE x TILE_SIZE.
# Draw your source image facing RIGHT; the game rotates it automatically.
SPRITE_HEAD   = "images\snake_head.png"    # head, facing right
SPRITE_BODY   = "images\snake_body.png"    # straight body segment, horizontal
SPRITE_CORNER = "images\snake_corner.png"  # bend: coming from the left, turning down
SPRITE_TAIL   = "images\snake_tail.png"    # tail tip, pointing left

# Other sprites
SPRITE_APPLE = "images\\apple.png"          # TILE_SIZE x TILE_SIZE, transparent bg
SPRITE_PANEL = "images\panel_bg.png"       # PANEL_WIDTH x WINDOW_HEIGHT side panel


#----------------------------------------------------------------------------
#Sounds

Apple_eaten = "assets\sounds\\apple..wav"