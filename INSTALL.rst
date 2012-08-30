Installation
############

The requirements in setup.py list 'feedgenerator'. For Python 2 pip will fetch
it from the cheeseshop for you. However, for Python 3 you need the Py3k port
feedgenerator. Currently it is available only here:
https://github.com/dmdm/feedgenerator-py3k/tree/from_django_1.5.dev20120824122350

If you want to import XML files, you need also to install BeautifulSoup4 and
lxml (bs4 needs lxml for parsing XML). Both can easily be installed via pip.
For lxml's C extentions to compile you almost certainly need to install the
header files of libxml2 (on Debian libxml2-dev and libxslt1-dev).

