#!/usr/bin/env python

import argparse
import locale
import os

from jinja2 import Environment, FileSystemLoader

import pytz

try:
    import readline  # NOQA
except ImportError:
    pass

try:
    import tzlocal
    _DEFAULT_TIMEZONE = tzlocal.get_localzone().zone
except ImportError:
    _DEFAULT_TIMEZONE = 'Europe/Rome'

from pelican import __version__

locale.setlocale(locale.LC_ALL, '')
try:
    _DEFAULT_LANGUAGE = locale.getlocale()[0]
except ValueError:
    # Don't fail on macosx: "unknown locale: UTF-8"
    _DEFAULT_LANGUAGE = None
if _DEFAULT_LANGUAGE is None:
    _DEFAULT_LANGUAGE = 'en'
else:
    _DEFAULT_LANGUAGE = _DEFAULT_LANGUAGE.split('_')[0]

_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "templates")
_jinja_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    trim_blocks=True,
)


_GITHUB_PAGES_BRANCHES = {
    'personal': 'main',
    'project': 'gh-pages'
}

CONF = {
    'pelican': 'pelican',
    'pelicanopts': '',
    'basedir': os.curdir,
    'ftp_host': 'localhost',
    'ftp_user': 'anonymous',
    'ftp_target_dir': '/',
    'ssh_host': 'localhost',
    'ssh_port': 22,
    'ssh_user': 'root',
    'ssh_target_dir': '/var/www',
    's3_bucket': 'my_s3_bucket',
    'cloudfiles_username': 'my_rackspace_username',
    'cloudfiles_api_key': 'my_rackspace_api_key',
    'cloudfiles_container': 'my_cloudfiles_container',
    'dropbox_dir': '~/Dropbox/Public/',
    'github_pages_branch': _GITHUB_PAGES_BRANCHES['project'],
    'default_pagination': 10,
    'siteurl': '',
    'lang': _DEFAULT_LANGUAGE,
    'timezone': _DEFAULT_TIMEZONE
}

# url for list of valid timezones
_TZ_URL = 'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones'


# Create a 'marked' default path, to determine if someone has supplied
# a path on the command-line.
class _DEFAULT_PATH_TYPE(str):
    is_default_path = True


_DEFAULT_PATH = _DEFAULT_PATH_TYPE(os.curdir)


def ask(question, answer=str, default=None, length=None):
    if answer == str:
        r = ''
        while True:
            if default:
                r = input('> {} [{}] '.format(question, default))
            else:
                r = input('> {} '.format(question))

            r = r.strip()

            if len(r) <= 0:
                if default:
                    r = default
                    break
                else:
                    print('You must enter something')
            else:
                if length and len(r) != length:
                    print('Entry must be {} characters long'.format(length))
                else:
                    break

        return r

    elif answer == bool:
        r = None
        while True:
            if default is True:
                r = input('> {} (Y/n) '.format(question))
            elif default is False:
                r = input('> {} (y/N) '.format(question))
            else:
                r = input('> {} (y/n) '.format(question))

            r = r.strip().lower()

            if r in ('y', 'yes'):
                r = True
                break
            elif r in ('n', 'no'):
                r = False
                break
            elif not r:
                r = default
                break
            else:
                print("You must answer 'yes' or 'no'")
        return r
    elif answer == int:
        r = None
        while True:
            if default:
                r = input('> {} [{}] '.format(question, default))
            else:
                r = input('> {} '.format(question))

            r = r.strip()

            if not r:
                r = default
                break

            try:
                r = int(r)
                break
            except ValueError:
                print('You must enter an integer')
        return r
    else:
        raise NotImplementedError(
            'Argument `answer` must be str, bool, or integer')


def ask_timezone(question, default, tzurl):
    """Prompt for time zone and validate input"""
    lower_tz = [tz.lower() for tz in pytz.all_timezones]
    while True:
        r = ask(question, str, default)
        r = r.strip().replace(' ', '_').lower()
        if r in lower_tz:
            r = pytz.all_timezones[lower_tz.index(r)]
            break
        else:
            print('Please enter a valid time zone:\n'
                  ' (check [{}])'.format(tzurl))
    return r


