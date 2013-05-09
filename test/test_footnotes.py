"""
Test that footnotes work as desired.
"""

import pytest

from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def setup_module(module):
    module.environ = {'tiddlyweb.config': {'markdown.wiki_link_base': ''}}


def test_simple_footnote():
    tiddler = Tiddler('Foo')

    tiddler.text = """
Oh Now
======

We always talked[^1] about how much this should
happen, but chose the wrong tools. We should have
known[^inevitable].

[^1]: Asynch, of course.
[^inevitable]: Time. Flows.
"""

    output = render(tiddler, environ)

    #  slip in a headerid test
    assert '<h1 id="oh-now">Oh Now</h1>' in output

    # check footnotes get in there
    assert 'talked<sup id="fnref-1"><a class="footnote-ref" href="#fn-1">1</a></sup> about' in output
    assert '<li id="fn-1">' in output
    assert '<a class="footnote-backref" href="#fnref-1" title="Jump back to footnote 1 in the text">&#8617;</a>' in output

@pytest.mark.xfail
def test_footnote_linked():
    tiddler = Tiddler('Foo')
    tiddler.text = """
Welcome
=======

I want to make a footnote[^1] for all the world to see.

And it will be glorious.

[^1]: http://example.com/
"""

    output = render(tiddler, environ)
    assert '&#160;">http' not in output
