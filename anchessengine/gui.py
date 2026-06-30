import os

import pygame

from anchessengine.constants import Color, Piece
from anchessengine.position import Position


WIDTH = 640
HEIGHT = 640
SQUARE_SIZE = WIDTH // 8

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

MENU_BACKGROUND = (31, 43, 34)
MENU_PANEL = (238, 238, 210)
MENU_TEXT = (20, 20, 20)
MENU_BUTTON = (118, 150, 86)
MENU_BUTTON_HOVER = (98, 130, 72)
MENU_BUTTON_TEXT = (255, 255, 255)

START_BUTTON_RECT = pygame.Rect(190, 315, 260, 58)
QUIT_BUTTON_RECT = pygame.Rect(190, 390, 260, 58)

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


# -------------------------------------------------------------
# Asset loading
# -------------------------------------------------------------

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

        resized_image = pygame.transform.smoothscale(
            cropped_image,
            (int(width * scale), int(height * scale)),
        )
        images[key] = resized_image

    return images


# -------------------------------------------------------------
# Board coordinate helpers
# -------------------------------------------------------------

def square_to_screen(square):
    """Convert internal square number into screen coordinates."""
    file_index = square % 8
    rank_index = square // 8

    x = file_index * SQUARE_SIZE
    y = (7 - rank_index) * SQUARE_SIZE

    return x, y


def screen_to_square(mouse_pos):
    """Convert mouse position into an internal square number."""
    x, y = mouse_pos
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE

    if not 0 <= col < 8 or not 0 <= row < 8:
        return None

    rank_index = 7 - row
    file_index = col

    return rank_index * 8 + file_index


def square_to_algebraic(square):
    """Convert internal square number into algebraic chess notation."""
    files = "abcdefgh"
    return f"{files[square % 8]}{square // 8 + 1}"


def file_of(square):
    return square % 8


def rank_of(square):
    return square // 8


def square_from_file_rank(file_index, rank_index):
    if 0 <= file_index < 8 and 0 <= rank_index < 8:
        return rank_index * 8 + file_index
    return None


# -------------------------------------------------------------
# Piece helpers
# -------------------------------------------------------------

def get_piece_on_square(position, square):
    """Return the piece on a square, or None if the square is empty."""
    if square is None:
        return None

    for piece, squares in position.piece_map.items():
        if square in squares:
            return piece

    return None


def is_white_piece(piece):
    return piece in Piece.white_pieces


def is_black_piece(piece):
    return piece in Piece.black_pieces


def piece_colour(piece):
    if is_white_piece(piece):
        return Color.WHITE
    if is_black_piece(piece):
        return Color.BLACK
    return None


def is_current_turn_piece(position, piece):
    """Return True if the piece belongs to the player whose turn it is."""
    return piece is not None and piece_colour(piece) == position.color_to_move


def is_enemy_piece(piece, target_piece):
    """Return True if target_piece is an opponent piece."""
    if piece is None or target_piece is None:
        return False
    return piece_colour(piece) != piece_colour(target_piece)


def is_own_piece(piece, target_piece):
    """Return True if target_piece belongs to the same player."""
    if piece is None or target_piece is None:
        return False
    return piece_colour(piece) == piece_colour(target_piece)


# -------------------------------------------------------------
# Basic legal move generation
# -------------------------------------------------------------

def add_if_available(position, piece, moves, file_index, rank_index):
    """Add a square if it is on board and not occupied by an own piece."""
    square = square_from_file_rank(file_index, rank_index)
    if square is None:
        return

    target_piece = get_piece_on_square(position, square)
    if not is_own_piece(piece, target_piece):
        moves.append(square)


def sliding_moves(position, piece, from_square, directions):
    """Generate rook, bishop and queen sliding moves with blockers."""
    moves = []
    start_file = file_of(from_square)
    start_rank = rank_of(from_square)

    for file_step, rank_step in directions:
        file_index = start_file + file_step
        rank_index = start_rank + rank_step

        while 0 <= file_index < 8 and 0 <= rank_index < 8:
            square = square_from_file_rank(file_index, rank_index)
            target_piece = get_piece_on_square(position, square)

            if target_piece is None:
                moves.append(square)
            elif is_enemy_piece(piece, target_piece):
                moves.append(square)
                break
            else:
                break

            file_index += file_step
            rank_index += rank_step

    return moves


def pawn_moves(position, piece, from_square):
    """Generate basic pawn moves, captures and two-square starts."""
    moves = []
    start_file = file_of(from_square)
    start_rank = rank_of(from_square)

    if piece == Piece.wP:
        direction = 1
        start_rank_required = 1
        enemy_check = is_black_piece
    elif piece == Piece.bP:
        direction = -1
        start_rank_required = 6
        enemy_check = is_white_piece
    else:
        return moves

    one_forward = square_from_file_rank(start_file, start_rank + direction)
    if one_forward is not None and get_piece_on_square(position, one_forward) is None:
        moves.append(one_forward)

        two_forward = square_from_file_rank(start_file, start_rank + 2 * direction)
        if start_rank == start_rank_required and two_forward is not None:
            if get_piece_on_square(position, two_forward) is None:
                moves.append(two_forward)

    for file_step in (-1, 1):
        capture_square = square_from_file_rank(
            start_file + file_step,
            start_rank + direction,
        )
        target_piece = get_piece_on_square(position, capture_square)

        if target_piece is not None and enemy_check(target_piece):
            moves.append(capture_square)

    return moves


