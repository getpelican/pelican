from pathlib import Path
import pytest
from zipfile import ZipFile


@pytest.mark.skipif(
    "not config.getoption('--check-wheel')",
    reason="Only run when --check-wheel is given",
)
def test_wheel_contents(pytestconfig):
    """
    This test, should test the contents of the wheel to make sure,
    that everything that is needed is included in the final build
    """
    wheel_file = pytestconfig.getoption("--check-wheel")
    assert wheel_file.endswith(".whl")
    files_list = ZipFile(wheel_file).namelist()
    ## Check is theme files are copiedto wheel
    simple_theme = Path("./pelican/themes/simple/templates")
    for x in simple_theme.iterdir():
        assert str(x) in files_list

    ## Check is tool templatesare copiedto wheel
    tools = Path("./pelican/tools/templates")
    for x in tools.iterdir():
        assert str(x) in files_list

    assert "pelican/tools/templates/tasks.py.jinja2" in files_list
