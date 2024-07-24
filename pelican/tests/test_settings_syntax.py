#
#  Focused on settings.py/load_source(), specifically syntax error handling
#
# Minimum version: Python 3.8
# Minimum version: Pytest 4.0, Python 3.8+
#
# To see collection/ordering of a fixture for a specific function, execute:
#
#  pytest -n0 --setup-plan \
#  test_settings_syntax.py::TestSettingsSyntax::test_load_source_syntax_indent


import errno
import inspect
import logging
import os
import shutil
import sys
from pathlib import Path

import pytest

from pelican.settings import load_source

# Valid Python file extension
EXT_PYTHON = ".py"
EXT_PYTHON_DISABLED = ".disabled"

# PC_ = Pelican Configuration or PELICANCONF or pelicanconf
# FILENAME_: file name without the extension
PC_FILENAME_DEFAULT = "pelicanconf"
PC_FILENAME_INDENT1_ERROR = "pelicanconf-indent1-error"
PC_FILENAME_INDENT2_ERROR = "pelicanconf-indent2-error"
PC_FILENAME_SYNTAX3_ERROR = "pelicanconf-syntax3-error"
PC_FILENAME_SYNTAX4_ERROR = "pelicanconf-syntax4-error"

# MODNAME_ = Module name
PC_MODNAME_DEFAULT = "pelicanconf"  # used if module_name is blank
PC_MODNAME_INDENT1_ERROR = "pelicanconf-indent1-error"  # PyPA error: no ending digit
PC_MODNAME_INDENT2_ERROR = "pelicanconf-indent2-error"  # PyPA error: no ending digit
PC_MODNAME_SYNTAX3_ERROR = "pelicanconf-syntax3-error"  # PyPA error: no ending digit
PC_MODNAME_SYNTAX4_ERROR = "pelicanconf-syntax4-error"  # PyPA error: no ending digit
PC_MODNAME_SYS_BUILTIN = "calendar"

# Iterators, for fixtures
PC_MODULES_EXPECTED = {PC_MODNAME_SYS_BUILTIN}
PC_MODULES_TEST = {
    PC_MODNAME_DEFAULT,
    PC_MODNAME_INDENT1_ERROR,
    PC_MODNAME_INDENT2_ERROR,
    PC_MODNAME_SYNTAX3_ERROR,
    PC_MODNAME_SYNTAX4_ERROR,
}

# FULLNAME_: filename + extension
PC_FULLNAME_INDENT1_ERROR: str = PC_FILENAME_INDENT1_ERROR + EXT_PYTHON
PC_FULLNAME_INDENT2_ERROR: str = PC_FILENAME_INDENT2_ERROR + EXT_PYTHON
PC_FULLNAME_SYNTAX3_ERROR: str = PC_FILENAME_SYNTAX3_ERROR + EXT_PYTHON
PC_FULLNAME_SYNTAX4_ERROR: str = PC_FILENAME_SYNTAX4_ERROR + EXT_PYTHON
# BLOB_: a file trying to hide from ruff/black syntax checkers for our syntax tests
BLOB_FULLNAME_INDENT1_ERROR = PC_FULLNAME_INDENT1_ERROR + EXT_PYTHON_DISABLED
BLOB_FULLNAME_INDENT2_ERROR = PC_FULLNAME_INDENT2_ERROR + EXT_PYTHON_DISABLED
BLOB_FULLNAME_SYNTAX3_ERROR = PC_FULLNAME_SYNTAX3_ERROR + EXT_PYTHON_DISABLED
BLOB_FULLNAME_SYNTAX4_ERROR = PC_FULLNAME_SYNTAX4_ERROR + EXT_PYTHON_DISABLED

# SyntaxError placement for use with settings/pelicanconf-syntax-error.py
SM_UT_SYNTAX_INDENT1_LINENO = 10  # tests/settings/pelicanconf-indent-error1.py.disabled
SM_UT_SYNTAX_INDENT1_OFFSET = 7  # tests/settings/pelicanconf-indent-error1.py.disabled
SM_UT_SYNTAX_INDENT2_LINENO = 5  # tests/settings/pelicanconf-indent-error2.py.disabled
SM_UT_SYNTAX_INDENT2_OFFSET = 1  # tests/settings/pelicanconf-indent-error2.py.disabled
SM_UT_SYNTAX_ERROR3_LINENO = 9  # tests/settings/pelicanconf-syntax-error3.py.disabled
SM_UT_SYNTAX_ERROR3_OFFSET = 30  # tests/settings/pelicanconf-syntax-error3.py.disabled
SM_UT_SYNTAX_ERROR4_LINENO = 13  # tests/settings/pelicanconf-syntax-error4.py.disabled
SM_UT_SYNTAX_ERROR4_OFFSET = 10  # tests/settings/pelicanconf-syntax-error4.py.disabled

