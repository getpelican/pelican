import os
from pathlib import Path
from shutil import which

from invoke import task

PKG_NAME = "pelican"
PKG_PATH = Path("pelican")
ACTIVE_VENV = os.environ.get("VIRTUAL_ENV", None)
VENV_HOME = Path(os.environ.get("WORKON_HOME", "~/virtualenvs"))
VENV_PATH = Path(ACTIVE_VENV) if ACTIVE_VENV else (VENV_HOME / PKG_NAME)
VENV = str(VENV_PATH.expanduser())

TOOLS = ["poetry", "pre-commit"]
POETRY = which("poetry") if which("poetry") else (VENV / Path("bin") / "poetry")
PRECOMMIT = (
    which("pre-commit") if which("pre-commit") else (VENV / Path("bin") / "pre-commit")
)


@task
def tests(c):
    """Run the test suite"""
    c.run(f"{VENV}/bin/pytest", pty=True)


@task
def black(c, check=False, diff=False):
    """Run Black auto-formatter, optionally with --check or --diff"""
    check_flag, diff_flag = "", ""
    if check:
        check_flag = "--check"
    if diff:
        diff_flag = "--diff"
    c.run(f"{VENV}/bin/black {check_flag} {diff_flag} {PKG_PATH} tasks.py")


@task
def isort(c, check=False, diff=False):
    check_flag, diff_flag = "", ""
    if check:
        check_flag = "-c"
    if diff:
        diff_flag = "--diff"
    c.run(
        f"{VENV}/bin/isort {check_flag} {diff_flag} --recursive {PKG_PATH}/* tasks.py"
    )


@task
def flake8(c):
    c.run(f"{VENV}/bin/flake8 {PKG_PATH} tasks.py")


@task
def lint(c):
    isort(c, check=True)
    black(c, check=True)
    flake8(c)


@task
def tools(c):
    """Install tools in the virtual environment if not already on PATH"""
    for tool in TOOLS:
        if not which(tool):
            c.run(f"{VENV}/bin/pip install {tool}")


@task
def precommit(c):
    """Install pre-commit hooks to .git/hooks/pre-commit"""
    c.run(f"{PRECOMMIT} install")


@task
def setup(c):
    c.run(f"{VENV}/bin/pip install -U pip")
    tools(c)
    c.run(f"{POETRY} install")
    precommit(c)
