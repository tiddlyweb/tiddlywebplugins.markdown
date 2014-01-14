"""
Render markdown syntax wikitext to HTML using the
Python Markdown library.

If 'markdown.wiki_link_base' is set in config, then
TiddlyWeb oriented features are turned on (see below),
otherwise the text is treated as straight Markdown.

By default some extensions are included:

fenced_code: http://pythonhosted.org/Markdown/extensions/fenced_code_blocks.html
def_list: http://pythonhosted.org/Markdown/extensions/definition_lists.html
foootnotes: http://pythonhosted.org/Markdown/extensions/footnotes.html
headerid: http://pythonhosted.org/Markdown/extensions/header_id.html

The TiddlyWeb features add the following. If TiddlySpace
is available, then @space additions are availble.

wikilinks: CamelCase and CamelCase@space
spacelinks: @space
freelinks: [[some page]] and [[some page]]@space
labeled freelinks: [[target|some page]] and [[target|some page]]@space
transclusion: see below

Wikilinks and freelinks will be prefixed by wiki_link_base.
Set it to '' to activate WikiLinks without any prefix.

Transclusion uses the following syntax:

    {{tiddler title}}

That will include tiddler with the given title from the
current context (recipe or bag) of the transcluding tiddler.
If in a TiddlySpace environment then interspace transclusion
is possible:

    {{tiddler title}}@spacename

To use this renderer on Tiddlers which have a type of
'text/x-markdown' adjust tiddlywebconfig.py to include:

 'wikitext.type_render_map' :{
     'text/x-markdown': 'tiddlywebplugins.markdown'
     }

If you want all text tiddlers to be rendered as markdown,
then set

 'wikitext.default_renderer': 'tiddlywebplugins.markdown'
"""

__version__ = '1.1.0'

# for sake of making config calls clean, we import render
# into this space
from .render import render as markdown_render

# keep linters happy
render = markdown_render
