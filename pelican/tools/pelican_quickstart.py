#!/usr/bin/env python

# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import six

import os
import string
import argparse
import sys
import codecs
import pytz

from pelican import __version__

_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "templates")

_GITHUB_PAGES_BRANCHES = {
    'personal': 'master',
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
    'lang': 'en',
    'timezone': 'Europe/Paris'
}

#url for list of valid timezones
_TZ_URL = 'http://en.wikipedia.org/wiki/List_of_tz_database_time_zones'

def _input_compat(prompt):
    if six.PY3:
        r = input(prompt)
    else:
        r = raw_input(prompt)
    return r

if six.PY3:
    str_compat = str
else:
    str_compat = unicode

# Create a 'marked' default path, to determine if someone has supplied
# a path on the command-line.
class _DEFAULT_PATH_TYPE(str_compat):
    is_default_path = True

_DEFAULT_PATH = _DEFAULT_PATH_TYPE(os.curdir)

def decoding_strings(f):
    def wrapper(*args, **kwargs):
        out = f(*args, **kwargs)
        if isinstance(out, six.string_types) and not six.PY3:
            # todo: make encoding configurable?
            if six.PY3:
                return out
            else:
                return out.decode(sys.stdin.encoding)
        return out
    return wrapper


def get_template(name, as_encoding='utf-8'):
    template = os.path.join(_TEMPLATES_DIR, "{0}.in".format(name))

    if not os.path.isfile(template):
        raise RuntimeError("Cannot open {0}".format(template))

    with codecs.open(template, 'r', as_encoding) as fd:
        line = fd.readline()
        while line:
            yield line
            line = fd.readline()
        fd.close()


@decoding_strings
def ask(question, answer=str_compat, default=None, l=None):
    if answer == str_compat:
        r = ''
        while True:
            if default:
                r = _input_compat('> {0} [{1}] '.format(question, default))
            else:
                r = _input_compat('> {0} '.format(question, default))

            r = r.strip()

            if len(r) <= 0:
                if default:
                    r = default
                    break
                else:
                    print('You must enter something')
            else:
                if l and len(r) != l:
                    print('You must enter a {0} letters long string'.format(l))
                else:
                    break

        return r

    elif answer == bool:
        r = None
        while True:
            if default is True:
                r = _input_compat('> {0} (Y/n) '.format(question))
            elif default is False:
                r = _input_compat('> {0} (y/N) '.format(question))
            else:
                r = _input_compat('> {0} (y/n) '.format(question))

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
                r = _input_compat('> {0} [{1}] '.format(question, default))
            else:
                r = _input_compat('> {0} '.format(question))

            r = r.strip()

            if not r:
                r = default
                break

            try:
                r = int(r)
                break
            except:
                print('You must enter an integer')
        return r
    else:
        raise NotImplemented('Argument `answer` must be str_compat, bool, or integer')