load_source_argument_list_count = 2

# Code starts here
# logging.basicConfig(level=0)
# log = logging.getLogger(__name__)
# logging.root.setLevel(logging.DEBUG)
# log.propagate = True

args = inspect.getfullargspec(load_source)
if ("name" not in args.args) and (args.args.__len__ != load_source_argument_list_count):
    # Skip this entire test file if load_source() only supports 1 argument
    pytest.mark.skip(
        "this class is only used with load_source() having "
        "support for a 'name' argument"
    )

# We need an existing Python system built-in module for testing load_source.
if PC_MODNAME_SYS_BUILTIN not in sys.modules:
    pytest.exit(
        errno.EACCES,
        "PC_MODNAME_SYS_BUILTIN variable MUST BE an existing system "
        "builtin module; this test is aborted",
    )

# Oppositional, PC_MODNAME_DEFAULT must NOT be a pre-existing system built-in module
if PC_MODNAME_DEFAULT in sys.modules:
    # We are not authorized to tamper outside our test area
    pytest.exit(
        errno.EACCES,
        f" Cannot reuses a system built-in module {PC_MODNAME_DEFAULT};"
        " this test is aborted",
    )


##########################################################################
#  module-based fixtures
#  (session-based fixtures resides in `conftest.py` file.)
##########################################################################
@pytest.fixture(scope="module")
def cwd_inside_tests_dir__fixture_module(get_tests_dir__fixture_session):
    """Work inside the `tests/` directory

    This pytest module-wide fixture will change the current working directory
    to the `pelican/pelican/tests` directory, run the unit test, then return
    back to its original directory.

    This fixture gets evoked exactly once (file-wide) due to `scope=module`.

    :return: Returns the path of the `tests/` directory
    :rtype: pathlib.Path"""
    tests_dir_path = get_tests_dir__fixture_session
    original_cwd = os.getcwd()
    os.chdir(tests_dir_path)

    yield Path(tests_dir_path)

    os.chdir(original_cwd)


@pytest.fixture(scope="module")
def cwd_inside_tests_settings_dir__fixture_module(
    get_tests_settings_dir__fixture_session,
):
    """Work inside the `tests/settings` directory

    This pytest module-wide fixture will change the current working directory
    to the `pelican/pelican/tests/settings` directory, run the unit test, then return
    back to its original directory.

    This fixture gets evoked exactly once (per-file) due to `scope=module`.

    :return: Returns the absolute path of the `tests/settings` directory
    :rtype: pathlib.Path"""
    tests_settings_dir_path = get_tests_settings_dir__fixture_session
    original_cwd = os.getcwd()
    os.chdir(tests_settings_dir_path)

    yield Path(tests_settings_dir_path)

    os.chdir(original_cwd)


@pytest.fixture(scope="module")
def cwd_inside_pelican_source_dir__fixture_module(
    get_pelican_source_dir__fixture_session,
):
    """Work inside the Pelican source directory

    This pytest module-wide fixture will change the current working directory
    to the Pelican source directory, run the unit test, then return back to its
    original directory.

    This fixture gets evoked exactly once (file-wide) due to `scope=module`.

    :return: Returns the Path of the Pelican source directory
    :rtype: pathlib.Path"""
    pelican_source_dir_path = get_pelican_source_dir__fixture_session
    original_cwd = os.getcwd()
    os.chdir(pelican_source_dir_path)

    yield Path(pelican_source_dir_path)

    os.chdir(original_cwd)


