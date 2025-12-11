# Part of Odoo. See LICENSE file for full copyright and licensing details.

from __future__ import annotations

import re
import logging
import json
from collections import defaultdict

import odoo.tools.translate as translate


_logger = logging.getLogger(__name__)


R_CONTEXTUALIZED_TRANSLATION = re.compile(r"""
    _\(
    (?P<context>[/\w-]+),
    (?P<translated>0|1)
    \{(?P<source>.*?)\}
    \[(?P<translation>.*)\]
    \)
""")


original_get_code_translations = translate.CodeTranslations._get_code_translations
original_TranslationImporter_save = translate.TranslationImporter.save

next_missing_source_id = 1


def contextualize_translation(context: str, source: str, translation: str)-> str:
    if R_CONTEXTUALIZED_TRANSLATION.match(translation):
        return translation
    translated = 1 if translation else 0
    escaped_source = source.replace('%s', '%%s')
    return f"_({context},{translated}{{{escaped_source}}}[{translation}])"


def CodeTranslations_get_code_translations(module_name, lang, filter_func):
    translations = original_get_code_translations(module_name, lang, filter_func)
    mapped = { source: contextualize_translation(module_name, source,translation)
        for source, translation in translations.items() }
    return mapped


def TranslationImporter_save(self, *args, **kwargs):
    global next_missing_source_id

    counts = defaultdict(lambda: 0)
    addons = set()

    # Iterate through model translations
    for model_name in self.model_translations:
        model_values = self.model_translations[model_name]
        for field_name in model_values:
            field_values = model_values[field_name]
            for xmlid in field_values:
                context = xmlid.split('.')[0]
                addons.add(context)
                record = field_values[xmlid]
                # TODO: not working!
                # Need to find a way to retrieve the actual 'en_US' value
                if 'en_US' in record:
                    # Get source from English value
                    source = record['en_US']
                else:
                    # No source (English is not installed)
                    source = f"MISSING_SOURCE_{str(next_missing_source_id).zfill(8)}"
                    next_missing_source_id += 1
                for lang in record:
                    if lang == 'en_US':
                        continue
                    record[lang] = contextualize_translation(context, source, record[lang])
                    counts[model_name] += 1

    # Iterate through model translated terms
    for model_name in self.model_terms_translations:
        model_values = self.model_terms_translations[model_name]
        for field_name in model_values:
            field_values = model_values[field_name]
            for xmlid in field_values:
                context = xmlid.split('.')[0]
                addons.add(context)
                record_values = field_values[xmlid]
                for source in record_values:
                    record = record_values[source]
                    for lang in record:
                        record[lang] = contextualize_translation(context, source, record[lang])
                        counts[model_name] += 1

    if len(counts):
        _logger.debug(f"TranslationImporter: writing values for addons {list(addons)}: {json.dumps(counts, sort_keys=True, indent=2)}")

    return original_TranslationImporter_save(self, *args, **kwargs)


translate.CodeTranslations._get_code_translations = CodeTranslations_get_code_translations
translate.TranslationImporter.save = TranslationImporter_save

# Reset cached translations
translate.code_translations.python_translations.clear()
translate.code_translations.web_translations.clear()
