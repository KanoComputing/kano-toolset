# test_hardware.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the kano.utils.hardware module


def test_board_property(board, board_property):
    from kano.utils.hardware import get_board_property

    prop_val = get_board_property(board.key, board_property.property)

    if board.is_valid:
        if board_property.is_valid:
            assert prop_val == getattr(board, board_property.property)
        else:
            assert prop_val is None
    else:
        assert prop_val is None


def test_detect_kano_keyboard_type(keyboard):
    from kano.utils.hardware import detect_kano_keyboard_type
    assert detect_kano_keyboard_type() == keyboard


def test_detect_kano_keyboard(keyboard):
    from kano.utils.hardware import detect_kano_keyboard
    if keyboard:
        assert detect_kano_keyboard()
    else:
        assert not detect_kano_keyboard()


def is_revision_valid(rev):
    try:
        int(rev, 16)
        return True
    except ValueError:
        # Not a hex value
        return False


def test_is_model_a(cpu):
    from kano.utils.hardware import is_model_a, RPI_A_PLUS_KEY

    assert (
        is_model_a(use_cached=False) ==
        (cpu.platform_key == RPI_A_PLUS_KEY)
    )


def test_is_model_a_w_revision(cpu):
    from kano.utils.hardware import is_model_a, RPI_A_PLUS_KEY

    assert (
        is_model_a(revision=cpu.revision, use_cached=False) ==
        (cpu.platform_key == RPI_A_PLUS_KEY)
    )


def test_is_model_b(cpu):
    from kano.utils.hardware import is_model_b, RPI_B_KEY

    assert (
        is_model_b(use_cached=False) ==
        (cpu.platform_key == RPI_B_KEY)
    )


def test_is_model_b_w_revision(cpu):
    from kano.utils.hardware import is_model_b, RPI_B_KEY

    assert (
        is_model_b(revision=cpu.revision, use_cached=False) ==
        (cpu.platform_key == RPI_B_KEY)
    )


def test_is_model_b_plus(cpu):
    from kano.utils.hardware import is_model_b_plus, RPI_B_PLUS_KEY

    assert (
        is_model_b_plus(use_cached=False) ==
        (cpu.platform_key == RPI_B_PLUS_KEY)
    )


def test_is_model_b_plus_w_revision(cpu):
    from kano.utils.hardware import is_model_b_plus, RPI_B_PLUS_KEY

    assert (
        is_model_b_plus(revision=cpu.revision, use_cached=False) ==
        (cpu.platform_key == RPI_B_PLUS_KEY)
    )


def test_is_model_2_b(cpu):
    from kano.utils.hardware import is_model_2_b, RPI_2_B_KEY

    assert (
        is_model_2_b(use_cached=False) ==
        (cpu.platform_key == RPI_2_B_KEY)
    )


def test_is_model_2_b_w_revision(cpu):
    from kano.utils.hardware import is_model_2_b, RPI_2_B_KEY

    assert (
        is_model_2_b(revision=cpu.revision, use_cached=False) ==
        (cpu.platform_key == RPI_2_B_KEY)
    )


def test_is_model_zero(cpu):
    from kano.utils.hardware import is_model_zero, RPI_ZERO_KEY

    assert (
        is_model_zero(use_cached=False) ==
        (cpu.platform_key == RPI_ZERO_KEY)
    )


def test_is_model_zero_w_revision(cpu):
    from kano.utils.hardware import is_model_zero, RPI_ZERO_KEY

    assert (
        is_model_zero(revision=cpu.revision, use_cached=False) ==
        (cpu.platform_key == RPI_ZERO_KEY)
    )


def test_is_model_zero_w(cpu):
    from kano.utils.hardware import is_model_zero_w, RPI_ZERO_W_KEY

    assert (
        is_model_zero_w(use_cached=False) ==
        (cpu.platform_key == RPI_ZERO_W_KEY)
    )


def test_is_model_zero_w_w_revision(cpu):
    from kano.utils.hardware import is_model_zero_w, RPI_ZERO_W_KEY

    assert (
        is_model_zero_w(revision=cpu.revision, use_cached=False) ==
        (cpu.platform_key == RPI_ZERO_W_KEY)
    )


def test_get_rpi_model(cpu):
    from kano.utils.hardware import get_rpi_model

    if is_revision_valid(cpu.revision):
        assert (
            get_rpi_model(use_cached=False) ==
            cpu.platform_key
        )
    else:
        assert (
            get_rpi_model(use_cached=False) ==
            'unknown revision: {}'.format(cpu.revision).strip()
        )


def test_get_rpi_model_w_revision(cpu):
    from kano.utils.hardware import get_rpi_model

    if not cpu.revision:
        return  # Same case as above

    if is_revision_valid(cpu.revision):
        assert (
            get_rpi_model(revision=cpu.revision, use_cached=False) ==
            cpu.platform_key
        )
    else:
        assert (
            get_rpi_model(revision=cpu.revision, use_cached=False) ==
            'unknown revision: {}'.format(cpu.revision).strip()
        )


def test_get_cpu_id(cpu):
    from kano.utils.hardware import get_cpu_id

    assert get_cpu_id() == cpu.serial
