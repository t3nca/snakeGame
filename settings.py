# ============================================================
#  settings.py  –  Single source-of-truth for every constant
# ============================================================

# ─── Grid / Window ──────────────────────────────────────────
TILE_SIZE    = 40           # pixels per tile
GRID_SIZE    = 12           # 12 × 12 = 144 tiles
PANEL_WIDTH  = 170          # side panel width (left & right)

BOARD_PX      = GRID_SIZE * TILE_SIZE            # 480
WINDOW_WIDTH  = BOARD_PX + 2 * PANEL_WIDTH       # 820
WINDOW_HEIGHT = BOARD_PX                         # 480

WINDOW_TITLE  = "S N A K E"

# ─── Frame rate / speed ─────────────────────────────────────
FPS_INITIAL          = 8    # snake moves per second at game start
FPS_MAX              = 20   # hard cap on speed
SPEED_BOOST_EVERY    = 5    # +1 FPS every N apples eaten  (0 = disabled)

# ─── Snake ──────────────────────────────────────────────────
SNAKE_START_COL    = GRID_SIZE // 2    # column index at start
SNAKE_START_ROW    = GRID_SIZE // 2    # row    index at start
SNAKE_START_DIR    = (1, 0)            # initial direction: right
SNAKE_START_LENGTH = 1                 # body segments at game start

# ─── Apple ──────────────────────────────────────────────────
APPLE_POINTS = 1            # score awarded per apple

# ─── Colours: board ─────────────────────────────────────────
C_TILE_LIGHT   = (106, 168,  79)
C_TILE_DARK    = ( 78, 140,  52)
C_BOARD_BORDER = ( 40,  40,  40)

# ─── Colours: snake ─────────────────────────────────────────
C_SNAKE_HEAD   = ( 34, 197,  94)
C_SNAKE_BODY   = ( 74, 222, 128)
C_SNAKE_OUTLINE= ( 21, 128,  61)
C_SNAKE_EYE    = (255, 255, 255)
C_SNAKE_PUPIL  = (  0,   0,   0)

# ─── Colours: apple ─────────────────────────────────────────
C_APPLE        = (220,  38,  38)
C_APPLE_DARK   = (153,  27,  27)
C_APPLE_SHINE  = (252, 165, 165)
C_STEM         = ( 92,  51,  23)
C_LEAF         = ( 34, 197,  94)

# ─── Colours: UI panels ─────────────────────────────────────
C_PANEL_BG     = ( 10,  10,  10)
C_PANEL_BORDER = ( 50,  50,  50)
C_SCANLINE     = (  0,   0,   0, 30)    # semi-transparent scanlines

# ─── Colours: text ──────────────────────────────────────────
C_LABEL        = (100, 100, 100)
C_VALUE_AMBER  = (251, 191,  36)   # amber – score / time digits
C_VALUE_DIM    = (120,  90,  10)   # dimmed segments (7-seg style)
C_WHITE        = (255, 255, 255)
C_BLACK        = (  0,   0,   0)
C_RED          = (239,  68,  68)
C_GREEN_BRIGHT = ( 74, 222, 128)

# ─── Font sizes ─────────────────────────────────────────────
FONT_TINY      = 13
FONT_SMALL     = 17
FONT_MEDIUM    = 24
FONT_LARGE     = 36
FONT_HUGE      = 48

# ─── 7-Segment digit geometry ───────────────────────────────
SEG_W   = 28       # digit bounding width
SEG_H   = 50       # digit bounding height
SEG_T   = 5        # bar thickness
SEG_GAP = 2        # gap between digits
