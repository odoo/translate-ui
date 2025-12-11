import {
    appTranslateFn,
    TranslatedString,
    translatedTerms,
    translatedTermsGlobal,
    translationLoaded,
    translationSprintf,
} from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { composeRegExp } from "@web/core/utils/strings";

/**
 * @typedef {{
 *  context: string;
 *  translated: boolean;
 *  source: string;
 *  translation: string;
 * }} ContextualizedTranslation
 */

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
    if (R_CONTEXTUALIZED_TRANSLATION.test(translation)) {
        return translation;
    }
    return `_(${context},${Number(translated)}{${source}}[${translation}])`;
}

const R_CONTEXTUALIZED_TRANSLATION = composeRegExp(
    /_\(/, // starting delimiter
    /(?<context>[/\w-]+),/, // translation context (i.e. module)
    /(?<translated>0|1)/, // 1 if translated, else 0
    /\{(?<source>.*?)\}/, // source string
    /\[(?<translation>.*)\]/, // translated string
    /\)/ // ending delimiter
);
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
        } else if (context === S_NO_CONTEXT && R_CONTEXTUALIZED_TRANSLATION.test(translation)) {
            return parseTranslatedText(translation)[0];
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
 * @param {string} text
 * @returns {[value: string, translations: ContextualizedTranslation[]]}
 */
export function parseTranslatedText(text) {
    /** @type {ContextualizedTranslation[]} */
    const translations = [];
    if (!text || !R_CONTEXTUALIZED_TRANSLATION.test(text)) {
        return [text, translations];
    }
    const translationStack = [];
    let pendingChars = "";
    let result = "";
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        pendingChars += char;
        if (char === "_" && text[i + 1] === "(") {
            if (!translationStack.length) {
                // Add pending chars except "_"
                result += pendingChars.slice(0, -1);
                pendingChars = pendingChars.slice(-1);
            }
            pendingChars += text[++i];
            translationStack.push([1, "", "", "", ""]);
            continue;
        } else if (!translationStack.length) {
            continue;
        }
        const currentTranslation = translationStack.at(-1);
        const partIndex = currentTranslation[0];
        if (char === "," && partIndex === 1) {
            currentTranslation[0] = 2;
        } else if (char === "{" && partIndex === 2) {
            currentTranslation[0] = 3;
        } else if (char === "}" && text[i + 1] === "[" && partIndex === 3) {
            pendingChars += text[++i];
            currentTranslation[0] = 4;
        } else if (char === "]" && text[i + 1] === ")" && partIndex === 4) {
            i++;
            // Add translation to result
            const [, context, translated, source, translation] = translationStack.pop();
            if (translationStack.length) {
                translationStack.at(-1)[4] += translation;
            } else {
                result += translation;
            }
            translations.push({
                context,
                translated: translated === "1",
                source,
                translation,
            });
            pendingChars = "";
        } else {
            // Not a special character: add the char to the current part
            currentTranslation[partIndex] += char;
        }
    }
    return [result + pendingChars, translations];
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
