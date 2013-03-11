from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def test_urlification():
    tiddler = Tiddler('blah')
    tiddler.text = """
lorem ipsum http://example.org dolor sit amet
... http://www.example.com/foo/bar ... and <http://example.com>
don't forget about http://www.example.com/search?q=tag:hello or goodbye
and you know this too http://example.com/tiddlers?select=tag:monkey;sort=-modified
so much stuff! and http://example.com/tiddlers?q=tag:@cdent wow
and how could we have forgotten http://example.com/~cdent of hyplan fame!
     """

    environ = {'tiddlyweb.config': {'markdown.wiki_link_base': ''}}
    output = render(tiddler, environ)

    for url in ["http://example.org", "http://www.example.com/foo/bar",
            'http://example.com', 'http://www.example.com/search?q=tag:hello',
            'http://example.com/tiddlers?select=tag:monkey;sort=-modified',
            'http://example.com/tiddlers?q=tag:@cdent',
            'http://example.com/~cdent']:
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
