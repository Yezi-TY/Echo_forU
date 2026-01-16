/**
 * i18next 配置
 */
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 导入语言资源
import zhCN from '../../locales/zh-CN/common.json';
import zhTW from '../../locales/zh-TW/common.json';
import en from '../../locales/en/common.json';
import ja from '../../locales/ja/common.json';

i18n
  .use(LanguageDetector) // 自动检测浏览器语言
  .use(initReactI18next) // 初始化 react-i18next
  .init({
    resources: {
      'zh-CN': {
        common: zhCN,
      },
      'zh-TW': {
        common: zhTW,
      },
      en: {
        common: en,
      },
      ja: {
        common: ja,
      },
    },
    fallbackLng: 'zh-CN', // 默认语言
    defaultNS: 'common', // 默认命名空间
    interpolation: {
      escapeValue: false, // React 已经转义了
    },
    detection: {
      // 语言检测配置
      // 在服务器端渲染时禁用检测，避免 hydration 错误
      order: typeof window !== 'undefined' ? ['localStorage', 'navigator', 'htmlTag'] : ['htmlTag'],
      caches: typeof window !== 'undefined' ? ['localStorage'] : [],
      lookupLocalStorage: 'i18nextLng',
    },
  });

export default i18n;

