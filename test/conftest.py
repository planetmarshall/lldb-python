import os
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

import pytest

@pytest.fixture(scope="session")
def executable() -> str:
    with TemporaryDirectory() as tmpdir:
        build_dir = Path(tmpdir) / "build"
        current_dir = os.path.dirname(__file__)
        run(["cmake", "-S", current_dir, "-B", build_dir, "-DCMAKE_BUILD_TYPE=Debug"], check=True)
        run(["cmake", "--build", build_dir], check=True)

        yield str(build_dir / "lldb-python-test")
