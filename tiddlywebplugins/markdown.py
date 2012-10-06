"""
Render markdown syntax wikitext to HTML
using the markdown2 library.

If 'markdown.wiki_link_base' is set in config,
then CamelCase words will becomes links, prefix
by wiki_link_base. Set it to '' to activate WikiLinks
without any prefix.

This version of markdown supports transclusion using
the following syntax:

    {{tiddler title}}

on a line by itself will include that tiddler, if it 
exists. If in a TiddlySpace environment then interspace
transclusion is possible:

    {{tiddler title}}@spacename

To use on Tiddlers which have a type of 'text/x-markdown'
adjust config to include:

 'wikitext.type_render_map' :{
     'text/x-markdown': 'tiddlywebplugins.markdown'
     }

If you want all text tiddlers to be rendered as markdown,
then set

 'wikitext.default_renderer': 'tiddlywebplugins.markdown'
"""

import re
import markdown2

from tiddlyweb.control import determine_bag_from_recipe
from tiddlyweb.util import renderable
from tiddlyweb.store import StoreError
from tiddlyweb.web.util import encode_name
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import PermissionsError
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.wikitext import render_wikitext

TRANSCLUDE_RE = re.compile(r'<p>{{([^}]+)}}</p>')
PATTERNS = {
    'freelink': re.compile(r'\[\[(.+?)\]\]'),
    'wikilink': re.compile(r'((?<=\s)[A-Z][a-z]+[A-Z]\w+\b)'),
    'barelink': re.compile(r'(?<!">|=")(https?://[-\w./#?%=&]+)')
}

try:
    from tiddlywebplugins.tiddlyspace.spaces import space_uri
    PATTERNS['spacelink'] = (
            re.compile(r'(?:^|(?<=\s))@([0-9a-z][0-9a-z\-]*[0-9a-z])(?:\b|$)'))
    PATTERNS['spacewikilink'] = (
            re.compile(r'(?:^|(?<=\s))([A-Z][a-z]+[A-Z]\w+)@([0-9a-z][0-9a-z\-]*[0-9a-z])(?=\s|$)'))
    PATTERNS['spacefreelink'] = (
            re.compile(r'(?:^|(?<=\s))\[\[(.+?)\]\]@([0-9a-z][0-9a-z\-]*[0-9a-z])(?:\s|$)'))
    TRANSCLUDE_RE = (
            re.compile(r'<p>{{([^}]+)}}(?:@([0-9a-z][0-9a-z\-]*[0-9a-z]))?</p>'))
except ImportError:
    pass


class SpaceLinker(object):

    def __init__(self, environ):
        self.environ = environ

    def __call__(self, match):
        match_length = len(match.groups())
        if match_length == 1:
            space_name = match.groups()[0]
            url = space_uri(self.environ, space_name)
            return (url, '@%s' % space_name)
        else:
            page_name = match.groups()[0]
            space_name = match.groups()[1]
            try:
                label, page = page_name.split("|", 1)
            except ValueError:
                label = page = page_name

            url = '%s%s' % (space_uri(self.environ, space_name),
                    encode_name(page))
            return (url, label)


class FreeLinker(object):

    def __init__(self, base):
        self.base = base

    def __call__(self, match):
        link = match.groups()[0]
        try:
            label, page = link.split("|", 1)
        except ValueError:  # no label
            label = page = link
        return (page, label)


# subclass original Markdown class to allow for custom link labels
# XXX: patch pending: https://github.com/trentm/python-markdown2/pull/53
g_escape_table = markdown2.g_escape_table
_hash_text = markdown2._hash_text


