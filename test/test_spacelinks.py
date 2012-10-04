import pytest

from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


environ = {
    'tiddlyweb.config': {
        'markdown.wiki_link_base': '',
        'server_host': {
            'host': 'tiddlyspace.org',
            'port': '8080',
            'scheme': 'http',
        }
    }
}

try:
    import tiddlywebplugins.tiddlyspace
    tiddlyspace = True
except ImportError:
    tiddlyspace = False


@pytest.mark.skipif('tiddlyspace == False')
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


@pytest.mark.skipif('tiddlyspace == False')
def test_bounded_spacelink():
    tiddler = Tiddler('test')
    tiddler.text = '# Hi\nVisit @cdent: for more info.'

    output = render(tiddler, environ)

    assert ' <a href="http://cdent.tiddlyspace.org:8080/">@cdent</a>' in output
    assert '@cdent' in output


@pytest.mark.skipif('tiddlyspace == False')
def test_spacelink_first():
    tiddler = Tiddler('test')
    tiddler.text = '@cdent for more info.'
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/">@cdent</a>' in output

    tiddler.text = '\n\n@cdent for more info.'
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/">@cdent</a>' in output


@pytest.mark.skipif('tiddlyspace == False')
def test_spacewiki_link():
    tiddler = Tiddler('test')
    tiddler.text = "This is WikiLink@cdent"
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/WikiLink">WikiLink</a>' in output
    assert 'This is <a' in output


@pytest.mark.skipif('tiddlyspace == False')
def test_spacewiki_first():
    tiddler = Tiddler('test')
    tiddler.text = "WikiLink@cdent"
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/WikiLink">WikiLink</a>' in output


@pytest.mark.skipif('tiddlyspace == False')
def test_spacefree_link():
    tiddler = Tiddler('test')
    tiddler.text = "This is [[Free Link]]@cdent"
    output = render(tiddler, environ)
    assert '<a href="http://cdent.tiddlyspace.org:8080/Free%20Link">Free Link</a>' in output