def main():
    parser = argparse.ArgumentParser(
        description="A kickstarter for Pelican",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--path', default=_DEFAULT_PATH,
                        help="The path to generate the blog into")
    parser.add_argument('-t', '--title', metavar="title",
                        help='Set the title of the website')
    parser.add_argument('-a', '--author', metavar="author",
                        help='Set the author name of the website')
    parser.add_argument('-l', '--lang', metavar="lang",
                        help='Set the default web site language')

    args = parser.parse_args()

    print('''Welcome to pelican-quickstart v{v}.

This script will help you create a new Pelican-based website.

Please answer the following questions so this script can generate the files
needed by Pelican.

    '''.format(v=__version__))

    project = os.path.join(
        os.environ.get('VIRTUAL_ENV', os.curdir), '.project')
    no_path_was_specified = hasattr(args.path, 'is_default_path')
    if os.path.isfile(project) and no_path_was_specified:
        CONF['basedir'] = open(project).read().rstrip("\n")
        print('Using project associated with current virtual environment. '
              'Will save to:\n%s\n' % CONF['basedir'])
    else:
        CONF['basedir'] = os.path.abspath(os.path.expanduser(
            ask('Where do you want to create your new web site?',
                answer=str, default=args.path)))

    CONF['sitename'] = ask('What will be the title of this web site?',
                           answer=str, default=args.title)
    CONF['author'] = ask('Who will be the author of this web site?',
                         answer=str, default=args.author)
    CONF['lang'] = ask('What will be the default language of this web site?',
                       str, args.lang or CONF['lang'], 2)

    if ask('Do you want to specify a URL prefix? e.g., https://example.com  ',
           answer=bool, default=True):
        CONF['siteurl'] = ask('What is your URL prefix? (see '
                              'above example; no trailing slash)',
                              str, CONF['siteurl'])

    CONF['with_pagination'] = ask('Do you want to enable article pagination?',
                                  bool, bool(CONF['default_pagination']))

    if CONF['with_pagination']:
        CONF['default_pagination'] = ask('How many articles per page '
                                         'do you want?',
                                         int, CONF['default_pagination'])
    else:
        CONF['default_pagination'] = False

    CONF['timezone'] = ask_timezone('What is your time zone?',
                                    CONF['timezone'], _TZ_URL)

    automation = ask('Do you want to generate a tasks.py/Makefile '
                     'to automate generation and publishing?', bool, True)

    if automation:
        if ask('Do you want to upload your website using FTP?',
               answer=bool, default=False):
            CONF['ftp'] = True,
            CONF['ftp_host'] = ask('What is the hostname of your FTP server?',
                                   str, CONF['ftp_host'])
            CONF['ftp_user'] = ask('What is your username on that server?',
                                   str, CONF['ftp_user'])
            CONF['ftp_target_dir'] = ask('Where do you want to put your '
                                         'web site on that server?',
                                         str, CONF['ftp_target_dir'])
        if ask('Do you want to upload your website using SSH?',
               answer=bool, default=False):
            CONF['ssh'] = True,
            CONF['ssh_host'] = ask('What is the hostname of your SSH server?',
                                   str, CONF['ssh_host'])
            CONF['ssh_port'] = ask('What is the port of your SSH server?',
                                   int, CONF['ssh_port'])
            CONF['ssh_user'] = ask('What is your username on that server?',
                                   str, CONF['ssh_user'])
            CONF['ssh_target_dir'] = ask('Where do you want to put your '
                                         'web site on that server?',
                                         str, CONF['ssh_target_dir'])

        if ask('Do you want to upload your website using Dropbox?',
               answer=bool, default=False):
            CONF['dropbox'] = True,
            CONF['dropbox_dir'] = ask('Where is your Dropbox directory?',
                                      str, CONF['dropbox_dir'])

        if ask('Do you want to upload your website using S3?',
               answer=bool, default=False):
            CONF['s3'] = True,
            CONF['s3_bucket'] = ask('What is the name of your S3 bucket?',
                                    str, CONF['s3_bucket'])

        if ask('Do you want to upload your website using '
               'Rackspace Cloud Files?', answer=bool, default=False):
            CONF['cloudfiles'] = True,
            CONF['cloudfiles_username'] = ask('What is your Rackspace '
                                              'Cloud username?', str,
                                              CONF['cloudfiles_username'])
            CONF['cloudfiles_api_key'] = ask('What is your Rackspace '
                                             'Cloud API key?', str,
                                             CONF['cloudfiles_api_key'])
            CONF['cloudfiles_container'] = ask('What is the name of your '
                                               'Cloud Files container?',
                                               str,
                                               CONF['cloudfiles_container'])

        if ask('Do you want to upload your website using GitHub Pages?',
               answer=bool, default=False):
            CONF['github'] = True,
            if ask('Is this your personal page (username.github.io)?',
                   answer=bool, default=False):
                CONF['github_pages_branch'] = \
                    _GITHUB_PAGES_BRANCHES['personal']
            else:
                CONF['github_pages_branch'] = \
                    _GITHUB_PAGES_BRANCHES['project']

    try:
        os.makedirs(os.path.join(CONF['basedir'], 'content'))
    except OSError as e:
        print('Error: {}'.format(e))

    try:
        os.makedirs(os.path.join(CONF['basedir'], 'output'))
    except OSError as e:
        print('Error: {}'.format(e))

    try:
        with open(os.path.join(CONF['basedir'], 'pelicanconf.py'),
                  'w', encoding='utf-8') as fd:
            conf_python = dict()
            for key, value in CONF.items():
                conf_python[key] = repr(value)

            _template = _jinja_env.get_template('pelicanconf.py.jinja2')
            fd.write(_template.render(**conf_python))
            fd.close()
    except OSError as e:
        print('Error: {}'.format(e))

    try:
        with open(os.path.join(CONF['basedir'], 'publishconf.py'),
                  'w', encoding='utf-8') as fd:
            _template = _jinja_env.get_template('publishconf.py.jinja2')
            fd.write(_template.render(**CONF))
            fd.close()
    except OSError as e:
        print('Error: {}'.format(e))

    if automation:
        try:
            with open(os.path.join(CONF['basedir'], 'tasks.py'),
                      'w', encoding='utf-8') as fd:
                _template = _jinja_env.get_template('tasks.py.jinja2')
                fd.write(_template.render(**CONF))
                fd.close()
        except OSError as e:
            print('Error: {}'.format(e))
        try:
            with open(os.path.join(CONF['basedir'], 'Makefile'),
                      'w', encoding='utf-8') as fd:
                py_v = 'python3'
                _template = _jinja_env.get_template('Makefile.jinja2')
                fd.write(_template.render(py_v=py_v, **CONF))
                fd.close()
        except OSError as e:
            print('Error: {}'.format(e))

    print('Done. Your new project is available at %s' % CONF['basedir'])


if __name__ == "__main__":
    main()
