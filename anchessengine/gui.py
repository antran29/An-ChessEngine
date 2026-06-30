import os
import time

import pygame

from anchessengine.constants import Color, Piece
from anchessengine.position import Position


BOARD_SIZE = 640
MENU_WIDTH = 960
MENU_HEIGHT = 640
SQUARE_SIZE = BOARD_SIZE // 8

LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)

COORDINATE_LIGHT = (240, 240, 240)
COORDINATE_DARK = (60, 60, 60)

SELECTED_LIGHT_FILL = (70, 140, 230, 160)
SELECTED_DARK_FILL = (70, 140, 230, 100)
SELECTED_BORDER = (20, 20, 20)

LEGAL_MOVE_FILL = (80, 200, 120, 95)
LEGAL_MOVE_DOT = (30, 120, 70)
CAPTURE_MOVE_FILL = (220, 70, 70, 120)
CAPTURE_BORDER = (150, 20, 20)

CASTLE_FILL = (245, 190, 65, 105)
CASTLE_BORDER = (170, 110, 20)
CASTLE_DOT = (190, 130, 25)

MENU_BG = (18, 28, 23)
MENU_LEFT = (30, 44, 37)
MENU_RIGHT = (38, 55, 45)
MENU_OPTION = (88, 125, 70)
MENU_OPTION_HOVER = (104, 145, 82)
MENU_TEXT = (245, 245, 235)
MENU_MUTED = (190, 200, 190)
MENU_GREEN = (118, 178, 75)
MENU_GREEN_DARK = (88, 140, 55)
MENU_BORDER = (95, 130, 90)
MENU_DARK_BUTTON = (50, 65, 55)
MENU_DROPDOWN = (48, 68, 56)

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
ASSET_DIR = os.path.join(PROJECT_ROOT, "assets", "pieces")

PIECE_IMAGE_FILES = {
    "black_king": "Chess_kdt60.png",
    "white_king": "Chess_klt60.png",
    "black_queen": "Chess_qdt60.png",
    "white_queen": "Chess_qlt60.png",
    "black_rook": "Chess_rdt60.png",
    "white_rook": "Chess_rlt60.png",
    "black_bishop": "Chess_bdt60.png",
    "white_bishop": "Chess_blt60.png",
    "black_knight": "Chess_ndt60.png",
    "white_knight": "Chess_nlt60.png",
    "black_pawn": "Chess_pdt60.png",
    "white_pawn": "Chess_plt60.png",
}

TURN_OPTIONS = ["White", "Black"]
TIMER_OPTIONS = [
    "No Timer",
    "5 minutes",
    "10 minutes",
    "10 minutes + 5 seconds per move",
]


def get_timer_settings(timer_label):
    """Return starting seconds and increment seconds for a menu timer label."""
    if timer_label in ("5 min", "5 minutes"):
        return 5 * 60, 0
    if timer_label in ("10 min", "10 minutes"):
        return 10 * 60, 0
    if timer_label in ("10 + 5", "10 minutes + 5 seconds per move"):
        return 10 * 60, 5

    return None, 0


def format_clock_time(seconds):
    """Format a clock value as MM:SS:CS.

    CS means centiseconds, so the last two digits show hundredths of
    a second. This keeps the timer compact while still showing
    sub-second countdown movement.
    """
    if seconds is None:
        return "--:--:--"

    total_centiseconds = max(0, int(seconds * 100))
    minutes = total_centiseconds // 6000
    remaining_centiseconds = total_centiseconds % 6000
    whole_seconds = remaining_centiseconds // 100
    centiseconds = remaining_centiseconds % 100

    return f"{minutes:02d}:{whole_seconds:02d}:{centiseconds:02d}"

CURRENT_BOARD_RECT = pygame.Rect(0, 0, BOARD_SIZE, BOARD_SIZE)
CURRENT_SQUARE_SIZE = SQUARE_SIZE
CURRENT_SIDE_PANEL_RECT = pygame.Rect(0, 0, 0, 0)

GAME_PANEL_WIDTH = 300
PANEL_BG = (31, 45, 37)
PANEL_CARD = (44, 62, 50)
PANEL_ACTIVE = (91, 130, 70)
PANEL_BORDER = (93, 125, 86)
PANEL_TEXT = (245, 245, 235)
PANEL_MUTED = (185, 195, 185)
PANEL_WARNING = (220, 90, 90)
PANEL_DANGER = (160, 58, 58)
PANEL_DANGER_HOVER = (188, 70, 70)
GAME_OVER_BG = (24, 35, 29)
GAME_OVER_CARD = (38, 55, 45)


# ---------------------------------------------------------------------
# Asset loading
# ---------------------------------------------------------------------

def load_piece_images():
    """Load, crop and resize chess piece images."""
    images = {}
    target_size = SQUARE_SIZE - 22

    for key, filename in PIECE_IMAGE_FILES.items():
        path = os.path.join(ASSET_DIR, filename)
        raw_image = pygame.image.load(path).convert_alpha()

        bounding_rect = raw_image.get_bounding_rect()
        cropped_image = raw_image.subsurface(bounding_rect).copy()

        width, height = cropped_image.get_size()
        scale = min(target_size / width, target_size / height)

        new_width = int(width * scale)
        new_height = int(height * scale)

        images[key] = pygame.transform.smoothscale(
            cropped_image,
            (new_width, new_height),
        )

    return images


def load_logo():
    """Load the project logo for the menu screen."""
    possible_logo_paths = [
        os.path.join(PROJECT_ROOT, "achess.png"),
        os.path.join(PROJECT_ROOT, "AChess.png"),
        os.path.join(PROJECT_ROOT, "AChess.PNG"),
    ]

    for logo_path in possible_logo_paths:
        if os.path.exists(logo_path):
            return pygame.image.load(logo_path).convert_alpha()

    return None


# ---------------------------------------------------------------------
# Scalable layout helpers
# ---------------------------------------------------------------------

def make_fonts(width, height):
    """Create fonts scaled to the current menu window size."""
    scale = max(0.75, min(width / MENU_WIDTH, height / MENU_HEIGHT))

    title_font = pygame.font.SysFont("Arial", int(40 * scale), bold=True)
    heading_font = pygame.font.SysFont("Arial", int(34 * scale), bold=True)
    body_font = pygame.font.SysFont("Arial", int(22 * scale), bold=True)
    button_font = pygame.font.SysFont("Arial", int(30 * scale), bold=True)
    small_font = pygame.font.SysFont("Arial", int(17 * scale), bold=True)
    coordinate_font = pygame.font.SysFont("Arial", 18, bold=True)

    return title_font, heading_font, body_font, button_font, small_font, coordinate_font


