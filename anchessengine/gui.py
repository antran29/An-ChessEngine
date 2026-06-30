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

MENU_BG = (20, 28, 24)
MENU_PANEL = (38, 48, 42)
MENU_PANEL_LIGHT = (48, 58, 52)
MENU_TEXT = (245, 245, 235)
MENU_MUTED = (185, 195, 185)
MENU_GREEN = (118, 178, 75)
MENU_GREEN_DARK = (88, 140, 55)
MENU_BORDER = (78, 95, 82)
MENU_SELECTED = (93, 125, 75)
MENU_DISABLED = (55, 65, 58)

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
ASSET_DIR = os.path.join(PROJECT_ROOT, "assets", "pieces")
LOGO_PATH = os.path.join(PROJECT_ROOT, "AChess.png")

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
            logo = pygame.image.load(logo_path).convert_alpha()
            return pygame.transform.smoothscale(logo, (150, 150))

    return None


# ---------------------------------------------------------------------
# Board coordinate helpers
# ---------------------------------------------------------------------

def square_to_screen(square):
    """Convert internal square number into screen coordinates."""
    file_index = square % 8
    rank_index = square // 8

    col = file_index
    row = 7 - rank_index

    x = col * SQUARE_SIZE
    y = row * SQUARE_SIZE

    return x, y


def screen_to_square(mouse_pos):
    """Convert mouse position into an internal square number."""
    x, y = mouse_pos

    if not 0 <= x < BOARD_SIZE or not 0 <= y < BOARD_SIZE:
        return None

    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE

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
        # The GUI uses its own move legality filter, so this is only a best-effort
        # sync for the original engine helper structures.
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

    # Pawns attack diagonally regardless of whether a piece is present.
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

    # Normal one-square pawn move.
    forward_rank = rank_index + direction
    if 0 <= forward_rank < 8:
        forward_square = coords_to_square(file_index, forward_rank)
        if get_piece_on_square_from_map(piece_map, forward_square) is None:
            moves.append(forward_square)

            # Two-square pawn move from the starting rank.
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

    # Remove captured piece if the target square is occupied.
    captured_piece = get_piece_on_square_from_map(simulated_map, target_square)
    if captured_piece is not None:
        simulated_map[captured_piece].discard(target_square)

    simulated_map[piece].discard(from_square)

    # Promote pawns to queen automatically for GUI play.
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
                    col * SQUARE_SIZE,
                    row * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
            )


def draw_coordinates(screen, font):
    """Draw board coordinates on the chess board."""
    files = "abcdefgh"

    for col in range(8):
        file_label = files[col]
        row = 7

        is_light_square = (row + col) % 2 == 0
        colour = COORDINATE_DARK if is_light_square else COORDINATE_LIGHT

        text = font.render(file_label, True, colour)
        screen.blit(
            text,
            (
                col * SQUARE_SIZE + SQUARE_SIZE - 16,
                row * SQUARE_SIZE + SQUARE_SIZE - 20,
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
                col * SQUARE_SIZE + 5,
                row * SQUARE_SIZE + 4,
            ),
        )


def draw_selected_square(screen, selected_square):
    """Highlight the selected square with a filled overlay."""
    if selected_square is None:
        return

    x, y = square_to_screen(selected_square)

    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE

    is_light_square = (row + col) % 2 == 0
    fill_colour = SELECTED_LIGHT_FILL if is_light_square else SELECTED_DARK_FILL

    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    highlight_surface.fill(fill_colour)
    screen.blit(highlight_surface, (x, y))

    pygame.draw.rect(
        screen,
        SELECTED_BORDER,
        pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE),
        2,
    )


