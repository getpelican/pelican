#
#  Focus on settings.py/load_source() only

# Minimum version: Python 3.6 (tempfile.mkdtemp())
# Minimum version: Pytest 4.0, Python 3.8+

import errno
import inspect
import locale
import logging
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureHandler, _remove_ansi_escape_sequences  # NOQA

from pelican.settings import (
    load_source,
)
from pelican.tests.support import unittest

# Valid Python file extension
EXT_PYTHON = ".py"
EXT_PYTHON_DISABLED = ".disabled"

# DIRSPEC_: where all the test config files are stored
# we hope that current working directory is always in pelican/pelican/tests
DIRSPEC_CURRENT: str = os.getcwd()
DIRSPEC_DATADIR: str = "settings" + os.sep
DIRSPEC_RELATIVE: str = DIRSPEC_DATADIR  # reuse 'tests/settings/' as scratch area

# PC_ = Pelican Configuration or PELICANCONF or pelicanconf
# FILENAME_: file name without the extension
PC_FILENAME_DEFAULT = "pelicanconf"
PC_FILENAME_VALID = "pelicanconf-valid"
PC_FILENAME_NOTFOUND = "pelicanconf-not-found"
PC_FILENAME_UNREADABLE = "pelicanconf-unreadable"
PC_FILENAME_SYNTAX_ERROR = "pelicanconf-syntax-error"

# MODNAME_ = Module name
PC_MODNAME_DEFAULT = PC_FILENAME_DEFAULT  # used if module_name is blank
PC_MODNAME_VALID = PC_FILENAME_VALID
PC_MODNAME_UNREADABLE = PC_FILENAME_UNREADABLE
PC_MODNAME_NOT_EXIST = PC_FILENAME_NOTFOUND
PC_MODNAME_DOTTED = "non-existing-module.cannot-get-there"  # there is a period
PC_MODNAME_SYS_BUILTIN = "calendar"

TMP_FILENAME_SUFFIX = PC_FILENAME_DEFAULT

# FULLNAME_: filename + extension
PC_FULLNAME_VALID: str = PC_FILENAME_VALID + EXT_PYTHON
PC_FULLNAME_NOTFOUND: str = PC_FILENAME_NOTFOUND + EXT_PYTHON
PC_FULLNAME_UNREADABLE: str = PC_FILENAME_UNREADABLE + EXT_PYTHON
PC_FULLNAME_SYNTAX_ERROR: str = PC_FILENAME_SYNTAX_ERROR + EXT_PYTHON
# BLOB_: a file trying to hide from ruff/black syntax checkers for our syntax tests
BLOB_FULLNAME_SYNTAX_ERROR = PC_FULLNAME_SYNTAX_ERROR + EXT_PYTHON_DISABLED

# DIRNAME_: a construct of where to find config file for specific test
PC_DIRNAME_NOTFOUND: str = "no-such-directory"
PC_DIRNAME_NOACCESS: str = "unreadable-directory"

# DIRSPEC_: the full directory path

# Our test files
BLOB_FILESPEC_UNREADABLE = Path(DIRSPEC_DATADIR) / PC_FULLNAME_UNREADABLE
BLOB_FILESPEC_SYNTAX_ERROR = Path(DIRSPEC_DATADIR) / str(
    PC_FULLNAME_SYNTAX_ERROR + EXT_PYTHON_DISABLED
)

# PATH_: the final path for unit tests here
# FILESPEC_: the full path + filename + extension
# REL_: relative path
RO_FILESPEC_REL_VALID_PATH = Path(DIRSPEC_DATADIR) / PC_FULLNAME_VALID
RO_FILESPEC_REL_SYNTAX_ERROR_PATH = Path(DIRSPEC_DATADIR) / PC_FULLNAME_SYNTAX_ERROR
RO_FILESPEC_REL_NOTFOUND_PATH = Path(DIRSPEC_DATADIR) / PC_FULLNAME_NOTFOUND
# FILESPEC_REL_UNREADABLE_PATH = Path(DIRSPEC_RELATIVE) / PC_FULLNAME_UNREADABLE

load_source_argument_count = 2

# Code starts here
logging.basicConfig(level=0)
log = logging.getLogger(__name__)
logging.root.setLevel(logging.DEBUG)
log.propagate = True


def remove_read_permissions(path):
    """Remove read permissions from this path, keeping all other permissions intact.

    :param path:  The path whose permissions to alter.
    :type path: str
    """
    no_user_reading = ~stat.S_IRUSR
    no_group_reading = ~stat.S_IRGRP
    no_other_reading = ~stat.S_IROTH
    no_reading = no_user_reading & no_group_reading & no_other_reading

    current_permissions = stat.S_IMODE(os.lstat(path).st_mode)
    os.chmod(path, current_permissions & no_reading)


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


