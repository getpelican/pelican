import unittest
from unittest.mock import MagicMock, patch

from pelican import DEFAULT_LOG_HANDLER, main


class TestLog(unittest.TestCase):
    @patch("pelican.get_instance")
    @patch("pelican.init_logging")
    def test_main_fatal_default(self, init_logging_mock, get_instance):
        get_instance.side_effect = lambda *args, **kwargs: (MagicMock(), MagicMock())
        main()
        init_logging_mock.assert_called_once_with(
            level=None,
            # default is "errors"
            fatal="errors",
            name="pelican",
            handler=DEFAULT_LOG_HANDLER,
            logs_dedup_min_level=30,
        )