def ask_timezone(question, default, tzurl):
    """Prompt for time zone and validate input"""
    lower_tz = [tz.lower() for tz in pytz.all_timezones]
    while True:
        r = ask(question, str_compat, default)
        r = r.strip().replace(' ', '_').lower()
        if r in lower_tz:
            r = pytz.all_timezones[lower_tz.index(r)]
            break
        else:
            print('Please enter a valid time zone:\n (check [{0}])'.format(tzurl))
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
        CONF['basedir'] = open(project, 'r').read().rstrip("\n")
        print('Using project associated with current virtual environment.'
              'Will save to:\n%s\n' % CONF['basedir'])
    else:
        CONF['basedir'] = os.path.abspath(os.path.expanduser(
            ask('Where do you want to create your new web site?', answer=str_compat, default=args.path)))

    CONF['sitename'] = ask('What will be the title of this web site?', answer=str_compat, default=args.title)
    CONF['author'] = ask('Who will be the author of this web site?', answer=str_compat, default=args.author)
    CONF['lang'] = ask('What will be the default language of this web site?', str_compat, args.lang or CONF['lang'], 2)

    if ask('Do you want to specify a URL prefix? e.g., http://example.com  ', answer=bool, default=True):
        CONF['siteurl'] = ask('What is your URL prefix? (see above example; no trailing slash)', str_compat, CONF['siteurl'])

    CONF['with_pagination'] = ask('Do you want to enable article pagination?', bool, bool(CONF['default_pagination']))

    if CONF['with_pagination']:
        CONF['default_pagination'] = ask('How many articles per page do you want?', int, CONF['default_pagination'])
    else:
        CONF['default_pagination'] = False

    CONF['timezone'] = ask_timezone('What is your time zone?', CONF['timezone'], _TZ_URL)

    automation = ask('Do you want to generate a Fabfile/Makefile to automate generation and publishing?', bool, True)
    develop = ask('Do you want an auto-reload & simpleHTTP script to assist with theme and site development?', bool, True)

    if automation:
        if ask('Do you want to upload your website using FTP?', answer=bool, default=False):
            CONF['ftp_host'] = ask('What is the hostname of your FTP server?', str_compat, CONF['ftp_host'])
            CONF['ftp_user'] = ask('What is your username on that server?', str_compat, CONF['ftp_user'])
            CONF['ftp_target_dir'] = ask('Where do you want to put your web site on that server?', str_compat, CONF['ftp_target_dir'])
        if ask('Do you want to upload your website using SSH?', answer=bool, default=False):
            CONF['ssh_host'] = ask('What is the hostname of your SSH server?', str_compat, CONF['ssh_host'])
            CONF['ssh_port'] = ask('What is the port of your SSH server?', int, CONF['ssh_port'])
            CONF['ssh_user'] = ask('What is your username on that server?', str_compat, CONF['ssh_user'])
            CONF['ssh_target_dir'] = ask('Where do you want to put your web site on that server?', str_compat, CONF['ssh_target_dir'])
        if ask('Do you want to upload your website using Dropbox?', answer=bool, default=False):
            CONF['dropbox_dir'] = ask('Where is your Dropbox directory?', str_compat, CONF['dropbox_dir'])
        if ask('Do you want to upload your website using S3?', answer=bool, default=False):
            CONF['s3_bucket'] = ask('What is the name of your S3 bucket?', str_compat, CONF['s3_bucket'])
        if ask('Do you want to upload your website using Rackspace Cloud Files?', answer=bool, default=False):
            CONF['cloudfiles_username'] = ask('What is your Rackspace Cloud username?', str_compat, CONF['cloudfiles_username'])
            CONF['cloudfiles_api_key'] = ask('What is your Rackspace Cloud API key?', str_compat, CONF['cloudfiles_api_key'])
            CONF['cloudfiles_container'] = ask('What is the name of your Cloud Files container?', str_compat, CONF['cloudfiles_container'])
        if ask('Do you want to upload your website using GitHub Pages?', answer=bool, default=False):
            if ask('Is this your personal page (username.github.io)?', answer=bool, default=False):
                CONF['github_pages_branch'] = _GITHUB_PAGES_BRANCHES['personal']
            else:
                CONF['github_pages_branch'] = _GITHUB_PAGES_BRANCHES['project']

    try:
        os.makedirs(os.path.join(CONF['basedir'], 'content'))
    except OSError as e:
        print('Error: {0}'.format(e))

    try:
        os.makedirs(os.path.join(CONF['basedir'], 'output'))
    except OSError as e:
        print('Error: {0}'.format(e))

    try:
        with codecs.open(os.path.join(CONF['basedir'], 'pelicanconf.py'), 'w', 'utf-8') as fd:
            conf_python = dict()
            for key, value in CONF.items():
                conf_python[key] = repr(value)

            for line in get_template('pelicanconf.py'):
                template = string.Template(line)
                fd.write(template.safe_substitute(conf_python))
            fd.close()
    except OSError as e:
        print('Error: {0}'.format(e))

    try:
        with codecs.open(os.path.join(CONF['basedir'], 'publishconf.py'), 'w', 'utf-8') as fd:
            for line in get_template('publishconf.py'):
                template = string.Template(line)
                fd.write(template.safe_substitute(CONF))
            fd.close()
    except OSError as e:
        print('Error: {0}'.format(e))

    if automation:
        try:
            with codecs.open(os.path.join(CONF['basedir'], 'fabfile.py'), 'w', 'utf-8') as fd:
                for line in get_template('fabfile.py'):
                    template = string.Template(line)
                    fd.write(template.safe_substitute(CONF))
                fd.close()
        except OSError as e:
            print('Error: {0}'.format(e))
        try:
            with codecs.open(os.path.join(CONF['basedir'], 'Makefile'), 'w', 'utf-8') as fd:
                mkfile_template_name = 'Makefile'
                py_v = 'PY?=python'
                if six.PY3:
                    py_v = 'PY?=python3'
                template = string.Template(py_v)
                fd.write(template.safe_substitute(CONF))
                fd.write('\n')
                for line in get_template(mkfile_template_name):
                    template = string.Template(line)
                    fd.write(template.safe_substitute(CONF))
                fd.close()
        except OSError as e:
            print('Error: {0}'.format(e))

    if develop:
        conf_shell = dict()
        for key, value in CONF.items():
            if isinstance(value, six.string_types) and ' ' in value:
                value = '"' + value.replace('"', '\\"') + '"'
            conf_shell[key] = value
        try:
            with codecs.open(os.path.join(CONF['basedir'], 'develop_server.sh'), 'w', 'utf-8') as fd:
                lines = list(get_template('develop_server.sh'))
                py_v = 'PY=${PY:-python}\n'
                if six.PY3:
                    py_v = 'PY=${PY:-python3}\n'
                lines = lines[:4] + [py_v] + lines[4:]
                for line in lines:
                    template = string.Template(line)
                    fd.write(template.safe_substitute(conf_shell))
                fd.close()
                os.chmod((os.path.join(CONF['basedir'], 'develop_server.sh')), 493) # mode 0o755
        except OSError as e:
            print('Error: {0}'.format(e))

    print('Done. Your new project is available at %s' % CONF['basedir'])

if __name__ == "__main__":
    main()
