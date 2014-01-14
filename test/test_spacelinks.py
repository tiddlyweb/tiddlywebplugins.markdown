import pytest

from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


try:
    from tiddlywebplugins.tiddlyspace.spaces import space_uri
    TIDDLYSPACE = True
except ImportError:
    TIDDLYSPACE = False


environ = {
    'tiddlyweb.config': {
        'markdown.wiki_link_base': '',
        'server_host': {
            'host': 'tiddlyspace.org',
            'port': '8080',
            'scheme': 'http',
        },
        'markdown.interlinker': space_uri
    }
}


@pytest.mark.skipif('TIDDLYSPACE == False')
def test_simple_spacelink():
    tiddler = Tiddler('test')
    tiddler.text = '# Hi\nVisit @cdent for more info.'

    output = render(tiddler, environ)

    assert '<a href="http://cdent.tiddlyspace.org:8080/">@cdent</a>' in output


def test_escaped_spacelink():
    tiddler = Tiddler('test')
    tiddler.text = '# Hi\nVisit ~@cdent for more info.'

    output = render(tiddler, environ)

    assert '<a href="http://cdent.tiddlyspace.org:8080/">@cdent</a>' not in output
    assert '@cdent' in output


@pytest.mark.skipif('TIDDLYSPACE == False')
def test_bounded_spacelink():
    tiddler = Tiddler('test')
    tiddler.text = '# Hi\nVisit @cdent: for more info.'

    output = render(tiddler, environ)

    assert ' <a href="http://cdent.tiddlyspace.org:8080/">@cdent</a>' in output
    assert '@cdent' in output


@pytest.mark.skipif('TIDDLYSPACE == False')
def test_spacelink_first():
    tiddler = Tiddler('test')
    tiddler.text = '@cdent for more info.'
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/">@cdent</a>' in output

    tiddler.text = '\n\n@cdent for more info.'
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/">@cdent</a>' in output


@pytest.mark.skipif('TIDDLYSPACE == False')
def test_spacewiki_link():
    tiddler = Tiddler('test')
    tiddler.text = "This is WikiLink@cdent"
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/WikiLink">WikiLink</a>' in output
    assert 'This is <a' in output


@pytest.mark.skipif('TIDDLYSPACE == False')
def test_spacewiki_first():
    tiddler = Tiddler('test')
    tiddler.text = "WikiLink@cdent"
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/WikiLink">WikiLink</a>' in output

    tiddler.text = "Hi WikiLink@cdent."
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/WikiLink">WikiLink</a>' in output

    tiddler.text = "Hi (WikiLink@cdent)"
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/WikiLink">WikiLink</a>' in output


@pytest.mark.skipif('TIDDLYSPACE == False')
def test_spacefree_link():
    tiddler = Tiddler('test')

    tiddler.text = "[[Free Link]]@cdent"
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/Free%20Link">Free Link</a>' in output
    tiddler.text = "lorem\n[[Free Link]]@cdent\nipsum"
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/Free%20Link">Free Link</a>' in output

    tiddler.text = "This is [[Free Link]]@cdent"
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/Free%20Link">Free Link</a>' in output

    tiddler.text = "This is [[Free Link]]@cdent: lorem ipsum"
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/Free%20Link">Free Link</a>' in output


@pytest.mark.skipif('TIDDLYSPACE == False')
def test_wiki_in_target():
    tiddler = Tiddler('test')
    tiddler.text = "[[posting|TiddlySpace Server Rebuild]]@blog"
    output = render(tiddler, environ)
    assert 'TiddlySpace' in output


@pytest.mark.skipif('TIDDLYSPACE == False')
def test_freelink_with_spacelink():
    # a freelink followed by a spacelink will get confused
    tiddler = Tiddler('Bar')
    environ = { 'tiddlyweb.config': {
        'markdown.wiki_link_base': '',
        'markdown.interlinker': space_uri,
        'server_host': {
            'scheme': 'http',
            'host': 'tiddlyspace.com',
            'port': '80'
            }
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
