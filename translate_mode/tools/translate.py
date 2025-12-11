# Part of Odoo. See LICENSE file for full copyright and licensing details.

from __future__ import annotations

import re
import logging

import odoo.tools.translate as translate


_logger = logging.getLogger(__name__)


R_CONTEXTUALIZED_STRING = re.compile(r"""
    _\(
    (?P<context>[/\w-]+),
    (?P<translated>0|1)
    \{(?P<source>.*?)\}
    \[(?P<translation>.*)\]
    \)
""")


original_get_code_translations = translate.CodeTranslations._get_code_translations
original_TranslationImporter_save = translate.TranslationImporter.save


def stringify_contextualized_string(context: str, source: str, translation: str)-> str:
    if R_CONTEXTUALIZED_STRING.match(translation):
        return translation
    translated = int(translation != source)
    escaped_source = source.replace('%s', '%%s')
    return f"_({context},{translated}{{{escaped_source}}}[{translation}])"


def CodeTranslations_get_code_translations(module_name, lang, filter_func):
    translations = original_get_code_translations(module_name, lang, filter_func)
    mapped = { source: stringify_contextualized_string(module_name, source,translation)
        for source, translation in translations.items() }
    return mapped

def TranslationImporter_save(self, *args, **kwargs):
    global_count = 0
    term_count = 0

    # Iterate through model translations
    for model_name in self.model_translations:
        model_values = self.model_translations[model_name]
        for field_name in model_values:
            field_values = model_values[field_name]
            # field = self.env[model_name]._fields.get(field_name)
            for xmlid in field_values:
                context = xmlid.split('.')[0]
                record = field_values[xmlid]
                for lang in record:
                    # TODO: find source
                    record[lang] = stringify_contextualized_string(context, "", record[lang])
                    global_count += 1

    # Iterate through model translated terms
    for model_name in self.model_terms_translations:
        model_values = self.model_terms_translations[model_name]
        for field_name in model_values:
            field_values = model_values[field_name]
            for xmlid in field_values:
                context = xmlid.split('.')[0]
                record = field_values[xmlid]
                for source in record:
                    terms = record[source]
                    for lang in terms:
                        terms[lang] = stringify_contextualized_string(context, source, terms[lang])
                        term_count += 1

    if global_count + term_count:
        _logger.warning(f"TranslationImported: flagged {global_count} model translations and {term_count} other translations")

    return original_TranslationImporter_save(self, *args, **kwargs)


translate.CodeTranslations._get_code_translations = CodeTranslations_get_code_translations
translate.TranslationImporter.save = TranslationImporter_save

# Reset cached translations
translate.code_translations.python_translations.clear()
translate.code_translations.web_translations.clear()
