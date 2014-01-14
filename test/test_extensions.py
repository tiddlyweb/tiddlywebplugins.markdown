from tiddlyweb.model.tiddler import Tiddler
from tiddlywebplugins.markdown import render

from py.test import raises


def test_instance_extensions():
    tiddler = Tiddler('Foo')
    tiddler.text = "hello world"

    environ = {
        'tiddlyweb.config': {
            'markdown.extensions': (['markdown.foo', 'markdown.bar'],
                    { 'foo': 'lipsum' })
        }
    }
    try:
        render(tiddler, environ)
        assert False
    except ImportError, exc:
        assert 'markdown.foo' in exc.args[0]
