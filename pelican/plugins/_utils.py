import importlib
import importlib.machinery
import importlib.util
import logging
import pkgutil
import sys


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


def load_legacy_plugin(plugin, plugin_paths):
    # Try to find plugin in PLUGIN_PATHS
    spec = importlib.machinery.PathFinder.find_spec(plugin, plugin_paths)
    if spec is None:
        # If failed, try to find it in normal importable locations
        spec = importlib.util.find_spec(plugin)
    if spec is None:
        raise ImportError('Cannot import plugin `{}`'.format(plugin))
    else:
        # create module object from spec
        mod = importlib.util.module_from_spec(spec)
        # place it into sys.modules cache
        # necessary if module imports itself at some point (e.g. packages)
        sys.modules[spec.name] = mod
        try:
            # try to execute it inside module object
            spec.loader.exec_module(mod)
        except Exception:  # problem with import
            try:
                # remove module from sys.modules since it can't be loaded
                del sys.modules[spec.name]
            except KeyError:
                pass
            raise

        # if all went well, we have the plugin module
        return mod


def load_plugins(settings):
    logger.debug('Finding namespace plugins')
    namespace_plugins = get_namespace_plugins()
    if namespace_plugins:
        logger.debug('Namespace plugins found:\n' +
                     '\n'.join(namespace_plugins))
    plugins = []
    if settings.get('PLUGINS') is not None:
        for plugin in settings['PLUGINS']:
            if isinstance(plugin, str):
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
                        plugin = load_legacy_plugin(
                            plugin,
                            settings.get('PLUGIN_PATHS', []))
                    except ImportError as e:
                        logger.error('Cannot load plugin `%s`\n%s', plugin, e)
                        continue
            plugins.append(plugin)
    else:
        plugins = list(namespace_plugins.values())

    return plugins
