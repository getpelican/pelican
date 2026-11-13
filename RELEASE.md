Release type: patch

Allow namespace plugins listed by name in ``PLUGINS`` to be loaded even when
they are hidden from ``pkgutil.iter_modules``, e.g. by setuptools PEP 660
editable installs
