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
    base = environ.get('tiddlyweb.config', {}).get('markdown.wiki_link_base')
    extensions = ['headerid', 'footnotes', 'fenced_code', 'def_list']
    extension_configs = {}
    extensions.append('tiddlywebplugins.markdown.autolink')
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
