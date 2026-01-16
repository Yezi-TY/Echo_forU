/**
 * 语言切换组件
 */
import React from 'react';
import { Select, MenuItem, FormControl, InputLabel, SelectChangeEvent } from '@mui/material';
import { useTranslation } from 'react-i18next';

const languages = [
  { code: 'zh-CN', label: '简体中文' },
  { code: 'zh-TW', label: '繁體中文' },
  { code: 'en', label: 'English' },
  { code: 'ja', label: '日本語' },
];

export const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();
  const [mounted, setMounted] = React.useState(false);
  const [currentLanguage, setCurrentLanguage] = React.useState('zh-CN');

  // 避免 hydration 错误：只在客户端挂载后使用 i18n.language
  React.useEffect(() => {
    setMounted(true);
    setCurrentLanguage(i18n.language);
  }, [i18n.language]);

  const handleChange = (event: SelectChangeEvent<string>) => {
    const newLang = event.target.value;
    setCurrentLanguage(newLang);
    i18n.changeLanguage(newLang);
  };

  return (
    <FormControl size="small" sx={{ minWidth: 120 }}>
      <InputLabel id="language-select-label">Language</InputLabel>
      <Select
        labelId="language-select-label"
        id="language-select"
        value={mounted ? currentLanguage : 'zh-CN'}
        label="Language"
        onChange={handleChange}
      >
        {languages.map((lang) => (
          <MenuItem key={lang.code} value={lang.code}>
            {lang.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default LanguageSwitcher;

