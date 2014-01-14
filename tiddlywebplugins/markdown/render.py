"""
Markdown rendering subsystem.

We keep the actual activity in here to avoid import difficulties
while still maintaining easy configuration of the module (in
tiddlywebconfig.py).
"""

import markdown


def render(tiddler, environ):
    """
    Render text in the provided tiddler to HTML.
    """
    config = environ.get('tiddlyweb.config', {})
    base = config.get('markdown.wiki_link_base')
    extra_extensions, extra_configs = config.get('markdown.extensions',
            ([], {}))

    extensions = ['headerid', 'footnotes', 'fenced_code', 'def_list',
            'tiddlywebplugins.markdown.autolink'] + extra_extensions
    extension_configs = {}
    extension_configs.update(extra_configs)

    if base is not None:
        extensions.append('tiddlywebplugins.markdown.links')
        extensions.append('tiddlywebplugins.markdown.transclusion')
        extension_configs['tiddlywebplugins.markdown.links'] = [
                ('base_url', base), ('environ', environ)]
        extension_configs['tiddlywebplugins.markdown.transclusion'] = [
                ('environ', environ), ('tiddler', tiddler)]

    return markdown.markdown(tiddler.text,
            extensions=extensions,
            extension_configs=extension_configs,
            output_format='html5')
