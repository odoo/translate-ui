# Part of Odoo. See LICENSE file for full copyright and licensing details.

from __future__ import annotations

import functools
import logging

import odoo.tools.translate as translate


_logger = logging.getLogger(__name__)


original_get_translation = translate.get_translation


def get_text_alias(source: str, /, *args, **kwargs) -> TranslatedString:
    module, lang = translate._get_translation_source(1)
    translation = get_translation(module, lang, source, args or kwargs)
    return TranslatedString(translation, source, module)


def get_translation(module: str, lang: str, source: str, args: tuple | dict) -> TranslatedString:
    translation = original_get_translation(module, lang, source, args)
    return TranslatedString(translation, source, module)


def LazyGettext_translate(self, lang: str = '') -> str:
    module, lang = translate._get_translation_source(2, self._module, lang, default_lang=self._default_lang)
    return get_translation(module, lang, self._source, self._args)


@functools.total_ordering
class TranslatedString(str):
    __slots__ = '_evaluated_str', 'context', 'source', 'translation'

    def __new__(cls, translation: str | TranslatedString, source: str, context: str):
        return super().__new__(cls, str(translation))

    def __init__(self, translation: str | TranslatedString, source: str, context: str):
        if isinstance(translation, TranslatedString):
            self.translation = translation.translation
            if not context:
                context = translation.context
            if not source:
                source = translation.source
        else:
            self.translation = translation
        self.context = context
        self.source = source
        self._evaluated_str = ""

    def _format(self):
        if not self._evaluated_str:
            translated = self.translation != self.source
            source = self.source.replace('%s', '%%s')
            self._evaluated_str = f"_({self.context},{int(translated)}{{{source}}}[{self.translation}])"
        return self._evaluated_str

    def __repr__(self):
        """ Show for the debugger"""
        args = {'context': self.context, 'source': self.source, 'translation': self.translation}
        return f"TranslatedString({args!r})"

    def __str__(self):
        return self._format()

    def __eq__(self, other):
        if not isinstance(other, TranslatedString):
            return False
        return (self.source == other.source and
                self.translation == other.translation and
                self.context == other.context)

    def __hash__(self):
        return self._format().__hash__()

    def __lt__(self, other):
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, str):
            return self._format() + other
        elif isinstance(other, TranslatedString):
            return self._format() + other._format()
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return other + self._format()
        return NotImplemented

    def __mod__(self, other):
        return self._format().__mod__(other)


translate._ = get_text_alias
translate.get_text_alias = get_text_alias
translate.get_translation = get_translation
translate.LazyGettext._translate = LazyGettext_translate