def draw_legal_moves(screen, legal_moves, position):
    """Highlight all legal target squares for the selected piece."""
    for square in legal_moves:
        x, y = square_to_screen(square)
        target_piece = get_piece_on_square(position, square)

        highlight_surface = pygame.Surface(
            (SQUARE_SIZE, SQUARE_SIZE),
            pygame.SRCALPHA,
        )

        if target_piece is None:
            highlight_surface.fill(LEGAL_MOVE_FILL)
            screen.blit(highlight_surface, (x, y))

            pygame.draw.circle(
                screen,
                LEGAL_MOVE_DOT,
                (
                    x + SQUARE_SIZE // 2,
                    y + SQUARE_SIZE // 2,
                ),
                9,
            )

        else:
            highlight_surface.fill(CAPTURE_MOVE_FILL)
            screen.blit(highlight_surface, (x, y))

            pygame.draw.rect(
                screen,
                CAPTURE_BORDER,
                pygame.Rect(x + 3, y + 3, SQUARE_SIZE - 6, SQUARE_SIZE - 6),
                4,
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
    for piece, squares in position.piece_map.items():
        image = get_piece_image(piece, piece_images)

        if image is None:
            continue

        for square in squares:
            x, y = square_to_screen(square)

            rect = image.get_rect(
                center=(
                    x + SQUARE_SIZE // 2,
                    y + SQUARE_SIZE // 2,
                )
            )

            screen.blit(image, rect)


def draw_button(screen, rect, text, font, bg_colour, border_colour, text_colour):
    """Draw a simple solid rectangular menu button."""
    pygame.draw.rect(screen, bg_colour, rect)
    pygame.draw.rect(screen, border_colour, rect, 2)

    text_surface = font.render(text, True, text_colour)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


def draw_info_box(screen, rect, label, font, selected=False):
    """Draw a simple rectangular setup option."""
    fill = MENU_SELECTED if selected else MENU_PANEL_LIGHT
    pygame.draw.rect(screen, fill, rect)
    pygame.draw.rect(screen, MENU_GREEN if selected else MENU_BORDER, rect, 2)

    text_surface = font.render(label, True, MENU_TEXT)
    screen.blit(text_surface, (rect.x + 18, rect.y + 15))


def draw_menu(screen, logo, fonts, selected_time, menu_message):
    """Draw the lobby/menu screen using simple solid UI blocks."""
    title_font, heading_font, body_font, button_font, small_font = fonts
    screen.fill(MENU_BG)

    left_panel = pygame.Rect(55, 65, 330, 510)
    right_panel = pygame.Rect(425, 65, 480, 510)

    pygame.draw.rect(screen, MENU_PANEL, left_panel)
    pygame.draw.rect(screen, MENU_BORDER, left_panel, 2)

    pygame.draw.rect(screen, MENU_PANEL, right_panel)
    pygame.draw.rect(screen, MENU_BORDER, right_panel, 2)

    if logo is not None:
        logo_rect = logo.get_rect(center=(left_panel.centerx, 160))
        screen.blit(logo, logo_rect)

    title = title_font.render("An Chess Engine", True, MENU_TEXT)
    title_rect = title.get_rect(center=(left_panel.centerx, 300))
    screen.blit(title, title_rect)

    flavour_lines = [
        "Every move shapes the board.",
        "Think ahead. Protect your king.",
        "Find the strongest move.",
    ]

    for index, line in enumerate(flavour_lines):
        text = body_font.render(line, True, MENU_MUTED)
        text_rect = text.get_rect(center=(left_panel.centerx, 355 + index * 32))
        screen.blit(text, text_rect)

    credit = small_font.render("Modified HSC Software Engineering Project", True, MENU_MUTED)
    credit_rect = credit.get_rect(center=(left_panel.centerx, 520))
    screen.blit(credit, credit_rect)

    heading = heading_font.render("Game Setup", True, MENU_TEXT)
    screen.blit(heading, (right_panel.x + 35, right_panel.y + 35))

    subheading = body_font.render("Choose your settings and start playing.", True, MENU_MUTED)
    screen.blit(subheading, (right_panel.x + 35, right_panel.y + 88))

    mode_rect = pygame.Rect(right_panel.x + 35, right_panel.y + 135, 410, 54)
    turn_rect = pygame.Rect(right_panel.x + 35, right_panel.y + 202, 410, 54)
    no_timer_rect = pygame.Rect(right_panel.x + 35, right_panel.y + 270, 410, 54)

    draw_info_box(screen, mode_rect, "Mode: Player vs Player", body_font, selected=True)
    draw_info_box(screen, turn_rect, "First turn: White", body_font, selected=True)
    draw_info_box(screen, no_timer_rect, "Timer: No Timer", body_font, selected=(selected_time == "No Timer"))

    controls_heading = body_font.render("Controls", True, MENU_TEXT)
    screen.blit(controls_heading, (right_panel.x + 35, right_panel.y + 350))

    controls = [
        "Click a piece to view legal moves.",
        "Click a highlighted square to move.",
        "Press ESC during the game to return here.",
    ]

    for index, line in enumerate(controls):
        text = small_font.render(line, True, MENU_MUTED)
        screen.blit(text, (right_panel.x + 35, right_panel.y + 382 + index * 26))

    if menu_message:
        message_text = small_font.render(menu_message, True, MENU_GREEN)
        screen.blit(message_text, (right_panel.x + 35, right_panel.y + 460))

    start_button = pygame.Rect(right_panel.x + 35, right_panel.y + 472, 410, 58)
    quit_button = pygame.Rect(right_panel.x + 35, right_panel.y + 540, 410, 34)

    draw_button(
        screen,
        start_button,
        "Start Game",
        button_font,
        MENU_GREEN,
        MENU_GREEN_DARK,
        MENU_TEXT,
    )
    draw_button(
        screen,
        quit_button,
        "Quit",
        body_font,
        MENU_PANEL_LIGHT,
        MENU_BORDER,
        MENU_TEXT,
    )

    return {
        "mode": mode_rect,
        "turn": turn_rect,
        "no_timer": no_timer_rect,
        "start": start_button,
        "quit": quit_button,
    }


def draw_game(screen, position, piece_images, coordinate_font, selected_square, legal_moves):
    """Draw the game board."""
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

    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("An Chess Engine - Menu")

    piece_images = load_piece_images()
    logo = load_logo()

    title_font = pygame.font.SysFont("Arial", 38, bold=True)
    heading_font = pygame.font.SysFont("Arial", 34, bold=True)
    body_font = pygame.font.SysFont("Arial", 21, bold=True)
    button_font = pygame.font.SysFont("Arial", 28, bold=True)
    small_font = pygame.font.SysFont("Arial", 18, bold=True)
    coordinate_font = pygame.font.SysFont("Arial", 18, bold=True)
    fonts = (title_font, heading_font, body_font, button_font, small_font)

    position = Position()
    sync_engine_state(position)

    selected_square = None
    legal_moves = []
    screen_mode = "menu"
    selected_time = "No Timer"
    menu_message = ""
    menu_buttons = {}
    running = True

    while running:
        if screen_mode == "menu":
            menu_buttons = draw_menu(screen, logo, fonts, selected_time, menu_message)
            pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if screen_mode == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_buttons.get("start") and menu_buttons["start"].collidepoint(event.pos):
                        screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
                        pygame.display.set_caption("An Chess Engine GUI - White to move")
                        position = Position()
                        sync_engine_state(position)
                        selected_square = None
                        legal_moves = []
                        screen_mode = "game"

                    elif menu_buttons.get("quit") and menu_buttons["quit"].collidepoint(event.pos):
                        running = False

                    elif menu_buttons.get("mode") and menu_buttons["mode"].collidepoint(event.pos):
                        menu_message = "Player vs Player selected."

                    elif menu_buttons.get("turn") and menu_buttons["turn"].collidepoint(event.pos):
                        menu_message = "Standard chess starts with White."

                    elif menu_buttons.get("no_timer") and menu_buttons["no_timer"].collidepoint(event.pos):
                        selected_time = "No Timer"
                        menu_message = "No Timer selected."

            elif screen_mode == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
                    pygame.display.set_caption("An Chess Engine - Menu")
                    selected_square = None
                    legal_moves = []
                    screen_mode = "menu"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicked_square = screen_to_square(event.pos)
                    clicked_piece = get_piece_on_square(position, clicked_square)

                    if clicked_square is None:
                        continue

                    # First click selects one of the current player's pieces.
                    if selected_square is None:
                        if is_current_turn_piece(position, clicked_piece):
                            selected_square = clicked_square
                            legal_moves = calculate_legal_moves(position, selected_square)
                            print(f"Selected {square_to_algebraic(clicked_square)}")
                        else:
                            selected_square = None
                            legal_moves = []
                            print("Select one of your own pieces.")

                    # Second click either changes selection or attempts a move.
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
            draw_game(
                screen,
                position,
                piece_images,
                coordinate_font,
                selected_square,
                legal_moves,
            )
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
