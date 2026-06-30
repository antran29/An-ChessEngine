import os

import pygame

from anchessengine.constants import Piece
from anchessengine.position import Position


WIDTH = 640
HEIGHT = 640
SQUARE_SIZE = WIDTH // 8

LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)

ASSET_DIR = os.path.join("assets", "pieces")

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


def load_piece_images():
    """Load and resize chess piece images."""
    images = {}

    for key, filename in PIECE_IMAGE_FILES.items():
        path = os.path.join(ASSET_DIR, filename)
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.smoothscale(
            image,
            (SQUARE_SIZE - 10, SQUARE_SIZE - 10),
        )
        images[key] = image

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


def get_piece_image(piece, piece_images):
    """Return the correct image for a chess piece."""
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

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_board(screen)
        draw_pieces(screen, position, piece_images)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()