def knight_moves(position, piece, from_square):
    """Generate knight moves from the selected square only."""
    moves = []
    start_file = file_of(from_square)
    start_rank = rank_of(from_square)

    for file_step, rank_step in (
        (1, 2),
        (2, 1),
        (2, -1),
        (1, -2),
        (-1, -2),
        (-2, -1),
        (-2, 1),
        (-1, 2),
    ):
        add_if_available(
            position,
            piece,
            moves,
            start_file + file_step,
            start_rank + rank_step,
        )

    return moves


def king_moves(position, piece, from_square):
    """Generate one-square king moves."""
    moves = []
    start_file = file_of(from_square)
    start_rank = rank_of(from_square)

    for file_step in (-1, 0, 1):
        for rank_step in (-1, 0, 1):
            if file_step == 0 and rank_step == 0:
                continue
            add_if_available(
                position,
                piece,
                moves,
                start_file + file_step,
                start_rank + rank_step,
            )

    return moves


def calculate_legal_moves(position, from_square):
    """Calculate basic legal target squares for the selected piece."""
    piece = get_piece_on_square(position, from_square)

    if not is_current_turn_piece(position, piece):
        return []

    if piece in (Piece.wP, Piece.bP):
        return pawn_moves(position, piece, from_square)

    if piece in (Piece.wN, Piece.bN):
        return knight_moves(position, piece, from_square)

    if piece in (Piece.wB, Piece.bB):
        return sliding_moves(position, piece, from_square, [(1, 1), (-1, 1), (1, -1), (-1, -1)])

    if piece in (Piece.wR, Piece.bR):
        return sliding_moves(position, piece, from_square, [(1, 0), (-1, 0), (0, 1), (0, -1)])

    if piece in (Piece.wQ, Piece.bQ):
        return sliding_moves(
            position,
            piece,
            from_square,
            [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)],
        )

    if piece in (Piece.wK, Piece.bK):
        return king_moves(position, piece, from_square)

    return []


def remove_piece_from_square(position, square):
    """Remove any piece from a square."""
    for piece, squares in position.piece_map.items():
        if square in squares:
            squares.remove(square)
            return piece
    return None


def apply_gui_move(position, from_square, to_square):
    """Apply a GUI move after it has already been checked as legal."""
    piece = get_piece_on_square(position, from_square)
    if piece is None:
        return False

    captured_piece = remove_piece_from_square(position, to_square)
    position.piece_map[piece].remove(from_square)

    # Simple automatic queen promotion for GUI play.
    if piece == Piece.wP and rank_of(to_square) == 7:
        piece = Piece.wQ
    elif piece == Piece.bP and rank_of(to_square) == 0:
        piece = Piece.bQ

    position.piece_map[piece].add(to_square)
    position.mailbox[from_square] = None
    position.mailbox[to_square] = piece

    position.board.update_position_bitboards(position.piece_map)
    position.update_attack_bitboards()
    position.evaluate_king_check()

    position.color_to_move = Color.BLACK if position.color_to_move == Color.WHITE else Color.WHITE

    return captured_piece is not None


# -------------------------------------------------------------
# Drawing helpers
# -------------------------------------------------------------

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
        row = 7
        is_light_square = (row + col) % 2 == 0
        colour = COORDINATE_DARK if is_light_square else COORDINATE_LIGHT
        text = font.render(files[col], True, colour)
        screen.blit(
            text,
            (col * SQUARE_SIZE + SQUARE_SIZE - 16, row * SQUARE_SIZE + SQUARE_SIZE - 20),
        )

    for row in range(8):
        col = 0
        is_light_square = (row + col) % 2 == 0
        colour = COORDINATE_DARK if is_light_square else COORDINATE_LIGHT
        text = font.render(str(8 - row), True, colour)
        screen.blit(text, (col * SQUARE_SIZE + 5, row * SQUARE_SIZE + 4))


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

    pygame.draw.rect(screen, SELECTED_BORDER, pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE), 2)


