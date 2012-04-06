#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import os
import string
import argparse

from pelican import __version__

TEMPLATES = {
    'Makefile' : '''
PELICAN=$pelican
PELICANOPTS=$pelicanopts

BASEDIR=$$(PWD)
INPUTDIR=$$(BASEDIR)/src
OUTPUTDIR=$$(BASEDIR)/output
CONFFILE=$$(BASEDIR)/pelican.conf.py

FTP_HOST=$ftp_host
FTP_USER=$ftp_user
FTP_TARGET_DIR=$ftp_target_dir

SSH_HOST=$ssh_host
SSH_USER=$ssh_user
SSH_TARGET_DIR=$ssh_target_dir

DROPBOX_DIR=$dropbox_dir

help:
\t@echo 'Makefile for a pelican Web site                                       '
\t@echo '                                                                      '
\t@echo 'Usage:                                                                '
\t@echo '   make html                        (re)generate the web site         '
\t@echo '   make clean                       remove the generated files        '
\t@echo '   ftp_upload                       upload the web site using FTP     '
\t@echo '   ssh_upload                       upload the web site using SSH     '
\t@echo '   dropbox_upload                   upload the web site using Dropbox '
\t@echo '                                                                      '


html: clean $$(OUTPUTDIR)/index.html
\t@echo 'Done'

$$(OUTPUTDIR)/%.html:
\t$$(PELICAN) $$(INPUTDIR) -o $$(OUTPUTDIR) -s $$(CONFFILE) $$(PELICANOPTS)

clean:
\trm -fr $$(OUTPUTDIR)
\tmkdir $$(OUTPUTDIR)

dropbox_upload: $$(OUTPUTDIR)/index.html
\tcp -r $$(OUTPUTDIR)/* $$(DROPBOX_DIR)

rsync_upload: $$(OUTPUTDIR)/index.html
\trsync --delete -rvz -e ssh $(OUTPUTDIR)/* $(SSH_USER)@$(SSH_HOST):$(SSH_TARGET_DIR)

ssh_upload: $$(OUTPUTDIR)/index.html
\tscp -r $$(OUTPUTDIR)/* $$(SSH_USER)@$$(SSH_HOST):$$(SSH_TARGET_DIR)

ftp_upload: $$(OUTPUTDIR)/index.html
\tlftp ftp://$$(FTP_USER)@$$(FTP_HOST) -e "mirror -R $$(OUTPUTDIR) $$(FTP_TARGET_DIR) ; quit"

github: $$(OUTPUTDIR)/index.html
\tghp-import $$(OUTPUTDIR)
\tgit push origin gh-pages

.PHONY: html help clean ftp_upload ssh_upload dropbox_upload github
''',

    'pelican.conf.py': '''#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = u"$author"
SITENAME = u"$sitename"
SITEURL = '/'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG='$lang'

# Blogroll
LINKS =  (
    ('Pelican', 'http://docs.notmyidea.org/alexis/pelican/'),
    ('Python.org', 'http://python.org'),
    ('Jinja2', 'http://jinja.pocoo.org'),
    ('You can modify those links in your config file', '#')
         )

# Social widget
SOCIAL = (
          ('You can add links in your config file', '#'),
         )

DEFAULT_PAGINATION = $default_pagination
'''
}

CONF = {
    'pelican' : 'pelican',
    'pelicanopts' : '',
    'basedir': '.',
    'ftp_host': 'localhost',
    'ftp_user': 'anonymous',
    'ftp_target_dir': '/',
    'ssh_host': 'locahost',
    'ssh_user': 'root',
    'ssh_target_dir': '/var/www',
    'dropbox_dir' : '~/Dropbox/Public/',
    'default_pagination' : 10,
    'lang': 'en'
}


