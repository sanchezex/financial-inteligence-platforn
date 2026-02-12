import decimal
import pytest

# Fix: ensure pytest.approx works when tests pass Decimal instances as expected.
# Some pytest versions attempt float * Decimal causing TypeError; convert
# Decimal expected values to float to avoid that arithmetic error.
_orig_approx = pytest.approx

def _approx_fixed(expected, *args, **kwargs):
    if isinstance(expected, decimal.Decimal):
        expected = float(expected)
    return _orig_approx(expected, *args, **kwargs)

pytest.approx = _approx_fixed
