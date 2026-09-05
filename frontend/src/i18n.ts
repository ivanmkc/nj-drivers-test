type I18nData = Record<string, Record<string, string>>;

let i18nData: I18nData = {};
let currentLang = localStorage.getItem('quiz_lang') || 'en';

const LANG_LABELS: Record<string, string> = {
  en: 'EN',
  ja: '\u65E5\u672C\u8A9E',
  es: 'ES',
  fr: 'FR',
};

const LANG_NAMES: Record<string, string> = {
  en: 'English',
  es: 'Spanish',
  ja: 'Japanese',
  fr: 'French',
};

export function getLang() {
  return currentLang;
}

export function setLang(lang: string) {
  currentLang = lang;
  localStorage.setItem('quiz_lang', lang);
}

export function getAllLangs() {
  return Object.keys(i18nData);
}

export function getLangLabel(lang: string) {
  return LANG_LABELS[lang] || lang.toUpperCase();
}

export function getLangName(lang: string) {
  return LANG_NAMES[lang] || lang;
}

export function isOfficialLang(
  lang: string,
  officialTestLanguages: string[] | null | undefined,
): boolean {
  if (!officialTestLanguages) return false;
  const name = LANG_NAMES[lang]?.toLowerCase();
  if (!name) return false;
  return officialTestLanguages.some((l) => l.toLowerCase() === name);
}

export async function loadI18n(basePath: string) {
  const res = await fetch(`${basePath}i18n.json`);
  if (!res.ok) throw new Error(`Failed to load i18n: ${res.status}`);
  i18nData = await res.json();
}

export function t(key: string, vars?: Record<string, string | number>): string {
  let s = i18nData[currentLang]?.[key] || i18nData['en']?.[key] || key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      s = s.replaceAll(`{${k}}`, String(v));
    }
  }
  return s;
}

export function categoryName(cat: string): string {
  const key = `cat_${cat}`;
  const localized = i18nData[currentLang]?.[key] || i18nData['en']?.[key];
  if (localized) return localized;
  return cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}