def ask(question, answer=str, default=None, l=None):
    if answer == str:
        r = ''
        while True:
            if default:
                r = raw_input('> {0} [{1}] '.format(question, default))
            else:
                r = raw_input('> {0} '.format(question, default))

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
                r = raw_input('> {0} (Y/n) '.format(question))
            elif default is False:
                r = raw_input('> {0} (y/N) '.format(question))
            else:
                r = raw_input('> {0} (y/n) '.format(question))

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
                print("You must answer `yes' or `no'")
        return r
    elif answer == int:
        r = None
        while True:
            if default:
                r = raw_input('> {0} [{1}] '.format(question, default))
            else:
                r = raw_input('> {0} '.format(question))

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
        raise NotImplemented('Arguent `answer` must be str, bool or integer')


def main():
    parser = argparse.ArgumentParser(
        description="A kickstarter for pelican",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--path', default=".",
            help="The path to generate the blog into")
    parser.add_argument('-t', '--title', metavar="title",
            help='Set the title of the website')
    parser.add_argument('-a', '--author', metavar="author",
            help='Set the author name of the website')
    parser.add_argument('-l', '--lang', metavar="lang",
            help='Set the default lang of the website')

    args = parser.parse_args()

    print('''Welcome to pelican-quickstart v{v}.

This script will help you creating a new Pelican based website.

Please answer the following questions so this script can generate the files needed by Pelican.

    '''.format(v=__version__))

    CONF['basedir'] = os.path.abspath(ask('Where do you want to create your new Web site ?', answer=str, default=args.path))
    CONF['sitename'] = ask('How will you call your Web site ?', answer=str, default=args.title)
    CONF['author'] = ask('Who will be the author of this Web site ?', answer=str, default=args.author)
    CONF['lang'] = ask('What will be the default language  of this Web site ?', str, args.lang or CONF['lang'], 2)

    CONF['with_pagination'] = ask('Do you want to enable article pagination ?', bool, bool(CONF['default_pagination']))

    if CONF['with_pagination']:
        CONF['default_pagination'] = ask('So how many articles per page do you want ?', int, CONF['default_pagination'])
    else:
        CONF['default_pagination'] = False

    mkfile = ask('Do you want to generate a Makefile to easily manage your website ?', bool, True)

    if mkfile:
        if ask('Do you want to upload your website using FTP ?', answer=bool, default=False):
            CONF['ftp_host'] = ask('What is the hostname of your FTP server ?', str, CONF['ftp_host'])
            CONF['ftp_user'] = ask('What is your username on this server ?', str, CONF['ftp_user'])
            CONF['ftp_traget_dir'] = ask('Where do you want to put your website on this server ?', str, CONF['ftp_target_dir'])

        if ask('Do you want to upload your website using SSH ?', answer=bool, default=False):
            CONF['ssh_host'] = ask('What is the hostname of your SSH server ?', str, CONF['ssh_host'])
            CONF['ssh_user'] = ask('What is your username on this server ?', str, CONF['ssh_user'])
            CONF['ssh_traget_dir'] = ask('Where do you want to put your website on this server ?', str, CONF['ssh_target_dir'])

        if ask('Do you want to upload your website using Dropbox ?', answer=bool, default=False):
            CONF['dropbox_dir'] = ask('Where is your Dropbox directory ?', str, CONF['dropbox_dir'])

    try:
        os.makedirs(os.path.join(CONF['basedir'], 'src'))
    except OSError, e:
        print('Error: {0}'.format(e))

    try:
        os.makedirs(os.path.join(CONF['basedir'], 'output'))
    except OSError, e:
        print('Error: {0}'.format(e))

    conf = string.Template(TEMPLATES['pelican.conf.py'])
    try:
        with open(os.path.join(CONF['basedir'], 'pelican.conf.py'), 'w') as fd:
            fd.write(conf.safe_substitute(CONF))
            fd.close()
    except OSError, e:
        print('Error: {0}'.format(e))

    if mkfile:
        Makefile = string.Template(TEMPLATES['Makefile'])

        try:
            with open(os.path.join(CONF['basedir'], 'Makefile'), 'w') as fd:
                fd.write(Makefile.safe_substitute(CONF))
                fd.close()
        except OSError, e:
            print('Error: {0}'.format(e))

    print('Done. Your new project is available at %s' % CONF['basedir'])
