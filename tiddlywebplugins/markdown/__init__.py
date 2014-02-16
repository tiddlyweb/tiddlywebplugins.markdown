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

The TiddlyWeb features add the following:

wikilinks: CamelCase
freelinks: [[some page]]
labeled freelinks: [[label|some page]]
transclusion: see below

Wikilinks and freelinks will be prefixed by `markdown.wiki_link_base`.
Set it to '' to activate WikiLinks without any prefix (this is probably
the best choice, it results in links relative to the current tiddler).

Transclusion uses the following syntax:

    {{tiddler title}}

That will include tiddler with the given title from the
current context (recipe or bag) of the transcluding tiddler.

Links and transclusion can be augmented with @target syntax:

    @target
    CamelCase@target
    [[some page]]@target
    [[label|some page]]@target
    {{tiddler title}}@target

`target` is resolved via three different configuration settings:

* `markdown.interlinker` names a function which returns a link
   to whatever might be considered a target of some kind. It's
   arguments are a WSGI environ and a string representing the
   target. It returns a URI for the target, without the title
   of the tiddler.

* `markdown.target_resolver` names a function which determinesh
   the tiddler object that is to be transcluded. It's arguments
   are a WSGI environ, a string representing the context from
   which a tiddler is being transcluded and a tiddler object.
   That tiddler object is modified in place to add the bag in
   which it can be found.

* `markdown.transclude_url` names a function which returns a
   link to a tiddler in a target context. It's arguments are a
   WSGI environ and a tiddler. It returns a URI for the tiddler
   that has been transcluded. This is useful for augmenting the
   output to include a link to the transcluded tiddler.

To use this renderer on Tiddlers which have a type of
'text/x-markdown' adjust tiddlywebconfig.py to include:

 'wikitext.type_render_map' :{
     'text/x-markdown': 'tiddlywebplugins.markdown'
     }

If you want all tiddlers that have no type set to be rendered
as markdown, then configure:

 'wikitext.default_renderer': 'tiddlywebplugins.markdown'
"""

__version__ = '1.2.3'

# for sake of making config calls clean, we import render
# into this space
from .render import render as markdown_render

# keep linters happy
render = markdown_render