def update_board_layout(screen):
    """Resize the board and reserve a right panel for game information."""
    global CURRENT_BOARD_RECT, CURRENT_SQUARE_SIZE, CURRENT_SIDE_PANEL_RECT

    width, height = screen.get_size()

    if width >= 880:
        panel_width = min(GAME_PANEL_WIDTH, max(250, int(width * 0.28)))
        available_width = width - panel_width - 30
        board_size = min(available_width, height - 20)
        board_size = max(320, board_size)
        board_size -= board_size % 8

        x = 10
        y = (height - board_size) // 2

        CURRENT_BOARD_RECT = pygame.Rect(x, y, board_size, board_size)
        CURRENT_SQUARE_SIZE = board_size // 8
        CURRENT_SIDE_PANEL_RECT = pygame.Rect(
            CURRENT_BOARD_RECT.right + 10,
            10,
            width - CURRENT_BOARD_RECT.right - 20,
            height - 20,
        )
    else:
        board_size = min(width, height) - 20
        board_size = max(320, board_size)
        board_size -= board_size % 8

        x = (width - board_size) // 2
        y = (height - board_size) // 2

        CURRENT_BOARD_RECT = pygame.Rect(x, y, board_size, board_size)
        CURRENT_SQUARE_SIZE = board_size // 8
        CURRENT_SIDE_PANEL_RECT = pygame.Rect(0, 0, 0, 0)

def scale_image_to_square(image):
    """Scale a piece image to the current square size."""
    target_size = max(24, CURRENT_SQUARE_SIZE - max(10, CURRENT_SQUARE_SIZE // 4))
    width, height = image.get_size()
    scale = min(target_size / width, target_size / height)
    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))
    return pygame.transform.smoothscale(image, (new_width, new_height))


# ---------------------------------------------------------------------
# Board coordinate helpers
# ---------------------------------------------------------------------

def square_to_screen(square):
    """Convert internal square number into screen coordinates."""
    file_index = square % 8
    rank_index = square // 8

    col = file_index
    row = 7 - rank_index

    x = CURRENT_BOARD_RECT.x + col * CURRENT_SQUARE_SIZE
    y = CURRENT_BOARD_RECT.y + row * CURRENT_SQUARE_SIZE

    return x, y


def screen_to_square(mouse_pos):
    """Convert mouse position into an internal square number."""
    x, y = mouse_pos

    if not CURRENT_BOARD_RECT.collidepoint(x, y):
        return None

    local_x = x - CURRENT_BOARD_RECT.x
    local_y = y - CURRENT_BOARD_RECT.y

    col = local_x // CURRENT_SQUARE_SIZE
    row = local_y // CURRENT_SQUARE_SIZE

    rank_index = 7 - row
    file_index = col

    return rank_index * 8 + file_index


def square_to_coords(square):
    """Convert square number into file and rank indexes."""
    return square % 8, square // 8


def coords_to_square(file_index, rank_index):
    """Convert file and rank indexes into a square number."""
    return rank_index * 8 + file_index


def square_to_algebraic(square):
    """Convert internal square number into algebraic chess notation."""
    files = "abcdefgh"

    file_index = square % 8
    rank_index = square // 8

    return f"{files[file_index]}{rank_index + 1}"


# ---------------------------------------------------------------------
# Position helpers
# ---------------------------------------------------------------------

def opposite_color(color):
    """Return the opposite chess colour."""
    return Color.BLACK if color == Color.WHITE else Color.WHITE


def color_name(color):
    """Return a readable colour name."""
    return "White" if color == Color.WHITE else "Black"


def piece_color(piece):
    """Return the colour of a piece, or None for empty values."""
    if piece in Piece.white_pieces:
        return Color.WHITE

    if piece in Piece.black_pieces:
        return Color.BLACK

    return None


def get_piece_on_square(position, square):
    """Return the piece on a square, or None if the square is empty."""
    if square is None:
        return None

    for piece, squares in position.piece_map.items():
        if square in squares:
            return piece

    return None


def get_piece_on_square_from_map(piece_map, square):
    """Return a piece from a piece_map dictionary."""
    for piece, squares in piece_map.items():
        if square in squares:
            return piece

    return None


def is_current_turn_piece(position, piece):
    """Return True if the piece belongs to the player whose turn it is."""
    return piece_color(piece) == position.color_to_move


def clone_piece_map(piece_map):
    """Create a safe copy of the current piece map."""
    return {piece: set(squares) for piece, squares in piece_map.items()}


def find_king_square(piece_map, color):
    """Return the king square for a colour."""
    king_piece = Piece.wK if color == Color.WHITE else Piece.bK
    king_squares = piece_map.get(king_piece, set())

    if not king_squares:
        return None

    return next(iter(king_squares))


def sync_engine_state(position):
    """Synchronise helper structures after a manual GUI move."""
    if hasattr(position, "sync_mailbox_from_piece_map"):
        position.sync_mailbox_from_piece_map()

    try:
        position.board.update_position_bitboards(position.piece_map)
        position.update_attack_bitboards()
        position.evaluate_king_check()
    except Exception:
        pass



# ---------------------------------------------------------------------
# Castling helpers
# ---------------------------------------------------------------------

CASTLING_ROUTES = {
    Color.WHITE: {
        "kingside": {
            "king_from": 4,
            "king_to": 6,
            "rook_from": 7,
            "rook_to": 5,
            "empty": [5, 6],
            "safe": [4, 5, 6],
        },
        "queenside": {
            "king_from": 4,
            "king_to": 2,
            "rook_from": 0,
            "rook_to": 3,
            "empty": [1, 2, 3],
            "safe": [4, 3, 2],
        },
    },
    Color.BLACK: {
        "kingside": {
            "king_from": 60,
            "king_to": 62,
            "rook_from": 63,
            "rook_to": 61,
            "empty": [61, 62],
            "safe": [60, 61, 62],
        },
        "queenside": {
            "king_from": 60,
            "king_to": 58,
            "rook_from": 56,
            "rook_to": 59,
            "empty": [57, 58, 59],
            "safe": [60, 59, 58],
        },
    },
}


def get_castle_side_from_rook_square(color, rook_square):
    """Return the castling side controlled by a rook square."""
    if color == Color.WHITE:
        if rook_square == 7:
            return "kingside"
        if rook_square == 0:
            return "queenside"

    if color == Color.BLACK:
        if rook_square == 63:
            return "kingside"
        if rook_square == 56:
            return "queenside"

    return None


def get_castle_side_from_king_target(color, target_square):
    """Return the castling side represented by a king target square."""
    for side, route in CASTLING_ROUTES[color].items():
        if target_square == route["king_to"]:
            return side

    return None


def can_castle_side(position, color, side):
    """Return True when a side can legally castle on the requested side."""
    route = CASTLING_ROUTES[color][side]
    side_index = 0 if side == "kingside" else 1
    enemy_color = opposite_color(color)

    if not position.castle_rights[color][side_index]:
        return False

    king_piece = Piece.wK if color == Color.WHITE else Piece.bK
    rook_piece = Piece.wR if color == Color.WHITE else Piece.bR

    if get_piece_on_square(position, route["king_from"]) != king_piece:
        return False

    if get_piece_on_square(position, route["rook_from"]) != rook_piece:
        return False

    for square in route["empty"]:
        if get_piece_on_square(position, square) is not None:
            return False

    # The king cannot castle out of, through, or into check.
    for square in route["safe"]:
        if is_square_attacked(position.piece_map, square, enemy_color):
            return False

    return True


