import pytest

from pynemail.ui import utils


@pytest.mark.parametrize("height, width, screen_h, screen_w, exp_y, exp_x", [
    (10, 8, 20, 20, 5, 6),
    (20, 60, 25, 80, 2, 10),
])
def test_center_window(height, width, screen_h, screen_w, exp_y, exp_x):
    y, x = utils.center(height, width, screen_h, screen_w)
    assert y == exp_y
    assert x == exp_x


@pytest.mark.parametrize("text, cols, result", [
    ('1234567890', 8, '12345...'),
    ('1234567890', 11, '1234567890 ')
])
def test_fit_text_to_cols(text, cols, result):
    shrunk_text = utils.fit_text_to_cols(text, cols)
    assert result == shrunk_text


@pytest.mark.parametrize("text, cols, result", [
    ('1234567890\n0123456789',   8, ['12345678', '90      ', '01234567', '89      ']),
    ('12 3456789012345',         8, ['12      ', '34567890', '12345   ']),
    ('12345 67890\n01234 56789', 8, ['12345   ', '67890   ', '01234   ', '56789   ']),
    ('12345 67890\n01',          8, ['12345   ', '67890   ', '01      ']),
    ('12345 6\n01',              8, ['12345 6 ', '01      ']),
])
def test_wrap_text_to_cols(text, cols, result):
    wrapped_text = utils.wrap_text_to_cols(text, cols)
    assert len(wrapped_text) == len(result)
    for l_exp, l_act in zip(result, wrapped_text):
        assert l_exp == l_act
