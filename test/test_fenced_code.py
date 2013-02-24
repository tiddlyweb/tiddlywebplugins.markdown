"""
Test that fenced_code works as desired.
"""

from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def setup_module(module):
    module.environ = {'tiddlyweb.config': {'markdown.wiki_link_base': ''}}


def test_simple_fence():
    tiddler = Tiddler('Foo')

    tiddler.text = """
Crikey
======

There was a problem in the system so we decided to make
some changes to the config:

```
True = False
```

We did not get the desired results:

```
the cow    died
```
"""

    output = render(tiddler, environ)

    assert """config:</p>
<pre><code>True = False
</code></pre>""" in output

    # see those 4 spaces
    assert """</p>
<pre><code>the cow    died
</code></pre>""" in output


