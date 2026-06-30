import os

import pygame

from anchessengine.constants import Piece
from anchessengine.position import Position


WIDTH = 640
HEIGHT = 640
SQUARE_SIZE = WIDTH // 8

LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
SELECTED_SQUARE = (255, 220, 80)

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

SELECTED_LIGHT_FILL = (70, 140, 230, 160)
SELECTED_DARK_FILL = (70, 140, 230, 100)
SELECTED_BORDER = (20, 20, 20)

def load_piece_images():
    """Load, crop and resize chess piece images."""
    images = {}
    target_size = SQUARE_SIZE - 22

    for key, filename in PIECE_IMAGE_FILES.items():
        path = os.path.join(ASSET_DIR, filename)

        raw_image = pygame.image.load(path).convert_alpha()

        # Crop transparent padding around the actual piece.
        bounding_rect = raw_image.get_bounding_rect()
        cropped_image = raw_image.subsurface(bounding_rect).copy()

        width, height = cropped_image.get_size()
        scale = min(target_size / width, target_size / height)

        new_width = int(width * scale)
        new_height = int(height * scale)

        resized_image = pygame.transform.smoothscale(
            cropped_image,
            (new_width, new_height),
        )

        images[key] = resized_image

    return images

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

    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE

    rank_index = 7 - row
    file_index = col

    return rank_index * 8 + file_index

def get_piece_on_square(position, square):
    """Return the piece on a square, or None if the square is empty."""
    for piece, squares in position.piece_map.items():
        if square in squares:
            return piece

    return None

def square_to_algebraic(square):
    """Convert internal square number to chess notation."""
    files = "abcdefgh"

    file_index = square % 8
    rank_index = square // 8

    return f"{files[file_index]}{rank_index + 1}"



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


def main():
    """Start the graphical chess board."""
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("An Chess Engine GUI")

    piece_images = load_piece_images()
    position = Position()
    selected_square = None

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_square = screen_to_square(event.pos)
                clicked_piece = get_piece_on_square(position, clicked_square)

                if clicked_piece is not None:
                    selected_square = clicked_square
                    print(f"Selected piece on {square_to_algebraic(clicked_square)}")
                else:
                    selected_square = None

        draw_board(screen)
        draw_selected_square(screen, selected_square)
        draw_pieces(screen, position, piece_images)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()