class Markdown(markdown2.Markdown):

    def __init__(self, *args, **kwargs):
        environ = kwargs['environ']
        tiddler = kwargs['tiddler']
        del kwargs['environ']
        del kwargs['tiddler']
        if environ is None:
            environ = {}
        self.environ = environ
        self.tiddler = tiddler
        self.transclude_stack = {}
        # super
        markdown2.Markdown.__init__(self, *args, **kwargs)

    def _do_link_patterns(self, text):
        link_from_hash = {}
        for regex, repl in self.link_patterns:
            replacements = []
            for match in regex.finditer(text):
                title = None  # XXX: rename variable (ambiguous/misleading)
                if hasattr(repl, "__call__"):
                    components = repl(match)  # XXX: rename variable
                    try:
                        href, title = components
                    except ValueError:
                        href = components
                else:
                    href = match.expand(repl)
                replacements.append((match.span(), href, title))
            for (start, end), href, title in reversed(replacements):
                escaped_href = (
                    href.replace('"', '&quot;')  # b/c of attr quote
                        # To avoid markdown <em> and <strong>:
                        .replace('*', g_escape_table['*'])
                        .replace('_', g_escape_table['_']))
                if not title:
                    title = text[start:end]
                link = '<a href="%s">%s</a>' % (escaped_href, title)
                hash = _hash_text(link)
                link_from_hash[hash] = link
                text = text[:start] + hash + text[end:]
        for hash, link in link_from_hash.items():
            text = text.replace(hash, link)
        return text

    def postprocess(self, text):

        def transcluder(match):
            space_recipe = None
            try:
                interior_title = match.groups()[0]
                space = match.groups()[1]
                if space:
                    space_recipe = '%s_public' % space
            except IndexError:
                pass

            if interior_title in self.transclude_stack:
                return ''
            try:
                self.transclude_stack[self.tiddler.title].append(
                        interior_title)
            except KeyError:
                self.transclude_stack[self.tiddler.title] = [interior_title]

            interior_tiddler = Tiddler(interior_title)
            try:
                store = self.environ['tiddlyweb.store']
                if space_recipe:
                    interior_bag = get_bag_from_recipe(self.environ,
                            space_recipe, interior_tiddler)
                    interior_tiddler.bag = interior_bag.name
                else:
                    if self.tiddler.recipe:
                        interior_bag = get_bag_from_recipe(self.environ,
                                self.tiddler.recipe, interior_tiddler)
                        interior_tiddler.bag = interior_bag.name
                    else:
                        interior_tiddler.bag = self.tiddler.bag
                interior_tiddler = store.get(interior_tiddler)
            except (StoreError, KeyError, PermissionsError), exc:
                return ''
            if renderable(interior_tiddler, self.environ):
                content = render_wikitext(interior_tiddler, self.environ)
            else:
                content = ''
            return '<article class="transclusion" data-title="%s" ' \
                    'data-bag="%s">%s</article>' % (interior_tiddler.title,
                            interior_tiddler.bag, content)

        return re.sub(TRANSCLUDE_RE, transcluder, text)


def get_bag_from_recipe(environ, recipe_name, tiddler):
    """
    Check recipe policy, determine which bag this tiddler
    ought to come from, and check that bag's policy too.
    Raises StoreError and PermissionsError.
    """
    store = environ['tiddlyweb.store']
    recipe = store.get(Recipe(recipe_name))
    recipe.policy.allows(environ['tiddlyweb.usersign'], 'read')
    bag = determine_bag_from_recipe(recipe, tiddler, environ)
    bag = store.get(Bag(bag.name))
    bag.policy.allows(environ['tiddlyweb.usersign'], 'read')
    return bag


def render(tiddler, environ):
    """
    Render text in the provided tiddler to HTML.
    """
    wiki_link_base = environ.get('tiddlyweb.config', {}).get(
            'markdown.wiki_link_base', None)
    if wiki_link_base is not None:
        link_patterns = [
            (PATTERNS['freelink'], FreeLinker(wiki_link_base)),
            (PATTERNS['wikilink'], r'\1'),
            (PATTERNS['barelink'], r'\1'),
        ]
        if 'spacelink' in PATTERNS:
            for pattern in ['spacelink', 'spacewikilink', 'spacefreelink']:
                link_patterns.insert(0, (PATTERNS[pattern],
                    SpaceLinker(environ)))
    else:
        link_patterns = []
    processor = Markdown(extras=['link-patterns'],
            link_patterns=link_patterns, environ=environ, tiddler=tiddler)
    return processor.convert(tiddler.text)
