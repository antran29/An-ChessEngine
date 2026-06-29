import pygame

from anchessengine.constants import Piece, piece_to_glyph
from anchessengine.position import Position


WIDTH = 640
HEIGHT = 640
SQUARE_SIZE = WIDTH // 8

LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)

WHITE_PIECE = (245, 245, 245)
BLACK_PIECE = (40, 40, 40)
OUTLINE = (20, 20, 20)


def square_to_screen(square):
    """Convert internal square number into a screen position."""
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


def get_piece_colour(piece):
    """Return white or black colour depending on the piece."""
    if piece in Piece.white_pieces:
        return WHITE_PIECE

    return BLACK_PIECE


def draw_pieces(screen, font, position):
    """Draw all pieces from the current engine position."""
    for piece, squares in position.piece_map.items():
        glyph = piece_to_glyph.get(piece)

        if not glyph:
            continue

        for square in squares:
            x, y = square_to_screen(square)

            piece_colour = get_piece_colour(piece)

            # Small outline so white pieces show clearly.
            outline_text = font.render(glyph, True, OUTLINE)
            piece_text = font.render(glyph, True, piece_colour)

            rect = piece_text.get_rect(
                center=(
                    x + SQUARE_SIZE // 2,
                    y + SQUARE_SIZE // 2,
                )
            )

            if piece in Piece.white_pieces:
                for offset_x, offset_y in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    outline_rect = rect.move(offset_x, offset_y)
                    screen.blit(outline_text, outline_rect)

            screen.blit(piece_text, rect)


def main():
    """Start the graphical chess board."""
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("An Chess Engine GUI")

    font = pygame.font.SysFont("Segoe UI Symbol", 64)

    position = Position()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_board(screen)
        draw_pieces(screen, font, position)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()