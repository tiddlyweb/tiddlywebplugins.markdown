
import shutil
from tiddlywebplugins.markdown import render
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.config import config

from tiddlywebplugins.utils import get_store


environ = {
    'tiddlyweb.config': {
        'markdown.wiki_link_base': '',
    'wikitext.type_render_map' : {
        'text/x-markdown': 'tiddlywebplugins.markdown'
        }
    }
}


def setup_module(module):
    try:
        shutil.rmtree('store')
    except:
        pass
    config['markdown.wiki_link_base'] = ''
    store = get_store(config)

    environ['tiddlyweb.store'] = store

    store.put(Bag('bag'))
    module.store = store

    tiddlerA = Tiddler('tiddler a', 'bag')
    tiddlerA.text = 'I am _tiddler_'
    store.put(tiddlerA)

def test_simple_transclude():
    tiddlerB = Tiddler('tiddler b', 'bag')
    tiddlerB.text = '''
You wish

{{tiddler a}}

And I wish too.
'''

    output = render(tiddlerB, environ)

    assert 'I am _tiddler_' in output
    assert 'You wish' in output

def test_double_render_transclude():
    tiddlerA = store.get(Tiddler('tiddler a', 'bag'))
    tiddlerA.type = 'text/x-markdown'
    store.put(tiddlerA)
    tiddlerB = Tiddler('tiddler b', 'bag')
    tiddlerB.text = '''
You wish

{{tiddler a}}

And I wish too.
'''

    output = render(tiddlerB, environ)

    assert 'I am <em>tiddler</em>' in output
    assert 'You wish' in output