def draw_legal_moves(screen, legal_moves, position):
    """Highlight legal target squares for the selected piece."""
    for square in legal_moves:
        x, y = square_to_screen(square)
        target_piece = get_piece_on_square(position, square)

        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

        if target_piece is None:
            highlight_surface.fill(LEGAL_MOVE_FILL)
            screen.blit(highlight_surface, (x, y))
            pygame.draw.circle(
                screen,
                LEGAL_MOVE_DOT,
                (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2),
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
    piece_image_map = {
        Piece.wK: "white_king",
        Piece.bK: "black_king",
        Piece.wQ: "white_queen",
        Piece.bQ: "black_queen",
        Piece.wR: "white_rook",
        Piece.bR: "black_rook",
        Piece.wB: "white_bishop",
        Piece.bB: "black_bishop",
        Piece.wN: "white_knight",
        Piece.bN: "black_knight",
        Piece.wP: "white_pawn",
        Piece.bP: "black_pawn",
    }
    key = piece_image_map.get(piece)
    return piece_images.get(key) if key else None


def draw_pieces(screen, position, piece_images):
    """Draw all pieces from the current engine position."""
    for piece, squares in position.piece_map.items():
        image = get_piece_image(piece, piece_images)
        if image is None:
            continue

        for square in squares:
            x, y = square_to_screen(square)
            rect = image.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
            screen.blit(image, rect)


def draw_centered_text(screen, text, font, colour, y):
    rendered = font.render(text, True, colour)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    screen.blit(rendered, rect)


def draw_button(screen, rect, text, font, mouse_pos):
    is_hovered = rect.collidepoint(mouse_pos)
    colour = MENU_BUTTON_HOVER if is_hovered else MENU_BUTTON

    pygame.draw.rect(screen, colour, rect, border_radius=10)
    pygame.draw.rect(screen, MENU_TEXT, rect, 2, border_radius=10)

    rendered = font.render(text, True, MENU_BUTTON_TEXT)
    text_rect = rendered.get_rect(center=rect.center)
    screen.blit(rendered, text_rect)


def draw_menu(screen, fonts):
    """Draw the lobby/menu screen before the game starts."""
    mouse_pos = pygame.mouse.get_pos()
    screen.fill(MENU_BACKGROUND)

    panel = pygame.Rect(70, 70, 500, 500)
    pygame.draw.rect(screen, MENU_PANEL, panel, border_radius=20)
    pygame.draw.rect(screen, MENU_TEXT, panel, 3, border_radius=20)

    draw_centered_text(screen, "An Chess Engine", fonts["title"], MENU_TEXT, 150)
    draw_centered_text(screen, "Pygame GUI Edition", fonts["subtitle"], MENU_TEXT, 205)
    draw_centered_text(screen, "Click a piece to preview moves, then click a target square.", fonts["small"], MENU_TEXT, 260)

    draw_button(screen, START_BUTTON_RECT, "Start Game", fonts["button"], mouse_pos)
    draw_button(screen, QUIT_BUTTON_RECT, "Quit", fonts["button"], mouse_pos)

    draw_centered_text(screen, "Current feature: local two-player chess board", fonts["small"], MENU_TEXT, 505)


def draw_game(screen, position, piece_images, coordinate_font, selected_square, legal_moves):
    draw_board(screen)
    draw_legal_moves(screen, legal_moves, position)
    draw_selected_square(screen, selected_square)
    draw_pieces(screen, position, piece_images)
    draw_coordinates(screen, coordinate_font)


# -------------------------------------------------------------
# Main application
# -------------------------------------------------------------

def main():
    """Start the chess GUI with a lobby/menu screen."""
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("An Chess Engine GUI")

    fonts = {
        "title": pygame.font.SysFont("Arial", 46, bold=True),
        "subtitle": pygame.font.SysFont("Arial", 28, bold=True),
        "button": pygame.font.SysFont("Arial", 26, bold=True),
        "small": pygame.font.SysFont("Arial", 18),
    }
    coordinate_font = pygame.font.SysFont("Arial", 18, bold=True)

    piece_images = load_piece_images()
    position = Position()
    position.board.update_position_bitboards(position.piece_map)
    position.update_attack_bitboards()
    position.evaluate_king_check()

    selected_square = None
    legal_moves = []
    current_screen = "menu"
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_screen == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
                if START_BUTTON_RECT.collidepoint(event.pos):
                    current_screen = "game"
                elif QUIT_BUTTON_RECT.collidepoint(event.pos):
                    running = False

            elif current_screen == "game" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_screen = "menu"
                    selected_square = None
                    legal_moves = []

            elif current_screen == "game" and event.type == pygame.MOUSEBUTTONDOWN:
                clicked_square = screen_to_square(event.pos)
                clicked_piece = get_piece_on_square(position, clicked_square)

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
                    selected_piece = get_piece_on_square(position, selected_square)

                    if selected_piece is None:
                        selected_square = None
                        legal_moves = []

                    elif clicked_square == selected_square:
                        selected_square = None
                        legal_moves = []

                    elif is_current_turn_piece(position, clicked_piece):
                        selected_square = clicked_square
                        legal_moves = calculate_legal_moves(position, selected_square)
                        print(f"Selected {square_to_algebraic(clicked_square)}")

                    elif clicked_square in legal_moves:
                        from_label = square_to_algebraic(selected_square)
                        to_label = square_to_algebraic(clicked_square)
                        apply_gui_move(position, selected_square, clicked_square)
                        print(f"Moved {from_label}{to_label}")
                        selected_square = None
                        legal_moves = []

                    else:
                        print(
                            f"Illegal move: "
                            f"{square_to_algebraic(selected_square)}"
                            f"{square_to_algebraic(clicked_square)}"
                        )
                        selected_square = None
                        legal_moves = []

        if current_screen == "menu":
            draw_menu(screen, fonts)
        else:
            draw_game(screen, position, piece_images, coordinate_font, selected_square, legal_moves)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
