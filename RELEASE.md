Release type: minor

- Add setting to selectively omit Typogrify filters `(#3439) <https://github.com/getpelican/pelican/pull/3439>`_
- Add more blocks to the Simple theme’s base template, making it easier to create new themes by inheriting from the Simple theme `(#3405) <https://github.com/getpelican/pelican/pull/3405>`_
- Fix auto-reload behavior upon changes to the theme, content or settings. Make default ``IGNORE_FILES`` recursively ignore all hidden files as well as the `default filters <https://watchfiles.helpmanual.io/api/filters/#watchfiles.DefaultFilter.ignore_dirs>`_ from ``watchfiles.DefaultFilter``. `(#3441) <https://github.com/getpelican/pelican/pull/3441>`_
- Get current year from the ``SOURCE_DATE_EPOCH`` environment variable, if available `(#3430) <https://github.com/getpelican/pelican/pull/3430>`_
- Add Python 3.13 to test matrix and remove Python 3.8 `(#3435) <https://github.com/getpelican/pelican/pull/3435>`_
- Require Typogrify 2.1+ and Pygments <2.19
