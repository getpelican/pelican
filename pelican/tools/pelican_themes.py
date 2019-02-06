#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import argparse
import os
import shutil
import sys


def err(msg, die=None):
    """Print an error message and exits if an exit code is given"""
    sys.stderr.write(msg + '\n')
    if die:
        sys.exit((die if type(die) is int else 1))


try:
    import pelican
except ImportError:
    err('Cannot import pelican.\nYou must '
        'install Pelican in order to run this script.',
        -1)


global _THEMES_PATH
_THEMES_PATH = os.path.join(
    os.path.dirname(
        os.path.abspath(pelican.__file__)
    ),
    'themes'
)

__version__ = '0.2'
_BUILTIN_THEMES = ['simple', 'notmyidea']


def main():
    """Main function"""

    parser = argparse.ArgumentParser(
        description="""Install themes for Pelican""")

    excl = parser.add_mutually_exclusive_group()
    excl.add_argument(
        '-l', '--list', dest='action', action="store_const", const='list',
        help="Show the themes already installed and exit")
    excl.add_argument(
        '-p', '--path', dest='action', action="store_const", const='path',
        help="Show the themes path and exit")
    excl.add_argument(
        '-V', '--version', action='version',
        version='pelican-themes v{0}'.format(__version__),
        help='Print the version of this script')

    parser.add_argument(
        '-i', '--install', dest='to_install', nargs='+', metavar="theme path",
        help='The themes to install')
    parser.add_argument(
        '-r', '--remove', dest='to_remove', nargs='+', metavar="theme name",
        help='The themes to remove')
    parser.add_argument(
        '-U', '--upgrade', dest='to_upgrade', nargs='+',
        metavar="theme path", help='The themes to upgrade')
    parser.add_argument(
        '-s', '--symlink', dest='to_symlink', nargs='+', metavar="theme path",
        help="Same as `--install', but create a symbolic link instead of "
             "copying the theme. Useful for theme development")
    parser.add_argument(
        '-c', '--clean', dest='clean', action="store_true",
        help="Remove the broken symbolic links of the theme path")

    parser.add_argument(
        '-v', '--verbose', dest='verbose',
        action="store_true",
        help="Verbose output")

    args = parser.parse_args()

    to_install = args.to_install or args.to_upgrade
    to_sym = args.to_symlink or args.clean

    if args.action:
        if args.action == 'list':
            list_themes(args.verbose)
        elif args.action == 'path':
            print(_THEMES_PATH)
    elif to_install or args.to_remove or to_sym:
        if args.to_remove:
            if args.verbose:
                print('Removing themes...')

            for i in args.to_remove:
                remove(i, v=args.verbose)

        if args.to_install:
            if args.verbose:
                print('Installing themes...')

            for i in args.to_install:
                install(i, v=args.verbose)

        if args.to_upgrade:
            if args.verbose:
                print('Upgrading themes...')

            for i in args.to_upgrade:
                install(i, v=args.verbose, u=True)

        if args.to_symlink:
            if args.verbose:
                print('Linking themes...')

            for i in args.to_symlink:
                symlink(i, v=args.verbose)

        if args.clean:
            if args.verbose:
                print('Cleaning the themes directory...')

            clean(v=args.verbose)
    else:
        print('No argument given... exiting.')


def themes():
    """Returns the list of the themes"""
    for i in os.listdir(_THEMES_PATH):
        e = os.path.join(_THEMES_PATH, i)

        if os.path.isdir(e):
            if os.path.islink(e):
                yield (e, os.readlink(e))
            else:
                yield (e, None)


def list_themes(v=False):
    """Display the list of the themes"""
    for t, l in themes():
        if not v:
            t = os.path.basename(t)
        if l:
            if v:
                print(t + (" (symbolic link to `" + l + "')"))
            else:
                print(t + '@')
        else:
            print(t)


def remove(theme_name, v=False):
    """Removes a theme"""

    theme_name = theme_name.replace('/', '')
    target = os.path.join(_THEMES_PATH, theme_name)

    if theme_name in _BUILTIN_THEMES:
        err(theme_name + ' is a builtin theme.\n'
            'You cannot remove a builtin theme with this script, '
            'remove it by hand if you want.')
    elif os.path.islink(target):
        if v:
            print('Removing link `' + target + "'")
        os.remove(target)
    elif os.path.isdir(target):
        if v:
            print('Removing directory `' + target + "'")
        shutil.rmtree(target)
    elif os.path.exists(target):
        err(target + ' : not a valid theme')
    else:
        err(target + ' : no such file or directory')


def install(path, v=False, u=False):
    """Installs a theme"""
    if not os.path.exists(path):
        err(path + ' : no such file or directory')
    elif not os.path.isdir(path):
        err(path + ' : not a directory')
    else:
        theme_name = os.path.basename(os.path.normpath(path))
        theme_path = os.path.join(_THEMES_PATH, theme_name)
        exists = os.path.exists(theme_path)
        if exists and not u:
            err(path + ' : already exists')
        elif exists and u:
            remove(theme_name, v)
            install(path, v)
        else:
            if v:
                print("Copying '{p}' to '{t}' ...".format(p=path,
                                                          t=theme_path))
            try:
                shutil.copytree(path, theme_path)

                try:
                    if os.name == 'posix':
                        for root, dirs, files in os.walk(theme_path):
                            for d in dirs:
                                dname = os.path.join(root, d)
                                os.chmod(dname, 493)  # 0o755
                            for f in files:
                                fname = os.path.join(root, f)
                                os.chmod(fname, 420)  # 0o644
                except OSError as e:
                    err("Cannot change permissions of files "
                        "or directory in `{r}':\n{e}".format(r=theme_path,
                                                             e=str(e)),
                        die=False)
            except Exception as e:
                err("Cannot copy `{p}' to `{t}':\n{e}".format(
                    p=path, t=theme_path, e=str(e)))


def symlink(path, v=False):
    """Symbolically link a theme"""
    if not os.path.exists(path):
        err(path + ' : no such file or directory')
    elif not os.path.isdir(path):
        err(path + ' : not a directory')
    else:
        theme_name = os.path.basename(os.path.normpath(path))
        theme_path = os.path.join(_THEMES_PATH, theme_name)
        if os.path.exists(theme_path):
            err(path + ' : already exists')
        else:
            if v:
                print("Linking `{p}' to `{t}' ...".format(
                    p=path, t=theme_path))
            try:
                os.symlink(path, theme_path)
            except Exception as e:
                err("Cannot link `{p}' to `{t}':\n{e}".format(
                    p=path, t=theme_path, e=str(e)))


def is_broken_link(path):
    """Returns True if the path given as is a broken symlink"""
    path = os.readlink(path)
    return not os.path.exists(path)


def clean(v=False):
    """Removes the broken symbolic links"""
    c = 0
    for path in os.listdir(_THEMES_PATH):
        path = os.path.join(_THEMES_PATH, path)
        if os.path.islink(path):
            if is_broken_link(path):
                if v:
                    print('Removing {0}'.format(path))
                try:
                    os.remove(path)
                except OSError:
                    print('Error: cannot remove {0}'.format(path))
                else:
                    c += 1

    print("\nRemoved {0} broken links".format(c))
