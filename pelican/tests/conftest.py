#
# File: conftest.py
# Tester: pytest
#
import contextlib
import locale
import logging
import os  # os.path is being discontinued; use pathlib.Path
import shutil
import sys
from pathlib import Path

import filelock
import pytest


@pytest.fixture(scope="session")
def locale_to_c__fixture_session():
    """Load/unload the "C" locale"""
    old_locale = locale.setlocale(locale.LC_ALL)
    locale.setlocale(locale.LC_ALL, "C")

    yield

    locale.setlocale(locale.LC_ALL, old_locale)


@pytest.fixture(scope="session")
def temp_dir_all_unit_tests__fixture_session(tmp_path_factory):
    """A temporary directory for ALL unit tests"""

    # By supplying a basename, this insulates us from unexpected TMPDIR environment.
    yield tmp_path_factory.mktemp(basename="tmp_pelican", numbered=False)

    shutil.rmtree(tmp_path_factory.getbasetemp())


@pytest.fixture(scope="session")
def temp_settings_dir_all_unit_tests__fixture_session(
    tmp_path_factory, temp_dir_all_unit_tests__fixture_session
):
    temp_path = temp_dir_all_unit_tests__fixture_session
    session_dirname: str = str(temp_path / "tmp_settings")
    session_temp_path = tmp_path_factory.mktemp(
        basename=session_dirname, numbered=False
    )

    yield session_temp_path

    shutil.rmtree(session_temp_path)


@pytest.fixture(scope="session")
def lockfile_sys_modules__fixture_session(temp_dir_all_unit_tests__fixture_session):
    """Provide a locking file specific to `sys.modules[]` (per pytest)"""
    # to be called only by fixture_session_serialize_sys_modules()
    lock_file = temp_dir_all_unit_tests__fixture_session / "sys_modules_serial.lock"
    yield filelock.FileLock(lock_file=str(lock_file))
    with contextlib.suppress(OSError):
        os.remove(path=lock_file)


@pytest.fixture(scope="session")
def serialize_sys_modules__fixture_session(lockfile_sys_modules__fixture_session):
    """mark function test as serial/sequential ordering

    Include `serial` in the function's argument list ensures
    that no other test(s) also having `serial` in its argument list
    shall run."""
    with lockfile_sys_modules__fixture_session.acquire(poll_interval=0.1):
        yield


@pytest.fixture(scope="session")
def assert_module_integrity__fixture_session(serialize_sys_modules__fixture_session):
    """Ensure that `sys.modules` is intact after all unit tests in this module"""
    saved_sys_modules = sys.modules
    yield
    if not (saved_sys_modules == sys.modules):
        raise AssertionError(f"Entire {__file__} failed to preserve sys.modules.")
    else:
        logging.debug("all modules accounted for in sys.modules[].")


@pytest.fixture(scope="session")
def get_tests_dir__fixture_session():
    """Get the absolute directory path of `tests` subdirectory

    pytest session-wide fixture will provide a full directory path to the
    location of this `test_settings_syntax.py` pytest script file.

    Note: used to assist in locating the `settings` directory underneath it,
    and to guide toward the root directory of this Pelican package.

    This fixture gets evoked exactly once package-wide due to `scope=session`.

    :return: Returns the absolute path of the tests directory
    :rtype: pathlib.Path"""
    abs_tests_dirpath: Path = Path(__file__).parent  # secret sauce
    yield abs_tests_dirpath


@pytest.fixture(scope="session")
def get_tests_settings_dir__fixture_session(get_tests_dir__fixture_session):
    """Get the absolute directory path of `tests/settings` subdirectory

    This pytest session-wide fixture will provide the full directory
    path of the `settings` subdirectory containing various test configuration
    files for the `test_settings*.py` unit tests.

    This fixture gets evoked exactly once package-wide due to `scope=session`.

    :return: Returns the absolute path of the `tests/settings` directory
    :rtype: pathlib.Path"""
    settings_dirpath: Path = get_tests_dir__fixture_session / "settings"
    yield settings_dirpath


@pytest.fixture(scope="session")
def get_pelican_source_dir__fixture_session(
    get_tests_dir__fixture_session,
):
    """Get the `pelican` source subdirectory in absolute directory path.
    This fixture gets evoked exactly once package-wide due to `scope=session`.

    :return: Returns the absolute path of the Pelican root directory
    :rtype: pathlib.Path"""
    test_abs_dirpath = get_tests_dir__fixture_session
    # Go up one directory to Pelican source directory
    pelican_source_subdir_path: Path = test_abs_dirpath.parent
    yield pelican_source_subdir_path


@pytest.fixture(scope="session")
def get_pelican_package_dir__fixture_session(
    get_pelican_source_dir__fixture_session,
):
    """Get the absolute directory path of `pelican` package root directory
    This fixture gets evoked exactly once package-wide due to `scope=session`.

    :return: Returns the path of the Pelican root directory
    :rtype: pathlib.Path"""
    pelican_source_subdir_path = get_pelican_source_dir__fixture_session
    # Go up one directory to Pelican root directory
    pelican_package_dir_path = pelican_source_subdir_path.parent
    yield Path(pelican_package_dir_path)


if __name__ == "__main__":
    # if executing this file alone, it tests this file alone.
    # Can execute from any current working directory
    pytest.main([__file__])

    # more, complex variants of pytest.
    # pytest.main([__file__, "-n0", "-rAw", "--capture=no", "--no-header"])
    # pytest.main([__file__, "-n0"])  # single-process, single-thread
