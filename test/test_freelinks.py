import pytest
from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def test_simple_freelinks():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '<a class="wikilink" href="Foo">' in output
    assert '>Foo</a>' in output
    assert '[[Foo]]' not in output
    assert output == '<p>lorem <a class="wikilink" href="Foo">Foo</a> ipsum</p>'

    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[Foo [] Bar]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[Foo [] Bar]]' in output


def test_spacing():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem[[Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert 'lorem[[Foo]]' in output

    tiddler = Tiddler('Foo')
    tiddler.text = '[[Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '<a class="wikilink" href="Foo">Foo</a>' in output

    tiddler = Tiddler('Foo')
    tiddler.text = '[[Foo|Bar Zoom]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '<a class="wikilink" href="Bar%20Zoom">Foo</a>' in output


def test_labeled_freelinks():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[hello world|Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '<a class="wikilink" href="Foo">' in output
    assert '>hello world</a>' in output
    assert '[[hello world|Foo]]' not in output
    assert output == '<p>lorem <a class="wikilink" href="Foo">hello world</a> ipsum</p>'

    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[hello [] world|Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[hello [] world|Foo]]' in output


def test_precedence():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[hello FooBar world]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[hello FooBar world]]' not in output
    assert '<a class="wikilink" href="FooBar">FooBar</a>' not in output
    assert '<a class="wikilink" href="hello%20FooBar%20world">hello FooBar world</a>' in output
    assert output == '<p>lorem <a class="wikilink" href="hello%20FooBar%20world">hello FooBar world</a> ipsum</p>'

    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[...|hello FooBar world]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[...|hello FooBar world]]' not in output
    assert '<a class="wikilink" href="FooBar">FooBar</a>' not in output
    assert '<a class="wikilink" href="hello%20FooBar%20world">...</a>' in output
    assert output == '<p>lorem <a class="wikilink" href="hello%20FooBar%20world">...</a> ipsum</p>'


# XXX: this can be fixed, but see:
# https://github.com/waylan/Python-Markdown/issues/196
@pytest.mark.xfail
def test_precedence_in_markdown_link():
    tiddler = Tiddler('Foo')
    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    tiddler.text = 'I see [foo LoremIpsum bar](http://example.org) you'
    output = render(tiddler, environ)
    assert output == '<p>I see <a href="http://example.org">foo LoremIpsum bar</a> you</p>'

def test_freelink_with_spacelink():
    # a freelink followed by a spacelink will get confused
    from tiddlywebplugins.tiddlyspace.spaces import space_uri
    tiddler = Tiddler('Bar')
    environ = { 'tiddlyweb.config': {
        'markdown.wiki_link_base': '',
        'server_host': {
            'scheme': 'http',
            'host': 'tiddlyspace.com',
            'port': '80'
            },
        'markdown.interlinker': space_uri,
        } }
    tiddler.text = 'I see [[fire]] and [[rain]] business'
    output = render(tiddler, environ)
    assert '>fire<' in output
    assert '>rain<' in output
    assert 'href="fire"' in output
    assert 'href="rain"' in output

    tiddler.text = 'I see [[fire]]@monkey and [[rain]]@monkey business'
    output = render(tiddler, environ)
    assert 'href="http://monkey.tiddlyspace.com/fire"' in output
    assert 'href="http://monkey.tiddlyspace.com/rain"' in output

    tiddler.text = 'I see [[fire]] and [[rain]]@monkey business'
    output = render(tiddler, environ)
    assert '>fire<' in output
    assert 'href="fire"' in output
    assert 'href="http://monkey.tiddlyspace' in output

    tiddler.text = 'I see [[rain]]@monkey and [[fire]] business'
    output = render(tiddler, environ)
    assert '>fire<' in output
    assert 'href="fire"' in output
    assert 'href="http://monkey.tiddlyspace.com/rain"' in output


def test_fragments():
    tiddler = Tiddler('Foo')
    tiddler.text = 'oh [[hi#cow]] bye'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert 'a class="wikilink" href="hi#cow">hi#cow</a>' in output

    tiddler = Tiddler('Foo')
    tiddler.text = 'oh [[what|hi#cow]] bye'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert 'a class="wikilink" href="hi#cow">what</a>' in output