class TestSettingsModuleName(unittest.TestCase):
    """load_source() w/ module_name arg"""

    # Exercises both the path and module_name arguments"""
    def setUp(self):
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, "C")
        self.saved_sys_modules = sys.modules

        # Something interesting ...:
        # below logic only works with ALL classes within a file
        # and does not work within a selective class.
        # So logic within this setUp() is file-wide, not per-class.

        args = inspect.getfullargspec(load_source)
        if ("name" not in args.args) and (
            args.args.__len__ != load_source_argument_count
        ):
            # Skip this entire test file if load_source() only supports 1 argument
            pytest.skip(
                "this class is only used with load_source() having "
                "support for a 'module_name' argument"
            )

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, self.old_locale)
        if PC_MODNAME_SYS_BUILTIN not in sys.modules:
            AssertionError(
                f"A built-in module named {PC_MODNAME_SYS_BUILTIN} got "
                "deleted; test setup failed"
            )
        if PC_MODNAME_DEFAULT in sys.modules:
            del sys.modules[PC_MODNAME_DEFAULT]
            AssertionError(
                f"One of many unittests did not remove {PC_MODNAME_DEFAULT} module."
            )
        if PC_MODNAME_VALID in sys.modules:
            del sys.modules[PC_MODNAME_VALID]
            AssertionError(
                f"One of many unittests did not remove {PC_MODNAME_VALID} module."
            )
        if PC_MODNAME_UNREADABLE in sys.modules:
            del sys.modules[PC_MODNAME_UNREADABLE]
            AssertionError(
                f"One of many unittests did not remove {PC_MODNAME_UNREADABLE} module."
            )
        if PC_MODNAME_NOT_EXIST in sys.modules:
            del sys.modules[PC_MODNAME_NOT_EXIST]
            AssertionError(
                f"One of many unittests did not remove {PC_MODNAME_NOT_EXIST} module."
            )
        if PC_MODNAME_DOTTED in sys.modules:
            del sys.modules[PC_MODNAME_DOTTED]
            AssertionError(
                f"One of many unittests did not remove {PC_MODNAME_DOTTED} module."
            )
        if self.saved_sys_modules != sys.modules:
            AssertionError(
                "sys.modules was not restored to its original glory; "
                "investigate faulty unit test"
            )
        # TODO delete any straggling temporary directory?

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        """add support for an assert based on subpattern in `caplog.text` output"""
        self._caplog = caplog

    # Blank arguments test series, by path argument, str type
    def test_load_source_str_all_blank_fail(self):
        """arguments all blank, str type; failing mode"""
        # Supply blank string to each argument and fail
        blank_filespec_str: str = ""
        module_name_str = ""

        module_spec = load_source(module_name_str, blank_filespec_str)  # NOQA: RUF100
        assert module_spec is None

    # Proper combinatorial - Focusing firstly on the path argument using str type
    def test_load_source_str_rel_dotted_fail(self):
        """dotted relative directory, str type; blank module; failing mode"""
        dotted_filespec_str: str = "."
        module_name_str = ""

        module_spec = load_source(module_name_str, dotted_filespec_str)  # NOQA: RUF100
        assert module_spec is None

    def test_load_source_str_rel_parent_fail(self):
        """relative parent, str type; blank module; failing mode"""
        parent_filespec_str: str = ".."
        # Let the load_source() determine its module name
        module_name_str = ""

        module_spec = load_source(module_name_str, parent_filespec_str)  # NOQA: RUF100
        assert module_spec is None

    def test_load_source_str_anchor_fail(self):
        """anchor directory, str type; blank module; failing mode"""
        anchor_filespec_str: str = os.sep
        # Let the load_source() determine its module name
        module_name_str = ""

        module_spec = load_source(module_name_str, anchor_filespec_str)  # NOQA: RUF100
        assert module_spec is None

    def test_load_source_str_cwd_fail(self):
        """current working dir, str type; blank module; failing mode"""
        cwd_filespec_str: str = str(Path.cwd())
        # Let the load_source() determine its module name
        module_name_str = ""

        module_spec = load_source(module_name_str, cwd_filespec_str)
        assert module_spec is None

    # Focusing on the path argument using Path type
    def test_load_source_path_all_blank_fail(self):
        """arguments blank; Path type; blank module; failing mode"""
        # Supply blank string to each argument and fail
        blank_filespec_path: Path = Path("")
        # Let the load_source() determine its module name
        module_name_str = ""

        module_spec = load_source(module_name_str, blank_filespec_path)
        assert module_spec is None

    def test_load_source_path_dot_fail(self):
        """dotted directory, Path type; blank module; failing mode"""
        dotted_filespec_path: Path = Path(".")
        # Let the load_source() determine its module name
        module_name_str = ""

        module_spec = load_source(module_name_str, dotted_filespec_path)
        assert module_spec is None

    def test_load_source_path_abs_anchor_fail(self):
        """anchor (absolute) directory, Path type; blank module; failing mode"""
        anchor_filespec_path: Path = Path(os.sep)
        # Let the load_source() determine its module name
        module_name_str = ""

        module_spec = load_source(module_name_str, anchor_filespec_path)
        assert module_spec is None

    def test_load_source_path_rel_parent_fail(self):
        """parent relative directory, Path type; blank module; failing mode"""
        parent_filespec_path: Path = Path("..")
        # Let the load_source() determine its module name
        module_name_str = ""

        module_spec = load_source(module_name_str, parent_filespec_path)
        assert module_spec is None

    def test_load_source_path_abs_cwd_fail(self):
        """current working (absolute) dir, Path type, blank module; failing mode"""
        blank_filespec_path: Path = Path.cwd()
        # Let the load_source() determine its module name
        module_name_str = ""

        module_spec = load_source(module_name_str, blank_filespec_path)
        assert module_spec is None

    # Actually start to try using Pelican configuration file
    # but with no module_name
    def test_load_source_str_rel_valid_pass(self):
        """valid relative path, str type; blank module; passing mode"""
        tmp_rel_path: Path = Path(
            tempfile.mkdtemp(dir=DIRSPEC_RELATIVE, suffix=TMP_FILENAME_SUFFIX)
        )
        valid_rel_filespec_str: str = str(tmp_rel_path / Path(".") / PC_FULLNAME_VALID)
        # Copy file to absolute temporary directory
        shutil.copy(RO_FILESPEC_REL_VALID_PATH, valid_rel_filespec_str)

        # Let the load_source() determine its module name
        module_name_str = ""
        if PC_MODNAME_VALID in sys.modules:
            AssertionError(
                f"{PC_MODNAME_VALID} is still in sys.modules; fatal error " f"out"
            )

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            # ignore return value due to sys.exit()
            module_spec = load_source(module_name_str, valid_rel_filespec_str)
            assert module_spec is not None
            assert hasattr(module_spec, "PATH"), (
                f"The {valid_rel_filespec_str} file did not provide a PATH "
                "object variable having a valid directory name, absolute or relative."
            )

        # Cleanup
        if PC_MODNAME_VALID in sys.modules:  # module_name is blank
            # del module after ALL asserts, errnos, and STDOUT
            del sys.modules[PC_MODNAME_VALID]
        Path(valid_rel_filespec_str).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here
        shutil.rmtree(tmp_rel_path)

    def test_load_source_str_abs_valid_pass(self):
        """valid absolute path, str type; blank module; passing mode"""
        # Set up absolute temporary directory
        tmp_abs_path: Path = Path(tempfile.mkdtemp(TMP_FILENAME_SUFFIX))
        valid_abs_filespec_str: str = str(tmp_abs_path / PC_FULLNAME_VALID)
        # Let the load_source() determine its module name
        module_name_str = ""
        if PC_MODNAME_VALID in sys.modules:
            AssertionError(
                f"{PC_MODNAME_VALID} is still in sys.modules; fatal error " f"out"
            )

        # Copy file to absolute temporary directory
        shutil.copy(RO_FILESPEC_REL_VALID_PATH, valid_abs_filespec_str)

        module_spec = load_source(module_name_str, valid_abs_filespec_str)
        # check if PATH is defined inside a valid Pelican configuration settings file
        assert module_spec is not None
        assert hasattr(module_spec, "PATH"), (
            f"The {valid_abs_filespec_str} file did not provide a PATH "
            "object variable having a valid directory name, absolute or relative."
        )

        # Cleanup
        if PC_MODNAME_VALID in sys.modules:
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_VALID]
        Path(valid_abs_filespec_str).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here
        shutil.rmtree(tmp_abs_path)

    def test_load_source_str_rel_not_found_fail(self):
        """relative not found, str type; blank module; failing mode"""
        if RO_FILESPEC_REL_NOTFOUND_PATH.exists():
            AssertionError(f"{RO_FILESPEC_REL_NOTFOUND_PATH} should not exist.")
        missing_rel_filespec_str: str = str(RO_FILESPEC_REL_NOTFOUND_PATH)
        # Let the load_source() determine its module name
        module_name_str = ""

        # since load_source only returns None or Module, check STDERR for 'not found'
        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            module_spec = load_source(module_name_str, missing_rel_filespec_str)
            # but we have to check for warning
            # message of 'assumed implicit module name'
            assert module_spec is None
            assert " not found" in self._caplog.text

    def test_load_source_str_abs_not_found_fail(self):
        """absolute not found, str type; blank module; failing mode"""
        # Set up absolute temporary directory
        tmp_abs_dirspec: Path = Path(tempfile.mkdtemp(TMP_FILENAME_SUFFIX))
        notfound_abs_filespec_path: Path = tmp_abs_dirspec / PC_FULLNAME_NOTFOUND
        # No need to copy file, but must check that none is there
        if notfound_abs_filespec_path.exists():
            # Ouch, to delete or to absolute fail?  We fail here, instead.
            AssertionError(f"Errant '{notfound_abs_filespec_path} found; FAILED")
        # Let the load_source() determine its module name
        module_name_str = ""

        # since load_source only returns None or Module, check STDERR for 'not found'
        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            module_spec = load_source(module_name_str, notfound_abs_filespec_path)
            # but we have to check for warning
            # message of 'assumed implicit module name'
            assert module_spec is None
            assert " not found" in self._caplog.text

        # Cleanup
        # This tree should be empty
        shutil.rmtree(tmp_abs_dirspec)

    def test_load_source_str_rel_no_access_fail(self):
        """relative not readable, str type; blank module; failing mode"""
        # Set up relative temporary directory "settings/pelicanXXXXXX"
        rel_tmp_path: Path = Path(
            tempfile.mkdtemp(
                dir=DIRSPEC_RELATIVE,
                suffix=TMP_FILENAME_SUFFIX,
            )
        )
        noaccess_rel_filespec_path: Path = rel_tmp_path / PC_FULLNAME_UNREADABLE
        # despite tempdir, check if file does NOT exist
        if noaccess_rel_filespec_path.exists():
            # Bad test setup, assert out
            AssertionError(
                f"File {noaccess_rel_filespec_path} should not " "exist in tempdir"
            )
        noaccess_rel_filespec_path.touch()  # wonder if GitHub preserves no-read bit
        remove_read_permissions(str(noaccess_rel_filespec_path))
        noaccess_rel_filespec_str = str(noaccess_rel_filespec_path)
        # File must exist; but one must check that it is unreadable there
        if os.access(noaccess_rel_filespec_str, os.R_OK):
            # Ouch, to change file perm bits or to absolute fail?  Fail here, instead.
            AssertionError(
                f"Errant '{noaccess_rel_filespec_str} unexpectedly readable; FAILED"
            )

        # Let the load_source() determine its module name
        module_name_str = ""
        if PC_MODNAME_UNREADABLE in sys.modules:
            AssertionError(
                f"{PC_MODNAME_UNREADABLE} is still in sys.modules; fatal " f"error out"
            )

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            module_spec = load_source(module_name_str, noaccess_rel_filespec_str)
            # but we have to check for a warning
            # message of 'assumed implicit module name'
            assert module_spec is None
            assert " is not readable" in self._caplog.text

        # Cleanup
        if PC_MODNAME_UNREADABLE in sys.modules:
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_UNREADABLE]
        Path(noaccess_rel_filespec_path).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(rel_tmp_path)

    def test_load_source_str_abs_no_access_fail(self):
        """absolute not readable, str type; blank module; failing mode"""
        # Set up absolute temporary "/$TEMPDIR/pelicanXXXXXX"
        abs_tmp_path: Path = Path(
            tempfile.mkdtemp(
                # dir= supplies us with absolute default, as a default
                suffix=TMP_FILENAME_SUFFIX,
            )
        )
        noaccess_abs_filespec_path: Path = abs_tmp_path / PC_FULLNAME_UNREADABLE
        # despite tempdir, check if file does NOT exist
        if noaccess_abs_filespec_path.exists():
            # Bad test setup, assert out
            AssertionError(
                f"File {noaccess_abs_filespec_path} should not " "exist in tempdir"
            )
        noaccess_abs_filespec_path.touch()
        remove_read_permissions(str(noaccess_abs_filespec_path))
        # do not need to copy REL into ABS but need to ensure no ABS is there
        if os.access(noaccess_abs_filespec_path, os.R_OK):
            # Ouch, to change file perm bits or to absolute fail?  Fail here, instead.
            AssertionError(
                f"Errant '{noaccess_abs_filespec_path} unexpectedly " "readable; FAILED"
            )

        # Let the load_source() determine its module name
        module_name_str = ""
        if PC_FILENAME_UNREADABLE in sys.modules:
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_FILENAME_UNREADABLE]

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            module_spec = load_source(module_name_str, noaccess_abs_filespec_path)
            # but we have to check for warning
            # message of 'assumed implicit module name'
            assert module_spec is None
            assert " is not readable" in self._caplog.text

        # Cleanup
        if PC_FILENAME_UNREADABLE in sys.modules:
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_FILENAME_UNREADABLE]
        Path(noaccess_abs_filespec_path).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(abs_tmp_path)

    # continue using the path argument, but starting with Path type,

    def test_load_source_path_rel_valid_pass(self):
        """valid relative path, Path type; blank module; passing mode"""
        # Use pelicanconf straight out of settings/pelicanconf-valid.py; no tempdir
        # Set up temporary relative "settings/pelicanXXXXXX"
        tmp_rel_path: Path = Path(
            tempfile.mkdtemp(dir=DIRSPEC_RELATIVE, suffix=TMP_FILENAME_SUFFIX)
        )
        valid_rel_filespec_path: Path = tmp_rel_path / PC_FULLNAME_VALID
        shutil.copyfile(RO_FILESPEC_REL_VALID_PATH, valid_rel_filespec_path)

        module_name_str = ""
        if PC_FILENAME_VALID in sys.modules:
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_FILENAME_VALID]

        module_spec = load_source(module_name_str, valid_rel_filespec_path)
        # check if PATH is defined inside a valid Pelican configuration settings file
        assert module_spec is not None
        assert hasattr(module_spec, "PATH"), (
            f"The {valid_rel_filespec_path} file did not provide a PATH "
            "object variable having a valid directory name, absolute or relative."
        )

        # Cleanup
        if PC_MODNAME_VALID in sys.modules:  # module_name is blank
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_VALID]
        Path(valid_rel_filespec_path).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(tmp_rel_path)

    def test_load_source_path_abs_valid_pass(self):
        """valid absolute path, Path type; blank module; passing mode"""
        # Set up temporary absolute "/$TEMPDIR/pelicanXXXXXX"
        abs_tmp_path: Path = Path(
            tempfile.mkdtemp(
                # dir= supplies us with absolute default, as a default
                suffix=TMP_FILENAME_SUFFIX,
            )
        )
        valid_abs_filespec_path: Path = abs_tmp_path / PC_FULLNAME_VALID
        shutil.copy(RO_FILESPEC_REL_VALID_PATH, valid_abs_filespec_path)

        # Let the load_source() determine its module name
        module_name_str = ""
        if PC_MODNAME_VALID in sys.modules:
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_VALID]

        module_spec = load_source(module_name_str, valid_abs_filespec_path)
        # check if PATH is defined inside a valid Pelican configuration settings file
        assert module_spec is not None
        assert hasattr(module_spec, "PATH"), (
            f"The {valid_abs_filespec_path} file did not provide a PATH "
            "object variable having a valid directory name, absolute or relative."
        )

        # Cleanup
        if PC_MODNAME_VALID in sys.modules:  # module_name is blank
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_VALID]
        Path(valid_abs_filespec_path).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(abs_tmp_path)

    def test_load_source_path_rel_not_found_fail(self):
        """relative not found, Path type; blank module; failing mode"""
        # Set up temporary relative "settings/pelicanXXXXXX"
        tmp_rel_dirspec_path: Path = Path(
            tempfile.mkdtemp(dir=DIRSPEC_RELATIVE, suffix=TMP_FILENAME_SUFFIX)
        )
        notfound_rel_filespec_path: Path = tmp_rel_dirspec_path / PC_FULLNAME_NOTFOUND
        # No need to copy file, but must check that none is there
        if notfound_rel_filespec_path.exists():
            # Ouch, to delete or to absolute fail?  We fail here, instead.
            AssertionError(f"did not expect {notfound_rel_filespec_path} in a tempdir.")

        # Let the load_source() determine its module name
        module_name_str = ""
        if PC_MODNAME_NOT_EXIST in sys.modules:
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_NOT_EXIST]

        # since load_source only returns None or Module, check STDERR for 'not found'
        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            module_spec = load_source(module_name_str, notfound_rel_filespec_path)
            # but we have to check for warning
            # message of 'assumed implicit module name'
            assert " not found" in self._caplog.text
            assert module_spec is None

        # Cleanup temporary
        if PC_MODNAME_NOT_EXIST in sys.modules:  # module_name is blank
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_NOT_EXIST]
        shutil.rmtree(tmp_rel_dirspec_path)

    def test_load_source_path_abs_not_found_fail(self):
        """absolute not found, Path type; blank module; failing mode"""
        # Set up temporary
        tmp_abs_dirspec_path: Path = Path(tempfile.mkdtemp(TMP_FILENAME_SUFFIX))
        missing_abs_filespec_path: Path = tmp_abs_dirspec_path / PC_FULLNAME_NOTFOUND
        # No need to copy file, but must check that none is there
        if missing_abs_filespec_path.exists():
            # Ouch, to delete or to absolute fail?  We fail here, instead.
            AssertionError(f"Errant '{missing_abs_filespec_path} found; FAILED")

        # Let the load_source determine its module name, error-prone
        module_name_str = ""
        if PC_MODNAME_NOT_EXIST in sys.modules:
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_NOT_EXIST]

        # since load_source only returns None or Module, check STDERR for 'not found'
        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            module_spec = load_source(module_name_str, missing_abs_filespec_path)
            # but we have to check for warning
            # message of 'assumed implicit module name'
            assert module_spec is None
            assert " not found" in self._caplog.text

        if PC_MODNAME_NOT_EXIST in sys.modules:  # module_name is blank
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_NOT_EXIST]
        shutil.rmtree(tmp_abs_dirspec_path)

    def test_load_source_path_rel_no_access_fail(self):
        """relative not readable, Path type; blank module; failing mode"""
        # Set up temporary
        tmp_rel_dirspec_path: Path = Path(
            tempfile.mkdtemp(dir=DIRSPEC_RELATIVE, suffix=TMP_FILENAME_SUFFIX)
        )
        noaccess_rel_filespec_path: Path = tmp_rel_dirspec_path / PC_FULLNAME_UNREADABLE
        # No need to copy file, but must check that none is there
        if noaccess_rel_filespec_path.exists():
            # Ouch, to delete or to absolute fail?  We fail here, instead.
            AssertionError(f"Errant '{noaccess_rel_filespec_path} found; FAILED")
        # wonder if GitHub preserves no-read bit (Update: Nope, gotta roll our own)
        Path(noaccess_rel_filespec_path).touch()
        remove_read_permissions(str(noaccess_rel_filespec_path))
        # do not need to copy REL into ABS but need to ensure no ABS is there
        if os.access(noaccess_rel_filespec_path, os.R_OK):
            # Ouch, to change file perm bits or to absolute fail?  Fail here, instead.
            AssertionError(
                f"Errant '{noaccess_rel_filespec_path} unexpectedly " "readable; FAILED"
            )

        # Let the load_source() determine its module name
        module_name_str = ""
        if PC_MODNAME_UNREADABLE in sys.modules:
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_UNREADABLE]

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            module_spec = load_source(module_name_str, noaccess_rel_filespec_path)
            # but we have to check for a warning
            # message of 'assumed implicit module name'
            assert module_spec is None
            assert " is not readable" in self._caplog.text

        # Cleanup
        if PC_MODNAME_UNREADABLE in sys.modules:  # module_name is blank
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_UNREADABLE]
        Path(noaccess_rel_filespec_path).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(tmp_rel_dirspec_path)

    def test_load_source_path_abs_no_access_fail(self):
        """absolute not readable, Path type; blank module; failing mode"""
        # Set up temporary relative "/$TEMPDIR/pelicanXXXXXX"
        tmp_abs_dirspec_path: Path = Path(
            tempfile.mkdtemp(
                # dir= supplies us with absolute default, as a default
                suffix=TMP_FILENAME_SUFFIX,
            )
        )
        noaccess_abs_filespec_path: Path = tmp_abs_dirspec_path / PC_FULLNAME_UNREADABLE
        # despite tempdir, check if file does NOT exist
        if noaccess_abs_filespec_path.exists():
            # Bad test setup, assert out
            AssertionError(
                f"File {noaccess_abs_filespec_path} should not " "exist in tempdir"
            )
        noaccess_abs_filespec_path.touch()  # wonder if GitHub preserves no-read bit
        remove_read_permissions(str(noaccess_abs_filespec_path))
        # do not need to copy REL into ABS but need to ensure no ABS is there
        if os.access(noaccess_abs_filespec_path, os.R_OK):
            # Ouch, to change file perm bits or to absolute fail?
            # Test setup fail here, Assert-hard.
            AssertionError(
                f"Errant '{noaccess_abs_filespec_path} unexpectedly " "readable; FAILED"
            )

        # Let the load_source() determine its module name
        module_name_str = ""
        if PC_MODNAME_NOT_EXIST in sys.modules:
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_NOT_EXIST]

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            module_spec = load_source(module_name_str, noaccess_abs_filespec_path)
            assert module_spec is None
            assert " is not readable" in self._caplog.text

        # Cleanup
        if PC_MODNAME_NOT_EXIST in sys.modules:  # module_name is blank
            # del module after ALL asserts, errnos, and STDOUT; before file removal
            del sys.modules[PC_MODNAME_NOT_EXIST]
        Path(noaccess_abs_filespec_path).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(tmp_abs_dirspec_path)

    # Everything afterward is all about the module_name

    # Start using module_name, but with valid (str type) path always
    # (will test valid module_name_str with invalid path afterward)

    def test_load_source_module_str_valid_pass(self):
        """valid module, relative path str type; passing mode"""
        # In Pelican, module name shall always be 'pelicanconf'
        module_name_str = PC_MODNAME_DEFAULT
        if module_name_str in sys.modules:
            AssertionError(
                f"Module {module_name_str} is still pre-loaded; fatal "
                f"setup error; aborted"
            )

        tmp_abs_dirspec_path: Path = Path(
            tempfile.mkdtemp(
                # dir= supplies us with absolute default, as a default
                suffix=TMP_FILENAME_SUFFIX,
            )
        )
        valid_abs_filespec_path: Path = tmp_abs_dirspec_path / PC_FULLNAME_VALID
        shutil.copyfile(RO_FILESPEC_REL_VALID_PATH, valid_abs_filespec_path)

        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            module_spec = load_source(module_name_str, valid_abs_filespec_path)
            # but we have to check for warning
            # message of 'assumed implicit module name'
            assert module_spec is not None
            assert hasattr(module_spec, "PATH"), (
                f"The {valid_abs_filespec_path} file did not provide a PATH "
                "object variable having a valid directory name, absolute or relative."
            )
            assert "Loaded module" in self._caplog.text

        # Cleanup
        if module_name_str in sys.modules:  # module_name used, not extracted from file
            # del module after ALL asserts, errnos, and STDOUT; but before file removal
            del sys.modules[module_name_str]
        Path(valid_abs_filespec_path).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(tmp_abs_dirspec_path)

    def test_load_source_module_str_rel_syntax_error_fail(self):
        """syntax error, relative path, str type; failing mode"""
        # In Pelican, module name shall always be 'pelicanconf'
        module_name_str = PC_MODNAME_DEFAULT
        if module_name_str in sys.modules:
            AssertionError(
                f"Module {module_name_str} is previously loaded; fatal "
                f"test setup; aborted"
            )

        # copy "pseudo-script" file into 'settings/pelicanXXXXX/(here)'
        # An essential avoidance of ruff/black's own syntax-error asserts
        blob: str = str(BLOB_FILESPEC_SYNTAX_ERROR)
        # Set up temporary relative "settings/pelicanXXXXXX/(here)"
        tmp_rel_dirspec_path: Path = Path(
            tempfile.mkdtemp(dir=DIRSPEC_RELATIVE, suffix=TMP_FILENAME_SUFFIX)
        )
        syntax_err_rel_filespec_str: str = str(
            tmp_rel_dirspec_path / PC_FULLNAME_SYNTAX_ERROR
        )
        # Copy mangled pseudo-Python file into temporary area as a Python file
        shutil.copyfile(blob, syntax_err_rel_filespec_str)

        with self._caplog.at_level(logging.DEBUG):
            with pytest.raises(SystemExit) as sample:
                self._caplog.clear()

                # ignore return value due to sys.exit()
                load_source(module_name_str, path=syntax_err_rel_filespec_str)
                assert sample.type == SystemExit
                assert sample.value.code == errno.ENOEXEC
            assert "invalid syntax" in self._caplog.text

        # Cleanup temporary
        if module_name_str in sys.modules:  # module_name used, not extracted from file
            # del module after ALL asserts, errnos, and STDOUT
            del sys.modules[module_name_str]
        Path(syntax_err_rel_filespec_str).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(tmp_rel_dirspec_path)

    def test_load_source_module_str_abs_syntax_error_fail(self):
        """ "syntax error; absolute path, str type; passing mode"""
        # In Pelican, module name shall always be 'pelicanconf'
        module_name_str = PC_MODNAME_DEFAULT
        if module_name_str in sys.modules:
            AssertionError(
                f"Module {module_name_str} is still preloaded; fatal " f"error; aborted"
            )

        # identify blob of  "pseudo-script" file (ruff/black avoidance of syntax-error)
        blob: str = str(Path(DIRSPEC_RELATIVE) / BLOB_FULLNAME_SYNTAX_ERROR)
        # Set up temporary absolute "/$TEMPDIR/pelicanXXXXXX/(here)"
        tmp_abs_dirspec_path: Path = Path(
            tempfile.mkdtemp(
                # dir= supplies us with absolute default, as a default
                suffix=TMP_FILENAME_SUFFIX
            )
        )
        syntax_err_abs_filespec_str: str = str(
            tmp_abs_dirspec_path / PC_FULLNAME_SYNTAX_ERROR
        )
        # despite tempdir, check if file does NOT exist
        if Path(syntax_err_abs_filespec_str).exists():
            # Bad test setup, assert out
            AssertionError(
                f"File {syntax_err_abs_filespec_str} should not " "exist in tempdir"
            )
        # Copy mangled pseudo-Python file into temporary absolute area as a Python file
        shutil.copyfile(blob, syntax_err_abs_filespec_str)

        with self._caplog.at_level(logging.DEBUG):
            with pytest.raises(SystemExit) as sample:
                self._caplog.clear()

                # ignore return value due to sys.exit()
                load_source(module_name_str, syntax_err_abs_filespec_str)
                assert sample.type == SystemExit
                assert sample.value.code == errno.ENOEXEC
            assert "invalid syntax" in self._caplog.text

        # Cleanup
        if module_name_str in sys.modules:  # module_name used, not extracted from file
            # del module after ALL asserts, errnos, and STDOUT
            del sys.modules[module_name_str]
        Path(syntax_err_abs_filespec_str).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(tmp_abs_dirspec_path)

    # Start using module_name, but with valid (path type) path always
    def test_load_source_perfect_pass(self):
        """valid module name; valid relative file, Path type; passing mode"""
        # In Pelican, module name shall always be 'pelicanconf'
        module_name_str = PC_MODNAME_DEFAULT
        if module_name_str in sys.modules:
            AssertionError(
                f"Module {PC_MODNAME_DEFAULT} is still pre-loaded; fatal "
                f"setup error; aborted."
            )

        # Set up temporary absolute "/$TEMPDIR/pelicanXXXXXX"
        tmp_rel_path: Path = Path(
            tempfile.mkdtemp(
                dir=DIRSPEC_RELATIVE,
                suffix=TMP_FILENAME_SUFFIX,
            )
        )
        valid_rel_filespec_path: Path = tmp_rel_path / PC_FULLNAME_VALID
        shutil.copy(RO_FILESPEC_REL_VALID_PATH, valid_rel_filespec_path)

        # Setup to capture STDOUT
        with self._caplog.at_level(logging.DEBUG):
            #  Clear any STDOUT for our upcoming regex pattern test
            self._caplog.clear()

            module_spec = load_source(module_name_str, valid_rel_filespec_path)
            # but we have to check for warning
            # message of 'assumed implicit module name'
            assert module_spec is not None
            assert hasattr(module_spec, "PATH"), (
                f"The {valid_rel_filespec_path} file did not provide a PATH "
                "object variable having a valid directory name, absolute or relative."
            )
            assert "Loaded module" in self._caplog.text

        # Cleanup
        if module_name_str in sys.modules:  # module_name used, not extracted from file
            # del module after ALL asserts, errnos, and STDOUT
            del sys.modules[module_name_str]
        Path(valid_rel_filespec_path).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(tmp_rel_path)

    def test_load_source_module_path_rel_syntax_error_fail(self):
        """Syntax error; valid relative file, Path type; valid module; passing mode"""
        # In Pelican, module name shall always be 'pelicanconf'
        module_name_str = PC_MODNAME_DEFAULT
        if module_name_str in sys.modules:
            AssertionError(
                f"Module {module_name_str} is still preloaded; fatal setup "
                f"error; aborted."
            )

        # identify blob of  "pseudo-script" file (ruff/black avoidance of syntax-error)
        blob: str = str(Path(DIRSPEC_RELATIVE) / BLOB_FULLNAME_SYNTAX_ERROR)
        # Set up temporary relative "settings/pelicanXXXXXX/(here)"
        tmp_rel_dirspec_path: Path = Path(
            tempfile.mkdtemp(dir=DIRSPEC_RELATIVE, suffix=TMP_FILENAME_SUFFIX)
        )
        syntax_err_rel_filespec_path: Path = (
            tmp_rel_dirspec_path / PC_FULLNAME_SYNTAX_ERROR
        )
        # despite tempdir, check if file does NOT exist
        if syntax_err_rel_filespec_path.exists():
            # Bad test setup, assert out
            AssertionError(
                f"File {syntax_err_rel_filespec_path!s} should not " "exist in tempdir"
            )
        # Copy mangled pseudo-Python file into temporary absolute area as a Python file
        shutil.copyfile(blob, syntax_err_rel_filespec_path)

        with self._caplog.at_level(logging.DEBUG):
            with pytest.raises(SystemExit) as sample:
                self._caplog.clear()

                # ignore return value due to sys.exit()
                load_source(module_name_str, path=syntax_err_rel_filespec_path)
                assert sample.type == SystemExit
                assert sample.value.code == errno.ENOEXEC
            assert "invalid syntax" in self._caplog.text

        # Cleanup
        if module_name_str in sys.modules:  # module_name used, not extracted from file
            # del module after ALL asserts, errnos, and STDOUT
            del sys.modules[module_name_str]
        Path(syntax_err_rel_filespec_path).unlink(missing_ok=True)

    def test_load_source_module_path_abs_syntax_error_fail(self):
        """Syntax error; valid absolute file, Path type; valid module; passing mode"""
        # In Pelican, module name shall always be 'pelicanconf'
        module_name_str = PC_MODNAME_DEFAULT
        if module_name_str in sys.modules:
            AssertionError(
                f"Module {module_name_str} is still preloaded; fatal setup "
                f"error; aborted."
            )

        # Set up temporary absolute "/$TEMPDIR/pelicanXXXXXX/(here)"
        tmp_abs_dirspec_path: Path = Path(
            tempfile.mkdtemp(
                # dir= supplies us with absolute default, as a default
                suffix=TMP_FILENAME_SUFFIX
            )
        )
        syntax_err_abs_filespec_path: Path = (
            tmp_abs_dirspec_path / PC_FULLNAME_SYNTAX_ERROR
        )
        # copy "pseudo-script" file to '/tmp' (ruff/black avoidance of syntax-error)
        blob = Path(DIRSPEC_DATADIR) / BLOB_FULLNAME_SYNTAX_ERROR
        # despite tempdir, check if file does NOT exist
        if Path(syntax_err_abs_filespec_path).exists():
            # Bad test setup, assert out
            AssertionError(
                f"File {syntax_err_abs_filespec_path} should not " "exist in tempdir"
            )
        # Copy mangled pseudo-Python file into temporary area as a Python file
        shutil.copyfile(blob, syntax_err_abs_filespec_path)

        with self._caplog.at_level(logging.DEBUG):
            with pytest.raises(SystemExit) as sample:
                self._caplog.clear()

                # ignore return value due to sys.exit()
                module_type = load_source(
                    module_name_str,
                    syntax_err_abs_filespec_path,
                )
                assert module_type is not None
                assert sample.type == SystemExit
                assert sample.value.code == errno.ENOEXEC
            assert "invalid syntax" in self._caplog.text

        # Cleanup temporary
        if module_name_str in sys.modules:  # module_name used, not derived from file
            # del module after ALL asserts, errnos, and STDOUT
            del sys.modules[module_name_str]
        Path(syntax_err_abs_filespec_path).unlink(missing_ok=False)
        # There is a danger of __pycache__ being overlooked here only if this fails
        shutil.rmtree(tmp_abs_dirspec_path)

    # Start misusing the module_name, but with valid (path type) path always
    def test_load_source_module_invalid_fail(self):
        """Non-existent module name; valid relative file, Path type; passing mode"""
        module_not_exist = PC_MODNAME_NOT_EXIST
        valid_filespec = RO_FILESPEC_REL_VALID_PATH

        if module_not_exist in sys.modules:
            AssertionError(
                f"Test setup error; module {module_not_exist} not "
                "supposed to exist. Aborted"
            )
        module_spec = load_source(module_not_exist, valid_filespec)
        # TODO Probably needs another assert here
        assert module_spec is not None

        # Cleanup
        # Really cannot clean up a module if it is not supposed to exist
        # It could be an accidental but actual module that we mistakenly targeted,
        # so do nothing for cleanup

    def test_load_source_module_taken_by_builtin_fail(self):
        """Built-in module name; valid relative file, Path type; failing mode"""
        module_name_taken_by_builtin = PC_MODNAME_SYS_BUILTIN
        # Check if it IS a system built-in module
        if module_name_taken_by_builtin not in sys.modules:
            AssertionError(
                f"Module {module_name_taken_by_builtin} is not a built-in "
                f"module; redefine PC_MONDNAME_SYS_BUILTIN"
            )
        valid_rel_filespec_path = RO_FILESPEC_REL_VALID_PATH
        # Taking Python system builtin module is always a hard exit
        with self._caplog.at_level(logging.DEBUG):
            with pytest.raises(SystemExit) as sample:
                self._caplog.clear()

                module_spec = load_source(
                    module_name_taken_by_builtin, valid_rel_filespec_path
                )
                # assert "taken by builtin" in self._caplog.text  # TODO add caplog here
                assert sample.type == SystemExit
                assert sample.value.code == errno.ENOEXEC
                assert module_spec is None
            assert "reserved the module name" in self._caplog.text
        # DO NOT PERFORM del sys.module[] here, this is a built-in
        # But do check that built-in module is left alone
        if module_name_taken_by_builtin not in sys.modules:
            pytest.exit(
                f"Module {module_name_taken_by_builtin} is not a built-in "
                f"module; redefine PC_MODNAME_SYS_BUILTIN"
            )

    def test_load_source_module_dotted_fail(self):
        """Dotted module name; valid relative file, Path type; failing mode"""
        dotted_module_name_str = PC_MODNAME_DOTTED
        valid_rel_filespec_str = str(RO_FILESPEC_REL_VALID_PATH)
        # Taking Python system builtin module is always a hard exit
        with self._caplog.at_level(logging.DEBUG):
            self._caplog.clear()

            module_spec = load_source(dotted_module_name_str, valid_rel_filespec_str)
            assert module_spec is None
            assert "Cannot use dotted module name" in self._caplog.text
        # DO NOT PERFORM del sys.module[] here, this is an impossible dotted module

    def test_load_source_only_valid_module_str_fail(self):
        """only valid module_name, str type, failing mode"""
        #   don't let Pelican search all over the places using PYTHONPATH
        module_spec = load_source(name=str(PC_MODNAME_DEFAULT), path="")
        # not sure if STDERR capture is needed
        assert module_spec is None
        # TODO load_source() always always assert this SystemExit; add assert here?


class TestSettingsGetFromFile(unittest.TestCase):
    """Exercises get_from_settings_file()"""

    def test_get_from_file(self):
        assert True


if __name__ == "__main__":
    unittest.main()
