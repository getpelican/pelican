Release type: minor

* Upgrade code to new minimum supported Python version: 3.8
* Settings support for ``pathlib.Path`` `(#2758) <https://github.com/getpelican/pelican/pull/2758>`_
* Various improvements to Simple theme (`#2976 <https://github.com/getpelican/pelican/pull/2976>`_ & `#3234 <https://github.com/getpelican/pelican/pull/3234>`_)
* Use Furo as Sphinx documentation theme `(#3023) <https://github.com/getpelican/pelican/pull/3023>`_
* Default to 100 articles maximum in feeds `(#3127) <https://github.com/getpelican/pelican/pull/3127>`_
* Add ``period_archives common context`` variable `(#3148) <https://github.com/getpelican/pelican/pull/3148>`_
* Use ``watchfiles`` as the file-watching backend `(#3151) <https://github.com/getpelican/pelican/pull/3151>`_
* Add GitHub Actions workflow for GitHub Pages `(#3189) <https://github.com/getpelican/pelican/pull/3189>`_
* Allow dataclasses in settings `(#3204) <https://github.com/getpelican/pelican/pull/3204>`_
* Switch build tool to PDM instead of Setuptools/Poetry `(#3220) <https://github.com/getpelican/pelican/pull/3220>`_
* Provide a ``plugin_enabled`` Jinja test for themes `(#3235) <https://github.com/getpelican/pelican/pull/3235>`_
* Preserve connection order in Blinker `(#3238) <https://github.com/getpelican/pelican/pull/3238>`_
* Remove social icons from default ``notmyidea`` theme `(#3240) <https://github.com/getpelican/pelican/pull/3240>`_
* Remove unreliable ``WRITE_SELECTED`` feature `(#3243) <https://github.com/getpelican/pelican/pull/3243>`_
* Importer: Report broken embedded video links when importing from Tumblr `(#3177) <https://github.com/getpelican/pelican/issues/3177>`_
* Importer: Remove newline addition when iterating Photo post types `(#3178) <https://github.com/getpelican/pelican/issues/3178>`_
* Importer: Force timestamp conversion in Tumblr importer to be UTC with offset `(#3221) <https://github.com/getpelican/pelican/pull/3221>`_
* Importer: Use tempfile for intermediate HTML file for Pandoc `(#3221) <https://github.com/getpelican/pelican/pull/3221>`_
* Switch linters to Ruff `(#3223) <https://github.com/getpelican/pelican/pull/3223>`_