def get_available_castles(position, selected_square):
    """Return legal castle routes for a selected king or rook."""
    piece = get_piece_on_square(position, selected_square)

    if not is_current_turn_piece(position, piece):
        return []

    color = position.color_to_move
    available = []

    if piece in (Piece.wK, Piece.bK):
        for side in ("kingside", "queenside"):
            route = CASTLING_ROUTES[color][side]
            if selected_square == route["king_from"] and can_castle_side(position, color, side):
                available.append((side, route))

    elif piece in (Piece.wR, Piece.bR):
        side = get_castle_side_from_rook_square(color, selected_square)
        if side and can_castle_side(position, color, side):
            available.append((side, CASTLING_ROUTES[color][side]))

    return available


def calculate_castle_targets(position, selected_square):
    """Return castling destination squares when the king is selected."""
    piece = get_piece_on_square(position, selected_square)

    if piece not in (Piece.wK, Piece.bK):
        return []

    return [route["king_to"] for _, route in get_available_castles(position, selected_square)]


def calculate_castle_highlights(position, selected_square):
    """Highlight the king and rook involved when castling is available."""
    highlight_squares = []

    for _, route in get_available_castles(position, selected_square):
        for square in (route["king_from"], route["rook_from"]):
            if square not in highlight_squares:
                highlight_squares.append(square)

    return highlight_squares


def get_castling_route_for_selection(position, from_square, target_square):
    """Return the castling side and route for a king castling attempt."""
    piece = get_piece_on_square(position, from_square)

    if piece not in (Piece.wK, Piece.bK):
        return None, None

    for side, route in get_available_castles(position, from_square):
        if target_square == route["king_to"]:
            return side, route

    return None, None


def apply_castling_move(position, side, route):
    """Apply castling by moving both the king and rook once."""
    color = position.color_to_move
    king_piece = Piece.wK if color == Color.WHITE else Piece.bK
    rook_piece = Piece.wR if color == Color.WHITE else Piece.bR

    position.piece_map[king_piece].discard(route["king_from"])
    position.piece_map[king_piece].add(route["king_to"])

    position.piece_map[rook_piece].discard(route["rook_from"])
    position.piece_map[rook_piece].add(route["rook_to"])

    # Castling can only happen once because moving the king removes both rights.
    position.castle_rights[color] = [0, 0]
    position.color_to_move = opposite_color(position.color_to_move)
    sync_engine_state(position)

    return True


def update_castle_rights_after_normal_move(position, piece, from_square, target_square, captured_piece):
    """Remove castling rights after king/rook movement or original rook capture."""
    moving_color = piece_color(piece)

    if piece in (Piece.wK, Piece.bK):
        position.castle_rights[moving_color] = [0, 0]

    elif piece in (Piece.wR, Piece.bR):
        side = get_castle_side_from_rook_square(moving_color, from_square)
        if side == "kingside":
            position.castle_rights[moving_color][0] = 0
        elif side == "queenside":
            position.castle_rights[moving_color][1] = 0

    if captured_piece in (Piece.wR, Piece.bR):
        captured_color = piece_color(captured_piece)
        side = get_castle_side_from_rook_square(captured_color, target_square)
        if side == "kingside":
            position.castle_rights[captured_color][0] = 0
        elif side == "queenside":
            position.castle_rights[captured_color][1] = 0


def get_gui_move_notation(position, from_square, target_square):
    """Return readable move notation for GUI move history."""
    side, _ = get_castling_route_for_selection(position, from_square, target_square)

    if side == "kingside":
        return "O-O"

    if side == "queenside":
        return "O-O-O"

    return f"{square_to_algebraic(from_square)}{square_to_algebraic(target_square)}"


# ---------------------------------------------------------------------
# Legal move engine used by the GUI
# ---------------------------------------------------------------------

def generate_pawn_moves(piece_map, piece, from_square, attack_only=False):
    """Generate pawn moves or pawn attack squares."""
    moves = []
    file_index, rank_index = square_to_coords(from_square)
    color = piece_color(piece)

    direction = 1 if color == Color.WHITE else -1
    start_rank = 1 if color == Color.WHITE else 6

    for file_step in (-1, 1):
        target_file = file_index + file_step
        target_rank = rank_index + direction

        if 0 <= target_file < 8 and 0 <= target_rank < 8:
            target = coords_to_square(target_file, target_rank)

            if attack_only:
                moves.append(target)
            else:
                target_piece = get_piece_on_square_from_map(piece_map, target)
                if target_piece is not None and piece_color(target_piece) != color:
                    moves.append(target)

    if attack_only:
        return moves

    forward_rank = rank_index + direction
    if 0 <= forward_rank < 8:
        forward_square = coords_to_square(file_index, forward_rank)
        if get_piece_on_square_from_map(piece_map, forward_square) is None:
            moves.append(forward_square)

            double_rank = rank_index + (2 * direction)
            if rank_index == start_rank and 0 <= double_rank < 8:
                double_square = coords_to_square(file_index, double_rank)
                if get_piece_on_square_from_map(piece_map, double_square) is None:
                    moves.append(double_square)

    return moves


def generate_knight_moves(piece_map, piece, from_square, attack_only=False):
    """Generate knight moves from one exact square."""
    moves = []
    file_index, rank_index = square_to_coords(from_square)
    color = piece_color(piece)

    for file_step, rank_step in [
        (1, 2),
        (2, 1),
        (2, -1),
        (1, -2),
        (-1, -2),
        (-2, -1),
        (-2, 1),
        (-1, 2),
    ]:
        target_file = file_index + file_step
        target_rank = rank_index + rank_step

        if 0 <= target_file < 8 and 0 <= target_rank < 8:
            target = coords_to_square(target_file, target_rank)
            target_piece = get_piece_on_square_from_map(piece_map, target)

            if attack_only or target_piece is None or piece_color(target_piece) != color:
                moves.append(target)

    return moves


def generate_sliding_moves(piece_map, piece, from_square, directions, attack_only=False):
    """Generate rook, bishop, and queen style sliding moves."""
    moves = []
    start_file, start_rank = square_to_coords(from_square)
    color = piece_color(piece)

    for file_step, rank_step in directions:
        target_file = start_file + file_step
        target_rank = start_rank + rank_step

        while 0 <= target_file < 8 and 0 <= target_rank < 8:
            target = coords_to_square(target_file, target_rank)
            target_piece = get_piece_on_square_from_map(piece_map, target)

            if target_piece is None:
                moves.append(target)
            else:
                if attack_only or piece_color(target_piece) != color:
                    moves.append(target)
                break

            target_file += file_step
            target_rank += rank_step

    return moves


