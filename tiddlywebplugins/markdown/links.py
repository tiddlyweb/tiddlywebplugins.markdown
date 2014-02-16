"""
Markdown extensions for freelinks and wikilinks, with
optional @target handling.
"""

import re

from markdown import util, inlinepatterns
from markdown.extensions.wikilinks import (WikiLinkExtension,
        WikiLinks)
from tiddlyweb.fixups import quote


FRONTBOUND = r'(?:^|(?<=[\s|\(]))'
FREELINKB = FRONTBOUND + r'\[\[([^]]+?)\]\]'
WIKILINKB = FRONTBOUND + r'(~?[A-Z][a-z]+[A-Z]\w+\b)'

FREELINK = FREELINKB + '(?!@)'
WIKILINK = WIKILINKB + '(?!@)'

TARGETLINK_BASE = r'(@[0-9A-Za-z][0-9A-Za-z\-]*[0-9A-Za-z])(?:\b|$)'
TARGETLINK = FRONTBOUND + TARGETLINK_BASE
WIKITARGET = WIKILINKB + TARGETLINK_BASE
FREETARGET = FREELINKB + TARGETLINK_BASE


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
        configs = self.getConfigs()
        tiddlywebconfig = configs['environ'].get('tiddlyweb.config', {})
        interlinker = tiddlywebconfig.get('markdown.interlinker', None)

        wikilinkPattern = MarkdownLinks(WIKILINK, configs)
        wikilinkPattern.md = md
        md.inlinePatterns.add('wikilink', wikilinkPattern, '<link')

        freelinkPattern = MarkdownLinks(FREELINK, configs)
        freelinkPattern.md = md
        md.inlinePatterns.add('freelink', freelinkPattern, '<wikilink')

        if interlinker:
            wikitargetlinkPattern = TargetLinks(WIKITARGET, configs)
            wikitargetlinkPattern.md = md
            md.inlinePatterns.add('wikitargetlink', wikitargetlinkPattern,
                    '<wikilink')

            freetargetlinkPattern = TargetLinks(FREETARGET, configs)
            freetargetlinkPattern.md = md
            md.inlinePatterns.add('freetargetlink', freetargetlinkPattern,
                    '<wikitargetlink')

            targetlinkPattern = TargetLinks(TARGETLINK, configs)
            targetlinkPattern.md = md
            md.inlinePatterns.add('targetlink', targetlinkPattern,
                    '>wikitargetlink')


class TargetLinks(inlinepatterns.Pattern):
    def __init__(self, pattern, config):
        inlinepatterns.Pattern.__init__(self, pattern)
        self.config = config
        tiddlywebconfig = config['environ'].get('tiddlyweb.config', {})
        self.interlinker = tiddlywebconfig.get('markdown.interlinker', None)

    def handleMatch(self, m):
        if m.lastindex == 4:  # we have a wikitargetlink or freetarget
            page = m.group(2)
            target = m.group(3)
            if page and target:
                if '|' in page:
                    label, destination = page.split('|', 1)
                else:
                    label = destination = page
                a = util.etree.Element('a')
                a.text = util.AtomicString(label)
                target = target.lstrip('@')
                target_base = self.interlinker(self.config['environ'], target)
                if not target_base.endswith('/'):
                    target_base = target_base + '/'
                a.set('href', target_base + encode_name(destination))
                return a
        else:
            matched_text = m.group(2)
            if matched_text:
                a = util.etree.Element('a')
                a.text = util.AtomicString(matched_text)
                target = a.text.lstrip('@')
                a.set('href', self.interlinker(self.config['environ'], target))
                return a
        return ''


class MarkdownLinks(WikiLinks):

    def handleMatch(self, m):
        matched_text = m.group(2)
        if matched_text:
            matched_text = matched_text.strip()
            base_url, end_url, html_class = self._getMeta()
            if '|' in matched_text:
                label, target = matched_text.split('|', 1)
            else:
                # short circuit escaping of ~WikiLink
                if (re.match(WIKILINK, matched_text)
                        and matched_text.startswith('~')):
                    return matched_text[1:]
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


def encode_name(name):
    """
    Like the encode_name found in tiddlyweb, but does not escape #.
    """
    return quote(name.encode('utf-8'), safe=".!~*'()#")
