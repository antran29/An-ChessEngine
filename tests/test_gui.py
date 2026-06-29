from anchessengine.gui import get_square_from_screen, square_to_screen


def test_square_to_screen_and_back():
    assert square_to_screen(0) == (0, 560)
    assert square_to_screen(7) == (560, 560)
    assert square_to_screen(56) == (0, 0)
    assert square_to_screen(63) == (560, 0)

    assert get_square_from_screen((0, 560)) == 0
    assert get_square_from_screen((79, 599)) == 0
    assert get_square_from_screen((560, 0)) == 63
