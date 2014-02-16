"""
Unworking stub for doing transclusion in markdown.
"""

import re

from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension

from tiddlyweb.control import determine_bag_from_recipe
from tiddlyweb.util import renderable
from tiddlyweb.store import StoreError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import PermissionsError
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web.util import tiddler_url
from tiddlyweb.wikitext import render_wikitext


TRANSCLUDE_RE = r'<p>{{([^}]+)}}(?:@([0-9A-Za-z][0-9A-Za-z\-]*[0-9A-Za-z]))?</p>'


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


# XXX: This should be moved to the tiddlyspace code repo at some
# point.
def tiddlyspace_target_resolver(environ, space, interior_tiddler):
    """
    Given a transclusion target that names a space, determine the
    bag and recipe of the target tiddler.
    """
    space_recipe = '%s_public' % space
    interior_bag = get_bag_from_recipe(environ, space_recipe,
            interior_tiddler)
    interior_tiddler.bag = interior_bag.name
    interior_tiddler.recipe = space_recipe


class TranscludeProcessor(Postprocessor):

    def __init__(self, pattern, config):
        Postprocessor.__init__(self)
        self.pattern = pattern
        self.environ = config['environ']
        self.tiddler = config['tiddler']
        self.store = self.environ.get('tiddlyweb.store')

    def transcluder(self, match):
        if 'markdown.transclusions' in self.environ:
            seen_titles = self.environ['markdown.transclusions']
        else:
            seen_titles = []

        interior_title = match.group(1)
        try:
            target = match.group(2)
        except IndexError:
            target = None

        # bail out if we have no store
        if not self.store:
            return match.group(0)

        try:
            interior_tiddler = self.resolve_tiddler(target, interior_title)
            interior_tiddler = self.store.get(interior_tiddler)
        except (StoreError, KeyError, PermissionsError):
            return match.group(0)

        semaphore_title = '%s:%s' % (interior_tiddler.bag,
                interior_tiddler.title)

        if semaphore_title not in seen_titles:
            seen_titles.append(semaphore_title)
            self.environ['markdown.transclusions'] = seen_titles
            if renderable(interior_tiddler, self.environ):
                content = render_wikitext(interior_tiddler, self.environ)
            else:
                content = ''
            seen_titles.pop()
            return '<article class="transclusion" data-uri="%s" ' \
                    'data-title="%s" data-bag="%s">%s</article>' % (
                            self.interior_url(interior_tiddler),
                            interior_tiddler.title,
                            interior_tiddler.bag, content)
        else:
            return match.group(0)

    def resolve_tiddler(self, target, title):
        interior_tiddler = Tiddler(title)
        if target:
            tiddlywebconfig = self.environ['tiddlyweb.config']
            target_resolver = tiddlywebconfig.get('markdown.target_resolver')
            if not target_resolver:
                interior_tiddler.bag = 'NoSuchBag'
            else:
                target_resolver(self.environ, target, interior_tiddler)
        else:
            if self.tiddler.recipe:
                interior_bag = get_bag_from_recipe(self.environ,
                        self.tiddler.recipe, interior_tiddler)
                interior_tiddler.bag = interior_bag.name
            else:
                interior_tiddler.bag = self.tiddler.bag
        return interior_tiddler

    def interior_url(self, tiddler):
        tiddlywebconfig = self.environ['tiddlyweb.config']
        interior_tiddler_url = tiddlywebconfig.get(
            'markdown.transclude_url', tiddler_url)
        return interior_tiddler_url(self.environ, tiddler)

    def run(self, text):
        return re.sub(self.pattern, self.transcluder, text)


class TransclusionExtension(Extension):

    def __init__(self, configs):
        self.config = {
                'environ': [{}, 'TiddlyWeb WSGI environ'],
                'tiddler': [None, 'The tiddler being worked on']
        }
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        transcludeProcessor = TranscludeProcessor(TRANSCLUDE_RE,
                self.getConfigs())
        transcludeProcessor.md = md
        md.postprocessors['transclusion'] = transcludeProcessor


def makeExtension(configs=None):
    return TransclusionExtension(configs=configs)
