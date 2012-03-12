from contextlib import contextmanager
from tempfile import mkdtemp
from shutil import rmtree

from pelican.contents import Article


@contextmanager
def temporary_folder():
    """creates a temporary folder, return it and delete it afterwards.

    This allows to do something like this in tests:

        >>> with temporary_folder() as d:
            # do whatever you want
    """
    tempdir = mkdtemp()
    yield tempdir
    rmtree(tempdir)


def get_article(title, slug, content, lang, extra_metadata=None):
    metadata = {'slug': slug, 'title': title, 'lang': lang}
    if extra_metadata is not None:
        metadata.update(extra_metadata)
    return Article(content, metadata=metadata)
