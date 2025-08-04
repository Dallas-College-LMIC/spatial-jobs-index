"""Test that handle_internal_error function exists."""


def test_handle_internal_error_function_exists():
    """Test that we can import handle_internal_error function from main module."""
    from app.main import handle_internal_error

    assert handle_internal_error is not None
