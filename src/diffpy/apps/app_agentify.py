import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_URL = "https://github.com/diffpy/cmi-agent-skills"
DIR_NAME = "cmi-skill"


def agentify(args):
    agent = args.agent
    system_flag = args.system
    if agent == "claude":
        skills_dir = ".claude/skills"
    elif agent == "codex":
        skills_dir = ".codex/skills"
    if system_flag:
        destination = Path().home() / skills_dir / DIR_NAME
    else:
        destination = Path().cwd() / skills_dir / DIR_NAME
    if destination.exists() and not args.update:
        raise FileExistsError(
            f"Agentic skill {DIR_NAME} already exists at {destination}. "
            "To overwrite, pass '--update' flag to update the skill"
        )
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subprocess.run(
            ["git", "clone", REPO_URL, str(tmp_path)],
            check=True,
        )
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(tmp_path / DIR_NAME, destination, dirs_exist_ok=True)
    print(f"Agentic skill {DIR_NAME} has been deployed to {destination}")
