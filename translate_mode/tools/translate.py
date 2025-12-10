# Part of Odoo. See LICENSE file for full copyright and licensing details.

from __future__ import annotations

from odoo.tools.translate import get_translation


class TranslatedString(str):
    __slots__ = '_evaluated_str', 'context', 'source', 'translation'

    def __new__(cls, translation: str, source: str, context: str, *args, **kwargs):
        return super().__new__(cls, translation, *args, **kwargs)

    def __init__(self, translation: str | TranslatedString, source: str, context: str):
        if isinstance(translation, TranslatedString):
            self.translation = translation.translation
            if not context:
                context = translation.context
        else:
            self.translation = translation
        self.context = context
        self.source = source
        self._evaluated_str = ""

    def __add__(self, other):
        if isinstance(other, TranslatedString):
            translation = self.translation + other.translation
            source = self.source + other.source
            return TranslatedString(translation, source, self.context)
        else:
            return self.translation.__add__(other)

    def __reduce__(self):
        return (TranslatedString, (self.translation, self.source, self.context))

    def __str__(self):
        if not self._evaluated_str:
            translated = self.translation != self.source
            self._evaluated_str = f"_({self.context},{int(translated)}{{{self.source}}}[{self.translation}])"
        return self._evaluated_str

    def __contains__(self, *args, **kwargs):
        return self.translation.__contains__(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        return self.translation.__eq__(*args, **kwargs)

    def __ge__(self, *args, **kwargs):
        return self.translation.__ge__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self.translation.__getitem__(*args, **kwargs)

    def __gt__(self, *args, **kwargs):
        return self.translation.__gt__(*args, **kwargs)

    def __hash__(self, *args, **kwargs):
        return self.translation.__hash__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self.translation.__iter__(*args, **kwargs)

    def __le__(self, *args, **kwargs):
        return self.translation.__le__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self.translation.__len__(*args, **kwargs)

    def __lt__(self, *args, **kwargs):
        return self.translation.__lt__(*args, **kwargs)

    def __mod__(self, *args, **kwargs):
        return self.translation.__mod__(*args, **kwargs)

    def __mul__(self, *args, **kwargs):
        return self.translation.__mul__(*args, **kwargs)

    def __ne__(self, *args, **kwargs):
        return self.translation.__ne__(*args, **kwargs)

    def __repr__(self, *args, **kwargs):
        return self.translation.__repr__(*args, **kwargs)

    def __rmod__(self, *args, **kwargs):
        return self.translation.__rmod__(*args, **kwargs)

    def __rmul__(self, *args, **kwargs):
        return self.translation.__rmul__(*args, **kwargs)

    def __sizeof__(self, *args, **kwargs):
        return self.translation.__sizeof__(*args, **kwargs)


def _get_translation(module: str, lang: str, source: str, args: tuple | dict) -> str:
    translation = get_translation(module, lang, source, args)
    return TranslatedString(translation, source, module)