def generate_king_moves(piece_map, piece, from_square, attack_only=False):
    """Generate king moves from one exact square."""
    moves = []
    file_index, rank_index = square_to_coords(from_square)
    color = piece_color(piece)

    for file_step in (-1, 0, 1):
        for rank_step in (-1, 0, 1):
            if file_step == 0 and rank_step == 0:
                continue

            target_file = file_index + file_step
            target_rank = rank_index + rank_step

            if 0 <= target_file < 8 and 0 <= target_rank < 8:
                target = coords_to_square(target_file, target_rank)
                target_piece = get_piece_on_square_from_map(piece_map, target)

                if attack_only or target_piece is None or piece_color(target_piece) != color:
                    moves.append(target)

    return moves


def generate_piece_moves(piece_map, piece, from_square, attack_only=False):
    """Generate pseudo-legal moves for one selected piece."""
    if piece in (Piece.wP, Piece.bP):
        return generate_pawn_moves(piece_map, piece, from_square, attack_only)

    if piece in (Piece.wN, Piece.bN):
        return generate_knight_moves(piece_map, piece, from_square, attack_only)

    if piece in (Piece.wB, Piece.bB):
        return generate_sliding_moves(
            piece_map,
            piece,
            from_square,
            [(1, 1), (1, -1), (-1, 1), (-1, -1)],
            attack_only,
        )

    if piece in (Piece.wR, Piece.bR):
        return generate_sliding_moves(
            piece_map,
            piece,
            from_square,
            [(1, 0), (-1, 0), (0, 1), (0, -1)],
            attack_only,
        )

    if piece in (Piece.wQ, Piece.bQ):
        return generate_sliding_moves(
            piece_map,
            piece,
            from_square,
            [
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
                (1, 1),
                (1, -1),
                (-1, 1),
                (-1, -1),
            ],
            attack_only,
        )

    if piece in (Piece.wK, Piece.bK):
        return generate_king_moves(piece_map, piece, from_square, attack_only)

    return []


def is_square_attacked(piece_map, square, attacking_color):
    """Return True if a square is attacked by the given colour."""
    for piece, squares in piece_map.items():
        if piece_color(piece) != attacking_color:
            continue

        for from_square in squares:
            attacked_squares = generate_piece_moves(
                piece_map,
                piece,
                from_square,
                attack_only=True,
            )

            if square in attacked_squares:
                return True

    return False


def apply_move_to_piece_map(piece_map, piece, from_square, target_square):
    """Return a simulated piece map after a move."""
    simulated_map = clone_piece_map(piece_map)

    captured_piece = get_piece_on_square_from_map(simulated_map, target_square)
    if captured_piece is not None:
        simulated_map[captured_piece].discard(target_square)

    simulated_map[piece].discard(from_square)

    target_rank = target_square // 8
    if piece == Piece.wP and target_rank == 7:
        simulated_map[Piece.wQ].add(target_square)
    elif piece == Piece.bP and target_rank == 0:
        simulated_map[Piece.bQ].add(target_square)
    else:
        simulated_map[piece].add(target_square)

    return simulated_map


def calculate_legal_moves(position, from_square):
    """Calculate legal target squares for the selected piece."""
    piece = get_piece_on_square(position, from_square)

    if not is_current_turn_piece(position, piece):
        return []

    legal_moves = []
    pseudo_moves = generate_piece_moves(position.piece_map, piece, from_square)
    own_color = position.color_to_move
    enemy_color = opposite_color(own_color)

    for target_square in pseudo_moves:
        simulated_map = apply_move_to_piece_map(
            position.piece_map,
            piece,
            from_square,
            target_square,
        )
        king_square = find_king_square(simulated_map, own_color)

        if king_square is None:
            continue

        if not is_square_attacked(simulated_map, king_square, enemy_color):
            legal_moves.append(target_square)

    # Add castling targets for a selected king or rook.
    for castle_target in calculate_castle_targets(position, from_square):
        if castle_target not in legal_moves:
            legal_moves.append(castle_target)

    return legal_moves


def apply_gui_move(position, from_square, target_square):
    """Apply a legal GUI move directly to the position state."""
    piece = get_piece_on_square(position, from_square)

    if piece is None:
        return False

    side, route = get_castling_route_for_selection(position, from_square, target_square)
    if route is not None:
        return apply_castling_move(position, side, route)

    if target_square not in calculate_legal_moves(position, from_square):
        return False

    captured_piece = get_piece_on_square(position, target_square)
    update_castle_rights_after_normal_move(
        position,
        piece,
        from_square,
        target_square,
        captured_piece,
    )

    position.piece_map = apply_move_to_piece_map(
        position.piece_map,
        piece,
        from_square,
        target_square,
    )
    position.color_to_move = opposite_color(position.color_to_move)
    sync_engine_state(position)

    return True


# ---------------------------------------------------------------------
# Drawing functions
# ---------------------------------------------------------------------

def draw_board(screen):
    """Draw the 8x8 chess board."""
    for row in range(8):
        for col in range(8):
            colour = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE

            pygame.draw.rect(
                screen,
                colour,
                pygame.Rect(
                    CURRENT_BOARD_RECT.x + col * CURRENT_SQUARE_SIZE,
                    CURRENT_BOARD_RECT.y + row * CURRENT_SQUARE_SIZE,
                    CURRENT_SQUARE_SIZE,
                    CURRENT_SQUARE_SIZE,
                ),
            )


