import types

from pelican import signals

def initialized(pelican):
    from pelican.settings import _DEFAULT_CONFIG
    _DEFAULT_CONFIG.setdefault('SUMMARY_BEGIN_MARKER',
                               '<!-- PELICAN_BEGIN_SUMMARY -->')
    _DEFAULT_CONFIG.setdefault('SUMMARY_END_MARKER',
                               '<!-- PELICAN_END_SUMMARY -->')
    if pelican:
        pelican.settings.setdefault('SUMMARY_BEGIN_MARKER',
                                    '<!-- PELICAN_BEGIN_SUMMARY -->')
        pelican.settings.setdefault('SUMMARY_END_MARKER',
                                    '<!-- PELICAN_END_SUMMARY -->')

def content_object_init(instance):
    # if summary is already specified, use it
    if 'summary' in instance.metadata:
        return

    def _get_content(self):
        content = self._content
        if self.settings['SUMMARY_BEGIN_MARKER']:
            content = content.replace(
                self.settings['SUMMARY_BEGIN_MARKER'], '', 1)
        if self.settings['SUMMARY_END_MARKER']:
            content = content.replace(
                self.settings['SUMMARY_END_MARKER'], '', 1)
        return content
    instance._get_content = types.MethodType(_get_content, instance)

    # extract out our summary
    if not hasattr(instance, '_summary'):
        content = instance._content
        begin_summary = -1
        end_summary = -1
        if instance.settings['SUMMARY_BEGIN_MARKER']:
            begin_summary = content.find(instance.settings['SUMMARY_BEGIN_MARKER'])
        if instance.settings['SUMMARY_END_MARKER']:
            end_summary = content.find(instance.settings['SUMMARY_END_MARKER'])
        if begin_summary != -1 or end_summary != -1:
            # the beginning position has to take into account the length
            # of the marker
            begin_summary = (begin_summary +
                            len(instance.settings['SUMMARY_BEGIN_MARKER'])
                            if begin_summary != -1 else 0)
            end_summary = end_summary if end_summary != -1 else None
            instance._summary = content[begin_summary:end_summary]

def register():
    signals.initialized.connect(initialized)
    signals.content_object_init.connect(content_object_init)
