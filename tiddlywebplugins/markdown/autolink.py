"""
Turn plain URI into links.

Heavily based on:

    https://github.com/r0wb0t/markdown-urlize

But simpler: just finds https? prefixed links.
"""

from markdown.inlinepatterns import Pattern
from markdown import Extension
from markdown.util import etree, AtomicString

BARELINK = r'(?<!">|=")(https?://[-\w./#?%=&:;@~]+)'


class LinkPattern(Pattern):

    def handleMatch(self, match):
        url = match.group(2)
        label = url

        link = etree.Element('a')
        link.set('href', url)
        link.text = AtomicString(label)
        return link


class TWAutoLink(Extension):
    def extendMarkdown(self, md, md_globals):
        linkPattern = LinkPattern(BARELINK, md)
        md.inlinePatterns.add('twautolink', linkPattern, '>autolink')


def makeExtension(configs=None):
    return TWAutoLink(configs=configs)
