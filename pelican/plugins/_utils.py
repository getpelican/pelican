import importlib
import logging
import pkgutil
import sys

import six


logger = logging.getLogger(__name__)


def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def get_namespace_plugins(ns_pkg=None):
    if ns_pkg is None:
        import pelican.plugins as ns_pkg

    return {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in iter_namespace(ns_pkg)
        if ispkg
    }


def list_plugins(ns_pkg=None):
    from pelican.log import init as init_logging
    init_logging(logging.INFO)
    ns_plugins = get_namespace_plugins(ns_pkg)
    if ns_plugins:
        logger.info('Plugins found:\n' + '\n'.join(ns_plugins))
    else:
        logger.info('No plugins are installed')


def load_plugins(settings):
    logger.debug('Finding namespace plugins')
    namespace_plugins = get_namespace_plugins()
    if namespace_plugins:
        logger.debug('Namespace plugins found:\n' +
                     '\n'.join(namespace_plugins))
    plugins = []
    if settings.get('PLUGINS') is not None:
        _sys_path = sys.path[:]

        for path in settings.get('PLUGIN_PATHS', []):
            sys.path.insert(0, path)

        for plugin in settings['PLUGINS']:
            if isinstance(plugin, six.string_types):
                logger.debug('Loading plugin `%s`', plugin)
                # try to find in namespace plugins
                if plugin in namespace_plugins:
                    plugin = namespace_plugins[plugin]
                elif 'pelican.plugins.{}'.format(plugin) in namespace_plugins:
                    plugin = namespace_plugins['pelican.plugins.{}'.format(
                        plugin)]
                # try to import it
                else:
                    try:
                        plugin = __import__(plugin, globals(), locals(),
                                            str('module'))
                    except ImportError as e:
                        logger.error('Cannot load plugin `%s`\n%s', plugin, e)
                        continue
            plugins.append(plugin)
        sys.path = _sys_path
    else:
        plugins = list(namespace_plugins.values())

    return plugins
