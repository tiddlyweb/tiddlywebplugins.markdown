"""
Render markdown syntax wikitext to HTML
using the markdown2 library.

If 'markdown.wiki_link_base' is set in config,
then CamelCase words will becomes links, prefix
by wiki_link_base. Set it to '' to activate WikiLinks
without any prefix.

This version of markdown supports transclusion using
the following syntax:

    {{tiddler title}}

on a line by itself will include that tiddler, if it
exists. If in a TiddlySpace environment then interspace
transclusion is possible:

    {{tiddler title}}@spacename

To use on Tiddlers which have a type of 'text/x-markdown'
adjust config to include:

 'wikitext.type_render_map' :{
     'text/x-markdown': 'tiddlywebplugins.markdown'
     }

If you want all text tiddlers to be rendered as markdown,
then set

 'wikitext.default_renderer': 'tiddlywebplugins.markdown'
"""

import markdown


def render(tiddler, environ):
    """
    Render text in the provided tiddler to HTML.
    """
    base = environ.get('tiddlyweb.config', {}).get('markdown.wiki_link_base')
    extensions = ['headerid', 'footnotes', 'fenced_code', 'def_list']
    extension_configs = {}
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
