import os

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

MODE_OPTIONS = ["Player vs Player"]
TURN_OPTIONS = ["White", "Black"]
TIMER_OPTIONS = ["No Timer", "5 min", "10 min", "15 + 10"]

CURRENT_BOARD_RECT = pygame.Rect(0, 0, BOARD_SIZE, BOARD_SIZE)
CURRENT_SQUARE_SIZE = SQUARE_SIZE


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
    """Resize and centre the chess board inside the current game window."""
    global CURRENT_BOARD_RECT, CURRENT_SQUARE_SIZE

    width, height = screen.get_size()
    board_size = min(width, height) - 20
    board_size = max(320, board_size)
    board_size -= board_size % 8

    x = (width - board_size) // 2
    y = (height - board_size) // 2

    CURRENT_BOARD_RECT = pygame.Rect(x, y, board_size, board_size)
    CURRENT_SQUARE_SIZE = board_size // 8


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

    return legal_moves


def apply_gui_move(position, from_square, target_square):
    """Apply a legal GUI move directly to the position state."""
    piece = get_piece_on_square(position, from_square)

    if piece is None:
        return False

    if target_square not in calculate_legal_moves(position, from_square):
        return False

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
        draw_text(screen, option, font, MENU_TEXT, (rect.x + 18, rect.y + 14))
        option_rects.append((rect, option))

    return option_rects


def draw_option_box(screen, rect, label, value, font):
    """Draw a clickable setup option."""
    pygame.draw.rect(screen, MENU_OPTION, rect)
    pygame.draw.rect(screen, MENU_GREEN, rect, 2)
    draw_text(screen, f"{label}: {value}", font, MENU_TEXT, (rect.x + 18, rect.y + 14))
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
        "Choose your settings and start playing.",
        body_font,
        MENU_MUTED,
        (right_x, int(height * 0.20)),
    )

    option_height = max(46, int(height * 0.075))
    option_gap = max(12, int(height * 0.025))
    option_y = int(height * 0.30)

    mode_rect = pygame.Rect(right_x, option_y, right_inner_width, option_height)
    turn_rect = pygame.Rect(right_x, mode_rect.bottom + option_gap, right_inner_width, option_height)
    timer_rect = pygame.Rect(right_x, turn_rect.bottom + option_gap, right_inner_width, option_height)

    draw_option_box(screen, mode_rect, "Mode", settings["mode"], body_font)
    draw_option_box(screen, turn_rect, "First turn", settings["turn"], body_font)
    draw_option_box(screen, timer_rect, "Timer", settings["timer"], body_font)

    controls_y = min(timer_rect.bottom + int(height * 0.055), int(height * 0.61))
    draw_text(screen, "Controls", body_font, MENU_TEXT, (right_x, controls_y))

    controls = [
        "Click a piece to view legal moves.",
        "Click a highlighted square to move.",
        "Press ESC during the game to return here.",
    ]

    for index, line in enumerate(controls):
        draw_text(
            screen,
            line,
            small_font,
            MENU_MUTED,
            (right_x, controls_y + 34 + index * 25),
        )

    if menu_message:
        draw_text(screen, menu_message, small_font, MENU_GREEN, (right_x, int(height * 0.74)))

    start_button = pygame.Rect(
        right_x,
        height - max(105, int(height * 0.17)),
        right_inner_width,
        max(50, int(height * 0.085)),
    )
    quit_button = pygame.Rect(
        right_x,
        start_button.bottom + max(10, int(height * 0.018)),
        right_inner_width,
        max(38, int(height * 0.06)),
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
    if dropdown_open == "mode":
        dropdown_rects = [("mode", rect, value) for rect, value in draw_dropdown(
            screen,
            mode_rect,
            MODE_OPTIONS,
            settings["mode"],
            body_font,
        )]
    elif dropdown_open == "turn":
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
        "mode": mode_rect,
        "turn": turn_rect,
        "timer": timer_rect,
        "start": start_button,
        "quit": quit_button,
        "dropdown_items": dropdown_rects,
    }


