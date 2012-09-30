from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def test_urlification():
    tiddler = Tiddler('blah')
    tiddler.text = """
lorem ipsum http://example.org dolor sit amet
... http://www.example.com/foo/bar ...
     """

    environ = {'tiddlyweb.config': {'markdown.wiki_link_base': ''}}
    output = render(tiddler, environ)

    for url in ["http://example.org", "http://www.example.com/foo/bar"]:
        assert '<a href="%(url)s">%(url)s</a>' % { "url": url } in output


def test_precedence():
    tiddler = Tiddler('cow')
    tiddler.text = """
* [Pry](http://www.philaquilina.com/2012/05/17/tossing-out-irb-for-pry/)
* [Rails console](http://37signals.com/svn/posts/3176-three-quick-rails-console-tips)
"""

    environ = {'tiddlyweb.config': {'markdown.wiki_link_base': ''}}
    output = render(tiddler, environ)

    assert "http://<a href" not in output
