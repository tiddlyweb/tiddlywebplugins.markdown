"""
Test that safe mode works as desired.
"""

from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def setup_module(module):
    module.environ = {'tiddlyweb.config': {}}
    tiddler = Tiddler('foo')
    tiddler.text = '''
# h1 header

<h3>h3 header</h3>
'''
    module.tiddler = tiddler


def test_default_escape():
    output = render(tiddler, environ)

    assert '<h1 id="h1-header">h1 header</h1>' in output
    assert '<h3' not in output
    assert '<p>&lt;h3' in output


def test_remove():
    environ['tiddlyweb.config']['markdown.safe_mode'] = 'remove'
    output = render(tiddler, environ)

    assert '<h1 id="h1-header">h1 header</h1>' in output
    assert '<h3' not in output
    assert '<p>&lt;h3' not in output
    assert 'h3 header' not in output


def test_replace():
    environ['tiddlyweb.config']['markdown.safe_mode'] = 'replace'
    output = render(tiddler, environ)

    assert '<h1 id="h1-header">h1 header</h1>' in output
    assert '<h3' not in output
    assert '<p>&lt;h3' not in output
    assert 'h3 header' not in output
    assert '<p>[HTML_REMOVED]</p>' in output


def test_false():
    environ['tiddlyweb.config']['markdown.safe_mode'] = False
    output = render(tiddler, environ)

    assert '<h1 id="h1-header">h1 header</h1>' in output
    assert '<h3>h3 header</h3>' in output
    assert '<p>&lt;h3' not in output
    assert '<p>[HTML_REMOVED]</p>' not in output


def test_disallowed():
    environ['tiddlyweb.config']['markdown.safe_mode'] = 'monkey'
    output = render(tiddler, environ)

    assert '<h1 id="h1-header">h1 header</h1>' in output
    assert '<h3' not in output
    assert '<p>&lt;h3' in output
