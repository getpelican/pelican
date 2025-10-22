import copy

from pelican.settings import DEFAULT_CONFIG, read_settings


def test_read_settings_does_not_mutate_default_config():
    """read_settings() must not modify DEFAULT_CONFIG in place."""
    baseline = copy.deepcopy(DEFAULT_CONFIG)
    _ = read_settings()  # no args
    assert DEFAULT_CONFIG == baseline


def test_read_settings_without_args_matches_defaults_for_stable_keys():
    """
    When called without args, read_settings() should reflect DEFAULT_CONFIG
    for keys that are not post-processed (to avoid false negatives).
    """
    settings = read_settings()  # no args = rely on defaults

    stable_keys = [
        "DEFAULT_LANG",
        "RELATIVE_URLS",
        "DELETE_OUTPUT_DIRECTORY",
        "DEFAULT_PAGINATION",
        "WITH_FUTURE_DATES",
        "USE_FOLDER_AS_CATEGORY",
        "STATIC_CHECK_IF_MODIFIED",
    ]

    for key in stable_keys:
        assert settings[key] == DEFAULT_CONFIG[key], key


def test_read_settings_override_dict_takes_precedence_and_keeps_defaults_unchanged():
    """Values passed via override= should win, while DEFAULT_CONFIG stays intact."""
    key = "DEFAULT_LANG"
    orig = DEFAULT_CONFIG[key]

    settings = read_settings(override={key: "fr"})
    assert settings[key] == "fr"
    # and the module-level default must remain unchanged
    assert DEFAULT_CONFIG[key] == orig
