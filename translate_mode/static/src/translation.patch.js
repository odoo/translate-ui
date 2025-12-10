import {
    appTranslateFn,
    TranslatedString,
    translatedTerms,
    translatedTermsGlobal,
    translationLoaded,
    translationSprintf,
} from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

/**
 * @template [T=unknown]
 * @typedef {import("@web/core/utils/strings").Substitutions<T>} Substitutions
 */

/**
 * @param {string} context
 * @param {boolean} translated
 * @param {string} source
 * @param {string} translation
 */
function stringifyContextualizedString(context, translated, source, translation) {
    return `_(${context},${Number(translated)}{${source}}[${translation}])`;
}

const S_NO_CONTEXT = Symbol("no-context");

patch(TranslatedString.prototype, {
    valueOf() {
        // Cannot call super: this will invoke the existing 'TranslatedString.valueOf'
        // method
        const source = String.prototype.valueOf.call(this);
        const { context, lazy, substitutions } = this;
        if (lazy && !translatedTerms[translationLoaded]) {
            // Evaluate lazy translated string while translations are not loaded
            // -> error
            throw new Error(`Cannot translate string: translations have not been loaded`);
        }
        let translation = translatedTerms[context]?.[source] ?? translatedTermsGlobal[source];
        const translated = typeof translation === "string";
        if (!translated) {
            // No translation: fallback to source term
            translation = source;
        }
        if (substitutions.length) {
            translation = translationSprintf(translation, substitutions);
        }
        if (isTranslateModeEnabled() && context !== S_NO_CONTEXT) {
            return stringifyContextualizedString(context, translated, source, translation);
        } else {
            return translation;
        }
    },
});

/**
 * @param {import("@web/env").OdooEnv} [env]
 */
export function isTranslateModeEnabled(env) {
    const debug = env?.debug ?? odoo.debug ?? "";
    return debug.includes("translate");
}

/**
 * Produces a translated string without a proper context, meaning that the resulting
 * translation will be ignored by the interactive translation system, and that its
 * surrounding context will be lost.
 *
 * This should only be used in the context of the 'InteractiveTranslationSidePanel'
 * to avoid recursive results (i.e. scan highlighted translations -> generating
 * results with other highlighted translations -> scan those translations -> etc.).
 *
 * @type {appTranslateFn}
 */
export function translateWithoutContext(source, ...substitutions) {
    return appTranslateFn(source, S_NO_CONTEXT, ...substitutions);
}
