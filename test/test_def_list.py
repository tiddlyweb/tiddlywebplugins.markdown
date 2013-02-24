"""
Test that def_list works as desired.
"""

from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def setup_module(module):
    module.environ = {'tiddlyweb.config': {'markdown.wiki_link_base': ''}}


def test_simple_def_list():
    tiddler = Tiddler('Foo')

    tiddler.text = """
Apple
:   Pomaceous fruit of plants of the genus Malus in 
    the family Rosaceae.

Orange
:   The fruit of an evergreen tree of the genus Citrus.
"""

    output = render(tiddler, environ)

    assert """<dt>Apple</dt>
<dd>Pomaceous fruit of plants of the genus Malus in 
the family Rosaceae.</dd>
<dt>Orange</dt>
<dd>The fruit of an evergreen tree of the genus Citrus.</dd>
</dl>""" in output

    # Note: the single space after the : is _required_
    tiddler.text = """
Apple
: Pomaceous fruit of plants of the genus Malus in 
the family Rosaceae.

Orange
: The fruit of an evergreen tree of the genus Citrus.
"""
    output = render(tiddler, environ)
    assert """<dt>Apple</dt>
<dd>Pomaceous fruit of plants of the genus Malus in 
the family Rosaceae.</dd>
<dt>Orange</dt>
<dd>The fruit of an evergreen tree of the genus Citrus.</dd>
</dl>""" in output
