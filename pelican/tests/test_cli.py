import unittest

from pelican import get_config, parse_arguments


class TestParseOverrides(unittest.TestCase):
    def test_flags(self):
        for flag in ['-e', '--extra-settings']:
            args = parse_arguments([flag, 'k=1'])
            self.assertDictEqual(args.overrides, {'k': 1})

    def test_parse_multiple_items(self):
        args = parse_arguments('-e k1=1 k2=2'.split())
        self.assertDictEqual(args.overrides, {'k1': 1, 'k2': 2})

    def test_parse_valid_json(self):
        json_values_python_values_map = {
            '""': '',
            'null': None,
            '"string"': 'string',
            '["foo", 12, "4", {}]': ['foo', 12, '4', {}]
        }
        for k, v in json_values_python_values_map.items():
            args = parse_arguments(['-e', 'k=' + k])
            self.assertDictEqual(args.overrides, {'k': v})

    def test_parse_invalid_syntax(self):
        invalid_items = ['k= 1', 'k =1', 'k', 'k v']
        for item in invalid_items:
            with self.assertRaises(ValueError):
                parse_arguments(f'-e {item}'.split())

    def test_parse_invalid_json(self):
        invalid_json = {
            '', 'False', 'True', 'None', 'some other string',
            '{"foo": bar}', '[foo]'
        }
        for v in invalid_json:
            with self.assertRaises(ValueError):
                parse_arguments(['-e ', 'k=' + v])


class TestGetConfigFromArgs(unittest.TestCase):
    def test_overrides_known_keys(self):
        args = parse_arguments([
            '-e',
            'DELETE_OUTPUT_DIRECTORY=false',
            'OUTPUT_RETENTION=["1.txt"]',
            'SITENAME="Title"'
        ])
        config = get_config(args)
        config_must_contain = {
            'DELETE_OUTPUT_DIRECTORY': False,
            'OUTPUT_RETENTION': ['1.txt'],
            'SITENAME': 'Title'
        }
        self.assertDictEqual(config, {**config, **config_must_contain})

    def test_overrides_non_default_type(self):
        args = parse_arguments([
            '-e',
            'DISPLAY_PAGES_ON_MENU=123',
            'PAGE_TRANSLATION_ID=null',
            'TRANSLATION_FEED_RSS_URL="someurl"'
        ])
        config = get_config(args)
        config_must_contain = {
            'DISPLAY_PAGES_ON_MENU': 123,
            'PAGE_TRANSLATION_ID': None,
            'TRANSLATION_FEED_RSS_URL': 'someurl'
        }
        self.assertDictEqual(config, {**config, **config_must_contain})
