import shutil

from tiddlywebplugins.markdown import render
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.config import config

from tiddlywebplugins.utils import get_store


environ = {
    'tiddlyweb.config': {
        'markdown.wiki_link_base': '',
    'wikitext.type_render_map': {
        'text/x-markdown': 'tiddlywebplugins.markdown'
        }
    },
    'tiddlyweb.usersign': {
        'name': 'GUEST',
        'roles': []
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

    recipe = Recipe('recipe_public')
    recipe.set_recipe([('bag', '')])
    store.put(recipe)

    tiddlerA = Tiddler('tiddler a', 'bag')
    tiddlerA.text = 'I am _tiddler_'
    store.put(tiddlerA)

    tiddlerB = Tiddler('tiddler b')
    tiddlerB.text = '''
You wish

{{tiddler a}}

And I wish too.
'''
    module.tiddlerB = tiddlerB


def test_no_bag():
    output = render(tiddlerB, environ)

    assert 'I am _tiddler_' not in output
    assert 'You wish' in output


def test_recipe():
    tiddlerB.recipe = 'recipe_public'
    output = render(tiddlerB, environ)

    assert 'I am _tiddler_' in output
    assert 'You wish' in output


def test_bag():
    output = render(tiddlerB, environ)
    tiddlerB.bag = 'bag'

    assert 'I am _tiddler_' in output
    assert 'You wish' in output


def test_double_render_transclude():
    tiddlerA = store.get(Tiddler('tiddler a', 'bag'))
    tiddlerA.type = 'text/x-markdown'
    store.put(tiddlerA)

    output = render(tiddlerB, environ)

    assert 'I am <em>tiddler</em>' in output
    assert 'You wish' in output


def test_space_include():
    tiddlerB.text = '''
Hey There

{{tiddler a}}@recipe

We called that from outside, yo
'''

    output = render(tiddlerB, environ)

    assert 'I am <em>tiddler</em>' in output
    assert 'We called that from outside,' in output
