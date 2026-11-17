import subprocess
import sys
import textwrap
from importlib.metadata import version

import openvisionauto


def test_version_is_exported():
    assert isinstance(openvisionauto.__version__, str)
    assert openvisionauto.__version__
    assert "__version__" in openvisionauto.__all__


def test_version_matches_installed_distribution():
    assert openvisionauto.__version__ == version("openvisionauto")


def test_version_falls_back_when_distribution_is_missing():
    # Reloading the module in-process would swap sys.modules and break the
    # monkeypatches other tests rely on, so probe the fallback in a subprocess.
    script = textwrap.dedent(
        """
        import importlib.metadata

        def _missing(name):
            raise importlib.metadata.PackageNotFoundError(name)

        importlib.metadata.version = _missing

        import openvisionauto

        print(openvisionauto.__version__)
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "0.0.0"