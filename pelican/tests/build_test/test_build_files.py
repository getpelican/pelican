import importlib.metadata
import tarfile
from pathlib import Path
from re import match
from zipfile import ZipFile

import pytest

version = importlib.metadata.version("pelican")


@pytest.mark.skipif(
    "not config.getoption('--check-build')",
    reason="Only run when --check-build is given",
)
def test_wheel_contents(pytestconfig):
    """
    This test should test the contents of the wheel to make sure
    that everything that is needed is included in the final build
    """
    dist_folder = pytestconfig.getoption("--check-build")
    wheels = Path(dist_folder).rglob(f"pelican-{version}-py3-none-any.whl")
    for wheel_file in wheels:
        files_list = ZipFile(wheel_file).namelist()
        # Check if theme files are copied to wheel
        simple_theme = Path("./pelican/themes/simple/templates")
        for x in simple_theme.iterdir():
            assert str(x) in files_list

        # Check if tool templates are copied to wheel
        tools = Path("./pelican/tools/templates")
        for x in tools.iterdir():
            assert str(x) in files_list

        assert "pelican/tools/templates/tasks.py.jinja2" in files_list


@pytest.mark.skipif(
    "not config.getoption('--check-build')",
    reason="Only run when --check-build is given",
)
@pytest.mark.parametrize(
    "expected_file",
    [
        ("THANKS"),
        ("README.rst"),
        ("CONTRIBUTING.rst"),
        ("docs/changelog.rst"),
        ("samples/"),
    ],
)
def test_sdist_contents(pytestconfig, expected_file):
    """
    This test should test the contents of the source distribution to make sure
    that everything that is needed is included in the final build.
    """
    dist_folder = pytestconfig.getoption("--check-build")
    sdist_files = Path(dist_folder).rglob(f"pelican-{version}.tar.gz")
    for dist in sdist_files:
        files_list = tarfile.open(dist, "r:gz").getnames()
        dir_matcher = ""
        if expected_file.endswith("/"):
            dir_matcher = ".*"
        filtered_values = [
            path
            for path in files_list
            if match(rf"^pelican-{version}/{expected_file}{dir_matcher}$", path)
        ]
        assert len(filtered_values) > 0