def draw_game(screen, position, piece_images, selected_square, legal_moves):
    """Draw the game board."""
    update_board_layout(screen)
    _, _, _, _, _, coordinate_font = make_fonts(*screen.get_size())
    screen.fill(MENU_BG)
    draw_board(screen)
    draw_legal_moves(screen, legal_moves, position)
    draw_selected_square(screen, selected_square)
    draw_pieces(screen, position, piece_images)
    draw_coordinates(screen, coordinate_font)


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
    screen_mode = "menu"
    settings = {
        "mode": "Player vs Player",
        "turn": "White",
        "timer": "No Timer",
    }
    dropdown_open = None
    menu_message = ""
    menu_buttons = {}
    running = True

    while running:
        if screen_mode == "menu":
            menu_buttons = draw_menu(screen, logo, settings, dropdown_open, menu_message)
            pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
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
                        position = Position()
                        if settings["turn"] == "Black":
                            position.color_to_move = Color.BLACK
                        else:
                            position.color_to_move = Color.WHITE
                        sync_engine_state(position)
                        selected_square = None
                        legal_moves = []
                        screen_mode = "game"
                        side = "White" if position.color_to_move == Color.WHITE else "Black"
                        pygame.display.set_caption(f"An Chess Engine GUI - {side} to move")

                    elif menu_buttons.get("quit") and menu_buttons["quit"].collidepoint(event.pos):
                        running = False

                    elif menu_buttons.get("mode") and menu_buttons["mode"].collidepoint(event.pos):
                        dropdown_open = None if dropdown_open == "mode" else "mode"
                        menu_message = "Choose a mode."

                    elif menu_buttons.get("turn") and menu_buttons["turn"].collidepoint(event.pos):
                        dropdown_open = None if dropdown_open == "turn" else "turn"
                        menu_message = "Choose who moves first."

                    elif menu_buttons.get("timer") and menu_buttons["timer"].collidepoint(event.pos):
                        dropdown_open = None if dropdown_open == "timer" else "timer"
                        menu_message = "Choose a timer option."

                    else:
                        dropdown_open = None

            elif screen_mode == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    selected_square = None
                    legal_moves = []
                    screen_mode = "menu"
                    pygame.display.set_caption("An Chess Engine - Menu")

                if event.type == pygame.MOUSEBUTTONDOWN:
                    update_board_layout(screen)
                    clicked_square = screen_to_square(event.pos)
                    clicked_piece = get_piece_on_square(position, clicked_square)

                    if clicked_square is None:
                        continue

                    if selected_square is None:
                        if is_current_turn_piece(position, clicked_piece):
                            selected_square = clicked_square
                            legal_moves = calculate_legal_moves(position, selected_square)
                            print(f"Selected {square_to_algebraic(clicked_square)}")
                        else:
                            selected_square = None
                            legal_moves = []
                            print("Select one of your own pieces.")

                    else:
                        if clicked_square == selected_square:
                            selected_square = None
                            legal_moves = []

                        elif is_current_turn_piece(position, clicked_piece):
                            selected_square = clicked_square
                            legal_moves = calculate_legal_moves(position, selected_square)
                            print(f"Selected {square_to_algebraic(clicked_square)}")

                        elif clicked_square in legal_moves:
                            from_square = selected_square
                            if apply_gui_move(position, selected_square, clicked_square):
                                print(
                                    f"Moved "
                                    f"{square_to_algebraic(from_square)}"
                                    f"{square_to_algebraic(clicked_square)}"
                                )
                            else:
                                print(
                                    f"Illegal move: "
                                    f"{square_to_algebraic(from_square)}"
                                    f"{square_to_algebraic(clicked_square)}"
                                )

                            selected_square = None
                            legal_moves = []
                            side = "White" if position.color_to_move == Color.WHITE else "Black"
                            pygame.display.set_caption(f"An Chess Engine GUI - {side} to move")

                        else:
                            print(
                                f"Illegal move: "
                                f"{square_to_algebraic(selected_square)}"
                                f"{square_to_algebraic(clicked_square)}"
                            )
                            selected_square = None
                            legal_moves = []

        if screen_mode == "game":
            draw_game(screen, position, piece_images, selected_square, legal_moves)
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