def draw_coordinates(screen, font):
    """Draw board coordinates on the chess board."""
    files = "abcdefgh"
    label_offset = max(4, CURRENT_SQUARE_SIZE // 16)

    for col in range(8):
        file_label = files[col]
        row = 7

        is_light_square = (row + col) % 2 == 0
        colour = COORDINATE_DARK if is_light_square else COORDINATE_LIGHT

        text = font.render(file_label, True, colour)
        screen.blit(
            text,
            (
                CURRENT_BOARD_RECT.x + col * CURRENT_SQUARE_SIZE + CURRENT_SQUARE_SIZE - 16,
                CURRENT_BOARD_RECT.y + row * CURRENT_SQUARE_SIZE + CURRENT_SQUARE_SIZE - 20,
            ),
        )

    for row in range(8):
        rank_label = str(8 - row)
        col = 0

        is_light_square = (row + col) % 2 == 0
        colour = COORDINATE_DARK if is_light_square else COORDINATE_LIGHT

        text = font.render(rank_label, True, colour)
        screen.blit(
            text,
            (
                CURRENT_BOARD_RECT.x + col * CURRENT_SQUARE_SIZE + label_offset,
                CURRENT_BOARD_RECT.y + row * CURRENT_SQUARE_SIZE + label_offset,
            ),
        )


def draw_selected_square(screen, selected_square):
    """Highlight the selected square with a filled overlay."""
    if selected_square is None:
        return

    x, y = square_to_screen(selected_square)

    col = (x - CURRENT_BOARD_RECT.x) // CURRENT_SQUARE_SIZE
    row = (y - CURRENT_BOARD_RECT.y) // CURRENT_SQUARE_SIZE

    is_light_square = (row + col) % 2 == 0
    fill_colour = SELECTED_LIGHT_FILL if is_light_square else SELECTED_DARK_FILL

    highlight_surface = pygame.Surface((CURRENT_SQUARE_SIZE, CURRENT_SQUARE_SIZE), pygame.SRCALPHA)
    highlight_surface.fill(fill_colour)
    screen.blit(highlight_surface, (x, y))

    pygame.draw.rect(
        screen,
        SELECTED_BORDER,
        pygame.Rect(x, y, CURRENT_SQUARE_SIZE, CURRENT_SQUARE_SIZE),
        max(1, CURRENT_SQUARE_SIZE // 40),
    )


def draw_castle_highlights(screen, castle_highlights):
    """Highlight the king and rook when castling is available."""
    for square in castle_highlights:
        x, y = square_to_screen(square)

        highlight_surface = pygame.Surface(
            (CURRENT_SQUARE_SIZE, CURRENT_SQUARE_SIZE),
            pygame.SRCALPHA,
        )
        highlight_surface.fill(CASTLE_FILL)
        screen.blit(highlight_surface, (x, y))

        inset = max(2, CURRENT_SQUARE_SIZE // 18)
        pygame.draw.rect(
            screen,
            CASTLE_BORDER,
            pygame.Rect(
                x + inset,
                y + inset,
                CURRENT_SQUARE_SIZE - inset * 2,
                CURRENT_SQUARE_SIZE - inset * 2,
            ),
            max(2, CURRENT_SQUARE_SIZE // 24),
        )


def draw_legal_moves(screen, legal_moves, position):
    """Highlight all legal target squares for the selected piece."""
    for square in legal_moves:
        x, y = square_to_screen(square)
        target_piece = get_piece_on_square(position, square)

        highlight_surface = pygame.Surface(
            (CURRENT_SQUARE_SIZE, CURRENT_SQUARE_SIZE),
            pygame.SRCALPHA,
        )

        if target_piece is None:
            highlight_surface.fill(LEGAL_MOVE_FILL)
            screen.blit(highlight_surface, (x, y))

            pygame.draw.circle(
                screen,
                LEGAL_MOVE_DOT,
                (
                    x + CURRENT_SQUARE_SIZE // 2,
                    y + CURRENT_SQUARE_SIZE // 2,
                ),
                max(5, CURRENT_SQUARE_SIZE // 9),
            )

        else:
            highlight_surface.fill(CAPTURE_MOVE_FILL)
            screen.blit(highlight_surface, (x, y))

            inset = max(2, CURRENT_SQUARE_SIZE // 20)
            pygame.draw.rect(
                screen,
                CAPTURE_BORDER,
                pygame.Rect(
                    x + inset,
                    y + inset,
                    CURRENT_SQUARE_SIZE - inset * 2,
                    CURRENT_SQUARE_SIZE - inset * 2,
                ),
                max(2, CURRENT_SQUARE_SIZE // 20),
            )


def get_piece_image(piece, piece_images):
    """Return the matching image for a chess piece."""
    if piece == Piece.wK:
        return piece_images["white_king"]
    if piece == Piece.bK:
        return piece_images["black_king"]
    if piece == Piece.wQ:
        return piece_images["white_queen"]
    if piece == Piece.bQ:
        return piece_images["black_queen"]
    if piece == Piece.wR:
        return piece_images["white_rook"]
    if piece == Piece.bR:
        return piece_images["black_rook"]
    if piece == Piece.wB:
        return piece_images["white_bishop"]
    if piece == Piece.bB:
        return piece_images["black_bishop"]
    if piece == Piece.wN:
        return piece_images["white_knight"]
    if piece == Piece.bN:
        return piece_images["black_knight"]
    if piece == Piece.wP:
        return piece_images["white_pawn"]
    if piece == Piece.bP:
        return piece_images["black_pawn"]

    return None


def draw_pieces(screen, position, piece_images):
    """Draw all pieces from the current engine position."""
    scaled_cache = {}

    for piece, squares in position.piece_map.items():
        image = get_piece_image(piece, piece_images)

        if image is None:
            continue

        if piece not in scaled_cache:
            scaled_cache[piece] = scale_image_to_square(image)

        scaled_image = scaled_cache[piece]

        for square in squares:
            x, y = square_to_screen(square)

            rect = scaled_image.get_rect(
                center=(
                    x + CURRENT_SQUARE_SIZE // 2,
                    y + CURRENT_SQUARE_SIZE // 2,
                )
            )

            screen.blit(scaled_image, rect)


def draw_text(screen, text, font, colour, position, center=False):
    """Draw text safely."""
    surface = font.render(text, True, colour)
    rect = surface.get_rect()

    if center:
        rect.center = position
    else:
        rect.topleft = position

    screen.blit(surface, rect)
    return rect


def draw_text_fit(screen, text, font, colour, rect, left_padding=18, right_padding=40):
    """Draw text inside a rectangle, reducing font size if needed."""
    max_width = max(20, rect.width - left_padding - right_padding)
    font_size = font.get_height()
    fitted_font = font

    while fitted_font.size(text)[0] > max_width and font_size > 14:
        font_size -= 1
        fitted_font = pygame.font.SysFont("Arial", font_size, bold=True)

    surface = fitted_font.render(text, True, colour)
    text_rect = surface.get_rect()
    text_rect.left = rect.x + left_padding
    text_rect.centery = rect.centery
    screen.blit(surface, text_rect)
    return text_rect


def draw_menu_button(screen, rect, text, font, bg_colour, border_colour, text_colour):
    """Draw a solid rectangular button."""
    pygame.draw.rect(screen, bg_colour, rect)
    pygame.draw.rect(screen, border_colour, rect, 2)
    draw_text(screen, text, font, text_colour, rect.center, center=True)


def draw_dropdown(screen, main_rect, options, selected_value, font):
    """Draw a dropdown list under a menu option."""
    option_rects = []
    item_height = main_rect.height

    for index, option in enumerate(options):
        rect = pygame.Rect(
            main_rect.x,
            main_rect.bottom + index * item_height,
            main_rect.width,
            item_height,
        )
        fill = MENU_GREEN if option == selected_value else MENU_DROPDOWN
        pygame.draw.rect(screen, fill, rect)
        pygame.draw.rect(screen, MENU_BORDER, rect, 2)
        draw_text_fit(screen, option, font, MENU_TEXT, rect, right_padding=18)
        option_rects.append((rect, option))

    return option_rects


def draw_option_box(screen, rect, label, value, font):
    """Draw a clickable setup option."""
    pygame.draw.rect(screen, MENU_OPTION, rect)
    pygame.draw.rect(screen, MENU_GREEN, rect, 2)
    draw_text_fit(screen, f"{label}: {value}", font, MENU_TEXT, rect, right_padding=48)
    draw_text(screen, "v", font, MENU_TEXT, (rect.right - 32, rect.y + 14))


def draw_menu(screen, logo, settings, dropdown_open, menu_message):
    """Draw a responsive solid-colour lobby/menu screen."""
    width, height = screen.get_size()
    title_font, heading_font, body_font, button_font, small_font, _ = make_fonts(width, height)

    screen.fill(MENU_BG)

    left_width = int(width * 0.43)
    right_width = width - left_width

    left_rect = pygame.Rect(0, 0, left_width, height)
    right_rect = pygame.Rect(left_width, 0, right_width, height)

    pygame.draw.rect(screen, MENU_LEFT, left_rect)
    pygame.draw.rect(screen, MENU_RIGHT, right_rect)

    separator = pygame.Rect(left_width - 2, 0, 4, height)
    pygame.draw.rect(screen, MENU_BG, separator)

    left_center_x = left_rect.centerx
    right_x = right_rect.x + max(34, int(right_width * 0.08))
    right_inner_width = right_width - max(68, int(right_width * 0.16))

    logo_size = min(180, max(95, int(height * 0.22)), max(90, int(left_width * 0.45)))
    if logo is not None:
        logo_scaled = pygame.transform.smoothscale(logo, (logo_size, logo_size))
        logo_rect = logo_scaled.get_rect(center=(left_center_x, int(height * 0.22)))
        screen.blit(logo_scaled, logo_rect)

    draw_text(
        screen,
        "An Chess Engine",
        title_font,
        MENU_TEXT,
        (left_center_x, int(height * 0.47)),
        center=True,
    )

    flavour_lines = [
        "Every move shapes the board.",
        "Think ahead. Protect your king.",
        "Find the strongest move.",
    ]
    line_gap = max(26, int(height * 0.045))
    start_y = int(height * 0.56)
    for index, line in enumerate(flavour_lines):
        draw_text(
            screen,
            line,
            body_font,
            MENU_MUTED,
            (left_center_x, start_y + index * line_gap),
            center=True,
        )

    draw_text(
        screen,
        "Modified HSC Software Engineering Project",
        small_font,
        MENU_MUTED,
        (left_center_x, int(height * 0.88)),
        center=True,
    )

    draw_text(screen, "Game Setup", heading_font, MENU_TEXT, (right_x, int(height * 0.13)))
    draw_text(
        screen,
        "Choose your turn and timer, then start playing.",
        body_font,
        MENU_MUTED,
        (right_x, int(height * 0.20)),
    )

    option_height = max(46, int(height * 0.075))
    option_gap = max(12, int(height * 0.025))
    option_y = int(height * 0.30)

    turn_rect = pygame.Rect(right_x, option_y, right_inner_width, option_height)
    timer_rect = pygame.Rect(right_x, turn_rect.bottom + option_gap, right_inner_width, option_height)

    draw_option_box(screen, turn_rect, "First turn", settings["turn"], body_font)
    draw_option_box(screen, timer_rect, "Timer", settings["timer"], body_font)

    controls_y = min(timer_rect.bottom + int(height * 0.050), int(height * 0.61))
    draw_text(screen, "Controls", body_font, MENU_TEXT, (right_x, controls_y))

    controls = [
        "Click a piece to view legal moves.",
        "Click a highlighted square to move.",
        "Press ESC during the game to return here.",
    ]

    control_line_gap = max(22, int(height * 0.038))
    first_control_y = controls_y + max(28, int(height * 0.045))

    for index, line in enumerate(controls):
        draw_text(
            screen,
            line,
            small_font,
            MENU_MUTED,
            (right_x, first_control_y + index * control_line_gap),
        )

    message_y = first_control_y + len(controls) * control_line_gap + 10
    if menu_message:
        draw_text(screen, menu_message, small_font, MENU_GREEN, (right_x, message_y))

    start_height = max(50, int(height * 0.085))
    quit_height = max(38, int(height * 0.06))
    button_gap = max(10, int(height * 0.018))
    start_y = max(message_y + 32, height - start_height - quit_height - button_gap - 16)

    if start_y + start_height + button_gap + quit_height > height - 8:
        start_y = height - start_height - quit_height - button_gap - 8

    start_button = pygame.Rect(
        right_x,
        start_y,
        right_inner_width,
        start_height,
    )
    quit_button = pygame.Rect(
        right_x,
        start_button.bottom + button_gap,
        right_inner_width,
        quit_height,
    )

    draw_menu_button(
        screen,
        start_button,
        "Start Game",
        button_font,
        MENU_GREEN,
        MENU_GREEN_DARK,
        MENU_TEXT,
    )
    draw_menu_button(
        screen,
        quit_button,
        "Quit",
        body_font,
        MENU_DARK_BUTTON,
        MENU_BORDER,
        MENU_TEXT,
    )

    dropdown_rects = []
    if dropdown_open == "turn":
        dropdown_rects = [("turn", rect, value) for rect, value in draw_dropdown(
            screen,
            turn_rect,
            TURN_OPTIONS,
            settings["turn"],
            body_font,
        )]
    elif dropdown_open == "timer":
        dropdown_rects = [("timer", rect, value) for rect, value in draw_dropdown(
            screen,
            timer_rect,
            TIMER_OPTIONS,
            settings["timer"],
            body_font,
        )]

    return {
        "turn": turn_rect,
        "timer": timer_rect,
        "start": start_button,
        "quit": quit_button,
        "dropdown_items": dropdown_rects,
    }


def draw_game_side_panel(screen, position, settings, clocks, move_history, status_message, surrender_pending=False):
    """Draw timers, current turn, move history, and surrender button."""
    if CURRENT_SIDE_PANEL_RECT.width <= 0:
        return {}

    panel = CURRENT_SIDE_PANEL_RECT
    pygame.draw.rect(screen, PANEL_BG, panel)
    pygame.draw.rect(screen, PANEL_BORDER, panel, 2)

    title_font = pygame.font.SysFont("Arial", max(22, panel.width // 10), bold=True)
    heading_font = pygame.font.SysFont("Arial", max(18, panel.width // 14), bold=True)
    body_font = pygame.font.SysFont("Arial", max(16, panel.width // 18), bold=True)
    small_font = pygame.font.SysFont("Arial", max(14, panel.width // 22), bold=True)

    margin = max(14, panel.width // 18)
    y = panel.y + margin

    side = color_name(position.color_to_move)
    draw_text(screen, f"{side} to move", title_font, PANEL_TEXT, (panel.x + margin, y))
    y += max(42, panel.height // 13)

    timer_total, _ = get_timer_settings(settings["timer"])

    def draw_clock_box(label, colour, value, active, top_y):
        rect = pygame.Rect(
            panel.x + margin,
            top_y,
            panel.width - margin * 2,
            max(62, panel.height // 10),
        )
        fill = PANEL_ACTIVE if active else PANEL_CARD
        pygame.draw.rect(screen, fill, rect)
        pygame.draw.rect(screen, PANEL_BORDER, rect, 2)
        draw_text(screen, label, small_font, colour, (rect.x + 12, rect.y + 8))

        value_surface = heading_font.render(value, True, PANEL_TEXT)
        value_rect = value_surface.get_rect()
        value_rect.centery = rect.centery
        value_rect.right = rect.right - 12
        screen.blit(value_surface, value_rect)

        return rect.bottom + max(10, panel.height // 45)

    if timer_total is None:
        black_time = "No Timer"
        white_time = "No Timer"
    else:
        black_time = format_clock_time(clocks[Color.BLACK])
        white_time = format_clock_time(clocks[Color.WHITE])

    y = draw_clock_box("Black", PANEL_TEXT, black_time, position.color_to_move == Color.BLACK, y)
    y = draw_clock_box("White", PANEL_TEXT, white_time, position.color_to_move == Color.WHITE, y)

    y += max(10, panel.height // 50)
    draw_text(screen, "Move History", heading_font, PANEL_TEXT, (panel.x + margin, y))
    y += max(34, panel.height // 16)

    status_box_height = max(38, panel.height // 18)
    surrender_height = max(42, panel.height // 15)
    status_y = panel.bottom - margin - status_box_height
    surrender_y = status_y - max(10, panel.height // 45) - surrender_height

    history_rect = pygame.Rect(
        panel.x + margin,
        y,
        panel.width - margin * 2,
        max(90, surrender_y - y - margin),
    )
    pygame.draw.rect(screen, PANEL_CARD, history_rect)
    pygame.draw.rect(screen, PANEL_BORDER, history_rect, 2)

    line_y = history_rect.y + 10
    line_gap = max(22, panel.height // 28)
    max_lines = max(4, (history_rect.height - 20) // line_gap)

    paired_moves = []
    for index in range(0, len(move_history), 2):
        move_number = index // 2 + 1
        white_move = move_history[index]
        black_move = move_history[index + 1] if index + 1 < len(move_history) else ""
        paired_moves.append(f"{move_number}. {white_move}   {black_move}")

    visible_moves = paired_moves[-max_lines:]
    if not visible_moves:
        draw_text(
            screen,
            "No moves yet.",
            small_font,
            PANEL_MUTED,
            (history_rect.x + 10, line_y),
        )
    else:
        for line in visible_moves:
            draw_text(
                screen,
                line,
                small_font,
                PANEL_TEXT,
                (history_rect.x + 10, line_y),
            )
            line_y += line_gap

    surrender_rect = pygame.Rect(
        panel.x + margin,
        surrender_y,
        panel.width - margin * 2,
        surrender_height,
    )
    surrender_colour = PANEL_WARNING if surrender_pending else PANEL_DANGER
    surrender_text = "Confirm Surrender" if surrender_pending else "Surrender"
    pygame.draw.rect(screen, surrender_colour, surrender_rect)
    pygame.draw.rect(screen, PANEL_BORDER, surrender_rect, 2)
    draw_text(screen, surrender_text, body_font, PANEL_TEXT, surrender_rect.center, center=True)

    status_rect = pygame.Rect(
        panel.x + margin,
        status_y,
        panel.width - margin * 2,
        status_box_height,
    )
    pygame.draw.rect(screen, PANEL_CARD, status_rect)
    pygame.draw.rect(screen, PANEL_BORDER, status_rect, 1)
    if status_message:
        draw_text_fit(screen, status_message, small_font, PANEL_MUTED, status_rect, left_padding=10, right_padding=10)
    else:
        draw_text(screen, "Ready.", small_font, PANEL_MUTED, (status_rect.x + 10, status_rect.y + 9))

    return {"surrender": surrender_rect}


def draw_game(screen, position, piece_images, selected_square, legal_moves, castle_highlights, settings, clocks, move_history, status_message, surrender_pending=False):
    """Draw the game board and the right-side match panel."""
    update_board_layout(screen)
    _, _, _, _, _, coordinate_font = make_fonts(*screen.get_size())
    screen.fill(MENU_BG)
    draw_board(screen)
    draw_castle_highlights(screen, castle_highlights)
    draw_legal_moves(screen, legal_moves, position)
    draw_selected_square(screen, selected_square)
    draw_pieces(screen, position, piece_images)
    draw_coordinates(screen, coordinate_font)
    return draw_game_side_panel(screen, position, settings, clocks, move_history, status_message, surrender_pending)



def draw_game_over(screen, winner_color, reason):
    """Draw the end-game screen with rematch and menu buttons."""
    width, height = screen.get_size()
    title_font, heading_font, body_font, button_font, small_font, _ = make_fonts(width, height)

    screen.fill(GAME_OVER_BG)

    card_width = min(560, width - 80)
    card_height = min(420, height - 80)
    card = pygame.Rect(0, 0, card_width, card_height)
    card.center = (width // 2, height // 2)

    pygame.draw.rect(screen, GAME_OVER_CARD, card)
    pygame.draw.rect(screen, MENU_BORDER, card, 3)

    winner_text = f"{color_name(winner_color)} Wins"
    loser_text = "Black loses" if winner_color == Color.WHITE else "White loses"

    draw_text(screen, "Game Over", heading_font, MENU_MUTED, (card.centerx, card.y + 55), center=True)
    draw_text(screen, winner_text, title_font, MENU_TEXT, (card.centerx, card.y + 115), center=True)
    draw_text(screen, loser_text, body_font, MENU_MUTED, (card.centerx, card.y + 165), center=True)

    if reason:
        draw_text(screen, reason, small_font, MENU_GREEN, (card.centerx, card.y + 205), center=True)

    button_width = card_width - 120
    button_height = 58
    rematch_button = pygame.Rect(card.x + 60, card.bottom - 150, button_width, button_height)
    menu_button = pygame.Rect(card.x + 60, rematch_button.bottom + 18, button_width, button_height)

    draw_menu_button(screen, rematch_button, "Rematch", button_font, MENU_GREEN, MENU_GREEN_DARK, MENU_TEXT)
    draw_menu_button(screen, menu_button, "Return to Main Menu", body_font, MENU_DARK_BUTTON, MENU_BORDER, MENU_TEXT)

    return {"rematch": rematch_button, "menu": menu_button}


# ---------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------

def main():
    """Start the graphical chess application."""
    pygame.init()

    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("An Chess Engine - Menu")

    piece_images = load_piece_images()
    logo = load_logo()

    position = Position()
    sync_engine_state(position)

    selected_square = None
    legal_moves = []
    castle_highlights = []
    screen_mode = "menu"
    settings = {
        "turn": "White",
        "timer": "No Timer",
    }
    dropdown_open = None
    menu_message = ""
    menu_buttons = {}
    game_buttons = {}
    game_over_buttons = {}
    move_history = []
    status_message = ""
    last_warning_message = None
    surrender_pending = False
    game_over_winner = Color.WHITE
    game_over_reason = ""
    timer_total = None
    timer_increment = 0
    clocks = {
        Color.WHITE: None,
        Color.BLACK: None,
    }
    last_timer_update = time.monotonic()
    running = True

    def set_status(message, dedupe=False):
        """Update status text and avoid repeating the same warning message."""
        nonlocal status_message, last_warning_message

        if dedupe and message == last_warning_message:
            status_message = message
            return

        print(message)
        status_message = message
        last_warning_message = message if dedupe else None

    def start_new_match():
        """Start or restart a match using the current menu settings."""
        nonlocal position, selected_square, legal_moves, castle_highlights
        nonlocal move_history, status_message, last_warning_message, surrender_pending
        nonlocal timer_total, timer_increment, clocks, last_timer_update, screen_mode, screen

        position = Position()
        position.color_to_move = Color.BLACK if settings["turn"] == "Black" else Color.WHITE
        sync_engine_state(position)

        timer_total, timer_increment = get_timer_settings(settings["timer"])
        clocks = {
            Color.WHITE: timer_total,
            Color.BLACK: timer_total,
        }

        selected_square = None
        legal_moves = []
        castle_highlights = []
        move_history = []
        status_message = ""
        last_warning_message = None
        surrender_pending = False
        screen_mode = "game"
        last_timer_update = time.monotonic()
        side = color_name(position.color_to_move)
        pygame.display.set_caption(f"An Chess Engine GUI - {side} to move")
        screen = pygame.display.set_mode((1000, 680), pygame.RESIZABLE)

    def end_game(winner_colour, reason):
        """Move to the end-game screen."""
        nonlocal screen_mode, game_over_winner, game_over_reason, selected_square
        nonlocal legal_moves, castle_highlights, surrender_pending

        game_over_winner = winner_colour
        game_over_reason = reason
        selected_square = None
        legal_moves = []
        castle_highlights = []
        surrender_pending = False
        screen_mode = "game_over"
        pygame.display.set_caption(f"An Chess Engine - {color_name(winner_colour)} Wins")

    while running:
        now = time.monotonic()
        if screen_mode == "game" and timer_total is not None:
            elapsed = now - last_timer_update
            active_colour = position.color_to_move
            clocks[active_colour] = max(0, clocks[active_colour] - elapsed)
            last_timer_update = now

            if clocks[active_colour] <= 0:
                loser = active_colour
                winner = opposite_color(loser)
                end_game(winner, f"{color_name(loser)} ran out of time.")
        else:
            last_timer_update = now

        if screen_mode == "menu":
            menu_buttons = draw_menu(screen, logo, settings, dropdown_open, menu_message)
            pygame.display.flip()
        elif screen_mode == "game_over":
            game_over_buttons = draw_game_over(screen, game_over_winner, game_over_reason)
            pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                if screen_mode == "game":
                    new_width = max(900, event.w)
                    new_height = max(560, event.h)
                else:
                    new_width = max(760, event.w)
                    new_height = max(520, event.h)
                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

            if screen_mode == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicked_dropdown_item = False

                    for setting_name, rect, value in menu_buttons.get("dropdown_items", []):
                        if rect.collidepoint(event.pos):
                            settings[setting_name] = value
                            dropdown_open = None
                            menu_message = f"{value} selected."
                            clicked_dropdown_item = True
                            break

                    if clicked_dropdown_item:
                        continue

                    if menu_buttons.get("start") and menu_buttons["start"].collidepoint(event.pos):
                        start_new_match()

                    elif menu_buttons.get("quit") and menu_buttons["quit"].collidepoint(event.pos):
                        running = False

                    elif menu_buttons.get("turn") and menu_buttons["turn"].collidepoint(event.pos):
                        dropdown_open = None if dropdown_open == "turn" else "turn"
                        menu_message = "Choose who moves first."

                    elif menu_buttons.get("timer") and menu_buttons["timer"].collidepoint(event.pos):
                        dropdown_open = None if dropdown_open == "timer" else "timer"
                        menu_message = "Choose a timer option."

                    else:
                        dropdown_open = None

            elif screen_mode == "game_over":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game_over_buttons.get("rematch") and game_over_buttons["rematch"].collidepoint(event.pos):
                        start_new_match()
                    elif game_over_buttons.get("menu") and game_over_buttons["menu"].collidepoint(event.pos):
                        screen_mode = "menu"
                        pygame.display.set_caption("An Chess Engine - Menu")
                        screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT), pygame.RESIZABLE)

            elif screen_mode == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    selected_square = None
                    legal_moves = []
                    castle_highlights = []
                    surrender_pending = False
                    screen_mode = "menu"
                    pygame.display.set_caption("An Chess Engine - Menu")
                    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT), pygame.RESIZABLE)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    update_board_layout(screen)

                    if game_buttons.get("surrender") and game_buttons["surrender"].collidepoint(event.pos):
                        if surrender_pending:
                            loser = position.color_to_move
                            winner = opposite_color(loser)
                            end_game(winner, f"{color_name(loser)} surrendered.")
                        else:
                            surrender_pending = True
                            set_status("Click Surrender again to confirm.", dedupe=True)
                        continue

                    if surrender_pending:
                        surrender_pending = False

                    clicked_square = screen_to_square(event.pos)
                    clicked_piece = get_piece_on_square(position, clicked_square)

                    if clicked_square is None:
                        continue

                    if selected_square is None:
                        if is_current_turn_piece(position, clicked_piece):
                            selected_square = clicked_square
                            legal_moves = calculate_legal_moves(position, selected_square)
                            castle_highlights = calculate_castle_highlights(position, selected_square)
                            set_status(f"Selected {square_to_algebraic(clicked_square)}")
                        else:
                            selected_square = None
                            legal_moves = []
                            castle_highlights = []
                            set_status("Select one of your own pieces.", dedupe=True)

                    else:
                        if clicked_square == selected_square:
                            selected_square = None
                            legal_moves = []
                            castle_highlights = []
                            set_status("Selection cleared.")

                        elif is_current_turn_piece(position, clicked_piece):
                            selected_square = clicked_square
                            legal_moves = calculate_legal_moves(position, selected_square)
                            castle_highlights = calculate_castle_highlights(position, selected_square)
                            set_status(f"Selected {square_to_algebraic(clicked_square)}")

                        elif clicked_square in legal_moves:
                            from_square = selected_square
                            moved_colour = position.color_to_move
                            move_text = get_gui_move_notation(position, from_square, clicked_square)

                            if apply_gui_move(position, selected_square, clicked_square):
                                move_history.append(move_text)
                                if timer_total is not None and timer_increment > 0:
                                    clocks[moved_colour] += timer_increment
                                set_status(f"Moved {move_text}")
                            else:
                                set_status(f"Illegal move: {move_text}")

                            selected_square = None
                            legal_moves = []
                            castle_highlights = []
                            surrender_pending = False
                            side = color_name(position.color_to_move)
                            pygame.display.set_caption(f"An Chess Engine GUI - {side} to move")

                        else:
                            illegal_text = (
                                f"Illegal move: "
                                f"{square_to_algebraic(selected_square)}"
                                f"{square_to_algebraic(clicked_square)}"
                            )
                            set_status(illegal_text)
                            selected_square = None
                            legal_moves = []
                            castle_highlights = []

        if screen_mode == "game":
            game_buttons = draw_game(
                screen,
                position,
                piece_images,
                selected_square,
                legal_moves,
                castle_highlights,
                settings,
                clocks,
                move_history,
                status_message,
                surrender_pending,
            )
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