@pytest.fixture(scope="module")
def cwd_inside_pelican_package_dir__fixture_module(
    get_pelican_package_dir__fixture_session,
):
    """Work inside the Pelican package root directory

    This pytest module-wide fixture will change the current working directory
    to the Pelican root directory, run the unit test, then return back to its
    original directory.

    This fixture gets evoked exactly once (file-wide) due to `scope=module`.

    :return: Returns the Path of the Pelican root directory
    :rtype: pathlib.Path"""
    pelican_package_dir_path = get_pelican_package_dir__fixture_session
    original_cwd = os.getcwd()
    os.chdir(pelican_package_dir_path)

    yield Path(pelican_package_dir_path)

    os.chdir(original_cwd)


@pytest.fixture(scope="module")
def cwd_inside_pelican_pkg_dir_rel_path_fixture_module(get_tests_dir__fixture_session):
    """Change to Pelican package root directory

    This pytest module-wide fixture will change the current working directory
    to the Pelican root directory, run the unit test, then return back to its
    original directory.

    This fixture gets evoked exactly once (file-wide) due to `scope=module`.

    :return: Returns the Path of the relative Pelican root directory (always ".")
    :rtype: pathlib.Path"""
    test_abs_dirpath: Path = Path(__file__).parent  # secret sauce
    pelican_source_subdir_path = test_abs_dirpath.parent
    pelican_package_dir_path = pelican_source_subdir_path.parent
    original_cwd = os.getcwd()
    os.chdir(pelican_package_dir_path)

    yield Path(".")

    os.chdir(original_cwd)


##########################################################################
#  module-specific (test_settings_syntax.py) functions
##########################################################################
def expected_in_sys_modules(module_name: str) -> bool:
    if module_name in sys.modules:
        return True
    raise AssertionError(f"Module {module_name} no longer is in sys.modules[].")


def not_expected_in_sys_modules(module_name: str) -> bool:
    if module_name not in sys.modules:
        return True
    raise AssertionError(f"Module {module_name} unexpectedly now in sys.modules[].")


def check_module_integrity():
    # Check if any modules were left behind by previous unit test(s).
    for not_expected_module in PC_MODULES_TEST:
        not_expected_in_sys_modules(not_expected_module)

    # Now check that we did not lose any critical/built-in module.
    for expected_module in PC_MODULES_EXPECTED:
        expected_in_sys_modules(expected_module)


