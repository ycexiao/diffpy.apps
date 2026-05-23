import json
import shutil
import socket
from pathlib import Path

import pytest


@pytest.fixture
def user_filesystem(tmp_path):
    base_dir = Path(tmp_path)
    home_dir = base_dir / "home_dir"
    home_dir.mkdir(parents=True, exist_ok=True)
    cwd_dir = base_dir / "cwd_dir"
    cwd_dir.mkdir(parents=True, exist_ok=True)

    home_config_data = {"username": "home_username", "email": "home@email.com"}
    with open(home_dir / "diffpyconfig.json", "w") as f:
        json.dump(home_config_data, f)

    yield tmp_path


def internet_available():
    try:
        socket.create_connection(("github.com", 443), timeout=3)
        return True
    except OSError:
        return False


git_available = shutil.which("git") is not None
AGENTIFY_AVAILABLE = internet_available() and git_available
