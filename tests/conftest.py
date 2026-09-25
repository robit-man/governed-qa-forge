from pathlib import Path

import pytest

from qaforge.fixtures import scaffold_workspace
from qaforge.workspace import Workspace


@pytest.fixture
def demo_workspace(tmp_path: Path) -> Workspace:
    path = scaffold_workspace(tmp_path / "workspace", demo=True)
    return Workspace(path)
