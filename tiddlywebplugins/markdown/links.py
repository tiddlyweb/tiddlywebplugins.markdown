from markdown import util, inlinepatterns
from markdown.extensions.wikilinks import (WikiLinkExtension,
        WikiLinks)

from tiddlyweb.web.util import encode_name

FRONTBOUND = r'(?:^|(?<=[\s|\(]))'
FREELINK = FRONTBOUND + r'\[\[(.+?)\]\]'
WIKILINK = FRONTBOUND + r'([A-Z][a-z]+[A-Z]\w+\b)'

SPACELINK_BASE = r'(@[0-9a-z][0-9a-z\-]*[0-9a-z])(?:\b|$)'
SPACELINK = FRONTBOUND + SPACELINK_BASE
WIKISPACE = WIKILINK + SPACELINK_BASE
FREESPACE = FREELINK + SPACELINK_BASE

TIDDLYSPACE = False

try:
    from tiddlywebplugins.tiddlyspace.spaces import space_uri
    TIDDLYSPACE = True
except ImportError:
    pass


class MarkdownLinksExtension(WikiLinkExtension):

    def __init__(self, configs):
        self.config = {
                'base_url': ['', 'String to append to beginning or URL.'],
                'end_url': ['', 'String to append to end of URL.'],
                'html_class': ['wikilink', 'CSS hook. Leave blank for none.'],
                'environ': [{}, 'Base wsgi environ'],
        }
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        self.md = md

        if TIDDLYSPACE:
            wikispacelinkPattern = SpaceLinks(WIKISPACE, self.getConfigs())
            wikispacelinkPattern.md = md
            md.inlinePatterns.add('wikispacelink', wikispacelinkPattern,
                    '<link')

            freespacelinkPattern = SpaceLinks(FREESPACE, self.getConfigs())
            freespacelinkPattern.md = md
            md.inlinePatterns.add('freespacelink', freespacelinkPattern,
                    '<wikispacelink')

            spacelinkPattern = SpaceLinks(SPACELINK, self.getConfigs())
            spacelinkPattern.md = md
            md.inlinePatterns.add('spacelink', spacelinkPattern,
                    '>wikispacelink')

        wikilinkPattern = MarkdownLinks(WIKILINK, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.add('wikilink', wikilinkPattern, '<link')

        freelinkPattern = MarkdownLinks(FREELINK, self.getConfigs())
        freelinkPattern.md = md
        md.inlinePatterns.add('freelink', freelinkPattern, '<wikilink')


class SpaceLinks(inlinepatterns.Pattern):
    def __init__(self, pattern, config):
        inlinepatterns.Pattern.__init__(self, pattern)
        self.config = config

    def handleMatch(self, m):
        if m.lastindex == 4:  # we have a wikispacelink or freespace
            page = m.group(2)
            space = m.group(3)
            if page and space:
                if '|' in page:
                    label, target = page
                else:
                    label = target = page
                a = util.etree.Element('a')
                a.text = util.AtomicString(label)
                space = space.lstrip('@')
                a.set('href', space_uri(self.config['environ'], space)
                        + encode_name(target))
                return a
        else:
            matched_text = m.group(2)
            if matched_text:
                a = util.etree.Element('a')
                a.text = util.AtomicString(matched_text)
                space = a.text.lstrip('@')
                a.set('href', space_uri(self.config['environ'], space))
                return a
        return ''


class MarkdownLinks(WikiLinks):

    def handleMatch(self, m):
        matched_text = m.group(2)
        if matched_text:
            matched_text = matched_text.strip()
            base_url, end_url, html_class = self._getMeta()
            if '|' in matched_text:
                label, target = matched_text.split('|')
            else:
                label = target = matched_text
            url = '%s%s%s' % (base_url, encode_name(target), end_url)
            a = util.etree.Element('a')
            a.text = util.AtomicString(label)
            a.set('href', url)
            if html_class:
                a.set('class', html_class)
        else:
            a = ''
        return a


def makeExtension(configs=None):
    return MarkdownLinksExtension(configs=configs)
