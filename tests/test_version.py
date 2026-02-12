"""Unit tests for __version__.py."""

import diffpy.apps  # noqa


def test_package_version():
    """Ensure the package version is defined and not set to the initial
    placeholder."""
    assert hasattr(diffpy.apps, "__version__")
    assert diffpy.apps.__version__ != "0.0.0"
