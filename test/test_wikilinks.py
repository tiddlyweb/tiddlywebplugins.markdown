from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


sample = """# Hello
    
This is WikiLink

* List
* List

This is not ~WikiLink because we escaped it.
"""

sample_linked = """

This is WikiLink and this is not: [NotLink](http://example.com).

This forthcoming in camel case but actually
a link [label](http://example.org/CamelCase)

This is (HtmlJavascript in parens).
This is (parens around HtmlJavascript).

"""


def test_no_wiki():
    tiddler = Tiddler('hello')
    tiddler.text = sample

    environ = {}
    output = render(tiddler, environ)
    assert '<h1 id="hello">' in output
    assert '<li>' in output
    assert 'href' not in output

    environ = {'tiddlyweb.config': {'markdown.wiki_link_base': ''}}
    output = render(tiddler, environ)
    assert 'href' in output
    assert '<a class="wikilink" href="WikiLink">' in output
    assert '>WikiLink</a>' in output
    assert 'is not WikiLink because we escaped' in output

    tiddler.text = sample_linked
    output = render(tiddler, environ)
    assert '"NotLink"' not in output
    assert '<a href="http://example.org/CamelCase">label</a>' in output

    assert '(<a class="wikilink" href="HtmlJavascript">HtmlJavascript</a> in parens)' in output
    assert '(parens around <a class="wikilink" href="HtmlJavascript">HtmlJavascript</a>)' in output