##########################################################################
#  All about the handling of module name
##########################################################################
class TestSettingsSyntax:
    """load_source() with focus on Syntax Handling"""

    ##########################################################################
    #  Per-class fixtures with focus on module name
    ##########################################################################

    ##########################################################################
    #  Function-specific (per unit test) fixtures with focus on module name
    ##########################################################################
    @pytest.fixture(scope="function", autouse=True)
    def inject_fixtures(self, caplog):
        """Save the console output by logger"""
        self._caplog = caplog

    @pytest.fixture(scope="function")
    def assert_module_integrity__fixture_func(
        self,
        serialize_sys_modules__fixture_session,
        assert_module_integrity__fixture_session,
    ):
        """Check for integrity of `sys.modules[]` thoroughly"""
        check_module_integrity()
        yield
        check_module_integrity()

    @pytest.fixture(scope="function")
    def cwd_inside_tempdir__fixture_func(
        self, temp_dir_all_unit_tests__fixture_session
    ):
        """Work inside the temporary directory"""
        tmp_dir = temp_dir_all_unit_tests__fixture_session
        original_cwd = os.getcwd()
        os.chdir(tmp_dir)

        yield tmp_dir

        os.chdir(original_cwd)

    ##########################################################################
    #  Test cases with focus on IndentationError syntax handling of Python file
    ##########################################################################
    def test_load_source_module_str_abs_indent1_error_tempdir_fail(
        self,
        cwd_inside_tempdir__fixture_func,
        get_tests_settings_dir__fixture_session,
        assert_module_integrity__fixture_func,
        locale_to_c__fixture_session,
    ):
        """syntax error; absolute path, str type; passing mode"""
        default_module = PC_MODNAME_INDENT1_ERROR
        not_expected_in_sys_modules(default_module)
        settings_data_dir: Path = get_tests_settings_dir__fixture_session
        blob: Path = settings_data_dir / BLOB_FULLNAME_INDENT1_ERROR
        tmp_dir_abs_path: Path = cwd_inside_tempdir__fixture_func
        indent_error_file: Path = tmp_dir_abs_path / PC_FULLNAME_INDENT1_ERROR
        # despite tempdir, check if file does NOT exist
        if indent_error_file.exists():
            # Bad test setup, assert out
            raise AssertionError(
                f"File {indent_error_file!s} should not exist in tempdir."
            )
        # Copy mangled pseudo-Python file into temporary absolute area as a Python file
        shutil.copyfile(blob, indent_error_file)

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()
            with pytest.raises(IndentationError) as sample:
                # ignore return value due to sys.exit()
                load_source(default_module, str(indent_error_file))
            assert sample.type == IndentationError
        # TODO Issue #09005 - say something to the end-user exactly where syntax err is
        # assert "unexpected indent" in self._caplog.text

        # Cleanup
        if expected_in_sys_modules(default_module):
            del sys.modules[default_module]
        indent_error_file.unlink(missing_ok=False)

    def test_load_source_module_str_abs_indent1_error_pkg_dir_fail(
        self,
        cwd_inside_pelican_package_dir__fixture_module,
        get_tests_settings_dir__fixture_session,
        assert_module_integrity__fixture_func,
        locale_to_c__fixture_session,
    ):
        """yntax error; absolute path, str type; passing mode"""
        default_module = PC_MODNAME_INDENT1_ERROR
        not_expected_in_sys_modules(default_module)
        settings_data_dir: Path = get_tests_settings_dir__fixture_session
        blob: Path = settings_data_dir / BLOB_FULLNAME_INDENT1_ERROR
        cwd_path: Path = cwd_inside_pelican_package_dir__fixture_module
        indent_error_file: Path = cwd_path / PC_FULLNAME_INDENT1_ERROR
        # despite tempdir, check if file does NOT exist
        if indent_error_file.exists():
            # Bad test setup, assert out
            raise AssertionError(
                f"File {indent_error_file!s} should not exist in tempdir."
            )
        # Copy mangled pseudo-Python file into temporary absolute area as a Python file
        shutil.copyfile(blob, indent_error_file)

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()
            with pytest.raises(IndentationError) as sample:
                # ignore return value due to sys.exit()
                load_source(default_module, str(indent_error_file))
            assert sample.type == IndentationError
        # TODO Issue #09005 - say something to the end-user exactly where syntax err is
        # assert "unexpected indent" in self._caplog.text

        # Cleanup
        if expected_in_sys_modules(default_module):
            del sys.modules[default_module]
        indent_error_file.unlink(missing_ok=False)

    def test_load_source_module_str_abs_indent1_error_src_dir_fail(
        self,
        cwd_inside_pelican_source_dir__fixture_module,
        get_tests_settings_dir__fixture_session,
        assert_module_integrity__fixture_func,
        locale_to_c__fixture_session,
    ):
        """syntax error; absolute path, str type; passing mode"""
        default_module = PC_MODNAME_INDENT1_ERROR
        not_expected_in_sys_modules(default_module)
        settings_data_dir = get_tests_settings_dir__fixture_session
        blob: Path = settings_data_dir / BLOB_FULLNAME_INDENT1_ERROR
        cwd_path: Path = cwd_inside_pelican_source_dir__fixture_module
        indent_error_file: Path = cwd_path / PC_FULLNAME_INDENT1_ERROR
        # despite tempdir, check if file does NOT exist
        if indent_error_file.exists():
            # Bad test setup, assert out
            raise AssertionError(
                f"File {indent_error_file!s} should not exist in tempdir."
            )
        # Copy mangled pseudo-Python file into temporary absolute area as a Python file
        shutil.copyfile(blob, indent_error_file)

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()
            with pytest.raises(IndentationError) as sample:
                # ignore return value due to sys.exit()
                load_source(default_module, str(indent_error_file))
            assert sample.type == IndentationError
        # TODO Issue #09005 - say something to the end-user exactly where syntax err is
        # assert "unexpected indent" in self._caplog.text

        # Cleanup
        if expected_in_sys_modules(default_module):
            del sys.modules[default_module]
        indent_error_file.unlink(missing_ok=False)

    def test_load_source_module_str_abs_indent1_error_tests_dir_fail(
        self,
        cwd_inside_tests_dir__fixture_module,
        get_tests_settings_dir__fixture_session,
        assert_module_integrity__fixture_func,
        locale_to_c__fixture_session,
    ):
        """syntax error; absolute path, str type; passing mode"""
        default_module = PC_MODNAME_INDENT1_ERROR
        not_expected_in_sys_modules(default_module)
        settings_data_dir = get_tests_settings_dir__fixture_session
        blob: Path = settings_data_dir / BLOB_FULLNAME_INDENT1_ERROR
        cwd_path: Path = cwd_inside_tests_dir__fixture_module
        indent_error_file: Path = cwd_path / PC_FULLNAME_INDENT1_ERROR
        # despite tempdir, check if file does NOT exist
        if indent_error_file.exists():
            # Bad test setup, assert out
            raise AssertionError(
                f"File {indent_error_file} should not exist in tempdir."
            )
        # Copy mangled pseudo-Python file into temporary absolute area as a Python file
        shutil.copyfile(blob, indent_error_file)

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()
            with pytest.raises(IndentationError) as sample:
                # ignore return value due to sys.exit()
                load_source(default_module, str(indent_error_file))
            assert sample.type == IndentationError
        # TODO Issue #09005 - say something to the end-user exactly where syntax err is
        # assert "unexpected indent" in self._caplog.text

        # Cleanup
        if expected_in_sys_modules(default_module):
            del sys.modules[default_module]
        indent_error_file.unlink(missing_ok=False)

    def test_load_source_module_str_abs_indent1_error_tests_settings_dir_fail(
        self,
        cwd_inside_tests_settings_dir__fixture_module,
        get_tests_settings_dir__fixture_session,
        assert_module_integrity__fixture_func,
        locale_to_c__fixture_session,
    ):
        """syntax error; absolute path, str type; passing mode"""
        default_module = PC_MODNAME_INDENT1_ERROR
        not_expected_in_sys_modules(default_module)
        settings_data_dir = get_tests_settings_dir__fixture_session
        blob: str = str(settings_data_dir / BLOB_FULLNAME_INDENT1_ERROR)
        cwd_path: Path = cwd_inside_tests_settings_dir__fixture_module
        indent_error_file: Path = cwd_path / PC_FULLNAME_INDENT1_ERROR
        # despite tempdir, check if file does NOT exist
        if indent_error_file.exists():
            raise AssertionError(
                f"File {indent_error_file!s} should not exist in tempdir."
            )
        # Copy mangled pseudo-Python file into temporary absolute area as a Python file
        shutil.copyfile(blob, indent_error_file)

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()
            with pytest.raises(IndentationError) as sample:
                # ignore return value due to sys.exit()
                load_source(default_module, str(indent_error_file))
            assert sample.type == IndentationError
        # TODO Issue #09005 - say something to the end-user exactly where syntax err is
        # assert "unexpected indent" in self._caplog.text

        # Cleanup
        if expected_in_sys_modules(default_module):
            del sys.modules[default_module]
        Path(indent_error_file).unlink(missing_ok=False)

    def test_load_source_module_str_rel_indent2_error_fail(
        self,
        locale_to_c__fixture_session,
        assert_module_integrity__fixture_func,
        get_tests_settings_dir__fixture_session,
        cwd_inside_tempdir__fixture_func,
    ):
        """syntax error, relative path, str type; failing mode"""
        # In Pelican, module name shall always be 'pelicanconf'
        indent_error_module = PC_MODNAME_INDENT2_ERROR
        not_expected_in_sys_modules(indent_error_module)
        settings_data_dir = get_tests_settings_dir__fixture_session
        blob: Path = settings_data_dir / BLOB_FULLNAME_INDENT2_ERROR
        temp_dir: Path = cwd_inside_tempdir__fixture_func
        indent_error_file: Path = temp_dir / PC_FULLNAME_INDENT2_ERROR
        # despite tempdir, check if file does NOT exist
        if indent_error_file.exists():
            raise AssertionError(
                f"File {indent_error_file!s} should not exist in tempdir."
            )
        # Copy mangled pseudo-Python file into temporary area as a Python file
        shutil.copyfile(blob, indent_error_file)

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()
            with pytest.raises(IndentationError) as sample:
                # ignore return value due to sys.exit()
                load_source(indent_error_module, path=str(indent_error_file))

            assert sample.type == IndentationError
            assert sample.value.lineno == SM_UT_SYNTAX_INDENT2_LINENO
            assert sample.value.offset == SM_UT_SYNTAX_INDENT2_OFFSET
        # Would be nice if a STDERR says something to end-user WHERE
        # the syntax err is  # TODO Issue #09005
        # assert "unexpected indent" in self._caplog.text

        if expected_in_sys_modules(indent_error_module):
            del sys.modules[indent_error_module]
        not_expected_in_sys_modules(indent_error_module)
        indent_error_file.unlink(missing_ok=False)

    def test_load_source_module_path_rel_syntax3_error_fail(
        self,
        locale_to_c__fixture_session,
        assert_module_integrity__fixture_func,
        get_tests_settings_dir__fixture_session,
        cwd_inside_tempdir__fixture_func,
    ):
        """Syntax error; valid relative file, Path type; valid module; passing mode"""
        # In Pelican, module name shall always be 'pelicanconf'
        syntax3_module = PC_MODNAME_SYNTAX3_ERROR
        not_expected_in_sys_modules(syntax3_module)
        settings_data_dir = get_tests_settings_dir__fixture_session
        blob: Path = settings_data_dir / BLOB_FULLNAME_SYNTAX3_ERROR
        cwd_path: Path = cwd_inside_tempdir__fixture_func
        syntax_error_file: Path = cwd_path / PC_FULLNAME_SYNTAX3_ERROR
        if syntax_error_file.exists():
            # Bad test setup, assert out
            raise AssertionError(
                f"File {syntax_error_file!s} should not exist in tempdir."
            )
        # Copy mangled pseudo-Python file into temporary absolute area as a Python file
        shutil.copyfile(blob, syntax_error_file)

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()
            with pytest.raises(SyntaxError) as sample:
                # ignore return value due to sys.exit()
                load_source(name=syntax3_module, path=str(syntax_error_file))
            assert sample.type == SyntaxError
        assert sample.value.lineno == SM_UT_SYNTAX_ERROR3_LINENO
        assert sample.value.offset == SM_UT_SYNTAX_ERROR3_OFFSET
        # TODO Issue #09005 - say something to the end-user exactly where syntax err is
        # assert "unexpected indent" in self._caplog.text

        if expected_in_sys_modules(syntax3_module):
            del sys.modules[syntax3_module]
        syntax_error_file.unlink(missing_ok=True)

    def test_load_source_module_path_abs_syntax4_error_fail(
        self,
        locale_to_c__fixture_session,
        assert_module_integrity__fixture_func,
        get_tests_settings_dir__fixture_session,
        cwd_inside_tempdir__fixture_func,
    ):
        """Syntax error; valid absolute file, Path type; valid module; passing mode"""
        # In Pelican, module name shall always be 'pelicanconf'
        default_module = PC_MODNAME_SYNTAX4_ERROR
        not_expected_in_sys_modules(default_module)
        settings_data_dir = get_tests_settings_dir__fixture_session
        blob: Path = settings_data_dir / BLOB_FULLNAME_SYNTAX4_ERROR
        cwd_path: Path = cwd_inside_tempdir__fixture_func
        syntax_error_file: Path = cwd_path / PC_FULLNAME_SYNTAX4_ERROR
        if syntax_error_file.exists():
            raise AssertionError(
                f"File {syntax_error_file!s} should not exist in tempdir."
            )
        # Copy mangled pseudo-Python file into temporary area as a Python file
        shutil.copyfile(blob, syntax_error_file)

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()
            with pytest.raises(SyntaxError) as sample:
                load_source(default_module, str(syntax_error_file))

            assert sample.type == SyntaxError
            assert sample.value.lineno == SM_UT_SYNTAX_ERROR4_LINENO
            assert sample.value.offset == SM_UT_SYNTAX_ERROR4_OFFSET
        # TODO Issue #09005 - say something to the end-user exactly where syntax err is
        # assert "unexpected indent" in self._caplog.text

        # Cleanup temporary
        if expected_in_sys_modules(default_module):
            del sys.modules[default_module]
        syntax_error_file.unlink(missing_ok=False)


if __name__ == "__main__":
    # if executing this file alone, it tests this file alone.
    # Can execute from any current working directory
    pytest.main([__file__])

    # more, complex variants of pytest.
    # pytest.main([__file__, "-n0", "-rAw", "--capture=no", "--no-header"])
    # pytest.main([__file__, "-n0"])  # single-process, single-thread
